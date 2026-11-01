#!/usr/bin/env python3
"""Hermetic Go CLI wrapper delegating to Bazel's rules_go toolchain.

Usage Examples:
  go test ./...
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# Only modify sys.path if we are running manually (not via bazel run/test)
if "BUILD_WORKSPACE_DIRECTORY" not in os.environ or "bin.wrapper_utils" not in sys.modules:
    sys.path.append(str(Path(__file__).parent.parent.resolve()))

from bin.wrapper_utils import run_bazel_target


def main() -> None:
    # When invoked as a subtool from another running Bazel process (e.g. staticcheck or goimports),
    # avoid re-invoking Bazel (which causes output-base lock deadlocks).
    # Instead, locate the hermetic Go binary directly in BUILD_EXECROOT.
    execroot = os.environ.get("BUILD_EXECROOT")
    if execroot:
        exe_name = "go.exe" if sys.platform == "win32" else "go"
        external_dir = Path(execroot) / "external"
        if external_dir.is_dir():
            for entry in external_dir.iterdir():
                if "rules_go" in entry.name and "go_sdk" in entry.name:
                    go_bin = entry / "bin" / exe_name
                    if go_bin.is_file():
                        sys.exit(subprocess.run([str(go_bin), *sys.argv[1:]], check=False).returncode)

    # Run @rules_go//go target with all arguments
    run_bazel_target("@rules_go//go", extra_args=sys.argv[1:])


if __name__ == "__main__":
    main()
