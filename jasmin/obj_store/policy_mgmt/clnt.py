  """Module for interacting with the S3 API."""

__author__ = """Philip Kershaw"""
__contact__ = 'philip.kershaw@stfc.ac.uk'
__copyright__ = "Copyright 2021 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
import json

import boto3
from botocore import UNSIGNED
from botocore.client import Config

from .policy import S3Policy


class S3PolicyClnt:
    """Class for interacting with S3 API to read and make changes to access
    policies"""
    def __init__(self, uri: str, key: str = None, secret: str = None) -> None:
        """Initialise Boto3 client"""
        if key is None:
            boto3.client('s3', config=Config(signature_version=UNSIGNED))

        elif secret is None:
            raise ValueError(
                        "Key and secret must be set for non-anonymous access")

        self._clnt = boto3.client('s3',
                        endpoint_url=uri, 
                        aws_access_key_id=key,
                        aws_secret_access_key=secret)

    def put(self, policy: S3Policy, bucket_name: str) -> None:
        """Write a policy to a given bucket"""

        # Set the new policy
        self._clnt.put_bucket_policy(Bucket=bucket_name, 
                                    Policy=policy.serialisation)

    def get(self, bucket_name: str) -> S3Policy:
        """Read existing policy for a given bucket"""

        # Get the policy
        get_bucket_policy_resp = self._clnt.get_bucket_policy(
                                                          Bucket=bucket_name)

        policy = S3Policy.from_string(get_bucket_policy_resp['Policy'])

        return policy                                