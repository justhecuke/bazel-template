from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

EXPECTED_MANIFEST_PARTS = 2
MAX_PARENT_TRAVERSAL = 5


def _find_in_manifest(subpath: str, probe_file: str) -> Path | None:
    manifest = os.environ.get("RUNFILES_MANIFEST_FILE")
    if not manifest or not Path(manifest).exists():
        return None
    target_suffix = f"{subpath}/{probe_file}".replace("\\", "/")
    with Path(manifest).open(encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(" ", 1)
            if len(parts) == EXPECTED_MANIFEST_PARTS and parts[0].endswith(target_suffix):
                return Path(parts[1]).parent
    return None


def _find_on_disk(subpath: str, probe_file: str) -> Path | None:
    current = Path(__file__).resolve().parent
    sub_name = Path(subpath).name
    for _ in range(MAX_PARENT_TRAVERSAL):
        for candidate in [current / subpath, current / sub_name]:
            if candidate.is_dir() and (candidate / probe_file).exists():
                return candidate
        current = current.parent
    for candidate in [Path.cwd() / subpath, Path.cwd() / sub_name]:
        if candidate.is_dir() and (candidate / probe_file).exists():
            return candidate
    return None


def find_runfile_dir(subpath: str, probe_file: str) -> Path:
    """Locate a directory both inside Bazel runfiles and standalone."""
    runfiles_dir = os.environ.get("RUNFILES_DIR")
    if runfiles_dir:
        for prefix in ["_main", "bazel_template"]:
            candidate = Path(runfiles_dir) / prefix / subpath
            if candidate.is_dir():
                return candidate

    manifest_match = _find_in_manifest(subpath, probe_file)
    if manifest_match:
        return manifest_match

    disk_match = _find_on_disk(subpath, probe_file)
    if disk_match:
        return disk_match

    raise FileNotFoundError(f"Could not locate {subpath} directory from test environment")


def get_bin_dir() -> Path:
    return find_runfile_dir("bin", "bazel.py")


def get_testdata_dir() -> Path:
    return find_runfile_dir("py/testdata", "sample_tool.py")


class WrapperArchitectureTest(unittest.TestCase):
    """Regression tests preventing architectural regressions, anti-patterns, and rule violations in bin/."""

    def setUp(self) -> None:
        self.bin_dir = get_bin_dir()
        self.bin_py_files = [f for f in self.bin_dir.glob("*.py") if f.name != "__init__.py"]
        self.assertGreater(len(self.bin_py_files), 5, "Failed to discover bin/*.py files")

    def test_syntax_validity_all_wrappers(self) -> None:
        """Every python script in bin/ must be valid, parseable Python syntax."""
        for py_file in self.bin_py_files:
            with self.subTest(file=py_file.name):
                content = py_file.read_text(encoding="utf-8")
                try:
                    ast.parse(content, filename=str(py_file))
                except SyntaxError as e:
                    self.fail(f"Syntax error in {py_file.name}: {e}")

    def test_no_output_scraping_or_ad_hoc_globbing(self) -> None:
        """Wrappers must NOT scrape bazel-bin, bazel-out, or external directories.

        Regression check against find_bazel_bin, find_hermetic_go_sdk, or custom
        filesystem probing that bypasses hermetic Bazel execution.
        """
        # All files in bin/ must never define or use these anti-pattern functions
        anti_pattern_identifiers = [
            "find_bazel_bin",
            "find_hermetic_go_sdk",
            "rules_go*go_sdk",
        ]

        for py_file in self.bin_py_files:
            content = py_file.read_text(encoding="utf-8")
            for pattern in anti_pattern_identifiers:
                with self.subTest(file=py_file.name, pattern=pattern):
                    self.assertNotIn(
                        pattern,
                        content,
                        f"Found forbidden output-scraping function/pattern '{pattern}' in {py_file.name}. "
                        "Wrappers must execute tools via Bazel, not by probing internal output trees.",
                    )

        # Tool wrappers (excluding the root bazel.py wrapper itself) must not inspect bazel-out/bazel-bin
        tool_wrappers = [f for f in self.bin_py_files if f.name not in ("bazel.py",)]
        for py_file in tool_wrappers:
            content = py_file.read_text(encoding="utf-8")
            for pattern in ["bazel-out", "bazel-bin"]:
                with self.subTest(file=py_file.name, pattern=pattern):
                    self.assertNotIn(
                        pattern,
                        content,
                        f"Found forbidden output-directory reference '{pattern}' in tool wrapper {py_file.name}.",
                    )

    def test_no_manual_goroot_or_toolchain_overrides(self) -> None:
        """Wrappers must NOT manually override GOROOT or mutate PATH to bypass toolchains.

        Toolchains must be managed hermetically by Bazel, not by wrapper scripts.
        """
        for py_file in self.bin_py_files:
            content = py_file.read_text(encoding="utf-8")
            with self.subTest(file=py_file.name):
                self.assertNotIn(
                    'env["GOROOT"]',
                    content,
                    f"{py_file.name} manually overrides GOROOT. Let rules_go manage toolchains.",
                )

    def test_cli_tools_delegate_to_run_bazel_target(self) -> None:
        """Standard CLI wrappers must delegate to run_bazel_target.

        Regression check against wrappers running raw subprocesses instead of Bazel.
        """
        expected_delegating_wrappers = {
            "buildifier.py",
            "buildozer.py",
            "gazelle.py",
            "go.py",
            "goimports.py",
            "pyrefly.py",
            "ruff.py",
            "staticcheck.py",
            "update_manifest.py",
        }

        for filename in expected_delegating_wrappers:
            py_file = self.bin_dir / filename
            if not py_file.exists():
                continue

            with self.subTest(wrapper=filename):
                content = py_file.read_text(encoding="utf-8")
                self.assertIn(
                    "run_bazel_target",
                    content,
                    f"{filename} must delegate execution via run_bazel_target.",
                )

    def test_bazel_wrapper_working_directory_preservation(self) -> None:
        """bin/bazel.py must NOT unconditionally force cwd changes to the workspace root.

        Unconditionally forcing cwd to workspace root breaks relative target resolution (e.g.
        running 'bazel build :calculator' from within go/calculator/).
        """
        bazel_py = self.bin_dir / "bazel.py"
        content = bazel_py.read_text(encoding="utf-8")
        self.assertNotIn(
            "@in_workspace_root",
            content,
            "bin/bazel.py must not decorate main() with @in_workspace_root, as this breaks relative targets.",
        )
        self.assertNotIn(
            "in_workspace_root",
            content,
            "bin/bazel.py must not import or use in_workspace_root.",
        )

    def test_bazel_venv_anchored_to_workspace_root(self) -> None:
        """bin/bazel.py must anchor venv_dir to the workspace root, not cwd."""
        bazel_py = self.bin_dir / "bazel.py"
        content = bazel_py.read_text(encoding="utf-8")
        self.assertIn(
            '.venv"',
            content,
        )
        # Verify it resolves relative to __file__, not just Path(".venv")
        self.assertNotIn(
            'venv_dir = Path(".venv")',
            content,
            "bin/bazel.py must anchor .venv to workspace root using __file__, not relative Path('.venv').",
        )

    def test_wrapper_triplet_integrity(self) -> None:
        """Every CLI tool in bin/ must have matching POSIX and Windows launchers conforming to templates."""
        cli_tool_names = [f.stem for f in self.bin_py_files if f.name not in ("wrapper_utils.py",)]
        self.assertGreater(len(cli_tool_names), 8, "Expected at least 9 CLI tools in bin/")

        for tool in cli_tool_names:
            with self.subTest(tool=tool):
                # 1. POSIX launcher (extensionless)
                posix_launcher = self.bin_dir / tool
                self.assertTrue(
                    posix_launcher.exists(),
                    f"Missing POSIX launcher for {tool}: expected {posix_launcher}",
                )
                posix_content = posix_launcher.read_text(encoding="utf-8").strip()
                self.assertTrue(
                    posix_content.startswith("#!/usr/bin/env bash"),
                    f"{tool} POSIX launcher must start with '#!/usr/bin/env bash'",
                )
                expected_exec = f'exec python3 "$(dirname "$0")/{tool}.py" "$@"'
                self.assertIn(
                    expected_exec,
                    posix_content,
                    f"{tool} POSIX launcher must contain: {expected_exec}",
                )

                # 2. Windows launcher (.cmd)
                cmd_launcher = self.bin_dir / f"{tool}.cmd"
                self.assertTrue(
                    cmd_launcher.exists(),
                    f"Missing Windows launcher for {tool}: expected {cmd_launcher}",
                )
                cmd_content = cmd_launcher.read_text(encoding="utf-8").strip()
                self.assertIn(
                    "@echo off",
                    cmd_content,
                    f"{tool}.cmd must contain '@echo off'",
                )
                expected_cmd_exec = f'python "%~dp0{tool}.py" %*'
                self.assertIn(
                    expected_cmd_exec,
                    cmd_content,
                    f"{tool}.cmd must invoke Python with quoted path: {expected_cmd_exec}",
                )
                # Disallow unquoted %~dp0 to prevent whitespace path bugs
                unquoted_pattern = f"%~dp0\\{tool}.py"
                self.assertNotIn(
                    unquoted_pattern,
                    cmd_content,
                    f"{tool}.cmd must not contain unquoted '{unquoted_pattern}'",
                )


class LauncherExecutionBehaviorTest(unittest.TestCase):
    """Execution tests verifying launcher behavior, argument forwarding, and environment preconditions."""

    def setUp(self) -> None:
        self.testdata_dir = get_testdata_dir()
        self.sample_py = self.testdata_dir / "sample_tool.py"
        self.sample_sh = self.testdata_dir / "sample_tool"
        self.sample_cmd = self.testdata_dir / "sample_tool.cmd"

        self.assertTrue(self.sample_py.exists(), f"Missing {self.sample_py}")
        self.assertTrue(self.sample_sh.exists(), f"Missing {self.sample_sh}")
        self.assertTrue(self.sample_cmd.exists(), f"Missing {self.sample_cmd}")

    def _get_execution_commands(self) -> list[tuple[str, list[str]]]:
        """Determine which launchers can be executed in the current environment."""
        cmds: list[tuple[str, list[str]]] = []

        if sys.platform == "win32":
            cmd_exe = os.environ.get("COMSPEC", "cmd.exe")
            cmds.append(("windows_cmd", [cmd_exe, "/c", str(self.sample_cmd)]))
            bash_exe = shutil.which("bash")
            python3_exe = shutil.which("python3")
            if bash_exe and python3_exe:
                cmds.append(("posix_bash_on_win", [bash_exe, str(self.sample_sh)]))
        else:
            cmds.append(("posix_bash", ["bash", str(self.sample_sh)]))

        return cmds

    def _get_test_env(self) -> dict[str, str]:
        env = os.environ.copy()
        py_exe = shutil.which("python") or shutil.which("python3") or sys.executable
        if py_exe:
            py_dir = str(Path(py_exe).parent)
            env["PATH"] = f"{py_dir}{os.pathsep}{env.get('PATH', '')}"
        return env

    def test_working_directory_preservation(self) -> None:
        """Launchers must preserve CWD, satisfying precondition required by tools like ruff and buildifier."""
        for launcher_type, base_cmd in self._get_execution_commands():
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = Path(tmp_dir).resolve()
                res = subprocess.run(
                    base_cmd,
                    cwd=str(tmp_path),
                    env=self._get_test_env(),
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(
                    res.returncode,
                    0,
                    f"[{launcher_type}] Launcher failed with code {res.returncode}. Stderr: {res.stderr}",
                )
                data = json.loads(res.stdout)
                self.assertEqual(
                    Path(data["cwd"]).resolve(),
                    tmp_path,
                    f"[{launcher_type}] CWD was not preserved",
                )

    def test_argument_forwarding_and_quoting(self) -> None:
        """Launchers must forward arguments verbatim, including spaces and flags."""
        test_args = [
            "--flag",
            "value with spaces",
            "-mode=fix",
            "--",
            "dir/file with space.txt",
        ]

        for launcher_type, base_cmd in self._get_execution_commands():
            with self.subTest(launcher=launcher_type):
                res = subprocess.run(
                    [*base_cmd, *test_args],
                    env=self._get_test_env(),
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(
                    res.returncode,
                    0,
                    f"[{launcher_type}] Launcher failed with code {res.returncode}. Stderr: {res.stderr}",
                )
                data = json.loads(res.stdout)
                self.assertEqual(
                    data["argv"],
                    test_args,
                    f"[{launcher_type}] Arguments were not forwarded verbatim",
                )

    def test_exit_code_propagation(self) -> None:
        """Launchers must propagate non-zero exit codes from Python."""
        for launcher_type, base_cmd in self._get_execution_commands():
            with self.subTest(launcher=launcher_type):
                res = subprocess.run(
                    [*base_cmd, "--exit-code", "42"],
                    env=self._get_test_env(),
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(
                    res.returncode,
                    42,
                    f"[{launcher_type}] Launcher returned {res.returncode}, expected 42",
                )

    def test_script_location_resolution(self) -> None:
        """Launchers must anchor __file__ to their own directory, not CWD."""
        for launcher_type, base_cmd in self._get_execution_commands():
            with tempfile.TemporaryDirectory() as tmp_dir:
                res = subprocess.run(
                    base_cmd,
                    cwd=tmp_dir,
                    env=self._get_test_env(),
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
                data = json.loads(res.stdout)
                self.assertEqual(
                    Path(data["file"]).resolve(),
                    self.sample_py.resolve(),
                    f"[{launcher_type}] Script file location did not resolve to sample_tool.py",
                )


class WrapperUtilsLogicTest(unittest.TestCase):
    """Unit tests verifying wrapper_utils.py argument handling."""

    def test_path_resolution_after_double_dash(self) -> None:
        """run_bazel_target logic must resolve file paths after '--' to absolute paths."""
        extra_args = ["-lint", "fix", "--", "BUILD.bazel", "MODULE.bazel"]
        resolve_paths = True

        cmd: list[str] = ["python", "bazel.py", "run", "//tools:buildifier", "--"]
        if extra_args:
            if resolve_paths and "--" in extra_args:
                sep_idx = extra_args.index("--")
                cmd.extend(extra_args[: sep_idx + 1])
                cmd.extend(str(Path(f).resolve()) for f in extra_args[sep_idx + 1 :])
            else:
                cmd.extend(extra_args)

        self.assertEqual(cmd[5], "-lint")
        self.assertEqual(cmd[6], "fix")
        self.assertEqual(cmd[7], "--")
        # Ensure arguments following '--' became absolute paths
        self.assertTrue(Path(cmd[8]).is_absolute(), f"Expected absolute path: {cmd[8]}")
        self.assertTrue(Path(cmd[9]).is_absolute(), f"Expected absolute path: {cmd[9]}")

    def test_no_double_dash_leaves_args_untouched(self) -> None:
        """When '--' is not present in extra_args, arguments must be preserved as-is."""
        extra_args = ["version"]
        cmd: list[str] = ["python", "bazel.py", "run", "@rules_go//go", "--"]
        cmd.extend(extra_args)
        self.assertEqual(cmd, ["python", "bazel.py", "run", "@rules_go//go", "--", "version"])


if __name__ == "__main__":
    unittest.main()
