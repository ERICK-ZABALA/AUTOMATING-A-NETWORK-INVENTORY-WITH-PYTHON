#!/usr/bin/env python

# Python
import os
import sys
import yaml
import time
import signal
import unittest
from shutil import rmtree
from tempfile import mkdtemp
from multiprocessing import Process
from collections import OrderedDict
from unittest.mock import Mock, patch, call, PropertyMock

# ATS
from pyats.topology import loader
from pyats.aetest import CommonCleanup
from pyats.datastructures import AttrDict
from pyats.aetest import container
from pyats.aetest.signals import AEtestPassxSignal
from pyats.connections.bases import BaseConnection
from pyats.results import Passed, Passx

# GenieTelemetry
from genie.telemetry.parser import Parser
from genie.telemetry.main import GenieTelemetry
from genie.telemetry import BasePlugin, Manager, TimedManager, processors


class MockConnection(BaseConnection):

    connected = False

    def connect(self):
        self.connected = True

    def disconnect(self):
        self.connected = False

    def __getattr__(self, *args, **kwargs):
        return Mock()

    def parse(self, *args, **kwargs):
        return "MOCKED_PARSER"

    def learn(self, *args, **kwargs):
        pass

    def execute(self, *args, **kwargs):
        return 'MOCKED_EXECUTION'

    def __init__(self, device, alias=None, via=None, **kwargs):

        if alias is None:
            alias = device.name

        super().__init__(device = device, alias = alias, via = via, **kwargs)

class MockTestScript(object):
    pass

class MockSection(object):

    parameters = {}
    result = Passed
    message = None

    def passx(self, message):
        self.result = Passx
        self.message = message

    def __str__(self):
        return 'MockSection'

class MockCleanup(CommonCleanup):
    pass

