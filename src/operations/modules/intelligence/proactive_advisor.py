"""
Proactive Advisor - Continuous enhancement recommendations.

Provides actionable recommendations without user prompting based on
code quality analysis, architecture patterns, and historical learnings.

Copyright © 2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProactiveRecommendation:
    """Proactive enhancement recommendation."""
    category: str  # "code_quality", "architecture", "performance", "security"
    priority: str  # "high", "medium", "low"
    title: str
    description: str
    suggested_action: str
    estimated_effort: str  # "5 minutes", "1 hour", etc.
    impact: str  # "High", "Medium", "Low"


class ProactiveAdvisor:
    """Generate proactive enhancement recommendations."""
    
    def __init__(self, ast_engine, analyzers: Dict[str, Any]):
        """
        Initialize proactive advisor.
        
        Args:
            ast_engine: AST engine for code analysis
            analyzers: Dict of analyzer instances (deduplication, architecture, code_smell)
        """
        self.ast_engine = ast_engine
        self.analyzers = analyzers
        
        # Recommendation triggers
        self.triggers = {
            'duplicate_code': self._trigger_duplicate_refactor,
            'architecture_violation': self._trigger_architecture_fix,
            'code_smell': self._trigger_code_cleanup,
            'test_gap': self._trigger_test_addition,
            'security_issue': self._trigger_security_fix,
            'performance_bottleneck': self._trigger_optimization
        }
        
    def generate_recommendations(
        self,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ProactiveRecommendation]:
        """
        Generate proactive recommendations based on current codebase state.
        
        Args:
            context: Optional context (current operation, affected files, etc.)
            
        Returns:
            List of prioritized recommendations
        """
        logger.info("Generating proactive recommendations")
        
        recommendations = []
        
        # Analyze code quality
        if 'deduplication' in self.analyzers:
            try:
                dedup_analysis = self.analyzers['deduplication'].analyze()
                if dedup_analysis.get('total_duplicates', 0) > 0:
                    recommendations.extend(self._trigger_duplicate_refactor(dedup_analysis))
            except Exception as e:
                logger.warning(f"Deduplication analysis failed: {e}")
            
        # Analyze architecture
        if 'architecture' in self.analyzers:
            try:
                arch_analysis = self.analyzers['architecture'].analyze()
                if arch_analysis.get('high_severity_count', 0) > 0:
                    recommendations.extend(self._trigger_architecture_fix(arch_analysis))
            except Exception as e:
                logger.warning(f"Architecture analysis failed: {e}")
            
        # Analyze code smells
        if 'code_smell' in self.analyzers:
            try:
                smell_analysis = self.analyzers['code_smell'].analyze(Path.cwd())
                if smell_analysis.get('total_smells', 0) > 0:
                    recommendations.extend(self._trigger_code_cleanup(smell_analysis))
            except Exception as e:
                logger.warning(f"Code smell analysis failed: {e}")
            
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda r: priority_order[r.priority])
        
        return recommendations[:10]  # Top 10 recommendations
        
    def _trigger_duplicate_refactor(self, analysis: Dict[str, Any]) -> List[ProactiveRecommendation]:
        """Generate recommendations for duplicate code."""
        recommendations = []
        
        duplicate_groups = analysis.get('duplicate_groups', [])
        
        for group in duplicate_groups[:3]:  # Top 3 duplicates
            recommendations.append(ProactiveRecommendation(
                category="code_quality",
                priority="high" if group.similarity_score > 0.95 else "medium",
                title=f"Refactor {len(group.locations)} duplicate code blocks",
                description=(
                    f"Found {len(group.locations)} instances of similar code "
                    f"({group.similarity_score:.0%} similarity, {group.lines_count} lines)"
                ),
                suggested_action=(
                    "Extract shared logic into utility function or module. "
                    f"{group.recommendation}"
                ),
                estimated_effort=f"{max(5, int(group.lines_count / 10))} minutes",
                impact="Medium - Reduces maintenance burden"
            ))
            
        return recommendations
        
    def _trigger_architecture_fix(self, analysis: Dict[str, Any]) -> List[ProactiveRecommendation]:
        """Generate recommendations for architecture violations."""
        recommendations = []
        
        violations = [v for v in analysis.get('violations', []) if v.severity == 'high']
        
        for violation in violations[:2]:  # Top 2 violations
            recommendations.append(ProactiveRecommendation(
                category="architecture",
                priority="high",
                title=f"Fix {violation.violation_type.replace('_', ' ')}",
                description=violation.description,
                suggested_action=violation.recommendation,
                estimated_effort="1-2 hours",
                impact="High - Improves modularity and maintainability"
            ))
            
        return recommendations
        
    def _trigger_code_cleanup(self, analysis: Dict[str, Any]) -> List[ProactiveRecommendation]:
        """Generate recommendations for code smells."""
        recommendations = []
        
        # Get high severity smells from priority fixes
        priority_fixes = analysis.get('priority_fixes', [])
        
        for fix_desc in priority_fixes[:2]:  # Top 2 priority fixes
            # Parse priority fix description
            # Format: "path:line - description: recommendation"
            parts = fix_desc.split(' - ', 1)
            if len(parts) == 2:
                location = parts[0]
                description = parts[1]
                
                recommendations.append(ProactiveRecommendation(
                    category="code_quality",
                    priority="medium",
                    title=f"Address code quality issue in {Path(location.split(':')[0]).name}",
                    description=description,
                    suggested_action="Review and apply suggested refactoring",
                    estimated_effort="30 minutes",
                    impact="Medium - Improves code readability"
                ))
            
        return recommendations
        
    def _trigger_test_addition(self, context: Dict[str, Any]) -> List[ProactiveRecommendation]:
        """Generate recommendations for test gaps."""
        # Placeholder - actual implementation would analyze test coverage
        return []
        
    def _trigger_security_fix(self, context: Dict[str, Any]) -> List[ProactiveRecommendation]:
        """Generate recommendations for security issues."""
        # Placeholder - actual implementation would use security analyzer
        return []
        
    def _trigger_optimization(self, context: Dict[str, Any]) -> List[ProactiveRecommendation]:
        """Generate recommendations for performance bottlenecks."""
        # Placeholder - actual implementation would use performance profiler
        return []
        
    def format_recommendations(self, recommendations: List[ProactiveRecommendation]) -> str:
        """
        Format recommendations as markdown report.
        
        Args:
            recommendations: List of recommendations
            
        Returns:
            Formatted markdown string
        """
        if not recommendations:
            return "✅ No immediate recommendations - code quality is good!"
            
        output = []
        output.append("## 💡 Proactive Recommendations\n")
        
        # Group by priority
        by_priority = {}
        for rec in recommendations:
            by_priority.setdefault(rec.priority, []).append(rec)
            
        for priority in ['high', 'medium', 'low']:
            if priority not in by_priority:
                continue
                
            priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}[priority]
            output.append(f"### {priority_icon} {priority.upper()} Priority\n")
            
            for rec in by_priority[priority]:
                output.append(f"**{rec.title}**")
                output.append(f"- Category: {rec.category}")
                output.append(f"- {rec.description}")
                output.append(f"- 💪 Action: {rec.suggested_action}")
                output.append(f"- ⏱️ Effort: {rec.estimated_effort}")
                output.append(f"- 📊 Impact: {rec.impact}\n")
                
        return '\n'.join(output)
