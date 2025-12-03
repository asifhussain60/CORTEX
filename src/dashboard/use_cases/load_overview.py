"""
Use Case: Load Overview Tab Data

Business logic for loading and formatting overview tab data.

Author: Asif Hussain
Created: 2025-11-30
CORTEX Version: 3.3.0
"""

from typing import Dict, Any
from datetime import datetime
import logging

from src.dashboard.data.repository_interface import (
    IComponentRepository,
    IIssueRepository,
    IHealthScoreRepository
)
from src.dashboard.domain import IssueSeverity

logger = logging.getLogger(__name__)


class LoadOverviewUseCase:
    """
    Use case for loading overview tab data.
    
    Follows Single Responsibility Principle - only handles overview logic.
    Follows Dependency Inversion - depends on interfaces, not concrete implementations.
    """
    
    def __init__(
        self,
        component_repo: IComponentRepository,
        issue_repo: IIssueRepository,
        health_repo: IHealthScoreRepository
    ):
        """
        Initialize use case with repository dependencies.
        
        Args:
            component_repo: Component data access
            issue_repo: Issue data access
            health_repo: Health score data access
        """
        self.component_repo = component_repo
        self.issue_repo = issue_repo
        self.health_repo = health_repo
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute use case to load overview data.
        
        Returns:
            Dict containing overview data for rendering
        """
        logger.info("Loading overview tab data")
        
        try:
            components = self.component_repo.get_all()
            all_issues = self.issue_repo.get_all()
            system_health = self.health_repo.get_system_health()
            
            total_components = len(components)
            total_loc = sum(c.lines_of_code for c in components)
            avg_complexity = (
                sum(c.complexity for c in components) / total_components
                if total_components > 0 else 0
            )
            avg_test_coverage = (
                sum(c.test_coverage for c in components) / total_components
                if total_components > 0 else 0
            )
            
            # Health distribution
            healthy_count = len([c for c in components if c.health_category == 'healthy'])
            warning_count = len([c for c in components if c.health_category == 'warning'])
            critical_count = len([c for c in components if c.health_category == 'critical'])
            
            # Issue breakdown
            blocker_issues = len([i for i in all_issues if i.severity == IssueSeverity.BLOCKER])
            critical_issues = len([i for i in all_issues if i.severity == IssueSeverity.CRITICAL])
            major_issues = len([i for i in all_issues if i.severity == IssueSeverity.MAJOR])
            minor_issues = len([i for i in all_issues if i.severity == IssueSeverity.MINOR])
            security_issues = len([i for i in all_issues if i.is_security_issue])
            
            # Language breakdown
            language_counts = {}
            for component in components:
                if component.language:
                    language_counts[component.language] = language_counts.get(component.language, 0) + 1
            
            # Build response
            overview_data = {
                'generated_at': datetime.now().isoformat(),
                'system_health': system_health.to_dict(),
                'statistics': {
                    'total_components': total_components,
                    'total_lines_of_code': total_loc,
                    'average_complexity': round(avg_complexity, 2),
                    'average_test_coverage': round(avg_test_coverage, 2),
                },
                'health_distribution': {
                    'healthy': healthy_count,
                    'warning': warning_count,
                    'critical': critical_count
                },
                'issue_breakdown': {
                    'blocker': blocker_issues,
                    'critical': critical_issues,
                    'major': major_issues,
                    'minor': minor_issues,
                    'total': len(all_issues),
                    'security': security_issues
                },
                'language_breakdown': language_counts,
                'top_issues': [
                    i.to_dict() for i in sorted(
                        all_issues,
                        key=lambda x: x.severity_rank
                    )[:10]
                ]
            }
            
            logger.info(f"Overview data loaded: {total_components} components, {len(all_issues)} issues")
            return overview_data
            
        except Exception as e:
            logger.error(f"Error loading overview data: {e}")
            raise
