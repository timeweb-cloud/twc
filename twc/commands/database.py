"""Database management commands."""

import re
import sys

import click
from click_aliases import ClickAliasedGroup

from twc import fmt
from twc.utils import merge_dicts
from . import (
    create_client,
    handle_request,
    set_value_from_config,
    options,
    debug,
    GLOBAL_OPTIONS,
    OUTPUT_FORMAT_OPTION,
)
from .project import (
    get_default_project_id,
    _project_list,
    _project_resource_move,
    _project_resource_list_databases,
)


@handle_request
def _database_list(client, *args, **kwargs):
    return client.get_databases(*args, **kwargs)


@handle_request
def _database_get(client, *args, **kwargs):
    return client.get_database(*args, **kwargs)


@handle_request
def _database_create(client, *args, **kwargs):
    return client.create_database(*args, **kwargs)


@handle_request
def _database_remove(client, *args, **kwargs):
    return client.delete_database(*args, **kwargs)


@handle_request
def _database_set(client, *args, **kwargs):
    return client.update_database(*args, **kwargs)


@handle_request
def _database_backup_list(client, *args, **kwargs):
    return client.get_database_backups(*args, **kwargs)


@handle_request
def _database_backup_create(client, *args, **kwargs):
    return client.create_database_backup(*args, **kwargs)


@handle_request
def _database_backup_remove(client, *args, **kwargs):
    return client.delete_database_backup(*args, **kwargs)


@handle_request
def _database_backup_restore(client, *args, **kwargs):
    return client.restore_database_backup(*args, **kwargs)


@handle_request
def _database_list_presets(client, *args, **kwargs):
    return client.get_database_presets(*args, **kwargs)


# ------------------------------------------------------------- #
# $ twc database                                                #
# ------------------------------------------------------------- #


@click.group("database", cls=ClickAliasedGroup)
@options(GLOBAL_OPTIONS[:2])
def database():
    """Manage databases."""


# ------------------------------------------------------------- #
# $ twc database list                                           #
# ------------------------------------------------------------- #


def print_databases(response: object, filters: str):
    if filters:
        dbs = fmt.filter_list(response.json()["dbs"], filters)
    else:
        dbs = response.json()["dbs"]

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


@database.command("list", aliases=["ls"], help="List databases.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option(
    "--limit",
    type=int,
    default=500,
    show_default=True,
    help="Items to display.",
)
@click.option("--filter", "-f", "filters", default="", help="Filter output.")
def database_list(config, profile, verbose, output_format, limit, filters):
    client = create_client(config, profile)
    response = _database_list(client, limit=limit)
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_databases,
    )


# ------------------------------------------------------------- #
# $ twc database get                                            #
# ------------------------------------------------------------- #


def print_database(response: object):
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


@database.command("get", help="Get database.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option(
    "--status",
    is_flag=True,
    help="Display status and exit with 0 if status is 'started'.",
)
@click.argument("db_id", type=int, required=True)
def database_get(config, profile, verbose, output_format, status, db_id):
    client = create_client(config, profile)
    response = _database_get(client, db_id)
    if status:
        _status = response.json()["db"]["status"]
        click.echo(_status)
        if _status == "started":
            sys.exit(0)
        else:
            sys.exit(1)
    fmt.printer(
        response,
        output_format=output_format,
        func=print_database,
    )


# ------------------------------------------------------------- #
# $ twc database list-presets                                   #
# ------------------------------------------------------------- #


def print_dbs_presets(response: object, filters: str):
    if filters:
        presets = fmt.filter_list(
            response.json()["databases_presets"], filters
        )
    else:
        presets = response.json()["databases_presets"]

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


@database.command(
    "list-presets", aliases=["lp"], help="List database presets."
)
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option("--filter", "-f", "filters", default="", help="Filter output.")
@click.option("--region", help="Use region (location).")
def database_list_presets(
    config, profile, verbose, output_format, filters, region
):
    if filters:
        filters = filters.replace("region", "location")
    if region:
        if filters:
            filters = filters + f",location:{region}"
        else:
            filters = f"location:{region}"

    client = create_client(config, profile)
    response = _database_list_presets(client)
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_dbs_presets,
    )


# ------------------------------------------------------------- #
# $ twc database create                                         #
# ------------------------------------------------------------- #


def set_params(params: tuple) -> dict:
    parameters = {}
    for param in params:
        if re.match(r"^([a-z_]+)=([0-9a-zA-Z]+)$", param):
            parameter, value = param.split("=")
            if value.isdigit():
                value = int(value)
            parameters[parameter] = value
        else:
            raise click.BadParameter(
                f"'{param}': Parameter can contain only digits,"
                " latin letters and underscore."
            )
    return parameters


