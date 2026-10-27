---
trigger: always_on
---

# List of Tools to use in the Repository

> **Important**: Never invoke, document, or reference tools with the `bin/` path prefix (e.g. `bin/bazel`, `bin/ruff`). All tools are placed on the `PATH` by mise; always invoke them by plain name.

// keep-sorted start block=yes case=no group_start_regex=# newline_separated=yes
## Bazel

The primary build tool the entire repository is built around.
ALWAYS invoke as `bazel`

## Buildifier

Standard Bazel lint/format tool.
ALWAYS invoke as `buildifier`

## Buildozer

Standard Bazel BUILD manipulation tool.
ALWAYS invoke as `buildozer`

## Gazelle

Standard Bazel BUILD auto-generation tool.
ALWAYS invoke as `gazelle`

## GitHub CLI

Official GitHub CLI tool (`gh`) for repository and PR management.

## MISE

Bootstrap tool to help get us started.
ONLY used to set up PATH and such so we can use bin/ wrappers.

## Prek

A better version of pre-commit which has poor support and slow updates.
ALWAYS invoke at `prek`

## Pyrefly

The default provided by Antigravity.
Should work better than pyright/pylance.
ALWAYS invoke at `pyrefly`

## Ruff

Linter for Python.
A de facto standard with possibility to extend.
ALWAYS invoke as `ruff`

// keep-sorted end