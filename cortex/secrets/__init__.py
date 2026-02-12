"""
Phase 51: Secrets Management & Audit Trail Hardening
Core provider interface and configuration

AC_START: AC-AUDIT-2026-02-12-001
Fix: CORE-035 violation - Remove duplicate ISecretsProvider definition
Resolution: Import from cortex.secrets.provider (canonical source)
"""

from typing import Any, Dict, List, Optional

# Import canonical ISecretsProvider from provider module
from cortex.secrets.provider import ISecretsProvider

from cortex.secrets.encryption import (
    EncryptedValue,
    EncryptionManager,
    decrypt_value,
    derive_key,
    encrypt_value,
)
