import os
import sys
import unittest
import pkg_resources
from unittest.mock import patch
from genie.ops.utils import ExtendOps
from pyats import configuration as cfg
from genie.conf.base.device import Device
from pkg_resources import load_entry_point
from pkg_resources import iter_entry_points
from genie.ops.utils import _load_ops_json, get_ops, get_ops_features
from genie.tests.ops.dummy_ops_pkg.dummy.nxos.dummy import Dummy as NxosDummy
from genie.tests.ops.dummy_ops_pkg.dummy.iosxe.dummy import Dummy as IosxeDummy
import genie.ops.utils

PYATS_EXT_OPS = 'pyats.libs.external.ops'
OPS_ENTRYPOINT = 'genie.libs.ops'


class TestExtendOps(unittest.TestCase):

    def setUp(self):
        sys.path.append(os.path.dirname(__file__))

    def test_extend_ops(self):
        ext = ExtendOps('dummy_ops_pkg')
        ext.extend()

        self.assertEqual(len(ext.output), 2)
        ext.output.pop('tokens', None)
        self.assertDictEqual({
            'dummy': {
                'iosxe': {
                    'class_name': 'Dummy',
                    'doc': 'Dummy Routing Ops Object',
                    'module_name': 'dummy.dummy',
                    'package': 'dummy_ops_pkg',
                    'uid': 'dummy',
                    'url': 'https://wwwin-github.cisco.com/pyATS/genielibs.cisco/tree/dev/dummy/iosxe/dummy.py#L4'
                },
                'nxos': {
                    'class_name': 'Dummy',
                    'doc': 'Dummy Routing Ops Object',
                    'module_name': 'dummy.dummy',
                    'package': 'dummy_ops_pkg',
                    'uid': 'dummy',
                    'url': 'https://wwwin-github.cisco.com/pyATS/genielibs.cisco/tree/dev/dummy/nxos/dummy.py#L4'
                }
            }},
            ext.output)

    def test_extend_ops_module_error(self):
        with self.assertRaises(ModuleNotFoundError):
            ExtendOps('dummy_ops_error')


class TestExtendedOpsUtils(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.device = Device(name='aDevice', os='generic',
                        custom={'abstraction': {'order':['os']}})

    def setUp(self):
        # Reset values between tests
        cfg[PYATS_EXT_OPS] = ""
        os.environ['PYATS_LIBS_EXTERNAL_OPS'] = ""
        genie.ops.utils.ops_data = None

    def test_extended_load_ops_json(self):
        cfg[PYATS_EXT_OPS] = "genie.tests.ops.dummy_ops_pkg"
        ops_json = _load_ops_json()
        dummy_dict = {
            'iosxe': {
                'module_name': 'dummy.dummy',
                'doc': 'Dummy Routing Ops Object',
                'package': 'genie.tests.ops.dummy_ops_pkg',
                'uid': 'dummy',
                'class_name': 'Dummy',
                'url': 'https://wwwin-github.cisco.com/pyATS/genielibs.cisco/tree/dev/dummy/iosxe/dummy.py#L4'
            },
            'nxos': {
                'module_name': 'dummy.dummy',
                'doc': 'Dummy Routing Ops Object',
                'package': 'genie.tests.ops.dummy_ops_pkg',
                'uid': 'dummy',
                'class_name': 'Dummy',
                'url': 'https://wwwin-github.cisco.com/pyATS/genielibs.cisco/tree/dev/dummy/nxos/dummy.py#L4'
            }
        }
        self.assertEqual(dummy_dict, ops_json['dummy'])

    def test_extended_get_ops(self):
        cfg[PYATS_EXT_OPS] = "genie.tests.ops.dummy_ops_pkg"
        self.device.os = 'iosxe'
        ops = get_ops(feature="dummy", device=self.device)
        self.assertEqual('genie.tests.ops.dummy_ops_pkg.dummy.iosxe.dummy', ops.__module__)
        self.assertEqual('Dummy', ops.__name__)

    def test_extended_get_ops_features(self):
        # Get the default Ops and then reset the ops_data so it will regenerate
        default_ops_features = get_ops_features()
        genie.ops.utils.ops_data = None
        # Now set the extended pkg and get the updated ops_data
        cfg[PYATS_EXT_OPS] = "genie.tests.ops.dummy_ops_pkg"
        extended_ops_features = get_ops_features()
        default_ops_features.append("dummy")
        self.assertEqual(set(extended_ops_features),
                         set(default_ops_features))

    def test_learn_ops_from_external_iosxe(self):

        # Test that Dummy Ops can't be found and raises an error
        with self.assertRaises(LookupError):
            self.device.learn("dummy")

        # Clear the loaded Ops data so genie.ops.utils._load_ops_json()
        # will regenerate the Ops metadata
        genie.ops.utils.ops_data = None

        # Test that Dummy Ops can now be found lookup works correctly
        cfg[PYATS_EXT_OPS] = "genie.tests.ops.dummy_ops_pkg"
        self.device.os = 'iosxe'
        with patch.object(IosxeDummy, 'learn') as cm:
            self.device.learn("dummy")
        cm.assert_called_once()


    def test_learn_ops_from_external_nxos(self):

        # Test that Dummy Ops can't be found and raises an error
        with self.assertRaises(LookupError):
            self.device.learn("dummy")

        # Clear the loaded Ops data so genie.ops.utils._load_ops_json()
        # will regenerate the Ops metadata
        genie.ops.utils.ops_data = None

        # Test that Dummy Ops can be found and abstract lookup works correctly
        os.environ['PYATS_LIBS_EXTERNAL_OPS'] = "genie.tests.ops.dummy_ops_pkg"
        self.device.os = 'nxos'
        with patch.object(NxosDummy, 'learn') as cm:
            self.device.learn("dummy")
        cm.assert_called_once()


    def test_learn_ops_from_genielibscisco(self):
        try:
            import genie.libs.cisco.ops
            _dist = pkg_resources.get_distribution("genie.libs.cisco")
            ep = load_entry_point(dist=_dist, group=OPS_ENTRYPOINT, name='cisco')
        except ImportError:
            raise unittest.SkipTest(
                "Failed to import genie.libs.cisco.ops. Skipping test as it requires the ops entry point")

        # Test that the genielibs.cisco entry point is correctly declared
        self.assertEqual(ep.__name__, "genie.libs.cisco.ops")

        # Now modify the entry point to reference the dummy ops package
        for entry in iter_entry_points(group=OPS_ENTRYPOINT):
            if entry.name == "cisco":
                entry.module_name = "genie.tests.ops.dummy_ops_pkg"

        # Test that Dummy Ops can be found and abstract lookup works correctly
        self.device.os = 'iosxe'
        with patch.object(IosxeDummy, 'learn') as cm:
            self.device.learn("dummy")
        cm.assert_called_once()

        self.device.os = 'nxos'
        with patch.object(NxosDummy, 'learn') as cm:
            self.device.learn("dummy")
        cm.assert_called_once()


if __name__ == '__main__':
    unittest.main()
