"""
Secrets provider configuration
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any


@dataclass
class SecretsConfig:
    """
    Configuration for secrets provider.
    
    Attributes:
        provider_type: Type of provider (aws|azure|vault|local)
        endpoint: Provider endpoint (URL, ARN, URI)
        region: AWS region or provider-specific location
        auth_type: Authentication method (iam|managed_identity|approle|env)
        metadata: Provider-specific settings (KMS key ID, etc.)
    """
    
    provider_type: str
    endpoint: Optional[str] = None
    region: Optional[str] = None
    auth_type: str = "env"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        from cortex.secrets.errors import ConfigError
        
        if self.provider_type not in ("aws", "azure", "vault", "local"):
            raise ConfigError(f"Invalid provider_type: {self.provider_type}")
        
        if self.provider_type == "aws" and not self.region:
            self.region = "us-east-1"
