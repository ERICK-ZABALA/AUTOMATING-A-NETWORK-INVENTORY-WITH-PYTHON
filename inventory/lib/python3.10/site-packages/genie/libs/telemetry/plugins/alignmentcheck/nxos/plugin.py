''' 
GenieTelemetry Alignment Check Plugin for NXOS.
'''

from ..plugin import Plugin as BasePlugin
from genie.telemetry.status import WARNING

class Plugin(BasePlugin):
    def execution(self, device, **kwargs):    
        return WARNING('NXOS not supported Alignment Check')
