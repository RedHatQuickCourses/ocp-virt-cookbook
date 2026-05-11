---
name: qe-validate
description: Run the QE validation agent against all tutorials (or a filtered subset) on a live OpenShift cluster. Produces a version-tagged compatibility report and commits version-tested updates for passing tutorials.
disable-model-invocation: true
---

Read and follow `.cursor/agents/qe.md`.

Parse module filters and flags from: $ARGUMENTS

Use `Co-authored-by: Claude <noreply@anthropic.com>` for the commit trailer.
