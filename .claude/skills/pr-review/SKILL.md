---
name: pr-review
description: Review one or more PRs from the upstream repo. Supports batch mode with automatic cluster cleanup. Detects previous review logs for follow-up mode.
disable-model-invocation: true
---

Read and follow `.cursor/agents/pr-reviewer.md`.

Parse PR numbers from: $ARGUMENTS

Multiple numbers activate batch mode. Before fetching a PR, check for `.cursor/output/pr-<number>.log` for follow-up review mode.
