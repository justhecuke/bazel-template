---
description: Finalize a GitHub PR from Local Changes
---

# Finalize a GitHub PR from Local Changes

## Inputs

1. Optional local git branch name.
   If not provided, use the current branch.

## Prerequisites

- Branch is not the trunk, main, or default branch
- Branch is a descendant of the trunk, main, or default branch
- Branch does not have a merged or finished PR

## Workflow

1. Push local branch.
   - If there is no PR for the branch, create a PR and create a title and description according to the contents of the PR.
2. Track CI for the PR with at least 1 minute between checks.
   - Every time a check return a non-finished status, increase the polling period by at least double.
   - If all checks pass, there is no work to be done and you can finish.
   - If there is at least one failure, continue to step (3).
3. Analyze failure, determine a fix, perform the fix.
   - Ask the human if a complex design decision requiring engineering tradeoffs is identified.
   - Fully automate simple fixes or changes that are objectively superior to what currently exists.
4. Commit and Push changes.
5. Go to (2)

### Tools

- Use the GitHub MCP server tools, especially to create and monitor the PR.

## End State

- PR has all CI checks passing