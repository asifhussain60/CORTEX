"""
Domain Entity: Recommendation

Represents an actionable recommendation for code improvement.

Author: Asif Hussain
Created: 2025-11-30
CORTEX Version: 3.3.0
"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


class RecommendationCategory(Enum):
    """Categories of recommendations"""
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    CODE_QUALITY = "code_quality"


class RecommendationPriority(Enum):
    """Recommendation priority levels"""
    CRITICAL = "critical"  # Must do immediately
    HIGH = "high"          # Do in current sprint
    MEDIUM = "medium"      # Do in next sprint
    LOW = "low"            # Do when possible


@dataclass
class Recommendation:
    """
    Domain entity representing an actionable recommendation.
    
    Pure business object with no external dependencies.
    """
    
    # Identity
    id: str
    category: RecommendationCategory
    priority: RecommendationPriority
    
    # Description
    title: str
    description: str
    rationale: str  # Why is this important?
    
    # Action
    action_items: List[str] = field(default_factory=list)
    expected_outcome: Optional[str] = None
    
    # Metrics
    effort_hours: float = 0.0
    impact_score: float = 0.0  # 0-10 (how much this improves quality)
    
    # Context
    affected_components: List[str] = field(default_factory=list)
    related_issues: List[str] = field(default_factory=list)  # Issue IDs
    
    # Resources
    documentation_links: List[str] = field(default_factory=list)
    code_examples: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: Optional[str] = None
    status: str = "open"  # open, in_progress, completed, dismissed
    
    def __post_init__(self):
        """Validate recommendation data"""
        if self.effort_hours < 0:
            raise ValueError(f"effort_hours must be >= 0, got {self.effort_hours}")
        
        if not 0 <= self.impact_score <= 10:
            raise ValueError(f"impact_score must be 0-10, got {self.impact_score}")
    
    @property
    def priority_rank(self) -> int:
        """Numeric rank for sorting (1=highest priority)"""
        ranks = {
            RecommendationPriority.CRITICAL: 1,
            RecommendationPriority.HIGH: 2,
            RecommendationPriority.MEDIUM: 3,
            RecommendationPriority.LOW: 4
        }
        return ranks[self.priority]
    
    @property
    def priority_color(self) -> str:
        """Color code for priority visualization"""
        colors = {
            RecommendationPriority.CRITICAL: "#dc3545",  # Red
            RecommendationPriority.HIGH: "#ffc107",      # Yellow
            RecommendationPriority.MEDIUM: "#17a2b8",    # Blue
            RecommendationPriority.LOW: "#6c757d"        # Gray
        }
        return colors[self.priority]
    
    @property
    def roi_score(self) -> float:
        """Return on Investment: impact per hour of effort"""
        if self.effort_hours == 0:
            return 0.0
        return round(self.impact_score / self.effort_hours, 2)
    
    @property
    def is_high_priority(self) -> bool:
        """Check if recommendation is critical or high priority"""
        return self.priority in [RecommendationPriority.CRITICAL, RecommendationPriority.HIGH]
    
    @property
    def is_quick_win(self) -> bool:
        """Check if this is a quick win (high impact, low effort)"""
        return self.impact_score >= 7 and self.effort_hours <= 2
    
    def add_action_item(self, action: str):
        """Add an action item to the recommendation"""
        if action not in self.action_items:
            self.action_items.append(action)
    
    def add_affected_component(self, component_path: str):
        """Add an affected component"""
        if component_path not in self.affected_components:
            self.affected_components.append(component_path)
    
    def mark_completed(self):
        """Mark recommendation as completed"""
        self.status = "completed"
    
    def mark_in_progress(self):
        """Mark recommendation as in progress"""
        self.status = "in_progress"
    
    def dismiss(self):
        """Dismiss this recommendation"""
        self.status = "dismissed"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'category': self.category.value,
            'priority': self.priority.value,
            'priority_rank': self.priority_rank,
            'priority_color': self.priority_color,
            'title': self.title,
            'description': self.description,
            'rationale': self.rationale,
            'action_items': self.action_items,
            'expected_outcome': self.expected_outcome,
            'effort_hours': self.effort_hours,
            'impact_score': self.impact_score,
            'roi_score': self.roi_score,
            'affected_components': self.affected_components,
            'related_issues': self.related_issues,
            'documentation_links': self.documentation_links,
            'code_examples': self.code_examples,
            'created_at': self.created_at,
            'status': self.status,
            'is_high_priority': self.is_high_priority,
            'is_quick_win': self.is_quick_win
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Recommendation':
        """Create Recommendation from dictionary"""
        # Convert category/priority strings to enums
        if isinstance(data.get('category'), str):
            data['category'] = RecommendationCategory(data['category'])
        if isinstance(data.get('priority'), str):
            data['priority'] = RecommendationPriority(data['priority'])
        
        # Remove computed properties
        filtered_data = {
            k: v for k, v in data.items()
            if k not in ['priority_rank', 'priority_color', 'roi_score', 'is_high_priority', 'is_quick_win']
        }
        
        return cls(**filtered_data)