class GenieTelemetryTestcase(unittest.TestCase):

    def setUp(self):

        global testbed, testbed_file, config_file, config_file2
        global runinfo_dir, script, section, clean_up

        directory = os.path.dirname(os.path.abspath(__file__))
        testbed_file = os.path.join(directory, 'scripts', 'testbed.yaml')
        config_file = os.path.join(directory, 'scripts', 'config.yaml')
        config_file2 = os.path.join(directory, 'scripts', 'config2.yaml')

        testbed = loader.load(testbed_file)
        runinfo_dir = mkdtemp(prefix='runinfo_dir')

        script = MockTestScript()
        section = MockSection()
        clean_up = MockCleanup()
        section.parent = script
        clean_up.parent = script

    def tearDown(self):
        rmtree(runinfo_dir)

    def test_base(self):

        with self.assertLogs('', level='INFO') as cm:
            processors.genie_telemetry_processor(section)
            output = '\n'.join(cm.output)
            msg = "'--genietelemetry' argument is not provided."
            self.assertTrue(msg in output)

        with self.assertLogs('', level='INFO') as cm:
            sys.argv = ['easypy', '--genietelemetry', config_file]
            processors.genie_telemetry_processor(section)
            output = '\n'.join(cm.output)
            msg = "no testbed supplied"
            self.assertTrue(msg in output)

    def test_passx_processor(self):
        [d.connect() for d in testbed.devices.values()]
        sys.argv = ['easypy', '--genietelemetry', config_file]
        with self.assertLogs('', level='INFO') as cm:
            # processors.runtime = Mock(side_effect=runtime)
            with patch.object(processors, 'runtime',
                              new_callable=PropertyMock) as mock_runtime:
                mock_runtime.testbed = testbed
                mock_runtime.runinfo = AttrDict()
                mock_runtime.runinfo.runinfo_dir = runinfo_dir
                processors.genie_telemetry_processor(section)

            output = '\n'.join(cm.output)
            msg = "failed to load abstration on device P1 for plugin mockplugin"
            self.assertTrue(msg in output)
            self.assertEqual(section.result, Passx)
            self.assertIsNotNone(section.message)
            msg = ("'genie.telemetry' caught anomalies: \n"
                  "genie.telemetry.tests.scripts.mockplugin\n\tP1\n\t\tpartial")
            self.assertEqual(msg, section.message)

            with patch.object(processors, 'runtime',
                              new_callable=PropertyMock) as mock_runtime:
                mock_runtime.testbed = testbed
                mock_runtime.runinfo = AttrDict()
                mock_runtime.runinfo.runinfo_dir = runinfo_dir
                with self.assertRaises(AEtestPassxSignal) as cm:
                    processors.genie_telemetry_processor(clean_up)
                    self.assertEqual(cm.exception.reason, msg)
                fname = os.path.join(runinfo_dir, 'telemetry.yaml')
                self.assertTrue(os.path.isfile(fname))
                with open(fname, 'r') as tempfile:
                    content = yaml.safe_load(tempfile)

                expected = { 'common cleanup': {
                                'genie.telemetry.tests.scripts.mockplugin': {
                                    'P1': {'status': 'Partial'}},
                                'Crash Dumps Plugin': {
                                    'P1': {'status': 'Ok'}},
                                'Traceback Check Plugin': {
                                    'P1': {'status': 'Ok'}}},
                            'MockSection': {
                                'genie.telemetry.tests.scripts.mockplugin': {
                                    'P1': {'status': 'Partial'}},
                                'Crash Dumps Plugin': {
                                    'P1': {'status': 'Ok'}},
                                'Traceback Check Plugin': {
                                    'P1': {'status': 'Ok',}}}
                            }
                self.assertEqual(sorted(content.keys()),
                                 sorted(expected.keys()))
                for key, value in expected.items():
                    self.assertTrue(key in content)
                    for plugin, devices in value.items():
                        content_devices = content[key].get(plugin, None)
                        self.assertIsNotNone(content_devices)
                        self.assertEqual(devices['P1']['status'],
                                         content_devices['P1']['status'])

    def test_pass_processor(self):
        [d.connect() for d in testbed.devices.values()]
        sys.argv = ['easypy', '--genietelemetry', config_file2]
        with self.assertLogs('', level='INFO') as cm:
            self.assertTrue(section.result)
            self.assertIsNone(section.message)
            # processors.runtime = Mock(side_effect=runtime)
            with patch.object(processors, 'runtime',
                              new_callable=PropertyMock) as mock_runtime:
                mock_runtime.testbed = testbed
                mock_runtime.runinfo = AttrDict()
                mock_runtime.runinfo.runinfo_dir = runinfo_dir
                processors.genie_telemetry_processor(section)

            output = '\n'.join(cm.output)
            msg = "failed to load abstration on device P1 for plugin mockplugin"
            self.assertFalse(msg in output)
            self.assertTrue(section.result)
            self.assertIsNone(section.message)

    def _test_main(self):
        sys.argv = ['genietelemetry', testbed_file,
                    '-configuration', config_file2,
                    '-runinfo_dir', runinfo_dir,
                    '-uid', 'mock',
                    '-no_mail']
        genie_telemetry = GenieTelemetry()
        p = Process(target=genie_telemetry.main)
        p.start()
        # wait for first interval
        time.sleep(15)

        # double ctrl+c event
        os.kill(p.pid, signal.SIGINT)
        time.sleep(1)
        os.kill(p.pid, signal.SIGINT)
        time.sleep(1)

        self.assertFalse(p.is_alive())

        fname = os.path.join(runinfo_dir, 'telemetry.yaml')
        self.assertTrue(os.path.isfile(fname))
        with open(fname, 'r') as tempfile:
            results = yaml.safe_load(tempfile)
        expected = {'Crash Dumps Plugin': {'P1': {'status': 'Ok'}},
                    'Traceback Check Plugin': {'P1': {'status': 'Ok'}}}
        content = {}
        for r in results.values():
            content.update(r)
        for plugin, devices in expected.items():
            content_devices = content.get(plugin, None)
            self.assertIsNotNone(content_devices)
            self.assertEqual(devices['P1']['status'],
                             content_devices['P1']['status'])

        fname = os.path.join(runinfo_dir, 'telemetry.log')
        self.assertTrue(os.path.isfile(fname))

        with open(fname, 'r') as logfile:
            logfiles = logfile.readlines()

        content = [x.strip() for x in logfiles]
        logs = ['Loading genie.telemetry Configuration',
                'Loading genie.telemetry Plugins',
                'Initializing genie.telemetry Plugins for Testbed Devices',
                'Initializing plugins for P1',
                ' - loading plugin',
                ' - loading plugin',
                'Starting TimedManager ...',
                'Setting up connection to device (P1)',
                None,
                'Telemetry Task',
                None,
                None,
                'Crash Dumps Plugin',
                None,
                '- device (P1)',
                'Status : Ok',
                ' - Result :',
                'No cores found!',
                None,
                'Telemetry Task',
                None,
                None,
                'Traceback Check Plugin',
                None,
                '- device (P1)',
                'Status : Ok',
                ' - Result :',
                '***** No patterns matched *****',
                'Ctrl+C keyboard interrupt detected...',
                'Aborting run & cleaning up as fast as possible...',
                None,
                'Monitoring Report']
        for expected, log in zip(logs, content[:len(logs)]):
            if not expected:
                continue
            self.assertTrue(expected in log)

    def test_help(self):
        sys.argv = ['genietelemetry', '-h']
        parser = Parser()
        help_output = parser.format_help()
        expected = '''
usage: genietelemetry [TESTBEDFILE]
                      [-h] [-loglevel] [-configuration FILE] [-uid UID]
                      [-runinfo_dir RUNINFO_DIR]
                      [-callback_notify CALLBACK_NOTIFY] [-timeout TIMEOUT]
                      [-connection_timeout CONNECTION_TIMEOUT] [-no_mail]
                      [-no_notify] [-mailto] [-mail_subject] [-notify_subject]
                      [-email_domain] [-smtp_host] [-smtp_port]
                      [-smtp_username] [-smtp_password]

genie telemetry command line arguments.

Example
-------
  genietelemetry /path/to/testbed.yaml

--------------------------------------------------------------------------------

Positional Arguments:
  TESTBEDFILE           testbed file to be monitored

Help:
  -h, -help             show this help message and exit

Logging:
  -loglevel             genie telemetry logging level
                        eg: -loglevel="INFO"

Configuration:
  -configuration FILE   configuration yaml file for plugins and settings
  -uid UID              Specify monitoring job uid
  -runinfo_dir RUNINFO_DIR
                        Specify directory to store execution logs
  -callback_notify CALLBACK_NOTIFY
                        Specify Liveview callback notify URI
  -timeout TIMEOUT      Specify plugin maximum execution length
                        Default to 300 seconds
  -connection_timeout CONNECTION_TIMEOUT
                        Specify connection timeout

Mailing:
  -no_mail              disable final email report
  -no_notify            disable notification on device health status other than "ok"
  -mailto               list of email recipients
  -mail_subject         report email subject header
  -notify_subject       notification email subject header
  -email_domain         default email domain
  -smtp_host            specify smtp host
  -smtp_port            specify smtp server port
  -smtp_username        specify smtp username
  -smtp_password        specify smtp password
'''
        self.maxDiff = None
        self.assertEqual(help_output.strip() , expected.strip())

if __name__ == '__main__':

    unittest.main()
