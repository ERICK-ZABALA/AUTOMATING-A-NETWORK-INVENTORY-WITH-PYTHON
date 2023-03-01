'''
GenieTelemetry Alignment Check Plugin.
'''

# Python
import re
import logging
import copy

# argparse
from pyats.utils import parser as argparse

# ATS
from pyats.log.utils import banner
from pyats.utils import parser as argparse
from pyats.datastructures import classproperty

# GenieTelemetry
from genie.telemetry.plugin import BasePlugin
from genie.telemetry.status import OK, WARNING, ERRORED, PARTIAL, CRITICAL

# module logger
logger = logging.getLogger(__name__)


class Plugin(BasePlugin):

    __plugin_name__ = 'Alignment Check Plugin'
    __version__ = '1.0.0'
    __supported_os__ = ['iosxe']

    @classproperty
    def parser(cls):
        parser = argparse.ArgsPropagationParser(add_help = False)
        parser.title = 'Alignment Check'
        
        # timeout
        # -------
        parser.add_argument('--alignmentcheck_timeout',
                            action="store",
                            default=300,
                            help="Specify duration <in seconds> to wait before "
                                 "timing out execution of a command")
        return parser

    def parse_args(self, argv):
        '''parse_args

        parse arguments if available, store results to self.args. This follows
        the easypy argument propagation scheme, where any unknown arguments to
        this plugin is then stored back into sys.argv and untouched.

        Does nothing if a plugin doesn't come with a built-in parser.
        '''

        # do nothing when there's no parser
        if not self.parser:
            return

        argv = copy.copy(argv)

        # avoid parsing unknowns
        self.args, _ = self.parser.parse_known_args(argv)


    def execution(self, device, **kwargs):

        # Init
        status = OK
        message = ''

        # Execute command to check for tracebacks - timeout set to 5 mins
        try:
            output = device.execute(self.show_cmd,
                                    timeout=self.args.alignmentcheck_timeout)
        except Exception as e:
            status += CRITICAL(str(e))
            return status
            
        if not output:
            return ERRORED('No output from {cmd}'.format(cmd=self.show_cmd))

        # Check for alignment errors. Hex values = problems.
        if '0x' in output:
            message = "Device {d} Alignment error detected: '{o}'"\
                .format(d=device.name, o=output)
            status += CRITICAL(message)
            logger.error(banner(message))

        # Log message to user
        if not message:
            message = "***** No alignment error found *****"
            status += OK(message)
            logger.info(banner(message))

        # Final status
        return status
