# Extraction Rules

Use these rules when session context is long, fragmented, or noisy.

## Preserve

- Project mission and the repo's role in that mission.
- Confirmed root causes.
- Stable architectural decisions.
- Hard user constraints.
- Borrowed patterns, external inspirations, and rejected approaches that explain the current design.
- Commands, files, logs, and identifiers needed to continue.
- Unfinished work that another agent cannot infer from git state alone.
- The short roadmap after the immediate next step.
- Receiver-side action guardrails.

## Compress

- Minor back-and-forth that does not affect execution.
- Reversible experiments.
- Recoverable repository structure.
- One-off review comments with no lasting consequence.

## Reject

- Empty summaries.
- Generic status language.
- Personal chatter.
- Advice not grounded in the actual work.
- Sections with no artifacts, constraints, or decisions.
- Reports that only recap the latest verification loop.
- Broad prose when a compact DSL block would preserve more entropy.

## Writing Standard

- Prefer direct statements.
- Prefer concrete nouns over abstractions.
- Prefer one decisive next step over a long option list.
- Preserve the project overview before the latest turn-by-turn execution detail.
- If a risk was already disproven, say so and tell the next agent not to repeat it.
- Prefer dense English DSL for stored handoff content.
- Reserve Chinese for the user-facing brief during handoff and resume.
