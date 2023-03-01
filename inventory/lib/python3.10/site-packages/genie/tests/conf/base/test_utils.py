#!/usr/bin/env python

import unittest
from unittest.mock import Mock
from collections import ChainMap, OrderedDict
from ipaddress import IPv4Interface, IPv6Interface
from ipaddress import IPv4Network, IPv6Network
from netaddr import EUI
import netaddr

from pyats.datastructures.logic import And, Or, Not

from genie.conf.base.link import Link
from genie.conf.base.device import Device
from genie.conf.base.testbed import Testbed
from genie.conf.base.utils import organize, QDict, prune_if
from genie.conf.base.utils import IPv4InterfaceRange, IPv6InterfaceRange, MACRange
from genie.conf.base.utils import IPv4InterfaceCache, IPv6InterfaceCache, MACCache
from genie.conf.base.attributes import SubAttributes, SubAttributesDict

def speed_higher_than_400(speed):
    if int(speed) <= 400:
        return True
    else:
        return False


def speed_lower_than_400(speed):
    if int(speed) >= 400:
        return True
    else:
        return False


class TestPruneIf(unittest.TestCase):

    def test_basic(self):

        data = {
            "k1": "foo",
            "k2": "bar",
            "k3": {
                "k4": "foobar",
                "k5": "foo",
                "k6": "bar",
            }
        }

        prune_if(data, lambda x: x == "foo")

        expected_output = {
            "k2": "bar",
            "k3": {
                "k4": "foobar",
                "k6": "bar",
            }
        }

        self.assertEqual(expected_output, data)

    def test_list(self):

        data = {
            "k1": ["foo", "bar", "foobar"],
            "k2": [
                {
                    "k1": "foo",
                    "k2": ["foo", "foo"]
                },
                "foo",
            ]
        }

        prune_if(data, lambda x: isinstance(x, str) and x.startswith("foo"))

        expected_output = {
            "k1": ["bar"],
            "k2": [
                {
                    "k2": []
                },
            ]
        }

        self.assertEqual(expected_output, data)

    def test_set(self):

        data = {
            "k1": {"foo", "bar", "foobar"},
            "k2": {
                "k3": [{"foo", "bar", "foobar"}, {"foo", "bar", "foobar"}],
                "k4": {"foo", "bar", "foobar"},
                "k5": "foo",
                "k6": "bar",
                "k7": "foobar"
            }
        }

        prune_if(data, lambda x: x == "foo")

        expected_output = {
            "k1": {"bar", "foobar"},
            "k2": {
                "k3": [{"bar", "foobar"}, {"bar", "foobar"}],
                "k4": {"bar", "foobar"},
                "k6": "bar",
                "k7": "foobar"
            }
        }

        self.assertEqual(expected_output, data)


