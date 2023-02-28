import sys
import logging
import importlib

try:
    from robot.api.deco import keyword
    from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError
except ImportError:
    sys.exit('ERROR: install robotframework package to enable the use of '
             'this package\n'
             'Eg: pip install unicon[robot]')

try:
    pcall = importlib.import_module('pyats.async').pcall
except ImportError:
    try:
        from pyats.async_ import pcall
    except ImportError:
        def pcall(*args, **kargs):
            raise RuntimeError('Cannot perform parallel calls without pyATS '
                                   'pyats.async module installed. \n'
                                   'Fix this with: pip install unicon[pyats]')

log = logging.getLogger(__name__)

class UniconRobot(object):
    """Unicon RobotFramework library

    This class uses the pyATS 'Unicon' library to interact with the CLI of devices.
    """
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    ROBOT_LIBRARY_DOC_FORMAT = 'reST'

    def __init__(self):
        """
        Attributes
            execute_timeout
            configure_timeout
            error_pattern
        """
        # save builtin so we dont have to re-create then everytime
        self.builtin = BuiltIn()

        # Arguments driving Unicon
        self.configure_timeout = None
        self.execute_timeout = None
        self.error_pattern = None

    @keyword('execute "${command}" on device "${device:[^"]+}"')
    def execute_command_on_device(self, command=None, device=None):
        """ Execute command on a specific device. "device" name is the name
        of the device from the testbed file """
        return self.execute_command_on_device_alias(command=command,
                                                    alias=None,
                                                    device=device)

    @keyword('execute "${command}" on devices "${devices}"')
    def execute_command_on_devices(self, command=None, devices=None):
        """ Execute the same command on multiple devices. Devices is a string
        ';' separated of devices, e.g. "R1;R2" Returns the output in a
        list """
        devices = [d.strip() for d in devices.split(';')]
        return [self.execute_command_on_device(command, device)\
                for device in devices]

    @keyword('execute "${command}" in parallel on devices "${devices}"')
    def execute_commands_in_parallel_on_device(self, command=None,
                                               devices=None):
        """ Execute a command in parallel on multiple devices. Devices is a
        string ';' separated of devices, e.g. "R1;R2"

        Returns the output in an ordered tuple where the output from the first device
        is in index 0, the second device in index 1 etc.  """

        devices = [d.strip() for d in devices.split(';')]
        return pcall(self.execute_command_on_device,
                     command=[command] * len(devices), device=devices)

    @keyword('execute "${command}" on device "${device}" '
             'using alias "${alias}"')
    def execute_command_on_device_alias(self, command=None, device=None,
                                        alias=None):
        """ Execute a CLI command on a specific session from a device. Before
        executing the command, enter/return is sent to get a prompt from the
        device. """

        log.info("Executing command {} on device {} "
                 "alias {}".format(command, device, alias))
        con = self._search_device(device, alias)

        kwargs = {}
        if self.error_pattern is not None:
            kwargs['error_pattern'] = self.error_pattern
        if self.execute_timeout:
            kwargs['timeout'] = self.execute_timeout

        return con.execute(command, **kwargs)

    @keyword('configure "${config:[^"]+}" on device "${device:[^"]+}"')
    def configure_device(self, config=None, device=None):
        """ Configure a device with the configuration provided. """
        return self.configure_config_on_device_alias(config, device, None)

    @keyword('configure "${config:[^"]+}" on devices "${devices:[^"]+}"')
    def configure_config_on_devices(self, config=None, devices=None):
        """ Configure the same config on multiple devices. Devices is a ';'
        separated list of devices, e.g. "R1;R2" Returns the output in a list
        """
        devices = [d.strip() for d in devices.split(';')]
        return [self.configure_config_on_device_alias(config, device, None)\
                for device in devices]

    @keyword('configure "${config:[^"]+}" in parallel on devices "${devices}"')
    def configure_configs_in_parallel_on_device(self, config=None,
                                                devices=None):
        """ Configure a config in parallel on multiple devices. Devices is a
         ';' separated list of devices, e.g. "R1;R2" """

        devices = [d.strip() for d in devices.split(';')]
        return pcall(self.configure_config_on_device_alias,
                     config=[config] * len(devices),
                     device=devices)

    @keyword('configure "${config}" on device "${device}" using alias '\
             '"${alias:[^"]+}"')
    def configure_config_on_device_alias(self, config=None, device=None,
                                         alias=None):
        """ Execute a CLI configuration on a specific alias from a device."""
        log.info("Configuring {} on device {} alias {}".format(config,
                                                               device,
                                                               alias))
        con = self._search_device(device, alias)

        kwargs = {}
        if self.error_pattern is not None:
            kwargs['error_pattern'] = self.error_pattern
        if self.configure_timeout:
            kwargs['timeout'] = self.configure_timeout

        return con.configure(config, **kwargs)

    @keyword('disable output logging for device "${device:[^"]+}" with '
             'alias "${alias:[^"]+}"')
    def disable_output_logging_alias(self, device=None, alias=None):
        """By default, unicon connection log all output when interacting
        with devices into log.html.  This keyword disables this behaviour. Use
        `enable output logging for device "${device}"` to re-enable it.
        """
        self._set_output_logging(device, alias, False)

    @keyword('enable output logging for device "${device:[^"]+}" using alias '
             '"${alias:[^"]+}"')
    def enable_output_logging_alias(self, device=None, alias=None):
        """Restore the default behaviour of logging all output when interacting
        with devices into log.html.
        """
        self._set_output_logging(device, alias, True)

    @keyword('disable output logging for device "${device:[^"]+}"')
    def disable_output_logging(self, device):
        """By default, unicon connection log all output when interacting with
        devices into log.html.  This keyword disables this behaviour. Use
        `enable output logging for device "${device}"` to re-enable it.
        """
        self._set_output_logging(device, None, False)

    @keyword('enable output logging for device "${device:[^"]+}"')
    def enable_output_logging(self, device):
        """Restore the default behaviour of logging all output when interacting
        with devices into log.html.  """
        self._set_output_logging(device, None, True)

    def _set_output_logging(self, device, alias, val):
        con = self._search_device(device, alias)
        con.log_user(enable=val)

    @keyword('send ctrl-${char} to device "${device:[^"]+}"')
    def send_control_c(self, char=None, device=None):
        """ Send Ctrl-<char> to the device.
        Supported characters: ``ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_``
        See https://en.wikipedia.org/wiki/C0_and_C1_control_codes#C0_(ASCII_and_derivatives)
        """
        return self.send_control_c_alias(char, device, None)

    @keyword('send ctrl-${char} to device "${device}" using alias "${alias}"')
    def send_control_c_alias(self, char=None, device=None, alias=None):
        """ Send Ctrl-<char> to the device.
        Supported characters: ``'ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_'``
        See https://en.wikipedia.org/wiki/C0_and_C1_control_codes#C0_(ASCII_and_derivatives)
        """
        control_characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_'

        CONTROL_CHAR = control_characters.find(char.upper())
        if CONTROL_CHAR < 0:
            raise ValueError('Unsupported control character %s' % char)
        else:
            con = self._search_device(device, alias)
            con.send(chr(CONTROL_CHAR+1))

    @keyword('send "${command}" to device "${device:[^"]+}"')
    def send_command_to_device(self, command=None, device=None):
        """ Send a command string (without RETURN) to the device """
        return self.send_command_to_device_with_alias(command, device, None)

    @keyword('send "${command}" to device "${device:[^"]+}" using alias '
             '"${alias}"')
    def send_command_to_device_with_alias(self, command=None, device=None,
                                          alias=None):
        """ Send a command string (without RETURN) to the device using alias """
        con = self._search_device(device, alias)
        return con.send(command)

    @keyword('set unicon execute timeout to "${execute_timeout}" seconds')
    def set_variable_execute_timeout(self, execute_timeout=None):
        """ Set the default execute_timeout for commands """
        log.info("Variable timeout set to {} seconds".format(execute_timeout))
        self.execute_timeout = execute_timeout

    @keyword('set unicon configure timeout to "${configure_timeout}" seconds')
    def set_variable_configure_timeout(self, configure_timeout=None):
        """ Set the default configure_timeout for commands """
        log.info("Variable configure timeout set to {} "
                 "seconds".format(configure_timeout))
        self.configure_timeout = configure_timeout

    @keyword('set unicon error pattern to "${error_pattern}"')
    def set_command_error_pattern(self, error_pattern=None):
        """ Set the default error_pattern for commands """
        log.info("Variable error pattern set to {}".format(error_pattern))
        self.error_pattern = error_pattern

    @keyword('set unicon setting "${key}" "${value}" on device "${device:[^"]+}"')
    def set_unicon_settings(self, key=None, value=None, device=None):
        self.set_unicon_settings_via_alias(key, value, device, None, None)

    @keyword('set unicon setting "${key}" "${value}" on device "${device} via "${via:[^"]+}"')
    def set_unicon_settings_via(self, key=None, value=None, device=None, via=None):
        self.set_unicon_settings_via_alias(key, value, device, via, None)

    @keyword('set unicon setting "${key}" "${value}" on device "${device:[^"]+} as alias "${alias}"')
    def set_unicon_settings_alias(self, key=None, value=None, device=None, alias=None):
        self.set_unicon_settings_via_alias(key, value, device, None, alias)

    @keyword('set unicon setting "${key}" "${value}" on device "${device} via "${via:[^"]+}" as alias "${alias}"')
    def set_unicon_settings_via_alias(self, key=None, value=None, device=None, via=None, alias=None):
        log.info("Setting {} to {}".format(key, value))
        try:
            con = self._search_device(device, alias)
        except Exception:
            # Alright no alias, then just use the device
            con = device

        # Is it connected?
        if not con.is_connected():
            con.instantiate()

        setattr(con.settings, key, value)

    @keyword('switch to vdc "${vdc}" on device "${device:[^"]+}"')
    def switch_to_vdc(self, vdc, device):
        """Use NXOS service 'switchto' to switch to a vpc on a device"""
        log.info("Switching to VDC {} on {}".format(vdc, device))
        self._search_device(device, None).switchto(vdc)

    @keyword('switch to vdc "${vdc}" on device "${device:[^"]+}" as alias "${alias:[^"]+}"')
    def switch_to_vdc_with_alias(self, vdc, device, alias):
        """Use NXOS service 'switchto' to switch to a vpc on a device using an alias"""
        log.info("Switching to VDC {} on {}".format(vdc, device))
        self._search_device(device, alias).switchto(vdc)

    @keyword('switchback to default vdc on device "${device:[^"]+}"')
    def switchback_to_default_vdc(self, device):
        """Use NXOS service 'switchback' to switch to a default vpc on a device"""
        log.info("Switching back to default VDC on device".format(device))
        self._search_device(device, None).switchback()

    @keyword('switchback to default vdc on device "${device:[^"]+}" as alias "${alias:[^"]+}"')
    def switchback_to_default_vdc_with_alias(self, device, alias):
        """Use NXOS service 'switchback' to switch to a default vpc on a device"""
        log.info("Switching back to default VDC on device".format(device))
        self._search_device(device, alias).switchback()

    @keyword('switch to state on device')
    def switch_to_state(self, **kwargs):
        """Use the 'switchto' service to switch to a state on a device

        Examples:

        .. code:: robotframework

            switch to state on device  state=enable   device=Firewall1
            switch to state on device  state=chassis  device=Firewall2   alias=connection2

        """
        device = kwargs.get('device')
        alias = kwargs.get('alias')
        state = kwargs.get('state')

        if device is None or state is None:
            raise RuntimeError("Missing 'device' or 'state' argument")

        log.info("Switching to state '{}' on '{}' with alias '{}'".format(state, device, alias))
        self._search_device(device, alias).switchto(state)

    def _search_device(self, name, alias):
        try:
            testbed = self.builtin.get_library_instance('pyats.robot.'
                                                        'pyATSRobot').testbed
        except RuntimeError as e:
            try:
                testbed = self.builtin.get_library_instance('ats.robot.'
                                                          'pyATSRobot').testbed
            except RuntimeError as e:
                # no pyATS
                raise RuntimeError("It is mandatory to have "
                                   "'Library pyats.robot."
                                   "pyATSRobot' in the Setting section.")
        except AttributeError as e:
            raise AttributeError("Could not find 'testbed' within "
                                 "pyATS library") from e

        try:
            # Find hostname and alias
            device = testbed.devices[name]
        except KeyError:
            raise KeyError("Unknown device {}".format(name))

        # Look for the alias. If it doesnt exist,  let it crash to the user as
        # only valid alias should be provided
        if alias:
            return getattr(device, alias)
        return device
