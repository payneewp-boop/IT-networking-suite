"""Parser tests for netagent.net across Windows, macOS, and Linux output."""

import unittest
from unittest import mock

from netagent import net

from .support import fake_run_from, patch_platform

# --- Sample command output --------------------------------------------------

WIN_ROUTE_PRINT = """\
===========================================================================
Active Routes:
Network Destination        Netmask          Gateway       Interface  Metric
          0.0.0.0          0.0.0.0      192.168.0.1     192.168.0.23     25
    192.168.0.0    255.255.255.0         On-link      192.168.0.23    281
===========================================================================
"""

# A "Default Gateway" line that lists an IPv6 address before the IPv4 one.
WIN_IPCONFIG_IPV6_FIRST = """\
Windows IP Configuration

Ethernet adapter Ethernet:
   Connection-specific DNS Suffix  . :
   Default Gateway . . . . . . . . . : fe80::1%11
                                       192.168.0.1
   NetBIOS over Tcpip. . . . . . . . : Enabled
"""

WIN_ARP = """\
Interface: 192.168.0.23 --- 0xb
  Internet Address      Physical Address      Type
  192.168.0.1           a4-2b-b0-11-22-33     dynamic
  192.168.0.50          00-11-22-aa-bb-cc     dynamic
  192.168.0.255         ff-ff-ff-ff-ff-ff     static
  255.255.255.255       ff-ff-ff-ff-ff-ff     static
"""

WIN_IPCONFIG_ALL_DNS = """\
Windows IP Configuration

Ethernet adapter Ethernet:
   DNS Servers . . . . . . . . . . . : 192.168.0.1
                                       8.8.8.8
                                       fec0:0:0:ffff::1%1
                                       1.1.1.1
   NetBIOS over Tcpip. . . . . . . . : Enabled
"""

MAC_NETSTAT = """\
Routing tables

Internet:
Destination        Gateway            Flags        Netif Expire
default            192.168.1.1        UGSc          en0
127.0.0.1          127.0.0.1          UH            lo0
"""

MAC_SCUTIL = """\
DNS configuration

resolver #1
  nameserver[0] : 192.168.1.1
  nameserver[1] : 8.8.8.8
"""

UNIX_ARP = """\
? (192.168.1.1) at a4:2b:b0:11:22:33 [ether] on eth0
laptop.local (192.168.1.50) at 00:11:22:aa:bb:cc [ether] on eth0
? (192.168.1.255) at ff:ff:ff:ff:ff:ff [ether] on eth0
"""

LINUX_IP_ROUTE = "default via 192.168.1.1 dev wlan0 proto dhcp metric 600\n"

LINUX_IP_NEIGH = """\
192.168.1.1 dev eth0 lladdr a4:2b:b0:11:22:33 REACHABLE
192.168.1.50 dev eth0 lladdr 00:11:22:aa:bb:cc STALE
192.168.1.99 dev eth0  FAILED
"""


class HelperTests(unittest.TestCase):
    def test_is_ip(self):
        self.assertTrue(net._is_ip("192.168.1.1"))
        self.assertFalse(net._is_ip("not-an-ip"))
        self.assertFalse(net._is_ip("999.1.1.1"))

    def test_norm_mac(self):
        self.assertEqual(net._norm_mac("A4-2B-B0-11-22-33"), "a4:2b:b0:11:22:33")
        self.assertEqual(net._norm_mac("a4:2b:b0:11:22:33"), "a4:2b:b0:11:22:33")
        self.assertIsNone(net._norm_mac("nope"))
        self.assertIsNone(net._norm_mac("a4:2b:b0:11:22"))  # too short


class GatewayTests(unittest.TestCase):
    def test_windows_route_print(self):
        with patch_platform(is_windows=True), mock.patch.object(
            net, "_run", fake_run_from({"route print": WIN_ROUTE_PRINT})
        ):
            self.assertEqual(net.default_gateway(), "192.168.0.1")

    def test_windows_ipconfig_fallback_ipv6_first(self):
        # route print yields nothing -> fall back to ipconfig, which lists an
        # IPv6 gateway before the real IPv4 one.
        with patch_platform(is_windows=True), mock.patch.object(
            net, "_run", fake_run_from({"ipconfig": WIN_IPCONFIG_IPV6_FIRST})
        ):
            self.assertEqual(net.default_gateway(), "192.168.0.1")

    def test_linux_ip_route(self):
        with patch_platform(), mock.patch.object(
            net, "_run", fake_run_from({"ip route": LINUX_IP_ROUTE})
        ):
            self.assertEqual(net.default_gateway(), "192.168.1.1")

    def test_macos_netstat(self):
        with patch_platform(is_mac=True), mock.patch.object(
            net, "_run", fake_run_from({"netstat": MAC_NETSTAT})
        ):
            self.assertEqual(net.default_gateway(), "192.168.1.1")


