#!/usr/bin/env python

# Import unittest module
import unittest
from unittest.mock import Mock

from pyats.topology.credentials import Credentials
from pyats.datastructures.logic import Not, Or
from pyats.topology.exceptions import UnknownInterfaceError
from pyats.topology.exceptions import DuplicateInterfaceError
from pyats.topology.bases import TopologyDict

# And import what's needed
from genie.conf import Genie
from genie.conf.base.link import Link
from genie.conf.base.device import Device
from genie.conf.base.testbed import Testbed
from genie.conf.base.exceptions import CountError
from genie.conf.base.interface import BaseInterface
from genie.metaparser.util.exceptions import SchemaMissingKeyError


class test_device(unittest.TestCase):

    def tearDown(self):
        Genie.testbed = None

    def test_init(self):
        '''Test the creation of a device itself and make sure it is assigned'''
        tb = Genie.testbed = Testbed()
        # Let's try with an object without argument
        with self.assertWarnsRegex(UserWarning,
                                   'Device myDevice OS is unknown'):
            dev = Device(testbed = tb, name='myDevice')

        # Make sure the attributes are set to their default values
        self.assertEqual(dev.name, 'myDevice')
        self.assertEqual(dev.aliases, [])
        self.assertEqual(dev.roles, [])
        self.assertEqual(dev.type, None)
        self.assertEqual(list(dev.interfaces), [])

        # Let's create a interface
        dev.os = 'nxos'
        intf = BaseInterface(device = dev, name='Ethernet4/47')
        # Since device no winherits from pyats_device we need to respect the
        # objects types.
        interfaces = TopologyDict()
        interfaces[intf] = intf

        # Let's try with an object with argument
        dev = Device(testbed = tb, name='myDevice', aliases=['anAlias', 'more'],
                     type='myType', interfaces=interfaces, roles=['uut'])

        # Make sure the attributes are set to the right values
        self.assertEqual(dev.name, 'myDevice')
        self.assertEqual(sorted(dev.aliases), sorted(['anAlias', 'more']))
        self.assertEqual(dev.roles, ['uut'])
        self.assertEqual(dev.type, 'myType')
        self.assertEqual(dev.interfaces[intf.name], intf)
        self.assertEqual(intf.device, dev)

    def test_add_device_without_os(self):
        '''Add a device with os=None'''
        tb = Genie.testbed = Testbed(name='MyTestbed')
        dev1 = Device(testbed = tb, name='myDeviceWithoutOs1', os=None)
        dev2 = Device(name='myDeviceWithoutOs2', os=None)
        tb.add_device(dev2)

    def test_add_interface(self):
        '''Add an interface to a device'''
        tb = Genie.testbed = Testbed()
        # Create a device
        dev = Device(testbed = tb, name='myDevice', os='nxos')
        self.assertEqual(dev.interfaces, TopologyDict())

        intf = BaseInterface(device = dev, name='Ethernet4/47',
                         aliases='myint')
        self.assertEqual(intf.device, dev)

        self.assertEqual(dev.interfaces[intf.name], intf)
        # self.assertEqual(dev.interfaces_map, {'Ethernet4/47':intf})

    def test_add_interface_already_existing(self):
        '''Add again the same interface to a device'''
        tb = Genie.testbed = Testbed()
        # Create a device
        dev = Device(testbed = tb, name='myDevice', os='nxos')
        self.assertEqual(dev.interfaces, TopologyDict())
        # self.assertEqual(dev.interfaces_map, {})

        intf = BaseInterface(device = dev, name='Ethernet4/47')

        with self.assertRaises(DuplicateInterfaceError):
            dev.add_interface(intf)

    def test_remove_interface(self):
        '''Remove an interface from a device'''
        tb = Genie.testbed = Testbed()
        # Create a device
        dev = Device(testbed = tb, name='myDevice', os='nxos')
        self.assertEqual(dev.interfaces, TopologyDict())
        # self.assertEqual(dev.interfaces_map, {})

        intf = BaseInterface(device = dev, name='Ethernet4/47')
        self.assertEqual(dev.interfaces[intf.name], intf)
        # self.assertEqual(dev.interfaces_map, {'Ethernet4/47':intf})

        dev.remove_interface(intf)
        self.assertEqual(intf.device, None)

    def test_remove_interface_doesnt_exist(self):
        '''Remove an interface from a device that does not exist'''
        tb = Genie.testbed = Testbed()
        # Create a device
        dev1 = Device(testbed = tb, name='myDevice1', os='nxos')
        dev2 = Device(testbed = tb, name='myDevice2', os='nxos')
        self.assertEqual(dev1.interfaces, TopologyDict())
        # self.assertEqual(dev1.interfaces_map, {})
        self.assertEqual(dev2.interfaces, TopologyDict())
        # self.assertEqual(dev2.interfaces_map, {})

        intf = BaseInterface(device = dev1, name='Ethernet4/47')

        with self.assertRaises(UnknownInterfaceError):
            dev2.remove_interface(intf)

    def test_removed_linked_interface(self):
        '''Remove an interface that is part of a link'''
        tb = Genie.testbed = Testbed()
        # Create a device
        dev = Device(testbed = tb, name='myDevice', os='nxos')
        self.assertEqual(dev.interfaces, TopologyDict())
        # self.assertEqual(dev.interfaces_map, {})

        intf = BaseInterface(device =dev, name='Ethernet4/47')

        # Create a link object
        link = Link(testbed = tb, name='r1-r2-1')
        # Add the interface to the link
        link.connect_interface(intf)

        # self.assertIn(link, intf.links)
        self.assertEqual(link, intf.link)
        self.assertIn(intf, link.interfaces)

        self.assertEqual(dev.interfaces[intf.name], intf)
        # self.assertEqual(dev.interfaces_map, {'Ethernet4/47':intf})

        # remove interface from the device, by name this time
        dev.remove_interface(intf.name)

        # self.assertIn(link, intf.links)
        self.assertEqual(link, intf.link)
        self.assertIn(intf, link.interfaces)

    def test_add_remove_add_interface(self):
        '''Add, remove and add again the same interface'''
        tb = Genie.testbed = Testbed()
        # Create a device
        dev = Device(testbed = tb, name='myDevice', os='nxos')
        self.assertEqual(dev.interfaces, TopologyDict())
        # self.assertEqual(dev.interfaces_map, {})

        intf = BaseInterface(device = dev, name='Ethernet4/47')
        self.assertEqual(dev.interfaces[intf.name], intf)
        # self.assertEqual(dev.interfaces_map, {'Ethernet4/47':intf})

        dev.remove_interface(intf)
        self.assertEqual(intf.device, None)

        dev.add_interface(intf)
        self.assertEqual(dev.interfaces[intf.name], intf)
        # self.assertEqual(dev.interfaces_map, {'Ethernet4/47':intf})

    def test_find_interfaces(self):
        '''Can you find interfaces?'''
        tb = Genie.testbed = Testbed()
        # Let's say there is no Interface
        dev = Device(testbed = tb, name='myDevice', os='nxos')

        output = dev.find_interfaces()

        self.assertEqual(output, [])

        # Add some interface to that device!

        intf1 = BaseInterface(device =dev, name='Ethernet4/47')
        intf2 = BaseInterface(device =dev, name='Ethernet4/48')
        intf3 = BaseInterface(device =dev, name='Ethernet4/49')
        intf4 = BaseInterface(device =dev, name='Ethernet4/50')
        intf5 = BaseInterface(device =dev, name='Ethernet4/51',
                              obj_state='inactive')
        output = dev.find_interfaces()

        # Order might be different
        self.assertEqual(set(output), set([intf1, intf2, intf3, intf4]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in \
                                                 [intf1, intf2, intf3, intf4]]))

        # Let's filter
        # Return many
        output = dev.find_interfaces(name=Or('Ethernet4/47', 'Ethernet4/48'))

        # Order might be different
        self.assertEqual(set(output), set([intf1, intf2]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [intf1, intf2]]))

        # count = 1
        output = dev.find_interfaces(name=Or('Ethernet4/47', 'Ethernet4/48'),
                                     count=1)

        self.assertEqual(len(output), 1)

        # Negative
        output = dev.find_interfaces(name=Not('Ethernet4/47'))

        # Order might be different
        self.assertEqual(set(output), set([intf2, intf3, intf4]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [intf2, intf3, intf4]]))

        # Verify if request 4, and only 2 is returned we get an exception
        with self.assertRaises(CountError):
            output = dev.find_interfaces(name=Or('Ethernet4/47',
                                                 'Ethernet4/48'),
                                         count=5)

        # Let's verify the state now
        output = dev.find_interfaces(obj_state=Or('inactive'))

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

        output = dev.find_interfaces(obj_state=alwaysTrue)

        self.assertEqual(set(output), set([intf1, intf2, intf3, intf4, intf5]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [intf1, intf2, intf3,\
                                                        intf4, intf5]]))

        output = dev.find_interfaces(obj_state=alwaysFalse)

        self.assertEqual(set(output), set([]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in []]))

        output = dev.find_interfaces(callable_=OnlyTrueForEthernet47)

        self.assertEqual(set(output), set([intf1]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [intf1]]))

    def test_find_iterable_interfaces(self):
        '''Can you find interfaces?'''
        tb = Genie.testbed = Testbed()
        # Let's say there is no Interface
        dev = Device(testbed = tb, name='myDevice', os='nxos')

        output = dev.find_interfaces()

        self.assertEqual(output, [])

        # Add some interface to that device!

        intf1 = BaseInterface(device = dev, name='Ethernet4/47')
        intf2 = BaseInterface(device = dev, name='Ethernet4/48')
        intf3 = BaseInterface(device = dev, name='Ethernet4/49')
        intf4 = BaseInterface(device = dev, name='Ethernet4/50')
        intf5 = BaseInterface(device =dev, name='Ethernet4/51',
                              obj_state='inactive')

        output = dev.find_interfaces(iterable=[intf1, intf2, intf3])

        # Order might be different
        self.assertEqual(set(output), set([intf1, intf2, intf3]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in \
                                                 [intf1, intf2, intf3]]))

        # Let's filter
        # Return many
        output = dev.find_interfaces(iterable=[intf1, intf2, intf3],
                                     name=Or('Ethernet4/47', 'Ethernet4/48'))

        # Order might be different
        self.assertEqual(set(output), set([intf1, intf2]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [intf1, intf2]]))

        # count = 1
        output = dev.find_interfaces(iterable=[intf1, intf2, intf3],
                                     name=Or('Ethernet4/47', 'Ethernet4/48'),
                                     count=1)

        self.assertEqual(len(output), 1)

        # Negative
        output = dev.find_interfaces(iterable=[intf1, intf2, intf3],
                                     name=Not('Ethernet4/47'))

        # Order might be different
        self.assertEqual(set(output), set([intf2, intf3]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [intf2, intf3]]))

        # Multi fields
        # Also test single output are also list
        output = dev.find_interfaces(iterable=[intf1, intf2, intf3],
                                     name=Not('Ethernet4/47'))

        # Order might be different
        self.assertEqual(set(output), set([intf2, intf3]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [intf2, intf3]]))

        # Verify if request 4, and only 2 is returned we get an exception
        with self.assertRaises(CountError):
            output = dev.find_interfaces(iterable=[intf1, intf2, intf3],
                                         name=Or('Ethernet4/47',
                                                 'Ethernet4/48'),
                                         count=5)

        # Make sure only interfaces can be given as iterable
        output = dev.find_interfaces(iterable=[])
        self.assertEqual(output, [])


        self.assertEqual(len(dev.find_interfaces(iterable=[dev])), 0)

        # Let's verify the state now
        output = dev.find_interfaces(iterable=[intf1, intf2, intf3,
                                               intf4, intf5],
                                     obj_state=Or('inactive'))

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

        output = dev.find_interfaces(iterable=[intf1, intf2, intf3,
                                               intf4, intf5],
                                     obj_state=alwaysTrue)

        self.assertEqual(set(output), set([intf1, intf2, intf3, intf4, intf5]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [intf1, intf2, intf3,\
                                                        intf4, intf5]]))

        output = dev.find_interfaces(iterable=[intf1, intf2, intf3,
                                               intf4, intf5],
                                     obj_state=alwaysFalse)

        self.assertEqual(set(output), set([]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in []]))

        output = dev.find_interfaces(iterable=[intf1, intf2, intf3,
                                               intf4, intf5],
                                     callable_=OnlyTrueForEthernet47)

        self.assertEqual(set(output), set([intf1]))
        self.assertEqual(sorted([intf.name for intf in output]),
                         sorted([intf.name for intf in [intf1]]))

    def test_testbed_attribute(self):
        tb = Genie.testbed = Testbed()
        dev = Device(testbed=tb, name='myDevice', os='nxos')

        self.assertEqual(dev.__testbed__(), dev.testbed)
        self.assertEqual(dev.__testbed__(), tb)

        dev.testbed = None
        self.assertEqual(dev.__testbed__, dev.testbed)
        self.assertEqual(dev.__testbed__, None)


    def test_learn_management(self):
        '''Add, remove and add again the same interface'''

        golden_output = '''
            CH-P2-TOR-1# show ip interface brief vrf all | include 172.27.230.58
            mgmt0                172.27.230.58   protocol-up/link-up/admin-up
        '''

        tb = Genie.testbed = Testbed()
        device = Device(testbed=tb, name='aDevice', os='nxos')
        device.custom = {}
        device.custom['abstraction'] = {}
        device.custom['abstraction']['order'] = ['os']
        device.mapping={}
        device.mapping['cli']='cli'
        # Give the device as a connection type
        # This is done in order to call the parser on the output provided
        device.connectionmgr.connections['cli'] = '5'

        def mapper(key):
            return golden_output

        # Return output above as input to parser when called
        device.execute = Mock()
        device.execute.side_effect = mapper
        device.connected = False

        # Call the learn_management API
        interface_name = device.learn_management(connection_ip='172.27.230.58')

        self.assertEqual(device.management_interface, 'mgmt0')

    def test_device_parse(self):
        device = Device(name='aDevice', os='iosxe')
        device.custom.setdefault("abstraction", {})["order"] = ["os"]

        output = """
        Vlan211 is up, line protocol is up
        IPv6 is enabled, link-local address is FE80::257:D2FF:FE28:1A71 
        No Virtual link-local address(es):
        Stateless address autoconfig enabled
        Global unicast address(es):
          2001:10::14:1, subnet is 2001:10::14:0/112 
            valid lifetime 2591911 preferred lifetime 604711
        Joined group address(es):
          FF02::1
          FF02::1:FF14:1
          FF02::1:FF28:1A71
        MTU is 1500 bytes
        ICMP error messages limited to one every 100 milliseconds
        ICMP redirects are enabled
        ICMP unreachables are sent
        ND DAD is enabled, number of DAD attempts: 1
        ND reachable time is 30000 milliseconds (using 30000)
        ND NS retransmit interval is 1000 milliseconds
        """

        parsed_output = {
            "Vlan211": {
                "joined_group_addresses":
                ["FF02::1", "FF02::1:FF14:1", "FF02::1:FF28:1A71"],
                "ipv6": {
                    "2001:10::14:1/112": {
                        "ip": "2001:10::14:1",
                        "prefix_length": "112",
                        "status": "valid",
                        "autoconf": {
                            "preferred_lifetime": 604711,
                            "valid_lifetime": 2591911
                        },
                    },
                    "FE80::257:D2FF:FE28:1A71": {
                        "ip": "FE80::257:D2FF:FE28:1A71",
                        "status": "valid",
                        "origin": "link_layer",
                    },
                    "enabled": True,
                    "nd": {
                        "suppress": False,
                        "dad_attempts": 1,
                        "ns_retransmit_interval": 1000,
                        "dad_enabled": True,
                        "reachable_time": 30000,
                        "using_time": 30000,
                    },
                    "icmp": {
                        "error_messages_limited": 100,
                        "redirects": True,
                        "unreachables": "sent",
                    },
                },
                "oper_status":
                "up",
                "enabled":
                True,
                "autoconf":
                True,
                "mtu":
                1500,
            },
        }

        out = device.parse('show ipv6 interface', output=output)

        self.assertEqual(out, parsed_output)
        from genie.conf.base.utils import QDict
        self.assertTrue(type(out), QDict)

        device.connected = True
        out = device.parse('show ipv6 interface', output=output, timeout=30)
        self.assertEqual(out, parsed_output)

        device.connected = False
        out = device.parse('show ipv6 interface', output=output, timeout=30)
        self.assertEqual(out, parsed_output)

        # create corrupted output for SchemaMissingKeyError
        output2 = output.replace('2001:10::14:1, subnet', ', subnet')
        with self.assertRaises(SchemaMissingKeyError):
            device.parse('show ipv6 interface', output=output2)

    def test_device_parse_raw_data(self):
        device = Device(name='aDevice', os='iosxe')
        device.custom.setdefault("abstraction", {})["order"] = ["os"]

        output = """
        BOOT variable does not exist\r\n
        CONFIG_FILE variable does not exist\r\n
        BOOTLDR variable does not exist\r\n
        Configuration register is 0x2102
        """

        parsed_output = {'active': {'configuration_register': '0x2102'}}

        out = device.parse('show bootvar', output=output)

        self.assertEqual(out, parsed_output)
        self.assertFalse(hasattr(out, 'raw_output'))

        out = device.parse('show bootvar', output=output, raw_data=True)
        self.assertEqual(out, parsed_output)
        self.assertTrue(hasattr(out, 'raw_output'))

        self.assertTrue(
            all(k in out.raw_output[0].keys()
                for k in ['command', 'kwargs', 'output']))

        self.assertEqual(
            out.raw_output[0],
            {'command': 'show bootvar',
             'kwargs': {},
             'output': output})


