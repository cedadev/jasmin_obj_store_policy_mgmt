#!/usr/bin/env python

"""Tests for `jasmin_obj_store_policy_mgmt` package."""

__author__ = """Philip Kershaw"""
__contact__ = 'philip.kershaw@stfc.ac.uk'
__copyright__ = "Copyright 2021 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
import os
from typing import List
import pytest

from click.testing import CliRunner
from jasmin.obj_store.policy_mgmt import cli
from jasmin.obj_store.policy_mgmt.policy import S3Policy, TS3PolicyStatement, \
    TS3Principal


@pytest.fixture
def policy_string() -> str:
    return """{
    "Version": "2008-10-17",
    "Id": "test-policy-2",
    "Statement": [
      {
        "Sid": "1: Standard access for users",
        "Effect": "Allow",
        "Principal": {
          "user": [],
          "group": [
            "test-members"
          ]
        },
        "Action": [
          "ListBucket"
        ],
        "Resource": "*"
      }
    ]
  }"""


def test_command_line_interface() -> None:
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 2 # Correct exit code for no CLI args passed
    assert 'Error' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert 'Usage' in help_result.output


def test_serialise_policy() -> None:
    version: str = S3Policy.VERSION
    statement: TS3PolicyStatement = {
        "Sid": "My Statement", 
        "Effect": "Allow",
        "Principal": TS3Principal(user="me", group=["admins"]),
        "Action": ["ListBucket"],
        "Resource": "*"
    }

    statement_list: List[TS3PolicyStatement] = [statement]

    policy = S3Policy(id="My Policy", statement=statement_list, version=version)
    print(policy.serialisation)

    assert "My Policy" in policy.serialisation


def test_parse_policy_from_file() -> None:
    this_dir: str = os.path.dirname(__file__)
    policy_filepath: str = os.path.join(this_dir, "access_policy.json")
    policy = S3Policy.from_policy_file(policy_filepath)

    assert "Standard access for users" in policy.serialisation


def test_parse_policy_from_string(policy_string: str) -> None:
    assert policy_string
    policy = S3Policy.from_string(policy_string)

    assert "Standard access for users" in policy.serialisation