#!/usr/bin/env python3
"""Launcher for staticcheck that restores the workspace working directory."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()


def _find_binary_from_manifest(exe_name: str) -> Path | None:
    manifest_file = os.environ.get("RUNFILES_MANIFEST_FILE")
    if manifest_file:
        manifest_path = Path(manifest_file)
        if manifest_path.is_file():
            with manifest_path.open(encoding="utf-8") as f:
                for line in f:
                    match line.strip().split(" ", 1):
                        case [rpath, target] if rpath.endswith(f"/{exe_name}"):
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


def _find_binary(exe_name: str) -> Path | None:
    from_manifest = _find_binary_from_manifest(exe_name)
    if from_manifest:
        return from_manifest

    search_dirs: list[Path] = []
    runfiles_dir = _find_runfiles_dir()
    if runfiles_dir:
        search_dirs.append(runfiles_dir)
    search_dirs.extend([SCRIPT_PATH.parent.parent, SCRIPT_PATH.parent.parent.parent])

    for base in search_dirs:
        if not base.is_dir():
            continue
        for root, _dirs, files in os.walk(base):
            if exe_name in files and "staticcheck_" in root:
                return Path(root) / exe_name
    return None


def main() -> None:
    exe_name = "staticcheck.exe" if sys.platform == "win32" else "staticcheck"
    found_bin = _find_binary(exe_name)

    if not found_bin:
        sys.stderr.write("Error: Could not locate staticcheck binary in runfiles.\n")
        sys.exit(1)

    workspace_dir = os.environ.get("BUILD_WORKING_DIRECTORY") or os.environ.get("BUILD_WORKSPACE_DIRECTORY")
    if workspace_dir:
        os.chdir(workspace_dir)

    res = subprocess.run([str(found_bin.resolve()), *sys.argv[1:]], check=False)
    sys.exit(res.returncode)


if __name__ == "__main__":
    main()
