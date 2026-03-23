# Agent Personas

These prompts define specialized agent personas for the OpenShift Virtualization Cookbook. Use them in Cursor Agent windows or Composer by loading the appropriate prompt when starting a session for that task.

**Location:** Personas live in `.cursor/agents/` (not `.cursor/agent`).

## 1. Architecture Overview

The `.cursor/` configuration follows a three-layer architecture:

```
Rules (rules/*.mdc)            always-applied global constraints
  |
Personas (agents/*.md)         long-form behavioral definitions for each role
  |
Skills (skills/*/SKILL.md)     thin slash-command wrappers that delegate to a persona
```

- **Rules** are loaded automatically by Cursor on every interaction. They enforce project-wide constraints (git policy, security, content quality) without requiring explicit invocation.
- **Personas** define the behavior, workflow, and domain knowledge for a specific role (writer, tester, reviewer, etc.). Each persona references `shared-constraints.mdc` for common rules and adds its own role-specific logic.
- **Skills** are slash commands (`/write`, `/review`, etc.) that the user types in Agent chat. Each skill is a thin wrapper that reads the corresponding persona file and follows it.

Supporting files:

- `guardrails.yaml` -- machine-readable policy constraints (consumed by tooling, not by Cursor directly)
- `output/` -- gitignored directory for runtime artifacts (review logs, cluster logs)

## 2. Slash Command Reference

Cursor Skills in `.cursor/skills/` provide slash commands. Type `/` in Agent chat and select:

| Command | Skill | Example |
|---------|-------|---------|
| `/pipeline` | coordinator | `/pipeline 45 12 25 68 67` - run write, test, review for multiple issues sequentially |
| `/write` | tutorial-writer | `/write 45` or `/write issue #45` - write tutorial from GitHub issue |
| `/test` | tutorial-tester | `/test feature-branch` or `/test cloud-init-ip-configuration` - test against cluster |
| `/review` | tutorial-reviewer | `/review cloud-init-ip-configuration` or `/review vm-configuration/cloning-vms` - review for grammar and language |
| `/commit` | git-assistant | `/commit` - stage and commit changes with a bulleted message |
| `/pr-message` | git-assistant | `/pr-message` - generate a `gh pr create` command (never executes it) |
| `/master-review` | master-review | **Not part of `/pipeline`.** One or many branches: `/master-review b1 b2`, discovery then `1,3` or `all`, or a tutorial slug. Sequential review and a batch summary table when N > 1 |
| `/pr-review` | pr-reviewer | `/pr-review 42` or `/pr-review #42` - fetch a PR locally, review all content types, optionally test tutorials via `oc`, write review log with `gh api` commands and cluster log to `.cursor/output/` |
| `/pr-review-cleanup` | pr-reviewer | `/pr-review-cleanup 42` - clean up cluster resources created during `/pr-review`. Reads the cluster log, lists resources, asks for confirmation, deletes in reverse order |

**Pipeline command alternatives:** The coordinator skill is named `pipeline`. To use a different command, rename the folder in `.cursor/skills/` (e.g. `pipeline` to `batch`, `process`, `queue`, or `run`). All would invoke the same coordinator persona.

Skills use `disable-model-invocation: true` so they run only when you explicitly invoke them.

## 3. MCP Server Reference

| Server | Used by | Required |
|--------|---------|----------|
| user-kubernetes | /test, /pr-review, /pr-review-cleanup | Only with cluster |
| plugin-openshift-virtualization | /test, /pr-review | Only with cluster |

## 4. Personas (Manual Use)

| Persona | File | Use When |
|---------|------|----------|
| **Tutorial Coordinator** | `tutorial-coordinator.md` | Orchestrating write, test, review for multiple issues (`/pipeline`; master review is separate) |
| **Tutorial Writer** | `tutorial-writer.md` | Creating new tutorials or expanding existing ones |
| **Tutorial Reviewer** | `tutorial-reviewer.md` | Reviewing documentation for grammar and language |
| **Tutorial Tester** | `tutorial-tester.md` | Testing tutorials against a live OpenShift cluster |
| **Tutorial Master Reviewer** | `tutorial-master-reviewer.md` | On-demand only (`/master-review`): holistic checks and handoff report after pipeline work is done |
| **PR Reviewer** | `pr-reviewer.md` | On-demand only (`/pr-review`): fetch a PR locally, structured review across all content types, optional cluster testing via `oc`, produces review log and cluster log in `.cursor/output/` |
| **Git Assistant** | `git-assistant.md` | Local git operations: commit messages (`/commit`), PR command generation (`/pr-message`) |

## 5. How to Add a New Skill

1. Create a new folder under `.cursor/skills/` with the desired command name (e.g. `skills/my-command/`).
2. Create `SKILL.md` inside the folder with the required YAML frontmatter:
   ```yaml
   ---
   name: my-command
   description: One-sentence description of what the skill does and when to use it.
   version: "1.0"
   disable-model-invocation: true
   ---
   ```
3. In the body, add a heading, a brief description, an invocation section, a workflow section that reads the target persona file, and a constraints section.
4. Add the skill to the slash command table in this README.
5. Test by typing `/my-command` in Agent chat.

## 6. How to Add a New Persona

