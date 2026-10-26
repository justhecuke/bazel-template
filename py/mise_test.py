from __future__ import annotations

import os
import tomllib
import unittest
from pathlib import Path

EXPECTED_MANIFEST_PARTS = 2
MAX_PARENT_TRAVERSAL = 5


def get_mise_toml_path() -> Path:
    """Locate .mise.toml both inside Bazel runfiles and standalone."""
    # 1. Check RUNFILES_DIR
    runfiles_dir = os.environ.get("RUNFILES_DIR")
    if runfiles_dir:
        for candidate in [
            Path(runfiles_dir) / "_main" / ".mise.toml",
            Path(runfiles_dir) / "bazel_template" / ".mise.toml",
        ]:
            if candidate.is_file():
                return candidate

    # 2. Check RUNFILES_MANIFEST_FILE (Windows)
    manifest = os.environ.get("RUNFILES_MANIFEST_FILE")
    if manifest and Path(manifest).exists():
        with Path(manifest).open(encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(" ", 1)
                if len(parts) == EXPECTED_MANIFEST_PARTS and (
                    parts[0] == "_main/.mise.toml"
                    or parts[0] == "bazel_template/.mise.toml"
                    or parts[0].endswith("/.mise.toml")
                ):
                    return Path(parts[1])

    # 3. Walk upwards from __file__ to find repository root containing .mise.toml
    current = Path(__file__).resolve().parent
    for _ in range(MAX_PARENT_TRAVERSAL):
        candidate = current / ".mise.toml"
        if candidate.is_file():
            return candidate
        current = current.parent

    # 4. Check current working directory
    cwd_candidate = Path.cwd() / ".mise.toml"
    if cwd_candidate.is_file():
        return cwd_candidate

    raise FileNotFoundError("Could not locate .mise.toml from test environment")


class MiseConfigTest(unittest.TestCase):
    """Regression test ensuring .mise.toml strictly conforms to repository philosophy."""

    def setUp(self) -> None:
        self.mise_path = get_mise_toml_path()
        self.assertTrue(self.mise_path.exists(), f".mise.toml not found at {self.mise_path}")
        content = self.mise_path.read_text(encoding="utf-8")
        self.config = tomllib.loads(content)

    def test_no_tools_block(self) -> None:
        """Mise must NEVER be used to provision tools via a [tools] block."""
        self.assertNotIn(
            "tools",
            self.config,
            ".mise.toml must NOT contain a [tools] block. All tools must be provisioned hermetically via Bazel.",
        )

    def test_path_configuration(self) -> None:
        """Mise [env] must configure _.path to include './bin'."""
        self.assertIn(
            "env",
            self.config,
            ".mise.toml must contain an [env] table.",
        )
        env = self.config["env"]
        # In TOML, '_.path = ["./bin"]' under [env] parses as env["_"]["path"]
        underscore = env.get("_")
        self.assertIsInstance(
            underscore,
            dict,
            ".mise.toml [env] must specify '_.path'.",
        )
        path_list = underscore.get("path")
        self.assertIsInstance(
            path_list,
            list,
            ".mise.toml '_.path' must be a list of paths.",
        )
        self.assertIn(
            "./bin",
            path_list,
            ".mise.toml '_.path' list must include './bin'.",
        )


if __name__ == "__main__":
    unittest.main()
