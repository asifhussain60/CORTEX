"""
Security infrastructure components for CORTEX.

Components:
- SecretsFilter: Log-level secret redaction
- InputValidator: Input sanitization and validation
- TokenBucketRateLimiter: Rate limiting with circuit breaker
- CryptoProvider: Cryptographic operations (AES-256-GCM, PBKDF2)
- CORSHandler: CORS and CSRF protection
- SecurityAuditor: Automated security scanning
- DefenseOrchestrator: Defense-in-depth coordination
- CrossRepoEnforcer: Cross-repository security enforcement

Phase: impl-arch-005-hardening (Production Hardening & Security)
Priority: P0 (Production Critical)
"""

from cortex.infrastructure.security.secrets_filter import SecretsFilter
from cortex.brain.core.input_validator import InputValidator
from cortex.infrastructure.security.rate_limiter import TokenBucketRateLimiter
from cortex.infrastructure.security.crypto_provider import CryptoProvider
from cortex.infrastructure.security.cors_handler import CORSHandler
from cortex.infrastructure.security.security_auditor import SecurityAuditor
from cortex.infrastructure.security.defense_orchestrator import DefenseOrchestrator
from cortex.infrastructure.security.cross_repo_enforcer import CrossRepoEnforcer

__all__ = [
    "SecretsFilter",
    "InputValidator",
    "TokenBucketRateLimiter",
    "CryptoProvider",
    "CORSHandler",
    "SecurityAuditor",
    "DefenseOrchestrator",
    "CrossRepoEnforcer",
]
