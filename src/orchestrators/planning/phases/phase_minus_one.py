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


@dataclass
class GovernanceConsultationResult:
    """Result of Phase -1 governance consultation."""
    success: bool
    governance_validation: Optional[GovernanceValidation]
    knowledge_context: Optional[KnowledgeContext]
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
        output_dir: Optional[Path] = None
    ):
        """
        Initialize Phase -1.
        
        Args:
            governance_integrator: Tier 0 governance integration
            knowledge_query: Tier 2 knowledge graph query
            output_dir: Directory for consultation reports
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize integrations
        self.governance = governance_integrator or GovernanceIntegrator()
        self.knowledge = knowledge_query or KnowledgeGraphQuery()
        
        # Output configuration
        self.output_dir = output_dir or Path("cortex-brain/documents/planning/governance-consultations")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("Phase -1 Knowledge Library initialized")
    
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
            
            # Step 3: Generate consultation report
            self.logger.info("Phase -1: Generating consultation report")
            report_path = self._generate_consultation_report(
                feature_name,
                governance_validation,
                knowledge_context
            )
            
            # Step 4: Compile recommendations
            recommendations = self._compile_recommendations(
                governance_validation,
                knowledge_context
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
        knowledge: Optional[KnowledgeContext]
    ) -> Optional[Path]:
        """Generate consultation report in Markdown."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            report_file = self.output_dir / f"consultation-{feature_name}-{timestamp}.md"
            
            # Build report content
            content = self._build_report_content(feature_name, governance, knowledge)
            
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
        knowledge: Optional[KnowledgeContext]
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
        
        lines.extend([
            "---",
            "",
            "## 3️⃣ Recommendations",
            ""
        ])
        
        # Recommendations
        recommendations = self._compile_recommendations(governance, knowledge)
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
        knowledge: Optional[KnowledgeContext]
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
