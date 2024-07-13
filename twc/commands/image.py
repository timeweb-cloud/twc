"""Manage disk images."""

import re
import sys
from logging import debug
from typing import Optional, List
from pathlib import Path
from uuid import UUID

import typer
from click import UsageError
from requests import Response

from twc import fmt
from twc.typerx import TyperAlias
from twc.apiwrap import create_client
from twc.api import ServerOSType
from .common import (
    verbose_option,
    config_option,
    profile_option,
    filter_option,
    yes_option,
    output_format_option,
    region_option,
)


image = TyperAlias(help=__doc__)


# ------------------------------------------------------------- #
# $ twc image list                                              #
# ------------------------------------------------------------- #


def print_images(response: Response, filters: Optional[str] = None):
    """Print table with images list."""
    images = response.json()["images"]
    if filters:
        images = fmt.filter_list(images, filters)

    table = fmt.Table()
    table.header(
        [
            "ID",
            # "NAME",
            "TYPE",
            "REGION",
            "STATUS",
            "SIZE",
        ]
    )
    for img in images:
        table.row(
            [
                img["id"],
                img["type"],
                # img["name"][:18] + "..."
                # if len(img["name"]) > 18
                # else img["name"],
                img["location"],
                img["status"],
                str(round(img["size"] / 1024)) + "G",
            ]
        )
    table.print()


@image.command("list", "ls")
def image_list(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    limit: int = typer.Option(500, help="Items to display."),
    filters: Optional[str] = filter_option,
):
    """List images."""
    client = create_client(config, profile)
    response = client.get_images(limit=limit)
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_images,
    )


# ------------------------------------------------------------- #
# $ twc image get                                               #
# ------------------------------------------------------------- #


def print_image(response: Response):
    """Print table with image info."""
    table = fmt.Table()
    table.header(
        [
            "ID",
            "NAME",
            "TYPE",
            "REGION",
            "STATUS",
            "DISK",
            "SIZE",
        ]
    )
    img = response.json()["image"]
    table.row(
        [
            img["id"],
            img["name"],
            img["type"],
            img["location"],
            img["status"],
            img["disk_id"],
            str(round(img["size"] / 1024)) + "G",
        ]
    )
    table.print()


@image.command("get")
def image_get(
    image_id: UUID,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    status: Optional[bool] = typer.Option(
        False,
        "--status",
        help="Display status and exit with 0 if status is 'created'.",
    ),
):
    """Get image info."""
    client = create_client(config, profile)
    response = client.get_image(image_id)
    if status:
        state = response.json()["image"]["status"]
        if state == "created":
            print(state)
            raise typer.Exit()
        sys.exit(state)
    fmt.printer(response, output_format=output_format, func=print_image)


# ------------------------------------------------------------- #
# $ twc image create                                            #
# ------------------------------------------------------------- #


@image.command("create")
def image_create(
    disk_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    name: Optional[str] = typer.Option(
        None, help="Image human readable name."
    ),
    desc: Optional[str] = typer.Option(None, help="Image description."),
):
    """Create image from existing Cloud Server disk."""
    client = create_client(config, profile)
    response = client.create_image(
        disk_id=disk_id, name=name, description=desc
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["image"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc image remove                                            #
# ------------------------------------------------------------- #


@image.command("remove", "rm")
def image_remove(
    image_ids: List[UUID] = typer.Argument(..., metavar="IMAGE_ID..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
):
    """Remove image."""
    if not yes:
        typer.confirm(
            "This action cannot be undone. Continue?",
            abort=True,
        )
    client = create_client(config, profile)
    for image_id in image_ids:
        response = client.delete_image(image_id)
        if response.status_code == 204:
            print(image_id)
        else:
            sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc image set                                               #
# ------------------------------------------------------------- #


@image.command("set")
def image_set_property(
    image_id: UUID,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    name: Optional[str] = typer.Option(
        None, help="Image human readable name."
    ),
    desc: Optional[str] = typer.Option(None, help="Image description."),
):
    """Change image name and description."""
    if not name and not desc:
        raise UsageError(
            "Nothing to do. Set one of options: ['--name', '--desc']"
        )
    client = create_client(config, profile)
    response = client.update_image(image_id, name=name, description=desc)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["image"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc image upload                                            #
# ------------------------------------------------------------- #


@image.command("upload")
def image_upload(
    file: str = typer.Argument(..., help="Direct HTTP(S) link to image."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    name: Optional[str] = typer.Option(
        None, help="Image human readable name."
    ),
    desc: Optional[str] = typer.Option(None, help="Image description."),
    os_type: ServerOSType = typer.Option(
        ServerOSType.OTHER.value,
        metavar="OS_TYPE",
        case_sensitive=False,
        help="OS type. This value is formal and not affects on server/image.",
    ),
    region: Optional[str] = region_option,
):
    """Upload image from URL."""
    client = create_client(config, profile)
    if re.match(r"https?://", file):
        debug(f"Upload URL: {file}")
    else:
        sys.exit(f"Invalid link: {file}")

    response = client.create_image(
        upload_url=file,
        name=name,
        description=desc,
        os_type=os_type,
        location=region,
    )

    # FUTURE: Implement file upload from local disk

    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["image"]["id"]),
    )
