"""
Domain Entity: Issue

Represents a code quality or security issue.

Author: Asif Hussain
Created: 2025-11-30
CORTEX Version: 3.3.0
"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


class IssueType(Enum):
    """Types of code issues"""
    CODE_SMELL = "code_smell"
    BUG = "bug"
    VULNERABILITY = "vulnerability"
    SECURITY_HOTSPOT = "security_hotspot"
    DUPLICATION = "duplication"
    COMPLEXITY = "complexity"
    STYLE = "style"


class IssueSeverity(Enum):
    """Issue severity levels"""
    BLOCKER = "blocker"      # Must fix immediately
    CRITICAL = "critical"    # Fix ASAP
    MAJOR = "major"          # Fix soon
    MINOR = "minor"          # Fix when possible
    INFO = "info"            # Optional improvement


@dataclass
class Issue:
    """
    Domain entity representing a code quality or security issue.
    
    Pure business object with no external dependencies.
    """
    
    # Identity
    id: str
    type: IssueType
    severity: IssueSeverity
    
    # Description
    title: str
    message: str
    
    # Location
    component_path: str
    file_path: str
    line_number: int = 0
    column_number: int = 0
    
    rule_id: Optional[str] = None
    rule_category: Optional[str] = None
    owasp_category: Optional[str] = None  # e.g., "A03:2021 Injection"
    cwe_id: Optional[str] = None          # Common Weakness Enumeration
    
    # Remediation
    effort_minutes: int = 0
    fix_suggestion: Optional[str] = None
    
    # Metadata
    detected_by: Optional[str] = None  # Tool name (e.g., "pylint", "bandit")
    detected_at: Optional[str] = None
    
    # Context
    code_snippet: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate issue data"""
        if self.line_number < 0:
            raise ValueError(f"line_number must be >= 0, got {self.line_number}")
        
        if self.column_number < 0:
            raise ValueError(f"column_number must be >= 0, got {self.column_number}")
        
        if self.effort_minutes < 0:
            raise ValueError(f"effort_minutes must be >= 0, got {self.effort_minutes}")
    
    @property
    def severity_rank(self) -> int:
        """Numeric rank for sorting (1=highest priority)"""
        ranks = {
            IssueSeverity.BLOCKER: 1,
            IssueSeverity.CRITICAL: 2,
            IssueSeverity.MAJOR: 3,
            IssueSeverity.MINOR: 4,
            IssueSeverity.INFO: 5
        }
        return ranks[self.severity]
    
    @property
    def severity_color(self) -> str:
        """Color code for severity visualization"""
        colors = {
            IssueSeverity.BLOCKER: "#8b0000",    # Dark red
            IssueSeverity.CRITICAL: "#dc3545",   # Red
            IssueSeverity.MAJOR: "#ffc107",      # Yellow
            IssueSeverity.MINOR: "#17a2b8",      # Blue
            IssueSeverity.INFO: "#6c757d"        # Gray
        }
        return colors[self.severity]
    
    @property
    def is_security_issue(self) -> bool:
        """Check if this is a security-related issue"""
        return self.type in [IssueType.VULNERABILITY, IssueType.SECURITY_HOTSPOT]
    
    @property
    def is_high_priority(self) -> bool:
        """Check if issue is high priority (blocker or critical)"""
        return self.severity in [IssueSeverity.BLOCKER, IssueSeverity.CRITICAL]
    
    @property
    def effort_hours(self) -> float:
        """Effort in hours"""
        return self.effort_minutes / 60.0
    
    def add_tag(self, tag: str):
        """Add a tag to this issue"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'type': self.type.value,
            'severity': self.severity.value,
            'severity_rank': self.severity_rank,
            'severity_color': self.severity_color,
            'title': self.title,
            'message': self.message,
            'component_path': self.component_path,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'column_number': self.column_number,
            'rule_id': self.rule_id,
            'rule_category': self.rule_category,
            'owasp_category': self.owasp_category,
            'cwe_id': self.cwe_id,
            'effort_minutes': self.effort_minutes,
            'effort_hours': self.effort_hours,
            'fix_suggestion': self.fix_suggestion,
            'detected_by': self.detected_by,
            'detected_at': self.detected_at,
            'code_snippet': self.code_snippet,
            'tags': self.tags,
            'is_security_issue': self.is_security_issue,
            'is_high_priority': self.is_high_priority
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Issue':
        """Create Issue from dictionary"""
        # Convert type/severity strings to enums
        if isinstance(data.get('type'), str):
            data['type'] = IssueType(data['type'])
        if isinstance(data.get('severity'), str):
            data['severity'] = IssueSeverity(data['severity'])
        
        # Remove computed properties
        filtered_data = {
            k: v for k, v in data.items()
            if k not in ['severity_rank', 'severity_color', 'is_security_issue', 'is_high_priority', 'effort_hours']
        }
        
        return cls(**filtered_data)
