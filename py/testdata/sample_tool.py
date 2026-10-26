#!/usr/bin/env python3
"""Test-only Python script for wrapper/launcher behavior verification."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def main() -> None:
    if "--exit-code" in sys.argv:
        idx = sys.argv.index("--exit-code")
        if idx + 1 < len(sys.argv):
            sys.exit(int(sys.argv[idx + 1]))
        sys.exit(1)

    payload = {
        "cwd": str(Path.cwd().resolve()),
        "argv": sys.argv[1:],
        "file": str(Path(__file__).resolve()),
        "path": os.environ.get("PATH", ""),
    }
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