class test_organizer(unittest.TestCase):

    def test_single_level(self):
        config = '''\
my first line
my second line
my third line'''

        expected_output = config

        output = organize(config)
        self.assertEqual(expected_output, output)

    def test_single_level_remove_dup(self):
        config = '''\
my first line
my first line
my second line
my third line
my fourth line
my second line
my second line
my first line
my third line'''

        expected_output = '''\
my first line
my second line
my third line
my fourth line'''

        output = organize(config)
        self.assertEqual(expected_output, output)

    def test_second_level_variant1(self):
        config = '''\
my first line
    my first line second level
    my second line second level
my second line
    my third line second level
    my fourth line second level
my third line'''

        expected_output = config

        output = organize(config)
        self.assertEqual(expected_output, output)

    def test_second_level_variant2(self):
        config = '''\
my first line
my second line
    my first line second level
    my second line second level
my third line
    my third line second level
    my fourth line second level'''

        expected_output = config

        output = organize(config)
        self.assertEqual(expected_output, output)

    def test_second_level_variant3(self):
        config = '''\
my first line
my second line
    my first line second level
    my second line second level
my third line
    my third line second level
    my fourth line second level
my fourth line'''

        expected_output = config

        output = organize(config)
        self.assertEqual(expected_output, output)

    def test_second_level_variant4(self):
        config = '''\
my first line
    my first line second level
    my second line second level'''

        expected_output = config

        output = organize(config)
        self.assertEqual(expected_output, output)

    def test_second_level_remove_dup1(self):
        config = '''\
my first line
    my first line second level
    my second line second level
my first line
    my third line in second level
my second line
    my fourth line second level
    my 5th line second level
my third line'''

        expected_output = '''\
my first line
    my first line second level
    my second line second level
    my third line in second level
my second line
    my fourth line second level
    my 5th line second level
my third line'''

        output = organize(config)
        self.assertEqual(expected_output, output)

    def test_second_level_remove_dup1(self):
        config = '''\
my first line
    my first line second level
    my second line second level
my first line
    my third line in second level
my second line
    my third line in second level
    my fourth line second level
    my 5th line second level
my third line'''

        expected_output = '''\
my first line
    my first line second level
    my second line second level
    my third line in second level
my second line
    my third line in second level
    my fourth line second level
    my 5th line second level
my third line'''

        output = organize(config)
        self.assertEqual(expected_output, output)

    def test_second_level_remove_dup2(self):
        config = '''\
my first line
    my first line second level
    my second line second level
my first line
    my third line
my second line
    my third line
    my fourth line second level
    my 5th line second level
my third line'''

        expected_output = '''\
my first line
    my first line second level
    my second line second level
    my third line
my second line
    my third line
    my fourth line second level
    my 5th line second level
my third line'''

        output = organize(config)
        self.assertEqual(expected_output, output)

    def test_second_level_remove_dup3(self):
        config = '''\
my third line
    my first line second level
    my second line second level
my first line
    my third line
my second line
    my third line
    my fourth line second level
    my 5th line second level
my third line'''

        expected_output = '''\
my third line
    my first line second level
    my second line second level
my first line
    my third line
my second line
    my third line
    my fourth line second level
    my 5th line second level'''

        output = organize(config)
        self.assertEqual(expected_output, output)

    def test_second_level_remove_dup4(self):
        config = '''\
my third line
    my first line second level
    my second line second level
my third line
    my third line
my second line
    my third line
    my fourth line second level
    my 5th line second level
my third line'''

        expected_output = '''\
my third line
    my first line second level
    my second line second level
    my third line
my second line
    my third line
    my fourth line second level
    my 5th line second level'''

        output = organize(config)
        self.assertEqual(expected_output, output)

    def test_third_level_variant1(self):
        config = '''\
my first line
    my first line second level
        my first line third level
        my second line third level
    my second line second level
my second line
    my third line
        my third line third level
    my fourth line second level
    my 5th line second level
my third line'''

        expected_output = config

        output = organize(config)
        self.assertEqual(expected_output, output)

    def test_third_level_variant2(self):
        config = '''\
my third line third level
my first line
    my first line second level
        my first line third level
        my second line third level
    my second line second level
    my second line second level
my second line
    my third line
        my third line third level
    my fourth line second level
    my 5th line second level
my first line
    my 6th line second level
    my first line second level
        my 4th line third level
    my second line second level
my third line'''

        expected_output = '''\
my third line third level
my first line
    my first line second level
        my first line third level
        my second line third level
        my 4th line third level
    my second line second level
    my 6th line second level
my second line
    my third line
        my third line third level
    my fourth line second level
    my 5th line second level
my third line'''

        output = organize(config)
        self.assertEqual(expected_output, output)

    def test_fourth_level_variant1(self):
        config = '''\
my third line third level
my first line
    my first line second level
        my first line third level
            my first line fourth level
            my second line fourth level
        my second line third level
    my second line second level
    my second line second level
my second line
    my third line
        my third line third level
    my fourth line second level
    my 5th line second level
my first line
    my 6th line second level
    my first line second level
        my first line third level
            my third line fourth level
            my fourth line fourth level
        my 4th line third level
    my second line second level
my third line'''

        expected_output = '''\
my third line third level
my first line
    my first line second level
        my first line third level
            my first line fourth level
            my second line fourth level
            my third line fourth level
            my fourth line fourth level
        my second line third level
        my 4th line third level
    my second line second level
    my 6th line second level
my second line
    my third line
        my third line third level
    my fourth line second level
    my 5th line second level
my third line'''

        output = organize(config)
        self.assertEqual(expected_output, output)

    def test_fifth_level_variant1(self):
        config = '''\
my third line third level
my first line
    my first line second level
        my first line third level
            my first line fourth level
            my second line fourth level
                my first line fifth level
        my second line third level
    my second line second level
    my second line second level
my second line
    my third line
        my third line third level
    my fourth line second level
    my 5th line second level
my first line
    my 6th line second level
    my first line second level
        my first line third level
            my third line fourth level
            my fourth line fourth level
            my second line fourth level
                my first line fifth level
                my second line fifth level
        my 4th line third level
    my second line second level
my third line'''

        expected_output = '''\
my third line third level
my first line
    my first line second level
        my first line third level
            my first line fourth level
            my second line fourth level
                my first line fifth level
                my second line fifth level
            my third line fourth level
            my fourth line fourth level
        my second line third level
        my 4th line third level
    my second line second level
    my 6th line second level
my second line
    my third line
        my third line third level
    my fourth line second level
    my 5th line second level
my third line'''

        output = organize(config)
        self.assertEqual(expected_output, output)


