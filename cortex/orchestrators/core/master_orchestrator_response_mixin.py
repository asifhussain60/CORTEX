"""
MasterOrchestratorResponseMixin — Response formatting and violation filtering.

Extracted from cortex/orchestrators/core/master_orchestrator.py (Phase 103-a, GAP-103-01).
Single Responsibility: Format responses with CORTEX headers and policy pipeline.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from cortex.intelligence.knowledge.unified_intelligence_context import UnifiedIntelligenceContext

_log = logging.getLogger(__name__)

# Phase 33/34 optional imports (graceful degradation)
ChatResponsePolicyValidator = None  # type: ignore[assignment]
suppress_verbosity = None  # type: ignore[assignment]
inject_plan_spine = None  # type: ignore[assignment]
SemanticDeduplicator = None  # type: ignore[assignment]
ResponseQualityScorer = None  # type: ignore[assignment]
RoleVerbosityProfiles = None  # type: ignore[assignment]
Role = None  # type: ignore[assignment]
PHASE_34_AVAILABLE = False

try:
    from cortex.orchestrators.response.chat_response_policy import (  # type: ignore[import]
        ChatResponsePolicyValidator,
        suppress_verbosity,
        inject_plan_spine,
    )
except ImportError:  # optional dependency — Phase 116-b GAP-116-04
    _log.warning("Optional dependency unavailable: cortex.orchestrators.response.chat_response_policy")

try:
    from cortex.orchestrators.response.advanced_optimization import (  # type: ignore[import]
        SemanticDeduplicator,
        ResponseQualityScorer,
        RoleVerbosityProfiles,
        Role,
    )
    PHASE_34_AVAILABLE = True
except ImportError:  # optional dependency — Phase 116-b GAP-116-04
    _log.warning("Optional dependency unavailable: cortex.orchestrators.response.advanced_optimization")


class MasterOrchestratorResponseMixin:
    """Mixin providing response formatting to MasterOrchestrator.

    Handles:
    - get_response_with_headers (policy pipeline + header injection)
    - _filter_critical_violations
    - _format_violation_summary
    """

    def _filter_critical_violations(self, violations: List[str]) -> List[str]:
        """
        Filter violations to identify critical ones that should block execution.

        Phase 20.5 Component #5: Early Violation Prevention

        Critical violations are those that:
        - Violate mandatory CORE rules (CORE-008, CORE-011, CORE-013)
        - Could cause production failures
        - Represent security issues

        Args:
            violations: List of all detected violations

        Returns:
            List[str]: Critical violations that warrant blocking execution

        Authority: AC-KNOWLEDGE-SYNTHESIS-001 (Phase 20.5)
        """
        critical_patterns = [
            "CORE-008",  # TDD required
            "CORE-013",  # No bare except
            "security",
            "authentication",
            "authorization",
            "injection",
            "production",
            "critical",
            "unsafe",
        ]

        critical = []
        for violation in violations:
            violation_lower = violation.lower()
            if any(pattern.lower() in violation_lower for pattern in critical_patterns):
                critical.append(violation)

        return critical

    def _format_violation_summary(
        self,
        critical_violations: List[str],
        unified_intelligence: "UnifiedIntelligenceContext"
    ) -> str:
        """
        Format violation summary with remediation guidance.

        Phase 20.5 Component #5: Early Violation Prevention

        Args:
            critical_violations: List of critical violations
            unified_intelligence: Full unified intelligence context

        Returns:
            str: Formatted violation summary with remediation steps

        Authority: AC-KNOWLEDGE-SYNTHESIS-001 (Phase 20.5)
        """
        lines = [
            "🛑 EXECUTION BLOCKED - Critical CORE Rule Violations Detected",
            "",
            f"Found {len(critical_violations)} critical violation(s):",
            ""
        ]

        for i, violation in enumerate(critical_violations, 1):
            lines.append(f"{i}. {violation}")

        # Add guidance if available
        guidance = unified_intelligence.get_guidance()
        if guidance:
            lines.append("")
            lines.append("📋 Remediation Guidance:")
            lines.append("")
            for i, guide in enumerate(guidance[:5], 1):  # Top 5 guidance items
                lines.append(f"{i}. {guide}")

        # Add cited rules
        cited_rules = unified_intelligence.get_cited_rules()
        if cited_rules:
            lines.append("")
            lines.append("📖 Relevant CORE Rules:")
            lines.append("")
            for rule in cited_rules[:5]:  # Top 5 rules
                lines.append(f"  - {rule}")

        lines.append("")
        lines.append("Please address these violations before proceeding.")

        return "\n".join(lines)

    def get_response_with_headers(self, response: str) -> str:
        """
        Wrap response with CORTEX headers and apply optimization policies.

        AC-ENH-002-01: Integrate ResponseHeaderInjector into MasterOrchestrator
        Phase 33: Apply ChatResponsePolicy for verbosity suppression
        Phase 34: Apply advanced response optimization (semantic dedup, quality scoring, role profiles)

        Policy pipeline:
        1. suppress_verbosity() - remove narration patterns (Phase 33)
        2. inject_plan_spine() - add progress indicator if phases available (Phase 33)
        3. semantic_deduplication() - remove redundant sentences (Phase 34)
        4. quality_scoring() - evaluate response quality (Phase 34)
        5. role_profile_application() - apply role-based formatting (Phase 34)
        6. ChatResponsePolicyValidator - validate 3-section structure (Phase 33)
        7. MarkdownReportBanPolicy - ensure no report files (Phase 33)
        8. Wrap with headers via ResponseHeaderInjector

        Applies header injection if injector is available, otherwise returns
        response unchanged (graceful degradation).

        Args:
            response: Response text to wrap

        Returns:
            Response wrapped with CORTEX headers and policies applied
        """
        try:
            # Phase 33: Apply response verbosity reduction policies
            # Step 1: Suppress narration patterns
            if suppress_verbosity is not None:
                response = suppress_verbosity(response)
                self.logger.log_operation_complete(
                    ac_id="AC-PHASE-33-001",
                    operation="SUPPRESS_VERBOSITY",
                    success=True,
                    details={"original_length": len(response)}
                )

            # Step 2: Inject plan spine if phases available
            if inject_plan_spine is not None and self.current_phase:
                try:
                    phases = [(self.current_phase, "active")]
                    response = inject_plan_spine(response, phases, section_index=1)
                    self.logger.log_operation_complete(
                        ac_id="AC-PHASE-33-002",
                        operation="INJECT_PLAN_SPINE",
                        success=True
                    )
                except Exception as spine_err:
                    self.logger.log_operation_complete(
                        ac_id="AC-PHASE-33-002",
                        operation="INJECT_PLAN_SPINE",
                        success=False,
                        details={"error": str(spine_err)}
                    )

            # Phase 34: Advanced response optimization
            if PHASE_34_AVAILABLE:
                try:
                    original_length = len(response)

                    # Step 3: Semantic deduplication
                    if SemanticDeduplicator is not None:
                        try:
                            deduplicator = SemanticDeduplicator(similarity_threshold=0.85)
                            response = deduplicator.deduplicate(response)
                            metrics = deduplicator.get_metrics()
                            self.logger.log_operation_complete(
                                ac_id="AC-PHASE-34-001",
                                operation="SEMANTIC_DEDUPLICATION",
                                success=True,
                                details={
                                    "original_length": original_length,
                                    "deduplicated_length": len(response),
                                    "reduction_rate": metrics.get("reduction_rate", 0),
                                }
                            )
                        except Exception as dedup_err:
                            self.logger.log_operation_complete(
                                ac_id="AC-PHASE-34-001",
                                operation="SEMANTIC_DEDUPLICATION",
                                success=False,
                                details={"error": str(dedup_err)}
                            )

                    # Step 4: Quality scoring (monitoring only, not modifying)
                    if ResponseQualityScorer is not None:
                        try:
                            scorer = ResponseQualityScorer()
                            context = self.current_operation or "general"
                            score = scorer.score_response(response, context)
                            self.logger.log_operation_complete(
                                ac_id="AC-PHASE-34-002",
                                operation="QUALITY_SCORING",
                                success=True,
                                details={
                                    "overall_score": score.overall,
                                    "clarity": score.clarity,
                                    "completeness": score.completeness,
                                    "conciseness": score.conciseness,
                                    "accuracy": score.accuracy,
                                    "relevance": score.relevance,
                                }
                            )
                        except Exception as score_err:
                            self.logger.log_operation_complete(
                                ac_id="AC-PHASE-34-002",
                                operation="QUALITY_SCORING",
                                success=False,
                                details={"error": str(score_err)}
                            )

                    # Step 5: Role profile application (default to ENGINEER for now)
                    if RoleVerbosityProfiles is not None and Role is not None:
                        try:
                            profiles = RoleVerbosityProfiles()
                            # Default to ENGINEER role (high detail, code preserved)
                            # Future: detect role from context or user preferences
                            role = Role.ENGINEER
                            response = profiles.apply_profile(response, role)
                            self.logger.log_operation_complete(
                                ac_id="AC-PHASE-34-003",
                                operation="ROLE_PROFILE_APPLICATION",
                                success=True,
                                details={
                                    "role": role.value,
                                    "final_length": len(response),
                                }
                            )
                        except Exception as profile_err:
                            self.logger.log_operation_complete(
                                ac_id="AC-PHASE-34-003",
                                operation="ROLE_PROFILE_APPLICATION",
                                success=False,
                                details={"error": str(profile_err)}
                            )

                except Exception as phase34_err:
                    # Log but continue - Phase 34 is additive, not blocking
                    self.logger.log_operation_complete(
                        ac_id="AC-PHASE-34-000",
                        operation="ADVANCED_OPTIMIZATION",
                        success=False,
                        details={"error": f"Phase 34 optimization failed: {str(phase34_err)}"}
                    )

            # Step 6: Validate 3-section structure
            if ChatResponsePolicyValidator is not None:
                try:
                    validator = ChatResponsePolicyValidator()
                    is_valid, errors = validator.validate_full_response(response)
                    if not is_valid:
                        self.logger.log_operation_complete(
                            ac_id="AC-PHASE-33-003",
                            operation="VALIDATE_3_SECTION",
                            success=False,
                            details={"errors": errors}
                        )
                    else:
                        self.logger.log_operation_complete(
                            ac_id="AC-PHASE-33-003",
                            operation="VALIDATE_3_SECTION",
                            success=True
                        )
                except Exception as val_err:
                    self.logger.log_operation_complete(
                        ac_id="AC-PHASE-33-003",
                        operation="VALIDATE_3_SECTION",
                        success=False,
                        details={"error": str(val_err)}
                    )

        except Exception as policy_err:
            # Log but continue - policies are additive, not blocking
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-33-001",
                operation="RESPONSE_POLICIES",
                success=False,
                details={"error": f"Policy application failed: {str(policy_err)}"}
            )

        # ═══════════════════════════════════════════════════════════════════════
        # GATE: Response Content Validation (CORE-002-RESPONSE - Inline-First)
        # ═══════════════════════════════════════════════════════════════════════
        # Validates response text for markdown file suggestions before sending to Copilot Chat
        # This is the response-level enforcement gate for 100% inline-first architecture
        if self._enforcement:
            try:
                validation_result = self._enforcement.validate_response_content(response)

                if validation_result.is_err():
                    # Response contains forbidden file suggestions - transform to inline
                    enforcement_result = validation_result.error
                    self.logger.log_operation_complete(
                        ac_id="AC-CORE-002-RESPONSE-001",
                        operation="RESPONSE_CONTENT_VIOLATION_DETECTED",
                        success=False,
                        details={
                            "violations": enforcement_result.violations,
                            "count": len(enforcement_result.violations),
                        }
                    )

                    # Transform response to suggest inline display instead
                    response = self._enforcement.transform_response_to_inline(response)
                    self.logger.log_operation_complete(
                        ac_id="AC-CORE-002-RESPONSE-002",
                        operation="RESPONSE_TRANSFORMED_TO_INLINE",
                        success=True,
                        details={"action": "Replaced file suggestions with inline alternatives"}
                    )
                else:
                    # Response passed validation - inline-first compliant
                    self.logger.log_operation_complete(
                        ac_id="AC-CORE-002-RESPONSE-001",
                        operation="RESPONSE_CONTENT_VALIDATION_PASSED",
                        success=True,
                        details={"message": "Response is inline-first compliant"}
                    )
            except Exception as validation_err:
                # Log but continue - validation error shouldn't break response
                self.logger.log_operation_complete(
                    ac_id="AC-CORE-002-RESPONSE-001",
                    operation="RESPONSE_CONTENT_VALIDATION",
                    success=False,
                    details={"error": f"Response validation error: {str(validation_err)}"}
                )

        # AC-ENH-002-01: Apply header injection (existing behavior)
        if not self.header_injector:
            return response

        try:
            # Build context from orchestrator state
            context: Dict[str, Any] = {
                "operation": self.current_operation or "coordination",
                "orchestrator": self.get_name(),
                "phase": self.current_phase or "coordination",
                "mode": self.get_mode().name,
                "author": "CORTEX",  # Master orchestrator is system-authored
            }

            # AC-ENH-002-01: Build header section using injector pattern
            header_section = self.header_injector._build_header_section(context)

            # AC-ENH-002-01: Build copyright section (appears after content)
            copyright_section = self.header_injector._build_copyright_section(context)

            # Assemble: header + content + copyright (NOT including footer for orchestrators)
            sections = []
            if header_section:
                sections.append(header_section)
            sections.append(response)
            if copyright_section:
                sections.append(copyright_section)

            # Use injector's assembly logic for consistent spacing
            wrapped_response = self.header_injector._assemble_sections(sections)

            return wrapped_response

        except Exception as e:
            # Graceful degradation: log error and return response with policies applied
            self.logger.log_operation_complete(
                ac_id="AC-ENH-002-01",
                operation="HEADER_INJECTION",
                success=False,
                details={"error": f"Header injection failed: {str(e)}"}
            )
            return response
