# Plan

Current arc: make the Claude Code setup survive its own context limits, then build
the two AV skills that do real work. Updated 2026-09-08.
That arc is complete; see **Where this stands** at the end.

## Phase 0 — ship the plugin  (done 2026-09-06)

`environment.md` shipped as av-it-toolkit v0.1.2 and verified by content, not just
version number. Root cause of the two-version-stale cache found: `plugin marketplace
update` and `plugin update` are separate operations and only the second installs.
Recorded to memory as `plugin-ship-sequence`.

## Phase 1 — PreCompact snapshot  (done 2026-09-07)

A hook that writes structured facts to a gitignored `.state/` when compaction fires,
so the next session knows what project was live and whether `dev/` was current.

Settled design decisions, so they don't get relitigated:

- **Pointers, not content.** The `dev/` files are the authoritative copy; copying
  them into the snapshot creates a second copy that can silently disagree.
- **Never raw transcript.** Structured facts only, per the credentials doctrine.
- **Per-project `.state`.** A hardcoded root would pool snapshots from every repo
  into this one. Caught in review. *Amended 2026-09-08:* derived by walking up from
  `$hook.cwd` to the `.git` entry, not from the cwd itself -- a session started in a
  subdirectory was reporting `dev/` MISSING while it sat one level up. The principle
  held; the derivation was wrong.
- **Catch-all `exit 0`.** A hook that fails loudly mid-compaction stalls the session;
  a missing snapshot is an inconvenience. The cost is real — this swallowed a genuine
  error through two debug rounds. Accepted: if snapshots stop appearing, the absence
  is the signal.
- **All three `dev/` names reported individually**, with `MISSING` where absent. The
  MISSING line is the informative one — it says the scaffolding was never written.

Verified end to end against a manual compaction; first snapshot 2026-09-07 21:18.
Re-verified after the git-root amendment on 2026-09-08 -- a real compaction this
time, not a synthetic stdin redirect, which is the only test that exercises the
hook as the harness actually calls it.

## Phase 2 — scaffolding and hygiene  (done 2026-09-07)

- [x] `dev/` written at the repo root and committed (PR #4)
- [x] Hook resolves `dev/` and `.state/` from the git root, not the raw session cwd
- [x] Stale worktree and its branch cleared; both were contained in main
- [x] Two CLAUDE.md inserts pasted (2026-09-08). Erik installed them and corrected
      the draft in passing; he also wrote *Resuming work* and *Compaction* sections
      that were not in it.
- [ ] Connector prune on claude.ai — low value, tidies the web UI only

The five-block CLAUDE.md item resolved to two. The other three (PowerShell traps,
execution policy, the working-state convention) are written in `context.md`, and
duplicating them into CLAUDE.md would create a second copy that can silently
disagree — the same failure the hook's pointers-not-content rule avoids.

## Phase 3 — the AV skills  (done 2026-09-07)

Shipped as av-it-toolkit 0.1.3 and 0.1.4. Four skills, audit clean.

`signal-flow-capture` (PR #5) turns one room walkthrough into Rooms + Devices
records. Named `-capture`, not `-doc`: it and `documentation-writer` are
same-family siblings, and "doc" in both names routes badly, so the distinguishing
verb goes where selection actually reads it. Scoped to capture; prose stays with
`documentation-writer`.

`structured-troubleshooting` (PR #6) diagnoses a fault and logs it. Doctrine had
routed to this skill since 0.1.2 while it did not exist — the routing table named
a destination that could never be selected.

Both write to Notion with the room relation set, because an unrelated page is
orphaned and will not surface on the room it concerns.

`dante-diagnostics` is **not** being built next. Dante failure modes already sit
inside `structured-troubleshooting`, and a fifth same-family skill pays
discovery-tier rent every session against an existing 15% sibling overlap. The
trigger to revisit is a real Dante fault that the current coverage handles badly.

## What to watch

Always-on metadata cost is ~810 est. tokens across four skills, paid every session
before any work starts. Size on disk is not the cost — the description is. Check
that number before adding a skill, not the line count.

## Where this stands

Phases 0-3 are closed. Nothing is queued behind them, and that is deliberate: the
next thing to build should come from a real fault or a real repetition, not from the
momentum of having just shipped something.

Open items live in `tasks.md`, and there is one -- the derivation line in chat
preferences. Everything else is either done or parked with a stated trigger.

Two facts learned late in the arc, both now in `context.md` because they are
operational rather than plan-shaped: CI gates every PR and refuses a merge two
different ways, and `main` is protected by a ruleset that makes the classic
protection endpoint return a misleading 404.
