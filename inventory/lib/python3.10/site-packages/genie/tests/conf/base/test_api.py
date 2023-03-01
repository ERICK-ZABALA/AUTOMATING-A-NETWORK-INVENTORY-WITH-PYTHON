import os
import sys
import importlib
import unittest
import weakref
from copy import deepcopy
from unittest import mock

from genie.libs.clean import BaseStage
from genie.conf.base.device import Device
from genie.conf.base.api import ExtendApis, CleanAPI
from genie.tests.conf.base.mock_errored_api_data import data_loader
from genie.json.exceptions import ApiImportError

from pyats.aetest.steps import Steps


class TestApi(unittest.TestCase):

    def setUp(self):
        self.device = Device(name='aDevice', os='iosxe',
                             custom={'abstraction': {'order':['os']}})

    def test_api_success(self):
        api = self.device.api.get_api('shut_interface', self.device)
        self.assertEqual(callable(api), True)
        self.assertEqual(api.__name__, 'shut_interface')

    def test_api_exception(self):
        with self.assertRaises(AttributeError):
            self.device.api.get_api('DontExists', self.device)

    @mock.patch('genie.conf.base.api._load_function_json', return_value=data_loader())
    def test_api_recall_error(self, mock_data):

        with self.assertRaises(NameError):
            importlib.reload(genie.libs.sdk.apis)
            self.device.api.get_api('clear_interface_counters', self.device)


class TestExtendApi(unittest.TestCase):

    def setUp(self):
        sys.path.append(os.path.dirname(__file__))

    def test_extend_api(self):
        ext = ExtendApis('dummy_api')
        ext.extend()
        summary = ext.output['extend_info']

        self.assertEqual(len(summary), 2)
        self.assertIn("api name: 'dummy_iosxe', tokens ['iosxe'], "
                      "module name: utils",
                      summary)
        self.assertIn("api name: 'dummy_common', tokens ['com'], "
                      "module name: utils",
                      summary)

    def test_extend_api_module_error(self):
        ext = ExtendApis('dummy_api_error')
        with self.assertRaises(ApiImportError):
            ext.extend()


