---
name: master-review
description: Final gate before human review (not part of /pipeline). Supports one branch, multiple branches, discovery, or tutorial slug.
version: "1.0"
disable-model-invocation: true
---

# Master Review

Read and follow `.cursor/agents/tutorial-master-reviewer.md`.

**Invocation:** `/master-review [branch1] [branch2] ...` -- accepts branch names, a tutorial slug (e.g. `cloning-vms`), or no argument for discovery mode. See persona for argument parsing details.
