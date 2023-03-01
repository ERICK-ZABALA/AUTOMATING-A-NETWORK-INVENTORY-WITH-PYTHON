import os
import sys
import time
import pathlib
import logging
import getpass
import platform
import traceback

from pyats import log
from pyats.utils import sig_handlers
from pyats.datastructures import AttrDict
from pyats.utils.import_utils import import_from_name

from .parser import Parser
from .manager import TimedManager
from .config import Configuration
from .email import MailBot, TextEmailReport
from .utils import escape, filter_exception, ordered_yaml_dump

# module logger
logger = logging.getLogger('genie.telemetry')

__LOG_FILE__ = 'telemetry.log'
__BUFF_SIZE__ = 5000

class StreamToLogger(object):
    """
    Class that clone stdout content and publishes to websocket queue.
    """

    publisher = None

    def write(self, message):
        # write to screen
        sys.__stdout__.write(message)
        # publish to liveview
        try:
            if self.publisher and message:
                self.publisher.put(dict(stream=message.strip('\n')))
        except Exception as e:
            sys.__stdout__.write(str(e))
        sys.__stdout__.flush()

    def flush(self):
        sys.__stdout__.flush()

    def close(self):
        pass

class GenieTelemetry(object):

    def __init__(self):
        '''Built-in __init__

        Initializes GenieTelemetry object with default values required for the
        parser.
        '''

        # collect environment information
        # -------------------------------
        self.env = AttrDict(
            argv = ' '.join(sys.argv),
            prefix = sys.prefix,
            user = getpass.getuser(),
            host = platform.node()
        )

        # enable double ctrl-c SIGINT handler
        # -----------------------------------
        sig_handlers.enable_double_ctrl_c()

        # create command-line argv parser
        # -------------------------------
        self.parser = Parser()
        self.manager = None
        self.liveview = None

        self.stream_logger = StreamToLogger()
        sys.stdout = self.stream_logger

    def main(self, testbed={},
                   testbed_file = None,
                   loglevel = None,
                   configuration={},
                   configuration_file=None,
                   no_mail = False,
                   no_notify = False,
                   mailto = None,
                   mail_subject = None,
                   notify_subject = None,
                   runinfo_dir = None,
                   uid = None,
                   callback_notify = None,
                   timeout = None,
                   email_domain = None,
                   smtp_host = None,
                   smtp_port = None,
                   pdb = False):

        '''run

        Business logic, runs everything
        '''
        # parse core arguments
        # --------------------
        args = self.parser.parse_args()

        # set defaults arguments
        # ----------------------
        testbed_file = testbed_file or args.testbedfile
        loglevel = loglevel or args.loglevel
        configuration_file = configuration_file or args.configuration

        if not configuration and not configuration_file:
            raise AttributeError("'-configuration <path to config_file.yaml>"
                                 " is missing.")

        self.testbed_file = testbed_file
        self.pdb = pdb or '-pdb' in sys.argv
        self.uid = uid or args.uid
        self.timeout = timeout or args.timeout
        self.callback_notify = callback_notify or args.callback_notify

        # configure runinfo dir and log file
        # ------------------------------
        runinfo_dir = runinfo_dir or args.runinfo_dir
        if not runinfo_dir:
            runinfo_dir = os.path.join(os.getcwd(), 'telemetry', self.uid)
            if not os.path.exists(runinfo_dir):
                try:
                    pathlib.Path(runinfo_dir).mkdir(parents=True)
                except FileExistsError:
                    pass

        self.runinfo_dir = runinfo_dir
        self.logfile = os.path.join(self.runinfo_dir, __LOG_FILE__)
        # configure log handler and logging level
        # ------------------------------
        log.managed_handlers.tasklog = log.TaskLogHandler(self.logfile)
        logger.addHandler(log.managed_handlers.tasklog)
        logger.setLevel(loglevel)


        # configure MailBot
        # ------------------------------
        self.mailbot = MailBot(instance = self,
                               from_addrs = self.env.user,
                               to_addrs = mailto or self.env.user,
                               subject = mail_subject,
                               notify_subject = notify_subject,
                               nomail = no_mail,
                               nonotify = no_notify,
                               email_domain = email_domain,
                               smtp_host = smtp_host,
                               smtp_port = smtp_port)

        # configure TextEmailReport
        # ------------------------------
        self.report = TextEmailReport(instance = self)

        try:
            with self.mailbot:

                # configure Live View
                # ------------------------------
                self.liveview = self.load_liveview()

                # configure Timed Manager
                # ------------------------------
                self.manager = TimedManager(instance=self,
                                        testbed=testbed,
                                        runinfo_dir= self.runinfo_dir,
                                        testbed_file=testbed_file,
                                        configuration=configuration,
                                        configuration_file=configuration_file,
                                        timeout=self.timeout)

                # start genie telemetry
                # ------------------------------
                self.start()
        except Exception:
            raise
        finally:
            # stop genie telemetry
            # ------------------------------
            self.stop()

            sys.stdout = sys.__stdout__

    def post_call_plugin(self, device, results):
        '''post_call_plugin

        post task right after each plugin execution. It emits out liveview
        websocket data if enabled.
        '''
        # skip, if liveview is not enabled
        if not self.liveview:
            return
        # massage the execution result
        websocket_data = []
        for p, res in results.items():
            for device, data in res.items():
                status = data.get('status')
                # to nanoseconds
                timestamp = int(time.time()*1000000000)
                websocket_data.append(dict(status=str(status).upper(),
                                           value=status.code,
                                           device=device,
                                           plugin=p,
                                           result=data.get('result'),
                                           timestamp=timestamp))
        # push result to websocket publisher queue
        self.publisher.put(dict(results=websocket_data))

    def post_run(self, device, plugin, result):
        '''post_run

        post task which gets called after each device plugin execution.
        it sends out notification if result is not ok along with snapshot of
        plugin current status.
        '''
        status = str(result.get('status', 'Ok')).capitalize()
        # verify whether we should send notify
        if status == 'Ok':
            return

        snapshots = []
        for n,s in self.get_status_snapshot(device, plugin).items():
            snapshots.append('   - {} : {}'.format(n,s))

        self.mailbot.send_notify(device=device,
                                 plugin=plugin,
                                 status=status,
                                 result=result.get('result', {}),
                                 snapshots='\n'.join(snapshots))

    def load_liveview(self):
        '''load_liveview

        Load liveview library if and only callback_notify uri is specified.
        '''
        if not self.callback_notify:
            return

        try:

            cls = import_from_name('ats_liveview.base.Feed')

        except (ImportError, AttributeError):
            return
        # instantiate telemetry view
        telemetryview = cls(self,
                            uid=self.uid,
                            runinfo_dir=self.runinfo_dir,
                            feed_type='telemetryviews',
                            events=('telemetryview',
                                    'telemetryview-subscribe',
                                    'telemetryview-unsubscribe',
                                    'telemetryview-error'))

        self.stream_logger.publisher = self.publisher = telemetryview.publisher

        return telemetryview

    def start(self):
        '''start

        1. Start Liveview Manager
        2. Start Timed Manager
        '''

        if self.liveview:
            logger.info('Starting Liveview Manager ... ')
            self.log_index = 0
            self.liveview.start()

        if self.manager:
            logger.info('Starting TimedManager ... ')
            devices = self.manager.setup()

            self.manager.start()

    def stop(self):
        '''stop

        1. Stop Timed Manager
        2. Stop Liveview Manager
        '''
        if self.manager:
            logger.info('Stopping TimedManager ... ')
            self.manager.takedown()

        if self.liveview:
            logger.info('Stopping Liveview Manager ... ')
            self.liveview.stop()

    # get testbed name - shortcuts
    @property
    def name(self):
        return self.manager.testbed.name

    # get testbed device names - shortcuts
    @property
    def devices(self):
        return ','.join(self.manager.devices.keys())

    # get overall rollup status - shortcuts
    @property
    def status(self):
        return str(self.manager.status).upper()

    # get statuses stats - shortcuts
    @property
    def statuses(self):
        return self.manager.statuses

    # get final report - shortcuts
    @property
    def summary(self):
        return self.manager.finalize_report()

    # get status snapshot of given device, except specified plugin - shortcuts
    def get_status_snapshot(self, device, plugin=None):
        snapshot = self.manager.plugins.get_device_plugins_status(device,
                                                                  label=True)
        if plugin:
            snapshot.pop(plugin, None)
        return snapshot

def main():
    '''command line entry point

    command-line entry point. Uses the default runtime and checks for whether a 
    jobfile is parsed from command line, if not, exist with parser error.

    strictly used for setuptools.load_entry_point/console_script. 
    '''

    try:

        GenieTelemetry().main()

    except Exception as e:

        print(filter_exception(*sys.exc_info()), file = sys.stderr)

        # and exiting with error code
        sys.exit(1)

    sys.exit(0)


