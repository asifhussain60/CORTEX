"""ISecretsProvider — abstract base for all secrets backends."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List


class ISecretsProvider(ABC):
    """Abstract protocol every secrets provider must implement."""

    @abstractmethod
    def get_secret(self, key: str) -> str:
        """Retrieve a secret value by *key*."""

    @abstractmethod
    def set_secret(self, key: str, value: str, **meta: Any) -> bool:
        """Create or update a secret."""

    @abstractmethod
    def delete_secret(self, key: str) -> bool:
        """Delete a secret."""

    @abstractmethod
    def list_secrets(self) -> List[str]:
        """List all secret keys."""

    @abstractmethod
    def rotate_secret(self, key: str) -> str:
        """Rotate a secret and return the new value."""

    def get(self, key: str) -> str:
        """Compatibility alias for get_secret."""
        return self.get_secret(key)

    def set(self, key: str, value: str, metadata: Any = None) -> bool:
        """Compatibility alias for set_secret."""
        return self.set_secret(key, value, **(metadata or {}))

    def delete(self, key: str) -> bool:
        """Compatibility alias for delete_secret."""
        return self.delete_secret(key)

    def list(self, prefix: str = "") -> List[str]:
        """Compatibility alias for list_secrets."""
        values = self.list_secrets()
        if not prefix:
            return values
        return [value for value in values if value.startswith(prefix)]

    def rotate(self, key: str) -> str:
        """Compatibility alias for rotate_secret."""
        return self.rotate_secret(key)
