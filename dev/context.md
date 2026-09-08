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

The hook resolves both `dev\` and `.state\` by walking up for a `.git` entry, not
from the raw session cwd -- a session started in `claude-plugins\av-it-toolkit`
still writes its snapshot to the repo root. `cwd` is recorded verbatim in the
snapshot regardless: where the session ran is a separate fact from where its state
belongs. Verified under two real compactions on 2026-09-08, not just a synthetic
stdin redirect. The second run checked the other half: the three `dev/` lines carried
the mtimes as they stood that minute, so the hook stats the files each time rather
than reusing anything from the previous snapshot.

## Where the authority sits

Claude authors hook **source** in `C:\Users\Erik\Claude development\hooks\`; Erik
runs `deploy-hooks.ps1` to install. Claude cannot write into any `.claude` directory
through the remote-device bridge. That is deliberate — hook config is code that runs
on every tool call, so authoring is delegated and the authority over what executes
stays with Erik. The same split applies to commits: Claude commits, Erik
authorizes the merge.

## Shipping a plugin version

Two operations, both required, then restart:

    claude plugin marketplace update erik-local   # refreshes the index only
    claude plugin update av-it-toolkit            # actually installs

Run from the repo root, never a worktree. Verify shipped **content**, not just the
version directory — a stale file under a fresh version number looks correct while the
agent reads old doctrine. `main` is branch-protected, so anything pushed goes via PR.

Protection is a **ruleset**, not classic branch protection -- the
`/branches/main/protection` REST endpoint returns 404 "Branch not protected", which
is not evidence that the branch is open. Read the merge state on the PR instead.

## CI gates the merge

`.github/workflows/ci.yml` has run on every pull request since 2026-07-19. Four jobs:
ubuntu py3.8 and py3.12, macos py3.12, windows py3.12. The three POSIX jobs finish in
13-15s; **windows takes 30-47s and is always the last to land**.

So a merge is not instant, and it can be refused for two different reasons. Read the
PR's `mergeStateStatus` before deciding what to do about it:

- **BLOCKED** -- checks still running. `gh pr merge` fails with "the base branch
  policy prohibits the merge", which reads like a permissions problem and is not one.
  Wait for the windows job. Do not reach for `--admin`.
- **BEHIND** -- checks passed, but `main` moved underneath and the ruleset requires
  the branch be current. `gh pr update-branch <n>` fixes it. That pushes a merge
  commit, which **re-runs the whole matrix**, so the wait happens a second time.

Both happened to PR #11 in sequence: blocked on checks, then behind after PR #10
landed while it waited. On a busy day, update the branch first and wait once.
Neither is the normal case -- PR #14 went green and merged on the first attempt.
Read the state before assuming a problem.

    gh pr view <n> --json mergeStateStatus -q .mergeStateStatus

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

## Concurrent sessions

Other Claude sessions work in this repo and push their own branches (`claude/*`).
A branch that appears on the remote mid-session is not necessarily this session's to
rebase, merge, or delete. Read it if it matters; leave it alone otherwise.
