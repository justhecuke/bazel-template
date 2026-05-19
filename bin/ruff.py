#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Only modify sys.path if we are running manually (not via bazel run/test)
if "BUILD_WORKSPACE_DIRECTORY" not in os.environ:
    sys.path.append(str(Path(__file__).parent.parent.resolve()))

from bin.wrapper_utils import run_bazel_target


def main():
    # Automatically locate and resolve the absolute path to pyproject.toml
    # to ensure the hermetic/sandboxed ruff execution in CI always uses our config.
    bin_dir = Path(__file__).parent.resolve()
    pyproject_toml = bin_dir.parent / "pyproject.toml"

    args = sys.argv[1:]
    if pyproject_toml.exists() and not any(arg.startswith("--config") for arg in args):
        # We need to insert the --config argument after 'check' or 'format'
        if args and args[0] in ("check", "format"):
            args.insert(1, f"--config={pyproject_toml.resolve()}")
        else:
            args.insert(0, f"--config={pyproject_toml.resolve()}")

    # Use the local alias defined in //tools:BUILD.bazel
    run_bazel_target("//tools:ruff", extra_args=args)


if __name__ == "__main__":
    main()
