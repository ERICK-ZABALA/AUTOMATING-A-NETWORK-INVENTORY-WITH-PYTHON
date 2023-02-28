from inspect import isclass
from importlib import import_module
from unicon.settings import DEFAULT_PLUGIN_LIST
from unicon.statemachine import StateMachine
from unicon.bases import BaseConnection

class Plugin(object):

    def __init__(self,
                 type,
                 state_machine,
                 connection_class,
                 services=[],
                 base_type='generic',
                 name=None):

        self.type = type
        self.state_machine =  state_machine
        self.connection_class = connection_class
        self.services = services
        self.base_type = base_type
        self.name = name
        self.validate_plugin()

    def validate_plugin(self):

        if self.type is None:
            Exception('Invalid type')

        # Check if already existing type

        if isclass(self.state_machine) and issubclass(self.state_machine, StateMachine):
            self.state_machine = self.state_machine()
        elif not isinstance(self.state_machine, StateMachine):
            raise Exception('Invalid State_machine ')

        if not isclass(self.connection_class) or \
                not issubclass(self.connection_class, BaseConnection):
            raise Exception('Invalid Connection class')


class UniconPluginManager(object):

    def __init__(self):

        self._plugin_list = dict()
        self._plugin_hierarchy = dict()

    def register_plugin(self, *args, **kwargs):

        if kwargs['type'] in self._plugin_list:
            raise Exception('Already registered')
        plugin_inst = Plugin(*args, **kwargs)
        self._plugin_list[kwargs['type']] = plugin_inst

    def discover_plugin(self):

        for plugin_name in DEFAULT_PLUGIN_LIST:
            #__import__(name='unicon.%s.setup' % plugin_name)
            import_module(name='unicon.%s.load_plugin' % plugin_name)
            #import_module('setup', package='unicon.%s' % plugin_name)

    def get_plugin(self, plugin_name):

        if plugin_name in self._plugin_list:
            return self._plugin_list[plugin_name]


def plugin(type,
           state_machine,
           connection_class,
           services=[],
           base_type='generic',
           name=None
           ):

    plugin_manager.register_plugin(type=type, state_machine=state_machine,
                                   connection_class=connection_class,
                                   services=services,base_type=base_type,
                                   name=name)


plugin_manager = UniconPluginManager()


