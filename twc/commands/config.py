"""Manage CLI configuration."""

import re
import os
import sys
import ctypes
import json
from typing import Optional, List
from enum import Enum
from pathlib import Path

import typer
import toml
import yaml

from twc.utils import merge_dicts
from twc.fmt import print_colored
from .common import (
    default_config_file,
    load_config,
    config_callback,
    config_option,
    profile_option,
)


config = typer.Typer(help=__doc__, no_args_is_help=False)


DEFAULT_CONFIG = {"default": {"token": None}}


def write_to_file(data: dict, filepath: Path) -> None:
    """Dump `data` dict into TOML and write into file."""
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            toml.dump(data, file)
        if os.name == "nt":
            hidden_file_attr = 0x02
            ctypes.windll.kernel32.SetFileAttributesW(
                filepath, hidden_file_attr
            )
        print(f"Done! Configuration is saved in {filepath}")
        sys.exit(0)
    except OSError as error:
        sys.exit(f"Error: Cannot write configration file: {error}")


def make_config(filepath: Path = default_config_file()) -> None:
    """Create new configuration file or edit existing profile token."""
    # Edit existing file
    if os.path.exists(filepath):
        if typer.confirm(
            "You already have TWC CLI configured, continue?",
            default=False,
        ):
            current_config = load_config()
            profile = typer.prompt("Enter profile name", default="default")
            token = typer.prompt(f"Enter API token for '{profile}'")
            try:
                # Edit existing profile
                current_config[profile] = merge_dicts(
                    current_config[profile],
                    {"token": token},
                )
            except KeyError:
                # Add new profile
                current_config[profile] = {}  # init new config section
                current_config[profile] = merge_dicts(
                    current_config[profile],
                    {"token": token},
                )
            write_to_file(current_config, filepath)
        else:
            sys.exit("Aborted!")
    # Make new file
    print("Create new configuration file. Enter your API token.")
    while True:
        token = input("Token: ")
        if token:
            DEFAULT_CONFIG.update({"default": {"token": token}})
            break
        print("Please enter token. Press ^C to cancel.")
    write_to_file(DEFAULT_CONFIG, filepath)


# ------------------------------------------------------------- #
# $ twc config                                                  #
# ------------------------------------------------------------- #


@config.callback(invoke_without_command=True)
def config_root_cmd(ctx: typer.Context):
    """Make new configuration file if not exist or edit existing."""
    if ctx.invoked_subcommand is None:
        make_config()


# ------------------------------------------------------------- #
# $ twc config init                                             #
# ------------------------------------------------------------- #


@config.command("init")
def config_init():
    """Make new configuration file if not exist or edit existing."""
    make_config()


# ------------------------------------------------------------- #
# $ twc config file                                             #
# ------------------------------------------------------------- #


@config.command("file")
def config_file(
    # pylint: disable=redefined-outer-name
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        envvar="TWC_CONFIG_FILE",
        show_envvar=False,
        exists=True,
        dir_okay=False,
        callback=config_callback,
        hidden=True,
        help="Use config.",
    ),
    locate: bool = typer.Option(
        False, "--locate", help="Open file directory in file manager."
    ),
):
    """Print config file path."""
    print(config)
    if locate:
        typer.launch(str(config), locate=True)


# ------------------------------------------------------------- #
# $ twc config dump                                             #
# ------------------------------------------------------------- #


class DumpFormat(str, Enum):
    """Configuration file format variants."""

    TOML = "toml"
    YAML = "yaml"
    JSON = "json"


@config.command("dump")
def config_dump(
    # pylint: disable=redefined-outer-name
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        envvar="TWC_CONFIG_FILE",
        show_envvar=False,
        exists=True,
        dir_okay=False,
        callback=config_callback,
        hidden=True,
        help="Use config.",
    ),
    profile: Optional[str] = profile_option,
    output_format: DumpFormat = typer.Option(
        DumpFormat.TOML.value,
        "--output",
        "-o",
        case_sensitive=False,
        help="Output format.",
    ),
    full_dump: bool = typer.Option(
        False, "--full", help="Dump full configuration."
    ),
):
    """Dump configuration."""
    if full_dump:
        config_dict = load_config(config)
    else:
        config_dict = load_config(config)[profile]

    encoders = {
        "toml": toml.dumps,
        "yaml": yaml.dump,
        "json": json.dumps,
    }

    print_colored(
        encoders[output_format.value](config_dict), lang=output_format.value
    )


# ------------------------------------------------------------- #
# $ twc config set                                              #
# ------------------------------------------------------------- #


def validate_params_callback(value: list) -> list:
    """Validate CLI configuration parameters."""
    for param in value:
        if not re.match(r"^[a-z0-9_]+=[a-z0-9-_.]+$", param, re.I):
            raise typer.BadParameter(
                f"'{param}': Parameter must be a KEY=VALUE pair."
            )
    return value


@config.command("set")
def config_set(
    params: List[str] = typer.Argument(
        ...,
        callback=validate_params_callback,
        help="List of KEY=VALUE parameters.",
    ),
    # pylint: disable=redefined-outer-name
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
):
    """Set config parameters."""
    config_dict = load_config(config)
    params_dict = {}
    for param in params:
        key, value = param.split("=")
        if value.isdigit():
            value = int(value)
        params_dict[key] = value
    config_dict[profile] = merge_dicts(config_dict[profile], params_dict)
    write_to_file(config_dict, config)


# ------------------------------------------------------------- #
# $ twc config unset                                            #
# ------------------------------------------------------------- #


@config.command("unset")
def config_unset(
    params: List[str] = typer.Argument(..., help="List of parameters."),
    # pylint: disable=redefined-outer-name
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
):
    """Unset config parameters."""
    config_dict = load_config(config)
    for param in params:
        try:
            del config_dict[profile][param]
        except KeyError:
            sys.exit(f"Error: No such key: '{param}'")
    write_to_file(config_dict, config)


# ------------------------------------------------------------- #
# $ twc config edit                                             #
# ------------------------------------------------------------- #


@config.command("edit")
def config_edit(
    # pylint: disable=redefined-outer-name
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        envvar="TWC_CONFIG_FILE",
        show_envvar=False,
        exists=True,
        dir_okay=False,
        callback=config_callback,
        hidden=True,
        help="Use config.",
    ),
):
    """Open configuration file in default editor."""
    typer.launch(str(config))


# ------------------------------------------------------------- #
# $ twc config profiles                                         #
# ------------------------------------------------------------- #


@config.command("profiles")
def config_profile(
    # pylint: disable=redefined-outer-name
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        envvar="TWC_CONFIG_FILE",
        show_envvar=False,
        exists=True,
        dir_okay=False,
        callback=config_callback,
        hidden=True,
        help="Use config.",
    ),
):
    """Display configuration profiles."""
    config_dict = load_config(config)
    for key in config_dict.keys():
        print(key)
