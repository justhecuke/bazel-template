#!/usr/bin/env python3
"""Gazelle Python manifest update script.

Regenerates the `gazelle_python.yaml` manifest containing package module mappings.

Usage Examples:
  Standalone:
    bin/update_manifest

  Via Bazel:
    bazel run //:gazelle_python_manifest_generator.update
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Only modify sys.path if we are running manually (not via bazel run/test)
if "BUILD_WORKSPACE_DIRECTORY" not in os.environ or "bin.wrapper_utils" not in sys.modules:
    sys.path.append(str(Path(__file__).parent.parent.resolve()))

from bin.wrapper_utils import run_bazel_target


def main() -> None:
    run_bazel_target("//:gazelle_python_manifest_generator.update", extra_args=sys.argv[1:])


if __name__ == "__main__":
    main()
