"""
Module:
    kleenex

Authors:
    Myles Dear(mdear), CSG Test - Ottawa
    Siming Yuan (siyuan), CSG Test - Ottawa

Description:
    This module provides a framework that allows users to:

    - plug in own orchestrators that bring up dynamic device
      topologies on a variety of different backends.

    - plug in their own cleaners that prepare a physical device for testing.
"""



# metadata
__version__ = '23.2'
__author__ = 'Cisco Systems Inc.'
__contact__ = ['pyats-support@cisco.com', 'pyats-support-ext@cisco.com']
__copyright__ = 'Copyright (c) 2017-2019, Cisco Systems Inc.'

from .bringup_manager import request_bringup_worker_server_shutdown
from .bringup_manager import BringUp
from .utils import parse_cli_args
from .utils import testbed_config_contains_logical_routers
from .utils import ArgvQuotingParser
from .utils import help_suppress_kleenex
from .kleenex_main import main,KleenexMain
from .engine import KleenexEngine
from .bases import BaseCleaner
from .loader import KleenexFileLoader
from .bases import BringUpBase, BringUpWorkerBase
from .schema import allowed_virtual_device_types
from .exceptions import TopologyDidntComeUpInTime
from .exceptions import YamlConfigError
from .bringup_signals import SignalError
