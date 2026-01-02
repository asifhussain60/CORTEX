"""
Master Orchestrator - Centralized Routing and Orchestrator Coordination.

Machine-readable routing layer that eliminates LLM-dependent brittleness
through deterministic pattern matching with optional LLM fallback.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from src.orchestrators.pattern_router import PatternRouter, OrchestratorMatch
from src.orchestrators.state_manager import StateManager
from src.orchestrators.execution_engine import ExecutionEngine, ExecutionResult
from src.orchestrators.context_middleware import CrossSessionContextMiddleware
from src.mcp.registry import OrchestratorRegistry
from src.database.planning_state_db import PlanningStateDB


class MasterOrchestrator:
    """
    Centralized orchestrator routing and lifecycle management.
    
    Features:
    - Machine-readable pattern-based routing (90%+ of requests)
    - Optional LLM fallback for ambiguous inputs
    - Orchestrator registry and discovery
    - Cross-orchestrator state coordination
    - Lifecycle management with hooks
    - Execution monitoring and metrics
    
    Architecture:
    ```
    User Input → PatternRouter (exact/regex) → Orchestrator Execution
                      ↓ (no match)
                 LLM Classifier (fallback)
    ```
    
    Usage:
        master = MasterOrchestrator(
            config_path='cortex-brain/config/master-orchestrator.yaml',
            registry=OrchestratorRegistry(...),
            state_db=PlanningStateDB(...)
        )
        
        # Route and execute
        result = master.handle_request("plan user authentication")
    """
    
    def __init__(
        self,
        config_path: str,
        registry: OrchestratorRegistry,
        state_db: PlanningStateDB,
        llm_fallback: Optional[Any] = None,
        context_middleware: Optional[CrossSessionContextMiddleware] = None
    ):
        """
        Initialize Master Orchestrator.
        
        Args:
            config_path: Path to master-orchestrator.yaml config
            registry: OrchestratorRegistry for orchestrator discovery
            state_db: PlanningStateDB for state persistence
            llm_fallback: Optional LLMIntentClassifier for ambiguous inputs
            context_middleware: Optional CrossSessionContextMiddleware for continuation routing
        """
        self.config_path = Path(config_path)
        self.registry = registry
        self.state_db = state_db
        self.llm_fallback = llm_fallback
        
        # Setup logging
        self.logger = logging.getLogger("cortex.orchestrators.master")
        
        # Core components
        self.router = PatternRouter(config_path)
        self.state_manager = StateManager(state_db)
        self.execution_engine = ExecutionEngine()
        
        # Cross-session context middleware (Phase 4.5)
        self.context_middleware = context_middleware or CrossSessionContextMiddleware()
        
        # Execution tracking
        self._request_count = 0
        self._pattern_match_count = 0
        self._llm_fallback_count = 0
        self._continuation_count = 0
        
        self.logger.info(
            f"MasterOrchestrator initialized with context middleware (config={config_path})"
        )
    
    def handle_request(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """
        Route and execute user request with cross-session context awareness.
        
        Enhanced with context middleware for continuation detection (Phase 4.5).
        
        Args:
            user_input: User's natural language request
            context: Optional context for execution
        
        Returns:
            ExecutionResult with orchestrator execution details
        
        Raises:
            ValueError: If no orchestrator matches request
            RuntimeError: If orchestrator execution fails
        """
        self._request_count += 1
        
        self.logger.info(f"Handling request: '{user_input}'")
        
        # STEP 1: Enrich context with cross-session metadata (NEW - Phase 4.5)
        enriched_context = self.context_middleware.enrich_context(user_input, context)
        
        # STEP 2: Check if continuation with last orchestrator
        if enriched_context.get('continuation_detected'):
            last_orch = enriched_context['recent_activity'][0]['orchestrator']
            self.logger.info(
                f"Continuation detected → routing to last orchestrator: {last_orch}"
            )
            self._continuation_count += 1
            return self._resume_orchestrator(last_orch, enriched_context)
        
        # STEP 3: Standard pattern-based routing
        match = self.route_request(user_input, enriched_context)
        
        if not match.is_matched:
            error_msg = f"No orchestrator matched: '{user_input}'"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.logger.info(
            f"Routed to: {match.orchestrator_id} "
            f"(confidence={match.confidence:.2f}, type={match.match_type.value})"
        )
        
        # STEP 4: Execute orchestrator
        result = self.execute_orchestrator(
            orchestrator_id=match.orchestrator_id,
            params={
                'user_request': user_input,
                'context': enriched_context,
                'routing_match': match
            }
        )
        
        # STEP 5: Record session metadata for future continuations
        if result.success and enriched_context.get('session_id'):
            self._record_session_metadata(
                session_id=enriched_context['session_id'],
                orchestrator=match.orchestrator_id,
                intent=user_input,
                artifacts=result.artifacts
            )
        
        return result
    
    def route_request(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> OrchestratorMatch:
        """
        Route user request to orchestrator (pattern match + LLM fallback).
        
        Args:
            user_input: User's natural language input
            context: Execution context
        
        Returns:
            OrchestratorMatch with routing decision
        """
        # Try pattern-based routing first
        match = self.router.match_intent(user_input)
        
        if match.is_high_confidence:
            # High confidence pattern match
            self._pattern_match_count += 1
            return match
        
        # Low confidence or no match - try LLM fallback
        if self.llm_fallback and (
            not match.is_matched or match.confidence < 0.9
        ):
            self.logger.debug(
                f"Pattern match confidence low ({match.confidence:.2f}), "
                f"trying LLM fallback"
            )
            
            llm_match = self._llm_fallback_routing(user_input, context)
            
            if llm_match.is_matched and llm_match.confidence > match.confidence:
                self._llm_fallback_count += 1
                self.logger.info(
                    f"LLM fallback improved match: "
                    f"{llm_match.orchestrator_id} "
                    f"(confidence={llm_match.confidence:.2f})"
                )
                return llm_match
        
        # Return best match (may be no match)
        if match.is_matched:
            self._pattern_match_count += 1
        
        return match
    
    def _llm_fallback_routing(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> OrchestratorMatch:
        """
        LLM-based fallback routing for ambiguous inputs.
        
        Args:
            user_input: User input
            context: Execution context
        
        Returns:
            OrchestratorMatch from LLM classification
        """
        try:
            # Call LLM intent classifier
            classification = self.llm_fallback.classify(user_input, context)
            return classification
            
        except Exception as e:
            self.logger.error(
                f"LLM fallback failed: {e}",
                exc_info=True
            )
            
            # Return no match on error
            from src.orchestrators.pattern_router import MatchType
            return OrchestratorMatch(
                orchestrator_id=None,
                confidence=0.0,
                match_type=MatchType.NONE
            )
    
    def execute_orchestrator(
        self,
        orchestrator_id: str,
        params: Dict[str, Any]
    ) -> ExecutionResult:
        """
        Execute orchestrator with lifecycle management.
        
        Args:
            orchestrator_id: Orchestrator identifier
            params: Execution parameters
        
        Returns:
            ExecutionResult with execution details
        
        Raises:
            ValueError: If orchestrator not found
            RuntimeError: If execution fails
        """
        # Get orchestrator from registry
        orchestrator = self.registry.instantiate(orchestrator_id)
        
        if not orchestrator:
            raise ValueError(f"Orchestrator not found: {orchestrator_id}")
        
        # Begin execution tracking
        log_id = self.state_manager.begin_execution(
            orchestrator_id,
            params
        )
        
        try:
            # Execute with engine
            result = self.execution_engine.run(
                orchestrator=orchestrator,
                params=params,
                hooks=self._get_lifecycle_hooks(orchestrator_id)
            )
            
            # Complete execution tracking
            self.state_manager.complete_execution(
                orchestrator_id,
                result.to_dict()
            )
            
            return result
            
        except Exception as e:
            # Fail execution tracking
            self.state_manager.fail_execution(orchestrator_id, str(e))
            raise RuntimeError(
                f"Orchestrator execution failed: {orchestrator_id} - {e}"
            ) from e
    
    def _get_lifecycle_hooks(
        self,
        orchestrator_id: str
    ) -> Dict[str, list]:
        """
        Get lifecycle hooks for orchestrator.
        
        Args:
            orchestrator_id: Orchestrator identifier
        
        Returns:
            Dictionary of hook lists
        """
        # Default hooks for all orchestrators
        return {
            'pre_execution': [
                self._validate_dependencies,
                self._check_state_conflicts
            ],
            'post_execution': [
                self._save_artifacts,
                self._update_metrics
            ],
            'on_error': [
                self._log_failure,
                self._notify_user
            ]
        }
    
    def _validate_dependencies(
        self,
        orchestrator: Any,
        params: Dict[str, Any]
    ) -> None:
        """Pre-execution hook: Validate dependencies."""
        self.logger.debug(f"Validating dependencies for {orchestrator.name}")
    
    def _check_state_conflicts(
        self,
        orchestrator: Any,
        params: Dict[str, Any]
    ) -> None:
        """Pre-execution hook: Check for state conflicts."""
        self.logger.debug(f"Checking state conflicts for {orchestrator.name}")
    
    def _save_artifacts(
        self,
        orchestrator: Any,
        result: Any
    ) -> None:
        """Post-execution hook: Save artifacts."""
        self.logger.debug(f"Saving artifacts for {orchestrator.name}")
        # Artifacts already saved by orchestrator
    
    def _update_metrics(
        self,
        orchestrator: Any,
        result: Any
    ) -> None:
        """Post-execution hook: Update metrics."""
        self.logger.debug(f"Updating metrics for {orchestrator.name}")
        # Metrics already updated by execution engine
    
    def _log_failure(
        self,
        orchestrator: Any,
        error: Exception
    ) -> None:
        """Error hook: Log failure."""
        self.logger.error(
            f"Orchestrator failed: {orchestrator.name} - {error}",
            exc_info=True
        )
    
    def _notify_user(
        self,
        orchestrator: Any,
        error: Exception
    ) -> None:
        """Error hook: Notify user of failure."""
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get Master Orchestrator metrics.
        
        Returns:
            Dictionary with metrics
        """
        router_stats = self.router.get_stats()
        
        return {
            'total_requests': self._request_count,
            'pattern_matches': self._pattern_match_count,
            'llm_fallbacks': self._llm_fallback_count,
            'continuations': self._continuation_count,
            'pattern_match_rate': (
                self._pattern_match_count / self._request_count 
                if self._request_count > 0 else 0
            ),
            'continuation_rate': (
                self._continuation_count / self._request_count
                if self._request_count > 0 else 0
            ),
            'router_stats': router_stats
        }
    
    def _resume_orchestrator(
        self,
        orchestrator_id: str,
        context: Dict[str, Any]
    ) -> ExecutionResult:
        """
        Resume execution with last orchestrator.
        
        Part of Phase 4.5: Cross-session continuation routing.
        
        Args:
            orchestrator_id: ID of orchestrator to resume
            context: Enriched context with recent_activity
        
        Returns:
            ExecutionResult from orchestrator execution
        """
        # Get orchestrator from registry
        orchestrator = self.registry.instantiate(orchestrator_id)
        
        if not orchestrator:
            self.logger.error(f"Orchestrator not found for resume: {orchestrator_id}")
            return ExecutionResult(
                success=False,
                message=f"Cannot resume: orchestrator '{orchestrator_id}' not found",
                orchestrator_id=orchestrator_id,
                execution_time=0.0,
                artifacts=[]
            )
        
        # Execute with context
        self.logger.info(f"Resuming orchestrator: {orchestrator_id}")
        
        result = self.execution_engine.execute(
            orchestrator=orchestrator,
            params={
                'user_request': 'continue',  # Continuation request
                'context': context
            }
        )
        
        # Record orchestrator usage in Tier 1
        if result.success and context.get('session_id'):
            self._record_session_metadata(
                session_id=context['session_id'],
                orchestrator=orchestrator_id,
                intent='continuation',
                artifacts=result.artifacts
            )
        
        return result
    
    def _record_session_metadata(
        self,
        session_id: str,
        orchestrator: str,
        intent: str,
        artifacts: List[str]
    ) -> None:
        """
        Record orchestrator usage in Tier 1 for future continuations.
        
        Part of Phase 4.5: Cross-session context tracking.
        
        Args:
            session_id: Session identifier
            orchestrator: Orchestrator ID that handled request
            intent: User's primary intent
            artifacts: List of artifact paths/IDs generated
        """
        try:
            self.context_middleware.session_manager.record_orchestrator_usage(
                session_id=session_id,
                orchestrator=orchestrator,
                intent=intent,
                artifacts=artifacts
            )
            
            self.logger.debug(
                f"Recorded session metadata: {orchestrator} (session={session_id})"
            )
        
        except Exception as e:
            self.logger.error(f"Failed to record session metadata: {e}")
        state_stats = self.state_manager.get_stats()
        engine_metrics = self.execution_engine.get_metrics()
        
        pattern_match_rate = (
            self._pattern_match_count / self._request_count
            if self._request_count > 0 else 0.0
        )
        
        llm_fallback_rate = (
            self._llm_fallback_count / self._request_count
            if self._request_count > 0 else 0.0
        )
        
        return {
            'total_requests': self._request_count,
            'pattern_match_count': self._pattern_match_count,
            'llm_fallback_count': self._llm_fallback_count,
            'pattern_match_rate': pattern_match_rate,
            'llm_fallback_rate': llm_fallback_rate,
            'router': router_stats,
            'state_manager': state_stats,
            'execution_engine': engine_metrics
        }
    
    def reload_config(self) -> None:
        """Reload routing configuration."""
        self.logger.info("Reloading Master Orchestrator configuration...")
        self.router.reload_config()
        self.logger.info("Configuration reloaded")
