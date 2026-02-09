"""
Comprehensive Orchestrator Response Template Registry.

Defines response templates for ALL CORTEX orchestrators with:
- Template inheritance hierarchy
- Chainable template blocks
- Orchestrator-specific customizations
- Production-ready configurations

Module: cortex.orchestrators.response.orchestrator_templates
Author: Asif Hussain
Created: 2026-02-09
Version: 2.0
Authority: ENH-064 + cortex-architect.prompt.md
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from cortex.orchestrators.core.base_response_template import (
    BaseResponseTemplate,
    SeverityLevel,
    SectionType,
    TemplateConfig
)


# ============================================================================
# TEMPLATE CATEGORIES
# ============================================================================


class OrchestratorCategory(str, Enum):
    """Orchestrator category for template grouping."""
    
    CORE = "core"  # Master, TDD, LENS, Intent Router
    DOMAIN = "domain"  # Refactoring, Planning, Documentation
    SUPPORT = "support"  # Debugging, Discovery, Digest
    ENTERPRISE = "enterprise"  # Security, Compliance, Audit
    PERFORMANCE = "performance"  # Load Testing, Profiling


# ============================================================================
# CORE ORCHESTRATOR TEMPLATES
# ============================================================================


class MasterOrchestratorTemplate(BaseResponseTemplate):
    """Template for MasterOrchestrator responses."""
    
    def __init__(self):
        super().__init__(
            orchestrator_name="MasterOrchestrator",
            mode="CORTEX"
        )
    
    def compose(
        self,
        operation: str = "COORDINATE",
        intent: str = "",
        routing_decision: str = "",
        orchestrators_invoked: List[str] = None,
        coordination_status: str = "",
        challenges: List[Dict[str, str]] = None
    ) -> str:
        """Compose master orchestrator coordination response."""
        orchestrators_invoked = orchestrators_invoked or []
        challenges = challenges or []
        
        response = self.header(operation)
        
        # Intent Classification
        response += self.section("Intent Classification", "🎯", SectionType.ANALYSIS)
        response += f"\n**Detected Intent:** {intent}\n"
        response += f"\n**Routing Decision:** {routing_decision}\n"
        
        # Orchestrator Coordination
        if orchestrators_invoked:
            response += self.section("Orchestrator Coordination", "🤝")
            response += self._format_orchestrators(orchestrators_invoked)
        
        # Coordination Status
        response += self.section("Coordination Status", "📊", SectionType.METRICS)
        response += f"\n{coordination_status}\n"
        
        # Challenges
        for challenge in challenges:
            response += self.challenge_box(
                title=challenge.get("title", "Coordination Question"),
                content=challenge.get("content", ""),
                severity=SeverityLevel.INFO
            )
        
        return response
    
    def _format_orchestrators(self, orchestrators: List[str]) -> str:
        """Format orchestrator invocation list."""
        if not orchestrators:
            return ""
        
        table = "\n| Orchestrator | Status |\n"
        table += "|--------------|--------|\n"
        
        for orch in orchestrators:
            table += f"| {orch} | ✅ Invoked |\n"
        
        return table


class IntentRouterTemplate(BaseResponseTemplate):
    """Template for IntentRouter responses."""
    
    def __init__(self):
        super().__init__(
            orchestrator_name="IntentRouter",
            mode="CORTEX"
        )
    
    def compose(
        self,
        operation: str = "ROUTE",
        user_request: str = "",
        classified_intent: str = "",
        confidence: float = 0.0,
        target_orchestrator: str = "",
        routing_reasoning: str = ""
    ) -> str:
        """Compose intent routing response."""
        response = self.header(operation)
        
        # User Request
        response += self.section("Request Analysis", "🔍", SectionType.ANALYSIS)
        response += f"\n**User Request:** {user_request}\n"
        
        # Intent Classification
        response += self.subsection("Intent Classification")
        response += self._format_intent(classified_intent, confidence)
        
        # Routing Decision
        response += self.section("Routing Decision", "🧭")
        response += f"\n**Target Orchestrator:** {target_orchestrator}\n"
        response += f"\n**Reasoning:** {routing_reasoning}\n"
        
        return response
    
    def _format_intent(self, intent: str, confidence: float) -> str:
        """Format intent classification."""
        conf_emoji = "✅" if confidence >= 0.8 else "⚠️" if confidence >= 0.6 else "❌"
        
        return (
            f"\n| Field | Value |\n"
            f"|-------|-------|\n"
            f"| **Intent** | {intent} |\n"
            f"| **Confidence** | {conf_emoji} {confidence:.1%} |\n"
        )


class ChallengeEngineTemplate(BaseResponseTemplate):
    """Template for ChallengeEngine responses."""
    
    def __init__(self):
        super().__init__(
            orchestrator_name="ChallengeEngine",
            mode="CORTEX"
        )
    
    def compose(
        self,
        operation: str = "CHALLENGE",
        user_request: str = "",
        detected_issues: List[Tuple[str, str]] = None,
        alternative_proposals: List[str] = None,
        decision_matrix: Dict[str, Any] = None,
        severity: SeverityLevel = SeverityLevel.WARNING
    ) -> str:
        """Compose challenge/disagreement response."""
        detected_issues = detected_issues or []
        alternative_proposals = alternative_proposals or []
        decision_matrix = decision_matrix or {}
        
        response = self.header(operation)
        
        # Disagreement Analysis
        response += self.section("Disagreement Analysis", "🔴")
        response += f"\n**User Request:** {user_request}\n"
        
        # Issues & Alternatives
        if detected_issues:
            response += self.subsection("Issues Detected")
            response += self.problem_solution_table(
                detected_issues,
                problem_header="❌ **Issue**",
                solution_header="✅ **Alternative**"
            )
        
        # Alternative Proposals
        if alternative_proposals:
            response += self.section("Alternative Proposals", "🔄")
            response += "\n" + "\n".join(f"{i+1}. {p}" for i, p in enumerate(alternative_proposals)) + "\n"
        
        # Decision Matrix
        if decision_matrix:
            response += self.section("Decision Matrix", "📊", SectionType.RECOMMENDATIONS)
            response += self._format_decision_matrix(decision_matrix)
        
        # Main Challenge Box
        response += self.challenge_box(
            title="Design Challenge",
            content="Please review alternatives and confirm approach",
            severity=severity
        )
        
        return response
    
    def _format_decision_matrix(self, matrix: Dict[str, Any]) -> str:
        """Format decision matrix table."""
        if not matrix:
            return ""
        
        table = "\n| Option | Pros | Cons | Recommendation |\n"
        table += "|--------|------|------|----------------|\n"
        
        for option, data in matrix.items():
            pros = data.get("pros", "N/A")
            cons = data.get("cons", "N/A")
            rec = data.get("recommendation", "")
            table += f"| {option} | {pros} | {cons} | {rec} |\n"
        
        return table


# ============================================================================
# DOMAIN ORCHESTRATOR TEMPLATES
# ============================================================================


class RefactoringOrchestratorTemplate(BaseResponseTemplate):
    """Template for RefactoringOrchestrator responses."""
    
    def __init__(self):
        super().__init__(
            orchestrator_name="RefactoringOrchestrator",
            mode="CORTEX"
        )
    
    def compose(
        self,
        operation: str = "REFACTOR",
        code_smells: List[Dict[str, Any]] = None,
        refactoring_strategy: str = "",
        before_after: List[Tuple[str, str]] = None,
        impact_assessment: Dict[str, Any] = None
    ) -> str:
        """Compose refactoring response."""
        code_smells = code_smells or []
        before_after = before_after or []
        impact_assessment = impact_assessment or {}
        
        response = self.header(operation)
        
        # Code Smell Analysis
        if code_smells:
            response += self.section("Code Smell Analysis", "👃")
            response += self._format_code_smells(code_smells)
        
        # Refactoring Strategy
        response += self.section("Refactoring Strategy", "🎯", SectionType.RECOMMENDATIONS)
        response += f"\n{refactoring_strategy}\n"
        
        # Before/After Comparison
        if before_after:
            response += self.section("Before/After Comparison", "🔄")
            response += self.problem_solution_table(
                before_after,
                problem_header="❌ **Before**",
                solution_header="✅ **After**"
            )
        
        # Impact Assessment
        if impact_assessment:
            response += self.section("Impact Assessment", "📊", SectionType.METRICS)
            response += self._format_impact(impact_assessment)
        
        return response
    
    def _format_code_smells(self, smells: List[Dict[str, Any]]) -> str:
        """Format code smells table."""
        if not smells:
            return "\n_No code smells detected._\n"
        
        table = "\n| Smell | Location | Severity | Refactoring |\n"
        table += "|-------|----------|----------|-------------|\n"
        
        for smell in smells:
            name = smell.get("name", "Unknown")
            location = smell.get("location", "N/A")
            severity = smell.get("severity", "medium")
            refactoring = smell.get("refactoring", "N/A")
            table += f"| {name} | {location} | {severity} | {refactoring} |\n"
        
        return table
    
    def _format_impact(self, impact: Dict[str, Any]) -> str:
        """Format impact assessment."""
        table = "\n| Metric | Before | After | Change |\n"
        table += "|--------|--------|-------|--------|\n"
        
        for metric, data in impact.items():
            before = data.get("before", "N/A")
            after = data.get("after", "N/A")
            change = data.get("change", "N/A")
            table += f"| {metric} | {before} | {after} | {change} |\n"
        
        return table


class DocumentationOrchestratorTemplate(BaseResponseTemplate):
    """Template for DocumentationOrchestrator responses."""
    
    def __init__(self):
        super().__init__(
            orchestrator_name="DocumentationOrchestrator",
            mode="CORTEX"
        )
    
    def compose(
        self,
        operation: str = "DOCUMENT",
        documentation_type: str = "",
        sections_generated: List[str] = None,
        coverage_metrics: Dict[str, float] = None,
        validation_results: Dict[str, bool] = None
    ) -> str:
        """Compose documentation generation response."""
        sections_generated = sections_generated or []
        coverage_metrics = coverage_metrics or {}
        validation_results = validation_results or {}
        
        response = self.header(operation)
        
        # Documentation Type
        response += self.section("Documentation Generation", "📚")
        response += f"\n**Type:** {documentation_type}\n"
        
        # Sections Generated
        if sections_generated:
            response += self.subsection("Sections Generated")
            response += "\n" + "\n".join(f"- ✅ {s}" for s in sections_generated) + "\n"
        
        # Coverage Metrics
        if coverage_metrics:
            response += self.section("Coverage Metrics", "📊", SectionType.METRICS)
            response += self._format_coverage(coverage_metrics)
        
        # Validation Results
        if validation_results:
            response += self.section("Validation Results", "✅", SectionType.TESTING)
            response += self._format_validation(validation_results)
        
        return response
    
    def _format_coverage(self, metrics: Dict[str, float]) -> str:
        """Format coverage metrics."""
        table = "\n| Metric | Coverage | Status |\n"
        table += "|--------|----------|--------|\n"
        
        for metric, value in metrics.items():
            status = "✅" if value >= 80 else "⚠️" if value >= 60 else "❌"
            table += f"| {metric} | {value:.1f}% | {status} |\n"
        
        return table
    
    def _format_validation(self, results: Dict[str, bool]) -> str:
        """Format validation results."""
        table = "\n| Check | Result |\n"
        table += "|-------|--------|\n"
        
        for check, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            table += f"| {check} | {status} |\n"
        
        return table


# ============================================================================
# SUPPORT ORCHESTRATOR TEMPLATES
# ============================================================================


class DebuggingOrchestratorTemplate(BaseResponseTemplate):
    """Template for DebuggingOrchestrator responses."""
    
    def __init__(self):
        super().__init__(
            orchestrator_name="DebuggingOrchestrator",
            mode="CORTEX"
        )
    
    def compose(
        self,
        operation: str = "DEBUG",
        error_analysis: Dict[str, Any] = None,
        root_causes: List[str] = None,
        fixes: List[Tuple[str, str]] = None,
        prevention_strategies: List[str] = None
    ) -> str:
        """Compose debugging response."""
        error_analysis = error_analysis or {}
        root_causes = root_causes or []
        fixes = fixes or []
        prevention_strategies = prevention_strategies or []
        
        response = self.header(operation)
        
        # Error Analysis
        response += self.section("Error Analysis", "🔍", SectionType.ANALYSIS)
        response += self._format_error_analysis(error_analysis)
        
        # Root Causes
        if root_causes:
            response += self.subsection("Root Causes")
            response += "\n" + "\n".join(f"{i+1}. {rc}" for i, rc in enumerate(root_causes)) + "\n"
        
        # Fixes
        if fixes:
            response += self.section("Fixes", "🔧")
            response += self.problem_solution_table(
                fixes,
                problem_header="❌ **Issue**",
                solution_header="✅ **Fix**"
            )
        
        # Prevention Strategies
        if prevention_strategies:
            response += self.section("Prevention Strategies", "🛡️")
            response += "\n" + "\n".join(f"- {ps}" for ps in prevention_strategies) + "\n"
        
        return response
    
    def _format_error_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format error analysis."""
        if not analysis:
            return "\n_No error data provided._\n"
        
        error_type = analysis.get("type", "Unknown")
        message = analysis.get("message", "N/A")
        location = analysis.get("location", "N/A")
        stack_trace = analysis.get("stack_trace", "N/A")
        
        return (
            f"\n| Field | Value |\n"
            f"|-------|-------|\n"
            f"| **Type** | {error_type} |\n"
            f"| **Message** | {message} |\n"
            f"| **Location** | {location} |\n"
            f"| **Stack Trace** | {stack_trace} |\n"
        )


