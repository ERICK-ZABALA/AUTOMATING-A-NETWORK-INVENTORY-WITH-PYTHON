'''
GenieTelemetry CpuUtilizationCheck Plugin
'''
# Python
import copy
import logging

# argparse
from argparse import ArgumentParser

# ATS
from pyats.log.utils import banner
from pyats.utils import parser as argparse
from pyats.datastructures import classproperty

# GenieTelemetry
from genie.telemetry.plugin import BasePlugin
from genie.telemetry.status import OK, WARNING, ERRORED, PARTIAL, CRITICAL

# Genie
from genie.utils.timeout import Timeout

# module logger
logger = logging.getLogger(__name__)


class Plugin(BasePlugin):

    __plugin_name__ = 'CPU utilization Check Plugin'
    __version__ = '1.0.0'
    __supported_os__ = ['iosxe']

    @classproperty
    def parser(cls):
        parser = argparse.ArgsPropagationParser(add_help = False)
        parser.title = 'CPU utilization Check'

        # timeout
        # -------
        parser.add_argument('--cpucheck_timeout',
                            action="store",
                            default=120,
                            help = "Specify poll timeout value\ndefault "
                                   "to 120 seconds")
        # # interval
        # # -------
        parser.add_argument('--cpucheck_interval',
                            action="store",
                            default=20,
                            help = "Specify poll interval value\ndefault "
                                   "to 20 seconds")
        # # five_min_percentage
        # # -------------------
        parser.add_argument('--cpucheck_fivemin_pcnt',
                            action="store",
                            default=60,
                            help = "Specify limited 5 minutes percentage of "
                                   "cpu usage\ndefault to 60")
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
        
        # create timeout object
        timeout = Timeout(max_time=int(self.args.cpucheck_timeout),
                          interval=int(self.args.cpucheck_interval))

        # loop status
        loop_stat_ok = True

        if not hasattr(self, 'PARSER_MODULE'):
            return WARNING('Does not have CPU related parsers to check')

        while timeout.iterate():
            # Execute command to get five minutes usage percentage
            try:
                cpu_dict = self.PARSER_MODULE(device).parse(
                    sort_time='5min', key_word='CPU')
            except Exception as e:
                return ERRORED('No output from show processes cpu\n{}'.format(e))

            # Check 5 minutes percentage smaller than cpucheck_fivemin_pcnt
            if int(cpu_dict['five_min_cpu']) >= int(self.args.cpucheck_fivemin_pcnt):
                message = "****** Device {d} *****\n".format(d=device.name)
                message += "Excessive CPU utilization detected for 5 min interval\n"
                message += "Allowed: {e}%\n".format(e=self.args.cpucheck_fivemin_pcnt)
                message += "Measured: FiveMin: {r}%".format(r=cpu_dict['five_min_cpu'])
                loop_stat_ok = False
                timeout.sleep()
            else:
                message = "***** CPU usage is Expected ***** \n"
                message += "Allowed threashold: {e} \n"\
                                .format(e=self.args.cpucheck_fivemin_pcnt)
                message += "Measured from device: {r}"\
                                .format(r=cpu_dict['five_min_cpu'])
                loop_stat_ok = True
                status += OK(message)
                logger.info(banner(message))
                break

        if not loop_stat_ok:
            status += CRITICAL(message)
            logger.error(banner(message))

        # Final status
        return status