class ArpTableTests(unittest.TestCase):
    def test_windows_arp(self):
        with patch_platform(is_windows=True), mock.patch.object(
            net, "_run", fake_run_from({"arp -a": WIN_ARP})
        ):
            table = net.arp_table()
        self.assertEqual(table["192.168.0.1"], "a4:2b:b0:11:22:33")
        self.assertEqual(table["192.168.0.50"], "00:11:22:aa:bb:cc")
        # Broadcast MACs are dropped.
        self.assertNotIn("192.168.0.255", table)
        self.assertNotIn("255.255.255.255", table)

    def test_unix_arp(self):
        with patch_platform(), mock.patch.object(
            net, "_run", fake_run_from({"arp -a": UNIX_ARP})
        ):
            table = net.arp_table()
        self.assertEqual(table["192.168.1.1"], "a4:2b:b0:11:22:33")
        self.assertEqual(table["192.168.1.50"], "00:11:22:aa:bb:cc")
        self.assertNotIn("192.168.1.255", table)

    def test_linux_ip_neigh_fallback(self):
        # `arp -a` returns nothing -> fall back to `ip neigh`.
        with patch_platform(), mock.patch.object(
            net, "_run", fake_run_from({"ip neigh": LINUX_IP_NEIGH})
        ):
            table = net.arp_table()
        self.assertEqual(table["192.168.1.1"], "a4:2b:b0:11:22:33")
        self.assertEqual(table["192.168.1.50"], "00:11:22:aa:bb:cc")
        # Entry without an lladdr is skipped.
        self.assertNotIn("192.168.1.99", table)


class DnsServerTests(unittest.TestCase):
    def test_windows_skips_ipv6_continuation(self):
        with patch_platform(is_windows=True), mock.patch.object(
            net, "_run", fake_run_from({"ipconfig": WIN_IPCONFIG_ALL_DNS})
        ):
            self.assertEqual(
                net.dns_servers(), ["192.168.0.1", "8.8.8.8", "1.1.1.1"]
            )

    def test_macos_scutil(self):
        with patch_platform(is_mac=True), mock.patch.object(
            net, "_run", fake_run_from({"scutil": MAC_SCUTIL})
        ):
            self.assertEqual(net.dns_servers(), ["192.168.1.1", "8.8.8.8"])

    def test_linux_resolv_conf(self):
        resolv = "# generated\nnameserver 192.168.1.1\nnameserver 8.8.8.8\n"
        with patch_platform(), mock.patch(
            "builtins.open", mock.mock_open(read_data=resolv)
        ):
            self.assertEqual(net.dns_servers(), ["192.168.1.1", "8.8.8.8"])


class PingTests(unittest.TestCase):
    def _ping_with(self, output):
        with mock.patch.object(net, "_run", lambda cmd, timeout=10: output):
            return net.ping_once("192.168.1.1")

    def test_windows_reply(self):
        self.assertEqual(
            self._ping_with("Reply from 192.168.1.1: bytes=32 time=14ms TTL=64"),
            14.0,
        )

    def test_sub_millisecond(self):
        self.assertEqual(
            self._ping_with("Reply from 192.168.1.1: bytes=32 time<1ms TTL=64"),
            1.0,
        )

    def test_unix_reply(self):
        out = "64 bytes from 192.168.1.1: icmp_seq=0 ttl=64 time=8.42 ms"
        self.assertEqual(self._ping_with(out), 8.42)

    def test_unreachable_returns_none(self):
        self.assertIsNone(self._ping_with("Request timed out."))

    def test_empty_returns_none(self):
        self.assertIsNone(self._ping_with(""))


if __name__ == "__main__":
    unittest.main()
