import unittest
from unittest.mock import Mock, patch

multiprocessing = __import__('multiprocessing').get_context('fork')

from genie.harness._commons_internal import pcall_configure


manager = multiprocessing.Manager()


def mock_configure(*args, device=None, **kwargs):
    device.configure.calls.append(kwargs)


class MockCopyFile:

    def copyfile(*args, device=None, **kwargs):
        device.calls.append(kwargs)


class FileUtilsMock:

    def from_device(self, *args, **kwargs):
        return MockCopyFile()


class TestGenieHarnessConfigure(unittest.TestCase):

    @patch('genie.harness._commons_internal._configure_on_device', new=mock_configure)
    def test_pcall_configure_jinja2(self):
        from genie.harness._commons_internal import pcall_configure
        device1 = Mock()
        device1.configure = Mock()
        device1.configure.calls = manager.list()
        device2 = Mock()
        device2.configure = Mock()
        device2.configure.calls = manager.list()
        device_dict = {
            "R1": [
                {
                    "device": device1,
                    "sleep": 1,
                    "rendered": "config text 1",
                    "type": "jinja",
                    "config_file": "cfg.j2",
                    "verify": None
                },
                {
                    "device": device1,
                    "sleep": 0,
                    "rendered": "config text 2",
                    "type": "jinja",
                    "config_file": "cfg.j2",
                    "configure_arguments": {"bulk": True},
                    "verify": None
                }
            ],
            "R2": [
                {
                    "device": device2,
                    "sleep": 0,
                    "rendered": "config text 3",
                    "type": "jinja",
                    "config_file": "cfg.j2",
                    "verify": None
                }
            ]
        }
        pcall_configure(device_dict)
        self.assertEqual(list(device1.configure.calls), [
            {'rendered': 'config text 1', 'config_file': 'cfg.j2', 'type': 'jinja'},
            {'rendered': 'config text 2', 'config_file': 'cfg.j2', 'type': 'jinja', 'configure_arguments': {'bulk': True}}
        ])
        self.assertEqual(list(device2.configure.calls), [
            {'rendered': 'config text 3', 'config_file': 'cfg.j2', 'type': 'jinja'}
        ])

    @patch('genie.harness._commons_internal.FileUtils', new=FileUtilsMock)
    def test_pcall_configure_copyfile(self):
        device1 = Mock()
        device1.calls = manager.list()
        device2 = Mock()
        device2.calls = manager.list()
        device_dict = {
            'R1': [{
                'device': device1,
                'source': 'http://server/file1.txt',
                'destination': 'running-config',
                'invalid': [],
                'sleep': 1,
                'config_file': 'file.txt',
                'verify': None,
            }],
            'R2': [{
                'device': device2,
                'source': 'http://server/file2.txt',
                'destination': 'running-config',
                'invalid': [],
                'sleep': 1,
                'config_file': 'file.txt',
                'verify': None,
            }]
        }
        pcall_configure(device_dict)
        self.assertEqual(list(device1.calls), [{
            'config_file': 'file.txt',
            'destination': 'running-config',
            'invalid': [],
            'source': 'http://server/file1.txt'
        }])
        self.assertEqual(list(device2.calls), [{
            'config_file': 'file.txt',
            'destination': 'running-config',
            'invalid': [],
            'source': 'http://server/file2.txt'
        }])


if __name__ == "__main__":
    unittest.main()
