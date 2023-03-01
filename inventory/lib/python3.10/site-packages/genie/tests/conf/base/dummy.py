from genie.conf.base.link import Link
from genie.conf.base.device import Device
from genie.conf.base.testbed import Testbed
from genie.conf.base.interface import BaseInterface as Interface


class AltTestbed(Testbed):
    pass

class AltInterface(Interface):
    pass

class AltLink(Link):
    pass

class AltDevice(Device):
    pass