@database.command("create", help="Create new database.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option(
    "--preset-id", type=int, required=True, help="Database preset ID."
)
@click.option("--name", required=True, help="Database display name.")
@click.option(
    "--type",
    "dbms",
    type=click.Choice(["mysql8", "mysql5", "postgres", "redis", "mongodb"]),
    required=True,
    help="DBMS.",
)
@click.option(
    "--hash-type",
    type=click.Choice(["caching_sha2", "mysql_native"]),
    default="caching_sha2",
    show_default=True,
    help="Authentication plugin for MySQL.",
)
@click.option(
    "--param",
    "params",
    multiple=True,
    help="Database parameters, can be multiple.",
)
@click.option(
    "--project-id",
    type=int,
    default=None,
    envvar="TWC_PROJECT",
    callback=set_value_from_config,
    help="Add database to specific project.",
)
@click.option("--login", default=None, help="Database user login.")
@click.option(
    "--password",
    prompt="Set database user password",
    hide_input=True,
    confirmation_prompt=True,
    help="Database user password.",
)
def database_create(
    config,
    profile,
    verbose,
    output_format,
    preset_id,
    name,
    dbms,
    hash_type,
    params,
    login,
    password,
    project_id,
):
    # pylint: disable=too-many-locals

    client = create_client(config, profile)

    if dbms == "mysql8":  # alias mysql8 for mysql
        dbms = "mysql"

    # Check preset_id
    for preset in _database_list_presets(client).json()["databases_presets"]:
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
        debug("Check project_id")
        projects = _project_list(client).json()["projects"]
        if not project_id in [prj["id"] for prj in projects]:
            raise click.BadParameter("Wrong project ID.")

    response = _database_create(client, **payload)

    # Add created DB to project if set
    if project_id:
        src_project = get_default_project_id(client)
        # Make useless request to avoid API bug (409 resource_not_found)
        _r = _project_resource_list_databases(client, src_project)
        new_db_id = response.json()["db"]["id"]
        debug(f"Add DB '{new_db_id}' to project '{project_id}'")
        project_resp = _project_resource_move(
            client,
            from_project=src_project,
            to_project=project_id,
            resource_id=new_db_id,
            resource_type="database",
        )
        debug(project_resp.text)

    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: click.echo(response.json()["db"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc database set                                            #
# ------------------------------------------------------------- #


@database.command("set", help="Set database properties or parameters.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option(
    "--preset-id", type=int, default=None, help="Database preset ID."
)
@click.option("--name", default=None, help="Database display name.")
@click.option(
    "--param",
    "params",
    metavar="PARAMETER=VALUE",
    multiple=True,
    default=None,
    help="Database parameters, can be multiple.",
)
@click.option(
    "--password",
    default=None,
    help="Database user password.",
)
@click.option(
    "--prompt-password",
    is_flag=True,
    help="Set database user password interactively.",
)
@click.option(
    "--external-ip",
    type=bool,
    default=None,
    help="Enable external IPv4 address.",
)
@click.argument("db_id", type=int, required=True)
def database_set(
    config,
    profile,
    verbose,
    output_format,
    preset_id,
    name,
    params,
    password,
    prompt_password,
    external_ip,
    db_id,
):
    # pylint: disable=too-many-locals

    client = create_client(config, profile)
    old_state = _database_get(client, db_id).json()["db"]
    new_params = {}

    if prompt_password:
        password = click.prompt(
            "Set database user password",
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

    response = _database_set(client, db_id, **payload)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: click.echo(response.json()["db"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc database remove                                         #
# ------------------------------------------------------------- #


@database.command("remove", aliases=["rm"], help="Remove database.")
@options(GLOBAL_OPTIONS)
@click.confirmation_option(prompt="This action cannot be undone. Continue?")
@click.argument("db_ids", nargs=-1, type=int, required=True)
def database_remove(config, profile, verbose, db_ids):
    client = create_client(config, profile)
    for db_id in db_ids:
        response = _database_remove(client, db_id)

        if response.status_code == 200:
            del_hash = response.json()["database_delete"]["hash"]
            del_code = click.prompt("Please enter confirmation code", type=int)
            response = _database_remove(
                client, db_id, delete_hash=del_hash, code=del_code
            )

        if response.status_code == 204:
            click.echo(db_id)
        else:
            fmt.printer(response)


# ------------------------------------------------------------- #
# $ twc database backup                                         #
# ------------------------------------------------------------- #


@database.group("backup", cls=ClickAliasedGroup)
@options(GLOBAL_OPTIONS[:2])
def db_backup():
    """Manage database backups."""


# ------------------------------------------------------------- #
# $ twc database backup list                                    #
# ------------------------------------------------------------- #


def print_db_backups(response: object):
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


@db_backup.command("list", aliases=["ls"], help="List backups.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.argument("db_id", type=int, required=True)
def database_backup_list(config, profile, verbose, output_format, db_id):
    client = create_client(config, profile)
    response = _database_backup_list(client, db_id)
    fmt.printer(
        response,
        output_format=output_format,
        func=print_db_backups,
    )


# ------------------------------------------------------------- #
# $ twc database backup create                                  #
# ------------------------------------------------------------- #


@db_backup.command("create", help="Backup database.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.argument("db_id", type=int, required=True)
def database_backup_create(config, profile, verbose, output_format, db_id):
    client = create_client(config, profile)
    response = _database_backup_create(client, db_id)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: click.echo(response.json()["backup"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc database backup remove                                  #
# ------------------------------------------------------------- #


@db_backup.command("remove", aliases=["rm"], help="Remove backup.")
@options(GLOBAL_OPTIONS)
@click.argument("db_id", type=int, required=True)
@click.argument("backup_id", type=int, required=True)
@click.confirmation_option(prompt="This action cannot be undone. Continue?")
def database_backup_remove(config, profile, verbose, db_id, backup_id):
    client = create_client(config, profile)
    response = _database_backup_remove(client, db_id, backup_id)
    if response.status_code == 204:
        click.echo(backup_id)
    else:
        fmt.printer(response)


# ------------------------------------------------------------- #
# $ twc database backup restore                                 #
# ------------------------------------------------------------- #


@db_backup.command("restore", help="Remove backup.")
@options(GLOBAL_OPTIONS)
@click.argument("db_id", type=int, required=True)
@click.argument("backup_id", type=int, required=True)
@click.confirmation_option(prompt="Data on target disk will lost. Continue?")
def database_backup_restore(config, profile, verbose, db_id, backup_id):
    client = create_client(config, profile)
    response = _database_backup_restore(client, db_id, backup_id)
    if response.status_code == 204:
        click.echo(backup_id)
    else:
        fmt.printer(response)
