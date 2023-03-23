"""Project management commands."""

import sys

import click
from click_aliases import ClickAliasedGroup

from twc import fmt
from . import (
    create_client,
    handle_request,
    options,
    GLOBAL_OPTIONS,
    OUTPUT_FORMAT_OPTION,
)


RESOURCE_TYPES = [
    "all",
    "server",
    "balancer",
    "bucket",
    "cluster",
    "database",
    "dedicated_server",
]


@handle_request
def _project_list(client, *args, **kwargs):
    return client.get_projects(*args, **kwargs)


@handle_request
def _project_get(client, *args, **kwargs):
    return client.get_project(*args, **kwargs)


@handle_request
def _project_create(client, *args, **kwargs):
    return client.create_project(*args, **kwargs)


@handle_request
def _project_remove(client, *args, **kwargs):
    return client.delete_project(*args, **kwargs)


@handle_request
def _project_set_property(client, *args, **kwargs):
    return client.update_project(*args, **kwargs)


@handle_request
def _project_resource_list(client, *args, **kwargs):
    return client.get_project_resources(*args, **kwargs)


@handle_request
def _project_resource_list_balancers(client, *args, **kwargs):
    return client.get_project_balancers(*args, **kwargs)


@handle_request
def _project_resource_list_buckets(client, *args, **kwargs):
    return client.get_project_buckets(*args, **kwargs)


@handle_request
def _project_resource_list_clusters(client, *args, **kwargs):
    return client.get_project_clusters(*args, **kwargs)


@handle_request
def _project_resource_list_databases(client, *args, **kwargs):
    return client.get_project_databases(*args, **kwargs)


@handle_request
def _project_resource_list_servers(client, *args, **kwargs):
    return client.get_project_servers(*args, **kwargs)


@handle_request
def _project_resource_list_dedicated_servers(client, *args, **kwargs):
    return client.get_project_dedicated_servers(*args, **kwargs)


@handle_request
def _project_resource_move(client, *args, **kwargs):
    return client.move_resource_to_project(*args, **kwargs)


# ------------------------------------------------------------- #
# $ twc project                                                 #
# ------------------------------------------------------------- #


@click.group("project", cls=ClickAliasedGroup)
@options(GLOBAL_OPTIONS[:2])
def project():
    """Manage Projects."""


# ------------------------------------------------------------- #
# $ twc project list                                            #
# ------------------------------------------------------------- #


def print_projects(response: object):
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


