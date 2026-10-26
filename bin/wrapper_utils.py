#!/usr/bin/env python3
"""Shared execution helpers for Bazel CLI tool wrappers in bin/.

Provides `run_bazel_target()` to execute Bazel targets cleanly and hermetically
through the root `bazel` wrapper.

Usage Examples:
  Within wrapper scripts:
    from bin.wrapper_utils import run_bazel_target

    run_bazel_target("//tools:ruff", extra_args=sys.argv[1:])
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys


def run_bazel_target(target: str, extra_args: list[str] | None = None, resolve_paths: bool = True) -> None:
    """Run a Bazel target via the local bazel.py wrapper.

    Args:
        target: The Bazel target to run (e.g. //tools:ruff).
        extra_args: Additional arguments forwarded after `--` to the target.
        resolve_paths: If True, any file arguments following a `--` separator
            are resolved to absolute paths. This is needed for tools like ruff
            that are invoked by prek with workspace-relative file paths.
    """
    bin_dir = pathlib.Path(__file__).parent
    bazel_py = str(bin_dir / "bazel.py")
    cmd = [sys.executable, bazel_py, "run", target, "--"]

    if extra_args:
        if resolve_paths and "--" in extra_args:
            sep_idx = extra_args.index("--")
            cmd.extend(extra_args[: sep_idx + 1])
            cmd.extend(str(pathlib.Path(f).resolve()) for f in extra_args[sep_idx + 1 :])
        else:
            cmd.extend(extra_args)

    if sys.platform != "win32":
        os.execvp(sys.executable, cmd)
    else:
        sys.exit(subprocess.run(cmd, check=False).returncode)