class test_IPv4InterfaceRange(unittest.TestCase):

    def test_init(self):

        with self.assertRaises(TypeError):
            IPv4InterfaceRange()
        IPv4InterfaceRange('10.0.0.0/24')

        rng = IPv4InterfaceRange('10.0.0.0/24', '10.0.0.0/24')
        self.assertEqual(rng.start, IPv4Interface('10.0.0.0/24'))
        self.assertEqual(len(rng), 0)
        self.assertEqual(rng.stop, IPv4Interface('10.0.0.0/24'))
        with self.assertRaises(IndexError):
            self.assertIs(rng[-1], None)
        self.assertEqual(rng.network, IPv4Network('10.0.0.0/24'))
        self.assertEqual(str(rng), '''IPv4InterfaceRange('10.0.0.0/24', '10.0.0.0/24')''')
        self.assertSequenceEqual(list(rng), [])

        rng = IPv4InterfaceRange('10.0.0.0/24', '10.0.0.5/24')
        self.assertEqual(str(rng), '10.0.0.0-10.0.0.4/24')
        self.assertEqual(rng.start, IPv4Interface('10.0.0.0/24'))
        self.assertEqual(len(rng), 5)
        self.assertEqual(rng.stop, IPv4Interface('10.0.0.5/24'))
        self.assertEqual(rng[-1], IPv4Interface('10.0.0.4/24'))
        self.assertEqual(rng.network, IPv4Network('10.0.0.0/24'))
        self.assertEqual(str(rng), '10.0.0.0-10.0.0.4/24')
        self.assertSequenceEqual(list(rng), [
            IPv4Interface('10.0.0.0/24'),
            IPv4Interface('10.0.0.1/24'),
            IPv4Interface('10.0.0.2/24'),
            IPv4Interface('10.0.0.3/24'),
            IPv4Interface('10.0.0.4/24'),
        ])


class test_IPv6InterfaceRange(unittest.TestCase):

    def test_init(self):

        with self.assertRaises(TypeError):
            IPv6InterfaceRange()
        IPv6InterfaceRange('10::0/80')

        rng = IPv6InterfaceRange('10::0/80', '10::0/80')
        self.assertEqual(rng.start, IPv6Interface('10::0/80'))
        self.assertEqual(len(rng), 0)
        self.assertEqual(rng.stop, IPv6Interface('10::0/80'))
        with self.assertRaises(IndexError):
            self.assertIs(rng[-1], None)
        self.assertEqual(rng.network, IPv6Network('10::0/80'))
        self.assertEqual(str(rng), '''IPv6InterfaceRange('10::/80', '10::/80')''')
        self.assertSequenceEqual(list(rng), [])

        rng = IPv6InterfaceRange('10::0/80', '10::5/80')
        self.assertEqual(rng.start, IPv6Interface('10::0/80'))
        self.assertEqual(len(rng), 5)
        self.assertEqual(rng.stop, IPv6Interface('10::5/80'))
        self.assertEqual(rng[-1], IPv6Interface('10::4/80'))
        self.assertEqual(rng.network, IPv6Network('10::0/80'))
        self.assertEqual(str(rng), '10::-10::4/80')
        self.assertSequenceEqual(list(rng), [
            IPv6Interface('10::0/80'),
            IPv6Interface('10::1/80'),
            IPv6Interface('10::2/80'),
            IPv6Interface('10::3/80'),
            IPv6Interface('10::4/80'),
        ])


