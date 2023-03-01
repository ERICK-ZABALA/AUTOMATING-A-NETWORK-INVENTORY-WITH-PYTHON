#!/usr/bin/env python

# Import unittest module
import unittest

from pyats.datastructures import WeakList
from pyats.topology.bases import TopologyDict
from pyats.datastructures.logic import And, Not, Or
from pyats.topology.exceptions import DuplicateInterfaceError
from pyats.topology.exceptions import UnknownInterfaceError
from pyats.topology.exceptions import DuplicateInterfaceConnectionError, LinkError

# And import what's needed
from genie.conf.base.device import Device
from genie.conf.base.testbed import Testbed
from genie.conf.base.exceptions import CountError
from genie.conf.base.interface import BaseInterface
from genie.conf.base.link import Link, LoopbackLink

class test_link(unittest.TestCase):

    def test_init(self):
        '''Test the creation of a link itself and make sure it is assigned'''
        tb = Testbed()
        # Let's try with an object without argument
        link = Link(testbed = tb, name='r1-r2-1')

        # Make sure the attributes are set to their default values
        self.assertEqual(link.name, 'r1-r2-1')
        self.assertEqual(link.aliases, [])
        self.assertEqual(link.interfaces, WeakList())
        # Create a device
        dev = Device(testbed = tb, name='myDevice', os='nxos')
        # Let's create a interface
        intf = BaseInterface(device = dev, name='Ethernet4/47')
        interfaces = [intf]

        # Let's try with an object without argument
        link = Link(testbed = tb, name='r1-r2-1',
                    aliases=['link1'], interfaces=interfaces)

        # Make sure the attributes are set to the value we decided
        self.assertEqual(link.name, 'r1-r2-1')
        self.assertEqual(link.aliases, ['link1'])
        self.assertIn(intf, link.interfaces)

    def test_connect_interface(self):
        '''Connect an interface to this link'''
        tb = Testbed()
        # Create a link
        link = Link(testbed = tb, name='r1-r2-1')
        self.assertEqual(link.interfaces, WeakList())
        # Create a device
        dev = Device(testbed = tb, name='myDevice', os='nxos')
        # Let's create a interface
        intf = BaseInterface(device = dev, name='Ethernet4/47')

        # Connect this interface to this link
        link.connect_interface(intf)

        self.assertIn(intf, link.interfaces)
        # Make sure that interface now has link too set up
        self.assertIn(link, intf.links)

    def test_connect_interface_already_existing(self):
        '''Connect an interface to this link that already exist'''
        tb =Testbed()
        # Create a link
        link = Link(testbed = tb, name='r1-r2-1')
        self.assertEqual(link.interfaces, WeakList())

        # Create a device
        dev = Device(testbed = tb, name='myDevice', os='nxos')
        # Let's create a interface
        intf = BaseInterface(device = dev, name='Ethernet4/47')

        # Connect this interface to this link
        link.connect_interface(intf)

        # Connect this interface to this link
        with self.assertRaises(DuplicateInterfaceConnectionError):
            link.connect_interface(intf)

        self.assertIn(intf, link.interfaces)
        # Make sure that interface now has link too set up
        self.assertIn(link, intf.links)

    def test_disconnect_interface(self):
        '''Remove an interface from a link'''
        tb = Testbed()
        # Create a link
        link = Link(testbed = tb, name='r1-r2-1')
        self.assertEqual(link.interfaces, WeakList())

        # Create a device
        dev = Device(testbed = tb, name='myDevice', os='nxos')
        # Let's create a interface
        intf = BaseInterface(device = dev, name='Ethernet4/47')

        # Connect this interface to this link
        link.connect_interface(intf)

        self.assertIn(intf, link.interfaces)
        # Make sure that interface now has link too set up
        self.assertIn(link, intf.links)

        # Disconnect the interface from the link
        link.disconnect_interface(intf)

        self.assertNotIn(intf, link.interfaces)
        self.assertNotIn(link, intf.links)

    def test_contains(self):
        '''Make sure __contains__ verify the interface is in the link'''
        tb = Testbed()

        link = Link(testbed = tb, name='r1-r2-1')
        self.assertEqual(link.interfaces, WeakList())

        # Create a device
        dev = Device(testbed = tb, name='myDevice', os='nxos')
        # Let's create a interface
        intf = BaseInterface(device = dev, name='Ethernet4/47')
        self.assertFalse(intf in link.interfaces)

        # Connect this interface to this link
        link.connect_interface(intf)
        self.assertTrue(intf in link.interfaces)

    def test_iter(self):
        '''Make sure __iter__ iter over the interfaces'''

        tb = Testbed()
        link = Link(testbed = tb, name='r1-r2-1')
        self.assertEqual(link.interfaces, WeakList())

        # Create a device
        dev = Device(testbed = tb, name='myDevice', os='nxos')
        # Let's create a interface
        intf = BaseInterface(device = dev, name='Ethernet4/47')
        self.assertNotIn(intf, link.interfaces)

        # Connect this interface to this link
        link.connect_interface(intf)
        self.assertIn(intf, link.interfaces)

    def test_devices(self):
        '''Helper function'''
        tb = Testbed()
        link = Link(testbed=tb ,name='r1-r2-1')
        self.assertEqual(link.interfaces, WeakList())

        # Create a device
        dev = Device(testbed = tb, name='myDevice', os='nxos')

        # Let's create a interface

        intf = BaseInterface(device = dev, name='Ethernet4/47')

        # Connect this interface to this link
        link.connect_interface(intf)

        # Interface is not associated to any device, so associated device should
        # be empty
        self.assertEqual(link.devices, tuple([dev]))
        dev.remove_interface(intf)
        self.assertEqual(link.devices, tuple([None]))

    def test_find_interfaces(self):

        tb = Testbed()
        # Let's say there is no Interface
        link = Link(testbed = tb, name='r1-r2-1')

        output = link.find_interfaces()

        self.assertEqual(output, [])

        # Create a device
        dev = Device(testbed = tb, name='myDevice', os='nxos')
        #Add some interface
        intf1 = BaseInterface(device = dev, name='Ethernet4/47')
        intf2 = BaseInterface(device = dev, name='Ethernet4/48')
        intf3 = BaseInterface(device = dev, name='Ethernet4/49')
        intf4 = BaseInterface(device = dev, name='Ethernet4/50')
        intf5 = BaseInterface(device=dev, name='Ethernet4/51', obj_state='inactive')

        link.connect_interface(intf1)
        link.connect_interface(intf2)
        link.connect_interface(intf3)
        link.connect_interface(intf4)
        link.connect_interface(intf5)

        output = link.find_interfaces()

        # Order might be different
        self.assertEqual(set(output), set([intf1, intf2, intf3, intf4]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in \
                                                 [intf1, intf2, intf3, intf4]]))

        # Let's filter
        # Return many
        output = link.find_interfaces(name=Or('Ethernet4/47', 'Ethernet4/48'))

        # Order might be different
        self.assertEqual(set(output), set([intf1, intf2]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [intf1, intf2]]))

        # count = 1
        output = link.find_interfaces(name=Or('Ethernet4/47', 'Ethernet4/48'),
                                      count=1)

        self.assertEqual(len(output), 1)

        # Negative
        output = link.find_interfaces(name=Not('Ethernet4/47'))

        # Order might be different
        self.assertEqual(set(output), set([intf2, intf3, intf4]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [intf2, intf3, intf4]]))

        # Verify if request 3, and only 2 is returned we get an exception
        with self.assertRaises(CountError):
            output = link.find_interfaces(name=Or('Ethernet4/47',
                                                  'Ethernet4/48'),
                                          count=5)

        # Let's verify the state now
        output = link.find_interfaces(obj_state=Or('inactive'))

        # Order might be different
        self.assertEqual(set(output), set([intf5]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [intf5]]))

        # Make sure it works if it is a callable
        def alwaysTrue(*args, **kwargs):
            return True
        def alwaysFalse(*args, **kwargs):
            return False

        def OnlyTrueForEthernet47(obj):
            if obj.name == 'Ethernet4/47':
                return True
            else:
                return False

        output = link.find_interfaces(obj_state=alwaysTrue)

        self.assertEqual(set(output), set([intf1, intf2, intf3, intf4, intf5]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [intf1, intf2, intf3,\
                                                        intf4, intf5]]))

        output = link.find_interfaces(obj_state=alwaysFalse)

        self.assertEqual(set(output), set([]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in []]))

        output = link.find_interfaces(callable_=OnlyTrueForEthernet47)

        self.assertEqual(set(output), set([intf1]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [intf1]]))

    def test_find_iterable_interfaces(self):
        '''Can you find interfaces?'''
        tb = Testbed()
        # Let's say there is no Interface
        dev = Device(testbed = tb, name='myDevice', os='nxos')
        link = Link(testbed=tb, name='r1-r2-1')

        output = link.find_interfaces()

        self.assertEqual(output, [])

        # Add some interface to that device!
        intf1 = BaseInterface(device = dev, name='Ethernet4/47')
        intf2 = BaseInterface(device = dev, name='Ethernet4/48')
        intf3 = BaseInterface(device = dev, name='Ethernet4/49')
        intf4 = BaseInterface(device = dev, name='Ethernet4/50')
        intf5 = BaseInterface(device=dev, name='Ethernet4/51', obj_state='inactive')

        link.connect_interface(intf1)
        link.connect_interface(intf2)
        link.connect_interface(intf3)
        link.connect_interface(intf4)
        link.connect_interface(intf5)

        output = link.find_interfaces(iterable=[intf1, intf2, intf3, intf5])

        # Order might be different
        self.assertEqual(set(output), set([intf1, intf2, intf3]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in \
                                                 [intf1, intf2, intf3]]))

        # Let's filter
        # Return many
        output = link.find_interfaces(iterable=[intf1, intf2, intf3],
                                     name=Or('Ethernet4/47', 'Ethernet4/48'))

        # Order might be different
        self.assertEqual(set(output), set([intf1, intf2]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [intf1, intf2]]))

        # count = 1
        output = link.find_interfaces(iterable=[intf1, intf2, intf3],
                                     name=Or('Ethernet4/47', 'Ethernet4/48'),
                                     count=1)

        self.assertEqual(len(output), 1)

        # Negative
        output = link.find_interfaces(iterable=[intf1, intf2, intf3],
                                     name=Not('Ethernet4/47'))

        # Order might be different
        self.assertEqual(set(output), set([intf2, intf3]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [intf2, intf3]]))

        # Multi fields
        # Also test single output are also list
        output = link.find_interfaces(iterable=[intf1, intf2, intf3],
                                     name=Not('Ethernet4/47'))

        # Order might be different
        self.assertEqual(set(output), set([intf2, intf3]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [intf2, intf3]]))

        # Verify if request 4, and only 2 is returned we get an exception
        with self.assertRaises(CountError):
            output = link.find_interfaces(iterable=[intf1, intf2, intf3],
                                         name=Or('Ethernet4/47',
                                                 'Ethernet4/48'),
                                         count=5)

        # Make sure only interfaces can be given as iterable
        output = link.find_interfaces(iterable=[])
        self.assertEqual(output, [])

        self.assertEqual(len(link.find_interfaces(iterable=[link])), 0)

        # Let's verify the state now
        output = link.find_interfaces(iterable=[intf1, intf2, intf3, intf4,
                                                intf5],
                                      obj_state=Or('inactive'))

        # Order might be different
        self.assertEqual(set(output), set([intf5]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [intf5]]))

        # Make sure it works if it is a callable
        def alwaysTrue(*args, **kwargs):
            return True
        def alwaysFalse(*args, **kwargs):
            return False

        def OnlyTrueForEthernet47(obj):
            if obj.name == 'Ethernet4/47':
                return True
            else:
                return False

        output = link.find_interfaces(iterable=[intf1, intf2, intf3, intf4,
                                                intf5], obj_state=alwaysTrue)

        self.assertEqual(set(output), set([intf1, intf2, intf3, intf4, intf5]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [intf1, intf2, intf3,\
                                                        intf4, intf5]]))

        output = link.find_interfaces(iterable=[intf1, intf2, intf3, intf4,
                                                intf5], obj_state=alwaysFalse)

        self.assertEqual(set(output), set([]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in []]))

        output = link.find_interfaces(iterable=[intf1, intf2, intf3, intf4,
                                                intf5],
                                      callable_=OnlyTrueForEthernet47)

        self.assertEqual(set(output), set([intf1]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [intf1]]))


    def test_testbed_attribute(self):

        tb = Testbed()

        link = Link(testbed = tb, name='r1-r2-1')

        self.assertEqual(link.testbed, tb)


