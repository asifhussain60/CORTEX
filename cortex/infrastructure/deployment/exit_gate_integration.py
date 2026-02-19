"""
EXIT GATE Deployment Validation Integration (Phase 38 Stage 10).

Integrates DeploymentValidator into MasterOrchestrator EXIT GATE for pre-deployment
validation and production readiness checks.

AC_START: AC-PHASE38-S10-002
Phase: 38 | Stage: 10 | Priority: P0
Description: EXIT GATE deployment validator integration
Requirements: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from cortex.deployment.deployment_validator import (
    DeploymentMode,
    DeploymentValidator,
    ValidationResult,
)

logger = logging.getLogger(__name__)


@dataclass
class DeploymentGateResult:
    """Result of EXIT GATE deployment validation.

    Attributes:
        allowed: Whether deployment is allowed to proceed
        validation_result: Detailed validation result
        gate_time_ms: Time spent in gate validation (ms)
        audit_id: Audit trail identifier
        block_reason: Reason deployment was blocked (if allowed=False)
    """
    allowed: bool
    validation_result: Optional[ValidationResult]
    gate_time_ms: float
    audit_id: str
    block_reason: Optional[str] = None


class DeploymentExitGate:
    """EXIT GATE integration for deployment validation.

    Provides pre-deployment validation checks integrated into the
    MasterOrchestrator EXIT GATE. Validates deployment readiness
    before allowing production deployment operations.

    Attributes:
        validator: DeploymentValidator instance
        audit_logger: Logger for audit trail
        fail_safe: Whether to allow deployment on validation errors
    """

    def __init__(
        self,
        mcp_endpoint: str = "http://localhost:8443",
        saas_api_endpoint: str = "http://localhost:8000",
        timeout: int = 30,
        fail_safe: bool = True
    ) -> None:
        """Initialize deployment EXIT GATE.

        Args:
            mcp_endpoint: MCP server endpoint URL
            saas_api_endpoint: SaaS API endpoint URL
            timeout: Validation timeout in seconds
            fail_safe: Allow deployment on validation errors (default: True)
        """
        self.validator = DeploymentValidator(
            mcp_endpoint=mcp_endpoint,
            saas_api_endpoint=saas_api_endpoint,
            timeout=timeout
        )
        self.audit_logger = logging.getLogger("cortex.deployment.audit")
        self.fail_safe = fail_safe

    async def validate_deployment_gate(
        self,
        operation_name: str,
        parameters: Dict[str, Any]
    ) -> DeploymentGateResult:
        """Validate deployment through EXIT GATE.

        Performs pre-deployment validation checks and determines whether
        deployment should be allowed to proceed.

        Args:
            operation_name: Name of operation (e.g., "deploy_mcp", "deploy_saas")
            parameters: Operation parameters containing deployment mode

        Returns:
            DeploymentGateResult with validation outcome
        """
        import time
        start_time = time.time()

        # Generate audit ID
        audit_id = f"AC-DEPLOY-{int(start_time * 1000)}"

        # AC_START marker
        self.audit_logger.info(f"AC_START: {audit_id}")
        self.audit_logger.info(f"Deployment validation: {operation_name}")

        try:
            # Detect deployment mode from parameters
            mode = self._detect_deployment_mode(operation_name, parameters)

            if mode is None:
                # Not a deployment operation - allow
                gate_time_ms = (time.time() - start_time) * 1000
                self.audit_logger.info(f"AC_COMPLETE: {audit_id} ✅ Not deployment operation")
                return DeploymentGateResult(
                    allowed=True,
                    validation_result=None,
                    gate_time_ms=gate_time_ms,
                    audit_id=audit_id
                )

            # Run validation
            self.audit_logger.info(f"Running deployment validation: mode={mode.value}")
            validation_result = await self.validator.validate_deployment(mode)

            gate_time_ms = (time.time() - start_time) * 1000

            # Determine if deployment allowed
            if validation_result.success:
                self.audit_logger.info(f"AC_COMPLETE: {audit_id} ✅ Deployment validation passed")
                self.audit_logger.info(f"Checks passed: {', '.join(validation_result.checks_passed)}")
                return DeploymentGateResult(
                    allowed=True,
                    validation_result=validation_result,
                    gate_time_ms=gate_time_ms,
                    audit_id=audit_id
                )
            else:
                # Validation failed
                block_reason = f"Validation failed: {', '.join(validation_result.errors)}"

                if self.fail_safe:
                    # Fail-safe mode: log error but allow deployment
                    self.audit_logger.warning(f"AC_COMPLETE: {audit_id} ⚠️ Validation failed (FAIL-SAFE)")
                    self.audit_logger.warning(f"Errors: {block_reason}")
                    self.audit_logger.warning("Deployment allowed due to fail_safe=True")
                    return DeploymentGateResult(
                        allowed=True,
                        validation_result=validation_result,
                        gate_time_ms=gate_time_ms,
                        audit_id=audit_id,
                        block_reason=block_reason
                    )
                else:
                    # Strict mode: block deployment
                    self.audit_logger.error(f"AC_COMPLETE: {audit_id} ❌ Deployment blocked")
                    self.audit_logger.error(f"Block reason: {block_reason}")
                    return DeploymentGateResult(
                        allowed=False,
                        validation_result=validation_result,
                        gate_time_ms=gate_time_ms,
                        audit_id=audit_id,
                        block_reason=block_reason
                    )

        except Exception as e:
            gate_time_ms = (time.time() - start_time) * 1000
            error_msg = f"Deployment validation error: {str(e)}"

            if self.fail_safe:
                # Fail-safe: log error but allow
                self.audit_logger.warning(f"AC_COMPLETE: {audit_id} ⚠️ Validation error (FAIL-SAFE)")
                self.audit_logger.warning(error_msg)
                return DeploymentGateResult(
                    allowed=True,
                    validation_result=None,
                    gate_time_ms=gate_time_ms,
                    audit_id=audit_id,
                    block_reason=error_msg
                )
            else:
                # Strict: block on error
                self.audit_logger.error(f"AC_COMPLETE: {audit_id} ❌ Deployment blocked (error)")
                self.audit_logger.error(error_msg)
                return DeploymentGateResult(
                    allowed=False,
                    validation_result=None,
                    gate_time_ms=gate_time_ms,
                    audit_id=audit_id,
                    block_reason=error_msg
                )

    def _detect_deployment_mode(
        self,
        operation_name: str,
        parameters: Dict[str, Any]
    ) -> Optional[DeploymentMode]:
        """Detect deployment mode from operation and parameters.

        Args:
            operation_name: Name of operation
            parameters: Operation parameters

        Returns:
            DeploymentMode or None if not deployment operation
        """
        # Check operation name
        if "deploy" not in operation_name.lower():
            return None

        # Check for explicit mode parameter
        mode_str = parameters.get("mode", "").lower()
        if mode_str == "mcp":
            return DeploymentMode.MCP
        elif mode_str == "saas":
            return DeploymentMode.SAAS
        elif mode_str == "hybrid":
            return DeploymentMode.HYBRID

        # Detect from operation name
        if "mcp" in operation_name.lower():
            return DeploymentMode.MCP
        elif "saas" in operation_name.lower():
            return DeploymentMode.SAAS

        # Default to MCP for generic "deploy"
        return DeploymentMode.MCP


def create_deployment_gate(
    mcp_endpoint: str = "http://localhost:8443",
    saas_api_endpoint: str = "http://localhost:8000",
    timeout: int = 30,
    fail_safe: bool = True
) -> DeploymentExitGate:
    """Factory function to create deployment EXIT GATE.

    Args:
        mcp_endpoint: MCP server endpoint URL
        saas_api_endpoint: SaaS API endpoint URL
        timeout: Validation timeout in seconds
        fail_safe: Allow deployment on validation errors

    Returns:
        DeploymentExitGate instance
    """
    return DeploymentExitGate(
        mcp_endpoint=mcp_endpoint,
        saas_api_endpoint=saas_api_endpoint,
        timeout=timeout,
        fail_safe=fail_safe
    )


# AC_COMPLETE: AC-PHASE38-S10-002 ✅ EXIT GATE integration module created
