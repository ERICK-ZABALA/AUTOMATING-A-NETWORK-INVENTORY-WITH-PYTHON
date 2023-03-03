__version__ = '23.2'

import pkgutil
__path__ = pkgutil.extend_path(__path__, __name__)

import logging
log = logging.getLogger(__name__)

from unicon.eal.expect import Spawn
from unicon.core.pluginmanager import PluginManager
__plugin_manager__ = PluginManager()

# Unicon Connection Factory class
from unicon.bases.connection import Connection

__plugin_manager__.discover_builtin_plugins()
__plugin_manager__.discover_external_plugins()

# import the pyATS topology adapter 
try:
    __import__('pyats.topology')
except ImportError:
    # Do not complain, this may be a non pyATS setup
    pass
else:
    from unicon.adapters.topology import Unicon, XRUTConnect

