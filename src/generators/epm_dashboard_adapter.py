"""
EPM Dashboard Adapter - Transform EPM Results to Interactive Dashboards

Converts EPM output data structures (AlignmentReport, validation results, etc.)
into DashboardLayer format compatible with DashboardTemplateGenerator.

Handles:
- System Alignment reports → 5-layer interactive dashboards
- Feature scores → D3.js visualizations (gauge, tree, matrix)
- Historical trends → Timeline visualizations
- Conflicts/recommendations → Structured tables and actions

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from src.generators.dashboard_template_generator import (
    DashboardTemplateGenerator,
    DashboardLayer,
    VisualizationConfig
)

logger = logging.getLogger(__name__)


class EPMDashboardAdapter:
    """
    Transforms EPM results into interactive dashboard format.
    
    Usage:
        adapter = EPMDashboardAdapter()
        layers = adapter.transform_alignment_report(alignment_report, conflicts)
        generator = DashboardTemplateGenerator()
        html = generator.generate_dashboard(
            title="System Alignment Report",
            layers=layers,
            author="CORTEX System Alignment",
            timestamp=datetime.now()
        )
    """
    
    def __init__(self):
        """Initialize EPM dashboard adapter."""
        self.logger = logging.getLogger(__name__)
    
    def transform_alignment_report(
        self,
        report: Any,
        conflicts: Optional[List[Any]] = None
    ) -> List[DashboardLayer]:
        """
        Transform AlignmentReport into 5-layer dashboard structure.
        
        Layers:
        1. Executive Summary - Overall health gauge, key metrics
        2. Feature Analysis - Feature hierarchy tree, integration scores
        3. Issues & Conflicts - Priority matrix, conflict list
        4. Historical Trends - Timeline of health scores over time
        5. Actions & Export - Remediation suggestions, export options
        
        Args:
            report: AlignmentReport from SystemAlignmentOrchestrator
            conflicts: Optional list of Conflict objects
            
        Returns:
            List of 5 DashboardLayer objects ready for generation
        """
        conflicts = conflicts or []
        
        layers = [
            self._create_executive_layer(report),
            self._create_analysis_layer(report),
            self._create_issues_layer(report, conflicts),
            self._create_trends_layer(report),
            self._create_actions_layer(report, conflicts)
        ]
        
        return layers
    
    def _create_executive_layer(self, report: Any) -> DashboardLayer:
        """
        Create Executive Summary layer.
        
        Content:
        - Overall health gauge (0-100%)
        - Key metrics (features, issues, warnings)
        - Status badge (Healthy/Warning/Critical)
        - Quick assessment summary
        """
        # Calculate key metrics
        total_features = len(report.feature_scores) if hasattr(report, 'feature_scores') else 0
        healthy_count = 0
        warning_count = 0
        critical_count = 0
        
        if hasattr(report, 'feature_scores'):
            for score in report.feature_scores.values():
                if hasattr(score, 'score'):
                    if score.score >= 90:
                        healthy_count += 1
                    elif score.score >= 70:
                        warning_count += 1
                    else:
                        critical_count += 1
        
        # Determine overall status
        if report.overall_health >= 90 and report.critical_issues == 0:
            status = "Healthy"
            status_emoji = "✅"
        elif report.overall_health >= 70:
            status = "Warning"
            status_emoji = "⚠️"
        else:
            status = "Critical"
            status_emoji = "❌"
        
        # Build content
        content = {
            'key_metrics': [
                {'label': 'Overall Health', 'value': f'{report.overall_health}%'},
                {'label': 'Total Features', 'value': str(total_features)},
                {'label': 'Critical Issues', 'value': str(report.critical_issues)},
                {'label': 'Warnings', 'value': str(report.warnings)},
                {'label': 'Healthy Features', 'value': f'{healthy_count}/{total_features}'}
            ],
            'text': self._generate_executive_summary_text(
                report, status, healthy_count, warning_count, critical_count
            )
        }
        
        # Health gauge visualization
        visualization = VisualizationConfig(
            viz_type='gauge',
            target_id='health-gauge',
            data={
                'value': report.overall_health,
                'label': 'System Health',
                'thresholds': [70, 90],  # Warning at 70%, healthy at 90%
                'status': status
            },
            width=400,
            height=300
        )
        
        return DashboardLayer(
            layer_id='layer-executive',
            name='Executive Summary',
            order=1,
            content=content,
            visualization=visualization
        )
    
    def _generate_executive_summary_text(
        self,
        report: Any,
        status: str,
        healthy: int,
        warning: int,
        critical: int
    ) -> str:
        """Generate executive summary narrative."""
        total = healthy + warning + critical
        
        # Build summary text
        lines = [
            f"System Status: **{status}**",
            "",
            f"The CORTEX system alignment shows an overall health score of **{report.overall_health}%**. ",
        ]
        
        if report.overall_health >= 90:
            lines.append("The system is in excellent health with all major components properly integrated and tested.")
        elif report.overall_health >= 70:
            lines.append("The system is functional but has some areas requiring attention to maintain optimal health.")
        else:
            lines.append("The system requires immediate attention due to critical integration issues.")
        
        lines.extend([
            "",
            f"**Feature Breakdown:**",
            f"- {healthy} features are healthy (≥90% integration)",
            f"- {warning} features have warnings (70-89% integration)",
            f"- {critical} features are critical (<70% integration)"
        ])
        
        if report.critical_issues > 0:
            lines.extend([
                "",
                f"⚠️ **{report.critical_issues} critical issues detected** requiring immediate resolution."
            ])
        
        if hasattr(report, 'catalog_features_new') and report.catalog_features_new > 0:
            lines.extend([
                "",
                f"📦 **{report.catalog_features_new} new features** discovered since last alignment review."
            ])
        
        return "\n".join(lines)
    
    def _create_analysis_layer(self, report: Any) -> DashboardLayer:
        """
        Create Feature Analysis layer.
        
        Content:
        - Feature integration scores table
        - Feature hierarchy tree visualization
        - Integration depth breakdown
        - Documentation and test coverage status
        """
        # Build feature table HTML
        feature_table_html = self._build_feature_table(report)
        
        # Prepare tree visualization data
        tree_data = self._build_feature_tree_data(report)
        
        content = {
            'text': f"""
