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

    # Normalize requirements.txt to LF to prevent OS-specific line ending differences
    # from altering the gazelle_python.yaml integrity hash.
    req_file = Path("requirements.txt")
    if req_file.exists():
        content = req_file.read_bytes().replace(b"\r\n", b"\n")
        req_file.write_bytes(content)


if __name__ == "__main__":
    main()
