# SKILL.md Frontmatter Lint Hook — Install & Reference

**Component:** `skill-frontmatter-lint.py`
**Event:** `PostToolUse`, matcher `Write|Edit`
**Purpose:** Catch the name-error class of SKILL.md bug at write time instead of at invocation time.
**Assumption flagged:** written in Python for cross-platform behavior (Windows and Linux wiring both given below). Zero third-party dependencies — stdlib only.

---

## 1. Why a hook and not an instruction

An instruction in `CLAUDE.md` asking Claude to check frontmatter is advisory — it competes with everything else in context and gets dropped under load. A hook is deterministic: it runs on every matching write, with no model judgment involved. That is the whole reason to spend a hook on this.

`PostToolUse` cannot *prevent* the write (the tool has already run), but exit code 2 pushes stderr straight back to Claude, which then corrects the file in the same turn. In practice that's the same outcome with less friction than a `PreToolUse` block.

---

## 2. What it checks

| Severity | Check |
|---|---|
| **Error** | `name` missing |
| **Error** | `name` ≠ parent directory name — *this is the bug that bit you; the skill silently fails to resolve* |
| **Error** | `name` not lowercase kebab-case, or over 64 chars |
| **Error** | `description` missing, or over 1024 chars |
| **Error** | Frontmatter fence missing, unclosed, or malformed |
| **Error** | Skill body empty |
| Warn | `description` under 40 chars |
| Warn | `description` never says *when* to use the skill (model invocation depends on this) |
| Warn | Unrecognized frontmatter key (catches typos like `descriptoin`) |
| Warn | Body under 20 words |

Errors → exit 2, findings on stderr, Claude fixes it.
Warnings only → exit 0 with a `systemMessage`, non-disruptive.
Any file not named `SKILL.md` → exit 0 immediately, no output. Safe to enable globally.

---

## 3. Design decisions worth knowing

**No PyYAML.** Skill frontmatter is flat `key: value` with occasional inline lists. A hook that crashes on a missing import is worse than one that parses a narrow grammar correctly. If frontmatter ever needs nested YAML, that decision gets revisited deliberately rather than by accident.

**Fails open.** Any unexpected exception exits **1**, not 2. A bug in the linter will never masquerade as a bad skill file. This matters: a false positive here trains you to ignore the hook, which is worse than having no hook.

**Warnings are not errors.** Unknown keys warn rather than fail, because the SKILL.md format gains fields over time and a hard failure would age badly.

---

## 4. Install

### 4.1 Place the script

**Windows**

```
%USERPROFILE%\.claude\hooks\skill-frontmatter-lint.py
```

**Linux / macOS**

```bash
mkdir -p ~/.claude/hooks
cp skill-frontmatter-lint.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/skill-frontmatter-lint.py
```

### 4.2 Wire it in `~/.claude/settings.json` (Windows: `%USERPROFILE%\.claude\settings.json`)

**Windows**

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python \"%USERPROFILE%\\.claude\\hooks\\skill-frontmatter-lint.py\"",
            "timeout": 15,
            "statusMessage": "Linting SKILL.md"
          }
        ]
      }
    ]
  }
}
```

**Linux / macOS**

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 $HOME/.claude/hooks/skill-frontmatter-lint.py",
            "timeout": 15,
            "statusMessage": "Linting SKILL.md"
          }
        ]
      }
    ]
  }
}
```

If you already have a `hooks` block, add the object to the existing `PostToolUse` array rather than replacing it.

### 4.3 Scope choice

`~/.claude/settings.json` (user scope) is the right home here — you author skills across all three of your contexts, so a project-scoped hook would only cover one. Use `.claude/settings.json` in a repo only if you later want a stricter project-specific ruleset.

---

## 5. Verify

Create a deliberately broken skill and confirm the hook fires:

```bash
mkdir -p /tmp/lint-test/bad-name
printf -- '---\nname: bad_Name\ndescription: short\n---\nBody.\n' > /tmp/lint-test/bad-name/SKILL.md
printf '{"tool_name":"Write","cwd":"/tmp/lint-test","tool_input":{"file_path":"/tmp/lint-test/bad-name/SKILL.md"}}' \
  | python3 ~/.claude/hooks/skill-frontmatter-lint.py; echo "exit=$?"
```

Expected: two ERROR lines (name mismatch, not kebab-case), three warnings, `exit=2`.

Then confirm the no-op path:

```bash
printf '{"tool_name":"Write","cwd":"/tmp","tool_input":{"file_path":"/tmp/notes.md"}}' \
  | python3 ~/.claude/hooks/skill-frontmatter-lint.py; echo "exit=$?"
```

Expected: no output, `exit=0`.

Finally, run `/doctor` in Claude Code to confirm the hook is registered and parsing.

**Verification status:** all five cases (valid skill, name mismatch, missing fence, warnings-only, non-skill file) were executed against this script and produced the documented output before handoff.

---

## 6. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Hook never fires | `matcher` typo, or settings.json invalid JSON | `/doctor`; validate the JSON |
| `python: command not found` | Not on PATH for the hook's shell | Use the absolute interpreter path in `command` |
| Fires on every markdown write | Wrong script installed | The filename check is `basename == "skill.md"`; confirm you copied the right file |
| Exit 1 with "hook failed" | Bug in the linter, *not* in your skill | Read the stderr message; the file itself was not judged |
| Windows path errors | Backslash escaping in JSON | Backslashes must be doubled: `\\.claude\\hooks\\` |

---

## 7. Next steps

1. Install at user scope and verify with §5.
2. Run it once against your existing skills to sweep for the name bug retroactively:
   `for f in ~/.claude/skills/*/SKILL.md; do printf '{"tool_name":"Write","cwd":"'"$HOME"'","tool_input":{"file_path":"'"$f"'"}}' | python3 ~/.claude/hooks/skill-frontmatter-lint.py; done`
3. Once this proves out, add the companion `PostToolUse` formatting hook and the `PreToolUse` destructive-command guardrail from the harness reference.

---

## Sources

- [Claude Code hooks reference](https://code.claude.com/docs/en/hooks)
- [Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [Steering Claude Code: CLAUDE.md, skills, hooks, rules, subagents](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more)
