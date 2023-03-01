
# Python
import time
import logging
from datetime import datetime

# GenieMonitor
from genie.telemetry.status import OK, WARNING, ERRORED, PARTIAL, CRITICAL

# Parsergen
from genie.parsergen import oper_fill_tabular

# abstract
from genie.abstract import Lookup

# Import FileUtils core utilities
from pyats.utils.fileutils import FileUtils

# Unicon
from unicon.eal.dialogs import Statement, Dialog

# module logger
logger = logging.getLogger(__name__)


def check_cores(device, core_list, **kwargs):

    # Init
    status = OK

    # Check if device is VDC
    try:
        output = device.parse('show vdc current-vdc')
    except Exception as e:
        logger.warning(e)
        meta_info = "Unable to execute 'show vdc current-vdc' to check if device is VDC"
        logger.error(meta_info)
        status = ERRORED(meta_info)
        return status

    # Check if device is VDC
    if 'current_vdc' in output and output['current_vdc']['id'] != '1':
        cmd = 'show cores'
    else:
        cmd = 'show cores vdc-all'

    # Execute command to check for cores
    header = [ "VDC", "Module", "Instance",
                "Process\-name", "PID", "Date\(Year\-Month\-Day Time\)" ]
    output = oper_fill_tabular(device = device, 
                               show_command = cmd,
                               header_fields = header, index = [5])

    if not output.entries:
        meta_info = "No cores found!"
        logger.info(meta_info)
        return OK(meta_info)
    
    # Parse through output to collect core information (if any)
    for k in sorted(output.entries.keys(), reverse=True):
        row = output.entries[k]
        date = row.get("Date\\(Year\\-Month\\-Day Time\\)", None)
        if not date:
            continue
        date_ = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

        # Save core info
        core_info = dict(module = row['Module'],
                         pid = row['PID'],
                         instance = row['Instance'],
                         process = row['Process\\-name'],
                         date = date.replace(" ", "_"))
        core_list.append(core_info)

        meta_info = "Core dump generated for process '{}' at {}".\
            format(row['Process\\-name'], date_)
        logger.error(meta_info)
        status += CRITICAL(meta_info)

    return status


def upload_to_server(device, core_list, *args, **kwargs):

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

    # Upload each core found
    for core in core_list:
        # Sample command:
        # copy core://<module-number>/<process-id>[/instance-num]
        #      tftp:[//server[:port]][/path] vrf management
        path = '{dest}/core_{pid}_{process}_{date}_{time}'.format(
                                                   dest = destination,
                                                   pid = core['pid'],
                                                   process = core['process'],
                                                   date = core['date'],
                                                   time = time.time())
        if port:
            server = '{server}:{port}'.format(server = server, port = port)

        if 'instance' in core:
            pid = '{pid}/{instance}'.format(pid = core['pid'],
                                            instance = core['instance'])

        message = "Core dump upload attempt from module {} to {} via server {}".\
                    format(core['module'], destination, server)

        # construction the module/pid for the copy process
        core['core'] = '{module}/{pid}'.format(module = core['module'],
                                               pid = core['pid'])
        try:
            # Check if filetransfer has been added to device before or not
            if not hasattr(device, 'filetransfer'):
                device.filetransfer = FileUtils.from_device(device)

            to_URL = '{protocol}://{address}/{path}'.format(
                protocol=protocol,
                address=server,
                path=path)

            from_URL = 'core://{core_path}'.format(core_path=core['core'])

            device.filetransfer.copyfile(device=device,
                                         source=from_URL,
                                         destination=to_URL)
        except Exception as e:
            if 'Tftp operation failed' in str(e):
                meta_info = "Core dump upload operation failed: {}".format(
                    message)
                logger.error(meta_info)
                status += ERRORED(meta_info)
            else:
                # Handle exception
                logger.error(e)
                status += ERRORED("Failed: {}".format(message))
        else:
            meta_info = "Core dump upload operation passed: {}".format(message)
            logger.info(meta_info)
            status += OK(meta_info)

    return status


def clear_cores(device, core_list, crashreport_list, **kwargs):

    # Execute command to delete cores
    try:
        device.execute('clear cores')
        meta_info = "Successfully cleared cores on device"
        logger.info(meta_info)
        status = OK(meta_info)
    except Exception as e:
        # Handle exception
        logger.warning(e)
        meta_info = "Unable to clear cores on device"
        logger.error(meta_info)
        status = ERRORED(meta_info)

    return status

def check_tracebacks(device, timeout, **kwargs):

    # Execute command to check for tracebacks
    output = device.execute('show logging logfile', timeout=timeout)

    return output

def clear_tracebacks(device, timeout, **kwargs):

    # Execute command to clear tracebacks
    output = device.execute('clear logging logfile', timeout=timeout)

    return output
