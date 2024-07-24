"""Common functions for commands."""

import re
import sys
from enum import Enum
from typing import Optional, Any
from pathlib import Path, PurePath
from logging import basicConfig, debug, DEBUG

import toml
import typer
from typer.core import TyperOption
from click import UsageError

from twc.__version__ import __version__
from twc.api.types import ServiceRegion, ServiceAvailabilityZone


class OutputFormat(str, Enum):
    """Data output formats. See `output_format_option`."""

    DEFAULT = "default"
    RAW = "raw"
    JSON = "json"
    YAML = "yaml"


def get_root_ctx(ctx: typer.Context) -> typer.Context:
    """Return the context of the root command. This function allows you
    to retrieve the `typer.Context` object for the root command using the
    current context.

    Each command has its own context, which stores data about the command
    itself, all options and arguments entered by the user, and other service
    information.

    Each `typer.Context` object has a `parent` field that contains a
    reference to the parent context. Thus it is possible to collect all
    available contexts.

    Specifically, this function loops through the objects in the `parent`
    field until it reaches the root context, whose `parent` is None and
    returns it.

    See *_callback functions below for examples.
    """
    context = ctx
    while True:
        debug(f"cli_parser: cmd={context.command}, params={context.params}")
        if context.parent is None:
            break
        context = context.parent
    return context


def default_config_file() -> Path:
    """Return default configuration file path."""
    filenames = [
        ".twcrc",
        ".twcrc.toml",
    ]
    for filename in filenames:
        filepath = Path(PurePath(Path.home()).joinpath(filename))
        if filepath.exists():
            debug(f"Configuration file found: {filepath}")
            return filepath
    return Path(PurePath(Path.home()).joinpath(filenames[0]))


def load_config(filepath: Optional[Path] = default_config_file()) -> dict:
    """Load configuration from TOML config file."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return toml.load(file)
    except FileNotFoundError:
        sys.exit(
            f"Configuration file {filepath} not found. Try run 'twc config'"
        )
    except OSError as error:
        sys.exit(f"Error: Cannot read configuration file {filepath}: {error}")
    except toml.TomlDecodeError as error:
        sys.exit(f"Error: Check your TOML syntax in file {filepath}: {error}")


def load_from_config_callback(
    param: TyperOption, value: Any, ctx: typer.Context
) -> Any:
    """Return value from config file. NOTE: This callback doesn't work with
    custom enumerations such as OutputFormat and may others. Typer will return
    None instead of actual value returning by this function.
    """
    if value is None:
        try:
            config = config_callback(ctx.params["config"], ctx)
            profile = profile_callback(ctx.params["profile"], ctx)
            debug(
                f"Set '{param.name}' value from file:"
                f" config={config}, profile={profile}"
            )
            value = load_config(config)[profile][param.name]
        except KeyError as err:
            debug(f"Not found key {err} in: {config}:{profile}")
            return None
    debug(f"Return value: {value}")
    if param.name == "output_format":
        value = value.lower()
    if param.name == "region":
        value = value.lower()
        regions = [v.value for v in ServiceRegion]
        if value not in regions:
            sys.exit(f"Error: Location not in {regions}")
    if param.name == "zone":
        value = value.lower()
        zones = [z.value for z in ServiceAvailabilityZone]
        if value not in zones:
            sys.exit(f"Error: Availability zone not in {zones}")
    return value


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        print(f"v{__version__}")
        raise typer.Exit()


def verbose_callback(value: bool) -> bool:
    """Typer callback to enable verbose mode. Set logger settings."""
    if value:
        basicConfig(
            force=True,
            level=DEBUG,
            format="%(asctime)s:%(levelname)s:%(name)s:%(module)s:%(funcName)s: %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    return value


def config_callback(value: Path, ctx: typer.Context) -> Path:
    """Lookup for '--config' option value and save it into `ctx`."""
    if not value:
        root_value = get_root_ctx(ctx).params["config"]
        debug(f"cli parser: root lvl: config={root_value}")
        value = root_value or default_config_file()
    return value


def profile_callback(value: str, ctx: typer.Context) -> str:
    """Lookup for '--profile' option value and save it into `ctx`."""
    if not value:
        root_value = get_root_ctx(ctx).params["profile"]
        debug(f"cli parser: root lvl: profile={root_value}")
        value = root_value or "default"
    return value


def filter_callback(value: str) -> str:
    """Validate filters format."""
    if value:
        if not re.match(
            r"^(([a-z0-9._-]+:[a-z0-9._\-/+%]+),?)+$", value, re.I
        ):
            raise UsageError(
                "Invalid filter format. Filter must contain comma separated "
                + "KEY:VALUE pairs. Allowed characters: [a-zA-Z0-9_.-/+%]"
            )
        # Make aliases
        value = value.replace("region:", "location:")
        value = value.replace("proto:", "protocol:")
        value = value.replace("rule_id:", "id:")
    return value


# ------------------------------------------------------------- #
# Very common CLI options.                                      #
# ------------------------------------------------------------- #


# version: Optional[bool] = version_option,

version_option = typer.Option(
    None,
    "--version",
    callback=version_callback,
    is_eager=True,
    help="Show version and exit.",
)


# verbose: Optional[bool] = verbose_option,

verbose_option = typer.Option(
    False,
    "--verbose",
    "-v",
    envvar="TWC_DEBUG",
    show_envvar=False,
    callback=verbose_callback,
    help="Enable verbose mode.",
    rich_help_panel="Global options",
)


# Do not use following 'config' and 'profile' options in __main__.py.
# They callbacks doesn't works properly at root level command e.g. twc -c ...


# config: Optional[Path] = config_option,

config_option = typer.Option(
    None,
    "--config",
    "-c",
    envvar="TWC_CONFIG_FILE",
    show_envvar=False,
    show_default=False,
    exists=True,
    dir_okay=False,
    callback=config_callback,
    help="Use config.",
    rich_help_panel="Global options",
)


# profile: Optional[str] = profile_option,

profile_option = typer.Option(
    None,
    "--profile",
    "-p",
    metavar="NAME",
    envvar="TWC_PROFILE",
    show_envvar=False,
    show_default=False,
    callback=profile_callback,
    help="Use profile.",
    rich_help_panel="Global options",
)


# output_format: Optional[str] = output_format_option,

output_format_option = typer.Option(
    None,
    "--output",
    "-o",
    metavar="FORMAT",
    envvar="TWC_OUTPUT_FORMAT",
    show_default=False,
    show_envvar=False,
    callback=load_from_config_callback,
    help=f"Output format, one of: [{'|'.join([k.value for k in OutputFormat])}].",
)


# filters: Optional[str] = filter_option,

filter_option = typer.Option(
    None,
    "--filter",
    "-f",
    metavar="KEY:VALUE",
    callback=filter_callback,
    help="Filter output.",
)


# yes: Optional[bool] = yes_option,

yes_option = typer.Option(
    False, "--yes", "-y", help="Confirm the action without prompting."
)


# region: Optional[str] = region_option,

region_option = typer.Option(
    "ru-1",
    metavar="REGION",
    envvar="TWC_REGION",
    show_envvar=False,
    callback=load_from_config_callback,
    help="Region (location).",
)

# availability_zone: Optional[str] = zone_option,

zone_option = typer.Option(
    None,
    metavar="ZONE",
    envvar="TWC_AVAILABILITY_ZONE",
    show_envvar=False,
    callback=load_from_config_callback,
    help="Availability zone.",
)
