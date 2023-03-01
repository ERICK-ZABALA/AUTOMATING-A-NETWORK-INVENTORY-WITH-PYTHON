import unittest
from unittest.mock import MagicMock

from genie.conf.base.config import Config, CliConfig, YangConfig, RestConfig


class test_config(unittest.TestCase):

    def setUp(self):
        self.device = MagicMock()

    def test_init_config(self):
        config = Config(self.device)
        self.assertEqual(config.device, self.device)
        self.assertEqual(config.unconfig, False)
        self.assertEqual(config.fkwargs, {})

    def test_two_configs(self):

        config = Config(self.device)
        config2 = Config(self.device, unconfig=True, extra_args=5)
        self.assertEqual(config2.fkwargs, {'extra_args': 5})
        self.assertEqual(config2.unconfig, True)
        self.assertFalse(config == config2)

        class x:
            pass
        f = x()
        self.assertFalse(config2 == 'str')
        config2 == 'str'
        config2 == 5
        config2 == f
        config2 == 'str'
        'str' == config2

    def test_init_cliConfig(self):
        cConfig = CliConfig(device=self.device, cli_config='ab')
        self.assertEqual(self.device, cConfig.device)
        self.assertEqual(cConfig.unconfig, False)
        self.assertEqual(cConfig.cli_config, 'ab')
        cConfig.apply()
        self.assertEqual(str(cConfig), 'ab')

    def test_init_Yangconfig(self):
        yConfig = YangConfig(device=self.device, ydk_obj='test', ncp='ncp',
                             crud_service='crud')

        self.assertEqual(self.device, yConfig.device)
        self.assertEqual(yConfig.unconfig, False)
        self.assertEqual(yConfig.ydk_obj, 'test')
        self.assertEqual(yConfig.ncp, 'ncp')
        self.assertEqual(yConfig.crud_service, 'crud')

    def test_init_RestConfig(self):
        rConfig = RestConfig(device=self.device, unconfig=False,
                         cli_payload='some output', dn='api/mo/sys.json',
                         partition='nx-api rest')

        self.assertEqual(self.device, rConfig.device)
        self.assertEqual(rConfig.unconfig, False)
        self.assertEqual(rConfig.cli_payload, 'some output')
        self.assertEqual(rConfig.dn, 'api/mo/sys.json')
        self.assertEqual(rConfig._partition, 'nx-api rest')

        # check print
        self.assertEqual(str(rConfig), 'some output')
