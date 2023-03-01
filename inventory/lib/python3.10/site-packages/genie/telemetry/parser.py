'''Parser Module

Module to handle all command-line parsing functionality/behavior

(standardization of how parsing at the command line is done, consolidate logic)
'''

import os
import sys
import uuid
import logging
import re as re

from pyats.utils import parser
from gettext import gettext

from genie.telemetry.email import MailBot
from genie.telemetry.config import Configuration

# declare module as infra
__genietelemetry_infra__ = True

CLI_DESCRIPTION = '''\
genie telemetry command line arguments.

Example
-------
  %(prog)s /path/to/testbed.yaml

--------------------------------------------------------------------------------
'''

class Parser(parser.ArgsPropagationParser):

    def __init__(self):

        # call ArgumentParser.__init__
        super().__init__(add_help = False)
                         
        # customize internals
        self.formatter_class = ParserFormatter
        self.prog = os.path.basename(sys.argv[0])
        self.description = CLI_DESCRIPTION % {'prog': self.prog}
        self.epilog = None

        # help me
        # -------
        # (custom help me including plugin's arguments)
        help_grp = self.add_argument_group('Help')
        help_grp.add_argument('-h', '-help',
                              action = 'help',
                              help = 'show this help message and exit')

        # testbed_file args
        # ------------
        self.add_argument('testbedfile',
                          nargs = '?',
                          metavar = 'TESTBEDFILE',
                          action = "store",
                          help = 'testbed file to be monitored')

        # modify titles
        self._optionals.title = 'Optional Arguments'
        self._positionals.title = 'Positional Arguments'

        # logging args
        # ------------
        log_grp = self.add_argument_group('Logging')
        log_grp.add_argument('-loglevel',
                             choices = ('CRITICAL', 'ERROR', 
                                        'WARNING', 'INFO', 'DEBUG'),
                             metavar = '',
                             default = logging.INFO,
                             help = 'genie telemetry logging level\n'
                                    'eg: -loglevel="INFO"')

        # configuration args
        # ------------
        config_grp = self.add_argument_group('Configuration')
        config_grp.add_argument('-configuration',
                                type = parser.FileType('r'),
                                metavar = 'FILE',
                                help = 'configuration yaml file for plugins and'
                                       ' settings')
        # uid args
        # ------------
        config_grp.add_argument('-uid',
                                action = "store",
                                default = str(uuid.uuid4()),
                                help = 'Specify monitoring job uid')
        # runinfo_dir args
        # ------------
        config_grp.add_argument('-runinfo_dir',
                                action = "store",
                                default = None,
                                help = 'Specify directory to store execution '
                                       'logs')
        # callback_notify args
        # ------------
        config_grp.add_argument('-callback_notify',
                                action = "store",
                                default = '',
                                help = 'Specify Liveview callback notify URI')
        # timeout args
        # ------------
        config_grp.add_argument('-timeout',
                                action = "store",
                                default = 300,
                                help = 'Specify plugin maximum execution '
                                       'length\nDefault to 300 seconds')
        # connection_timeout args
        # ------------
        config_grp.add_argument('-connection_timeout',
                                action = "store",
                                default = 10,
                                help = 'Specify connection timeout')


    def _get_subsystems(self):

        # build list of core component classes
        subsystems = [ MailBot ]

        # build list of plugin classes
        config = Configuration.parser.parse_args().configuration
        if config:
            plugins = Configuration().load_plugin_classess(config=config)
            subsystems.extend(plugins)

        return subsystems

    def format_usage(self):
        # start with the base parser args
        actions = self._actions.copy()
        mut_excl_grp = self._mutually_exclusive_groups.copy()

        # create a formatter
        formatter = self._get_formatter()

        # add usage
        formatter.add_usage(self.usage, actions, mut_excl_grp)

        return formatter.format_help()

    def format_help(self):
        subsystems = self._get_subsystems()
        # start with the base parser args
        actions = self._actions.copy()
        mut_excl_grp = self._mutually_exclusive_groups.copy()

        # include subsystem parsers
        for subsystem in subsystems:
            actions += subsystem.parser._actions
            mut_excl_grp += subsystem.parser._mutually_exclusive_groups

        # create a formatter
        formatter = self._get_formatter()

        # add usage
        formatter.add_usage(self.usage, actions, mut_excl_grp)

        # add general description
        formatter.add_text(self.description)
        
        # add this parser's argument groups
        for action_group in self._action_groups:
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()

        # add subsystem parserargument groups
        for subsystem in subsystems:

            # get the parser
            # (this is important because they are classproperty)
            # (eg, each call returns a new parser instance)
            parser = subsystem.parser

            # try to get subsystem.parser title
            # default to subsystem name if available, or just class name
            title = getattr(subsystem.parser, 'title', 
                            getattr(subsystem, 'name', 
                                    subsystem.__class__.__name__))

            formatter.start_section(title)

            for group in parser._action_groups:
                if group in (parser._positionals, parser._optionals):
                    # standard positiona/optional arguments
                    formatter.add_arguments(group._group_actions)
                else:
                    # add a new section for each sub-group
                    formatter.start_section(group.title)
                    formatter.add_text(group.description)
                    formatter.add_arguments(group._group_actions)
                    formatter.end_section()

            formatter.end_section()

        # epilog
        formatter.add_text(self.epilog)

        # determine help from format above
        return formatter.format_help()


