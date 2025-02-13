"""Manage domains and DNS records."""

import re
import sys
from enum import Enum
from typing import Optional, List
from pathlib import Path

import typer
from requests import Response

from twc import fmt
from twc.typerx import TyperAlias
from twc.apiwrap import create_client
from twc.api import DNSRecordType
from .common import (
    verbose_option,
    config_option,
    profile_option,
    filter_option,
    output_format_option,
    yes_option,
)


domain = TyperAlias(help=__doc__)
domain_subdomain = TyperAlias(help="Manage subdomains.")
domain_record = TyperAlias(help="Manage DNS records.")
domain.add_typer(domain_record, name="record", aliases=["records", "rec"])
domain.add_typer(
    domain_subdomain, name="subdomain", aliases=["subdomains", "sub"]
)


# ------------------------------------------------------------- #
# $ twc domain list                                             #
# ------------------------------------------------------------- #


def print_domains(
    response: Response,
    filters: Optional[str] = None,
    with_subdomains: bool = False,
):
    """Print table with domains list."""
    domains = response.json()["domains"]
    if filters:
        domains = fmt.filter_list(domains, filters)
    table = fmt.Table()
    table.header(
        [
            "FQDN",
            "STATUS",
            "EXPIRATION",
        ]
    )
    for domain_json in domains:
        table.row(
            [
                domain_json["fqdn"],
                domain_json["domain_status"],
                domain_json["expiration"],
            ]
        )
        if with_subdomains:
            for subdomain in domain_json["subdomains"]:
                table.row(
                    [
                        subdomain["fqdn"],
                        "",
                        "",
                    ]
                )
    table.print()


@domain.command("list", "ls")
def domains_list(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
    limit: Optional[int] = typer.Option(
        100,
        "--limit",
        "-l",
        help="Number of items to display.",
    ),
    with_subdomains: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Show subdomains too.",
    ),
):
    """List domains."""
    client = create_client(config, profile)
    response = client.get_domains(limit=limit)
    dom_count = response.json()["meta"]["total"]
    if dom_count > limit:
        print(
            f"NOTE: Only {limit} of {dom_count} domain names is displayed.\n"
            "NOTE: Use '--limit' option to set number of domains to display.",
            file=sys.stderr,
        )
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        with_subdomains=with_subdomains,
        func=print_domains,
    )


# ------------------------------------------------------------- #
# $ twc domain info                                             #
# ------------------------------------------------------------- #


def print_domain_info(response: Response):
    """Print domain info."""
    domain_json = response.json()["domain"]

    output = (
        f'Domain: {domain_json["fqdn"]}\n'
        + f'Exp date: {domain_json["expiration"]}\n'
        + f'Registrar: {domain_json["provider"]}\n'
        + f'ID: {domain_json["id"]}\n'
        + f'Technical: {domain_json["is_technical"]}\n'
        + "Subdomains: \n"
        + "".join(
            (f'  FQDN: {sub["fqdn"]}\n' + f'    ID: {sub["id"]}\n')
            for sub in domain_json["subdomains"]
        )
    )
    print(output.strip())


