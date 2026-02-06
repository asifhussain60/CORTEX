"""
Shared types for Intelligence Orchestrators.

Contains dataclasses shared across multiple intelligence components
to avoid circular dependencies.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 34B Week 3 (Increment 6)
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class TechStack:
    """
    Technology stack representation.
    
    Captures language, frameworks, and version information
    for a codebase.
    """
    language: str
    frameworks: List[str] = field(default_factory=list)
    version: Optional[str] = None
    
    def __hash__(self):
        """Make TechStack hashable for caching."""
        return hash((
            self.language,
            tuple(sorted(self.frameworks)),
            self.version
        ))
    
    def __eq__(self, other):
        """Compare TechStack instances."""
        if not isinstance(other, TechStack):
            return False
        return (
            self.language == other.language and
            sorted(self.frameworks) == sorted(other.frameworks) and
            self.version == other.version
        )


@dataclass
class ReadinessScore:
    """
    Readiness score for a tech stack.
    
    4-factor weighted scoring:
    - Best practices coverage: 40%
    - TDD support: 30%
    - Security tooling: 20%
    - Cross-repo usage: 10%
    """
    overall: float  # 0.0 to 1.0
    best_practices: float  # 0.0 to 1.0
    tdd_support: float  # 0.0 to 1.0
    security: float  # 0.0 to 1.0
    usage: float  # 0.0 to 1.0
    action: str  # "ready", "needs_work", "learn_required"
    timestamp: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def calculate(
        cls,
        best_practices: float,
        tdd_support: float,
        security: float,
        usage: float,
    ) -> "ReadinessScore":
        """
        Calculate weighted readiness score.
        
        Weights:
        - Best practices: 40%
        - TDD support: 30%
        - Security: 20%
        - Usage: 10%
        """
        overall = (
            best_practices * 0.4 +
            tdd_support * 0.3 +
            security * 0.2 +
            usage * 0.1
        )
        
        # Determine action
        if overall >= 0.7:
            action = "ready"
        elif overall >= 0.4:
            action = "needs_work"
        else:
            action = "learn_required"
        
        return cls(
            overall=overall,
            best_practices=best_practices,
            tdd_support=tdd_support,
            security=security,
            usage=usage,
            action=action,
        )
