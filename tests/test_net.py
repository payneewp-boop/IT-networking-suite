"""Parser tests for netagent.net across Windows, macOS, and Linux output."""

import ipaddress
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

# Windows `netstat -rn` — same numeric default-route row as `route print`.
WIN_NETSTAT = """\
===========================================================================
IPv4 Route Table
===========================================================================
Active Routes:
Network Destination        Netmask          Gateway       Interface  Metric
          0.0.0.0          0.0.0.0      192.168.0.1     192.168.0.23     25
===========================================================================
"""

# PowerShell Get-DnsClientServerAddress output: one IP per line, no labels.
WIN_POWERSHELL_DNS = "192.168.0.1\n8.8.8.8\n"

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

    def test_windows_netstat_fallback(self):
        # route print yields nothing -> the numeric `netstat -rn` table is the
        # locale-independent fallback before any label parsing.
        with patch_platform(is_windows=True), mock.patch.object(
            net, "_run", fake_run_from({"netstat": WIN_NETSTAT})
        ):
            self.assertEqual(net.default_gateway(), "192.168.0.1")

    def test_windows_ipconfig_fallback_ipv6_first(self):
        # Neither routing-table command matched -> last-resort ipconfig label,
        # which lists an IPv6 gateway before the real IPv4 one.
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
    def test_windows_powershell_primary(self):
        # PowerShell output is the locale-independent primary source.
        with patch_platform(is_windows=True), mock.patch.object(
            net, "_run", fake_run_from({"powershell": WIN_POWERSHELL_DNS})
        ):
            self.assertEqual(net.dns_servers(), ["192.168.0.1", "8.8.8.8"])

    def test_windows_ipconfig_fallback_skips_ipv6(self):
        # PowerShell yields nothing -> fall back to ipconfig /all, skipping the
        # IPv6 continuation line but still catching the IPv4 resolver after it.
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

    def test_localized_german_reply(self):
        # Non-English Windows localizes "time" (here "Zeit") but keeps "ms".
        out = "Antwort von 192.168.1.1: Bytes=32 Zeit=14ms TTL=64"
        self.assertEqual(self._ping_with(out), 14.0)

    def test_localized_spanish_reply(self):
        out = "Respuesta desde 192.168.1.1: bytes=32 tiempo=9ms TTL=64"
        self.assertEqual(self._ping_with(out), 9.0)

    def test_unreachable_returns_none(self):
        self.assertIsNone(self._ping_with("Request timed out."))

    def test_empty_returns_none(self):
        self.assertIsNone(self._ping_with(""))


# --- Mutation-testing gaps ---------------------------------------------------
# Found by the lab challenger in claude-development
# (lab/reports/it-networking-suite-challenge-2026-10-07.md): each case kills
# breakages the parser tests above let through.

WIN_IPCONFIG_TWO_ADAPTERS = """\
Windows IP Configuration

Ethernet adapter vEthernet (Default Switch):
   IPv4 Address. . . . . . . . . . . : 172.20.0.1
   Subnet Mask . . . . . . . . . . . : 255.255.240.0
   Default Gateway . . . . . . . . . :

Ethernet adapter Ethernet:
   IPv4 Address. . . . . . . . . . . : 192.168.0.23
   Subnet Mask . . . . . . . . . . . : 255.255.255.0
   Default Gateway . . . . . . . . . : 192.168.0.1
"""


class PingCommandTests(unittest.TestCase):
    # The wait flag means milliseconds on Windows and macOS but seconds on
    # Linux; a mix-up makes every sweep on one OS time out or take minutes.
    def test_windows_waits_in_milliseconds(self):
        with patch_platform(is_windows=True):
            self.assertEqual(net.ping_cmd("10.0.0.1", 2, 750),
                             ["ping", "-n", "2", "-w", "750", "10.0.0.1"])

    def test_macos_waits_in_milliseconds(self):
        with patch_platform(is_mac=True):
            self.assertEqual(net.ping_cmd("10.0.0.1", 1, 750),
                             ["ping", "-c", "1", "-W", "750", "10.0.0.1"])

    def test_linux_waits_in_whole_seconds_never_zero(self):
        with patch_platform():
            self.assertEqual(net.ping_cmd("10.0.0.1", 3, 2600),
                             ["ping", "-c", "3", "-W", "3", "10.0.0.1"])
            self.assertEqual(net.ping_cmd("10.0.0.1", 1, 300)[4], "1")


