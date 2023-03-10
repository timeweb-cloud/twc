"""TWC CLI commands package.

__init__.py module contains common functions, decorators and variables.
"""

import os
import sys
import logging

import click
import toml

from twc.__version__ import __version__, __pyversion__
from twc.api import TimewebCloud
from twc.api import (
    UnauthorizedError,
    NonJSONResponseError,
    BadResponseError,
    UnexpectedResponseError,
)


# -----------------------------------------------------------------------
# Configuration


USER_AGENT = f"TWC-CLI/{__version__} Python {__pyversion__}"
DEFAULT_CONFIG = {"default": {"token": ""}}
DEFAULT_CONFIGURATOR_ID = 11
REGIONS_WITH_CONFIGURATOR = ["ru-1"]
REGIONS_WITH_IPV6 = ["ru-1", "pl-1"]
REGIONS_WITH_IMAGES = ["ru-1"]


def get_default_config_file() -> str:
    if os.name == "nt":
        env_home = "USERPROFILE"
    else:
        env_home = "HOME"
    return os.path.join(os.getenv(env_home), ".twcrc")


def load_config(filepath: str = get_default_config_file()):
    """Load configuration from TOML config file."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return toml.load(file)
    except (OSError, FileNotFoundError) as error:
        sys.exit(f"Error: {filepath}: {error}: Try run 'twc config'")
    except toml.TomlDecodeError as error:
        sys.exit(f"Error: {filepath}: {error}")


def set_value_from_config(ctx, param, value):
    """Callback for Click to load option values from configuration file."""
    if value is None:
        if not os.path.exists(ctx.params["config"]):
            return None
        try:
            value = load_config(ctx.params["config"])[ctx.params["profile"]][
                param.name
            ]
        except KeyError:
            return None
    return value


# -----------------------------------------------------------------------
# Logger


def set_logger(ctx, param, value):
    """Click callback for '--verbose' option. Set logger settings.
    Log HTTP requests and anything else.
    """
    if value:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s:%(levelname)s:%(name)s: %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )


def debug(message: str, *args, **kwargs):
    """Print DEBUG log message"""
    logging.debug(message, *args, **kwargs)


def log_request(response: object):
    """Log data from `requests.PreparedRequest` and `requests.Response`
    objects. Hide auth Bearer token.
    """
    request_headers = response.request.headers
    request_headers.update(
        {"Authorization": "Bearer <SENSITIVE_DATA_DELETED>"}
    )

    for key in list(request_headers.keys()):
        debug(f"Request header: {key}: {request_headers[key]}")

    if response.request.method in ["POST", "PUT", "PATCH"]:
        debug(f"Request body (raw): {response.request.body}")

    for key in list(response.headers.keys()):
        debug(f"Response header: {key}: {response.headers[key]}")


# -----------------------------------------------------------------------
# CLI


GLOBAL_OPTIONS = [
    click.help_option("--help"),
    click.version_option(__version__, "--version", prog_name="twc"),
    click.option(
        "--verbose",
        "-v",
        is_flag=True,
        envvar="TWC_DEBUG",
        callback=set_logger,
        help="Enable verbose mode.",
    ),
    click.option(
        "--config",
        "-c",
        metavar="FILE",
        envvar="TWC_CONFIG_FILE",
        default=get_default_config_file(),
        is_eager=True,
        show_default=True,
        help="Use config file.",
    ),
    click.option(
        "--profile",
        "-p",
        envvar="TWC_PROFILE",
        default="default",
        show_default=True,
        is_eager=True,
        help="Use profile.",
    ),
]

OUTPUT_FORMAT_OPTION = [
    click.option(
        "--output",
        "-o",
        "output_format",
        type=click.Choice(["default", "raw", "json", "yaml"]),
        envvar="TWC_OUTPUT_FORMAT",
        callback=set_value_from_config,
        help="Output format.",
    )
]


def options(options_list: list):
    """Add multiple options to command."""

    def wrapper(func):
        for option in reversed(options_list):
            func = option(func)
        return func

    return wrapper


class MutuallyExclusiveOption(click.Option):
    """Add mutually exclusive options support for Click. Example::

    @click.option(
        "--dry",
        is_flag=True,
        cls=MutuallyExclusiveOption,
        mutually_exclusive=["wet"],
    )
    @click.option("--wet", is_flag=True)
    """

    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = set(kwargs.pop("mutually_exclusive", []))
        help = kwargs.get("help", "")  # pylint: disable=redefined-builtin
        if self.mutually_exclusive:
            kwargs["help"] = help + (
                " NOTE: This argument is mutually exclusive with "
                f"arguments: [{', '.join(self.mutually_exclusive)}]."
            )
        super().__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            raise click.UsageError(
                f"Illegal usage: '{self.name}' is mutually exclusive with "
                f"arguments: [{', '.join(self.mutually_exclusive)}]."
            )
        return super().handle_parse_result(ctx, opts, args)


def confirm_action(question: str, default: str = "no"):
    """Ask a yes/no question via input() and return their answer.

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {
        "yes": True,
        "y": True,
        "ye": True,
        "no": False,
        "n": False,
    }
    if default is None:
        prompt = "[y/n]"
    elif default == "yes":
        prompt = "[Y/n]"
    elif default == "no":
        prompt = "[y/N]"
    else:
        raise ValueError(f"Invalid default answer: '{default}'")

    while True:
        choice = input(f"{question} {prompt}: ").lower()
        if default is not None and choice == "":
            return valid[default]
        if choice in valid:
            return valid[choice]
        sys.exit("Please respond with 'yes' or 'no' (or 'y' or 'n').")


# -----------------------------------------------------------------------
# API interaction


def handle_request(func):
    def wrapper(*args, **kwargs):
        try:
            response = func(*args, **kwargs)

            log_request(response)
            if not response.text:
                debug("No response body")

            if response.status_code not in [200, 201, 204]:
                raise BadResponseError
        except UnauthorizedError:
            print(
                "Error: Unauthorized. "
                + "Please check your API access token. Try run 'twc config'",
                file=sys.stderr,
            )
            sys.exit(1)
        except BadResponseError:
            resp = response.json()
            print("Error occurred. Details:", file=sys.stderr)
            print(f"Status code: {resp['status_code']}", file=sys.stderr)
            print(f" Error code: {resp['error_code']}", file=sys.stderr)
            if isinstance(resp["message"], list):
                for message in resp["message"]:
                    print(f"    Message: {message}", file=sys.stderr)
            else:
                print(f"    Message: {resp['message']}", file=sys.stderr)
            print(f"Response ID: {resp['response_id']}", file=sys.stderr)
            sys.exit(1)
        except (NonJSONResponseError, UnexpectedResponseError) as error:
            sys.exit(f"Error: {error}")
        return response

    return wrapper


def create_client(config, profile):
    """Create API client instance with access token."""

    debug(f"TWC CLI {__version__} Python {__pyversion__}")
    debug(f"Args: {sys.argv[1:]}")

    env_token = os.getenv("TWC_TOKEN")

    if env_token:
        debug("Get Timeweb Cloud token from environment variable")
        return TimewebCloud(env_token, user_agent=USER_AGENT)

    try:
        debug(f"Configuration: config file={config}; profile={profile}")
        token = load_config(config)[profile]["token"]
        return TimewebCloud(token, user_agent=USER_AGENT)
    except KeyError:
        sys.exit(f"Profile '{profile}' not found in {config}")
