#!/usr/bin/env python3
"""Hermetic rustfmt CLI wrapper for Rust source formatting.

Usage Examples:
  rustfmt --edition 2021 -- rs/calculator.rs
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
    # Use the local alias defined in //tools:BUILD.bazel
    run_bazel_target("//tools:rustfmt", extra_args=sys.argv[1:], resolve_paths=True)


if __name__ == "__main__":
    main()
