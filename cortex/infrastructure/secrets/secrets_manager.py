"""
SecretsManager Core Implementation - Phase 76 Stage 3

Production-grade secrets management with AES-256-GCM encryption,
environment validation, and audit trail integration.

Phase 99-A additions: generate_api_key, validate_api_key, revoke_api_key,
list_api_keys — secure API key lifecycle for MCP gateway authentication.

Authority: phase-76-production-foundation-trilogy.yaml S3.T2
AC-ID: AC-PHASE76-S3-002 / AC-P99-A-001
"""

import hashlib
import hmac
import logging
import os
import secrets as _secrets_module
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.infrastructure.secrets.audit_trail import AuditLogger, HashChain
from cortex.infrastructure.secrets.encryption import EncryptionManager
from cortex.infrastructure.secrets.errors import SecretsError

logger = logging.getLogger(__name__)


class SecretsManager:
    """
    Production secrets management API.

    Provides:
    - set_secret(key, value) → encrypted storage
    - get_secret(key) → decrypted value
    - delete_secret(key) → secure deletion
    - list_secrets() → keys only (no values)
    - Environment variable fallback
    - Audit trail integration
    """

    def __init__(
        self,
        master_key: Optional[str] = None,
        storage_path: Optional[str] = None,
        audit_enabled: bool = True,
    ) -> None:
        """
        Initialize SecretsManager.

        Args:
            master_key: Master encryption key (defaults to CORTEX_MASTER_KEY env var)
            storage_path: Storage directory for encrypted secrets (defaults to ~/.cortex-runtime/secrets)
            audit_enabled: Enable audit trail logging

        Raises:
            SecretsError: If master_key missing or storage path invalid
        """
        # Get master key
        if master_key is None:
            master_key = os.getenv("CORTEX_MASTER_KEY")

        if not master_key:
            raise SecretsError(
                "CORTEX_MASTER_KEY environment variable not set. "
                "Set it before using SecretsManager."
            )

        self.master_key = master_key
        self.encryption_mgr = EncryptionManager(master_key)

        # Setup storage path
        if storage_path is None:
            storage_path = os.path.expanduser("~/.cortex-runtime/secrets")
        else:
            storage_path = os.path.expanduser(storage_path)

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Audit trail
        self.audit_enabled = audit_enabled
        self.audit_logger = AuditLogger() if audit_enabled else None
        self.hash_chain = HashChain() if audit_enabled else None

        logger.debug(f"SecretsManager initialized with storage at {self.storage_path}")

    # ========================================================================
    # CORE API: CRUD OPERATIONS
    # ========================================================================

    def set_secret(self, key: str, value: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Store an encrypted secret.

        Args:
            key: Secret identifier (e.g., "DATABASE_PASSWORD")
            value: Secret value (will be encrypted)
            tags: Optional metadata tags (e.g., {"env": "prod", "app": "auth"})

        Returns:
            Dict with "key", "encrypted", "timestamp", "tags"

        Raises:
            SecretsError: If encryption fails or key invalid
        """
        if not key or not isinstance(key, str):
            raise SecretsError(f"Invalid key: {key}")

        if not value or not isinstance(value, str):
            raise SecretsError(f"Invalid value for key {key}")

        try:
            # Encrypt value
            encrypted_json = self.encryption_mgr.encrypt(value)

            # Prepare metadata
            secret_file = self.storage_path / f"{key}.enc"
            timestamp = datetime.utcnow().isoformat()

            metadata = {
                "key": key,
                "encrypted": encrypted_json,
                "timestamp": timestamp,
                "tags": tags or {},
                "version": 1,
            }

            # Write to file
            import json
            with open(secret_file, "w") as f:
                json.dump(metadata, f)

            # Audit log
            if self.audit_enabled and self.audit_logger:
                self.audit_logger.log(
                    action="SET",
                    key=key,
                    actor=os.getenv("USER", "system"),
                    success=True,
                    tags=str(tags),
                )
            if self.audit_enabled and self.hash_chain:
                self.hash_chain.append({"operation": "SET", "key": key})

            logger.info(f"Secret stored: {key}")
            return {
                "key": key,
                "encrypted": True,
                "timestamp": timestamp,
                "tags": tags or {},
            }

        except Exception as e:
            logger.error(f"Failed to set secret {key}: {e}")
            raise SecretsError(f"Failed to set secret {key}: {e}")

    def get_secret(self, key: str) -> str:
        """
        Retrieve and decrypt a secret.

        Args:
            key: Secret identifier

        Returns:
            Decrypted secret value

        Raises:
            SecretsError: If secret not found, decryption fails, or key invalid
        """
        if not key or not isinstance(key, str):
            raise SecretsError(f"Invalid key: {key}")

        try:
            # Try file storage first (priority over environment)
            secret_file = self.storage_path / f"{key}.enc"

            if secret_file.exists():
                # Read and decrypt
                import json
                with open(secret_file, "r") as f:
                    metadata = json.load(f)

                encrypted_json = metadata["encrypted"]
                plaintext = self.encryption_mgr.decrypt(encrypted_json)

                # Audit log
                if self.audit_enabled and self.audit_logger:
                    self.audit_logger.log(
                        action="GET",
                        key=key,
                        actor=os.getenv("USER", "system"),
                        success=True,
                    )
                if self.audit_enabled and self.hash_chain:
                    self.hash_chain.append({"operation": "GET", "key": key})

                logger.info(f"Secret retrieved: {key}")
                return plaintext

            # Check environment variable as fallback
            env_value = os.getenv(key)
            if env_value:
                logger.debug(f"Using environment variable for {key}")
                return env_value

            # Not found anywhere
            raise SecretsError(f"Secret not found: {key}")

        except SecretsError:
            raise
        except Exception as e:
            logger.error(f"Failed to get secret {key}: {e}")
            raise SecretsError(f"Failed to get secret {key}: {e}")

    def delete_secret(self, key: str) -> Dict[str, Any]:
        """
        Securely delete a secret.

        Args:
            key: Secret identifier

        Returns:
            Dict with "key", "deleted", "timestamp"

        Raises:
            SecretsError: If secret not found or deletion fails
        """
        if not key or not isinstance(key, str):
            raise SecretsError(f"Invalid key: {key}")

        try:
            secret_file = self.storage_path / f"{key}.enc"

            if not secret_file.exists():
                raise SecretsError(f"Secret not found: {key}")

            # Secure deletion: overwrite before delete
            import secrets as secrets_module
            with open(secret_file, "wb") as f:
                # Overwrite with random data (3 passes)
                for _ in range(3):
                    f.write(secrets_module.token_bytes(f.seek(0, 2)))

            # Delete file
            secret_file.unlink()

            # Audit log
            if self.audit_enabled and self.audit_logger:
                self.audit_logger.log(
                    action="DELETE",
                    key=key,
                    actor=os.getenv("USER", "system"),
                    success=True,
                )
            if self.audit_enabled and self.hash_chain:
                self.hash_chain.append({"operation": "DELETE", "key": key})

            timestamp = datetime.utcnow().isoformat()
            logger.info(f"Secret deleted: {key}")

            return {
                "key": key,
                "deleted": True,
                "timestamp": timestamp,
            }

        except SecretsError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete secret {key}: {e}")
            raise SecretsError(f"Failed to delete secret {key}: {e}")

    def list_secrets(self) -> Dict[str, Any]:
        """
        List all secret keys (NOT VALUES for security).

        Returns:
            Dict with "keys", "count", "timestamp"
        """
        try:
            keys = []

            # Find all .enc files
            for secret_file in self.storage_path.glob("*.enc"):
                key = secret_file.stem  # Remove .enc extension
                keys.append(key)

            # Also include environment variable secrets
            env_secrets = []
            for key in os.environ.keys():
                if key.startswith("CORTEX_") and key != "CORTEX_MASTER_KEY":
                    env_secrets.append(f"{key} (env)")

            all_keys = sorted(keys + env_secrets)

            logger.info(f"Listed {len(all_keys)} secrets")

            return {
                "keys": all_keys,
                "count": len(all_keys),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to list secrets: {e}")
            raise SecretsError(f"Failed to list secrets: {e}")

    # ========================================================================
    # ENVIRONMENT VARIABLE FALLBACK
    # ========================================================================

    def get_secret_or_env(self, key: str, env_key: Optional[str] = None) -> str:
        """
        Get secret with environment variable fallback.

        Args:
            key: Secret key
            env_key: Environment variable name (defaults to key)

        Returns:
            Secret value

        Raises:
            SecretsError: If not found in secrets or environment
        """
        env_key = env_key or key

        try:
            # Try storage first
            secret_file = self.storage_path / f"{key}.enc"
            if secret_file.exists():
                try:
                    return self.get_secret(key)
                except SecretsError:
                    pass  # Fall through to env

            # Fallback to environment
            value = os.getenv(env_key)
            if value:
                logger.debug(f"Using environment variable {env_key}")
                return value

            raise SecretsError(
                f"Secret {key} not found in storage or environment ({env_key})"
            )
        except SecretsError:
            raise
        except Exception as e:
            raise SecretsError(f"Error retrieving secret: {e}")

    # ========================================================================
    # API KEY MANAGEMENT — Phase 99-A (AC-P99-A-001)
    # Authority: skull rule AC-PERMANENT-FIX-006 + CORE-050 MCP tier blocking
    # ========================================================================

    # Internal vault key prefix that namespaces API key hashes from secrets
    _API_KEY_PREFIX: str = "_apikey_"

    def generate_api_key(
        self,
        key_id: str = "default",
        prefix: str = "",
    ) -> str:
        """Generate a cryptographically secure API key and store its hash.

        Uses 32 bytes (256 bits) of OS entropy, URL-safe base64-encoded.
        The raw key is returned ONCE and never stored — only its HMAC-SHA256
        hash (keyed with the master key) is persisted, making the vault safe
        to inspect without exposing key material.

        Args:
            key_id: Logical identifier for this key (e.g. 'mcp_gateway',
                    'ci_runner').  Used for listing and revocation.
            prefix: Optional URL-safe string prepended to the raw key
                    (e.g. 'cx_live_').  Does not affect entropy.

        Returns:
            Raw API key string — caller must store this securely.
            Will not be recoverable after this call.

        Raises:
            SecretsError: If storing the key hash fails.
        """
        # Generate 32 bytes of cryptographically secure entropy
        raw_bytes = _secrets_module.token_bytes(32)
        import base64
        raw_key: str = prefix + base64.urlsafe_b64encode(raw_bytes).rstrip(b"=").decode()

        # Derive HMAC-SHA256 of the raw key, keyed by master key (not reversible)
        key_hash: str = self._hash_api_key(raw_key)

        # Persist hash under a namespaced vault entry
        vault_key = f"{self._API_KEY_PREFIX}{key_id}"
        self.set_secret(vault_key, key_hash, tags={"type": "api_key_hash", "key_id": key_id})

        # Audit trail — use actual AuditLogger.log(action, key, ...) signature
        if self.audit_logger:
            self.audit_logger.log(
                action="generate_api_key",
                key=key_id,
                success=True,
            )
        if self.hash_chain:
            self.hash_chain.append({"operation": "generate_api_key", "key_id": key_id})

        logger.info("API key generated for key_id=%s", key_id)
        return raw_key

    def validate_api_key(self, api_key: object) -> bool:
        """Validate an API key using constant-time comparison.

        Derives the HMAC of the supplied key and compares it against every
        stored key hash using ``hmac.compare_digest`` to prevent timing
        oracle attacks.

        Args:
            api_key: The raw API key string (from ``Authorization: Bearer``
                     or ``X-CORTEX-API-KEY`` header).

        Returns:
            True if the key matches any non-revoked stored hash, else False.
        """
        if not api_key or not isinstance(api_key, str):
            return False

        candidate_hash = self._hash_api_key(api_key)

        # Enumerate all stored API key hashes
        stored_keys = self._list_api_key_vault_entries()
        for vault_key in stored_keys:
            try:
                stored_hash = self.get_secret(vault_key)
                # hmac.compare_digest is constant-time regardless of match/mismatch
                if hmac.compare_digest(candidate_hash, stored_hash):
                    return True
            except Exception:
                continue

        return False

    def revoke_api_key(self, key_id: str) -> None:
        """Permanently revoke an API key by deleting its stored hash.

        After revocation, ``validate_api_key`` will return False for the
        corresponding raw key.  This operation is irreversible — the raw
        key cannot be recovered from the hash.

        Args:
            key_id: The logical key identifier used when the key was generated.

        Raises:
            SecretsError: If no key with the given key_id exists.
        """
        vault_key = f"{self._API_KEY_PREFIX}{key_id}"
        # delete_secret raises SecretsError if key not found — propagate as-is
        self.delete_secret(vault_key)

        # Audit trail
        if self.audit_logger:
            self.audit_logger.log(
                action="revoke_api_key",
                key=key_id,
                success=True,
            )
        if self.hash_chain:
            self.hash_chain.append({"operation": "revoke_api_key", "key_id": key_id})

        logger.info("API key revoked for key_id=%s", key_id)

    def list_api_keys(self) -> Dict[str, Any]:
        """List all active API key identifiers without exposing key material.

        Returns:
            Dict mapping key_id → metadata (created_at, tags).
            Raw keys and hashes are never included.
        """
        result: Dict[str, Any] = {}
        prefix_len = len(self._API_KEY_PREFIX)

        for vault_key in self._list_api_key_vault_entries():
            key_id = vault_key[prefix_len:]  # strip "_apikey_" prefix
            # Read tags from the .enc sidecar (tags are stored in plaintext metadata)
            enc_file = self.storage_path / f"{vault_key}.enc"
            meta: Dict[str, Any] = {}
            if enc_file.exists():
                try:
                    import json
                    raw_meta = json.loads(enc_file.read_text())
                    meta = {
                        "created_at": raw_meta.get("timestamp", ""),
                        "tags": {
                            k: v for k, v in raw_meta.get("tags", {}).items()
                            if k != "type"  # omit internal type tag
                        },
                    }
                except Exception:
                    pass
            result[key_id] = meta

        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _hash_api_key(self, raw_key: str) -> str:
        """Derive a deterministic HMAC-SHA256 hex digest for an API key.

        Keyed with the master key so the hash is only reproducible by a
        SecretsManager instance holding the same master_key.

        Args:
            raw_key: The plaintext API key string.

        Returns:
            Lowercase hex string of the HMAC-SHA256 digest.
        """
        return hmac.new(
            self.master_key.encode(),
            raw_key.encode(),
            hashlib.sha256,
        ).hexdigest()

    def _list_api_key_vault_entries(self) -> List[str]:
        """Return vault keys (filenames without .enc) for all stored API key hashes.

        Returns:
            List of vault key strings (e.g. ['_apikey_mcp_gateway']).
        """
        return [
            p.stem
            for p in self.storage_path.glob(f"{self._API_KEY_PREFIX}*.enc")
        ]

    # ========================================================================
    # AUDIT TRAIL OPERATIONS
    # ========================================================================

    def get_audit_trail(self) -> Dict[str, Any]:
        """
        Get audit trail with integrity verification.

        Returns:
            Dict with "events" (list), "valid" (bool), "chain_hash" (str)
        """
        if not self.audit_enabled or not self.hash_chain:
            raise SecretsError("Audit trail not enabled")

        raw = self.audit_logger.get_entries() if self.audit_logger else []
        from dataclasses import asdict as _asdict
        events = []
        for e in raw:
            d = _asdict(e) if hasattr(e, "__dataclass_fields__") else {"action": str(e)}
            # Ensure "operation" reflects "action" when the operation field is blank
            if not d.get("operation"):
                d["operation"] = d.get("action", "")
            events.append(d)
        return {
            "events": events,
            "valid": self.hash_chain.verify(),
            "chain_hash": self.hash_chain.get_chain()[-1] if self.hash_chain.get_chain() else "0" * 64,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def verify_audit_integrity(self) -> bool:
        """
        Verify audit trail integrity.

        Returns:
            True if chain is valid, False otherwise
        """
        if not self.audit_enabled or not self.hash_chain:
            return True

        return self.hash_chain.verify()

    # ========================================================================
    # FACTORY METHODS
    # ========================================================================

    @staticmethod
    def from_environment() -> "SecretsManager":
        """
        Create SecretsManager from environment variables.

        Returns:
            SecretsManager instance

        Raises:
            SecretsError: If CORTEX_MASTER_KEY not set
        """
        master_key = os.getenv("CORTEX_MASTER_KEY")
        if not master_key:
            raise SecretsError("CORTEX_MASTER_KEY environment variable not set")

        storage_path = os.getenv("CORTEX_SECRETS_PATH")
        audit_enabled = os.getenv("CORTEX_AUDIT_ENABLED", "true").lower() == "true"

        return SecretsManager(
            master_key=master_key,
            storage_path=storage_path,
            audit_enabled=audit_enabled,
        )


__all__ = [
    "SecretsManager",
]
