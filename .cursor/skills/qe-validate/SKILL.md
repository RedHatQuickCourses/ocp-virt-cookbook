---
name: qe-validate
description: Run the QE validation agent against all tutorials (or a filtered subset) on a live OpenShift cluster. Produces a version-tagged compatibility report and commits version-tested updates for passing tutorials.
version: "1.0"
disable-model-invocation: true
---

# QE Validate

Read and follow `.cursor/agents/qe.md`.

**Invocation:** `/qe-validate [module1] [module2] [--dry-run]` -- with no arguments, validates all tutorials. Pass module names (e.g., `getting-started networking`) to filter. Use `--dry-run` to print the tutorial inventory without testing.
