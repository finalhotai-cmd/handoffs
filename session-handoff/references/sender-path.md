# Sender Path

Use this path when the current thread already contains enough first-hand work state to serialize into a new `OH`.

## Eligibility

You are eligible only if the thread contains at least one of:

- concrete decisions,
- inspected or changed files,
- commands run,
- validations or failures,
- unfinished work that advanced in this thread.

If the thread is cold-started and only knows about prior reports or skill docs, it is not the sender.

## Workflow

1. Read `references/handoff-schema.md`.
2. Read `references/extraction-rules.md` if context is noisy or long.
3. Gather project-level mission, current task, what is already done, design lineage, constraints, risks, and next-step roadmap.
4. Write the final Markdown report directly into `$HOME/0-handoff/reports/YYYYMMDD-HHMM-project-topic.md`.
5. Run `python3 scripts/register_handoff.py --report-path /abs/path/to/report.md`.
6. If registration fails, read the error, fix the existing report file, and rerun registration until it succeeds.

## What To Gather

- The exact problem being solved.
- The project itself: what it exists to do.
- What is already done.
- Hard constraints from the user or environment.
- Decisions already made and why they should persist.
- External inspirations, borrowed patterns, and rejected alternatives that shaped the current design.
- Key files, commands, logs, or artifacts to inspect next.
- The immediate next action plus the short roadmap after that.
- The receiver-side user gate: explain first, wait for ack, then act.
- A `Resume DSL.READ_FIRST` list that points only to implementation-critical files, not general docs.

## What To Avoid

- Long chat recap.
- Generic praise or filler.
- Restating recoverable repository facts.
- Dumping every file touched.
- Mid-task speculation that was never confirmed.
- Placeholder sections such as `TBD`.
- Vague lines that cannot be traced to a file, command, decision, or risk.
- Reports that only summarize the latest validation loop and omit the broader project.

## Anti-Hollow Rule

Reject the handoff if it lacks any of these:

- concrete files or artifacts,
- at least one durable decision or constraint,
- the project mission and current project stage,
- the design lineage or inspirations that explain why the current shape exists,
- a forward roadmap beyond the immediate next move,
- a real next step,
- receiver guardrails,
- enough detail for another agent to continue without re-reading the whole chat.

## Hard Rules

- Never inline large payloads into shell commands.
- Never pipe section JSON to any script.
- Always write the final `.md` artifact first.
- Registration is mandatory before claiming the sender flow is complete.

## Script Usage

Example:

```bash
python3 scripts/register_handoff.py \
  --report-path "$HOME/0-handoff/reports/20260417-2100-codex-project111-session-handoff.md"
```

The registrar validates the final Markdown artifact, normalizes deterministic metadata, and updates `$HOME/0-handoff/index/latest.json`.
