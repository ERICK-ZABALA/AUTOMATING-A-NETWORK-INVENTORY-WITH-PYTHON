#!/bin/env python
""" Unit tests for data mapping """

import unittest
import pathlib
import os

from genie.harness.script import TestScript
from genie.testbed import load

class TestDataMapping(unittest.TestCase):
    def test_data_mapping(self):
        testbed = load(
            os.path.join(pathlib.Path(__file__).parent.absolute(), 'script/testbed_map.yaml')
        )
        data_mapping = """devices:
  nx-osv-1:
    label: hello
    context: cli
    mapping:
      cli: a
  csr1000v-1:
    context: cli
    mapping:
      cli: a
topology:
  csr1000v-1:
    interfaces:
      int1:
        label: orange
  links:
    link1:
      label: blue
"""
        link_dict = {i.alias: i for i in testbed.links}
        self.assertNotIn('hello', testbed.devices)
        self.assertNotIn('blue', link_dict)
        self.assertEqual(testbed.devices['csr1000v-1'].interfaces['int1'].alias, 'superint')
        tmp = 'test_datafile.yaml'
        with open(tmp, 'w') as file:
          file.write(data_mapping)
        testscript = TestScript(module=unittest)
        testbed = testscript.organize_testbed(testbed, tmp, None)
        self.assertIn('hello', testbed.devices)
        link_dict = {i.alias: i for i in testbed.links}
        self.assertIn('blue', link_dict)
        self.assertEqual(testbed.devices['csr1000v-1'].interfaces['int1'].alias, 'orange')
        if os.path.isfile(tmp):
          os.remove(tmp)

if __name__ == '__main__':
    unittest.main()
