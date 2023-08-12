"""Manage Cloud Firewall rules and groups."""

import re
import sys
import json
import textwrap
from typing import Optional, List, Tuple
from pathlib import Path
from uuid import UUID
from enum import Enum
from ipaddress import ip_network
from datetime import datetime
import logging

import typer
from click import UsageError
import yaml
from requests import Response

from twc import fmt
from twc.api import TimewebCloud, FirewallProto
from twc.typerx import TyperAlias
from twc.apiwrap import create_client
from .common import (
    verbose_option,
    config_option,
    profile_option,
    filter_option,
    output_format_option,
    OutputFormat,
    yes_option,
)


firewall = TyperAlias(help=__doc__)
firewall_group = TyperAlias(help="Manage firewall groups.")
firewall_rule = TyperAlias(help="Manage firewall rules.")
firewall.add_typer(firewall_group, name="group", aliases=["groups"])
firewall.add_typer(firewall_rule, name="rule", aliases=["rules"])


class _ResourceType(str, Enum):
    SERVER = "server"
    DATABASE = "database"
    BALANCER = "balancer"


class _ResourceType2(str, Enum):
    # Ugly class for 'show' command
    SERVER = "server"
    DATABASE = "database"
    BALANCER = "balancer"
    ALL = "all"


# API issue: inconsistent resource naming: database->dbaas
RESOURCE_TYPES = {
    "server": "server",
    "database": "dbaas",  # fix naming
    "balancer": "balancer",
}


# ------------------------------------------------------------- #
# $ twc firewall show                                           #
# ------------------------------------------------------------- #


def print_firewall_status(data: list):
    print("Groups total:", len(data))
    rules_total = 0
    for group in data:
        rules_total += len(group["rules"])
    print("Rules total:", rules_total)
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


def print_rules_by_service(rules, filters):
    if filters:
        rules = fmt.filter_list(rules, filters)
    table = fmt.Table()
    table.header(
        [
            "GROUP ID",
            "RULE ID",
            "DIRECTION",
            "PROTO",
            "PORTS",
            "CIDR",
        ]
    )
    for rule in rules:
        table.row(
            [
                rule["group_id"],
                rule["id"],
                rule["direction"],
                rule["protocol"],
                rule["port"],
                rule["cidr"],
            ]
        )
    table.print()


@firewall.command("show")
def firewall_status(
    resource_type: _ResourceType2 = typer.Argument(
        ...,
        metavar="(server|database|balancer|all)",
    ),
    resource_id: str = typer.Argument(None),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
):
    """Display firewall status."""
    client = create_client(config, profile)
    data = []

    if resource_type in [r.value for r in _ResourceType]:
        rules_total = []
        if resource_id is None:
            raise UsageError(
                "Resource ID is required for "
                f"{[r.value for r in _ResourceType]}"
            )
        groups_ = client.get_resource_firewall_groups(
            int(resource_id), RESOURCE_TYPES[resource_type]
        ).json()["groups"]
        for group_ in groups_:
            rules_ = client.get_firewall_rules(group_["id"]).json()["rules"]
            rules_total.extend(rules_)
        print_rules_by_service(rules_total, filters)

    if resource_type == "all":
        if resource_id:
            groups = [client.get_firewall_group(resource_id).json()["group"]]
        else:
            groups = client.get_firewall_groups().json()["groups"]

        for group in groups:
            rules = client.get_firewall_rules(group["id"]).json()["rules"]
            resources = client.get_firewall_group_resources(
                group["id"]
            ).json()["resources"]
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
# $ twc firewall group create                                   #
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


# ------------------------------------------------------------- #
# $ twc firewall group remove                                   #
# ------------------------------------------------------------- #


