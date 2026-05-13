#!/usr/bin/env python3
"""
Wrapper to run hermetic buildifier via Bazel.
"""

import os
import pathlib
import sys
import subprocess


def main():
    # Call our bazel.py wrapper to ensure it runs inside the venv.
    bazel_py = os.path.join(os.path.dirname(__file__), "bazel.py")

    # If the caller provides a '--' separator, we treat everything after it as
    # a file path and resolve it to an absolute path. This is crucial for hooks
    # like prek/pre-commit because Bazel runs the tool in a sandbox where
    # relative paths are invalid.
    try:
        sep_idx = sys.argv.index("--")
        flags = sys.argv[1:sep_idx]
        files = [str(pathlib.Path(f).resolve()) for f in sys.argv[sep_idx + 1:]]
        extra_args = flags + (["--"] + files if files else [])
    except ValueError:
        # No '--' found, just pass everything through as is.
        extra_args = sys.argv[1:]

    cmd = [sys.executable, bazel_py, "run", "@buildifier_prebuilt//:buildifier", "--"] + extra_args

    if sys.platform != "win32":
        os.execvp(sys.executable, cmd)
    else:
        sys.exit(subprocess.run(cmd).returncode)


if __name__ == "__main__":
    main()
