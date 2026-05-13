#!/usr/bin/env python3
import os
import subprocess
import sys


def main():
    # Call our bazel.py wrapper to ensure it runs inside the venv.
    bazel_py = os.path.join(os.path.dirname(__file__), "bazel.py")

    # If the caller provides a '--' separator, we treat everything after it as
    # a file path and resolve it to an absolute path. This ensures that even
    # if ruff is run from Bazel's sandbox, it can find local files.
    try:
        import pathlib

        sep_idx = sys.argv.index("--")
        flags = sys.argv[1:sep_idx]
        files = [str(pathlib.Path(f).resolve()) for f in sys.argv[sep_idx + 1 :]]
        extra_args = flags + (["--"] + files if files else [])
    except ValueError:
        # No '--' found, just pass everything through as is.
        extra_args = sys.argv[1:]

    # Use //tools:ruff which is an alias to the hermetic binary.
    cmd = [sys.executable, bazel_py, "run", "//tools:ruff", "--"] + extra_args

    if sys.platform != "win32":
        os.execvp(sys.executable, cmd)
    else:
        sys.exit(subprocess.run(cmd).returncode)


if __name__ == "__main__":
    main()
