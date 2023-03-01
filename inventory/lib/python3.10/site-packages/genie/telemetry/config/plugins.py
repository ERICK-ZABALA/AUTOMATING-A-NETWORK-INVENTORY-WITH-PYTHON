import sys
import logging
from copy import copy
from operator import attrgetter
from genie.abstract.magic import Lookup

from genie.telemetry.utils import get_plugin_name

# declare module as infra
__genietelemetry_infra__ = True

# module logger
logger = logging.getLogger(__name__)

class PluginManager(object):
    '''Plugin Manager class

    Instanciates, configures, manages and runs all genie telemetry plugins. This
    is the main driver behind the genie telemetry plugin system.

    In any given process, there is only a single instance of PluginManager.
    '''

    def __init__(self):

        # list of plugin class instances
        self._plugins = dict()

        # dictionary of plugin-device abstraction cache pair
        self._cache = dict()

    def has_device_plugins(self, device):
        '''has_device_plugins

        checks whether device has any plugins
        '''
        return any(device in c for c in self._cache.values())

    def get_device_plugins(self, device):
        '''get_device_plugins

        retrieve plugins associated with given device
        '''
        device = getattr(device , 'name', device)

        plugins = dict()
        for name, cached in self._cache.items():
            if device in cached:
                plugins[name] = cached.get(device).get('instance', None)

        return plugins

    def set_device_plugin_status(self, device, plugin, status):
        '''set_device_plugin_status

        set specific plugin status of given device
        '''
        for plugin_name, plugin_cache in self._plugins.items():
            # plugin name doesn't match, skip
            if plugin != plugin_cache.get('plugin_label'):
                continue
            # the device isn't cached for the plugin, skip
            device_cache = self._cache.get(plugin_name, {}).get(device, {})
            if not device_cache:
                continue
            status_label = str(status).upper()
            self._cache[plugin_name][device]['status'] = status
            self._cache[plugin_name][device]['status_label'] = status_label

    def get_device_plugins_status(self, device, label=False):
        '''get_device_plugins_status

        get all plugin status of given device

        Argument:
            - label: Flag, if true, return status_label instead of status
        '''
        device = getattr(device , 'name', device)
        statuses = dict()
        for devices in self._cache.values():
            dev = devices.get(device, {})
            # the device isn't cached, skip
            if not dev:
                continue
            plugin = dev.get('instance', None)
            if label:
                status = dev.get('status_label', 'STATUS NOT AVAILABLE')
            else:
                status = dev.get('status', None)

            statuses[get_plugin_name(plugin)] = status

        return statuses

    def init_plugins(self, device_name, device):
        '''init_plugins

        initializing plugins for device
        '''
        logger.info('Initializing plugins for %s' % device_name)

        for plugin_name, plugin_cache in self._plugins.items():

            devices = plugin_cache.get('devices', [])
            if devices and device_name not in devices:
                logger.debug('Skipping plugin %s for device %s' % (plugin_name,
                                                                   device_name))
                continue

            self._cache[plugin_name].setdefault(device_name, {})

            argv = copy(sys.argv[1:])
            plugin = self.load_plugin(device, **plugin_cache)
            self._cache[plugin_name][device_name]['instance'] = plugin

            # Add configuration YAML plugin arguments to argv for parsing
            for key, value in plugin_cache['plugin_arguments'].items():
                # if key already exists in argv (provided to easypy as --key)
                # then argv takes priority over YAML value
                if key not in str(argv):
                    argv.extend(('--{key}'.format(key=key), str(value)))

            # parse plugin arguments
            # ----------------------
            # (saves arguments to plugin.args)
            plugin.parse_args(argv)
            self._cache[plugin_name][device_name]['args'] = plugin.args

            plugin_cache.setdefault('plugin_label', get_plugin_name(plugin))

    def get_plugin_classes(self):

        plugins = []
        for plugin_name, plugin_cache in self._plugins.items():
            name = plugin_cache.get('name', plugin_name)
            module = plugin_cache.get('module', None)
            if not name or not module:
                continue
            class_name = '{}.Plugin'.format(name)
            try:
                plugin_cls = self.get_plugin_cls(module, module, class_name)
            except Exception:
                continue
            plugins.append(plugin_cls)

        return plugins

    def get_plugin_cls(self, plugin_module, base_module, class_name):

        if plugin_module == base_module:
            modules = [plugin_module]
        else:
            modules = [plugin_module, base_module]

        for module in modules:
            for name in (class_name, 'Plugin'):
                try:
                    plugin_cls = attrgetter(name)(module)
                except AttributeError:
                    continue
                return plugin_cls

        raise AttributeError('%s Plugin class is not defined' % class_name)

    def load_plugin_cls(self, device, name=None, module=None):
        '''load_plugin_cls

        return loaded plugin abstraction class
        '''

        device_name = getattr(device, 'name', device)

        if module:
            if not getattr(device, 'os', None):
                raise AttributeError('%s attribute [os] is not defined'
                                                                % device_name)
            if not getattr(device, 'custom', None):
                raise AttributeError('%s custom abstraction is missing'
                                                                % device_name)
            try:
                plugin_module = Lookup.from_device(device,
                                                   packages={ name: module })
            except Exception:
                logger.error('failed to load abstration on device {} for plugin'
                             ' {}'.format(device_name, name))
                logger.error('fallback to load as standard plugin')
                plugin_module = module
        else:
            plugin_module = module

        class_name = '{}.Plugin'.format(name)
        plugin_cls = self.get_plugin_cls(plugin_module, module, class_name)

        # caching the plugin cls returned from abstraction magic
        self._cache[name][device_name]['cls'] = plugin_cls

        return plugin_cls


    def load_plugin(self, device, name=None, module=None, kwargs={}, **kw):
        '''load_plugin

        return loaded plugin
        '''
        logger.info(' - loading plugin %s' % name)

        plugin_kwargs = dict(**kwargs)

        plugin_cls = self.load_plugin_cls(device, name=name, module=module)

        return plugin_cls(**plugin_kwargs)


    def load(self, data):
        '''loads plugins from dictionary data

        this api loads plugins defined in a specific dictionary format (same as
        that defined in load_from_yaml). It does the heavy-lifting of actual
        plugin module loading and instanciatation.

        Arguments
        ---------
            data (dict): dictionary data format, same as yaml schema

        Example
        -------
            PluginManater().load({'KeepAlive': {
                                         'enabled': True,
                                         'module': 'genietelemetry_libs.plugins',
                                         'interval': 60})

        Returns
        -------
            list of discovered and loaded plugins
        '''

        # sort plugin by order into list
        plugins = sorted(data.items())

        # loop over plugin configs and init interval dictionary
        for name, plugin in plugins:
            # Do we want to execute this plugins ?
            # If not enable, do not execute it
            if not plugin.get('enabled', False):
                logger.debug('Plugin %s is not enabled' % name)
                continue

            self._plugins[name] = plugin
            self._cache.setdefault(name, {})