**Feature Integration Analysis**

This layer provides detailed analysis of all discovered CORTEX features and their integration depth.

{feature_table_html}

**Integration Scoring:**
- **Discovered (20%):** Feature file exists in correct location
- **Imported (40%):** Can be imported without errors
- **Instantiated (60%):** Class can be instantiated successfully
- **Documented (70%):** Has documentation in prompts/modules/
- **Tested (80%):** Has test coverage ≥70%
- **Wired (90%):** Entry point trigger exists in response-templates.yaml
- **Optimized (100%):** Performance benchmarks pass
"""
        }
        
        visualization = VisualizationConfig(
            viz_type='tree',
            target_id='feature-tree',
            data=tree_data,
            width=960,
            height=600
        )
        
        return DashboardLayer(
            layer_id='layer-analysis',
            name='Feature Analysis',
            order=2,
            content=content,
            visualization=visualization
        )
    
    def _build_feature_table(self, report: Any) -> str:
        """Build HTML table of feature scores."""
        if not hasattr(report, 'feature_scores') or not report.feature_scores:
            return "<p><em>No features discovered</em></p>"
        
        rows = []
        for feature_name, score in sorted(report.feature_scores.items()):
            status_emoji = "✅" if score.score >= 90 else "⚠️" if score.score >= 70 else "❌"
            issues_text = ", ".join(score.issues) if hasattr(score, 'issues') and score.issues else "None"
            
            rows.append(f"""
                <tr>
                    <td>{status_emoji} {feature_name}</td>
                    <td style="text-align: center;">{score.feature_type if hasattr(score, 'feature_type') else 'N/A'}</td>
                    <td style="text-align: center;"><strong>{score.score}%</strong></td>
                    <td>{issues_text}</td>
                </tr>
            """)
        
        table_html = f"""
<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
    <thead>
        <tr style="background: #2c3e50; color: white;">
            <th style="padding: 10px; text-align: left;">Feature</th>
            <th style="padding: 10px; text-align: center;">Type</th>
            <th style="padding: 10px; text-align: center;">Score</th>
            <th style="padding: 10px; text-align: left;">Issues</th>
        </tr>
    </thead>
    <tbody>
        {''.join(rows)}
    </tbody>
