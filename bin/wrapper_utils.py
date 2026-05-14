#!/usr/bin/env python3
import os
import pathlib
import subprocess
import sys


def resolve_bazel_path():
    """Locate the bazel.py wrapper script relative to the current script."""
    bin_dir = pathlib.Path(__file__).parent
    return str(bin_dir / "bazel.py")


def run_bazel_target(target, extra_args=None, resolve_paths=True):
    """
    Runs a Bazel target using the local bazel.py wrapper.

    Args:
        target: The Bazel target to run (e.g., //tools:ruff).
        extra_args: List of additional arguments to pass to the target.
        resolve_paths: If True, treats arguments after '--' as files and resolves them to absolute paths.
    """
    bazel_py = resolve_bazel_path()
    cmd = [sys.executable, bazel_py, "run", target, "--"]

    args = []
    if extra_args:
        has_sep = "--" in extra_args
        if resolve_paths and has_sep:
            sep_idx = extra_args.index("--")
            # Keep everything up to and including the separator
            args.extend(extra_args[: sep_idx + 1])
            # Resolve every argument after the separator to an absolute path
            args.extend([str(pathlib.Path(f).resolve()) for f in extra_args[sep_idx + 1 :]])
        else:
            args.extend(extra_args)

    cmd.extend(args)

    if sys.platform != "win32":
        os.execvp(sys.executable, cmd)
    else:
        sys.exit(subprocess.run(cmd).returncode)
