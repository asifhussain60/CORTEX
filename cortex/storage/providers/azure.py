"""Azure Blob Storage provider."""

from typing import List

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
    from azure.core.exceptions import ClientAuthenticationError, ResourceNotFoundError
    from azure.storage.blob import BlobServiceClient
except ImportError:
    BlobServiceClient = None
    ResourceNotFoundError = None
    ClientAuthenticationError = None


class AzureBlobProvider(IKnowledgeProvider):
    """
    Azure Blob Storage implementation of IKnowledgeProvider.

    Enables enterprise-grade cloud storage with Azure Blob Storage,
    supporting multi-region replication, lifecycle management, and tier options.

    AC-PHASE50-S4-001: Uses azure-storage-blob SDK
    AC-PHASE50-S4-002: Supports all IKnowledgeProvider methods with Azure Blob operations
    AC-PHASE50-S4-003: Maps Azure errors to StorageError hierarchy
    AC-PHASE50-S4-004: Handles authentication via config credentials or DefaultAzureCredential
    AC-PHASE50-S4-005: Supports optional container path prefix
    """

    def __init__(self, config: StorageConfig) -> None:
        """
        Initialize AzureBlobProvider.

        Args:
            config: StorageConfig with backend="azure" and endpoint="https://account.blob.core.windows.net/container"

        Raises:
            ConfigurationError: If endpoint is None or invalid
            PermissionError: If Azure credentials missing or invalid
        """
        if BlobServiceClient is None:
            raise ConfigurationError(
                "azure-storage-blob not installed. Install with: pip install azure-storage-blob"
            )

        if config.endpoint is None:
            raise ConfigurationError(
                "AzureBlobProvider requires endpoint (https://account.blob.core.windows.net/container)"
            )

        self.config = config

        # AC-PHASE50-S4-005: Parse account and container from endpoint
        try:
            endpoint = config.endpoint
            # Remove https:// prefix if present
            if endpoint.startswith("https://"):
                endpoint = endpoint[8:]

            # Parse account and container
            # Format: account.blob.core.windows.net/container
            parts = endpoint.split("/")
            account_part = parts[0]

            # Extract account name from account.blob.core.windows.net
            self.account_name = account_part.split(".")[0]
            self.container_name = parts[1] if len(parts) > 1 else "default"

        except Exception as e:
            raise ConfigurationError(f"Invalid Azure endpoint: {config.endpoint}") from e

        # AC-PHASE50-S4-001: Initialize Azure BlobServiceClient
        try:
            if config.credentials and "connection_string" in config.credentials:
                # Use connection string
                self.blob_client = BlobServiceClient.from_connection_string(
                    config.credentials["connection_string"]
                )
            elif config.credentials and "account_key" in config.credentials:
                # Use account name and key
                account_url = config.endpoint
                self.blob_client = BlobServiceClient(
                    account_url=account_url,
                    credential=config.credentials["account_key"]
                )
            else:
                # Use DefaultAzureCredential (Azure CLI, environment variables, etc.)
                try:
                    from azure.identity import DefaultAzureCredential
                    account_url = config.endpoint
                    self.blob_client = BlobServiceClient(
                        account_url=account_url,
                        credential=DefaultAzureCredential()
                    )
                except Exception as e:
                    raise ConfigurationError(f"Failed to initialize Azure credentials: {e}") from e
        except ClientAuthenticationError as e:
            raise PermissionError(f"Azure authentication failed: {e}") from e
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize Azure Blob client: {e}") from e

    def _get_blob_name(self, path: str) -> str:
        """
        Construct Azure blob name from path.

        Args:
            path: Relative path

        Returns:
            Full blob name
        """
        return path.lstrip("/")

    def read(self, path: str) -> str:
        """
        Read blob content from Azure.

        AC-PHASE50-S4-002: Implement read() method
        AC-PHASE50-S4-003: Map Azure errors to StorageError hierarchy

        Args:
            path: Relative path to blob

        Returns:
            Blob content as string

        Raises:
            NotFoundError: If blob doesn't exist
            PermissionError: If access denied
            NetworkError: On connection failures
            StorageError: On other Azure errors
        """
        try:
            blob_name = self._get_blob_name(path)
            container_client = self.blob_client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(blob_name)

            blob_data = blob_client.download_blob()
            content = blob_data.readall().decode("utf-8")
            return content

        except ResourceNotFoundError as e:
            raise NotFoundError(f"Blob not found: {path}") from e
        except ClientAuthenticationError as e:
            raise PermissionError(f"Access denied to {path}") from e
        except Exception as e:
            if "timeout" in str(e).lower() or "connection" in str(e).lower():
                raise NetworkError(f"Network error reading {path}: {e}") from e
            raise StorageError(f"Failed to read {path}: {e}") from e

    def write(self, path: str, content: str) -> None:
        """
        Write content to Azure blob.

        AC-PHASE50-S4-002: Implement write() method
        AC-PHASE50-S4-003: Map Azure errors to StorageError hierarchy

        Args:
            path: Relative path to blob
            content: Content to write

        Raises:
            PermissionError: If access denied
            NetworkError: On connection failures
            StorageError: On other Azure errors
        """
        try:
            blob_name = self._get_blob_name(path)
            container_client = self.blob_client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(blob_name)

            blob_client.upload_blob(content.encode("utf-8"), overwrite=True)
        except ClientAuthenticationError as e:
            raise PermissionError(f"Access denied to {path}") from e
        except Exception as e:
            if "timeout" in str(e).lower() or "connection" in str(e).lower():
                raise NetworkError(f"Network error writing {path}: {e}") from e
            raise StorageError(f"Failed to write {path}: {e}") from e

    def list(self, path: str) -> List[str]:
        """
        List blobs in container.

        AC-PHASE50-S4-002: Implement list() method
        AC-PHASE50-S4-003: Map Azure errors to StorageError hierarchy

        Args:
            path: Relative path prefix (empty string = root)

        Returns:
            List of blob names

        Raises:
            NetworkError: On connection failures
            StorageError: On other Azure errors
        """
        try:
            container_client = self.blob_client.get_container_client(self.container_name)

            blob_names = []
            # Azure list_blobs returns BlobProperties objects
            for blob in container_client.list_blobs(name_starts_with=path if path else None):
                blob_names.append(blob.name)

            return sorted(blob_names)
        except Exception as e:
            if "timeout" in str(e).lower() or "connection" in str(e).lower():
                raise NetworkError(f"Network error listing {path}: {e}") from e
            raise StorageError(f"Failed to list {path}: {e}") from e

    def exists(self, path: str) -> bool:
        """
        Check if blob exists in Azure.

        AC-PHASE50-S4-002: Implement exists() method

        Args:
            path: Relative path to check

        Returns:
            True if blob exists, False otherwise
        """
        try:
            blob_name = self._get_blob_name(path)
            container_client = self.blob_client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(blob_name)

            blob_client.get_blob_properties()
            return True
        except ResourceNotFoundError:
            return False
        except Exception:
            return False

    def delete(self, path: str) -> None:
        """
        Delete blob from Azure.

        AC-PHASE50-S4-002: Implement delete() method
        AC-PHASE50-S4-003: Map Azure errors to StorageError hierarchy

        Args:
            path: Relative path to delete

        Raises:
            NotFoundError: If blob doesn't exist
            PermissionError: If access denied
            NetworkError: On connection failures
            StorageError: On other Azure errors
        """
        try:
            # Verify blob exists
            if not self.exists(path):
                raise NotFoundError(f"Blob not found: {path}")

            blob_name = self._get_blob_name(path)
            container_client = self.blob_client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(blob_name)

            blob_client.delete_blob()
        except NotFoundError:
            raise
        except ClientAuthenticationError as e:
            raise PermissionError(f"Access denied to {path}") from e
        except Exception as e:
            if "timeout" in str(e).lower() or "connection" in str(e).lower():
                raise NetworkError(f"Network error deleting {path}: {e}") from e
            raise StorageError(f"Failed to delete {path}: {e}") from e
