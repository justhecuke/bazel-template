#!/usr/bin/env python3
"""Launcher for staticcheck that restores the workspace working directory and provisions hermetic Go."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()


def _find_file_from_manifest(predicate: Callable[[str], bool]) -> Path | None:
    manifest_file = os.environ.get("RUNFILES_MANIFEST_FILE")
    if manifest_file:
        manifest_path = Path(manifest_file)
        if manifest_path.is_file():
            with manifest_path.open(encoding="utf-8") as f:
                for line in f:
                    match line.strip().split(" ", 1):
                        case [rpath, target] if predicate(rpath):
                            candidate = Path(target)
                            if candidate.is_file():
                                return candidate
                        case _:
                            continue
    return None


def _find_runfiles_dir() -> Path | None:
    runfiles_env = os.environ.get("PYTHON_RUNFILES") or os.environ.get("RUNFILES_DIR")
    if runfiles_env and Path(runfiles_env).is_dir():
        return Path(runfiles_env)

    for parent in [SCRIPT_PATH, *SCRIPT_PATH.parents]:
        if parent.name.endswith(".runfiles") and parent.is_dir():
            return parent
    return None


def _find_binary(rel_suffix: str, exe_name: str) -> Path | None:
    from_manifest = _find_file_from_manifest(lambda rpath: rpath.endswith(f"{rel_suffix}/{exe_name}"))
    if from_manifest:
        return from_manifest

    runfiles_dir = _find_runfiles_dir()
    if runfiles_dir:
        for repo_dir in runfiles_dir.iterdir():
            if not repo_dir.is_dir():
                continue
            candidate = repo_dir / rel_suffix / exe_name
            if candidate.is_file():
                return candidate

    return None


def main() -> None:
    exe_name = "staticcheck.exe" if sys.platform == "win32" else "staticcheck"
    go_exe = "go.exe" if sys.platform == "win32" else "go"

    found_bin = _find_binary("cmd/staticcheck/staticcheck_", exe_name)
    if not found_bin:
        found_bin = _find_binary("cmd/staticcheck", exe_name)

    if not found_bin:
        sys.stderr.write("Error: Could not locate staticcheck binary in runfiles.\n")
        sys.exit(1)

    hermetic_go = _find_binary("go/tools/go_bin_runner/bin", go_exe)
    if not hermetic_go:
        hermetic_go = _find_binary("bin", go_exe)

    if hermetic_go:
        os.environ["PATH"] = str(hermetic_go.parent.resolve()) + os.pathsep + os.environ.get("PATH", "")

    workspace_dir = os.environ.get("BUILD_WORKING_DIRECTORY") or os.environ.get("BUILD_WORKSPACE_DIRECTORY")
    if workspace_dir:
        os.chdir(workspace_dir)

    res = subprocess.run([str(found_bin.resolve()), *sys.argv[1:]], check=False)
    sys.exit(res.returncode)


if __name__ == "__main__":
    main()
