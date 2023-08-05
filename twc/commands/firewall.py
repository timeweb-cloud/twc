"""Manage Cloud Firewall rules and groups."""

import sys
import json
import textwrap
from typing import Optional, List
from pathlib import Path
from uuid import UUID
from ipaddress import (
    IPv4Network,
    IPv6Network,
    AddressValueError,
    NetmaskValueError,
)

import typer
import yaml
from requests import Response

from twc import fmt
from twc.typerx import TyperAlias
from twc.apiwrap import create_client
from .common import (
    verbose_option,
    config_option,
    profile_option,
    output_format_option,
    OutputFormat,
    filter_option,
)


firewall = TyperAlias(help=__doc__)
firewall_group = TyperAlias(help="Manage firewall groups.")
firewall_rule = TyperAlias(help="Manage firewall rules.")
firewall.add_typer(firewall_group, name="group", aliases=["groups"])
firewall.add_typer(firewall_rule, name="rule", aliases=["rules"])


# ------------------------------------------------------------- #
# $ twc firewall status                                         #
# ------------------------------------------------------------- #


def print_firewall_status(data: list):
    for group in data:
        info = f"Group: {group['name']} ({group['id']})"
        for rule in group["rules"]:
            info += "\n" + textwrap.indent(
                textwrap.dedent(
                    f"""
                Rule: {rule['id']}
                  Direction: {rule['direction']}
                  Protocol: {rule['protocol']}
                  Port: {rule['port']}
                  CIDR: {rule['cidr']}
                """
                ).strip(),
                "  ",
            )
        if group["resources"]:
            info += "\n  Resources:\n"
            servers = [
                r["id"] for r in group["resources"] if r["type"] == "server"
            ]
            databases = [
                r["id"] for r in group["resources"] if r["type"] == "dbaas"
            ]
            balancers = [
                r["id"] for r in group["resources"] if r["type"] == "balancer"
            ]
            if servers:
                info += textwrap.indent(f"Servers: {servers}\n", " " * 4)
            if databases:
                info += textwrap.indent(f"Databases: {databases}\n", " " * 4)
            if balancers:
                info += textwrap.indent(
                    f"Load Balancers: {balancers}\n", " " * 4
                )
        print(info.strip())


@firewall.command("status")
def firewall_status(
    group_id: List[UUID] = typer.Argument(None),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """Print firewall status."""
    client = create_client(config, profile)
    data = []

    if group_id:
        groups = group_id
    else:
        groups = client.get_firewall_groups().json()["groups"]

    for group in groups:
        rules = client.get_firewall_rules(group["id"]).json()["rules"]
        resources = client.get_firewall_group_resources(group["id"]).json()[
            "resources"
        ]
        data.append(
            {
                "id": group["id"],
                "name": group["name"],
                "rules": rules,
                "resources": resources,
            }
        )

    formats = [f.value for f in OutputFormat]
    if output_format in formats:
        if output_format == "raw":
            print(data)
        else:
            encoders = {
                "yaml": yaml.dump,
                "json": json.dumps,
            }
            fmt.print_colored(
                encoders[output_format](data), lang=output_format
            )
    else:
        print_firewall_status(data)


# ------------------------------------------------------------- #
# $ twc firewall group list                                     #
# ------------------------------------------------------------- #


def print_firewall_groups(response: Response):
    groups = response.json()["groups"]
    table = fmt.Table()
    table.header(["ID", "NAME"])
    for group in groups:
        table.row(
            [
                group["id"],
                group["name"],
            ]
        )
    table.print()


@firewall_group.command("list")
def firewall_group_list(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """List groups."""
    client = create_client(config, profile)
    response = client.get_firewall_groups()
    fmt.printer(
        response,
        output_format=output_format,
        func=print_firewall_groups,
    )


# ------------------------------------------------------------- #
# $ twc firewall groupi create                                  #
# ------------------------------------------------------------- #


@firewall_group.command("create")
def firewall_group_create(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    name: str = typer.Option(..., help="Group display name."),
    desc: Optional[str] = typer.Option(None, help="Description."),
):
    """Create new group of firewall rules."""
    client = create_client(config, profile)
    response = client.create_firewall_group(
        name=name,
        description=desc,
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["group"]["id"]),
    )
