---
name: write
description: Write a new tutorial for the OpenShift Virtualization Cookbook. Use when the user invokes /write with an issue number (e.g. /write 45 or /write issue #45) to create a tutorial from a GitHub issue.
version: "1.0"
disable-model-invocation: true
---

# Tutorial Writer

Adopt the Tutorial Writer persona and create a tutorial from a GitHub issue.

## Invocation

The user invokes this skill with: `/write <issue>` or `/write issue #45`

Parse the issue number from the user's message (e.g. 45, #45, issue 45).

## Workflow

1. Read and follow the full persona: `.cursor/agents/tutorial-writer.md`
2. Fetch the GitHub issue content (title, body, labels) to understand the tutorial requirements
3. Create a branch: `git checkout -b tutorial/<short-name>` (derive from issue title)
4. Write the tutorial following the persona's structure and guidelines
5. Add the page to the module's nav.adoc
6. Create attachment YAML files if the tutorial includes manifests
7. Run `npm run build` to verify
8. Commit all changes to the branch

## Constraints

- Work only on the local branch. Never open PRs or comment on Issues/PRs remotely.
- If the user shares cluster credentials, you may test and fix issues on the same branch.
