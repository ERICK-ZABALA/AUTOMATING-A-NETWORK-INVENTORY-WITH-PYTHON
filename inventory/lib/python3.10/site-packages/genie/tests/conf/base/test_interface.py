#!/usr/bin/env python

#Todo unittest for Port-channel and sub-interface

import unittest
from unittest.mock import Mock
from netaddr import mac_cisco, EUI, core
from ipaddress import ip_network, IPv4Network, IPv4Address, ip_address,\
                      IPv4Interface, IPv6Interface

from pyats.datastructures import WeakList
from pyats.datastructures.logic import And, Not, Or
from pyats.topology.exceptions import DuplicateInterfaceError
from pyats.topology.exceptions import UnknownInterfaceError
from pyats.topology.exceptions import DuplicateInterfaceConnectionError, LinkError

# And import what's needed
from genie.conf import Genie
from genie.conf.base.link import Link
from genie.conf.base.device import Device
from genie.conf.base.testbed import Testbed
from genie.conf.base.exceptions import CountError
from genie.conf.base.interface import BaseInterface
from genie.conf.base.attributes import SubAttributesDict
from genie.conf.base.exceptions import UnknownInterfaceTypeError

class test_interface(unittest.TestCase):

    def tearDown(self):
        Genie.testbed = None

    def test_init(self):
        '''Test the creation interface itself and make sure it is assigned'''
        tb = Genie.testbed = Testbed()
        device = Device(testbed = tb, name='myDevice', os='nxos')
        link = Link(testbed = tb, name='myLink')
        # Let's try with an object without argument
        intf = BaseInterface(device = device , name='Ethernet4/47')

        # Make sure the attributes are set to their default values
        self.assertEqual(intf.name, 'Ethernet4/47')
        self.assertTrue(isinstance(intf, BaseInterface))
        self.assertEqual(intf.links, WeakList())
        self.assertEqual(intf.aliases, [])

        # Let's try with an object with argument
        intf = BaseInterface(name='Ethernet4/48',
                               device=device, links=[link], aliases=['e4/48'])

        # Make sure the attributes are set to the right values
        self.assertTrue(isinstance(intf, BaseInterface))
        self.assertEqual(intf.links[0], link)
        self.assertEqual(intf.aliases, ['e4/48'])

    def test_interface_setter(self):
        tb = Genie.testbed = Testbed()
        device = Device(testbed=tb, name='myDevice', os='nxos')

        intf = BaseInterface(device=device,
                             name='Ethernet4/47')
        intf.device = device
        self.assertNotEqual(intf.device, None)

    def test_interface_getter(self):
        tb = Genie.testbed = Testbed()
        device = Device(testbed=tb, name='myDevice', os='nxos')

        intf = BaseInterface(device=device,
                             name='Ethernet4/47')
        self.assertNotEqual(intf.device, None)

        intf = BaseInterface(device=device,
                             name='Banana')
        self.assertNotEqual(intf.device, None)

    def test_find_iterable_links(self):
        '''Can you find the links in the provided iterable'''
        # Let's say there is no Link
        tb = Genie.testbed = Testbed()

        # Add some Link to that Interface!
        link1 = Link(testbed = tb, name='r1-r2-1', aliases=['one'])
        link2 = Link(testbed = tb, name='r1-r2-2', aliases=['two'])
        link3 = Link(testbed = tb, name='r1-r2-3', aliases=['three'])
        link4 = Link(testbed = tb, name='r1-r2-4', aliases=['four'])
        link5 = Link(testbed = tb, name='r1-r2-5', obj_state='inactive')

        output = tb.find_links(iterable=[link1, link2, link3, link5])

        # Order might be different
        self.assertEqual(set(output), set([link1, link2, link3]))
        self.assertEqual(sorted([link.name for link in output]),
                         sorted([link.name for link in \
                                                 [link1, link2, link3]]))

        # Let's filter
        # Return many
        output = tb.find_links(iterable=[link1, link2, link3],
                               name=Or('r1-r2-1', 'r1-r2-3'))

        # Order might be different
        self.assertEqual(set(output), set([link1, link3]))
        self.assertEqual(sorted([link.name for link in output]),
                         sorted([link.name for link in [link1, link3]]))

        # count = 1
        output = tb.find_links(iterable=[link1, link2, link3],
                               name=Or('r1-r2-1', 'r1-r2-3'), count=1)

        self.assertEqual(len(output), 1)

        # Negative
        output = tb.find_links(iterable=[link1, link2, link3],
                               name=Not('r1-r2-1'))

        # Order might be different
        self.assertEqual(set(output), set([link2, link3]))
        self.assertEqual(sorted([link.name for link in output]),
                         sorted([link.name for link in [link2, link3]]))

        # Multi fields
        output = tb.find_links(iterable=[link1, link2, link3],
                               name=Not('r1-r2-1'), aliases=Or('two'))

        # Order might be different
        self.assertEqual(set(output), set([link2]))
        self.assertEqual(sorted([link.name for link in output]),
                         sorted([link.name for link in [link2]]))

        # Verify if request 3, and only 2 is returned we get an exception

        with self.assertRaises(CountError):
            output = tb.find_links(name=Or('r1-r2-1', 'r1-r2-2'), count=3)

        # Make sure only links can be given as iterable
        output = tb.find_links(iterable=[])
        self.assertEqual(output, [])

        self.assertEqual(len(tb.find_links(iterable=[tb])), 0)

    def test_device_attribute(self):
        tb = Genie.testbed = Testbed()
        dev = Device(testbed = tb, name='myDevice', os='nxos')

        interface = BaseInterface(device = dev,
                               name='Ethernet4/47')

        interface.device = dev

        self.assertEqual(interface.__device__(), interface.device)
        self.assertEqual(interface.__device__(), dev)

        interface.device = None
        self.assertEqual(interface.__device__, interface.device)
        self.assertEqual(interface.__device__, None)


