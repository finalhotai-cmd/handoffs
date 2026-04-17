# Sender Workflow

The canonical sender workflow is:

1. Write the final handoff Markdown file directly into `$HOME/0-handoff/reports/`.
2. Run `python3 scripts/register_handoff.py --report-path /abs/path/to/report.md`.
3. If validation fails, repair the file and rerun the registrar.

There is no supported stdin JSON emitter path.
