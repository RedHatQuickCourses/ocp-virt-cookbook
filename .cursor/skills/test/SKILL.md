---
name: test
description: Test a tutorial against a live OpenShift cluster. Use when the user invokes /test with a branch name or tutorial path (e.g. /test feature-branch or /test cloud-init-ip-configuration) to validate tutorials.
version: "1.0"
disable-model-invocation: true
---

# Tutorial Tester

Adopt the Tutorial Tester persona and validate a tutorial against a live cluster.

## Invocation

The user invokes this skill with: `/test <branch-or-tutorial>` or `/test feature-branch` or `/test cloud-init-ip-configuration`

Parse from the user's message:
- Branch name (e.g. `feature-branch`, `tutorial/vm-snapshots`) - checkout that branch first, then test the tutorials changed on it
- Or tutorial identifier (e.g. `cloud-init-ip-configuration`, `vm-configuration/cloud-init-ip-configuration`) - test that specific tutorial

## Workflow

1. Read and follow the full persona: `.cursor/agents/tutorial-tester.md`
2. If a branch was given: `git checkout <branch>`
3. Identify the tutorial(s) to test (from branch diff or from the tutorial identifier)
4. Generate or update test scaffolding with `python tests/generate-test.py modules/<module>/pages/<tutorial>.adoc` if needed
5. Run the Ansible playbook against the cluster
6. Fix any issues found, commit fixes to the branch
7. Generate a report for the human user (summary, details, recommendations)

## Constraints

- Work only on the local branch. Never open PRs or comment on Issues/PRs remotely.
- All changes stay on the branch. Generate the report in chat for the human user.
