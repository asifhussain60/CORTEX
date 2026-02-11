"""
Response Format Integration.

Integration with gateway, enforcement mechanisms,
and production format gate.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 29 Stage 3 specification
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

from cortex.brain.core.response_format_validator import ResponseFormatValidator
from cortex.brain.core.response_optimizer import ResponseOptimizer

logger = logging.getLogger(__name__)


class IntegrationError(Exception):
    """Base exception for integration errors."""
    pass


class EnforcementLevel(Enum):
    """Enforcement strictness levels."""
    STRICT = "STRICT"      # Maximum enforcement
    MODERATE = "MODERATE"  # Balanced enforcement
    LENIENT = "LENIENT"    # Minimal enforcement


@dataclass
class IntegrationResult:
    """
    Integration processing result.

    Attributes:
        final_response: Final formatted response
        corrections_applied: Number of corrections
        validation_score: Validation quality score
        metrics: Optional metrics dictionary
        corrected: Whether corrections were applied
        response: Alias for final_response
    """
    final_response: str
    corrections_applied: int
    validation_score: float
    metrics: Optional[Dict[str, Any]] = None

    @property
    def corrected(self) -> bool:
        """Whether corrections were applied."""
        return self.corrections_applied > 0

    @property
    def response(self) -> str:
        """Alias for final_response."""
        return self.final_response


class FormatEnforcer:
    """
    Format enforcer with configurable levels.

    Enforces format standards with auto-correction.
    """

    def __init__(self, level: EnforcementLevel = EnforcementLevel.MODERATE):
        """
        Initialize enforcer.

        Args:
            level: Enforcement strictness level
        """
        self.level = level
        self.optimizer = ResponseOptimizer()
        logger.info(f"FormatEnforcer initialized with level: {level.value}")

    def enforce(
        self,
        response: str,
        orchestrator: str = "MasterOrchestrator",
    ) -> IntegrationResult:
        """
        Enforce format standards.

        Args:
            response: Response to enforce
            orchestrator: Orchestrator name

        Returns:
            IntegrationResult: Enforcement result
        """
        # Optimize based on level
        if self.level == EnforcementLevel.STRICT:
            # Maximum corrections
            optimization = self.optimizer.optimize(response, orchestrator, improve_flow=True)
        elif self.level == EnforcementLevel.MODERATE:
            # Balanced corrections
            optimization = self.optimizer.optimize(response, orchestrator, improve_flow=True)
        else:  # LENIENT
            # Minimal corrections (header only if missing)
            optimization = self.optimizer.optimize(response, orchestrator, improve_flow=False)

        return IntegrationResult(
            final_response=optimization.optimized_text,
            corrections_applied=len(optimization.corrections),
            validation_score=1.0 - optimization.improvement_score,
        )


class FormatGate:
    """
    Production format gate.

    Validates responses meet quality threshold before release.
    """

    DEFAULT_THRESHOLD = 0.7  # 70% quality minimum
    PRODUCTION_THRESHOLD = 0.85  # 85% for production

    def __init__(self, production_mode: bool = False):
        """
        Initialize format gate.

        Args:
            production_mode: Whether in production mode
        """
        self.production_mode = production_mode
        self.validator = ResponseFormatValidator()
        self.threshold = self.PRODUCTION_THRESHOLD if production_mode else self.DEFAULT_THRESHOLD
        logger.info(f"FormatGate initialized (production={production_mode}, threshold={self.threshold})")

    def check(self, response: str, threshold: Optional[float] = None) -> bool:
        """
        Check if response passes gate.

        Args:
            response: Response to check
            threshold: Optional custom threshold

        Returns:
            bool: True if passes gate
        """
        validation = self.validator.validate(response)

        used_threshold = threshold if threshold is not None else self.threshold

        passed = validation.score >= used_threshold and validation.is_valid

        if not passed:
            logger.warning(
                f"Response failed gate: score={validation.score:.2f}, "
                f"threshold={used_threshold:.2f}, violations={len(validation.violations)}"
            )

        return passed


class ResponseFormatIntegration:
    """
    Response Format Integration System.

    Coordinates validation, optimization, and enforcement across CORTEX.
    """

    def __init__(self, enforcement_level: EnforcementLevel = EnforcementLevel.MODERATE):
        """
        Initialize integration system.

        Args:
            enforcement_level: Enforcement strictness level
        """
        self.validator = ResponseFormatValidator()
        self.optimizer = ResponseOptimizer()
        self.enforcer = FormatEnforcer(level=enforcement_level)
        self.gate = FormatGate()

        logger.info(f"ResponseFormatIntegration initialized with {enforcement_level.value}")

    def process(
        self,
        response: Optional[str],
        orchestrator: str = "MasterOrchestrator",
        enforce: bool = True,
        collect_metrics: bool = False,
    ) -> IntegrationResult:
        """
        Process response through full format pipeline.

        Args:
            response: Response to process
            orchestrator: Orchestrator name
            enforce: Whether to enforce corrections
            collect_metrics: Whether to collect detailed metrics

        Returns:
            IntegrationResult: Processing result
        """
        if not response:
            response = "No content provided."

        try:
            # Validate
            validation = self.validator.validate(response)

            if enforce and not validation.is_valid:
                # Optimize/correct
                optimization = self.optimizer.optimize(response, orchestrator)
                final_response = optimization.optimized_text
                corrections_applied = len(optimization.corrections)
            else:
                final_response = response
                corrections_applied = 0

            # Re-validate
            final_validation = self.validator.validate(final_response)

            # Collect metrics if requested
            metrics = None
            if collect_metrics:
                metrics = {
                    'quality_score': final_validation.score,
                    'validation_score': final_validation.score,
                    'violations': len(final_validation.violations),
                    'corrections_applied': corrections_applied,
                }

            return IntegrationResult(
                final_response=final_response,
                corrections_applied=corrections_applied,
                validation_score=final_validation.score,
                metrics=metrics,
            )

        except Exception as e:
            logger.error(f"Integration processing error: {e}")
            # Return original with error metrics
            return IntegrationResult(
                final_response=response or "Error processing response",
                corrections_applied=0,
                validation_score=0.0,
                metrics={'error': str(e)} if collect_metrics else None,
            )

    def process_gateway_response(
        self,
        gateway_response: Any,
        orchestrator: str = "MasterOrchestrator",
    ) -> IntegrationResult:
        """
        Process gateway response.

        Args:
            gateway_response: Gateway response object
            orchestrator: Orchestrator name

        Returns:
            IntegrationResult: Processing result
        """
        # Extract response text from gateway response
        # Gateway response is a mock in tests, so handle gracefully
        try:
            if hasattr(gateway_response, 'result'):
                response_text = str(gateway_response.result)
            else:
                response_text = str(gateway_response)
        except Exception:
            response_text = "Gateway response processing"

        return self.process(response_text, orchestrator, enforce=True)