1. Create a new `.md` file in `.cursor/agents/` (e.g. `agents/my-persona.md`).
2. Start with a heading and a one-paragraph role description.
3. Add a `## Shared Constraints` section referencing `.cursor/rules/shared-constraints.mdc`.
4. Add persona-specific constraints and workflow sections.
5. Add a `## Reference` section listing shared-constraints and any other files the persona depends on.
6. Update the persona table in this README.
7. Optionally create a skill wrapper in `.cursor/skills/` to expose it as a slash command.

## 7. Configuration File Index

| File | Purpose |
|------|---------|
| `rules/allowed-commands.mdc` | Whitelist of CLI tools the agent may run |
| `rules/project-guidelines.mdc` | AsciiDoc, Antora, content quality standards, domain guidance |
| `rules/shared-constraints.mdc` | Git policy, commit attribution, tutorial content rules, build gate |
| `rules/security-policy.mdc` | Credential handling, context exclusions, cluster safety |
| `rules/reviewer-rubric.mdc` | 10-area documentation review rubric |
| `guardrails.yaml` | Machine-readable policy constraints |
| `agents/README.md` | This file -- architecture guide, onboarding, file index |
| `agents/git-assistant.md` | Git Assistant persona |
| `agents/tutorial-writer.md` | Tutorial Writer persona |
| `agents/tutorial-tester.md` | Tutorial Tester persona |
| `agents/tutorial-reviewer.md` | Tutorial Reviewer persona |
| `agents/tutorial-coordinator.md` | Tutorial Coordinator (pipeline orchestrator) persona |
| `agents/tutorial-master-reviewer.md` | Tutorial Master Reviewer persona |
| `agents/pr-reviewer.md` | PR Reviewer persona |
| `skills/*/SKILL.md` | Slash command wrappers (one per skill folder) |

## 8. Output Artifacts

All runtime output goes to `.cursor/output/` (gitignored). This includes:

| Artifact | Generated by | Format |
|----------|-------------|--------|
| `pr-<N>.log` | `/pr-review` | Review findings with `gh api` command for the human to run |
| `pr-<N>-cluster.log` | `/pr-review` | Timestamped `oc` command output from cluster testing |
| `pr-<N>-previous.log` | `/pr-review` (follow-up mode) | Renamed previous review log for resolution tracking |

To clean up:
- **Cluster resources:** Run `/pr-review-cleanup <N>` after inspecting the cluster state.
- **Log files:** Delete files from `.cursor/output/` manually when no longer needed.

## 9. Onboarding Checklist

```
[ ] Read this README
[ ] Review rules/ files (especially shared-constraints.mdc and project-guidelines.mdc)
[ ] Review security-policy.mdc for credential and context exclusion rules
[ ] Try /write with a test issue
[ ] Try /review on an existing tutorial
[ ] Verify npm run build passes
[ ] Familiarize yourself with the MCP server reference (section 3)
```

## Shared Constraints (All Personas)

All personas follow the rules in `.cursor/rules/shared-constraints.mdc`:

- Work only on a local branch. Never on main.
- Commit with the `Co-authored-by: cursor[bot]` trailer.
- NEVER open pull requests. NEVER push to any remote. NEVER comment on Issues or PRs remotely.
- All changes stay local until the human user decides to push or open a PR.
- Tutorial code blocks must not contain bash loops, conditionals, or multi-line scripts.
- Run `npm run build` before committing.

**PR Reviewer exception:** The PR Reviewer persona is read-only. It never commits, never pushes, and never modifies the fetched branch. It writes two log files to `.cursor/output/`: a review log (`pr-<number>.log`) with line-level `gh api` commands the human can selectively execute to comment on the PR, and a cluster log (`pr-<number>-cluster.log`) with timestamped command output from testing. Cluster cleanup is a separate skill (`/pr-review-cleanup`) the human invokes after inspecting the cluster state.

## How to Use

**With slash commands:** Type `/write`, `/test`, or `/review` in Agent chat, then add your argument when needed (e.g. `/write 45`). After `/pipeline` or manual write/test/review is finished on a branch, run `/master-review` when you want the handoff report (it is not part of `/pipeline`). To review a pull request, use `/pr-review <number>`. After inspecting the cluster, use `/pr-review-cleanup <number>` to remove test resources.

**Manual:** Reference the persona: "Use the tutorial writer persona from .cursor/agents/tutorial-writer.md" and provide your task.

## Dependencies

- **Writer** and **Reviewer**: Project guidelines (`.cursor/rules/project-guidelines.mdc`) and reviewer rubric (`.cursor/rules/reviewer-rubric.mdc`) are referenced within the personas
- **Tester**: Requires `oc` authenticated to a cluster, Ansible with kubernetes.core, and the `tests/` directory structure
- **Master Reviewer**: Not run by `/pipeline`. Invoke `/master-review` when write, test, and review are done; one branch, several in sequence, or discovery plus multi-select. Produces per-branch handoff reports and a batch summary when multiple branches are reviewed
- **PR Reviewer**: Not run by `/pipeline`. Invoke `/pr-review <number>` to review a PR. Requires `gh` CLI for fetching, optionally `oc` for cluster testing. Produces `.cursor/output/pr-<number>.log` and `.cursor/output/pr-<number>-cluster.log`. Cleanup is separate: `/pr-review-cleanup <number>`
