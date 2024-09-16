"""Manage Timeweb Cloud account."""

from typing import Optional
from pathlib import Path
from textwrap import dedent

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


whoami = TyperAlias(help="Display current login.", no_args_is_help=False)


# ------------------------------------------------------------- #
# $ twc whoami                                                  #
# ------------------------------------------------------------- #


@whoami.callback(invoke_without_command=True)
def whoami_callback(
    verbose: Optional[bool] = verbose_option,
    config: Optional[Path] = config_option,
    profile: Optional[str] = profile_option,
    output_format: Optional[str] = output_format_option,
):
    """Display current login."""
    client = create_client(config, profile)
    response = client.get_account_status()
    login = response.json()["status"]["login"]
    fmt.printer(
        {"login": login, "profile": profile},
        output_format=output_format,
        func=lambda data: print(data["login"]),
    )


# ------------------------------------------------------------- #


account = TyperAlias(help=__doc__)
account_access = TyperAlias(help="Manage account access restrictions.")
account.add_typer(account_access, name="access")


# ------------------------------------------------------------- #
# $ twc account status                                          #
# ------------------------------------------------------------- #


def print_account_status(response: Response):
    """Print table with account info."""
    status = response.json()["status"]
    output = dedent(
        f"""
        Login: {status["login"]}
        Provider: {status["company_info"]["name"]}
        Yandex.Metrika ID: {status["ym_client_id"]}
        Blocked: {status["is_blocked"]}
        Permanently blocked: {status["is_permanent_blocked"]}
        Send bill emails: {status["is_send_bill_letters"]}
        Password changed at: {status["last_password_changed_at"]}
        """
    ).strip()
    print(output)


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
    finances = response.json()["finances"]
    output = dedent(
        f"""
        Balance: {finances["balance"]}
        Currency: {finances["currency"]}
        Discount: {finances["discount_percent"]}
          Discount ends at: {finances["discount_end_date_at"]}
        Hourly cost: {finances["hourly_cost"]}
        Hourly fee: {finances["hourly_fee"]}
        Hours left: {finances["hours_left"]}
        Monthly cost: {finances["monthly_cost"]}
        Monthly fee: {finances["monthly_fee"]}
        Total paid: {finances["total_paid"]}
        Autopay card: {finances["autopay_card_info"]}
        """
    ).strip()
    print(output)


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
                print(f"  {ip_addr}")
        else:
            print("IP restrictions: disabled")

    if by_country:
        if restrictions["is_country_restrictions_enabled"]:
            print("Country restrictions: enabled")
            print("Allowed countries:")
            for country in restrictions["white_list"]["countries"]:
                print(f"  {country}")
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