class SubnetTests(unittest.TestCase):
    def test_host_bits_are_dropped(self):
        with mock.patch.object(net, "local_ip", return_value="192.168.0.23"):
            self.assertEqual(str(net.local_subnet()), "192.168.0.0/24")
            self.assertEqual(str(net.local_subnet(16)), "192.168.0.0/16")


class GatewayEdgeTests(unittest.TestCase):
    def test_no_route_anywhere_is_none(self):
        for windows in (True, False):
            with patch_platform(is_windows=windows), mock.patch.object(
                net, "_run", fake_run_from({})
            ):
                self.assertIsNone(net.default_gateway())

    def test_ipconfig_blank_gateway_does_not_borrow_the_next_adapter(self):
        # The first adapter has no gateway. Its block must end at the next
        # adapter header, not run on and report that adapter's own address.
        with patch_platform(is_windows=True), mock.patch.object(
            net, "_run", fake_run_from({"ipconfig": WIN_IPCONFIG_TWO_ADAPTERS})
        ):
            self.assertEqual(net.default_gateway(), "192.168.0.1")


class ArpEdgeTests(unittest.TestCase):
    def test_unix_incomplete_entry_skipped(self):
        out = "? (192.168.1.77) at (incomplete) on en0 ifscope [ethernet]\n"
        with patch_platform(), mock.patch.object(net, "_run", fake_run_from({"arp -a": out})):
            self.assertEqual(net.arp_table(), {})

    def test_zero_mac_dropped_on_windows(self):
        out = "  192.168.0.9           00-00-00-00-00-00     dynamic\n"
        with patch_platform(is_windows=True), mock.patch.object(
            net, "_run", fake_run_from({"arp -a": out})
        ):
            self.assertEqual(net.arp_table(), {})


class DnsDedupeTests(unittest.TestCase):
    def test_duplicates_and_bad_addresses_dropped_in_order(self):
        with patch_platform(is_windows=True), mock.patch.object(
            net, "_run", fake_run_from({"Get-DnsClientServerAddress":
                                        "8.8.8.8\n192.168.0.1\n8.8.8.8\n999.1.1.1\n"})
        ):
            self.assertEqual(net.dns_servers(), ["8.8.8.8", "192.168.0.1"])


class PortScanTests(unittest.TestCase):
    class FakeSocket:
        def __init__(self, *args):
            pass

        def settimeout(self, timeout):
            pass

        def connect_ex(self, address):
            if address[1] == 23:
                raise OSError("unreachable")
            return 0 if address[1] == 80 else 111

        def close(self):
            pass

    def test_only_accepting_ports_reported_sorted(self):
        with mock.patch.object(net.socket, "socket", self.FakeSocket):
            self.assertTrue(net.scan_port("10.0.0.5", 80))
            self.assertFalse(net.scan_port("10.0.0.5", 443))
            self.assertFalse(net.scan_port("10.0.0.5", 23))
            self.assertEqual(net.scan_ports("10.0.0.5", [443, 80, 23, 22]), [80])


class SweepTests(unittest.TestCase):
    def test_only_answering_hosts_returned_in_input_order(self):
        replies = {"10.0.0.2": 1.5, "10.0.0.4": 0.0}  # 0.0 ms is still a reply
        with mock.patch.object(net, "ping_once", lambda host, timeout_ms: replies.get(host)):
            hosts = list(ipaddress.ip_network("10.0.0.0/29").hosts())
            self.assertEqual(net.ping_sweep(hosts), ["10.0.0.2", "10.0.0.4"])

    def test_ping_once_gives_the_run_a_deadline_past_the_ping_wait(self):
        seen = {}

        def fake(cmd, timeout=10):
            seen["timeout"] = timeout
            return ""

        with patch_platform(), mock.patch.object(net, "_run", fake):
            self.assertIsNone(net.ping_once("10.0.0.1", 2000))
        self.assertEqual(seen["timeout"], 5.0)


if __name__ == "__main__":
    unittest.main()
