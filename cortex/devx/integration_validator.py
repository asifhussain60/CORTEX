"""Integration Validator

Author: CORTEX Framework
"""

from dataclasses import dataclass

@dataclass
class ValidationIssue:
    """Validation issue."""
    issue_id: str
    severity: str
    message: str

__all__ = ["ValidationIssue"]