</table>
"""
        return table_html
    
    def _build_feature_tree_data(self, report: Any) -> Dict[str, Any]:
        """Build hierarchical tree data for D3.js visualization."""
        if not hasattr(report, 'feature_scores') or not report.feature_scores:
            return {'name': 'CORTEX', 'children': []}
        
        # Group features by type
        feature_groups: Dict[str, List[Dict[str, Any]]] = {}
        
        for feature_name, score in report.feature_scores.items():
            feature_type = score.feature_type if hasattr(score, 'feature_type') else 'other'
            
            if feature_type not in feature_groups:
                feature_groups[feature_type] = []
            
            feature_groups[feature_type].append({
                'name': feature_name,
                'value': score.score,
                'status': 'healthy' if score.score >= 90 else 'warning' if score.score >= 70 else 'critical'
            })
        
        # Build tree structure
        children = []
        for group_name, features in sorted(feature_groups.items()):
            avg_score = sum(f['value'] for f in features) / len(features) if features else 0
            children.append({
                'name': group_name.capitalize(),
                'value': round(avg_score, 1),
                'children': features
            })
        
        return {
            'name': 'CORTEX Features',
            'children': children
        }
    
    def _create_issues_layer(self, report: Any, conflicts: List[Any]) -> DashboardLayer:
        """
        Create Issues & Conflicts layer.
        
        Content:
        - Priority matrix visualization
        - Critical issues list
        - Detected conflicts table
        - Impact assessment
        """
        # Build issues content
        issues_html = self._build_issues_content(report, conflicts)
        
        # Priority matrix data
        matrix_data = self._build_priority_matrix_data(report, conflicts)
        
        content = {
            'text': f"""
**Issues & Conflicts Report**

{issues_html}

**Priority Matrix Legend:**
- **High Priority / High Impact:** Immediate action required
- **High Priority / Low Impact:** Schedule for next sprint
- **Low Priority / High Impact:** Monitor closely
- **Low Priority / Low Impact:** Address during maintenance
"""
        }
        
        visualization = VisualizationConfig(
            viz_type='matrix',
            target_id='priority-matrix',
            data=matrix_data,
            width=600,
            height=600
        )
        
        return DashboardLayer(
            layer_id='layer-issues',
            name='Issues & Conflicts',
            order=3,
            content=content,
            visualization=visualization
        )
    
    def _build_issues_content(self, report: Any, conflicts: List[Any]) -> str:
        """Build issues and conflicts HTML content."""
        sections = []
        
        # Critical issues
        if report.critical_issues > 0:
            sections.append(f"""
<div style="background: #fee; padding: 15px; border-left: 4px solid #c33; margin: 10px 0;">
    <h4 style="margin: 0 0 10px 0;">❌ Critical Issues: {report.critical_issues}</h4>
    <p>These issues require immediate attention and may prevent system functionality.</p>
</div>
""")
        
        # Warnings
        if report.warnings > 0:
            sections.append(f"""
<div style="background: #ffeaa7; padding: 15px; border-left: 4px solid #f39c12; margin: 10px 0;">
    <h4 style="margin: 0 0 10px 0;">⚠️ Warnings: {report.warnings}</h4>
    <p>These issues should be addressed to maintain system health.</p>
</div>
""")
        
        # Conflicts
        if conflicts:
            conflicts_list = "\n".join([
                f"<li><strong>{c.conflict_type if hasattr(c, 'conflict_type') else 'Unknown'}:</strong> {c.description if hasattr(c, 'description') else str(c)}</li>"
                for c in conflicts[:10]  # Limit to 10
            ])
            sections.append(f"""
<div style="background: #dfe6e9; padding: 15px; border-left: 4px solid #636e72; margin: 10px 0;">
    <h4 style="margin: 0 0 10px 0;">🔄 Detected Conflicts: {len(conflicts)}</h4>
    <ul>{conflicts_list}</ul>
    {f'<p><em>...and {len(conflicts) - 10} more</em></p>' if len(conflicts) > 10 else ''}
</div>
""")
        
        # Healthy state
        if report.critical_issues == 0 and report.warnings == 0 and not conflicts:
            sections.append("""
<div style="background: #d4edda; padding: 15px; border-left: 4px solid #28a745; margin: 10px 0;">
    <h4 style="margin: 0 0 10px 0;">✅ No Issues Detected</h4>
    <p>System is healthy with no critical issues, warnings, or conflicts.</p>
