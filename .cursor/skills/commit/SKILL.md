---
name: commit
description: Commit staged and unstaged changes to the current local branch with a concise, bulleted commit message. Use when the user invokes /commit. Never pushes to any remote.
version: "1.0"
disable-model-invocation: true
---

# Commit to Local Branch

Stage and commit all current changes to the local branch with a well-crafted message.

## Invocation

The user invokes this skill with: `/commit`

## Workflow

1. Read and follow the full persona: `.cursor/agents/git-assistant.md`
2. Run `git status` to see all changed, staged, and untracked files
3. Run `git diff` (unstaged) and `git diff --cached` (staged) to understand the changes
4. Run `git log -3 --oneline` to match the repository's commit style
5. Draft a commit message:
   - Short title line summarizing the change
   - Bulleted list body (max 5 bullets, concise)
   - Co-authored-by trailer
6. Stage relevant files with `git add`
7. Commit using a HEREDOC for the message
8. Run `git status` to confirm the working tree is clean

## Constraints

- NEVER push to any remote. All operations are local only.
- NEVER create pull requests or interact with remote repositories.
- Messages must be bulleted lists, max 5 lines, no emojis.
