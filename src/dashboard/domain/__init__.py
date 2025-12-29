"""
Dashboard Domain Layer

Pure business entities with no external dependencies.
Following Domain-Driven Design principles.

Author: Asif Hussain
Created: 2025-11-30
CORTEX Version: 3.3.0
"""

from src.dashboard.domain.component import Component, ComponentType
from src.dashboard.domain.dependency import Dependency, DependencyType, DependencyStrength
from src.dashboard.domain.health_score import HealthScore, LayerScore
from src.dashboard.domain.issue import Issue, IssueType, IssueSeverity
from src.dashboard.domain.recommendation import Recommendation, RecommendationCategory, RecommendationPriority

__all__ = [
    # Component
    'Component',
    'ComponentType',
    
    # Dependency
    'Dependency',
    'DependencyType',
    'DependencyStrength',
    
    # Health Score
    'HealthScore',
    'LayerScore',
    
    # Issue
    'Issue',
    'IssueType',
    'IssueSeverity',
    
    # Recommendation
    'Recommendation',
    'RecommendationCategory',
    'RecommendationPriority',
]
