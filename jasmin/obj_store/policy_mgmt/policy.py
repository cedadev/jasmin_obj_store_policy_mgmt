"""Main module for writing policy templates."""

__author__ = """Philip Kershaw"""
__contact__ = 'philip.kershaw@stfc.ac.uk'
__copyright__ = "Copyright 2021 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
import json
from typing import List, TypedDict, Union, overload


class TS3Principal(TypedDict):
    user: Union[str, List[str]]
    group: Union[str, List[str]]


class TS3PolicyStatement(TypedDict):
    Sid: str
    Effect: str
    Principal: TS3Principal
    Action: List[str]
    Resource: str


class TS3Policy(TypedDict):
    Version: str
    Id: str
    Statement: List[TS3PolicyStatement]


class S3Policy:
    """Class for expressing components of an S3 access policy. 
    """
    # Standard version string for S3
    VERSION = "2008-10-17"
 
    def __init__(self, version: str = VERSION, id: str = None, 
                statement: List[TS3PolicyStatement] = None) -> None:
        if statement is None:
            statement = []

        if id is None:
            id = ""

        self._policy = TS3Policy(Version=version, Id=id, Statement=statement)

    @classmethod
    def from_file(cls, policy_filepath: str) -> 'S3Policy':
        """Construct policy from input JSON file"""
        policy = cls()
        policy.parse_from_file(policy_filepath)

        return policy

    @classmethod
    def from_string(cls, policy_s: str) -> 'S3Policy':
        """Construct policy from input JSON file"""
        policy = cls()
        policy.parse_from_string(policy_s)

        return policy

    def __repr__(self) -> str:
        return json.dumps(self._policy)

    @property
    def serialisation(self) -> str:
        return self.__repr__()

    def parse_from_file(self, policy_filepath: str) -> None:
        """Set policy from input JSON file"""
        with open(policy_filepath, "r") as policy_file:
            policy_file_d = json.load(policy_file)

        self._policy = TS3Policy(policy_file_d)

    def parse_from_string(self, policy_s: str) -> None:
        """Set policy from JSON policy string serialisation"""
        policy_file_d = json.loads(policy_s)

        self._policy = TS3Policy(policy_file_d)


