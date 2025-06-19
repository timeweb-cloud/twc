"""Manage databases."""

import re
import sys
import textwrap
from datetime import date, datetime
from typing import Optional, List
from pathlib import Path
from ipaddress import IPv4Address, IPv4Network

import typer
from requests import Response

from twc import fmt
from twc.typerx import TyperAlias
from twc.api import ServiceRegion, MySQLAuthPlugin, BackupInterval
from twc.apiwrap import create_client
from twc.vars import REGION_ZONE_MAP
from twc.utils import merge_dicts
from .common import (
    verbose_option,
    config_option,
    profile_option,
    filter_option,
    yes_option,
    output_format_option,
    load_from_config_callback,
    zone_option,
)


database = TyperAlias(help=__doc__)
database_backup = TyperAlias(help="Manage database backups.")
database.add_typer(database_backup, name="backup")
database_user = TyperAlias(help="Manage database users.")
database.add_typer(database_user, name="user")
database_instance = TyperAlias(
    help="Manage instances in cluster (databases/topics/etc)."
)
database.add_typer(database_instance, name="instance", aliases=["db"])


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
# $ twc database list-types                                     #
# ------------------------------------------------------------- #


@database.command("list-types", "lt")
def database_list_types(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """List database configuration presets."""
    client = create_client(config, profile)
    response = client.get_database_types().json()
    table = fmt.Table()
    table.header(["TYPE", "DATABASE", "VERSION"])
    for service in response["types"]:
        table.row(
            [
                service["type"],
                service["name"],
                service["version"],
            ]
        )
    table.print()


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


def dbms_parameters_callback(value: str) -> List[str]:
    if value:
        return value.split(",")
    return []


@database.command("create")
def database_create(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    availability_zone: Optional[str] = zone_option,
    preset_id: int = typer.Option(..., help="Database configuration preset."),
    dbms: str = typer.Option(
        ...,
        "--type",
        help="Database management system. See TYPE in `twc database list-types`.",
    ),
    hash_type: Optional[MySQLAuthPlugin] = typer.Option(
        MySQLAuthPlugin.CACHING_SHA2.value,
        case_sensitive=False,
        help="Authentication plugin for MySQL.",
    ),
    name: str = typer.Option(..., help="Database cluster display name."),
    params: Optional[List[str]] = typer.Option(
        None,
        "--param",
        metavar="PARAM=VALUE",
        help="Database config parameters, can be multiple.",
    ),
    login: Optional[str] = typer.Option(
        # DEPRECATED
        None,
        hidden=True,
        help="Database user login.",
    ),
    password: Optional[str] = typer.Option(
        # DEPRECATED
        None,
        hidden=True,
    ),
    user_login: Optional[str] = typer.Option(None, help="User login."),
    user_password: Optional[str] = typer.Option(None, help="User password."),
    user_host: Optional[str] = typer.Option(
        "%", help="User host for MySQL, Postgres"
    ),
    user_privileges: Optional[str] = typer.Option(
        None,
        help="Comma-separated list of user privileges.",
        callback=dbms_parameters_callback,
    ),
    user_desc: Optional[str] = typer.Option(None, help="Comment for user."),
    db_name: Optional[str] = typer.Option(None, help="Database name."),
    db_desc: Optional[str] = typer.Option(None, help="Database comment."),
    network_id: Optional[str] = typer.Option(None, help="Private network ID."),
    private_ip: Optional[str] = typer.Option(
        None, help="Private IPv4 address."
    ),
    public_ip: Optional[str] = typer.Option(
        None, help="Public IPv4 address. New address by default."
    ),
    no_public_ip: Optional[bool] = typer.Option(
        False, "--no-public-ip", help="Do not add public IPv4 address."
    ),
    project_id: Optional[int] = typer.Option(
        None,
        envvar="TWC_PROJECT",
        show_envvar=False,
        callback=load_from_config_callback,
        help="Add database cluster to specific project.",
    ),
    enable_backups: Optional[bool] = typer.Option(
        False,
        "--enable-backups",
        help="Enable atomatic backups of database cluster.",
    ),
    backup_keep: Optional[int] = typer.Option(
        1,
        show_default=True,
        help="Number of backups to keep.",
    ),
    backup_start_date: Optional[datetime] = typer.Option(
        date.today().strftime("%Y-%m-%d"),
        formats=["%Y-%m-%d"],
        show_default=False,
        help="Start date of the first backup creation [default: today].",
    ),
    backup_interval: Optional[BackupInterval] = typer.Option(
        BackupInterval.DAY.value,
        "--backup-interval",
        help="Backup interval.",
    ),
    backup_day_of_week: Optional[int] = typer.Option(
        1,
        min=1,
        max=7,
        help="The day of the week on which backups will be created."
        " NOTE: This option works only with interval 'week'."
        " First day of week is monday.",
    ),
):
    """Create managed database cluster."""
    client = create_client(config, profile)

    payload = {
        "dbms": dbms,
        "preset_id": preset_id,
        "name": name,
        "hash_type": hash_type,
        "config_parameters": {},
        "network": {},
    }

    if enable_backups:
        backup_start_date = backup_start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        payload["auto_backups"] = {
            "copy_count": backup_keep,
            "creation_started_at": backup_start_date,
            "interval": backup_interval,
            "day_of_week": backup_day_of_week,
        }

    if network_id:
        payload["network"]["id"] = network_id
        if private_ip:
            net = IPv4Network(
                client.get_vpc(network_id).json()["vpc"]["subnet_v4"]
            )
            if IPv4Address(private_ip) >= net.network_address + 4:
                payload["network"]["ip"] = private_ip
            else:
                # First 3 addresses is reserved by Timeweb Cloud for gateway and future use.
                sys.exit(
                    f"Error: Private address '{private_ip}' is not allowed. "
                    "IP must be at least the fourth in order in the network."
                )
    if public_ip:
        try:
            _ = IPv4Address(public_ip)
            payload["network"]["floating_ip"] = public_ip
        except ValueError:
            sys.exit(f"Error: '{public_ip}' is not valid IPv4 address.")
    else:
        # Get new public IPv4 address.
        if no_public_ip is False:
            zone = None
            if preset_id and not availability_zone:
                for preset in client.get_database_presets().json()[
                    "databases_presets"
                ]:
                    if preset["id"] == preset_id:
                        zone = REGION_ZONE_MAP[preset["location"]]
            if availability_zone:
                zone = availability_zone
            ip = client.create_floating_ip(availability_zone=zone).json()[
                "ip"
            ]["ip"]
            payload["network"]["floating_ip"] = ip

    if login:
        print(
            "--login is deprecated use --user-login instead", file=sys.stderr
        )
        user_login = login

    if password:
        print(
            "--password is deprecated use --user-password instead",
            file=sys.stderr,
        )
        user_password = password

    if user_password and not user_login:
        sys.exit("Error: --user-login required if --user-password is set.")

    if user_login:
        if not user_password:
            user_password = typer.prompt(
                "Database user password",
                hide_input=True,
                confirmation_prompt=True,
            )
        payload["admin"] = {
            "login": user_login,
            "password": user_password,
            "host": user_host,
            "privileges": user_privileges,
            "description": user_desc or "",
        }

    if db_name:
        payload["instance"] = {
            "name": db_name,
            "description": db_desc or "",
        }

    if params:
        payload["config_parameters"] = set_params(params)

    if project_id:
        payload["project_id"] = project_id

    response = client.create_database2(**payload)

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


def print_autobackup_settings(response: Response):
    """Print backup settings info."""
    table = fmt.Table()
    settings = response.json()["auto_backups_settings"]
    translated_keys = {
        "copy_count": "Keep copies",
        "creation_start_at": "Backup start date",
        "is_enabled": "Enabled",
        "interval": "Interval",
        "day_of_week": "Day of week",
    }
    for key in settings.keys():
        table.row([translated_keys[key], ":", settings[key]])
    table.print()


@database_backup.command("schedule")
def database_backup_schedule(
    db_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    status: bool = typer.Option(
        False,
        "--status",
        help="Display automatic backups status.",
    ),
    enable: Optional[bool] = typer.Option(
        None,
        "--enable/--disable",
        show_default=False,
        help="Enable or disable automatic backups.",
    ),
    keep: int = typer.Option(
        1,
        show_default=True,
        help="Number of backups to keep.",
    ),
    start_date: datetime = typer.Option(
        date.today().strftime("%Y-%m-%d"),
        formats=["%Y-%m-%d"],
        show_default=False,
        help="Start date of the first backup creation [default: today].",
    ),
    interval: BackupInterval = typer.Option(
        BackupInterval.DAY.value,
        "--interval",
        help="Backup interval.",
    ),
    day_of_week: Optional[int] = typer.Option(
        1,
        min=1,
        max=7,
        help="The day of the week on which backups will be created."
        " NOTE: This option works only with interval 'week'."
        " First day of week is monday.",
    ),
):
    """Manage database cluster automatic backup settings."""
    client = create_client(config, profile)

    if status:
        response = client.get_database_autobackup_settings(db_id)
        fmt.printer(
            response,
            output_format=output_format,
            func=print_autobackup_settings,
        )
        if response.json()["auto_backups_settings"]["is_enabled"]:
            sys.exit(0)
        else:
            sys.exit(1)

    start_date = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    response = client.update_database_autobackup_settings(
        db_id,
        is_enabled=enable,
        copy_count=keep,
        creation_start_at=start_date,
        interval=interval,
        day_of_week=day_of_week,
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=print_autobackup_settings,
    )


# ------------------------------------------------------------- #
# $ twc database user list                                      #
# ------------------------------------------------------------- #


def _print_database_users(response: Response):
    users = response.json()["admins"]
    table = fmt.Table()
    table.header(["ID", "LOGIN", "HOST", "CREATED"])
    for user in users:
        table.row(
            [
                user["id"],
                user["login"],
                user["host"],
                user["created_at"],
            ]
        )
    table.print()


@database_user.command("list", "ls")
def database_user_list(
    db_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """List database users."""
    client = create_client(config, profile)
    response = client.get_database_users(db_id)
    fmt.printer(
        response,
        output_format=output_format,
        func=_print_database_users,
    )


# ------------------------------------------------------------- #
# $ twc database user get                                       #
# ------------------------------------------------------------- #


def _print_database_user(response: Response):
    user = response.json()["admin"]
    out = textwrap.dedent(
        f"""
        Login:       {user['login']}
        Host:        {user['host']}
        Created:     {user['created_at']}
        Description: {user['description']}
        """
    ).strip()
    print(out)
    print()
    table = fmt.Table()
    table.header(["INSTANCE_ID", "PRIVILEGES"])
    for instance in user["instances"]:
        table.row(
            [
                instance["instance_id"],
                ", ".join(instance["privileges"]),
            ]
        )
    table.print()


@database_user.command("get")
def database_user_get(
    db_id: int,
    user_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """Get database user."""
    client = create_client(config, profile)
    response = client.get_database_user(db_id, user_id)
    fmt.printer(
        response,
        output_format=output_format,
        func=_print_database_user,
    )


# ------------------------------------------------------------- #
# $ twc database user create                                    #
# ------------------------------------------------------------- #


@database_user.command("create")
def database_user_create(
    db_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    login: str = typer.Option(..., help="User login."),
    password: str = typer.Option(
        ...,
        prompt=True,
        hide_input=True,
        confirmation_prompt=True,
        help="User password.",
    ),
    host: Optional[str] = typer.Option(
        "%", help="User host for MySQL, Postgres"
    ),
    instance_id: Optional[int] = typer.Option(
        None,
        help="The specific instance ID to which the privileges will be "
        "applied. If not specified, the privileges will be applied to "
        "all available instances.",
    ),
    privileges: Optional[str] = typer.Option(
        [],
        help="Comma-separated list of user privileges.",
        callback=dbms_parameters_callback,
    ),
    desc: Optional[str] = typer.Option(None, help="Comment for user."),
):
    """Create database users."""
    client = create_client(config, profile)
    response = client.create_database_user(
        db_id=db_id,
        login=login,
        password=password,
        privileges=privileges,
        host=host,
        instance_id=instance_id,
        description=desc,
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["admin"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc database user remove                                    #
# ------------------------------------------------------------- #


@database_user.command("remove", "rm")
def database_user_remove(
    db_id: int,
    user_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
):
    """Delete database user."""
    client = create_client(config, profile)
    response = client.get_database_user(db_id, user_id)
    if response.status_code == 204:
        print(user_id)
    else:
        sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc database instance list                                  #
# ------------------------------------------------------------- #


def _print_database_instances(response: Response):
    instances = response.json()["instances"]
    table = fmt.Table()
    table.header(["ID", "NAME", "CREATED", "DESCRIPTION"])
    for i in instances:
        table.row(
            [
                i["id"],
                i["name"],
                i["created_at"],
                i["description"],
            ]
        )
    table.print()


@database_instance.command("list", "ls")
def database_instance_list(
    db_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """List databases in database cluster."""
    client = create_client(config, profile)
    response = client.get_database_instances(db_id)
    fmt.printer(
        response,
        output_format=output_format,
        func=_print_database_instances,
    )


# ------------------------------------------------------------- #
# $ twc database instance create                                #
# ------------------------------------------------------------- #


@database_instance.command("create")
def database_instance_create(
    db_id: int,
    name: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    desc: Optional[str] = typer.Option(None, help="Comment for database."),
):
    """Create database in database cluster."""
    client = create_client(config, profile)
    response = client.create_database_instance(
        db_id, name=name, description=desc
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["instance"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc database instance remove                                #
# ------------------------------------------------------------- #


@database_instance.command("remove", "rm")
def database_instance_remove(
    db_id: int,
    instance_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
):
    """Delete database from cluster."""
    client = create_client(config, profile)
    response = client.get_database_user(db_id, instance_id)
    if response.status_code == 204:
        print(instance_id)
    else:
        sys.exit(fmt.printer(response))
