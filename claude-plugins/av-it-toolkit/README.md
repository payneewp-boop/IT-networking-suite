# av-it-toolkit

Local Claude plugin packaging Erik's two custom skills as a complementary pair,
with the shared environment reference bundled inside instead of pointed at
`/mnt/skills/user/shared/`.

## Contents

```
av-it-toolkit/
├── .claude-plugin/plugin.json     # name, version, description
├── reference/environment.md       # shared context, read by both skills
├── skills/
│   ├── automation-advisor/        # SKILL.md + references/tool-playbooks.md
│   └── documentation-writer/      # SKILL.md + references/templates.md
├── CHANGELOG.md
└── README.md
```

## Why one plugin

Both skills need the same environment facts (licensed tool stack, design
priority order, context boundaries). Bundling `environment.md` inside the
plugin means the pair versions and moves as one unit, with no dependency on a
path outside it — one fewer moving part.

## Install locally

There is no `claude plugin install <path>`. Install via the local marketplace:

```
/plugin marketplace add C:\Users\Erik\IT-networking-suite\claude-plugins
/plugin install av-it-toolkit@erik-local
```

Or load it for one session without installing:

```
claude --plugin-dir C:\Users\Erik\IT-networking-suite\claude-plugins\av-it-toolkit
```

Verify with `claude plugin list`, or `/plugin` → Installed (and the Errors tab).

## Versioning

Bump `version` in `.claude-plugin/plugin.json` and add a `CHANGELOG.md` entry
in the same commit. Semver: patch for wording, minor for new guidance or a new
reference file, major for a changed skill name or removed behavior.

## Maintenance notes

- The `description` frontmatter in each SKILL.md drives triggering — edit it
  deliberately and re-test with a few realistic prompts after any change.
