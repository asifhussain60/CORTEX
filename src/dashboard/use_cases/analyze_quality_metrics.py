"""
Use Case: Analyze Quality Metrics

Business logic for quality metrics analysis and visualization.

Author: Asif Hussain
Created: 2025-11-30
CORTEX Version: 3.3.0
"""

from typing import Dict, Any, List
import logging

from src.dashboard.data.repository_interface import (
    IComponentRepository,
    IIssueRepository
)
from src.dashboard.domain import IssueType, IssueSeverity

logger = logging.getLogger(__name__)


class AnalyzeQualityMetricsUseCase:
    """
    Use case for analyzing quality metrics.
    
    Provides data for quality tab visualizations.
    """
    
    def __init__(
        self,
        component_repo: IComponentRepository,
        issue_repo: IIssueRepository
    ):
        """
        Initialize use case with repository dependencies.
        
        Args:
            component_repo: Component data access
            issue_repo: Issue data access
        """
        self.component_repo = component_repo
        self.issue_repo = issue_repo
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute use case to analyze quality metrics.
        
        Returns:
            Dict containing quality analysis data
        """
        logger.info("Analyzing quality metrics")
        
        try:
            components = self.component_repo.get_all()
            issues = self.issue_repo.get_all()
            
            # Complexity analysis
            complexity_distribution = self._analyze_complexity(components)
            
            # Test coverage analysis
            coverage_analysis = self._analyze_test_coverage(components)
            
            # Code smells analysis
            code_smells = [i for i in issues if i.type == IssueType.CODE_SMELL]
            code_smell_breakdown = self._breakdown_by_rule(code_smells)
            
            # Duplication analysis
            duplication_total = sum(c.duplicate_lines for c in components)
            duplication_by_component = [
                {'component': c.name, 'path': c.path, 'duplicate_lines': c.duplicate_lines}
                for c in sorted(components, key=lambda x: x.duplicate_lines, reverse=True)[:10]
            ]
            
            # Components needing attention
            components_needing_attention = self._identify_problem_components(components, issues)
            
            # Technical debt estimation
            technical_debt = self._estimate_technical_debt(issues)
            
            quality_data = {
                'complexity': complexity_distribution,
                'test_coverage': coverage_analysis,
                'code_smells': {
                    'total': len(code_smells),
                    'breakdown': code_smell_breakdown
                },
                'duplication': {
                    'total_lines': duplication_total,
                    'top_offenders': duplication_by_component
                },
                'problem_components': components_needing_attention,
                'technical_debt': technical_debt,
                'quality_score': self._calculate_overall_quality_score(components, issues)
            }
            
            logger.info(f"Quality metrics analyzed: {len(code_smells)} code smells, {duplication_total} duplicate lines")
            return quality_data
            
        except Exception as e:
            logger.error(f"Error analyzing quality metrics: {e}")
            raise
    
    def _analyze_complexity(self, components: List) -> Dict[str, Any]:
        """Analyze code complexity distribution"""
        complexities = [c.complexity for c in components if c.complexity > 0]
        
        if not complexities:
            return {'average': 0, 'max': 0, 'distribution': {}}
        
        avg_complexity = sum(complexities) / len(complexities)
        max_complexity = max(complexities)
        
        # Distribution buckets
        distribution = {
            'low': len([c for c in complexities if c < 10]),
            'medium': len([c for c in complexities if 10 <= c < 20]),
            'high': len([c for c in complexities if 20 <= c < 30]),
            'very_high': len([c for c in complexities if c >= 30])
        }
        
        return {
            'average': round(avg_complexity, 2),
            'max': max_complexity,
            'distribution': distribution
        }
    
    def _analyze_test_coverage(self, components: List) -> Dict[str, Any]:
        """Analyze test coverage statistics"""
        coverages = [c.test_coverage for c in components if c.test_coverage > 0]
        
        if not coverages:
            return {'average': 0, 'distribution': {}}
        
        avg_coverage = sum(coverages) / len(coverages)
        
        distribution = {
            'none': len([c for c in components if c.test_coverage == 0]),
            'low': len([c for c in coverages if 0 < c < 50]),
            'medium': len([c for c in coverages if 50 <= c < 80]),
            'good': len([c for c in coverages if c >= 80])
        }
        
        return {
            'average': round(avg_coverage, 2),
            'distribution': distribution,
            'untested_components': len([c for c in components if c.test_coverage == 0])
        }
    
    def _breakdown_by_rule(self, issues: List) -> Dict[str, int]:
        """Breakdown issues by rule category"""
        breakdown = {}
        for issue in issues:
            category = issue.rule_category or 'uncategorized'
            breakdown[category] = breakdown.get(category, 0) + 1
        
        # Sort by count
        return dict(sorted(breakdown.items(), key=lambda x: x[1], reverse=True))
    
    def _identify_problem_components(self, components: List, issues: List) -> List[Dict]:
        """Identify components with multiple quality issues"""
        problem_components = []
        
        for component in components:
            component_issues = [i for i in issues if i.component_path == component.path]
            
            if component_issues:
                problem_components.append({
                    'name': component.name,
                    'path': component.path,
                    'health_score': component.health_score,
                    'issue_count': len(component_issues),
                    'complexity': component.complexity,
                    'test_coverage': component.test_coverage,
                    'priority_score': self._calculate_priority_score(component, component_issues)
                })
        
        # Sort by priority score
        problem_components.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return problem_components[:20]  # Top 20
    
    def _calculate_priority_score(self, component, issues: List) -> float:
        """Calculate priority score for fixing (higher = more urgent)"""
        # Factors: issue count, severity, complexity, low coverage
        issue_weight = len(issues) * 2
        severity_weight = sum(5 - i.severity_rank for i in issues)
        complexity_penalty = component.complexity / 10
        coverage_penalty = (100 - component.test_coverage) / 10
        
        return issue_weight + severity_weight + complexity_penalty + coverage_penalty
    
    def _estimate_technical_debt(self, issues: List) -> Dict[str, Any]:
        """Estimate technical debt in hours"""
        total_effort = sum(i.effort_minutes for i in issues) / 60.0
        
        by_severity = {}
        for severity in IssueSeverity:
            severity_issues = [i for i in issues if i.severity == severity]
            by_severity[severity.value] = {
                'count': len(severity_issues),
                'hours': sum(i.effort_minutes for i in severity_issues) / 60.0
            }
        
        return {
            'total_hours': round(total_effort, 2),
            'total_days': round(total_effort / 8, 2),
            'by_severity': by_severity
        }
    
    def _calculate_overall_quality_score(self, components: List, issues: List) -> float:
        """Calculate overall quality score (0-100)"""
        if not components:
            return 0.0
        
        # Weighted factors
        avg_health = sum(c.health_score for c in components) / len(components)
        avg_coverage = sum(c.test_coverage for c in components) / len(components)
        
        # Issue penalty
        issues_per_component = len(issues) / len(components)
        issue_penalty = min(issues_per_component * 2, 20)  # Max 20 point penalty
        
        quality_score = (avg_health * 0.6) + (avg_coverage * 0.4) - issue_penalty
        
        return max(0, min(100, round(quality_score, 2)))