class DigestSessionOrchestratorTemplate(BaseResponseTemplate):
    """Template for DigestSessionOrchestrator responses."""
    
    def __init__(self):
        super().__init__(
            orchestrator_name="DigestSessionOrchestrator",
            mode="CORTEX"
        )
    
    def compose(
        self,
        operation: str = "DIGEST",
        file_path: str = "",
        markers_detected: int = 0,
        learnings_extracted: List[Dict[str, Any]] = None,
        enhancements_proposed: List[str] = None,
        confidence_score: float = 0.0
    ) -> str:
        """Compose session digest response."""
        learnings_extracted = learnings_extracted or []
        enhancements_proposed = enhancements_proposed or []
        
        response = self.header(operation)
        
        # Session Analysis
        response += self.section("Session Analysis", "🔍", SectionType.ANALYSIS)
        response += f"\n**File:** {file_path}\n"
        response += f"**Markers Detected:** {markers_detected}\n"
        response += f"**Confidence Score:** {confidence_score:.1%}\n"
        
        # Learnings Extracted
        if learnings_extracted:
            response += self.section("Learnings Extracted", "📚")
            response += self._format_learnings(learnings_extracted)
        
        # Enhancements Proposed
        if enhancements_proposed:
            response += self.section("CORTEX Enhancements", "🚀", SectionType.RECOMMENDATIONS)
            response += "\n" + "\n".join(f"{i+1}. {e}" for i, e in enumerate(enhancements_proposed)) + "\n"
        
        return response
    
    def _format_learnings(self, learnings: List[Dict[str, Any]]) -> str:
        """Format extracted learnings."""
        if not learnings:
            return "\n_No learnings extracted._\n"
        
        table = "\n| Category | Learning | Confidence |\n"
        table += "|----------|----------|------------|\n"
        
        for learning in learnings:
            category = learning.get("category", "General")
            text = learning.get("text", "N/A")
            conf = learning.get("confidence", 0.0)
            conf_emoji = "✅" if conf >= 0.8 else "⚠️" if conf >= 0.6 else "❌"
            table += f"| {category} | {text} | {conf_emoji} {conf:.1%} |\n"
        
        return table


