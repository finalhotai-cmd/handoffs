# Session-Handoff V2 Rewrite Plan

## Summary

Replace the sender-side `stdin JSON -> emit_handoff.py -> Markdown` flow with a single direct-write flow:

- AI writes the final `.md` handoff report directly under `handoffs/reports/`.
- A new `register_handoff.py` validates and registers that file.
- `emit_handoff.py` is removed.
- Sender docs and schema are rewritten to describe the final Markdown artifact, not an intermediate JSON payload.

This plan is decision-complete for implementation and assumes the Antigravity constraint is already settled: shell-mediated large-content write is invalid and not part of the supported design.

## Implementation Changes

### 1. Registrar script

Add `session-handoff-v1/scripts/register_handoff.py` with one CLI:

```bash
python3 scripts/register_handoff.py --report-path /abs/path/to/report.md
```

Behavior:

- Read one existing Markdown report file from disk.
- Parse frontmatter without adding new third-party dependencies.
- Reuse the current lightweight frontmatter approach already used by `find_handoff.py`; if useful, extract shared helpers instead of duplicating parsing logic.
- Validate:
  - file exists and is readable
  - filename matches `YYYYMMDD-HHMM-<project-slug>-<topic-slug>.md`
  - frontmatter exists and parses
  - required keys exist: `id`, `created_at`, `project_name`, `workspace_root`, `task_title`, `status`, `execution_mode`, `user_gate`, `brief_lang`, `tags`, `key_files`, `next_step`
  - `execution_mode == "plan_then_wait"`
  - `user_gate == "required"`
  - `workspace_root` is absolute
  - `id == filename stem`
  - all 8 required sections exist in the canonical order
  - each section contains exactly one fenced `handoff` block
  - minimum semantic gates remain: non-trivial `PROJECT_MISSION`, non-empty `INSPIRATIONS`, non-empty `ROADMAP`, explicit wait-for-ack behavior in `User Gate DSL`
- Auto-fix only deterministic metadata:
  - filename timestamp is the source of truth
  - registrar normalizes or overwrites frontmatter `created_at` from the filename timestamp instead of failing on mismatch
  - keep `id` strict; mismatch is a hard error, not auto-fix
- On success:
  - update `handoffs/index/latest.json`
  - keep the current `latest.json` shape:
    - `latest`
    - `metadata.project_name`
    - `metadata.workspace_root`
    - `metadata.task_title`
    - `metadata.status`
    - `metadata.next_step`
  - print the registered report path
- On failure:
  - exit `1`
  - return a short deterministic repair message that tells the writer exactly what to change

### 2. Sender workflow rewrite

Update `references/sender-path.md` to remove all `stdin JSON` / generator usage.

New required flow:

1. Read schema guidance.
2. Gather first-hand state.
3. Write the final Markdown report directly to `handoffs/reports/YYYYMMDD-HHMM-project-topic.md`.
4. Run `register_handoff.py --report-path <path>`.
5. If registration fails, edit the existing file and retry until registration succeeds.

Hard rules to include:

- never inline large payloads into shell commands
- never pipe section JSON to any script
- always create the final `.md` artifact first
- registration is mandatory before claiming sender flow is complete

### 3. Schema rewrite

Update `references/handoff-schema.md` so it specifies the final Markdown artifact directly.

Add or clarify:

- filename shape and generation rule
- `id` must equal filename stem
- `created_at` is normalized from filename timestamp by the registrar
- required frontmatter fields
- required section headings and order
- each section must contain a fenced `handoff` block
- direct-write loop: write -> register -> repair -> re-register
- the schema no longer defines a JSON payload contract for emitter input

Keep `branch` optional unless already present.

### 4. Legacy cleanup

Update `references/emit-handoff.md` to point to the new direct-write plus registrar flow.

Delete `session-handoff-v1/scripts/emit_handoff.py` entirely after the new path is implemented.

No in-repo deprecation path, dual-path mode, or compatibility wrapper is added.

## Public Interfaces / Contract Changes

- New script interface:
  - `python3 scripts/register_handoff.py --report-path /abs/path/to/report.md`
- Removed script interface:
  - `emit_handoff.py` and all `stdin JSON` generation usage
- Stable persisted index contract:
  - `handoffs/index/latest.json` keeps its current shape
- Writer contract changes:
  - writers now produce the final Markdown report directly
  - registrar is the only validation and registration gate

## Test Plan

### Success cases

1. Write a valid report file with all required frontmatter and 8 sections, then run registrar and confirm:
   - exit `0`
   - returned path matches the file
   - `index/latest.json` updates correctly
2. Write a large report around `100 KB`, register it, and confirm no freeze and successful index update.
3. Write a valid report whose `created_at` differs from the filename timestamp, then confirm registrar normalizes `created_at` instead of failing.

### Failure cases

1. invalid filename shape
2. missing frontmatter block
3. missing required frontmatter key
4. `id` / filename mismatch
5. non-absolute `workspace_root`
6. missing section heading
7. wrong section order
8. missing fenced `handoff` block
9. hollow `PROJECT_MISSION`
10. empty `INSPIRATIONS`
11. empty `ROADMAP`
12. missing wait-for-ack guard in `User Gate DSL`

Each failure must produce a short repairable error message.

## Assumptions And Defaults

- No new Python dependency is introduced; implementation stays stdlib-only.
- `find_handoff.py` continues to read report files as it does today and remains compatible with the rewritten reports.
- `latest.json` remains a single-pointer index, not a richer registry.
- `created_at` mismatch is treated as auto-fixable redundancy; `id` mismatch is treated as a hard integrity error.
- `branch` remains optional.
- Because this conversation is currently in Plan Mode, implementation is not executed in this turn; this plan is the execution spec.
