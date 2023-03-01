
import unittest
import collections.abc
import contextlib
import warnings

from genie.conf import Genie
from genie.conf.base import Testbed
from genie.conf.base.config import CliConfig

class TestCase(unittest.TestCase):

    def setUp(self):
        Genie.testbed = Testbed()

    def tearDown(self):
        Genie.testbed = None

    def assertMultiLineDictEqual(self, output, expected_output):
        outputs = {}
        for key, value in output.items():
            if isinstance(value, CliConfig):
                outputs[key] = str(value)
            elif isinstance(value, list):
                values = []
                for v in value:
                    values.append(str(v))
                outputs[key] = '\n'.join(values)
            else:
                outputs[key] = value
        if isinstance(outputs, collections.abc.Mapping):
            self.assertCountEqual(outputs.keys(), expected_output.keys())
            for key in sorted(outputs.keys()):
                output_list = sorted(outputs[key].splitlines())
                expected_list = sorted(expected_output[key].splitlines())
                self.assertEqual(output_list, expected_list,
                                          msg='{} value'.format(key))
        else:
            output_list = sorted(output.splitlines())
            expected_list = sorted(expected_output.splitlines())
            self.assertEqual(output_list, expected_list)

    @contextlib.contextmanager
    def assertNoWarnings(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('error')
            yield
            self.assertSequenceEqual(w, (), 'list of warnings')


