"""Test module for interacting with the Caringo DataCore API."""
__author__ = """Philip Kershaw"""
__contact__ = "philip.kershaw@stfc.ac.uk"
__copyright__ = "Copyright 2021 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
import json
import os

import pytest

from jasmin.obj_store.policy_mgmt.caringo_clnt import CaringoClnt
from jasmin.obj_store.policy_mgmt.policy import S3Policy


@pytest.fixture
def this_dir() -> str:
    return os.path.dirname(__file__)


@pytest.fixture
def creds_filepath(this_dir: str) -> str:
    return os.path.join(this_dir, "caringo-creds.json")


@pytest.fixture
def creds(creds_filepath: str) -> dict:
    with open(creds_filepath) as creds_file:
        creds = json.load(creds_file)

    if creds.get("passwd") is None:
        import getpass

        creds["passwd"] = getpass.getpass(prompt="password: ")

    return creds


@pytest.fixture
def s3_policy_filepath(this_dir: str) -> str:
    return os.path.join(this_dir, "access_policy.json")


@pytest.fixture
def settings_filepath(this_dir: str) -> str:
    return os.path.join(this_dir, "caringo-settings.yaml")


@pytest.fixture
def settings(settings_filepath: str) -> dict:
    settings = CaringoClnt.parse_config_file(settings_filepath)

    return settings


@pytest.fixture
def s3_policy(s3_policy_filepath: str) -> S3Policy:
    s3_policy = S3Policy.from_file(s3_policy_filepath)
    return s3_policy


def test_get_s3_policy_from_dict(s3_policy_filepath: str) -> S3Policy:
    with open(s3_policy_filepath) as s3_policy_file:
        s3_policy_dict = json.load(s3_policy_file)

    s3_policy = S3Policy.from_dict(s3_policy_dict)
    return s3_policy


def test_init(creds: dict, settings: dict) -> CaringoClnt:
    clnt = CaringoClnt(
        settings["base_uri"],
        creds["username"],
        creds["passwd"],
        tenancy_name=settings["tenancy_name"],
        domain_name=settings["domain_name"],
    )
    assert clnt

    return clnt


def test_from_config_file(settings_filepath: str, creds_filepath: str) -> None:
    # Inject setting for creds file environment variable
    clnt = CaringoClnt.from_config(settings_filepath, creds_filepath)

    assert clnt


def test_get_domain_etc(creds: dict, settings: dict) -> None:
    clnt = test_init(creds, settings)
    etc_doc = clnt.get_domain_etc()
    assert etc_doc


def test_get_domain_policy(creds: dict, settings: dict) -> None:
    clnt = test_init(creds, settings)
    policy = clnt.get_domain_policy()
    assert policy


def test_put_domain_policy(creds: dict, settings: dict, s3_policy: S3Policy) -> None:
    clnt = test_init(creds, settings)

    clnt.put_domain_policy(s3_policy)
