"""
Validation Framework for CORTEX Clean Architecture

Provides FluentValidation-style validators for command and query validation.
Supports chainable validation rules, custom validators, and async validation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

from .validation_result import ValidationResult, ValidationError
from .validator import Validator
from .validation_rule import ValidationRule
from .validator_extensions import RuleBuilder
from .common_validators import (
    NotEmptyValidator,
    MinLengthValidator,
    MaxLengthValidator,
    RegexValidator,
    RangeValidator,
    EmailValidator,
    UrlValidator,
    PredicateValidator,
)
from .validator_registry import ValidatorRegistry, get_validator_registry
from .conversation_validators import (
    CaptureConversationValidator,
    LearnPatternValidator,
    UpdateContextRelevanceValidator,
    UpdatePatternConfidenceValidator,
)
from .conversation_query_validators import (
    SearchContextQueryValidator,
    GetConversationQualityQueryValidator,
    FindSimilarPatternsQueryValidator,
)

__all__ = [
    # Core validation framework
    "ValidationResult",
    "ValidationError",
    "Validator",
    "ValidationRule",
    "RuleBuilder",
    # Built-in validators
    "NotEmptyValidator",
    "MinLengthValidator",
    "MaxLengthValidator",
    "RegexValidator",
    "RangeValidator",
    "EmailValidator",
    "UrlValidator",
    "PredicateValidator",
    # Validator registry
    "ValidatorRegistry",
    "get_validator_registry",
    # Command validators
    "CaptureConversationValidator",
    "LearnPatternValidator",
    "UpdateContextRelevanceValidator",
    "UpdatePatternConfidenceValidator",
    # Query validators
    "SearchContextQueryValidator",
    "GetConversationQualityQueryValidator",
    "FindSimilarPatternsQueryValidator",
]
