from .base import Base, ConfigurableBase
from .base import DeviceFeature, InterfaceFeature, LinkFeature
from .link import Link, LoopbackLink, EmulatedLink, VirtualLink
from .device import Device
from .testbed import Testbed
from .interface import BaseInterface
from .api import API
# import the loader
# this forces the appearance of genie.conf.base.loader
# because it's a class obj appearing as a module
from . import loader

Interface = BaseInterface  # Hide internal implementation
