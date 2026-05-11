---
name: pr-review-cleanup
description: Clean up cluster resources created during a /pr-review session. Reads the cluster log, confirms with the human, then deletes in reverse order.
disable-model-invocation: true
---

Read and follow `.cursor/agents/pr-reviewer.md` for constraints.

Parse PR number from: $ARGUMENTS

Read the cluster log at `.cursor/output/pr-<number>-cluster.log`, show the resource list, ask for confirmation, then delete in reverse order.
