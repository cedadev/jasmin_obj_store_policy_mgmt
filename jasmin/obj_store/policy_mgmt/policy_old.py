"""Main module for writing policy templates."""

__author__ = """Philip Kershaw"""
__contact__ = 'philip.kershaw@stfc.ac.uk'
__copyright__ = "Copyright 2021 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
from abc import ABC
import json
from typing import List, TypedDict, Dict, Any, Union


class PolicyDeclBase(ABC):
    """Base class for expressing components of an S3 access policy. It enables
    instances to set attributes which will set an internal dict ready for 
    serialisation in JSON
    """
    TEMPLATE: Dict[str, Any] = {}

    def __init__(self) -> None:
        self._tmpl = self.TEMPLATE.copy()

    def __setattr__(self, name: str, value) -> None:
        if name.startswith('_'):
            super().__setattr__(name, value)
            return

        if name not in self.TEMPLATE.keys():
            raise AttributeError('{!r} has no attribute {!r}'.format(
                self.__class__.__name__, name))

        # TODO: allow for case where single user or group is specified as a 
        # string
        if not isinstance(value, type(self.TEMPLATE[name])):
            raise TypeError(
                'Attribute {!r} is {!r} type, expecting {!r}'.format(
                    name, type(value), type(self.TEMPLATE)))

        self._tmpl[name] = value

    def __getattr__(self, name: str) -> None:
        if name not in self.TEMPLATE.keys():
            raise AttributeError('{!r} has no attribute {!r}'.format(
                self.__class__.__name__, name))
        
        return self._tmpl[name]

    @property
    def dict(self) -> dict:
        return self._tmpl

    @property
    def serialisation(self) -> str:
        return json.dumps(self._tmpl)


class TS3Principal(TypedDict):
    user: Union[str, List[str]]
    group: Union[str, List[str]]


class S3Principal(PolicyDeclBase):
    """Principal block for S3 Policy"""
    TEMPLATE: TS3Principal = {
        "user": [],
        "group": []
    }


class TS3PolicyStatement(TypedDict):
    Sid: str
    Effect: str
    Principal: TS3Principal
    Action: List[str]
    Resource: str


class S3PolicyStatement(PolicyDeclBase):
    """Statement block from S3 Policy"""
    TEMPLATE: TS3PolicyStatement = {
        "Sid": "",
        "Effect": "",
        "Principal": S3Principal(),
        "Action": [],
        "Resource": ""
    }


class TS3Policy(TypedDict):
    Version: str
    Id: str
    Statement: List[TS3PolicyStatement]


class S3Policy(PolicyDeclBase):
    """S3 Policy"""
    TEMPLATE: TS3Policy = {
        "Version": "",
        "Id": "",
        "Statement": []
    }