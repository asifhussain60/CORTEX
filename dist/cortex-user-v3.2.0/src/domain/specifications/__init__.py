"""
Specification Pattern for CORTEX Domain.

Provides composable business rules and query specifications.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

from .specification import ISpecification, Specification
from .composite_specification import AndSpecification, OrSpecification, NotSpecification
from .expression_specification import ExpressionSpecification
from .common_specifications import (
    HighQualityConversationSpec,
    RecentConversationSpec,
    NamespaceMatchSpec,
    PatternConfidenceSpec,
    MinimumParticipantsSpec,
    EntityCountSpec,
    ContextRelevanceSpec,
    TierSpec,
)

__all__ = [
    "ISpecification",
    "Specification",
    "AndSpecification",
    "OrSpecification",
    "NotSpecification",
    "ExpressionSpecification",
    "HighQualityConversationSpec",
    "RecentConversationSpec",
    "NamespaceMatchSpec",
    "PatternConfidenceSpec",
    "MinimumParticipantsSpec",
    "EntityCountSpec",
    "ContextRelevanceSpec",
    "TierSpec",
]
