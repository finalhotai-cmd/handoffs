# Task Plan: Fix session-handoff Freeze (Hybrid Fix)

## Goal
Resolve the PTY buffer deadlock by moving large content writes to native tools while keeping a lightweight shell script for metadata indexing and validation.

## Current Phase
Phase 3: Verification & Closeout

## Phases

### Phase 1: Requirements & Discovery
- [x] Analyze session-handoff freeze causes
- [x] Compare with planning-with-files robustness
- [x] Formulate Hybrid V2 (Direct Write + Registrar)
- **Status:** complete

### Phase 2: Refactoring Implementation
- [x] Create `scripts/register_handoff.py` (Linter + Indexer)
- [x] Update `references/sender-path.md` (Intent-based workflow)
- [x] Update `references/handoff-schema.md` (Markdown context)
- [x] Add shared parsing helpers for frontmatter and section extraction
- [x] Update `references/emit-handoff.md` to the new direct-write contract
- **Status:** complete

### Phase 3: Verification & Cleanup
- [x] Verify large payload registration (100KB test)
- [x] Delete problematic `scripts/emit_handoff.py`
- [x] Review blocking issues (P0/P1 only)
- [x] Fix registrar root mismatch bug
- [x] Re-review P0/P1 after the fix
- [x] Rename the skill directory to `session-handoff`
- [x] Remove legacy alias and stale textual references
- [x] Deliver walkthrough
- **Status:** complete

## Key Questions
1. How to ensure AI calculates the timestamp consistently? (Provided in template)
2. What happens if direct write fails? (Standard tool error handling)

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Use `write_to_file` for content | Native IDE tools bypass PTY pipes and 64KB buffers. |
| Retain Python for Registry | AI is bad at modifying existing JSON (latest.json) precisely; Python is safer. |
| Post-hoc Validation | Ensures schema correctess without risking pipe deadlock during transmission. |
| Remove `emit_handoff.py` entirely | Antigravity cannot rely on shell-mediated large-payload generation; fallback-in-repo is not a goal. |
| Keep `latest.json` shape unchanged | Existing finder logic already depends on `latest` plus compact metadata. |
| Treat filename timestamp as the source of truth | `created_at` mismatch is deterministic and should be normalized, not block registration. |
| Require `report-path` under `<root>/reports` | Prevents successful registration from producing an unusable `latest.json` pointer. |
| Do not block on regex whitespace hardening | Current parser enforces the canonical schema; without a concrete failing artifact from the direct-write path, this remains non-blocking hardening rather than a correctness defect. |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| PTY Deadlock | 1 | Architecture change to File-based transfer. |
| Root mismatch in registrar | 1 | Enforced `report-path` to live under `<root>/reports` before updating `latest.json`. |
