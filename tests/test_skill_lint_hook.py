"""Tests for claude-hooks/skill-frontmatter-lint.py, run the way Claude Code runs it.

The hook is a script, not part of the netagent package, so each test writes a
SKILL.md into a temp directory and pipes a PostToolUse payload to the script in
a subprocess. That exercises the real contract: stdin JSON in, exit code and
stdout/stderr out.

The source of record for the hook is claude-development/hooks/. This copy went
six weeks without the keys added there, and nothing noticed; the recognised-key
cases below are what would have.
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

HOOK = Path(__file__).resolve().parent.parent / "claude-hooks" / "skill-frontmatter-lint.py"

BODY = (
    "This body has enough words in it to pass the thin body check that the "
    "linter applies to every skill file it is handed by the hook.\n"
)
DESCRIPTION = "Test fixture. Use when checking how the frontmatter linter reads a skill."


def skill_text(name="demo-skill", description=DESCRIPTION, extra="", body=BODY):
    lines = ["---", "name: %s" % name]
    if description is not None:
        lines.append("description: %s" % description)
    if extra:
        lines.append(extra)
    lines.append("---")
    return "\n".join(lines) + "\n" + body


class SkillLintHookTests(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def run_hook(self, text, dir_name="demo-skill", file_name="SKILL.md"):
        skill_dir = self.root / dir_name
        skill_dir.mkdir(exist_ok=True)
        path = skill_dir / file_name
        path.write_text(text, encoding="utf-8")
        payload = {"tool_name": "Write", "tool_input": {"file_path": str(path)}, "cwd": str(self.root)}
        # The hook's messages contain an em dash; pin the encoding so the
        # Windows runner's console code page cannot change what we read back.
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        proc = subprocess.run(
            [sys.executable, str(HOOK)],
            input=json.dumps(payload).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            timeout=30,
        )
        return proc.returncode, proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8")

    def test_clean_skill_is_silent(self):
        code, out, err = self.run_hook(skill_text())
        self.assertEqual((code, out, err), (0, "", ""))

    def test_documented_and_local_keys_are_recognised(self):
        # context/agent/background: the isolation trio from
        # code.claude.com/docs/en/skills. compatibility: the local convention
        # for runtime prerequisites. Each was once called a typo here.
        for extra in ("context: fork", "agent: general-purpose", "background: true",
                      "compatibility: Python 3.9+"):
            with self.subTest(extra=extra):
                code, out, err = self.run_hook(skill_text(extra=extra))
                self.assertEqual((code, out, err), (0, "", ""))

    def test_unknown_key_still_warns(self):
        code, out, err = self.run_hook(skill_text(extra="colour: blue"))
        self.assertEqual(code, 0)
        self.assertIn("unrecognized frontmatter key: colour", json.loads(out)["systemMessage"])

    def test_name_not_matching_directory_is_an_error(self):
        code, out, err = self.run_hook(skill_text(name="other-name"))
        self.assertEqual(code, 2)
        self.assertIn("does not match parent directory 'demo-skill'", err)

    def test_missing_description_is_an_error(self):
        code, out, err = self.run_hook(skill_text(description=None))
        self.assertEqual(code, 2)
        self.assertIn("missing required key: description", err)

    def test_other_files_are_ignored(self):
        code, out, err = self.run_hook("not frontmatter at all", file_name="README.md")
        self.assertEqual((code, out, err), (0, "", ""))


if __name__ == "__main__":
    unittest.main()
