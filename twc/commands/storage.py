"""Object Storage management commands."""

import sys

import click
from click_aliases import ClickAliasedGroup

from twc import fmt
from twc.vars import TWC_S3_ENDPOINT
from . import (
    create_client,
    handle_request,
    set_value_from_config,
    options,
    debug,
    GLOBAL_OPTIONS,
    OUTPUT_FORMAT_OPTION,
)
from .project import (
    get_default_project_id,
    _project_list,
    _project_resource_move,
    _project_resource_list_buckets,
)


@handle_request
def _storage_list(client, *args, **kwargs):
    return client.get_buckets(*args, **kwargs)


@handle_request
def _storage_mb(client, *args, **kwargs):
    return client.create_bucket(*args, **kwargs)


@handle_request
def _storage_rb(client, *args, **kwargs):
    return client.delete_bucket(*args, **kwargs)


@handle_request
def _storage_set(client, *args, **kwargs):
    return client.update_bucket(*args, **kwargs)


@handle_request
def _storage_user_list(client, *args, **kwargs):
    return client.get_storage_users(*args, **kwargs)


@handle_request
def _storage_user_passwd(client, *args, **kwargs):
    return client.update_storage_user_secret(*args, **kwargs)


@handle_request
def _storage_transfer_new(client, *args, **kwargs):
    return client.start_storage_transfer(*args, **kwargs)


@handle_request
def _storage_transfer_status(client, *args, **kwargs):
    return client.get_storage_transfer_status(*args, **kwargs)


@handle_request
def _storage_subdomain_list(client, *args, **kwargs):
    return client.get_bucket_subdomains(*args, **kwargs)


@handle_request
def _storage_subdomain_add(client, *args, **kwargs):
    return client.add_bucket_subdomains(*args, **kwargs)


@handle_request
def _storage_subdomain_remove(client, *args, **kwargs):
    return client.delete_bucket_subdomains(*args, **kwargs)


@handle_request
def _storage_subdomain_gencert(client, *args, **kwargs):
    return client.gen_cert_for_bucket_subdomain(*args, **kwargs)


@handle_request
def _storage_list_presets(client, *args, **kwargs):
    return client.get_storage_presets(*args, **kwargs)


# ------------------------------------------------------------- #
# $ twc storage                                                 #
# ------------------------------------------------------------- #


@click.group(
    "storage",
    cls=ClickAliasedGroup,
    short_help="Manage Object Storage buckets.",
)
@options(GLOBAL_OPTIONS[:2])
def storage():
    """Manage Object Storage buckets.

    NOTE: TWC CLI does not implement S3-compatible API client, it uses
    Timeweb Cloud specific API methods instead. Use third party S3 clients
    to manage objects e.g. s3cmd, rclone, etc.
    """


# ------------------------------------------------------------- #
# $ twc storage list                                            #
# ------------------------------------------------------------- #


def print_buckets(response: object, filters: str):
    if filters:
        buckets = fmt.filter_list(response.json()["buckets"], filters)
    else:
        buckets = response.json()["buckets"]

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


@storage.command("list", aliases=["ls"], help="List buckets.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option("--filter", "-f", "filters", default="", help="Filter output.")
def storage_list(config, profile, verbose, output_format, filters):
    client = create_client(config, profile)
    response = _storage_list(client)
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_buckets,
    )


# ------------------------------------------------------------- #
# $ twc storage list-presets                                    #
# ------------------------------------------------------------- #


def print_storage_presets(response: object, filters: str):
    if filters:
        presets = fmt.filter_list(response.json()["storages_presets"], filters)
    else:
        presets = response.json()["storages_presets"]

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


@storage.command(
    "list-presets", aliases=["lp"], help="List Object Storage presets."
)
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option("--filter", "-f", "filters", default="", help="Filter output.")
@click.option("--region", help="Use region (location).")
def storage_list_presets(
    config, profile, verbose, output_format, filters, region
):
    if filters:
        filters = filters.replace("region", "location")
    if region:
        if filters:
            filters = filters + f",location:{region}"
        else:
            filters = f"location:{region}"

    client = create_client(config, profile)
    response = _storage_list_presets(client)
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_storage_presets,
    )


# ------------------------------------------------------------- #
# $ twc storage mb                                              #
# ------------------------------------------------------------- #


