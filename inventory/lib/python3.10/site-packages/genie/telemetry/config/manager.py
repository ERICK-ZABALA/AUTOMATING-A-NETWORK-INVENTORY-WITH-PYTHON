import logging
from io import TextIOBase

# argparse
from pyats.utils import parser as argparse
from pyats.utils.dicts import recursive_update
from pyats.datastructures import AttrDict, classproperty

from .loader import ConfigLoader
from .plugins import PluginManager

# declare module as infra
__genietelemetry_infra__ = True

# module logger
logger = logging.getLogger(__name__)

class Configuration(object):
    '''Configuration

    genie telemetry configuration object. Core concept that allows genie
    telemetry to load configuration for user plugins, and as well allows device
    connections to be swapped with different port.

    '''

    def __init__(self, plugins = None):
        self._plugins = AttrDict()
        self.connections = AttrDict()
        self._loader = ConfigLoader()
        self.plugins = (plugins or PluginManager)()

    def load_plugin_classess(self, config = None):

        if isinstance(config, (dict, str, TextIOBase)):
            self.update(self._loader.load(config))

        self.plugins.load(self._plugins)
        return self.plugins.get_plugin_classes()

    def load(self, config = None, devices = {}):
        logger.info('Loading genie.telemetry Configuration')
        # load configuration provided via input argument
        # -----------------------------
        if isinstance(config, (dict, str, TextIOBase)):
            self.update(self._loader.load(config))

        logger.info('Loading genie.telemetry Plugins')
        self.plugins.load(self._plugins)

        logger.info('Initializing genie.telemetry Plugins for Testbed Devices')
        for name, device in devices.items():
            self.plugins.init_plugins(name, device)

    def update(self, config):
        recursive_update(self._plugins, config.get('plugins', {}))
        recursive_update(self.connections, config.get('connections', {}))

    @classproperty
    def parser(cls):
        parser = argparse.ArgsPropagationParser(add_help = False)
        parser.title = 'Configuration'

        # timeout
        # -------
        parser.add_argument('-configuration',
                            type = argparse.FileType('r'),
                            metavar = 'FILE',
                            help = 'configuration yaml file for plugins and'
                                   ' settings')
        return parser

    def parse_args(self, argv):
        '''parse_args

        parse arguments if available, store results to self.args. This follows
        the easypy argument propagation scheme, where any unknown arguments to
        this plugin is then stored back into sys.argv and untouched.

        Does nothing if a plugin doesn't come with a built-in parser.
        '''

        # do nothing when there's no parser
        if not self.parser:
            return

        # avoid parsing unknowns
        self.args, _ = self.parser.parse_known_args(argv)