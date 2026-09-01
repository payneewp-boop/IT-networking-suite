# Changelog

All notable changes to `av-it-toolkit`.

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
