"""
EnforcementOrchestrator — thin coordinator extracted from the 1,866-line monolith.

Phase 103-e god-object decomposition: the 11 agent classes now live in
enforcement_orchestrator/agents/; this file contains only the orchestrator
itself, singleton accessor, and the re-exported __all__.

AC-ID: AC-P103E-ORCH-001
Author: Asif Hussain
"""

from __future__ import annotations

import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

from cortex.core.result import Err, Ok, Result
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin  # Phase 90c
from cortex.orchestrators.core.governance_registry import GovernanceRegistry
from cortex.intelligence.learning.opj_mixin import OPJMixin  # Phase 52: OPJ intelligence
from cortex.intelligence.learning.reinforcement_signal import SignalType  # Phase 83-d: URS

from cortex.orchestrators.core.enforcement_orchestrator.models import (
    EnforcementLevel,
    EnforcementResult,
)
from cortex.orchestrators.core.enforcement_orchestrator.agents import (
    GovernanceEnforcementAgent,
    SecurityCheckpointAgent,
    ComplianceValidationAgent,
    FileNamingEnforcementAgent,
    IncrementalExecutionAgent,
    MarkdownSuppressionAgent,
    ResponseContentValidationAgent,
    ArchitectureIntegrityAgent,
    DiscoveryEnforcementAgent,
    ExtendedGovernanceAgent,
    SweepCompositionEnforcementAgent,
)

# Phase 58-C: DomainBrain + Memory wiring (decision-making orchestrator)
try:
    from cortex.intelligence.domain_brain import DomainBrainAPI as _EnfDomainBrainAPI  # type: ignore[attr-defined]
except Exception:
    _EnfDomainBrainAPI = None  # type: ignore[assignment,misc]

try:
    from cortex.intelligence.memory.tier2_adaptive.hallucination_prevention import (  # type: ignore[import]
        BehavioralBoundaryRules as _EnfBehavioralBoundaryRules,
    )
except Exception:
    _EnfBehavioralBoundaryRules = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

# Import telemetry (Phase 4)
try:
    from cortex.governance.telemetry import get_telemetry
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False
    logger.warning("Governance telemetry not available (cortex.governance.telemetry)")


