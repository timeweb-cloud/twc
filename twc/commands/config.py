"""CLI configuration."""

import os
import sys
import ctypes
import json

import yaml
import toml
import click
from click_default_group import DefaultGroup

from twc import fmt
from twc import utils
from twc.vars import DEFAULT_CONFIG
from . import (
    options,
    load_config,
    get_default_config_file,
    GLOBAL_OPTIONS,
)


def write_to_file(data: str, filepath: str):
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            toml.dump(data, file)
        if os.name == "nt":
            hidden_file_attr = 0x02
            ctypes.windll.kernel32.SetFileAttributesW(
                filepath, hidden_file_attr
            )
        click.echo(f"Done! Configuration is saved in {filepath}")
        sys.exit(0)
    except OSError as error:
        sys.exit(f"Error: {error}")


def make_config(filepath: str = get_default_config_file()):
    """Create new configuration file."""
    if os.path.exists(filepath):
        if click.confirm(
            "You already have TWC CLI configured, continue?",
            default=False,
        ):
            current_config = load_config()
            profile = click.prompt("Enter profile name", default="default")
            token = click.prompt(f"Enter API token for '{profile}'")
            current_config[profile] = utils.merge_dicts(
                current_config[profile],
                {"token": token},
            )
            write_to_file(current_config, filepath)
        else:
            sys.exit("Aborted!")

    click.echo("Create new configuration file. Enter your API token.")
    while True:
        token = input("Token: ")
        if token:
            DEFAULT_CONFIG.update({"default": {"token": token}})
            break
        click.echo("Please enter token. Press ^C to cancel.")
    write_to_file(DEFAULT_CONFIG, filepath)


# ------------------------------------------------------------- #
# $ twc config                                                  #
# ------------------------------------------------------------- #


@click.group(
    "config", cls=DefaultGroup, default="init", default_if_no_args=True
)
@options(GLOBAL_OPTIONS[:2])
def config():
    """Manage CLI configuration."""


# ------------------------------------------------------------- #
# $ twc config init                                             #
# ------------------------------------------------------------- #


@config.command("init", help="Create confiration file and profile.")
@options(GLOBAL_OPTIONS[:2])
def config_init():
    make_config()


# ------------------------------------------------------------- #
# $ twc config file                                             #
# ------------------------------------------------------------- #


@config.command("file", help="Display path to configuration file.")
@options(GLOBAL_OPTIONS[:4])
def config_file(config, verbose):
    click.echo(click.format_filename(config.encode()))


# ------------------------------------------------------------- #
# $ twc config dump                                             #
# ------------------------------------------------------------- #


@config.command("dump", help="Dump configuration.")
@options(GLOBAL_OPTIONS)
@click.option(
    "--full", "full_dump", is_flag=True, help="Dump full configuration."
)
@click.option(
    "--output",
    "-o",
    "output_format",
    type=click.Choice(["toml", "yaml", "json"]),
    default="toml",
    show_default=True,
    help="Output format.",
)
def config_dump(config, profile, verbose, full_dump, output_format):
    if full_dump:
        config_dict = load_config(config)
    else:
        config_dict = load_config(config)[profile]

    if output_format == "toml":
        fmt.print_colored(toml.dumps(config_dict), lang="toml")
    elif output_format == "yaml":
        fmt.print_colored(yaml.dump(config_dict), lang="yaml")
    elif output_format == "json":
        fmt.print_colored(json.dumps(config_dict), lang="json")


# ------------------------------------------------------------- #
# $ twc config set                                              #
# ------------------------------------------------------------- #


@config.command("set", help="Set config parameter.")
@options(GLOBAL_OPTIONS)
@click.argument("params", nargs=-1, metavar="PARAM=VALUE")
def config_set(config, profile, verbose, params):
    if not params:
        raise click.UsageError("Nothing to do.")
    config_dict = load_config(config)
    params_dict = {}
    for param in params:
        key, value = param.split("=")
        if value.isdigit():
            value = int(value)
        params_dict[key] = value
    config_dict[profile] = utils.merge_dicts(config_dict[profile], params_dict)
    write_to_file(config_dict, config)


# ------------------------------------------------------------- #
# $ twc config edit                                             #
# ------------------------------------------------------------- #


@config.command("edit", help="Open config file in default editor.")
@options(GLOBAL_OPTIONS[:4])
def config_edit(config, verbose):
    click.launch(config)
