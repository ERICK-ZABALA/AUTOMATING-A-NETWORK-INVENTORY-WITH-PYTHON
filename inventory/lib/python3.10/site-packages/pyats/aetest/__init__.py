'''
Module:
    aetest

Description:
    This module defines the base classes required to write testscripts. It's
    name is a direct carry over from Tcl-ATS's AEtest package.

    In short, this module is designed to offer a similar look-and-feel of its
    Tcl counterpart, whilst leveraging and building based on the advanced
    object-oriented capabilities of the Python Language.

    aetest can be broken down as follows:

        - Common Sections
        - Testcases

    For more detailed explanation and usages, refer to aetest documentation on
    pyATS home page: http://wwwin-pyats.cisco.com/
'''
# metadata
__version__ = '23.2'
__author__ = 'Cisco Systems Inc.'
__contact__ = ['pyats-support@cisco.com', 'pyats-support-ext@cisco.com']
__copyright__ = 'Copyright (c) 2017-2019, Cisco Systems Inc.'

# declare module as infra
__aetest_infra__ = True

# Configuration values for logging
CFG_LOG_BANNERS = 'aetest.logging.banners'
DEFAULT_LOG_BANNERS = True

# user's short-cut call to infra
from .main import main

# user section definitions
from .commons import CommonSetup, CommonCleanup
from .loop import loop
from .processors import processors, skip, skipIf, skipUnless
from .sections import subsection, setup, test, cleanup
from .testcase import Testcase
from .utils import exit_cli_code

# Easypy integration requirements (Main class and AEReporter class)
from .main import AEtest as Main
from .reporter import AEReporter

# force imports (trigger the module->obj mechanism)
from . import runtime
from . import discovery
