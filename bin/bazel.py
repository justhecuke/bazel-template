#!/usr/bin/env python3
"""
Wrapper to ensure Bazel runs inside an isolated Python venv.
Prevents system-level Python packages from leaking into Bazel's bootstrap process.
"""

import os
import shutil
import subprocess
import sys


def _bootstrap_venv(venv_dir):
    """Ensure an isolated Python venv exists for Bazel bootstrap."""
    if not os.path.isdir(venv_dir):
        print("Bootstrapping isolated Python venv...")
        python_exe = "python3" if shutil.which("python3") else "python"
        subprocess.run([python_exe, "-m", "venv", venv_dir], check=True)


def _setup_windows_bash(env):
    """Detect and set BAZEL_SH for Git Bash on Windows."""
    if "BAZEL_SH" in env:
        return

    potential_bashes = [
        "C:\\Program Files\\Git\\bin\\bash.exe",
        "C:\\Program Files\\Git\\usr\\bin\\bash.exe",
        shutil.which("bash"),
    ]
    for bash_path in potential_bashes:
        if bash_path and os.path.exists(bash_path):
            # Avoid the broken WSL shim in System32
            if "System32" not in bash_path:
                env["BAZEL_SH"] = bash_path
                return


def _get_bazel_cmd(env):
    """Locate bazelisk/bazel and build the command list."""
    bazel_exe = shutil.which("bazelisk", path=env["PATH"]) or shutil.which("bazel", path=env["PATH"])
    if not bazel_exe:
        print("Error: Could not find bazelisk or bazel in PATH.")
        sys.exit(1)

    cmd = [bazel_exe] + sys.argv[1:]

    # On Windows, enable runfiles by default as many Python-based tools (like Gazelle) depend on them.
    if sys.platform == "win32" and len(sys.argv) > 1 and sys.argv[1] in ["run", "test", "build"]:
        if "--enable_runfiles" not in sys.argv:
            cmd.insert(2, "--enable_runfiles")

    return bazel_exe, cmd


def main():
    venv_dir = ".venv"
    _bootstrap_venv(venv_dir)

    # Activate venv environment in our current process copy
    env = os.environ.copy()
    if sys.platform == "win32":
        venv_bin = os.path.join(venv_dir, "Scripts")
    else:
        venv_bin = os.path.join(venv_dir, "bin")

    env["VIRTUAL_ENV"] = os.path.abspath(venv_dir)
    env["PATH"] = f"{os.path.abspath(venv_bin)}{os.pathsep}{env.get('PATH', '')}"

    if sys.platform == "win32":
        _setup_windows_bash(env)
        # Bypass UAC elevation triggers for targets with "update", "setup", or "install" in their name.
        env["__COMPAT_LAYER"] = "RunAsInvoker"

    bazel_exe, cmd = _get_bazel_cmd(env)

    # Execute the real bazel
    if sys.platform != "win32":
        os.execvpe(bazel_exe, cmd, env)
    else:
        sys.exit(subprocess.run(cmd, env=env).returncode)


if __name__ == "__main__":
    main()
