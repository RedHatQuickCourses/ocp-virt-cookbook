---
name: pr-review-cleanup
description: Clean up cluster resources created during a /pr-review session. Reads the cluster log, confirms with the human, then deletes in reverse order.
version: "1.0"
disable-model-invocation: true
---

# PR Review Cleanup

Read and follow `.cursor/agents/pr-reviewer.md` for constraints.

**Invocation:** `/pr-review-cleanup <number>` -- the PR number identifies which cluster log to read (`.cursor/output/pr-<number>-cluster.log`).

**Workflow:**
1. Parse the cluster log for resource-creating commands (`oc apply`, `oc create`, `oc run`).
2. Show the human the resource list and ask for confirmation.
3. Delete in reverse order. Log cleanup commands to the same cluster log.
4. Never delete resources not in the log. Never delete cluster-wide resources without individual confirmation.
