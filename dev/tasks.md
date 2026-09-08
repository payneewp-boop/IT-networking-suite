# Tasks

Short-horizon and concrete. Anything that needs a paragraph of justification belongs
in `plan.md`. Updated 2026-09-08.

## Now

- [ ] Add the derivation line to chat preferences.

## Someday

- [ ] Connector prune on claude.ai. Tidies the web UI; negligible effect on Claude
      Code, where only five account connectors inject tools.
- [ ] `dante-diagnostics` — **not yet, deliberately.** Dante failure modes (clock
      contention, subscription vs. presence, primary/secondary, sample-rate mismatch)
      are already inside `structured-troubleshooting`. A fifth same-family skill pays
      discovery-tier rent every session against an existing 15% sibling overlap.
      Build it when a real Dante fault shows where the current coverage is thin —
      not before.
- [ ] Watch the always-on metadata cost. Four skills currently cost ~810 est. tokens
      before any work starts, paid whether they fire or not. That is the number to
      check before adding a fifth, not the size of the skill on disk.

## Done

- [x] 2026-09-08 Second real compaction confirmed the hook reads live mtimes.
      The new snapshot landed beside the first at the repo root, recorded the same
      plugin-subdirectory cwd, and carried the three `dev/` timestamps as they stood
      that minute -- 17:34, 16:42, 15:14. The first run proved the files were found;
      this one proves nothing is cached between runs. Hook work closed.
- [x] 2026-09-08 CLAUDE.md updated: hook source, the `<repo>\dev\` pointer, and a
      Hooks and plugins section carrying the authority split and the two-command ship
      sequence. Erik pasted it; Claude drafted only -- the file sits under `.claude`,
      which is the same boundary the section itself describes. He also added Resuming
      work and Compaction sections that were not in the draft.
- [x] 2026-09-08 Verified the git-root fix under a **real** compaction, not a
      synthetic stdin redirect. Session cwd was two levels down in
      `claude-plugins\av-it-toolkit`; the snapshot landed at the repo root with all
      three `dev/` files timestamped, and recorded the true cwd verbatim. That was
      the last thing standing between the fix and calling it proven.
- [x] 2026-09-08 Deleted the pre-fix snapshot and the plugin's now-empty `.state/`.
      It held three `MISSING` lines for files that existed one directory up -- the
      defect's fingerprint, worth seeing once and not worth keeping.
- [x] 2026-09-08 Pruned the plugin cache to 0.1.4 alone (479K -> 90K). The live
      bundle was checked byte-for-byte against repo source first, so the prune
      removed only superseded copies.
- [x] 2026-09-07 av-it-toolkit 0.1.4: `structured-troubleshooting` built and shipped.
      Doctrine had routed to it since 0.1.2 while it did not exist, so the routing
      table named a destination that could never be selected. (PR #6)
- [x] 2026-09-07 av-it-toolkit 0.1.3: `signal-flow-capture` built and shipped. Named
      `-capture`, not `-doc`, so the distinguishing verb sits in the name where skill
      routing reads it. (PR #5)
- [x] 2026-09-07 Fixed four live audit errors: both original skills pointed at
      `../../reference/environment.md`, which escapes the skill directory and did not
      resolve from inside the bundle. An agent following that instruction failed the
      read and improvised. Now `${CLAUDE_PLUGIN_ROOT}`.
- [x] 2026-09-07 Backfilled the 0.1.2 CHANGELOG entry, which had shipped without one.
- [x] 2026-09-07 Hook resolves `dev/` and `.state/` from the git root, not the raw
      session cwd. Verified against three start directories.
- [x] 2026-09-07 `dev/` scaffolding written and committed. (PR #4)
- [x] 2026-09-07 Cleared the stale worktree and its branch; both were fully contained
      in main, so nothing was lost.
- [x] 2026-09-07 PreCompact hook written, wired, installed, verified against a real
      compaction.
- [x] 2026-09-07 Fixed the BOM false-green in the `-Verify` lint fixture. It had been
      passing for the wrong reason, so the kebab-case rule had never once been tested.
- [x] 2026-09-07 CurrentUser execution policy set to RemoteSigned.
- [x] 2026-09-06 Diagnosed the plugin ship sequence; recorded to memory.