class test_MacAddressRange(unittest.TestCase):

    def test_init(self):

        with self.assertRaises(TypeError):
            MACRange()
        MACRange('10.0.0')

        rng = MACRange('10.0.0', '10.0.0')
        self.assertEqual(rng.start, EUI('10.0.0'))
        self.assertEqual(len(rng), 0)
        self.assertEqual(rng.stop, EUI('10.0.0'))
        with self.assertRaises(IndexError):
            self.assertIs(rng[-1], None)
        self.assertEqual(str(rng), '''MACRange('0010.0000.0000', '0010.0000.0000')''')
        self.assertSequenceEqual(list(rng), [])

        rng = MACRange('10.0.0', '10.0.5')
        self.assertEqual(rng.start, EUI('10.0.0'))
        self.assertEqual(len(rng), 5)
        self.assertEqual(rng.stop, EUI('10.0.5'))
        self.assertEqual(rng[-1], EUI('10.0.4'))
        self.assertEqual(str(rng), '0010.0000.0000-0010.0000.0004')
        self.assertSequenceEqual(list(rng), [
            EUI('10.0.0'),
            EUI('10.0.1'),
            EUI('10.0.2'),
            EUI('10.0.3'),
            EUI('10.0.4'),
        ])


class test_IPv4InterfaceCache(unittest.TestCase):

    def test_reserve(self):

        r = IPv4InterfaceCache()

        v = r.reserve(count=1)
        self.assertEqual(len(v), 1)
        self.assertEqual(v.network.prefixlen, 30)

        v = r.reserve(count=2)
        self.assertEqual(len(v), 2)
        self.assertEqual(v.network.prefixlen, 30)

        v = r.reserve(count=2)
        v2 = r.reserve(count=2)
        self.assertNotEqual(v.start, v2.start)

        v = r.reserve(prefixlen=24)
        self.assertEqual(len(v), 256 - 2)
        self.assertEqual(v.network.prefixlen, 24)

        v = r.reserve(netmask='255.255.255.0')
        self.assertEqual(len(v), 256 - 2)
        self.assertEqual(v.network.prefixlen, 24)

        v = r.reserve('1.2.3.4')
        self.assertEqual(len(v), 1)
        self.assertEqual(v.network.prefixlen, 32)
        self.assertEqual(v.start, IPv4Interface('1.2.3.4/32'))

        v = r.reserve('1.2.3.1/24')
        self.assertEqual(len(v), 256 - 2)
        self.assertEqual(v.network.prefixlen, 24)
        self.assertEqual(v.start, IPv4Interface('1.2.3.1/24'))

        v = r.reserve('1.2.3.0/255.255.255.255')
        self.assertEqual(len(v), 1)
        self.assertEqual(v.network.prefixlen, 32)
        self.assertEqual(v.start, IPv4Interface('1.2.3.0/32'))

        v = r.reserve(type='A')  # type: A, B, C, X, local
        self.assertEqual(len(v), 0x01000000 - 2)
        self.assertEqual(v.network.prefixlen, 8)


