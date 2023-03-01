''' 
GenieTelemetry Traceback Check Plugin for IOSXR.
'''

from ..plugin import Plugin as BasePlugin


class Plugin(BasePlugin):

    show_cmd = 'show logging'
    clear_cmd = 'clear logging'
