"""Module for interacting with the Caringo DataCore API."""
__author__ = """Philip Kershaw"""
__contact__ = "philip.kershaw@stfc.ac.uk"
__copyright__ = "Copyright 2021 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
import logging
import typing
import urllib.parse
from typing import Any, List, Mapping, Optional, Union

import requests
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


class CaringoClnt:
    """Web service client to interact with Caringo DataCore API"""

    TOK_PATH = ".TOKEN/"
    COOKIE_NAME = "token"
    ADM_IFACE_PFX = "/_admin/manage/"
    DOMAIN_PATH_TMPL = "tenants/{tenant}/domains/{domain}/{operation}"

    def __init__(self, base_uri: str, username: str, passwd: str) -> None:
        self._base_uri: str = base_uri
        self._adm_uri: str = urllib.parse.urljoin(self._base_uri, self.ADM_IFACE_PFX)

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

    @property
    def tok(self) -> Union[None, str]:
        return self._tok

    def _get_domain_item(
        self, tenant_name: str, domain_name: str, operation: str
    ) -> Union[dict, List[dict]]:
        """Execute GET operation on given artifact for domain. operation
        is a path suffix"""
        if not tenant_name:
            raise RequestError("Tenant name is not set - API call not dispatched")

        if not domain_name:
            raise RequestError("Domain name is not set - API call not dispatched")

        path_dict: dict = {
            "tenant": tenant_name,
            "domain": domain_name,
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
        tenant_name: str,
        domain_name: str,
        operation: str,
        payload: Union[str, Mapping[str, Any]],
    ) -> None:
        """Execute PUT operation on given artifact for domain. operation
        is a path suffix"""
        if not tenant_name:
            raise RequestError("Tenant name is not set - API call not dispatched")

        if not domain_name:
            raise RequestError("Domain name is not set - API call not dispatched")

        path_dict: dict = {
            "tenant": tenant_name,
            "domain": domain_name,
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

    def get_domain_etc(
        self, tenant_name: str, domain_name: str
    ) -> Union[dict, List[dict]]:
        """Get etc document for given domain"""
        log.info("Calling get_domain_etc...")
        operation: str = "etc"
        return self._get_domain_item(tenant_name, domain_name, operation)

    def get_domain_policy(self, tenant_name: str, domain_name: str) -> S3Policy:
        """Get etc document for given domain"""
        log.info("Calling get_domain_policy...")
        operation: str = "etc/policy.json"
        policy_d = self._get_domain_item(tenant_name, domain_name, operation)

        return S3Policy.from_dict(typing.cast(dict, policy_d))

    def put_domain_policy(
        self, tenant_name: str, domain_name: str, policy: S3Policy
    ) -> None:
        """Set access policy for a given domain"""
        log.info("Calling get_domain_etc...")
        operation: str = "etc/policy.json"

        self._put_domain_item(tenant_name, domain_name, operation, policy.serialisation)
