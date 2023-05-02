"""Manage databases."""

import re
import sys
from typing import Optional, List
from pathlib import Path

import typer
from requests import Response

from twc import fmt
from twc.typerx import TyperAlias
from twc.api import ServiceRegion, DBMS, MySQLAuthPlugin
from twc.apiwrap import create_client
from twc.utils import merge_dicts
from .common import (
    verbose_option,
    config_option,
    profile_option,
    filter_option,
    yes_option,
    output_format_option,
    load_from_config_callback,
)


database = TyperAlias(help=__doc__)
database_backup = TyperAlias(help="Manage database backups.")
database.add_typer(database_backup, name="backup")


# ------------------------------------------------------------- #
# $ twc database list                                           #
# ------------------------------------------------------------- #


def print_databases(response: Response, filters: Optional[str]):
    """Print table with databases list."""
    # pylint: disable=invalid-name
    dbs = response.json()["dbs"]
    if filters:
        dbs = fmt.filter_list(dbs, filters)
    table = fmt.Table()
    table.header(
        [
            "ID",
            "NAME",
            "STATUS",
            "TYPE",
            "IPV4",
            "INTERNAL IP",
        ]
    )
    for db in dbs:
        table.row(
            [
                db["id"],
                db["name"],
                db["status"],
                db["type"],
                db["ip"],
                db["local_ip"],
            ]
        )
    table.print()


@database.command("list", "ls")
def database_list(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    limit: int = typer.Option(500, help="Items to display."),
    filters: Optional[str] = filter_option,
):
    """List databases."""
    client = create_client(config, profile)
    response = client.get_databases(limit=limit)
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_databases,
    )


# ------------------------------------------------------------- #
# $ twc database get                                            #
# ------------------------------------------------------------- #


def print_database(response: Response):
    """Print table with database info."""
    # pylint: disable=invalid-name
    db = response.json()["db"]
    table = fmt.Table()
    table.header(
        [
            "ID",
            "NAME",
            "STATUS",
            "TYPE",
            "IPV4",
            "INTERNAL IP",
        ]
    )
    table.row(
        [
            db["id"],
            db["name"],
            db["status"],
            db["type"],
            db["ip"],
            db["local_ip"],
        ]
    )
    table.print()


@database.command("get")
def database_get(
    db_id: int,
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
    response = client.get_database(db_id)
    if status:
        state = response.json()["db"]["status"]
        if state == "started":
            print(state)
            raise typer.Exit()
        sys.exit(state)
    fmt.printer(response, output_format=output_format, func=print_database)


# ------------------------------------------------------------- #
# $ twc database list-presets                                   #
# ------------------------------------------------------------- #


def print_dbs_presets(response: Response, filters: Optional[str]):
    """Print table with database presets list."""
    presets = response.json()["databases_presets"]
    if filters:
        presets = fmt.filter_list(presets, filters)
    table = fmt.Table()
    table.header(
        [
            "ID",
            "REGION",
            "PRICE",
            "CPU",
            "RAM",
            "DISK",
            "TYPE",
        ]
    )
    for preset in presets:
        table.row(
            [
                preset["id"],
                preset["location"],
                preset["price"],
                preset["cpu"],
                str(round(preset["ram"] / 1024)) + "G",
                str(round(preset["disk"] / 1024)) + "G",
                preset["type"],
            ]
        )
    table.print()


@database.command("list-presets", "lp")
def database_list_presets(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
    region: Optional[ServiceRegion] = typer.Option(
        None,
        case_sensitive=False,
        help="Use region (location).",
    ),
):
    """List database configuration presets."""
    if region:
        filters = f"{filters},location:{region}"
    client = create_client(config, profile)
    response = client.get_database_presets()
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_dbs_presets,
    )


# ------------------------------------------------------------- #
# $ twc database create                                         #
# ------------------------------------------------------------- #


def set_params(params: list) -> dict:
    """Return dict with database config_parameters."""
    parameters = {}
    for param in params:
        if re.match(r"^([a-z_]+)=([0-9a-zA-Z]+)$", param):
            parameter, value = param.split("=")
            if value.isdigit():
                value = int(value)
            parameters[parameter] = value
        else:
            raise typer.BadParameter(
                f"'{param}': Parameter can contain only digits,"
                " latin letters and underscore."
            )
    return parameters