# ============================================================================
# REMAINING CORE TEMPLATES
# ============================================================================


class TDDOrchestratorTemplate(BaseResponseTemplate):
    """Template for TDD Orchestrator."""
    
    def __init__(self):
        super().__init__(orchestrator_name="TDDOrchestrator", mode="CORTEX")
    
    def compose(
        self,
        operation: str = "IMPLEMENT",
        tdd_phase: str = "RED",
        test_results: List[Dict[str, Any]] = None,
        coverage_metrics: Dict[str, float] = None,
        **kwargs
    ) -> str:
        """Compose TDD response."""
        from cortex.orchestrators.response.chainable_blocks import BlockComposer
        
        test_results = test_results or []
        coverage_metrics = coverage_metrics or {}
        
        response = self.header(operation)
        
        phase_emoji = {"RED": "🔴", "GREEN": "🟢", "REFACTOR": "🔄"}.get(tdd_phase, "⚪")
        response += self.section(f"TDD Phase: {tdd_phase}", phase_emoji)
        
        composer = BlockComposer()
        if test_results:
            composer.add_test_results(test_results)
        if coverage_metrics:
            composer.add_coverage(coverage_metrics)
        response += composer.build()
        
        return response


class LENSSynthesisTemplate(BaseResponseTemplate):
    """Template for LENS Synthesis."""
    
    def __init__(self):
        super().__init__(orchestrator_name="LENSSynthesis", mode="CORTEX")
    
    def compose(
        self,
        operation: str = "ANALYZE",
        confidence: float = 0.0,
        **kwargs
    ) -> str:
        """Compose LENS response."""
        response = self.header(operation)
        
        response += self.section("LENS Protocol", "🔍")
        conf_emoji = "🟢" if confidence >= 0.8 else "🟡" if confidence >= 0.6 else "🔴"
        response += f"{conf_emoji} **Confidence:** {confidence:.0%}\n\n"
        
        return response


