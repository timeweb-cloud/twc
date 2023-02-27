"""Account management commands."""

import click

from twc import fmt
from . import (
    create_client,
    handle_request,
    options,
    GLOBAL_OPTIONS,
    OUTPUT_FORMAT_OPTION,
)


@handle_request
def _account_finances(client):
    return client.get_account_finances()


@handle_request
def _account_status(client):
    return client.get_account_status()


@handle_request
def _restrictions_status(client):
    return client.get_account_restrictions()


# ------------------------------------------------------------- #
# $ twc account                                                 #
# ------------------------------------------------------------- #


@click.group()
@options(GLOBAL_OPTIONS[:2])
def account():
    """Manage Timeweb Cloud account."""


# ------------------------------------------------------------- #
# $ twc account status                                          #
# ------------------------------------------------------------- #


def print_account_status(response: object):
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


@account.command("status", help="Get account status.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
def account_status(config, profile, verbose, output_format):
    client = create_client(config, profile)
    response = _account_status(client)
    fmt.printer(
        response, output_format=output_format, func=print_account_status
    )


# ------------------------------------------------------------- #
# $ twc account finances                                        #
# ------------------------------------------------------------- #


def print_account_finances(response: object):
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


@account.command("finances", help="Get finances.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
def account_finances(config, profile, verbose, output_format):
    client = create_client(config, profile)
    response = _account_finances(client)
    fmt.printer(
        response, output_format=output_format, func=print_account_finances
    )


# ------------------------------------------------------------- #
# $ twc account access                                          #
# ------------------------------------------------------------- #


@account.group()
@options(GLOBAL_OPTIONS[:2])
def access():
    """Manage account access restrictions."""


# ------------------------------------------------------------- #
# $ twc account access restrictions                             #
# ------------------------------------------------------------- #


def print_restrictions_status(response: object, by_ip: bool, by_country: bool):
    restrictions = response.json()

    if not by_ip and not by_country:
        by_ip = by_country = True

    if by_ip:
        if restrictions["is_ip_restrictions_enabled"]:
            click.echo("IP restrictions: enabled")
            click.echo("Allowed IPs:")
            for ip_addr in restrictions["white_list"]["ips"]:
                click.echo(f" - {ip_addr}")
        else:
            click.echo("IP restrictions: disabled")

    if by_country:
        if restrictions["is_country_restrictions_enabled"]:
            click.echo("Country restrictions: enabled")
            click.echo("Allowed countries:")
            for country in restrictions["white_list"]["countries"]:
                click.echo(f" - {country}")
        else:
            click.echo("Country restrictions: disabled")


@access.command("restrictions", help="View access restrictions status.")
@options(GLOBAL_OPTIONS)
@options(OUTPUT_FORMAT_OPTION)
@click.option("--by-ip", is_flag=True, help="Display IP restrictions.")
@click.option(
    "--by-country", is_flag=True, help="Display country restrictions."
)
def restrictions_status(
    config, profile, verbose, output_format, by_ip, by_country
):
    client = create_client(config, profile)
    response = _restrictions_status(client)
    fmt.printer(
        response,
        output_format=output_format,
        func=print_restrictions_status,
        by_ip=by_ip,
        by_country=by_country,
    )
