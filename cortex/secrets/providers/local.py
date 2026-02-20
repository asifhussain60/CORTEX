"""LocalSecretsProvider — in-memory/file-based secrets for dev/test."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.secrets.errors import SecretNotFoundError, StorageError
from cortex.secrets.secrets_provider import ISecretsProvider


class LocalSecretsProvider(ISecretsProvider):
    """Simple in-process secrets store backed by a JSON file (or memory)."""

    def __init__(
        self,
        storage_path: Optional[str] = None,
        initial_secrets: Optional[Dict[str, str]] = None,
    ) -> None:
        self._path = Path(storage_path) if storage_path else None
        self._store: Dict[str, str] = {}
        if initial_secrets:
            self._store.update(initial_secrets)
        if self._path and self._path.exists():
            try:
                self._store.update(json.loads(self._path.read_text()))
            except Exception as exc:
                raise StorageError(f"Failed to load secrets from {self._path}: {exc}") from exc

    def _persist(self) -> None:
        if self._path:
            self._path.write_text(json.dumps(self._store, indent=2))

    def get_secret(self, key: str) -> str:
        if key not in self._store:
            raise SecretNotFoundError(f"Secret '{key}' not found")
        return self._store[key]

    def set_secret(self, key: str, value: str, **meta: Any) -> bool:
        self._store[key] = value
        self._persist()
        return True

    def delete_secret(self, key: str) -> bool:
        if key not in self._store:
            return False
        del self._store[key]
        self._persist()
        return True

    def list_secrets(self) -> List[str]:
        return list(self._store.keys())

    def rotate_secret(self, key: str) -> str:
        import secrets as _secrets
        if key not in self._store:
            raise SecretNotFoundError(f"Secret '{key}' not found")
        new_value = _secrets.token_urlsafe(32)
        self._store[key] = new_value
        self._persist()
        return new_value
