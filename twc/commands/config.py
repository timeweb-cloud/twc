"""CLI configuration."""

import os
import sys
import ctypes

import toml
import click

from . import options, get_default_config_file, GLOBAL_OPTIONS, DEFAULT_CONFIG


def make_config(filepath: str = get_default_config_file()):
    """Create new configuration file."""
    if os.path.exists(filepath):
        sys.exit(f"File '{filepath}' already exists.")
    else:
        click.echo("Create new configuration file. Enter your API token.")
        while True:
            token = input("Token: ")
            if token:
                DEFAULT_CONFIG.update({"default": {"token": token}})
                break
            click.echo("Please enter token. Press ^C to cancel.")
        try:
            with open(filepath, "w", encoding="utf-8") as file:
                toml.dump(DEFAULT_CONFIG, file)
            if os.name == "nt":
                hidden_file_attr = 0x02
                ctypes.windll.kernel32.SetFileAttributesW(
                    filepath, hidden_file_attr
                )
            click.echo(f"Success! Configuration is saved in {filepath}")
        except OSError as error:
            sys.exit(f"Error: {error}")


# ------------------------------------------------------------- #
# $ twc config                                                  #
# ------------------------------------------------------------- #


@click.command("config", help="Make new configuration file.")
@options(GLOBAL_OPTIONS[:2])
def config():
    make_config()