@storage.command("mb", help="Make bucket.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option("--preset-id", type=int, help="Bucket preset ID.")
@click.option(
    "--project-id",
    type=int,
    default=None,
    envvar="TWC_PROJECT",
    callback=set_value_from_config,
    help="Add bucket to specific project.",
)
@click.option(
    "--type",
    "bucket_type",
    type=click.Choice(["public", "private"]),
    default="private",
    show_default=True,
    help="Bucket access policy.",
)
@click.argument("bucket_name", type=str, required=True)
def storage_mb(
    config,
    profile,
    verbose,
    output_format,
    preset_id,
    project_id,
    bucket_type,
    bucket_name,
):
    # pylint: disable=too-many-locals

    client = create_client(config, profile)

    if not preset_id:
        # Select minimal preset
        preset_id = 389  # 10G disk

    is_public = False
    if bucket_type == "public":
        is_public = True

    if project_id:
        debug("Check project_id")
        projects = _project_list(client).json()["projects"]
        if not project_id in [prj["id"] for prj in projects]:
            raise click.BadParameter("Wrong project ID.")

    debug(f"Create bucket 'NAME-PREFIX-{bucket_name}'")
    response = _storage_mb(
        client, name=bucket_name, preset_id=preset_id, is_public=is_public
    )

    # Add created bucket to project if set
    if project_id:
        src_project = get_default_project_id(client)
        # Make useless request to avoid API bug (409 resource_not_found)
        _r = _project_resource_list_buckets(client, src_project)
        new_bucket_id = response.json()["bucket"]["id"]
        debug(f"Add bucket '{new_bucket_id}' to project '{project_id}'")
        project_resp = _project_resource_move(
            client,
            from_project=src_project,
            to_project=project_id,
            resource_id=new_bucket_id,
            resource_type="storage",
        )
        debug(project_resp.text)

    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: click.echo(response.json()["bucket"]["name"]),
    )


# ------------------------------------------------------------- #
# $ twc storage rb                                              #
# ------------------------------------------------------------- #


def get_bucket_id_by_name(client, bucket_name: str):
    debug(f"Get bucket_id by name '{bucket_name}'")
    buckets = _storage_list(client).json()["buckets"]
    for bucket in buckets:
        if bucket["name"] == bucket_name:
            return bucket["id"]
        if str(bucket["id"]) == bucket_name:
            return bucket["id"]
    return None


@storage.command("rb", help="Remove bucket.")
@options(GLOBAL_OPTIONS)
@click.confirmation_option(prompt="This action cannot be undone. Continue?")
@click.argument("buckets", nargs=-1, required=True)
def storage_rb(config, profile, verbose, buckets):
    client = create_client(config, profile)
    for bucket in buckets:
        bucket_id = get_bucket_id_by_name(client, bucket)
        if not bucket_id:
            sys.exit(f"Error: Bucket '{bucket}' not found.")

        response = _storage_rb(client, bucket_id)

        if response.status_code == 200:
            del_hash = response.json()["bucket_delete"]["hash"]
            del_code = click.prompt("Please enter confirmation code", type=int)
            response = _storage_rb(
                client, bucket_id, delete_hash=del_hash, code=del_code
            )
        if response.status_code == 204:
            click.echo(bucket)
        else:
            fmt.printer(response)


# ------------------------------------------------------------- #
# $ twc storage set                                             #
# ------------------------------------------------------------- #


@storage.command("set", help="Set bucket parameters and properties.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option("--preset-id", type=int, help="Bucket preset ID.")
@click.option(
    "--type",
    "bucket_type",
    type=click.Choice(["public", "private"]),
    default=None,
    help="Bucket access policy.",
)
@click.argument("bucket", required=True)
def storage_set(
    config,
    profile,
    verbose,
    output_format,
    preset_id,
    bucket_type,
    bucket,
):
    client = create_client(config, profile)

    bucket_id = get_bucket_id_by_name(client, bucket)
    if not bucket_id:
        sys.exit(f"Error: Bucket '{bucket}' not found.")

    payload = {}

    if preset_id:
        payload["preset_id"] = preset_id

    if bucket_type:
        if bucket_type == "public":
            payload["is_public"] = True
        else:
            payload["is_public"] = False

    response = _storage_set(client, bucket_id, **payload)

    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: click.echo(response.json()["bucket"]["name"]),
    )


# ------------------------------------------------------------- #
# $ twc storage user                                            #
# ------------------------------------------------------------- #


@storage.group("user", cls=ClickAliasedGroup)
@options(GLOBAL_OPTIONS[:2])
def storage_user():
    """Manage Object Storage users."""


