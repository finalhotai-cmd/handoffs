---
name: session-handoff
description: 交接、接手工作
---

# Session Handoff

1. Decide the route first.
2. If the route is unresolved, ask the user which path to take and stop.
3. Do not read other reference files before the route is chosen.
4. Read only the chosen path:
   - `Sender Path` -> `references/sender-path.md`
   - `Receiver Path` -> `references/receiver-path.md`

Rules:

- `Receiver Path` is the default when the thread is cold-started, empty, low-context, or has no concrete work state.
- `Receiver Path` also applies when the user wants to 接手, continue, resume, cold-start, restore context, or inspect an existing `OH`.
- `Sender Path` requires explicit write intent plus first-hand current-thread state; broad handoff words alone do not force sender.
- First-hand state means concrete decisions, inspected or changed files, commands run, validations, failures, or unfinished work advanced in this thread.
- If the thread lacks first-hand state, it cannot enter `Sender Path`, even if the user says `交接` or asks to write an `OH`.
- If the thread has content but the intent is ambiguous, ask the user instead of guessing.