@domain.command("info")
def domain_info(
    domain_name: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """Get domain info."""
    client = create_client(config, profile)
    response = client.get_domain(domain_name)
    fmt.printer(
        response,
        output_format=output_format,
        func=print_domain_info,
    )


# ------------------------------------------------------------- #
# $ twc domain rm                                               #
# ------------------------------------------------------------- #


@domain.command("remove", "rm")
def domain_delete(
    domain_names: List[str] = typer.Argument(..., metavar="DOMAIN_NAME..."),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    yes: Optional[bool] = yes_option,
    force: bool = typer.Option(False, "--force", help="Force removal."),
):
    """Remove domain names."""
    if not yes:
        typer.confirm("This action cannot be undone. Continue?", abort=True)
    client = create_client(config, profile)
    for domain_name in domain_names:
        # API Issue: API removes domain if subdomain is passed
        # Prevent domain removal!
        if re.match(r"^(.+\.){2}.+$", domain_name) and not force:
            sys.exit(
                "Error: It looks like you want to delete a subdomain.\n"
                "Please use command 'twc domain rmsub SUBDOMAIN' for this.\n"
                "NOTE: This command will delete the domain itself even if its"
                " subdomain is passed. If you are sure you want to continue "
                "use the '--force' option."
            )
        response = client.delete_domain(domain_name)
        if response.status_code == 204:
            print(domain_name)
        else:
            sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc domain add                                              #
# ------------------------------------------------------------- #


@domain.command("add", "create")
def domain_add(
    domain_name: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
):
    """Add domain to account."""
    client = create_client(config, profile)
    response = client.add_domain(domain_name)
    if response.status_code == 204:
        print(domain_name)
    else:
        sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc domain record list                                      #
# ------------------------------------------------------------- #


def print_domain_record_list(
    response: Response,
    requested_domain: str,
    filters: Optional[str] = None,
    with_subdomains: bool = False,
):
    """Print domain records."""
    records = response.json()["dns_records"]

    if not with_subdomains:
        records = filter(lambda x: "subdomain" not in x["data"], records)

    if filters:
        records = fmt.filter_list(records, filters)

    table = fmt.Table()
    table.header(
        [
            "NAME",
            "ID",
            "TYPE",
            "VALUE",
        ]
    )

    for record in records:
        if "subdomain" in record["data"]:
            _sub = record["data"]["subdomain"]
            if _sub is None:
                fqdn = requested_domain
            else:
                fqdn = _sub + "." + requested_domain
        else:
            fqdn = requested_domain
        table.row(
            [
                fqdn,
                record["id"],
                record["type"],
                record["data"]["value"],
            ]
        )
    table.print()


@domain_record.command("list", "ls")
def domain_records_list(
    domain_name: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
    with_subdomains: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Show subdomain records too.",
    ),
):
    """List DNS-records on domain."""
    client = create_client(config, profile)
    response = client.get_domain_dns_records(domain_name)
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        with_subdomains=with_subdomains,
        requested_domain=domain_name,
        func=print_domain_record_list,
    )


# ------------------------------------------------------------- #
# $ twc domain record remove                                    #
# ------------------------------------------------------------- #


@domain_record.command("remove", "rm")
def domain_remove_dns_record(
    domain_name: str,
    record_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
):
    """Delete one DNS-record on domain."""
    client = create_client(config, profile)
    response = client.delete_domain_dns_record(domain_name, record_id)
    if response.status_code == 204:
        print(record_id)
    else:
        sys.exit(fmt.printer(response))


# ------------------------------------------------------------- #
# $ twc domain record add                                       #
# ------------------------------------------------------------- #


class SRVProtocol(str, Enum):
    """Supported protocols for SRV records."""

    TCP = "TCP"
    UPD = "UDP"
    TLS = "TLS"


