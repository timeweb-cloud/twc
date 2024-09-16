"""Manage projects."""

import sys
from typing import Optional, List
from pathlib import Path

import typer
from click import UsageError
from requests import Response

from twc import fmt
from twc.typerx import TyperAlias
from twc.apiwrap import create_client
from twc.api import TimewebCloud, ResourceType
from .common import (
    verbose_option,
    config_option,
    profile_option,
    yes_option,
    output_format_option,
)


project = TyperAlias(help=__doc__)
project_resource = TyperAlias(help="Manage Project resources.")
project.add_typer(project_resource, name="resource", aliases=["rsrc"])

# API issue: Inconsistent resource naming
# Some entities have different names in cases.
RESOURCE_TYPES = [
    *[r.value for r in ResourceType],
    "cluster",  # also named 'kubernetes'
    "bucket",  # also named 'storage'
    "dedicated_server",  # also named 'dedicated'
]


# ------------------------------------------------------------- #
# $ twc project list                                            #
# ------------------------------------------------------------- #


def print_projects(response: Response):
    """Print table with projects list."""
    projects = response.json()["projects"]
    table = fmt.Table()
    table.header(
        [
            "ID",
            "NAME",
            "DEFAULT",
            "DESCRIPTION",
        ]
    )
    for prj in projects:
        table.row(
            [
                prj["id"],
                prj["name"],
                prj["is_default"],
                prj["description"],
            ]
        )
    table.print()


@project.command("list", "ls")
def project_list(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """List Projects."""
    client = create_client(config, profile)
    response = client.get_projects()
    fmt.printer(response, output_format=output_format, func=print_projects)


# ------------------------------------------------------------- #
# $ twc project create                                          #
# ------------------------------------------------------------- #


@project.command("create")
def image_create(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    name: Optional[str] = typer.Option(None, help="Project display name."),
    desc: Optional[str] = typer.Option(None, help="Project description."),
    avatar_id: Optional[str] = typer.Option(None, help="Avatar ID."),
):
    """Create project."""
    client = create_client(config, profile)
    response = client.create_project(
        name=name, description=desc, avatar_id=avatar_id
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["project"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc project remove                                          #
# ------------------------------------------------------------- #


@project.command("remove", "rm")
def project_remove(
    project_ids: List[int] = typer.Argument(..., metavar="PROJECT_ID..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
):
    """Remove project. Not affects on project resources."""
    if not yes:
        typer.confirm(
            "Project resources will be moved to default project. Continue?",
            abort=True,
        )
    client = create_client(config, profile)
    for project_id in project_ids:
        response = client.delete_project(project_id)
        if response.status_code == 204:
            print(project_id)
        else:
            sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc project set                                             #
# ------------------------------------------------------------- #


@project.command("set")
def project_set_property(
    project_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    name: Optional[str] = typer.Option(None, help="Project display name."),
    desc: Optional[str] = typer.Option(None, help="Project description."),
    avatar_id: Optional[str] = typer.Option(None, help="Avatar ID."),
):
    """Change proejct name, description and avatar."""
    if not name and not desc and not avatar_id:
        raise UsageError(
            "Nothing to do. Set one of options: "
            "['--name', '--desc', '--avatar-id']"
        )
    client = create_client(config, profile)
    response = client.update_project(
        project_id, name=name, description=desc, avatar_id=avatar_id
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["project"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc project resource list                                   #
# ------------------------------------------------------------- #


def print_resources(response: Response):
    """Print table with project resources list."""
    resources = response.json()
    del resources["response_id"]
    del resources["meta"]
    resource_keys = list(resources.keys())
    table = fmt.Table()
    table.header(
        [
            "ID",
            "NAME",
            "REGION",
            "RESOURCE TYPE",
        ]
    )
    for key in resource_keys:
        if resources[key]:
            for resource in resources[key]:
                table.row(
                    [
                        resource["id"],
                        resource.get("name", resource.get("fqdn")),
                        resource.get("location", "ru-1"),
                        key[:-1],  # this is resource name e.g. 'server'
                    ]
                )
    table.print()


@project_resource.command("list", "ls")
def project_resource_list(
    project_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    resource_type: Optional[str] = typer.Option(
        None, "--type", help="Resource type."
    ),
):
    """List project resources."""
    client = create_client(config, profile)
    if not resource_type:
        response = client.get_project_resources(project_id)
    elif resource_type in ["bucket", "storage"]:
        response = client.get_project_buckets(project_id)
    elif resource_type in ["kubernetes", "cluster"]:
        response = client.get_project_clusters(project_id)
    elif resource_type == "balancer":
        response = client.get_project_balancers(project_id)
    elif resource_type == "database":
        response = client.get_project_databases(project_id)
    elif resource_type in ["dedicated", "dedicated_server"]:
        response = client.get_project_dedicated_servers(project_id)
    elif resource_type == "server":
        response = client.get_project_servers(project_id)
    else:
        raise UsageError(
            f"Resource type is not in [{', '.join(RESOURCE_TYPES)}]"
        )
    fmt.printer(response, output_format=output_format, func=print_resources)


# ------------------------------------------------------------- #
# $ twc project resource move                                   #
# ------------------------------------------------------------- #


def resolve_bucket_id(client: TimewebCloud, name: str):
    """Return bucket ID by bucket name."""
    buckets = client.get_buckets().json()["buckets"]
    for bucket in buckets:
        if bucket["name"] == name:
            return bucket["id"]
    sys.exit(f"Error: Bucket '{name}' not found.")


def print_result(response: Response):
    """Print response for project_resource_move()"""
    if response.status_code == 200:
        print(response.json()["resource"]["resource_id"])
    else:
        sys.exit(fmt.printer(response))


@project_resource.command("move", "mv")
def project_resource_move(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    project_id: int = typer.Argument(..., help="Destination project ID."),
    balancer: Optional[List[int]] = typer.Option(
        None, help="Move load balancer."
    ),
    bucket: Optional[List[str]] = typer.Option(
        None, help="Move object storage bucket."
    ),
    cluster: Optional[List[int]] = typer.Option(
        None, help="Move Kubernetes cluster."
    ),
    database: Optional[List[int]] = typer.Option(None, help="Move database."),
    dedicated: Optional[List[int]] = typer.Option(
        None, help="Move dedicated server."
    ),
    server: Optional[List[int]] = typer.Option(
        None, help="Move Cloud Server."
    ),
):
    """Move resources between projects."""
    client = create_client(config, profile)
    if balancer:
        for balancer_id in balancer:
            print_result(
                client.add_balancer_to_project(balancer_id, project_id)
            )
    if bucket:
        for bucket_id in bucket:
            if not bucket_id.isdigit():
                bucket_id = resolve_bucket_id(client, bucket_id)
            response = client.add_bucket_to_project(bucket_id, project_id)
            if response.status_code == 200:
                print(bucket_id)
            else:
                sys.exit(fmt.printer(response))
    if cluster:
        for cluster_id in cluster:
            print_result(client.add_cluster_to_project(cluster_id, project_id))
    if database:
        for database_id in database:
            print_result(
                client.add_database_to_project(database_id, project_id)
            )
    if dedicated:
        for dedic_id in dedicated:
            print_result(
                client.add_dedicated_server_to_project(dedic_id, project_id)
            )
    if server:
        for server_id in server:
            print_result(client.add_server_to_project(server_id, project_id))
