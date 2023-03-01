
import getpass
from ipaddress import IPv4Interface, IPv6Interface, ip_address

from pyats.utils.schemaengine import (
    Or,
    Any,
    Use,
    Optional,
    Schema,
    Use,
    And,
    Default,
    Fallback
)
from pyats.utils.exceptions import SchemaError
from pyats.utils.import_utils import import_from_name, translate_host

# declare module as infra
__genietelemetry_infra__ = True

def str_or_list(value):
    '''check_file

    translates str/list into list.
    '''

    if isinstance(value, str):
        # convert string to list
        value = [value, ]

    return value


def validate_plugins(data):
    try:
        assert type(data) is dict

        for plugin, config in data.items():
            assert type(config) is dict

            assert 'module' in config

            assert type(config['module']) is str

            # by default all plugins are always enabled and 30 seconds interval
            config.setdefault('enabled', True)
            config.setdefault('interval', 30)
            config.setdefault('devices', []) # plugin device filter
            # Check if user passed in plugin_arguments through YAML
            config.setdefault('plugin_arguments', {})

            assert type(config['devices']) is list

            # build the plugin arguments
            # If user given any arg not defined in the yaml file,
            # it is passes as kwargs to the __init__ of the plugins
            kwargs = {}

            for key, value in list(config.items()):
                if key in ('enabled', 'module', 'interval', 'devices',
                           'plugin_arguments'):
                    continue

                kwargs[key] = config.pop(key)

            # Basically, plugin name = class name.
            # let's find it inside the loaded module
            config['module'] = import_from_name(config['module'])
            config['kwargs'] = kwargs
            config['name'] = plugin

    except Exception as e:
        raise SchemaError("Invalid genietelemetry_config.yaml input for "
                          "plugins") from e
    return data

config_schema = {
    Optional("plugins"): Use(validate_plugins),
    Optional('connections'): {
        Any(): {
            Optional('via'): str,
            Optional('alias'): str,
        },
    },
    Any(): Any(),
}


testbed_schema = {
    Optional('extends'): Use(str_or_list), # extends file or list of files

    'testbed': {
        Optional('name'): str,
        Optional('alias'): str,
        Optional('class'): Use(import_from_name),
        'tacacs': {
            'login_prompt': Default(str, 'login:'),
            'password_prompt': Default(str, 'Password:'),
            'username': Default(str, getpass.getuser()),
        },
        'passwords': {
            'tacacs': Default(str, 'lab'),
            'enable': Default(str, 'lab'),
            'line': Default(str, 'lab'),
            'linux': Default(str, 'lab'),
        },
        Optional('custom'): dict,
        Optional('servers'): {
            Any(): {
                Optional('server'): str,
                Optional('type'): str,
                Optional('address'): str,
                Optional('path'): str,
                Optional('username'): str,
                Optional('password'): str,
                Optional('laas'): {
                    Optional('port'): int,
                    Optional('notification_port'): int,
                    Optional('image_dir'): str,
                },
                Optional('custom'): dict,
            },
        },
        Optional('network'): Any(),
        Optional('iou'): {
            Optional('iou_flags'): str,
            Optional('iou'): str,
        },
        Optional('bringup'): {
            Optional('xrut'): {
                'sim_dir': str,
                'base_dir': str,
            },
        },
        Optional('testbed_file'): str, # not to be filled by hand
    },

    'devices': {
        Any() : {
            'type': str,
            Optional('class'): Use(import_from_name),
            Optional('alias'): str,
            Optional('region'): str,
            Optional('role'): str,
            Optional('os'): str,
            Optional('series'): str,
            Optional('model'): str,
            Optional('power'): str,
            Optional('hardware'): Any(),
            'tacacs': {
                'login_prompt': Fallback(str, 'testbed.tacacs.login_prompt'),
                'password_prompt':
                                Fallback(str, 'testbed.tacacs.password_prompt'),
                'username': Fallback(str, 'testbed.tacacs.username'),
            },
            'passwords': {
                'tacacs': Fallback(str, 'testbed.passwords.tacacs'),
                'enable': Fallback(str, 'testbed.passwords.enable'),
                'line': Fallback(str, 'testbed.passwords.line'),
                'linux': Fallback(str, 'testbed.passwords.linux'),
            },
            'connections': {
                Optional('defaults'): {
                    Optional('class'): Use(import_from_name),
                    Optional('alias'): str,
                    Optional('via'): str,
                },
                Any(): {
                    Optional('class'): Use(import_from_name),
                    Optional('protocol'): str,
                    Optional('ip'): And(Use(translate_host), ip_address),
                    Any(): Any(),
                },
            },
            Optional('clean'): dict,
            Optional('auto_bringup'): dict,
            Optional('custom'): dict,
            Any(): Any(),
        },
    },

    Optional('topology'): {
        Optional('links'): {
            Any(): {
                Optional('class'): Use(import_from_name),
                Optional('alias'): str,
                Any(): Any(),
            }
        },
        Any(): {
            'interfaces': {
                Any(): {
                    'type': str,
                    Optional('alias'): str,
                    Optional('class'): Use(import_from_name),
                    Optional('link'): str,
                    Optional('ipv4'): IPv4Interface,
                    Optional('ipv6'): IPv6Interface,
                    Any(): Any(),
                },
            },
        },
    },
}