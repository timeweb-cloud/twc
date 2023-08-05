"""Manage virtual networks."""

import sys
from typing import Optional, List
from pathlib import Path
from ipaddress import (
    IPv4Network,
    AddressValueError,
    NetmaskValueError,
)

import typer
from requests import Response

from twc import fmt
from twc.typerx import TyperAlias
from twc.apiwrap import create_client
from twc.vars import REGIONS_WITH_LAN
from .common import (
    verbose_option,
    config_option,
    profile_option,
    yes_option,
    output_format_option,
    filter_option,
    region_option,
)


vpc = TyperAlias(help=__doc__)


# ------------------------------------------------------------- #
# $ twc vpc list                                                #
# ------------------------------------------------------------- #


def print_networks(response: Response, filters: Optional[str] = None):
    nets = response.json()["vpcs"]
    if filters:
        nets = fmt.filter_list(nets, filters)
    table = fmt.Table()
    table.header(["ID", "REGION", "SUBNET"])
    for net in nets:
        table.row(
            [
                net["id"],
                net["location"],
                net["subnet_v4"],
            ]
        )
    table.print()


@vpc.command("list", "ls")
def vpc_list(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
):
    """List networks."""
    client = create_client(config, profile)
    response = client.get_vpcs()
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_networks,
    )


# ------------------------------------------------------------- #
# $ twc vpc create                                              #
# ------------------------------------------------------------- #


def validate_network(value):
    if value:
        try:
            network = IPv4Network(value)
        except (NetmaskValueError, AddressValueError, ValueError) as err:
            sys.exit(f"Error: Invalid CIDR: {err}")
        if not network.is_private:
            sys.exit(f"Error: Network {value} is not for private usage.")
        net_192 = IPv4Network("192.168.0.0/16")
        net_10 = IPv4Network("10.0.0.0/8")
        if not network.subnet_of(net_10) and not network.subnet_of(net_192):
            sys.exit(
                "Error: Only subnets of 10.0.0.0/8 and 192.168.0.0/16 is allowed."
            )
        if not (network.prefixlen >= 16 and network.prefixlen <= 32):
            sys.exit("Error: Minimum network prefix is 32, maximum is 16.")
    return value


@vpc.command("create")
def vpc_create(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    name: str = typer.Option(..., help="Network display name."),
    desc: Optional[str] = typer.Option(None, help="Description."),
    subnet: str = typer.Option(
        ...,
        callback=validate_network,
        help="Network IPv4 CIDR.",
    ),
    region: Optional[str] = region_option,
):
    """Create network."""
    client = create_client(config, profile)
    if region not in REGIONS_WITH_LAN:
        sys.exit(
            f"Error: Cannot create network in location '{region}'. "
            f"Available regions is {REGIONS_WITH_LAN}"
        )
    response = client.create_vpc(
        name,
        description=desc,
        subnet=subnet,
        location=region,
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["vpc"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc vpc remove                                              #
# ------------------------------------------------------------- #


@vpc.command("remove", "rm")
def vpc_remove(
    vpc_ids: List[str] = typer.Argument(..., metavar="VPC_ID..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    yes: Optional[bool] = yes_option,
):
    """Remove network."""
    if not yes:
        typer.confirm("This action cannot be undone. Continue?", abort=True)
    client = create_client(config, profile)
    for vpc_id in vpc_ids:
        response = client.delete_vpc(vpc_id)
        if response.status_code == 204:
            print(vpc_id)
        else:
            sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc vpc set                                                 #
# ------------------------------------------------------------- #


@vpc.command("set")
def vpc_set(
    vpc_id: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    name: Optional[str] = typer.Option(None, help="Network display name."),
    desc: Optional[str] = typer.Option(None, help="Description."),
):
    """Set network properties."""
    client = create_client(config, profile)
    response = client.update_vpc(vpc_id, name=name, description=desc)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["vpc"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc vpc list-ports                                          #
# ------------------------------------------------------------- #


def print_ports(response: Response, filters: Optional[str] = None):
    ports = response.json()["vpc_ports"]
    if filters:
        ports = fmt.filter_list(ports, filters)
    table = fmt.Table()
    table.header(
        [
            "ID",
            "NAT",
            "IP",
        ]
    )
    for port in ports:
        table.row(
            [
                port["id"],
                port["nat_mode"],
                port["ipv4"],
            ]
        )
    table.print()


@vpc.command("list-ports", "lsp", "ports")
def vpc_ports(
    vpc_id: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
):
    """List network ports."""
    client = create_client(config, profile)
    response = client.get_vpc_ports(vpc_id)
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_ports,
    )


# ------------------------------------------------------------- #
# $ twc vpc show                                                #
# ------------------------------------------------------------- #


def print_resources(response: Response, filters: Optional[str] = None):
    resources = response.json()["services"]
    if filters:
        resources = fmt.filter_list(resources, filters)
    table = fmt.Table()
    table.header(
        [
            "ID",
            "NAME",
            "TYPE",
            "PUBLIC IP",
            "PRIVATE IP",
        ]
    )
    for res in resources:
        table.row(
            [
                res["id"],
                res["name"],
                res["type"],
                res["public_ip"],
                res["local_ip"],
            ]
        )
    table.print()


@vpc.command("show")
def vpc_show(
    vpc_id: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
):
    """List resources in network."""
    client = create_client(config, profile)
    response = client.get_services_in_vpc(vpc_id)
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_resources,
    )
