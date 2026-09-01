# Tool Playbooks

Concrete starting patterns and common gotchas for each preferred tool. Read the
relevant section before writing implementation steps so guidance is specific.
Pick the lightest tool that solves the problem — a formula beats a script, a
filter beats a cron job.

## Table of contents
- [Gmail](#gmail)
- [Google Sheets & Forms](#google-sheets--forms)
- [Google Apps Script](#google-apps-script)
- [Excel & Power Query](#excel--power-query)
- [PowerShell & Command Prompt](#powershell--command-prompt)
- [Python](#python)
- [Choosing between tools](#choosing-between-tools)

---

## Gmail

**Good for:** auto-labeling, archiving noise, routing, templated replies, cleanup.

**Filters (native, no code):**
- Build from a search first (`from:`, `subject:`, `has:attachment`,
  `older_than:30d`), verify it matches the right mail, then "Create filter."
- Common actions: apply label, skip inbox (archive), mark read, never send to
  spam, forward, delete.
- One filter can apply a label AND archive in the same rule — no need for two.

**Templates:** enable Settings → Advanced → Templates for canned replies.

**Gotchas:**
- Filters apply going forward. To also process existing mail, run the same
  search, select all, and apply the label/archive manually once.
- `older_than:`/`newer_than:` accept `d`, `m`, `y` (e.g. `older_than:6m`).
- Filters can't do conditional logic or scheduling — escalate to Apps Script
  when you need "if X then do Y on a schedule."

## Google Sheets & Forms

**Good for:** inventory, intake, dashboards, lookups, light reporting.

**Reach for these before scripting:**
- `QUERY()` — SQL-like slicing for dashboards/summaries.
- `FILTER()`, `SORTN()`, `UNIQUE()` — dynamic subsets without helper columns.
- `XLOOKUP()` (or `INDEX/MATCH`) — lookups; avoid fragile `VLOOKUP` column
  offsets.
- Data → Data validation — dropdowns and input rules to stop bad entries at the
  source.
- Named ranges — make formulas readable and stable when rows shift.

**Forms:** use Forms for structured intake so data lands clean in a linked
Sheet — no re-typing, and every field is standardized by design.

**Gotchas:**
- Volatile functions (`NOW`, `TODAY`, big `ARRAYFORMULA` chains) slow large
  sheets. Cache to static values when history doesn't need to recalc.
- Guard against error spam with `IFERROR()` around lookups.

## Google Apps Script

**Good for:** scheduled jobs, Gmail+Sheets automation, auto-generated reports,
anything filters/formulas can't reach.

**Pattern:**
- Extensions → Apps Script from the host Sheet/Doc.
- Triggers (clock icon) run functions on a schedule (e.g. daily digest, weekly
  cleanup) — no server needed.
- Keep functions small and single-purpose; log with `console.log()` and check
  Executions for failures.

**Gotchas:**
- Quotas exist (script runtime, daily email sends, trigger count). Fine for
  small-shop volume; note the ceiling if the user scales up.
- First run prompts for OAuth authorization — expected, not an error.
- Wrap external calls in `try/catch` and log failures so a silent break is
  visible.

## Excel & Power Query

**Good for:** repeatable data cleanup, merging files, refreshable reports on
Windows.

**Power Query (Data → Get & Transform):**
- Import → transform (split, trim, unpivot, filter, type) → load. Steps are
  recorded, so next month you just hit **Refresh** instead of redoing cleanup.
- Merge queries = a maintainable join across files/tabs without lookup formulas.
- Append queries = stack many files (e.g. monthly exports) into one table.

**Gotchas:**
- Source file paths/column names are load-bearing — renaming a column upstream
  breaks the query. Keep source layout stable or handle with a rename step.
- Prefer Power Query over VBA for data shaping; reserve VBA for UI/automation
  Power Query can't do.

## PowerShell & Command Prompt

**Good for:** Windows file/system tasks, batch renames, log parsing, scheduled
IT jobs, network/asset checks.

**Patterns:**
- Bulk file ops: `Get-ChildItem | Where-Object {...} | Rename-Item / Copy-Item`.
- Export structured output: `... | Export-Csv report.csv -NoTypeInformation`.
- Schedule with Task Scheduler pointing at a `.ps1`.

**Gotchas:**
- Execution policy can block scripts. For a one-off, run
  `powershell -ExecutionPolicy Bypass -File script.ps1` rather than weakening the
  machine-wide policy.
- Always dry-run destructive commands with `-WhatIf` first.
- Batch (`.bat`) is fine for trivial glue; use PowerShell once there's any logic,
  filtering, or structured output.

## Python

**Good for:** heavier data work, API calls, cross-platform scripting, anything
Sheets/PowerShell make awkward.

**Reach for:** `pandas` (tabular cleanup/merges), `requests` (APIs), `pathlib`
(files), `openpyxl` (write .xlsx), standard `csv`/`json`.

**Gotchas:**
- Add a dependency list (`requirements.txt`) and a one-line run command so it's
  reproducible on another machine.
- Log actions and wrap I/O in `try/except` so failures are visible, not silent.
- Don't default to Python when a native tool already does the job — it adds an
  install/runtime dependency to maintain.

## Choosing between tools

| Situation | Reach for |
|---|---|
| Auto-sort / clean up mail | Gmail filters |
| Structured data entry | Google Forms → Sheets |
| Dashboards, lookups, small reports | Sheets formulas (`QUERY`, `XLOOKUP`) |
| Scheduled Gmail/Sheets job or auto-report | Apps Script |
| Repeatable file/data cleanup on Windows | Excel Power Query |
| Windows file/system/IT automation | PowerShell |
| APIs, big data, cross-platform logic | Python |

When two tools tie, pick the one already in the user's daily workflow — the
fewer new things to learn and maintain, the more likely the automation survives.