class ParserFormatter(parser.RawTextHelpFormatter):

    def _format_usage(self, usage, actions, groups, prefix):
        '''_format_usage

        Basically the exact same as parent class's _format_usage - except the
        positional arguments now show up before optional arguments in the usage
        text.

        This is needed as GenieTelemetry parser is a multiple stack/stage parser.

        '''
        
        if prefix is None:
            prefix = gettext('usage: ')

        # if usage is specified, use that
        if usage is not None:
            usage = usage % dict(prog=self._prog)

        # if no optionals or positionals are available, usage is just prog
        elif usage is None and not actions:
            usage = '%(prog)s' % dict(prog=self._prog)

        # if optionals and positionals are available, calculate usage
        elif usage is None:
            prog = '%(prog)s' % dict(prog=self._prog)

            # split optionals from positionals
            optionals = []
            positionals = []
            for action in actions:
                if action.option_strings:
                    optionals.append(action)
                else:
                    positionals.append(action)

            # build full usage string
            format = self._format_actions_usage
            action_usage = format(positionals + optionals, groups)
            usage = ' '.join([s for s in [prog, action_usage] if s])

            # wrap the usage parts if it's too long
            text_width = self._width - self._current_indent
            if len(prefix) + len(usage) > text_width:

                # break usage into wrappable parts
                part_regexp = r'\(.*?\)+|\[.*?\]+|\S+'
                opt_usage = format(optionals, groups)
                pos_usage = format(positionals, groups)
                opt_parts = re.findall(part_regexp, opt_usage)
                pos_parts = re.findall(part_regexp, pos_usage)
                assert ' '.join(opt_parts) == opt_usage
                assert ' '.join(pos_parts) == pos_usage

                # helper for wrapping lines
                def get_lines(parts, indent, prefix=None):
                    lines = []
                    line = []
                    if prefix is not None:
                        line_len = len(prefix) - 1
                    else:
                        line_len = len(indent) - 1
                    for part in parts:
                        if line_len + 1 + len(part) > text_width and line:
                            lines.append(indent + ' '.join(line))
                            line = []
                            line_len = len(indent) - 1
                        line.append(part)
                        line_len += len(part) + 1
                    if line:
                        lines.append(indent + ' '.join(line))
                    if prefix is not None:
                        lines[0] = lines[0][len(indent):]
                    return lines

                # if prog is short, follow it with optionals or positionals
                if len(prefix) + len(prog) <= 0.75 * text_width:
                    indent = ' ' * (len(prefix) + len(prog) + 1)
                    
                    if pos_parts:
                        lines = get_lines([prog] + pos_parts, indent, prefix)
                        lines.extend(get_lines(opt_parts, indent))
                    elif opt_parts:
                        lines = get_lines([prog] + opt_parts, indent, prefix)
                    else:
                        lines = [prog]

                # if prog is long, put it on its own line
                else:
                    indent = ' ' * len(prefix)
                    parts = pos_parts + opt_parts
                    lines = get_lines(parts, indent)
                    if len(lines) > 1:
                        lines = []
                        lines.extend(get_lines(pos_parts, indent))
                        lines.extend(get_lines(opt_parts, indent))
                    lines = [prog] + lines

                # join lines into usage
                usage = '\n'.join(lines)

        # prefix with 'usage:'
        return '%s%s\n\n' % (prefix, usage)

