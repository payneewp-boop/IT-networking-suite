"""Tests for the audit agent's DNS classification logic."""

import unittest

from netagent.agents.audit import _check_dns


def _severity_for(dns, gateway, server):
    for sev, check, _detail in _check_dns(dns, gateway):
        if check == f"DNS {server}":
            return sev
    return None


class CheckDnsTests(unittest.TestCase):
    GATEWAY = "192.168.1.1"

    def test_router_dns_passes(self):
        self.assertEqual(_severity_for([self.GATEWAY], self.GATEWAY, self.GATEWAY), "PASS")

    def test_known_public_dns_warns(self):
        self.assertEqual(_severity_for(["8.8.8.8"], self.GATEWAY, "8.8.8.8"), "WARN")

    def test_local_stub_passes(self):
        self.assertEqual(_severity_for(["127.0.0.1"], self.GATEWAY, "127.0.0.1"), "PASS")

    def test_unrecognized_dns_warns_not_fails(self):
        # A resolver that is neither the router nor a known public one (e.g. the
        # ISP's own DNS via DHCP) must warn, not fail — otherwise a normal home
        # network reports a scary FAIL on every run.
        sev = _severity_for(["203.0.113.5"], self.GATEWAY, "203.0.113.5")
        self.assertEqual(sev, "WARN")

    def test_no_dns_config_warns(self):
        findings = _check_dns([], self.GATEWAY)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0][0], "WARN")

    def test_no_findings_are_fail(self):
        # With the ISP-DNS calibration, DNS alone should never produce a FAIL.
        dns = [self.GATEWAY, "8.8.8.8", "203.0.113.5", "127.0.0.1"]
        severities = {sev for sev, _c, _d in _check_dns(dns, self.GATEWAY)}
        self.assertNotIn("FAIL", severities)


if __name__ == "__main__":
    unittest.main()
