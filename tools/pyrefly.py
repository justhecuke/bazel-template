from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path


def setup_bin_path() -> None:
    # Locate the runfiles directory
    # Bazel sets RUNFILES_DIR or we can search relative to __file__
    runfiles_dir = os.environ.get("RUNFILES_DIR")
    if runfiles_dir:
        base_dir = Path(runfiles_dir)
    else:
        # Fallback when running without sandboxing environment variables
        base_dir = Path(__file__).parent.parent

    # Look for the external pyrefly repository directory in runfiles
    exe_name = "pyrefly.exe" if sys.platform == "win32" else "pyrefly"

    found_bin_dir = None
    # We walk the runfiles tree looking for 'bin/pyrefly.exe' or 'bin/pyrefly'
    for root, _dirs, files in os.walk(base_dir):
        if exe_name in files:
            p = Path(root)
            if p.name == "bin":
                found_bin_dir = p
                break
            elif not found_bin_dir:
                # Fallback to any directory containing the executable
                found_bin_dir = p

    if found_bin_dir:
        # Add the binary directory to PATH so the python code subprocess.run can locate it
        os.environ["PATH"] = str(found_bin_dir.resolve()) + os.pathsep + os.environ.get("PATH", "")


def change_to_workspace() -> None:
    # When running under 'bazel run', Bazel sets BUILD_WORKSPACE_DIRECTORY to the actual host workspace path.
    # Changing the working directory ensures pyrefly runs relative to the actual workspace code, not the sandbox.
    workspace_dir = os.environ.get("BUILD_WORKSPACE_DIRECTORY")
    if workspace_dir:
        os.chdir(workspace_dir)


if __name__ == "__main__":
    setup_bin_path()
    change_to_workspace()
    sys.argv[0] = "pyrefly"
    runpy.run_module("pyrefly", run_name="__main__")