# ------------------------------------------------------------- #
# $ twc storage user list                                       #
# ------------------------------------------------------------- #


def print_storage_users(response: object):
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


@storage_user.command("list", aliases=["ls"], help="List storage users.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
def storage_user_list(config, profile, verbose, output_format):
    client = create_client(config, profile)
    response = _storage_user_list(client)
    fmt.printer(
        response,
        output_format=output_format,
        func=print_storage_users,
    )


# ------------------------------------------------------------- #
# $ twc storage user passwd                                     #
# ------------------------------------------------------------- #


def get_storage_user(client, access_key: str = None):
    """Return user_id and access_key. If customer have only one storage
    user on account `access_key` is optional, user_id and access_key will
    taken from user info. If customer have multile storage users `access_key`
    is required.
    """
    users = _storage_user_list(client).json()
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


@storage_user.command("passwd", help="Set new secret_key for storage user.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option(
    "--secret-key", prompt=True, hide_input=True, confirmation_prompt=True
)
@click.argument("access_key", metavar="[ACCESS_KEY]", nargs=-1, type=str)
def storage_user_passwd(
    config, profile, verbose, output_format, secret_key, access_key
):
    client = create_client(config, profile)
    if access_key:
        access_key = list(access_key)[0]  # get element from tuple
    user_id, access_key = get_storage_user(client, access_key)
    if not user_id:
        sys.exit(f"User with access key '{access_key}' not found.")
    debug(f"User ID is '{user_id}'")
    debug(f"Change secret_key for '{user_id}'")
    response = _storage_user_passwd(
        client, user_id=user_id, secret_key=secret_key
    )

    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: click.echo(
            response.json()["user"]["access_key"]
        ),
    )


# ------------------------------------------------------------- #
# $ twc storage transfer                                        #
# ------------------------------------------------------------- #


@storage.group(
    "transfer",
    short_help="File transfer between object storage buckets.",
    hidden=True,
)
@options(GLOBAL_OPTIONS[:2])
def storage_transfer():
    """File transfer between object storage buckets.

    You can start file transfer from any S3-compatible object storage
    (including Timeweb Cloud Object Storage) to specified destination
    bucket.

    WARNING: This feature have unstable API, may occur errors.
    """


# ------------------------------------------------------------- #
# $ twc storage transfer new                                    #
# ------------------------------------------------------------- #


@storage_transfer.command("new", help="Start new file tranfer.")
@options(GLOBAL_OPTIONS)
@click.option(
    "--bucket", "src_bucket", required=True, help="Source bucket name."
)
@click.option("--access-key", required=True, help="Source bucket access key.")
@click.option("--secret-key", required=True, help="Source bucket secret key.")
@click.option("--region", default="", help="Source region.")
@click.option("--endpoint", default=None, help="Source storage endpoint.")
@click.option(
    "--force-path-style", is_flag=True, help="Force path-style bucket address."
)
@click.argument("dst_bucket", required=True)
def storage_transfer_new(
    config,
    profile,
    verbose,
    access_key,
    secret_key,
    region,
    endpoint,
    force_path_style,
    src_bucket,
    dst_bucket,
):
    client = create_client(config, profile)
    response = _storage_transfer_new(
        client,
        src_bucket=src_bucket,
        dst_bucket=dst_bucket,
        access_key=access_key,
        secret_key=secret_key,
        endpoint=endpoint,
        location=region,
        force_path_style=force_path_style,
    )
    if response.status_code == 204:
        click.echo(dst_bucket)
    else:
        fmt.printer(response)


# ------------------------------------------------------------- #
# $ twc storage transfer status                                 #
# ------------------------------------------------------------- #


def print_transfer_status(response):
    transfer = response.json()["transfer_status"]

    table = fmt.Table()
    translated_keys = {
        "status": "Status",
        "tries": "Tries",
        "total_count": "Total objects",
        "total_size": "Total size",
        "uploaded_count": "Uploaded objects",
        "uploaded_size": "Uploaded (size)",
        "errors": "Errors",
    }
    for key in transfer.keys():
        table.row([translated_keys[key], ":", transfer[key]])
    table.print()


