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


def _clean_path_for_target() -> None:
    if "PATH" not in os.environ:
        return

    # Filter out the local bin directory from the PATH of the spawned Bazel target.
    # This prevents recursive wrapper execution (e.g. goimports invoking bin/go,
    # which recursively calls Bazel and triggers lock errors).
    path_parts = os.environ["PATH"].split(os.pathsep)
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

    # Prepend the hermetic Go binary path if it exists to allow Go tools (like goimports or staticcheck)
    # to invoke the hermetic Go compiler without hitting recursive wrapper execution or missing-system-go errors.
    if workspace_root:
        hermetic_go_dir = (
            workspace_root / "bazel-bin" / "external" / "rules_go+" / "go" / "tools" / "go_bin_runner" / "bin"
        )
        if hermetic_go_dir.exists():
            cleaned_parts.insert(0, str(hermetic_go_dir.resolve()))

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
