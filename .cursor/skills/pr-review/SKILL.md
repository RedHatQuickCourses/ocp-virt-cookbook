---
name: pr-review
description: Review one or more pull requests from the upstream repo (RedHatQuickCourses/ocp-virt-cookbook). Accepts multiple PR numbers for sequential batch review with automatic cluster cleanup between PRs. Detects previous review logs to enable follow-up mode with resolution tracking. Fetches each PR locally, performs structured review across all content types, optionally tests tutorials via oc commands, writes a review log with line-level gh api commands, and a cluster log with timestamped command output. Use when the user invokes /pr-review with one or more PR numbers.
version: "1.0"
disable-model-invocation: true
---

# PR Reviewer

Adopt the PR Reviewer persona and review a pull request from the upstream repository.

## Invocation

The user invokes this skill with one or more PR numbers:

```
/pr-review <number>
/pr-review #42
/pr-review 91 92 93
/pr-review #91 #92 #93
```

Parse all PR numbers from the message (numeric, with or without `#`). Deduplicate (if the same number appears twice, process it only once). Preserve the order the user provided. If more than one PR number is provided, this is a **batch invocation**.

## Workflow

1. Read and follow the full persona: `.cursor/agents/pr-reviewer.md`
2. Parse all PR numbers. Determine if this is a batch invocation (more than one PR).
3. **For each PR number, in order**, run the Per-PR Workflow below.
4. **Batch only:** After the Per-PR Workflow completes for a PR:
   a. If cluster testing was performed for this PR, run the cleanup workflow from `.cursor/skills/pr-review-cleanup/SKILL.md` automatically -- skip the human confirmation step (see "Batch Mode" in the persona for details).
   b. Return to the `main` branch: `git checkout main`.
   c. Proceed to the next PR.
5. **Batch only:** After all PRs are processed, print a batch summary table in chat (see "Batch Mode" in the persona).
6. **Single-PR only:** After the Per-PR Workflow completes, remind the user about `/pr-review-cleanup <number>`.

### Per-PR Workflow

1. **Detect previous review log:**
   - Check if `.cursor/output/pr-<number>.log` exists.
   - If it exists, read and parse the file to extract all findings (severity, file, line range, description). These become the "previous findings" context for follow-up review mode.
   - Rename the existing log to `.cursor/output/pr-<number>-previous.log`. If `-previous.log` already exists, rename it to `pr-<number>-previous-<N>.log` where `<N>` is the next available number starting from 2.
   - If no previous log exists, proceed as a normal first-pass review.
2. Fetch the PR branch locally: `gh pr checkout <number> --repo RedHatQuickCourses/ocp-virt-cookbook`
3. Capture PR metadata: `gh pr view <number> --repo RedHatQuickCourses/ocp-virt-cookbook`
4. Capture HEAD SHA: `git rev-parse HEAD`
5. Scope detection: `git diff main...HEAD --stat` and `git log main..HEAD --oneline` to classify changed files into categories
6. If tutorials or manifests are present (categories 1 or 2):
   - Check cluster reachability with `KUBECONFIG=<path> oc cluster-info`
   - Detect cluster topology (SNO vs multi-node) with `oc get nodes`
   - If tutorial requires multi-node and cluster is SNO, ask the human for an alternative cluster before skipping
7. Review all changed files against the category-specific criteria in the persona. If in follow-up mode, also check each previous finding for resolution (see persona for details).
8. If tutorials are present and cluster is available, test via `oc` commands. Log every command and output to `.cursor/output/pr-<number>-cluster.log`
9. Run `npm run build` and record result
10. Write the review log to `.cursor/output/pr-<number>.log` (follow-up format if previous findings exist; first-pass format otherwise)
11. Print chat summary (verdict, build/test status, finding counts, resolution status if follow-up, log paths). In batch mode, omit the `/pr-review-cleanup` reminder.
12. If any findings are too complex for the log, include a Detailed Findings section in chat

## Constraints

- Read-only for all code and git state. Never add, commit, or push.
- NEVER execute `gh api` commands. Generate them in the log for the human to run.
- NEVER run Ansible test playbooks. Test only via `oc` commands.
- In single-PR mode, NEVER clean up cluster resources. That is `/pr-review-cleanup`.
- In batch mode, cluster cleanup runs automatically between PRs (without human confirmation) to ensure a clean cluster for the next review. See "Batch Mode" in the persona.
- NEVER approve, comment on, or merge the PR remotely.
