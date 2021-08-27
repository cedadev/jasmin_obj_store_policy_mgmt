"""Integration tests for `jasmin_obj_store_policy_mgmt` package."""

__author__ = """Philip Kershaw"""
__contact__ = 'philip.kershaw@stfc.ac.uk'
__copyright__ = "Copyright 2021 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
import os
import json

import pytest

from jasmin.obj_store.policy_mgmt.policy import S3Policy
from jasmin.obj_store.policy_mgmt.clnt import S3PolicyClnt

@pytest.fixture
def this_dir() -> str:
    return os.path.dirname(__file__)

@pytest.fixture
def creds_filepath(this_dir: str) -> str:
    return os.path.join(this_dir, "creds.json")

@pytest.fixture
def creds(creds_filepath: str) -> dict:
    with open(creds_filepath) as creds_file:
        creds = json.load(creds_file)

    return creds

@pytest.fixture
def settings_filepath(this_dir: str) -> str:
    return os.path.join(this_dir, "settings.json")

@pytest.fixture
def settings(settings_filepath: str) -> dict:
    with open(settings_filepath) as settings_file:
        settings = json.load(settings_file)

    return settings

def test_get_access_policy(creds: dict, settings: dict) -> None:
    """Try retrieving an existing policy"""
    policy_clnt = S3PolicyClnt(settings["endpoint"], key=creds["key"], 
                            secret=["secret"])
                            
    policy = policy_clnt.get(settings['bucket_name'])

    assert "Sid" in policy.serialisation
