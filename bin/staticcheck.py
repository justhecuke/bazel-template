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
    # Forward all command line arguments directly to honnef.co/go/tools/cmd/staticcheck@v0.5.1
    # If no files/packages are specified, default to checking the whole repository (./...)
    args = sys.argv[1:]
    if not args:
        args = ["./..."]

    run_bazel_target(
        "@rules_go//go",
        extra_args=["run", "honnef.co/go/tools/cmd/staticcheck@v0.6.0", *args],
        resolve_paths=False,
    )


if __name__ == "__main__":
    main()
