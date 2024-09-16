"""Manage object storage buckets.

NOTE: TWC CLI does not implement S3-compatible API client, it uses Timeweb
Cloud specific API methods instead. Use third party S3 clients to manage
objects e.g. s3cmd, rclone, etc.
"""

import sys
from logging import debug
from typing import Optional, List
from pathlib import Path
from enum import Enum

import typer
from requests import Response

from twc import fmt
from twc.typerx import TyperAlias
from twc.apiwrap import create_client
from twc.api import TimewebCloud, ServiceRegion, BucketType
from .common import (
    verbose_option,
    config_option,
    profile_option,
    filter_option,
    yes_option,
    output_format_option,
)


storage = TyperAlias(help=__doc__, short_help="Manage object storage buckets.")
storage_user = TyperAlias(help="Manage Object Storage users.")
storage_subdomain = TyperAlias(help="Manage subdomains.")
storage.add_typer(storage_user, name="user")
storage.add_typer(storage_subdomain, name="subdomain", aliases=["domain"])

# FUTURE: Implement storage_transfer group. Waiting for API bugfix.

# ------------------------------------------------------------- #
# $ twc storage list                                            #
# ------------------------------------------------------------- #


def print_buckets(response: Response, filters: Optional[str] = None):
    """Print table with buckets list."""
    buckets = response.json()["buckets"]
    if filters:
        buckets = fmt.filter_list(buckets, filters)
    table = fmt.Table()
    table.header(
        [
            "ID",
            "NAME",
            "REGION",
            "STATUS",
            "TYPE",
        ]
    )
    for bucket in buckets:
        table.row(
            [
                bucket["id"],
                bucket["name"],
                bucket["location"],
                bucket["status"],
                bucket["type"],
            ]
        )
    table.print()


@storage.command("list", "ls")
def storage_list(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
):
    """List buckets."""
    client = create_client(config, profile)
    response = client.get_buckets()
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_buckets,
    )


# ------------------------------------------------------------- #
# $ twc storage list-presets                                    #
# ------------------------------------------------------------- #


def print_storage_presets(response: Response, filters: Optional[str] = None):
    """Print table with storage presets."""
    presets = response.json()["storages_presets"]
    if filters:
        presets = fmt.filter_list(presets, filters)
    table = fmt.Table()
    table.header(
        [
            "ID",
            "REGION",
            "PRICE",
            "DISK",
        ]
    )
    for preset in presets:
        table.row(
            [
                preset["id"],
                preset["location"],
                preset["price"],
                str(round(preset["disk"] / 1024)) + "G",
            ]
        )
    table.print()


@storage.command("list-presets", "lp")
def storage_list_presets(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
    region: Optional[ServiceRegion] = typer.Option(
        None,
        case_sensitive=False,
        help="Use region (location).",
    ),
):
    """List Object Storage presets."""
    if region:
        filters = f"{filters},location:{region}"
    client = create_client(config, profile)
    response = client.get_storage_presets()
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_storage_presets,
    )


# ------------------------------------------------------------- #
# $ twc storage mb                                              #
# ------------------------------------------------------------- #


@storage.command("mb", short_help="Make bucket.")
def storage_mb(
    bucket: str = typer.Argument(..., help="Bucket name."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    preset_id: Optional[int] = typer.Option(None, help="Storage preset."),
    bucket_type: BucketType = typer.Option(
        BucketType.PRIVATE.value,
        "--type",
        case_sensitive=False,
        help="Bucket access policy.",
    ),
    project_id: Optional[int] = typer.Option(
        None,
        envvar="TWC_PROJECT",
        show_envvar=False,
        help="Add bucket to specific project.",
    ),
):
    """Make bucket.

    NOTE: A unique prefix for the account will be added to the bucket name
    e.g. 'my-bucket' will created as 'c7a04e58-my-bucket'. Prefix will not
    be added when creating a bucket via S3 clients.
    """
    client = create_client(config, profile)

    if not preset_id:
        # Select minimal preset
        preset_id = 389  # 10G disk

    is_public = False
    if bucket_type == BucketType.PUBLIC:
        is_public = True

    if project_id:
        if not project_id in [
            prj["id"] for prj in client.get_projects().json()["projects"]
        ]:
            sys.exit(f"Wrong project ID: Project '{project_id}' not found.")

    debug(f"Create bucket 'NAME_PREFIX-{bucket}'")
    response = client.create_bucket(
        name=bucket, preset_id=preset_id, is_public=is_public
    )

    # Add created bucket to project if set
    if project_id:
        client.add_bucket_to_project(
            response.json()["bucket"]["id"],
            project_id,
        )

    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["bucket"]["name"]),
    )


# ------------------------------------------------------------- #
# $ twc storage rb                                              #
# ------------------------------------------------------------- #


