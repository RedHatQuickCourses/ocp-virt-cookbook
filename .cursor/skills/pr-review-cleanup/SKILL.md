---
name: pr-review-cleanup
description: Clean up cluster resources created during a /pr-review session. Reads the cluster log, lists resources created, asks for human confirmation, then deletes in reverse order. Logs all cleanup commands to the same cluster log. Use when the user invokes /pr-review-cleanup with a PR number after inspecting the cluster.
version: "1.0"
disable-model-invocation: true
---

# PR Review Cleanup

Clean up cluster resources created during a `/pr-review` session.

## Invocation

The user invokes this skill with: `/pr-review-cleanup <number>` or `/pr-review-cleanup #42`

The PR number tells the skill which cluster log to read for context.

## Workflow

1. Read the persona at `.cursor/agents/pr-reviewer.md` for constraints.
2. Read the cluster log at `.cursor/output/pr-<number>-cluster.log` to understand what resources were created during the review.
3. Parse the log for every `oc apply`, `oc create`, `oc run`, and similar resource-creating command. Build a list of resources (kind, name, namespace) that were created.
4. Show the human the list of resources to be deleted and ask for confirmation before proceeding.
5. After confirmation, delete resources in reverse order of creation (last created, first deleted). If a namespace was created specifically for the test, offer to delete the entire namespace instead of individual resources.
6. Log every cleanup command and its output to the same cluster log file (`.cursor/output/pr-<number>-cluster.log`) using the same timestamped format:
   ```
   [YYYY-MM-DD HH:MM:SS] $ <cleanup command>
   <output>
   ```
7. After cleanup, append a final entry:
   ```
   [YYYY-MM-DD HH:MM:SS] Cleanup complete. Resources deleted: <count>
   ```
8. Print a brief confirmation in chat: what was deleted, any resources that failed to delete.

## Constraints

- Uses the same KUBECONFIG as the `/pr-review` session (read it from the cluster log or ask the human).
- NEVER deletes resources that were NOT created during the review. Only delete what appears in the cluster log.
- NEVER deletes cluster-wide resources (nodes, CRDs, cluster roles) unless the human explicitly confirms each one individually.
- NEVER runs without human confirmation of the resource list.
- NEVER modifies any code or git state.
- NEVER pushes to any remote or interacts with GitHub.
