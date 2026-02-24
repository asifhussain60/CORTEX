"""
Coherence Models for Cross-Layer Validation.

Data models supporting cross-layer coherence validation:
- CoherenceReport: Overall validation report with issues
- ContractValidation: Individual contract validation result
- CoherenceIssue: Specific coherence issue found
- IntegrationValidation: Aggregate validation across contracts

Authority: CORTEX-SELF-IMPROVEMENT-SDLC.yaml Phase 0
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

# ============================================================================
# ENUMS
# ============================================================================

class IssueType(str, Enum):
    """Types of coherence issues that can be detected.

    Used to categorize cross-layer alignment problems.
    """
    ENUM_MISMATCH = "enum_mismatch"
    FIELD_NAME_MISMATCH = "field_name_mismatch"
    TYPE_INCOMPATIBILITY = "type_incompatibility"
    MISSING_MAPPING = "missing_mapping"


class CoherenceStatus(str, Enum):
    """Overall status of a coherence validation.

    PASS: All validations passed
    FAIL: Critical issues found
    WARNING: Non-critical issues found
    """
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


# ============================================================================
# CORE COHERENCE MODELS
# ============================================================================

@dataclass
class CoherenceIssue:
    """A specific coherence issue found during validation.

    Represents a mismatch between Python and JavaScript layers.

    Attributes:
        issue_type: Category of the issue
        python_value: Value on the Python side
        javascript_value: Value on the JavaScript side
        recommendation: How to fix the issue
        severity: Impact level (LOW, MEDIUM, HIGH, CRITICAL)
    """
    issue_type: IssueType
    python_value: str
    javascript_value: str
    recommendation: str
    severity: str


@dataclass
class ContractValidation:
    """Result of validating a single interface contract.

    Attributes:
        contract_id: Which contract was validated
        is_valid: Whether validation passed
        tests_run: Number of validation tests executed
        tests_passed: Number of tests that passed
        error_message: Description of failure if not valid
    """
    contract_id: str
    is_valid: bool
    tests_run: int
    tests_passed: int
    error_message: Optional[str] = None


@dataclass
class CoherenceReport:
    """Overall coherence validation report.

    Main output of validate_cross_layer_coherence().

    Attributes:
        status: Overall status (PASS, FAIL, WARNING)
        issues: List of coherence issues found
        contracts_validated: Number of contracts checked
        validation_timestamp: When validation was performed
    """
    status: CoherenceStatus
    issues: List[CoherenceIssue]
    contracts_validated: int
    validation_timestamp: datetime


@dataclass
class IntegrationValidation:
    """Aggregate validation result across all contracts.

    Used by cortex_validate_integration MCP tool.

    Attributes:
        overall_valid: Whether all validations passed
        contract_validations: Individual contract results
        total_tests: Total tests across all contracts
        total_passed: Total passed tests
    """
    overall_valid: bool
    contract_validations: List[ContractValidation]
    total_tests: int
    total_passed: int
