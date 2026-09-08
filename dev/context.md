# Context

Durable orientation for this repo. Read this first after a compaction or a cold start.
Changes rarely — if something here is only true this week, it belongs in `plan.md`.

## What this repo is

`IT-networking-suite` holds the AV/IT tooling: the `netagent` Python package, the
`av-it-toolkit` Claude Code plugin under `claude-plugins/`, and hook sources under
`claude-hooks/`. The plugin ships doctrine and skills; the package does the scanning.

## System of record

Notion, per `claude-plugins/av-it-toolkit/reference/environment.md`. Rooms, Devices,
Config records, Troubleshooting log and SOPs all live there — not in Google Drive,
which it supersedes, and not in this repo.

The named exception is this directory. `dev/plan.md`, `dev/context.md` and
`dev/tasks.md` are local working state and do not go to Notion. That exception is
what makes the PreCompact hook meaningful: it reports on these three files by name.

## Where the authority sits

Claude authors hook **source** in `C:\Users\Erik\Claude development\hooks\`; Erik
runs `deploy-hooks.ps1` to install. Claude cannot write into any `.claude` directory
through the remote-device bridge. That is deliberate — hook config is code that runs
on every tool call, so authoring is delegated and the authority over what executes
stays with Erik. The same split applies to commits: Claude proposes, Erik says the
word.

## Shipping a plugin version

Two operations, both required, then restart:

    claude plugin marketplace update erik-local   # refreshes the index only
    claude plugin update av-it-toolkit            # actually installs

Run from the repo root, never a worktree. Verify shipped **content**, not just the
version directory — a stale file under a fresh version number looks correct while the
agent reads old doctrine. `main` is branch-protected, so anything pushed goes via PR.

## Environment facts that have cost time

- Windows PowerShell 5.1 only; `pwsh` (7.x) is not installed on this machine.
- `&&` is not a statement separator in PowerShell — use `;` or the Bash tool.
- `Set-Content -Encoding UTF8` on 5.1 prepends a BOM. For anything a parser reads
  first-byte-sensitively (settings.json, SKILL.md fixtures), write BOM-less via
  `[System.IO.File]::WriteAllText(..., New-Object System.Text.UTF8Encoding($false))`.
- `[Console]::In.ReadToEnd()` reads a real stdin redirect but is *not* populated by a
  PowerShell pipeline. Smoke-test hooks with `< file`, not with `|`.
- CurrentUser execution policy is RemoteSigned (set 2026-09-07). If Group Policy ever
  sets MachinePolicy or UserPolicy it overrides that; the fallback is
  `-ExecutionPolicy Bypass` per invocation, never a weaker machine-wide policy.

## Credentials

Never printed, echoed, or written. Transcripts are plaintext JSONL under
`~/.claude/projects/` and cannot be un-written. A secret occupies two places only:
its environment variable, and the HTTPS body going to its own issuer. Rotation is
Erik's, never Claude's.
