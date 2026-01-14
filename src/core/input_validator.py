"""
Input Validation Framework for CORTEX

This module implements the Input Validation Framework (AC-VALIDATE-001 through AC-VALIDATE-005)
that gates all LLM inputs and prevents hallucinations through structured validation.

Components:
- InputValidator: Main validation orchestrator
- ValidationResult: Result dataclass for validation outcomes
- CanonicalIntent: Standardized intent representation
- ValidationError: Custom exception for validation failures
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Any
import json
import logging

from src.core.governance_registry import GovernanceRegistry


class SeverityLevel(Enum):
    """Severity levels for validation errors"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationError:
    """Represents a validation error"""
    code: str
    message: str
    severity: SeverityLevel
    context: Optional[Dict[str, Any]] = None
    remediation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary"""
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "context": self.context or {},
            "remediation": self.remediation
        }


@dataclass
class CanonicalIntent:
    """Standardized intent representation (AC-VALIDATE-001)"""
    original_intent: str
    canonical_form: str
    intent_type: str  # e.g., "implement", "fix", "validate", "query"
    confidence_score: float  # 0.0-1.0
    ambiguity_resolved: bool
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate canonical form"""
        if not self.canonical_form:
            raise ValueError("canonical_form cannot be empty")
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError("confidence_score must be between 0.0 and 1.0")


