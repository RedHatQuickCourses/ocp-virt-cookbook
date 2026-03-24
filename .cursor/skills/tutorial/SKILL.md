---
name: tutorial
description: Run the full tutorial pipeline (research, write, test, review, commit) from one or more GitHub issues. Issues are processed sequentially, one branch at a time.
version: "1.0"
disable-model-invocation: true
---

# Tutorial

Read and follow `.cursor/agents/tutorial.md`.

**Invocation:** `/tutorial <issue> [issue2] ...` -- parse issue numbers from `45`, `#45`, `issue 45`, or comma/space-separated lists. Issues are processed sequentially. Each issue produces one branch with a finished tutorial.
