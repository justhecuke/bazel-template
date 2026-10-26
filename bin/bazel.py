#!/usr/bin/env python3
"""Bazel CLI wrapper with Python bootstrap isolation.

Runs Bazel inside an isolated root .venv to prevent host Python packages
from leaking into rules_python.

Usage Examples:
  bin/bazel test //...
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def _bootstrap_venv(venv_dir: Path) -> None:
    """Ensure an isolated Python venv exists for Bazel bootstrap."""
    if not venv_dir.is_dir():
        print("Bootstrapping isolated Python venv...")
        python_exe = "python3" if shutil.which("python3") else "python"
        subprocess.run([python_exe, "-m", "venv", str(venv_dir)], check=True)


def _setup_windows_bash(env: dict[str, str]) -> None:
    """Detect and set BAZEL_SH for Git Bash on Windows."""
    if "BAZEL_SH" in env:
        return

    potential_bashes = [
        "C:\\Program Files\\Git\\bin\\bash.exe",
        "C:\\Program Files\\Git\\usr\\bin\\bash.exe",
        shutil.which("bash"),
    ]
    for bash_path in potential_bashes:
        if bash_path and Path(bash_path).exists():
            # Avoid the broken WSL shim in System32
            if "System32" not in bash_path:
                env["BAZEL_SH"] = bash_path
                return


def _get_bazel_cmd(env: dict[str, str]) -> tuple[str, list[str]]:
    """Locate bazelisk/bazel and build the command list."""
    bazel_exe = shutil.which("bazelisk", path=env["PATH"]) or shutil.which("bazel", path=env["PATH"])
    if not bazel_exe:
        print("Error: Could not find bazelisk or bazel in PATH.")
        sys.exit(1)

    cmd = [bazel_exe, *sys.argv[1:]]

    # Auto-inject --config=ci in CI environments for execution commands
    if len(sys.argv) > 1 and sys.argv[1] in ["build", "test", "run", "coverage"]:
        if env.get("CI") == "true" and "--config=ci" not in sys.argv:
            cmd.insert(2, "--config=ci")

    # On Windows, enable runfiles by default as many Python-based tools (like Gazelle) depend on them.
    if sys.platform == "win32" and len(sys.argv) > 1 and sys.argv[1] in ["run", "test", "build"]:
        if "--enable_runfiles" not in sys.argv:
            cmd.insert(2, "--enable_runfiles")

    return bazel_exe, cmd


def main() -> None:
    workspace_root = Path(__file__).parent.parent.resolve()

    # Prevent "bazel should not be called from a bazel output directory" when tools
    # like goimports run inside bazel-out and invoke nested wrapper commands (e.g. go).
    workspace_env = os.environ.get("BUILD_WORKSPACE_DIRECTORY") or os.environ.get("BUILD_WORKING_DIRECTORY")
    if workspace_env:
        os.chdir(workspace_env)
    else:
        cwd_str = str(Path.cwd()).replace("\\", "/")
        if "bazel-out" in cwd_str or "execroot" in cwd_str:
            os.chdir(workspace_root)

    venv_dir = workspace_root / ".venv"
    _bootstrap_venv(venv_dir)

    # Activate venv environment in our current process copy
    env = os.environ.copy()
    if sys.platform == "win32":
        venv_bin = venv_dir / "Scripts"
    else:
        venv_bin = venv_dir / "bin"

    env["VIRTUAL_ENV"] = str(venv_dir.resolve())
    env["PATH"] = f"{venv_bin.resolve()}{os.pathsep}{env.get('PATH', '')}"

    if sys.platform == "win32":
        _setup_windows_bash(env)
        # Bypass UAC elevation triggers for targets with "update", "setup", or "install" in their name.
        env["__COMPAT_LAYER"] = "RunAsInvoker"

    bazel_exe, cmd = _get_bazel_cmd(env)

    # Execute the real bazel
    if sys.platform != "win32":
        os.execvpe(bazel_exe, cmd, env)
    else:
        sys.exit(subprocess.run(cmd, env=env, check=False).returncode)


if __name__ == "__main__":
    main()
