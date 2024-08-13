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
from twc.api import TimewebCloud, FirewallProto, FirewallPolicy
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
        info = f"Group: {group['name']} ({group['id']}) {group['policy']}"
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
        _ResourceType2.ALL,
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
                    "policy": group["policy"],
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
    table.header(["ID", "POLICY", "NAME"])
    for group in groups:
        table.row(
            [
                group["id"],
                group["policy"],
                group["name"],
            ]
        )
    table.print()


@firewall_group.command("list", "ls")
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
# $ twc firewall group get                                      #
# ------------------------------------------------------------- #


def print_firewall_group(response: Response):
    group = response.json()["group"]
    table = fmt.Table()
    table.header(["ID", "POLICY", "NAME"])
    table.row(
        [
            group["id"],
            group["policy"],
            group["name"],
        ]
    )
    table.print()


@firewall_group.command("get")
def firewall_group_get(
    group_id: UUID,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """Get firewall fules group."""
    client = create_client(config, profile)
    response = client.get_firewall_group(group_id)
    fmt.printer(
        response,
        output_format=output_format,
        func=print_firewall_group,
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
    policy: Optional[FirewallPolicy] = typer.Option(
        FirewallPolicy.DROP,
        case_sensitive=False,
        help="Default firewall policy",
    ),
):
    """Create new group of firewall rules."""
    client = create_client(config, profile)
    response = client.create_firewall_group(
        name=name,
        description=desc,
        policy=policy,
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
# $ twc firewall group dump                                     #
# ------------------------------------------------------------- #


@firewall_group.command("dump")
def firewall_group_dump(
    group_id: UUID,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
):
    """Dump firewall rules."""
    client = create_client(config, profile)
    group = client.get_firewall_group(group_id).json()["group"]
    rules = client.get_firewall_rules(group_id, limit=1000).json()["rules"]
    dump = {"group": group, "rules": rules}
    fmt.print_colored(json.dumps(dump), lang="json")


# ------------------------------------------------------------- #
# $ twc firewall group restore                                  #
# ------------------------------------------------------------- #


def _get_rules_diff(
    rules_local: List[dict], rules_remote: List[dict]
) -> Tuple[List[dict], List[dict]]:
    loc = [rule.copy() for rule in rules_local]
    rem = [rule.copy() for rule in rules_remote]

    for l in loc:
        del l["id"]
        del l["group_id"]
    for r in rem:
        del r["id"]
        del r["group_id"]

    # Rules from rules_local that not present in rules_remote
    to_create = []
    for idx, rule in enumerate(loc):
        if rule not in rem:
            to_create.append(rules_local[idx])

    # Rules from rules_remote that not present in rules_local
    to_delete = []
    for idx, rule in enumerate(rem):
        if rule not in loc:
            to_delete.append(rules_remote[idx])

    return to_create, to_delete


@firewall_group.command("restore")
def firewall_group_restore(
    group_id: UUID,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    dump_file: Optional[typer.FileText] = typer.Option(
        None, "-f", "--file", help="Firewall rules dump in JSON format."
    ),
    rules_only: Optional[bool] = typer.Option(
        False,
        "--rules-only",
        help="Do not restore group name and description.",
    ),
    dry_run: Optional[bool] = typer.Option(
        False, "--dry-run", help="Does not make any changes."
    ),
):
    """Restore firewall rules group from dump file."""
    try:
        dump = json.load(dump_file)
    except json.JSONDecodeError as e:
        sys.exit(f"Error: Cannot load dump file: {dump_file.name}: {e}")

    client = create_client(config, profile)
    group = client.get_firewall_group(group_id).json()["group"]
    rules = client.get_firewall_rules(group_id, limit=1000).json()["rules"]
    if group["policy"].lower() != dump["group"]["policy"].lower():
        sys.exit(
            f"Error: Cannot restore rules to group with {group['policy']} policy. "
            "Create new rules group instead."
        )

    # Make list of rules to be created, updated or deleted
    # fmt: off
    rules_to_add, rules_to_del = _get_rules_diff(dump['rules'], rules)
    rules_to_upd = [r for r in rules_to_add if r['id'] in [r['id'] for r in rules]]
    rules_to_add = [r for r in rules_to_add if r not in rules_to_upd]
    rules_to_del = [r for r in rules_to_del if r['id'] not in [r['id'] for r in rules_to_upd]]
    # fmt: on

    if rules_to_add == rules_to_upd == rules_to_del == []:
        sys.exit("Nothing to do")

    if dry_run:
        fstring = "{sign} {id:<37} {direction:<8} {portproto:<18} {cidr}"
        rules_lists = [
            (rules_to_add, "Following new rules will be created:", "+"),
            (rules_to_upd, "Following rules will be updated:", "+"),
            (rules_to_del, "Following rules will be deleted:", "-"),
        ]
        for rules_list in rules_lists:
            if rules_list[0]:
                print(rules_list[1])
                for rule in rules_list[0]:
                    rule_id = rule["id"]
                    if rules_list == rules_lists[0]:
                        rule_id = "known-after-create"
                    print(
                        " "
                        + fstring.format(
                            sign=rules_list[2],
                            id=rule_id,
                            direction=rule["direction"],
                            portproto=f"{rule['port']}/{rule['protocol']}",
                            cidr=rule["cidr"],
                        )
                    )
        return

    if rules_only is False and dry_run is False:
        client.update_firewall_group(
            group_id,
            name=dump["group"]["name"],
            description=dump["group"]["description"],
        )

    for rule in rules_to_add:
        del rule["id"]
        del rule["group_id"]
        client.create_firewall_rule(group_id, **rule)

    for rule in rules_to_upd:
        client.update_firewall_rule(**rule)

    for rule in rules_to_del:
        client.delete_firewall_rule(group_id, rule["id"])


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
# $ twc firewall rule create                                    #
# ------------------------------------------------------------- #


def port_proto_callback(values) -> List[Tuple[Optional[str], str]]:
    new_values = []
    for value in values:
        if not re.match(r"((^\d+(-\d+)?\/)?((tcp|udp|icmp)6?)$)", value, re.I):
            sys.exit(
                f"Error: Malformed argument: '{value}': "
                "correct patterns: '22/TCP', '2000-3000/UDP', 'ICMP', etc."
            )
        pair = value.split("/")
        if len(pair) == 1:
            ports, proto = None, pair[0]
        else:
            ports, proto = pair
        new_values.append((ports, proto.lower()))
    return new_values


def validate_cidr_callback(value):
    if value is not None:
        try:
            assert ip_network(value)
        except ValueError as err:
            sys.exit(f"Error: Invalid CIDR: {err}")
    return value


@firewall_rule.command("create", "add")
def firewall_rule_create(
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
    group_policy: Optional[FirewallPolicy] = typer.Option(
        FirewallPolicy.DROP,
        case_sensitive=False,
        help="Default firewall policy, can be used with '--make-group'",
    ),
    direction_: bool = typer.Option(
        True, "--ingress/--egress", help="Traffic direction."
    ),
    cidr: Optional[str] = typer.Option(
        None,
        metavar="IP_NETWORK",
        callback=validate_cidr_callback,
        help="IPv4 or IPv6 CIDR. [default: 0.0.0.0/0 or ::/0]",
    ),
):
    """Create new firewall rule."""
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
        group_resp = client.create_firewall_group(
            group_name, policy=group_policy
        )
        group = group_resp.json()["group"]["id"]
        logging.debug("New firewall rules group: %s", group)
        fmt.printer(
            group_resp,
            output_format=output_format,
            func=lambda x: print("Created rules group:", group),
        )
    for rule in ports:
        port, proto = rule
        if not cidr:
            if proto in [
                FirewallProto.TCP6,
                FirewallProto.UDP6,
                FirewallProto.ICMP6,
            ]:
                cidr = "::/0"
            else:
                cidr = "0.0.0.0/0"
        if direction_ is True:
            direction = "ingress"
        else:
            direction = "egress"
        response = client.create_firewall_rule(
            group,
            direction=direction,
            port=port,
            protocol=proto,
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
            if str(rule_id) == rule["id"]:
                return group["id"]
    sys.exit(f"Error: Rule '{rule_id}' not found")


@firewall_rule.command("remove", "rm")
def firewall_rule_remove(
    rules_ids: List[UUID] = typer.Argument(..., metavar="RULE_ID..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
):
    """Remove firewall rule."""
    client = create_client(config, profile)
    for rule_id in rules_ids:
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
    proto: Optional[FirewallProto] = typer.Option(
        None, case_sensitive=False, help="Protocol."
    ),
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
        "protocol": proto,
        "cidr": cidr,
    }
    response = client.update_firewall_rule(**payload)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["rule"]["id"]),
    )
