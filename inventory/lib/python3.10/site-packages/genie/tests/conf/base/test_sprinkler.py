#!/usr/bin/env python

import unittest

from netaddr import mac_cisco, EUI, core
from ipaddress import ip_network, IPv4Network, IPv4Address, ip_address

from genie.conf import Genie
from genie.conf.base.device import Device
from genie.conf.base.testbed import Testbed
from genie.conf.base.utils import organize
from genie.conf.base.interface import BaseInterface
from genie.conf.base.sprinkler import InterfaceName, IpUtils, Ip, Ipv6

class test_sprinkler(unittest.TestCase):

    def tearDown(self):
        Genie.testbed = None

    def test_loopback_interface(self):

        tb = Genie.testbed = Testbed()
        dev = Device(testbed=tb, name='my_device', os='nxos')

        loopback = InterfaceName.loopback(device=dev, name='loopback')
        self.assertEqual(loopback, 'loopback0')

        # Even if repeat, same name as not placed into device yet
        loopback = InterfaceName.loopback(device=dev, name='loopback')
        self.assertEqual(loopback, 'loopback0')

        BaseInterface(name=loopback, device=dev)

        # Even if repeat, same name as not placed into device yet
        loopback = InterfaceName.loopback(device=dev, name='loopback')
        self.assertEqual(loopback, 'loopback1')

        for number in range(1, 1024):
            loopback = InterfaceName.loopback(device=dev, name='loopback')
            self.assertEqual(loopback, 'loopback'+str(number))
            BaseInterface(name=loopback, device=dev)

        with self.assertRaises(ValueError):
            loopback = InterfaceName.loopback(device=dev, name='loopback')

        # Delete one and space should be available now
        del dev.interfaces['loopback0']
        loopback = InterfaceName.loopback(device=dev, name='loopback')
        self.assertEqual(loopback, 'loopback0')

    def test_loopback_interface_special_iterable(self):

        tb = Genie.testbed = Testbed()
        dev = Device(testbed=tb, name='my_device', os='nxos')
        for number in range(0, 5):
            loopback = InterfaceName.loopback(device=dev, name='loopback',
                                              iterable=range(number, 5))
            self.assertEqual(loopback, 'loopback'+str(number))
            BaseInterface(name=loopback, device=dev)

        with self.assertRaises(ValueError):
            loopback = InterfaceName.loopback(device=dev, name='loopback',
                                              iterable=range(number, 5))


    def test_vlan_interface(self):

        tb = Genie.testbed = Testbed()
        dev = Device(testbed=tb, name='my_device', os='nxos')

        vlan = InterfaceName.vlan(device=dev, name='vlan')
        self.assertEqual(vlan, 'vlan0')

        # Even if repeat, same name as not placed into device yet
        vlan = InterfaceName.vlan(device=dev, name='vlan')
        self.assertEqual(vlan, 'vlan0')

        BaseInterface(name=vlan, device=dev)

        # Even if repeat, same name as not placed into device yet
        vlan = InterfaceName.vlan(device=dev, name='vlan')
        self.assertEqual(vlan, 'vlan1')

        for number in range(1, 100):
            vlan = InterfaceName.vlan(device=dev, name='vlan')
            self.assertEqual(vlan, 'vlan'+str(number))
            BaseInterface(name=vlan, device=dev)

        # Create the rest quickly
        for number in range(100, 4095):
            BaseInterface(name='vlan'+str(number), device=dev)

        with self.assertRaises(ValueError):
            vlan = InterfaceName.vlan(device=dev, name='vlan')

    def test_vlan_interface_special_iterable(self):

        tb = Genie.testbed = Testbed()
        dev = Device(testbed=tb, name='my_device', os='nxos')

        for number in range(0, 5):
            vlan = InterfaceName.vlan(device=dev, name='vlan',
                                              iterable=range(number, 5))
            self.assertEqual(vlan, 'vlan'+str(number))
            BaseInterface(name=vlan, device=dev)

        with self.assertRaises(ValueError):
            vlan = InterfaceName.vlan(device=dev, name='vlan',
                                              iterable=range(number, 5))

    def test_port_channel_interface(self):

        tb = Genie.testbed = Testbed()
        dev = Device(testbed=tb, name='my_device', os='nxos')

        port_channel = InterfaceName.port_channel(device=dev,
                                                  name='port-channel')
        self.assertEqual(port_channel, 'port-channel0')

        # Even if repeat, same name as not placed into device yet
        port_channel = InterfaceName.port_channel(device=dev,
                                                  name='port-channel')
        self.assertEqual(port_channel, 'port-channel0')

        BaseInterface(name=port_channel, device=dev)

        # Even if repeat, same name as not placed into device yet
        port_channel = InterfaceName.port_channel(device=dev,
                                                  name='port-channel')
        self.assertEqual(port_channel, 'port-channel1')

        for number in range(1, 100):
            port_channel = InterfaceName.port_channel(device=dev,
                                                      name='port-channel')
            self.assertEqual(port_channel, 'port-channel'+str(number))
            BaseInterface(name=port_channel, device=dev)

        for number in range(100, 4097):
            BaseInterface(name='port-channel'+str(number), device=dev)

        with self.assertRaises(ValueError):
            port_channel = InterfaceName.port_channel(device=dev,
                                                      name='port-channel')

    def test_port_channel_interface_special_iterable(self):

        tb = Genie.testbed = Testbed()
        dev = Device(testbed=tb, name='my_device', os='nxos')

        for number in range(0, 5):
            port_channel = InterfaceName.port_channel(device=dev,
                                                      name='port-channel',
                                                      iterable=range(number, 5))
            self.assertEqual(port_channel, 'port-channel'+str(number))
            BaseInterface(name=port_channel, device=dev)

        with self.assertRaises(ValueError):
            port_channel = InterfaceName.port_channel(device=dev,
                                                      name='port-channel',
                                                      iterable=range(number, 5))

    def tearDown(self):
        Genie.testbed = None

