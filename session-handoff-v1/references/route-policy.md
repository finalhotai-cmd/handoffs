# Route Policy

This file defines only the initial routing decision.
It exists so `SKILL.md` can stay minimal and the sender/receiver workflows can live elsewhere.

## Routing Layers

There are two distinct instruction layers:

1. Skill activation keywords.
2. Actual routing after the skill has been invoked.

Use broad activation keywords freely. They only get the agent into this skill.
Do not use keyword matching alone to choose `Sender Path`.

## Default Rules

- If the thread is cold-started, empty, or has no concrete work state, choose `Receiver Path`.
- If the thread has content but the semantic intent is unclear, ask the user which path to take.
- If the user explicitly asks for a new `OH` and the thread already contains first-hand work state, choose `Sender Path`.
- If the user wants to continue, resume, cold-start, restore context, or inspect an existing `OH`, choose `Receiver Path`.
- If the thread lacks first-hand state, it cannot enter `Sender Path` even when the user says `交接`.
- The receiver path should not depend on a project folder to locate work; use global `handoffs` plus report metadata.

## First-Hand State

`Sender Path` requires current-thread evidence such as:

- concrete decisions made in this thread,
- files inspected or changed in this thread,
- commands run in this thread,
- validations or failures observed in this thread,
- unfinished work advanced in this thread.

If that state is missing, stay on `Receiver Path` or ask the user to continue working first.

## Ambiguity Rule

If the model cannot confidently infer intent from the current thread, do not guess.

- Ask the user which flow they want.
- Do not synthesize a sender decision from broad handoff words alone.
- Do not inspect extra docs before the route is decided.

## Disallowed Before Routing

- `git status`
- broad `rg`
- repository sweeps
- reading sender or receiver workflow docs
- reading old `OH` files
