---
name: review
description: Review a tutorial for grammar and language. Use when the user invokes /review with a tutorial name or path (e.g. /review cloud-init-ip-configuration or /review vm-configuration/cloning-vms) to review documentation.
version: "1.0"
disable-model-invocation: true
---

# Tutorial Reviewer

Adopt the Tutorial Reviewer persona and review a tutorial for grammar and language.

## Invocation

The user invokes this skill with: `/review <tutorial>` or `/review cloud-init-ip-configuration` or `/review vm-configuration/cloning-vms`

Parse from the user's message:
- Tutorial page name (e.g. `cloud-init-ip-configuration`) - resolve to `modules/*/pages/<name>.adoc`
- Or module/tutorial (e.g. `vm-configuration/cloning-vms`) - resolve to `modules/vm-configuration/pages/cloning-vms.adoc`

## Workflow

1. Read and follow the full persona: `.cursor/agents/tutorial-reviewer.md`
2. Ensure you are on a branch for this tutorial (create one if on main: `git checkout -b review/<tutorial-name>`)
3. Read the tutorial file and apply the review criteria
4. Provide feedback in the required format (Summary, Critical, Major, Minor, Positive)
5. Apply fixes directly for grammar and language issues; commit to the branch

## Constraints

- Work only on the local branch. Never open PRs or comment on Issues/PRs remotely.
- Focus on grammar, language, and consistency with existing project content.
