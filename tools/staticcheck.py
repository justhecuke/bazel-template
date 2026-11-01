#!/usr/bin/env python3
"""Launcher for staticcheck that restores the workspace working directory."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    workspace_dir = os.environ.get("BUILD_WORKING_DIRECTORY") or os.environ.get("BUILD_WORKSPACE_DIRECTORY")
    if workspace_dir:
        os.chdir(workspace_dir)

    exe_name = "staticcheck.exe" if sys.platform == "win32" else "staticcheck"
    runfiles_dir = os.environ.get("RUNFILES_DIR")
    found_bin = None

    if runfiles_dir:
        for root, _dirs, files in os.walk(runfiles_dir):
            if exe_name in files:
                found_bin = Path(root) / exe_name
                break

    if not found_bin:
        # Fallback to searching relative to this script
        for root, _dirs, files in os.walk(Path(__file__).parent.parent):
            if exe_name in files and "staticcheck_" in root:
                found_bin = Path(root) / exe_name
                break

    if not found_bin:
        sys.stderr.write("Error: Could not locate staticcheck binary in runfiles.\n")
        sys.exit(1)

    res = subprocess.run([str(found_bin), *sys.argv[1:]], check=False)
    sys.exit(res.returncode)


if __name__ == "__main__":
    main()
