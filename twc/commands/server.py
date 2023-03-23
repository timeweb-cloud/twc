"""Cloud Server management commands."""

import re
import os
import sys
import datetime

import click
from click_aliases import ClickAliasedGroup

from twc import fmt
from . import (
    create_client,
    handle_request,
    options,
    debug,
    confirm_action,
    set_value_from_config,
    MutuallyExclusiveOption,
    GLOBAL_OPTIONS,
    OUTPUT_FORMAT_OPTION,
    DEFAULT_CONFIGURATOR_ID,
    REGIONS_WITH_CONFIGURATOR,
    REGIONS_WITH_IPV6,
)
from .ssh_key import (
    _ssh_key_list,
    _ssh_key_new,
    _ssh_key_add,
)
from .image import _image_list
from .project import (
    _project_list,
    _project_resource_list_servers,
    _project_resource_move,
)


@handle_request
def _server_list(client, **kwargs):
    return client.get_servers(**kwargs)


@handle_request
def _server_get(client, *args, **kwargs):
    return client.get_server(*args, **kwargs)


@handle_request
def _server_create(client, *args, **kwargs):
    return client.create_server(*args, **kwargs)


@handle_request
def _server_update(client, *args, **kwargs):
    return client.update_server(*args, **kwargs)


@handle_request
def _server_action(client, *args, **kwargs):
    return client.do_action_with_server(*args, **kwargs)


@handle_request
def _server_clone(client, *args):
    return client.clone_server(*args)


@handle_request
def _server_remove(client, *args):
    return client.delete_server(*args)


@handle_request
def _get_server_configurators(client):
    return client.get_server_configurators()


@handle_request
def _server_presets(client):
    return client.get_server_presets()


@handle_request
def _server_software(client):
    return client.get_server_software()


@handle_request
def _server_os_images(client):
    return client.get_server_os_images()


@handle_request
def _server_logs(client, *args, **kwargs):
    return client.get_server_logs(*args, **kwargs)


@handle_request
def _server_set_boot_mode(client, *args, **kwargs):
    return client.set_server_boot_mode(*args, **kwargs)


@handle_request
def _server_set_nat_mode(client, *args, **kwargs):
    return client.set_server_nat_mode(*args, **kwargs)


@handle_request
def _server_ip_list(client, *args):
    return client.get_ips_by_server_id(*args)


@handle_request
def _server_ip_add(client, *args, **kwargs):
    return client.add_ip_addr(*args, **kwargs)


@handle_request
def _server_ip_remove(client, *args, **kwargs):
    return client.delete_ip_addr(*args, **kwargs)


@handle_request
def _server_ip_set_ptr(client, *args, **kwargs):
    return client.update_ip_addr(*args, **kwargs)


@handle_request
def _server_disk_list(client, *args):
    return client.get_disks_by_server_id(*args)


@handle_request
def _server_disk_get(client, *args):
    return client.get_disk(*args)


@handle_request
def _server_disk_add(client, *args, **kwargs):
    return client.add_disk(*args, **kwargs)


@handle_request
def _server_disk_remove(client, *args, **kwargs):
    return client.delete_disk(*args, **kwargs)


@handle_request
def _server_disk_resize(client, *args, **kwargs):
    return client.update_disk(*args, **kwargs)


@handle_request
def _server_disk_autobackup_status(client, *args, **kwargs):
    return client.get_disk_autobackup_settings(*args, **kwargs)


@handle_request
def _server_disk_autobackup_update(client, *args, **kwargs):
    return client.update_disk_autobackup_settings(*args, **kwargs)


@handle_request
def _server_backup_list(client, *args, **kwargs):
    return client.get_disk_backups(*args, **kwargs)


@handle_request
def _server_backup_get(client, *args, **kwargs):
    return client.get_disk_backup(*args, **kwargs)


@handle_request
def _server_backup_create(client, *args, **kwargs):
    return client.create_disk_backup(*args, **kwargs)


@handle_request
def _server_backup_set_property(client, *args, **kwargs):
    return client.update_disk_backup(*args, **kwargs)


@handle_request
def _server_backup_remove(client, *args, **kwargs):
    return client.delete_disk_backup(*args, **kwargs)


@handle_request
def _server_backup_do_action(client, *args, **kwargs):
    return client.do_action_with_disk_backup(*args, **kwargs)


# ------------------------------------------------------------- #
# $ twc server                                                  #
# ------------------------------------------------------------- #


@click.group("server", cls=ClickAliasedGroup)
@options(GLOBAL_OPTIONS[:2])
def server():
    """Manage Cloud Servers."""


# ------------------------------------------------------------- #
# $ twc server list                                             #
# ------------------------------------------------------------- #


def print_servers(response: object, filters: str, ids: bool):
    if filters:
        servers = fmt.filter_list(response.json()["servers"], filters)
    else:
        servers = response.json()["servers"]

    if ids:
        for _server in servers:
            click.echo(_server["id"])
        return

    table = fmt.Table()
    table.header(
        [
            "ID",
            "NAME",
            "REGION",
            "STATUS",
            "IPV4",
        ]
    )
    for _server in servers:
        for network in _server["networks"]:
            if network["type"] == "public":
                for ip_addr in network["ips"]:
                    if (
                        ip_addr["type"] == "ipv4"
                        and ip_addr["is_main"] is True
                    ):
                        main_ipv4 = ip_addr["ip"]
        table.row(
            [
                _server["id"],
                _server["name"],
                _server["location"],
                _server["status"],
                main_ipv4,
            ]
        )
    table.print()


@server.command("list", aliases=["ls"], help="List Cloud Servers.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option("--filter", "-f", "filters", default="", help="Filter output.")
@click.option("--region", help="Use region (location).")
@click.option(
    "--limit",
    type=int,
    default=500,
    show_default=True,
    help="Items to display.",
)
@click.option("--ids", is_flag=True, help="Print only server IDs.")
def server_list(
    config, profile, verbose, region, output_format, filters, limit, ids
):
    if filters:
        filters = filters.replace("region", "location")
    if region:
        if filters:
            filters = filters + f",location:{region}"
        else:
            filters = f"location:{region}"

    client = create_client(config, profile)
    response = _server_list(client, limit=limit)
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_servers,
        ids=ids,
    )


# ------------------------------------------------------------- #
# $ twc server get                                              #
# ------------------------------------------------------------- #


def print_server(response: object):
    _server = response.json()["server"]

    for network in _server["networks"]:
        if network["type"] == "public":
            for ip_addr in network["ips"]:
                if ip_addr["type"] == "ipv4" and ip_addr["is_main"] is True:
                    main_ipv4 = ip_addr["ip"]

    table = fmt.Table()
    table.header(
        [
            "ID",
            "NAME",
            "REGION",
            "STATUS",
            "IPV4",
        ]
    )
    table.row(
        [
            _server["id"],
            _server["name"],
            _server["location"],
            _server["status"],
            main_ipv4,
        ]
    )
    table.print()


