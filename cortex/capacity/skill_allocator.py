"""Capacity Planning - Skill Allocator for CAP-006-008.

Phase 17 Track C implementation.
"""

from typing import List
from dataclasses import dataclass, field

# Import from multi_model_estimation_engine
from cortex.capacity.multi_model_estimation_engine import SkillLevel


@dataclass
class TaskClassification:
    """Task classification result."""
    task_description: str
    required_skill: SkillLevel
    complexity_score: int
    reasoning: str = ""


@dataclass
class TeamComposition:
    """Team composition recommendation."""
    senior_count: int = 0
    mid_count: int = 0
    junior_count: int = 0
    total_engineers: int = 0
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class SkillAllocator:
    """CAP-006-008: Task Classifier & Team Optimizer with Brooks' Law."""
    
    SENIOR_KEYWORDS = [
        "architecture", "security", "auth", "design", "refactor",
        "algorithm", "performance", "scalability", "oauth", "jwt"
    ]
    
    MID_KEYWORDS = [
        "api", "endpoint", "integration", "service", "database",
        "rest", "graphql", "crud"
    ]
    
    JUNIOR_KEYWORDS = [
        "test", "unit test", "documentation", "docs", "readme",
        "comment", "typo", "formatting"
    ]
    
    def classify_task(self, task_description: str, complexity_score: int) -> TaskClassification:
        """CAP-006: Classify task by skill level."""
        desc_lower = task_description.lower()
        
        if any(k in desc_lower for k in self.SENIOR_KEYWORDS):
            return TaskClassification(task_description, SkillLevel.SENIOR, complexity_score, "Senior domain")
        
        if any(k in desc_lower for k in self.JUNIOR_KEYWORDS):
            return TaskClassification(task_description, SkillLevel.JUNIOR, complexity_score, "Junior domain")
        
        if any(k in desc_lower for k in self.MID_KEYWORDS):
            return TaskClassification(task_description, SkillLevel.MIDLEVEL, complexity_score, "Mid domain")
        
        if complexity_score >= 70:
            return TaskClassification(task_description, SkillLevel.SENIOR, complexity_score, "High complexity")
        elif complexity_score >= 40:
            return TaskClassification(task_description, SkillLevel.MIDLEVEL, complexity_score, "Medium complexity")
        else:
            return TaskClassification(task_description, SkillLevel.JUNIOR, complexity_score, "Low complexity")
    
    def optimize_team(self, total_hours: float, senior_hours: float, 
                     mid_hours: float, junior_hours: float, hours_per_week: float = 40.0) -> TeamComposition:
        """CAP-007: Optimize team composition."""
        import math
        
        effective_hours = hours_per_week * 0.7 * 4  # 4-week baseline
        
        senior_count = max(1, math.ceil(senior_hours / effective_hours))
        mid_count = math.ceil(mid_hours / effective_hours)
        junior_count = math.ceil(junior_hours / effective_hours)
        
        total_engineers = senior_count + mid_count + junior_count
        
        warnings = []
        recommendations = []
        
        if total_engineers > 15:
            channels = self.calculate_communication_channels(total_engineers)
            warnings.append(f"Brooks' Law Warning: {total_engineers} engineers = {channels} channels")
            warnings.append("Consider splitting into independent workstreams")
            recommendations.append(f"Split into 2-3 teams of ~{total_engineers//2} engineers")
        
        if total_hours < 50:
            recommendations.append("Small project: 1-2 engineers optimal")
        
        return TeamComposition(senior_count, mid_count, junior_count, total_engineers, warnings, recommendations)
    
    @staticmethod
    def calculate_communication_channels(num_engineers: int) -> int:
        """CAP-008: Calculate communication channels."""
        return num_engineers * (num_engineers - 1) // 2