class test_ip_to_mac(unittest.TestCase):

    def tearDown(self):
        Genie.testbed = None

    def test_mcast_ip_mac(self):

        mac = IpUtils.ip_to_mac(host_addr='224.234.23.45')
        mac1 = EUI('0100.5e6a.172d')
        mac1.dialect = mac_cisco
        self.assertEqual(mac, mac1)
        mac2 = EUI('0000.5e6a.172d')
        mac2.dialect = mac_cisco
        self.assertNotEqual(mac, mac2)

        mac = IpUtils.ip_to_mac(host_addr='224.1.1.1')
        mac3 = EUI('0100.5e01.0101')
        mac3.dialect = mac_cisco
        self.assertEqual(mac, mac3)
        mac4 = EUI('0000.5e01.0101')
        mac4.dialect = mac_cisco
        self.assertNotEqual(mac, mac4)

    def test_ucast_ip_mac(self):

        mac = IpUtils.ip_to_mac(host_addr='10.234.23.45')
        mac1 = EUI('0000.0aea.172d')
        mac1.dialect = mac_cisco
        self.assertEqual(mac, mac1)
        mac2 = EUI('0100.0aea.172d')
        mac2.dialect = mac_cisco
        self.assertNotEqual(mac, mac2)

        mac = IpUtils.ip_to_mac(host_addr='1.1.1.1')
        mac3 = EUI('0000.0101.0101')
        mac3.dialect = mac_cisco
        self.assertEqual(mac, mac3)
        mac4 = EUI('0100.5e01.0101')
        mac4.dialect = mac_cisco
        self.assertNotEqual(mac, mac4)

