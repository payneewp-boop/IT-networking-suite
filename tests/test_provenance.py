"""Vendored copies in claude-hooks/ match what claude-hooks/PROVENANCE.md records.

A copy is a promise that what is on disk is the thing that was reviewed. The
hook test says what happens without a check: this copy went six weeks without
keys added upstream, and nothing noticed.

Two directions of drift, two checks:

* the copy was edited here        -> its sha256 no longer matches the pin;
* upstream moved and the copy did not -> it no longer matches the source, which
  can only be seen where a claude-development checkout exists, so it is skipped
  elsewhere (CI) and says so.

Hashes are taken over LF-normalised bytes, because .gitattributes stores LF and
a Windows checkout writes CRLF.
"""

import hashlib
import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "claude-hooks"
PROVENANCE = VENDOR / "PROVENANCE.md"

# | `file.py` | `path/in/claude-development.py` | sha256 `<64 hex>` |
ROW = re.compile(r"^\| `([^`]+)` \| `([^`]+)` \| sha256 `([0-9a-f]{64})` \|\s*$")


def sha256_lf(path):
    data = Path(path).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def read_pins():
    """Return {file name: (source path, sha256)} from the table."""
    pins = {}
    for line in PROVENANCE.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line)
        if m:
            pins[m.group(1)] = (m.group(2), m.group(3))
    return pins


def find_upstream():
    """Locate a claude-development checkout, or return None."""
    env = os.environ.get("CLAUDE_DEVELOPMENT")
    if env:
        # An explicit path is the only one tried: a typo should skip loudly, not
        # quietly check some other folder.
        candidates = [Path(env)]
    else:
        candidates = [ROOT.parent / "Claude-development", ROOT.parent / "claude-development"]
    for c in candidates:
        if (c / "hooks").is_dir():
            return c
    return None


class VendoredHookTests(unittest.TestCase):
    def test_the_record_has_rows(self):
        self.assertTrue(read_pins(), "%s has no table rows" % PROVENANCE.name)

    def test_every_script_has_a_row_and_every_row_a_script(self):
        pins = read_pins()
        on_disk = {p.name for p in VENDOR.glob("*.py")}
        self.assertEqual(
            sorted(on_disk - set(pins)), [],
            "a .py with no row in PROVENANCE.md is an unpinned copy",
        )
        self.assertEqual(
            sorted(set(pins) - on_disk), [],
            "PROVENANCE.md records a file that is not in claude-hooks/",
        )

    def test_each_copy_matches_its_pin(self):
        for name, (_source, want) in sorted(read_pins().items()):
            with self.subTest(file=name):
                got = sha256_lf(VENDOR / name)
                self.assertEqual(
                    got, want,
                    "%s was edited here, or re-copied without updating the hash "
                    "in PROVENANCE.md (steps under 'Updating').\n  recorded: %s\n  on disk:  %s"
                    % (name, want, got),
                )

    def test_each_copy_matches_the_source_when_it_can_be_seen(self):
        upstream = find_upstream()
        if upstream is None:
            self.skipTest(
                "no claude-development checkout found (set CLAUDE_DEVELOPMENT or "
                "put it beside this repo), so upstream drift was not checked"
            )
        for name, (source, _want) in sorted(read_pins().items()):
            with self.subTest(file=name):
                src = upstream / source
                self.assertTrue(src.is_file(), "%s is not in %s" % (source, upstream))
                self.assertEqual(
                    sha256_lf(VENDOR / name), sha256_lf(src),
                    "%s differs from claude-development/%s: upstream moved on, or "
                    "this copy was edited. Re-copy it and update PROVENANCE.md" % (name, source),
                )


if __name__ == "__main__":
    unittest.main()
