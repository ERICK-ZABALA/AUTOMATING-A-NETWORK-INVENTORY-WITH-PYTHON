import unittest
import yaml, os

YAML_DIR = os.path.join(os.path.dirname(__file__), 'yamls')


class TestbedMarkupProcessorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global TestbedMarkupProcessor, MarkupError

        from pyats.topology.loader.markup import TestbedMarkupProcessor
        from pyats.utils.yaml.exceptions import MarkupError

    def test_subclass(self):
        from pyats.utils.yaml import markup

        self.assertTrue(issubclass(TestbedMarkupProcessor, markup.Processor))

    def test_markup_processor(self):
        with open(os.path.join(YAML_DIR, 'testbed.yaml')) as f:
            data = yaml.safe_load(f)

        p = TestbedMarkupProcessor()

        data = p(data)
        
        intf = data['topology']['device-a']['interfaces']
        overall_lookup = intf['Ethernet4/6']['mgmt']
        should_equal=data['devices']['device-a']['connections']['alt']['ip']
        self.assertEqual(str(overall_lookup), str(should_equal))

        overall_lookup = data['devices']['device-a']['clean']['mgt_itf']['ipv4']['address']
        should_equal=data['devices']['device-a']['connections']['a']['ip']
        self.assertEqual(str(overall_lookup), str(should_equal))


    def test_markup_failure_non_device(self):
        context = '''
testbed:
    name: some testbed

devices:
    myDevice:
        type: testType

topology:
    myDevice:
        interfaces:
            Eth1/1:
                ip: "%{self.ip}"
        '''
        data = yaml.safe_load(context)
        p = TestbedMarkupProcessor()

        with self.assertRaises(MarkupError):
            data = p(data)

    def test_markup_failure_no_such_key(self):
        context = '''
testbed:
    name: some testbed

devices:
    myDevice:
        type: testType

topology:
    myDevice:
        interfaces:
            Eth1/1:
                ip: "%{devices.myDevice.connections.alt.ip}"
        '''

        data = yaml.safe_load(context)

        p = TestbedMarkupProcessor()

        with self.assertRaises(MarkupError):
            data = p(data)


    def test_markup_self_is_self(self):
        context = '''
devices:
    myDevice:
        type: testType
        name: "%{self}"
'''

        data = yaml.safe_load(context)
        p = TestbedMarkupProcessor()

        data = p(data)

        self.assertEqual(data['devices']['myDevice']['name'], 'myDevice')

    def test_markup_list(self):
        context = '''
devices:
    myDevice:
        type: testType
        name: "%{self}"
        custom: 
            my_list:
                - "%{self}"
                - "%{self.type}"
'''

        data = yaml.safe_load(context)
        p = TestbedMarkupProcessor()

        data = p(data)
        self.assertEqual(data['devices']['myDevice']['custom']['my_list'], 
                         ['myDevice', 'testType'])


    def test_markup_mega_complex_bad(self):
        """ Test an example of failing markup from a real user.
        Ensure appropriate debug is thrown to allow user
        to diagnose the problem.
        """

        with open(os.path.join(YAML_DIR, 'markup_complex_bad.yaml')) as f:
            data = yaml.safe_load(f)

        p = TestbedMarkupProcessor()

        with self.assertRaisesRegex(MarkupError,
                'devices.*inter-rtr.*clean.*pre_clean.*10'):
            out = p(data)

    def test_markup_illegal_log_phys_itf_name_request(self):
        context = '''
testbed:
    name: some testbed %INTF{my_logical_itf}

devices:
    myDevice:
        type: testType

topology:
    myDevice:
        interfaces:
            Eth1/1:
                alias: my_logical_itf
                ip: 1.2.3.4
        '''

        data = yaml.safe_load(context)

        p = TestbedMarkupProcessor()

        with self.assertRaises(MarkupError):
            data = p(data)


    def test_markup_log_phys_itf_name_request(self):
        context = '''
testbed:
    name: some testbed

devices:
    myDevice:
        type: testType
        custom:
            my_actual_itf:  "%INTF{my_logical_itf}"

topology:
    myDevice:
        interfaces:
            Eth1/1:
                alias: my_logical_itf
                ip: 1.2.3.4
        '''

        data = yaml.safe_load(context)

        p = TestbedMarkupProcessor()

        data = p(data)
        self.assertEqual(
            data['devices']['myDevice']['custom']['my_actual_itf'],
            'Eth1/1')

        # Ensure processor does not keep state and can be used again.
        data = yaml.safe_load(context)
        data = p(data)
        self.assertEqual(
            data['devices']['myDevice']['custom']['my_actual_itf'],
            'Eth1/1')

        # Now, take away the interface alias, re-scan markup and ensure that
        # the log->act interface markup is ignored, indicating that state
        # has been correctly cleared.
        context2 = '''
testbed:
    name: some testbed

devices:
    myDevice:
        type: testType
        custom:
            my_actual_itf:  "%INTF{my_logical_itf}"

topology:
    myDevice:
        interfaces:
            Eth1/1:
                ip: 1.2.3.4
        '''

        data = yaml.safe_load(context2)
        data = p(data)
        self.assertEqual(
            data['devices']['myDevice']['custom']['my_actual_itf'],
            '%INTF{my_logical_itf}')


class TopologyLoaderTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global Interface, Testbed, Device, Link, loader, MarkupError
        global SchemaMissingKeyError, IPv4Interface, IPv6Interface
        global TestbedMarkupProcessor

        from pyats.topology.loader.markup import TestbedMarkupProcessor

        from genie.conf.base.link import Link
        from genie.conf.base.device import Device
        from genie.conf.base.testbed import Testbed
        from genie.conf.base.interface import BaseInterface as Interface

        from genie.conf.base import loader 
        from pyats.utils.yaml.exceptions import MarkupError
        from pyats.utils.exceptions import SchemaMissingKeyError
        from ipaddress import IPv4Interface, IPv6Interface

    def test_module_is_instance(self):
        self.assertEqual(loader.__class__.__name__, "TestbedFileLoader")

    def test_contains_schema(self):
        from pyats.topology import schema
        self.assertEqual(schema.production_schema, loader.schema)

    def test_load_dict_with_markups(self):
        context = '''
devices:
    myDevice:
        type: "%{self}"
        connections: 
            a: 
                protocol: telnet
                ip: 1.1.1.1
'''

        context = loader.load_arbitrary(context)
        p = TestbedMarkupProcessor()

        data = p(context)

        self.assertEqual(data['devices']['myDevice']['type'], 'myDevice')

    def test_load_near_empty_dict(self):
        data = {
            'devices': {}
        }
        config = loader.load_arbitrary(data)
        self.assertIn('testbed', config)
        self.assertIn('devices', config)
        self.assertIn('topology', config)

    def test_load_defaults(self):
        config = loader.load_arbitrary(os.path.join(YAML_DIR, 
                                                    'bare_minimum.yaml'))

        self.assertIn('testbed', config)
        self.assertIn('devices', config)
        self.assertIn('topology', config)

        self.assertIs(type(config['testbed']), dict)
        self.assertIs(type(config['devices']), dict)
        self.assertIs(type(config['topology']), dict)
        self.assertEqual(config['testbed']['name'], 'bare_minimum')

    def test_load_empty(self):
        config = loader.load_arbitrary(os.path.join(YAML_DIR, 
                                                        'CONFIG.empty'))
        self.assertIn('testbed', config)
        self.assertIn('devices', config)
        self.assertIn('topology', config)

        self.assertIs(type(config['testbed']), dict)
        self.assertIs(type(config['devices']), dict)
        self.assertIs(type(config['topology']), dict)
        self.assertEqual(config['testbed']['name'], 'empty')

    def test_load_none(self):
        config = loader.load_arbitrary(None)
        self.assertIn('testbed', config)
        self.assertIn('devices', config)
        self.assertIn('topology', config)

        self.assertIs(type(config['testbed']), dict)
        self.assertIs(type(config['devices']), dict)
        self.assertIs(type(config['topology']), dict)

    def test_load_yaml(self):
        # note: requires self.testbed.yaml at this file's location
        tbfile = os.path.join(YAML_DIR, 'pass.yaml')
        testbed = loader.load(tbfile)

        # AssertionError: <class 'genie_libs.conf.testbed.Testbed'> is not
        # <class 'genie.conf.base.testbed.Testbed'>
        # self.assertIs(type(testbed), Testbed)
        self.assertEqual(testbed.alias, 'lalala')
        self.assertEqual(testbed.testbed_file, tbfile)
        self.assertEqual(len(testbed.devices), 2)
        self.assertEqual(testbed.name, 'test_testbed-pass')
        self.assertIn('device-a', testbed.devices)
        self.assertIn('device-b', testbed.devices)
        # AssertionError: <class 'genie_libs.conf.device.Device'> is not
        # <class 'genie.conf.base.device.Device'>
        # self.assertIs(type(testbed.devices['device-a']), Device)
        # self.assertIs(type(testbed.devices['device-b']), Device)

        deviceA = testbed.devices['device-a']
        deviceB = testbed.devices['device-b']
        self.assertEqual(deviceA.alias, 'bbb')

        self.assertEqual(deviceA.links, deviceB.links)
        self.assertIs(type(deviceA.interfaces['Ethernet4/6'].link), Link)
        self.assertEqual(deviceA.interfaces['Ethernet4/6'].link.name, 'link-x')
        self.assertEqual(
                    len(deviceA.interfaces['Ethernet4/6'].link.interfaces), 2)
        self.assertIs(deviceA.interfaces['Ethernet4/6'].link, 
                      deviceB.interfaces['Ethernet5/1'].link)
        self.assertTrue(isinstance(deviceA.interfaces['Ethernet4/6'].ipv4, 
                                    IPv4Interface))
        self.assertTrue(isinstance(deviceA.interfaces['Ethernet4/6'].ipv6,
                                    IPv6Interface))
        self.assertEqual(deviceA.interfaces['Ethernet4/6'].alias, 'woot')

    def test_load_via_yaml_extra_topo_device(self):
        with self.assertRaises(Exception):
            loader.load(os.path.join(YAML_DIR, 'extra_topo_device.yaml'))

    def test_load_missing_key(self):
        with self.assertRaises(MarkupError):
            loader.load(os.path.join(YAML_DIR, 'missing_key.yaml'))

    def test_load_via_dict(self):
        with open(os.path.join(YAML_DIR, 'pass.yaml'), 'r') as config:
            config = yaml.safe_load(config)

        testbed = loader.load(config)

        # AssertionError: <class 'genie_libs.conf.testbed.Testbed'> is not
        # <class 'genie.conf.base.testbed.Testbed'>
        # self.assertIs(type(testbed), Testbed)
        self.assertEqual(len(testbed.devices), 2)
        self.assertEqual(testbed.name, 'test_testbed-pass')
        self.assertIn('device-a', testbed.devices)
        self.assertIn('device-b', testbed.devices)
        # AssertionError: <class 'genie_libs.conf.device.Device'> is not
        # <class 'genie.conf.base.device.Device'>
        # self.assertIs(type(testbed.devices['device-a']), Device)
        # self.assertIs(type(testbed.devices['device-b']), Device)

        deviceA = testbed.devices['device-a']
        deviceB = testbed.devices['device-b']

        self.assertEqual(deviceA.links, deviceB.links)
        self.assertIs(type(deviceA.interfaces['Ethernet4/6'].link), Link)
        self.assertEqual(deviceA.interfaces['Ethernet4/6'].link.name, 'link-x')
        self.assertEqual(
                    len(deviceA.interfaces['Ethernet4/6'].link.interfaces), 2)
        self.assertIs(deviceA.interfaces['Ethernet4/6'].link, 
                      deviceB.interfaces['Ethernet5/1'].link)

    def test_yaml_config_error(self):
        from pyats.topology import exceptions
        with self.assertRaises(exceptions.MissingDeviceError):
            testbed = loader.load(os.path.join(YAML_DIR, 'config_error.yaml'))

    def test_load_detailed_links(self):
        testbed = loader.load(os.path.join(YAML_DIR, 'detailed_links.yaml'))

        # AssertionError: <class 'genie_libs.conf.testbed.Testbed'> is not
        # <class 'genie.conf.base.testbed.Testbed'>
        # self.assertIs(type(testbed), Testbed)
        self.assertEqual(len(testbed.devices), 2)
        self.assertEqual(testbed.name, 'test_link_details')
        self.assertIn('device-a', testbed.devices)
        self.assertIn('device-b', testbed.devices)
        # AssertionError: <class 'genie_libs.conf.device.Device'> is not
        # <class 'genie.conf.base.device.Device'>
        # self.assertIs(type(testbed.devices['device-a']), Device)
        # self.assertIs(type(testbed.devices['device-b']), Device)

        deviceA = testbed.devices['device-a']
        deviceB = testbed.devices['device-b']

        self.assertIs(type(deviceA.interfaces['Ethernet4/6'].link), Link)
        self.assertEqual(deviceA.interfaces['Ethernet4/6'].link.name, 'link-x')
        self.assertEqual(
                    len(deviceA.interfaces['Ethernet4/6'].link.interfaces), 2)
        self.assertIs(deviceA.interfaces['Ethernet4/6'].link, 
                      deviceB.interfaces['Ethernet5/1'].link)

        linkx = deviceA.interfaces['Ethernet4/6'].link
        linky = deviceA.interfaces['Ethernet4/7'].link

        self.assertEqual(linkx.x, 1)
        self.assertEqual(linkx.y, 2)

        self.assertEqual(linky.xxx, 3)
        self.assertEqual(linky.yyy, 4)

        link_no_end = deviceB.interfaces['Ethernet5/3'].link
        self.assertEqual(link_no_end.name, 'no-end')
        self.assertFalse(hasattr(link_no_end,'x'))
        self.assertFalse(hasattr(link_no_end,'y'))

        self.assertEqual(len(testbed.links), 3)
        self.assertEqual(testbed.links, set([linkx, linky, link_no_end]))

    def test_load_subclassed_objects(self):
        testbed = loader.load(os.path.join(YAML_DIR, 'subclasses.yaml'))

        from genie.tests.conf.base.dummy import AltDevice, AltInterface, AltLink
        from genie.tests.conf.base.dummy import AltTestbed

        self.assertIs(type(testbed), AltTestbed)
        self.assertEqual(len(testbed.devices), 3)
        self.assertEqual(testbed.name, 'subclasses')
        self.assertIn('dev-a', testbed)
        self.assertIn('dev-b', testbed)
        self.assertIn('dev-c', testbed)
        self.assertIs(type(testbed.devices['dev-a']), AltDevice)
        self.assertIs(type(testbed.devices['dev-b']), AltDevice)
        # AssertionError: <class 'genie_libs.conf.device.Device'> is not
        # <class 'genie.conf.base.device.Device'>
        # self.assertIs(type(testbed.devices['dev-c']), Device)

        deviceA = testbed.devices['dev-a']
        deviceB = testbed.devices['dev-b']
        deviceC = testbed.devices['dev-c']

        self.assertIs(type(deviceA.interfaces['Eth1/1'].link), AltLink)
        self.assertIs(type(deviceA.interfaces['Eth1/2'].link), AltLink)
        self.assertIs(type(deviceA.interfaces['Eth1/3'].link), Link)
        self.assertEqual(deviceA.interfaces['Eth1/1'].link.alias, 'woot')
        self.assertIs(deviceA.interfaces['Eth1/1'].link,
                      deviceB.interfaces['Eth1/1'].link)
        self.assertIs(deviceA.interfaces['Eth1/1'].link,
                      deviceC.interfaces['Eth1/1'].link)
        self.assertEqual(deviceC.interfaces['Eth1/1'].link.x, True)
        self.assertIs(deviceA.interfaces['Eth1/2'].link,
                      deviceB.interfaces['Eth1/2'].link)
        self.assertIs(deviceA.interfaces['Eth1/2'].link,
                      deviceC.interfaces['Eth1/2'].link)
        self.assertIs(deviceA.interfaces['Eth1/3'].link,
                      deviceB.interfaces['Eth1/3'].link)
        self.assertIs(deviceA.interfaces['Eth1/3'].link,
                      deviceC.interfaces['Eth1/3'].link)

        self.assertEqual(len(testbed.links), 3)
        self.assertEqual(testbed.links, 
                         set([deviceA.interfaces['Eth1/1'].link,
                              deviceA.interfaces['Eth1/2'].link,
                              deviceA.interfaces['Eth1/3'].link]))

    def test_load_subclassed_objects_failure(self):
        from pyats.utils.exceptions import SchemaError

        with self.assertRaises(SchemaError):
            testbed = loader.load(os.path.join(YAML_DIR, 'subclass_error.yaml'))

    def test_load_str_get_exception(self):
        from pyats.utils.yaml.exceptions import LoadError

        with self.assertRaises(LoadError):
            loader.load('some string')

    def test_load_defaults_extends(self):
        ''' Test using the extends key to inherit content from another file'''
        actual_tb = loader.load(os.path.join(YAML_DIR, 'extends_tb.yaml'))

        # Test base fields
        self.assertEqual(actual_tb.devices['device-a'].type, 'test device')
        self.assertEqual(actual_tb.devices['device-b'].type, 'test device2')

        # Test overloaded fields
        self.assertEqual(actual_tb.devices['device-a'].\
            connections['a']['ip'].exploded, '2.2.2.2')
        self.assertEqual(actual_tb.devices['device-a'].\
            connections['a']['port'], 2002)

        self.assertEqual(actual_tb.devices['device-b'].\
            connections['a']['ip'].exploded, '3.3.3.3')
        self.assertEqual(actual_tb.devices['device-b'].\
            connections['a']['port'], 2003)


class TestCombo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global loader
        global TestbedMarkupProcessor

        from genie.conf.base import loader
        from pyats.topology.loader.markup import TestbedMarkupProcessor

    def test_load_file(self):
        data = loader.load_arbitrary(os.path.join(YAML_DIR, 'testbed.yaml'))

        data = TestbedMarkupProcessor()(data)
        intf = data['topology']['device-a']['interfaces']
        overall_lookup = intf['Ethernet4/6']['mgmt']

        should_equal=data['devices']['device-a']['connections']['alt']['ip']
        self.assertEqual(str(overall_lookup), str(should_equal))

    def test_load_dict(self):
        data =  yaml.safe_load(os.path.join(YAML_DIR, 'testbed.yaml'))
        config = loader.load_arbitrary(data)

        config = TestbedMarkupProcessor()(config)
        intf = config['topology']['device-a']['interfaces']
        overall_lookup = intf['Ethernet4/6']['mgmt']

        should_equal=config['devices']['device-a']['connections']['alt']['ip']
        self.assertEqual(str(overall_lookup), str(should_equal))

if __name__ == "__main__": # pragma: no cover
    unittest.main()
