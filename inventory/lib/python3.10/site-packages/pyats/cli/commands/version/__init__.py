from ...base import CommandWithSubcommands

from .check import VersionCheckSubCommand
from .update import VersionUpdateCommand

class VersionCommand(CommandWithSubcommands):

    name = 'version'
    help = 'commands related to version display and manipulation'
    
    SUBCOMMANDS = [VersionCheckSubCommand,
                   VersionUpdateCommand]
    SUBCMDS_ENTRYPOINT = 'pyats.cli.commands.version'