@storage_transfer.command("status", help="Display file tranfer status.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.argument("bucket", required=True)
def storage_transfer_status(config, profile, verbose, output_format, bucket):
    client = create_client(config, profile)
    bucket_id = get_bucket_id_by_name(client, bucket)
    response = _storage_transfer_status(client, bucket_id)
    fmt.printer(
        response,
        output_format=output_format,
        func=print_transfer_status,
    )


# ------------------------------------------------------------- #
# $ twc storage subdomain                                       #
# ------------------------------------------------------------- #


@storage.group("subdomain", cls=ClickAliasedGroup)
@options(GLOBAL_OPTIONS[:2])
def storage_subdomain():
    """Manage subdomains."""


# ------------------------------------------------------------- #
# $ twc storage subdomain list                                  #
# ------------------------------------------------------------- #


def print_subdomains(response):
    subdomains = response.json()["subdomains"]
    table = fmt.Table()
    table.header(
        [
            "ID",
            "SUBDOMAIN",
            "CERT RELEASED",
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


@storage_subdomain.command(
    "list", aliases=["ls"], help="List subdomains attached to bucket."
)
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.argument("bucket", required=True)
def storage_subdomain_list(config, profile, verbose, output_format, bucket):
    client = create_client(config, profile)
    bucket_id = get_bucket_id_by_name(client, bucket)
    debug(f"bucket_id {bucket_id}")
    response = _storage_subdomain_list(client, bucket_id)
    fmt.printer(
        response,
        output_format=output_format,
        func=print_subdomains,
    )


# ------------------------------------------------------------- #
# $ twc storage subdomain add                                   #
# ------------------------------------------------------------- #


def print_subdomains_state(response):
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


@storage_subdomain.command("add", help="Attach subdomains to bucket.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.argument("subdomains", nargs=-1, required=True)
@click.argument("bucket", required=True)
def storage_subdomain_add(
    config, profile, verbose, output_format, bucket, subdomains
):
    client = create_client(config, profile)
    bucket_id = get_bucket_id_by_name(client, bucket)
    response = _storage_subdomain_add(client, bucket_id, list(subdomains))
    fmt.printer(
        response,
        output_format=output_format,
        func=print_subdomains_state,
    )


# ------------------------------------------------------------- #
# $ twc storage subdomain remove                                #
# ------------------------------------------------------------- #


@storage_subdomain.command("remove", aliases=["rm"], help="Remove subdomains.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.confirmation_option(prompt="Subdomains will be deleted. Continue?")
@click.argument("bucket", required=True)
@click.argument("subdomains", nargs=-1, required=True)
def storage_subdomain_remove(
    config, profile, verbose, output_format, bucket, subdomains
):
    client = create_client(config, profile)
    bucket_id = get_bucket_id_by_name(client, bucket)
    response = _storage_subdomain_remove(client, bucket_id, list(subdomains))
    fmt.printer(
        response,
        output_format=output_format,
        func=print_subdomains_state,
    )


# ------------------------------------------------------------- #
# $ twc storage subdomain gencert                               #
# ------------------------------------------------------------- #


@storage_subdomain.command(
    "gencert", help="Request TLS certificate for subdomains."
)
@options(GLOBAL_OPTIONS)
@click.argument("subdomains", nargs=-1, required=True)
def storage_subdomain_gencert(config, profile, verbose, subdomains):
    client = create_client(config, profile)
    for subdomain in subdomains:
        response = _storage_subdomain_gencert(client, subdomain)
        if response.status_code == 201:
            click.echo(subdomain)
        else:
            fmt.printer(response)


# ------------------------------------------------------------- #
# $ twc storage genconfig                                       #
# ------------------------------------------------------------- #


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


@storage.command("genconfig", help="Generate config file for S3 clients.")
@options(GLOBAL_OPTIONS)
@click.option("--user-id", type=int, help="Object Storage user ID.")
@click.option(
    "--client",
    "s3_client",
    type=click.Choice(["s3cmd", "rclone"]),
    required=True,
    help="S3 client.",
)
@click.option(
    "--save-to", help="Path to file. NOTE: Existing file will be overwitten."
)
def storage_genconfig(config, profile, verbose, user_id, s3_client, save_to):
    client = create_client(config, profile)

    # Get access_key and secret_key by user_id (or not)
    storage_users = _storage_user_list(client).json()["users"]
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

    file_content = templates[s3_client].format(
        access_key=access_key,
        secret_key=secret_key,
        endpoint=TWC_S3_ENDPOINT,
    )

    if save_to:
        with open(save_to, "w", encoding="utf-8") as s3_config:
            s3_config.write(file_content)
    else:
        fmt.print_colored(file_content, lang="ini")
