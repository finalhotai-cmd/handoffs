# Findings: Session-Handoff Freeze Analysis

## Discovery Log

### 1. PTY Deadlock (The "Killer" Bug)
- **Source**: Gemini & Claude Cross-Analysis.
- **Root Cause**: The communication channel used `sys.stdin.read()` for large payloads.
- **Mechanism**:
  - Parent writes to Stdin → PTY echoes to Stdout.
  - Payload > ~4KB fills PTY Stdout buffer.
  - OS blocks Parent write until Stdout is read.
  - Parent is waiting for script completion (no read); Script is waiting for Stdin EOF (no completion).
  - **Deadlock confirmed.**

### 2. XON/XOFF Interference
- **Finding**: Binary character `0x13` (Ctrl+S) in JSON can pause the PTY transmission invisibly.

### 3. Native Robustness vs. Script Fragility
- **Comparison**: `planning-with-files` is robust because it uses the platform's native `write_to_file` tool which operates outside the Shell/PTY layer.
- **Lesson**: AI should be the primary writer for heavy content, and the shell should only handle lightweight metadata.

## Consensus Solution: Hybrid V2 Architecture

1.  **AI Direct Write**: AI generates Markdown and uses `write_to_file` directly. No more JSON-to-MD conversion via Python.
2.  **Post-hoc Registry**: A new script `register_handoff.py` reads the MD from disk, validates the format (Linting), and updates the global index.
3.  **Feedback Loop**: If validation fails, the script returns errors, and the AI fixes the file on disk.

## Implementation Findings

### 4. Direct-Write Rewrite Shipped
- Added `session-handoff/scripts/register_handoff.py`.
- Added `session-handoff/scripts/handoff_format.py` to share frontmatter and section parsing.
- Updated `session-handoff/scripts/find_handoff.py` to use the shared parser.
- Rewrote `references/sender-path.md`, `references/handoff-schema.md`, and `references/emit-handoff.md` to document the final Markdown artifact plus registrar flow.
- Deleted `session-handoff/scripts/emit_handoff.py`.

### 5. Registration Contract Verified
- Registrar validates filename shape, required frontmatter, canonical section order, fenced `handoff` blocks, and semantic minimums.
- Registrar normalizes `created_at` from the filename timestamp instead of failing on that mismatch.
- `latest.json` shape remains:
  - `latest`
  - `metadata.project_name`
  - `metadata.workspace_root`
  - `metadata.task_title`
  - `metadata.status`
  - `metadata.next_step`

### 6. Blocking Review Outcome
- Initial blocking review found one real P1:
  - registrar could accept reports outside `<root>/reports` and then write an unusable latest pointer
- Fix applied:
  - registrar now rejects any `--report-path` outside `<root>/reports`
- Follow-up P0/P1 review result:
  - no remaining blocking findings
- Additional external review pressure remained on `regex_extraction_fragility`, but no concrete reproducer from the canonical direct-write sender path was produced.
- Current disposition:
  - keep it as optional future hardening
  - do not treat it as a release-blocking correctness issue

### 7. Verification Evidence
- `python3 -m py_compile` passed for `handoff_format.py`, `find_handoff.py`, and `register_handoff.py`.
- Valid in-root report registration succeeded.
- Large report registration succeeded without freeze.
- Out-of-root report registration is now rejected deterministically.
- `find_handoff.py` successfully resolves and ranks the newly registered reports.

### 8. Package Naming And Residue Cleanup
- The skill directory was renamed from `session-handoff-v1` to `session-handoff`.
- The paired `ai-peer-review/.../session-handoff-v1` artifact directory was renamed to `.../session-handoff`.
- The legacy alias file `references/receive-handoff.md` was removed because `receiver-path.md` is the canonical receiver reference.
- Remaining stale textual references to `session-handoff-v1` were cleared from planning files and review artifacts.
- The schema example no longer uses the old `Codex_Project111` sample values.