def resolve_bucket_id(client: TimewebCloud, bucket_name: str):
    """Return bucket ID by name."""
    debug(f"Get bucket_id by name '{bucket_name}'")
    for bucket in client.get_buckets().json()["buckets"]:
        if bucket["name"] == bucket_name:
            return bucket["id"]
        if str(bucket["id"]) == bucket_name:
            return bucket["id"]
    sys.exit(f"Error: Bucket '{bucket_name}' not found.")


@storage.command("rb")
def storage_rb(
    buckets: List[str] = typer.Argument(..., metavar="BUCKET"),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
):
    """Remove bucket."""
    if not yes:
        typer.confirm("This action cannot be undone. Continue?", abort=True)
    client = create_client(config, profile)
    for bucket in buckets:
        bucket_id = resolve_bucket_id(client, bucket)
        response = client.delete_bucket(bucket_id)
        if response.status_code == 200:
            del_hash = response.json()["bucket_delete"]["hash"]
            del_code = typer.prompt("Please enter confirmation code", type=int)
            response = client.delete_bucket(
                bucket_id, delete_hash=del_hash, code=del_code
            )
        if response.status_code == 204:
            print(bucket)
        else:
            sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc storage set                                             #
# ------------------------------------------------------------- #


@storage.command("set")
def storage_set(
    bucket: str = typer.Argument(..., help="Bucket name."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    preset_id: Optional[int] = typer.Option(None, help="Storage preset."),
    bucket_type: Optional[BucketType] = typer.Option(
        None,
        "--type",
        case_sensitive=False,
        help="Bucket access policy.",
    ),
):
    """Set bucket parameters and properties."""
    client = create_client(config, profile)
    bucket_id = resolve_bucket_id(client, bucket)
    payload = {}
    if preset_id:
        payload["preset_id"] = preset_id
    if bucket_type:
        if bucket_type == "public":
            payload["is_public"] = True
        else:
            payload["is_public"] = False
    response = client.update_bucket(bucket_id, **payload)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["bucket"]["name"]),
    )


# ------------------------------------------------------------- #
# $ twc storage user list                                       #
# ------------------------------------------------------------- #


def print_storage_users(response: Response):
    """Print table with sotrage users list."""
    users = response.json()["users"]
    table = fmt.Table()
    table.header(
        [
            "ID",
            "ACCESS KEY",
        ]
    )
    for user in users:
        table.row(
            [
                user["id"],
                user["access_key"],
            ]
        )
    table.print()


@storage_user.command("list", "ls")
def storage_user_list(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """List storage users."""
    client = create_client(config, profile)
    response = client.get_storage_users()
    fmt.printer(
        response,
        output_format=output_format,
        func=print_storage_users,
    )


# ------------------------------------------------------------- #
# $ twc storage user passwd                                     #
# ------------------------------------------------------------- #


def get_storage_user(client: TimewebCloud, access_key: Optional[str] = None):
    """Return user_id and access_key. If customer have only one storage
    user on account `access_key` is optional, user_id and access_key will
    taken from user info. If customer have multile storage users `access_key`
    is required.
    """
    users = client.get_storage_users().json()
    user_id = None

    # If access_key argument is set, set effective access key
    if users["meta"]["total"] == 1:
        user_id = users["users"][0]["id"]
        access_key = users["users"][0]["access_key"]
    else:
        if access_key:
            for user in users["users"]:
                if user["access_key"] == access_key:
                    user_id = user["id"]
    return user_id, access_key


@storage_user.command("passwd")
def storage_user_passwd(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    access_key: Optional[str] = typer.Argument(None),
    secret_key: str = typer.Option(
        ...,
        prompt="Storage user password",
        confirmation_prompt=True,
        hide_input=True,
        help="",
    ),
):
    """Set new secret_key for storage user."""
    client = create_client(config, profile)
    user_id, access_key = get_storage_user(client, access_key)
    if not user_id:
        sys.exit(f"User with access key '{access_key}' not found.")
    debug(f"User ID is '{user_id}'")
    debug(f"Change secret_key for '{user_id}'")
    response = client.update_storage_user_secret(
        user_id=user_id, secret_key=secret_key
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["user"]["access_key"]),
    )


# ------------------------------------------------------------- #
# $ twc storage subdomain list                                  #
# ------------------------------------------------------------- #


def print_subdomains(response: Response):
    """Print table with subdomains list."""
    subdomains = response.json()["subdomains"]
    table = fmt.Table()
    table.header(
        [
            "ID",
            "SUBDOMAIN",
            "CERT_RELEASED",
            "STATUS",
        ]
    )
    for sub in subdomains:
        table.row(
            [
                sub["id"],
                sub["subdomain"],
                sub["cert_released"],
                sub["status"],
            ]
        )
    table.print()


