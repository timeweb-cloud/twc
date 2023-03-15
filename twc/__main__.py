"""Command Line Interface initial module."""

import click

from .commands import options, GLOBAL_OPTIONS
from .commands.account import account
from .commands.config import config
from .commands.server import server
from .commands.ssh_key import ssh_key
from .commands.image import image
from .commands.project import project


@click.group()
@options(GLOBAL_OPTIONS[:2])
def cli():
    """Timeweb Cloud Command Line Interface."""


cli.add_command(account)
cli.add_command(config)
cli.add_command(server)
cli.add_command(ssh_key)
cli.add_command(image)
cli.add_command(project)
