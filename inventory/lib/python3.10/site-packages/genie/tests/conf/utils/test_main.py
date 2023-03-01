#!/usr/bin/env python

# Import unittest module
import os
import stat
import unittest
import subprocess

from pyats.topology import loader
from pyats.utils.yaml.exceptions import LoadError

from genie.conf.main import Genie
from genie.conf.base.testbed import Testbed

class test_Genie(unittest.TestCase):

    def tearDown(self):
        Genie.testbed = None

    def test_init_full_path(self):
        self.assertEqual(Genie.testbed, None)

        test_path = os.path.dirname(os.path.abspath(__file__))
        pyATS_tb = os.path.join(test_path, 'tb.yaml')

        Genie.init(testbed=pyATS_tb)
        self.assertTrue(isinstance(Genie.testbed, Testbed))

    def test_init_testbed_file_not_found(self):
        self.assertEqual(Genie.testbed, None)

        pyATS_tb = os.path.join('/wrong/tb.yaml')

        with self.assertRaises(LoadError):
            Genie.init(testbed=pyATS_tb)

    def test_init_testbed_wrong_arg(self):
        self.assertEqual(Genie.testbed, None)

        pyATS_tb = os.path.join('illegalArg')

        with self.assertRaises(LoadError):
            Genie.init(testbed=pyATS_tb)

    def test_init_testbed_not_accessible(self):
        self.assertEqual(Genie.testbed, None)

        test_path = os.path.dirname(os.path.abspath(__file__))
        pyATS_tb = os.path.join(test_path, 'tb.yaml')

        # get current access permission state
        current_rwxmode = oct(os.stat(pyATS_tb).st_mode)[-3:]
        subprocess.call(["chmod", "-r", pyATS_tb])
        with self.assertRaises(LoadError):
            Genie.init(testbed=pyATS_tb)
        # reset access permission state
        subprocess.call(["chmod", current_rwxmode, pyATS_tb])

    def test_init_testbed_object(self):
        test_path = os.path.dirname(os.path.abspath(__file__))
        pyATS_tb = loader.load(os.path.join(test_path, 'tb.yaml'))
        Genie.init(testbed=pyATS_tb)
        self.assertTrue(isinstance(Genie.testbed, Testbed))

    def test_init_wrong_testbed_object(self):

        class wrongTestbed(object):
            pass
        testbed = wrongTestbed()

        with self.assertRaises(LoadError):
            Genie.init(testbed=testbed)

    def test_init_from_dict(self):
        tb_dict = {
            'devices': {
                'PE1': {
                    'type': 'router',
                    'connections': {
                        'vty': {
                            'ip': '111.111.111.111',
                            'port': '9999',
                            'protocol': 'telnet',
                            'password': 'cisco',
                            'username': 'cisco',
                            'os': 'iosxe'
                        }
                    }
                }
            }
        }

        tb = Genie.init(testbed=tb_dict)
        self.assertTrue(isinstance(tb, Testbed))
        self.assertEqual(tb.devices['PE1'].custom.abstraction['order'], ['os', 'platform', 'model'])

    def test_init_from_quick_dict(self):
        tb_dict = {
            "devices":{
                "PE1":{
                    "ip":"172.25.192.104",
                    "port": 17005,
                    "protocol": "telnet",
                    "username": "admin",
                    "password": "cisco",
                    "os": "iosxe",
                }
            }
        }

        tb = Genie.init(testbed=tb_dict)
        self.assertTrue(isinstance(tb, Testbed))
        self.assertEqual(tb.devices['PE1'].custom.abstraction['order'], ['os', 'platform', 'model'])


if __name__ == '__main__':
    unittest.main()
