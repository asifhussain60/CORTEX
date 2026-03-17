"""SecretsConfig — configuration dataclass for secrets backends."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from cortex.infrastructure.secrets.errors import ConfigError


@dataclass
class SecretsConfig:
    """Configuration for a secrets provider backend."""

    backend: str = "local"               # local | aws | azure | vault
    provider_type: Optional[str] = None   # compatibility alias for backend
    endpoint: Optional[str] = None         # compatibility endpoint alias
    region: Optional[str] = None        # AWS region / Azure location
    vault_addr: Optional[str] = None    # HashiCorp Vault address
    vault_token: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    azure_vault_url: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    azure_client_id: Optional[str] = None
    azure_client_secret: Optional[str] = None
    namespace: str = "cortex"
    timeout: int = 30
    extra: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    auth_type: Optional[str] = "env"

    def __post_init__(self) -> None:
        """Normalize compatibility aliases into canonical fields."""
        if self.provider_type:
            self.backend = self.provider_type

        valid_backends = {"local", "aws", "azure", "vault"}
        if self.backend not in valid_backends:
            raise ConfigError(f"Unknown provider_type/backend: {self.backend}")

        if self.backend == "azure" and self.endpoint and not self.azure_vault_url:
            self.azure_vault_url = self.endpoint

        if self.backend == "vault" and self.endpoint and not self.vault_addr:
            self.vault_addr = self.endpoint

    @classmethod
    def from_env(cls: object) -> "SecretsConfig":
        """Build config from environment variables."""
        import os
        return cls(
            backend=os.getenv("SECRETS_BACKEND", "local"),
            region=os.getenv("AWS_REGION"),
            vault_addr=os.getenv("VAULT_ADDR"),
            vault_token=os.getenv("VAULT_TOKEN"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            azure_vault_url=os.getenv("AZURE_VAULT_URL"),
        )