class test_ip(unittest.TestCase):

    def tearDown(self):
        Genie.testbed = None

    def test_ipv4_classfull(self):

        ipv4 = Ip(network="10.1.1.0",mask='24')
        ipv4.next_network()
        self.assertEqual('10.1.2.0', ipv4.network.network_address.compressed)
        self.assertEqual('10.1.2.1', ipv4.next_ip().ip.compressed)
        ipv4.next_network()
        self.assertNotEqual('10.1.3.1', ipv4.network.network_address.compressed)
        self.assertEqual('10.1.3.0', ipv4.network.network_address.compressed)

        ipv4 = Ip(network="10.1.252.0",mask='24')
        ipv4.next_network()
        self.assertEqual('10.1.253.0', ipv4.network.network_address.compressed)
        self.assertEqual('10.1.253.1', ipv4.next_ip().ip.compressed)
        ipv4.next_network()
        self.assertNotEqual('10.1.254.1', ipv4.network.network_address.compressed)
        self.assertEqual('10.1.254.0', ipv4.network.network_address.compressed)

        ipv4 = Ip(network="10.1.0.0",mask='16')
        ipv4.next_network()
        self.assertEqual('10.2.0.0', ipv4.network.network_address.compressed)
        self.assertEqual('10.2.0.1', ipv4.next_ip().ip.compressed)
        ipv4.next_network()
        self.assertNotEqual('10.3.0.1', ipv4.network.network_address.compressed)
        self.assertEqual('10.3.0.0', ipv4.network.network_address.compressed)

        ipv4 = Ip(network="10.252.0.0",mask='16')
        ipv4.next_network()
        self.assertEqual('10.253.0.0', ipv4.network.network_address.compressed)
        self.assertEqual('10.253.0.1', ipv4.next_ip().ip.compressed)
        ipv4.next_network()
        self.assertNotEqual('10.254.0.1', ipv4.network.network_address.compressed)
        self.assertEqual('10.254.0.0', ipv4.network.network_address.compressed)

        with self.assertRaises(StopIteration):
             ipv4.next_network()

        ipv4.reset()
        self.assertNotEqual('10.254.0.0', ipv4.network.network_address.compressed)
        self.assertEqual('10.252.0.0', ipv4.network.network_address.compressed)

        ipv4 = Ip(network="10.252.23.34",mask='32')
        with self.assertRaises(ValueError):
             ipv4.next_network()

    def test_ipv4_classless(self):

        ipv4 = Ip(network='192.168.0.0',mask='22')
        ipv4.next_network()
        self.assertEqual('192.168.4.0', ipv4.network.network_address.compressed)
        self.assertEqual('192.168.4.1', ipv4.next_ip().ip.compressed)
        ipv4.next_network()
        self.assertEqual('192.168.8.0', ipv4.network.network_address.compressed)
        self.assertNotEqual('192.168.8.2', ipv4.next_ip().ip.compressed)
        self.assertEqual('192.168.8.2', ipv4.next_ip().ip.compressed)
        ipv4.next_network()
        self.assertNotEqual('192.168.16.0', ipv4.network.network_address.compressed)

        ipv4 = Ip(network='192.168.248.0',mask='22')
        ipv4.next_network()
        self.assertEqual('192.168.252.0', ipv4.network.network_address.compressed)
        self.assertNotEqual('192.168.252.2', ipv4.next_ip().ip.compressed)
        self.assertEqual('192.168.252.2', ipv4.next_ip().ip.compressed)
        with self.assertRaises(StopIteration):
             ipv4.next_network()
        ipv4.reset()
        self.assertNotEqual('192.168.252.0', ipv4.network.network_address.compressed)
        self.assertEqual('192.168.248.0', ipv4.network.network_address.compressed)

        ipv4 = Ip(network='192.168.0.0',mask='25')
        ipv4.next_network()
        self.assertEqual('192.168.0.128', ipv4.network.network_address.compressed)
        self.assertNotEqual('192.168.0.130', ipv4.next_ip().ip.compressed)
        self.assertNotEqual('192.168.0.131', ipv4.next_ip().ip.compressed)
        self.assertEqual('192.168.0.131', ipv4.next_ip().ip.compressed)
        with self.assertRaises(StopIteration):
             ipv4.next_network()


    def test_ipv6_classfull(self):

        ipv6 = Ipv6(network="2001:db00::",mask='64')
        ipv6.next_network()
        self.assertEqual('2001:db00:0:1::',
                         ipv6.network.network_address.compressed)
        self.assertEqual('2001:db00:0:1::1', ipv6.next_ip().ip.compressed)
        ipv6.next_network()
        self.assertNotEqual('2001:db00:0:2::1',
                            ipv6.network.network_address.compressed)
        self.assertEqual('2001:db00:0:2::',
                         ipv6.network.network_address.compressed)

        ipv6 = Ipv6(network="2001:db00:0:252::",mask='64')
        ipv6.next_network()
        self.assertEqual('2001:db00:0:253::',
                         ipv6.network.network_address.compressed)
        self.assertEqual('2001:db00:0:253::1',
                         ipv6.next_ip().ip.compressed)
        ipv6.next_network()
        self.assertNotEqual('2001:db00:0:254::1',
                         ipv6.network.network_address.compressed)
        self.assertEqual('2001:db00:0:254::1',
                         ipv6.next_ip().ip.compressed)
        self.assertNotEqual('2001:db00:0:254::0',
                         ipv6.network.network_address.compressed)

        ipv6 = Ipv6(network="2001:db00::",mask='112')
        ipv6.next_network()
        self.assertEqual('2001:db00::1:0',
                         ipv6.network.network_address.compressed)
        self.assertEqual('2001:db00::1:1', ipv6.next_ip().ip.compressed)
        ipv6.next_network()
        self.assertNotEqual('2001:db00::2:1',
                            ipv6.network.network_address.compressed)
        self.assertEqual('2001:db00::2:0',
                         ipv6.network.network_address.compressed)

        ipv6 = Ipv6(network="2001:db00::fffc:0",mask='112')
        ipv6.next_network()
        self.assertEqual('2001:db00::fffd:0',
                         ipv6.network.network_address.compressed)
        self.assertEqual('2001:db00::fffd:1', ipv6.next_ip().ip.compressed)
        ipv6.next_network()
        self.assertNotEqual('2001:db00::fffe:1',
                            ipv6.network.network_address.compressed)
        self.assertEqual('2001:db00::fffe:0',
                         ipv6.network.network_address.compressed)

        with self.assertRaises(StopIteration):
             ipv6.next_network()

        ipv6.reset()
        self.assertNotEqual('2001:db00::fffe:0',
                            ipv6.network.network_address.compressed)
        self.assertEqual('2001:db00::fffc:0',
                         ipv6.network.network_address.compressed)

        ipv6 = Ip(network="2001:db00::ee34",mask='128')
        with self.assertRaises(ValueError):
             ipv6.next_network()

    def test_ipv6_classless(self):

        ipv6 = Ipv6(network="2001:db00::",mask='69')
        ipv6.next_network()
        self.assertEqual('2001:db00:0:0:800::',
                         ipv6.network.network_address.compressed)
        self.assertNotEqual('2001:db00::800:0:0:2',
                            ipv6.next_ip().ip.compressed)
        self.assertEqual('2001:db00::800:0:0:2', ipv6.next_ip().ip.compressed)
        ipv6.next_network()
        self.assertEqual('2001:db00:0:0:1000::',
                         ipv6.network.network_address.compressed)
        self.assertNotEqual('2001:db00::1000:0:0:2',
                            ipv6.next_ip().ip.compressed)
        self.assertEqual('2001:db00::1000:0:0:2', ipv6.next_ip().ip.compressed)

        ipv6 = Ipv6(network="2001:db00:0:0:b800::",mask='69')
        ipv6.next_network()
        self.assertEqual('2001:db00:0:0:c000::',
                         ipv6.network.network_address.compressed)
        self.assertNotEqual('2001:db00::c000:0:0:2',
                            ipv6.next_ip().ip.compressed)
        self.assertEqual('2001:db00::c000:0:0:2', ipv6.next_ip().ip.compressed)
        ipv6.next_network()
        self.assertEqual('2001:db00:0:0:c800::',
                         ipv6.network.network_address.compressed)
        self.assertNotEqual('2001:db00::c800:0:0:2',
                            ipv6.next_ip().ip.compressed)
        self.assertEqual('2001:db00::c800:0:0:2', ipv6.next_ip().ip.compressed)

        ipv6 = Ipv6(network="2001:db00::4000",mask='114')
        ipv6.next_network()
        self.assertEqual('2001:db00::8000',
                         ipv6.network.network_address.compressed)
        self.assertEqual('2001:db00::8001',
                         ipv6.next_ip().ip.compressed)
        ipv6.next_network()
        self.assertEqual('2001:db00::c000',
                         ipv6.network.network_address.compressed)
        self.assertNotEqual('2001:db00::c002',
                         ipv6.next_ip().ip.compressed)
        self.assertEqual('2001:db00::c002',
                         ipv6.next_ip().ip.compressed)

        with self.assertRaises(StopIteration):
             ipv6.next_network()

        ipv6.reset()
        self.assertNotEqual('2001:db00::c000',
                            ipv6.network.network_address.compressed)
        self.assertEqual('2001:db00::4000',
                         ipv6.network.network_address.compressed)

if __name__ == '__main__':
    unittest.main()