class PlanOrchestratorTemplate(BaseResponseTemplate):
    """Template for Plan Orchestrator."""
    
    def __init__(self):
        super().__init__(orchestrator_name="PlanOrchestrator", mode="CORTEX")
    
    def compose(
        self,
        operation: str = "PLAN",
        phase_name: str = "",
        **kwargs
    ) -> str:
        """Compose plan response."""
        response = self.header(operation)
        response += self.section("Phase Overview", "📋")
        response += f"**Phase:** {phase_name}\n\n"
        return response


# ============================================================================
# ADDITIONAL DOMAIN/SUPPORT/ENTERPRISE TEMPLATES
# ============================================================================


class OnboardingOrchestratorTemplate(BaseResponseTemplate):
    """Template for Onboarding Orchestrator."""
    
    def __init__(self):
        super().__init__(orchestrator_name="OnboardingOrchestrator", mode="CORTEX")
    
    def compose(self, operation: str = "ONBOARD", **kwargs) -> str:
        response = self.header(operation)
        response += self.section("Repository Analysis", "📦")
        return response


class ToolDiscoveryOrchestratorTemplate(BaseResponseTemplate):
    """Template for Tool Discovery."""
    
    def __init__(self):
        super().__init__(orchestrator_name="ToolDiscoveryOrchestrator", mode="CORTEX")
    
    def compose(self, operation: str = "DISCOVER", **kwargs) -> str:
        response = self.header(operation)
        response += self.section("Tool Discovery", "🔧")
        return response