class StubConnection(object):
    def __init__(self, device, alias, via):
        self.obj = device
        self.connected = False

    def connect(self):
        self.connected = True

    def execute(self):
        pass

    def test_get_self_obj(self):
        return self.obj

    def is_connected(self):
        return self.connected

    def disconnect(self):
        self.connected = False

class TestPyatsDeviceClass(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global AttrDict
        global Device, Interface, Link, Testbed
        global DuplicateDeviceError, TopologyDict

        from genie.conf.base.interface import BaseInterface as Interface
        from pyats.datastructures import AttrDict

        from pyats.topology.bases import TopologyDict
        from pyats.topology.exceptions import DuplicateDeviceError

    def setUp(self):
        self.testbed = Testbed(name = 'testTestbed')
        self.device = Device(name = 'testDevice')
        self.intf = Interface(name = 'testInterface', type = 'testType')
        self.link = Link(name = 'testLink')

    def test_create_bare_device(self):
        from pyats.connections import ConnectionManager
        obj = Device('testDevice2')

        # <class 'genie_libs.conf.device.Device'> is not
        # <class 'genie.conf.base.device.Device'>
        # self.assertIs(type(obj), Device)
        self.assertTrue(hasattr(obj, 'type'))
        self.assertTrue(hasattr(obj, 'alias'))
        self.assertTrue(hasattr(obj, 'testbed'))
        self.assertTrue(hasattr(obj, 'tacacs'))
        self.assertTrue(hasattr(obj, 'connections'))
        self.assertTrue(hasattr(obj, 'connectionmgr'))
        self.assertTrue(hasattr(obj, 'passwords'))
        self.assertTrue(hasattr(obj, 'clean'))
        self.assertTrue(hasattr(obj, 'custom'))
        self.assertTrue(hasattr(obj, 'interfaces'))

        self.assertIs(obj.type, None)
        self.assertIs(obj.testbed, None)
        self.assertEqual(obj.alias, obj.name)
        self.assertIs(type(obj.tacacs), AttrDict)
        self.assertIs(type(obj.connections), AttrDict)
        self.assertIs(type(obj.passwords), AttrDict)
        self.assertIs(type(obj.clean), AttrDict)
        self.assertIs(type(obj.interfaces), TopologyDict)
        self.assertIs(type(obj.connectionmgr), ConnectionManager)

        self.assertFalse(obj.tacacs)
        self.assertFalse(obj.passwords)
        self.assertFalse(obj.clean)
        self.assertFalse(obj.interfaces)
        self.assertFalse(obj.custom)

    def test_create_with_testbed(self):
        obj = Device('testDevice2', testbed = self.testbed)
        self.assertIs(obj.testbed, self.testbed)

    def test__alias(self):
        obj = Device('testDevice2', alias = 'lalala')
        self.assertEqual(obj.alias, 'lalala')
        self.assertEqual(obj.name, 'testDevice2')

    def test_create_with_dict(self):
        config = {'name': 'testDevice2',
                  'type': 'testType',
                  'passwords': {'enable': 'lab',
                                'line': 'lab',
                                'tacacs': 'CSCO12345^'},
                  'tacacs': {'login_prompt': 'login:',
                             'password_prompt': 'Password:',
                             'username': 'admin'},
                  'connections': {'a': {'protocol': 'telnet',
                                    'ip': '1.1.1.1',
                                    'port': 2001, },
                                  'b': {'protocol': 'telnet',
                                        'ip': '2.2.2.2',
                                        'port': 2003, },
                                  'alt': {'ip': '5.5.5.5',
                                          'protocol': 'telnet'}},
                  'clean': {'post_clean': 'some post_clean info',
                            'pre_clean': 'some pre_clean info'}}

        obj = Device(**config)
        assert obj.tacacs.login_prompt == 'login:'
        assert obj.tacacs.password_prompt == 'Password:'
        assert obj.tacacs.username == 'admin'
        assert type(obj.connections.a) is AttrDict
        assert type(obj.connections.b) is AttrDict
        assert type(obj.connections.alt) is AttrDict
        assert obj.passwords.enable == 'lab'
        assert obj.passwords.line == 'lab'
        assert obj.passwords.tacacs == 'CSCO12345^'
        assert obj.clean.post_clean == 'some post_clean info'
        assert obj.clean.pre_clean == 'some pre_clean info'
        self.assertFalse(obj.interfaces)

    def test_device_support_kwargs(self):
        a = Device('testDevice2', custom_arg1 =1, testarg = 2)
        self.assertEqual(a.custom_arg1, 1)
        self.assertEqual(a.testarg, 2)

    def test_device_custom_arg(self):
        a = Device('testDevice2', custom = {'a':2, 'b':4})
        self.assertEqual(a.custom.a, 2)
        self.assertEqual(a.custom.b, 4)

    def test_allow_duplicates_outside_of_testbed(self):
        a = Device('testDevice2')
        b = Device('testDevice2')

    def test_create_with_interface_list(self):
        intf1 = Interface('Eth1/1', 'test')
        intf2 = Interface('Eth1/2', 'test')
        d = Device(name = 'testDevice2', interfaces = [intf1, intf2])
        self.assertEqual(len(d.interfaces), 2)
        self.assertEqual(d.interfaces[intf1.name].device, d)
        self.assertEqual(d.interfaces[intf2.name].device, d)

    def test_testbed_weakref(self):
        class TestTestbed(object):
            credentials = Credentials({})
            def __contains__(self, obj):
                return True

        import weakref

        device = Device(name = 'testDevice')
        tb = TestTestbed()
        device.testbed = tb
        self.assertTrue(isinstance(type(device).testbed, property))
        self.assertTrue(isinstance(device.testbed.__weakref__, weakref.ReferenceType))

    def test_create_with_markups(self):
        config = {'name': 'testDevice2',
                  'type': 'testType',
                  'passwords': {'enable': 'lab',
                                'line': 'lab',
                                'tacacs': 'CSCO12345^'},
                  'tacacs': {'login_prompt': 'login:',
                             'password_prompt': 'Password:',
                             'username': 'admin'},
                  'connections': {'a': {'protocol': 'telnet',
                                        'ip': '1.1.1.1',
                                        'port': 2001, },
                                  'b': {'protocol': 'telnet',
                                        'ip': '2.2.2.2',
                                        'port': 2003, },
                                  'vty': {'ip': '5.5.5.5',
                                          'protocol': 'telnet'}},
                 'clean': {'post_clean':'mgmt_ip = %{self.connections.vty.ip}\n'
                                        'name = %{self}',
                            'pre_clean':'console = %{self.connections.b.ip}\n'
                                        'password = %{self.passwords.line}'}}

        obj = Device(**config)

        # note, markups are no longer supported in device inits
        with self.assertRaises(AssertionError):
            assert obj.clean.post_clean == ('mgmt_ip = 5.5.5.5\n'
                                            'name = testDevice2')
        with self.assertRaises(AssertionError):
            assert obj.clean.pre_clean == ('console = 2.2.2.2\n'
                                           'password = lab')


    def test_add_interface(self):
        self.assertFalse(self.device.interfaces)

        self.device.add_interface(self.intf)

        self.assertEqual(len(self.device.interfaces), 1)
        self.assertIs(self.device.interfaces[self.intf.name], self.intf)
        self.assertIs(self.intf.device, self.device)

    def test_duplicate_interface(self):
        self.device.add_interface(self.intf)

        intf = Interface(name = 'testInterface', type='dupe')
        from pyats.topology import exceptions

        with self.assertRaises(exceptions.DuplicateInterfaceError):
            self.device.add_interface(intf)

    def test_remove_interface(self):
        self.device.add_interface(self.intf)
        self.device.remove_interface(self.intf)

        self.assertFalse(self.device.interfaces)

    def test_remove_interface_by_name(self):
        self.device.add_interface(self.intf)
        self.device.remove_interface(self.intf.name)

        self.assertFalse(self.device.interfaces)

    def test_remove_interface_error(self):
        from pyats.topology import exceptions

        with self.assertRaises(exceptions.UnknownInterfaceError):
            self.device.remove_interface('nonexistent')

    def test_remote_devices(self):
        deviceA = Device('testDeviceA')
        deviceB = Device('testDeviceB')
        deviceC = Device('testDeviceC')
        intf1 = Interface(name = 'Eth1/1',
                          type = 'test',
                          link = self.link)
        intf2 = Interface(name = 'Eth1/2',
                          type = 'test',
                          link = self.link)
        intf3 = Interface(name = 'Eth1/3',
                          type = 'test',
                          link = self.link)
        deviceA.add_interface(intf1)
        deviceB.add_interface(intf2)
        deviceC.add_interface(intf3)
        self.assertEqual(deviceA.remote_devices, set([deviceB, deviceC]))
        self.assertEqual(deviceB.remote_devices, set([deviceA, deviceC]))
        self.assertEqual(deviceC.remote_devices, set([deviceA, deviceB]))

        del deviceC
        del intf3
        import gc; gc.collect()
        self.assertEqual(deviceA.remote_devices, set([deviceB]))
        self.assertEqual(deviceB.remote_devices, set([deviceA]))

    def test_remote_devices_empty(self):
        deviceA = Device('testDeviceA')
        self.assertFalse(deviceA.remote_devices)

    def test_remote_interfaces_empty(self):
        deviceA = Device('testDeviceA')
        self.assertFalse(deviceA.remote_interfaces)

    def test_remote_interfaces(self):
        deviceA = Device('testDeviceA')
        deviceB = Device('testDeviceB')
        deviceC = Device('testDeviceC')
        intf1 = Interface(name = 'Eth1/1',
                          type = 'test',
                          link = self.link)
        intf2 = Interface(name = 'Eth1/2',
                          type = 'test',
                          link = self.link)
        intf3 = Interface(name = 'Eth1/3',
                          type = 'test',
                          link = self.link)
        deviceA.add_interface(intf1)
        deviceB.add_interface(intf2)
        deviceC.add_interface(intf3)

        self.assertEqual(deviceA.remote_interfaces, set([intf2, intf3]))
        self.assertEqual(deviceB.remote_interfaces, set([intf1, intf3]))
        self.assertEqual(deviceC.remote_interfaces, set([intf1, intf2]))

        del deviceC
        del intf3
        import gc; gc.collect()
        self.assertEqual(deviceA.remote_interfaces, set([intf2]))
        self.assertEqual(deviceB.remote_interfaces, set([intf1]))


    def test_links_no_link(self):
        self.assertIs(type(self.device.links), set)
        self.assertEqual(self.device.links, set())

    def test_links_with_link(self):
        intf1 = Interface(name = 'Eth1/1',
                          type = 'test',
                          link = self.link)
        intf2 = Interface(name = 'Eth1/2',
                          type = 'test',
                          link = self.link)

        self.device.add_interface(intf1)
        self.device.add_interface(intf2)

        self.assertIs(intf1.link, intf2.link)
        self.assertIn(intf1.link, self.device.links)

    def test_in(self):
        intf1 = Interface(name = 'Eth1/1',
                          type = 'test',
                          link = self.link)
        intf2 = Interface(name = 'Eth1/2',
                          type = 'test',
                          link = self.link)

        self.device.add_interface(intf1)
        self.device.add_interface(intf2)
        self.assertIn(intf1, self.device)
        self.assertIn(intf1, self.device)
        self.assertIn('Eth1/1', self.device)
        self.assertIn('Eth1/2', self.device)
        self.assertNotIn(Interface(name = 'Eth1/3',
                          type = 'test'), self.device)

    def test_iter(self):
        intf1 = Interface(name = 'Eth1/1',
                          type = 'test',
                          link = self.link)
        intf2 = Interface(name = 'Eth1/2',
                          type = 'test',
                          link = self.link)

        self.device.add_interface(intf1)
        self.device.add_interface(intf2)

        intfs = []
        for intf in self.device:
            intfs.append(intf)

        self.assertEqual(intfs, list(self.device.interfaces.values()))

    ## A meeting is needed to discuss the connection methods between
    ## Genie and Pyats
    def test_connect(self):

        self.assertFalse(self.device.is_connected())

        self.device.connect(StubConnection)
        self.assertTrue(self.device.is_connected())

        # Default connection is 'default' for non unicon/rest/yang connection classes
        self.assertIs(self.device.default.obj, self.device)
        self.assertEqual(self.device.execute, self.device.default.execute)
        self.assertIs(self.device.test_get_self_obj(), self.device)

    def test_connection_alias(self):

        self.device.connect(StubConnection, alias = 'testAlias')

        self.assertIn('testAlias', self.device.connectionmgr.connections)
        self.assertTrue(self.device.testAlias.is_connected())
        self.assertIs(self.device.testAlias.obj, self.device)
        self.assertEqual(self.device.testAlias.execute,
                                self.device.connectionmgr.testAlias.execute)
        self.assertIs(self.device.testAlias.test_get_self_obj(), self.device)

    def test_disconnect(self):

        self.device.connect(StubConnection)

        self.assertTrue(self.device.is_connected())
        self.device.disconnect()

        self.assertFalse(self.device.is_connected())

        self.device.connect(StubConnection)
        self.assertTrue(self.device.is_connected())

    def test_destroy_connection(self):
        self.device.connect(StubConnection)

        self.device.destroy()

        self.assertFalse(self.device.connectionmgr.connections)

    def test_device_testbed_can_be_None(self):
        self.device.testbed = None

    def test_garbage_collection(self):
        intf1 = Interface(name = 'Eth1/1',
                          type = 'test',
                          link = self.link)
        intf2 = Interface(name = 'Eth1/2',
                          type = 'test',
                          link = self.link)

        self.device.add_interface(intf1)
        self.device.add_interface(intf2)

        self.assertEqual(self.link.interfaces, [intf1, intf2])
        self.device.remove_interface(intf2)
        del intf2

        import gc; gc.collect()
        self.assertEqual(self.link.interfaces, [intf1,])

    def test_assign_testbed_adds_device(self):
        self.device.testbed = self.testbed
        self.assertIn(self.device, self.testbed)


    def test_assign_testbed_none_removes_device(self):
        self.device.testbed = self.testbed
        self.assertIn(self.device, self.testbed)
        self.device.testbed = None
        self.assertNotIn(self.device, self.testbed)

    def test_find_links(self):
        device_a = Device('a')
        device_b = Device('b')

        link = Link('commonlink')

        device_a.add_interface(Interface('Eth1/1', 'eth', link=link))
        device_b.add_interface(Interface('Eth1/1', 'eth', link=link))

        self.assertIs(link, list(device_a.find_links(device_b))[0])
        self.assertIs(link,
                    list(device_a.find_links(device_b.interfaces['Eth1/1']))[0])

    def test_find_links_loopback(self):
        device = Device('a')

        link = Link('loopback')

        device.add_interface(Interface('Eth1/1', 'eth', link=link))
        device.add_interface(Interface('Eth2/1', 'eth', link=link))
        device.add_interface(Interface('Eth3/1', 'eth', link=Link('noend')))
        self.assertEqual(set([link]), device.find_links(device))

    def test_interface_alias(self):
        intf1 = Interface(name = 'Eth1/1',
                          type = 'test',
                          alias = 'alias_1')
        intf2 = Interface(name = 'Eth1/2',
                          type = 'test',
                          alias = 'alias_2')

        self.device.add_interface(intf1)
        self.device.add_interface(intf2)

        device = self.device

        self.assertIs(device.interfaces['Eth1/1'], device.interfaces['alias_1'])
        self.assertIs(device.interfaces['Eth1/2'], device.interfaces['alias_2'])

        self.assertEqual(device.interfaces.aliases, set(['alias_1', 'alias_2']))
        self.assertTrue(device.interfaces.is_alias('alias_1'))
        self.assertTrue(device.interfaces.is_alias('alias_2'))
        self.assertFalse(device.interfaces.is_alias('Eth1/1'))
        self.assertFalse(device.interfaces.is_alias('Eth1/2'))

    def test_interface_alias_in_operatiro(self):
        intf1 = Interface(name = 'Eth1/1',
                          type = 'test',
                          alias = 'alias_1')
        intf2 = Interface(name = 'Eth1/2',
                          type = 'test',
                          alias = 'alias_2')

        self.device.add_interface(intf1)
        self.device.add_interface(intf2)

        self.assertIn('alias_1', self.device)
        self.assertIn('alias_2', self.device)

    def test_recursive_dir(self):

        attrs = dir(self.device)

        self.assertIn('connect', attrs)
        self.assertIn('disconnect', attrs)
        self.assertIn('disconnect_all', attrs)
        self.assertIn('is_connected', attrs)
        self.assertIn('destroy', attrs)
        self.assertIn('destroy_all', attrs)

    def test_recursive_dir_with_connection_mgr(self):

        class DummyObj(object):
            def lala(self): pass
            def woot(self): pass

        self.device.connectionmgr.connections[
            self.device.connectionmgr.default_alias]=DummyObj
        self.device.connectionmgr.connections['awesome']= 'yes!'

        attrs = dir(self.device)
        self.assertIn(self.device.connectionmgr.default_alias, attrs)

        self.assertIn('lala', attrs)
        self.assertIn('woot', attrs)
        self.assertIn('awesome', attrs)


if __name__ == '__main__':
    unittest.main()
