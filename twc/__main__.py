"""CLI for Timeweb Cloud services."""

from typing import Optional
from pathlib import Path

import typer

from .typerx import TyperAlias
from .commands import (
    config,
    account,
    server,
    ssh_key,
    image,
    project,
    database,
    storage,
    balancer,
    cluster,
    domain,
    vpc,
    firewall,
    floating_ip,
    whoami,
)
from .commands.common import version_callback, version_option, verbose_option


cli = TyperAlias(
    help=__doc__,
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
cli.add_typer(config, name="config")
cli.add_typer(account, name="account")
cli.add_typer(server, name="server", aliases=["servers", "s"])
cli.add_typer(ssh_key, name="ssh-key", aliases=["ssh-keys", "k"])
cli.add_typer(image, name="image", aliases=["images", "i"])
cli.add_typer(project, name="project", aliases=["projects", "p"])
cli.add_typer(database, name="database", aliases=["databases", "db"])
cli.add_typer(storage, name="storage", aliases=["storages", "s3"])
cli.add_typer(balancer, name="balancer", aliases=["balancers", "lb"])
cli.add_typer(
    cluster, name="cluster", aliases=["clusters", "kubernetes", "k8s"]
)
cli.add_typer(domain, name="domain", aliases=["domains", "d"])
cli.add_typer(vpc, name="vpc", aliases=["vpcs", "network", "networks"])
cli.add_typer(firewall, name="firewall", aliases=["fw"])
cli.add_typer(floating_ip, name="ip", aliases=["ips"])
cli.add_typer(whoami, name="whoami", aliases=[])


@cli.command("version")
def version_command():
    """Show version and exit."""
    version_callback(True)


@cli.callback()
def root(
    version: Optional[bool] = version_option,
    verbose: Optional[bool] = verbose_option,
    # pylint: disable=redefined-outer-name
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        envvar="TWC_CONFIG_FILE",
        show_envvar=False,
        show_default=False,
        exists=True,
        dir_okay=False,
        help="Use config.",
        rich_help_panel="Global options",
    ),
    profile: Optional[str] = typer.Option(
        None,
        "--profile",
        "-p",
        metavar="NAME",
        envvar="TWC_PROFILE",
        show_envvar=False,
        show_default=False,
        help="Use profile.",
        rich_help_panel="Global options",
    ),
):
    # pylint: disable=unused-argument
    """Callback for root level command options."""


if __name__ == "__main__":
    cli()
