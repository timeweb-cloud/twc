"""Manage floating IPs."""

import sys
from typing import Optional, List
from pathlib import Path
from uuid import UUID

import typer
from requests import Response

from twc import fmt
from twc.api import TimewebCloud, ResourceType
from twc.apiwrap import create_client
from twc.typerx import TyperAlias
from .common import (
    verbose_option,
    config_option,
    profile_option,
    yes_option,
    output_format_option,
    load_from_config_callback,
)


floating_ip = TyperAlias(help=__doc__)


def get_floating_ip_id(client: TimewebCloud, ip_addr: str) -> Optional[str]:
    ips = client.get_floating_ips().json()["ips"]
    for ip in ips:
        if ip["ip"] == ip_addr:
            return ip["id"]
    return None


# ------------------------------------------------------------- #
# $ twc floating-ip list                                        #
# ------------------------------------------------------------- #


def _print_floating_ips(response: Response):
    table = fmt.Table()
    table.header(["IP", "PTR", "ZONE", "ANTI_DDOS", "USED_ON"])
    ips = response.json()["ips"]
    for ip in ips:
        used = None
        if ip["resource_type"]:
            used = f"{ip['resource_type']}:{ip['resource_id']}"
        table.row(
            [
                ip["ip"],
                ip["ptr"],
                ip["availability_zone"],
                ip["is_ddos_guard"],
                used,
            ]
        )
    table.print()


@floating_ip.command("list", "ls")
def floating_ip_list(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """List floating IPs."""
    client = create_client(config, profile)
    response = client.get_floating_ips()
    fmt.printer(
        response,
        output_format=output_format,
        func=_print_floating_ips,
    )


# ------------------------------------------------------------- #
# $ twc floating-ip get                                         #
# ------------------------------------------------------------- #


def _print_floating_ip(response: Response):
    table = fmt.Table()
    table.header(["IP", "PTR", "ZONE", "ANTI_DDOS", "USED_ON"])
    ip = response.json()["ip"]
    used = None
    if ip["resource_type"]:
        used = f"{ip['resource_type']}:{ip['resource_id']}"
    table.row(
        [
            ip["ip"],
            ip["ptr"],
            ip["availability_zone"],
            ip["is_ddos_guard"],
            used,
        ]
    )
    table.print()


@floating_ip.command("get")
def floating_ip_get(
    ip: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """Get floating IP."""
    client = create_client(config, profile)
    try:
        _ = UUID(ip)
    except ValueError:
        ip = get_floating_ip_id(client, ip)
    response = client.get_floating_ip(ip)
    fmt.printer(
        response,
        output_format=output_format,
        func=_print_floating_ip,
    )


# ------------------------------------------------------------- #
# $ twc floating-ip create                                      #
# ------------------------------------------------------------- #


@floating_ip.command("create")
def floating_ip_create(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    availability_zone: str = typer.Option(
        ...,
        metavar="ZONE",
        envvar="TWC_AVAILABILITY_ZONE",
        show_envvar=False,
        callback=load_from_config_callback,
        help="Availability zone.",
    ),
    ddos_protection: bool = typer.Option(
        False,
        "--ddos-protection",
        show_default=True,
        help="Request IP-address with L3/L4 DDoS protection.",
    ),
):
    """Create new floating IP."""
    client = create_client(config, profile)
    response = client.create_floating_ip(
        availability_zone=availability_zone,
        ddos_protection=ddos_protection,
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["ip"]["ip"]),
    )


# ------------------------------------------------------------- #
# $ twc floating-ip remove                                      #
# ------------------------------------------------------------- #


@floating_ip.command("remove", "rm")
def floating_ip_remove(
    floating_ips: List[str] = typer.Argument(..., metavar="IP..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
):
    """Remove floating IPs."""
    if not yes:
        typer.confirm("This action cannot be undone, continue?", abort=True)

    client = create_client(config, profile)
    for ip in floating_ips:
        try:
            _ = UUID(ip)
        except ValueError:
            ip = get_floating_ip_id(client, ip)
        response = client.delete_floating_ip(ip)
        if response.status_code == 204:
            print(ip)
        else:
            sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc floating-ip attach                                      #
# ------------------------------------------------------------- #


@floating_ip.command("attach")
def floating_ip_attach(
    ip: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    server: Optional[int] = typer.Option(
        None, help="Attach IP to Cloud Server."
    ),
    balancer: Optional[int] = typer.Option(
        None, help="Attach IP to Load Balancer."
    ),
    database: Optional[int] = typer.Option(
        None, help="Attach IP to managed database cluster."
    ),
):
    """Attach floating IP to service."""
    client = create_client(config, profile)
    try:
        _ = UUID(ip)
    except ValueError:
        ip = get_floating_ip_id(client, ip)
    resource_type = resource_id = None
    if server:
        resource_type = ResourceType.SERVER
        resource_id = server
    if balancer:
        resource_type = ResourceType.BALANCER
        resource_id = balancer
    if database:
        resource_type = ResourceType.DATABASE
        resource_id = database
    response = client.attach_floating_ip(
        ip,
        resource_type=resource_type,
        resource_id=resource_id,
    )
    if not resource_type or not resource_id:
        sys.exit(
            "Error: Please set one of options: ['--server', '--balancer', '--database']"
        )
    if response.status_code == 204:
        print(resource_id)
    else:
        sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc floating-ip detach                                      #
# ------------------------------------------------------------- #


@floating_ip.command("detach")
def floating_ip_detach(
    ip: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
):
    """Detach floating IP from service."""
    client = create_client(config, profile)
    try:
        _ = UUID(ip)
    except ValueError:
        ip = get_floating_ip_id(client, ip)
    response = client.detach_floating_ip(ip)
    if response.status_code == 204:
        print(ip)
    else:
        sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc floating-ip set                                         #
# ------------------------------------------------------------- #


@floating_ip.command("set")
def floating_ip_set(
    ip: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    comment: Optional[str] = typer.Option(None, help="Set comment."),
    ptr: Optional[str] = typer.Option(None, help="Set reverse DNS pointer."),
):
    """Set floating IP parameters."""
    client = create_client(config, profile)
    try:
        _ = UUID(ip)
    except ValueError:
        ip = get_floating_ip_id(client, ip)
    response = client.update_floating_ip(ip, comment=comment, ptr=ptr)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["ip"]["ip"]),
    )