class test_IPv6InterfaceCache(unittest.TestCase):

    def test_reserve(self):

        r = IPv6InterfaceCache()

        v = r.reserve(count=1)
        self.assertEqual(len(v), 1)
        self.assertEqual(v.network.prefixlen, 126)

        v = r.reserve(count=2)
        self.assertEqual(len(v), 2)
        self.assertEqual(v.network.prefixlen, 126)

        v = r.reserve(count=2)
        v2 = r.reserve(count=2)
        self.assertNotEqual(v.start, v2.start)

        v = r.reserve(prefixlen=97)
        self.assertEqual(len(v), 0x80000000 - 2)
        self.assertEqual(v.network.prefixlen, 97)

        v = r.reserve(prefixlen=64)
        with self.assertRaises(OverflowError):
            # See UserRange.__len__ -- Python limits len() to ssize_t.
            len(v)
        # UserRange.__len__ still works.
        self.assertEqual(v.__len__(), 0x10000000000000000 - 2)
        self.assertEqual(v.network.prefixlen, 64)

        if False:
            # IPv6Interface does not support /netmask format, only /prefixlen.
            v = r.reserve(netmask='ffff:ffff:ffff:ffff:0000:0000:0000:0000')
            with self.assertRaises(OverflowError):
                # See UserRange.__len__ -- Python limits len() to ssize_t.
                len(v)
            # UserRange.__len__ still works.
            self.assertEqual(v.__len__(), 0x10000000000000000 - 2)

        v = r.reserve('1:2::3:4')
        self.assertEqual(len(v), 1)
        self.assertEqual(v.network.prefixlen, 128)

        v = r.reserve('1:2::3:0/112')
        self.assertEqual(len(v), 0x10000 - 2)
        self.assertEqual(v.network.prefixlen, 112)

        if False:
            # IPv6Interface does not support /netmask format, only /prefixlen.
            v = r.reserve('1:2::3:0/ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff')
            self.assertEqual(len(v), 1)
            self.assertEqual(v.network.prefixlen, 128)

        v = r.reserve('1:2::3:0/128')
        self.assertEqual(len(v), 1)
        self.assertEqual(v.network.prefixlen, 128)

        v = r.reserve(type='multicast')  # type: unicast, loal, link-local, site-local, multicast
        self.assertEqual(len(v), 1)
        self.assertTrue(str(v.start).startswith('ff10:'))
        self.assertEqual(v.network.prefixlen, 128)


class test_MacAddressCache(unittest.TestCase):

    def test_reserve(self):

        r = MACCache()

        v = r.reserve(count=1)
        self.assertEqual(len(v), 1)

        v = r.reserve(count=2)
        self.assertEqual(len(v), 2)

        v = r.reserve(count=2)
        v2 = r.reserve(count=2)
        self.assertNotEqual(v.start, v2.start)

        v = r.reserve(prefixlen=40)
        self.assertEqual(len(v), 256)

        v = r.reserve('1.2.3')
        self.assertEqual(len(v), 1)

        v = r.reserve('1.2.0', prefixlen=32)
        self.assertEqual(len(v), 65536)
        self.assertEqual(str(v.start), '0001.0002.0000')

        v = r.reserve('1.2.3', prefixlen=48)
        self.assertEqual(len(v), 1)
        self.assertEqual(str(v.start), '0001.0002.0003')

        v = r.reserve(type='local')  # type: global, local, unicast, multicast, global|local-unicast|multicast
        self.assertEqual(len(v), 1)
        self.assertTrue(int(v.start) & 0x020000000000)  # local?
        self.assertFalse(int(v.start) & 0x010000000000)  # multicast?

        v = r.reserve(type='global')  # type: global, local, unicast, multicast, global|local-unicast|multicast
        self.assertEqual(len(v), 1)
        self.assertFalse(int(v.start) & 0x020000000000)  # local?
        self.assertFalse(int(v.start) & 0x010000000000)  # multicast?

        v = r.reserve(type='unicast')  # type: global, local, unicast, multicast, global|local-unicast|multicast
        self.assertEqual(len(v), 1)
        self.assertFalse(int(v.start) & 0x020000000000)  # local?
        self.assertFalse(int(v.start) & 0x010000000000)  # multicast?

        v = r.reserve(type='multicast')  # type: global, local, unicast, multicast, global|local-unicast|multicast
        self.assertEqual(len(v), 1)
        self.assertFalse(int(v.start) & 0x020000000000)  # local?
        self.assertTrue(int(v.start) & 0x010000000000)  # multicast?

