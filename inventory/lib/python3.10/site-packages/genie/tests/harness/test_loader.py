#!/bin/env python
""" Unit tests for the datafile loader within genie """

import os
import unittest
from genie.conf.base import Testbed
from genie.harness.datafile.loader import TriggerdatafileLoader
from genie.testbed import load as GenieTbLoader
from pyats.utils.yaml.loader import Loader

class TestLoader(unittest.TestCase):
    curr_dir = os.path.dirname(os.path.abspath(__file__))

    def test_markup_processor_testbed_device_and_topology(self):
        """ Tests that the testbed object is loadable using
            markup processor in other
        """

        # load testbed object from yaml
        with open(os.path.join(self.curr_dir, "script/testbed1.yaml")) as f:
            testbed_yaml = Loader().load(f.read())
        testbed_obj = Testbed(raw_config=testbed_yaml)
        loader = TriggerdatafileLoader(testbed=testbed_obj)

        trigger_datafile_1 = """
            TriggerTest:
                source:
                    pkg: fruit
                    class: banana
                devices: ['%{testbed.devices.PE1.alias}']
        """
        # load trigger_datafile
        loaded_1 = loader.load(trigger_datafile_1)
        # checking markup worked correctly
        self.assertEqual(['uut'], loaded_1['TriggerTest']['devices'])
        # checking that the testbed obj was removed
        with self.assertRaises(KeyError):
            _ = loaded_1['testbed']

        # device: PE1, topology interface: GigabitEthernet2
        trigger_datafile_2 = """
            TriggerTest:
                source:
                    pkg: fruit
                    class: banana
                devices: ['unut']
                test_sections:
                    apply_config:
                        print:
                            value: "%{testbed.topology.PE1.interfaces.GigabitEthernet2.type}"
        """
        loaded_2 = loader.load(trigger_datafile_2)
        self.assertEqual('ethernet', loaded_2['TriggerTest']['test_sections']['apply_config']['print']['value'])

    def test_markup_processor_testbed_device_and_topology_alias_replacement(self):
        """ Tests that the testbed object is loadable using
            markup processor and the device name are replaced 
            properly with its aliases
        """
        with open(os.path.join(self.curr_dir, "script/testbed1.yaml")) as f:
            testbed_yaml = Loader().load(f.read())
        testbed_obj = Testbed(raw_config=testbed_yaml)
        loader = TriggerdatafileLoader(testbed=testbed_obj)

        # device: PE1, alias: uut
        trigger_datafile_1 = """
            TriggerTest:
                source:
                    pkg: fruit
                    class: banana
                devices: ['%{testbed.devices.uut.alias}']
        """
        loaded_1 = loader.load(trigger_datafile_1)
        self.assertEqual(['uut'], loaded_1['TriggerTest']['devices'])

        # device: P1, alias: unut
        trigger_datafile_2 = """
            TriggerTest:
                source:
                    pkg: fruit
                    class: banana
                devices: ['unut']
                test_sections:
                    apply_config:
                        print:
                            value: "%{testbed.devices.unut.connections.cli.ip}"
        """
        loaded_2 = loader.load(trigger_datafile_2)
        self.assertEqual('1.1.1.1', loaded_2['TriggerTest']['test_sections']['apply_config']['print']['value'])

        # device: PE1, topology interface: GigabitEthernet3, alias: pe1-p1-2
        trigger_datafile_3 = """
            TriggerTest:
                source:
                    pkg: fruit
                    class: banana
                devices: ['unut']
                test_sections:
                    apply_config:
                        print:
                            value: "%{testbed.topology.PE1.interfaces.pe1-p1-2.type}"
        """
        loaded_3 = loader.load(trigger_datafile_3)
        self.assertEqual('ethernet', loaded_3['TriggerTest']['test_sections']['apply_config']['print']['value'])

        # device: PE1, alias: uut, topology interface: GigabitEthernet3 alias: pe1-p1-2
        trigger_datafile_4 = """
            TriggerTest:
                source:
                    pkg: fruit
                    class: banana
                devices: ['unut']
                test_sections:
                    apply_config:
                        print:
                            value: "%{testbed.topology.uut.interfaces.pe1-p1-2.type}"
        """
        loaded_4 = loader.load(trigger_datafile_4)
        self.assertEqual('ethernet', loaded_4['TriggerTest']['test_sections']['apply_config']['print']['value'])

        # topology links, call by device, device: P2_link alias: p2_link_alias
        trigger_datafile_5 = """
            TriggerTest:
                source:
                    pkg: fruit
                    class: banana
                devices: ['unut']
                test_sections:
                    apply_config:
                        print:
                            value: "%{testbed.topology.links.p2_link_alias.alias}"
        """
        loaded_5 = loader.load(trigger_datafile_5)

        # topology links, call by device alias, device: P2_link alias: p2_link_alias
        trigger_datafile_6 = """
            TriggerTest:
                source:
                    pkg: fruit
                    class: banana
                devices: ['unut']
                test_sections:
                    apply_config:
                        print:
                            value: "%{testbed.topology.links.P2_link.alias}"
        """
        loaded_6 = loader.load(trigger_datafile_6)
        self.assertEqual(loaded_5['TriggerTest']['test_sections']['apply_config']['print']['value'],
                         loaded_6['TriggerTest']['test_sections']['apply_config']['print']['value'])

        # topology links, call by device alias, device: link-x, alias: x-link
        trigger_datafile_7 = """
            TriggerTest:
                source:
                    pkg: fruit
                    class: banana
                devices: ['unut']
                test_sections:
                    apply_config:
                        print:
                            value: "%{testbed.topology.links.x-link.x}"
        """
        loaded_7 = loader.load(trigger_datafile_7)
        self.assertEqual(1, loaded_7['TriggerTest']['test_sections']['apply_config']['print']['value'])

        # device name: ixia, device alias: tgen
        trigger_datafile_8 = """
            TriggerTest:
                source:
                    pkg: fruit
                    class: banana
                devices: ['%{testbed.devices.tgen.alias}']
        """
        loaded_8 = loader.load(trigger_datafile_8)

        # device name: ixia, device alias: tgen
        trigger_datafile_9 = """
            TriggerTest:
                source:
                    pkg: fruit
                    class: banana
                devices: ['%{testbed.devices.ixia.alias}']

        """
        loaded_9 = loader.load(trigger_datafile_9)
        self.assertEqual(loaded_8['TriggerTest']['devices'],loaded_9['TriggerTest']['devices'])

        # topology device ixia, device interface:11/5, device.alias: tgen, interface.alias: IXIA_11_05-HUB1
        trigger_datafile_10 = """
            TriggerTest:
                source:
                    pkg: fruit
                    class: banana
                devices: ['unut']
                test_sections:
                    apply_config:
                        print:
                            value: "%{testbed.topology.ixia.interfaces.IXIA_11_05-HUB1.custom.hardware.portcard}"
        """
        loaded_10 = loader.load(trigger_datafile_10)

        # topology device ixia, device interface:11/5, device.alias: tgen, interface.alias: IXIA_11_05-HUB1
        trigger_datafile_11 = """
            TriggerTest:
                source:
                    pkg: fruit
                    class: banana
                devices: ['unut']
                test_sections:
                    apply_config:
                        print:
                            value: "%{testbed.topology.tgen.interfaces.11/5.custom.hardware.portcard}"
        """
        loaded_11 = loader.load(trigger_datafile_11)
        self.assertEqual(loaded_10['TriggerTest']['test_sections']['apply_config']['print']['value'],
                        loaded_11['TriggerTest']['test_sections']['apply_config']['print']['value'])

    def test_markup_processor_not_same_devices_in_testbed_device_and_topology(self):
        """ Tests to see loader module functions properly when the testbed has no topology
            or has topology but not with the same number of devices
        """
        # testbed that has no topology whatsoever
        with open(os.path.join(self.curr_dir, "script/testbed2.yaml")) as f:
            testbed_yaml = Loader().load(f.read())
        testbed_obj = Testbed(raw_config=testbed_yaml)
        loader = TriggerdatafileLoader(testbed=testbed_obj)

        trigger_datafile_1 = """
            TriggerTest:
                source:
                    pkg: fruit
                    class: banana
                devices: ["%{testbed.devices.P2.alias}"]
        """
        loaded_1 = loader.load(trigger_datafile_1)
        self.assertEqual(['P2'], loaded_1['TriggerTest']['devices'])

        # testbed with 2 devices but topology has 1 device
        with open(os.path.join(self.curr_dir, "script/testbed3.yaml")) as f:
            testbed_yaml = Loader().load(f.read())
        testbed_obj = Testbed(raw_config=testbed_yaml)
        loader = TriggerdatafileLoader(testbed=testbed_obj)

        trigger_datafile_2 = """
            TriggerTest:
                source:
                    pkg: fruit
                    class: banana
                devices: ["%{testbed.devices.P1.alias}"]
        """
        loaded_2 = loader.load(trigger_datafile_2)
        self.assertEqual(['unut'], loaded_2['TriggerTest']['devices'])

        trigger_datafile_3 = """
            TriggerTest:
                source:
                    pkg: fruit
                    class: banana
                devices: ['unut']
                test_sections:
                    apply_config:
                        print:
                            value: "%{testbed.topology.unut.interfaces.pe1-p1-1.type}"
        """
        loaded_3 = loader.load(trigger_datafile_3)
        self.assertEqual('ethernet', loaded_3['TriggerTest']['test_sections']['apply_config']['print']['value'])

    def test_topology_original_name_insertion(self):
        """ Tests that the testbed object is loadable using
            markup processor in other
        """

        # load testbed object from yaml
        with open(os.path.join(self.curr_dir, "script/testbed1.yaml")) as f:
            testbed_yaml = Loader().load(f.read())
        testbed_obj = Testbed(raw_config=testbed_yaml)
        loader = TriggerdatafileLoader(testbed=testbed_obj)

        # device: PE1, topology interface: GigabitEthernet2
        trigger_datafile = """
            TriggerTest:
                source:
                    pkg: fruit
                    class: banana
                devices: ['unut']
                test_sections:
                    test1: "%{testbed.topology.uut._name}"
                    test2: "%{testbed.topology.PE1.interfaces.pe1-p1-1._name}"
                    test3: "%{testbed.topology.links.P2_link._name}"
                    test4: "%{testbed.topology.links.p2_link_alias._name}"
        """
        loaded = loader.load(trigger_datafile)
        self.assertEqual('PE1', loaded['TriggerTest']['test_sections']['test1'])
        self.assertEqual('GigabitEthernet2', loaded['TriggerTest']['test_sections']['test2'])
        self.assertEqual('P2_link', loaded['TriggerTest']['test_sections']['test3'])
        self.assertEqual('P2_link', loaded['TriggerTest']['test_sections']['test4'])

    def test_load_datafile_with_markup_in_testbed(self):
        """ Tests that we can load a datafile if theres markup inside
        the testbed file """
        # load testbed object from yaml
        with open(os.path.join(self.curr_dir, "script/testbed_with_markup.yaml")) as f:
            testbed_obj = GenieTbLoader(f.read())

        loader = TriggerdatafileLoader(testbed=testbed_obj)

        # device: PE1, topology interface: GigabitEthernet2
        trigger_datafile = """
            TriggerTest:
                source:
                    pkg: fruit
                    class: banana
                devices: ['uut']
                test_sections:
                    test1: test
        """

        # This will raise exception if the testbed markups aren't resolved
        # before attempting trigger_datafile loading
        loader.load(trigger_datafile)


if __name__ == '__main__':
    unittest.main()