class TestPyatsInterfaceClass(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        global Interface, Device, Link, IPv4Interface, IPv6Interface
        global Link
        from genie.conf.base.interface import BaseInterface as Interface
        from ipaddress import IPv4Interface, IPv6Interface

    def setUp(self):
        self.device = Device(name = 'testDevice')
        self.intf = Interface(name = 'testInterface', type = 'testType')
        self.link = Link(name = 'testLink')

    def test_creation_bare(self):
        intf = Interface(name = 'testInterface',
                         type = 'testType')

        # AssertionError: <class 'genie_libs.conf.interface.Interface'> is not
        # <class 'genie.conf.base.interface.BaseInterface'>
        # self.assertIs(type(intf), Interface)
        self.assertTrue(hasattr(intf, 'name'))
        self.assertTrue(hasattr(intf, 'alias'))
        self.assertTrue(hasattr(intf, 'type'))
        self.assertTrue(hasattr(intf, 'ipv4'))
        self.assertTrue(hasattr(intf, 'ipv6'))
        self.assertTrue(hasattr(intf, 'link'))

        self.assertEqual(intf.name, 'testInterface')
        self.assertEqual(intf.alias, 'testInterface')
        self.assertIs(intf.type, 'testType')
        self.assertIs(intf.ipv4, None)
        self.assertIs(intf.ipv6, None)
        self.assertIs(intf.link, None)

    def test_alias(self):
        intf = Interface(name = 'testInterface',
                         type = 'testType',
                         alias = 'godmode')        

        self.assertEqual(intf.alias, 'godmode')
        self.assertEqual(intf.name, 'testInterface')

    def test_creation_with_ip(self):
        intf = Interface(name = 'testInterface',
                         type = 'testType',
                         ipv4 = '1.1.1.1/24',
                         ipv6 = 'fc00::/7')

        # AssertionError: <class 'genie_libs.conf.interface.Interface'> is not
        # <class 'genie.conf.base.interface.BaseInterface'>
        # self.assertIs(type(intf), Interface)
        self.assertIs(type(intf.ipv4), IPv4Interface)
        self.assertIs(type(intf.ipv6), IPv6Interface)
        self.assertIs(intf.link, None)


    def test_creation_with_link_object(self):
        intf = Interface(name = 'testInterface',
                         type = 'testType',
                         ipv4 = '1.1.1.1/24',
                         ipv6 = 'fc00::/7',
                         link = self.link)

        self.assertIs(intf.link, self.link)
        self.assertIn(intf, intf.link.interfaces)
        self.assertEqual(len(intf.link.interfaces), 1)

    def test_remote_interfaces(self):
        intf1 = Interface(name = 'testInterface_1',
                          type = 'testType',
                          ipv4 = '1.1.1.1/24',
                          link = self.link)

        intf2 = Interface(name = 'testInterface_2',
                          type = 'testType',
                          ipv4 = '1.1.1.2/24',
                          link = self.link)

        self.assertIs(intf1.link, intf2.link)
        self.assertEqual(len(intf1.link.interfaces), 2)
        self.assertIs(type(intf1.remote_interfaces),  set)
        self.assertEqual(len(intf1.remote_interfaces), 1)
        self.assertIn(intf2, intf1.remote_interfaces)
        self.assertIn(intf1, intf2.remote_interfaces)

    def test_remote_interfaces_error(self):
        intf1 = Interface(name = 'testInterface_1',
                          type = 'testType',
                          ipv4 = '1.1.1.1/24')

        intf1.link = self.link

        self.link.interfaces = []

        from pyats.topology import exceptions
        with self.assertRaises(exceptions.LinkError):
            intf1.remote_interfaces

    def test_remote_interfaces_empty(self):
        intf1 = Interface(name = 'testInterface_1',
                          type = 'testType',
                          ipv4 = '1.1.1.1/24')
        self.assertEqual(intf1.remote_interfaces, set())

    def test_remote_devices_empty(self):
        intf1 = Interface(name = 'testInterface_1',
                          type = 'testType',
                          ipv4 = '1.1.1.1/24')
        self.assertEqual(intf1.remote_devices, set())

    def test_remote_devices(self):
        intf1 = Interface(name = 'testInterface_1',
                          type = 'testType')
        intf2 = Interface(name = 'testInterface_2',
                          type = 'testType')
        intf3 = Interface(name = 'testInterface_3',
                          type = 'testType')
        self.link.connect_interface(intf1)
        self.link.connect_interface(intf2)
        self.link.connect_interface(intf3)
        
        deviceA = Device('A')
        deviceB = Device('B')
        deviceC = Device('C')

        deviceA.add_interface(intf1)
        deviceB.add_interface(intf2)
        deviceC.add_interface(intf3)

        self.assertEqual(intf1.remote_devices, set([deviceB, deviceC]))
        self.assertEqual(intf2.remote_devices, set([deviceA, deviceC]))
        self.assertEqual(intf3.remote_devices, set([deviceA, deviceB]))
        self.link.disconnect_interface(intf2)

        self.assertEqual(intf1.remote_devices, set([deviceC]))
        self.assertEqual(intf2.remote_devices, set())
        self.assertEqual(intf3.remote_devices, set([deviceA]))

    def test_weakref(self):
        class DummyDevice(object):
            from pyats.topology.bases import TopologyDict
            interfaces = TopologyDict()
            def __contains__(self, obj):
                return True

            # Fake add_intrerface as intf.device setter will require devive
            # to have interfaces attribute and add_interface method.
            def add_interface(self, obj):
                pass

        device = DummyDevice()

        self.intf.device = device

        del device
        import gc; gc.collect()

        self.assertIs(self.intf.device, None)

    def test_assign_device_adds_interface(self):
        self.intf.device = self.device

        self.assertIn(self.intf, self.device)

    def test_none_device_removes_interface(self):
        self.intf.device = self.device

        self.assertIn(self.intf, self.device)
        self.intf.device = None
        self.assertNotIn(self.intf, self.device)

    def test_cannot_delete_link_attr(self):
        with self.assertRaises(AttributeError):
            del self.intf.link

    def test_assign_link_adds_interface(self):
        self.intf.link = self.link
        self.assertIn(self.intf, self.link)

    def test_none_link_removes_interface(self):
        self.intf.link = self.link

        self.assertIn(self.intf, self.link)
        self.intf.link = None
        self.assertNotIn(self.intf, self.link)


if __name__ == '__main__':
    unittest.main()