def print_server_networks(response: object):
    networks = response.json()["server"]["networks"]
    for network in networks:
        if network["type"] == "public":
            table = fmt.Table()
            table.header(
                [
                    "NETWORK",
                    "ADDRESS",
                    "VERSION",
                    "PTR",
                    "PRIMARY",
                ]
            )
            for ip_addr in network["ips"]:
                table.row(
                    [
                        network["type"],
                        ip_addr["ip"],
                        ip_addr["type"],
                        ip_addr["ptr"],
                        ip_addr["is_main"],
                    ]
                )
            table.print()
        else:
            table = fmt.Table()
            for ip_addr in network["ips"]:
                table.row([network["type"], ip_addr["ip"], ip_addr["type"]])
            table.print()


def print_server_disks(response: object):
    disks = response.json()["server"]["disks"]
    table = fmt.Table()
    table.header(
        [
            "ID",
            "NAME",
            "MOUNTED",
            "SYSTEM",
            "TYPE",
            "STATUS",
            "SIZE",
            "USED",
        ]
    )
    for disk in disks:
        table.row(
            [
                disk["id"],
                disk["system_name"],
                disk["is_mounted"],
                disk["is_system"],
                disk["type"],
                disk["status"],
                str(round(disk["size"] / 1024)) + "G",
                str(round(disk["used"] / 1024, 1)) + "G",
            ]
        )
    table.print()


@server.command("get", help="Get Cloud Server.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option(
    "--status",
    is_flag=True,
    help="Display status and exit with 0 if status is 'on'.",
)
@click.option("--networks", is_flag=True, help="Display networks.")
@click.option("--disks", is_flag=True, help="Display disks.")
@click.argument("server_id", type=int, required=True)
def server_get(
    config, profile, verbose, output_format, status, networks, disks, server_id
):
    client = create_client(config, profile)
    response = _server_get(client, server_id)
    if status:
        _status = response.json()["server"]["status"]
        if _status == "on":
            click.echo(_status)
            sys.exit(0)
        else:
            sys.exit(_status)
    if networks:
        print_server_networks(response)
        sys.exit(0)
    if disks:
        print_server_disks(response)
        sys.exit(0)
    fmt.printer(response, output_format=output_format, func=print_server)


# ------------------------------------------------------------- #
# $ twc server create                                           #
# ------------------------------------------------------------- #


def get_os_name_by_id(os_images: list, os_id: int) -> str:
    """Return human readable operating system name by OS ID::

    79 --> ubuntu-22.04
    65 --> windows-2012-standard
    """
    for os in os_images:
        if os["id"] == os_id:
            if os["family"] == "linux":
                return f"{os['name']}-{os['version']}"
            return f"{os['name']}-{os['version']}-{os['version_codename']}"
    return None


def get_os_id_by_name(os_images: list, os_name: str) -> int:
    """Return OS image ID by name. For example::

    ubuntu-22.04 --> 79
    windows-2012-standard --> 65
    """
    os_id = None

    if os_name.startswith("windows-"):
        name, version, codename = os_name.split("-")
        for os in os_images:
            if (
                os["name"] == name
                and os["version"] == version
                and os["version_codename"] == codename
            ):
                os_id = os["id"]
    else:
        name, version = os_name.split("-")
        for os in os_images:
            if os["name"] == name and os["version"] == version:
                os_id = os["id"]
    return os_id


def get_project_id_by_server_id(client, projects: list, server_id: int) -> int:
    """Return project_id by server_id."""
    for project in projects:
        for server in _project_resource_list_servers(
            client, project["id"]
        ).json()["servers"]:
            if server["id"] == server_id:
                return project["id"]
    return None


def size_to_mb(size: str) -> int:
    """Transform string like '5G' into integer in megabytes.
    Case insensitive. For example::

        1T --> 1048576
        5G --> 5120
        1024M  --> 1024
        2048 --> 2048

    NOTE! This function does not support floats e.g. 1.5T x--> 1572864
    """
    match = re.match(r"^([0-9]+)([mgt]?)$", size, re.I)
    if match:
        try:
            val, unit = list(match.groups())
            if unit.lower() == "g":
                return int(val) * 1024
            if unit.lower() == "t":
                return int(val) * 1048576
            return int(val)
        except TypeError:
            return None
    else:
        return None


def check_value(
    value: int, minv: int = 0, maxv: int = 0, step: int = 0
) -> bool:
    """Check integer `value` is suitable with required limitations.
    Return True if success. This function is for value testing by
    `server_configurators` requirements.
    """
    try:
        # pylint: disable=chained-comparison
        return value <= maxv and value >= minv and (value / step).is_integer()
    except TypeError:
        return None


def validate_bandwidth(ctx, param, value):
    """Return valid bandwidth value or exit. See "Callback for Validation"
    at https://click.palletsprojects.com/en/8.1.x/options
    """
    if not value:
        return None

    if check_value(value, minv=100, maxv=1000, step=100):
        return value

    raise click.BadParameter("Value must be in range 100-1000 with step 100.")


def validate_image(client, image: str) -> int:
    """Return valid os_id or exit."""
    debug("Get list of OS images...")
    os_images = _server_os_images(client).json()["servers_os"]

    if re.match(r"^[a-z]+-[0-9.]+$", image, re.I):
        return get_os_id_by_name(os_images, image)

    try:
        if int(image) in [int(os["id"]) for os in os_images]:
            return int(image)
        return None
    except (TypeError, ValueError):
        return None


def validate_cpu(configurator: dict, value: int) -> int:
    """Return valid cpu value or exit."""
    if check_value(
        value,
        minv=configurator["requirements"]["cpu_min"],
        maxv=configurator["requirements"]["cpu_max"],
        step=configurator["requirements"]["cpu_step"],
    ):
        return value

    raise click.BadParameter("Too many or too few CPUs.")


def validate_ram(configurator: dict, value: str) -> int:
    """Return valid RAM value in megabytes or exit."""
    if check_value(
        size_to_mb(value),
        minv=configurator["requirements"]["ram_min"],
        maxv=configurator["requirements"]["ram_max"],
        step=configurator["requirements"]["ram_step"],
    ):
        return size_to_mb(value)

    raise click.BadParameter("Too large or too small size of RAM.")


def validate_disk(configurator: dict, value: str) -> int:
    """Return valid disk value in megabytes or exit."""
    if check_value(
        size_to_mb(value),
        minv=configurator["requirements"]["disk_min"],
        maxv=configurator["requirements"]["disk_max"],
        step=configurator["requirements"]["disk_step"],
    ):
        return size_to_mb(value)

    raise click.BadParameter("Too large or too small disk size.")


def get_configuration(
    client, configurator_id: int, cpu: int, ram: str, disk: str
) -> dict:
    """Return `configuration` if CPU, RAM and Disk values is valid or exit.
    This function is used into server_create().
    """
    configurators = _get_server_configurators(client).json()

    for item in configurators["server_configurators"]:
        if item["id"] == configurator_id:
            configurator = item  # <-- current configurator

    return {
        "configurator_id": configurator_id,
        "cpu": validate_cpu(configurator, cpu),
        "ram": validate_ram(configurator, ram),
        "disk": validate_disk(configurator, disk),
    }


