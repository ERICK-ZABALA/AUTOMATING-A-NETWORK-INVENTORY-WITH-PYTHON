'''
Module:
    genie

Description:
    This module defines the base classes required to write testscripts. It's
    name is a direct carry over from Tcl-ATS's AEtest package.

    In short, this module is designed to offer a similar look-and-feel of its
    Tcl counterpart, whilst leveraging and building based on the advanced
    object-oriented capabilities of the Python Language.

    aetest can be broken down as follows:

        - Common Sections
        - Testcases
        - Python ``unittest`` support

    For more detailed explanation and usages, refer to aetest documentation on
    pyATS home page: http://wwwin-pyats.cisco.com/
'''
# metadata
__copyright__ = 'Cisco Systems, Inc. Cisco Confidential'

# declare module as infra
__genie_infra__ = True

# user's short-cut call to infra
from .main import main

# Easypy integration requirements (Main class and AEReporter class)
# Needed for easypy task, for test_harness
from .main import Genie as Main
from pyats.aetest import AEReporter

