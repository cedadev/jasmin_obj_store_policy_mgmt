#!/usr/bin/env python

"""Tests for `jasmin_obj_store_policy_mgmt` package."""

__author__ = """Philip Kershaw"""
__contact__ = "philip.kershaw@stfc.ac.uk"
__copyright__ = "Copyright 2021 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
import json
import os
import typing
from typing import List

import pytest
from click.testing import CliRunner

from jasmin.obj_store.policy_mgmt import cli
from jasmin.obj_store.policy_mgmt.policy import (
    S3Policy,
    TS3PolicyStatement,
    TS3Principal,
)


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


@pytest.fixture
def policy_dict(policy_string: str) -> dict:
    return json.loads(typing.cast(str, policy_string))


def test_cli_basic_invocation() -> None:
    """Basic tests of the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0  # Correct exit code for no CLI args passed
    assert "Usage" in result.output

    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert "Usage" in help_result.output

    badcmd_result = runner.invoke(cli.main, ["badcmd"])
    assert badcmd_result.exit_code == 2
    assert "Error: No such command" in badcmd_result.output


def test_cli_cmds() -> None:
    """Test the CLI command options."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ["get"])
    assert result.exit_code == 2  # Correct exit code for no CLI args passed
    assert "Error:" in result.output

    help_result = runner.invoke(cli.main, ["get", "--help"])
    assert help_result.exit_code == 2
    assert "Options:" in result.output

    cli_opts = [
        "--base_uri",
        "http://localhost:3000/" "-u",
        "user" "--tenancy_name",
        "mytenancy",
        "--domain_name",
        "mydomain",
        "get",
    ]
    help_result = runner.invoke(cli.main, cli_opts)
    assert help_result.exit_code == 2
    assert "Options:" in result.output


def test_serialise_policy() -> None:
    version: str = S3Policy.VERSION
    statement: TS3PolicyStatement = {
        "Sid": "My Statement",
        "Effect": "Allow",
        "Principal": TS3Principal(user="me", group=["admins"]),
        "Action": ["ListBucket"],
        "Resource": "*",
    }

    statement_list: List[TS3PolicyStatement] = [statement]

    policy = S3Policy(id="My Policy", statement=statement_list, version=version)
    print(policy.serialisation)

    assert "My Policy" in policy.serialisation


def test_parse_policy_from_file() -> None:
    this_dir: str = os.path.dirname(__file__)
    policy_filepath: str = os.path.join(this_dir, "access_policy.json")
    policy = S3Policy.from_file(policy_filepath)

    assert "Standard access for users" in policy.serialisation


def test_parse_policy_from_string(policy_string: str) -> None:
    policy = S3Policy.from_string(policy_string)

    assert "test-members" in policy.serialisation


def test_parse_policy_from_dict(policy_dict: dict) -> None:
    policy = S3Policy.from_dict(policy_dict)

    assert "ListBucket" in policy.serialisation
