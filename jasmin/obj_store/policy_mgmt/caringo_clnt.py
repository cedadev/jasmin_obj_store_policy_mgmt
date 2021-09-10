"""Module for interacting with the Caringo DataCore API."""
__author__ = """Philip Kershaw"""
__contact__ = 'philip.kershaw@stfc.ac.uk'
__copyright__ = "Copyright 2021 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
from typing import Union, List
import urllib.parse

import requests
from requests.auth import HTTPBasicAuth


class AuthenticationError(Exception):
    """Error Authenticating client"""


class RequestError(Exception):
    """Error with API request"""


class CaringoClnt:
    """Web service client to interact with Caringo DataCore API"""
    TOK_PATH = ".TOKEN/"
    COOKIE_NAME = "token"
    ADM_IFACE_PFX = "/_admin/manage/"
    DOMAIN_PATH_TMPL = "tenants/{tenant}/domains/{domain}/{operation}"

    def __init__(self, base_uri: str, username: str, passwd: str) -> None:
        self._base_uri = base_uri
        self._adm_uri = urllib.parse.urljoin(self._base_uri, self.ADM_IFACE_PFX)
        
        # Call API to get token and initiate session
        self.get_tok(username, passwd)

    def get_tok(self, username: str, passwd: str) -> None:
        """Obtain a token in order to start a session"""

        tok_uri = urllib.parse.urljoin(self._base_uri, self.TOK_PATH)
        resp = requests.post(tok_uri, auth=HTTPBasicAuth(username, passwd))
        if not resp.ok:
            raise AuthenticationError("Error authenticating "
                                    "user {!r}: {}".format(username, resp.text))

        self._tok = resp.cookies.get(self.COOKIE_NAME)
        if self._tok is None:
            raise AuthenticationError("Expecting cookie named "
                                    "{!r} in response".format(self.COOKIE_NAME))

    def _get_domain_item(self, tenant_name: str, 
                domain_name: str, operation: str) -> Union[dict, List[dict]]:
        """Execute GET operation on given artifact for domain. operation
        is a path suffix"""
        path_dict = {
            "tenant": tenant_name, "domain": domain_name, "operation": operation
        }

        path = self.DOMAIN_PATH_TMPL.format(**path_dict)
        domain_uri = urllib.parse.urljoin(self._adm_uri, path)

        cookies = {self.COOKIE_NAME: self._tok}
        resp = requests.get(domain_uri, cookies=cookies)
        if not resp.ok:
            raise RequestError("Error calling GET for {!r}: {}".format(
                                                        domain_uri, resp.text))

        return resp.json()

    def get_domain_etc(self, tenant_name: str, 
                        domain_name: str) -> Union[dict, List[dict]]:
        """Get etc document for given domain"""
        operation = "etc"
        return self._get_domain_item(tenant_name, domain_name, operation)

    def get_domain_policy(self, tenant_name: str, 
                        domain_name: str) -> Union[dict, List[dict]]:
        """Get etc document for given domain"""
        operation = "etc/policy.json"
        return self._get_domain_item(tenant_name, domain_name, operation)

