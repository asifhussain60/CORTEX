"""
Health Integration for CORTEX EPM Documentation Generator

Integrates EPMO health validation results with documentation generation
to provide health-aware documentation with scores, recommendations,
and actionable insights.

Features:
- Health score integration in documentation
- Remediation recommendations embedding
- Quality metrics visualization
- Health-based documentation priorities
- Auto-fix suggestions in docs
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import json

# Import EPMO health system
try:
    from ..health import run_health_system, EPMOHealthValidator
    from ..health.validation_suite import ValidationResult
    from ..health.remediation_engine import RemediationAction
    HEALTH_SYSTEM_AVAILABLE = True
except ImportError:
    # Fallback if health system not available
    HEALTH_SYSTEM_AVAILABLE = False


@dataclass
class HealthDocumentationData:
    """Health information to be embedded in documentation."""
    overall_score: float
    dimension_scores: Dict[str, Dict[str, Any]]
    remediation_actions: List[Dict[str, Any]]
    health_status: str  # 'excellent', 'good', 'fair', 'poor'
    priority_issues: List[Dict[str, Any]]
    auto_fixable_issues: List[Dict[str, Any]]
    effort_estimate: Dict[str, float]
    recommendations: List[str]


@dataclass
class HealthAwareDocumentation:
    """Documentation enriched with health information."""
    module_path: str
    health_data: HealthDocumentationData
    documentation_sections: Dict[str, str] = field(default_factory=dict)
    health_warnings: List[str] = field(default_factory=list)
    quality_badges: List[str] = field(default_factory=list)


class HealthIntegration:
    """
    Integrates EPMO health validation with documentation generation.
    
    Provides health-aware documentation that includes quality metrics,
    remediation guidance, and actionable recommendations.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.health_available = HEALTH_SYSTEM_AVAILABLE
        self._health_validator = None
        
        if self.health_available:
            try:
                self._health_validator = EPMOHealthValidator()
            except Exception:
                self.health_available = False
    
    def get_health_documentation_data(self, epmo_path: Path) -> Optional[HealthDocumentationData]:
        """
        Get health data formatted for documentation integration.
        
        Args:
            epmo_path: Path to the Entry Point Module
            
        Returns:
            HealthDocumentationData if health system is available, None otherwise
        """
        if not self.health_available:
            return None
        
        try:
            # Run comprehensive health check
            health_result = run_health_system(epmo_path, self.project_root)
            
            # Extract health report data
            health_report = health_result['health_report']
            remediation_plan = health_result.get('remediation_plan', [])
            effort_estimate = health_result.get('effort_estimate', {})
            
            # Process remediation actions
            remediation_actions = []
            auto_fixable_issues = []
            priority_issues = []
            
            for action in remediation_plan:
                action_data = {
                    'description': action.get('description', 'No description'),
                    'auto_fixable': action.get('auto_fixable', False),
                    'priority': action.get('priority', 'medium'),
                    'estimated_effort_minutes': action.get('estimated_effort_minutes', 0),
                    'action_type': action.get('action_type', 'unknown')
                }
                remediation_actions.append(action_data)
                
                if action_data['auto_fixable']:
                    auto_fixable_issues.append(action_data)
                
                if action_data['priority'] == 'high':
                    priority_issues.append(action_data)
            
            # Determine health status
            overall_score = health_report['overall_score']
            health_status = self._determine_health_status(overall_score)
            
            # Generate recommendations
            recommendations = self._generate_health_recommendations(
                health_report, remediation_actions
            )
            
            return HealthDocumentationData(
                overall_score=overall_score,
                dimension_scores=health_report['dimension_scores'],
                remediation_actions=remediation_actions,
                health_status=health_status,
                priority_issues=priority_issues,
                auto_fixable_issues=auto_fixable_issues,
                effort_estimate=effort_estimate,
                recommendations=recommendations
            )
            
        except Exception as e:
            print(f"Warning: Could not get health data: {e}")
            return None
    
    def create_health_aware_documentation(
        self, 
        epmo_path: Path, 
        module_analysis: Dict[str, Any]
    ) -> HealthAwareDocumentation:
        """
        Create documentation enriched with health information.
        
        Args:
            epmo_path: Path to the Entry Point Module
            module_analysis: Results from AST parser and dependency analysis
            
        Returns:
            HealthAwareDocumentation with integrated health data
        """
        # Get health data
        health_data = self.get_health_documentation_data(epmo_path)
        
        if health_data is None:
            # Create minimal health data if system unavailable
            health_data = HealthDocumentationData(
                overall_score=0.0,
                dimension_scores={},
                remediation_actions=[],
                health_status='unknown',
                priority_issues=[],
                auto_fixable_issues=[],
                effort_estimate={},
                recommendations=['Health system not available']
            )
        
        # Create documentation sections with health integration
        doc_sections = self._create_health_documentation_sections(
            health_data, module_analysis
        )
        
        # Generate health warnings
        health_warnings = self._generate_health_warnings(health_data)
        
        # Create quality badges
        quality_badges = self._create_quality_badges(health_data)
        
        return HealthAwareDocumentation(
            module_path=str(epmo_path),
            health_data=health_data,
            documentation_sections=doc_sections,
            health_warnings=health_warnings,
            quality_badges=quality_badges
        )
    
    def _determine_health_status(self, overall_score: float) -> str:
        """Determine textual health status from numeric score."""
        if overall_score >= 90:
            return 'excellent'
        elif overall_score >= 75:
            return 'good'
        elif overall_score >= 60:
            return 'fair'
        else:
            return 'poor'
    
    def _generate_health_recommendations(
        self, 
        health_report: Dict[str, Any], 
        remediation_actions: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate actionable health recommendations."""
        recommendations = []
        
        # Overall score recommendations
        overall_score = health_report['overall_score']
        if overall_score < 85:
            recommendations.append(
                f"Overall health score is {overall_score:.1f}/100. "
                "Consider addressing the remediation actions below to improve code quality."
            )
        
        # Dimension-specific recommendations
        dimension_scores = health_report.get('dimension_scores', {})
        for dim_name, dim_data in dimension_scores.items():
            score = dim_data.get('score', 0)
            if score < 70:
                recommendations.append(
                    f"{dim_name} score is low ({score:.1f}%). "
                    "This area requires immediate attention."
                )
        
        # Auto-fix recommendations
        auto_fixable_count = len([a for a in remediation_actions if a.get('auto_fixable')])
        if auto_fixable_count > 0:
            recommendations.append(
                f"{auto_fixable_count} issues can be automatically fixed. "
                "Run the auto-fix engine to resolve these quickly."
            )
        
        return recommendations
    
    def _create_health_documentation_sections(
        self, 
        health_data: HealthDocumentationData, 
        module_analysis: Dict[str, Any]
    ) -> Dict[str, str]:
        """Create documentation sections with integrated health information."""
        sections = {}
        
        # Health Overview Section
        sections['health_overview'] = self._create_health_overview_section(health_data)
        
        # Quality Metrics Section
        sections['quality_metrics'] = self._create_quality_metrics_section(health_data)
        
        # Remediation Guide Section
        if health_data.remediation_actions:
            sections['remediation_guide'] = self._create_remediation_section(health_data)
        
        # Auto-Fix Section
        if health_data.auto_fixable_issues:
            sections['auto_fix_guide'] = self._create_auto_fix_section(health_data)
        
        return sections
    
    def _create_health_overview_section(self, health_data: HealthDocumentationData) -> str:
        """Create health overview documentation section."""
        status_emoji = {
            'excellent': '🟢',
            'good': '🔵', 
            'fair': '🟡',
            'poor': '🔴',
            'unknown': '⚪'
        }
        
        emoji = status_emoji.get(health_data.health_status, '⚪')
        
        section = f"""## Health Overview {emoji}

**Overall Health Score:** {health_data.overall_score:.1f}/100  
**Status:** {health_data.health_status.title()}

This Entry Point Module has been automatically analyzed for code quality, documentation,
test coverage, performance, architecture, and maintainability.
"""
        
        if health_data.overall_score < 85:
            section += f"""
⚠️ **Action Required:** Health score is below the recommended threshold of 85/100.
Review the remediation guide below for specific improvements.
"""
        
        return section
    
    def _create_quality_metrics_section(self, health_data: HealthDocumentationData) -> str:
        """Create quality metrics documentation section."""
        section = "## Quality Metrics\n\n"
        
        if not health_data.dimension_scores:
            section += "Quality metrics not available.\n"
            return section
        
        section += "| Dimension | Score | Weight | Status |\n"
        section += "|-----------|-------|--------|---------|\n"
        
        for dim_name, dim_data in health_data.dimension_scores.items():
            score = dim_data.get('score', 0)
            weight = dim_data.get('weight', 0) * 100
            
            # Status indicator
            if score >= 85:
                status = "✅ Good"
            elif score >= 70:
                status = "⚠️ Fair"
            else:
                status = "❌ Needs Attention"
            
            section += f"| {dim_name} | {score:.1f}% | {weight:.0f}% | {status} |\n"
        
        return section
    
    def _create_remediation_section(self, health_data: HealthDocumentationData) -> str:
        """Create remediation guide documentation section."""
        section = "## Remediation Guide\n\n"
        section += f"Found {len(health_data.remediation_actions)} improvement opportunities.\n\n"
        
        # Group by priority
        high_priority = [a for a in health_data.remediation_actions if a.get('priority') == 'high']
        medium_priority = [a for a in health_data.remediation_actions if a.get('priority') == 'medium']
        low_priority = [a for a in health_data.remediation_actions if a.get('priority') == 'low']
        
        if high_priority:
            section += "### High Priority Issues\n\n"
            for i, action in enumerate(high_priority, 1):
                auto_fix = " (Auto-fixable)" if action.get('auto_fixable') else ""
                effort = action.get('estimated_effort_minutes', 0)
                section += f"{i}. **{action.get('description', 'No description')}**{auto_fix}\n"
                section += f"   - Estimated effort: {effort} minutes\n"
                section += f"   - Type: {action.get('action_type', 'Unknown')}\n\n"
        
        if medium_priority:
            section += "### Medium Priority Issues\n\n"
            for i, action in enumerate(medium_priority, 1):
                auto_fix = " (Auto-fixable)" if action.get('auto_fixable') else ""
                section += f"{i}. {action.get('description', 'No description')}{auto_fix}\n"
        
        if low_priority:
            section += f"\n### Low Priority Issues ({len(low_priority)} items)\n\n"
            section += "Consider addressing these when time permits:\n"
            for action in low_priority[:3]:  # Show first 3
                section += f"- {action.get('description', 'No description')}\n"
            if len(low_priority) > 3:
                section += f"- ... and {len(low_priority) - 3} more\n"
        
        return section
    
    def _create_auto_fix_section(self, health_data: HealthDocumentationData) -> str:
        """Create auto-fix guide documentation section."""
        section = "## Quick Fixes Available\n\n"
        
        auto_fixable = health_data.auto_fixable_issues
        section += f"🔧 {len(auto_fixable)} issues can be automatically fixed:\n\n"
        
        for i, action in enumerate(auto_fixable, 1):
            effort = action.get('estimated_effort_minutes', 0)
            action_type = action.get('action_type', 'Unknown')
            section += f"{i}. **{action_type}:** {action.get('description', 'No description')}\n"
            if effort > 0:
                section += f"   - Time saved: {effort} minutes\n"
        
        section += "\n**To apply auto-fixes:**\n"
        section += "```bash\n"
        section += "# Run CORTEX auto-fix engine\n"
        section += "cortex auto-fix <module-path>\n"
        section += "```\n"
        
        return section
    
    def _generate_health_warnings(self, health_data: HealthDocumentationData) -> List[str]:
        """Generate health-based warnings for documentation."""
        warnings = []
        
        if health_data.overall_score < 60:
            warnings.append("⚠️ Low overall health score - significant improvements needed")
        
        if health_data.priority_issues:
            warnings.append(f"🔥 {len(health_data.priority_issues)} high-priority issues require immediate attention")
        
        # Check for specific dimension issues
        for dim_name, dim_data in health_data.dimension_scores.items():
            score = dim_data.get('score', 0)
            if score < 50:
                warnings.append(f"❌ {dim_name} score is critically low ({score:.1f}%)")
        
        return warnings
    
    def _create_quality_badges(self, health_data: HealthDocumentationData) -> List[str]:
        """Create quality badge indicators."""
        badges = []
        
        # Overall health badge
        score = health_data.overall_score
        if score >= 90:
            badges.append("![Health](https://img.shields.io/badge/Health-Excellent-brightgreen)")
        elif score >= 75:
            badges.append("![Health](https://img.shields.io/badge/Health-Good-green)")
        elif score >= 60:
            badges.append("![Health](https://img.shields.io/badge/Health-Fair-yellow)")
        else:
            badges.append("![Health](https://img.shields.io/badge/Health-Poor-red)")
        
        # Auto-fix available badge
        if health_data.auto_fixable_issues:
            count = len(health_data.auto_fixable_issues)
            badges.append(f"![Auto-Fix](https://img.shields.io/badge/Auto_Fix-{count}_Available-blue)")
        
        # Maintenance effort badge
        total_effort = sum(
            action.get('estimated_effort_minutes', 0) 
            for action in health_data.remediation_actions
        )
        if total_effort > 0:
            hours = total_effort / 60
            if hours < 1:
                badges.append(f"![Effort](https://img.shields.io/badge/Effort-{total_effort}min-lightblue)")
            else:
                badges.append(f"![Effort](https://img.shields.io/badge/Effort-{hours:.1f}h-lightblue)")
        
        return badges


def get_health_integration_data(epmo_path: Path, project_root: Path = None) -> Dict[str, Any]:
    """
    Convenience function to get health integration data in serializable format.
    
    Args:
        epmo_path: Path to the Entry Point Module
        project_root: Root path of the project (defaults to current directory)
        
    Returns:
        Dictionary containing health integration data for documentation
    """
    if project_root is None:
        project_root = Path('.')
    
    health_integration = HealthIntegration(project_root)
    health_data = health_integration.get_health_documentation_data(epmo_path)
    
    if health_data is None:
        return {
            'status': 'health_system_unavailable',
            'message': 'EPMO health system not available'
        }
    
    # Convert to serializable format
    return {
        'status': 'success',
        'overall_score': health_data.overall_score,
        'health_status': health_data.health_status,
        'dimension_scores': health_data.dimension_scores,
        'remediation_actions_count': len(health_data.remediation_actions),
        'auto_fixable_count': len(health_data.auto_fixable_issues),
        'priority_issues_count': len(health_data.priority_issues),
        'recommendations': health_data.recommendations,
        'quality_badges': health_integration._create_quality_badges(health_data),
        'health_warnings': health_integration._generate_health_warnings(health_data)
    }