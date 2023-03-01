
# Python
import re
import logging

# ATS
from pyats.log.utils import banner

# GenieMonitor
from genie.telemetry.status import OK, WARNING, ERRORED, PARTIAL, CRITICAL

# abstract
from genie.abstract import Lookup

# Import FileUtils core utilities
from pyats.utils.fileutils import FileUtils

# Unicon
from unicon.eal.dialogs import Statement, Dialog
from unicon.eal.utils import expect_log

# module logger
logger = logging.getLogger(__name__)


def check_cores(device, core_list, crashreport_list, timeout, crash_type=None):

    # Init
    status = OK

    # Construct the core pattern to be parsed later
    # 1613827  -rw-         56487348  Oct 17 2017 15:56:59 +17:00  PE1_RP_0_x86_64_crb_linux_iosd-universalk9-ms_15866_20171016-155604-PDT.core.gz
    # 7763     -rw-        107847329   Jul 5 2018 12:53:55 +00:00  kernel.rp_RP-EDISON_0_20180705125020.core.flat.gz
    # 7761     -rw-            36003   Jul 5 2018 12:50:20 +00:00  kernel.rp_RP-EDISON_0_20180705125020.txt
    core_pattern = re.compile(r'(?P<number>\d+) '
        '+(?P<permissions>[rw\-]+) +(?P<filesize>\d+) '
        '+(?P<month>\w+) +(?P<date>\d+) +(?P<year>\d+) '
        '+(?P<time>[\w\:]+) +(?P<timezone>(\S+)) +(?P<core>((.*\.core\.gz)|(.*\.core\.flat\.gz)|(.*\.txt)))$', re.IGNORECASE)

    # Construct the crashreport pattern to be parsed later
    # 62  -rw-           125746  Jul 30 2016 05:47:28 +00:00  crashinfo_RP_00_00_20160730-054724-UTC
    crashinfo_pattern = re.compile(r'(?P<number>\d+) '
        '+(?P<permissions>[rw\-]+) +(?P<filesize>\d+) '
        '+(?P<month>\w+) +(?P<date>\d+) +(?P<year>\d+) '
        '+(?P<time>[\w\:]+) +(?P<timezone>(\S+)) '
        '+(?P<core>(crashinfo.*))$', re.IGNORECASE)

    # define default checking dir
    locations = ['flash:/core', 'bootflash:/core', 'harddisk:/core', 'crashinfo:']

    # if provided 
    if crash_type:
        for crash_string in crash_type.split(','):
            locations.append('flash:{}*'.format(crash_string.strip())) if crash_string else None

    # Execute command to check for cores and crashinfo reports
    for location in locations:
        try:
            output = device.execute('dir {}'.format(location), timeout=timeout)
        except Exception as e:
            if any(isinstance(item, TimeoutError) for item in e.args):
                # Handle exception
                logger.warning(e)
                logger.warning(banner("dir {} execution exceeded the timeout value {}".format(location, timeout)))
            else:
                # Handle exception
                logger.warning(e)
                logger.warning(banner("Location '{}' does not exist on device".format(location)))

            continue
        
        if 'Invalid input detected' in output or \
           'No such file' in output :
            logger.warning("Location '{}' does not exist on device".format(location))
            continue
        elif not output:
            meta_info = "Unable to check for cores"
            logger.error(meta_info)
            return ERRORED(meta_info)

        for line in output.splitlines():
            line = line.strip()

            m = core_pattern.match(line)
            if m:
                core = m.groupdict()['core']
                meta_info = "Core dump generated:\n'{}'".format(core)
                logger.error(meta_info)
                status += CRITICAL(meta_info)
                core_info = dict(location = location,
                                 core = core)
                core_list.append(core_info)
                continue

            m = crashinfo_pattern.match(line)
            if m:
                crashreport = m.groupdict()['core']
                meta_info = "Crashinfo report generated:\n'{}'".\
                    format(crashreport)
                logger.error(meta_info)
                status += CRITICAL(meta_info)
                crashreport_info = dict(location = location,
                    core = crashreport)
                crashreport_list.append(crashreport_info)
                continue

            # find user defined crashed files other than crashinfo
            pattern = location.split(':')[1]
            if pattern and '/' not in pattern:
                m = re.compile(r'{}'.format(pattern)).match(line)
                if m:
                    crashreport = line
                    meta_info = "Crashinfo report generated:\n'{}' on device {}".\
                        format(line, device.name)
                    logger.error(meta_info)
                    status += CRITICAL(meta_info)
                    crashreport_info = dict(location = location,
                        core = crashreport)
                    crashreport_list.append(crashreport_info)
                    continue

        if not core_list:
            meta_info = "No cores found at location: {}".format(
                location)
            logger.info(meta_info)
            status += OK(meta_info)

        if not crashreport_list:
            meta_info = "No crashreports found at location: {}".\
                format(location)
            logger.info(meta_info)
            status += OK(meta_info)

    return status


