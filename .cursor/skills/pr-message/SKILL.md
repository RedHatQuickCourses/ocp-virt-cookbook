---
name: pr-message
description: Generate a gh pr create command targeting the upstream repo (RedHatQuickCourses/ocp-virt-cookbook) with a concise bulleted PR message. Use when the user invokes /pr-message. Never executes the command.
version: "1.0"
disable-model-invocation: true
---

# Generate PR Command and Message

Output the full `gh pr create` command for the user to copy and run. Never execute it.

## Invocation

The user invokes this skill with: `/pr-message`

## Workflow

1. Read and follow the full persona: `.cursor/agents/git-assistant.md`
2. Run `git branch --show-current` to identify the current branch
3. Run `git log main..HEAD --oneline` to see all commits on the branch
4. Run `git diff main...HEAD --stat` to see the scope of changes
5. Draft a PR title from the branch commits
6. Draft a PR body as exactly 5 bulleted lines and nothing else (no headers, no test plan, no extra text)
7. Output the complete command as a code block:
   - `git push -u origin HEAD` (remind user to run this first)
   - `gh pr create --repo RedHatQuickCourses/ocp-virt-cookbook --title "..." --body "..."`
8. Do NOT execute the command. Display it for the user to run.

## Constraints

- NEVER push to any remote. NEVER execute `gh pr create`.
- Always target `--repo RedHatQuickCourses/ocp-virt-cookbook`.
- PR body must be exactly 5 bulleted lines and nothing else (no headers, no sections, no test plan).
- No emojis.
