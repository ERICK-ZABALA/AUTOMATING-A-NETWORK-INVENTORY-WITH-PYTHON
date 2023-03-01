#!/usr/bin/env python

# Import unittest module
import unittest, os, gc, yaml, logging
from unittest.mock import Mock
import collections

from pyats.datastructures.logic import And, Not, Or
from pyats.utils.objects import R
from pyats.topology.exceptions import DuplicateDeviceError, UnknownDeviceError,\
                                    DuplicateLinkError

# Let's test Testbed, so let's import the module
# And whats needed to test it
from genie.tests.conf import TestCase
from genie.conf import Genie
from genie.conf.base import Base
from genie.conf.base.link import Link
from genie.conf.base.device import Device
from genie.conf.base.testbed import Testbed
from genie.conf.base.interface import BaseInterface
from genie.conf.base.exceptions import CountError, UnknownLinkError

yaml_dir = os.path.join(os.path.dirname(__file__), 'yamls')


class test_testbed(TestCase):

    def test_init(self):
        '''Test the creation of a testbed itself and make sure it is assigned'''

        # Let's try with an object without argument
        tb = Testbed()

        # Make sure the attributes are set to their default values
        self.assertEqual(tb.name, None)
        self.assertEqual(list(tb.devices), [])
        self.assertEqual(list(tb.links), [])

        # Let's do the same, but with arguments
        tb = Testbed(name='testbed_name')

        # Make sure the attributes are set to correct value
        self.assertEqual(tb.name, 'testbed_name')
        self.assertEqual(list(tb.devices), [])
        self.assertEqual(list(tb.links), [])

    def test_add_remove_device(self):
        '''Add a device to a testbed'''
        # Create a testbed
        tb = Testbed()

        # Create a fake device object
        device = Device(testbed = tb, name='PE1', aliases=['uut'], os='nxos')

        # Make sure it was added correctly
        self.assertIn('PE1', tb.devices)
        self.assertEqual(tb.devices['PE1'], device)

        # Make sure testbed was added to device
        self.assertEqual(tb.devices['PE1'].testbed, tb)

        # Now remove the device
        tb.remove_device(device)

        # Make sure it was added correctly
        self.assertNotIn('PE1', tb.devices)

        # Make sure testbed was removed correctly to the device
        self.assertEqual(device.testbed, None)

    def test_add_remove_interface(self):
        '''Add a device to a testbed'''
        # Create a testbed
        tb = Testbed()

        # Create a fake device object
        device = Device(testbed = tb, name='PE1', aliases=['uut'], os='nxos')

        # Create a fake Interface object
        interface = BaseInterface(device = device, name='Ethernet4/7')

        # Make sure it was added correctly
        self.assertIn('PE1', tb.devices)
        self.assertIn(interface.name, tb.devices['PE1'].interfaces)
        self.assertEqual(tb.devices['PE1'], device)

        # Make sure testbed was added to device
        self.assertEqual(tb.devices['PE1'].testbed, tb)

        # Now remove the interface
        tb.devices['PE1'].remove_interface(interface)

        # Make sure it was removed correctly
        self.assertNotIn(interface, tb.devices['PE1'].interfaces)

    def test_add_remove_link(self):
        # '''Add/Remove a link to a testbed'''
        '''Add/Remove a link by removing device.interface'''

        # Create a testbed
        tb = Testbed()

        # Device is needed for new genie/pyats objects implementation.
        # Links are retrieved from the device object in pyats so we need to 
        # define a device
        # Create a fake device object
        device = Device(testbed = tb, name='PE1', aliases=['uut'], os='nxos')

        # Create a fake Interface object
        interface = BaseInterface(device = device, name='Ethernet4/7')

        # Create a fake link object
        link = Link(testbed = tb, name='r1-r2-1', aliases=['myLink'])

        # Add this interface to a device and a link
        link.connect_interface(interface)

        # Make sure it was added correctly
        self.assertIn(link, tb.links)
        # self.assertEqual(tb.links['r1-r2-1'], link)

        # Make sure link was added to the device
        self.assertIn(link, device.links)
        self.assertIn(device, link.devices)

        # Remove interface from the device
        device.remove_interface(interface)

        # Make sure it was removed correctly
        self.assertNotIn(link, tb.links)


    def test_add_remove_link_with_interface(self):
        # '''Add/Remove a link to a testbed'''
        '''Add/Remove a link by removing testbed.device'''

        tb = Testbed()
        # Create a fake link object
        link = Link(testbed = tb, name='r1-r2-1')

        # Create a fake device object
        device = Device(testbed = tb, name='PE1', os='nxos')

        # Create a fake Interface object
        interface = BaseInterface(device = device, name='Ethernet4/7')

        # Add this interface to a device and a link
        link.connect_interface(interface)

        # Verify it
        self.assertIn(interface, link.interfaces)

        # Create a testbed
        tb = Testbed()

        # Make sure links is empty
        self.assertEqual(list(tb.links), [])
        self.assertEqual(tb.links, set())

        # Add link to testbed
        # tb.add_link(link)

        # Add device to testbed
        tb.add_device(device)

        # Make sure it was added correctly
        self.assertIn(link, tb.links)

        # Remove device from testbed
        tb.remove_device(device)

        # Make sure it was removed correctly
        self.assertNotIn(link, tb.links)

        # Make sure the Interface is also gone from this testbed
        self.assertNotIn(interface, tb.interfaces)

    def test_wrong_device(self):
        '''Look for a device that doesn't exist in testbed'''

        # Create a testbed
        tb = Testbed()

        # Look for device 'PE1'
        with self.assertRaises(KeyError):
            tb.devices['PE1']

    def test_wrong_link(self):
        '''Look for a link that doesn't exist in testbed'''

        # Create a testbed
        tb = Testbed()

        # Create a link
        link = Link(name='r1-r2-1')

        # Try to get the link from the testbed
        with self.assertRaises(KeyError):
            tb.links.pop()

    def test_add_already_existing_device(self):
        '''Add a device that already exists on the testbed'''
        tb = Testbed()
        # Create a fake device object
        device = Device(testbed = tb, name='PE1', os='nxos')

        # Create a testbed
        tb = Testbed()

        # Add device to testbed
        tb.add_device(device)
        with self.assertRaises(DuplicateDeviceError):
            tb.add_device(device)

    def test_add_remove_add_device(self):
        '''Add a device, remove it, and add it again'''

        # Create a testbed
        tb = Testbed()

        # Create a fake device object
        device = Device(testbed = tb, name='PE1', aliases=['uut'], os='nxos')

        # Removing it by name this time
        tb.remove_device(device.name)

        with self.assertRaises(UnknownDeviceError):
            tb.remove_device(device.name)

        # Add device to testbed
        tb.add_device(device)

    def test_find_devices(self):
        '''Can you find some device?!'''

        # Let's say there is no device
        tb = Testbed()

        output = tb.find_devices()

        self.assertEqual(output, [])

        # Let's add some device
        dev1 = Device(testbed=tb, name='PE1', aliases=['uut'], os='nxos')
        dev2 = Device(testbed=tb, name='P1', aliases=['helper1'], os='nxos')
        dev3 = Device(testbed=tb, name='core', aliases=['helper2'], os='nxos')
        dev4 = Device(testbed=tb, name='devx', obj_state='inactive', os='nxos')

        output = tb.find_devices()

        # Order might be different
        self.assertEqual(set(output), set([dev1, dev2, dev3]))
        self.assertEqual(sorted([link.name for link in output]),
                         sorted([link.name for link in [dev1, dev2, dev3]]))

        # Let's filter
        output = tb.find_devices(name=Or('PE1', 'P1'))

        # Order might be different
        self.assertEqual(set(output), set([dev1, dev2]))
        self.assertEqual(sorted([dev.name for dev in output]),
                         sorted([dev.name for dev in [dev1, dev2]]))

        # count = 1
        output = tb.find_devices(name=Or('PE1', 'P1'), count=1)

        self.assertEqual(len(output), 1)

        # Negative
        output = tb.find_devices(name=Not('PE1'))

        # Order might be different
        self.assertEqual(set(output), set([dev2, dev3]))
        self.assertEqual(sorted([link.name for link in output]),
                         sorted([link.name for link in [dev2, dev3]]))

        # Multi fields
        # Also test single output are also list
        output = tb.find_devices(name=Not('PE1'), aliases=Or('helper1'))

        # Order might be different
        self.assertEqual(set(output), set([dev2]))
        self.assertEqual(sorted([link.name for link in output]),
                         sorted([link.name for link in [dev2]]))

        # Verify if request 3, and only 2 is returned we get an exception
        with self.assertRaises(CountError):
            output = tb.find_devices(name=Or('PE1', 'P1'), count=3)

        # Let's verify the state now
        output = tb.find_devices(obj_state=Or('inactive'))

        # Order might be different
        self.assertEqual(set(output), set([dev4]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [dev4]]))

        # Make sure it works if it is a callable
        def alwaysTrue(*args, **kwargs):
            return True
        def alwaysFalse(*args, **kwargs):
            return False

        def OnlyTrueFordevX(obj):
            if obj.name == 'devx':
                return True
            else:
                return False

        output = tb.find_devices(obj_state=alwaysTrue)

        self.assertEqual(set(output), set([dev1, dev2, dev3, dev4]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [dev1, dev2, dev3,
                                                        dev4]]))

        output = tb.find_devices(obj_state=alwaysFalse)

        self.assertEqual(set(output), set([]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in []]))

        output = tb.find_devices(obj_state=alwaysTrue,
                                 callable_=OnlyTrueFordevX)

        self.assertEqual(set(output), set([dev4]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [dev4]]))


    def test_find_iterable_devices(self):
        '''Can you find some device in this iterable?!'''

        # Let's say there is no device
        tb = Testbed()

        output = tb.find_devices()

        self.assertEqual(output, [])

        # Let's add some device
        dev1 = Device(testbed=tb, name='PE1', aliases=['uut'], os='nxos')
        dev2 = Device(testbed=tb, name='P1', aliases=['helper1'], os='nxos')
        dev3 = Device(testbed=tb, name='core', aliases=['helper2'], os='nxos')
        dev4 = Device(testbed=tb, name='devx', obj_state='inactive', os='nxos')

        output = tb.find_devices(iterable={'PE1':dev1, 'P1':dev2})
        output = tb.find_devices(iterable=[dev1, dev2])

        # Order might be different
        self.assertEqual(set(output), set([dev1, dev2]))
        self.assertEqual(sorted([link.name for link in output]),
                         sorted([link.name for link in [dev1, dev2]]))

        # Let's filter
        output = tb.find_devices(iterable=[dev1, dev2],
                                 name=Or('PE1', 'P1'))

        # Order might be different
        self.assertEqual(set(output), set([dev1, dev2]))
        self.assertEqual(sorted([dev.name for dev in output]),
                         sorted([dev.name for dev in [dev1, dev2]]))

        # count = 1
        output = tb.find_devices(iterable=[dev1, dev2], name=Or('PE1', 'P1'),
                                 count=1)

        self.assertEqual(len(output), 1)

        # Negative
        output = tb.find_devices(iterable=[dev1, dev2], name=Not('PE1'))

        # Order might be different
        self.assertEqual(set(output), set([dev2]))
        self.assertEqual(sorted([link.name for link in output]),
                         sorted([link.name for link in [dev2]]))

        # Multi fields
        # Also test single output are also list
        output = tb.find_devices(iterable=[dev1, dev2], name=Not('PE1'),
                                 aliases=Or('helper1'))

        # Order might be different
        self.assertEqual(set(output), set([dev2]))
        self.assertEqual(sorted([link.name for link in output]),
                         sorted([link.name for link in [dev2]]))

        # Verify if request 3, and only 2 is returned we get an exception
        with self.assertRaises(CountError):
            output = tb.find_devices(iterable=[dev1, dev2],
                                     name=Or('PE1', 'P1'), count=3)

        # Let's verify the state now
        output = tb.find_devices(iterable=[dev1, dev2, dev3, dev4],
                                 obj_state=Or('inactive'))

        # Order might be different
        self.assertEqual(set(output), set([dev4]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [dev4]]))

        # Make sure it works if it is a callable
        def alwaysTrue(*args, **kwargs):
            return True
        def alwaysFalse(*args, **kwargs):
            return False

        def OnlyTrueFordevX(obj):
            if obj.name == 'devx':
                return True
            else:
                return False

        output = tb.find_devices(iterable=[dev1, dev2, dev3, dev4],
                                 obj_state=alwaysTrue)

        self.assertEqual(set(output), set([dev1, dev2, dev3, dev4]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [dev1, dev2, dev3,
                                                        dev4]]))

        output = tb.find_devices(iterable=[dev1, dev2, dev3, dev4],
                                 obj_state=alwaysFalse)

        self.assertEqual(set(output), set([]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in []]))

        output = tb.find_devices(iterable=[dev1, dev2, dev3, dev4],
                                 obj_state=alwaysTrue,
                                 callable_=OnlyTrueFordevX)

        self.assertEqual(set(output), set([dev4]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [dev4]]))

    def test_find_links(self):
        '''Can you find links?'''

        # Let's say there is no Link
        tb = Testbed()

        output = tb.find_links()

        self.assertEqual(output, [])

        # Add some Link to that Interface!
        link1 = Link(testbed=tb, name='r1-r2-1', aliases=['one'])
        link2 = Link(testbed=tb, name='r1-r2-2', aliases=['two'])
        link3 = Link(testbed=tb, name='r1-r2-3', aliases=['three'])
        link4 = Link(testbed=tb, name='r1-r2-4', aliases=['four'])
        link5 = Link(testbed=tb, name='r1-r2-5', obj_state='inactive')

        # Create a fake device object
        device = Device(testbed = tb, name='PE1', os='nxos')

        # Create a fake Interface object
        interface1 = BaseInterface(device = device, name='Ethernet4/7')
        interface2 = BaseInterface(device = device, name='Ethernet4/8')
        interface3 = BaseInterface(device = device, name='Ethernet4/9')
        interface4 = BaseInterface(device = device, name='Ethernet4/10')
        interface5 = BaseInterface(device = device, name='Ethernet4/11')

        # Add this interface to a device and a link
        link1.connect_interface(interface1)
        link2.connect_interface(interface2)
        link3.connect_interface(interface3)
        link4.connect_interface(interface4)
        link5.connect_interface(interface5)

        output = tb.find_links()

        # Order might be different
        self.assertEqual(set(output), set([link1, link2, link3, link4]))
        self.assertEqual(sorted([link.name for link in output]),
                         sorted([link.name for link in \
                                                 [link1, link2, link3, link4]]))

        # Let's filter
        # Return many
        output = tb.find_links(name=Or('r1-r2-1', 'r1-r2-3'))

        # Order might be different
        self.assertEqual(set(output), set([link1, link3]))
        self.assertEqual(sorted([link.name for link in output]),
                         sorted([link.name for link in [link1, link3]]))

        # count = 1
        output = tb.find_links(name=Or('r1-r2-1', 'r1-r2-3'), count=1)

        self.assertEqual(len(output), 1)

        # Negative
        output = tb.find_links(name=Not('r1-r2-1'))

        # Order might be different
        self.assertEqual(set(output), set([link2, link3, link4]))
        self.assertEqual(sorted([link.name for link in output]),
                         sorted([link.name for link in [link2, link3, link4]]))

        # Multi fields
        output = tb.find_links(name=Not('r1-r2-1'), aliases=Or('two'))

        # Order might be different
        self.assertEqual(set(output), set([link2]))
        self.assertEqual(sorted([link.name for link in output]),
                         sorted([link.name for link in [link2]]))

        # Verify if request 3, and only 2 is returned we get an exception

        with self.assertRaises(CountError):
            output = tb.find_devices(name=Or('PE1', 'P1'), count=3)

        # Make sure only links can be given as iterable
        output = tb.find_links(iterable=[])
        self.assertEqual(output, [])

        self.assertEqual(len(tb.find_links(iterable=[tb])), 0)

        # Let's verify the state now
        output = tb.find_links(obj_state=Or('inactive'))

        # Order might be different
        self.assertEqual(set(output), set([link5]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [link5]]))

        # Make sure it works if it is a callable
        def alwaysTrue(*args, **kwargs):
            return True
        def alwaysFalse(*args, **kwargs):
            return False

        def OnlyTrueForlink5(obj):
            if obj.name == 'r1-r2-5':
                return True
            else:
                return False

        output = tb.find_links(iterable=[link1, link2, link3, link5],
                               obj_state=alwaysTrue)

        self.assertEqual(set(output), set([link1, link2, link3, link5]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [link1, link2, link3,
                                                        link5]]))

        output = tb.find_links(iterable=[link1, link2, link3, link5],
                               obj_state=alwaysFalse)

        self.assertEqual(set(output), set([]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in []]))

        output = tb.find_links(iterable=[link1, link2, link3, link5],
                               obj_state=alwaysTrue,
                               callable_=OnlyTrueForlink5)

        self.assertEqual(set(output), set([link5]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [link5]]))

    def test_find_r_links(self):
        '''Test R function of find links'''
        # Let's say there is no Link
        tb = Testbed()

        dev1 = Device(testbed=tb, name='PE1', aliases=['uut'], os='nxos')
        dev2 = Device(testbed=tb, name='P1', aliases=['helper1'], os='nxos')
        dev3 = Device(testbed=tb, name='core', aliases=['helper2'], os='nxos')
        dev4 = Device(testbed=tb, name='dev', obj_state='inactive', os='nxos')

        # Add some Link to that Interface!
        link1 = Link(testbed=tb, name='r1-r2-1', aliases=['one'])
        link2 = Link(testbed=tb, name='r1-r2-2', aliases=['two'])
        link3 = Link(testbed=tb, name='r1-r2-3', aliases=['three'])
        link4 = Link(testbed=tb, name='r1-r2-4', aliases=['four'])
        link5 = Link(testbed=tb, name='r1-r2-5', obj_state='inactive')

        interface1 = BaseInterface(device = dev1, name='Ethernet4/1')
        interface2 = BaseInterface(device = dev1, name='Ethernet4/2')
        interface3 = BaseInterface(device = dev2, name='Ethernet4/3')
        interface4 = BaseInterface(device = dev3, name='Ethernet4/4')
        interface5 = BaseInterface(device = dev3, name='Ethernet4/5')

        # add those interfaces to the links
        link1.connect_interface(interface1)
        link1.connect_interface(interface3)

        link2.connect_interface(interface2)

        link3.connect_interface(interface4)

        link5.connect_interface(interface5)

        # Find all the links that have an interfaces on device PE1
        output = tb.find_links(R(interfaces__device__name='PE1'))

        self.assertEqual(set(output), set([link1, link2]))
        self.assertEqual(sorted([link.name for link in output]),
                         sorted([link.name for link in \
                                                 [link1, link2]]))

        # Find all the links that have an interfaces on device PE1 and
        # connected to P1
        output = tb.find_links(R(interfaces__device__name='PE1'),
                               R(interfaces__device__name='P1'))

        self.assertEqual(set(output), set([link1]))
        self.assertEqual(sorted([link.name for link in output]),
                         sorted([link.name for link in [link1]]))

        # Find all the links that have an interfaces on device PE1 and on this
        # device it has interface Ethernet4/1

        output = tb.find_links(R(interfaces__device__name='PE1',
                                 interfaces__name='Ethernet4/1'))

        self.assertEqual(set(output), set([link1]))
        self.assertEqual(sorted([link.name for link in output]),
                         sorted([link.name for link in [link1]]))

        # Find all the links that have an interfaces on device PE1 and on this
        # device it has interface Ethernet4/3
        output = tb.find_links(R(interfaces__device__name='PE1',
                                     interfaces__name='Ethernet4/3'))

        self.assertEqual(set(output), set([]))
        self.assertEqual(sorted([link.name for link in output]),
                         sorted([link.name for link in []]))

    def test_find_iterable_links(self):
        '''Can you find the links in the provided iterable'''
        # Let's say there is no Link
        tb = Testbed()

        # Add some Link to that Interface!
        link1 = Link(testbed=tb, name='r1-r2-1', aliases=['one'])
        link2 = Link(testbed=tb, name='r1-r2-2', aliases=['two'])
        link3 = Link(testbed=tb, name='r1-r2-3', aliases=['three'])
        link4 = Link(testbed=tb, name='r1-r2-4', aliases=['four'])
        link5 = Link(testbed=tb, name='r1-r2-5', obj_state='inactive')

        output = tb.find_links(iterable=[link1, link2, link3, link5])

        # Order might be different
        self.assertEqual(set(output), set([link1, link2, link3]))
        self.assertEqual(sorted([link.name for link in output]),
                         sorted([link.name for link in \
                                                 [link1, link2, link3]]))

        # Let's filter
        # Return many
        output = tb.find_links(iterable=[link1, link2, link3, link5],
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
            output = tb.find_devices(name=Or('PE1', 'P1'), count=3)

        # Make sure only links can be given as iterable
        output = tb.find_links(iterable=[])
        self.assertEqual(output, [])

        self.assertEqual(len(tb.find_links(iterable=[tb])), 0)

        # Let's verify the state now
        output = tb.find_links(iterable=[link1, link2, link3, link5],
                               obj_state=Or('inactive'))

        # Order might be different
        self.assertEqual(set(output), set([link5]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [link5]]))

        # Make sure it works if it is a callable
        def alwaysTrue(*args, **kwargs):
            return True
        def alwaysFalse(*args, **kwargs):
            return False

        def OnlyTrueForlink5(obj):
            if obj.name == 'r1-r2-5':
                return True
            else:
                return False

        output = tb.find_links(iterable=[link1, link2, link3, link5],
                               obj_state=alwaysTrue)

        self.assertEqual(set(output), set([link1, link2, link3, link5]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [link1, link2, link3,
                                                        link5]]))

        output = tb.find_links(iterable=[link1, link2, link3, link5],
                               obj_state=alwaysFalse)

        self.assertEqual(set(output), set([]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in []]))

        output = tb.find_links(iterable=[link1, link2, link3, link5],
                               obj_state=alwaysTrue,
                               callable_=OnlyTrueForlink5)

        self.assertEqual(set(output), set([link5]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [link5]]))

    def test_set_active_objects(self):
        '''Test set_active_objects testbed functionality'''
        # Let's say there is no Link
        testbed = Testbed(name='myTestbed')
        dev1 = Device(name='PE1', testbed=testbed, aliases=['uut'], os='iosxe')
        dev2 = Device(name='P1', testbed=testbed, aliases=['helper'], os='iosxe')
        intf_dev1 = BaseInterface(name='Ethernet3/7', device=dev1, aliases=['PE1'])
        intf_dev2 = BaseInterface(name='Ethernet3/7', device=dev2, aliases=['P1'])
        link1 = Link(name='dev1-dev2-1', testbed=testbed, aliases=['used link'])
        link1.connect_interface(intf_dev1)
        link1.connect_interface(intf_dev2)
        link2 = Link(name='dev1-dev2-1', testbed=testbed, aliases=['unused link'])

        # dev1.interfaces is a TopologyDict
        testbed.set_active_interfaces(dev1.interfaces)

        self.assertEqual(dev1.interfaces['Ethernet3/7'],
            testbed.find_interfaces(obj_state='active')[0])
        self.assertEqual(dev1,
            testbed.find_devices(obj_state='active')[0])

        self.assertEqual(dev2.interfaces['Ethernet3/7'],
            testbed.find_interfaces(obj_state='inactive')[0])
        self.assertEqual(dev2,
            testbed.find_devices(obj_state='inactive')[0])

    def test_instances(self):

        class X(Base):
            pass

        class A(X):
            def __hash__(self):
                return 0

        class B(Base):
            def __hash__(self):
                return 0

        tb = Testbed(name='tb')
        self.assertCountEqual(tb.object_instances(), [])

        x = X(testbed=tb)  # Not hashable, never tracked
        self.assertCountEqual(tb.object_instances(), [])
        self.assertCountEqual(tb.object_instances(X), [])
        self.assertCountEqual(tb.object_instances(A), [])
        self.assertCountEqual(tb.object_instances(B), [])

        a = A(testbed=tb)
        self.assertCountEqual(tb.object_instances(), [a])
        self.assertCountEqual(tb.object_instances(X), [a])
        self.assertCountEqual(tb.object_instances(A), [a])
        self.assertCountEqual(tb.object_instances(B), [])

        b = B(testbed=tb)
        self.assertCountEqual(tb.object_instances(), [a, b])
        self.assertCountEqual(tb.object_instances(X), [a])
        self.assertCountEqual(tb.object_instances(A), [a])
        self.assertCountEqual(tb.object_instances(B), [b])

        del a
        self.assertCountEqual(tb.object_instances(), [b])
        self.assertCountEqual(tb.object_instances(X), [])
        self.assertCountEqual(tb.object_instances(A), [])
        self.assertCountEqual(tb.object_instances(B), [b])

        del b
        self.assertCountEqual(tb.object_instances(), [])
        self.assertCountEqual(tb.object_instances(X), [])
        self.assertCountEqual(tb.object_instances(A), [])
        self.assertCountEqual(tb.object_instances(B), [])

        dev1 = Device(testbed=tb, name='dev1', os='nxos')
        dev2 = Device(testbed=tb, name='dev2', os='nxos')
        self.assertCountEqual(tb.object_instances(), [dev1, dev2])
        self.assertCountEqual(tb.object_instances(Device), [dev1, dev2])

        tb2 = Testbed(name='tb2')
        dev21 = Device(testbed=tb2, name='dev21', os='iosxr')
        self.assertCountEqual(tb.object_instances(), [dev1, dev2])
        self.assertCountEqual(tb.object_instances(Device), [dev1, dev2])
        self.assertCountEqual(tb2.object_instances(), [dev21])
        self.assertCountEqual(tb2.object_instances(Device), [dev21])

        intf1 = BaseInterface(device=dev1, name='Ethernet0/0')
        self.assertCountEqual(tb.object_instances(), [dev1, dev2, intf1])
        self.assertCountEqual(tb.object_instances(Device), [dev1, dev2])
        self.assertCountEqual(tb.object_instances(BaseInterface), [intf1])
        self.assertCountEqual(tb2.object_instances(), [dev21])
        self.assertCountEqual(tb2.object_instances(Device), [dev21])
        self.assertCountEqual(tb2.object_instances(BaseInterface), [])

