---
name: tutorial
description: Run the full tutorial pipeline (research, write, test, review, commit) from one or more GitHub issues. Issues are processed sequentially, one branch at a time.
disable-model-invocation: true
---

Read and follow `.cursor/agents/tutorial.md`.

Parse issue numbers from: $ARGUMENTS

Process each issue sequentially through the full pipeline. Use `Co-authored-by: Claude <noreply@anthropic.com>` for the commit trailer.