def add_ssh_key_from_file(
    client, ssh_key_file: str, existing_ssh_keys: list
) -> int:
    """Return integer SSH-key ID. Add new SSH-key if not exist."""
    ssh_key_name = os.path.basename(ssh_key_file)
    try:
        with open(ssh_key_file, "r", encoding="utf-8") as pubkey:
            ssh_key_body = pubkey.read().strip()
    except (OSError, IOError, FileNotFoundError) as error:
        sys.exit(f"Error: Cannot read SSH-key: {error}")

    # I don't want to add the same key over and over
    for exist_key in existing_ssh_keys:
        if ssh_key_body == exist_key["body"]:
            debug(
                f"SSH-Key '{ssh_key_name}' already exists,"
                f" ID {exist_key['id']} is used."
            )
            return exist_key["id"]

    debug(f"Add new SSH-key '{ssh_key_name}'...")
    added_key = _ssh_key_new(
        client,
        name=ssh_key_name,
        body=ssh_key_body,
        is_default=False,
    )
    ssh_key_id = added_key.json()["ssh_key"]["id"]
    debug(f"New SSH-key '{ssh_key_name}' ID is '{ssh_key_id}'")
    return ssh_key_id


def add_ssh_key(client, existing_ssh_keys: list, pubkey: str) -> int:
    """Retrun SSH-key ID. from file, by SSH-key ID or by SSH-key name."""
    # From filesystem
    if os.path.exists(pubkey):
        debug(f"SSH-key to add: file: {pubkey}")
        return add_ssh_key_from_file(client, pubkey, existing_ssh_keys)

    # Add by ID
    if pubkey.isdigit():
        if int(pubkey) in [key["id"] for key in existing_ssh_keys]:
            debug(f"SSH-key to add: ID: {pubkey}")
            return int(pubkey)
        sys.exit(f"Error: SSH-key with ID {pubkey} not found.")

    # Add by name
    for ssh_key in existing_ssh_keys:
        if pubkey == ssh_key["name"]:
            debug(f"SSH-key to add: name: {pubkey} ID: {ssh_key['id']}")
            return ssh_key["id"]

    sys.exit(f"Error: SSH-key '{pubkey}' not found.")


