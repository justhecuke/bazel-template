#!/usr/bin/env python3
"""Launcher for staticcheck that restores the workspace working directory."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _find_runfiles_dir() -> Path | None:
    runfiles_env = os.environ.get("PYTHON_RUNFILES") or os.environ.get("RUNFILES_DIR")
    if runfiles_env and Path(runfiles_env).is_dir():
        return Path(runfiles_env)

    for parent in [Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        if parent.name.endswith(".runfiles") and parent.is_dir():
            return parent
    return None


def _find_binary(exe_name: str) -> Path | None:
    search_dirs: list[Path] = []
    runfiles_dir = _find_runfiles_dir()
    if runfiles_dir:
        search_dirs.append(runfiles_dir)
    search_dirs.extend(
        [
            Path(__file__).resolve().parent.parent,
            Path(__file__).resolve().parent.parent.parent,
        ]
    )

    for base in search_dirs:
        if not base.is_dir():
            continue
        for root, _dirs, files in os.walk(base):
            if exe_name in files and "staticcheck_" in root:
                return Path(root) / exe_name
    return None


def main() -> None:
    workspace_dir = os.environ.get("BUILD_WORKING_DIRECTORY") or os.environ.get("BUILD_WORKSPACE_DIRECTORY")
    if workspace_dir:
        os.chdir(workspace_dir)

    exe_name = "staticcheck.exe" if sys.platform == "win32" else "staticcheck"
    found_bin = _find_binary(exe_name)

    if not found_bin:
        sys.stderr.write("Error: Could not locate staticcheck binary in runfiles.\n")
        sys.exit(1)

    res = subprocess.run([str(found_bin), *sys.argv[1:]], check=False)
    sys.exit(res.returncode)


if __name__ == "__main__":
    main()
