#!/usr/bin/env python3
"""Hermetic Go CLI wrapper delegating to Bazel's rules_go toolchain.

Usage Examples:
  Standalone:
    bin/go test ./...

  Via Bazel:
    bazel run @rules_go//go -- test ./...
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
    # Run @rules_go//go target with all arguments
    run_bazel_target("@rules_go//go", extra_args=sys.argv[1:])


if __name__ == "__main__":
    main()