@server.command("create", help="Create Cloud Server.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option("--name", required=True, help="Cloud Server display name.")
@click.option("--comment", help="Comment.")
@click.option("--avatar-id", default=None, help="Avatar ID.")
@click.option(
    "--image", required=True, help="OS ID, name or image UUID to install."
)
@click.option(
    "--preset-id",
    type=int,
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["cpu", "ram", "disk"],
    help="Configuration preset ID.",
)
@click.option("--cpu", type=int, help="Number of CPUs.")
@click.option("--ram", help="RAM size, e.g. 1024M, 1G.")
@click.option("--disk", help="Primary disk size e.g. 15360M, 15G.")
@click.option(
    "--bandwidth",
    type=int,
    callback=validate_bandwidth,
    help="Network bandwidth.",
)
@click.option(
    "--software-id", type=int, default=None, help="Software ID to install."
)
@click.option(
    "--ssh-key",
    metavar="FILE|ID|NAME",
    default=None,
    multiple=True,
    help="SSH-key, can be multiple.",
)
@click.option(
    "--ddos-protection",
    type=bool,
    default=False,
    show_default=True,
    help="Enable DDoS-Guard.",
)
@click.option(
    "--local-network",
    type=bool,
    default=False,
    show_default=True,
    help="Enable local network.",
)
@click.option(
    "--project-id",
    type=int,
    default=None,
    envvar="TWC_PROJECT",
    callback=set_value_from_config,
    help="Add server to specific project.",
)
def server_create(
    config,
    profile,
    verbose,
    output_format,
    name,
    comment,
    avatar_id,
    image,
    preset_id,
    cpu,
    ram,
    disk,
    bandwidth,
    software_id,
    ssh_key,
    ddos_protection,
    local_network,
    project_id,
):
    """Create Cloud Server."""
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches

    client = create_client(config, profile)

    # Set server parameters
    payload = {
        "name": name,
        "comment": comment,
        "software_id": software_id,
        "avatar_id": avatar_id,
        "is_ddos_guard": ddos_protection,
        "is_local_network": local_network,
    }

    # Get os_id or exit
    debug("Looking for os_id...")
    os_id = validate_image(client, image)
    if os_id:
        debug(f"os_id is '{os_id}'")
        payload["os_id"] = os_id
    else:
        debug("os_id not found, looking for image_id...")
        if image in [
            img["id"] for img in _image_list(client).json()["images"]
        ]:
            debug(f"image_id is '{image}'")
            payload["image_id"] = image
        else:
            raise click.BadParameter("Wrong image name or ID.")

    # Fallback bandwidth to minimum
    if not bandwidth and not preset_id:
        payload["bandwidth"] = 100

    # SSH-keys
    ssh_keys_ids = []
    if ssh_key:
        debug("Get SSH-keys...")
        existing_ssh_keys = _ssh_key_list(client).json()["ssh_keys"]

        for pubkey in ssh_key:
            ssh_keys_ids.append(add_ssh_key(client, existing_ssh_keys, pubkey))

    payload["ssh_keys_ids"] = ssh_keys_ids

    # Create Cloud Server from configurator or preset
    if cpu or ram or disk:
        debug("Get configurator...")
        payload["configuration"] = get_configuration(
            client,
            DEFAULT_CONFIGURATOR_ID,
            cpu,
            ram,
            disk,
        )
    elif preset_id:
        # Set bandwidth value from preset if option is not set
        if not bandwidth:
            debug("Check preset_id...")
            presets = _server_presets(client).json()["server_presets"]
            for preset in presets:
                if preset["id"] == preset_id:
                    debug(f"Set bandwidth from preset: {preset['bandwidth']}")
                    payload["bandwidth"] = preset["bandwidth"]

        payload["preset_id"] = preset_id
    else:
        raise click.UsageError(
            "Configuration or preset is required. "
            "Set '--cpu', '--ram' and '--disk' or '--preset-id'"
        )

    if project_id:
        debug("Check project_id")
        projects = _project_list(client).json()["projects"]
        if not project_id in [prj["id"] for prj in projects]:
            raise click.BadParameter("Wrong project ID.")

    # Do request
    debug("Create Cloud Server...")
    response = _server_create(client, **payload)

    # Add created server to project if set
    if project_id:
        new_server_id = response.json()["server"]["id"]
        debug(f"Add server '{new_server_id}' to project '{project_id}'")
        old_project_id = get_project_id_by_server_id(
            client, projects, new_server_id
        )
        project_resp = _project_resource_move(
            client,
            from_project=old_project_id,
            to_project=project_id,
            resource_id=new_server_id,
            resource_type="server",
        )
        debug(project_resp.text)

    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: click.echo(response.json()["server"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc server set-property                                     #
# ------------------------------------------------------------- #


@server.command("set-property", help="Update Cloud Server properties.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option("--name", help="Cloud server display name.")
@click.option("--comment", help="Comment.")
@click.option("--avatar-id", default=None, help="Avatar ID.")
@click.argument("server_id", type=int, required=True)
def server_set_property(
    config,
    profile,
    verbose,
    output_format,
    name,
    comment,
    avatar_id,
    server_id,
):
    client = create_client(config, profile)
    payload = {}

    if name:
        payload["name"] = name
    if comment:
        payload["comment"] = comment
    if avatar_id:
        payload["avatar_id"] = avatar_id

    if not payload:
        raise click.UsageError(
            "Nothing to do. Set one of "
            "['--name', '--comment', '--avatar-id']"
        )

    response = _server_update(client, server_id, payload)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: click.echo(response.json()["server"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc server resize                                           #
# ------------------------------------------------------------- #


@server.command("resize", help="Change CPU, RAM, disk and bandwidth.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option(
    "--preset-id",
    type=int,
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["cpu", "ram", "disk"],
    help="Configuration preset ID.",
)
@click.option("--cpu", type=int, help="Number of vCPUs.")
@click.option("--ram", help="RAM size, e.g. 1024M, 1G.")
@click.option("--disk", help="Primary disk size e.g. 15360M, 15G.")
@click.option(
    "--bandwidth",
    type=int,
    callback=validate_bandwidth,
    help="Network bandwidth.",
)
@click.option(
    "--yes",
    "confirmed",
    is_flag=True,
    help="Confirm the action without prompting.",
)
@click.argument("server_id", type=int, required=True)
def server_resize(
    config,
    profile,
    verbose,
    output_format,
    preset_id,
    cpu,
    ram,
    disk,
    bandwidth,
    confirmed,
    server_id,
):
    """Resize Cloud Server CPU, RAM and primary disk size."""
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements

    client = create_client(config, profile)
    payload = {}

    # Save original server state
    debug("Get server original state...")
    old_state = _server_get(client, server_id).json()["server"]

    # Get original server preset tags
    old_preset_tags = []
    if old_state["preset_id"]:
        debug(f"Get preset tags by preset_id {old_state['preset_id']}...")
        presets = _server_presets(client).json()["server_presets"]
        for preset in presets:
            if preset["id"] == old_state["preset_id"]:
                old_preset_tags = preset["tags"]
        debug(f"Preset tags is {old_preset_tags}")

    # Return error if user tries to change dedicated server
    if "vds_dedic" in old_preset_tags:
        sys.exit(
            "Error: Cannot change dedicated server."
            + "Please contact techsupport."
        )

    # Handle case: user tries to change configurator or switch from
    # preset to configurator.

    # Return error if user tries to switch from preset to configurator in
    # location where configurator is unavailable.
    if cpu or ram or disk:
        if old_state["location"] not in REGIONS_WITH_CONFIGURATOR:
            sys.exit(
                "Error: Can not change configuration in location "
                + f"'{old_state['location']}'. Change preset_id instead."
            )

        # Get original server configurator_id
        configurator_id = old_state["configurator_id"]
        configurator = None

        # Get configurator_id if user tries to switch from preset to
        # configurator. Don't ask what is this.
        debug("Get configurator_id...")
        if not configurator_id:
            if (
                "ssd_2022" in old_preset_tags
                or "discount35" in old_preset_tags
            ):
                configurator_id = 11  # discount configurator
            else:
                configurator_id = 9  # old full price configurator

        # Get configurator by configurator_id
        debug(f"configurator_id is {configurator_id}, get confugurator...")
        configurators = _get_server_configurators(client).json()
        for item in configurators["server_configurators"]:
            if item["id"] == configurator_id:
                configurator = item  # <-- this!

        # Check configurator and return error if configurator is unavailable
        debug(f"Configurator: '{configurator}'")
        if configurator_id and not configurator:
            sys.exit(
                "Error: Configurator is not available for your server. "
                + "Try to create new server."
            )

        # Add configurator key to payload
        payload["configurator"] = {}

        # Get original size of primary disk
        for old_disk in old_state["disks"]:
            if old_disk["is_system"]:  # is True
                primary_disk_size = old_disk["size"]

        # Fill payload with original server specs
        payload["configurator"].update(
            {
                "configurator_id": configurator_id,
                "cpu": old_state["cpu"],
                "ram": old_state["ram"],
                "disk": primary_disk_size,
            }
        )

        # Refill payload with parameters from command line
        if cpu:
            payload["configurator"].update(
                {"cpu": validate_cpu(configurator, cpu)}
            )

        if ram:
            payload["configurator"].update(
                {"ram": validate_ram(configurator, ram)}
            )

        if disk:
            payload["configurator"].update(
                {"disk": validate_disk(configurator, disk)}
            )

    if bandwidth:
        payload["bandwidth"] = bandwidth

    # Handle case: user tries to change preset to another preset.
    # Check passed preset_id and exit on fail
    if preset_id:
        # I cannot want to change preset to itself
        if preset_id == old_state["preset_id"]:
            sys.exit(
                "Error: Cannot change preset to itself. "
                f"Server already have preset_id {old_state['preset_id']}."
            )

        presets = _server_presets(client).json()["server_presets"]
        for preset in presets:
            if preset["id"] == preset_id:
                payload["preset_id"] = preset_id
        try:
            payload["preset_id"]
        except KeyError:
            sys.exit(f"Error: Invalid preset_id {preset_id}")

    # Prompt if no option --yes passed
    if not confirmed:
        if not confirm_action("Server will restart, continue?"):
            sys.exit("Aborted!")

    # Make request
    response = _server_update(client, server_id, payload)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: click.echo(response.json()["server"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc server reinstall                                        #
# ------------------------------------------------------------- #


def get_ssh_keys_by_server_id(client, server_id) -> list:
    """Return list of SSH-keys added to the server server_id."""
    ssh_keys = _ssh_key_list(client).json()["ssh_keys"]
    ssh_keys_list = []
    for pubkey in ssh_keys:
        for server in pubkey["used_by"]:
            if server["id"] == server_id:
                ssh_keys_list.append(pubkey["id"])
    return ssh_keys_list


@server.command("reinstall", help="Reinstall OS or software.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option(
    "--image", default=None, help="OS ID, name or image UUID to install."
)
@click.option(
    "--software-id", type=int, default=None, help="Software ID to install."
)
@click.option(
    "--add-ssh-keys",
    type=bool,
    default=True,
    show_default=True,
    help="Readd SSH-keys to reinstalled server.",
)
@click.confirmation_option(
    prompt="All data on Cloud Server will be lost.\n"
    "This action cannot be undone. Are you sure?"
)
@click.argument("server_id", type=int, required=True)
def server_reinstall(
    config,
    profile,
    verbose,
    output_format,
    image,
    software_id,
    add_ssh_keys,
    server_id,
):
    client = create_client(config, profile)
    payload = {}

    if image:
        os_id = validate_image(client, image)
        if os_id:
            payload["os_id"] = os_id
        else:
            if image in [
                img["id"] for img in _image_list(client).json()["images"]
            ]:
                payload["image_id"] = image
            else:
                raise click.BadParameter("Wrong image name or ID.")
    else:
        old_state = _server_get(client, server_id).json()["server"]
        if old_state["image"]:
            payload["image_id"] = old_state["image"]["id"]
        else:
            payload["os_id"] = old_state["os"]["id"]

    if software_id:
        payload["software_id"] = software_id

    if add_ssh_keys:
        debug(f"Get SSH-keys by server_id '{server_id}'")
        ssh_keys = get_ssh_keys_by_server_id(client, server_id)
        debug(f"SSH-keys to add: {ssh_keys}")

    debug(f"Reinstalling with params: {payload}")
    response = _server_update(client, server_id, payload)

    if add_ssh_keys and ssh_keys:
        debug(f"Readding SSH-keys {ssh_keys} to server '{server_id}'")
        ssh_add_resp = _ssh_key_add(client, server_id, ssh_key_ids=ssh_keys)
        if not ssh_add_resp.status_code == 204:
            fmt.printer(ssh_add_resp)

    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: click.echo(response.json()["server"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc server clone                                            #
# ------------------------------------------------------------- #


@server.command("clone", help="Clone Cloud Server.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.argument("server_id", type=int, required=True)
def server_clone(config, profile, output_format, verbose, server_id):
    client = create_client(config, profile)
    response = _server_clone(client, server_id)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: click.echo(response.json()["server"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc server remove                                           #
# ------------------------------------------------------------- #


@server.command("remove", aliases=["rm"], help="Remove Cloud Server.")
@options(GLOBAL_OPTIONS)
@click.argument("server_ids", nargs=-1, type=int, required=True)
@click.confirmation_option(
    prompt="This action cannot be undone. Are you sure?"
)
def server_remove(config, profile, verbose, server_ids):
    client = create_client(config, profile)

    for server_id in server_ids:
        response = _server_remove(client, server_id)
        if response.status_code == 204:
            click.echo(server_id)
        else:
            fmt.printer(response)


# ------------------------------------------------------------- #
# $ twc server <action>                                         #
# boot, reboot, shutdown, reset-root-password                   #
# ------------------------------------------------------------- #

# ------------------------------------------------------------- #
# $ twc server boot                                             #
# ------------------------------------------------------------- #


@server.command("boot", aliases=["start"], help="Boot Cloud Server.")
@options(GLOBAL_OPTIONS)
@click.argument("server_ids", nargs=-1, type=int, required=True)
def server_start(config, profile, verbose, server_ids):
    client = create_client(config, profile)

    for server_id in server_ids:
        response = _server_action(client, server_id, action="start")
        if response.status_code == 204:
            click.echo(server_id)
        else:
            fmt.printer(response)


# ------------------------------------------------------------- #
# $ twc server reboot                                           #
# ------------------------------------------------------------- #


@server.command("reboot", aliases=["restart"], help="Reboot Cloud Server.")
@options(GLOBAL_OPTIONS)
@click.option("--hard", "hard_reboot", is_flag=True, help="Do hard reboot.")
@click.argument("server_ids", nargs=-1, type=int, required=True)
def server_reboot(config, profile, verbose, server_ids, hard_reboot):
    if hard_reboot:
        action = "hard_reboot"
    else:
        action = "boot"
    client = create_client(config, profile)

    for server_id in server_ids:
        response = _server_action(client, server_id, action=action)
        if response.status_code == 204:
            click.echo(server_id)
        else:
            fmt.printer(response)


# ------------------------------------------------------------- #
# $ twc server shutdown                                         #
# ------------------------------------------------------------- #


@server.command("shutdown", aliases=["stop"], help="Shutdown Cloud Server.")
@options(GLOBAL_OPTIONS)
@click.option(
    "--hard", "hard_shutdown", is_flag=True, help="Do hard shutdown."
)
@click.argument("server_ids", nargs=-1, type=int, required=True)
def server_shutdown(config, profile, verbose, server_ids, hard_shutdown):
    if hard_shutdown:
        action = "hard_shutdown"
    else:
        action = "shutdown"
    client = create_client(config, profile)

    for server_id in server_ids:
        response = _server_action(client, server_id, action=action)
        if response.status_code == 204:
            click.echo(server_id)
        else:
            fmt.printer(response)


# ------------------------------------------------------------- #
# $ twc server reset-root-password                              #
# ------------------------------------------------------------- #


@server.command("reset-root-password", help="Reset root user password.")
@options(GLOBAL_OPTIONS)
@click.confirmation_option(
    prompt="New password will sent to contact email. Continue?"
)
@click.argument("server_id", type=int, required=True)
def server_reset_root(config, profile, verbose, server_id):
    client = create_client(config, profile)
    response = _server_action(client, server_id, action="reset_password")
    if response.status_code == 204:
        click.echo(server_id)
    else:
        fmt.printer(response)


# ------------------------------------------------------------- #
# $ twc server list-presets                                     #
# ------------------------------------------------------------- #


def print_presets(response: object, filters: str):
    if filters:
        presets = fmt.filter_list(response.json()["server_presets"], filters)
    else:
        presets = response.json()["server_presets"]
    table = fmt.Table()
    table.header(
        [
            "ID",
            "REGION",
            "PRICE",
            "CPU",
            "FREQ",
            "RAM",
            "DISK",
            "DISK TYPE",
            "BANDWIDTH",
            "DESCRIPTION",
            "LOCAL NETWORK",
        ]
    )
    for preset in presets:
        table.row(
            [
                preset["id"],
                preset["location"],
                preset["price"],
                preset["cpu"],
                preset["cpu_frequency"],
                str(round(preset["ram"] / 1024)) + "G",
                str(round(preset["disk"] / 1024)) + "G",
                preset["disk_type"],
                preset["bandwidth"],
                preset["description_short"],
                preset["is_allowed_local_network"],
            ]
        )
    table.print()


@server.command("list-presets", help="List configuration presets.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option("--region", "-r", help="Use region (location).")
@click.option("--filter", "-f", "filters", default="", help="Filter output.")
def server_presets(config, profile, verbose, output_format, filters, region):
    if filters:
        filters = filters.replace("region", "location")
    if region:
        if filters:
            filters = filters + f",location:{region}"
        else:
            filters = f"location:{region}"

    client = create_client(config, profile)
    response = _server_presets(client)
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_presets,
    )


# ------------------------------------------------------------- #
# $ twc server list-os-images                                   #
# ------------------------------------------------------------- #


def print_os_images(response: object, filters: str):
    if filters:
        os_list = fmt.filter_list(response.json()["servers_os"], filters)
    else:
        os_list = response.json()["servers_os"]
    table = fmt.Table()
    table.header(
        ["ID", "FAMILY", "NAME", "VERSION", "CODENAME", "REQUIREMENTS"]
    )
    for os in os_list:
        try:
            value = round(os["requirements"]["disk_min"] / 1024)
            requirements = f"Disk >= {value}G"
        except KeyError:
            requirements = ""
        table.row(
            [
                os["id"],
                os["family"],
                os["name"],
                os["version"],
                os["version_codename"],
                requirements,
            ]
        )
    table.print()


@server.command(
    "list-os-images", help="List prebuilt operating system images."
)
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option("--filter", "-f", "filters", default="", help="Filter output.")
def server_os_images(config, profile, verbose, output_format, filters):
    client = create_client(config, profile)
    response = _server_os_images(client)
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_os_images,
    )


# ------------------------------------------------------------- #
# $ twc server list-software                                    #
# ------------------------------------------------------------- #


def print_software(response: object):
    table = fmt.Table()
    table.header(["ID", "NAME", "OS"])
    for soft in response.json()["servers_software"]:
        table.row(
            [
                soft["id"],
                soft["name"],
                ", ".join([str(k) for k in soft["os_ids"]]),
            ]
        )
    table.print()


@server.command("list-software", help="List software.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
def server_software(config, profile, verbose, output_format):
    client = create_client(config, profile)
    response = _server_software(client)
    fmt.printer(response, output_format=output_format, func=print_software)


# ------------------------------------------------------------- #
# $ twc server logs                                             #
# ------------------------------------------------------------- #


def print_logs(response: object):
    event_log = response.json()["server_logs"]
    for line in event_log:
        click.echo(
            f"{line['logged_at']} id={line['id']} event={line['event']}"
        )


@server.command("logs", help="View Cloud Server events log.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option(
    "--limit",
    type=int,
    default=500,
    show_default=True,
    help="Items to display.",
)
@click.option(
    "--order",
    default="asc",
    show_default=True,
    type=click.Choice(["asc", "desc"]),
    help="Sort logs by datetime.",
)
@click.argument("server_id", type=int, required=True)
def server_logs(
    config, profile, verbose, output_format, limit, order, server_id
):
    client = create_client(config, profile)
    response = _server_logs(
        client, server_id=server_id, limit=limit, order=order
    )
    fmt.printer(response, output_format=output_format, func=print_logs)


# ------------------------------------------------------------- #
# $ twc server set-boot-mode                                    #
# ------------------------------------------------------------- #


@server.command("set-boot-mode", help="Set Cloud Server boot mode.")
@options(GLOBAL_OPTIONS)
@click.option(
    "--server-id",
    "server_ids",
    type=int,
    multiple=True,
    required=True,
    help="Cloud Server ID, can be multiple.",
)
@click.confirmation_option(prompt="Server will reboot, continue?")
@click.argument(
    "boot_mode",
    type=click.Choice(["default", "single", "recovery_disk"]),
    required=True,
)
def server_set_boot_mode(config, profile, verbose, boot_mode, server_ids):
    client = create_client(config, profile)

    for server_id in server_ids:
        response = _server_set_boot_mode(
            client, server_id, boot_mode=boot_mode
        )
        if response.status_code == 204:
            click.echo(server_id)
        else:
            fmt.printer(response)


# ------------------------------------------------------------- #
# $ twc server set-nat-mode                                     #
# ------------------------------------------------------------- #


@server.command("set-nat-mode", help="Set Cloud Server NAT mode.")
@options(GLOBAL_OPTIONS)
@click.option(
    "--server-id",
    "server_ids",
    type=int,
    multiple=True,
    required=True,
    help="Cloud Server ID, can be multiple.",
)
@click.argument(
    "nat_mode",
    type=click.Choice(["dnat_and_snat", "snat", "no_nat"]),
    required=True,
)
def server_set_nat_mode(config, profile, verbose, nat_mode, server_ids):
    client = create_client(config, profile)

    for server_id in server_ids:
        response = _server_set_nat_mode(client, server_id, nat_mode=nat_mode)
        if response.status_code == 204:
            click.echo(server_id)
        else:
            fmt.printer(response)


# ------------------------------------------------------------- #
# $ twc server ip                                               #
# ------------------------------------------------------------- #


@server.group("ip", cls=ClickAliasedGroup)
@options(GLOBAL_OPTIONS[:2])
def ip_addr():
    """Manage public IPs."""


# ------------------------------------------------------------- #
# $ twc server ip list                                          #
# ------------------------------------------------------------- #


def print_ips(response: object):
    ips = response.json()["server_ips"]
    table = fmt.Table()
    table.header(["ADDRESS", "VERSION", "PTR", "PRIMARY"])
    for ip_addr in ips:
        table.row(
            [
                ip_addr["ip"],
                ip_addr["type"],
                ip_addr["ptr"],
                ip_addr["is_main"],
            ]
        )
    table.print()


@ip_addr.command(
    "list", aliases=["ls"], help="List public IPs attached to Cloud Server."
)
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.argument("server_id", type=int, required=True)
def server_ip_list(config, profile, verbose, output_format, server_id):
    client = create_client(config, profile)
    response = _server_ip_list(client, server_id)
    fmt.printer(response, output_format=output_format, func=print_ips)


# ------------------------------------------------------------- #
# $ twc server ip add                                           #
# ------------------------------------------------------------- #


@ip_addr.command("add", help="Attach new IP to Cloud Server.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option(
    "--ipv4/--ipv6", default=True, show_default=True, help="IP version."
)
@click.option("--ptr", help="IP address pointer (RDNS).")
@click.option(
    "--to-server",
    "server_id",
    type=int,
    required=True,
    help="Cloud Server ID.",
)
def server_ip_add(
    config, profile, verbose, output_format, ipv4, ptr, server_id
):
    client = create_client(config, profile)
    if not ipv4:
        debug("Get Cloud Server location...")
        location = _server_get(client, server_id).json()["server"]["location"]
        if location not in REGIONS_WITH_IPV6:
            sys.exit(f"Error: IPv6 is not available in location '{location}'.")
        ip_version = "ipv6"
    else:
        ip_version = "ipv4"

    response = _server_ip_add(client, server_id, version=ip_version, ptr=ptr)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: click.echo(response.json()["server_ip"]["ip"]),
    )


# ------------------------------------------------------------- #
# $ twc server ip remove                                        #
# ------------------------------------------------------------- #


def get_server_id_by_ip(client, ip_address):
    """Return server_id if IP address found or return None."""
    servers = _server_list(client, limit=10000).json()["servers"]
    for server in servers:
        for network in server["networks"]:
            for ip_addr in network["ips"]:
                if ip_address == ip_addr["ip"]:
                    return server["id"]
    return None


@ip_addr.command("remove", aliases=["rm"], help="Remove IP address.")
@options(GLOBAL_OPTIONS)
@click.confirmation_option(
    prompt="This action cannot be undone. Are you sure?"
)
@click.argument("ip_address", required=True)
def server_ip_remove(config, profile, verbose, ip_address):
    client = create_client(config, profile)

    debug("Looking for IP address...")
    server_id = get_server_id_by_ip(client, ip_address)
    if not server_id:
        sys.exit(f"IP address '{ip_address}' not found.")

    debug("Check IP...")
    ips = _server_ip_list(client, server_id).json()["server_ips"]
    for ip_addr in ips:
        if ip_addr["ip"] == ip_address and ip_addr["is_main"]:
            sys.exit("Error: Cannot remove Cloud Server primaty IP address.")

    response = _server_ip_remove(client, server_id, ip_address)

    if response.status_code == 204:
        click.echo(ip_address)
    else:
        fmt.printer(response)


# ------------------------------------------------------------- #
# $ twc server ip set-ptr                                       #
# ------------------------------------------------------------- #


@ip_addr.command("set-ptr", help="Set IP pointer (RDNS).")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option("--address", "ip_address", required=True, help="IP address.")
@click.argument("ptr", required=True)
def server_ip_set_ptr(
    config, profile, verbose, output_format, ip_address, ptr
):
    client = create_client(config, profile)

    debug("Looking for IP address...")
    server_id = get_server_id_by_ip(client, ip_address)
    if not server_id:
        sys.exit(f"IP address '{ip_address}' not found.")

    response = _server_ip_set_ptr(
        client, server_id, ip_addr=ip_address, ptr=ptr
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: click.echo(response.json()["server_ip"]["ip"]),
    )


# ------------------------------------------------------------- #
# $ twc server disk                                             #
# ------------------------------------------------------------- #


@server.group("disk", cls=ClickAliasedGroup)
@options(GLOBAL_OPTIONS[:2])
def disk():
    """Manage Cloud Server disks."""


# ------------------------------------------------------------- #
# $ twc server disk list                                        #
# ------------------------------------------------------------- #


def print_disks(response: object):
    disks = response.json()["server_disks"]
    table = fmt.Table()
    table.header(
        [
            "ID",
            "NAME",
            "MOUNTED",
            "SYSTEM",
            "TYPE",
            "STATUS",
            "SIZE",
            "USED",
        ]
    )
    for disk in disks:
        table.row(
            [
                disk["id"],
                disk["system_name"],
                disk["is_mounted"],
                disk["is_system"],
                disk["type"],
                disk["status"],
                str(round(disk["size"] / 1024)) + "G",
                str(round(disk["used"] / 1024, 1)) + "G",
            ]
        )
    table.print()


@disk.command("list", aliases=["ls"], help="List Cloud Server disks.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.argument("server_id", type=int, required=True)
def server_disk_list(config, profile, verbose, output_format, server_id):
    client = create_client(config, profile)
    response = _server_disk_list(client, server_id)
    fmt.printer(response, output_format=output_format, func=print_disks)


# ------------------------------------------------------------- #
# $ twc server disk list-all                                    #
# ------------------------------------------------------------- #


def print_all_disks(response: object):
    servers = response.json()["servers"]
    table = fmt.Table()
    table.header(
        [
            "SERVER",
            "DISK",
            "NAME",
            "MOUNTED",
            "SYSTEM",
            "TYPE",
            "STATUS",
            "SIZE",
            "USED",
        ]
    )
    for server in servers:
        for disk in server["disks"]:
            table.row(
                [
                    server["id"],
                    disk["id"],
                    disk["system_name"],
                    disk["is_mounted"],
                    disk["is_system"],
                    disk["type"],
                    disk["status"],
                    str(round(disk["size"] / 1024)) + "G",
                    str(round(disk["used"] / 1024, 1)) + "G",
                ]
            )
    table.print()


@disk.command("list-all", aliases=["la"], help="List disks from all servers.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option(
    "--limit",
    type=int,
    default=500,
    show_default=True,
    help="Items to display."
    " NOTE: This option affects on servers count, not disks.",
)
def server_disk_list_all(config, profile, verbose, output_format, limit):
    client = create_client(config, profile)
    response = _server_list(client, limit=limit)
    fmt.printer(response, output_format=output_format, func=print_all_disks)


# ------------------------------------------------------------- #
# $ twc server disk get                                         #
# ------------------------------------------------------------- #


def print_disk(response: object):
    disk = response.json()["server_disk"]
    table = fmt.Table()
    table.header(
        [
            "ID",
            "NAME",
            "MOUNTED",
            "SYSTEM",
            "TYPE",
            "STATUS",
            "SIZE",
            "USED",
        ]
    )
    table.row(
        [
            disk["id"],
            disk["system_name"],
            disk["is_mounted"],
            disk["is_system"],
            disk["type"],
            disk["status"],
            str(round(disk["size"] / 1024)) + "G",
            str(round(disk["used"] / 1024, 1)) + "G",
        ]
    )
    table.print()


def get_server_id_by_disk_id(client, disk_id: int) -> int:
    debug("Looking for server_id by disk_id...")
    server_id = None
    servers = _server_list(client, limit=10000).json()["servers"]
    for server in servers:
        for disk in server["disks"]:
            if int(disk_id) == disk["id"]:
                server_id = server["id"]
    return server_id


@disk.command("get", help="Get Cloud Server disk.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.argument("disk_id", type=int, required=True)
def server_disk_get(config, profile, verbose, output_format, disk_id):
    client = create_client(config, profile)
    server_id = get_server_id_by_disk_id(client, disk_id)
    if not server_id:
        sys.exit(f"Error: Disk {disk_id} not found.")
    response = _server_disk_get(client, server_id, disk_id)
    fmt.printer(response, output_format=output_format, func=print_disk)


# ------------------------------------------------------------- #
# $ twc server disk add                                         #
# ------------------------------------------------------------- #


@disk.command("add", help="Add disk to Cloud Server.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option("--size", required=True, help="Disk size e.g. 50G.")
@click.option(
    "--to-server",
    "server_id",
    type=int,
    metavar="SERVER_ID",
    required=True,
    help="Cloud Server ID.",
)
def server_disk_add(config, profile, verbose, output_format, size, server_id):
    client = create_client(config, profile)
    if check_value(size_to_mb(size), minv=5120, maxv=512000, step=5120):
        response = _server_disk_add(client, server_id, size=size_to_mb(size))
    else:
        raise click.BadParameter(
            "Value must be in range 5120-512000M with step 5120."
        )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: click.echo(response.json()["server_disk"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc server disk remove                                      #
# ------------------------------------------------------------- #


@disk.command("remove", aliases=["rm"], help="Remove disks.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.confirmation_option(prompt="This action cannot be undone, continue?")
@click.argument("disk_ids", nargs=-1, type=int, required=True)
def server_disk_remove(config, profile, verbose, output_format, disk_ids):
    client = create_client(config, profile)
    for disk_id in disk_ids:
        server_id = get_server_id_by_disk_id(client, disk_id)
        response = _server_disk_remove(client, server_id, disk_id)
        if response.status_code == 204:
            click.echo(disk_id)
        else:
            fmt.printer(response)


# ------------------------------------------------------------- #
# $ twc server disk resize                                      #
# ------------------------------------------------------------- #


@disk.command("resize", help="Change disk size (only increase).")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option("--size", required=True, help="Disk size e.g. 50G.")
@click.argument("disk_id", type=int, required=True)
def server_disk_resize(config, profile, verbose, output_format, size, disk_id):
    client = create_client(config, profile)
    server_id = get_server_id_by_disk_id(client, disk_id)
    if check_value(size_to_mb(size), minv=5120, maxv=512000, step=5120):
        response = _server_disk_resize(
            client, server_id, disk_id, size=size_to_mb(size)
        )
    else:
        raise click.BadParameter(
            "Value must be in range 5120-512000M with step 5120."
        )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: click.echo(response.json()["server_disk"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc server disk auto-backup                                 #
# ------------------------------------------------------------- #


def print_autobackup_settings(response: object):
    table = fmt.Table()
    settings = response.json()["auto_backups_settings"]
    translated_keys = {
        "copy_count": "Keep copies",
        "creation_start_at": "Backup start date",
        "is_enabled": "Enabled",
        "interval": "Interval",
        "day_of_week": "Day of week",
    }
    for key in settings.keys():
        table.row([translated_keys[key], ":", settings[key]])
    table.print()


@disk.command("auto-backup", help="Manage disk automatic backups settings.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option(
    "--status", is_flag=True, help="Display automatic backups status."
)
@click.option(
    "--enable/--disable",
    default=False,
    show_default=True,
    help="Enable backups.",
)
@click.option(
    "--keep",
    type=int,
    default=1,
    show_default=True,
    help="Number of backups to keep.",
)
@click.option(
    "--start-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=datetime.date.today().strftime("%Y-%m-%d"),
    help="Start date of the first backup creation. [default: today]",
)
@click.option(
    "--interval",
    type=click.Choice(["day", "week", "month"]),
    default="day",
    show_default=True,
    help="Backup interval.",
)
@click.option(
    "--day-of-week",
    type=click.IntRange(min=1, max=7),
    help="The day of the week on which backups will be created."
    " NOTE: This option works only with interval 'week'.",
)
@click.argument("disk_id", type=int, required=True)
def server_disk_autobackup(
    config,
    profile,
    verbose,
    output_format,
    status,
    enable,
    keep,
    start_date,
    interval,
    day_of_week,
    disk_id,
):
    client = create_client(config, profile)
    server_id = get_server_id_by_disk_id(client, disk_id)

    if status:
        response = _server_disk_autobackup_status(client, server_id, disk_id)
        fmt.printer(
            response,
            output_format=output_format,
            func=print_autobackup_settings,
        )
        if response.json()["auto_backups_settings"]["is_enabled"]:
            sys.exit(0)
        else:
            sys.exit(1)

    start_date = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    response = _server_disk_autobackup_update(
        client,
        server_id,
        disk_id,
        is_enabled=enable,
        copy_count=keep,
        creation_start_at=start_date,
        interval=interval,
        day_of_week=day_of_week,
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=print_autobackup_settings,
    )


# ------------------------------------------------------------- #
# $ twc server backup                                           #
# ------------------------------------------------------------- #


@server.group("backup", cls=ClickAliasedGroup)
@options(GLOBAL_OPTIONS[:2])
def backup():
    """Manage Cloud Server disk backups."""


# ------------------------------------------------------------- #
# $ twc server backup list                                      #
# ------------------------------------------------------------- #


def print_backups(response: object):
    backups = response.json()["backups"]
    table = fmt.Table()
    table.header(
        [
            "ID",
            "DISK",
            "STATUS",
            "CREATED",
            "SIZE",
            "TYPE",
            "COMMENT",
        ]
    )
    for backup in backups:
        table.row(
            [
                backup["id"],
                backup["name"],
                backup["status"],
                backup["created_at"],
                str(round(backup["size"] / 1024)) + "G",
                backup["type"],
                backup["comment"],
            ]
        )
    table.print()


@backup.command("list", aliases=["ls"], help="List backups by disk_id.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.argument("disk_id", type=int, required=True)
def server_backup_list(config, profile, verbose, output_format, disk_id):
    client = create_client(config, profile)
    server_id = get_server_id_by_disk_id(client, disk_id)
    response = _server_backup_list(client, server_id, disk_id)
    fmt.printer(response, output_format=output_format, func=print_backups)


# ------------------------------------------------------------- #
# $ twc server backup get                                       #
# ------------------------------------------------------------- #


def print_backup(response: object):
    backup = response.json()["backup"]
    table = fmt.Table()
    table.header(
        [
            "ID",
            "DISK",
            "STATUS",
            "CREATED",
            "SIZE",
            "TYPE",
            "COMMENT",
        ]
    )
    table.row(
        [
            backup["id"],
            backup["name"],
            backup["status"],
            backup["created_at"],
            str(round(backup["size"] / 1024)) + "G",
            backup["type"],
            backup["comment"],
        ]
    )
    table.print()


@backup.command("get", help="Get backup.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.argument("disk_id", type=int, required=True)
@click.argument("backup_id", type=int, required=True)
def server_backup_get(
    config, profile, verbose, output_format, disk_id, backup_id
):
    client = create_client(config, profile)
    server_id = get_server_id_by_disk_id(client, disk_id)
    response = _server_backup_get(client, server_id, disk_id, backup_id)
    fmt.printer(response, output_format=output_format, func=print_backup)


# ------------------------------------------------------------- #
# $ twc server backup create                                    #
# ------------------------------------------------------------- #


@backup.command("create", help="Create disk backup.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option("--comment", type=str, default=None, help="Comment.")
@click.argument("disk_id", type=int, required=True)
def server_backup_create(
    config, profile, verbose, output_format, comment, disk_id
):
    client = create_client(config, profile)
    server_id = get_server_id_by_disk_id(client, disk_id)
    response = _server_backup_create(
        client, server_id, disk_id, comment=comment
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: click.echo(response.json()["backup"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc server backup set-property                              #
# ------------------------------------------------------------- #


@backup.command("set-property", help="Change backup properties.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option("--comment", type=str, default=None, help="Comment.")
@click.argument("disk_id", type=int, required=True)
@click.argument("backup_id", type=int, required=True)
def server_backup_set_property(
    config, profile, verbose, output_format, comment, disk_id, backup_id
):
    client = create_client(config, profile)
    server_id = get_server_id_by_disk_id(client, disk_id)
    response = _server_backup_set_property(
        client, server_id, disk_id, backup_id, comment=comment
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: click.echo(response.json()["backup"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc server backup remove                                    #
# ------------------------------------------------------------- #


@backup.command("remove", aliases=["rm"], help="Remove backup.")
@options(GLOBAL_OPTIONS)
@click.argument("disk_id", type=int, required=True)
@click.argument("backup_id", nargs=-1, type=int, required=True)
@click.confirmation_option(
    prompt="This action cannot be undone. Are you sure?"
)
def server_backup_remove(config, profile, verbose, disk_id, backup_id):
    client = create_client(config, profile)
    server_id = get_server_id_by_disk_id(client, disk_id)
    for backup in backup_id:
        response = _server_backup_remove(client, server_id, disk_id, backup)
        if response.status_code == 204:
            click.echo(server_id)
        else:
            fmt.printer(response)


# ------------------------------------------------------------- #
# $ twc server backup restore                                   #
# ------------------------------------------------------------- #


@backup.command("restore", help="Restore backup.")
@options(GLOBAL_OPTIONS)
@click.argument("disk_id", type=int, required=True)
@click.argument("backup_id", type=int, required=True)
@click.confirmation_option(prompt="Data on target disk will lost. Continue?")
def server_backup_restore(config, profile, verbose, disk_id, backup_id):
    client = create_client(config, profile)
    server_id = get_server_id_by_disk_id(client, disk_id)
    response = _server_backup_do_action(
        client, server_id, disk_id, backup_id, action="restore"
    )
    if response.status_code == 204:
        click.echo(server_id)
    else:
        fmt.printer(response)


# ------------------------------------------------------------- #
# $ twc server backup mount                                     #
# ------------------------------------------------------------- #


@backup.command("mount", help="Attach backup as external drive.")
@options(GLOBAL_OPTIONS)
@click.argument("disk_id", type=int, required=True)
@click.argument("backup_id", type=int, required=True)
def server_backup_mount(config, profile, verbose, disk_id, backup_id):
    client = create_client(config, profile)
    server_id = get_server_id_by_disk_id(client, disk_id)
    response = _server_backup_do_action(
        client, server_id, disk_id, backup_id, action="mount"
    )
    if response.status_code == 204:
        click.echo(server_id)
    else:
        fmt.printer(response)


# ------------------------------------------------------------- #
# $ twc server backup unmount                                   #
# ------------------------------------------------------------- #


@backup.command("unmount", help="Detach backup from Cloud Server.")
@options(GLOBAL_OPTIONS)
@click.argument("disk_id", type=int, required=True)
@click.argument("backup_id", type=int, required=True)
def server_backup_unmount(config, profile, verbose, disk_id, backup_id):
    client = create_client(config, profile)
    server_id = get_server_id_by_disk_id(client, disk_id)
    response = _server_backup_do_action(
        client, server_id, disk_id, backup_id, action="unmount"
    )
    if response.status_code == 204:
        click.echo(server_id)
    else:
        fmt.printer(response)
