---
name: pr-review
description: Review one or more PRs from the upstream repo. Supports batch mode with automatic cluster cleanup. Detects previous review logs for follow-up mode.
version: "1.0"
disable-model-invocation: true
---

# PR Review

Read and follow `.cursor/agents/pr-reviewer.md`.

**Invocation:** `/pr-review <number> [number2] ...` -- accepts one or more PR numbers (with or without `#`). Multiple numbers activate batch mode.

**Previous review detection:** Before fetching a PR, check for `.cursor/output/pr-<number>.log`. If found, rename to `-previous.log` (with numeric suffix for older logs), parse findings, and pass them to the persona as context for follow-up review mode.
