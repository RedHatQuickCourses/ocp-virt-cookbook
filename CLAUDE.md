# OpenShift Virtualization Cookbook

Antora-based AsciiDoc documentation project. Tutorials live in `modules/<module>/pages/*.adoc`.

## Rules

Read and follow these rules files on every interaction:

- `.cursor/rules/shared-constraints.mdc` -- git policy, commit attribution, content rules, build gate
- `.cursor/rules/project-guidelines.mdc` -- AsciiDoc standards, review criteria, terminology, domain guidance
- `.cursor/rules/security-policy.mdc` -- credential handling, context exclusions, cluster safety
- `.cursor/rules/allowed-commands.mdc` -- whitelist of CLI commands

## Commit Attribution

When committing with Claude Code, use this trailer instead of the Cursor one:

```
Co-authored-by: Claude <noreply@anthropic.com>
```

## Skills

Slash-command skills are in `.claude/skills/`. Each references an agent persona under `.cursor/agents/`.

| Command | What it does |
|---------|-------------|
| `/tutorial` | Full pipeline (research, write, test, review, commit) from GitHub issues |
| `/master-review` | Final unbiased review of ready branches before human handoff |
| `/commit` | Commit with bulleted message |
| `/pr-message` | Generate `gh pr create` command |
| `/pr-review` | Review incoming upstream PRs |
| `/pr-review-cleanup` | Clean up cluster resources from PR review |
| `/qe-validate` | Validate tutorials against live cluster, update version annotations, generate issue commands |

## Build

```bash
npm run build    # Antora build -- must pass before committing
npm run serve    # Preview at http://localhost:8080
```

## Upstream Repository

```
RedHatQuickCourses/ocp-virt-cookbook
```
