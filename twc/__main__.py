"""Command Line Interface initial module."""

from gettext import gettext as _

import click

from .commands import options, GLOBAL_OPTIONS
from .commands.account import account
from .commands.config import config
from .commands.server import server
from .commands.ssh_key import ssh_key
from .commands.image import image
from .commands.project import project
from .commands.database import database


class AliasedCmdGroup(click.Group):
    """Add aliases for Click commands. Needs a global variable
    ALIASES with dict. Exmaple:

    @click.group(cls=AliasedCmdGroup)
    def cli():
        '''CLI.'''

    cli.add_command(my_cmd)
    ALIASES = {"my-cmd-alias": my_cmd}
    """

    def get_command(self, ctx, cmd_name):
        """Add aliased commands to parser."""
        try:
            cmd_name = ALIASES[cmd_name].name
        except KeyError:
            pass
        return super().get_command(ctx, cmd_name)

    def format_commands(self, ctx, formatter) -> None:
        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            if cmd is None:
                continue
            if cmd.hidden:
                continue
            commands.append((subcommand, cmd))

        if len(commands):
            limit = formatter.width - 6 - max(len(cmd[0]) for cmd in commands)
            rows = []
            for subcommand, cmd in commands:
                # Get command alias
                alias = ""
                for a in list(ALIASES.keys()):
                    if ALIASES[a].name == cmd.name:
                        alias = f" ({a})"
                help = cmd.get_short_help_str(limit)
                rows.append((subcommand + alias, help))
            if rows:
                with formatter.section(_("Commands")):
                    formatter.write_dl(rows)


@click.group(cls=AliasedCmdGroup)
@options(GLOBAL_OPTIONS[:2])
def cli():
    """Timeweb Cloud Command Line Interface."""


cli.add_command(account)
cli.add_command(config)
cli.add_command(server)
cli.add_command(ssh_key)
cli.add_command(image)
cli.add_command(project)
cli.add_command(database)


# -- Aliases list for root level commands. --
# If there are several aliases, only the last one will
# be printed in the help text.
ALIASES = {
    "servers": server,
    "s": server,
    "keys": ssh_key,
    "k": ssh_key,
    "images": image,
    "i": image,
    "projects": project,
    "p": project,
    "dbs": database,
    "db": database,
}
