"""API Client wrapper for CLI."""

import os
import sys
import textwrap
from pathlib import Path
from logging import debug, warning

from .api import TimewebCloud
from .api import exceptions as exc
from .commands.common import load_config


def request_handler(func):
    """Error handler decorator for requests. Wrap API exceptions
    and exit with human-readable error message.
    """

    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except exc.NetworkError as err:
            sys.exit(f"Error: {err}")
        except exc.UnauthorizedError as err:
            sys.exit(
                textwrap.dedent(
                    f"""
                    Error: {err}
                    Please check your API access token. Try run 'twc config'
                    """
                ).strip()
            )
        except exc.MalformedResponseError as err:
            sys.exit(
                textwrap.dedent(
                    f"""
                    Error: API returned malformed response: {err}
                    Try run command with '--verbose' option for details.
                    """
                ).strip()
            )
        except exc.UnexpectedResponseError as err:
            sys.exit(
                textwrap.dedent(
                    f"""
                    Error: API returned unexpected response: {err}
                    Try run command with '--verbose' option for details.
                    """
                ).strip()
            )
        except exc.TimewebCloudException as err:
            sys.exit(
                textwrap.dedent(
                    f"""
                    Error ocurred.
                    Status code: {err.status_code}
                    Error code: {err.error_code}
                    Message: {err.message}
                    Response ID: {err.response_id}
                    """
                ).strip()
            )

    return wrapper


def create_client(config: Path, profile: str, **kwargs) -> TimewebCloud:
    """API client wrapper. Read configuration file and return
    `TimewebCloud` object with decorator.
    """
    token = os.getenv("TWC_TOKEN")
    log_settings = os.getenv("TWC_LOG")
    api_endpoint = os.getenv("TWC_ENDPOINT")

    if api_endpoint:
        warning("Using API URL from environment: %s", api_endpoint)
        kwargs["api_base_url"] = api_endpoint

    if log_settings:
        for param in log_settings.split(","):
            if param.lower() == "debug":
                pass  # FUTURE: set logging.DEBUG

    if token:
        debug("Config: use API token from environment")
    else:
        try:
            debug(f"Config: file={config}, profile={profile}")
            token = load_config(config)[profile]["token"]
        except KeyError:
            sys.exit(f"Error: Profile '{profile}' not found in {config}")

    return TimewebCloud(token, request_decorator=request_handler, **kwargs)
