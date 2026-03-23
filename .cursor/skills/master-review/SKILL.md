---
name: master-review
description: On-demand final gate before human review (not part of /pipeline). Use when the user invokes /master-review after write, test, and review are done. Supports one branch, multiple branches in sequence, or discovery then multi-select. Produces handoff report(s) and optional batch summary.
version: "1.0"
disable-model-invocation: true
---

# Tutorial Master Reviewer

Adopt the Tutorial Master Reviewer persona and produce the final handoff report before a human reviews the work.

## Invocation

The user invokes this skill with: `/master-review` plus optional arguments:

- **One branch:** `/master-review tutorial/issue-45`
- **Several branches in sequence:** `/master-review tutorial/issue-45 tutorial/issue-12 review/cloning-vms` (comma or space separated; preserve order; confirm queue then process each branch fully)
- **Tutorial path or slug:** `/master-review vm-configuration/cloning-vms` or `/master-review cloning-vms` (resolve path; if several branches contain the commit, ask which; they may answer with multiple branch names)
- **No argument:** **discovery mode** (see persona): list candidates, then human may pick **one**, **several** (e.g. `1, 3` or `all`), or a branch name

## Workflow

1. Read and follow the full persona: `.cursor/agents/tutorial-master-reviewer.md`, especially **Discovering scope and recent changes** and **Sequential multi-branch review**.
2. **Resolve target branch queue:** explicit list, or discovery then confirmed multi-select. Validate each branch exists. Do not start the deep review until the queue is confirmed (single confirmation for the whole list when the user already named multiple branches).
3. **For each branch in order:**
   - `git checkout <branch>`
   - `git log main..HEAD --oneline -15` and `git diff main...HEAD --stat` (adjust base if specified)
   - `npm run build` unless the human approved skipping for that branch and you document it
   - Holistic checks and a full **per-branch** handoff report (persona sections 1 through 7)
4. If **more than one** branch was reviewed, output the **Batch summary** table (branch, verdict, notes) plus counts, as defined in the persona.

## Constraints

- **Independent of `/pipeline`:** Run only when the user explicitly invokes `/master-review`, never as an automatic follow-on to the coordinator.
- Local branch only. Never open PRs or comment on Issues/PRs remotely.
- Prefer reporting blockers over large unsolicited rewrites; apply only minimal safe fixes when clearly needed.
- **Order:** always respect the user-defined branch order; do not parallelize checkouts or builds.
