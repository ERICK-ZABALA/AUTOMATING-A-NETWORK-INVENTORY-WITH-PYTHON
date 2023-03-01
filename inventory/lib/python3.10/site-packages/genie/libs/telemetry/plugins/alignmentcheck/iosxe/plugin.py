''' 
GenieTelemetry Alignment Check Plugin for IOSXE.
'''

from ..plugin import Plugin as BasePlugin


class Plugin(BasePlugin):

    show_cmd = 'show alignment'
