"""Run a bundled Bazel tool binary in the user's original working directory."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

EXPECTED_MANIFEST_PARTS = 2
MIN_ARGV_LEN = 2


def _resolve_runfile(rlocation_path: str) -> Path:
    """Resolve a Bazel rlocationpath via RUNFILES_MANIFEST_FILE or RUNFILES_DIR."""
    normalized = rlocation_path.replace("\\", "/")

    manifest_file = os.environ.get("RUNFILES_MANIFEST_FILE")
    if manifest_file:
        manifest_path = Path(manifest_file)
        if manifest_path.is_file():
            for line in manifest_path.read_text(encoding="utf-8").splitlines():
                parts = line.split(" ", 1)
                if len(parts) == EXPECTED_MANIFEST_PARTS and parts[0] == normalized:
                    return Path(parts[1])

    runfiles_dir = os.environ.get("RUNFILES_DIR")
    if runfiles_dir:
        candidate = Path(runfiles_dir) / normalized
        if candidate.exists():
            return candidate

    # Fallback: relative to this script's runfiles root
    fallback = Path(__file__).resolve().parent.parent / normalized
    if fallback.exists():
        return fallback

    raise FileNotFoundError(f"Could not locate runfile: {rlocation_path}")


def main() -> None:
    if len(sys.argv) < MIN_ARGV_LEN:
        print("Usage: run_in_cwd.py <tool_rlocationpath> [args...]", file=sys.stderr)
        sys.exit(1)

    tool_path = _resolve_runfile(sys.argv[1])
    tool_args = sys.argv[2:]

    working_dir = os.environ.get("BUILD_WORKING_DIRECTORY") or os.environ.get("BUILD_WORKSPACE_DIRECTORY")
    if working_dir:
        os.chdir(working_dir)

    if sys.platform != "win32":
        os.execv(str(tool_path), [str(tool_path), *tool_args])
    else:
        sys.exit(subprocess.run([str(tool_path), *tool_args], check=False).returncode)


if __name__ == "__main__":
    main()
