# python
import os
import sys
import time
import logging
import traceback
import multiprocessing
from datetime import datetime

from pyats.topology import loader
from pyats.utils.dicts import recursive_update

from genie.telemetry.config import (
    Configuration,
    PluginManager as BaseManager
)
from genie.telemetry.config.schema import testbed_schema
from genie.telemetry.manager import Manager
from genie.telemetry.status import CRITICAL
from genie.telemetry.utils import get_plugin_name

# declare module as infra
__genietelemetry_infra__ = True

logger = logging.getLogger(__name__)

class PluginManager(BaseManager):
    '''Plugin Manager class

    In any given process, there is only a single instance of PluginManager.
    '''

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # dictionary of interval-plugins pair
        self._plugin_interval = dict()

        # list of plugin intervals
        self._intervals = list()

    def load(self, data):

        super().load(data)

        # init plugin interval dictionary
        for name, plugin in self._plugins.items():
            interval = plugin.get('interval', 30)
            self._plugin_interval.setdefault(interval, [])
            if name not in self._plugin_interval[interval]:
                self._plugin_interval[interval].append(name)

        # init plugin interval dictionary
        self._intervals = sorted(self._plugin_interval.keys())

class TimedManager(Manager):

    def __init__(self,
                 testbed={},
                 testbed_file=None,
                 configuration={},
                 configuration_file=None,
                 **kwargs):

        if not testbed and not testbed_file:
            raise FileNotFoundError('Did you forget to provide a testbed file?')

        super().__init__(testbed or self.load_testbed(testbed_file),
                         configuration=(configuration or configuration_file),
                         plugins=PluginManager,
                         **kwargs)


    def load_testbed(self, testbed_file):

        if not testbed_file:
            raise FileNotFoundError('Did you forget to provide a testbed file?')

        elif not os.path.isfile(testbed_file):
            raise FileNotFoundError("The provided testbed_file '%s' does not "
                                    "exist." % testbed_file)

        elif not os.access(testbed_file, os.R_OK):
            raise PermissionError("Testbed file '%s' is not accessible"
                                  % testbed_file)

        loader.schema = testbed_schema
        return loader.load(os.path.abspath(testbed_file))


    def get_device_plugins(self, device, interval):

        plugin_runs = {}

        # get list of plugin to be executed at this interval
        for plugin_name in self.plugins._plugin_interval[interval]:
            device_plugin = self.plugins._cache[plugin_name].get(device.name,
                                                                 {})
            if not device_plugin:
                continue
            plugin = device_plugin.get('instance', None)
            if not plugin:
                continue
            plugin_runs[plugin_name] = plugin

        return plugin_runs

    def start(self):
        try:
            interval = 0
            while True:

                interval += 1
                time_now = datetime.utcnow().strftime("%b %d %H:%M:%S UTC %Y")
                self.run(time_now, interval)
                time.sleep(1)

        except SystemExit:
            logger.warning('System Exit detected...')
            logger.warning('Aborting run & cleaning up '
                           'as fast as possible...')

        except KeyboardInterrupt:
            # ctrl+c handle
            # -------------
            logger.warning('Ctrl+C keyboard interrupt detected...')
            logger.warning('Aborting run & cleaning up '
                           'as fast as possible...')

        except Exception as e:
            message= ''.join(traceback.format_exception(*sys.exc_info()))
            logger.error('exception occurred {}'.format(message.strip()))


    def run(self, tag, interval):
        '''run plugins

        Arguments
        ---------
            device (device): current executing device
            interval (integer): current execution interval

        '''

        for i in self.plugins._intervals:

            # skip if not it's turn
            if interval % i:
                continue

            super().run('{} ({})'.format(tag, i), i)


    def call_plugin(self, device, plugins):

        is_connected = self.is_connected(device.name, device)
        if not is_connected:            
            connection = self.connections.get(device.name, {})
            timeout = connection.pop('timeout', self.connection_timeout)
            logger.info('Lost Connection - Attempt to Recover Connection '
                        'with Device ({})'.format(device.name))
            # best effort, attempt to connect at least once.
            try:
                device.connect(timeout=timeout,
                               **connection)
            except Exception as e:
                connection_failed = ('Lost Connection, failed to '
                                     'recover. exception: ({})'.format(str(e)))
            else:
                connection_failed = 'Lost Connection, failed to recover'
                is_connected = self.is_connected(device.name, device)
                logger.info('Connection Re-Established for '
                            'Device ({})'.format(device.name))

        results = dict()
        for plugin in plugins:
            # skip plugin execution if device isn't connected
            if is_connected:
                result = super().call_plugin(device, [plugin])
            else:
                # bad connection
                result = dict()
                plugin_name = get_plugin_name(plugin)

                execution = result.setdefault(plugin_name,
                                              {}).setdefault(device.name,{})
                execution['status'] = CRITICAL
                execution['result'] = {
                                        datetime.utcnow().isoformat():
                                        connection_failed
                                      }

            recursive_update(results, result)

            if hasattr(self.instance, 'post_call_plugin'):
                self.instance.post_call_plugin(device, result)

        return results