"""
Use Case: Generate Recommendations

Business logic for generating actionable recommendations.

Author: Asif Hussain
Created: 2025-11-30
CORTEX Version: 3.3.0
"""

from typing import Dict, Any, List
import logging
from datetime import datetime

from src.dashboard.data.repository_interface import (
    IComponentRepository,
    IIssueRepository,
    IDependencyRepository
)
from src.dashboard.domain import (
    Recommendation,
    RecommendationCategory,
    RecommendationPriority,
    IssueSeverity
)

logger = logging.getLogger(__name__)


class GenerateRecommendationsUseCase:
    """
    Use case for generating actionable recommendations.
    
    Analyzes components, issues, and dependencies to produce prioritized recommendations.
    """
    
    def __init__(
        self,
        component_repo: IComponentRepository,
        issue_repo: IIssueRepository,
        dependency_repo: IDependencyRepository
    ):
        """
        Initialize use case with repository dependencies.
        
        Args:
            component_repo: Component data access
            issue_repo: Issue data access
            dependency_repo: Dependency data access
        """
        self.component_repo = component_repo
        self.issue_repo = issue_repo
        self.dependency_repo = dependency_repo
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute use case to generate recommendations.
        
        Returns:
            Dict containing recommendations grouped by category and priority
        """
        logger.info("Generating recommendations")
        
        try:
            components = self.component_repo.get_all()
            issues = self.issue_repo.get_all()
            dependencies = self.dependency_repo.get_all()
            
            recommendations = []
            
            # Generate recommendations from different analyzers
            recommendations.extend(self._recommend_from_security_issues(issues))
            recommendations.extend(self._recommend_from_test_coverage(components))
            recommendations.extend(self._recommend_from_complexity(components))
            recommendations.extend(self._recommend_from_dependencies(dependencies))
            recommendations.extend(self._recommend_from_health_scores(components))
            
            # Sort by ROI (Return on Investment)
            recommendations.sort(key=lambda r: r.roi_score, reverse=True)
            
            # Group recommendations
            grouped_recommendations = {
                'by_category': self._group_by_category(recommendations),
                'by_priority': self._group_by_priority(recommendations),
                'quick_wins': [r.to_dict() for r in recommendations if r.is_quick_win],
                'high_impact': [r.to_dict() for r in recommendations if r.impact_score >= 8],
                'all': [r.to_dict() for r in recommendations]
            }
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            return grouped_recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            raise
    
    def _recommend_from_security_issues(self, issues: List) -> List[Recommendation]:
        """Generate recommendations from security vulnerabilities"""
        recommendations = []
        
        security_issues = [i for i in issues if i.is_security_issue]
        critical_security = [i for i in security_issues if i.is_high_priority]
        
        if critical_security:
            rec = Recommendation(
                id=f"sec-critical-{datetime.now().timestamp()}",
                category=RecommendationCategory.SECURITY,
                priority=RecommendationPriority.CRITICAL,
                title=f"Fix {len(critical_security)} Critical Security Vulnerabilities",
                description=f"There are {len(critical_security)} critical/blocker security issues that pose immediate risk.",
                rationale="Security vulnerabilities can lead to data breaches, unauthorized access, and system compromise.",
                action_items=[
                    "Review all critical security issues in Security tab",
                    "Prioritize OWASP Top 10 vulnerabilities",
                    "Apply patches or code fixes",
                    "Run security scan again to verify fixes"
                ],
                expected_outcome="Elimination of critical security risks",
                effort_hours=sum(i.effort_hours for i in critical_security),
                impact_score=10.0,
                affected_components=[i.component_path for i in critical_security[:5]],
                related_issues=[i.id for i in critical_security],
                created_at=datetime.now().isoformat()
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _recommend_from_test_coverage(self, components: List) -> List[Recommendation]:
        """Generate recommendations from test coverage analysis"""
        recommendations = []
        
        untested = [c for c in components if c.test_coverage < 10]
        low_coverage = [c for c in components if 10 <= c.test_coverage < 50]
        
        if untested:
            rec = Recommendation(
                id=f"test-untested-{datetime.now().timestamp()}",
                category=RecommendationCategory.TESTING,
                priority=RecommendationPriority.HIGH,
                title=f"Add Tests to {len(untested)} Untested Components",
                description=f"{len(untested)} components have less than 10% test coverage.",
                rationale="Untested code is prone to bugs and makes refactoring risky.",
                action_items=[
                    "Start with critical business logic components",
                    "Write unit tests for public APIs",
                    "Aim for at least 60% coverage initially",
                    "Set up CI/CD to enforce minimum coverage"
                ],
                expected_outcome="Reduced bug rate and safer refactoring",
                effort_hours=len(untested) * 2.0,  # 2 hours per component
                impact_score=8.0,
                affected_components=[c.path for c in untested[:10]],
                created_at=datetime.now().isoformat()
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _recommend_from_complexity(self, components: List) -> List[Recommendation]:
        """Generate recommendations from complexity analysis"""
        recommendations = []
        
        high_complexity = [c for c in components if c.complexity > 20]
        
        if high_complexity:
            rec = Recommendation(
                id=f"complexity-refactor-{datetime.now().timestamp()}",
                category=RecommendationCategory.MAINTAINABILITY,
                priority=RecommendationPriority.MEDIUM,
                title=f"Refactor {len(high_complexity)} High-Complexity Components",
                description=f"{len(high_complexity)} components have cyclomatic complexity > 20.",
                rationale="High complexity makes code harder to understand, test, and maintain.",
                action_items=[
                    "Extract methods to reduce complexity",
                    "Apply Single Responsibility Principle",
                    "Consider design patterns (Strategy, State, etc.)",
                    "Add explanatory comments for complex logic"
                ],
                expected_outcome="Improved code readability and maintainability",
                effort_hours=len(high_complexity) * 1.5,
                impact_score=7.0,
                affected_components=[c.path for c in high_complexity[:10]],
                created_at=datetime.now().isoformat()
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _recommend_from_dependencies(self, dependencies: List) -> List[Recommendation]:
        """Generate recommendations from dependency analysis"""
        recommendations = []
        
        circular_deps = [d for d in dependencies if d.is_circular]
        
        if circular_deps:
            rec = Recommendation(
                id=f"arch-circular-{datetime.now().timestamp()}",
                category=RecommendationCategory.ARCHITECTURE,
                priority=RecommendationPriority.HIGH,
                title=f"Break {len(circular_deps)} Circular Dependencies",
                description="Circular dependencies indicate architectural issues and hinder modularity.",
                rationale="Circular dependencies create tight coupling, make testing difficult, and prevent independent deployment.",
                action_items=[
                    "Identify dependency cycles in Architecture tab",
                    "Apply Dependency Inversion Principle",
                    "Introduce interfaces to break cycles",
                    "Consider extracting shared logic to separate module"
                ],
                expected_outcome="Cleaner architecture with better modularity",
                effort_hours=len(circular_deps) * 1.0,
                impact_score=8.5,
                affected_components=list(set([d.source for d in circular_deps[:10]])),
                created_at=datetime.now().isoformat()
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _recommend_from_health_scores(self, components: List) -> List[Recommendation]:
        """Generate recommendations from health score analysis"""
        recommendations = []
        
        critical_health = [c for c in components if c.health_category == 'critical']
        
        if critical_health:
            rec = Recommendation(
                id=f"health-critical-{datetime.now().timestamp()}",
                category=RecommendationCategory.CODE_QUALITY,
                priority=RecommendationPriority.HIGH,
                title=f"Improve {len(critical_health)} Critical Health Components",
                description=f"{len(critical_health)} components have health scores below 70.",
                rationale="Low health scores indicate multiple quality issues that compound over time.",
                action_items=[
                    "Review 7-layer health breakdown for each component",
                    "Address failing layers (tests, documentation, etc.)",
                    "Prioritize components with most dependents",
                    "Set health score targets and track progress"
                ],
                expected_outcome="Improved overall system health",
                effort_hours=len(critical_health) * 3.0,
                impact_score=9.0,
                affected_components=[c.path for c in critical_health[:10]],
                created_at=datetime.now().isoformat()
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _group_by_category(self, recommendations: List[Recommendation]) -> Dict[str, List]:
        """Group recommendations by category"""
        grouped = {}
        for rec in recommendations:
            category = rec.category.value
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(rec.to_dict())
        return grouped
    
    def _group_by_priority(self, recommendations: List[Recommendation]) -> Dict[str, List]:
        """Group recommendations by priority"""
        grouped = {}
        for rec in recommendations:
            priority = rec.priority.value
            if priority not in grouped:
                grouped[priority] = []
            grouped[priority].append(rec.to_dict())
        return grouped
