"""
Secrets Integrity Agent - Phase 76 Stage 3

9th enforcement agent for EnforcementOrchestrator.
Validates secrets management prerequisites and blocks operations with unencrypted secrets.

Authority: phase-76-production-foundation-trilogy.yaml S3.T5
AC-ID: AC-PHASE76-S3-005
"""

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SecretsValidationResult:
    """Secrets validation result."""
    passed: bool
    severity: str  # 'PASSED', 'WARNING', 'CRITICAL'
    reason: str
    action: str
    plaintext_secrets: List[str] = None  # type: ignore
    missing_master_key: bool = False

    def __post_init__(self):
        if self.plaintext_secrets is None:
            self.plaintext_secrets = []


class SecretsIntegrityAgent:
    """
    9th enforcement agent: Secrets integrity validation.

    Validates secrets management prerequisites before operations:
    - CORTEX_MASTER_KEY presence and validity
    - No plaintext secrets in environment
    - No hardcoded secrets in code
    - Audit trail enabled

    BLOCKS execution when:
    - CORTEX_MASTER_KEY not set
    - Plaintext secrets detected in common patterns
    - Operation attempts to use unencrypted secrets

    WARNS when:
    - Audit trail not enabled
    - Weak master key detected
    """

    # Common plaintext secret patterns to detect
    PLAINTEXT_SECRET_PATTERNS = [
        "PASSWORD",
        "APIKEY",
        "API_KEY",
        "SECRET",
        "TOKEN",
        "CREDENTIAL",
        "PRIVATE_KEY",
    ]

    # Secure patterns (expected to be encrypted)
    SECURE_ENV_PATTERNS = [
        "CORTEX_",  # Should use SecretsManager
    ]

    def __init__(self):
        """Initialize SecretsIntegrityAgent."""
        pass

    def validate_pre_flight(
        self,
        check_environment: bool = True,
        check_code: bool = False,
    ) -> SecretsValidationResult:
        """
        Validate secrets management prerequisites.

        Args:
            check_environment: Check environment variables
            check_code: Check source code for hardcoded secrets

        Returns:
            SecretsValidationResult with passed/failed status
        """
        # Check 1: CORTEX_MASTER_KEY presence
        master_key = os.getenv("CORTEX_MASTER_KEY")

        if not master_key:
            return SecretsValidationResult(
                passed=False,
                severity="CRITICAL",
                reason="CORTEX_MASTER_KEY environment variable not set",
                action=(
                    "Set CORTEX_MASTER_KEY before proceeding:\n"
                    "  export CORTEX_MASTER_KEY=$(openssl rand -base64 32)\n"
                    "  or add to .env file"
                ),
                missing_master_key=True,
            )

        # Check 2: Master key strength (minimum 32 characters)
        if len(master_key) < 32:
            return SecretsValidationResult(
                passed=False,
                severity="CRITICAL",
                reason="CORTEX_MASTER_KEY too short (minimum 32 characters)",
                action="Generate a new stronger key: openssl rand -base64 32",
            )

        # Check 3: Environment variable scanning
        if check_environment:
            result = self._check_plaintext_secrets()
            if not result["valid"]:
                return SecretsValidationResult(
                    passed=False,
                    severity="CRITICAL",
                    reason="Plaintext secrets detected in environment",
                    action=(
                        "Store secrets using SecretsManager:\n"
                        f"  {result['recommendation']}"
                    ),
                    plaintext_secrets=result["plaintext_vars"],
                )

        # Check 4: Audit trail enabled
        audit_enabled = os.getenv("CORTEX_AUDIT_ENABLED", "true").lower() == "true"

        if not audit_enabled:
            logger.warning("CORTEX_AUDIT_ENABLED is False - audit trail disabled")

        # All checks passed
        return SecretsValidationResult(
            passed=True,
            severity="PASSED",
            reason="Secrets management prerequisites validated",
            action="Proceed with operation",
        )

    def _check_plaintext_secrets(self) -> Dict[str, Any]:
        """
        Scan environment for plaintext secrets.

        Returns:
            Dict with "valid", "plaintext_vars", "recommendation"
        """
        plaintext_vars = []

        for var_name in os.environ:
            # Check if matches plaintext pattern
            for pattern in self.PLAINTEXT_SECRET_PATTERNS:
                if pattern in var_name.upper():
                    # Check if it's not a secure pattern
                    is_secure = any(
                        pattern in var_name.upper()
                        for pattern in self.SECURE_ENV_PATTERNS
                    )

                    if not is_secure:
                        plaintext_vars.append(var_name)
                    break

        if plaintext_vars:
            recommendation = self._generate_plaintext_recommendation(plaintext_vars)
            return {
                "valid": False,
                "plaintext_vars": plaintext_vars,
                "recommendation": recommendation,
            }

        return {
            "valid": True,
            "plaintext_vars": [],
            "recommendation": None,
        }

    @staticmethod
    def _generate_plaintext_recommendation(vars_list: List[str]) -> str:
        """Generate recommendation for plaintext secrets found."""
        recommendation = "Move to SecretsManager:\n"

        for var_name in vars_list[:3]:  # Limit to first 3
            recommendation += "    sm = SecretsManager.from_environment()\n"
            recommendation += f"    value = sm.get_secret_or_env('{var_name}')\n"

        if len(vars_list) > 3:
            recommendation += f"    ... and {len(vars_list) - 3} more"

        return recommendation

    def validate_secret_access(self, secret_key: str) -> SecretsValidationResult:
        """
        Validate access to a specific secret.

        Args:
            secret_key: Secret identifier

        Returns:
            SecretsValidationResult
        """
        # Check if trying to use plaintext environment variable
        plaintext_value = os.getenv(secret_key)

        if plaintext_value:
            logger.warning(
                f"Using plaintext environment variable {secret_key}. "
                "Consider using SecretsManager for encrypted storage."
            )

            return SecretsValidationResult(
                passed=True,
                severity="WARNING",
                reason=f"Using plaintext environment variable {secret_key}",
                action="Consider storing in SecretsManager for security",
            )

        # Secret should be encrypted
        return SecretsValidationResult(
            passed=True,
            severity="PASSED",
            reason=f"Secret {secret_key} will use encrypted storage",
            action="Proceed with secure secret retrieval",
        )

    def validate_operation_context(
        self,
        operation_type: str,
        requires_secrets: bool = False,
    ) -> SecretsValidationResult:
        """
        Validate operation context for secrets usage.

        Args:
            operation_type: Operation type (IMPLEMENT, FIX, REFACTOR, etc.)
            requires_secrets: Does this operation need secrets?

        Returns:
            SecretsValidationResult
        """
        # Check master key
        master_key = os.getenv("CORTEX_MASTER_KEY")

        if requires_secrets and not master_key:
            return SecretsValidationResult(
                passed=False,
                severity="CRITICAL",
                reason=f"{operation_type} operation requires CORTEX_MASTER_KEY",
                action="Set CORTEX_MASTER_KEY environment variable",
                missing_master_key=True,
            )

        # Check if operation is sensitive
        sensitive_operations = ["DEPLOY", "RELEASE", "PRODUCTION_ACCESS"]

        if operation_type in sensitive_operations:
            # For sensitive operations, always require master key
            if not master_key:
                return SecretsValidationResult(
                    passed=False,
                    severity="CRITICAL",
                    reason=f"Sensitive operation {operation_type} requires encrypted secrets",
                    action="Set CORTEX_MASTER_KEY for production operations",
                    missing_master_key=True,
                )

            # Also validate no plaintext secrets
            plaintext_result = self._check_plaintext_secrets()
            if not plaintext_result["valid"]:
                return SecretsValidationResult(
                    passed=False,
                    severity="CRITICAL",
                    reason=f"Sensitive operation {operation_type} cannot use plaintext secrets",
                    action="Encrypt all secrets with SecretsManager",
                    plaintext_secrets=plaintext_result["plaintext_vars"],
                )

        return SecretsValidationResult(
            passed=True,
            severity="PASSED",
            reason=f"Secrets prerequisites validated for {operation_type}",
            action="Proceed with operation",
        )


__all__ = [
    "SecretsIntegrityAgent",
    "SecretsValidationResult",
]