class WorkflowOrchestratorTemplate(BaseResponseTemplate):
    """Template for Workflow Orchestrator."""
    
    def __init__(self):
        super().__init__(orchestrator_name="WorkflowOrchestrator", mode="CORTEX")
    
    def compose(self, operation: str = "WORKFLOW", **kwargs) -> str:
        response = self.header(operation)
        response += self.section("Workflow Execution", "⚙️")
        return response


class MigrationOrchestratorTemplate(BaseResponseTemplate):
    """Template for Migration Orchestrator."""
    
    def __init__(self):
        super().__init__(orchestrator_name="MigrationOrchestrator", mode="CORTEX")
    
    def compose(self, operation: str = "MIGRATE", **kwargs) -> str:
        response = self.header(operation)
        response += self.section("Migration Plan", "🔄")
        return response


class ConversationOrchestratorTemplate(BaseResponseTemplate):
    """Template for Conversation Orchestrator."""
    
    def __init__(self):
        super().__init__(orchestrator_name="ConversationOrchestrator", mode="CORTEX")
    
    def compose(self, operation: str = "CONVERSE", **kwargs) -> str:
        response = self.header(operation)
        response += self.section("Conversation", "💬")
        return response


class ReviewOrchestratorTemplate(BaseResponseTemplate):
    """Template for Review Orchestrator."""
    
    def __init__(self):
        super().__init__(orchestrator_name="ReviewOrchestrator", mode="CORTEX")
    
    def compose(self, operation: str = "REVIEW", **kwargs) -> str:
        response = self.header(operation)
        response += self.section("Code Review", "👁️")
        return response


