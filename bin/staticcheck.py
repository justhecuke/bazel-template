#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.resolve()))

from bin.wrapper_utils import run_bazel_target


def main() -> None:
    # Forward all command line arguments directly to //tools:staticcheck
    # If no files/packages are specified, default to checking the Go application packages (go/calculator/...)
    args = sys.argv[1:]
    if not args:
        args = ["go/calculator/..."]

    run_bazel_target(
        "//tools:staticcheck",
        extra_args=args,
        resolve_paths=False,
    )


if __name__ == "__main__":
    main()
