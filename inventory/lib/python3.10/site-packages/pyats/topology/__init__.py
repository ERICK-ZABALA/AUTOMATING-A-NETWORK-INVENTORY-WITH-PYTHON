'''
Module:
    Topology

Authors:
    Siming Yuan (siyuan), CSG - Ottawa

Description:
    This module provides two functionalities:
        1. testbed description, conceptually similar to ATS Tcl CONFIG file.
        2. testbed topology information conceptually similar to ATS Tcl's
           MAP file.

    In Python ATS infrastructure, the above two are combined together and
    featured in one YAML file. The YAML file is then read to create a Topology
    object.

    The following graph depics what a typical topology looks like::

        +--------------------------------------------------------------------------+
        | Testbed Object                                                           |
        |                                                                          |
        | +-----------------------------+          +-----------------------------+ |
        | | Device Object - myRouterA   |          | Device Object - myRouterB   | |
        | |                             |          |                             | |
        | |         device interfaces   |          |          device interfaces  | |
        | | +----------+ +----------+   |          |   +----------+ +----------+ | |
        | | | intf Obj | | intf Obj |   |          |   |  intf Obj| | intf Obj | | |
        | | | Eth1/1   | | Eth1/2 *-----------*----------*  Eth1/1| | Eth1/2   | | |
        | | +----------+ + ---------+   |     |    |   +----------+ +----------+ | |
        | +-----------------------------+     |    +-----------------------------+ |
        |                                     |                                    |
        |                               +-----*----+                               |
        |                               | Link Obj |                               |
        |                               |rtrA-rtrB |                               |
        |                               +----------+                               |
        +--------------------------------------------------------------------------+


Notes:
    ipaddress module is called py2-ipaddress in PyPI, a backport of
    Python3's standard ipaddress module, documentation at:
    http://docs.python.org/3.3/library/ipaddress
'''

# metadata
__version__ = '23.2'
__author__ = 'Cisco Systems Inc.'
__contact__ = ['pyats-support@cisco.com', 'pyats-support-ext@cisco.com']
__copyright__ = 'Copyright (c) 2017-2019, Cisco Systems Inc.'

from .link import Link, LinkBase
from .interface import Interface, InterfaceBase
from .device import Device, DeviceBase
from .testbed import Testbed, TestbedBase

# import the loader
# this forces the appearance of pyats.topology.loader
# because it's a class obj appearing as a module
from . import loader
