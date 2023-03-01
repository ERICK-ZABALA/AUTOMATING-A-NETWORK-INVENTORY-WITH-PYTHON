import unittest
from unittest.mock import patch
from genie.harness.utils import connect_device
from genie.conf import Genie
from genie.conf.base.device import Device
from genie.conf.base.testbed import Testbed

class PoolSizeException(Exception):
    pass

class TestUtils(unittest.TestCase):

    def setUp(self):
        config = {'name': 'testDevice2',
                  'os': 'iosxe',
                  'passwords': {'enable': 'lab',
                                'line': 'lab',
                                'tacacs': 'CSCO12345^'},
                  'tacacs': {'login_prompt': 'login:',
                             'password_prompt': 'Password:',
                             'username': 'admin'},
                  'connections': {'cli': {'protocol': 'telnet',
                                        'ip': '1.1.1.1',
                                        'port': 2001, }},
                 'custom': {'abstraction': {'order': ['os']}
                 }}
        self.testbed = Genie.testbed = Testbed()
        self.device = Device(testbed = self.testbed, **config)

    def mock_connect(self, via='', init_exec_commands='', alias='', prompt_recovery='', pool_size=None):
        if pool_size:
            raise PoolSizeException
        else:
            pass

    @patch("pyats.connections.manager.ConnectionManager.connect", mock_connect)
    def test_device_connect(self):
        self.device.mapping = {'cli': 'cli'}
        connect_device(self.device)

    @patch("pyats.connections.manager.ConnectionManager.connect", mock_connect)
    def test_device_connect_with_pool_size(self):
        self.device.mapping = {'cli': 'cli'}
        with self.assertRaises(PoolSizeException):
            connect_device(self.device, pool_size=1)

if __name__ == '__main__':
    unittest.main()
