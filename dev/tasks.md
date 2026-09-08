# Tasks

Short-horizon and concrete. Anything that needs a paragraph of justification belongs
in `plan.md`. Updated 2026-09-07.

## Now

- [ ] **Hook: resolve `dev/` from the git root.** `precompact-snapshot.ps1` uses
      `$hook.cwd` verbatim, so a session started in `claude-plugins/av-it-toolkit`
      reports all three files MISSING even though they exist at the repo root. Walk
      up for a `.git` entry and fall back to `cwd` when there is none. `.state/`
      should stay keyed to the same resolved root. Edit the source in
      `Claude development\hooks\`, then Erik runs `deploy-hooks.ps1`.
- [ ] **Hand over the five CLAUDE.md blocks** as one paste-ready block.
- [ ] **Decide whether `dev/` is committed or ignored.** Currently untracked and not
      ignored, which is the one state that is definitely wrong. `.state/` is ignored
      because it is machine-local churn; these three are hand-written intent and
      probably want history.

## Next

- [ ] Merge PR #4 (`gitignore-state-and-worktree`).
- [ ] Remove `claude-plugins/av-it-toolkit/.claude/worktrees/` once no session holds
      it. Already gitignored, so this is disk hygiene, not correctness.
- [ ] Add the derivation line to chat preferences.
- [ ] Draft `signal-flow-doc`.

## Someday

- [ ] Connector prune on claude.ai. Tidies the web UI; negligible effect on Claude
      Code, where only five account connectors inject tools.

## Done

- [x] 2026-09-07 PreCompact hook written, wired, installed, verified against a real
      compaction.
- [x] 2026-09-07 Fixed the BOM false-green in the `-Verify` lint fixture. It had been
      passing for the wrong reason, so the kebab-case rule had never once been tested.
- [x] 2026-09-07 CurrentUser execution policy set to RemoteSigned.
- [x] 2026-09-06 Diagnosed the plugin ship sequence; recorded to memory.
