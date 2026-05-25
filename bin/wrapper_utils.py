#!/usr/bin/env python3
from __future__ import annotations

import os
import pathlib
import subprocess
import sys


def _clean_path_for_bazel() -> None:
    """Remove the local bin/ wrapper directory from PATH before invoking Bazel.

    When prek runs hooks, it adds the workspace bin/ to PATH so that bare
    commands like `bazel` resolve to our wrapper. But if a tool invoked by
    `bazel run` then calls another binary (e.g. goimports calling `go`), it
    would hit our bin/go wrapper and recurse back into Bazel, causing lock
    contention. Stripping bin/ from PATH breaks that cycle.
    """
    if "PATH" not in os.environ:
        return

    bin_dir = pathlib.Path(__file__).parent.resolve()
    path_parts = os.environ["PATH"].split(os.pathsep)
    cleaned = [p for p in path_parts if p.strip() and pathlib.Path(p).resolve() != bin_dir]
    os.environ["PATH"] = os.pathsep.join(cleaned)


def run_bazel_target(target: str, extra_args: list[str] | None = None, resolve_paths: bool = True) -> None:
    """Run a Bazel target via the local bazel.py wrapper.

    Args:
        target: The Bazel target to run (e.g. //tools:ruff).
        extra_args: Additional arguments forwarded after `--` to the target.
        resolve_paths: If True, any file arguments following a `--` separator
            are resolved to absolute paths. This is needed for tools like ruff
            that are invoked by prek with workspace-relative file paths.
    """
    bin_dir = pathlib.Path(__file__).parent
    bazel_py = str(bin_dir / "bazel.py")
    cmd = [sys.executable, bazel_py, "run", target, "--"]

    if extra_args:
        if resolve_paths and "--" in extra_args:
            sep_idx = extra_args.index("--")
            cmd.extend(extra_args[: sep_idx + 1])
            cmd.extend(str(pathlib.Path(f).resolve()) for f in extra_args[sep_idx + 1 :])
        else:
            cmd.extend(extra_args)

    _clean_path_for_bazel()

    if sys.platform != "win32":
        os.execvp(sys.executable, cmd)
    else:
        sys.exit(subprocess.run(cmd, check=False).returncode)
