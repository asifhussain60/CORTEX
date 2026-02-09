"""Azure Key Vault provider (stub for Phase 51 S3)"""
from cortex.secrets.provider import ISecretsProvider
from cortex.secrets.config import SecretsConfig
from typing import Optional, Dict, Any, List

class AzureKeyVaultProvider(ISecretsProvider):
    def __init__(self, config: SecretsConfig):
        self.config = config
    
    def get(self, secret_id: str) -> Optional[str]:
        pass
    
    def set(self, secret_id: str, value: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        pass
    
    def delete(self, secret_id: str) -> None:
        pass
    
    def rotate(self, secret_id: str) -> str:
        return ""
    
    def list(self, prefix: str = "") -> List[str]:
        return []
