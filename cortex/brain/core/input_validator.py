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

from cortex.orchestrators.core.governance_registry import GovernanceRegistry


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

    def _validate_ac_id_format(self, ac_ids: Set[str]) -> bool:
        """
        AC-VALIDATE-006: AC-ID format validation.
        
        Validates that all AC-IDs follow the pattern AC-{CATEGORY}-{NNN}
        or AC-{CATEGORY}-{NNN}-{NN} for sub-requirements.
        
        Args:
            ac_ids: Set of AC-IDs to validate
        
        Returns:
            True if all AC-IDs are valid format, False otherwise
        """
        if not ac_ids:
            return True

        # Pattern: AC-{CATEGORY}-{NNN} or AC-{CATEGORY}-{NNN}-{NN}
        # CATEGORY: Must start with letter, followed by letters/numbers
        # NNN: Exactly 3 digits
        # Optional NN: Exactly 2 digits
        format_pattern = r"^AC-[A-Z][A-Z0-9]*-\d{3}(?:-\d{2})?$"

        for ac_id in ac_ids:
            if not re.match(format_pattern, ac_id.strip()):
                return False

        return True

    def _validate_phase_alignment(
        self, ac_ids: Set[str], current_phase: Optional[str] = None
    ) -> bool:
        """
        AC-VALIDATE-007: Phase alignment enforcement.
        
        Validates that request AC-IDs match the current phase.
        E.g., PHASE-02 requests should only reference AC-IDs from PHASE-02.
        
        Args:
            ac_ids: Set of AC-IDs to validate
            current_phase: Current phase (e.g., "PHASE-02")
        
        Returns:
            True if all AC-IDs align with current phase, False otherwise
        """
        if not ac_ids or not current_phase:
            return True

        try:
            # Extract phase number from current_phase (e.g., "PHASE-02" -> "02")
            phase_match = re.match(r"PHASE-(\d+)", current_phase)
            if not phase_match:
                return True  # Cannot determine phase, skip check

            current_phase_num = phase_match.group(1)

            # Extract phase number from each AC-ID
            # AC-IDs from earlier phases are allowed (backward compat)
            for ac_id in ac_ids:
                ac_match = re.match(r"AC-([A-Z0-9]+)-\d{3}", ac_id)
                if ac_match:
                    ac_category = ac_match.group(1)
                    # Try to find this AC-ID in registry
                    try:
                        rules = self.governance_registry.get_rules_by_ac_id(ac_id)
                        for rule in rules:
                            rule_phase = rule.get("phase", "")
                            if rule_phase:
                                # Extract phase number
                                rule_phase_match = re.match(
                                    r"PHASE-(\d+)", rule_phase
                                )
                                if rule_phase_match:
                                    rule_phase_num = rule_phase_match.group(1)
                                    # AC-ID phase must be <= current phase
                                    if int(rule_phase_num) > int(current_phase_num):
                                        return False
                    except Exception:
                        # AC-ID not found in registry, skip phase check
                        continue

            return True

        except Exception as e:
            self.logger.debug(f"Phase alignment check error: {e}")
            return True  # Default to True on error

    def _validate_no_ac_id_conflicts(self, ac_ids: Set[str]) -> bool:
        """
        AC-VALIDATE-008: Request contradiction detection.
        
        Detects conflicting or contradictory AC-IDs in the request.
        Checks for semantic contradictions and mutual exclusivity.
        
        Args:
            ac_ids: Set of AC-IDs to validate
        
        Returns:
            True if no contradictions detected, False if conflicts found
        """
        if len(ac_ids) < 2:
            return True

        try:
            # Build conflict map from registry
            conflict_map: Dict[str, Set[str]] = {}

            for ac_id in ac_ids:
                try:
                    rules = self.governance_registry.get_rules_by_ac_id(ac_id)
                    for rule in rules:
                        conflicts = rule.get("conflicts_with", [])
                        if conflicts:
                            if ac_id not in conflict_map:
                                conflict_map[ac_id] = set()
                            
                            for conflict in conflicts:
                                if isinstance(conflict, dict):
                                    conflict_ac_id = conflict.get("ac_id")
                                else:
                                    conflict_ac_id = str(conflict)
                                
                                if conflict_ac_id:
                                    conflict_map[ac_id].add(conflict_ac_id)
                except Exception:
                    continue

            # Check if any two AC-IDs are in conflict
            for ac_id in ac_ids:
                if ac_id in conflict_map:
                    for conflicting_ac_id in conflict_map[ac_id]:
                        if conflicting_ac_id in ac_ids:
                            return False

            return True

        except Exception as e:
            self.logger.debug(f"AC-ID conflict detection error: {e}")
            return True  # Default to True on error

    def _validate_schema_compliance(self, request_data: Any) -> bool:
        """
        AC-VALIDATE-009: Schema validation.
        
        Validates that the request matches the expected orchestrator input schema.
        
        Args:
            request_data: The request data to validate
        
        Returns:
            True if schema is valid, False otherwise
        """
        try:
            # If request_data is string, try parsing as JSON
            if isinstance(request_data, str):
                try:
                    request_data = json.loads(request_data)
                except json.JSONDecodeError:
                    # String is not JSON, but still valid input
                    return True

            # If request_data is dict, validate structure
            if isinstance(request_data, dict):
                # Required fields for a valid request
                required_fields = ["action", "context"]
                
                for field in required_fields:
                    if field not in request_data:
                        return False

                # Validate action field
                action = request_data.get("action")
                if not isinstance(action, str) or not action.strip():
                    return False

                # Validate context field is dict
                context = request_data.get("context")
                if context is not None and not isinstance(context, dict):
                    return False

                return True

            # If request_data is list, each item should be valid dict
            if isinstance(request_data, list):
                return all(
                    isinstance(item, dict) and "action" in item
                    for item in request_data
                )

            return True

        except Exception as e:
            self.logger.debug(f"Schema validation error: {e}")
            return False

    def _validate_backward_compatibility(self, version: Optional[str] = None) -> bool:
        """
        AC-VALIDATE-010: Backward compatibility checks.
        
        Validates version compatibility of the request with CORTEX components.
        
        Args:
            version: Version string to validate (e.g., "1.0", "2.1")
        
        Returns:
            True if version is compatible, False otherwise
        """
        if not version:
            return True  # No version specified, assume compatible

        try:
            # Current CORTEX version
            current_version = "1.0"
            
            # Parse version string
            version_pattern = r"^(\d+)\.(\d+)(?:\.(\d+))?$"
            match = re.match(version_pattern, version.strip())
            
            if not match:
                return False  # Invalid version format

            major, minor, patch = match.groups()
            major = int(major)
            minor = int(minor)
            patch = int(patch) if patch else 0

            # Current version is 1.0.x
            current_major, current_minor, current_patch = 1, 0, 0

            # Backward compatibility rules:
            # - Major version must match
            # - Minor version must be <= current minor
            # - Patch version is ignored
            if major != current_major:
                return False  # Major version mismatch

            if minor > current_minor:
                return False  # Future minor version

            return True

        except Exception as e:
            self.logger.debug(f"Backward compatibility check error: {e}")
            return False
