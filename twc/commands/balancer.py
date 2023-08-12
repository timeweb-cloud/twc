"""Manage load balancers."""

import re
import sys
from typing import Optional, List
from pathlib import Path
from logging import debug

import typer
from requests import Response

from twc import fmt
from twc.typerx import TyperAlias
from twc.apiwrap import create_client
from twc.api import TimewebCloud
from twc.api.types import LoadBalancerAlgo, LoadBalancerProto
from .common import (
    verbose_option,
    config_option,
    profile_option,
    filter_option,
    yes_option,
    output_format_option,
    load_from_config_callback,
)


balancer = TyperAlias(help=__doc__)
balancer_backend = TyperAlias(help="Manage load balancer backends.")
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


@balancer.command("create")
def balancer_create(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    name: str = typer.Option(..., help="Load balancer display name."),
    replicas: int = typer.Option(
        1,
        min=1,
        max=2,
        help="Load balancer replica count.",
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
    project_id: Optional[int] = typer.Option(
        None,
        envvar="TWC_PROJECT",
        show_envvar=False,
        callback=load_from_config_callback,
        help="Add load balancer to specific project.",
    ),
    network: Optional[str] = typer.Option(None, help="Private network ID."),
):
    """Create load balancer."""
    client = create_client(config, profile)

    preset_id = None
    for preset in client.get_load_balancer_presets().json()[
        "balancers_presets"
    ]:
        if preset["replica_count"] == replicas:
            preset_id = preset["id"]
    if not preset_id:
        sys.exit(f"Error: Cannot set {replicas} load balancer replicas.")

    if project_id:
        if not project_id in [
            prj["id"] for prj in client.get_projects().json()["projects"]
        ]:
            sys.exit(f"Wrong project ID: Project '{project_id}' not found.")

    payload = {
        "name": name,
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
    }

    if network:
        payload["network"] = {"id": network}

    # Create LB
    response = client.create_load_balancer(**payload)

    # Add created LB to project if set
    if project_id:
        client.add_balancer_to_project(
            response.json()["balancer"]["id"],
            project_id,
        )

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
# $ twc balancer backend add                                    #
# ------------------------------------------------------------- #


@balancer_backend.command("add")
def blancer_backend_add(
    balancer_id: int = typer.Argument(...),
    backends: List[str] = typer.Argument(..., metavar="BACKEND..."),
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