@domain_record.command("add", "create")
def domain_add_dns_record(
    domain_name: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
    record_type: DNSRecordType = typer.Option(
        ...,
        "--type",
        case_sensitive=False,
        metavar="TYPE",
        help=f"[{'|'.join([k.value for k in DNSRecordType])}]",
    ),
    value: Optional[str] = typer.Option(
        None,
        help="Record value. Skip it for SRV records.",
    ),
    priority: Optional[int] = typer.Option(
        None,
        "--prio",
        help="Record priority. Supported for MX, SRV records.",
    ),
    service: Optional[str] = typer.Option(
        None,
        "--service",
        help="Service for SRV record e.g '_matrix'.",
    ),
    proto: Optional[SRVProtocol] = typer.Option(
        None,
        "--proto",
        help="Protocol for SRV record.",
    ),
    host: Optional[str] = typer.Option(
        None,
        "--host",
        help="Host for SRV record.",
    ),
    port: Optional[int] = typer.Option(
        None,
        "--port",
        help="Port for SRV record.",
        min=1,
        max=65535,
    ),
    ttl: Optional[int] = typer.Option(
        None, "--ttl", help="Time-To-Live for DNS record."
    ),
    second_ld: Optional[bool] = typer.Option(
        False,
        "--2ld",
        help="Parse subdomain as 2LD.",
    ),
):
    """Add dns record for domain or subdomain."""
    client = create_client(config, profile)

    if record_type != "SRV" and not value:
        sys.exit("Error: --value is expected for non-SRV DNS records")

    null_subdomain = False

    if second_ld:
        offset = 3
    else:
        offset = 2

    subdomain = domain_name
    original_domain_name = domain_name
    domain_name = ".".join(domain_name.split(".")[-offset:])

    if subdomain == domain_name:
        subdomain = None

    if record_type.lower() == "txt":
        if subdomain is None:
            null_subdomain = True
        else:
            # 'ftp.example.org' --> 'ftp'
            subdomain = ".".join(subdomain.split(".")[:-offset])
    else:
        subdomain = ".".join(original_domain_name.split(".")[:-offset])
        if subdomain != "":
            domain_name = original_domain_name
            subdomain = None

    payload = {
        "fqdn": domain_name,
        "dns_record_type": record_type,
        "value": value,
        "subdomain": subdomain,
        "priority": priority,
        "ttl": ttl,
        "protocol": "_" + proto if proto else None,
        "service": service,
        "host": host,
        "port": port,
        "null_subdomain": null_subdomain,
    }

    response = client.add_domain_dns_record(**payload)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["dns_record"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc domain record update                                    #
# ------------------------------------------------------------- #


@domain_record.command("update", "upd")
def domain_update_dns_records(
    domain_name: str,
    record_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
    record_type: DNSRecordType = typer.Option(
        ...,
        "--type",
        case_sensitive=False,
        metavar="TYPE",
        help=f"[{'|'.join([k.value for k in DNSRecordType])}]",
    ),
    value: Optional[str] = typer.Option(...),
    priority: Optional[int] = typer.Option(
        None,
        "--prio",
        help="Record priority. Supported for MX, SRV records.",
    ),
    second_ld: Optional[bool] = typer.Option(
        False,
        "--2ld",
        help="Parse subdomain as 2LD.",
    ),
):
    """Update DNS record."""
    client = create_client(config, profile)

    if second_ld:
        offset = 3
    else:
        offset = 2

    subdomain = domain_name
    domain_name = ".".join(domain_name.split(".")[-offset:])

    if subdomain == domain_name:
        subdomain = None

    if record_type.lower() == "txt" and subdomain is not None:
        subdomain = ".".join(subdomain.split(".")[:-offset])
    elif subdomain is not None:
        domain_name = subdomain
        subdomain = None

    response = client.update_domain_dns_record(
        domain_name, record_id, record_type, value, subdomain, priority
    )
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["dns_record"]["id"]),
    )


# ------------------------------------------------------------- #
# $ twc domain sub add                                          #
# ------------------------------------------------------------- #


@domain_subdomain.command("add", "create")
def domain_add_subdomain(
    subdomain: str = typer.Argument(..., metavar="FQDN"),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
    second_ld: Optional[bool] = typer.Option(
        False,
        "--2ld",
        help="Parse subdomain as 2LD.",
    ),
):
    """Create subdomain."""
    client = create_client(config, profile)

    if second_ld:
        offset = 3
    else:
        offset = 2

    domain_name = ".".join(subdomain.split(".")[-offset:])
    subdomain = ".".join(subdomain.split(".")[:-offset])

    # API issue: You cannot create 'www' subdomain
    if subdomain.startswith("www."):
        sys.exit(
            "Error: API does not support custom www subdomains. "
            "www subdomain always have the same A-record with @"
        )

    response = client.add_subdomain(domain_name, subdomain)
    fmt.printer(
        response,
        output_format=output_format,
        func=lambda response: print(response.json()["subdomain"]["fqdn"]),
    )


# ------------------------------------------------------------- #
# $ twc domain sub remove                                       #
# ------------------------------------------------------------- #


@domain_subdomain.command("remove", "rm")
def domain_rm_subdomain(
    subdomain: str = typer.Argument(..., metavar="FQDN"),
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
    second_ld: Optional[bool] = typer.Option(
        False,
        "--2ld",
        help="Parse subdomain as 2LD.",
    ),
    yes: Optional[bool] = yes_option,
):
    """Delete subdomain with they DNS records."""
    if not yes:
        typer.confirm("This action cannot be undone. Continue?", abort=True)
    client = create_client(config, profile)

    if second_ld:
        offset = 3
    else:
        offset = 2

    domain_name = ".".join(subdomain.split(".")[-offset:])
    subdomain = ".".join(subdomain.split(".")[:-offset])

    response = client.delete_subdomain(domain_name, subdomain)
    if response.status_code == 204:
        print(subdomain)
    else:
        sys.exit(fmt.printer(response))
