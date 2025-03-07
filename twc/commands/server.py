"""Manage Cloud Servers."""

import re
import sys
import webbrowser
from enum import Enum
from logging import debug
from typing import Optional, List, Union
from pathlib import Path
from datetime import date, datetime
from ipaddress import IPv4Address, IPv6Address, IPv4Network

import typer
from click import UsageError
from requests import Response

from twc import fmt
from twc.typerx import TyperAlias
from twc.apiwrap import create_client
from twc.api import (
    TimewebCloud,
    ServerAction,
    ServiceRegion,
    ServerLogOrder,
    ServerBootMode,
    ServerNATMode,
    IPVersion,
    BackupInterval,
    BackupAction,
)
from twc.vars import (
    REGIONS_WITH_IPV6,
    CONTROL_PANEL_URL,
)
from .common import (
    verbose_option,
    config_option,
    profile_option,
    filter_option,
    yes_option,
    output_format_option,
    region_option,
    zone_option,
    load_from_config_callback,
)


server = TyperAlias(help=__doc__)
server_ip = TyperAlias(help="Manage public IPs.")
server_disk = TyperAlias(help="Manage Cloud Server disks.")
server_backup = TyperAlias(help="Manage Cloud Server disk backups.")
server.add_typer(server_ip, name="ip", deprecated=True)
server.add_typer(server_disk, name="disk")
server.add_typer(server_backup, name="backup")


# ------------------------------------------------------------- #
# $ twc server list                                             #
# ------------------------------------------------------------- #


def print_servers(
    response: Response, filters: Optional[str], ids: bool = False
):
    """Print table with Cloud Servers list."""
    servers = response.json()["servers"]
    if filters:
        servers = fmt.filter_list(servers, filters)
    if ids:
        for srv in servers:
            print(srv["id"])
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
    for srv in servers:
        main_ipv4 = None
        for network in srv["networks"]:
            if network["type"] == "public":
                for addr in network["ips"]:
                    if addr["type"] == "ipv4" and addr["is_main"]:
                        main_ipv4 = addr["ip"]
        table.row(
            [
                srv["id"],
                srv["name"],
                srv["location"],
                srv["status"],
                main_ipv4,
            ]
        )
    table.print()


@server.command("list", "ls")
def server_list(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
    limit: int = typer.Option(500, help="Items to display."),
    ids: bool = typer.Option(False, help="Print only server IDs."),
):
    """List Cloud Servers."""
    client = create_client(config, profile)
    response = client.get_servers(limit=limit)
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


def print_server(response: Response):
    """Print table with Cloud Server info."""
    srv = response.json()["server"]
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
    main_ipv4 = None
    for network in srv["networks"]:
        if network["type"] == "public":
            for addr in network["ips"]:
                if addr["type"] == "ipv4" and addr["is_main"]:
                    main_ipv4 = addr["ip"]
    table.row(
        [
            srv["id"],
            srv["name"],
            srv["location"],
            srv["status"],
            main_ipv4,
        ]
    )
    table.print()


def print_server_networks(response: Response):
    """Print information about networks (public and private)."""
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
            for addr in network["ips"]:
                table.row(
                    [
                        network["type"],
                        addr["ip"],
                        addr["type"],
                        addr["ptr"],
                        addr["is_main"],
                    ]
                )
            table.print()
        else:
            table = fmt.Table()
            for addr in network["ips"]:
                table.row([network["type"], addr["ip"], addr["type"]])
            table.print()


def print_server_disks(response: Response):
    """Print table with server disks."""
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


@server.command("get")
def server_get(
    server_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    status: bool = typer.Option(
        False,
        "--status",
        help="Display status and exit with 0 if status is 'on'.",
    ),
    networks: bool = typer.Option(
        False, "--networks", help="Display networks."
    ),
    disks: bool = typer.Option(False, "--disks", help="Display disks."),
):
    """Get Cloud Server info."""
    client = create_client(config, profile)
    response = client.get_server(server_id)
    if status:
        state = response.json()["server"]["status"]
        if state == "on":
            print(state)
            raise typer.Exit()
        sys.exit(state)
    if networks:
        print_server_networks(response)
        raise typer.Exit()
    if disks:
        print_server_disks(response)
        raise typer.Exit()
    fmt.printer(response, output_format=output_format, func=print_server)


# ------------------------------------------------------------- #
# $ twc server create                                           #
# ------------------------------------------------------------- #


