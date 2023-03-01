import os

from pyats.log import managed_handlers
from pyats.results import Passed, Failed, Skipped

import logging

logger = logging.getLogger(__name__)

RESULT_MAP = {
    'PASS': Passed,
    'FAIL': Failed,
    'NOT_RUN': Skipped,
}

class AEReportListener(object):
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, client,
                       runinfo_dir,
                       task_id):
        self.client = client
        self.runinfo_dir = runinfo_dir
        self.task_id = task_id

        self.in_test = False
        self.keyword_index = 1

        self.parameters = {}

        # rig the logging system so start/end messages only show in tasklog
        logger.handlers.append(managed_handlers.tasklog)
        logger.propagate = False

    @property
    def logfile(self):
        return managed_handlers.tasklog.logfile

    def start_suite(self, name, attributes):
        # flush log
        managed_handlers.tasklog.flush()

        suite_args = {'id': self.task_id,
                      #'name': attributes['longname'],
                      'name': os.path.basename(attributes['source']).split('.')[0],
                      'logfile': self.logfile,
                      'testscript': attributes['source']}

        if self.parameters:
            suite_args['parameters'] = str(self.parameters)

        suite_args['description'] = attributes.pop('doc', None)
        suite_args['robotid'] = attributes.pop('id', None)
        attributes.pop('starttime', None)

        self.client.start_task(**suite_args)

    def end_suite(self, name, attributes):
        # flush log
        managed_handlers.tasklog.flush()

        self.client.stop_task()

    def start_test(self, name, attributes):
        logger.info("Starting testcase '%s'" % name)

        self.in_test = True
        self.keyword_index = 1
        # flush log
        managed_handlers.tasklog.flush()

        tc_name = attributes['longname'].split('.')[1]

        tc_args = {'type': 'Testcase',
                   'id': tc_name,
                   'name': tc_name,
                   'logfile': self.logfile}

        tc_args['description'] = attributes.pop('doc', None)
        tc_args['robotid'] = attributes.pop('id', None)
        attributes.pop('starttime', None)

        tc_args.update(attributes)

        # start tc
        self.client.start_section(**tc_args)

    def end_test(self, name, attributes):
        result = RESULT_MAP[attributes['status']]
        result = result.clone(reason=attributes['message'])

        logger.info("The result of testcase '%s' is => %s"
                    % (name, result.value.upper()))
        self.in_test = False

        # flush log
        managed_handlers.tasklog.flush()

        # stop tc
        self.client.stop_section(result = result)

    def start_keyword(self, name, attributes):
        if not self.in_test:
            return

        logger.info("Starting section '%s'" % name)

        # flush log
        managed_handlers.tasklog.flush()

        kw_args = {'type': 'TestSection',
                   'id': '%d_%s' % (self.keyword_index, attributes['kwname']),
                   'name': attributes['kwname'],
                   'logfile': self.logfile,
        }

        # Enforces section ID uniqueness even when using the same keyword
        # multiple times
        self.keyword_index += 1

        kw_args['description'] = attributes.pop('doc', None)
        attributes.pop('starttime', None)
        attributes.pop('type', None)

        kw_args.update(attributes)

        # start section
        self.client.start_section(**kw_args)

    def end_keyword(self, name, attributes):
        if not self.in_test:
            return

        result = RESULT_MAP[attributes['status']]
        logger.info("The result of section '%s' is => %s"
                    % (name, result.value.upper()))

        # flush log
        managed_handlers.tasklog.flush()

        # report it
        self.client.stop_section(result = result)
