from ...base import CommandWithSubcommands

from .abstract import MigrateAbstractCommand

class MigrateCommand(CommandWithSubcommands):

    name = 'migrate'
    help = 'utilities for migrating to future versions of pyATS'

    SUBCOMMANDS = [MigrateAbstractCommand]
    SUBCMDS_ENTRYPOINT = 'pyats.cli.commands.migrate'