def size_to_mb(size: str) -> int:
    """Transform string like '5G' into integer in megabytes.
    Case insensitive. NOTE: This function does not support floats e.g. 1.5T.
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


def validate_cpu(req: dict, value: int) -> int:
    """Return valid cpu value or exit."""
    minv = req["cpu_min"]
    maxv = req["cpu_max"]
    step = req["cpu_step"]
    if check_value(value, minv, maxv, step):
        return value
    sys.exit(
        "Error: Too many or too few vCPUs. Required: "
        + f"min {minv}, max {maxv} with step {step}."
    )


def validate_ram(req: dict, value: int) -> int:
    """Return valid RAM value in megabytes or exit."""
    minv = req["ram_min"]
    maxv = req["ram_max"]
    step = req["ram_step"]
    if check_value(value, minv, maxv, step):
        return value
    sys.exit(
        "Error: Too large or too small RAM size. Required: "
        + f"min {round(minv/1024)}G, "
        + f"max {round(maxv/1024)}G "
        + f"with step {round(step/1024)}G."
    )


def validate_disk(req: dict, value: int) -> int:
    """Return valid disk value in megabytes or exit."""
    minv = req["disk_min"]
    maxv = req["disk_max"]
    step = req["disk_step"]
    if check_value(value, minv, maxv, step):
        return value
    sys.exit(
        "Error: Too large or too small disk size. Required: "
        + f"min {round(minv/1024)}G, "
        + f"max {round(maxv/1024/1024)}T "
        + f"with step {round(step/1024)}G."
    )


def validate_bandwidth(req: dict, value: int) -> int:
    """Return valid bandwidth value in megabytes or exit."""
    minv = req["network_bandwidth_min"]
    maxv = req["network_bandwidth_max"]
    step = req["network_bandwidth_step"]
    if check_value(value, minv, maxv, step):
        return value
    sys.exit(
        "Error: Too large or too small bandwidth value. Required: "
        + f"min {minv}, max {maxv} with step {step}."
    )


def get_requirements(client: TimewebCloud, configurator_id: int) -> dict:
    """Return configurator requirements."""
    debug(f"Get requirements for configurator_id: {configurator_id}")
    configurators = client.get_server_configurators().json()
    for configurator in configurators["server_configurators"]:
        if configurator["id"] == configurator_id:
            return configurator["requirements"]
    return None


def bandwidth_callback(value: int) -> int:
    """Return valid bandwidth value or exit. See "Callback for Validation"
    at https://click.palletsprojects.com/en/8.1.x/options
    """
    if not value:
        return None
    if check_value(value, minv=100, maxv=1000, step=100):
        return value
    sys.exit(
        "Error: '--bandwidth' value must be in range 100-1000 with step 100."
    )


def set_bandwidth_from_preset(client: TimewebCloud, preset_id: int) -> int:
    """Return bandwidth value from preset."""
    debug(f"Set network bandwidth from preset_id: {preset_id}")
    presets = client.get_server_presets().json()["server_presets"]
    return [p for p in presets if p["id"] == preset_id][0]["bandwidth"]


def get_os_id_by_name(client: TimewebCloud, os_name: str) -> int:
    """Return OS image ID by name. For example::

    ubuntu-22.04 -> 79
    windows-2012-standard -> 65
    """
    # pylint: disable=invalid-name
    os_images = client.get_server_os_images().json()["servers_os"]
    # Lookup for Windows
    if os_name.startswith("windows-"):
        name, version, codename = os_name.split("-")
        for os in os_images:
            if (
                os["name"] == name
                and os["version"] == version
                and os["version_codename"] == codename
            ):
                return os["id"]
    # Lookup for Linux
    if len(os_name.split("-")) > 2:  # OS must have only name and version
        return None
    name, version = os_name.split("-")
    for os in os_images:
        if os["name"] == name and os["version"] == version:
            return os["id"]
    return None


def get_image(client: TimewebCloud, image: str) -> tuple:
    """Return tuple(os_id, image_id) or exit."""
    if image.isdigit():
        # 'image' is os_id. Not guarantied to correct, API will return error.
        return int(image), None
    if re.match(r"^[a-z]+-[0-9.]+(-[a-z_]+)?$", image, re.I):
        # 'image' is OS name in 'name-version[-codename]' notation.
        os_id = get_os_id_by_name(client, image)
        if os_id:
            return os_id, None
    if image in [
        img["id"] for img in client.get_images(limit=1000).json()["images"]
    ]:
        # 'image' is user image UUID.
        return None, image
    sys.exit(f"Error: Wrong OS ID, OS name or image UUID: '{image}'")


def process_ssh_key(client: TimewebCloud, ssh_key: str) -> int:
    """Upload SSH key (if needed) and return SSH key ID or exit."""
    uploaded_ssh_keys = client.get_ssh_keys().json()["ssh_keys"]
    # Add from filesystem
    if Path(ssh_key).exists():
        ssh_key_name = Path(ssh_key).name
        try:
            with open(ssh_key, "r", encoding="utf-8") as pubkey:
                ssh_key_body = pubkey.read().strip()
        except (OSError, IOError, FileNotFoundError) as error:
            sys.exit(f"Error: Cannot read SSH-key: {error}")
        for uploaded_key in uploaded_ssh_keys:
            # Do not reupload already uploaded SSH-key
            if ssh_key_body == uploaded_key["body"]:
                debug(
                    f"SSH-Key '{ssh_key_name}' already exists,"
                    f" ID {uploaded_key['id']} is used."
                )
                return uploaded_key["id"]
        # Upload new SSH-key
        debug(f"Upload new SSH-key '{ssh_key_name}'...")
        return client.add_new_ssh_key(
            name=ssh_key_name, body=ssh_key_body
        ).json()["ssh_key"]["id"]
    # Add by ID
    if ssh_key.isdigit():
        if int(ssh_key) in [key["id"] for key in uploaded_ssh_keys]:
            debug(f"SSH-key to add: ID: {ssh_key}")
            return int(ssh_key)
        sys.exit(f"Error: SSH-key with ID '{ssh_key}' not found.")
    # Add by name. IT IS AMBIGIOUS!
    for uploaded_key in uploaded_ssh_keys:
        if ssh_key == uploaded_key["name"]:
            debug(
                f"SSH-key to add by name: {ssh_key} ID: {uploaded_key['id']}"
            )
            return uploaded_key["id"]
    # Exit on failure
    sys.exit(f"Error: SSH-key '{ssh_key}' not found.")


def select_configurator(client: TimewebCloud, kind: str, region: str) -> int:
    """Find and return configurator_id by location name."""
    kind = kind.replace("-", "_")
    configurators_by_type = client.get_server_preset_types().json()[
        "configurators"
    ]
    available_configurators = configurators_by_type.get(kind, None)
    if not available_configurators:
        sys.exit(
            f"Error: Unable to select server configurator_id: no configurators with type '{kind}'"
        )
    for configurator in available_configurators:
        if configurator["location"] == region:
            return configurator["id"]
    sys.exit(
        f"Error: Unable to select configurator_id: no configurators for region {region}"
    )


class InstanceKind(str, Enum):
    """Instance types used to select configurator."""

    STANDARD = "standard"
    PREMIUM = "premium"
    DEDICATED_CPU = "dedicated-cpu"


@server.command("create")
def server_create(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    name: str = typer.Option(..., help="Cloud Server display name."),
    comment: str = typer.Option(None, help="Comment."),
    avatar_id: str = typer.Option(None, help="Avatar ID."),
    image: str = typer.Option(..., help="OS ID, OS name or image UUID."),
    preset_id: int = typer.Option(
        None,
        help="Cloud Server configuration preset ID. "
        "NOTE: This argument is mutually exclusive with arguments: "
        "['--cpu', '--ram', '--disk', '--gpu'].",
    ),
    configurator_id: int = typer.Option(
        None, help="ID of configuration constraints set."
    ),
    instance_kind: Optional[InstanceKind] = typer.Option(
        InstanceKind.PREMIUM,
        "--type",
        help="Cloud Server type. "
        "Servers with GPU always is 'premium'. "
        "This option will be ignored if '--gpu' or '--preset-id' is set.",
    ),
    cpu: int = typer.Option(None, help="Number of vCPUs."),
    ram: str = typer.Option(
        None, metavar="SIZE", help="RAM size, e.g. 1024M, 1G."
    ),
    disk: str = typer.Option(
        None, metavar="SIZE", help="System disk size, e.g. 10240M, 10G."
    ),
    gpus: Optional[int] = typer.Option(None, min=0, max=4, hidden=True),
    gpu: Optional[int] = typer.Option(
        None,
        min=0,
        max=4,
        help="Number of GPUs to attach.",
    ),
    bandwidth: int = typer.Option(
        None, callback=bandwidth_callback, help="Network bandwidth."
    ),
    software_id: int = typer.Option(None, help="Software ID to install."),
    ssh_keys: Optional[List[str]] = typer.Option(
        None, "--ssh-key", help="SSH-key file, name or ID. Can be multiple."
    ),
    user_data: Optional[typer.FileText] = typer.Option(
        None, help="user-data file for cloud-init."
    ),
    ddos_protection: bool = typer.Option(
        False,
        "--ddos-protection",
        show_default=True,
        help="Request public IPv4 with L3/L4 DDoS protection.",
    ),
    local_network: Optional[bool] = typer.Option(
        # is_local_network paramenter is deprecated!
        None,
        "--local-network",
        show_default=True,
        help="Enable LAN.",
        hidden=True,
    ),
    network: Optional[str] = typer.Option(None, help="Private network ID."),
    private_ip: Optional[str] = typer.Option(
        None, help="Private IPv4 address."
    ),
    public_ip: Optional[str] = typer.Option(
        None, help="Public IPv4 address. New address by default."
    ),
    no_public_ip: Optional[bool] = typer.Option(
        False, "--no-public-ip", help="Do not add public IPv4 address."
    ),
    nat_mode: ServerNATMode = typer.Option(
        None,
        "--nat-mode",
        metavar="MODE",
        help="Apply NAT mode.",
    ),
    region: Optional[str] = region_option,
    availability_zone: Optional[str] = zone_option,
    project_id: int = typer.Option(
        None,
        envvar="TWC_PROJECT",
        show_envvar=False,
        callback=load_from_config_callback,
        help="Add server to specific project.",
    ),
    disable_ssh_password_auth: Optional[bool] = typer.Option(
        False,
        "--disable-ssh-password-auth",
        help="Disable sshd password authentication.",
    ),
):
    """Create Cloud Server."""
    client = create_client(config, profile)
    payload = {
        "name": name,
        "comment": comment,
        "avatar_id": avatar_id,
        "software_id": software_id,
        "is_ddos_guard": ddos_protection,
        "availability_zone": availability_zone,
        "network": {},
    }

    if local_network is not None:
        print(
            "Option --local-network is deprecated and will be removed soon",
            file=sys.stderr,
        )
        payload["is_local_network"] = local_network

    if disable_ssh_password_auth:
        if not ssh_keys:
            print(
                "You applied --disable-ssh-password-auth, but no ssh keys is set. "
                "Pass keys to --ssh-key option or setup master ssh key.",
                file=sys.stderr,
            )
        payload["is_root_password_required"] = False

    instance_kind = instance_kind.value
    if gpus:
        gpu = gpus
    if gpu:
        instance_kind = "gpu"

    # Check availability zone
    usable_zones = ServiceRegion.get_zones(region)
    if availability_zone is not None and availability_zone not in usable_zones:
        sys.exit(
            f"Error: Wrong availability zone, usable zones are: {usable_zones}"
        )

    # Set network parameters
    if nat_mode or private_ip:
        if not network:
            sys.exit("Error: Pass '--network' option first.")
    if network:
        payload["network"]["id"] = network
        if private_ip:
            net = IPv4Network(
                client.get_vpc(network).json()["vpc"]["subnet_v4"]
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
        # New public IPv4 address will be automatically requested with
        # correct availability zone. This is an official dirty hack.
        if no_public_ip is False:
            payload["network"]["floating_ip"] = "create_ip"

    # Set server configuration parameters
    if preset_id and (cpu or ram or disk or gpu):
        raise UsageError(
            "'--preset-id' is mutually exclusive with: "
            + "['--cpu', '--ram', '--disk', '--gpu']."
        )
    if not preset_id and not (cpu or ram or disk):
        raise UsageError(
            "One of parameters is required: '--preset-id' or "
            + "['--cpu', '--ram', '--disk']."
        )
    if not preset_id:
        for param in ["cpu", "ram", "disk"]:
            if not locals()[param]:
                raise UsageError(f"Missing parameter: '--{param}'.")
        # Select configurator_id by region
        if not configurator_id:
            configurator_id = select_configurator(
                client, kind=instance_kind, region=region
            )
        requirements = get_requirements(client, configurator_id)
        payload["configuration"] = {
            "configurator_id": configurator_id,
            "cpu": validate_cpu(requirements, cpu),
            "ram": validate_ram(requirements, size_to_mb(ram)),
            "disk": validate_disk(requirements, size_to_mb(disk)),
        }
        if gpu:
            payload["configuration"]["gpu"] = gpu
        if bandwidth:
            payload["bandwidth"] = validate_bandwidth(requirements, bandwidth)
        else:
            payload["bandwidth"] = requirements["network_bandwidth_min"]
    else:
        payload["preset_id"] = preset_id
        if not bandwidth:
            payload["bandwidth"] = set_bandwidth_from_preset(client, preset_id)

    # Set server operating system
    os_id, image_id = get_image(client, image)
    if os_id:
        payload["os_id"] = os_id
    else:
        payload["image_id"] = image_id

    # Upload / add SSH-keys
    ssh_keys_ids = []
    if ssh_keys:
        for key in ssh_keys:
            ssh_keys_ids.append(process_ssh_key(client, key))
    payload["ssh_keys_ids"] = ssh_keys_ids

    # Set cloud-init user-data
    if user_data:
        payload["cloud_init"] = user_data.read()

    if project_id:
        payload["project_id"] = project_id

    # Create Cloud Server
    debug("Create Cloud Server...")
    response = client.create_server(**payload)

    if nat_mode:
        debug(f"Set NAT mode to '{nat_mode}'")
        client.set_server_nat_mode(
            response.json()["server"]["id"], nat_mode=nat_mode
        )

    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["server"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc server set                                              #
# ------------------------------------------------------------- #


@server.command("set")
def server_set(
    server_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    name: str = typer.Option(None, help="Cloud Server display name."),
    comment: str = typer.Option(None, help="Comment."),
    avatar_id: str = typer.Option(None, help="Avatar ID."),
):
    """Set Cloud Server properties."""
    if not name and not comment and not avatar_id:
        raise UsageError(
            "Nothing to do. Set one of options: "
            "['--name', '--comment', '--avatar-id']"
        )

    client = create_client(config, profile)
    response = client.update_server(
        server_id,
        name=name,
        comment=comment,
        avatar_id=avatar_id,
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["server"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc server resize                                           #
# ------------------------------------------------------------- #


@server.command("resize")
def server_resize(
    server_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    preset_id: int = typer.Option(
        None,
        help="Cloud Server configuration preset ID. "
        "NOTE: This argument is mutually exclusive with arguments: "
        "['--cpu', '--ram', '--disk'].",
    ),
    cpu: int = typer.Option(None, help="Number of vCPUs."),
    ram: str = typer.Option(
        None, metavar="SIZE", help="RAM size, e.g. 1024M, 1G."
    ),
    disk: str = typer.Option(
        None, metavar="SIZE", help="System disk size, e.g. 10240M, 10G."
    ),
    bandwidth: int = typer.Option(
        None, callback=bandwidth_callback, help="Network bandwidth."
    ),
    yes: Optional[bool] = yes_option,
):
    """Update vCPUs number, RAM, disk and bandwidth."""
    client = create_client(config, profile)
    payload = {}

    # Save original server state
    debug("Get server original state...")
    old_state = client.get_server(server_id).json()["server"]

    # Get original server preset tags
    old_preset_tags = []
    if old_state["preset_id"]:
        debug(f"Get preset tags by preset_id {old_state['preset_id']}...")
        presets = client.get_server_presets().json()["server_presets"]
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
        # Get original server configurator_id
        configurator_id = old_state["configurator_id"]
        configurator = None

        # Get configurator_id if user tries to switch from preset to
        # configurator. Don't ask what is this.
        debug("Get configurator_id...")
        if not configurator_id:
            configurator_id = select_configurator(
                client,
                region=old_state["location"],
                kind="premium",
            )

        # Get configurator by configurator_id
        debug(f"configurator_id is {configurator_id}, get confugurator...")
        configurators = client.get_server_configurators().json()
        for item in configurators["server_configurators"]:
            if item["id"] == configurator_id:
                configurator = item  # <-- this!

        # Check configurator and return error if configurator is unavailable
        debug(f"Configurator: {configurator}")
        if configurator_id and not configurator:
            sys.exit(
                "Error: Configurator is not available for your server. "
                + "Try to create new server."
            )

        # Add configuration key to payload
        payload["configuration"] = {}

        # Get original size of primary disk
        primary_disk_size = 0
        for old_disk in old_state["disks"]:
            if old_disk["is_system"]:  # is True
                primary_disk_size = old_disk["size"]

        # Fill payload with original server specs
        payload["configuration"].update(
            {
                "configurator_id": configurator_id,
                "cpu": old_state["cpu"],
                "ram": old_state["ram"],
                "disk": primary_disk_size,
            }
        )

        # Refill payload with parameters from command line
        requirements = configurator["requirements"]

        if cpu:
            payload["configuration"].update(
                {"cpu": validate_cpu(requirements, cpu)}
            )

        if ram:
            payload["configuration"].update(
                {"ram": validate_ram(requirements, size_to_mb(ram))}
            )

        if disk:
            payload["configuration"].update(
                {"disk": validate_disk(requirements, size_to_mb(disk))}
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

        presets = client.get_server_presets().json()["server_presets"]
        for preset in presets:
            if preset["id"] == preset_id:
                if not preset["location"] == old_state["location"]:
                    sys.exit(
                        f"Error: Preset location '{preset['location']}'"
                        " does not match with server location "
                        f"'{old_state['location']}'."
                    )
                payload["preset_id"] = preset_id
        try:
            payload["preset_id"]
        except KeyError:
            sys.exit(f"Error: Invalid preset_id '{preset_id}'")

    # Prompt if no option --yes passed
    if not yes:
        if not typer.confirm("Server will restart. Continue?", default=False):
            sys.exit("Aborted!")

    # Make request
    response = client.update_server(server_id, **payload)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["server"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc server reinstall                                        #
# ------------------------------------------------------------- #


def get_ssh_keys_by_server_id(client: TimewebCloud, server_id: int) -> list:
    """Return list of SSH-keys added to the server server_id."""
    ssh_keys = client.get_ssh_keys().json()["ssh_keys"]
    ssh_keys_list = []
    for pubkey in ssh_keys:
        for _server in pubkey["used_by"]:
            if _server["id"] == server_id:
                ssh_keys_list.append(pubkey["id"])
    return ssh_keys_list


@server.command("reinstall")
def server_reinstall(
    server_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    image: str = typer.Option(None, help="OS ID, OS name or image UUID."),
    software_id: int = typer.Option(None, help="Software ID to install."),
    add_ssh_keys: bool = typer.Option(
        True,
        "--add-ssh-keys",
        show_default=True,
        help="Readd SSH-keys to reinstalled server.",
    ),
    yes: Optional[bool] = yes_option,
):
    """Reinstall OS or software."""
    if not yes:
        typer.confirm(
            "All data on Cloud Server will be lost.\n"
            "This action cannot be undone. Continue?",
            abort=True,
        )

    client = create_client(config, profile)
    payload = {}

    if image:
        os_id, image_id = get_image(client, image)
        if os_id:
            payload["os_id"] = os_id
        else:
            payload["image_id"] = image_id
    else:
        old_state = client.get_server(server_id).json()["server"]
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
    response = client.update_server(server_id, **payload)

    if add_ssh_keys and ssh_keys:
        debug(f"Readding SSH-keys {ssh_keys} to server '{server_id}'")
        client.add_ssh_key_to_server(server_id, ssh_keys_ids=ssh_keys)

    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["server"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc server clone                                            #
# ------------------------------------------------------------- #


@server.command("clone")
def server_clone(
    server_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """Clone Cloud Server."""
    client = create_client(config, profile)
    response = client.clone_server(server_id)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["server"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc server remove                                           #
# ------------------------------------------------------------- #


@server.command("remove", "rm")
def server_remove(
    server_ids: List[int] = typer.Argument(..., metavar="SERVER_ID..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
    keep_public_ip: Optional[bool] = typer.Option(
        False,
        "--keep-public-ip",
        help="Do not remove public IP attached to server. [default: false]",
    ),
):
    """Remove Cloud Server."""
    if not yes:
        typer.confirm("This action cannot be undone. Continue?", abort=True)

    client = create_client(config, profile)
    for server_id in server_ids:
        server_data = client.get_server(server_id).json()["server"]
        response = client.delete_server(server_id)
        if response.status_code == 200:
            del_hash = response.json()["server_delete"]["hash"]
            del_code = typer.prompt("Please enter confirmation code", type=int)
            response = client.delete_server(
                server_id, delete_hash=del_hash, code=del_code
            )
        if response.status_code == 204:
            print(server_id)
        else:
            sys.exit(fmt.printer(response))
        if keep_public_ip is False:
            for network in server_data["networks"]:
                for ip in network["ips"]:
                    if ip.get("id") is not None:
                        client.delete_floating_ip(ip["id"])


# ------------------------------------------------------------- #
# $ twc server <action>                                         #
# boot, reboot, shutdown, reset-root-password                   #
# ------------------------------------------------------------- #

# ------------------------------------------------------------- #
# $ twc server boot                                             #
# ------------------------------------------------------------- #


@server.command("boot", "start")
def server_start(
    server_ids: List[int] = typer.Argument(..., metavar="SERVER_ID..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
):
    """Boot Cloud Server."""
    client = create_client(config, profile)
    for server_id in server_ids:
        response = client.do_action_with_server(
            server_id, action=ServerAction.START
        )
        if response.status_code == 204:
            print(server_id)
        else:
            sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc server reboot                                           #
# ------------------------------------------------------------- #


@server.command("reboot", "restart")
def server_reboot(
    server_ids: List[int] = typer.Argument(..., metavar="SERVER_ID..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    hard_reboot: bool = typer.Option(False, "--hard", help="Do hard reboot."),
):
    """Reboot Cloud Server."""
    if hard_reboot:
        action = ServerAction.HARD_REBOOT
    else:
        action = ServerAction.REBOOT

    client = create_client(config, profile)
    for server_id in server_ids:
        response = client.do_action_with_server(server_id, action=action)
        if response.status_code == 204:
            print(server_id)
        else:
            sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc server shutdown                                         #
# ------------------------------------------------------------- #


@server.command("shutdown", "stop")
def server_shutdown(
    server_ids: List[int] = typer.Argument(..., metavar="SERVER_ID..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    hard_shutdown: bool = typer.Option(
        False, "--hard", help="Do hard shutdown."
    ),
):
    """Shutdown Cloud Server."""
    if hard_shutdown:
        action = ServerAction.HARD_SHUTDOWN
    else:
        action = ServerAction.SHUTDOWN

    client = create_client(config, profile)
    for server_id in server_ids:
        response = client.do_action_with_server(server_id, action=action)
        if response.status_code == 204:
            print(server_id)
        else:
            sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc server reset-root-password                              #
# ------------------------------------------------------------- #


@server.command("reset-root-password")
def server_reset_root(
    server_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
):
    """Reset root user password."""
    if not yes:
        typer.confirm(
            "New password will sent to your contact email. Continue?",
            abort=True,
        )
    client = create_client(config, profile)
    response = client.do_action_with_server(
        server_id,
        action=ServerAction.RESET_PASSWORD,
    )
    if response.status_code == 204:
        print(server_id)
    else:
        sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc server list-presets                                     #
# ------------------------------------------------------------- #


def print_presets(response: Response, filters: Optional[str] = None):
    """Print table with server presets."""
    presets = response.json()["server_presets"]
    if filters:
        presets = fmt.filter_list(presets, filters)
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
            "TYPE",
            "BANDW",
            "LAN",
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
                preset["is_allowed_local_network"],
            ]
        )
    table.print()


@server.command("list-presets", "lp")
def server_list_presets(
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
    response = client.get_server_presets()
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_presets,
    )


# ------------------------------------------------------------- #
# $ twc server list-os-images                                   #
# ------------------------------------------------------------- #


def print_os_images(response: Response, filters: Optional[str] = None):
    """Print table with OS imagees list."""
    # pylint: disable=invalid-name
    os_list = response.json()["servers_os"]
    if filters:
        os_list = fmt.filter_list(os_list, filters)
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


@server.command("list-os-images", "li")
def server_list_os_images(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
):
    """List prebuilt operating system images."""
    client = create_client(config, profile)
    response = client.get_server_os_images()
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_os_images,
    )


# ------------------------------------------------------------- #
# $ twc server list-software                                    #
# ------------------------------------------------------------- #


def print_software(response: Response):
    """Print table with list of software."""
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


@server.command("list-software", "lsw")
def server_software(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """List software."""
    client = create_client(config, profile)
    response = client.get_server_software()
    fmt.printer(response, output_format=output_format, func=print_software)


# ------------------------------------------------------------- #
# $ twc server history                                          #
# ------------------------------------------------------------- #


def print_history(response: Response):
    """Print server events log."""
    log = response.json()["server_logs"]
    for line in log:
        print(f"{line['logged_at']} id={line['id']} event={line['event']}")


@server.command("history")
def server_history(
    server_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    limit: int = typer.Option(500, help="Items to display."),
    order: ServerLogOrder = typer.Option(
        ServerLogOrder.ASC.value,
        show_default=True,
        help="Sort log by datetime.",
    ),
):
    """View Cloud Server events log."""
    client = create_client(config, profile)
    response = client.get_server_logs(
        server_id=server_id, limit=limit, order=order
    )
    fmt.printer(response, output_format=output_format, func=print_history)


# ------------------------------------------------------------- #
# $ twc server set-boot-mode                                    #
# ------------------------------------------------------------- #


@server.command("set-boot-mode", help="Set Cloud Server boot mode.")
def server_set_boot_mode(
    server_ids: List[int] = typer.Argument(
        ..., metavar="SERVER_ID...", help="Cloud Server ID, Can be multiple."
    ),
    boot_mode: ServerBootMode = typer.Argument(
        ...,
        metavar="MODE",
        help=f"Boot mode: [{'|'.join(ServerBootMode)}]",
    ),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
):
    """Set Cloud Server boot mode."""
    if not yes:
        typer.confirm("Server will reboot. Continue?", abort=True)

    client = create_client(config, profile)
    for server_id in server_ids:
        response = client.set_server_boot_mode(server_id, boot_mode=boot_mode)
        if response.status_code == 204:
            print(server_id)
        else:
            sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc server set-nat-mode                                     #
# ------------------------------------------------------------- #


@server.command("set-nat-mode")
def server_set_nat_mode(
    server_ids: List[int] = typer.Argument(
        ..., metavar="SERVER_ID...", help="Cloud Server ID, can be multiple."
    ),
    nat_mode: ServerNATMode = typer.Argument(
        ...,
        metavar="MODE",
        help=f"NAT mode: [{'|'.join(ServerNATMode)}]",
    ),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
):
    """Set Cloud Server NAT mode."""
    client = create_client(config, profile)

    for server_id in server_ids:
        response = client.set_server_nat_mode(server_id, nat_mode=nat_mode)
        if response.status_code == 204:
            print(server_id)
        else:
            sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc server ip list                                          #
# ------------------------------------------------------------- #


def print_ips(response: Response):
    """Print table with public IPs."""
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


@server_ip.command("list", "ls")
def server_ip_list(
    server_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """List public IPs attached to Cloud Server."""
    client = create_client(config, profile)
    response = client.get_ips(server_id)
    fmt.printer(response, output_format=output_format, func=print_ips)


# ------------------------------------------------------------- #
# $ twc server ip add                                           #
# ------------------------------------------------------------- #


@server_ip.command("add")
def server_ip_add(
    server_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    ptr: Optional[str] = typer.Option(
        None,
        metavar="POINTER",
        help="IP address pointer (RDNS).",
    ),
    ipv: bool = typer.Option(True, "--ipv4/--ipv6", help="IP version."),
):
    """Attach new IP to Cloud Server."""
    client = create_client(config, profile)
    if not ipv:
        debug("Get Cloud Server location...")
        location = client.get_server(server_id).json()["server"]["location"]
        if location not in REGIONS_WITH_IPV6:
            sys.exit(f"Error: IPv6 is not available in location '{location}'.")
        ip_version = IPVersion.IPV6
    else:
        ip_version = IPVersion.IPV4

    response = client.add_ip(server_id, version=ip_version, ptr=ptr)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["server_ip"]["ip"]),
    )


# ------------------------------------------------------------- #
# $ twc server ip remove                                        #
# ------------------------------------------------------------- #


def get_server_id_by_ip(
    client: TimewebCloud,
    ip_address: Union[IPv4Address, IPv6Address],
) -> int:
    """Return server_id if IP address found or return None."""
    for _server in client.get_servers(limit=10000).json()["servers"]:
        for network in _server["networks"]:
            for ip_addr in network["ips"]:
                if ip_address == ip_addr["ip"]:
                    return _server["id"]
    return None


@server_ip.command("remove", "rm")
def server_ip_remove(
    ip_address: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
):
    """Remove IP address."""
    if not yes:
        typer.confirm("This action cannot be undone. Continue?", abort=True)

    client = create_client(config, profile)

    debug("Looking for IP address...")
    server_id = get_server_id_by_ip(client, ip_address)
    if not server_id:
        sys.exit(f"IP address '{ip_address}' not found.")

    debug("Check IP...")
    ips = client.get_ips(server_id).json()["server_ips"]
    for ip_addr in ips:
        if ip_addr["ip"] == ip_address and ip_addr["is_main"]:
            sys.exit("Error: Cannot remove Cloud Server primaty IP address.")

    response = client.delete_ip(server_id, ip_address)
    if response.status_code == 204:
        print(ip_address)
    else:
        sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc server ip set                                           #
# ------------------------------------------------------------- #


@server_ip.command("set")
def server_ip_set_ptr(
    ip_address: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    ptr: Optional[str] = typer.Option(
        None,
        metavar="POINTER",
        help="IP address pointer (RDNS).",
    ),
):
    """Set IP pointer (RDNS)."""
    client = create_client(config, profile)

    debug("Looking for IP address...")
    server_id = get_server_id_by_ip(client, ip_address)
    if not server_id:
        sys.exit(f"IP address '{ip_address}' not found.")

    response = client.update_ip(server_id, ip=ip_address, ptr=ptr)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["server_ip"]["ip"]),
    )


# ------------------------------------------------------------- #
# $ twc server disk list                                        #
# ------------------------------------------------------------- #


def print_disks(response: Response):
    """Print table with disks list."""
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


@server_disk.command("list", "ls")
def server_disk_list(
    server_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """List Cloud Server disks."""
    client = create_client(config, profile)
    response = client.get_disks(server_id)
    fmt.printer(response, output_format=output_format, func=print_disks)


# ------------------------------------------------------------- #
# $ twc server disk get                                         #
# ------------------------------------------------------------- #


def print_disk(response: Response):
    """Print table with disk info."""
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


def get_server_id_by_disk_id(client: TimewebCloud, disk_id: int) -> int:
    """Find server_id by disk_id and return server_id."""
    debug("Looking for server_id by disk_id...")
    for _server in client.get_servers(limit=10000).json()["servers"]:
        for disk in _server["disks"]:
            if int(disk_id) == disk["id"]:
                return _server["id"]
    return None


@server_disk.command("get")
def server_disk_get(
    disk_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """Get Cloud Server disk."""
    client = create_client(config, profile)
    server_id = get_server_id_by_disk_id(client, disk_id)
    if not server_id:
        sys.exit(f"Error: Disk {disk_id} not found.")
    response = client.get_disk(server_id, disk_id)
    fmt.printer(response, output_format=output_format, func=print_disk)


# ------------------------------------------------------------- #
# $ twc server disk add                                         #
# ------------------------------------------------------------- #


@server_disk.command("add")
def server_disk_add(
    server_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    size: str = typer.Option(..., metavar="SIZE", help="Disk size e.g. 50G."),
):
    """Add disk to Cloud Server."""
    client = create_client(config, profile)
    if check_value(size_to_mb(size), minv=5120, maxv=512000, step=5120):
        response = client.add_disk(server_id, size=size_to_mb(size))
    else:
        raise UsageError(
            "Value must be in range 5120-512000M with step 5120M."
        )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["server_disk"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc server disk remove                                      #
# ------------------------------------------------------------- #


@server_disk.command("remove", "rm")
def server_disk_remove(
    disk_ids: List[int] = typer.Argument(..., metavar="DISK_ID..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
):
    """Remove disks."""
    if not yes:
        typer.confirm("This action cannot be undone. Continue?", abort=True)
    client = create_client(config, profile)
    for disk_id in disk_ids:
        server_id = get_server_id_by_disk_id(client, disk_id)
        response = client.delete_disk(server_id, disk_id)
        if response.status_code == 204:
            print(disk_id)
        else:
            sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc server disk resize                                      #
# ------------------------------------------------------------- #


@server_disk.command("resize")
def server_disk_resize(
    disk_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    size: str = typer.Option(..., metavar="SIZE", help="Disk size e.g. 50G."),
):
    """Increase disk size."""
    client = create_client(config, profile)
    server_id = get_server_id_by_disk_id(client, disk_id)
    if check_value(size_to_mb(size), minv=5120, maxv=512000, step=5120):
        response = client.update_disk(
            server_id, disk_id, size=size_to_mb(size)
        )
    else:
        raise UsageError("Value must be in range 5120-512000M with step 5120.")
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["server_disk"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc server backup schedule                                  #
# ------------------------------------------------------------- #


def print_autobackup_settings(response: Response):
    """Print backup settings info."""
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


@server_backup.command("schedule")
def server_backup_schedule(
    disk_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    status: bool = typer.Option(
        False,
        "--status",
        help="Display automatic backups status.",
    ),
    enable: Optional[bool] = typer.Option(
        None,
        "--enable/--disable",
        show_default=False,
        help="Enable or disable automatic backups.",
    ),
    keep: int = typer.Option(
        1,
        show_default=True,
        help="Number of backups to keep.",
    ),
    start_date: datetime = typer.Option(
        date.today().strftime("%Y-%m-%d"),
        formats=["%Y-%m-%d"],
        show_default=False,
        help="Start date of the first backup creation [default: today].",
    ),
    interval: BackupInterval = typer.Option(
        BackupInterval.DAY.value,
        "--interval",
        help="Backup interval.",
    ),
    day_of_week: Optional[int] = typer.Option(
        1,
        min=1,
        max=7,
        help="The day of the week on which backups will be created."
        " NOTE: This option works only with interval 'week'."
        " First day of week is monday.",
    ),
):
    """Manage disk automatic backup settings."""
    client = create_client(config, profile)
    server_id = get_server_id_by_disk_id(client, disk_id)

    if status:
        response = client.get_disk_autobackup_settings(server_id, disk_id)
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

    response = client.update_disk_autobackup_settings(
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
# $ twc server backup list                                      #
# ------------------------------------------------------------- #


def print_backups(response: Response):
    """Print table of backups list."""
    backups = response.json()["backups"]
    table = fmt.Table()
    table.header(
        [
            "ID",
            "DISK",
            "CREATED",
            "STATUS",
        ]
    )
    for backup in backups:
        table.row(
            [
                backup["id"],
                backup["name"],
                backup["created_at"],
                backup["status"],
            ]
        )
    table.print()


@server_backup.command("list", "ls")
def server_backup_list(
    disk_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """List backups by disk_id."""
    client = create_client(config, profile)
    server_id = get_server_id_by_disk_id(client, disk_id)
    response = client.get_disk_backups(server_id, disk_id)
    fmt.printer(response, output_format=output_format, func=print_backups)


# ------------------------------------------------------------- #
# $ twc server backup get                                       #
# ------------------------------------------------------------- #


def print_backup(response: object):
    """Print table with backup info."""
    backup = response.json()["backup"]
    table = fmt.Table()
    table.header(
        [
            "ID",
            "DISK",
            "CREATED",
            "STATUS",
        ]
    )
    table.row(
        [
            backup["id"],
            backup["name"],
            backup["created_at"],
            backup["status"],
        ]
    )
    table.print()


@server_backup.command("get")
def server_backup_get(
    disk_id: int,
    backup_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """Get disk backup info."""
    client = create_client(config, profile)
    server_id = get_server_id_by_disk_id(client, disk_id)
    response = client.get_disk_backup(server_id, disk_id, backup_id)
    fmt.printer(response, output_format=output_format, func=print_backup)


# ------------------------------------------------------------- #
# $ twc server backup create                                    #
# ------------------------------------------------------------- #


@server_backup.command("create")
def server_backup_create(
    disk_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    comment: Optional[str] = typer.Option(None, help="Comment."),
):
    """Create disk backup."""
    client = create_client(config, profile)
    server_id = get_server_id_by_disk_id(client, disk_id)
    response = client.create_disk_backup(server_id, disk_id, comment=comment)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["backup"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc server backup set                                       #
# ------------------------------------------------------------- #


@server_backup.command("set")
def server_backup_set(
    disk_id: int,
    backup_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    comment: Optional[str] = typer.Option(None, help="Comment."),
):
    """Change backup properties."""
    if not comment:
        raise UsageError("Nothing to do. Set one of options: ['--comment']")

    client = create_client(config, profile)
    server_id = get_server_id_by_disk_id(client, disk_id)
    response = client.update_disk_backup(
        server_id, disk_id, backup_id, comment=comment
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["backup"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc server backup remove                                    #
# ------------------------------------------------------------- #


@server_backup.command("remove", "rm")
def server_backup_remove(
    disk_id: int,
    backup_ids: List[int] = typer.Argument(..., metavar="BACKUP_ID..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
):
    """Remove backups."""
    if not yes:
        typer.confirm("This action cannot be undone. Continue?", abort=True)
    client = create_client(config, profile)
    server_id = get_server_id_by_disk_id(client, disk_id)
    for backup_id in backup_ids:
        response = client.delete_disk_backup(server_id, disk_id, backup_id)
        if response.status_code == 204:
            print(server_id)
        else:
            sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc server backup restore                                   #
# ------------------------------------------------------------- #


@server_backup.command("restore")
def server_backup_restore(
    disk_id: int,
    backup_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
):
    """Restore backup."""
    if not yes:
        typer.confirm("Data on target disk will lost. Continue?", abort=True)
    client = create_client(config, profile)
    server_id = get_server_id_by_disk_id(client, disk_id)
    response = client.do_action_with_disk_backup(
        server_id, disk_id, backup_id, action=BackupAction.RESTORE
    )
    if response.status_code == 204:
        print(server_id)
    else:
        sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc server backup mount                                     #
# ------------------------------------------------------------- #


@server_backup.command("mount")
def server_backup_mount(
    disk_id: int,
    backup_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
):
    """Attach backup as external drive."""
    client = create_client(config, profile)
    server_id = get_server_id_by_disk_id(client, disk_id)
    response = client.do_action_with_disk_backup(
        server_id, disk_id, backup_id, action=BackupAction.MOUNT
    )
    if response.status_code == 204:
        print(server_id)
    else:
        sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc server backup unmount                                   #
# ------------------------------------------------------------- #


@server_backup.command("unmount")
def server_backup_unmount(
    disk_id: int,
    backup_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
):
    """Detach backup from Cloud Server."""
    client = create_client(config, profile)
    server_id = get_server_id_by_disk_id(client, disk_id)
    response = client.do_action_with_disk_backup(
        server_id, disk_id, backup_id, action=BackupAction.UNMOUNT
    )
    if response.status_code == 204:
        print(server_id)
    else:
        sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc server dash                                             #
# ------------------------------------------------------------- #


@server.command("dash")
def server_dash(
    server_id: int,
    tab: bool = typer.Option(
        True, "--tab/--win", help="Open in new tab or new window."
    ),
    do_print: bool = typer.Option(
        False,
        "--print",
        help="Print URL instead of opening web browser.",
    ),
):
    """Open Cloud Server dashboard in web browser."""
    url = f"{CONTROL_PANEL_URL}/servers/{server_id}"
    if do_print:
        print(url)
        raise typer.Exit()
    if tab:
        webbrowser.open_new_tab(url)
    else:
        webbrowser.open_new(url)


# ------------------------------------------------------------- #
# $ twc server vnc                                              #
# ------------------------------------------------------------- #


@server.command("vnc")
def server_vnc(
    server_id: int,
    tab: bool = typer.Option(
        True, "--tab/--win", help="Open in new tab or new window."
    ),
    do_print: bool = typer.Option(
        False,
        "--print",
        help="Print URL instead of opening web browser.",
    ),
):
    """Open Cloud Server web VNC console in browser."""
    url = f"{CONTROL_PANEL_URL}/servers/{server_id}/console"
    if do_print:
        print(url)
        raise typer.Exit()
    if tab:
        webbrowser.open_new_tab(url)
    else:
        webbrowser.open_new(url)
