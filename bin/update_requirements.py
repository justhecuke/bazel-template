#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Only modify sys.path if we are running manually (not via bazel run/test)
if "BUILD_WORKSPACE_DIRECTORY" not in os.environ:
    sys.path.append(str(Path(__file__).parent.parent.resolve()))

from bin.wrapper_utils import run_bazel_target


def main():
    run_bazel_target("//:requirements.update", extra_args=sys.argv[1:])


if __name__ == "__main__":
    main()
