"""AWS S3 storage provider."""

from typing import Any, Dict, List, Optional

from cortex.storage.config import StorageConfig
from cortex.storage.errors import (
    ConfigurationError,
    NetworkError,
    NotFoundError,
    PermissionError,
    StorageError,
)
from cortex.storage.provider import IKnowledgeProvider

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    boto3 = None
    NoCredentialsError = None
    ClientError = None


class S3StorageProvider(IKnowledgeProvider):
    """
    AWS S3 implementation of IKnowledgeProvider.

    Enables enterprise-grade cloud storage with multi-region replication,
    versioning, and lifecycle management via AWS S3.

    AC-PHASE50-S3-001: Uses boto3 for AWS S3 interaction
    AC-PHASE50-S3-002: Supports all IKnowledgeProvider methods with S3 operations
    AC-PHASE50-S3-003: Maps S3 errors to StorageError hierarchy
    AC-PHASE50-S3-004: Handles authentication via config credentials or environment
    AC-PHASE50-S3-005: Supports optional bucket path prefix (endpoint parsing)
    """

    def __init__(self, config: StorageConfig) -> None:
        """
        Initialize S3StorageProvider.

        Args:
            config: StorageConfig with backend="s3" and endpoint="s3://bucket/prefix"

        Raises:
            ConfigurationError: If endpoint is None or invalid
            PermissionError: If AWS credentials missing or invalid
        """
        if boto3 is None:
            raise ConfigurationError("boto3 not installed. Install with: pip install boto3")

        if config.endpoint is None:
            raise ConfigurationError("S3StorageProvider requires endpoint (s3://bucket/prefix)")

        self.config = config

        # AC-PHASE50-S3-005: Parse bucket and prefix from endpoint
        try:
            endpoint = config.endpoint
            if endpoint.startswith("s3://"):
                endpoint = endpoint[5:]

            if "/" in endpoint:
                self.bucket_name, self.prefix = endpoint.split("/", 1)
                if self.prefix and not self.prefix.endswith("/"):
                    self.prefix += "/"
            else:
                self.bucket_name = endpoint
                self.prefix = ""
        except Exception as e:
            raise ConfigurationError(f"Invalid S3 endpoint: {config.endpoint}") from e

        # AC-PHASE50-S3-001: Initialize boto3 S3 client
        try:
            kwargs = {}
            if config.credentials:
                kwargs["aws_access_key_id"] = config.credentials.get("aws_access_key_id")
                kwargs["aws_secret_access_key"] = config.credentials.get("aws_secret_access_key")
                kwargs["region_name"] = config.credentials.get("region_name", "us-east-1")

            self.s3_client = boto3.client("s3", **kwargs)
        except NoCredentialsError as e:
            raise PermissionError(f"AWS credentials not found: {e}") from e
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize S3 client: {e}") from e

    def _get_s3_key(self, path: str) -> str:
        """
        Construct S3 object key from path.

        Args:
            path: Relative path

        Returns:
            Full S3 object key with prefix
        """
        return f"{self.prefix}{path}".lstrip("/")

    def read(self, path: str) -> str:
        """
        Read object content from S3.

        AC-PHASE50-S3-002: Implement read() method
        AC-PHASE50-S3-003: Map S3 errors to StorageError hierarchy

        Args:
            path: Relative path to object

        Returns:
            Object content as string

        Raises:
            NotFoundError: If object doesn't exist
            PermissionError: If access denied
            NetworkError: On connection failures
            StorageError: On other S3 errors
        """
        try:
            key = self._get_s3_key(path)
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            content = response["Body"].read().decode("utf-8")
            return content

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "NoSuchKey":
                raise NotFoundError(f"Object not found: {path}") from e
            elif error_code == "AccessDenied":
                raise PermissionError(f"Access denied to {path}") from e
            else:
                raise StorageError(f"S3 error reading {path}: {error_code}") from e
        except Exception as e:
            if "timeout" in str(e).lower() or "connection" in str(e).lower():
                raise NetworkError(f"Network error reading {path}: {e}") from e
            raise StorageError(f"Failed to read {path}: {e}") from e

    def write(self, path: str, content: str) -> None:
        """
        Write content to S3 object.

        AC-PHASE50-S3-002: Implement write() method
        AC-PHASE50-S3-003: Map S3 errors to StorageError hierarchy

        Args:
            path: Relative path to object
            content: Content to write

        Raises:
            PermissionError: If access denied
            NetworkError: On connection failures
            StorageError: On other S3 errors
        """
        try:
            key = self._get_s3_key(path)
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=content.encode("utf-8")
            )
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "AccessDenied":
                raise PermissionError(f"Access denied to {path}") from e
            else:
                raise StorageError(f"S3 error writing {path}: {error_code}") from e
        except Exception as e:
            if "timeout" in str(e).lower() or "connection" in str(e).lower():
                raise NetworkError(f"Network error writing {path}: {e}") from e
            raise StorageError(f"Failed to write {path}: {e}") from e

    def list(self, path: str) -> List[str]:
        """
        List objects in S3 prefix.

        AC-PHASE50-S3-002: Implement list() method
        AC-PHASE50-S3-003: Map S3 errors to StorageError hierarchy

        Args:
            path: Relative path prefix (empty string = root)

        Returns:
            List of relative paths (object keys)

        Raises:
            NetworkError: On connection failures
            StorageError: On other S3 errors
        """
        try:
            prefix = self._get_s3_key(path)
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )

            entries = []
            if "Contents" in response:
                for obj in response["Contents"]:
                    key = obj["Key"]
                    # Remove prefix to get relative path
                    if key.startswith(self.prefix):
                        relative = key[len(self.prefix):]
                    else:
                        relative = key
                    entries.append(relative)

            return sorted(entries)
        except Exception as e:
            if "timeout" in str(e).lower() or "connection" in str(e).lower():
                raise NetworkError(f"Network error listing {path}: {e}") from e
            raise StorageError(f"Failed to list {path}: {e}") from e

    def exists(self, path: str) -> bool:
        """
        Check if object exists in S3.

        AC-PHASE50-S3-002: Implement exists() method

        Args:
            path: Relative path to check

        Returns:
            True if object exists, False otherwise
        """
        try:
            key = self._get_s3_key(path)
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "404":
                return False
            return False
        except Exception:
            return False

    def delete(self, path: str) -> None:
        """
        Delete object from S3.

        AC-PHASE50-S3-002: Implement delete() method
        AC-PHASE50-S3-003: Map S3 errors to StorageError hierarchy

        Args:
            path: Relative path to delete

        Raises:
            NotFoundError: If object doesn't exist
            PermissionError: If access denied
            NetworkError: On connection failures
            StorageError: On other S3 errors
        """
        try:
            # Verify object exists first
            if not self.exists(path):
                raise NotFoundError(f"Object not found: {path}")

            key = self._get_s3_key(path)
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
        except NotFoundError:
            raise
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "NoSuchKey":
                raise NotFoundError(f"Object not found: {path}") from e
            elif error_code == "AccessDenied":
                raise PermissionError(f"Access denied to {path}") from e
            else:
                raise StorageError(f"S3 error deleting {path}: {error_code}") from e
        except Exception as e:
            if "timeout" in str(e).lower() or "connection" in str(e).lower():
                raise NetworkError(f"Network error deleting {path}: {e}") from e
            raise StorageError(f"Failed to delete {path}: {e}") from e
