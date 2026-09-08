# Changelog

All notable changes to `av-it-toolkit`.

## [0.1.3] - 2026-09-07

### Added
- `signal-flow-capture` skill: turns one room walkthrough into a Rooms page plus
  a Devices page per box, each with a ROOM-DEVICE-PORT label and the room
  relation set. Scoped to capture only -- prose stays with
  `documentation-writer`. Named `-capture`, not `-doc`, so the distinguishing
  verb sits in the name where skill routing reads it.
- `references/record-shapes.md`: field tables for both databases, the Dante
  subscription table, and the fields deliberately excluded (serials, firmware).

### Fixed
- Both existing skills pointed at `../../reference/environment.md`, which
  escapes the skill directory and did not resolve from inside the bundle. An
  agent following that instruction failed the read. Now
  `${CLAUDE_PLUGIN_ROOT}/reference/environment.md`.

### Changed
- `plugin.json` description no longer says "paired" -- there are three skills.

## [0.1.2] - 2026-09-06

Backfilled: this version shipped without a changelog entry.

### Changed
- `reference/environment.md`: Notion designated system of record, superseding
  Google Drive; added the database map, the relation requirement, the
  ROOM-DEVICE-PORT label standard, the `dev/` working-state exception and the
  six-month promotion rule.

## [0.1.1] - 2026-09-01

### Changed
- `reference/environment.md` confirmed accurate by Erik; removed the
  "reconstructed, verify before relying on it" banner and the open-items
  section. The file is now authoritative.

## [0.1.0] - 2026-09-01

### Added
- Initial packaging of `automation-advisor` and `documentation-writer` as one
  versioned local plugin.
- `reference/environment.md` bundled inside the plugin (previously referenced
  from `/mnt/skills/user/shared/`); content reconstructed from stated
  preferences and marked for verification.
- Pointer to the bundled reference added to the top of both SKILL.md bodies
  (relative path; `${CLAUDE_PLUGIN_ROOT}` does not expand in SKILL.md body text).
- `claude-plugins/.claude-plugin/marketplace.json` so the plugin can be installed
  from a local marketplace.
