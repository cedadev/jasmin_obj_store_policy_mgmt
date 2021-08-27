"""Test module for interacting with the Caringo DataCore API."""
__author__ = """Philip Kershaw"""
__contact__ = 'philip.kershaw@stfc.ac.uk'
__copyright__ = "Copyright 2021 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
import os
import json
import pytest

from ..caringo_clnt import CaringoClnt

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

    if creds.get('passwd') is None:
        import getpass
        creds['passwd'] = getpass.getpass(prompt="password: ")

    return creds

@pytest.fixture
def settings_filepath(this_dir: str) -> str:
    return os.path.join(this_dir, "caringo-settings.json")

@pytest.fixture
def settings(settings_filepath: str) -> dict:
    with open(settings_filepath) as settings_file:
        settings = json.load(settings_file)

    return settings

def test_init(creds: dict, settings: dict) -> CaringoClnt:
    clnt = CaringoClnt(settings['base_uri'], creds['username'], creds['passwd'])
    assert clnt

    return clnt

def test_get_domain_etc(creds: dict, settings: dict) -> None:
    clnt = test_init(creds, settings)
    etc_doc = clnt.get_domain_etc(settings['tenancy_name'], 
                                settings['domain_name'])
    assert etc_doc

def test_get_domain_policy(creds: dict, settings: dict) -> None:
    clnt = test_init(creds, settings)
    policy = clnt.get_domain_policy(settings['tenancy_name'], 
                                    settings['domain_name'])
    assert policy
