"""Tests for CLI argument wiring (including the --json flag on every agent)."""

import io
import unittest
from contextlib import redirect_stdout

from netagent import util
from netagent.cli import build_parser


class JsonFlagTests(unittest.TestCase):
    def setUp(self):
        self.parser = build_parser()

    def test_every_agent_accepts_json(self):
        for cmd in ("inventory", "audit", "connectivity", "report"):
            with self.subTest(command=cmd):
                args = self.parser.parse_args([cmd, "--json"])
                self.assertTrue(args.json)

    def test_json_defaults_off(self):
        for cmd in ("inventory", "audit", "connectivity", "report"):
            with self.subTest(command=cmd):
                args = self.parser.parse_args([cmd])
                self.assertFalse(args.json)

    def test_audit_json_and_markdown_combine(self):
        args = self.parser.parse_args(["audit", "--json", "--markdown"])
        self.assertTrue(args.json)
        self.assertTrue(args.markdown)


class EmitJsonTests(unittest.TestCase):
    def test_emit_json_is_valid(self):
        import json

        buf = io.StringIO()
        with redirect_stdout(buf):
            util.emit_json({"a": 1, "nested": {"b": [1, 2, None]}})
        parsed = json.loads(buf.getvalue())
        self.assertEqual(parsed["nested"]["b"], [1, 2, None])


if __name__ == "__main__":
    unittest.main()
