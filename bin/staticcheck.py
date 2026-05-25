#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.resolve()))

from bin.wrapper_utils import _clean_path_for_target


def main() -> None:
    # Forward all command line arguments directly to staticcheck
    # If no files/packages are specified, default to checking the Go application packages (go/calculator/...)
    args = sys.argv[1:]
    if not args:
        args = ["./go/calculator/..."]

    workspace_root = Path(__file__).parent.parent.resolve()

    # 1. Compile the staticcheck tool hermetically using our bazel.py wrapper
    bazel_py = workspace_root / "bin" / "bazel.py"
    subprocess.run([sys.executable, str(bazel_py), "build", "//tools:staticcheck"], check=True)

    # 2. Locate the compiled binary under the bazel-bin directory
    bin_name = "staticcheck.exe" if sys.platform == "win32" else "staticcheck"
    staticcheck_bin = None

    # Attempt to locate dynamically under bazel-bin/external/ to handle any Bzlmod variations
    bazel_bin_dir = workspace_root / "bazel-bin" / "external"
    if bazel_bin_dir.exists():
        for p in bazel_bin_dir.glob("**/staticcheck_/" + bin_name):
            staticcheck_bin = p
            break

    # Fallback to the expected path if the dynamic search finds nothing
    if not staticcheck_bin:
        staticcheck_bin = (
            workspace_root
            / "bazel-bin"
            / "external"
            / "gazelle++go_deps+co_honnef_go_tools"
            / "cmd"
            / "staticcheck"
            / "staticcheck_"
            / bin_name
        )

    if not staticcheck_bin.exists():
        print(f"Error: Could not locate compiled staticcheck binary at {staticcheck_bin}", file=sys.stderr)
        sys.exit(1)

    # 3. Clean the PATH environment variable to prepend the native hermetic Go SDK
    # and remove recursive Bazel wrappers.
    _clean_path_for_target()

    # 4. Run the staticcheck binary natively in the current working directory (workspace root)
    result = subprocess.run([str(staticcheck_bin), *args], check=False)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
