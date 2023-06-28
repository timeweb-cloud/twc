"""Manage domain dns record.

NOTE: !WARNING HELP PLEASE
"""


from typing import Optional
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
)


domain = TyperAlias(help=__doc__, short_help="Manage domains.")
domain_subdomains = TyperAlias(help="Manage subdomains.")
domain_record = TyperAlias(help="Manage DNS records.")
domain.add_typer(domain_record, name="record", aliases=["record", "rec"])
domain.add_typer(
    domain_subdomains, name="subdomain", aliases=["subdomain", "sub"]
)

# ------------------------------------------------------------- #
# $ twc domain list                                             #
# ------------------------------------------------------------- #


def print_domains(response: Response, filters: Optional[str] = None):
    """Print table with domains list."""
    domains = response.json()["domains"]
    if filters:
        domains = fmt.filter_list(domains, filters)
    table = fmt.Table()
    table.header(
        [
            "FQDN",
            "ID",
            "IP",
            "STATUS",
            "EXPIRATION",
        ]
    )
    for domain_json in domains:
        table.row(
            [
                domain_json["fqdn"],
                domain_json["id"],
                domain_json["linked_ip"],
                domain_json["domain_status"],
                domain_json["expiration"],
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
):
    """List domains."""
    client = create_client(config, profile)
    response = client.get_domains()
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_domains,
    )


# ------------------------------------------------------------- #
# $ twc domain list-all                                         #
# ------------------------------------------------------------- #


def print_domains_all(response: Response, filters: Optional[str] = None):
    """Print domains and subdomains."""
    domains = response.json()["domains"]
    if filters:
        domains = fmt.filter_list(domains, filters)

    table = fmt.Table()
    table.header(
        [
            "FQDN",
            "ID",
            "IP",
            "SUBDOMAIN",
        ]
    )
    for domain_json in domains:
        table.row(
            [
                domain_json["fqdn"],
                domain_json["id"],
                domain_json["linked_ip"],
                "",
            ]
        )
        for subdomain in domain_json["subdomains"]:
            table.row(
                [
                    subdomain["fqdn"],
                    subdomain["id"],
                    subdomain["linked_ip"],
                    "true",
                ]
            )
        table.row(["", "", "", ""])

    table.print()


@domain.command("list-all", "la")
def domain_list_all(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
):
    """List all domains."""
    client = create_client(config, profile)
    response = client.get_domains()
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_domains_all,
    )


# ------------------------------------------------------------- #
# $ twc domain info domain.io                                   #
# ------------------------------------------------------------- #


def print_domain_info(response: Response, filters: Optional[str] = None):
    """Print domain info."""
    domain_json = response.json()["domain"]

    output = (
        f'Domain: {domain_json["fqdn"]}\n'
        + f'Exp date: {domain_json["expiration"]}\n'
        + f'Technical: {domain_json["is_technical"]}\n'
        + f'Provider: {domain_json["provider"]}\n'
        + "Subdomain: \n"
        + "".join(
            (
                f'  Domain: {sub["fqdn"]}\n'
                + f'    ID: {sub["id"]}\n'
                + f'    IP: {sub["linked_ip"]}\n'
            )
            for sub in domain_json["subdomains"]
        )
    )
    print(output)


@domain.command("info")
def domain_info(
    domain_name: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
):
    """Get domain info."""
    client = create_client(config, profile)
    response = client.get_domain(domain_name)
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_domain_info,
    )


# ------------------------------------------------------------- #
# $ twc domain rm domain.io                                     #
# ------------------------------------------------------------- #


@domain.command("delete", "del", "rm")
def domain_delete(
    domain_name: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
):
    """List Object Storage presets."""
    client = create_client(config, profile)
    response = client.delete_domain(domain_name)
    fmt.printer(
        response,
        output_format=output_format,
        func=(lambda x,: print("Complite!") if x.status_code == 204 else None),
    )


# ------------------------------------------------------------- #
# $ twc domain add domain.io                                    #
# ------------------------------------------------------------- #


@domain.command("add")
def domain_add(
    domain_name: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
):
    """Add domain to account."""
    client = create_client(config, profile)
    response = client.add_domain(domain_name)
    fmt.printer(
        response,
        output_format=output_format,
        func=(lambda x: print("Complite!") if x.status_code == 204 else None),
    )


# ------------------------------------------------------------- #
# $ twc domain record list domain.io                            #
# ------------------------------------------------------------- #


def print_domain_record_list(
    response: Response,
    not_ignore_subdomains,
    response_domain,
    filters: Optional[str] = None,
):
    """Print domain records."""
    domains = response.json()["dns_records"]

    if not not_ignore_subdomains:
        domains = filter(lambda x: "subdomain" not in x["data"], domains)

    if filters:
        domains = fmt.filter_list(domains, filters)

    table = fmt.Table()
    table.header(
        [
            *(["SUB"] if not_ignore_subdomains else []),
            "TYPE",
            "VALUE",
            "ID",
        ]
    )

    for domain_json in domains:
        table.row(
            [
                *(
                    [domain_json["data"]["subdomain"]]
                    if "subdomain" in domain_json["data"]
                    else [""]
                    if not_ignore_subdomains
                    else []
                ),
                domain_json["type"],
                domain_json["data"]["value"],
                domain_json["id"],
            ]
        )
    print(f"DOMAIN: {response_domain}\n")
    table.print()


