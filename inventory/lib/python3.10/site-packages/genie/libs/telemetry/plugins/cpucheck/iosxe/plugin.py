''' 
GenieTelemetry CpuUtilizationCheck Plugin for IOSXE
'''

from ..plugin import Plugin as BasePlugin

# parser
from genie.libs.parser.iosxe.show_platform import ShowProcessesCpuSorted

class Plugin(BasePlugin):

	PARSER_MODULE = ShowProcessesCpuSorted
