#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.resolve()))

from bin.wrapper_utils import run_bazel_target


def main() -> None:
    # Run @rules_go//go target with all arguments
    run_bazel_target("@rules_go//go", extra_args=sys.argv[1:])


if __name__ == "__main__":
    main()