class TestCleanAPI(unittest.TestCase):

    def setUp(self):
        self.device = Device(name='aDevice', os='iosxe',
            custom={'abstraction': {'order': ['os']}})

    def test_attributes(self):
        self.assertIsInstance(self.device.api.clean, CleanAPI)
        self.assertEqual(self.device.api.clean.device, weakref.ref(self.device))
        self.assertTrue(isinstance(self.device.api.clean.history, dict))

    @mock.patch('genie.libs.clean.utils.load_clean_json')
    def test_retrieve_existing_stage(self, clean_json):
        clean_json.return_value = {
            "ExistsStage": {
                "iosxe": {
                      "package": "genie.libs.clean",
                      "module_name": "stages.stages",
                      "uid": "ExistsStage",
                }
            }
        }

        class ExistsStage(BaseStage):
            pass

        with mock.patch('genie.libs.clean.stages.stages.ExistsStage', ExistsStage, create=True):

            # Make sure the returned class is instantiated and its the expected class
            self.assertIsInstance(self.device.api.clean.ExistsStage, ExistsStage)
            self.assertEqual(self.device.api.clean.ExistsStage, ExistsStage())

            # Make sure the stage has mandatory parameters setup
            self.assertEqual(self.device.api.clean.ExistsStage.parameters['device'], self.device)
            self.assertIsInstance(self.device.api.clean.ExistsStage.parameters['steps'], Steps)

    @mock.patch('genie.libs.clean.utils.load_clean_json')
    def test_retrieve_non_existent_stage(self, clean_json):
        clean_json.return_value = {
            "DoesntExistStage": {
                "iosxe": {
                      "package": "genie.libs.clean",
                      "module_name": "stages.stages",
                      "uid": "DoesntExistStage",
                }
            }
        }

        with self.assertRaises(Exception) as cm:
            self.device.api.clean.DefinitelyDoesntExistStage

        self.assertIn(
            "The clean stage 'DefinitelyDoesntExistStage' does not exist in the json file",
            str(cm.exception)
        )

        with self.assertRaises(Exception) as cm:
            self.device.api.clean.DoesntExistStage

        self.assertIn(
            "The clean stage 'DoesntExistStage' does not exist under the following abstraction tokens",
            str(cm.exception)
        )

    @mock.patch('genie.libs.clean.utils.load_clean_json')
    def test_dir(self, clean_json):
        before = dir(self.device.api.clean)

        clean_json.return_value = {
            "ExistsStage": {
                "iosxe": {
                      "package": "genie.libs.clean",
                      "module_name": "stages.stages",
                      "uid": "ExistsStage",
                }
            },
            "SomeOtherOs": {
                "nxos": {
                      "package": "genie.libs.clean",
                      "module_name": "stages.stages",
                      "uid": "SomeOtherOs",
                }
            },
        }

        after = dir(self.device.api.clean)

        # nxos stages should not appear on an iosxe device
        self.assertEqual(self.device.os, 'iosxe')
        self.assertEqual(['ExistsStage'] + before, after)

    @mock.patch('genie.conf.base.api.CleanAPI.get_template_args')
    @mock.patch('genie.conf.base.api.CleanAPI.get_template')
    def test_call_clean(self, clean_template, clean_template_default_args):
        """
        Call clean without overriding anything from clean template
        """

        template_data = {"order": ["connect"], "connect": {"foo": "bar"}}
        clean_template.return_value = template_data
        clean_template_default_args.return_value = {}

        clean_json = []

        def capture_clean_json(self, device):
            clean_json.append(deepcopy(device.clean))

        with mock.patch("genie.libs.clean.PyatsDeviceClean.clean", new=capture_clean_json):
            self.device.api.clean()

        self.assertEqual(clean_json[-1], template_data)
        clean_json.clear()

        # test setting template_name to None
        new_data = {"order": ["connect"], "connect": {"foo1": "bar1"}}
        with mock.patch("genie.libs.clean.PyatsDeviceClean.clean", new=capture_clean_json):
            self.device.api.clean(template_name=None, template_override=new_data)

        self.assertEqual(clean_json[-1], new_data)
        clean_json.clear()

        # test unused stages removed
        new_data = {"order": ["connect2"], "connect": {}, "connect2": {}}
        with mock.patch("genie.libs.clean.PyatsDeviceClean.clean", new=capture_clean_json):
            self.device.api.clean(template_name=None, template_override=new_data)

        expected_data = {"order": ["connect2"], "connect2": {}}
        self.assertEqual(clean_json[-1], expected_data)
        clean_json.clear()

    @mock.patch('genie.conf.base.api.CleanAPI.get_template_args')
    @mock.patch('genie.conf.base.api.CleanAPI.get_template')
    def test_call_clean_sub_args(self, clean_template, clean_template_default_args):
        """
        Test substituting arguments into clean template
        """
        from genie.conf.base.api import OPTIONAL, REQUIRED

        # test 1: CLEANARG not provided raises TypeError
        template_data = {"order": ["connect"], "connect": {"foo": r"%CLEANARG{fooarg}"}}
        clean_template.return_value = template_data
        clean_template_default_args.return_value = {}

        clean_json = []

        def capture_clean_json(self, device):
            clean_json.append(deepcopy(device.clean))

        with mock.patch("genie.libs.clean.PyatsDeviceClean.clean", new=capture_clean_json):
            with self.assertRaises(TypeError) as cm:
                self.device.api.clean()

        self.assertIn(
            "Required clean argument 'fooarg' not provided",
            str(cm.exception)
        )

        # test 2: argument from default template args
        clean_template_default_args.return_value = {"fooarg": "fooval"}
        with mock.patch("genie.libs.clean.PyatsDeviceClean.clean", new=capture_clean_json):
            self.device.api.clean()

        expected_data = {"order": ["connect"], "connect": {"foo": "fooval"}}
        self.assertEqual(clean_json[-1], expected_data)
        clean_json.clear()

        # test 3: argument must come from user and isnt provided
        clean_template_default_args.return_value = {"fooarg": REQUIRED}
        with mock.patch("genie.libs.clean.PyatsDeviceClean.clean", new=capture_clean_json):
            with self.assertRaises(TypeError) as cm:
                self.device.api.clean()

        self.assertIn(
            "Some required clean arguments not provided",
            str(cm.exception)
        )

        # test 4: user provides the required arg
        with mock.patch("genie.libs.clean.PyatsDeviceClean.clean", new=capture_clean_json):
            self.device.api.clean(fooarg="user_value")

        expected_data = {"order": ["connect"], "connect": {"foo": "user_value"}}
        self.assertEqual(clean_json[-1], expected_data)
        clean_json.clear()

        # test 5: optional args which arent provided are removed from data
        clean_template_default_args.return_value = {"fooarg": OPTIONAL}
        with mock.patch("genie.libs.clean.PyatsDeviceClean.clean", new=capture_clean_json):
            self.device.api.clean()

        expected_data = {"order": ["connect"], "connect": {}}
        self.assertEqual(clean_json[-1], expected_data)
        clean_json.clear()

        # test 6: template override
        template_data = {"order": ["connect"], "connect": {"foo": r"%CLEANARG{fooarg}"}}
        clean_template.return_value = template_data
        clean_template_default_args.return_value = {}

        template_override = {"connect": {"bar": r"%CLEANARG{bararg}"}}
        with mock.patch("genie.libs.clean.PyatsDeviceClean.clean", new=capture_clean_json):
            self.device.api.clean(template_override=template_override, fooarg="foo2", bararg="bar2")

        expected_data = {"order": ["connect"], "connect": {"foo": "foo2", "bar": "bar2"}}
        self.assertEqual(clean_json[-1], expected_data)
        clean_json.clear()


if __name__ == '__main__':
    unittest.main()
