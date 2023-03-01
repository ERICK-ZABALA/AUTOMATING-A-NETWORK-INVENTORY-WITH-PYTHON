import yaml
import traceback
from pyats.datastructures import OrderableDict

# declare module as infra
__genietelemetry_infra__ = True

ESCAPE_STD = (("&", "&amp;"),
              ("<", "&lt;"),
              (">", "&gt;"),
              ("\"", "&quot;"),
              ("\n", "\u000A"))

def escape(stdinput):
    # liveview stream character escape
    for esc in ESCAPE_STD:
        stdinput = stdinput.replace(*esc)

    return stdinput


def filter_exception(exc_type, exc_value, tb):
    '''filter_exception

    Filters an exception's traceback stack and removes genie telemetry stack
    frames from it to make it more apparent that the error came from a script.
    Should be only used on user-script errors, and must not be used when an
    error is caught from genie.telemetry infra itself.

    Any frame with __genietelemetry_infra__ flag set is considered
    genie.telemetry infra stack.

    Returns
    -------
        properly formatted exception message with stack trace, with
        genie.telemetry stacks removed

    '''

    # Skip GenieTelemetry traceback levels
    while tb and tb.tb_frame.f_globals.get('__genietelemetry_infra__', False):
        tb = tb.tb_next

    # return the formatted exception
    return ''.join(traceback.format_exception(exc_type, exc_value, tb)).strip()

def ordered_yaml_dump(data,
                      stream=None,
                      Dumper=yaml.SafeDumper,
                      **kwds):

    class OrderedYamlDumper(Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
                        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                        data.items())

    OrderedYamlDumper.add_representer(OrderableDict, _dict_representer)

    return yaml.dump(data, stream, OrderedYamlDumper, **kwds)

def get_plugin_name(plugin):
    return getattr(plugin, 'name', getattr(plugin, '__plugin_name__',
                                   getattr(plugin, '__module__',
                                   type(plugin).__name__)))