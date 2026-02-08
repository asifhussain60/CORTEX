"""Phase 48 S5: Prompt Enhancement for Challenge Gate Integration.

Minimal adjustments to cortex-architect.prompt.md based on validation insights.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class EnhancementType(str, Enum):
    """Types of prompt enhancements."""

    EXAMPLE = "example"
    RULE = "rule"
    CLARIFICATION = "clarification"
    BEHAVIORAL_GUIDE = "behavioral_guide"
    EDGE_CASE = "edge_case"


@dataclass
class PromptEnhancement:
    """A single enhancement to a prompt."""

    type: EnhancementType
    section: str  # e.g., "SILENT AUTONOMOUS EXECUTION"
    current_text: str
    enhanced_text: str
    rationale: str
    impact: str  # "low", "medium", "high"


@dataclass
class AgentEnhancement:
    """Enhancement to an agent specification."""

    agent_name: str
    agent_file: str
    enhancement: str
    rationale: str
    impact: str  # "low", "medium", "high"


@dataclass
class PromptEnhancementReport:
    """Report of all prompt enhancements."""

    timestamp: str
    phase: str
    prompt_enhancements: List[PromptEnhancement]
    agent_enhancements: List[AgentEnhancement]
    total_impact: str  # "low", "medium", "high"
    recommendations: List[str]


class PromptEnhancementOrchestrator:
    """Orchestrator for minimal prompt/agent enhancements.

    Based on Phase 48 S1-S4 validation insights, applies targeted
    enhancements to cortex-architect.prompt.md and agent specifications.
    """

    def __init__(self):
        """Initialize prompt enhancement orchestrator."""
        self.enhancements: List[PromptEnhancement] = []
        self.agent_enhancements: List[AgentEnhancement] = []

    def identify_enhancements(self) -> List[PromptEnhancement]:
        """Identify needed prompt enhancements based on Phase 48 learnings.

        Returns:
            List of identified enhancements.
        """
        enhancements = []

        # S1 Learning: Registry consistency is critical
        enhancements.append(
            PromptEnhancement(
                type=EnhancementType.RULE,
                section="PHASE DISCOVERY PROTOCOL",
                current_text="Always check cortex-registry/_cortex-master/index.yaml for phase metadata",
                enhanced_text=(
                    "MANDATORY: Check cortex-registry/_cortex-master/index.yaml FIRST for phase metadata. "
                    "Registry is SSOT. Verify: phase status, dependencies, test targets, ROI scores before proceeding."
                ),
                rationale="S1 validation showed registry drift causes execution misalignment",
                impact="medium",
            )
        )

        # S2 Learning: Dependency documentation
        enhancements.append(
            PromptEnhancement(
                type=EnhancementType.BEHAVIORAL_GUIDE,
                section="ORCHESTRATOR INTEGRATION",
                current_text="Document all orchestrator dependencies in wiring.yaml",
                enhanced_text=(
                    "Document ALL orchestrator dependencies in wiring.yaml with tier classification (core/domain/support). "
                    "Use DependencyGraphGenerator to verify no circular dependencies. "
                    "Run DependencyGraph analysis on every wiring change."
                ),
                rationale="S2 showed circular dependencies can silently break CORTEX mesh",
                impact="high",
            )
        )

        # S3 Learning: Challenge gate integration
        enhancements.append(
            PromptEnhancement(
                type=EnhancementType.RULE,
                section="SILENT AUTONOMOUS EXECUTION",
                current_text="Proceed silently after user says 'proceed'",
                enhanced_text=(
                    "⚠️ CHALLENGE GATE REQUIREMENT: "
                    "1. Generate challenges with ROI-scored alternatives (cortex_challenge) "
                    "2. Display to user for review (stop for decision) "
                    "3. Only proceed after implicit/explicit confirmation on alternative selection"
                ),
                rationale="S3 Challenge Gate prevents regressions before implementation",
                impact="high",
            )
        )

        # S3 Learning: Alternative evaluation
        enhancements.append(
            PromptEnhancement(
                type=EnhancementType.CLARIFICATION,
                section="CHALLENGE GATE EVALUATION",
                current_text="Challenges provide alternatives",
                enhanced_text=(
                    "Challenge alternatives must include: "
                    "- Description (clear problem statement) "
                    "- ROI score (0.0-1.0 numeric comparison) "
                    "- Effort estimate (low/medium/high + days) "
                    "- Risk level (low/medium/high) "
                    "- Pros/cons (3+ each minimum) "
                    "- Implementation time (e.g., '3 days')"
                ),
                rationale="S3 showed incomplete alternatives confuse decision-making",
                impact="medium",
            )
        )

        # S4 Learning: CORTEX self-analysis integration
        enhancements.append(
            PromptEnhancement(
                type=EnhancementType.RULE,
                section="PRE-IMPLEMENTATION VALIDATION",
                current_text="Run HolisticValidationOrchestrator before IMPLEMENT",
                enhanced_text=(
                    "Run 3-part validation BEFORE ANY IMPLEMENT: "
                    "1. HolisticValidationOrchestrator (registry/wiring/dependencies/CORE rules) "
                    "2. CortexBrainIntegrationOrchestrator (architecture drift, internal packages, security) "
                    "3. ChallengeGateOrchestrator (alternatives with ROI scores) "
                    "Block if risk_score > 0.7 OR critical challenges OR security issues"
                ),
                rationale="S4 showed CORTEX self-analysis catches issues before cascading",
                impact="high",
            )
        )

        # S4 Learning: Security gate integration
        enhancements.append(
            PromptEnhancement(
                type=EnhancementType.RULE,
                section="SECURITY-FIRST MINDSET",
                current_text="Consider security for every request",
                enhanced_text=(
                    "MANDATORY SECURITY CHECKS (S4 derived): "
                    "1. Run SecurityGateAnalysis before IMPLEMENT (blocks if critical) "
                    "2. Check for hardcoded secrets, injection vulnerabilities, permission checks "
                    "3. Recommend internal security packages (cortex.config, cortex.common.serialization) "
                    "4. Verify compliance_status = 'compliant' before proceeding"
                ),
                rationale="S4 security analysis prevents vulnerability propagation into CORTEX",
                impact="high",
            )
        )

        # S4 Learning: Architecture drift monitoring
        enhancements.append(
            PromptEnhancement(
                type=EnhancementType.BEHAVIORAL_GUIDE,
                section="ARCHITECTURE INTEGRITY",
                current_text="Maintain CORTEX architecture consistency",
                enhanced_text=(
                    "CONTINUOUS ARCHITECTURE MONITORING (S4 derived): "
                    "1. Every 5 phases, run ArchitectureDriftDetection via cortex_brain "
                    "2. Detect: MCP-FIRST violations, tier coupling, circular dependencies, CORE rules drift "
                    "3. If drift_score > 0.3, trigger refactoring phase before continuing "
                    "4. Generate recommendations to maintain architecture integrity"
                ),
                rationale="S4 showed drift accumulates silently without monitoring",
                impact="medium",
            )
        )

        self.enhancements = enhancements
        return enhancements

    def identify_agent_enhancements(self) -> List[AgentEnhancement]:
        """Identify needed agent enhancements.

        Returns:
            List of agent enhancements.
        """
        enhancements = []

        # Challenge Gate Agent
        enhancements.append(
            AgentEnhancement(
                agent_name="ChallengeEngine",
                agent_file="agents/core/challenge_engine.yaml",
                enhancement=(
                    "Add behaviors: generate challenges from operation + target, "
                    "score alternatives by ROI (0.0-1.0), format for user display, "
                    "track user decision on alternative selection"
                ),
                rationale="S3 requires Challenge Engine for pre-implementation decisions",
                impact="high",
            )
        )

        # Validation Agent Enhancement
        enhancements.append(
            AgentEnhancement(
                agent_name="HolisticValidationAgent",
                agent_file="agents/core/holistic_validation_agent.yaml",
                enhancement=(
                    "Add capabilities: "
                    "1. Run HolisticValidationOrchestrator (registry/wiring/dependencies) "
                    "2. Run DependencyGraphGenerator (cycle detection, impact analysis) "
                    "3. Score regression risk (0.0-1.0) "
                    "4. Block if risk > 0.7"
                ),
                rationale="S1-S2 core validation logic needs agent implementation",
                impact="high",
            )
        )

        # CORTEX Self-Analysis Agent
        enhancements.append(
            AgentEnhancement(
                agent_name="CortexSelfAnalysisAgent",
                agent_file="agents/domain/cortex_self_analysis_agent.yaml",
                enhancement=(
                    "Add capabilities: "
                    "1. Run CortexBrainIntegrationOrchestrator (architecture, packages, security) "
                    "2. Detect architecture drift (violations, affected components) "
                    "3. Recommend internal package migrations "
                    "4. Generate security compliance report"
                ),
                rationale="S4 requires agent to perform CORTEX self-analysis",
                impact="high",
            )
        )

        # Security Gate Agent
        enhancements.append(
            AgentEnhancement(
                agent_name="SecurityCheckpointAgent",
                agent_file="agents/core/security_checkpoint_agent.yaml",
                enhancement=(
                    "Add behaviors: run SecurityGateAnalysis before IMPLEMENT, "
                    "detect secrets/injections/permission issues, "
                    "block if critical vulnerabilities, "
                    "recommend internal security packages"
                ),
                rationale="S4 security analysis needs agent integration",
                impact="high",
            )
        )

        self.agent_enhancements = enhancements
        return enhancements

    def generate_enhancement_report(self) -> PromptEnhancementReport:
        """Generate comprehensive enhancement report.

        Returns:
            PromptEnhancementReport with all findings.
        """
        prompt_enhancements = self.identify_enhancements()
        agent_enhancements = self.identify_agent_enhancements()

        # Calculate total impact
        impact_scores = {
            "low": 1,
            "medium": 2,
            "high": 3,
        }
        prompt_impacts = [
            impact_scores.get(e.impact, 0) for e in prompt_enhancements
        ]
        agent_impacts = [impact_scores.get(e.impact, 0) for e in agent_enhancements]

        avg_impact = (
            sum(prompt_impacts + agent_impacts) / len(prompt_impacts + agent_impacts)
            if prompt_impacts or agent_impacts
            else 0
        )

        if avg_impact >= 2.5:
            total_impact = "high"
        elif avg_impact >= 1.5:
            total_impact = "medium"
        else:
            total_impact = "low"

        recommendations = [
            "Apply prompt enhancements first (cortex-architect.prompt.md)",
            "Update agent YAML specifications after prompt changes",
            "Run full regression tests (515+) after enhancements",
            "Update documentation with Challenge Gate workflow",
            "Version bump: cortex-architect.prompt.md v15.4 → v15.5",
        ]

        return PromptEnhancementReport(
            timestamp="2026-02-08T00:00:00Z",
            phase="Phase 48 S5",
            prompt_enhancements=prompt_enhancements,
            agent_enhancements=agent_enhancements,
            total_impact=total_impact,
            recommendations=recommendations,
        )

    def format_enhancement_for_documentation(
        self, enhancement: PromptEnhancement
    ) -> str:
        """Format enhancement for documentation.

        Args:
            enhancement: Enhancement to format

        Returns:
            Formatted enhancement string.
        """
        lines = []
        lines.append(f"\n### {enhancement.type.value.title()}: {enhancement.section}")
        lines.append(f"\n**Rationale:** {enhancement.rationale}")
        lines.append(f"**Impact:** {enhancement.impact}")
        lines.append(f"\n**Current:**\n```\n{enhancement.current_text}\n```")
        lines.append(f"\n**Enhanced:**\n```\n{enhancement.enhanced_text}\n```")

        return "\n".join(lines)

    def format_report_for_documentation(
        self, report: PromptEnhancementReport
    ) -> str:
        """Format report for documentation.

        Args:
            report: Report to format

        Returns:
            Formatted report string.
        """
        lines = []
        lines.append(f"\n## 📋 Phase 48 S5: Prompt Enhancement Report")
        lines.append(f"\n**Total Impact:** {report.total_impact.upper()}")
        lines.append(f"**Prompt Enhancements:** {len(report.prompt_enhancements)}")
        lines.append(f"**Agent Enhancements:** {len(report.agent_enhancements)}")

        lines.append(f"\n### Prompt Enhancements")
        for enhancement in report.prompt_enhancements:
            lines.append(self.format_enhancement_for_documentation(enhancement))

        lines.append(f"\n### Agent Enhancements")
        for agent_enh in report.agent_enhancements:
            lines.append(f"\n#### {agent_enh.agent_name}")
            lines.append(f"File: `{agent_enh.agent_file}`")
            lines.append(f"**Enhancement:** {agent_enh.enhancement}")
            lines.append(f"**Rationale:** {agent_enh.rationale}")
            lines.append(f"**Impact:** {agent_enh.impact}")

        lines.append(f"\n### Recommendations")
        for i, rec in enumerate(report.recommendations, 1):
            lines.append(f"{i}. {rec}")

        return "\n".join(lines)
