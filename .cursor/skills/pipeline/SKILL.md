---
name: pipeline
description: Run the tutorial pipeline (write, test, review) for multiple GitHub issues sequentially. Use when the user invokes /pipeline with issue numbers (e.g. /pipeline 45 12 25) to produce complete tutorials. Rename folder to batch, process, queue, or run for alternative command. Master review is separate; use /master-review when ready.
version: "1.0"
disable-model-invocation: true
---

# Tutorial Pipeline Coordinator

Adopt the Tutorial Coordinator persona and process multiple issues through the full pipeline.

## Invocation

The user invokes this skill with: `/pipeline <issue1> <issue2> ...` or `/pipeline 45 12 25 68 67`

Parse all issue numbers from the message. Formats accepted: `45`, `#45`, `issue 45`, `45, 12, 25`.

## Workflow

1. Read and follow the full persona: `.cursor/agents/tutorial-coordinator.md`
2. Parse and deduplicate issue numbers
3. For each issue, sequentially: Write -> Test -> Review
4. Report progress after each issue
5. Produce final summary report when done

## Constraints

- Sequential only. One issue at a time.
- One branch per issue. Never open PRs or comment remotely.
- All changes stay local for human review.