</div>
""")
        
        return "\n".join(sections)
    
    def _build_priority_matrix_data(self, report: Any, conflicts: List[Any]) -> Dict[str, Any]:
        """Build priority matrix data for visualization."""
        # Create matrix cells (Priority vs Impact)
        matrix = {
            'dimensions': ['High Priority', 'Low Priority'],
            'categories': ['High Impact', 'Low Impact'],
            'cells': []
        }
        
        # Categorize issues
        high_priority_high_impact = []
        high_priority_low_impact = []
        low_priority_high_impact = []
        low_priority_low_impact = []
        
        # Critical issues = high priority, high impact
        if report.critical_issues > 0:
            high_priority_high_impact.append({
                'label': f'{report.critical_issues} Critical Issues',
                'count': report.critical_issues
            })
        
        # Warnings = high priority, low impact
        if report.warnings > 0:
            high_priority_low_impact.append({
                'label': f'{report.warnings} Warnings',
                'count': report.warnings
            })
        
        # Conflicts vary by severity
        if conflicts:
            for conflict in conflicts:
                severity = getattr(conflict, 'severity', 'medium')
                if severity == 'high':
                    high_priority_high_impact.append({
                        'label': getattr(conflict, 'description', 'Conflict')[:50],
                        'count': 1
                    })
                elif severity == 'medium':
                    high_priority_low_impact.append({
                        'label': getattr(conflict, 'description', 'Conflict')[:50],
                        'count': 1
                    })
                else:
                    low_priority_low_impact.append({
                        'label': getattr(conflict, 'description', 'Conflict')[:50],
                        'count': 1
                    })
        
        matrix['cells'] = [
            {'priority': 'high', 'impact': 'high', 'items': high_priority_high_impact, 'count': len(high_priority_high_impact)},
            {'priority': 'high', 'impact': 'low', 'items': high_priority_low_impact, 'count': len(high_priority_low_impact)},
            {'priority': 'low', 'impact': 'high', 'items': low_priority_high_impact, 'count': len(low_priority_high_impact)},
            {'priority': 'low', 'impact': 'low', 'items': low_priority_low_impact, 'count': len(low_priority_low_impact)}
        ]
        
        return matrix
    
    def _create_trends_layer(self, report: Any) -> DashboardLayer:
        """
        Create Historical Trends layer.
        
        Content:
        - Health score timeline
        - Feature count evolution
        - Issue trend analysis
        - Velocity metrics
        """
        # Build trends narrative
        trends_text = self._build_trends_narrative(report)
        
        # Timeline visualization data
        timeline_data = self._build_timeline_data(report)
        
        content = {
            'text': trends_text
        }
        
        visualization = VisualizationConfig(
            viz_type='timeline',
            target_id='trends-timeline',
            data=timeline_data,
            width=960,
            height=300
        )
        
        return DashboardLayer(
            layer_id='layer-trends',
            name='Historical Trends',
            order=4,
            content=content,
            visualization=visualization
        )
    
    def _build_trends_narrative(self, report: Any) -> str:
        """Build trends analysis narrative."""
        lines = [
            "**Historical Performance Trends**",
            "",
            f"Current overall health: **{report.overall_health}%**",
            ""
        ]
        
        # Add catalog trend if available
        if hasattr(report, 'catalog_features_new') and report.catalog_features_new > 0:
            lines.extend([
                f"**New Features Discovered:** {report.catalog_features_new} features added since last alignment",
                ""
            ])
        
        if hasattr(report, 'catalog_days_since_review') and report.catalog_days_since_review:
            lines.extend([
                f"**Days Since Last Review:** {report.catalog_days_since_review} days",
                ""
            ])
        
        lines.extend([
            "**Trend Analysis:**",
            "- Health score trajectory over time shown in timeline below",
            "- Feature count evolution tracks system growth",
            "- Issue trends help identify improvement or degradation patterns",
            "",
            "*Historical data tracked in `cortex-brain/metrics-history/alignment_history.jsonl`*"
        ])
        
        return "\n".join(lines)
    
    def _build_timeline_data(self, report: Any) -> Dict[str, Any]:
        """Build timeline data for D3.js visualization."""
        # Timeline data structure
        timeline = {
            'series': [
                {
                    'name': 'Overall Health',
                    'data': [
                        {
                            'date': report.timestamp.isoformat() if hasattr(report.timestamp, 'isoformat') else str(report.timestamp),
                            'value': report.overall_health
                        }
                    ]
                },
                {
                    'name': 'Features',
                    'data': [
                        {
                            'date': report.timestamp.isoformat() if hasattr(report.timestamp, 'isoformat') else str(report.timestamp),
                            'value': len(report.feature_scores) if hasattr(report, 'feature_scores') else 0
                        }
                    ]
                },
                {
                    'name': 'Issues',
                    'data': [
                        {
                            'date': report.timestamp.isoformat() if hasattr(report.timestamp, 'isoformat') else str(report.timestamp),
                            'value': report.critical_issues + report.warnings
                        }
                    ]
                }
            ],
            'xAxis': 'Time',
            'yAxis': 'Score / Count'
        }
        
        return timeline
    
    def _create_actions_layer(self, report: Any, conflicts: List[Any]) -> DashboardLayer:
        """
        Create Actions & Export layer.
        
        Content:
        - Remediation suggestions
        - Recommended next steps
        - Export buttons (PDF, PNG, PPTX)
        - Action items for follow-up
        """
        # Build actions content
        actions_text = self._build_actions_content(report, conflicts)
        
        # Action buttons
        actions = [
            {'id': 'export-pdf-btn', 'label': 'Export to PDF', 'type': 'primary'},
            {'id': 'export-png-btn', 'label': 'Export to PNG', 'type': 'secondary'},
            {'id': 'export-pptx-btn', 'label': 'Export to PowerPoint', 'type': 'secondary'},
            {'id': 'create-workitem-btn', 'label': 'Create Work Item', 'type': 'secondary'}
        ]
        
        content = {
            'text': actions_text,
            'actions': actions
        }
        
        # Thumbnail preview visualization
        visualization = VisualizationConfig(
            viz_type='thumbnail',
            target_id='export-preview',
            data={'preview': 'dashboard-content'},
            width=300,
            height=200
        )
        
        return DashboardLayer(
            layer_id='layer-actions',
            name='Actions & Export',
            order=5,
            content=content,
            visualization=visualization
        )
    
    def _build_actions_content(self, report: Any, conflicts: List[Any]) -> str:
        """Build actions and recommendations content."""
        lines = [
            "**Recommended Actions**",
            ""
        ]
        
        # Remediation suggestions
        if hasattr(report, 'remediation_suggestions') and report.remediation_suggestions:
            lines.extend([
                f"**Auto-Remediation Available:** {len(report.remediation_suggestions)} suggestions",
                ""
            ])
            for idx, suggestion in enumerate(report.remediation_suggestions[:5], 1):
                suggestion_type = getattr(suggestion, 'suggestion_type', 'unknown')
                feature = getattr(suggestion, 'feature_name', 'Unknown')
                lines.append(f"{idx}. **{suggestion_type.title()}** for {feature}")
            
            if len(report.remediation_suggestions) > 5:
                lines.append(f"   *...and {len(report.remediation_suggestions) - 5} more suggestions*")
            lines.append("")
        
        # Fix templates (Align 2.0)
        if hasattr(report, 'fix_templates') and report.fix_templates:
            lines.extend([
                f"**Fix Templates Generated:** {len(report.fix_templates)} automated fixes available",
                ""
            ])
        
        # Priority actions
        lines.extend([
            "**Priority Action Items:**",
            ""
        ])
        
        if report.critical_issues > 0:
            lines.append(f"1. 🔴 **URGENT:** Resolve {report.critical_issues} critical issues")
        
        if report.warnings > 0:
            lines.append(f"2. 🟡 **Important:** Address {report.warnings} warnings")
        
        if conflicts:
            lines.append(f"3. 🔄 **Review:** Investigate {len(conflicts)} detected conflicts")
        
        if hasattr(report, 'catalog_features_new') and report.catalog_features_new > 0:
            lines.append(f"4. 📦 **Catalog:** Review {report.catalog_features_new} newly discovered features")
        
        lines.extend([
            "",
            "**Export Options:**",
            "- **PDF:** Full report with embedded visualizations",
            "- **PNG:** High-resolution image for presentations",
            "- **PowerPoint:** Editable slides for stakeholder meetings",
            "",
            "**Next Steps:**",
            "1. Review detailed analysis in layers above",
            "2. Prioritize remediation based on impact",
            "3. Export report for team review",
            "4. Track progress in next alignment cycle"
        ])
        
        return "\n".join(lines)
