# Receiver Path

Use this path when the user wants to continue, resume, cold-start, 接手, restore context, inspect an existing `OH`, or when route selection is ambiguous and the safest default is to resume work.

## Default Flow

1. Resolve the target report immediately.
   - Default command:
     `python3 scripts/find_handoff.py --root /Volumes/OSX\ ExtNVME/code_projects/handoffs`
   - If and only if the user explicitly gives a project, query, or target report, add `--workspace-root`, `--query`, or `--status`.
2. Open the exact `OH` path returned by that command.
3. Read the selected `OH` report only.
4. Extract:
   - `Goal DSL.PROJECT_MISSION`
   - `State DSL.PROJECT_STAGE`
   - `Context DSL.INSPIRATIONS`
   - `workspace_root`
   - `task_title`
   - `status`
   - `key_files`
   - `next_step`
5. Convert the `Resume DSL` and `User Gate DSL` into a short Chinese brief for the user.
6. Tell the user:
   - what you believe the project is trying to achieve,
   - which outside patterns or prior skills shaped the current design,
   - what you believe the current task is,
   - what you plan to inspect first,
   - what you plan to change,
   - and what you will not do yet.
7. Wait for explicit acknowledgement before any mutation, implementation, or side-effecting command.

## Matching Priority

Prefer reports in this order:

1. `key_files` or `task_title` that best match the user's request.
2. `status: in_progress`.
3. Most recent timestamp.
4. `workspace_root` only as a weak tiebreaker or when the user explicitly supplied it.

## When To Read More Than The Report

Read sender references only if:

- the report is clearly stale,
- critical files are missing,
- the next step is too vague,
- or multiple reports tie with no clear winner.

Do not load `README.md`, the full skill reference set, `Resume DSL.READ_FIRST`, or older reports by default on the receiver path.
Open those only after user acknowledgement or when the matched report is provably incomplete.
Do not read `sender-path.md`, `state-files`, legacy handoff skills, or run `git status` before the target `OH` is resolved.
Do not use `workspace_root` as a hard precondition for receiver selection.

## Hard Gate

The receiver must not treat a matched `OH` file as execution permission.

- Reading is allowed.
- Planning is allowed.
- Project-level restatement to the user is required.
- Explaining the plan to the user is required.
- Acting is blocked until the user confirms.
- Target resolution before context reconstruction is required.
