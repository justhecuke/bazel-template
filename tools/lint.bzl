load("@aspect_rules_lint//lint:ruff.bzl", "lint_ruff_aspect")

ruff = lint_ruff_aspect(
    binary = "//tools:ruff",
    configs = ["//:pyproject.toml"],
)
