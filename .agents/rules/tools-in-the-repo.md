---
trigger: always_on
---

# List of Tools to use in the Repository

// keep-sorted start block=yes case=no group_start_regex=# newline_separated=yes
## Bazel

The primary build tool the entire repository is built around.

## Buildifier

Standard Bazel lint/format tool.

## Buildozer

Standard Bazel BUILD manipulation tool.

## Gazelle

Standard Bazel BUILD auto-generation tool.

## MISE

Bootstrap tool to help get us started.
ONLY used to set up PATH and such so we can use bin/ wrappers.

## Prek

A better version of pre-commit which has poor support and slow updates.

## Pyrefly

The default provided by Antigravity.
Should work better than pyright/pylance.

## Ruff

Linter for Python.
A de facto standard with possibility to extend.

// keep-sorted end