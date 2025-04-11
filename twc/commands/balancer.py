"""Manage load balancers."""

import re
import sys
from enum import Enum
from typing import Optional, List
from pathlib import Path
from logging import debug
from ipaddress import IPv4Address, IPv4Network

import typer
from requests import Response

from twc import fmt
from twc.typerx import TyperAlias
from twc.apiwrap import create_client
from twc.api import TimewebCloud
from twc.vars import REGION_ZONE_MAP
from twc.api.types import LoadBalancerAlgo, LoadBalancerProto, ServiceRegion
from .common import (
    verbose_option,
    config_option,
    profile_option,
    filter_option,
    yes_option,
    region_option,
    zone_option,
    output_format_option,
    load_from_config_callback,
)


balancer = TyperAlias(help=__doc__)
balancer_backend = TyperAlias(help="Manage load balancer backend servers.")
balancer_rule = TyperAlias(help="Manage load balancer rules.")
balancer.add_typer(balancer_backend, name="backend", aliases=["backends"])
balancer.add_typer(balancer_rule, name="rule", aliases=["rules"])


# ------------------------------------------------------------- #
# $ twc balancer list                                           #
# ------------------------------------------------------------- #


def print_balancers(response: Response, filters: Optional[str]):
    """Print table with balancers list."""
    balancers = response.json()["balancers"]
    if filters:
        balancers = fmt.filter_list(balancers, filters)
    table = fmt.Table()
    table.header(
        [
            "ID",
            "NAME",
            "STATUS",
            "INTERNAL IP",
            "EXTERNAL IP",
        ]
    )
    for lb in balancers:
        table.row(
            [
                lb["id"],
                lb["name"],
                lb["status"],
                lb["local_ip"],
                lb["ip"],
            ]
        )
    table.print()


@balancer.command("list", "ls")
def balancer_list(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
):
    """List load balancers."""
    client = create_client(config, profile)
    response = client.get_load_balancers()
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_balancers,
    )


# ------------------------------------------------------------- #
# $ twc balancer get                                            #
# ------------------------------------------------------------- #


def print_balancer(response: Response):
    """Print table with load balancer info."""
    lb = response.json()["balancer"]
    table = fmt.Table()
    table.header(
        [
            "ID",
            "NAME",
            "STATUS",
            "INTERNAL IP",
            "EXTERNAL IP",
        ]
    )
    table.row(
        [
            lb["id"],
            lb["name"],
            lb["status"],
            lb["local_ip"],
            lb["ip"],
        ]
    )
    table.print()


