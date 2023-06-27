"""Manage Kubernetes clusters."""

import re
import sys
from typing import Optional, List
from pathlib import Path

import typer
from requests import Response

from twc import fmt
from twc.typerx import TyperAlias
from twc.apiwrap import create_client
from .common import (
    verbose_option,
    config_option,
    profile_option,
    filter_option,
    yes_option,
    output_format_option,
)


cluster = TyperAlias(help=__doc__)
cluster_group = TyperAlias(help="Manage cluster node groups.")
cluster_node = TyperAlias(help="Manage cluster nodes.")
cluster.add_typer(cluster_group, name="group", aliases=["groups"])
cluster.add_typer(cluster_node, name="node", aliases=["nodes"])


# ------------------------------------------------------------- #
# $ twc cluster list                                            #
# ------------------------------------------------------------- #


def print_clusters(response: Response, filters: Optional[str]):
    """Print table with K8s clusters list."""
    clusters = response.json()["clusters"]
    if filters:
        clusters = fmt.filter_list(clusters, filters)
    table = fmt.Table()
    table.header(
        [
            "ID",
            "NAME",
            "STATUS",
            "VERSION",
        ]
    )
    for cl in clusters:
        table.row(
            [
                cl["id"],
                cl["name"],
                cl["status"],
                cl["k8s_version"],
            ]
        )
    table.print()


@cluster.command("list", "ls")
def cluster_list(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
):
    """List Kubernetes clusters."""
    client = create_client(config, profile)
    response = client.get_k8s_clusters()
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_clusters,
    )


# ------------------------------------------------------------- #
# $ twc cluster remove                                          #
# ------------------------------------------------------------- #


