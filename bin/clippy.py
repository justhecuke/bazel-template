#!/usr/bin/env python3
"""Hermetic Clippy CLI wrapper for Rust static analysis and linting.

Usage Examples:
  clippy
  clippy //rs/...
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Only modify sys.path if we are running manually (not via bazel run/test)
if "BUILD_WORKSPACE_DIRECTORY" not in os.environ or "bin.wrapper_utils" not in sys.modules:
    sys.path.append(str(Path(__file__).parent.parent.resolve()))

from bin.wrapper_utils import run_bazel_target


def main() -> None:
    targets = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
    flags = [arg for arg in sys.argv[1:] if arg.startswith("-")]

    if not targets:
        targets = ["//..."]

    extra_args = [
        "--aspects=@rules_rust//rust:defs.bzl%rust_clippy_aspect",
        "--output_groups=+clippy_checks",
        *flags,
        *targets[:-1],
    ]

    run_bazel_target(
        targets[-1],
        extra_args=extra_args,
        command="build",
    )


if __name__ == "__main__":
    main()