@storage_subdomain.command("list", "ls")
def storage_subdomain_list(
    bucket: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """List subdomains attached to bucket."""
    client = create_client(config, profile)
    bucket_id = resolve_bucket_id(client, bucket)
    debug(f"bucket_id {bucket_id}")
    response = client.get_bucket_subdomains(bucket_id)
    fmt.printer(
        response,
        output_format=output_format,
        func=print_subdomains,
    )


# ------------------------------------------------------------- #
# $ twc storage subdomain add                                   #
# ------------------------------------------------------------- #


def print_subdomains_state(response: Response):
    """Print table with subdomains status."""
    subdomains = response.json()["subdomains"]
    table = fmt.Table()
    table.header(
        [
            "SUBDOMAIN",
            "STATUS",
        ]
    )
    for sub in subdomains:
        table.row(
            [
                sub["subdomain"],
                sub["status"],
            ]
        )
    table.print()


@storage_subdomain.command("add")
def storage_subdomain_add(
    bucket: str = typer.Argument(...),
    subdomains: List[str] = typer.Argument(..., metavar="SUBDOMAIN..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """Attach subdomains to bucket."""
    client = create_client(config, profile)
    bucket_id = resolve_bucket_id(client, bucket)
    response = client.add_bucket_subdomains(bucket_id, subdomains)
    fmt.printer(
        response,
        output_format=output_format,
        func=print_subdomains_state,
    )


# ------------------------------------------------------------- #
# $ twc storage subdomain remove                                #
# ------------------------------------------------------------- #


@storage_subdomain.command("remove", "rm")
def storage_subdomain_remove(
    bucket: str = typer.Argument(...),
    subdomains: List[str] = typer.Argument(..., metavar="SUBDOMAIN..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
):
    """Remove subdomains."""
    if not yes:
        typer.confirm("Subdomains will be deleted. Continue?", abort=True)
    client = create_client(config, profile)
    bucket_id = resolve_bucket_id(client, bucket)
    response = client.delete_bucket_subdomains(bucket_id, subdomains)
    if response.status_code == 204:
        for subdomain in subdomains:
            print(subdomain)
    else:
        sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc storage subdomain gencert                               #
# ------------------------------------------------------------- #


@storage_subdomain.command("gencert", "cert")
def storage_subdomain_gencert(
    subdomains: List[str] = typer.Argument(..., metavar="SUBDOMAIN..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
):
    """Request TLS certificate for subdomains."""
    client = create_client(config, profile)
    for subdomain in subdomains:
        response = client.gen_cert_for_bucket_subdomain(subdomain)
        if response.status_code == 204:
            print(subdomain)
        else:
            sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc storage genconfig                                       #
# ------------------------------------------------------------- #


class S3Client(str, Enum):
    """S3 clients."""

    RCLONE = "rclone"
    S3CMD = "s3cmd"


S3CMD_CONFIG_TEMPLATE = """
[default]
access_key = {access_key}
secret_key = {secret_key}
bucket_location = ru-1
host_base = {endpoint}
host_bucket = {endpoint}
use_https = True
"""

RCLONE_CONFIG_TEMPLATE = """
[twc]
type = s3
provider = Other
env_auth = false
access_key_id = {access_key}
secret_access_key = {secret_key}
region = ru-1
endpoint = https://{endpoint}
"""


@storage.command("genconfig", "gencfg", "cfg")
def storage_genconfig(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    user_id: Optional[int] = typer.Option(
        None, help="Object Storage user ID."
    ),
    s3_client: S3Client = typer.Option(..., "--client", help="S3 client."),
    save: Optional[Path] = typer.Option(
        None,
        help="Path to file. NOTE: Existing file will be overwitten.",
    ),
    save_to: Optional[Path] = typer.Option(
        None,
        help="Path to file. NOTE: Existing file will be overwitten.",
        hidden=True,
    ),
):
    """Generate config file for S3 clients."""
    client = create_client(config, profile)

    # Get access_key and secret_key by user_id (or not)
    storage_users = client.get_storage_users().json()["users"]
    if user_id:
        for user in storage_users:
            if user_id == user["id"]:
                access_key = user["access_key"]
                secret_key = user[user_id]["secret_key"]
            else:
                sys.exit(f"Error: user with ID '{user_id}' not found.")
    else:
        user_id, access_key = get_storage_user(client)
        secret_key = storage_users[0]["secret_key"]

    templates = {
        "s3cmd": S3CMD_CONFIG_TEMPLATE.strip(),
        "rclone": RCLONE_CONFIG_TEMPLATE.strip(),
    }

    endpoint = "s3.timeweb.cloud"
    if not access_key.isupper():
        # Legacy object storage service have lowercase usernames only.
        # New storage, on the contrary, always has keys in uppercase.
        endpoint = "s3.timeweb.com"

    file_content = templates[s3_client].format(
        access_key=access_key,
        secret_key=secret_key,
        endpoint=endpoint,
    )

    if save_to:
        save = save_to
    if save:
        with open(save, "w", encoding="utf-8") as s3_config:
            s3_config.write(file_content)
    else:
        fmt.print_colored(file_content, lang="ini")
