"""Manage Kubernetes clusters."""

import re
import sys
from typing import Optional, List
from pathlib import Path

import typer
from requests import Response

from twc import fmt
from twc.typerx import TyperAlias
from twc.api import TimewebCloud
from twc.apiwrap import create_client
from .common import (
    verbose_option,
    config_option,
    profile_option,
    filter_option,
    yes_option,
    output_format_option,
    load_from_config_callback,
)


cluster = TyperAlias(help=__doc__)
cluster_group = TyperAlias(help="Manage worker node groups.")
cluster_node = TyperAlias(help="Manage worker nodes.")
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
        help="Add workers node group.",
    ),
    project_id: Optional[int] = typer.Option(
        None,
        envvar="TWC_PROJECT",
        show_envvar=False,
        callback=load_from_config_callback,
        help="Add cluster to specific project.",
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

    if project_id:
        if not project_id in [
            prj["id"] for prj in client.get_projects().json()["projects"]
        ]:
            sys.exit(f"Wrong project ID: Project '{project_id}' not found.")

    response = client.create_k8s_cluster(
        name=name,
        description=desc,
        k8s_version=k8s_version,
        network_driver=network_driver,
        ingress=ingress,
        worker_groups=worker_groups,
        preset_id=master_preset_id,
    )

    # Add created cluster to project if set
    if project_id:
        client.add_cluster_to_project(
            response.json()["cluster"]["id"],
            project_id,
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
    """Download KubeConfig."""
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


# ------------------------------------------------------------- #
# $ twc cluster group add                                       #
# ------------------------------------------------------------- #


@cluster_group.command("add")
def cluster_group_add(
    cluster_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    name: str = typer.Option(..., help="Node group display name."),
    preset_id: int = typer.Option(..., help="Nodes configuration preset."),
    nodes: int = typer.Option(1, help="Number of nodes in group."),
):
    """Add new node group."""
    client = create_client(config, profile)
    response = client.create_k8s_node_group(
        cluster_id,
        name=name,
        preset_id=preset_id,
        node_count=nodes,
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["node_group"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc cluster group remove                                    #
# ------------------------------------------------------------- #


def get_cluster_id_by_group(client: TimewebCloud, group_id: int) -> int:
    clusters = client.get_k8s_clusters().json()["clusters"]
    for _cluster in clusters:
        groups = client.get_k8s_node_groups(_cluster["id"]).json()[
            "node_groups"
        ]
        for group in groups:
            if group_id == group["id"]:
                return _cluster["id"]
    sys.exit(f"Error: Node group '{group_id}' not found.")


@cluster_group.command("remove", "rm")
def cluster_group_remove(
    group_ids: List[int] = typer.Argument(..., metavar="GROUP_ID..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
):
    """Remove node group."""
    if not yes:
        typer.confirm("This action cannot be undone. Continue?", abort=True)
    client = create_client(config, profile)
    for group_id in group_ids:
        cluster_id = get_cluster_id_by_group(client, group_id)
        response = client.delete_k8s_node_group(cluster_id, group_id)
        if response.status_code == 204:
            print(group_id)
        else:
            sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc cluster group scale-up                                  #
# ------------------------------------------------------------- #


@cluster_group.command("scale-up")
def cluster_group_scaleup(
    group_id: int,
    count: Optional[int] = typer.Argument(1, help="Nodes count."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """Add worker nodes to group."""
    client = create_client(config, profile)
    cluster_id = get_cluster_id_by_group(client, group_id)
    response = client.add_k8s_nodes_to_group(cluster_id, group_id, count)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(
            f"Nodes in group {group_id}:", response.json()["meta"]["total"]
        ),
    )


# ------------------------------------------------------------- #
# $ twc cluster group scale-down                                #
# ------------------------------------------------------------- #


@cluster_group.command("scale-down")
def cluster_group_scaledown(
    group_id: int,
    count: Optional[int] = typer.Argument(1, help="Nodes count."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """Remove worker nodes from group."""
    client = create_client(config, profile)
    cluster_id = get_cluster_id_by_group(client, group_id)
    response = client.delete_k8s_nodes_from_group(cluster_id, group_id, count)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(
            f"Nodes in group {group_id}:", response.json()["meta"]["total"]
        ),
    )


# ------------------------------------------------------------- #
# $ twc cluster node list                                       #
# ------------------------------------------------------------- #


def print_nodes(response: Response):
    nodes = response.json()["nodes"]
    table = fmt.Table()
    table.header(
        [
            "ID",
            "GROUP",
            "TYPE",
            "STATUS",
            "CREATED",
            "CPU/RAM/DISK",
        ]
    )
    for node in nodes:
        table.row(
            [
                node["id"],
                node["group_id"],
                node["type"],
                node["status"],
                node["created_at"],
                str(node["cpu"])
                + "/"
                + str(round(node["ram"] / 1024))
                + "G/"
                + str(node["disk"])
                + "G",
            ]
        )
    table.print()


@cluster_node.command("list", "ls")
def cluster_node_list(
    cluster_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """List cluster node groups."""
    client = create_client(config, profile)
    response = client.get_k8s_nodes(cluster_id)
    fmt.printer(
        response,
        output_format=output_format,
        func=print_nodes,
    )


# ------------------------------------------------------------- #
# $ twc cluster node remove                                     #
# ------------------------------------------------------------- #


@cluster_node.command("remove", "rm")
def cluster_node_remove(
    cluster_id: int,
    node_ids: List[int] = typer.Argument(..., metavar="NODE_ID..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
):
    """Remove nodes from cluster."""
    if not yes:
        typer.confirm("This action cannot be undone. Continue?", abort=True)
    client = create_client(config, profile)
    for node_id in node_ids:
        response = client.delete_k8s_node(cluster_id, node_id)
        if response.status_code == 204:
            print(node_id)
        else:
            sys.exit(fmt.printer(response))
