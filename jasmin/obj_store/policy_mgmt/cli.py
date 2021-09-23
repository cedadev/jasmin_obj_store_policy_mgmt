"""Console script for jasmin_obj_store_policy_mgmt."""

__author__ = """Philip Kershaw"""
__contact__ = 'philip.kershaw@stfc.ac.uk'
__copyright__ = "Copyright 2021 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
import sys
import logging
import os
import json
import typing
from typing import Union
from collections import namedtuple
from enum import Enum
import click

from jasmin.obj_store.policy_mgmt.caringo_clnt import CaringoClnt

log = logging.getLogger(__name__)

THIS_DIR = os.path.dirname(__file__)
DEF_CREDS_FILENAME = "creds.json"
DEF_CREDS_FILEPATH = os.path.join(THIS_DIR, DEF_CREDS_FILENAME)

class ExitCode(Enum):
    SUCCESS = 0
    ERROR = 1
    NO_ARGS = 2

CliCtx = namedtuple('CliCtx', ['clnt', 'domain_name', 'tenancy_name'])

@click.group()
@click.option('-b', '--base-uri', 
    help='URI to object store domain')
@click.option('-d', '--domain_name', required=True,
    help='Domain Name')
@click.option('-t', '--tenancy_name', required=True,
    help='Tenancy Name')
@click.option('-u', '--username', 
    help='username for access to object store API. Alternatively get from file '
    'set by --creds-filepath option')
@click.option('-c', '--creds-filepath', 
    help='File path to JSON-formatted file containing "key" and "secret"')
@click.option('-l', '--log-filepath', default=None,
    help='Write logging output to a log file')
@click.pass_context
def main(ctx: click.Context, base_uri: str, domain_name: str, tenancy_name: str, 
        username: str, creds_filepath: str, log_filepath: str) -> ExitCode:
    """Console script for Object store policy management utility."""
    
    if log_filepath is not None:
        logging.basicConfig(filename=log_filepath,
                    format='%(asctime)s %(name)s [%(levelname)s]: %(message)s',
                    level=logging.INFO)

    if creds_filepath is not None:
        log.info("Checking object store credentials file ...")
        with open(os.path.expandvars(creds_filepath)) as creds_file:
            creds = json.load(creds_file)

        username = creds['username']
        passwd = creds.get("passwd")

    elif username is None:
        log.info("No credentials set. Exiting...")
        return ExitCode.ERROR

    # Password may be omitted from credentials file and obtained from CLI 
    # prompt instead
    if passwd is None:
        import getpass
        passwd = getpass.getpass(prompt="Object Store API Password: ")
    
    clnt = CaringoClnt(base_uri, username, passwd)
    ctx.obj = CliCtx(clnt, domain_name, tenancy_name)

    return ExitCode.SUCCESS

@click.command()
@click.pass_obj
def get(ctx: CliCtx) -> None:
    click.echo('get command')
    
    policy = ctx.clnt.get_domain_policy(ctx.tenancy_name, ctx.domain_name)
    print(policy.serialisation)

@click.command()
def put(ctx: CliCtx, policy_filepath: str) -> None:
    click.echo('put command')

main.add_command(get)
main.add_command(put)


if __name__ == "__main__":
    status = main()
    sys.exit(status) # pragma: no cover
