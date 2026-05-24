#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path

# Only modify sys.path if we are running manually (not via bazel run/test)
if "BUILD_WORKSPACE_DIRECTORY" not in os.environ:
    sys.path.append(str(Path(__file__).parent.parent.resolve()))

from bin.wrapper_utils import run_bazel_target


def main() -> None:
    # Forward all command line arguments directly to the //tools:pyrefly target
    run_bazel_target("//tools:pyrefly", extra_args=sys.argv[1:])


if __name__ == "__main__":
    main()
