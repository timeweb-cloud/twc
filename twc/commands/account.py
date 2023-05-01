"""Manage Timeweb Cloud account."""

from typing import Optional
from pathlib import Path

import typer
from requests import Response

from twc import fmt
from twc.typerx import TyperAlias
from twc.apiwrap import create_client
from .common import (
    verbose_option,
    config_option,
    profile_option,
    output_format_option,
)


account = TyperAlias(help=__doc__)
account_access = TyperAlias(help="Manage account access restrictions.")
account.add_typer(account_access, name="access")


# ------------------------------------------------------------- #
# $ twc account status                                          #
# ------------------------------------------------------------- #


def print_account_status(response: Response):
    """Print table with account info."""
    table = fmt.Table()
    status = response.json()["status"]
    translated_keys = {
        "company_info": "Company",
        "ym_client_id": "Yandex.Metrika client ID",
        "is_blocked": "Blocked",
        "is_permanent_blocked": "Permanently blocked",
        "is_send_bill_letters": "Send bill emails",
        "last_password_changed_at": "Password changed at",
    }
    for key in status.keys():
        try:
            if key == "company_info":
                table.row([translated_keys[key], ":", status[key]["name"]])
            else:
                table.row([translated_keys[key], ":", status[key]])
        except KeyError:
            pass
    table.print()


@account.command("status")
def account_status(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """Display account status."""
    client = create_client(config, profile)
    response = client.get_account_status()
    fmt.printer(
        response, output_format=output_format, func=print_account_status
    )


# ------------------------------------------------------------- #
# $ twc account finances                                        #
# ------------------------------------------------------------- #


def print_account_finances(response: Response):
    """Print table with finances info."""
    table = fmt.Table()
    finances = response.json()["finances"]
    translated_keys = {
        "balance": "Balance",
        "currency": "Currency",
        "discount_end_date_at": "Discount ends at",
        "discount_percent": "Discount",
        "hourly_cost": "Hourly cost",
        "hourly_fee": "Hourly fee",
        "monthly_cost": "Monthly cost",
        "monthly_fee": "Monthly fee",
        "total_paid": "Total paid",
        "hours_left": "Hours left",
        "autopay_card_info": "Autopay Card",
    }
    for key in finances.keys():
        try:
            table.row([translated_keys[key], ":", finances[key]])
        except KeyError:
            pass
    table.print()


@account.command("finances")
def account_finances(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """Get finances."""
    client = create_client(config, profile)
    response = client.get_account_finances()
    fmt.printer(
        response, output_format=output_format, func=print_account_finances
    )


# ------------------------------------------------------------- #
# $ twc account access restrictions                             #
# ------------------------------------------------------------- #


def print_restrictions_status(
    response: Response, by_ip: bool, by_country: bool
):
    """Print restrictions info."""
    restrictions = response.json()

    if not by_ip and not by_country:
        by_ip = by_country = True

    if by_ip:
        if restrictions["is_ip_restrictions_enabled"]:
            print("IP restrictions: enabled")
            print("Allowed IPs:")
            for ip_addr in restrictions["white_list"]["ips"]:
                print(f" - {ip_addr}")
        else:
            print("IP restrictions: disabled")

    if by_country:
        if restrictions["is_country_restrictions_enabled"]:
            print("Country restrictions: enabled")
            print("Allowed countries:")
            for country in restrictions["white_list"]["countries"]:
                print(f" - {country}")
        else:
            print("Country restrictions: disabled")


@account_access.command("restrictions")
def restrictions_status(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
    by_ip: Optional[bool] = typer.Option(
        False, "--by-ip", help="Display IP restrictions."
    ),
    by_country: Optional[bool] = typer.Option(
        False, "--by-country", help="Display country restrictions."
    ),
):
    """View access restrictions status."""
    client = create_client(config, profile)
    response = client.get_account_restrictions()
    fmt.printer(
        response,
        output_format=output_format,
        func=print_restrictions_status,
        by_ip=by_ip,
        by_country=by_country,
    )
