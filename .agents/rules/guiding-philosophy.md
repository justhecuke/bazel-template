---
trigger: always_on
---

# Agent Instructions for bazel-template

This repository adheres to a strict philosophy of **Bazel-driven hermeticity**. When acting as an AI assistant or performing automated tasks in this workspace, you must follow these rules.

## 0. Philosophy
- Bazel skeleton meant as a base for expansion by third parties.
- Be opinionated for simplicity.
- Use one tool for specific roles.
- Use automated tools to enforce consistency such as:
  - lint
  - static analysis
  - testing
  - formatting
  - dependency management
  
## 1. Absolute Hermeticity
- Everything must be provisioned via Bazel (dependencies, tooling, formatting, execution).
- Do not use global package managers (`npm -g`, `pip install --global`, `apt-get`, `brew`, `choco`, etc.) to install any tools.
- Do not use system dependencies if a Bazel-managed hermetic toolchain or dependency exists.
- The repository must be entirely self-contained.

## 2. Tool Provisioning & Wrapper Scripts
- **Mise (`.mise.toml`) is ONLY used to set the `PATH`** (specifically appending `./bin` to the PATH). It must never be used to provision tools via the `[tools]` block.
- Any CLI tools (like `buildifier`, `buildozer`, Python formatters, linters) should be added as Bazel dependencies (e.g., `buildifier_prebuilt` in `MODULE.bazel`).
- To make these tools easily accessible, create wrapper scripts in the `bin/` directory. These wrappers should simply run the tool via Bazel, e.g., `bazel run //tools:<target> -- "$@"`.
- **Never invoke or document tools with the `bin/` prefix**: Because `mise` prepends `./bin` to `PATH`, all wrapper tools must ALWAYS be invoked, documented, and referred to by their bare command names (e.g., `bazel`, `buildifier`, `ruff`, `update_ide_paths`), NEVER as `bin/<tool>` or `python bin/<tool>.py`.

## 3. Python Bootstrap Isolation
- Bazel's `rules_python` relies on a system Python for its initial bootstrap phase. To prevent global system Python packages from leaking into Bazel and breaking hermeticity, Bazel must always run inside a clean, isolated Python virtual environment.
- The `bin/bazel` and `bin/bazel.cmd` wrapper scripts automatically create a clean `.venv` and activate it before forwarding commands to the real `bazel.exe` or `bazelisk`.
- Do not bypass these wrappers unless absolutely necessary. If you must invoke bazel directly, ensure the `.venv` is activated.
- Never commit `.venv` or any other virtual environments to source control.

## 4. Cross-Platform Support
- Always consider both Unix/macOS and Windows environments. 
- Use cross-platform Python scripts (`.py`) for wrappers in `bin/` rather than sprawling platform-specific shell scripts (`.cmd`, `.bat`, `.sh`).
- Use path-agnostic operations whenever possible (e.g., standard forward slashes in Bazel files).