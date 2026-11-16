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


def run_bazel_target(
    target: str,
    extra_args: list[str] | None = None,
    command: str = "run",
) -> None:
    """Run a Bazel target via the local bazel.py wrapper.

    Args:
        target: The Bazel target or target pattern (e.g. //tools:ruff or //...).
        extra_args: Additional arguments forwarded verbatim to the target.
        command: Bazel command to invoke ('run' or 'build'). Defaults to 'run'.
    """
    bin_dir = pathlib.Path(__file__).parent
    bazel_py = str(bin_dir / "bazel.py")

    if command == "run":
        cmd = [sys.executable, bazel_py, "run", target, "--"]
        if extra_args:
            cmd.extend(extra_args)
    else:
        cmd = [sys.executable, bazel_py, command]
        if extra_args:
            cmd.extend(extra_args)
        cmd.append(target)

    if sys.platform != "win32":
        os.execvp(sys.executable, cmd)
    else:
        sys.exit(subprocess.run(cmd, check=False).returncode)
