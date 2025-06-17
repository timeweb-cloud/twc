"""Manage apps."""

from typing import Optional
from pathlib import Path

import typer
from requests import Response

from twc import fmt
from twc.typerx import TyperAlias
from twc.apiwrap import create_client
from .common import (
    verbose_option,
    config_option,
    profile_option,
    filter_option,
    output_format_option,
)


apps = TyperAlias(help=__doc__)


# ------------------------------------------------------------- #
# $ twc apps list                                           #
# ------------------------------------------------------------- #


def print_apps(response: Response, filters: Optional[str]):
    """Print table with apps list."""
    # pylint: disable=invalid-name
    _apps = response.json()["apps"]
    if filters:
        _apps = fmt.filter_list(_apps, filters)
    table = fmt.Table()
    table.header(
        [
            "ID",
            "NAME",
            "STATUS",
            "TYPE",
            "IPV4",
        ]
    )
    for app in _apps:
        table.row(
            [
                app["id"],
                app["name"],
                app["status"],
                app["type"],
                app["ip"],
            ]
        )
    table.print()


@apps.command("list", "ls")
def apps_list(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
):
    """List apps."""
    client = create_client(config, profile)
    response = client.get_apps()
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_apps,
    )


@apps.command("create")
def app_create(
    yml_config_path: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    status: Optional[bool] = typer.Option(
        False,
        "--status",
        help="Display status and exit with 0 if status is 'started'.",
    ),
):
    """Create app"""
    client = create_client(config, profile)
    response = client.create_app(yml_config_path)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["app"]["id"]),
    )


def print_vcs_providers(response: Response):
    """Print table with vcs list."""
    # pylint: disable=invalid-name
    providers = response.json()["providers"]
    table = fmt.Table()
    table.header(
        [
            "LOGIN",
            "PROVIDER",
            "PROVIDER_ID",
        ]
    )
    for provider in providers:
        table.row(
            [
                provider["login"],
                provider["provider"],
                provider["provider_id"],
            ]
        )
    table.print()


@apps.command("get-vcs-providers")
def app_get_vcs_providers(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """Get VCS providers."""
    client = create_client(config, profile)
    response = client.get_vcs_providers()
    fmt.printer(
        response, output_format=output_format, func=print_vcs_providers
    )


def print_vcs_repositories(response: Response):
    """Print table with vcs list."""
    # pylint: disable=invalid-name
    providers = response.json()["repositories"]
    table = fmt.Table()
    table.header(["FULL NAME", "ID", "NAME", "URL", "IS PRIVATE"])
    for provider in providers:
        table.row(
            [
                provider["full_name"],
                provider["id"],
                provider["name"],
                provider["url"],
                provider["is_private"],
            ]
        )
    table.print()


@apps.command("get-repositories")
def app_get_repositories(
    vcs_provider_id: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """Get repositories."""
    client = create_client(config, profile)
    response = client.get_repositories(vcs_provider_id)
    fmt.printer(
        response, output_format=output_format, func=print_vcs_repositories
    )


def print_apps_tarifs(response: Response, typ: str):
    """Print Timeweb Cloud Apps tarifs."""
    # pylint: disable=invalid-name
    if typ == "backend":
        key = "backend_presets"
    elif typ == "frontend":
        key = "frontend_presets"
    else:
        raise KeyError("Tarifs can be only backend or frontend")

    providers = response.json()[key]
    table = fmt.Table()
    if key == "backend_presets":
        table.header(
            [
                "CPU",
                "CPU FREQUENCY",
                "DESCRIPTION",
                "DESCRIPTION SHORT",
                "DISK",
                "ID",
                "LOCATION",
                "PRICE",
                "RAM",
            ]
        )
        for provider in providers:
            table.row(
                [
                    provider["cpu"],
                    provider["cpu_frequency"],
                    provider["description"],
                    provider["description_short"],
                    provider["disk"],
                    provider["id"],
                    provider["location"],
                    provider["price"],
                    provider["ram"],
                ]
            )
    elif key == "frontend_presets":
        table.header(
            [
                "DESCRIPTION",
                "DESCRIPTION_SHORT",
                "DISK",
                "ID",
                "LOCATION",
                "PRICE",
                "REQUESTS",
            ]
        )
        for provider in providers:
            table.row(
                [
                    provider["description"],
                    provider["description_short"],
                    provider["disk"],
                    provider["id"],
                    provider["location"],
                    provider["price"],
                    provider["requests"],
                ]
            )
    table.print()


@apps.command("list-presets")
def get_apps_tarifs(
    _type: str = typer.Argument(..., metavar="TYPE"),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """Get tarifs; backend or frontend"""
    client = create_client(config, profile)
    response = client.get_apps_tarifs()
    fmt.printer(
        response,
        output_format=output_format,
        typ=_type,
        func=print_apps_tarifs,
    )


def print_app_delete_response(response: Response, app_id: int):
    """Print table with apps list."""
    # pylint: disable=invalid-name
    table = fmt.Table()
    table.header(
        [
            "ID",
        ]
    )
    table.row(
        [
            app_id,
        ]
    )
    table.print()


@apps.command("delete")
def delete_app(
    app_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """Delete apps."""
    client = create_client(config, profile)
    response = client.delete_app(app_id)
    fmt.printer(
        response,
        output_format=output_format,
        app_id=app_id,
        func=print_app_delete_response,
    )


def get_app(response: Response):
    """Print table with apps list."""
    # pylint: disable=invalid-name
    app = response.json()["app"]
    table = fmt.Table()
    table.header(
        [
            "ID",
            "LOCATION",
            "STATUS",
            "TYPE",
            "IPV4",
        ]
    )
    table.row(
        [
            app["id"],
            app["location"],
            app["status"],
            app["type"],
            app["ip"],
        ]
    )
    table.print()


@apps.command("get")
def app_get(
    app_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    status: Optional[bool] = typer.Option(
        False,
        "--status",
        help="Display status and exit with 0 if status is 'started'.",
    ),
):
    """Get database info."""
    client = create_client(config, profile)
    response = client.get_app(app_id)
    fmt.printer(response, output_format=output_format, func=get_app)
