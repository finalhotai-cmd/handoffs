# Handoff Schema

Every `OH` report lives under:

```text
/Volumes/OSX ExtNVME/code_projects/handoffs/reports/
```

Use this filename shape:

```text
YYYYMMDD-HHMM-<project-slug>-<topic-slug>.md
```

Use dense English DSL for machine-to-machine transfer.

- Prefer compact key-value blocks.
- Prefer identifiers, paths, commands, and decisions over prose.
- User-facing Chinese brief happens outside the report, at handoff/resume time.

## Direct-Write Contract

The writer must create the final Markdown artifact directly.

- Do not generate section JSON for a converter script.
- Do not pipe large payloads through shell stdin.
- Write the final `.md` file first.
- Then run `python3 scripts/register_handoff.py --report-path /abs/path/to/report.md`.
- If registration fails, repair the existing report file and rerun the registrar.

## Filename And Frontmatter Rules

- `id` must equal the filename stem.
- `created_at` must exist in frontmatter.
- The registrar treats the filename timestamp as the source of truth and normalizes `created_at`.
- `workspace_root` must be absolute.
- `status` should usually be `in_progress`, `blocked`, or `done`.
- `execution_mode` must be `plan_then_wait`.
- `user_gate` must be `required`.
- `key_files` must contain files worth opening first, not every touched file.
- `next_step` must be a concrete next action, not a vague summary.
- `branch` is optional.

## Required Frontmatter

```yaml
---
id: 20260320-1530-codex-project111-session-handoff
created_at: 2026-03-20 15:30
project_name: Codex_Project111
workspace_root: /Volumes/OSX ExtNVME/code_projects/Codex_Project111
branch: codex/session-handoff
task_title: Build unified session handoff skill
status: in_progress
execution_mode: plan_then_wait
user_gate: required
brief_lang: zh-CN
tags:
  - handoff
  - skill
key_files:
  - /abs/path/one
  - /abs/path/two
next_step: Run the finder script, read this report, then edit the skill draft.
---
```

## Required Sections

```markdown
## 1. Goal DSL

## 2. State DSL

## 3. Context DSL

## 4. Evidence DSL

## 5. Work DSL

## 6. Resume DSL

## 7. Risk DSL

## 8. User Gate DSL
```

Each section must contain exactly one fenced `handoff` block.

## Required Semantic Coverage

Every report must preserve both:

- the project-level frame,
- and the current-session execution state.

Do not emit a report that only summarizes the last one or two turns.

Minimum required keys by section:

- `Goal DSL`
  - `PROJECT_MISSION`
  - `CURRENT_TASK`
  - `OUTPUT`
  - `DONE_WHEN`
- `State DSL`
  - `PROJECT_STAGE`
  - `SESSION_FOCUS`
  - `DONE`
  - `IN_FLIGHT`
- `Context DSL`
  - `PROJECT_SCOPE`
  - `USER_REQ`
  - `DECISIONS`
  - `CONSTRAINTS`
  - `INSPIRATIONS`
- `Evidence DSL`
  - `FILES`
  - `CMDS`
  - `ARTIFACTS`
- `Work DSL`
  - `COMPLETED`
  - `NEXT`
  - `ROADMAP`
- `Resume DSL`
  - `READ_FIRST`
  - `CHECK_FIRST`
  - `PLAN_BRIEF_CN`
  - `EXECUTE_AFTER_ACK`
- `Risk DSL`
  - `MISREAD`
  - `DUP_WORK`
  - `NO_GO`
- `User Gate DSL`
  - `ASK_USER`
  - `WAIT_FOR_ACK`
  - `NO_MUTATION_BEFORE_ACK`
  - `BRIEF_CN`

## DSL Example

````text
## 1. Goal DSL

```handoff
PROJECT_MISSION: create a reusable cross-project AI handoff system
CURRENT_TASK: build unified session handoff skill
OUTPUT: skill folder + finder/registrar scripts
DONE_WHEN: receiver can select correct OH and must plan before mutate
```

## 2. State DSL

```handoff
PROJECT_STAGE: consolidating architecture and validation rules
SESSION_FOCUS: replace stdin generation with direct-write registration
DONE:
  - drafted core skill structure
IN_FLIGHT:
  - rewriting sender workflow
```

## 3. Context DSL

```handoff
PROJECT_SCOPE:
  - cross-project handoff storage and retrieval
USER_REQ:
  - use dense English DSL
DECISIONS:
  - sender writes final markdown directly
CONSTRAINTS:
  - do not create AGENTS.md in project roots
INSPIRATIONS:
  - claude-skill-registry handoff skill
  - Continuous-Claude-v3 task chain
```

## 4. Evidence DSL

```handoff
FILES:
  - /abs/path/one
  - /abs/path/two
CMDS:
  - python3 scripts/register_handoff.py --report-path /abs/path/to/report.md
ARTIFACTS:
  - /Volumes/OSX ExtNVME/code_projects/handoffs/index/latest.json
```

## 5. Work DSL

```handoff
COMPLETED:
  - removed the stdin handoff generator
NEXT:
  - validate the written report with the registrar
ROADMAP:
  - improve finder ranking
  - harden registration errors
```

## 8. User Gate DSL

```handoff
ASK_USER: true
WAIT_FOR_ACK: true
NO_MUTATION_BEFORE_ACK: true
BRIEF_CN: 先用中文向用户说明准备做什么，再等确认。
```
````

## Registrar Expectations

The registrar must reject reports when any of these hold:

- invalid filename shape,
- missing frontmatter,
- missing required frontmatter keys,
- `id` and filename mismatch,
- wrong section order,
- missing `handoff` fence,
- hollow required section keys,
- absent `INSPIRATIONS`,
- absent `ROADMAP`,
- missing wait-for-ack guard.

The registrar may auto-fix only deterministic metadata, such as normalizing `created_at` from the filename timestamp.

## Field Rules

- `Resume DSL.READ_FIRST` should point to implementation-critical files only. Do not include `README.md` or older `OH` files unless the current report is explicitly marked incomplete.
- On the receiver path, `Resume DSL.READ_FIRST` is deferred until after user acknowledgement unless the matched report is provably incomplete.
- Every report must contain project mission, adopted inspirations, roadmap, decisions, evidence, and explicit receiver guardrails.
- Prefer concise, execution-oriented DSL over retrospective narration.
