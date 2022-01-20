"""Console script for jasmin_obj_store_policy_mgmt."""

__author__ = """Philip Kershaw"""
__contact__ = "philip.kershaw@stfc.ac.uk"
__copyright__ = "Copyright 2021 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
import json
import logging
import os
import sys
from collections import namedtuple
from enum import Enum

import click
import requests

from jasmin.obj_store.policy_mgmt.caringo_clnt import (
    AuthenticationError,
    CaringoClnt,
    RequestError,
)
from jasmin.obj_store.policy_mgmt.s3_clnt import S3Policy

log = logging.getLogger(__name__)

THIS_DIR = os.path.dirname(__file__)
DEF_CREDS_FILENAME = "creds.json"
DEF_CREDS_FILEPATH = os.path.join(THIS_DIR, DEF_CREDS_FILENAME)


class ExitCode(Enum):
    SUCCESS = 0
    ERROR = 1
    NO_ARGS = 2


CliCtx = namedtuple("CliCtx", ["clnt"])


@click.group()
@click.option("-b", "--base-uri", help="URI to object store domain")
@click.option("-d", "--domain-name", help="Domain Name")
@click.option("-t", "--tenancy-name", help="Tenancy Name")
@click.option(
    "-u",
    "--username",
    help="username for access to object store API. Alternatively get from file "
    "set by --creds-filepath option",
)
@click.option(
    "-c",
    "--creds-filepath",
    help='File path to JSON-formatted file containing "username" and "passwd"',
)
@click.option(
    "-f",
    "--config-filepath",
    help='File path to YAML-formatted file containing "baseuri", "domain_name" '
    'and "tenancy_name"',
)
@click.option(
    "-l", "--log-filepath", default=None, help="Write logging output to a log file"
)
@click.pass_context
def main(  # noqa: C901
    ctx: click.Context,
    base_uri: str,
    domain_name: str,
    tenancy_name: str,
    username: str,
    creds_filepath: str,
    config_filepath: str,
    log_filepath: str,
) -> ExitCode:
    """Console script for Object store policy management utility."""

    if log_filepath is not None:
        logging.basicConfig(
            filename=log_filepath,
            format="%(asctime)s %(name)s [%(levelname)s]: %(message)s",
            level=logging.INFO,
        )
    else:
        logging.basicConfig(level=logging.CRITICAL)

    passwd = None

    if creds_filepath is not None:
        log.info("Checking object store credentials file ...")
        with open(os.path.expandvars(creds_filepath)) as creds_file:
            creds = json.load(creds_file)

        username = creds["username"]
        passwd = creds.get("passwd")

    elif username is None:
        log.info("No username set. Exiting...")
        raise click.MissingParameter("No username set")

    # Password may be omitted from credentials file and obtained from CLI
    # prompt instead
    elif passwd is None:
        import getpass

        passwd = getpass.getpass(prompt="Object Store API Password: ")

    if config_filepath is not None:
        settings = CaringoClnt.parse_config_file(config_filepath)
        if settings.get("base_uri") is not None:
            base_uri = settings["base_uri"]

        if settings.get("domain_name") is not None:
            domain_name = settings["domain_name"]

        if settings.get("tenancy_name") is not None:
            tenancy_name = settings["tenancy_name"]

    if base_uri is None:
        raise click.MissingParameter("No base URI set")

    if domain_name is None:
        raise click.MissingParameter("No domain name set")

    if tenancy_name is None:
        raise click.MissingParameter("No tenancy name set")

    try:
        clnt = CaringoClnt(
            base_uri,
            username,
            passwd,
            domain_name=domain_name,
            tenancy_name=tenancy_name,
        )

    except requests.exceptions.RequestException as req_exec:
        log.exception("")
        raise SystemExit(f"Obtaining authentication token: {req_exec}")

    except AuthenticationError as auth_exc:
        log.exception("")
        raise SystemExit(str(auth_exc))

    ctx.obj = CliCtx(clnt)

    return ExitCode.SUCCESS


@click.command()
@click.pass_obj
def get(ctx: CliCtx) -> None:
    """Retrieve an existing policy"""
    try:
        policy = ctx.clnt.get_domain_policy()
    except RequestError as req_exc:
        log.exception("")
        raise SystemExit(str(req_exc))

    print(policy.serialisation)


@click.command()
@click.option(
    "-p", "--policy-filepath", required=True, help="S3 Policy file to send as an update"
)
@click.pass_obj
def update(ctx: CliCtx, policy_filepath: str) -> None:
    """Update a policy"""

    try:
        s3_policy = S3Policy.from_file(policy_filepath)
    except Exception as exc:
        log.exception("")
        raise SystemExit(str(exc))

    try:
        ctx.clnt.put_domain_policy(s3_policy)
    except RequestError as req_exc:
        log.exception("")
        raise SystemExit(str(req_exc))


main.add_command(get)
main.add_command(update)


if __name__ == "__main__":
    status = main()
    sys.exit(status)  # pragma: no cover
