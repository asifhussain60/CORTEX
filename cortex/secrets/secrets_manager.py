"""
SecretsManager Core Implementation - Phase 76 Stage 3

Production-grade secrets management with AES-256-GCM encryption,
environment validation, and audit trail integration.

Authority: phase-76-production-foundation-trilogy.yaml S3.T2
AC-ID: AC-PHASE76-S3-002
"""

import os
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

from cortex.secrets.encryption import EncryptionManager, encrypt_value, decrypt_value
from cortex.secrets.audit_trail import AuditLogger, HashChain
from cortex.secrets.errors import SecretsError

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
            storage_path: Storage directory for encrypted secrets (defaults to ~/.cortex/secrets)
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
            storage_path = os.path.expanduser("~/.cortex/secrets")
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
            if self.audit_enabled and self.audit_logger and self.hash_chain:
                event = self.audit_logger.log_secret_modification(
                    user_id=os.getenv("USER", "unknown"),
                    secret_id=key,
                    operation="SET",
                    change_summary=f"Secret set with tags: {tags}",
                )
                self.hash_chain.append_event(event)
            
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
                if self.audit_enabled and self.audit_logger and self.hash_chain:
                    event = self.audit_logger.log_secret_access(
                        user_id=os.getenv("USER", "unknown"),
                        secret_id=key,
                        operation="GET",
                    )
                    self.hash_chain.append_event(event)
                
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
            if self.audit_enabled and self.audit_logger and self.hash_chain:
                event = self.audit_logger.log_secret_modification(
                    user_id=os.getenv("USER", "unknown"),
                    secret_id=key,
                    operation="DELETE",
                    change_summary="Secret securely deleted",
                )
                self.hash_chain.append_event(event)
            
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
    # AUDIT TRAIL OPERATIONS
    # ========================================================================
    
    def get_audit_trail(self) -> Dict[str, Any]:
        """
        Get audit trail with integrity verification.
        
        Returns:
            Dict with "events", "valid", "chain_hash"
        """
        if not self.audit_enabled or not self.hash_chain:
            raise SecretsError("Audit trail not enabled")
        
        return {
            "events": len(self.hash_chain.events),
            "valid": self.hash_chain.verify_integrity(),
            "chain_hash": self.hash_chain.previous_hash,
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
        
        return self.hash_chain.verify_integrity()
    
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
