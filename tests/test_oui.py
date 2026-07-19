"""Tests for the MAC-vendor (OUI) lookup against a temporary cache file."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from netagent import oui

# IEEE oui.csv layout: Registry, Assignment, Organization Name, Address
SAMPLE_OUI_CSV = """\
Registry,Assignment,Organization Name,Organization Address
MA-L,A42BB0,Acme Networks Inc,123 Example St
MA-L,001122,Example Corp,456 Sample Ave
"""


class OuiLookupTests(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        cache = Path(self._tmp.name) / "oui.csv"
        cache.write_text(SAMPLE_OUI_CSV, encoding="utf-8")
        # Point the module at our temp cache and clear its memoized table.
        self._patch = mock.patch.object(oui, "OUI_CACHE", cache)
        self._patch.start()
        oui._cache = None

    def tearDown(self):
        self._patch.stop()
        oui._cache = None
        self._tmp.cleanup()

    def test_known_vendor(self):
        self.assertEqual(oui.lookup("a4:2b:b0:11:22:33"), "Acme Networks Inc")

    def test_case_and_separator_insensitive(self):
        self.assertEqual(oui.lookup("A4-2B-B0-AA-BB-CC"), "Acme Networks Inc")
        self.assertEqual(oui.lookup("00:11:22:de:ad:be"), "Example Corp")

    def test_unknown_prefix(self):
        self.assertEqual(oui.lookup("ff:ff:ff:00:00:00"), "")

    def test_empty_mac(self):
        self.assertEqual(oui.lookup(""), "")
        self.assertEqual(oui.lookup(None), "")


class OuiDownloadTests(unittest.TestCase):
    def test_existing_cache_is_not_redownloaded(self):
        with TemporaryDirectory() as tmp:
            cache = Path(tmp) / "oui.csv"
            cache.write_text(SAMPLE_OUI_CSV, encoding="utf-8")
            with mock.patch.object(oui, "OUI_CACHE", cache), mock.patch(
                "urllib.request.urlopen"
            ) as urlopen:
                self.assertTrue(oui.ensure_oui_db(quiet=True))
                urlopen.assert_not_called()

    def test_download_failure_degrades_gracefully(self):
        with TemporaryDirectory() as tmp:
            cache = Path(tmp) / "missing.csv"
            with mock.patch.object(oui, "OUI_CACHE", cache), mock.patch(
                "urllib.request.urlopen", side_effect=OSError("offline")
            ):
                # Should return False, never raise, and not create the file.
                self.assertFalse(oui.ensure_oui_db(quiet=True))
                self.assertFalse(cache.exists())


if __name__ == "__main__":
    unittest.main()
