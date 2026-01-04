"""
Phase -1: Knowledge Library - Governance Consultation.

Executes BEFORE Phase 0 to consult Tier 0 (brain-protection-rules.yaml) and
Tier 2 (knowledge-graph.yaml) for governance compliance and knowledge graph insights.

This phase ensures all planning decisions align with CORTEX governance and learn
from previous executions before any planning work begins.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

from src.orchestrators.planning.governance_integrator import (
    GovernanceIntegrator,
    GovernanceValidation
)
from src.orchestrators.planning.knowledge_graph_query import (
    KnowledgeGraphQuery,
    KnowledgeContext
)
# C50-04: AST Scanning Integration
from src.cortex_agents.knowledge_library import KnowledgeLibrary, KnowledgeDiscovery


@dataclass
class GovernanceConsultationResult:
    """Result of Phase -1 governance consultation."""
    success: bool
    governance_validation: Optional[GovernanceValidation]
    knowledge_context: Optional[KnowledgeContext]
    knowledge_discovery: Optional[KnowledgeDiscovery]  # C50-04: AST scanning results
    consultation_report_path: Optional[str]
    violations: List[str]
    warnings: List[str]
    recommendations: List[str]
    execution_time_seconds: float


class PhaseMinusOne:
    """
    Phase -1: Knowledge Library - Pre-Planning Governance Consultation.
    
    Features:
    - Tier 0 consultation: brain-protection-rules.yaml (SKULL rules)
    - Tier 2 consultation: knowledge-graph.yaml (patterns, lessons)
    - Consultation report generation
    - Governance validation BEFORE planning
    - Knowledge graph insights integration
    
    Execution Order:
        Phase -1 → Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4
    
    Output:
    - Governance consultation report (Markdown)
    - Validation results (violations, warnings)
    - Knowledge insights (patterns, lessons)
    """
    
    def __init__(
        self,
        governance_integrator: Optional[GovernanceIntegrator] = None,
        knowledge_query: Optional[KnowledgeGraphQuery] = None,
        knowledge_library: Optional[KnowledgeLibrary] = None,  # C50-04
        output_dir: Optional[Path] = None,
        enable_ast_scanning: bool = True  # C50-04
    ):
        """
        Initialize Phase -1.
        
        Args:
            governance_integrator: Tier 0 governance integration
            knowledge_query: Tier 2 knowledge graph query
            knowledge_library: C50-04 Knowledge Library for AST scanning
            output_dir: Directory for consultation reports
            enable_ast_scanning: C50-04 Enable enhanced AST analysis
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize integrations
        self.governance = governance_integrator or GovernanceIntegrator()
        self.knowledge = knowledge_query or KnowledgeGraphQuery()
        
        # C50-04: Initialize Knowledge Library for AST scanning
        self.knowledge_library = knowledge_library
        self.enable_ast_scanning = enable_ast_scanning
        
        # Output configuration
        self.output_dir = output_dir or Path("cortex-brain/documents/planning/governance-consultations")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Phase -1 Knowledge Library initialized (AST scanning: {enable_ast_scanning})")
    
    def execute(
        self,
        feature_name: str,
        user_request: str,
        plan_context: Optional[Dict[str, Any]] = None
    ) -> GovernanceConsultationResult:
        """
        Execute Phase -1: Consult governance and knowledge library.
        
        Args:
            feature_name: Name of feature being planned
            user_request: Original user request
            plan_context: Optional planning context
        
        Returns:
            Consultation result with governance validation and knowledge insights
        """
        start_time = datetime.now()
        self.logger.info(f"Phase -1: Starting governance consultation for '{feature_name}'")
        
        try:
            # Step 1: Query Tier 0 (brain-protection-rules.yaml)
            self.logger.info("Phase -1: Querying Tier 0 governance rules")
            governance_validation = self._query_governance_rules(
                feature_name, user_request, plan_context
            )
            
            # Step 2: Query Tier 2 (knowledge-graph.yaml)
            self.logger.info("Phase -1: Querying Tier 2 knowledge graph")
            knowledge_context = self._query_knowledge_graph(
                feature_name, user_request
            )
            
            # Step 2.5: C50-04 - Knowledge Library AST Scanning
            knowledge_discovery = None
            if self.enable_ast_scanning and self.knowledge_library:
                self.logger.info("Phase -1: Executing Knowledge Library AST scanning (C50-04)")
                try:
                    knowledge_discovery = self.knowledge_library.scan_workspace(
                        target_feature=feature_name,
                        enable_ast_scanning=True
                    )
                    
                    # Log findings
                    stats = knowledge_discovery.scan_statistics
                    self.logger.info(
                        f"Phase -1: AST scan complete - "
                        f"{stats.get('injection_points_found', 0)} injection points, "
                        f"{stats.get('security_issues_found', 0)} security issues, "
                        f"{stats.get('performance_issues_found', 0)} performance issues"
                    )
                    
                    # Check for critical security issues
                    critical_security = [
                        issue for issue in knowledge_discovery.security_issues
                        if issue.severity == 'critical'
                    ]
                    if critical_security:
                        self.logger.warning(
                            f"Phase -1: Found {len(critical_security)} CRITICAL security issues - "
                            "review before proceeding"
                        )
                    
                except Exception as e:
                    self.logger.warning(f"Phase -1: Knowledge Library scanning failed: {e}")
            elif self.enable_ast_scanning:
                self.logger.warning("Phase -1: AST scanning enabled but Knowledge Library not initialized")
            
            # Step 3: Generate consultation report
            self.logger.info("Phase -1: Generating consultation report")
            report_path = self._generate_consultation_report(
                feature_name,
                governance_validation,
                knowledge_context,
                knowledge_discovery  # C50-04: Include AST results
            )
            
            # Step 4: Compile recommendations
            recommendations = self._compile_recommendations(
                governance_validation,
                knowledge_context,
                knowledge_discovery  # C50-04: Include AST recommendations
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Check for blocking violations
            violations = governance_validation.violations if governance_validation else []
            warnings = governance_validation.warnings if governance_validation else []
            success = len([v for v in violations if v.get('severity') == 'blocked']) == 0
            
            self.logger.info(
                f"Phase -1: Complete in {duration:.2f}s "
                f"({len(violations)} violations, {len(warnings)} warnings)"
            )
            
            return GovernanceConsultationResult(
                success=success,
                governance_validation=governance_validation,
                knowledge_context=knowledge_context,
                knowledge_discovery=knowledge_discovery,  # C50-04
                consultation_report_path=str(report_path) if report_path else None,
                violations=[v.get('message', str(v)) for v in violations],
                warnings=warnings,
                recommendations=recommendations,
                execution_time_seconds=duration
            )
            
        except Exception as e:
            self.logger.error(f"Phase -1: Consultation failed: {e}", exc_info=True)
            duration = (datetime.now() - start_time).total_seconds()
            
            return GovernanceConsultationResult(
                success=False,
                governance_validation=None,
                knowledge_context=None,
                knowledge_discovery=None,  # C50-04
                consultation_report_path=None,
                violations=[f"Phase -1 execution error: {str(e)}"],
                warnings=[],
                recommendations=[],
                execution_time_seconds=duration
            )
    
    def _query_governance_rules(
        self,
        feature_name: str,
        user_request: str,
        plan_context: Optional[Dict[str, Any]]
    ) -> Optional[GovernanceValidation]:
        """Query Tier 0 brain-protection-rules.yaml."""
        try:
            # Build validation context
            validation_context = {
                'feature_name': feature_name,
                'user_request': user_request,
                'plan_type': 'feature_implementation',
                'timestamp': datetime.now().isoformat()
            }
            
            if plan_context:
                validation_context.update(plan_context)
            
            # Validate against SKULL rules using validate_feature_request
            validation = self.governance.validate_feature_request(
                feature_name=feature_name,
                context=validation_context
            )
            
            self.logger.info(
                f"Phase -1: Governance validation complete "
                f"(valid={validation.is_valid}, violations={len(validation.violations)})"
            )
            
            return validation
            
        except Exception as e:
            self.logger.error(f"Phase -1: Governance query failed: {e}")
            return None
    
    def _query_knowledge_graph(
        self,
        feature_name: str,
        user_request: str
    ) -> Optional[KnowledgeContext]:
        """Query Tier 2 knowledge-graph.yaml."""
        try:
            # Query for related patterns and lessons using get_feature_context
            context = self.knowledge.get_feature_context(feature_name)
            
            self.logger.info(
                f"Phase -1: Knowledge graph query complete "
                f"(patterns={len(context.patterns) if context else 0}, "
                f"related={len(context.related_features) if context else 0})"
            )
            
            return context
            
        except Exception as e:
            self.logger.error(f"Phase -1: Knowledge graph query failed: {e}")
            return None
    
    def _generate_consultation_report(
        self,
        feature_name: str,
        governance: Optional[GovernanceValidation],
        knowledge: Optional[KnowledgeContext],
        knowledge_discovery: Optional[KnowledgeDiscovery] = None  # C50-04
    ) -> Optional[Path]:
        """Generate consultation report in Markdown."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            report_file = self.output_dir / f"consultation-{feature_name}-{timestamp}.md"
            
            # Build report content
            content = self._build_report_content(
                feature_name,
                governance,
                knowledge,
                knowledge_discovery  # C50-04
            )
            
            # Write report
            report_file.write_text(content, encoding='utf-8')
            
            self.logger.info(f"Phase -1: Consultation report: {report_file}")
            
            return report_file
            
        except Exception as e:
            self.logger.error(f"Phase -1: Report generation failed: {e}")
            return None
    
    def _build_report_content(
        self,
        feature_name: str,
        governance: Optional[GovernanceValidation],
        knowledge: Optional[KnowledgeContext],
        knowledge_discovery: Optional[KnowledgeDiscovery] = None  # C50-04
    ) -> str:
        """Build consultation report content."""
        lines = [
            f"# 🛡️ Phase -1 Governance Consultation Report",
            f"",
            f"**Feature:** {feature_name}",
            f"**Consultation Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Analyst:** CORTEX Planning System v5.0",
            f"",
            f"---",
            f"",
            f"## 1️⃣ Tier 0: Brain Protection Rules (SKULL)",
            f""
        ]
        
        # Governance section
        if governance:
            lines.extend([
                f"**Validation Status:** {'✅ PASS' if governance.is_valid else '❌ FAIL'}",
                f"**Rules Applied:** {len(governance.applied_rules)}",
                f"**Violations:** {len(governance.violations)}",
                f"**Warnings:** {len(governance.warnings)}",
                f""
            ])
            
            if governance.violations:
                lines.append("### 🚨 Violations")
                lines.append("")
                for violation in governance.violations:
                    severity = violation.get('severity', 'unknown')
                    message = violation.get('message', str(violation))
                    lines.append(f"- **[{severity.upper()}]** {message}")
                lines.append("")
            
            if governance.warnings:
                lines.append("### ⚠️ Warnings")
                lines.append("")
                for warning in governance.warnings:
                    lines.append(f"- {warning}")
                lines.append("")
        else:
            lines.extend([
                "**Status:** ⚠️ Governance query unavailable",
                ""
            ])
        
        lines.extend([
            "---",
            "",
            "## 2️⃣ Tier 2: Knowledge Graph Insights",
            ""
        ])
        
        # Knowledge graph section
        if knowledge:
            lines.extend([
                f"**Patterns Found:** {len(knowledge.patterns)}",
                f"**Related Features:** {len(knowledge.related_features)}",
                f"**Dependencies:** {len(knowledge.dependencies)}",
                f"**Risks:** {len(knowledge.risks)}",
                f""
            ])
            
            if knowledge.patterns:
                lines.append("### 📚 Relevant Patterns")
                lines.append("")
                for pattern in knowledge.patterns[:5]:  # Top 5
                    lines.append(f"- {pattern}")
                lines.append("")
            
            if knowledge.recommendations:
                lines.append("### 💡 Knowledge Recommendations")
                lines.append("")
                for rec in knowledge.recommendations[:5]:  # Top 5
                    lines.append(f"- {rec}")
                lines.append("")
        else:
            lines.extend([
                "**Status:** ⚠️ Knowledge graph query unavailable",
                ""
            ])
        
        # C50-04: AST Scanning Results
        if knowledge_discovery:
            lines.extend([
                "---",
                "",
                "## 🔬 AST Scanning Analysis (C50-04)",
                ""
            ])
            
            stats = knowledge_discovery.scan_statistics
            lines.extend([
                f"**Files Scanned:** {stats.get('files_scanned', 0)}",
                f"**Injection Points:** {stats.get('injection_points_found', 0)}",
                f"**Security Issues:** {stats.get('security_issues_found', 0)}",
                f"**Performance Issues:** {stats.get('performance_issues_found', 0)}",
                ""
            ])
            
            # Injection points (top 3)
            if knowledge_discovery.injection_points:
                lines.append("### 🎯 Top Injection Points")
                lines.append("")
                for point in knowledge_discovery.injection_points[:3]:
                    lines.append(f"- **{point.file_path}:{point.line_number}** (score: {point.score:.2f})")
                    lines.append(f"  - Type: `{point.injection_type}`")
                    lines.append(f"  - Reasoning: {point.reasoning}")
                lines.append("")
            
            # Security issues (critical/high only)
            critical_security = [
                issue for issue in knowledge_discovery.security_issues
                if issue.severity in ['critical', 'high']
            ]
            if critical_security:
                lines.append("### 🔒 Critical/High Security Issues")
                lines.append("")
                for issue in critical_security[:5]:  # Top 5
                    severity_icon = "🔴" if issue.severity == "critical" else "🟠"
                    lines.append(f"- {severity_icon} **{issue.issue_type}** - {issue.file_path}:{issue.line_number}")
                    lines.append(f"  - {issue.description}")
                    lines.append(f"  - Recommendation: {issue.recommendation}")
                lines.append("")
            
            # Performance issues (high only)
            high_perf = [
                issue for issue in knowledge_discovery.performance_issues
                if issue.severity == 'high'
            ]
            if high_perf:
                lines.append("### ⚡ High-Impact Performance Issues")
                lines.append("")
                for issue in high_perf[:5]:
                    lines.append(f"- 🔴 **{issue.issue_type}** - {issue.file_path}:{issue.line_number}")
                    lines.append(f"  - {issue.description}")
                    lines.append(f"  - Impact: {issue.estimated_impact}")
                lines.append("")
        
        lines.extend([
            "---",
            "",
            "## 3️⃣ Recommendations",
            ""
        ])
        
        # Recommendations
        recommendations = self._compile_recommendations(governance, knowledge, knowledge_discovery)
        if recommendations:
            for rec in recommendations:
                lines.append(f"- {rec}")
        else:
            lines.append("- No specific recommendations at this time")
        
        lines.extend([
            "",
            "---",
            "",
            f"**Copyright © 2025-2026 Asif Hussain. All rights reserved.**"
        ])
        
        return '\n'.join(lines)
    
    def _compile_recommendations(
        self,
        governance: Optional[GovernanceValidation],
        knowledge: Optional[KnowledgeContext],
        knowledge_discovery: Optional[KnowledgeDiscovery] = None  # C50-04
    ) -> List[str]:
        """Compile actionable recommendations from consultation."""
        recommendations = []
        
        # Governance recommendations
        if governance:
            if governance.violations:
                recommendations.append(
                    f"🚨 Address {len(governance.violations)} governance violation(s) before proceeding"
                )
            if governance.warnings:
                recommendations.append(
                    f"⚠️ Review {len(governance.warnings)} warning(s) for best practices"
                )
        
        # Knowledge recommendations
        if knowledge:
            if knowledge.patterns:
                recommendations.append(
                    f"📚 Consider applying {len(knowledge.patterns)} relevant pattern(s)"
                )
            if knowledge.recommendations:
                # Add top 3 recommendations from knowledge graph
                for rec in knowledge.recommendations[:3]:
                    recommendations.append(f"💡 {rec}")
        
        # C50-04: AST Scanning Recommendations
        if knowledge_discovery:
            # Security recommendations
            critical_security = [
                issue for issue in knowledge_discovery.security_issues
                if issue.severity == 'critical'
            ]
            if critical_security:
                recommendations.append(
                    f"🔒 URGENT: Address {len(critical_security)} critical security issue(s) before implementation"
                )
            
            # Performance recommendations
            high_perf = [
                issue for issue in knowledge_discovery.performance_issues
                if issue.severity == 'high'
            ]
            if high_perf:
                recommendations.append(
                    f"⚡ Consider refactoring {len(high_perf)} high-complexity function(s) for maintainability"
                )
            
            # Injection point recommendations
            if knowledge_discovery.injection_points:
                top_point = knowledge_discovery.injection_points[0]
                recommendations.append(
                    f"🎯 Optimal injection point: {top_point.file_path}:{top_point.line_number} "
                    f"(score: {top_point.score:.2f})"
                )
        
        # Default recommendation
        if not recommendations:
            recommendations.append("✅ No governance blockers - proceed with planning")
        
        return recommendations


# Convenience function for direct execution
def execute_phase_minus_one(
    feature_name: str,
    user_request: str,
    plan_context: Optional[Dict[str, Any]] = None,
    output_dir: Optional[Path] = None
) -> GovernanceConsultationResult:
    """
    Execute Phase -1 governance consultation.
    
    Args:
        feature_name: Feature being planned
        user_request: Original user request
        plan_context: Optional planning context
        output_dir: Directory for reports
    
    Returns:
        Consultation result
    """
    phase = PhaseMinusOne(output_dir=output_dir)
    return phase.execute(feature_name, user_request, plan_context)