@dataclass
class ValidationResult:
    """Result of input validation"""
    input_id: str
    valid: bool
    timestamp: datetime
    validation_method: str
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    validation_time_ms: float = 0.0

    def has_errors(self) -> bool:
        """Check if validation has critical errors"""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if validation has warnings"""
        return len(self.warnings) > 0

    def error_count(self) -> int:
        """Get total error count"""
        return len(self.errors)

    def warning_count(self) -> int:
        """Get total warning count"""
        return len(self.warnings)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "input_id": self.input_id,
            "valid": self.valid,
            "timestamp": self.timestamp.isoformat(),
            "validation_method": self.validation_method,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
            "error_count": self.error_count(),
            "warning_count": self.warning_count(),
            "validation_time_ms": self.validation_time_ms,
            "metadata": self.metadata
        }


class InputValidator:
    """
    Main validator for LLM inputs.
    
    Implements:
    - AC-VALIDATE-001: Intent canonicalization
    - AC-VALIDATE-002: AC-ID existence check
    - AC-VALIDATE-003: Evidence bundle pre-check
    - AC-VALIDATE-004: Cross-reference coherence
    - AC-VALIDATE-005: Semantic output validation
    """

    # AC-ID pattern: AC-{CATEGORY}-{NNN}
    AC_ID_PATTERN = re.compile(r"^AC-[A-Z0-9]+-\d{3}$")
    
    # Common intent canonicalization mappings
    INTENT_MAPPINGS = {
        "impl": "implement",
        "add": "implement",
        "create": "implement",
        "build": "implement",
        "debug": "fix",
        "bug": "fix",
        "issue": "fix",
        "broken": "fix",
        "test": "validate",
        "verify": "validate",
        "check": "validate",
        "ask": "query",
        "how": "query",
        "what": "query",
        "why": "query",
    }

    def __init__(self):
        """Initialize InputValidator"""
        self.logger = logging.getLogger(__name__)
        self.governance_registry = GovernanceRegistry.instance()
        self._ac_id_cache: Set[str] = set()
        self._last_cache_update = None

    def validate_input(self, input_text: str, input_id: str = None) -> ValidationResult:
        """
        Comprehensive input validation orchestrator.
        
        Applies all validation checks in sequence:
        1. Intent canonicalization (AC-VALIDATE-001)
        2. AC-ID existence (AC-VALIDATE-002)
        3. Evidence bundle structure (AC-VALIDATE-003)
        4. Cross-reference coherence (AC-VALIDATE-004)
        5. Semantic validation (AC-VALIDATE-005)
        
        Args:
            input_text: The input text to validate
            input_id: Optional unique identifier for this input
        
        Returns:
            ValidationResult with all validation checks
        """
        start_time = datetime.now()
        input_id = input_id or f"input_{datetime.now().isoformat()}"
        
        result = ValidationResult(
            input_id=input_id,
            valid=True,
            timestamp=datetime.now(),
            validation_method="comprehensive"
        )

        try:
            # AC-VALIDATE-001: Intent canonicalization
            self._validate_intent_canonicalization(input_text, result)
            
            # AC-VALIDATE-002: AC-ID existence check
            self._validate_ac_id_existence(input_text, result)
            
            # AC-VALIDATE-003: Evidence bundle structure
            self._validate_evidence_bundle_structure(input_text, result)
            
            # AC-VALIDATE-004: Cross-reference coherence
            self._validate_cross_reference_coherence(input_text, result)
            
            # AC-VALIDATE-005: Semantic output validation
            self._validate_semantic_output(input_text, result)
            
        except Exception as e:
            self.logger.error(f"Validation error for {input_id}: {str(e)}")
            result.errors.append(ValidationError(
                code="VALIDATION_EXCEPTION",
                message=f"Unexpected validation error: {str(e)}",
                severity=SeverityLevel.CRITICAL
            ))
            result.valid = False

        # Set final validity based on critical errors
        result.valid = not result.has_errors()
        
        # Calculate validation time
        result.validation_time_ms = (datetime.now() - start_time).total_seconds() * 1000

        # Log the validation (for tracking AC-VALIDATE metrics)
        self.logger.info(
            f"Validation complete for {input_id}: valid={result.valid}, "
            f"errors={result.error_count()}, warnings={result.warning_count()}, "
            f"time_ms={result.validation_time_ms}"
        )

        return result

    def _validate_intent_canonicalization(
        self, 
        input_text: str, 
        result: ValidationResult
    ) -> None:
        """
        AC-VALIDATE-001: Intent canonicalization.
        
        Resolves intent ambiguity by standardizing user intent to canonical form.
        Maps colloquial terms to standard intent types.
        """
        if not input_text or len(input_text.strip()) == 0:
            result.errors.append(ValidationError(
                code="EMPTY_INPUT",
                message="Input text cannot be empty",
                severity=SeverityLevel.ERROR,
                remediation="Provide a non-empty input"
            ))
            return

        canonical_intent = self._canonicalize_intent(input_text)
        result.metadata["canonical_intent"] = {
            "original": canonical_intent.original_intent,
            "canonical": canonical_intent.canonical_form,
            "type": canonical_intent.intent_type,
            "confidence": canonical_intent.confidence_score,
            "ambiguity_resolved": canonical_intent.ambiguity_resolved
        }

        # Warn if confidence is low
        if canonical_intent.confidence_score < 0.7:
            result.warnings.append(ValidationError(
                code="LOW_CONFIDENCE_INTENT",
                message=f"Intent canonicalization confidence low: {canonical_intent.confidence_score:.2f}",
                severity=SeverityLevel.WARNING,
                remediation="Consider rephrasing the input more clearly"
            ))

    def _validate_ac_id_existence(
        self,
        input_text: str,
        result: ValidationResult
    ) -> None:
        """
        AC-VALIDATE-002: AC-ID existence check.
        
        Verifies that all referenced AC-IDs exist in the governance registry.
        """
        # Find all AC-IDs in the input
        ac_ids = self._extract_ac_ids(input_text)
        
        if not ac_ids:
            # No AC-IDs mentioned - this is fine
            result.metadata["ac_ids_found"] = 0
            return

        result.metadata["ac_ids_found"] = len(ac_ids)
        result.metadata["ac_ids"] = list(ac_ids)

        # Check each AC-ID against governance registry
        missing_ac_ids = []
        for ac_id in ac_ids:
            if not self._ac_id_exists(ac_id):
                missing_ac_ids.append(ac_id)

        if missing_ac_ids:
            result.errors.append(ValidationError(
                code="INVALID_AC_IDS",
                message=f"The following AC-IDs do not exist: {', '.join(missing_ac_ids)}",
                severity=SeverityLevel.ERROR,
                context={"missing_ac_ids": missing_ac_ids},
                remediation="Verify AC-ID references in PHASE roadmap YAML files"
            ))

    def _validate_evidence_bundle_structure(
        self,
        input_text: str,
        result: ValidationResult
    ) -> None:
        """
        AC-VALIDATE-003: Evidence bundle pre-check.
        
        Validates structure of evidence bundles mentioned in input.
        """
        # Look for evidence bundle patterns in the input
        # Evidence bundles typically contain JSON or structured data
        
        try:
            # Try to find JSON structures
            json_patterns = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', input_text)
            
            for json_str in json_patterns:
                try:
                    json.loads(json_str)
                except json.JSONDecodeError as e:
                    result.errors.append(ValidationError(
                        code="MALFORMED_JSON",
                        message=f"Malformed JSON in evidence bundle: {str(e)}",
                        severity=SeverityLevel.ERROR,
                        context={"json_sample": json_str[:100]},
                        remediation="Ensure all JSON is valid and properly formatted"
                    ))

            result.metadata["evidence_bundles_checked"] = len(json_patterns)
            
        except Exception as e:
            result.warnings.append(ValidationError(
                code="EVIDENCE_CHECK_ERROR",
                message=f"Could not fully validate evidence bundles: {str(e)}",
                severity=SeverityLevel.WARNING
            ))

    def _validate_cross_reference_coherence(
        self,
        input_text: str,
        result: ValidationResult
    ) -> None:
        """
        AC-VALIDATE-004: Cross-reference coherence.
        
        Verifies that AC-ID references are consistent and resolve correctly.
        """
        ac_ids = self._extract_ac_ids(input_text)
        
        if not ac_ids:
            return

        # Get all referenced rules/requirements
        referenced_items = {}
        for ac_id in ac_ids:
            try:
                rules = self.governance_registry.get_rules_by_ac_id(ac_id)
                referenced_items[ac_id] = {
                    "rule_count": len(rules),
                    "rules": [r.get("rule_id", "unknown") for r in rules]
                }
            except Exception as e:
                result.warnings.append(ValidationError(
                    code="CROSS_REF_LOOKUP_FAILED",
                    message=f"Could not resolve cross-references for {ac_id}: {str(e)}",
                    severity=SeverityLevel.WARNING
                ))

        result.metadata["cross_references"] = referenced_items

    def _validate_semantic_output(
        self,
        input_text: str,
        result: ValidationResult
    ) -> None:
        """
        AC-VALIDATE-005: Semantic output validation.
        
        Validates semantic correctness of the input (no contradictions, etc.)
        """
        # Check for common semantic issues
        semantic_issues = []

        # Check for contradictory statements
        if self._has_contradictions(input_text):
            semantic_issues.append(ValidationError(
                code="SEMANTIC_CONTRADICTION",
                message="Input contains contradictory statements",
                severity=SeverityLevel.WARNING,
                remediation="Review input for logical contradictions"
            ))

        # Check for circular references
        ac_ids = self._extract_ac_ids(input_text)
        if len(ac_ids) > 1:
            if self._has_circular_references(ac_ids):
                semantic_issues.append(ValidationError(
                    code="CIRCULAR_REFERENCE",
                    message="Input contains circular AC-ID references",
                    severity=SeverityLevel.ERROR,
                    remediation="Remove circular dependencies between AC-IDs"
                ))

        # Add all semantic issues to result
        for issue in semantic_issues:
            if issue.severity == SeverityLevel.ERROR:
                result.errors.append(issue)
            else:
                result.warnings.append(issue)

        result.metadata["semantic_checks"] = {
            "has_contradictions": any(
                issue.code == "SEMANTIC_CONTRADICTION" for issue in semantic_issues
            ),
            "has_circular_refs": any(
                issue.code == "CIRCULAR_REFERENCE" for issue in semantic_issues
            )
        }

    def _canonicalize_intent(self, input_text: str) -> CanonicalIntent:
        """
        Convert colloquial input intent to canonical form.
        
        Returns CanonicalIntent with standardized intent type.
        """
        text_lower = input_text.lower()
        
        # Default intent type
        intent_type = "query"
        confidence_score = 0.5
        ambiguity_resolved = False

        # Check for known intent mappings - prioritize by specificity
        # First check for exact word boundaries (highest priority)
        best_match = None
        best_score = -1  # Start at -1 so we can prioritize word boundaries
        
        for colloquial, canonical in self.INTENT_MAPPINGS.items():
            if colloquial in text_lower:
                # Check if it's a complete word (word boundary) - give it higher priority
                pattern = r'\b' + re.escape(colloquial) + r'\b'
                if re.search(pattern, text_lower):
                    match_score = len(colloquial) * 10  # 10x priority for word boundary
                else:
                    match_score = len(colloquial)
                
                if match_score > best_score:
                    best_score = match_score
                    best_match = canonical
        
        if best_match:
            intent_type = best_match
            confidence_score = 0.9
            ambiguity_resolved = True
        else:
            # If still at default, check for obvious patterns
            if any(word in text_lower for word in ["implement", "create", "build"]):
                intent_type = "implement"
                confidence_score = 0.85
                ambiguity_resolved = True
            elif any(word in text_lower for word in ["fix", "debug", "broken"]):
                intent_type = "fix"
                confidence_score = 0.85
                ambiguity_resolved = True
            elif any(word in text_lower for word in ["test", "verify", "validate"]):
                intent_type = "validate"
                confidence_score = 0.85
                ambiguity_resolved = True

        return CanonicalIntent(
            original_intent=input_text,
            canonical_form=f"INTENT: {intent_type.upper()}",
            intent_type=intent_type,
            confidence_score=confidence_score,
            ambiguity_resolved=ambiguity_resolved
        )

    def _extract_ac_ids(self, text: str) -> Set[str]:
        """Extract all AC-IDs from text"""
        # Pattern: AC-{ALPHANUM+}-{0-9} where {ALPHANUM+} can contain letters and numbers
        # E.g., AC-AR-006-01, AC-FR-002-03, AC-VALIDATE-001
        pattern = r"AC-[A-Z][A-Z0-9]*-\d{3}(?:-\d{2})?"
        matches = re.findall(pattern, text)
        return set(matches)

    def _ac_id_exists(self, ac_id: str) -> bool:
        """Check if AC-ID exists in governance registry"""
        try:
            rules = self.governance_registry.get_rules_by_ac_id(ac_id)
            return len(rules) > 0
        except Exception:
            return False

    def _has_contradictions(self, text: str) -> bool:
        """Detect obvious contradictions in text"""
        text_lower = text.lower()
        
        contradictions = [
            ("must not" in text_lower and "must" in text_lower),
            ("cannot" in text_lower and "should" in text_lower and "required" in text_lower),
        ]
        
        return any(contradictions)

    def _has_circular_references(self, ac_ids: Set[str]) -> bool:
        """Detect circular dependencies between AC-IDs"""
        if len(ac_ids) < 2:
            return False

        # Build dependency graph
        dependencies: Dict[str, Set[str]] = {}
        for ac_id in ac_ids:
            try:
                rules = self.governance_registry.get_rules_by_ac_id(ac_id)
                dependencies[ac_id] = set()
                for rule in rules:
                    depends_on = rule.get("depends_on", [])
                    if depends_on:
                        for dep in depends_on:
                            if isinstance(dep, dict):
                                dep_ac_id = dep.get("ac_id")
                            else:
                                dep_ac_id = str(dep)
                            if dep_ac_id in ac_ids:
                                dependencies[ac_id].add(dep_ac_id)
            except Exception:
                continue

        # Check for cycles using DFS
        def has_cycle(node: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in dependencies.get(node, set()):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        visited: Set[str] = set()
        for ac_id in ac_ids:
            if ac_id not in visited:
                if has_cycle(ac_id, visited, set()):
                    return True

        return False
