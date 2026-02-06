"""
Coordinator - Routes operations to appropriate orchestrators

AC-PHASE-24: Master Orchestrator Decomposition
- Tier 1 routing: Intent classification → appropriate handler
- Stage management: LENS → Challenge → DoR → Execution
- Fallback management: Graceful degradation on failures
"""

from __future__ import annotations

import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class PipelineStage(Enum):
    """Pipeline execution stages."""
    LENS_CONTEXT = "lens_context"
    CHALLENGE = "challenge"
    DOR_VALIDATION = "dor_validation"
    EXECUTION = "execution"
    COMPLETION = "completion"


@dataclass
class StageResult:
    """Result from a pipeline stage."""
    stage: PipelineStage
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None


class Coordinator:
    """
    Routes operations through pipeline stages.

    Responsibilities:
    - Select appropriate stage based on intent
    - Execute stage in sequence
    - Handle stage transitions
    - Manage fallback routes

    Example:
        coordinator = Coordinator()
        result = coordinator.coordinate_operation(
            user_request="implement cache layer",
            intent_type="IMPLEMENT"
        )
    """

    def __init__(self, orchestrators: Optional[Dict[str, Any]] = None):
        """Initialize coordinator."""
        self.stage_handlers: Dict[PipelineStage, Any] = {}
        self.fallback_routes: Dict[PipelineStage, PipelineStage] = {}
        self.orchestrators = orchestrators or {}
        self.logger = logging.getLogger(__name__)

    def register_stage_handler(
        self,
        stage: PipelineStage,
        handler: Any,
        fallback_to: Optional[PipelineStage] = None
    ) -> None:
        """
        Register a handler for a pipeline stage.

        Args:
            stage: Pipeline stage identifier
            handler: Callable handler for the stage
            fallback_to: Fallback stage if this one fails
        """
        self.stage_handlers[stage] = handler
        if fallback_to:
            self.fallback_routes[stage] = fallback_to

    def coordinate_operation(
        self,
        user_request: str,
        intent_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Coordinate operation through pipeline stages.

        Args:
            user_request: User's original request
            intent_type: Classification (IMPLEMENT, FIX, REFACTOR, etc.)
            context: Additional context data

        Returns:
            Operation result with all stage outputs
        """
        context = context or {}
        results: List[StageResult] = []

        # Determine initial stage based on intent
        stages = self._determine_stages(intent_type)

        for stage in stages:
            result = self._execute_stage(stage, user_request, context)
            results.append(result)

            if not result.success and stage in self.fallback_routes:
                # Execute fallback stage
                fallback_stage = self.fallback_routes[stage]
                result = self._execute_stage(fallback_stage, user_request, context)
                results.append(result)

            # Stop on critical failures
            if not result.success and stage == PipelineStage.DOR_VALIDATION:
                break

        return {
            "stages": results,
            "success": all(r.success for r in results),
            "final_context": context
        }

    def _determine_stages(self, intent_type: str) -> List[PipelineStage]:
        """Determine which stages to execute based on intent."""
        # All intents go through LENS context
        stages = [PipelineStage.LENS_CONTEXT]

        # IMPLEMENT/FIX/REFACTOR need challenge + DoR
        if intent_type in ["IMPLEMENT", "FIX", "REFACTOR"]:
            stages.extend([
                PipelineStage.CHALLENGE,
                PipelineStage.DOR_VALIDATION,
                PipelineStage.EXECUTION
            ])
        elif intent_type in ["ANALYZE"]:
            # Analysis skips challenge/DoR
            stages.append(PipelineStage.EXECUTION)
        else:
            # Default: execution only
            stages.append(PipelineStage.EXECUTION)

        stages.append(PipelineStage.COMPLETION)
        return stages

    def _execute_stage(
        self,
        stage: PipelineStage,
        user_request: str,
        context: Dict[str, Any]
    ) -> StageResult:
        """Execute a pipeline stage."""
        handler = self.stage_handlers.get(stage)

        if not handler:
            return StageResult(
                stage=stage,
                success=False,
                data={},
                error=f"No handler registered for {stage.value}"
            )

        try:
            result = handler(user_request, context)
            return StageResult(
                stage=stage,
                success=True,
                data=result
            )
        except Exception as e:
            return StageResult(
                stage=stage,
                success=False,
                data={},
                error=str(e)
            )

    def execute_stage_challenge(
        self,
        user_request: str,
        context: Dict[str, Any]
    ) -> StageResult:
        """
        Execute CHALLENGE stage: Comprehension-driven analysis.
        AC-PERMANENT-FIX-006: Stage 1 challenge-driven comprehension logic.
        AC-CHALLENGE-SYSTEM-002: Challenge generation and presentation.

        Extracted from master_orchestrator.process_user_request() lines 1347-1450.
        """
        try:
            # AC-PERMANENT-FIX-006: Graceful fallback if InteractionOrchestrator unavailable
            interaction_orch = self.orchestrators.get("interaction_orchestrator")
            if not interaction_orch:
                self.logger.info("InteractionOrchestrator unavailable - skipping challenge")
                return StageResult(
                    stage=PipelineStage.CHALLENGE,
                    success=True,
                    data={"challenge_needed": False, "reason": "orchestrator_unavailable"},
                    error=None
                )

            # Build RoundContext for comprehension turn
            try:
                from cortex.brain.core.orchestrator.conversation_protocol import RoundContext
                from datetime import datetime
                round_context = RoundContext(
                    round_number=1,
                    user_input=user_request,
                    previous_context=context.get("conversation_history", {}),
                    orchestrator_name="interaction_orchestrator"
                )
            except ImportError:
                self.logger.warning("RoundContext import failed - proceeding without challenge")
                return StageResult(
                    stage=PipelineStage.CHALLENGE,
                    success=True,
                    data={"challenge_needed": False},
                    error=None
                )

            # AC-CHALLENGE-SYSTEM-002: Execute comprehension turn with challenge
            try:
                result = interaction_orch.execute_turn_with_challenge(round_context)
            except Exception as e:
                # Log but don't fail - challenge is optional (graceful degradation)
                self.logger.warning(f"Challenge generation failed: {e}. Proceeding without.")
                return StageResult(
                    stage=PipelineStage.CHALLENGE,
                    success=True,
                    data={"challenge_needed": False},
                    error=None
                )

            # If challenge generated, return it for user review
            if result and result.get("type") == "challenge":
                return StageResult(
                    stage=PipelineStage.CHALLENGE,
                    success=True,
                    data={"challenge": result, "challenge_generated": True},
                    error=None
                )

            # No challenge needed, proceed
            return StageResult(
                stage=PipelineStage.CHALLENGE,
                success=True,
                data={"challenge_generated": False},
                error=None
            )

        except Exception as e:
            self.logger.error(f"Challenge stage unexpected error: {e}")
            return StageResult(
                stage=PipelineStage.CHALLENGE,
                success=False,
                data={},
                error=str(e)
            )

    def execute_stage_execution(
        self,
        user_request: str,
        context: Dict[str, Any]
    ) -> StageResult:
        """
        Execute EXECUTION stage: Intent routing → Governance → Domain execution.
        AC-GOVE-REM-001: Intent classification (Stage 2).
        AC-PHASE-6C-001: Governance enforcement (Stage 3).

        Extracted from master_orchestrator.execute_operation() lines 1430-1600+.
        """
        try:
            # Stage 2: AC-GOVE-REM-001 Intent Classification
            intent_router = self.orchestrators.get("intent_router")
            if intent_router:
                try:
                    routing_decision = intent_router.classify_intent(
                        user_request,
                        {"operation": context.get("operation_name", "unknown")}
                    )
                    self.logger.info(f"Intent classified: {routing_decision.intent_type}")
                except Exception as e:
                    self.logger.warning(f"Intent classification failed: {e}")
                    routing_decision = None
            else:
                routing_decision = None

            # Stage 3: AC-PHASE-6C-001 Governance Enforcement
            enforcement_orch = self.orchestrators.get("enforcement_orchestrator")
            if enforcement_orch:
                try:
                    enforcement_result = enforcement_orch.validate_operation({
                        "intent": routing_decision.intent_type if routing_decision else None,
                        "operation": context.get("operation_name"),
                        "parameters": context.get("parameters", {})
                    })

                    # Check enforcement level
                    if hasattr(enforcement_result, "level"):
                        from cortex.orchestrators.core.enforcement_orchestrator import EnforcementLevel
                        if enforcement_result.level == EnforcementLevel.BLOCKED:
                            self.logger.error(f"Governance violation: {enforcement_result}")
                            return StageResult(
                                stage=PipelineStage.EXECUTION,
                                success=False,
                                data={},
                                error=f"Governance enforcement blocked: {enforcement_result}"
                            )
                        elif enforcement_result.level == EnforcementLevel.WARNING:
                            self.logger.warning(f"Governance warning: {enforcement_result}")
                            # Continue execution with warning
                except Exception as e:
                    self.logger.warning(f"Governance validation failed: {e}")

            # Stage 4: Domain execution delegation
            execution_orch = self.orchestrators.get("execution_orchestrator")
            if execution_orch:
                try:
                    exec_result = execution_orch.execute_tdd_cycle(
                        intent=routing_decision.intent_type if routing_decision else "UNKNOWN",
                        parameters=context.get("parameters", {})
                    )
                    return StageResult(
                        stage=PipelineStage.EXECUTION,
                        success=True,
                        data=exec_result,
                        error=None
                    )
                except Exception as e:
                    self.logger.error(f"Execution orchestrator failed: {e}")
                    return StageResult(
                        stage=PipelineStage.EXECUTION,
                        success=False,
                        data={},
                        error=str(e)
                    )
            else:
                self.logger.error("No execution orchestrator available")
                return StageResult(
                    stage=PipelineStage.EXECUTION,
                    success=False,
                    data={},
                    error="No execution orchestrator registered"
                )

        except Exception as e:
            self.logger.error(f"Execution stage unexpected error: {e}")
            return StageResult(
                stage=PipelineStage.EXECUTION,
                success=False,
                data={},
                error=str(e)
            )
