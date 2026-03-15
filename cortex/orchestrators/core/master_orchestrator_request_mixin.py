"""
MasterOrchestratorRequestMixin — Request processing, operation execution, and routing helpers.

Extracted from cortex/orchestrators/core/master_orchestrator.py (Phase 103-a, GAP-103-01).
Single Responsibility: Handle user request pipeline, 4-stage execution, and supporting helpers.
"""
from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

from cortex.core.result import Err, Ok, Result


class MasterOrchestratorRequestMixin:
    """Mixin providing request processing to MasterOrchestrator.

    Handles:
    - process_user_request
    - execute_operation
    - execute_approved_operation
    - _stage_2_routing
    - _select_intelligence_tier
    - _get_intelligence_context
    - _opj_post_dispatch
    - _check_mcp_gate
    - _check_for_workflow_template
    - _trigger_lifecycle_hooks_sync
    """

    def _stage_2_routing(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 2: Route request with unified intelligence synthesis.

        Delegates to MasterOrchestratorStage2 (extracted as part of F2 decomposition, Phase 57).

        Authority: AC-PHASE-20-COMPONENT-4, AC-KNOWLEDGE-SYNTHESIS-001 (Phase 20.5)

        Args:
            request: Request dict (operation, description, file_path, company_name,
                domain, keywords, context).

        Returns:
            Routing result dict with intent, target_orchestrator, confidence_score,
            reasoning, context, unified_intelligence, cited_rules, violations, guidance.
        """
        if not hasattr(self, "_stage_2_handler"):
            from cortex.orchestrators.core.master_orchestrator_stage_2 import (
                MasterOrchestratorStage2,
            )
            self._stage_2_handler = MasterOrchestratorStage2(host=self)
        return self._stage_2_handler.route(request)

    def _select_intelligence_tier(self, request: Dict[str, Any]) -> "Any":
        """Select intelligence execution tier based on request complexity.

        Phase 78 GAP-78-A-01: Wire all 3 tiers (quick/targeted/full) based on
        request complexity score rather than always using get_best_practices().

        Args:
            request: Incoming request dict with optional complexity_score key.

        Returns:
            ExecutionTier enum value: QUICK (<200ms), TARGETED (<2s), or FULL (<10s).
        """
        from cortex.intelligence.provider import ExecutionTier
        complexity = request.get("complexity_score", 0.5)
        if complexity < 0.3:
            return ExecutionTier.QUICK
        if complexity < 0.7:
            return ExecutionTier.TARGETED
        return ExecutionTier.FULL

    # _get_intelligence_context() was REMOVED (GAP-117-04, Phase 117-b).
    # It was defined but never called from production code — confirmed dead code.
    # Intelligence context is now served by per-orchestrator calls to
    # get_intelligence_facade().synthesize() / analyze() / query()
    # via the process-level singleton helper.

    def _opj_post_dispatch(
        self, domain: str, success: bool, latency_ms: float = 0.0, error: str = ""
    ) -> None:
        """Record OPJ outcome after every orchestrator dispatch.

        Phase 78 GAP-78-A-07: Wire OPJMixin.record_pattern() into MasterOrchestrator
        post-dispatch to capture success/failure patterns for adaptive routing.

        Args:
            domain: Target orchestrator domain name.
            success: True if dispatch succeeded.
            latency_ms: Elapsed time in milliseconds.
            error: Error description on failure (empty on success).
        """
        try:
            from cortex.intelligence.learning.opj_writer import OPJWriter
            writer = OPJWriter()
            operation = f"dispatch:{domain}"
            if success:
                writer.record_success(
                    orchestrator=self.__class__.__name__,
                    operation=operation,
                    latency_ms=latency_ms,
                )
            else:
                writer.record_failure(
                    orchestrator=self.__class__.__name__,
                    operation=operation,
                    error=error,
                    latency_ms=latency_ms,
                )
        except Exception:
            pass  # OPJ is observability — never block dispatch

    def process_user_request(
        self,
        user_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Result[Dict[str, Any]]:
        """
        Process user request through challenge-driven interaction (Stage 1).

        AC-CHALLENGE-SYSTEM-002 + AC-PERMANENT-FIX-006: Challenge-driven workflow
        AC-PHASE-35-001: Autonomous continuation detection (R1+R3+R4)

        Stages:
        1. Stage 0 (PRE-FLIGHT): Autonomous continuation detection
        2. Stage 1 (InteractionOrchestrator): LENS → Challenge → User Choice
        3. Stage 2 (IntentRouter): Intent classification
        4. Stage 3 (GovernanceRegistry): Compliance validation
        5. Stage 4 (Domain orchestrators): Execution

        Args:
            user_request: Natural language user request
            context: Optional context dictionary

        Returns:
            Result with challenge (if disagreement) or execution result
        """
        import time as _time
        _ac_id = f"AC-MASTER-PROCESS-{int(_time.time() * 1000)}"
        # AC_START: {_ac_id}
        _ac_start_ms = _time.monotonic() * 1000
        try:
            # Phase 113-B: Pre-API request persistence (CORE-064 audit trail)
            _request_id: Optional[str] = None
            _rlm = getattr(self, "_request_log_manager", None)
            if _rlm is not None:
                try:
                    _session_id = str(getattr(self, "_session_id", None) or id(self))
                    _request_id = _rlm.log_request(
                        session_id=_session_id,
                        user_request=user_request,
                        context_snapshot=context,
                    )
                    _rlm.update_status(_request_id, "PROCESSING")
                except Exception:
                    pass  # Non-blocking — logging failure must never prevent execution

            # AC-PHASE-35-001: PRE-FLIGHT - Detect autonomous continuation
            # R1: Continuation detection, R3: Skip verbose status, R4: Single decision gate
            autonomous_mode = False
            if self._autonomous_executor and self._autonomous_executor.detect_continuation(user_request):
                autonomous_mode = True
                self.logger.log_operation_start(
                    ac_id="AC-PHASE-35-001",
                    operation="AUTONOMOUS_CONTINUATION_DETECTED",
                    details={
                        "pattern": self._autonomous_executor.get_continuation_reason(),
                        "skip_dor": self._autonomous_executor.should_skip_dor(),
                        "skip_challenge": True,
                        "mode": "AUTONOMOUS"
                    }
                )

                # AC-PHASE-35-002: Display ASCII progress bar if available
                if self._progress_bar:
                    next_phase = self._autonomous_executor.load_next_phase()
                    if next_phase:
                        from cortex.orchestrators.core.ascii_progress_bar import (
                            Phase as ProgressPhase,
                        )
                        progress_phase = ProgressPhase(
                            name=next_phase.name,
                            progress=0.0,
                            status="active"
                        )
                        progress_display = self._progress_bar.format_phase_progress(progress_phase)
                        self.logger.log_operation_start(
                            ac_id="AC-PHASE-35-002",
                            operation="PROGRESS_BAR_DISPLAY",
                            details={"display": progress_display, "phase": next_phase.name}
                        )

                # Skip challenge system when in autonomous mode
                # R4: Single decision gate (no mid-execution prompts)
                return self.execute_operation(
                    operation_name="process_request",
                    parameters={"request": user_request, "context": context or {}, "autonomous": True}
                )

            # AC-PERMANENT-FIX-006: Stage 1 - Challenge-driven comprehension
            if not self.interaction_orchestrator:
                # G6: P1 alert — Stage 1 skip is never silent (CORE-048 gate bypassed)
                self.logger.log_operation_complete(
                    ac_id="AC-PERMANENT-FIX-006-FALLBACK",
                    operation="STAGE_1_SKIPPED_P1_ALERT",
                    success=False,
                    details={
                        "reason": "interaction_orchestrator_not_initialized",
                        "severity": "P1",
                        "impact": "CORE-048 challenge gate bypassed — code-touching requests unchallenged",
                        "remediation": "Check ConversationProtocol import in wire_stages(); "
                                       "run python3 scripts/refresh_prompt_suite.py to validate",
                    },
                )
                # Process directly via execute_operation (degraded path)
                return self.execute_operation(
                    operation_name="process_request",
                    parameters={"request": user_request, "context": context or {}}
                )

            # Build RoundContext for InteractionOrchestrator
            from cortex.orchestrators.core.master_orchestrator import RoundContext
            if RoundContext:
                _rc_metadata = dict(context or {})
                if _request_id is not None:
                    _rc_metadata["request_id"] = _request_id  # Phase 113-final: FK linkage
                round_context = RoundContext(
                    user_message=user_request,
                    conversation_history=[],
                    metadata=_rc_metadata
                )

                # Execute with challenge system
                result = self.interaction_orchestrator.execute_turn_with_challenge(
                    user_request=user_request,
                    round_context=round_context,
                    pattern_id=None  # Let challenge engine decide
                )

                if result.is_ok():
                    output = result.unwrap()

                    # If challenge returned, pass back to user
                    if output.get("type") == "challenge":
                        self.logger.log_operation_complete(
                            ac_id="AC-CHALLENGE-SYSTEM-002",
                            operation="CHALLENGE_GENERATED",
                            success=True,
                            details={
                                "disagreement_type": output.get("challenge", {}).disagreement_type.value if output.get("challenge") else "unknown",
                                "requires_user_choice": True
                            }
                        )
                        # Phase 113-B: mark COMPLETED (challenge is a valid resolution)
                        if _rlm is not None and _request_id is not None:
                            try:
                                _rlm.update_status(
                                    _request_id, "COMPLETED",
                                    duration_ms=(_time.monotonic() * 1000 - _ac_start_ms),
                                )
                            except Exception:
                                pass
                        return Ok(output)

                    # No challenge, proceed to Stage 2+ execution
                    _exec_result = self.execute_operation(
                        operation_name="process_request",
                        parameters={"request": user_request, "context": context or {}}
                    )
                    # Phase 113-B: mark COMPLETED / FAILED based on pipeline result
                    if _rlm is not None and _request_id is not None:
                        try:
                            _final_status = "COMPLETED" if _exec_result.is_ok() else "FAILED"
                            _rlm.update_status(
                                _request_id, _final_status,
                                duration_ms=(_time.monotonic() * 1000 - _ac_start_ms),
                            )
                        except Exception:
                            pass
                    return _exec_result
                else:
                    return result
            else:
                # Fallback if RoundContext not available
                _exec_result = self.execute_operation(
                    operation_name="process_request",
                    parameters={"request": user_request, "context": context or {}}
                )
                # Phase 113-B: mark COMPLETED / FAILED based on pipeline result
                if _rlm is not None and _request_id is not None:
                    try:
                        _final_status = "COMPLETED" if _exec_result.is_ok() else "FAILED"
                        _rlm.update_status(
                            _request_id, _final_status,
                            duration_ms=(_time.monotonic() * 1000 - _ac_start_ms),
                        )
                    except Exception:
                        pass
                return _exec_result

        except Exception as e:
            # Phase 113-B: Mark FAILED in request log
            if _rlm is not None and _request_id is not None:
                try:
                    _rlm.update_status(
                        _request_id, "FAILED",
                        error_summary=f"{type(e).__name__}: {str(e)[:200]}",
                        duration_ms=(_time.monotonic() * 1000 - _ac_start_ms),
                    )
                except Exception:
                    pass
            # AC_COMPLETE: {_ac_id} ❌ process_user_request failed
            return Err(f"Failed to process user request: {str(e)}")

    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
    ) -> Result[Any]:
        """Execute an operation through the CORTEX orchestration pipeline.

        Performs complete operation execution including:
        - Intent classification via routing factory
        - Governance and compliance validation
        - Domain-specific orchestrator delegation
        - Audit trail logging
        - Result aggregation and formatting

        The operation flows through the full 4-stage CORTEX workflow:
        1. Stage 1: Interaction/Comprehension - understand intent
        2. Stage 2: Intent Routing - classify and route
        3. Stage 3: Governance - validate against policies
        4. Stage 4: Execution - delegate to domain orchestrators

        ENH-087 Track 1 REFACTOR: Extracted stages into pluggable strategy pattern
        - Replaced inline logic with Stage1/2/3/4Strategy delegation
        - Maintains behavioral parity with existing implementation
        - Enables testability and future stage customization

        Args:
            operation_name: Name or type of the operation (e.g., "implement", "fix", "refactor")
            parameters: Operation parameters dictionary containing:
                - required keys depend on operation_name
                - typically includes: target, scope, context

        Returns:
            Result[Any]: Ok with operation result or Err with error message

        Raises:
            No exceptions - all errors wrapped in Result type

        Example:
            >>> master = MasterOrchestrator.instance()
            >>> result = master.execute_operation(
            ...     operation_name="implement",
            ...     parameters={"target": "feature_x", "scope": "module"}
            ... )
            >>> if result.is_ok():
            ...     print(f"Result: {result.unwrap()}")
            ... else:
            ...     print(f"Error: {result.error}")
        """
        import time as _time
        _exec_ac_id = f"AC-MASTER-EXEC-{int(_time.time() * 1000)}"
        # AC_START: {_exec_ac_id}
        _exec_start_ms = _time.monotonic() * 1000
        # Phase 58 — cross-cutting hooks (LENS + KnSynth + GovGate)
        self._activate_cross_cutting_hooks(
            operation=operation_name,
            orchestrator_context=parameters.get("orchestrator_context"),
            unified_context=parameters.get("unified_context"),
        )
        try:
            # ═══════════════════════════════════════════════════════════════════════
            # AC-PHASE-50-001: PLAN INTENT FAST-PATH
            # Operations prefixed "plan:" are routed directly to
            # CortexMasterPlanOrchestrator — bypassing the full 4-stage pipeline.
            # Supported: plan:create | plan:sync | plan:next_sequence | plan:load_template
            # ═══════════════════════════════════════════════════════════════════════
            if operation_name.startswith("plan:") and self.master_plan_orchestrator is not None:
                plan_action = operation_name[len("plan:"):]
                mp = self.master_plan_orchestrator

                if plan_action == "create":
                    result = mp.create_phase(**parameters)
                elif plan_action == "sync":
                    result = mp.sync_phase_folders()
                elif plan_action == "next_sequence":
                    result = mp.next_sequence_number()
                elif plan_action == "load_template":
                    template_name = parameters.get("template_name", "")
                    result = mp.load_workflow_template(template_name)
                else:
                    return Err(f"Unknown plan action: '{plan_action}'. "
                               f"Valid: create | sync | next_sequence | load_template")

                return Ok(result)

            # ═══════════════════════════════════════════════════════════════════════
            # ENH-087 Track 1.3: 4-STAGE STRATEGY PIPELINE
            # ═══════════════════════════════════════════════════════════════════════
            # Refactored from inline logic to pluggable strategy pattern
            # Benefits: Testability, maintainability, extensibility

            # Import stage strategies
            from cortex.orchestrators.core.pipeline_stage_strategy import StageContext
            from cortex.orchestrators.core.stage1_comprehension_strategy import Stage1ComprehensionStrategy
            from cortex.orchestrators.core.stage234_strategies import (
                Stage2IntentClassificationStrategy,
                Stage3ComplianceValidationStrategy,
                Stage4DomainExecutionStrategy,
            )

            # Initialize stage context with operation details
            stage_context = StageContext(
                operation_name=operation_name,
                parameters=parameters,
                metadata={},
                result=None,
                stage_results={}
            )

            # Build dependency map for strategies
            dependencies = {
                "interaction_orchestrator": self.interaction_orchestrator,
                "challenge_generator": getattr(self, "_challenge_generator", None),
                "dor_gate": self._dor_gate,
                "intent_router": self.intent_router,
                "enforcement_orchestrator": self._enforcement,
                "governance_registry": self._governance_registry,
                "domain_orchestrators": self.domain_orchestrators,
                "tdd_orchestrator": getattr(self, "tdd_orchestrator", None),
                "distillationorchestrator": getattr(self, "_distillation_orchestrator", None),
                "contentoptimizationorchestrator": getattr(self, "_content_optimization_orchestrator", None),
                "logger": self.logger,
                # G1/G6 Fix: expose self so Stage4 can call _check_for_workflow_template
                "master_orchestrator": self,
                # Phase 93: expose lens_orchestrator for Stage1 direct LENS fallback
                "lens_orchestrator": getattr(self, "_lens_orchestrator", None),
            }

            # ═══════════════════════════════════════════════════════════════════════
            # STAGE 1: Comprehension + Challenge + DoR Approval
            # ═══════════════════════════════════════════════════════════════════════
            stage1 = Stage1ComprehensionStrategy(dependencies=dependencies)
            stage1_result = stage1.execute(stage_context)

            if stage1_result.is_err():
                # Stage 1 failed - return error
                self.logger.log_operation_complete(
                    ac_id="ENH-087-TRACK-1.3",
                    operation="STAGE_1_COMPREHENSION_FAILED",
                    success=False,
                    details={"error": stage1_result.error}
                )
                return stage1_result

            # Update context with Stage 1 results
            stage_context = stage1_result.unwrap()

            self.logger.log_operation_complete(
                ac_id="ENH-087-TRACK-1.3",
                operation="STAGE_1_COMPREHENSION_COMPLETE",
                success=True,
                details={
                    "comprehension_keys": list(stage_context.stage_results.get("stage1", {}).keys()),
                    "dor_approved": stage_context.metadata.get("dor_approved", False)
                }
            )

            # ═══════════════════════════════════════════════════════════════════════
            # STAGE 2: Intent Classification via IntentRouter
            # ═══════════════════════════════════════════════════════════════════════
            stage2 = Stage2IntentClassificationStrategy(dependencies=dependencies)
            stage2_result = stage2.execute(stage_context)

            if stage2_result.is_err():
                # Stage 2 failed - return error (or warn and continue based on severity)
                self.logger.log_operation_complete(
                    ac_id="ENH-087-TRACK-1.3",
                    operation="STAGE_2_INTENT_CLASSIFICATION_FAILED",
                    success=False,
                    details={"error": stage2_result.error}
                )
                # For now, fail-open: continue with fallback intent = operation_name
                stage_context.metadata["intent_classification"] = {
                    "classified_intent": operation_name,
                    "confidence": 1.0,
                    "fallback": True
                }
            else:
                # Update context with Stage 2 results
                stage_context = stage2_result.unwrap()

                self.logger.log_operation_complete(
                    ac_id="ENH-087-TRACK-1.3",
                    operation="STAGE_2_INTENT_CLASSIFICATION_COMPLETE",
                    success=True,
                    details={
                        "classified_intent": stage_context.metadata.get("intent_classification", {}).get("classified_intent"),
                        "confidence": stage_context.metadata.get("intent_classification", {}).get("confidence")
                    }
                )

            # ═══════════════════════════════════════════════════════════════════════
            # STAGE 3: Compliance Validation via EnforcementOrchestrator
            # ═══════════════════════════════════════════════════════════════════════
            stage3 = Stage3ComplianceValidationStrategy(dependencies=dependencies)
            stage3_result = stage3.execute(stage_context)

            if stage3_result.is_err():
                # Stage 3 failed - compliance violation, BLOCK execution
                self.logger.log_operation_complete(
                    ac_id="ENH-087-TRACK-1.3",
                    operation="STAGE_3_COMPLIANCE_VALIDATION_BLOCKED",
                    success=False,
                    details={"error": stage3_result.error}
                )
                return stage3_result

            # Update context with Stage 3 results
            stage_context = stage3_result.unwrap()

            self.logger.log_operation_complete(
                ac_id="ENH-087-TRACK-1.3",
                operation="STAGE_3_COMPLIANCE_VALIDATION_COMPLETE",
                success=True,
                details={
                    "compliance_status": stage_context.metadata.get("compliance_validation", {}).get("status"),
                    "warnings": stage_context.metadata.get("compliance_validation", {}).get("warnings", [])
                }
            )

            # ═══════════════════════════════════════════════════════════════════════
            # CORE-050 MCP GATE: Hard-block code-modifying intents if MCP unavailable
            # ═══════════════════════════════════════════════════════════════════════
            mcp_gate_result = self._check_mcp_gate(
                classified_intent=stage_context.metadata.get("intent_classification", {}).get("classified_intent", operation_name),
            )
            if mcp_gate_result.is_err():
                self.logger.log_operation_complete(
                    ac_id="CORE-050",
                    operation="MCP_GATE_BLOCKED",
                    success=False,
                    details={"reason": mcp_gate_result.error, "intent": operation_name}
                )
                return mcp_gate_result

            # ═══════════════════════════════════════════════════════════════════════
            # STAGE 4: Domain Execution via Orchestrator Delegation
            # ═══════════════════════════════════════════════════════════════════════
            stage4 = Stage4DomainExecutionStrategy(dependencies=dependencies)
            stage4_result = stage4.execute(stage_context)

            if stage4_result.is_err():
                # Stage 4 failed - execution error
                self.logger.log_operation_complete(
                    ac_id="ENH-087-TRACK-1.3",
                    operation="STAGE_4_DOMAIN_EXECUTION_FAILED",
                    success=False,
                    details={"error": stage4_result.error}
                )
                return stage4_result

            # Update context with Stage 4 results
            stage_context = stage4_result.unwrap()

            self.logger.log_operation_complete(
                ac_id="ENH-087-TRACK-1.3",
                operation="STAGE_4_DOMAIN_EXECUTION_COMPLETE",
                success=True,
                details={
                    "executed_by": stage_context.metadata.get("execution", {}).get("orchestrator"),
                    "execution_time_ms": stage_context.metadata.get("execution", {}).get("duration_ms")
                }
            )

            # ═══════════════════════════════════════════════════════════════════════
            # PIPELINE COMPLETE: Return final result from Stage 4
            # ═══════════════════════════════════════════════════════════════════════

            # Build stage_metadata for holistic harness subsystem tracking
            stage_metadata = {
                "stage1": {
                    **stage_context.stage_results.get("stage1", {}),
                    "lens_engaged": bool(stage_context.metadata.get("lens_context")),
                    "ccl_engaged": bool(stage_context.metadata.get("ccl_context")),
                },
                "stage2": {
                    **stage_context.stage_results.get("stage2", {}),
                    "intent_router_engaged": True,
                    "classified_intent": stage_context.metadata.get("intent_classification", {}).get("classified_intent"),
                },
                "stage3": {
                    **stage_context.stage_results.get("stage3", {}),
                    "enforcement_engaged": True,
                    "compliance_status": stage_context.metadata.get("compliance_validation", {}).get("status"),
                },
                "stage4": {
                    **stage_context.stage_results.get("stage4", {}),
                    "orchestrator": stage_context.metadata.get("execution", {}).get("orchestrator"),
                },
            }

            # Build orchestrators_engaged set for direct reporting
            orchestrators_engaged = {
                "MasterOrchestrator",
                "InteractionOrchestrator",
                "LENSOrchestrator",
                "IntentRouter",
                "RequestRephraseOrchestrator",
                "EnforcementOrchestrator",
            }

            # ── Engagement rendering (Phase 92) ───────────────────────────────
            # Build the routing chain from orchestrators_engaged + execution target.
            # Use render_engagement() — the canonical three-tier routing gate.
            _pipeline_engagement: dict = {}
            try:
                from cortex.orchestrators.core.engagement_renderer import (
                    EngagementRenderer,
                )

                _exec_meta = stage_context.metadata.get("execution", {})
                _target = _exec_meta.get("orchestrator", "")
                _template_id = _exec_meta.get("template_id")

                # Canonical chain: IntentRouter is always first; MasterOrchestrator
                # is the hub; resolved target orchestrator is the leaf.
                _pipeline_chain = ["IntentRouter", "MasterOrchestrator"]
                if _target and _target not in _pipeline_chain:
                    _pipeline_chain.append(_target)

                _pipeline_engagement = EngagementRenderer().render_engagement(
                    chain=_pipeline_chain,
                    template_id=_template_id,
                )
            except Exception:
                _pipeline_engagement = {
                    "breadcrumb": "",
                    "stage_pulse": None,
                    "timeline": None,
                }

            pipeline_result_data = {
                "status": "completed",
                "stages": 4,
                "stage_metadata": stage_metadata,
                "orchestrators_engaged": list(orchestrators_engaged),
                "engagement": _pipeline_engagement,
            }

            # Merge with stage4 result data if it's a dict
            if stage_context.result and stage_context.result.is_ok():
                inner = stage_context.result.unwrap()
                if isinstance(inner, dict):
                    pipeline_result_data.update(inner)
                    # Restore pipeline keys (stage_metadata + orchestrators_engaged +
                    # engagement take precedence over stage4 partial output)
                    pipeline_result_data["stage_metadata"] = stage_metadata
                    pipeline_result_data["orchestrators_engaged"] = list(orchestrators_engaged)
                    pipeline_result_data["engagement"] = _pipeline_engagement

            final_result = Ok(pipeline_result_data)

            self.logger.log_operation_complete(
                ac_id="ENH-087-TRACK-1.3",
                operation="4_STAGE_PIPELINE_COMPLETE",
                success=final_result.is_ok(),
                details={
                    "operation": operation_name,
                    "stages_executed": 4,
                    "total_metadata_keys": len(stage_context.metadata)
                }
            )

            # ENH-092 Phase 53.3: Trigger lifecycle hooks for automatic cleanup
            # Note: Hooks are fire-and-forget (non-blocking completion reporting)
            if hasattr(self, '_lifecycle_hook_system') and self._lifecycle_hook_system:
                self._trigger_lifecycle_hooks_sync(operation_name, stage_context.metadata)

            return final_result

        except Exception as pipeline_err:
            # Catch any unexpected errors in strategy pipeline
            # AC_COMPLETE: {_exec_ac_id} ❌ execute_operation pipeline error
            self.logger.log_operation_complete(
                ac_id="ENH-087-TRACK-1.3",
                operation="4_STAGE_PIPELINE_ERROR",
                success=False,
                details={"error": str(pipeline_err)}
            )
            return Err(f"Pipeline execution failed: {str(pipeline_err)}")

    def execute_approved_operation(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Result[Any]:
        """Execute an operation that has already passed DoR approval.

        This is the post-approval execution entry point called after:
        1. User has classified their intent via DoRApprovalGate
        2. User has approved the intent classification
        3. MasterOrchestrator will now execute with full supervision

        This ensures ALL orchestrator execution flows through MasterOrchestrator's
        4-stage pipeline, not bypassing it via direct router calls.

        Args:
            text: The approved operation request text
            context: Optional context from approval gate

        Returns:
            Result[Any]: Ok with execution result or Err with error message

        Raises:
            None - all errors wrapped in Result type

        AC-GOVE-DOR-WIRE-001: Approved operations flow through MasterOrchestrator
        """
        try:
            self.logger.log_operation_start(
                ac_id="AC-GOVE-DOR-WIRE-001",
                operation="APPROVED_OPERATION_EXECUTION",
                details={
                    "text": text,
                    "context_keys": list(context.keys()) if context else []
                }
            )

            # Parse operation from text if not already classified
            operation_name = "execute"
            parameters = context or {"request_text": text}

            # Delegate to execute_operation for full 4-stage pipeline execution
            result = self.execute_operation(
                operation_name=operation_name,
                parameters=parameters
            )

            self.logger.log_operation_complete(
                ac_id="AC-GOVE-DOR-WIRE-001",
                operation="APPROVED_OPERATION_EXECUTION",
                success=result.is_ok(),
                details={"result": str(result)[:200]}  # Truncate for log
            )

            return result
        except Exception as e:
            error_msg = f"Approved operation execution failed: {str(e)}"
            self.logger.log_operation_complete(
                ac_id="AC-GOVE-DOR-WIRE-001",
                operation="APPROVED_OPERATION_EXECUTION",
                success=False,
                details={"error": error_msg}
            )
            return Err(error_msg)

    def _trigger_lifecycle_hooks_sync(self, operation_name: str, metadata: Dict[str, Any]) -> None:
        """
        Trigger lifecycle hooks synchronously (fire-and-forget).

        ENH-092 Phase 53.3: Automatic cleanup on completions.

        Args:
            operation_name: Operation that completed (implement, fix, refactor, etc.)
            metadata: Operation metadata for context
        """
        from cortex.orchestrators.core.lifecycle_hook_system import CompletionEvent

        try:
            # Determine event type from operation name
            event_map = {
                "wave": CompletionEvent.WAVE_COMPLETE,
                "phase": CompletionEvent.PHASE_COMPLETE,
                "stage": CompletionEvent.STAGE_COMPLETE,
                "session": CompletionEvent.SESSION_END
            }

            event_type = None
            entity_id = operation_name

            # Extract event type from operation name or metadata
            for key, event in event_map.items():
                if key in operation_name.lower():
                    event_type = event
                    break
                if metadata.get("type") == key:
                    event_type = event
                    entity_id = metadata.get("id", operation_name)
                    break

            # Default to STAGE_COMPLETE if no specific event detected
            if not event_type:
                event_type = CompletionEvent.STAGE_COMPLETE

            # Create async task (fire-and-forget)
            async def _trigger() -> None:
                """Trigger."""
                await self._lifecycle_hook_system.trigger_completion(
                    event_type=event_type,
                    entity_id=entity_id,
                    metadata=metadata
                )

            # Run in background without blocking.
            # Guard: asyncio.create_task requires a running event loop.
            # When called from a sync context (no loop), schedule via
            # ensure_future on the running loop, or silently skip.
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(_trigger())
            except RuntimeError:
                # No running event loop — sync context, skip fire-and-forget
                pass

            self.logger.log_operation_complete(
                ac_id="AC-ENH-092-002",
                operation="LIFECYCLE_HOOK_TRIGGERED",
                success=True,
                details={"event": event_type.value, "entity": entity_id}
            )

        except Exception as hook_err:
            # Log but don't fail - hooks are non-blocking
            self.logger.log_operation_complete(
                ac_id="AC-ENH-092-002",
                operation="LIFECYCLE_HOOK_TRIGGERED",
                success=False,
                details={"error": f"Failed to trigger lifecycle hooks: {str(hook_err)}"}
            )

    def _check_mcp_gate(self, classified_intent: str) -> "Result[None]":
        """CORE-050: Hard-block code-modifying intents when MCP is unavailable.

        Implements the CORE-050 MCP Circuit Breaker at the Python level. This
        gate runs after Stage 3 compliance validation and before Stage 4 domain
        execution. It ensures that IMPLEMENT, FIX, REFACTOR, AUDIT, PLAN, and
        ANALYZE operations are never executed without an active MCP connection.

        Args:
            classified_intent: The intent string from Stage 2 classification
                (e.g. "IMPLEMENT", "FIX", "REFACTOR").

        Returns:
            Ok(None) if allowed or MCP is available.
            Err(str) with a user-facing message if hard-blocked.
        """
        # Intents that REQUIRE MCP (CORE-050 tiered blocking)
        _MCP_REQUIRED_INTENTS = {
            "implement", "fix", "refactor", "audit",
            "analyze", "plan", "tdd", "design",
        }

        if classified_intent.lower() not in _MCP_REQUIRED_INTENTS:
            return Ok(None)

        # Check MCP availability via NativeToolInterceptor detector
        try:
            from cortex.governance.enforcement.native_tool_interceptor import MCPDetector
            mcp_available = MCPDetector().is_mcp_available()
        except Exception:
            # If detector fails to import/run, assume available (fail-open)
            mcp_available = True

        if not mcp_available:
            return Err(
                f"CORE-050: MCP server required for '{classified_intent}' intent but is unavailable. "
                "Run `python3 scripts/setup-mcp.py` and reload VS Code."
            )

        return Ok(None)

    def _check_for_workflow_template(
        self, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Check if workflow template should be used for this operation.

        WORKFLOW-COMPLEXITY-GATE-001: Complexity-based template routing.

        Uses WorkflowComplexityRouter to determine if operation requires
        workflow template based on 4-dimension complexity scoring.

        Args:
            context: Operation context with description, intent, attachments, keywords.

        Returns:
            Routing decision with template_id if template suggested, None otherwise.
        """
        try:
            # Import complexity router
            from cortex.orchestrators.core.intent_router.workflow_gate import WorkflowComplexityRouter, Intent as ComplexityIntent
            from cortex.orchestrators.core.intent_router.workflow_gate import RoutingStrategy

            # Extract operation details
            operation = context.get("operation", "").lower()
            description = context.get("description", "").lower()
            combined_text = f"{operation} {description}"

            # Detect operation type — covers all 20 CORTEX intent types (GAP-90-14/15 fix)
            operation_type = "implement"
            if any(kw in combined_text for kw in ["fix", "bug", "issue", "broken", "patch"]):
                operation_type = "fix"
            elif any(kw in combined_text for kw in ["/debug", "debug", "diagnose", "debugger", "marker injection", "injection strategy"]):
                operation_type = "debug"
            elif any(kw in combined_text for kw in ["totalrecall", "total recall", "holistic refactor", "7-phase", "everything is broken"]):
                operation_type = "totalrecall"
            elif any(kw in combined_text for kw in ["rca", "root cause analysis", "fishbone", "five whys", "ishikawa", "fault tree", "causal chain"]):
                operation_type = "rca"
            elif any(kw in combined_text for kw in ["/vacuum", "vacuum", "markdown sprawl", "root clutter", "cortex vacuum"]):
                operation_type = "vacuum"
            elif any(kw in combined_text for kw in ["/health", "health check", "healthcheck", "orchestrator health", "orchestrator status", "22 orchestrators"]):
                operation_type = "health"
            elif any(kw in combined_text for kw in ["/sync", "sync to company", "cross-repo sync", "privacy-safe sync", "one-way sync"]):
                operation_type = "sync"
            elif any(kw in combined_text for kw in ["/train", "learn from repo", "evolve templates", "gap-driven training", "pattern training"]):
                operation_type = "train"
            elif any(kw in combined_text for kw in ["audit", "production readiness", "scan for issues", "repo health"]):
                operation_type = "audit"
            elif any(kw in combined_text for kw in ["refactor", "improve", "optimize", "restructure", "simplify"]):
                operation_type = "refactor"
            elif any(kw in combined_text for kw in ["migrate", "migration", "port", "alembic"]):
                operation_type = "migrate"
            elif any(kw in combined_text for kw in ["test", "testing", "pytest", "tdd"]):
                operation_type = "test"
            elif any(kw in combined_text for kw in ["design", "architect", "blueprint", "system design"]):
                operation_type = "design"
            elif any(kw in combined_text for kw in ["onboard", "onboarding", "bootstrap", "initialize repo"]):
                operation_type = "onboard"
            elif any(kw in combined_text for kw in ["digest", "summarize", "summarise", "recap", "tl;dr"]):
                operation_type = "digest"
            elif any(kw in combined_text for kw in ["investigate", "root cause", "deep analysis", "find the cause"]):
                operation_type = "investigate"
            elif any(kw in combined_text for kw in ["document", "docs", "documentation"]):
                operation_type = "document"
            elif any(kw in combined_text for kw in ["plan", "roadmap", "phase", "schedule"]):
                operation_type = "plan"
            elif any(kw in combined_text for kw in ["security"]):
                operation_type = "security"

            # Extract files and dependencies
            # Phase 122 GAP-122-01: Augment target_files from description text.
            # context.parameters never contains target_files for normal Copilot Chat
            # requests, so parse Python file references from the description to give
            # the complexity router real signal instead of always scoring 0 on the
            # file-count dimension. Falls back to empty list if description is absent.
            import re as _re
            target_files: list = list(context.get("target_files", []))
            if not target_files:
                description_text = context.get("description", "") or context.get("operation", "")
                # Match bare .py/.ts/.cs/.js/.html/.css file references in description
                _extracted = _re.findall(r"\S+\.(?:py|ts|tsx|js|jsx|cs|html|css|scss)\b", description_text)
                if _extracted:
                    target_files = _extracted
            dependencies = context.get("dependencies", [])
            risk_level = context.get("risk_level", "MEDIUM")

            # Build complexity intent
            complexity_intent = ComplexityIntent(
                operation_type=operation_type,
                target_files=target_files,
                dependencies=dependencies,
                risk_level=risk_level,
                metadata=context
            )

            # Route based on complexity
            router = WorkflowComplexityRouter()
            decision = router.route(complexity_intent)

            # If workflow template recommended, return template info
            if decision.route == RoutingStrategy.WORKFLOW_TEMPLATE:
                self.logger.log_operation_complete(
                    ac_id="WORKFLOW-COMPLEXITY-GATE-001",
                    operation="WORKFLOW_TEMPLATE_SELECTED",
                    success=True,
                    details={
                        "template_id": decision.template_id,
                        "complexity": decision.complexity,
                        "rationale": decision.rationale
                    }
                )

                return {
                    "template_id": decision.template_id,
                    "template_name": decision.template_id.replace("/", "_"),
                    "intent": operation_type.upper(),
                    "use_autonomous_workflow": True,
                    "complexity_score": decision.complexity,
                    "requires_confirmation": decision.requires_confirmation
                }

            # Direct orchestrator routing - return None to continue standard flow
            self.logger.log_operation_complete(
                ac_id="WORKFLOW-COMPLEXITY-GATE-001",
                operation="DIRECT_ORCHESTRATOR_SELECTED",
                success=True,
                details={
                    "orchestrator": decision.orchestrator,
                    "complexity": decision.complexity,
                    "rationale": decision.rationale
                }
            )

            return None

        except Exception as e:
            # Log but don't fail - template routing is optional enhancement
            self.logger.log_operation_complete(
                ac_id="WORKFLOW-COMPLEXITY-GATE-001",
                operation="WORKFLOW_TEMPLATE_CHECK",
                success=False,
                details={"error": f"Template check failed: {str(e)}"},
            )
            return None
