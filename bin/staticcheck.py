#!/usr/bin/env python3
"""Hermetic staticcheck CLI wrapper for Go advanced static analysis.

Usage Examples:
  staticcheck ./...
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
    # Forward all command line arguments directly to staticcheck.
    # If no packages are specified, default to checking all Go packages in the repository.
    args = sys.argv[1:]
    if not args:
        args = ["./..."]

    run_bazel_target("//tools:staticcheck", extra_args=args, resolve_paths=False)


if __name__ == "__main__":
    main()