@domain_record.command("list", "ls")
def domain_records_list(
    domain_name: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
    not_ignore_subdomains: bool = typer.Option(
        False,
        "--not-ignore-subdomains",
        case_sensitive=False,
        help="Not ignoring TXT subdomain records.",
    ),
):
    """List dns records on domain."""
    client = create_client(config, profile)
    response = client.get_domain_dns_records(domain_name)

    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_domain_record_list,
        not_ignore_subdomains=not_ignore_subdomains,
        response_domain=domain_name,
    )


# ------------------------------------------------------------- #
# $ twc domain record rm domain.io record_id                    #
# ------------------------------------------------------------- #


@domain_record.command("delete", "rm")
def domain_remove_dns_record(
    domain_name: str,
    record_id: int,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
):
    """Delete one dns record on domain."""
    client = create_client(config, profile)
    response = client.delete_domain_dns_record(domain_name, record_id)

    fmt.printer(
        response,
        output_format=output_format,
        func=(lambda x: print("Complite!") if x.status_code == 204 else None),
        response_domain=domain_name,
    )


# ------------------------------------------------------------- #
# $ twc domain record rma domain.io                             #
# ------------------------------------------------------------- #


@domain_record.command("delete-all", "rma")
def domain_remove_all_dns_record(
    domain_json: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    not_ignore_subdomains: bool = typer.Option(
        False,
        "--not-ignore-subdomains",
        case_sensitive=False,
        help="Not ignoring TXT subdomain records.",
    ),
    filters: Optional[str] = filter_option,
):
    """Delete all dns records on domain."""
    client = create_client(config, profile)

    response = client.get_domain_dns_records(domain_json)
    domains = response.json()["dns_records"]

    if not not_ignore_subdomains:
        domains = filter(lambda x: "subdomain" not in x["data"], domains)

    for record in domains:
        client.delete_domain_dns_record(domain_json, record["id"])

    fmt.printer(
        response,
        output_format=output_format,
        func=(lambda x: print("Complite!") if x.status_code == 204 else None),
    )


# ------------------------------------------------------------- #
# $ twc domain record add domain.io                             #
# ------------------------------------------------------------- #


def print_dns_record(
    response: Response, response_domain: str, filters: Optional[str] = None
):
    """Print dns record."""
    domain_record_json = response.json()["dns_record"]

    table = fmt.Table()
    table.header(
        [
            "TYPE",
            "VALUE",
            "ID",
        ]
    )

    table.row(
        [
            domain_record_json["type"],
            domain_record_json["data"]["value"],
            domain_record_json["id"],
        ]
    )
    print(f"DOMAIN: {response_domain}\n add record\n")
    table.print()


@domain_record.command("add")
def domain_add_dns_records(
    domain_name: str,
    dns_record_type: DNSRecordType,
    value: str,
    priority: Optional[int] = None,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
):
    """Add dns record."""
    client = create_client(config, profile)
    subdomain_name = None

    if len(domain_name.split(".")) > 2:
        subdomain_name = domain_name
        domain_name = ".".join(subdomain_name.split(".")[-2:])
        print(domain_name)
        print(subdomain_name)

    response = client.add_domain_dns_record(
        domain_name, dns_record_type, value, subdomain_name, priority
    )
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_dns_record,
        response_domain=domain_name,
    )


# ------------------------------------------------------------- #
# $ twc domain record update domain.io record_id type value     #
# ------------------------------------------------------------- #


@domain_record.command("update", "up")
def domain_update_dns_records(
    domain_name: str,
    record_id: int,
    dns_record_type: DNSRecordType,
    value: str,
    subdomain: Optional[str] = None,
    priority: Optional[int] = None,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
):
    """Update dns record on record_id."""
    client = create_client(config, profile)

    response = client.update_domain_dns_record(
        domain_name, record_id, dns_record_type, value, subdomain, priority
    )
    fmt.printer(
        response,
        output_format=output_format,
        filters=filters,
        func=print_dns_record,
        response_domain=domain_name,
    )


# ------------------------------------------------------------- #
# $ twc domain sub add subdomain.domain.io                      #
# ------------------------------------------------------------- #


@domain_subdomains.command("add")
def domain_add_subdomain(
    subdomain_name: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
):
    """Delete one dns record on domain."""
    client = create_client(config, profile)

    domain_name = ".".join(subdomain_name.split(".")[-2:])

    response = client.add_subdomain(
        domain_name, ".".join(subdomain_name.split(".")[:-2])
    )

    fmt.printer(
        response,
        output_format=output_format,
        func=(lambda x,: print("Complite!") if x.status_code == 201 else None),
    )


# ------------------------------------------------------------- #
# $ twc domain sub rm subdomain.domain.io                      #
# ------------------------------------------------------------- #


@domain_subdomains.command("delete", "rm")
def domain_add_subdomain(
    subdomain_name: str,
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    filters: Optional[str] = filter_option,
):
    """Delete one dns record on domain."""
    client = create_client(config, profile)

    response = client.delete_subdomain(subdomain_name)

    fmt.printer(
        response,
        output_format=output_format,
        func=(lambda x,: print("Complite!") if x.status_code == 204 else None),
    )