class test_build(TestCase):

    def setUp(self):
        self.tb = Testbed()

        # Let's add some device
        self.dev1 = Device(testbed = self.tb, name='PE1', os='nxos')
        self.dev2 = Device(testbed = self.tb, name='P1', os='nxos')
        self.dev3 = Device(testbed = self.tb, name='core', os='nxos')

        # Create a fake Interface object
        self.interface1 = BaseInterface(device = self.dev1, name='Ethernet4/1')
        self.interface2 = BaseInterface(device = self.dev1, name='Ethernet4/2')
        self.interface3 = BaseInterface(device = self.dev2, name='Ethernet4/3')
        self.interface4 = BaseInterface(device = self.dev3, name='Ethernet4/4')
        self.interface5 = BaseInterface(device = self.dev3, name='Ethernet4/5')

        # Connect them via links
        self.link1 = Link(testbed=self.tb ,name='r1-r2-1')
        self.link2 = Link(testbed=self.tb ,name='r1-r2-2')

        self.link1.connect_interface(self.interface1)
        self.link1.connect_interface(self.interface3)

        self.link2.connect_interface(self.interface2)
        self.link2.connect_interface(self.interface4)

    def test_build_config(self):
        # Let's say there is no device
        tb = Testbed()

        output = tb.build_config(apply = False)
        self.assertEqual(output, {})

        # Let's add some device
        dev1 = Device(testbed = tb, name='PE1', os='nxos')
        dev2 = Device(testbed = tb, name='P1', os='nxos')
        dev3 = Device(testbed = tb, name='core', os='nxos')

        output = tb.build_config(apply = False)

        expected_output = {}

        self.assertEqual(output, expected_output)

        # Create a fake Interface object
        interface1 = BaseInterface(device = dev1, name='Ethernet4/1',
                               description='unittest',
                               shutdown=False,speed='auto',bandwidth=1000,
                               delay=100,duplex = 'auto',
                               cdp=True, ipv4 = '1.1.1.1/24',
                               ipv6 = '1::1/128')

        interface2 = BaseInterface(device = dev1, name='Ethernet4/2',
                               description='unittest',
                               shutdown=False,speed='auto',bandwidth=1000,
                               delay=100,duplex = 'auto',
                               cdp=True, ipv4 = '1.1.1.2/24',
                               ipv6 = '1::2/128')

        interface3 = BaseInterface(device = dev2, name='Ethernet4/3',
                               description='unittest',
                               shutdown=False,speed='auto',bandwidth=1000,
                               delay=100,duplex = 'auto',
                               cdp=True, ipv4 = '1.1.1.3/24',
                               ipv6 = '1::3/128')

        interface4 = BaseInterface(device = dev3, name='Ethernet4/4',
                               description='unittest',
                               shutdown=False,speed='auto',bandwidth=1000,
                               delay=100,duplex = 'auto',
                               cdp=True, ipv4 = '1.1.1.4/24',
                               ipv6 = '1::4/128')

        interface5 = BaseInterface(device = dev3, name='Ethernet4/5',
                               description='unittest',
                               shutdown=False,speed='auto',bandwidth=1000,
                               delay=100,duplex = 'auto',
                               cdp=True, ipv4 = '1.1.1.5/24',
                               ipv6 = '1::5/128')

        link1 = Link(testbed=tb ,name='r1-r2-1')
        link2 = Link(testbed=tb ,name='r1-r2-2')

        link1.connect_interface(interface1)
        link1.connect_interface(interface3)

        link2.connect_interface(interface2)
        link2.connect_interface(interface4)
        expected_output = {
            'P1':
            'interface Ethernet4/3\n'
            ' cdp enable\n'
            ' bandwidth 1000\n'
            ' delay 100\n'
            ' description unittest\n'
            ' no shutdown\n'
            ' ip address 1.1.1.3 255.255.255.0\n'
            ' ipv6 address 1::3/128\n'
            ' duplex auto\n'
            ' speed auto\n'
            ' exit',

            'PE1':
            'interface Ethernet4/1\n'
            ' cdp enable\n'
            ' bandwidth 1000\n'
            ' delay 100\n'
            ' description unittest\n'
            ' no shutdown\n'
            ' ip address 1.1.1.1 255.255.255.0\n'
            ' ipv6 address 1::1/128\n'
            ' duplex auto\n'
            ' speed auto\n'
            ' exit\n'
            'interface Ethernet4/2\n'
            ' cdp enable\n'
            ' bandwidth 1000\n'
            ' delay 100\n'
            ' description unittest\n'
            ' no shutdown\n'
            ' ip address 1.1.1.2 255.255.255.0\n'
            ' ipv6 address 1::2/128\n'
            ' duplex auto\n'
            ' speed auto\n'
            ' exit',

            'core':
            'interface Ethernet4/4\n'
            ' cdp enable\n'
            ' bandwidth 1000\n'
            ' delay 100\n'
            ' description unittest\n'
            ' no shutdown\n'
            ' ip address 1.1.1.4 255.255.255.0\n'
            ' ipv6 address 1::4/128\n'
            ' duplex auto\n'
            ' speed auto\n'
            ' exit\n'
            'interface Ethernet4/5\n'
            ' cdp enable\n'
            ' bandwidth 1000\n'
            ' delay 100\n'
            ' description unittest\n'
            ' no shutdown\n'
            ' ip address 1.1.1.5 255.255.255.0\n'
            ' ipv6 address 1::5/128\n'
            ' duplex auto\n'
            ' speed auto\n'
            ' exit',

         }
        output = tb.build_config(apply = False)

        self.maxDiff = None
        self.assertMultiLineDictEqual(output, expected_output)
        #mock
        dev1.cli = Mock()
        dev1.configure = Mock()
        dev2.cli = Mock()
        dev2.configure = Mock()
        dev3.cli = Mock()
        dev3.configure = Mock()
        output = tb.build_config(apply = True)

    def test_build_unconfig(self):
        # Let's say there is no device
        tb = Genie.testbed = Testbed()

        output = tb.build_unconfig(apply = False)
        self.assertEqual(output, {})

        # Let's add some device
        dev1 = Device(testbed = tb, name='PE1', os='nxos')
        dev2 = Device(testbed = tb, name='P1', os='nxos')
        dev3 = Device(testbed = tb, name='core', os='nxos')

        output = tb.build_unconfig(apply = False)
        expected_output = {}

        self.assertEqual(output, expected_output)

        # Create a fake Interface object
        interface1 = BaseInterface(device = dev1, name='Ethernet4/1')
        interface2 = BaseInterface(device = dev1, name='Ethernet4/2')
        interface3 = BaseInterface(device = dev2, name='Ethernet4/3')
        interface4 = BaseInterface(device = dev3, name='Ethernet4/4')
        interface5 = BaseInterface(device = dev3, name='Ethernet4/5')

        link1 = Link(testbed=tb ,name='r1-r2-1')
        link2 = Link(testbed=tb ,name='r1-r2-2')

        link1.connect_interface(interface1)
        link1.connect_interface(interface3)

        link2.connect_interface(interface2)
        link2.connect_interface(interface4)

        output = tb.build_unconfig(apply = False)

        expected_output = {
            'PE1':
            'default interface Ethernet4/1\n'
            'default interface Ethernet4/2',

            'P1':
            'default interface Ethernet4/3',

            'core':
            'default interface Ethernet4/4\n'
            'default interface Ethernet4/5',
        }
        self.assertMultiLineDictEqual(output, expected_output)

        #mock
        dev1.cli = Mock()
        dev1.configure = Mock()
        dev2.cli = Mock()
        dev2.configure = Mock()
        dev3.cli = Mock()
        dev3.configure = Mock()
        output = tb.build_config(apply = True)

    def test_basic_config(self):
        # Let's configure those interfaces
        self.interface1.description = 'unittest'
        self.interface1.shutdown = False

        self.interface2.speed = 'auto'
        self.interface2.duplex = 'auto'
        self.interface2.bandwidth = 1000
        self.interface2.delay = 100

        self.interface3.mtu = 1500
        self.interface3.cdp = True
        self.interface3.ipv4 = '1.1.1.1/24'

        self.interface4.ipv6 = '1::1/128'
        self.interface4.load_interval = 300
        self.interface4.load_interval_counter = 1

        self.interface5.flowcontrol_receive = 'on'

        output = self.tb.build_config(apply = False)
        # The output is in a dict, and the ordered is of course random.
        expected_output = {
            'PE1':
            'interface Ethernet4/1\n'
            ' description unittest\n'
            ' no shutdown\n'
            ' exit\n'
            'interface Ethernet4/2\n'
            ' bandwidth 1000\n'
            ' delay 100\n'
            ' duplex auto\n'
            ' speed auto\n'
            ' exit',

            'P1':
            'interface Ethernet4/3\n'
            ' cdp enable\n'
            ' mtu 1500\n'
            ' ip address 1.1.1.1 255.255.255.0\n'
            ' exit',

            'core':
            'interface Ethernet4/4\n'
            ' ipv6 address 1::1/128\n'
            ' load-interval 300\n'
            ' load-interval counter 1\n'
            ' exit\n'
            'interface Ethernet4/5\n'
            ' flowcontrol receive on\n'
            ' exit',
        }

        self.assertMultiLineDictEqual(output, expected_output)

    def test_basic_unconfig(self):
        # Let's configure those interfaces
        self.interface1.description = 'unittest'
        self.interface1.shutdown = False
        self.interface2.speed = 'auto'
        self.interface2.duplex = 'auto'
        self.interface2.bandwidth = 1000
        self.interface2.delay = 100
        self.interface3.mtu = 1500
        self.interface3.cdp = True
        self.interface3.ipv4 = '1.1.1.1/24'
        self.interface4.ipv6 = '1::1/128'
        self.interface4.load_interval = 300
        self.interface4.load_interval_counter = 1
        self.interface5.flowcontrol_receive = 'on'


        output = self.tb.build_unconfig(apply = False)
        # The output is in a dict, and the ordered is of course random.
        expected_output = {
            'PE1':
            'default interface Ethernet4/1\n'
            'default interface Ethernet4/2',

            'P1':
            'default interface Ethernet4/3',

            'core':
            'default interface Ethernet4/4\n'
            'default interface Ethernet4/5',
        }
        self.assertMultiLineDictEqual(output, expected_output)