@database.command("create")
def database_create(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    preset_id: int = typer.Option(..., help="Database configuration preset."),
    dbms: DBMS = typer.Option(
        ...,
        "--type",
        case_sensitive=False,
        help="Database management system.",
    ),
    hash_type: Optional[MySQLAuthPlugin] = typer.Option(
        MySQLAuthPlugin.CACHING_SHA2.value,
        case_sensitive=False,
        help="Authentication plugin for MySQL.",
    ),
    name: str = typer.Option(..., help="Database instance display name."),
    params: Optional[List[str]] = typer.Option(
        None,
        "--param",
        metavar="PARAM=VALUE",
        help="Database parameters, can be multiple.",
    ),
    login: Optional[str] = typer.Option(None, help="Database user login."),
    password: str = typer.Option(
        ...,
        prompt="Database user password",
        confirmation_prompt=True,
        hide_input=True,
    ),
    project_id: Optional[int] = typer.Option(
        None,
        envvar="TWC_PROJECT",
        show_envvar=False,
        callback=load_from_config_callback,
        help="Add database to specific project.",
    ),
):
    """Create managed database instance."""
    client = create_client(config, profile)

    # Check preset_id
    for preset in client.get_database_presets().json()["databases_presets"]:
        if preset["id"] == preset_id:
            _dbms = re.sub(
                r"[0-9]+", "", dbms
            )  # transform 'mysql5' to 'mysql', etc.
            if not preset["type"].startswith(_dbms):
                sys.exit(
                    f"Error: DBMS '{dbms}' doesn't match with preset_id type."
                )

    payload = {
        "dbms": dbms,
        "preset_id": preset_id,
        "name": name,
        "hash_type": hash_type,
        "login": login,
        "password": password,
        "config_parameters": {},
    }

    if params:
        payload["config_parameters"] = set_params(params)

    if project_id:
        if not project_id in [
            prj["id"] for prj in client.get_projects().json()["projects"]
        ]:
            sys.exit(f"Wrong project ID: Project '{project_id}' not found.")

    response = client.create_database(**payload)

    # Add created DB to project if set
    if project_id:
        client.add_database_to_project(
            response.json()["db"]["id"],
            project_id,
        )

    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["db"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc database set                                            #
# ------------------------------------------------------------- #


@database.command("set")
def database_set(
    db_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    preset_id: Optional[int] = typer.Option(
        None, help="Database configuration preset."
    ),
    external_ip: bool = typer.Option(
        True, help="Enable external IPv4 address."
    ),
    name: Optional[str] = typer.Option(
        None, help="Database instance display name."
    ),
    params: Optional[List[str]] = typer.Option(
        None,
        "--param",
        metavar="PARAM=VALUE",
        help="Database parameters, can be multiple.",
    ),
    password: Optional[str] = typer.Option(
        None, help="Database user password"
    ),
    prompt_password: Optional[bool] = typer.Option(
        False, help="Set database user password interactively."
    ),
):
    """Set database properties and parameters."""
    client = create_client(config, profile)
    old_state = client.get_database(db_id).json()["db"]
    new_params = {}
    if prompt_password:
        password = typer.prompt(
            "Database user password",
            hide_input=True,
            confirmation_prompt=True,
        )
    payload = {
        "preset_id": preset_id,
        "name": name,
        "password": password,
        "config_parameters": {},
        "external_ip": external_ip,
    }
    if params:
        new_params = set_params(params)
    if new_params:
        payload["config_parameters"] = merge_dicts(
            old_state["config_parameters"], new_params
        )
    response = client.update_database(db_id, **payload)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["db"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc database remove                                         #
# ------------------------------------------------------------- #


@database.command("remove", "rm")
def database_remove(
    db_ids: List[int] = typer.Argument(..., metavar="DB_ID..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
):
    """Remove database."""
    if not yes:
        typer.confirm("This action cannot be undone. Continue?", abort=True)
    client = create_client(config, profile)
    for db_id in db_ids:
        response = client.delete_database(db_id)
        if response.status_code == 200:
            del_hash = response.json()["database_delete"]["hash"]
            del_code = typer.prompt("Please enter confirmation code", type=int)
            response = client.delete_database(
                db_id, delete_hash=del_hash, code=del_code
            )
        if response.status_code == 204:
            print(db_id)
        else:
            sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc database backup list                                    #
# ------------------------------------------------------------- #


def print_db_backups(response: Response):
    """Print table with DB backup list."""
    backups = response.json()["backups"]
    table = fmt.Table()
    table.header(
        [
            "ID",
            "DISK",
            "CREATED",
            "STATUS",
        ]
    )
    for bak in backups:
        table.row(
            [
                bak["id"],
                bak["name"],
                bak["created_at"],
                bak["status"],
            ]
        )
    table.print()


@database_backup.command("list", "ls")
def database_backup_list(
    db_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """List backups."""
    client = create_client(config, profile)
    response = client.get_database_backups(db_id)
    fmt.printer(
        response,
        output_format=output_format,
        func=print_db_backups,
    )


# ------------------------------------------------------------- #
# $ twc database backup create                                  #
# ------------------------------------------------------------- #


@database_backup.command("create")
def database_backup_create(
    db_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """Backup database."""
    client = create_client(config, profile)
    response = client.create_database_backup(db_id)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["backup"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc database backup remove                                  #
# ------------------------------------------------------------- #


@database_backup.command("remove", "rm")
def database_backup_remove(
    db_id: int,
    backup_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
):
    """Remove backup."""
    if not yes:
        typer.confirm("This action cannot be undone. Continue?", abort=True)
    client = create_client(config, profile)
    response = client.delete_database_backup(db_id, backup_id)
    if response.status_code == 204:
        print(backup_id)
    else:
        sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc database backup restore                                 #
# ------------------------------------------------------------- #


@database_backup.command("restore")
def database_backup_restore(
    db_id: int,
    backup_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
):
    """Restore backup."""
    if not yes:
        typer.confirm("Data on target disk will lost. Continue?", abort=True)
    client = create_client(config, profile)
    response = client.restore_database_backup(db_id, backup_id)
    if response.status_code == 204:
        print(backup_id)
    else:
        sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc database backup schedule                                #
# ------------------------------------------------------------- #

# FUTURE: Waiting for API endpoint release.
