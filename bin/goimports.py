#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.resolve()))

from bin.wrapper_utils import run_bazel_target


def main() -> None:
    # Resolve all incoming file arguments to absolute paths manually
    resolved_args = []
    # Ensure -w (write back to file) is included by default for formatting
    has_w = False
    for arg in sys.argv[1:]:
        if arg == "-w":
            has_w = True
        # If it's a file/directory path, resolve it to an absolute path
        if not arg.startswith("-"):
            resolved_args.append(str(Path(arg).resolve()))
        else:
            resolved_args.append(arg)

    extra_args = []
    if not has_w:
        extra_args.append("-w")
    extra_args.extend(resolved_args)

    # Invoke //tools:goimports target
    run_bazel_target("//tools:goimports", extra_args=extra_args, resolve_paths=False)


if __name__ == "__main__":
    main()
