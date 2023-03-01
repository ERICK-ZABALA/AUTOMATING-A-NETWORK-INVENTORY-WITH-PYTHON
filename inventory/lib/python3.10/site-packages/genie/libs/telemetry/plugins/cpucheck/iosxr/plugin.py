''' 
GenieTelemetry CpuUtilizationCheck Plugin for IOSXR
'''

from ..plugin import Plugin as BasePlugin
from genie.telemetry.status import WARNING


class Plugin(BasePlugin):
    def execution(self, device, **kwargs):    
        return WARNING('IOSXR not supported CpuUtilizationCheck')