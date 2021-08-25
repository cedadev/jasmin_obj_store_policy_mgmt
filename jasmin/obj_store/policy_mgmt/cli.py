"""Console script for jasmin_obj_store_policy_mgmt."""

__author__ = """Philip Kershaw"""
__contact__ = 'philip.kershaw@stfc.ac.uk'
__copyright__ = "Copyright 2020 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
import sys
import logging
import os
import json

import click


log = logging.getLogger(__name__)

THIS_DIR = os.path.dirname(__file__)
DEF_CREDS_FILENAME = "creds.json"
DEF_CREDS_FILEPATH = os.path.join(THIS_DIR, DEF_CREDS_FILENAME)

@click.command()
@click.option('-u', '--s3-uri', required=True,
    help='URI to S3 object store (not including bucket or path)')
@click.option('-c', '--creds-filepath', required=True,
    help='File path to JSON-formatted file containing S3 "key" and "secret"')
@click.option('-p', '--policy-filepath', required=True,
    help='Policy file to process')
@click.option('-l', '--log-filepath', default=None,
    help='Write logging output to a log file')
def main(s3_uri: str, creds_filepath: str, policy_filepath: str, 
        log_filepath: str) -> int:
    """Console script for Object store policy management utility."""

    if log_filepath is not None:
        logging.basicConfig(filename=log_filepath,
                    format='%(asctime)s %(name)s [%(levelname)s]: %(message)s',
                    encoding='utf-8', 
                    level=logging.INFO)
        
    log.info("Checking object store credentials ...")
    with open(os.path.expandvars(creds_filepath)) as creds_file:
        creds = json.load(creds_file)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