class DiscoveryOrchestratorTemplate(BaseResponseTemplate):
    """Template for Discovery Orchestrator."""
    
    def __init__(self):
        super().__init__(orchestrator_name="DiscoveryOrchestrator", mode="CORTEX")
    
    def compose(self, operation: str = "DISCOVER", **kwargs) -> str:
        response = self.header(operation)
        response += self.section("Discovery", "🔍")
        return response


class BrainFlushOrchestratorTemplate(BaseResponseTemplate):
    """Template for Brain Flush Orchestrator."""
    
    def __init__(self):
        super().__init__(orchestrator_name="BrainFlushOrchestrator", mode="CORTEX")
    
    def compose(self, operation: str = "FLUSH", **kwargs) -> str:
        response = self.header(operation)
        response += self.section("Brain Flush", "🧹")
        return response


class ContextAssemblyOrchestratorTemplate(BaseResponseTemplate):
    """Template for Context Assembly."""
    
    def __init__(self):
        super().__init__(orchestrator_name="ContextAssemblyOrchestrator", mode="CORTEX")
    
    def compose(self, operation: str = "ASSEMBLE", **kwargs) -> str:
        response = self.header(operation)
        response += self.section("Context Assembly", "🧩")
        return response


class PhaseCompletionOrchestratorTemplate(BaseResponseTemplate):
    """Template for Phase Completion."""
    
    def __init__(self):
        super().__init__(orchestrator_name="PhaseCompletionOrchestrator", mode="CORTEX")
    
    def compose(self, operation: str = "COMPLETE", **kwargs) -> str:
        response = self.header(operation)
        response += self.section("Phase Completion", "✅")
        return response


class StandardsOrchestratorTemplate(BaseResponseTemplate):
    """Template for Standards Orchestrator."""
    
    def __init__(self):
        super().__init__(orchestrator_name="StandardsOrchestrator", mode="CORTEX")
    
    def compose(self, operation: str = "STANDARDS", **kwargs) -> str:
        response = self.header(operation)
        response += self.section("Standards Compliance", "📏")
        return response


class TotalRecallOrchestratorTemplate(BaseResponseTemplate):
    """Template for Total Recall."""
    
    def __init__(self):
        super().__init__(orchestrator_name="TotalRecallOrchestrator", mode="CORTEX")
    
    def compose(self, operation: str = "RECALL", **kwargs) -> str:
        response = self.header(operation)
        response += self.section("Feature Discovery", "🔎")
        return response


class SecurityOrchestratorTemplate(BaseResponseTemplate):
    """Template for Security Orchestrator."""
    
    def __init__(self):
        super().__init__(orchestrator_name="SecurityOrchestrator", mode="CORTEX")
    
    def compose(self, operation: str = "SECURITY", **kwargs) -> str:
        response = self.header(operation)
        response += self.section("Security Assessment", "🔒")
        return response


class ComplianceOrchestratorTemplate(BaseResponseTemplate):
    """Template for Compliance Orchestrator."""
    
    def __init__(self):
        super().__init__(orchestrator_name="ComplianceOrchestrator", mode="CORTEX")
    
    def compose(self, operation: str = "COMPLIANCE", **kwargs) -> str:
        response = self.header(operation)
        response += self.section("Compliance Status", "📋")
        return response