class Test_QDict(unittest.TestCase):

    def test_is_subclass(self):
        self.assertTrue(issubclass(QDict, dict))
    
    def test_functionality(self):
        obj = QDict({'rp': {'1': {'NX-OSv Supervisor Module': {'ports': '0', 'model': 'N7K-SUP1', 'status': 'active', 'software': '7.3(0)D1(1)', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '5e-00-40-01-00-00 to 5e-00-40-01-07-ff', 'serial_number': 'TM40010000B'}}}, 'lc': {'2': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '02-00-0c-00-02-00 to 02-00-0c-00-02-7f', 'serial_number': 'TM40010000C'}}, '3': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '02-00-0c-00-03-00 to 02-00-0c-00-03-7f', 'serial_number': 'TM40010000D'}}, '4': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': [1,2,3], 'mac_address': '02-00-0c-00-04-00 to 02-00-0c-00-04-7f', 'serial_number': 'TM40010000E'}}}})
        output = obj.q.contains('rp')
        self.assertEqual(output.reconstruct(),
                {'rp': {'1': {'NX-OSv Supervisor Module': {'ports': '0', 'model': 'N7K-SUP1', 'status': 'active', 'software': '7.3(0)D1(1)', 'hardware': '0.0', 'slot/world_wide_name': '--', 'mac_address': '5e-00-40-01-00-00 to 5e-00-40-01-07-ff', 'serial_number': 'TM40010000B'}}}})

        output = obj.q.contains('[1,2]', regex=True)
        self.assertEqual(output.reconstruct(),
                {"rp":{"1":{"NX-OSv Supervisor Module":{"ports":"0","model":"N7K-SUP1","status":"active","software":"7.3(0)D1(1)","hardware":"0.0","slot/world_wide_name":"--","mac_address":"5e-00-40-01-00-00 to 5e-00-40-01-07-ff","serial_number":"TM40010000B"}}},"lc":{"2":{"NX-OSv Ethernet Module":{"ports":"48","model":"N7K-F248XP-25","status":"ok","software":"NA","hardware":"0.0","slot/world_wide_name":"--","mac_address":"02-00-0c-00-02-00 to 02-00-0c-00-02-7f","serial_number":"TM40010000C"}},'4': {'NX-OSv Ethernet Module': {'slot/world_wide_name': [1, 2]}}}})

        output = obj.q.contains('lc').contains('4')
        self.assertEqual(output.reconstruct(),
                {'lc': {'4': {'NX-OSv Ethernet Module': {'ports': '48', 'model': 'N7K-F248XP-25', 'status': 'ok', 'software': 'NA', 'hardware': '0.0', 'slot/world_wide_name': [1, 2, 3], 'mac_address': '02-00-0c-00-04-00 to 02-00-0c-00-04-7f', 'serial_number': 'TM40010000E'}}}})

        output = obj.q.contains('lc').contains('4').contains('status')
        self.assertEqual(output.reconstruct(),
                {'lc': {'4': {'NX-OSv Ethernet Module': {'status': 'ok'}}}})
        
        output = obj.q.contains('.*ware', regex=True)
        self.assertEqual(output.reconstruct(),
                {"rp":{"1":{"NX-OSv Supervisor Module":{"software":"7.3(0)D1(1)","hardware":"0.0"}}},"lc":{"2":{"NX-OSv Ethernet Module":{"software":"NA","hardware":"0.0"}},"3":{"NX-OSv Ethernet Module":{"software":"NA","hardware":"0.0"}},"4":{"NX-OSv Ethernet Module":{"software":"NA","hardware":"0.0"}}}})

    def test_cached(self):
        obj = QDict()
        self.assertEqual(id(obj.q), id(obj.q))

if __name__ == '__main__':
    unittest.main()