class TestPyatsTestbedClass(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global Interface, Testbed, Device, Link, AttrDict, TopologyDict

        from genie.conf.base.testbed import Testbed
        from genie.conf.base.interface import BaseInterface as Interface
        from genie.conf.base.link import Link
        from genie.conf.base.device import Device
        from pyats.topology.bases import TopologyDict
        from pyats.datastructures import AttrDict

    def setUp(self):
        # standard test testbed with two devices and 1 link
        self.testbed = Testbed(name = 'testTestbed')

        # create the devices and add to testbed
        deviceA = Device(name = 'deviceA', type = '')
        deviceB = Device(name = 'deviceB', type = '')

        self.testbed.add_device(deviceA)
        self.testbed.add_device(deviceB)

        link = Link(name = 'link-1')

        # add interfaces and link connection to device
        deviceA.add_interface(Interface(name = 'eth1/1',
                                        link = link,
                                        type = ''))
        deviceB.add_interface(Interface(name = 'eth2/1',
                                        link = link,
                                        type = ''))

    def tearDown(self):
        gc.collect()

    def test_device_must_have_unique_name(self):
        testbed = Testbed(name = 'testTestbed')

        deviceA = Device(name = 'device', type = '')
        deviceB = Device(name = 'device', type = '')

        testbed.add_device(deviceA)
        from pyats.topology import exceptions

        with self.assertRaises(exceptions.DuplicateDeviceError):
            testbed.add_device(deviceB)

    def test_remove_error(self):
        from pyats.topology import exceptions

        with self.assertRaises(exceptions.UnknownDeviceError):
            self.testbed.remove_device('woot')

        device = Device(name = 'newdevice', type = '')

        with self.assertRaises(exceptions.UnknownDeviceError):
            self.testbed.remove_device(device)

    def test_create_empty(self):
        testbed = Testbed(name = 'emptyTb')

        self.assertEqual(testbed.name, 'emptyTb')
        # type(testbed) = <class 'genie_libs.conf.testbed.Testbed'>
        # Testbed = <class 'genie.conf.base.testbed.Testbed'>
        self.assertIsNot(type(testbed), Testbed)
        self.assertFalse(testbed.devices)
        self.assertTrue(hasattr(testbed, 'alias'))
        self.assertTrue(hasattr(testbed, 'tacacs'))
        self.assertTrue(hasattr(testbed, 'passwords'))
        self.assertTrue(hasattr(testbed, 'clean'))
        self.assertTrue(hasattr(testbed, 'custom'))
        self.assertTrue(hasattr(testbed, 'servers'))
        self.assertTrue(hasattr(testbed, 'testbed_file'))

        self.assertIs(type(testbed.tacacs), AttrDict)
        self.assertIs(type(testbed.servers), AttrDict)
        self.assertIs(type(testbed.passwords), AttrDict)
        self.assertIs(type(testbed.clean), AttrDict)
        self.assertIs(type(testbed.devices), TopologyDict)
        self.assertIs(testbed.testbed_file, None)
        self.assertEqual(testbed.alias, testbed.name)
        self.assertFalse(testbed.tacacs)
        self.assertFalse(testbed.servers)
        self.assertFalse(testbed.passwords)
        self.assertFalse(testbed.clean)
        self.assertFalse(testbed.custom)

    def test_create_with_devices(self):
        deviceA = Device(name = 'deviceA', type = '')
        deviceB = Device(name = 'deviceB', type = '')

        testbed = Testbed(name = 'testTestbed', devices = [deviceA, deviceB])
        self.assertEqual(len(testbed.devices), 2)
        self.assertIs(deviceA.testbed, testbed)
        self.assertIs(deviceB.testbed, testbed)
        self.assertIn(deviceA, testbed)
        self.assertIn(deviceB, testbed)

    def test_alias(self):
        testbed = Testbed(name = 'emptyTb', alias = 'lalala')
        self.assertEqual(testbed.alias, 'lalala')
        self.assertEqual(testbed.name, 'emptyTb')

    def test_create_with_kwargs(self):
        testbed = Testbed(name = 'emptyTb', awesome = True)
        self.assertEqual(testbed.awesome, True)

    # Not valid since genie testbed can be initialized without a name
    # def test_create_must_have_name(self):
    #     with self.assertRaises(TypeError):
    #         Testbed()

    def test_servers_field(self):
        servers = {
            'a': dict(a=1,b=2),
            'b': dict(x=1,y=2),
        }

        testbed = Testbed(name = 'servers', servers = servers)
        self.assertEqual(testbed.servers.a.a, 1)
        self.assertEqual(testbed.servers.a.b, 2)
        self.assertEqual(testbed.servers.b.x, 1)
        self.assertEqual(testbed.servers.b.y, 2)

    def test_devices(self):
        self.assertEqual(len(self.testbed.devices), 2)

        self.assertIn('deviceA', self.testbed.devices)
        self.assertIn('deviceB', self.testbed.devices)

        for device in self.testbed.devices.values():
            # AssertionError: <class 'genie_libs.conf.device.Device'>
            # is not <class 'genie.conf.base.device.Device'>
            self.assertIsNot(type(device), Device)

    def test_get_link(self):
        links = self.testbed.links
        self.assertEqual(len(links), 1)
        self.assertIs(type(links), set)
        self.assertEqual(list(links)[0].name, 'link-1')
        self.assertIs(type(list(links)[0]), Link)

    def test_add_device(self):
        added_device = Device(name = 'iGotAdded', type = '')
        self.testbed.add_device(added_device)

        self.assertIn('iGotAdded', self.testbed.devices)
        self.assertIn(added_device, list(self.testbed.devices.values()))
        self.assertIs(added_device.testbed, self.testbed)
        self.assertEqual(len(self.testbed.devices), 3)

    def test_remove_device(self):
        deviceA = self.testbed.devices['deviceA']
        deviceB = self.testbed.devices['deviceB']
        self.testbed.remove_device(deviceA)

        self.assertEqual(deviceA.testbed, None)
        self.assertEqual(len(self.testbed.devices), 1)

        self.testbed.remove_device('deviceB')
        self.assertEqual(deviceB.testbed, None)
        self.assertEqual(len(self.testbed.devices), 0)

    def test_garbage_collection(self):
        testbed = Testbed(name = 'testTestbed')

        deviceA = Device(name = 'deviceA', type = '')
        deviceB = Device(name = 'deviceB', type = '')

        testbed.add_device(deviceA)
        testbed.add_device(deviceB)

        link = Link(name = 'link-1')

        # add interfaces and link connection to device
        deviceA.add_interface(Interface(name = 'eth1/1',
                                        link = link,
                                        type = ''))
        deviceB.add_interface(Interface(name = 'eth2/1',
                                        link = link,
                                        type = ''))

        # cleanup locals
        del link
        del deviceA

        link = testbed.devices['deviceB'].interfaces['eth2/1'].link
        self.assertEqual(len(link.interfaces), 2)

        testbed.remove_device('deviceA')
        gc.collect()
        # garbage collection should've propagated all the way
        intf = testbed.devices['deviceB'].interfaces['eth2/1']
        self.assertEqual(link.interfaces, [intf,])

        testbed.remove_device(deviceB)

        self.assertFalse(testbed.devices)
        self.assertIs(deviceB.testbed, None)
        self.assertFalse(testbed.links)

    def test_in_operator(self):
        deviceA = self.testbed.devices['deviceA']
        deviceB = self.testbed.devices['deviceB']

        self.assertIn(deviceA, self.testbed)
        self.assertIn(deviceB, self.testbed)
        self.assertIn('deviceA', self.testbed)
        self.assertIn('deviceA', self.testbed)
        self.assertNotIn(Device(name = 'deviceC', type = ''), self.testbed)

    def test_iter(self):
        devices = []
        for d in self.testbed:
            devices.append(d)

        self.assertEqual(devices, list(self.testbed.devices.values()))

    def test_links_error(self):
        deviceC = Device(name = 'deviceC', type = '', testbed = self.testbed)

        link = Link(name = 'link-1')

        # add interfaces and link connection to device
        deviceC.add_interface(Interface(name = 'eth1/1',
                                        link = link,
                                        type = ''))
        deviceC.add_interface(Interface(name = 'eth2/1',
                                        link = link,
                                        type = ''))

        from pyats.topology.exceptions import DuplicateLinkError
        with self.assertRaises(DuplicateLinkError):
            self.testbed.links

    def test_device_aliases(self):
        testbed = Testbed(name = 'testTestbed')

        deviceA = Device(name = 'deviceA', alias = 'aliasA')
        deviceB = Device(name = 'deviceB', alias = 'aliasB')

        testbed.add_device(deviceA)
        testbed.add_device(deviceB)

        self.assertIs(testbed.devices['aliasA'], testbed.devices['deviceA'])
        self.assertIs(testbed.devices['aliasB'], testbed.devices['deviceB'])

        self.assertEqual(testbed.devices.aliases, set(['aliasA', 'aliasB']))
        self.assertTrue(testbed.devices.is_alias('aliasA'))
        self.assertTrue(testbed.devices.is_alias('aliasB'))
        self.assertFalse(testbed.devices.is_alias('deviceA'))
        self.assertFalse(testbed.devices.is_alias('deviceB'))

    def test_device_aliases_in_operator(self):
        testbed = Testbed(name = 'testTestbed')

        deviceA = Device(name = 'deviceA', alias = 'aliasA')
        deviceB = Device(name = 'deviceB', alias = 'aliasB')

        testbed.add_device(deviceA)
        testbed.add_device(deviceB)

        self.assertIn('aliasA', testbed)
        self.assertIn('aliasB', testbed)


class TestTestbedSqueeze(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global loader
        from genie.conf.base import loader


    def setUp(self):
        # standard test testbed with two devices and 1 link
        self.testbed = loader.load(
            os.path.join(
                os.path.dirname(__file__), 'yamls', 'squeeze_testbed.yaml'))

    def tearDown(self):
        gc.collect()


    def assert_interfaces_equal(self, expected_interface_names, device_name):
        """ Helper function to compare expected with actual interfaces. """
        self.assertEqual(expected_interface_names,
            sorted(self.testbed.devices[device_name].interfaces.keys()))


    def test_squeeze_topology1_extend(self):
        """ Ensure links are expanded to include their connected devices.
        Also ensure that any interface or device not selected is removed.
        """
        tb = self.testbed
        tb.squeeze('lshared')
        links = sorted([link.name for link in tb.links])
        self.assertEqual(['r3', 'r4', 'r8'], sorted(tb.devices.keys()))
        self.assertEqual(['lshared'], links)
        self.assert_interfaces_equal(['GigabitEthernet0/2'], 'r3')
        self.assert_interfaces_equal(['GigabitEthernet0/6'], 'r4')
        self.assert_interfaces_equal(['GigabitEthernet0/3'], 'r8')


    def test_squeeze_topology1_no_extend(self):
        """ Ensure links are not expanded to include their connected devices
        on user request.
        Also ensure that any interface or device not selected is removed.
        """
        tb = self.testbed
        tb.squeeze('lshared', extend_devices_from_links=False)
        links = sorted([link.name for link in tb.links])
        self.assertEqual([], sorted(tb.devices.keys()))
        self.assertEqual([], links)


    def test_squeeze_topology2(self):
        """ Ensure links are expanded to include their connected devices.
        Add additional devices and ensure they are kept in the topology.
        These additional devices are not connected to the named link.
        """
        tb = self.testbed
        tb.squeeze('r1', 'r2', 'lshared')
        links = sorted([link.name for link in tb.links])
        self.assertEqual(['r1', 'r2', 'r3', 'r4', 'r8'],
            sorted(tb.devices.keys()))
        self.assertEqual(['lshared'], links)
        self.assert_interfaces_equal([], 'r1')
        self.assert_interfaces_equal([], 'r2')
        self.assert_interfaces_equal(['GigabitEthernet0/2'], 'r3')
        self.assert_interfaces_equal(['GigabitEthernet0/6'], 'r4')
        self.assert_interfaces_equal(['GigabitEthernet0/3'], 'r8')


    def test_squeeze_topology2_no_extend(self):
        """ Ensure links are not expanded to include their connected devices.
        Add additional devices and ensure they are kept in the topology.
        These additional devices are not connected to the named link.
        """
        tb = self.testbed
        tb.squeeze('r1', 'r2', 'lshared', extend_devices_from_links=False)
        links = sorted([link.name for link in tb.links])
        self.assertEqual(['r1', 'r2'],
            sorted(tb.devices.keys()))
        self.assertEqual([], links)
        self.assert_interfaces_equal([], 'r1')
        self.assert_interfaces_equal([], 'r2')


    def test_squeeze_topology3(self):
        """ Specify parallel links between two devices.  """
        tb = self.testbed
        tb.squeeze('l1_2', 'l2_4_1', 'l2_4_2')
        links = sorted([link.name for link in tb.links])
        self.assertEqual(['r1', 'r2', 'r4'], sorted(tb.devices.keys()))
        self.assertEqual(['l1_2', 'l2_4_1', 'l2_4_2'], links)
        self.assert_interfaces_equal(['GigabitEthernet0/0'], 'r1')
        self.assert_interfaces_equal(
            ['GigabitEthernet0/0', 'GigabitEthernet0/1', 'GigabitEthernet0/2'],
            'r2')
        self.assert_interfaces_equal(
            ['GigabitEthernet0/0', 'GigabitEthernet0/1'], 'r4')


    def test_squeeze_topology4(self):
        """ Specify only devices.  """
        tb = self.testbed
        tb.squeeze('r7', 'r9', 'r6')
        links = sorted([link.name for link in tb.links])
        self.assertEqual(['r6', 'r7', 'r9'], sorted(tb.devices.keys()))
        self.assertEqual([], links)
        self.assert_interfaces_equal([], 'r6')
        self.assert_interfaces_equal([], 'r7')
        self.assert_interfaces_equal([], 'r9')


    def test_squeeze_topology5(self):
        """ Specify an unknown device or link.  """
        tb = self.testbed
        tb.squeeze('lunknown')
        links = sorted([link.name for link in tb.links])
        self.assertEqual([], sorted(tb.devices.keys()))
        self.assertEqual([], links)



    def common_asserts_topo6_7(self, tb):
        links = sorted([link.name for link in tb.links])
        self.assertEqual(['r1', 'r3', 'r4', 'r6', 'r8', 'r9'],
            sorted(tb.devices.keys()))
        self.assertEqual(['l1_3', 'l3_4', 'l4_6_2', 'l6_8_1', 'l8_9'], links)
        self.assert_interfaces_equal(['GigabitEthernet0/1'], 'r1')
        self.assert_interfaces_equal(
            ['GigabitEthernet0/0', 'GigabitEthernet0/1'], 'r3')
        self.assert_interfaces_equal(
            ['GigabitEthernet0/2', 'GigabitEthernet0/5'], 'r4')
        self.assert_interfaces_equal(
            ['GigabitEthernet0/1', 'GigabitEthernet0/4'], 'r6')
        self.assert_interfaces_equal(
            ['GigabitEthernet0/0', 'GigabitEthernet0/2'], 'r8')
        self.assert_interfaces_equal(['GigabitEthernet0/1'], 'r9')

    def test_squeeze_topology6(self):
        """ Specify wanted devices and interconnecting links.
        """
        tb = self.testbed
        tb.squeeze('r1', 'r3', 'r4', 'r6', 'r8', 'r9',
            'l1_3', 'l3_4', 'l4_6_2', 'l6_8_1', 'l8_9',)
        self.common_asserts_topo6_7(tb)


    def test_squeeze_topology7(self):
        """ Same test as test_squeeze_topology6, but without explicitly
        specified devices.
        """
        tb = self.testbed
        tb.squeeze('l1_3', 'l3_4', 'l4_6_2', 'l6_8_1', 'l8_9',)
        self.common_asserts_topo6_7(tb)


    def test_squeeze_topology8(self):
        """ Ensure device and link aliases are respected.
        Also ensure that interfaces with no links are pruned. """
        tb = self.testbed
        tb.squeeze('r1_alias', 'r5_alias', 'l1_2_alias', 'l4_6_1_alias')
        links = sorted([link.name for link in tb.links])
        self.assertEqual(['r1', 'r2', 'r4', 'r5', 'r6'],
            sorted(tb.devices.keys()))
        self.assertEqual(['l1_2', 'l4_6_1'], links)
        self.assert_interfaces_equal(['GigabitEthernet0/0'], 'r1')
        self.assert_interfaces_equal(['GigabitEthernet0/0'], 'r2')
        self.assert_interfaces_equal(['GigabitEthernet0/4'], 'r4')
        self.assert_interfaces_equal([], 'r5')
        self.assert_interfaces_equal(['GigabitEthernet0/0'], 'r6')


    def test_squeeze_topology8_no_extend(self):
        """ Ensure device and link aliases are respected.
        Also ensure that interfaces with no links are pruned. """
        tb = self.testbed
        tb.squeeze('r1_alias', 'r5_alias', 'l1_2_alias', 'l4_6_1_alias',
            extend_devices_from_links=False)
        links = sorted([link.name for link in tb.links])
        self.assertEqual(['r1', 'r5'],
            sorted(tb.devices.keys()))
        self.assertEqual([], links)
        self.assert_interfaces_equal([], 'r1')
        self.assert_interfaces_equal([], 'r5')


    def test_squeeze_topology9(self):
        """ Ensure device and link aliases are respected.
        Also ensure that interfaces with no links are pruned. """
        tb = self.testbed
        tb.squeeze('r3', 'r4', 'r6', 'l1_2', 'l2_4_1', 'l4_6_1', 'lshared')
        links = sorted([link.name for link in tb.links])
        self.assertEqual(['r1', 'r2', 'r3', 'r4', 'r6', 'r8'],
            sorted(tb.devices.keys()))
        self.assertEqual(['l1_2', 'l2_4_1', 'l4_6_1', 'lshared'], links)
        self.assert_interfaces_equal(['GigabitEthernet0/0'], 'r1')
        self.assert_interfaces_equal(
            ['GigabitEthernet0/0', 'GigabitEthernet0/1'], 'r2')
        self.assert_interfaces_equal(['GigabitEthernet0/2'], 'r3')
        self.assert_interfaces_equal(
            ['GigabitEthernet0/0', 'GigabitEthernet0/4', 'GigabitEthernet0/6'],
            'r4')
        self.assert_interfaces_equal(['GigabitEthernet0/0'], 'r6')
        self.assert_interfaces_equal(['GigabitEthernet0/3'], 'r8')


    def test_squeeze_topology9_no_extend(self):
        """ Ensure device and link aliases are respected.
        Also ensure that interfaces with no links are pruned. """
        tb = self.testbed
        tb.squeeze('r3', 'r4', 'r6', 'l1_2', 'l2_4_1', 'l4_6_1', 'lshared',
            extend_devices_from_links=False)
        links = sorted([link.name for link in tb.links])
        self.assertEqual(['r3', 'r4', 'r6'],
            sorted(tb.devices.keys()))
        self.assertEqual(['l4_6_1', 'lshared'], links)
        self.assert_interfaces_equal(['GigabitEthernet0/2'], 'r3')
        self.assert_interfaces_equal(
            ['GigabitEthernet0/4', 'GigabitEthernet0/6'], 'r4')
        self.assert_interfaces_equal(['GigabitEthernet0/0'], 'r6')

if __name__ == '__main__':
    unittest.main()