@cluster.command("remove", "rm")
def cluster_remove(
    cluster_ids: List[int] = typer.Argument(..., metavar="CLUSTER_ID..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
):
    """Remove Kubernetes cluster."""
    if not yes:
        typer.confirm("This action cannot be undone. Continue?", abort=True)
    client = create_client(config, profile)
    for cluster_id in cluster_ids:
        response = client.delete_k8s_cluster(cluster_id)
        if response.status_code == 200:
            del_hash = response.json()["cluster_delete"]["hash"]
            del_code = typer.prompt("Please enter confirmation code", type=int)
            response = client.delete_k8s_cluster(
                cluster_id, delete_hash=del_hash, code=del_code
            )
        if response.status_code == 204:
            print(cluster_id)
        else:
            sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc cluster create                                          #
# ------------------------------------------------------------- #


@cluster.command("create")
def cluster_create(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    name: str = typer.Option(..., help="Cluster's display name."),
    desc: str = typer.Option(None, help="Cluster description."),
    k8s_version: Optional[str] = typer.Option(
        None,
        help="Kubernetes version."
        " See 'twc k8s list-k8s-versions'. Latest by deafult.",
    ),
    master_preset_id: Optional[int] = typer.Option(
        None,
        help="Master node configuration preset. Minimal by default.",
    ),
    network_driver: Optional[str] = typer.Option(
        "canal",
        help="Network driver.",
    ),
    ingress: bool = typer.Option(True, help="Enable Nginx ingress."),
    worker_groups: List[str] = typer.Option(
        None,
        "--add-worker-group",
        metavar="NAME,PRESET_ID,NODE_COUNT",
        help="Add worker nodes group.",
    ),
):
    """Create Kubernetes cluster."""
    client = create_client(config, profile)

    if worker_groups:
        actual_worker_groups = []
        pattern = (
            "^((name=)?[a-z0-9_-]+),((preset=)?[0-9]+),((count=)?[0-9]+)$"
        )
        for wg in worker_groups:
            if not re.match(pattern, wg, re.I):
                sys.exit(
                    "Error: Wrong worker group pattern.\n"
                    "Pattern must include comma sepatated sections:\n"
                    " - name (group name, only a-zA-Z0-9-_)\n"
                    " - preset (nodes preset_id, number)\n"
                    " - count (number of workers)\n"
                    "Correct pattern: "
                    "'name=my_group1,preset=399,count=2' or 'my_group1,399,2'"
                )
            _name, _preset, _count = wg.split(",")
            worker_group = {
                "name": _name.replace("name=", ""),
                "preset_id": int(_preset.replace("preset=", "")),
                "node_count": int(_count.replace("count=", "")),
            }
            actual_worker_groups.append(worker_group)
        worker_groups = actual_worker_groups

    # Select latest K8s version
    if not k8s_version:
        versions = client.get_k8s_versions().json()["k8s_versions"]
        versions.sort(
            key=lambda s: [int(u.replace("v", "")) for u in s.split(".")],
            reverse=True,
        )
        k8s_version = versions[0]  # apply latest version

    # Select minimal master node preset excluding promo preset.
    # Promo preset has 'limit=1'.
    if not master_preset_id:
        presets = client.get_k8s_presets().json()["k8s_presets"]
        master_presets = [
            p for p in presets if p["type"] == "master" and p["limit"] is None
        ]
        master_presets_ram = [p["ram"] for p in master_presets]
        for preset in master_presets:
            if preset["ram"] == min(master_presets_ram):
                master_preset_id = preset["id"]

    response = client.create_k8s_cluster(
        name=name,
        description=desc,
        k8s_version=k8s_version,
        network_driver=network_driver,
        ingress=ingress,
        worker_groups=worker_groups,
        preset_id=master_preset_id,
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["cluster"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc cluster kubeconfig                                      #
# ------------------------------------------------------------- #


@cluster.command("kubeconfig", "kubecfg", "cfg")
def cluster_kubeconfig(
    cluster_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    save: Optional[Path] = typer.Option(
        None,
        help="Path to file. NOTE: Existing file will be overwitten.",
    ),
):
    """Download kubeconfig.yaml."""
    client = create_client(config, profile)
    file_content = client.get_k8s_cluster_kubeconfig(cluster_id).text
    if save:
        with open(save, "w", encoding="utf-8") as kubeconfig:
            kubeconfig.write(file_content)
    else:
        fmt.print_colored(file_content, lang="yaml")


# ------------------------------------------------------------- #
# $ twc cluster list-k8s-versions                               #
# ------------------------------------------------------------- #


@cluster.command("list-k8s-versions", "lv")
def cluster_list_versions(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """List available Kubernetes versions."""
    client = create_client(config, profile)
    response = client.get_k8s_versions()
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: [
            print(v) for v in response.json()["k8s_versions"]
        ],
    )


# ------------------------------------------------------------- #
# $ twc cluster list-network-drivers                            #
# ------------------------------------------------------------- #


@cluster.command("list-network-drivers")
def cluster_list_network_drivers(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """List available Kubernetes network drivers."""
    client = create_client(config, profile)
    response = client.get_k8s_network_drivers()
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: [
            print(v) for v in response.json()["network_drivers"]
        ],
    )


# ------------------------------------------------------------- #
# $ twc cluster list-presets                                    #
# ------------------------------------------------------------- #


def print_presets(response: Response, filters: Optional[str] = None):
    """Print table with K8s nodes presets."""
    presets = response.json()["k8s_presets"]
    if filters:
        presets = fmt.filter_list(presets, filters)
    table = fmt.Table()
    table.header(
        [
            "ID",
            "PRICE",
            "CPU",
            "RAM",
            "DISK",
            "TYPE",
        ]
    )
    for preset in presets:
        table.row(
            [
                preset["id"],
                preset["price"],
                preset["cpu"],
                str(round(preset["ram"] / 1024)) + "G",
                str(preset["disk"]) + "G",
                preset["type"],
            ]
        )
    table.print()


@cluster.command("list-presets", "lp")
def cluster_list_presets(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
):
    """List nodes configuration presets."""
    client = create_client(config, profile)
    response = client.get_k8s_presets()
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_presets,
    )


# ------------------------------------------------------------- #
# $ twc cluster show                                           #
# ------------------------------------------------------------- #


def print_cluster_info(response: Response):
    info = response.json()["resources"]
    table = fmt.Table()
    table.header(
        [
            "RESOURCE",
            "REQUESTED",
            "ALLOCATABLE",
            "CAPACITY",
            "USED",
        ]
    )
    resources = list(info.keys())
    resources.remove("nodes")
    for r in resources:
        table.row(
            [
                r,
                info[r]["requested"],
                info[r]["allocatable"],
                info[r]["capacity"],
                info[r]["used"],
            ]
        )
    table.print()


@cluster.command("show")
def cluster_show(
    cluster_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """Show cluster resource usage."""
    client = create_client(config, profile)
    response = client.get_k8s_cluster_resources(cluster_id)
    fmt.printer(
        response,
        output_format=output_format,
        func=print_cluster_info,
    )


# ------------------------------------------------------------- #
# $ twc cluster group list                                      #
# ------------------------------------------------------------- #


def print_node_groups(response: Response):
    groups = response.json()["node_groups"]
    table = fmt.Table()
    table.header(
        [
            "ID",
            "NAME",
            "CREATED",
            "PRESET",
            "NODES",
        ]
    )
    for group in groups:
        table.row(
            [
                group["id"],
                group["name"],
                group["created_at"],
                group["preset_id"],
                group["node_count"],
            ]
        )
    table.print()


@cluster_group.command("list", "ls")
def cluster_group_list(
    cluster_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """List cluster node groups."""
    client = create_client(config, profile)
    response = client.get_k8s_node_groups(cluster_id)
    fmt.printer(
        response,
        output_format=output_format,
        func=print_node_groups,
    )
