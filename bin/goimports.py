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

    extra_args = ["run", "golang.org/x/tools/cmd/goimports@v0.30.0"]
    if not has_w:
        extra_args.append("-w")
    extra_args.extend(resolved_args)

    # Invoke @rules_go//go target with the goimports command and absolute file paths
    # Set resolve_paths=False because we have already manually resolved them
    run_bazel_target("@rules_go//go", extra_args=extra_args, resolve_paths=False)


if __name__ == "__main__":
    main()