@balancer.command("get")
def balancer_get(
    balancer_id: int,
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
    """Get load balancer info."""
    client = create_client(config, profile)
    response = client.get_load_balancer(balancer_id)
    if status:
        state = response.json()["balancer"]["status"]
        if state == "started":
            print(state)
            raise typer.Exit()
        sys.exit(state)
    fmt.printer(response, output_format=output_format, func=print_balancer)


# ------------------------------------------------------------- #
# $ twc balancer create                                         #
# ------------------------------------------------------------- #


class CertType(str, Enum):
    """..."""

    CUSTOM = "custom"
    LETS_ENCRYPT = "lets_encrypt"


@balancer.command("create")
def balancer_create(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    name: str = typer.Option(..., help="Load balancer display name."),
    desc: Optional[str] = typer.Option(
        None, help="Load balancer description."
    ),
    preset_id: Optional[int] = typer.Option(
        None, help="Load balancer preset ID."
    ),
    replicas: int = typer.Option(
        1,
        min=1,
        max=2,
        help="Load balancer replica count. Ignored if --preset-id set.",
    ),
    algo: LoadBalancerAlgo = typer.Option(
        LoadBalancerAlgo.ROUND_ROBIN.value,
        help="Balancer algorythm.",
    ),
    port: int = typer.Option(80, help="Load balancer listen port."),
    path: str = typer.Option("/", help="URL path."),
    proto: LoadBalancerProto = typer.Option(
        LoadBalancerProto.HTTP.value, help="Health check protocol."
    ),
    inter: int = typer.Option(10, help="Health checks interval in seconds."),
    timeout: int = typer.Option(5, help="Health check timeout in seconds."),
    rise: int = typer.Option(
        3,
        help="Number of successful health checks to consider backend as operational.",
    ),
    fall: int = typer.Option(
        2,
        help="Number of unsuccessfull health checks to consider backend as dead.",
    ),
    sticky: bool = typer.Option(False, help="Stick on client IP."),
    proxy_protocol: bool = typer.Option(False),
    force_https: bool = typer.Option(False),
    backend_keepalive: bool = typer.Option(False),
    max_connections: Optional[int] = typer.Option(
        None, help="Backend server's maximum number of concurrent connections."
    ),
    connect_timeout: Optional[int] = typer.Option(
        None,
        help="Maximum time to wait for a connection attempt to a backend server to succeed.",
    ),
    client_timeout: Optional[int] = typer.Option(
        None, help="Maximum inactivity time on the client side."
    ),
    server_timeout: Optional[int] = typer.Option(
        None, help="Maximum time for pending data staying into output buffer."
    ),
    http_timeout: Optional[int] = typer.Option(
        None, help="Maximum allowed time to wait for a complete HTTP request."
    ),
    project_id: Optional[int] = typer.Option(
        None,
        envvar="TWC_PROJECT",
        show_envvar=False,
        callback=load_from_config_callback,
        help="Add load balancer to specific project.",
    ),
    network: Optional[str] = typer.Option(
        None, hidden=True, help="Private network ID."
    ),
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
    region: Optional[str] = region_option,
    availability_zone: Optional[str] = zone_option,
    cert_type: Optional[CertType] = typer.Option(
        None,
        help="SSL certificate type. Falls to 'custom' "
        "if --cert-data and --cert-key set.",
    ),
    cert_domain: Optional[str] = typer.Option(
        None,
        help="Domain name for which the certificate was issued. "
        "Note: domain name A-record will set to load balancer's public IP.",
    ),
    cert_data: Optional[typer.FileText] = typer.Option(
        None, help="Fullchain certificate file."
    ),
    cert_key: Optional[typer.FileText] = typer.Option(
        None, help="Certificate key file."
    ),
):
    """Create load balancer."""
    client = create_client(config, profile)

    payload = {
        "name": name,
        "comment": desc,
        "preset_id": preset_id,
        "algo": algo,
        "proto": proto,
        "port": port,
        "path": path,
        "inter": inter,
        "timeout": timeout,
        "fall": fall,
        "rise": rise,
        "sticky": sticky,
        "proxy_protocol": proxy_protocol,
        "force_https": force_https,
        "backend_keepalive": backend_keepalive,
        "network": {},
        "project_id": project_id,
        "certificates": {},
        "max_connections": max_connections,
        "connect_timeout": connect_timeout,
        "client_timeout": client_timeout,
        "server_timeout": server_timeout,
        "http_timeout": http_timeout,
    }

    if cert_type == CertType.CUSTOM:
        if not cert_data or not cert_key:
            sys.exit(
                "Error: --cert-data and --cert-key is required if --cert-type is 'custom'"
            )
    elif cert_type == CertType.LETS_ENCRYPT:
        if cert_data or cert_key:
            sys.exit(
                "Error: --cert-data and --cert-key is not allowed with --cert-type 'lets_encrypt'"
            )
    if not cert_type:
        if cert_data and not cert_key:
            sys.exit("Error: --cert-key is required.")
        if cert_key and not cert_data:
            sys.exit("Error: --cert-data is required.")
        if cert_data and cert_key:
            cert_type = CertType.CUSTOM
    if cert_type and not cert_domain:
        sys.exit(
            "Error: --cert-domain is required if --cert-type and/or --cert-data, --cert-key is set."
        )
    if cert_type:
        payload["certificates"] = {
            "type": cert_type.value,
            "fqdn": cert_domain,
            **({"cert_data": cert_data.read()} if cert_data else {}),
            **({"key_data": cert_key.read()} if cert_key else {}),
        }

    if not preset_id:
        for preset in client.get_load_balancer_presets().json()[
            "balancers_presets"
        ]:
            if (
                preset["replica_count"] == replicas
                and preset["location"] == region
            ):
                preset_id = preset["id"]
        if not preset_id:
            sys.exit(f"Error: Cannot set {replicas} load balancer replicas.")

    if network:
        print(
            "Option --network is deprecated and will be removed soon, "
            "use --network-id instead",
            file=sys.stderr,
        )
        network_id = network

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
            if not preset_id and not availability_zone and not region:
                sys.exit(
                    "Error: Unable to get IPv4 address, at least one of "
                    "[--preset-id, --region, --availability-zone] "
                    "must be set to determine correct location."
                )
            if region:
                zone = REGION_ZONE_MAP[region]
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

    # Create LB
    response = client.create_load_balancer(**payload)

    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["balancer"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc balancer set                                            #
# ------------------------------------------------------------- #


@balancer.command("set")
def balancer_set(
    balancer_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    name: Optional[str] = typer.Option(
        None, help="Load balancer display name."
    ),
    replicas: Optional[int] = typer.Option(
        None,
        min=1,
        max=2,
        help="Load balancer replica count.",
    ),
    algo: LoadBalancerAlgo = typer.Option(None, help="Balancer algorythm."),
    port: Optional[int] = typer.Option(
        None, help="Load balancer listen port."
    ),
    path: Optional[str] = typer.Option(None, help="URL path."),
    proto: Optional[LoadBalancerProto] = typer.Option(
        None, help="Health check protocol."
    ),
    inter: Optional[int] = typer.Option(
        None, help="Health checks interval in seconds."
    ),
    timeout: Optional[int] = typer.Option(
        None, help="Health check timeout in seconds."
    ),
    rise: Optional[int] = typer.Option(
        None,
        help="Number of successful health checks to consider backend as operational.",
    ),
    fall: Optional[int] = typer.Option(
        None,
        help="Number of unsuccessfull health checks to consider backend as dead.",
    ),
    sticky: Optional[bool] = typer.Option(None, help="Stick on client IP."),
    proxy_protocol: Optional[bool] = typer.Option(None),
    force_https: Optional[bool] = typer.Option(None),
    backend_keepalive: Optional[bool] = typer.Option(None),
    max_connections: Optional[int] = typer.Option(
        None, help="Backend server's maximum number of concurrent connections."
    ),
    connect_timeout: Optional[int] = typer.Option(
        None,
        help="Maximum time to wait for a connection attempt to a backend server to succeed.",
    ),
    client_timeout: Optional[int] = typer.Option(
        None, help="Maximum inactivity time on the client side."
    ),
    server_timeout: Optional[int] = typer.Option(
        None, help="Maximum time for pending data staying into output buffer."
    ),
    http_timeout: Optional[int] = typer.Option(
        None, help="Maximum allowed time to wait for a complete HTTP request."
    ),
):
    """Change load balancer parameters."""
    client = create_client(config, profile)

    preset_id = None
    if replicas is not None:
        for preset in client.get_load_balancer_presets().json()[
            "balancers_presets"
        ]:
            if preset["replica_count"] == replicas:
                preset_id = preset["id"]
        if not preset_id:
            sys.exit(f"Error: Cannot set {replicas} load balancer replicas.")

    response = client.update_load_balancer(
        balancer_id=balancer_id,
        name=name,
        preset_id=preset_id,
        algo=algo,
        proto=proto,
        port=port,
        path=path,
        inter=inter,
        timeout=timeout,
        fall=fall,
        rise=rise,
        sticky=sticky,
        proxy_protocol=proxy_protocol,
        force_https=force_https,
        backend_keepalive=backend_keepalive,
        max_connections=max_connections,
        connect_timeout=connect_timeout,
        client_timeout=client_timeout,
        server_timeout=server_timeout,
        http_timeout=http_timeout,
    )

    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["balancer"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc balancer remove                                         #
# ------------------------------------------------------------- #


@balancer.command("remove", "rm")
def balancer_remove(
    balancer_ids: List[int] = typer.Argument(..., metavar="BALANCER_ID..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
):
    """Remove load balancer."""
    if not yes:
        typer.confirm("This action cannot be undone. Continue?", abort=True)
    client = create_client(config, profile)
    for balancer_id in balancer_ids:
        response = client.delete_load_balancer(balancer_id)
        if response.status_code == 200:
            del_hash = response.json()["balancer_delete"]["hash"]
            del_code = typer.prompt("Please enter confirmation code", type=int)
            response = client.delete_load_balancer(
                balancer_id, delete_hash=del_hash, code=del_code
            )
        if response.status_code == 204:
            print(balancer_id)
        else:
            sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc balancer backed list                                    #
# ------------------------------------------------------------- #


@balancer_backend.command("list", "ls")
def blancer_backend_list(
    balancer_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """List load balancer backends."""
    client = create_client(config, profile)
    response = client.get_load_balancer_ips(balancer_id)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print("\n".join(response.json()["ips"])),
    )


# ------------------------------------------------------------- #
# $ twc balancer list-presets                                     #
# ------------------------------------------------------------- #


def _print_presets(response: Response, filters: Optional[str] = None):
    presets = response.json()["balancers_presets"]
    if filters:
        presets = fmt.filter_list(presets, filters)
    table = fmt.Table()
    table.header(
        [
            "ID",
            "REGION",
            "PRICE",
            "REPLICAS",
            "BANDW",
            "RPS",
        ]
    )
    for preset in presets:
        table.row(
            [
                preset["id"],
                preset["location"],
                preset["price"],
                preset["replica_count"],
                preset["bandwidth"],
                preset["request_per_second"],
            ]
        )
    table.print()


@balancer.command("list-presets", "lp")
def balancer_list_presets(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
    region: Optional[ServiceRegion] = typer.Option(
        None, help="Use region (location)."
    ),
):
    """List configuration presets."""
    if region:
        filters = f"{filters},location:{region}"
    client = create_client(config, profile)
    response = client.get_load_balancer_presets()
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=_print_presets,
    )


# ------------------------------------------------------------- #
# $ twc balancer backend add                                    #
# ------------------------------------------------------------- #


@balancer_backend.command("add")
def blancer_backend_add(
    balancer_id: int = typer.Argument(...),
    backends: List[str] = typer.Argument(..., metavar="BACKEND_IP..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
):
    """Add new backend servers to balancer."""
    client = create_client(config, profile)
    response = client.add_ips_to_load_balancer(balancer_id, backends)
    if response.status_code == 204:
        print("\n".join(backends))
    else:
        sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc balancer backed remove                                  #
# ------------------------------------------------------------- #


@balancer_backend.command("remove", "rm")
def blancer_backend_remove(
    balancer_id: int = typer.Argument(...),
    backends: List[str] = typer.Argument(..., metavar="BACKEND..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
):
    """Remove load balancer backends."""
    if not yes:
        typer.confirm("This action cannot be undone. Continue?", abort=True)
    client = create_client(config, profile)
    response = client.delete_ips_from_load_balancer(balancer_id, backends)
    if response.status_code == 204:
        print("\n".join(backends))
    else:
        sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc balancer rule list                                      #
# ------------------------------------------------------------- #


def print_balancer_rules(response: Response):
    """Print balancers list."""
    rules = response.json()["rules"]
    table = fmt.Table()
    table.header(
        [
            "ID",
            "FRONTEND PORT",
            "FRONTEND PROTO",
            "BACKEND PORT",
            "BACKEND PROTO",
        ]
    )
    for rule in rules:
        table.row(
            [
                rule["id"],
                rule["balancer_port"],
                rule["balancer_proto"],
                rule["server_port"],
                rule["server_proto"],
            ]
        )
    table.print()


@balancer_rule.command("list", "ls")
def balancer_rule_list(
    balancer_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """List load balancer rules."""
    client = create_client(config, profile)
    response = client.get_load_balancer_rules(balancer_id)
    fmt.printer(
        response,
        output_format=output_format,
        func=print_balancer_rules,
    )


# ------------------------------------------------------------- #
# $ twc balancer rule add                                       #
# ------------------------------------------------------------- #


def validate_balancer_port_proto_callback(value):
    """Typer callback for PORT/PROTO validation."""
    if value:
        if not re.match(r"^\d+\/(http|http2|https|tcp)$", value, re.I):
            sys.exit(
                f"Error: Malformed argument: '{value}': "
                "Correct patterns: '443/HTTPS', '2000/TCP', etc.\n"
                "Available protocols: "
                f"{', '.join([lb.value for lb in LoadBalancerProto])}"
            )
        port, proto = value.split("/")
        port = int(port)
        return port, proto
    return value


@balancer_rule.command("add")
def balancer_rule_add(
    balancer_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    frontend: str = typer.Option(
        ...,
        callback=validate_balancer_port_proto_callback,
        metavar="PORT/PROTO",
        help="Frontend port and protocol.",
    ),
    backend: str = typer.Option(
        ...,
        callback=validate_balancer_port_proto_callback,
        metavar="PORT/PROTO",
        help="Backend port and protocol.",
    ),
):
    """Add load balancer rule."""
    client = create_client(config, profile)

    f_port, f_proto = frontend
    b_port, b_proto = backend

    response = client.create_load_balancer_rule(
        balancer_id,
        balancer_port=f_port,
        balancer_proto=f_proto,
        server_port=b_port,
        server_proto=b_proto,
    )

    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["rule"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc balancer rule update                                    #
# ------------------------------------------------------------- #


def get_balancer_id_by_rule(client: TimewebCloud, rule_id: int) -> int:
    """Return load balancer ID by balancer rule ID."""
    balancers = client.get_load_balancers().json()["balancers"]
    for lb in balancers:
        rules = client.get_load_balancer_rules(lb["id"]).json()["rules"]
        for rule in rules:
            debug(f"{rule['id']} from {lb['id']} compare with {rule_id}")
            if rule["id"] == rule_id:
                return lb["id"]
    sys.exit(f"Error: Rule '{rule_id}' not found.")


@balancer_rule.command("update", "upd")
def balancer_rule_update(
    rule_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    frontend: Optional[str] = typer.Option(
        None,
        callback=validate_balancer_port_proto_callback,
        metavar="PORT/PROTO",
        help="Frontend port and protocol.",
    ),
    backend: Optional[str] = typer.Option(
        None,
        callback=validate_balancer_port_proto_callback,
        metavar="PORT/PROTO",
        help="Backend port and protocol.",
    ),
):
    """Update load balancer rule."""
    client = create_client(config, profile)

    f_port = f_proto = None
    b_port = b_proto = None

    balancer_id = get_balancer_id_by_rule(client, rule_id)
    old_rules = client.get_load_balancer_rules(balancer_id).json()["rules"]
    for old_rule in old_rules:
        if old_rule["id"] == rule_id:
            f_port = old_rule["balancer_port"]
            f_proto = old_rule["balancer_proto"]
            b_port = old_rule["server_port"]
            b_proto = old_rule["server_proto"]

    if frontend:
        f_port, f_proto = frontend
    if backend:
        b_port, b_proto = backend

    response = client.update_load_balancer_rule(
        balancer_id,
        rule_id,
        balancer_port=f_port,
        balancer_proto=f_proto,
        server_port=b_port,
        server_proto=b_proto,
    )

    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["rule"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc balancer rule remove                                    #
# ------------------------------------------------------------- #


@balancer_rule.command("remove", "rm")
def balancer_rule_remove(
    rule_ids: List[int] = typer.Argument(..., metavar="RULE_ID..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
):
    """Remove load balancer rule."""
    if not yes:
        typer.confirm("This action cannot be undone. Continue?", abort=True)
    client = create_client(config, profile)
    for rule_id in rule_ids:
        balancer_id = get_balancer_id_by_rule(client, rule_id)
        response = client.delete_load_balancer_rule(balancer_id, rule_id)
        if response.status_code == 204:
            print(rule_id)
        else:
            sys.exit(fmt.printer(response))
