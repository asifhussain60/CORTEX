"""
Data structures for UnifiedOnboardingOrchestrator.
====================================================

Shared data classes used by tests and implementation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any


class OnboardingType(Enum):
    """Types of onboarding workflows."""
    REPOSITORY = "repository"
    USER = "user"
    ENVIRONMENT = "environment"


class ValidationStatus(Enum):
    """Validation result status."""
    VALID = "valid"
    INVALID = "invalid"
    PARTIAL = "partial"
    ERROR = "error"


@dataclass
class RepositoryProfile:
    """Repository onboarding profile."""
    path: str
    name: str
    language: str
    project_type: str
    has_tests: bool
    test_coverage: float
    dependencies: List[str]
    is_valid: bool
    issues: List[str]


@dataclass
class UserProfile:
    """User onboarding profile."""
    user_id: str
    name: str
    role: str
    preferences: Dict[str, Any]
    is_complete: bool
    pending_steps: List[str]


@dataclass
class SetupResult:
    """Environment setup result."""
    success: bool
    environment_type: str
    config_applied: Dict[str, Any]
    errors: List[str]
    warnings: List[str]


@dataclass
class ValidationResult:
    """Validation result for onboarding profile."""
    status: ValidationStatus
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    recommendations: List[str]
