#!/usr/bin/env python3
from __future__ import annotations

import os
import pathlib
import subprocess
import sys


def resolve_bazel_path() -> str:
    """Locate the bazel.py wrapper script relative to the current script."""
    bin_dir = pathlib.Path(__file__).parent
    return str(bin_dir / "bazel.py")


def _filter_path_and_find_workspace(path_parts: list[str]) -> tuple[list[str], pathlib.Path | None]:
    """Filters out the local wrapper bin directory and finds workspace root."""
    cleaned_parts = []
    workspace_root = None
    for part in path_parts:
        if not part.strip():
            continue
        try:
            part_path = pathlib.Path(part).resolve()
            if part_path.name == "bin" and (part_path / "bazel.py").exists():
                workspace_root = part_path.parent
                continue
        except Exception:
            pass
        cleaned_parts.append(part)
    return cleaned_parts, workspace_root


def _find_native_go_sdk_bin(workspace_root: pathlib.Path) -> pathlib.Path | None:
    """Locates the native, un-wrapped Go SDK bin directory inside the runner runfiles."""
    runner_dir = workspace_root / "bazel-bin" / "external" / "rules_go+" / "go" / "tools" / "go_bin_runner" / "bin"
    if not runner_dir.exists():
        return None

    # Support both Windows and Unix runfiles directory layouts
    for runfiles_name in ["go.exe.runfiles", "go.runfiles"]:
        runfiles_dir = runner_dir / runfiles_name
        if runfiles_dir.exists():
            # Dynamically find the Go SDK subdirectory under runfiles
            for path in runfiles_dir.iterdir():
                if "go_sdk" in path.name and (path / "bin").exists():
                    return path / "bin"
    return None


def _clean_path_for_target() -> None:
    if "PATH" not in os.environ:
        return

    # Filter out the local bin directory from the PATH of the spawned Bazel target.
    # This prevents recursive wrapper execution (e.g. goimports invoking bin/go,
    # which recursively calls Bazel and triggers lock errors).
    path_parts = os.environ["PATH"].split(os.pathsep)
    cleaned_parts, workspace_root = _filter_path_and_find_workspace(path_parts)

    # Locate and prepend the native hermetic Go SDK binary directory (inside go_bin_runner's runfiles)
    # to the PATH of the spawned target. This completely prevents recursive Bazel executions.
    if workspace_root:
        go_sdk_bin = _find_native_go_sdk_bin(workspace_root)

        # Fall back to the runner_dir if the native Go SDK has not been extracted/built yet
        if go_sdk_bin:
            go_path = go_sdk_bin
        else:
            go_path = workspace_root / "bazel-bin" / "external" / "rules_go+" / "go" / "tools" / "go_bin_runner" / "bin"

        if go_path.exists():
            cleaned_parts.insert(0, str(go_path.resolve()))

    os.environ["PATH"] = os.pathsep.join(cleaned_parts)


def run_bazel_target(target: str, extra_args: list[str] | None = None, resolve_paths: bool = True) -> None:
    """
    Runs a Bazel target using the local bazel.py wrapper.

    Args:
        target: The Bazel target to run (e.g., //tools:ruff).
        extra_args: List of additional arguments to pass to the target.
        resolve_paths: If True, treats arguments after '--' as files and resolves them to absolute paths.
    """
    bazel_py = resolve_bazel_path()
    cmd = [sys.executable, bazel_py, "run", target, "--"]

    args = []
    if extra_args:
        has_sep = "--" in extra_args
        if resolve_paths and has_sep:
            sep_idx = extra_args.index("--")
            # Keep everything up to and including the separator
            args.extend(extra_args[: sep_idx + 1])
            # Resolve every argument after the separator to an absolute path
            args.extend([str(pathlib.Path(f).resolve()) for f in extra_args[sep_idx + 1 :]])
        else:
            args.extend(extra_args)

    cmd.extend(args)

    _clean_path_for_target()

    if sys.platform != "win32":
        os.execvp(sys.executable, cmd)
    else:
        sys.exit(subprocess.run(cmd, check=False).returncode)
