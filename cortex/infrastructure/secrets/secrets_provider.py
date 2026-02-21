"""ISecretsProvider — abstract base for all secrets backends."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


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
