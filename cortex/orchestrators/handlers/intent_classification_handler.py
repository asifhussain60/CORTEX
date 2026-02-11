"""
Intent Classification Handler - AC-REM-HIGH-001

Extracted from MasterOrchestrator to handle intent classification
and context analysis (LENS Protocol).

Implements: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
CORE-013 (specific exceptions)
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from cortex.core.result import Err, Ok, Result
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


@dataclass
class Intent:
    """Represents a classified operation intent."""

    intent_type: str
    scope: str  # File, Module, System, Domain
    confidence: float  # 0.0-1.0
    context: Dict[str, Any]
    ac_id: Optional[str] = None


class IntentClassificationHandler:
    """
    Handle intent classification using LENS Protocol.

    LENS Framework:
    - Language: NLP analysis
    - Examination: AST parsing
    - Navigation: Git history analysis
    - Synthesis: Context aggregation

    AC-ID: AC-CORE-008 (TDD), AC-CORE-011 (type hints)
    """

    def __init__(self) -> None:
        """Initialize handler with logger."""
        self.logger = EnhancedAuditLogger.instance()

    def classify(self, text: str, context: Dict[str, Any]) -> Result[Intent]:
        """
        Classify operation intent.

        Args:
            text: Operation text
            context: Operation context (file, module, etc.)

        Returns:
            Result with classified Intent or error details

        Raises:
            ValueError: If text is empty or invalid
        """
        try:
            if not text or not isinstance(text, str):
                return Err("Invalid intent text: must be non-empty string")

            # Perform intent classification
            intent_type = self._analyze_text(text)
            scope = self._determine_scope(context)
            confidence = self._calculate_confidence(text, context)
            ac_id = self._extract_ac_id(text)

            intent = Intent(
                intent_type=intent_type,
                scope=scope,
                confidence=confidence,
                context=context,
                ac_id=ac_id,
            )

            self.logger.log_operation(
                operation="INTENT_CLASSIFIED",
                details={"intent_type": intent_type, "confidence": confidence},
                ac_id=ac_id,
            )

            return Ok(intent)

        except ValueError as e:
            self.logger.log_error(f"Intent classification validation failed: {e}")
            return Err(f"Classification failed: {e}")
        except KeyError as e:
            self.logger.log_error(f"Missing context key: {e}")
            return Err(f"Missing context: {e}")
        except Exception as e:
            self.logger.log_error(
                f"Unexpected error in intent classification: {e}",
                exc_info=True,
            )
            return Err(f"Unexpected error: {e}")

    def _analyze_text(self, text: str) -> str:
        """
        Analyze text to determine intent type.

        Returns:
            Intent type (e.g., "CODE_REVIEW", "IMPLEMENTATION", "TESTING")
        """
        text_lower = text.lower()

        if any(x in text_lower for x in ["test", "unit", "integration"]):
            return "TESTING"
        elif any(x in text_lower for x in ["review", "check", "validate"]):
            return "CODE_REVIEW"
        elif any(x in text_lower for x in ["implement", "create", "add"]):
            return "IMPLEMENTATION"
        else:
            return "GENERAL"

    def _determine_scope(self, context: Dict[str, Any]) -> str:
        """
        Determine operation scope.

        Returns:
            Scope (File, Module, System, Domain)
        """
        if "file_path" in context:
            return "File"
        elif "module_name" in context:
            return "Module"
        elif "domain" in context:
            return "Domain"
        else:
            return "System"

    def _calculate_confidence(self, text: str, context: Dict[str, Any]) -> float:
        """
        Calculate classification confidence.

        Returns:
            Confidence score 0.0-1.0
        """
        score = 0.5

        if len(text) > 20:
            score += 0.1
        if context:
            score += 0.2
        if "ac_id" in text.upper():
            score += 0.2

        return min(score, 1.0)

    def _extract_ac_id(self, text: str) -> Optional[str]:
        """
        Extract AC-ID from text if present.

        Returns:
            AC-ID string or None
        """
        import re
        match = re.search(r'AC-[A-Z0-9]+-\d+', text)
        return match.group(0) if match else None
