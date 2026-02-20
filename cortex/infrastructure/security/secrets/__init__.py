"""
Phase 51: Secrets Management & Audit Trail Hardening
Core provider interface and configuration

AC_START: AC-AUDIT-2026-02-12-001
Fix: CORE-035 violation - Remove duplicate ISecretsProvider definition
Resolution: Import from cortex.infrastructure.security.secrets.provider (canonical source)

AC_START: AC-PHASE51-EXPORT-001
Enhancement: Export Phase 51 secrets management functions
"""

from typing import Any, Dict, List, Optional

# Import canonical ISecretsProvider from provider module
from cortex.infrastructure.security.secrets.secrets_provider import ISecretsProvider

from cortex.infrastructure.security.secrets.encryption import (
    EncryptedValue,
    EncryptionManager,
    decrypt_value,
    derive_key,
    encrypt_value,
)

# Phase 51: Enhanced secrets management (AES-256-GCM + audit trail + rotation)
from cortex.infrastructure.security.secrets.management import (
    # Encryption
    encrypt_secret,
    decrypt_secret,
    derive_encryption_key,
    get_master_key,
    
    # Vault operations
    store_secret,
    get_secret,
    delete_secret,
    list_secrets,
    
    # Rotation
    check_rotation_status,
    rotate_secret,
    batch_rotate_secrets,
    rollback_secret,
    get_secret_history,
    get_rotation_metrics,
    rotate_encryption_key,
    send_notification,  # Added for test compatibility
    
    # Audit trail
    get_audit_log,
    query_audit_log,
    rotate_audit_log,
    verify_audit_log,
    
    # Log sanitization
    sanitize_log_message,
    sanitize_exception,
    sanitize_json,
    sanitize_command_line,
)

# AC_COMPLETE: AC-PHASE51-EXPORT-001 ✅ Phase 51 functions exported