def upload_to_server(device, core_list, crashreport_list, **kwargs):

    # Init
    status= OK

    # Get info
    port = kwargs['port']
    server = kwargs['server']
    timeout = kwargs['timeout']
    destination = kwargs['destination']
    protocol = kwargs['protocol']
    username = kwargs['username']
    password = kwargs['password']

    # Check values are not None
    for item in kwargs:
        if item in ['protocol', 'server', 'destination', 'username', 'password'] and \
           kwargs[item] is None:
            meta_info = "Unable to upload core dump - parameters `{}` not provided."\
                        " Required parameters are: `protocol`, `server`, "\
                        "`destination`, `username`, `password`".format(item)
            return ERRORED(meta_info)

    # preparing the full list to iterate over
    full_list = core_list + crashreport_list

    if port:
        server = '{server}:{port}'.format(server=server, port=port)

    # Upload each core/crashinfo report found
    for item in full_list:

        if 'crashinfo' in item['core']:
            file_type = 'Crashreport'
        else:
            file_type = 'Core'

        message = "{} upload attempt from {} to {} via server {}".format(
            file_type, item['location'], destination, server)

        try:
            # Check if filetransfer has been added to device before or not
            if not hasattr(device, 'filetransfer'):
                device.filetransfer = FileUtils.from_device(device)

            to_URL = '{protocol}://{address}/{path}'.format(
                protocol=protocol,
                address=server,
                path=destination)

            from_URL = '{location}//{core_path}'.format(
                location=item['location'], core_path=item['core'])

            device.filetransfer.copyfile(device=device,
                                         source=from_URL,
                                         destination=to_URL)
        except Exception as e:
            if 'Tftp operation failed' in e:
                meta_info = "{} upload operation failed: {}".format(file_type,
                    message)
                logger.error(meta_info)
                status += ERRORED(meta_info)
            else:
                # Handle exception
                logger.warning(e)
                status += ERRORED("Failed: {}".format(message))

        meta_info = "{} upload operation passed: {}".format(file_type, message)
        logger.info(meta_info)
        status += OK(meta_info)

    return status


def clear_cores(device, core_list, crashreport_list):

    # Create dialog for response
    dialog = Dialog([
        Statement(pattern=r'Delete.*',
                  action='sendline()',
                  loop_continue=True,
                  continue_timer=False),
        ])

    # preparing the full list to iterate over
    full_list = core_list + crashreport_list

    # Delete cores from the device
    for item in full_list:
        try:
            # Execute delete command for this core
            cmd = 'delete {location}/{core}'.format(
                core=item['core'],location=item['location'])
            output = device.execute(cmd, timeout=300, reply=dialog)
            # Log to user
            meta_info = 'Successfully deleted {location}/{core}'.format(
                core=item['core'],location=item['location'])
            logger.info(meta_info)
            return OK(meta_info)
        except Exception as e:
            # Handle exception
            logger.warning(e)
            meta_info = 'Unable to delete {location}/{core}'.format(
                core=item['core'],location=item['location'])
            logger.error(meta_info)
            return ERRORED(meta_info)

def check_tracebacks(device, timeout, **kwargs):

    # Execute command to check for tracebacks
    output = device.execute('show logging', timeout=timeout)

    return output

def clear_tracebacks(device, timeout, **kwargs):

    # Execute command to clear tracebacks
    output = device.execute('clear logging', timeout=timeout)

    return output