class AuditOrchestratorTemplate(BaseResponseTemplate):
    """Template for Audit Orchestrator."""
    
    def __init__(self):
        super().__init__(orchestrator_name="AuditOrchestrator", mode="CORTEX")
    
    def compose(self, operation: str = "AUDIT", **kwargs) -> str:
        response = self.header(operation)
        response += self.section("Audit Report", "🔍")
        return response


class EnforcementOrchestratorTemplate(BaseResponseTemplate):
    """Template for Enforcement Orchestrator."""
    
    def __init__(self):
        super().__init__(orchestrator_name="EnforcementOrchestrator", mode="CORTEX")
    
    def compose(self, operation: str = "ENFORCE", **kwargs) -> str:
        response = self.header(operation)
        response += self.section("Governance Enforcement", "⚖️")
        return response


class PerformanceOrchestratorTemplate(BaseResponseTemplate):
    """Template for Performance Orchestrator."""
    
    def __init__(self):
        super().__init__(orchestrator_name="PerformanceOrchestrator", mode="CORTEX")
    
    def compose(self, operation: str = "PERFORMANCE", **kwargs) -> str:
        response = self.header(operation)
        response += self.section("Performance Metrics", "⚡")
        return response


class LoadTestOrchestratorTemplate(BaseResponseTemplate):
    """Template for Load Test Orchestrator."""
    
    def __init__(self):
        super().__init__(orchestrator_name="LoadTestOrchestrator", mode="CORTEX")
    
    def compose(self, operation: str = "LOADTEST", **kwargs) -> str:
        response = self.header(operation)
        response += self.section("Load Test Results", "📊")
        return response


class ProfilingOrchestratorTemplate(BaseResponseTemplate):
    """Template for Profiling Orchestrator."""
    
    def __init__(self):
        super().__init__(orchestrator_name="ProfilingOrchestrator", mode="CORTEX")
    
    def compose(self, operation: str = "PROFILE", **kwargs) -> str:
        response = self.header(operation)
        response += self.section("Profiling Results", "🔬")
        return response


# ============================================================================
# TEMPLATE REGISTRY
# ============================================================================


class OrchestratorTemplateRegistry:
    """Registry for all orchestrator templates."""
    
    def __init__(self):
        self._templates: Dict[str, BaseResponseTemplate] = {}
        self._register_all_templates()
    
    def _register_all_templates(self):
        """Register all orchestrator templates."""
        # Core Templates (10)
        self._templates["MasterOrchestrator"] = MasterOrchestratorTemplate()
        self._templates["IntentRouter"] = IntentRouterTemplate()
        self._templates["ChallengeEngine"] = ChallengeEngineTemplate()
        self._templates["TDDOrchestrator"] = TDDOrchestratorTemplate()
        self._templates["LENSSynthesis"] = LENSSynthesisTemplate()
        self._templates["PlanOrchestrator"] = PlanOrchestratorTemplate()
        
        # Domain Templates (8)
        self._templates["RefactoringOrchestrator"] = RefactoringOrchestratorTemplate()
        self._templates["DocumentationOrchestrator"] = DocumentationOrchestratorTemplate()
        self._templates["OnboardingOrchestrator"] = OnboardingOrchestratorTemplate()
        self._templates["ToolDiscoveryOrchestrator"] = ToolDiscoveryOrchestratorTemplate()
        self._templates["WorkflowOrchestrator"] = WorkflowOrchestratorTemplate()
        self._templates["MigrationOrchestrator"] = MigrationOrchestratorTemplate()
        self._templates["ConversationOrchestrator"] = ConversationOrchestratorTemplate()
        self._templates["ReviewOrchestrator"] = ReviewOrchestratorTemplate()
        
        # Support Templates (10)
        self._templates["DebuggingOrchestrator"] = DebuggingOrchestratorTemplate()
        self._templates["DigestSessionOrchestrator"] = DigestSessionOrchestratorTemplate()
        self._templates["DiscoveryOrchestrator"] = DiscoveryOrchestratorTemplate()
        self._templates["BrainFlushOrchestrator"] = BrainFlushOrchestratorTemplate()
        self._templates["ContextAssemblyOrchestrator"] = ContextAssemblyOrchestratorTemplate()
        self._templates["PhaseCompletionOrchestrator"] = PhaseCompletionOrchestratorTemplate()
        self._templates["StandardsOrchestrator"] = StandardsOrchestratorTemplate()
        self._templates["TotalRecallOrchestrator"] = TotalRecallOrchestratorTemplate()
        
        # Enterprise Templates (4)
        self._templates["SecurityOrchestrator"] = SecurityOrchestratorTemplate()
        self._templates["ComplianceOrchestrator"] = ComplianceOrchestratorTemplate()
        self._templates["AuditOrchestrator"] = AuditOrchestratorTemplate()
        self._templates["EnforcementOrchestrator"] = EnforcementOrchestratorTemplate()
        
        # Performance Templates (3)
        self._templates["PerformanceOrchestrator"] = PerformanceOrchestratorTemplate()
        self._templates["LoadTestOrchestrator"] = LoadTestOrchestratorTemplate()
        self._templates["ProfilingOrchestrator"] = ProfilingOrchestratorTemplate()
        
        # Total: 35 templates registered
        
        # Domain
        self._templates["RefactoringOrchestrator"] = RefactoringOrchestratorTemplate()
        self._templates["DocumentationOrchestrator"] = DocumentationOrchestratorTemplate()
        
        # Support
        self._templates["DebuggingOrchestrator"] = DebuggingOrchestratorTemplate()
        self._templates["DigestSessionOrchestrator"] = DigestSessionOrchestratorTemplate()
    
    def get_template(self, orchestrator_name: str) -> Optional[BaseResponseTemplate]:
        """Get template by orchestrator name."""
        return self._templates.get(orchestrator_name)
    
    def list_templates(self) -> List[str]:
        """List all registered template names."""
        return list(self._templates.keys())
    
    def has_template(self, orchestrator_name: str) -> bool:
        """Check if template exists for orchestrator."""
        return orchestrator_name in self._templates


