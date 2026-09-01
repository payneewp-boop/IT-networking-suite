#!/usr/bin/env python3
"""
skill-frontmatter-lint.py — Claude Code PostToolUse hook

Purpose
    Validates SKILL.md frontmatter immediately after Claude writes or edits it,
    and reports problems back to Claude so it can self-correct in the same turn.

Trigger
    PostToolUse, matcher "Write|Edit". Exits silently (0) for any file that is
    not named SKILL.md, so it is safe to leave enabled globally.

Contract
    stdin  : PostToolUse JSON (tool_name, tool_input.file_path, cwd, ...)
    stdout : JSON {"systemMessage": "..."} on pass-with-warnings
    stderr : findings, with exit 2, when there are errors (shown to Claude)
    exit   : 0 = clean or warnings only
             2 = errors found; stderr is surfaced to Claude
             1 = hook itself failed (never blocks, never lies about the file)

Design notes
    - Zero dependencies. Deliberately does NOT import PyYAML: skill frontmatter
      is flat key/value plus occasional inline lists, and a hook that crashes on
      a missing import is worse than a hook that parses a narrow grammar well.
      If frontmatter ever needs nested YAML, revisit this decision explicitly.
    - Fails open. Any unexpected exception exits 1 with a note rather than
      exit 2, so a bug in the linter never masquerades as a bad skill file.
"""

import json
import os
import re
import sys

MAX_NAME_LEN = 64
MAX_DESC_LEN = 1024

# Keys the linter recognizes. Unknown keys are warnings, not errors — the
# format gains fields over time and a hard failure here would age badly.
KNOWN_KEYS = {
    "name",
    "description",
    "allowed-tools",
    "disable-model-invocation",
    "argument-hint",
    "model",
    "license",
    "version",
    "metadata",
}

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def parse_frontmatter(text):
    """Return (dict_of_keys, body_text, error_or_None).

    Handles the flat `key: value` grammar used by SKILL.md, including inline
    lists (`allowed-tools: [Read, Grep]`) and quoted values. Continuation lines
    (indented) are appended to the previous key so wrapped descriptions parse.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text, "file does not start with a '---' frontmatter fence"

    close = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            close = i
            break
    if close is None:
        return {}, text, "frontmatter block is never closed with '---'"

    keys = {}
    last = None
    for raw in lines[1:close]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[:1] in (" ", "\t") and last:
            keys[last] = (keys[last] + " " + raw.strip()).strip()
            continue
        if ":" not in raw:
            return {}, text, "malformed frontmatter line: %r" % raw
        key, _, value = raw.partition(":")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        keys[key] = value
        last = key

    body = "\n".join(lines[close + 1:])
    return keys, body, None


def lint(path):
    """Return (errors, warnings)."""
    errors, warnings = [], []

    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        return ["cannot read file: %s" % exc], []

    keys, body, parse_error = parse_frontmatter(text)
    if parse_error:
        return [parse_error], []

    # --- name -------------------------------------------------------------
    # This is the check that earns the hook: the skill name must equal its
    # parent directory name, or the skill silently fails to resolve.
    dir_name = os.path.basename(os.path.dirname(os.path.abspath(path)))
    name = keys.get("name", "")

    if not name:
        errors.append("missing required key: name")
    else:
        if name != dir_name:
            errors.append(
                "name '%s' does not match parent directory '%s' — the skill "
                "will not resolve. Rename one to match the other." % (name, dir_name)
            )
        if not NAME_RE.match(name):
            errors.append(
                "name '%s' is not lowercase kebab-case (a-z, 0-9, single "
                "hyphens)" % name
            )
        if len(name) > MAX_NAME_LEN:
            errors.append("name is %d chars; limit is %d" % (len(name), MAX_NAME_LEN))

    # --- description ------------------------------------------------------
    desc = keys.get("description", "")
    if not desc:
        errors.append(
            "missing required key: description — without it the model cannot "
            "decide when to invoke this skill"
        )
    else:
        if len(desc) > MAX_DESC_LEN:
            errors.append(
                "description is %d chars; limit is %d" % (len(desc), MAX_DESC_LEN)
            )
        if len(desc) < 40:
            warnings.append(
                "description is very short (%d chars) — state both what the "
                "skill does and when to use it" % len(desc)
            )
        if not re.search(r"\b(use|when|trigger)\b", desc, re.I):
            warnings.append(
                "description does not say WHEN to use the skill — model "
                "invocation depends on this"
            )

    # --- structure --------------------------------------------------------
    for key in sorted(set(keys) - KNOWN_KEYS):
        warnings.append("unrecognized frontmatter key: %s (typo?)" % key)

    if not body.strip():
        errors.append("skill body is empty — frontmatter alone does nothing")
    elif len(body.split()) < 20:
        warnings.append("skill body is very thin (%d words)" % len(body.split()))

    return errors, warnings


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # not a hook invocation we understand; stay out of the way

    path = (payload.get("tool_input") or {}).get("file_path") or ""
    if os.path.basename(path).lower() != "skill.md":
        sys.exit(0)

    errors, warnings = lint(path)
    rel = os.path.relpath(path, payload.get("cwd") or os.getcwd())

    if errors:
        print("SKILL.md frontmatter errors in %s:" % rel, file=sys.stderr)
        for item in errors:
            print("  ERROR  %s" % item, file=sys.stderr)
        for item in warnings:
            print("  warn   %s" % item, file=sys.stderr)
        print("Fix these before continuing.", file=sys.stderr)
        sys.exit(2)

    if warnings:
        json.dump(
            {
                "systemMessage": "SKILL.md lint (%s): %s"
                % (rel, "; ".join(warnings))
            },
            sys.stdout,
        )
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # fail open — never fake a lint failure
        print("skill-frontmatter-lint hook failed: %s" % exc, file=sys.stderr)
        sys.exit(1)
