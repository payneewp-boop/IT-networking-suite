"""Shared test helpers: fake command runner and platform patching.

The networking layer funnels every external command through ``net._run``. Tests
patch that single seam with canned ``arp`` / ``ipconfig`` / ``route`` / ``ping``
output, so parser behaviour is verified without ever touching the real system.
"""

from unittest import mock

from netagent import net


def fake_run_from(mapping):
    """Build a stand-in for net._run that returns canned output by command.

    ``mapping`` maps a substring of the joined command to its stdout. The first
    matching pattern wins; anything unmatched returns '' (like a failed command).
    """

    def fake(cmd, timeout=10):
        joined = " ".join(cmd)
        for pattern, output in mapping.items():
            if pattern in joined:
                return output
        return ""

    return fake


def patch_platform(is_windows=False, is_mac=False):
    """Context manager forcing net's platform flags for a test."""
    return mock.patch.multiple(net, IS_WINDOWS=is_windows, IS_MAC=is_mac)