class test_looklike_link(unittest.TestCase):

    def test_init(self):
        '''Test the creation of a link itself and make sure it is assigned'''
        tb = Testbed()
        # Create a device
        dev = Device(testbed = tb, name='myDevice', os='nxos')
        # Let's try with an object without argument
        link = Link(testbed = tb, name='r1-r2-1')

        # Make sure the attributes are set to their default values
        self.assertEqual(link.name, 'r1-r2-1')
        self.assertEqual(link.aliases, [])
        self.assertEqual(link.interfaces, WeakList())

        # Let's create a interface
        intf = BaseInterface(device = dev, name='loopback1')
        interfaces = [intf]

        # Let's try with an object without argument
        link = Link(testbed = tb,name='r1-r2-1',
                    aliases=['link1','main'], interfaces=interfaces)

        # Make sure the attributes are set to the value we decided
        self.assertEqual(link.name, 'r1-r2-1')
        self.assertEqual(sorted(link.aliases), sorted(['link1','main']))
        self.assertIn(intf, link.interfaces)

        self.assertIn(link, intf.links)

        link.disconnect_interface(intf)
        self.assertNotIn(link, intf.links)


class DummyInterface(object):

        def __init__(self, name, type):
            self.link = None
            self.name = name
            self.type = type

        def _on_added_from_link (self, obj):
            pass

        def _on_removed_from_link (self, obj):
            pass


