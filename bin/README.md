# Repository Tool Wrappers (`bin/`)

This directory contains transparent wrapper scripts for developer tools used in the repository.

## Architecture

To provide a consistent cross-platform developer experience while maintaining hermetic Bazel execution, each CLI tool is structured as a **triplet**:

1. **`<tool>` (POSIX Bash Launcher)**:
   A lightweight shell script (`#!/usr/bin/env bash`) forwarding invocations to `python3 "$(dirname "$0")/<tool>.py" "$@"`.
2. **`<tool>.cmd` (Windows CMD Launcher)**:
   A batch script (`@echo off` / `python "%~dp0<tool>.py" %*`) enabling execution via Windows `PATH` / `PATHEXT`.
3. **`<tool>.py` (Cross-Platform Python Implementation)**:
   The actual tool logic delegating hermetically to Bazel targets via `wrapper_utils.py` (`run_bazel_target`) or standalone execution.

## Tool Roster

- `bazel`: Root wrapper bootstrapping isolated `.venv` before running Bazelisk/Bazel.
- `buildifier`: Linting and formatting for Bazel build files.
- `buildozer`: Batch edits for Bazel build files.
- `gazelle`: Automated generation of Bazel BUILD files for Go and Python.
- `go`: Hermetic Go toolchain driver.
- `goimports`: Automated Go import formatting.
- `pyrefly`: Static type checker for Python.
- `ruff`: High-performance Python linter and formatter.
- `staticcheck`: Static analysis for Go.
- `update_ide_paths`: Generates `pyrefly.toml` and `pyrightconfig.json` with external Bazel dependency paths.
- `update_manifest`: Regenerates `gazelle_python.yaml` package mapping.
- `update_requirements`: Compiles `requirements.in` to `requirements.txt`.

## Maintenance & Generation

<!-- TODO: Make the POSIX and Windows launchers templates that get expanded and put into the repository at rest with conformance tests. -->
