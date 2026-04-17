---
name: session-handoff
description: Create and resume cross-project AI handoffs stored under /Volumes/OSX ExtNVME/code_projects/handoffs. Use when the user asks to hand off work, continue from a previous AI session, resume unfinished work, or mentions 交接, 接手, handoff, continue previous task, or restore context.
---

# Session Handoff

Use this skill for one purpose: resolve the route first, then follow exactly one path.

1. Read `references/route-policy.md`.
2. If the route is unresolved, ask the user which path to take and stop.
3. If the route is `Sender Path`, read `references/sender-path.md`.
4. If the route is `Receiver Path`, read `references/receiver-path.md`.
5. Do not read any other reference files before the route is chosen.

Rules:

- `Receiver Path` is the default when the thread is cold-started, low-context, or the user did not explicitly ask for a new `OH`.
- `Sender Path` requires both explicit write intent and first-hand work state in the current thread.
- If the thread has content but the intent is ambiguous, ask the user instead of guessing.
- If the thread has no concrete state to serialize, it cannot enter `Sender Path`.
- The receiver path must not mutate anything before explicit user acknowledgement.
- Do not create or overwrite project-root `AGENTS.md`.
