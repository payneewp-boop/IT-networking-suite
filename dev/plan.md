# Plan

Current arc: make the Claude Code setup survive its own context limits, then build
the two AV skills that do real work. Updated 2026-09-07.

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
- **Per-project `.state`, derived from `$hook.cwd`.** A hardcoded root would pool
  snapshots from every repo into this one. Caught in review.
- **Catch-all `exit 0`.** A hook that fails loudly mid-compaction stalls the session;
  a missing snapshot is an inconvenience. The cost is real — this swallowed a genuine
  error through two debug rounds. Accepted: if snapshots stop appearing, the absence
  is the signal.
- **All three `dev/` names reported individually**, with `MISSING` where absent. The
  MISSING line is the informative one — it says the scaffolding was never written.

Verified end to end against a manual compaction; first snapshot 2026-09-07 21:18.

## Phase 2 — scaffolding and hygiene  (in progress)

- [x] `dev/` written at the repo root
- [ ] Hook resolves `dev/` from the git root, not the raw session cwd — see tasks.md
- [ ] Five CLAUDE.md blocks handed over as one paste-ready block
- [ ] PR #4 merged; stale worktree at `claude-plugins/av-it-toolkit/.claude/worktrees/`
      removed once no session holds it
- [ ] Connector prune on claude.ai — low value, tidies the web UI only

## Phase 3 — the AV skills  (next)

`signal-flow-doc` first. It turns a single room walkthrough into a Rooms record plus
its Devices rows in one pass, which is the highest-leverage thing on the list: it is
the step that currently doesn't happen, so rooms stay undocumented.

`dante-diagnostics` second, because it is only useful once rooms and devices exist to
diagnose against.

Both write to Notion and both follow the `ROOM-DEVICE-PORT` label standard.
Design priority order stays: reliability > simplicity > maintainability > cost > scalability.
