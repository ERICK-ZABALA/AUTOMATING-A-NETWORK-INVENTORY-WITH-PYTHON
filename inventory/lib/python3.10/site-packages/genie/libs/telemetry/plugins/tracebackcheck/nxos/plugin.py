''' 
GenieTelemetry Traceback Check Plugin for NXOS.
'''

from ..plugin import Plugin as BasePlugin


class Plugin(BasePlugin):

    show_cmd = 'show logging logfile'
    clear_cmd = 'clear logging logfile'
