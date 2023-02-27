"""SSH-key management commands."""

import os
import sys

import click
from click_aliases import ClickAliasedGroup

from twc import fmt
from . import (
    create_client,
    handle_request,
    options,
    GLOBAL_OPTIONS,
    OUTPUT_FORMAT_OPTION,
)


@handle_request
def _ssh_key_list(client):
    return client.get_ssh_keys()


@handle_request
def _ssh_key_get(client, *args):
    return client.get_ssh_key(*args)


@handle_request
def _ssh_key_new(client, **kwargs):
    return client.add_new_ssh_key(**kwargs)


@handle_request
def _ssh_key_edit(client, *args, **kwargs):
    return client.update_ssh_key(*args, **kwargs)


@handle_request
def _ssh_key_add(client, *args, **kwargs):
    return client.add_ssh_key_to_server(*args, **kwargs)


@handle_request
def _ssh_key_remove(client, *args):
    return client.delete_ssh_key(*args)


@handle_request
def _ssh_key_remove_from_server(client, *args):
    return client.delete_ssh_key_from_server(*args)


# ------------------------------------------------------------- #
# $ twc ssh-key                                                 #
# ------------------------------------------------------------- #


@click.group("ssh-key", cls=ClickAliasedGroup)
@options(GLOBAL_OPTIONS[:2])
def ssh_key():
    """Manage SSH-keys."""


# ------------------------------------------------------------- #
# $ twc ssh-key list                                            #
# ------------------------------------------------------------- #


def print_ssh_keys(response: object):
    table = fmt.Table()
    table.header(["ID", "NAME", "DEFAULT", "SERVERS"])
    keys = response.json()["ssh_keys"]
    for key in keys:
        table.row(
            [
                key["id"],
                key["name"],
                key["is_default"],
                ", ".join([str(k["id"]) for k in key["used_by"]]),
            ]
        )
    table.print()


@ssh_key.command("list", aliases=["ls"], help="List SSH-keys.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
def ssh_key_list(config, profile, verbose, output_format):
    client = create_client(config, profile)
    response = _ssh_key_list(client)
    fmt.printer(
        response,
        output_format=output_format,
        func=print_ssh_keys,
    )


# ------------------------------------------------------------- #
# $ twc ssh-key get                                             #
# ------------------------------------------------------------- #


def print_ssh_key(response: object):
    table = fmt.Table()
    table.header(["ID", "NAME", "DEFAULT", "SERVERS"])
    key = response.json()["ssh_key"]
    table.row(
        [
            key["id"],
            key["name"],
            key["is_default"],
            ", ".join([str(k["id"]) for k in key["used_by"]]),
        ]
    )
    table.print()


@ssh_key.command("get", help="Get SSH-key by ID.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.argument("ssh_key_id", required=True)
def ssh_key_get(config, profile, verbose, output_format, ssh_key_id):
    client = create_client(config, profile)
    response = _ssh_key_get(client, ssh_key_id)
    fmt.printer(
        response,
        output_format=output_format,
        func=print_ssh_key,
    )


# ------------------------------------------------------------- #
# $ twc ssh-key new                                             #
# ------------------------------------------------------------- #


@ssh_key.command("new", help="Add new SSH-key.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option("--name", help="SSH-key display name.")
@click.option(
    "--default",
    type=bool,
    default=False,
    show_default=True,
    help="If True add this key to all new Cloud Servers.",
)
@click.argument("public_key_file", type=click.Path(exists=True), required=True)
def ssh_key_new(
    config, profile, verbose, output_format, name, default, public_key_file
):
    if not name:
        name = os.path.basename(public_key_file)

    try:
        with open(public_key_file, "r", encoding="utf-8") as pubkey:
            body = pubkey.read().strip()
    except (OSError, IOError, FileNotFoundError) as error:
        sys.exit(f"Error: {error}")

    client = create_client(config, profile)
    response = _ssh_key_new(
        client,
        name=name,
        is_default=default,
        body=body,
    )

    fmt.printer(response, output_format=output_format, func=print_ssh_key)


# ------------------------------------------------------------- #
# $ twc ssh-key edit                                            #
# ------------------------------------------------------------- #


@ssh_key.command("edit", help="Edit SSH-key and they properties.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option("--name", default=None, help="SSH-key display name.")
@click.option(
    "--default",
    type=bool,
    default=False,
    show_default=True,
    help="If True add this key to all new Cloud Servers.",
)
@click.option(
    "--file",
    "public_key_file",
    type=click.Path(),
    default=None,
    help="Public key file.",
)
@click.argument("ssh_key_id", required=True)
def ssh_key_edit(
    config,
    profile,
    verbose,
    output_format,
    name,
    default,
    public_key_file,
    ssh_key_id,
):
    client = create_client(config, profile)
    payload = {}

    if name:
        payload.update({"name": name})

    if default:
        payload.update({"is_default": default})

    if public_key_file:
        try:
            with open(public_key_file, "r", encoding="utf-8") as pubkey:
                body = pubkey.read().strip()
                payload.update({"body": body})
        except (OSError, IOError, FileNotFoundError) as error:
            sys.exit(f"Error: {error}")

    if not payload:
        raise click.UsageError(
            "Nothing to do. Set one of ['--name', '--file', '--default']"
        )

    response = _ssh_key_edit(client, ssh_key_id, data=payload)

    fmt.printer(response, output_format=output_format, func=print_ssh_key)


# ------------------------------------------------------------- #
# $ twc ssh-key add                                             #
# ------------------------------------------------------------- #


@ssh_key.command(
    "add", aliases=["copy"], help="Copy SSH-keys to Cloud Server."
)
@options(GLOBAL_OPTIONS)
@click.option(
    "--to-server",
    "server_id",
    type=int,
    help="Cloud Server ID.",
)
@click.argument("ssh_key_ids", nargs=-1, required=True)
def ssh_key_add(config, profile, verbose, server_id, ssh_key_ids):
    client = create_client(config, profile)
    response = _ssh_key_add(client, server_id, ssh_key_ids=list(ssh_key_ids))
    if response.status_code == 204:
        print(server_id)
    else:
        fmt.printer(response)


# ------------------------------------------------------------- #
# $ twc ssh-key remove                                          #
# ------------------------------------------------------------- #


@ssh_key.command("remove", aliases=["rm"], help="Remove SSH-keys.")
@options(GLOBAL_OPTIONS)
@click.option(
    "--from-server",
    "server_id",
    type=int,
    help="Remove SSH-key from Cloud Server instead of remove key itself.",
)
@click.confirmation_option(
    prompt="If you do not specify '--from-server' option "
    "SSH-key will be deleted\nfrom all servers where it was added "
    "and also deleted itself.\nContinue?"
)
@click.argument("ssh_key_ids", nargs=-1, required=True)
def ssh_key_remove(config, profile, verbose, server_id, ssh_key_ids):
    client = create_client(config, profile)
    if server_id:
        if len(ssh_key_ids) >= 2:
            raise click.UsageError("Cannot remove multiple keys from server.")
        response = _ssh_key_remove_from_server(
            client, server_id, list(ssh_key_ids)[0]
        )
        if response.status_code == 204:
            print(list(ssh_key_ids)[0])
        else:
            fmt.printer(response)
    else:
        for key_id in ssh_key_ids:
            response = _ssh_key_remove(client, key_id)
            if response.status_code == 204:
                print(key_id)
            else:
                fmt.printer(response)