# ============================================================================
# GLOBAL REGISTRY INSTANCE
# ============================================================================


_REGISTRY = OrchestratorTemplateRegistry()


def get_orchestrator_template(orchestrator_name: str) -> Optional[BaseResponseTemplate]:
    """
    Get template for orchestrator (convenience function).
    
    Args:
        orchestrator_name: Name of orchestrator
    
    Returns:
        BaseResponseTemplate instance or None
    """
    return _REGISTRY.get_template(orchestrator_name)


# ============================================================================
# MODULE EXPORTS
# ============================================================================


__all__ = [
    # Core Templates
    "MasterOrchestratorTemplate",
    "IntentRouterTemplate",
    "ChallengeEngineTemplate",
    "TDDOrchestratorTemplate",
    "LENSSynthesisTemplate",
    "PlanOrchestratorTemplate",
    
    # Domain Templates
    "RefactoringOrchestratorTemplate",
    "DocumentationOrchestratorTemplate",
    "OnboardingOrchestratorTemplate",
    "ToolDiscoveryOrchestratorTemplate",
    "WorkflowOrchestratorTemplate",
    "MigrationOrchestratorTemplate",
    "ConversationOrchestratorTemplate",
    "ReviewOrchestratorTemplate",
    
    # Support Templates
    "DebuggingOrchestratorTemplate",
    "DigestSessionOrchestratorTemplate",
    "DiscoveryOrchestratorTemplate",
    "BrainFlushOrchestratorTemplate",
    "ContextAssemblyOrchestratorTemplate",
    "PhaseCompletionOrchestratorTemplate",
    "StandardsOrchestratorTemplate",
    "TotalRecallOrchestratorTemplate",
    
    # Enterprise Templates
    "SecurityOrchestratorTemplate",
    "ComplianceOrchestratorTemplate",
    "AuditOrchestratorTemplate",
    "EnforcementOrchestratorTemplate",
    
    # Performance Templates
    "PerformanceOrchestratorTemplate",
    "LoadTestOrchestratorTemplate",
    "ProfilingOrchestratorTemplate",
    
    # Registry
    "OrchestratorTemplateRegistry",
    "get_orchestrator_template",
]