class EnforcementOrchestrator(OPJMixin, OrchestratorProtocolMixin, WorkflowEnforcementMixin, WorkflowTemplateMixin):
    """
    Pre-execution governance enforcement orchestrator with 11-agent system.

    Validates operations against 3-tier governance before execution:
    - Executes 11 agents in parallel for speed (<150ms target)
    - Aggregates violations and warnings
    - Blocks execution on Tier 0 violations
    - Escalates Tier 1 warnings without blocking

    Agent Architecture (11 agents):
    1. GovernanceEnforcementAgent: CORE-008, 011, 012, 013, 029, 030
    2. SecurityCheckpointAgent: CORE-025, 026, 027
    3. ComplianceValidationAgent: Tier 1 rules
    4. FileNamingEnforcementAgent: CORE-028
    5. IncrementalExecutionAgent: CORE-001, 004
    6. MarkdownSuppressionAgent: CORE-002
    7. ArchitectureIntegrityAgent: CORE-017-020, 032, 034, 035, 038-041
    8. DiscoveryEnforcementAgent: CORE-030, 035 (ENH-047)
    9. ResponseContentValidationAgent: CORE-002-RESPONSE
    10. ExtendedGovernanceAgent: CORE-058..063 (GAP-008)
    11. SweepCompositionEnforcementAgent: CORE-064 (Phase 56)

    Coverage: 35/35 CORE rules automated (100%)
    """

    # Phase 90c — must remain False: EnforcementOrchestrator IS the governance gate.
    PHASE90_GATEWAY_EXEMPT: bool = True

    def __init__(self, governance_registry: Optional[GovernanceRegistry] = None) -> None:
        """
        Initialize enforcement orchestrator with 11-agent system.

        Args:
            governance_registry: Optional governance registry (injected)
        """
        self.governance_registry = governance_registry
        self.agents = [
            GovernanceEnforcementAgent(),
            SecurityCheckpointAgent(),
            ComplianceValidationAgent(),
            FileNamingEnforcementAgent(),
            IncrementalExecutionAgent(),
            MarkdownSuppressionAgent(),
            ArchitectureIntegrityAgent(),
            DiscoveryEnforcementAgent(),
            ResponseContentValidationAgent(),
            ExtendedGovernanceAgent(),
            SweepCompositionEnforcementAgent(),
        ]
        logger.info(f"EnforcementOrchestrator initialized with {len(self.agents)} agents (35/35 CORE rules)")

    def get_recommended_template(self) -> str:
        """Get the recommended workflow template for enforcement operations."""
        return "security/compliance-audit"

    def _inject_governance_knowledge(self) -> Dict[str, Any]:
        """Inject governance knowledge YAMLs into enforcement context.

        Phase 78 GAP-78-A-04: Wire cortex-registry/governance/*.yaml
        so rule validation is knowledge-informed (not just hard-coded rule IDs).

        Returns:
            Dict with governance knowledge from development-rules, compliance-rules,
            operations-rules, data-rules, security-rules YAMLs.
        """
        try:
            from cortex.intelligence.facade import get_intelligence_facade
            facade = get_intelligence_facade()
            return facade.synthesize(query="governance:enforcement")
        except Exception:
            return {}

    def _load_governance_knowledge(self) -> Dict[str, Any]:
        """Load governance knowledge from canonical knowledge-base YAMLs.

        Phase 78 GAP-78-A-04: Convenience wrapper.

        Returns:
            Merged dict of all governance knowledge YAML contents.
        """
        return self._inject_governance_knowledge()

    def validate_operation(self, operation: Dict[str, Any]) -> Result[EnforcementResult, EnforcementResult]:
        """
        Validate operation against governance rules using 11-agent system.

        Args:
            operation: Operation context with intent, target_file, test_file, etc.

        Returns:
            Ok(EnforcementResult) if compliant or warnings only
            Err(EnforcementResult) if Tier 0 violations detected
        """
        start_time = time.time()
        all_violations: List[str] = []
        all_warnings: List[str] = []

        # Phase 58 — cross-cutting hooks: LENS + KnSynth only (GovGate skipped — this IS the gate)
        lens_ctx = self._extract_lens_context(operation.get("orchestrator_context"))
        self._consume_unified_context(operation.get("unified_context"))

        telemetry = get_telemetry() if TELEMETRY_AVAILABLE else None
        intent = operation.get("intent", "UNKNOWN")

        with ThreadPoolExecutor(max_workers=7) as executor:
            futures = {executor.submit(agent.validate, operation): agent for agent in self.agents}

            for future in as_completed(futures):
                agent = futures[future]
                agent_start_time = time.time()

                try:
                    result = future.result()
                    agent_name = result.metadata.get("agent", agent.__class__.__name__)
                    agent_latency_ms = (time.time() - agent_start_time) * 1000

                    if telemetry:
                        telemetry.record_agent_invocation(
                            agent_name=agent_name,
                            intent=intent,
                            result=result.level.value,
                            latency_ms=agent_latency_ms,
                            violations_count=len(result.violations),
                            warnings_count=len(result.warnings),
                        )

                    if result.violations:
                        all_violations.extend(result.violations)
                        logger.warning(f"{agent_name} detected {len(result.violations)} violations")

                        if telemetry:
                            for violation in result.violations:
                                rule_id = "UNKNOWN"
                                if "CORE-" in violation:
                                    match = re.search(r'CORE-\d+', violation)
                                    if match:
                                        rule_id = match.group(0)
                                telemetry.record_violation(
                                    rule_id=rule_id,
                                    violation_message=violation,
                                    agent_name=agent_name,
                                )

                    if result.warnings:
                        all_warnings.extend(result.warnings)
                        logger.info(f"{agent_name} issued {len(result.warnings)} warnings")

                        if telemetry:
                            for warning in result.warnings:
                                rule_id = "UNKNOWN"
                                if "CORE-" in warning or "TIER-" in warning:
                                    match = re.search(r'(CORE|TIER)-\d+', warning)
                                    if match:
                                        rule_id = match.group(0)
                                telemetry.record_warning(
                                    rule_id=rule_id,
                                    warning_message=warning,
                                    agent_name=agent_name,
                                )

                except Exception as e:
                    agent_name = agent.__class__.__name__
                    logger.error(f"{agent_name} validation failed: {e}")
                    all_warnings.append(f"Agent {agent_name} validation error: {str(e)}")

        execution_time_ms = (time.time() - start_time) * 1000

        if all_violations:
            enforcement_result = EnforcementResult(
                level=EnforcementLevel.BLOCKED,
                violations=all_violations,
                warnings=all_warnings,
                metadata={
                    "agent_count": len(self.agents),
                    "execution_time_ms": round(execution_time_ms, 2),
                    "blocked": True,
                },
            )
            self._opj_record_failure(
                operation="validate_operation",
                error=f"{len(all_violations)} governance violation(s): {'; '.join(all_violations[:2])}",
                attempted_fix="see violation details",
                confidence=0.9,
                avoid_in_future=f"Ensure operation satisfies: {'; '.join(all_violations[:2])}",
            )
            return Err(enforcement_result)

        level = EnforcementLevel.WARNING if all_warnings else EnforcementLevel.PASS
        enforcement_result = EnforcementResult(
            level=level,
            violations=[],
            warnings=all_warnings,
            metadata={
                "agent_count": len(self.agents),
                "execution_time_ms": round(execution_time_ms, 2),
                "blocked": False,
            },
        )
        self._opj_record_success(
            operation="validate_operation",
            context={"intent": str(intent)[:200], "agent_count": len(self.agents)},
            resolution=f"All {len(self.agents)} agents passed in {round(execution_time_ms, 1)}ms",
            confidence=0.85,
        )
        return Ok(enforcement_result)

    def _format_governance_rule_with_book(self, rule_id: str) -> str:
        """
        Format governance rule with book reference for inline display.

        Args:
            rule_id: CORE rule ID (e.g., "CORE-008")

        Returns:
            Formatted string with book reference, falls back to rule_id.

        AC-ID: AC-PHASE-06-S2-001
        """
        try:
            from cortex.orchestrators.core.business_wisdom_formatter import BusinessWisdomFormatter

            formatter = BusinessWisdomFormatter()
            markdown = formatter.format_governance_with_books(
                rule_ids=[rule_id],
                max_display=1,
                include_icon=False,
            )

            if markdown:
                lines = markdown.split("\n")
                for line in lines:
                    if line.startswith("- "):
                        return line[2:].strip()

            return rule_id

        except Exception as e:
            logger.warning(f"Failed to format rule {rule_id} with book reference: {e}")
            return rule_id

    def validate_response_content(
        self, response_text: str, allow_markdown: bool = False
    ) -> Result[EnforcementResult, EnforcementResult]:
        """
        Validate response content for markdown file suggestions (CORE-002-RESPONSE).

        Args:
            response_text: The response being sent to Copilot Chat
            allow_markdown: Override to allow markdown suggestions (default False)

        Returns:
            Ok(result) if no violations, Err(result) if CORE-002-RESPONSE violated
        """
        start_time = time.time()

        agent = ResponseContentValidationAgent()
        validation_result = agent.validate({
            "response_text": response_text,
            "allow_markdown_suggestions": allow_markdown,
        })

        execution_time_ms = (time.time() - start_time) * 1000
        validation_result.metadata["execution_time_ms"] = round(execution_time_ms, 2)

        if validation_result.is_blocked():
            logger.warning(
                f"Response contains markdown file suggestions: "
                f"{len(validation_result.violations)} violations"
            )
            return Err(validation_result)

        logger.debug(f"Response content validation passed in {execution_time_ms:.2f}ms")
        return Ok(validation_result)

    def transform_response_to_inline(self, response_text: str) -> str:
        """
        Transform response that suggests file creation to inline-only alternatives.

        Args:
            response_text: Original response

        Returns:
            Transformed response suggesting inline display
        """
        return ResponseContentValidationAgent.transform_response_to_inline(response_text)

    def validate_intent_classification(
        self, intent_reflection: Dict[str, Any]
    ) -> Result[List[str], List[str]]:
        """
        Validate intent classification integrity (Layer 1: Pre-Execution Gate).

        Args:
            intent_reflection: IntentReflection dict with DoR fields

        Returns:
            Ok([]) if valid, Err([violations]) if invalid

        AC-ID: REM-003-01
        """
        violations: List[str] = []

        required_fields = ["intent_type", "target_handler", "dor_confidence", "scope"]
        for field in required_fields:
            if not intent_reflection.get(field):
                violations.append(
                    f"Intent classification incomplete: missing '{field}' field"
                )

        governance_rules = intent_reflection.get("governance_rules", [])
        business_principles = intent_reflection.get("business_principles", {})

        if governance_rules and not business_principles:
            violations.append(
                "Intent classification integrity violation: "
                "governance_rules present but business_principles not populated"
            )

        dor_confidence = intent_reflection.get("dor_confidence", 0)
        if not (0.0 <= dor_confidence <= 1.0):
            violations.append(
                f"DoR confidence out of range: {dor_confidence} (must be 0.0-1.0)"
            )

        if violations:
            return Err(violations)
        return Ok([])

    def validate_dor_confidence(
        self,
        promised_confidence: float,
        intent_type: str,
        available_context: Dict[str, Any],
    ) -> Result[List[str], List[str]]:
        """
        Validate DoR confidence is not artificially inflated (Layer 1).

        Args:
            promised_confidence: DoR confidence from intent classification
            intent_type: Type of intent (IMPLEMENT, FIX, etc.)
            available_context: Context used for confidence calculation

        Returns:
            Ok([]) if confidence justified, Err([violations]) if suspicious

        AC-ID: REM-003-01
        """
        violations: List[str] = []
        context_score = 0.0

        if available_context.get("target_file_exists"):
            context_score += 0.2
        if available_context.get("test_file_exists"):
            context_score += 0.2
        if available_context.get("similar_patterns_found"):
            context_score += 0.2
        if available_context.get("clear_requirements"):
            context_score += 0.2
        if available_context.get("dependencies_known"):
            context_score += 0.2

        if promised_confidence > (context_score + 0.3):
            violations.append(
                f"DoR confidence suspiciously high: {promised_confidence:.0%} "
                f"with only {context_score:.0%} context quality "
                f"(maximum justified: {(context_score + 0.3):.0%})"
            )

        min_confidence = {
            "IMPLEMENT": 0.60,
            "FIX": 0.50,
            "REFACTOR": 0.70,
            "ANALYZE": 0.40,
        }.get(intent_type, 0.50)

        if promised_confidence < min_confidence:
            violations.append(
                f"DoR confidence too low for {intent_type}: {promised_confidence:.0%} "
                f"(minimum: {min_confidence:.0%})"
            )

        if violations:
            return Err(violations)
        return Ok([])

    def validate_business_principles_mapping(
        self,
        governance_rules: List[str],
        business_principles: Dict[str, str],
    ) -> Result[List[str], List[str]]:
        """
        Validate governance rules correctly mapped to business principles (Layer 1).

        Args:
            governance_rules: List of CORE-XXX rule IDs
            business_principles: Dict of {principle_name: technical_term}

        Returns:
            Ok([]) if mapping valid, Err([violations]) if incorrect

        AC-ID: REM-003-01
        """
        violations: List[str] = []

        if not governance_rules:
            return Ok([])

        if not business_principles:
            violations.append(
                f"Business principles mapping missing: "
                f"{len(governance_rules)} governance rules require explanation"
            )
            return Err(violations)

        rules_mentioned: List[str] = []
        for principle, technical in business_principles.items():
            if "CORE-" in technical:
                rules_mentioned.append(
                    technical.split("(")[1].split(")")[0] if "(" in technical else ""
                )

        unmapped_rules = [rule for rule in governance_rules if rule not in rules_mentioned]

        if unmapped_rules:
            violations.append(
                f"Governance rules not mapped to business principles: {', '.join(unmapped_rules)}"
            )

        if violations:
            return Err(violations)
        return Ok([])

    # ── Phase 83-d: URS signal emission ─────────────────────────────────────

    def _emit_enforcement_signal(
        self,
        operation: str,
        violations: List[str],
        warnings: List[str],
    ) -> None:
        """Emit a reinforcement signal after governance validation.

        Args:
            operation: The enforcement operation that completed.
            violations: List of violation messages.
            warnings: List of warning messages.
        """
        if violations:
            signal = SignalType.MILD_PUNISHMENT
        elif warnings:
            signal = SignalType.MILD_REWARD
        else:
            signal = SignalType.STRONG_REWARD

        self._urs_emit_signal(
            signal_type=signal,
            pattern_id=operation,
            context={
                "violation_count": len(violations),
                "warning_count": len(warnings),
            },
        )

    def get_capabilities(self) -> List[str]:
        """
        Get enforcement orchestrator capabilities.

        Returns:
            List of capability strings
        """
        return [
            "governance_enforcement",
            "rule_validation",
            "pre_execution_gate",
            "tier_0_blocking",
            "tier_1_escalation",
            "intent_classification_validation",
            "dor_confidence_validation",
            "business_principles_mapping_validation",
        ]


# ============================================================================
# SINGLETON ACCESS
# ============================================================================

_enforcement_orchestrator_instance: Optional[EnforcementOrchestrator] = None


def get_enforcement_orchestrator() -> EnforcementOrchestrator:
    """
    Get singleton enforcement orchestrator instance.

    Returns:
        EnforcementOrchestrator instance
    """
    global _enforcement_orchestrator_instance

    if _enforcement_orchestrator_instance is None:
        _enforcement_orchestrator_instance = EnforcementOrchestrator()

    return _enforcement_orchestrator_instance
