"""Manage SSH-keys."""

import sys
from typing import Optional, List
from pathlib import Path

import typer
from click import UsageError
from requests import Response

from twc import fmt
from twc.typerx import TyperAlias
from twc.apiwrap import create_client
from .common import (
    verbose_option,
    config_option,
    profile_option,
    yes_option,
    output_format_option,
)


ssh_key = TyperAlias(help=__doc__)


# ------------------------------------------------------------- #
# $ twc ssh-key list                                            #
# ------------------------------------------------------------- #


def print_ssh_keys(response: Response):
    """Print table with SSH-keys list."""
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


@ssh_key.command("list", "ls")
def ssh_key_list(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """List SSH-keys."""
    client = create_client(config, profile)
    response = client.get_ssh_keys()
    fmt.printer(
        response,
        output_format=output_format,
        func=print_ssh_keys,
    )


# ------------------------------------------------------------- #
# $ twc ssh-key get                                             #
# ------------------------------------------------------------- #


def print_ssh_key(response: Response):
    """Print table with SSH-key info."""
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


@ssh_key.command("get")
def ssh_key_get(
    ssh_key_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """Get SSH-key by ID."""
    client = create_client(config, profile)
    response = client.get_ssh_key(ssh_key_id)
    fmt.printer(
        response,
        output_format=output_format,
        func=print_ssh_key,
    )


# ------------------------------------------------------------- #
# $ twc ssh-key new                                             #
# ------------------------------------------------------------- #


@ssh_key.command("new")
def ssh_key_new(
    public_key_file: Path = typer.Argument(
        ...,
        metavar="FILE",
        exists=True,
        dir_okay=False,
    ),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    name: Optional[str] = typer.Option(None, help="SSH-key display name."),
    default: Optional[bool] = typer.Option(
        False,
        "--default",
        help="Set as default key for new Cloud Servers.",
    ),
):
    """Upload new SSH-key."""
    if not name:
        name = Path(public_key_file).name

    try:
        with open(public_key_file, "r", encoding="utf-8") as pubkey:
            body = pubkey.read().strip()
    except (OSError, IOError, FileNotFoundError) as error:
        sys.exit(f"Error: {error}")

    client = create_client(config, profile)
    response = client.add_new_ssh_key(
        name=name,
        is_default=default,
        body=body,
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["ssh_key"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc ssh-key edit                                            #
# ------------------------------------------------------------- #


@ssh_key.command("edit", "set", "update", "upd")
def ssh_key_edit(
    ssh_key_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    name: Optional[str] = typer.Option(None, help="SSH-key display name."),
    public_key_file: Optional[Path] = typer.Option(
        None,
        metavar="FILE",
        exists=True,
        dir_okay=False,
        help="Public key file.",
    ),
    default: Optional[bool] = typer.Option(
        False,
        "--default",
        help="Set as default key for new Cloud Servers.",
    ),
):
    """Edit SSH-key and they properties."""
    client = create_client(config, profile)
    body = None

    if public_key_file:
        try:
            with open(public_key_file, "r", encoding="utf-8") as pubkey:
                body = pubkey.read().strip()
        except (OSError, IOError, FileNotFoundError) as error:
            sys.exit(f"Error: {error}")

    response = client.update_ssh_key(
        ssh_key_id,
        name=name,
        body=body,
        is_default=default,
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["ssh_key"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc ssh-key add                                             #
# ------------------------------------------------------------- #


@ssh_key.command("add", "copy")
def ssh_key_add(
    server_id: int = typer.Argument(...),
    ssh_keys_ids: List[int] = typer.Argument(..., metavar="SSH_KEY_ID..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
):
    """Copy SSH-keys to Cloud Server."""
    client = create_client(config, profile)
    response = client.add_ssh_key_to_server(server_id, ssh_keys_ids)
    if response.status_code == 204:
        print(server_id)
    else:
        sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc ssh-key remove                                          #
# ------------------------------------------------------------- #


@ssh_key.command("remove", "rm")
def ssh_key_remove(
    ssh_keys_ids: List[int] = typer.Argument(..., metavar="SSH_KEY_ID..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    server_id: Optional[int] = typer.Option(
        None,
        "--from-server",
        metavar="SERVER_ID",
        help="Remove SSH-key from server instead of remove key itself.",
    ),
    yes: Optional[bool] = yes_option,
):
    """Remove SSH-keys."""
    if not yes:
        typer.confirm(
            "If you do not specify '--from-server' option "
            "SSH-key will be deleted\nfrom all servers where it was added "
            "and also deleted itself.\nContinue?",
            abort=True,
        )
    client = create_client(config, profile)
    if server_id:
        if len(ssh_keys_ids) >= 2:
            raise UsageError("Cannot remove multiple keys from server.")
        response = client.delete_ssh_key_from_server(
            server_id, ssh_keys_ids[0]
        )
        if response.status_code == 204:
            print(ssh_keys_ids[0])
            raise typer.Exit()
        sys.exit(fmt.printer(response))

    for ssh_key_id in ssh_keys_ids:
        response = client.delete_ssh_key(ssh_key_id)
        if response.status_code == 204:
            print(ssh_key_id)
        else:
            sys.exit(fmt.printer(response))
