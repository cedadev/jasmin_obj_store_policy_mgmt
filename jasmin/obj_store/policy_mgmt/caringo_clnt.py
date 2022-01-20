"""Module for interacting with the Caringo DataCore API."""
__author__ = """Philip Kershaw"""
__contact__ = "philip.kershaw@stfc.ac.uk"
__copyright__ = "Copyright 2021 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
import json
import logging
import typing
import urllib.parse
from typing import Any, List, Mapping, Optional, Tuple, Union

import requests
import yaml
from requests.auth import HTTPBasicAuth

from jasmin.obj_store.policy_mgmt.policy import S3Policy

log = logging.getLogger(__name__)


class Error(Exception):
    """Base error class for Caringo Client"""


class RequestError(Error):
    """Error with API request"""

    def __init__(self, message: str, resp: Optional[requests.Response] = None) -> None:
        super().__init__(message)
        self.resp = resp


class AuthenticationError(RequestError):
    """Error Authenticating client"""


class ConfigError(Error):
    """Error with configuration options"""


class CaringoClnt:
    """Web service client to interact with Caringo DataCore API"""

    TOK_PATH = ".TOKEN/"
    COOKIE_NAME = "token"
    ADM_IFACE_PFX = "/_admin/manage/"
    DOMAIN_PATH_TMPL = "tenants/{tenant}/domains/{domain}/{operation}"
    CREDS_FILEPATH_ENVVAR_NAME = "JASMIN_OSPM_CREDS_FILEPATH"

    def __init__(
        self,
        base_uri: str,
        username: str,
        passwd: str,
        domain_name: str = None,
        tenancy_name: str = None,
    ) -> None:
        self._base_uri: str = base_uri
        self._adm_uri: str = urllib.parse.urljoin(self._base_uri, self.ADM_IFACE_PFX)

        self._domain_name: Union[str, None] = domain_name
        self._tenancy_name: Union[str, None] = tenancy_name

        # Call API to get token and initiate session
        self.init_session(username, passwd)

    def init_session(self, username: str, passwd: str) -> None:
        """Obtain a token in order to start a session"""
        log.info("Get access token...")
        tok_uri: str = urllib.parse.urljoin(self._base_uri, self.TOK_PATH)

        self._session = requests.Session()
        resp: requests.Response = self._session.post(
            tok_uri, auth=HTTPBasicAuth(username, passwd)
        )
        if not resp.ok:
            raise AuthenticationError(
                "Error authenticating " "user {!r}: {}".format(username, resp.text),
                resp=resp,
            )

        self._tok = resp.cookies.get(self.COOKIE_NAME)  # type: ignore
        if self._tok is None:
            raise AuthenticationError(
                "Expecting cookie named {!r} in response".format(self.COOKIE_NAME),
                resp=resp,
            )

    @classmethod
    def from_config(cls, config_filepath: str, creds_filepath: str) -> "CaringoClnt":
        """Instantiate client from a YAML configuration file and optional creds
        file"""

        settings = cls.parse_config_file(config_filepath)
        creds_args: Tuple[str, str] = cls.parse_creds_file(creds_filepath)

        obj = cls(
            settings["base_uri"],
            *creds_args,
            tenancy_name=settings["tenancy_name"],
            domain_name=settings["domain_name"],
        )

        return obj

    @classmethod
    def parse_config_file(cls, config_filepath: str) -> dict:
        """Read settings from YAML file"""
        with open(config_filepath) as config_file:
            settings = yaml.safe_load(config_file)

        return settings

    @staticmethod
    def parse_creds_file(creds_filepath: str) -> Tuple[str, str]:
        "Read username and password from separate credentials file"
        with open(creds_filepath) as creds_file:
            creds = json.load(creds_file)

        return creds["username"], creds["passwd"]

    @property
    def domain_name(self) -> str:
        return self._domain_name

    @domain_name.setter
    def domain_name(self, value: str):
        self._domain_name = value

    @property
    def tenancy_name(self) -> str:
        return self._tenancy_name

    @tenancy_name.setter
    def tenancy_name(self, value: str):
        self._tenancy_name = value

    @property
    def tok(self) -> Union[None, str]:
        return self._tok

    def _get_domain_item(self, operation: str) -> Union[dict, List[dict]]:
        """Execute GET operation on given artifact for domain. operation
        is a path suffix"""
        if not self._tenancy_name:
            raise RequestError("Tenancy name is not set - API call not dispatched")

        if not self._domain_name:
            raise RequestError("Domain name is not set - API call not dispatched")

        path_dict: dict = {
            "tenant": self._tenancy_name,
            "domain": self._domain_name,
            "operation": operation,
        }

        path: str = self.DOMAIN_PATH_TMPL.format(**path_dict)
        domain_uri: str = urllib.parse.urljoin(self._adm_uri, path)

        resp = self._session.get(domain_uri)
        if not resp.ok:
            raise RequestError(
                "{} response calling GET for {!r}: {}".format(
                    resp.status_code, domain_uri, resp.text
                ),
                resp=resp,
            )

        return resp.json()

    def _put_domain_item(
        self,
        operation: str,
        payload: Union[str, Mapping[str, Any]],
    ) -> None:
        """Execute PUT operation on given artifact for domain. operation
        is a path suffix"""
        if not self._tenancy_name:
            raise RequestError("Tenancy name is not set - API call not dispatched")

        if not self._domain_name:
            raise RequestError("Domain name is not set - API call not dispatched")

        path_dict: dict = {
            "tenant": self._tenancy_name,
            "domain": self._domain_name,
            "operation": operation,
        }

        path: str = self.DOMAIN_PATH_TMPL.format(**path_dict)
        domain_uri: str = urllib.parse.urljoin(self._adm_uri, path)

        resp: requests.Response = self._session.put(domain_uri, data=payload)
        if not resp.ok:
            raise RequestError(
                "{} response calling PUT for {!r}: {}".format(
                    resp.status_code, domain_uri, resp.text
                ),
                resp=resp,
            )

    def get_domain_etc(self) -> Union[dict, List[dict]]:
        """Get etc document for given domain"""
        log.info("Calling get_domain_etc...")
        operation: str = "etc"
        return self._get_domain_item(operation)

    def get_domain_policy(self) -> S3Policy:
        """Get etc document for given domain"""
        log.info("Calling get_domain_policy...")
        operation: str = "etc/policy.json"
        policy_d = self._get_domain_item(operation)

        return S3Policy.from_dict(typing.cast(dict, policy_d))

    def put_domain_policy(self, policy: S3Policy) -> None:
        """Set access policy for a given domain"""
        log.info("Calling get_domain_etc...")
        operation: str = "etc/policy.json"

        self._put_domain_item(operation, policy.serialisation)