@project.command("list", aliases=["ls"], help="List Projects.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
def project_list(
    config,
    profile,
    verbose,
    output_format,
):
    client = create_client(config, profile)
    response = _project_list(client)
    fmt.printer(response, output_format=output_format, func=print_projects)


# ------------------------------------------------------------- #
# $ twc project create                                          #
# ------------------------------------------------------------- #


@project.command("create", help="Create image.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option("--name", required=True, help="Project name.")
@click.option("--desc", default=None, help="Project description.")
@click.option("--avatar-id", default=None, help="Project image.")
def image_create(
    config, profile, verbose, output_format, name, desc, avatar_id
):
    client = create_client(config, profile)
    response = _project_create(
        client, name=name, description=desc, avatar_id=avatar_id
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: click.echo(response.json()["project"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc project remove                                          #
# ------------------------------------------------------------- #


@project.command(
    "remove",
    aliases=["rm"],
    help="Remove project. Not affects on project resources.",
)
@options(GLOBAL_OPTIONS)
@click.confirmation_option(
    prompt="Project resources will be moved to default project. Continue?"
)
@click.argument("project_id", nargs=-1, required=True)
def project_remove(config, profile, verbose, project_id):
    client = create_client(config, profile)

    for prj in project_id:
        response = _project_remove(client, prj)
        if response.status_code == 204:
            click.echo(prj)
        else:
            fmt.printer(response)


# ------------------------------------------------------------- #
# $ twc project set-property                                    #
# ------------------------------------------------------------- #


@project.command(
    "set-property", help="Change proejct name, description and avatar."
)
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option("--name", default=None, help="Project name.")
@click.option("--desc", default=None, help="Project description.")
@click.option("--avatar-id", default=None, help="Project image.")
@click.argument("project_id", required=True)
def project_set_property(
    config, profile, verbose, output_format, name, desc, avatar_id, project_id
):
    client = create_client(config, profile)
    response = _project_set_property(
        client, project_id, name=name, description=desc, avatar_id=avatar_id
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: click.echo(response.json()["project"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc project resource                                        #
# ------------------------------------------------------------- #


@project.group("resource", cls=ClickAliasedGroup)
@options(GLOBAL_OPTIONS[:2])
def resource():
    """Manage Project resources."""


# ------------------------------------------------------------- #
# $ twc project resource list                                   #
# ------------------------------------------------------------- #


def print_resources(response, resource_type: str):
    resources = response.json()
    resource_keys = list(resources.keys())
    resource_keys.remove("response_id")
    resource_keys.remove("meta")

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
            if resource_type in {key[:-1], "all"}:
                for item in resources[key]:
                    try:
                        location = item["location"]
                    except KeyError:
                        # Balancers, clusters, and databases has no 'location' field.
                        # These services is available only in 'ru-1' location.
                        location = "ru-1"
                    table.row(
                        [
                            item["id"],
                            item["name"],
                            location,
                            key[:-1],
                        ]
                    )
    table.print()


@resource.command("list", aliases=["ls"], help="List project resources.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option(
    "--type",
    "resource_type",
    type=click.Choice(RESOURCE_TYPES),
    default="all",
    show_default=True,
    help="Resource type.",
)
@click.argument("project_id", type=int, required=True)
def project_resource_list(
    config, profile, verbose, output_format, resource_type, project_id
):
    client = create_client(config, profile)
    response = _project_resource_list(client, project_id)
    fmt.printer(
        response,
        output_format=output_format,
        resource_type=resource_type,
        func=print_resources,
    )


# ------------------------------------------------------------- #
# $ twc project resource move                                   #
# ------------------------------------------------------------- #


def get_project_id_by_resource(client, resource_id, resource_type: str) -> int:
    """Return project_id by resource_id and resource_type."""
    projects = _project_list(client).json()["projects"]

    for prj in projects:

        if resource_type == "server":
            resources = _project_resource_list_servers(client, prj["id"])
        if resource_type == "balancer":
            resources = _project_resource_list_balancers(client, prj["id"])
        if resource_type == "bucket":
            resources = _project_resource_list_buckets(client, prj["id"])
        if resource_type == "cluster":
            resources = _project_resource_list_clusters(client, prj["id"])
        if resource_type == "database":
            resources = _project_resource_list_databases(client, prj["id"])
        if resource_type == "dedicated_server":
            resources = _project_resource_list_dedicated_servers(
                client, prj["id"]
            )

        for resource in resources.json()[resource_type + "s"]:
            if resource["id"] == resource_id:
                return prj["id"]
    return None


@resource.command(
    "move", aliases=["mv"], help="Move resources between projects."
)
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option(
    "--resource-id", type=int, required=True, help="Resource ID to move."
)
@click.option(
    "--type",
    "resource_type",
    type=click.Choice(RESOURCE_TYPES[1:]),
    required=True,
    help="Resource type.",
)
@click.option(
    "--to-project",
    "project_id",
    type=int,
    required=True,
    help="Destination Project ID.",
)
def project_resource_move(
    config,
    profile,
    verbose,
    output_format,
    resource_id,
    resource_type,
    project_id,
):
    client = create_client(config, profile)

    # Change resource_type 'server' to 'servers', etc.
    old_project_id = get_project_id_by_resource(
        client, resource_id, resource_type
    )
    if not old_project_id:
        sys.exit(
            f"Error: Cannot find project_id "
            f"for resource '{resource_type} with ID {resource_id}'."
        )

    # Prepare resource types for _project_resource_move()
    resources_map = {
        "server": "server",
        "balancer": "balancer",
        "database": "database",
        "cluster": "kubernetes",
        "bucket": "storage",
        "dedicated_server": "dedicated",
    }

    response = _project_resource_move(
        client,
        from_project=old_project_id,
        to_project=project_id,
        resource_id=resource_id,
        resource_type=resources_map[resource_type],
    )

    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: click.echo(
            response.json()["resource"]["resource_id"]
        ),
    )
