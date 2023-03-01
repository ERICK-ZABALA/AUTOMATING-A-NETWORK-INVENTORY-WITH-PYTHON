import os
import yaml
import inspect
import logging
import tempfile
import importlib

from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError

from pyats.topology import loader
from pyats.aetest import executer, reporter
from pyats.aetest.script import TestScript
from pyats.aetest.parameters import discover_parameters
from pyats.aetest.processors import discover_global_processors
from pyats.results import (Passed, Failed, Aborted, Errored,
                         Skipped, Blocked, Passx)

log = logging.getLogger(__name__)


class pyATSRobot(object):
    '''pyASTS RobotFramework library'''

    # Need to maintain the testscript object
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self):
        # Need to create a testscript
        self.testscript = TestScript(Script)
        # save builtin so we dont have to re-create then everytime
        self.builtin = BuiltIn()
        self.connect_kwargs = {}

        # If datafile, then load it up
        try:
            self.datafile = self.builtin.get_variable_value('${datafile}')
        except (RuntimeError, RobotNotRunningError) as e:
            self.datafile = None

    @property
    def testbed(self):
        '''Return testscript.parameters['testbed']'''
        return self.testscript.parameters['testbed'] if 'testbed' in \
               self.testscript.parameters else None

    @testbed.setter
    def testbed(self, testbed):
        '''Store Testbed within pyATS testscript'''
        self.testscript.parameters['testbed'] = testbed

    @keyword('use testbed "${testbed}"')
    def use_testbed(self, testbed=None):
        """ Load testbed YAML file and instantiate testbed object """
        self.testbed = loader.load(testbed)

    @keyword('run testcase')
    def run_testcase_kwargs(self, python_path, *args, **kwargs):
        '''The keyword allow to call any pyATS testcase by passing the full
        python path of the testcase.'''
        return self.run_testcase(python_path, *args, **kwargs)

    @keyword('run testcase "${pythonpath:[^"]+}"')
    def run_testcase(self, python_path, *args, **kwargs):
        '''The keyword allow to call any pyATS testcase by passing the full
        python path of the testcase.'''

        # Split the name of the module
        # Last word should be class name, rest should be pythonpath of module
        module, attr_name = python_path.rsplit('.', 1)

        # Load the module
        mod = importlib.import_module(module)

        # Find the right attribute
        try:
            attribute = getattr(mod, attr_name)
        except AttributeError as e:
            raise AttributeError("Couldn't find '{name}' in "
                                 "'{mod}'".format(name=attr_name,
                                                  mod=mod)) from e

        # The way the datafile is loaded,
        # 1) Load datafile
        # 2) Check testscript.module if those sections exists
        # 3) If it doesnt exists, explodes. <- Issue
        # So this piece of code fix that up :)
        # It only load this particular testcase
        if self.datafile:
            # Now that we found
            old_module = self.testscript.module
            old_source = self.testscript.source
            self.testscript.module = mod
            self.testscript.source = inspect.getsourcefile(mod)

            try:
                x = self._load_pyats_datafile(attr_name)
            finally:
                # Revert back
                self.testscript.module = old_module
                self.testscript.source = old_source

        # Global processors
        # collect script-defined global processors
        discover_global_processors(mod)

        # compute parameters from module object
        parameters = discover_parameters(mod)

        # assign parameters to self
        parameters.update(self.testscript.parameters)
        self.testscript.parameters = parameters

        cls = attribute()

        # Now that's its instantiated, let's execute it
        # Get the parameters ready
        cls.parent = self.testscript
        cls.parent.parameters['testbed'] = self.testbed
        cls.parameters.update(kwargs)

        # Set the tags
        tags = cls.groups if hasattr(cls, 'groups') else []

        try:
            # Make sure its reset, as we dont need some of these functionalities
            executer.reset()
            result = cls()
        except Exception as e:
            # No need, as pyats has already logged the error
            pass

        # Resync the testbed, just in case it changed
        self.testbed = cls.parameters['testbed']

        # Maps the result RobotFramework
        self._convert_result(result, attr_name, ' '.join(tags))

    def _convert_result(self, result, name, tags):
        ''''
            pyATS    RobotFramework  Reason
            Passed   Pass            Passed is a pass
            Failed   Fail            Failed is a fail
            Aborted  Fail            An abort is because of a failure
            Errored  Fail            An error is because of a failure
            Skipped  Pass            A skip is not a failure
            Blocked  Pass            A block is not a failure
            Passx    Pass            Passx is a pass with exception
        '''
        fail_group = [Failed, Aborted, Errored]
        pass_group = [Passed, Skipped, Blocked, Passx]

        if result in fail_group:
            self.builtin.fail('{n} has {r}'.format(n=name, r=result.value),
                              tags)

        if result in pass_group:
            self.builtin.pass_execution('{n} has {r}'.format(n=name,
                                                             r=result.value),
                                        tags)

        raise Exception('{r} is not a supported result'.format(r=result.value))

    def _load_pyats_datafile(self, name):
        '''Workaround to load datafile for only the specific name'''

        # Remove all the other data information other than name
        with open(self.datafile) as f:
           datafile = yaml.safe_load(f)

        new_datafile = {}
        if name in datafile:
            new_datafile = {name: datafile[name]}


        elif name in datafile['testcases']:
            new_datafile = {'testcases':{name: datafile['testcases'][name]}}

        # Delete common setup/cleanup
        # Delete testcases
        datafile.pop('common_setup', None)
        datafile.pop('common_cleanup', None)
        datafile.pop('testcases', None)

        # Get the rest
        new_datafile.update(datafile)

        # Create new file - 'w' so we overwrite if a file already exists
        with tempfile.NamedTemporaryFile(mode ='w',
                                         prefix='datafile_',
                                         delete=False) as f:
            yaml.dump(new_datafile, f, default_flow_style = False)

        try:
            self.testscript.load_datafile(datafile = f.name)
        finally:
            # Delete the file
            os.remove(f.name)

    @keyword('connect to device')
    def connect_to_device_kwargs(self, device, **kwargs):
        """ Connect to device via connection as defined in testbed.yaml.
        `device` is a required argument. You can pass additional arguments
        via  `key=value`  syntax.
        """
        device = self._search_device(device)
        log.info("Connecting to device '{}'".format(device))
        log.info("kwargs: {}".format(kwargs))
        device.connect(**kwargs)

    # Connect to the device - All Alternatives
    @keyword('connect to devices "${devices}"')
    def connect_to_devices(self, devices=None):
        """ Connect to devices via connection as defined in testbed.yaml.
        Specify devices with semi-colon separated list, e.g. "R1;R2"
        """
        devices = [d.strip() for d in devices.split(';')]
        for device in devices:
            self.connect_via_to_device_as_alias(device, None, None)

    @keyword('connect to all devices')
    def connect_to_all_devices(self):
        """ Connect to all devices """
        devices = self.testbed.devices
        for device in devices:
            self.connect_via_to_device_as_alias(device, None, None)

    @keyword('connect to device "${device:[^"]+}"')
    def connect_to_device(self, device=None):
        """ Connect to device connection as defined in testbed.yaml """
        self.connect_via_to_device_as_alias(device, None, None)

    @keyword('connect to device "${device:[^"]+}" via "${via:[^"]+}"')
    def connect_via_to_device(self, device, via):
        """ Connect to a device with non-default via. """
        self.connect_via_to_device_as_alias(device, via, None)

    @keyword('connect to device "${device:[^"]+}" as alias "${alias:[^"]+}"')
    def connect_alias_to_device(self, device, alias):
        """ Connect to a device via non-default alias. """
        self.connect_via_to_device_as_alias(device, None, alias)

    @keyword('connect to device "${device:[^"]+}" via "${via:[^"]+}" as alias "${alias}"')
    def connect_via_to_device_as_alias(self, device=None, via=None, alias=None):
        """ Create a new alias by connecting to a device via non-default connection """
        device = self._search_device(device)
        kwargs = {}
        if self.connect_kwargs:
            kwargs.update(self.connect_kwargs)
        if alias:
            kwargs['alias'] = alias
        if via:
            kwargs['via'] = via

        log.info("Connecting to device '{}'".format(device))
        log.info("kwargs: {}".format(kwargs))
        device.connect(**kwargs)

    @keyword('disconnect from device "${device:[^"]+}"')
    def disconnect_from_device(self, device=None):
        """ Disconnect from device with default alias """
        self.disconnect_from_device_with_alias(device=device, alias=None)

    @keyword('disconnect from devices "${devices:[^"]+}"')
    def disconnect_from_devices(self, devices=None):
        """ Disconnect from devices with default alias.
        Specify devices with semi-colon separated list, e.g. "R1;R2"
        """
        devices = [d.strip() for d in devices.split(';')]
        for device in devices:
            self.disconnect_from_device_with_alias(device=device, alias=None)

    @keyword('disconnect from all devices')
    def disconnect_from_devices(self):
        """ Disconnect from all devices with default alias.
        """
        devices = self.testbed.devices
        for device in devices:
            self.disconnect_from_device_with_alias(device=device, alias=None)

    @keyword('disconnect from device "${device:[^"]+}" with alias "${alias}"')
    def disconnect_from_device_with_alias(self, device=None, alias=None):
        """ Disconnect from device using alias """
        device = self._search_device(device)
        if alias and hasattr(device, alias):
            con = getattr(device, alias, None)
            if con is None:
                raise ValueError("Invalid alias {} for device {}".format(device, alias))
            con.disconnect()
        else:
            device.disconnect()

    def _search_device(self, name):
        try:
            # Find hostname and alias
            return self.testbed.devices[name]
        except KeyError:
            raise KeyError("Unknown device {}".format(name))


# Script Holder
class Script(object):
    pass
