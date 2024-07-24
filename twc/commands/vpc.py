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
from twc.api import ServiceRegion
from twc.typerx import TyperAlias
from twc.apiwrap import create_client
from twc.vars import REGIONS_WITH_LAN, ZONES_WITH_LAN
from .common import (
    verbose_option,
    config_option,
    profile_option,
    yes_option,
    output_format_option,
    filter_option,
    region_option,
    zone_option,
)


vpc = TyperAlias(help=__doc__)
vpc_port = TyperAlias(help="Manage network ports.")
vpc.add_typer(vpc_port, name="port", aliases=["ports"])

ALLOWED_SUBNETS = [
    IPv4Network("10.0.0.0/8"),
    IPv4Network("192.168.0.0/16"),
    IPv4Network("172.16.0.0/12"),
]


# ------------------------------------------------------------- #
# $ twc vpc list                                                #
# ------------------------------------------------------------- #


def print_networks(response: Response, filters: Optional[str] = None):
    nets = response.json()["vpcs"]
    if filters:
        nets = fmt.filter_list(nets, filters)
    table = fmt.Table()
    table.header(["ID", "REGION", "ZONE", "SUBNET"])
    for net in nets:
        table.row(
            [
                net["id"],
                net["location"],
                net["availability_zone"],
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

        is_valid = False
        for subnet in ALLOWED_SUBNETS:
            if network.subnet_of(subnet):
                is_valid = True

        if is_valid is False:
            sys.exit(
                f"Error: Network {value} is not subnet of: "
                f"{[n.with_prefixlen for n in ALLOWED_SUBNETS]}"
            )
    return value


@vpc.command("create")
def vpc_create(
    subnet: str = typer.Argument(
        ...,
        metavar="NETWORK_SUBNET",
        callback=validate_network,
        help="IPv4 network CIDR.",
    ),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    name: str = typer.Option(None, help="Network display name."),
    desc: Optional[str] = typer.Option(None, help="Description."),
    region: Optional[str] = region_option,
    availability_zone: Optional[str] = zone_option,
):
    """Create network."""
    client = create_client(config, profile)
    if region not in REGIONS_WITH_LAN:
        sys.exit(
            f"Error: Cannot create network in location '{region}'. "
            f"Available regions are: {REGIONS_WITH_LAN}"
        )
    usable_zones = set(ZONES_WITH_LAN).intersection(
        set(ServiceRegion.get_zones(region))
    )
    if availability_zone is not None and availability_zone not in usable_zones:
        sys.exit(
            f"Error: Cannot create network in region '{region}' with "
            f"availability zone '{availability_zone}'. "
            f"Usable zones are: {list(usable_zones)}"
        )
    if not name:
        name = subnet
    response = client.create_vpc(
        name,
        description=desc,
        subnet=subnet,
        location=region,
        availability_zone=availability_zone,
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
# $ twc vpc port list                                           #
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


@vpc_port.command("list", "ls")
def vpc_ports_list(
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
            "PRIVATE IP",
            "PUBLIC IP",
        ]
    )
    for res in resources:
        table.row(
            [
                res["id"],
                res["name"],
                res["type"],
                res["local_ip"],
                res["public_ip"],
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