@firewall_group.command("remove", "rm")
def firewall_group_remove(
    group_ids: List[UUID] = typer.Argument(..., metavar="GROUP_ID..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
):
    """Remove rules group. All rules in group will lost."""
    if not yes:
        typer.confirm("This action cannot be undone. Continue?", abort=True)
    client = create_client(config, profile)
    for group_id in group_ids:
        response = client.delete_firewall_group(group_id)
        if response.status_code == 204:
            print(group_id)
        else:
            sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc firewall group set                                      #
# ------------------------------------------------------------- #


@firewall_group.command("set")
def firewall_group_set(
    group_id: UUID,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    name: Optional[str] = typer.Option(None, help="Group display name"),
    desc: Optional[str] = typer.Option(None, help="Description."),
):
    """Set rules group properties."""
    client = create_client(config, profile)
    if not name and not desc:
        raise UsageError(
            "Nothing to do. Set one of options: ['--name', '--desc']"
        )
    if not name:
        # Get old firewall group name, because name is required
        name = client.get_firewall_group(group_id).json()["group"]["name"]
    response = client.update_firewall_group(group_id, name, desc)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["group"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc firewall link                                           #
# ------------------------------------------------------------- #


@firewall.command("link")
def firewall_link(
    resource_type: _ResourceType = typer.Argument(
        ...,
        metavar="(server|database|balancer)",
    ),
    resource_id: int = typer.Argument(...),
    group_id: UUID = typer.Argument(...),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """Link rules group to service."""
    client = create_client(config, profile)
    response = client.link_resource_to_firewall(
        group_id,
        resource_id,
        RESOURCE_TYPES[resource_type],
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["resource"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc firewall unlink                                         #
# ------------------------------------------------------------- #


@firewall.command("unlink")
def firewall_unlink(
    resource_type: _ResourceType = typer.Argument(
        ...,
        metavar="(server|database|balancer)",
    ),
    resource_id: int = typer.Argument(...),
    group_id: UUID = typer.Argument(None),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    all_groups: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Unlink all linked firewall groups.",
    ),
):
    """Unlink rules group from service."""
    if not all_groups and group_id is None:
        raise UsageError(
            "One of parameters is required: ['--all', 'GROUP_ID']"
        )
    client = create_client(config, profile)
    if all_groups:
        groups_ = client.get_resource_firewall_groups(
            resource_id, RESOURCE_TYPES[resource_type]
        )
        groups = [g["id"] for g in groups_.json()["groups"]]
    else:
        groups = [group_id]
    for group in groups:
        response = client.unlink_resource_from_firewall(
            group,
            resource_id,
            RESOURCE_TYPES[resource_type],
        )
        if response.status_code == 204:
            print("Unlinked:", group)
        else:
            sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc firewall rule list                                      #
# ------------------------------------------------------------- #


def print_rules(response: Response):
    rules = response.json()["rules"]
    table = fmt.Table()
    table.header(
        [
            "ID",
            "DIRECTION",
            "PROTO",
            "PORTS",
            "CIDR",
        ]
    )
    for rule in rules:
        table.row(
            [
                rule["id"],
                rule["direction"],
                rule["protocol"],
                rule["port"],
                rule["cidr"],
            ]
        )
    table.print()


@firewall_rule.command("list", "ls")
def filrewall_rule_list(
    group_id: UUID,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """List rules in group."""
    client = create_client(config, profile)
    response = client.get_firewall_rules(group_id)
    fmt.printer(
        response,
        output_format=output_format,
        func=print_rules,
    )


# ------------------------------------------------------------- #
# $ twc firewall rule add                                       #
# ------------------------------------------------------------- #


def port_proto_callback(values) -> List[Tuple[Optional[str], str]]:
    new_values = []
    for value in values:
        if not re.match(r"((^\d+(-\d+)?/)?(tcp|udp)$)|(^icmp$)", value, re.I):
            sys.exit(
                f"Error: Malformed argument: '{value}': "
                "correct patterns: '22/TCP', '2000-3000/UDP', 'ICMP', etc."
            )
        if re.match(r"^icmp$", value, re.I):
            new_values.append((None, "icmp"))
        else:
            ports, proto = value.split("/")
            new_values.append((ports, proto.lower()))
    return new_values


def validate_cidr_callback(value):
    if value is not None:
        try:
            assert ip_network(value)
        except ValueError as err:
            sys.exit(f"Error: Invalid CIDR: {err}")
    return value


@firewall_rule.command("add")
def firewall_allow(
    ports: List[str] = typer.Argument(
        ...,
        metavar="[PORT[-PORT]/]PROTO...",
        callback=port_proto_callback,
        help="List of port/protocol pairs e.g. 22/TCP, 2000-3000/UDP, ICMP",
    ),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    group: Optional[UUID] = typer.Option(
        None,
        "--group",
        "-g",
        help="Firewall rules group UUID.",
    ),
    make_group: Optional[bool] = typer.Option(
        None,
        "--make-group",
        "-G",
        help="Add rules in new rules group.",
    ),
    group_name: Optional[str] = typer.Option(
        None,
        help="Rules group name, can be used with '--make-group'",
    ),
    direction_: bool = typer.Option(
        True, "--ingress/--egress", help="Traffic direction."
    ),
    cidr: Optional[str] = typer.Option(
        "0.0.0.0/0",
        metavar="IP_NETWORK",
        callback=validate_cidr_callback,
        help="IPv4 or IPv6 CIDR.",
    ),
):
    """Add new firewall rule."""
    client = create_client(config, profile)
    if make_group is not None and group is not None:
        raise UsageError(
            "'--group' and '--make-group' options is mutually exclusive."
        )
    if make_group is None and group is None:
        raise UsageError(
            "One of options is required: ['--group', '--make-group']"
        )
    if make_group:
        if group_name is None:
            group_name = "Firewall Group " + datetime.now().strftime(
                "%Y.%m.%d-%H:%M:%S"
            )
        group_resp = client.create_firewall_group(group_name)
        group = group_resp.json()["group"]["id"]
        logging.debug("New firewall rules group: %s", group)
        fmt.printer(
            group_resp,
            output_format=output_format,
            func=lambda x: print("Created rules group:", group),
        )
    for port in ports:
        if direction_ is True:
            direction = "ingress"
        else:
            direction = "egress"
        response = client.create_firewall_rule(
            group,
            direction=direction,
            port=port[0],  # :str port or port range
            proto=port[1],  # :str protocol name
            cidr=cidr,
        )
        fmt.printer(
            response,
            output_format=output_format,
            func=lambda response: print(response.json()["rule"]["id"]),
        )


# ------------------------------------------------------------- #
# $ twc firewall rule remove                                    #
# ------------------------------------------------------------- #


def get_group_id_by_rule(client: TimewebCloud, rule_id: UUID) -> str:
    groups = client.get_firewall_groups().json()["groups"]
    for group in groups:
        rules = client.get_firewall_rules(group["id"]).json()["rules"]
        for rule in rules:
            if rule_id == rule["id"]:
                return group["id"]
    sys.exit(f"Error: Rule '{rule_id}' not found")


@firewall_rule.command("remove", "rm")
def firewall_rule_remove(
    rule_id: UUID,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
):
    """Remove firewall rule."""
    client = create_client(config, profile)
    group_id = get_group_id_by_rule(client, rule_id)
    response = client.delete_firewall_rule(group_id, rule_id)
    if response.status_code == 204:
        print(rule_id)
    else:
        sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc firewall rule update                                    #
# ------------------------------------------------------------- #


@firewall_rule.command("update", "upd")
def filrewa_rule_update(
    rule_id: UUID,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    direction_: Optional[bool] = typer.Option(
        None,
        "--ingress/--egress",
        help="Traffic direction.",
    ),
    cidr: Optional[str] = typer.Option(
        None,
        metavar="IP_NETWORK",
        callback=validate_cidr_callback,
        help="IPv4 or IPv6 CIDR.",
    ),
    port: Optional[str] = typer.Option(
        None,
        metavar="PORT[-PORT]",
        help="Port or ports range e.g. 22, 2000-3000",
    ),
    proto: Optional[FirewallProto] = typer.Option(None, help="Protocol."),
):
    """Change firewall rule."""
    client = create_client(config, profile)
    group_id = get_group_id_by_rule(client, rule_id)
    old_state = client.get_firewall_rule(group_id, rule_id).json()["rule"]
    if direction_ is None:
        direction = old_state["direction"]
    elif direction is True:
        direction = ("ingress",)
    else:
        direction = "egress"
    if proto is None:
        proto = old_state["protocol"]
    if cidr is None:
        cidr = old_state["cidr"]
    payload = {
        "group_id": group_id,
        "rule_id": rule_id,
        "direction": direction,
        "port": port,
        "proto": proto,
        "cidr": cidr,
    }
    response = client.update_firewall_rule(**payload)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["rule"]["id"]),
    )
