#!/usr/bin/env python3
"""Python pip requirements lockfile update script.

Compiles dependencies from `requirements.in` into `requirements.txt` via rules_python
and normalizes line endings to LF.

Usage Examples:
  Standalone:
    bin/update_requirements

  Via Bazel:
    bazel run //:requirements.update
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    workspace_root = Path(__file__).parent.parent.resolve()
    bazel_py = workspace_root / "bin" / "bazel.py"
    cmd = [sys.executable, str(bazel_py), "run", "//:requirements.update", "--", *sys.argv[1:]]
    res = subprocess.run(cmd, check=False)

    # Normalize requirements.txt to LF to prevent OS-specific line endings
    # from altering the gazelle_python.yaml integrity hash.
    req_file = workspace_root / "requirements.txt"
    if req_file.exists():
        content = req_file.read_bytes().replace(b"\r\n", b"\n")
        req_file.write_bytes(content)

    sys.exit(res.returncode)


if __name__ == "__main__":
    main()