class TestPyatsLinkClass(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global Link

    def setUp(self):
        self.link = Link(name = 'testLink')
        
    def test_creation(self):
        obj = Link(name = 'testLink')

        self.assertIs(type(obj), Link)
        self.assertTrue(hasattr(obj, 'name'))
        self.assertTrue(hasattr(obj, 'alias'))
        self.assertTrue(hasattr(obj, 'interfaces'))
        self.assertFalse(obj.interfaces)
        self.assertEqual(obj.name, 'testLink')
        self.assertEqual(obj.alias, 'testLink')

    def test_creation_kwargs(self):
        obj = Link(name = 'testLink', custom_info = 'junk')
        
        self.assertIs(type(obj), Link)
        self.assertTrue(hasattr(obj, 'custom_info'))

    def test_alias(self):
        obj = Link(name = 'testLink', alias = 'woot')
   
        self.assertEqual(obj.alias, 'woot')
        self.assertEqual(obj.name, 'testLink')

    def test_creation_duplicates(self):
        self.assertIsNot(Link(name = 'testLink'), Link(name = 'testLink'))
            
    def test_creation_uniques(self):
        link1 = Link(name = 'testLink1')
        link2 = Link(name = 'testLink2')
        self.assertNotEqual(id(link1), id(link2))

    def test_creation_with_intfs(self):
        intf1 = DummyInterface('Eth1/1', 'test')
        link = Link('testLink', interfaces=[intf1])
        
        self.assertIn(intf1, link.interfaces)
        self.assertIs(intf1.link, link)
        
        intf2 = DummyInterface('Eth1/2', 'test')
        link = Link('testLink2', interfaces=[intf1, intf2])
        
        self.assertIn(intf1, link.interfaces)
        self.assertIs(intf1.link, link)
        self.assertIn(intf2, link.interfaces)
        self.assertIs(intf2.link, link)
    
    def test_connect_interface(self):
        intf = DummyInterface('Eth1/1', 'test')
        self.link.connect_interface(intf)
        
        self.assertIs(intf.link, self.link)
        self.assertIn(intf, self.link.interfaces)
        
    def test_add_list_of_intf(self):
        intf1 = DummyInterface('Eth1/1', 'test')
        intf2 = DummyInterface('Eth2/1', 'test')
        
        with self.assertRaises(TypeError):
            self.link.connect_interface([intf1, intf2])
        
    def test_disconnect_interface(self):
        intf = DummyInterface('Eth1/1', 'test')
        self.link.connect_interface(intf)
        self.link.disconnect_interface(intf)
        
        self.assertIs(intf.link, None)
        self.assertNotIn(intf, self.link.interfaces)
        self.assertFalse(self.link.interfaces)
        
    def test_remove_list_of_intf(self):
        intf1 = DummyInterface('Eth1/1', 'test')
        intf2 = DummyInterface('Eth2/1', 'test')
        
        self.link.connect_interface(intf1)
        self.link.connect_interface(intf2)

        with self.assertRaises(TypeError):
            self.link.disconnect_interface([intf1, intf2])

    def test_remove_non_existent(self):
        from pyats.topology.exceptions import LinkError

        with self.assertRaises(LinkError):
            self.link.disconnect_interface(DummyInterface('Eth1/1', 'test'))

    def test_add_duplicate_interface(self):
        intf1 = DummyInterface('Eth1/1', 'test')
        self.link.connect_interface(intf1)
        from pyats.topology.exceptions import DuplicateInterfaceConnectionError

        with self.assertRaises(DuplicateInterfaceConnectionError):
            self.link.connect_interface(intf1)

    def test_weakref(self):
        intf1 = DummyInterface('Eth1/1', 'test')
        intf2 = DummyInterface('Eth2/1', 'test')
        self.link.connect_interface(intf1)
        self.link.connect_interface(intf2)

        self.assertIs(intf1.link, self.link)
        self.assertIs(intf2.link, self.link)
        self.assertIn(intf1, self.link.interfaces)
        self.assertIn(intf2, self.link.interfaces)
        self.assertEqual(len(self.link.interfaces), 2)

        del intf1
        # force garbage collection
        import gc; gc.collect()

        self.assertEqual(len(self.link.interfaces), 1)
        self.assertEqual(self.link.interfaces, [intf2,])

    def test_in_operator(self):
        intf1 = DummyInterface('Eth1/1', 'test')
        intf2 = DummyInterface('Eth2/1', 'test')
        self.link.connect_interface(intf1)
        self.link.connect_interface(intf2)

        self.assertIn(intf1, self.link)
        self.assertIn(intf2, self.link)

    def test_iterate(self):
        intf1 = DummyInterface('Eth1/1', 'test')
        intf2 = DummyInterface('Eth2/1', 'test')
        self.link.connect_interface(intf1)
        self.link.connect_interface(intf2)

        tmp = []
        for i in self.link:
            tmp.append(i)

        self.assertEqual(tmp, self.link.interfaces)

    def test_connected_devices(self):
        intf1 = DummyInterface('Eth1/1', 'test')
        intf2 = DummyInterface('Eth2/1', 'test')
        self.link.connect_interface(intf1)
        self.link.connect_interface(intf2)

        intf1.device = device1 = object()
        intf2.device = device2 = object()

        self.assertEqual(set([device1, device2]), self.link.connected_devices)


if __name__ == '__main__':
    unittest.main()
