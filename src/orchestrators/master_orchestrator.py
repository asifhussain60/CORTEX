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
from src.orchestrators.response_renderer import ResponseRenderer
from src.orchestrators.response_middleware import ResponseMiddleware
from src.orchestrators.audit_logger import (
    get_audit_logger,
    AuditLevel,
    AuditCategory
)
from src.mcp.registry import OrchestratorRegistry
from src.database.planning_state_db import PlanningStateDB

# CORTEX v5 Middleware (Phase -2, Runtime, Phase N+1)
from src.orchestrators.middleware.setup_verification import SetupVerificationMiddleware
from src.orchestrators.middleware.governance_checkpoint import GovernanceCheckpointMiddleware
from src.orchestrators.middleware.teardown_refactor import TeardownRefactorMiddleware


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
        context_middleware: Optional[CrossSessionContextMiddleware] = None,
        response_renderer: Optional[ResponseRenderer] = None,
        response_middleware: Optional[ResponseMiddleware] = None
    ):
        """
        Initialize Master Orchestrator.
        
        Args:
            config_path: Path to master-orchestrator.yaml config
            registry: OrchestratorRegistry for orchestrator discovery
            state_db: PlanningStateDB for state persistence
            llm_fallback: Optional LLMIntentClassifier for ambiguous inputs
            context_middleware: Optional CrossSessionContextMiddleware for continuation routing
            response_renderer: Optional ResponseRenderer for markdown generation
            response_middleware: Optional ResponseMiddleware for system message injection
        """
        self.config_path = Path(config_path)
        self.registry = registry
        self.state_db = state_db
        self.llm_fallback = llm_fallback
        
        # Setup logging
        self.logger = logging.getLogger("cortex.orchestrators.master")
        self.audit_logger = get_audit_logger()
        
        # Core components
        self.router = PatternRouter(config_path)
        self.state_manager = StateManager(state_file=state_db.db_path if state_db else None)
        self.execution_engine = ExecutionEngine()
        
        # Cross-session context middleware (Phase 4.5)
        self.context_middleware = context_middleware or CrossSessionContextMiddleware()
        
        # Response rendering pipeline (Phase 6.4 - Option B fix)
        self.response_renderer = response_renderer or ResponseRenderer()
        self.response_middleware = response_middleware or ResponseMiddleware()
        
        # CORTEX v5 Universal Pattern Middleware (C50-20)
        self.setup_verifier = SetupVerificationMiddleware(workspace_root=Path.cwd())
        self.governance_checkpoint = GovernanceCheckpointMiddleware(brain_path=Path.cwd() / "cortex-brain")
        self.teardown_refactor = TeardownRefactorMiddleware(workspace_root=Path.cwd())
        
        # Execution tracking
        self._request_count = 0
        self._pattern_match_count = 0
        self._llm_fallback_count = 0
        self._continuation_count = 0
        
        self.logger.info(
            f"MasterOrchestrator initialized with context middleware + response pipeline (config={config_path})"
        )
        
        # Initialize orchestrator registry for AC-SCAFFOLD-003 enforcement
        from src.orchestrators.master.orchestrator_registry import OrchestratorRegistry
        self.orchestrator_registry = OrchestratorRegistry(workspace_root=Path.cwd())
    
    def _validate_orchestrator_registration(
        self,
        orchestrator_id: str
    ) -> tuple[bool, str]:
        """
        AC-SCAFFOLD-003: Validate that orchestrator is registered.
        
        Prevents bypass by ensuring all orchestrators are registered
        with MasterOrchestrator before routing.
        
        Args:
            orchestrator_id: Orchestrator to validate
        
        Returns:
            (is_valid, reason_or_ok)
        """
        # Check registration
        is_registered = self.orchestrator_registry.is_registered(orchestrator_id)
        if not is_registered:
            reason = f"Orchestrator not registered: {orchestrator_id}"
            self.logger.warning(reason)
            self.audit_logger.log(
                level=AuditLevel.WARNING,
                category=AuditCategory.SECURITY,
                component="MasterOrchestrator",
                operation="validate_registration",
                message=reason,
                metadata={'orchestrator_id': orchestrator_id}
            )
            return False, reason
        
        # Check routing validity
        is_valid, reason = self.orchestrator_registry.validate_for_routing(
            orchestrator_id
        )
        
        if not is_valid:
            self.logger.warning(reason)
            self.audit_logger.log(
                level=AuditLevel.WARNING,
                category=AuditCategory.SECURITY,
                component="MasterOrchestrator",
                operation="validate_routing",
                message=reason,
                metadata={'orchestrator_id': orchestrator_id}
            )
            return False, reason
        
        # All checks passed
        self.logger.debug(f"Orchestrator registration validated: {orchestrator_id}")
        return True, "OK"
    
    def _check_review_schedule(
        self,
        orchestrator_id: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Check if holistic review should be triggered before orchestrator execution.
        
        Reads progress.json from parent plan to determine if a holistic review
        is scheduled and should auto-trigger at this point.
        
        Args:
            orchestrator_id: Target orchestrator about to execute
            context: Execution context (may contain parent_plan_id)
        
        Returns:
            Review configuration dict if review needed, None otherwise
            Dict contains: review_number, review_name, document_path, scope, etc.
        """
        # Check if context has parent plan information
        parent_plan_id = context.get('parent_plan_id')
        if not parent_plan_id:
            # No parent plan = no automatic review triggering
            return None
        
        # Load progress.json for parent plan
        progress_file = Path(
            f"cortex-brain/documents/planning/active/{parent_plan_id}/tracking/progress.json"
        )
        
        if not progress_file.exists():
            self.logger.debug(f"No progress.json found for {parent_plan_id}")
            return None
        
        try:
            import json
            with open(progress_file, 'r') as f:
                progress_data = json.load(f)
            
            # Check if holistic reviews enabled
            reviews_config = progress_data.get('holistic_reviews', {})
            if not reviews_config.get('enabled') or not reviews_config.get('auto_trigger'):
                return None
            
            # Check schedule for pending reviews
            schedule = reviews_config.get('schedule', [])
            for review in schedule:
                if review['status'] == 'not_started':
                    # Check if trigger condition met
                    trigger_condition = review.get('trigger_condition', '')
                    
                    # Parse trigger condition (e.g., "phase_1_complete")
                    if trigger_condition.startswith('phase_'):
                        phase_num = int(trigger_condition.split('_')[1])
                        
                        # Check if phase complete in progress
                        current_phase = progress_data.get('progress', {}).get('current_phase', 0)
                        
                        if current_phase >= phase_num:
                            # Review should be triggered
                            self.logger.info(
                                f"Holistic Review #{review['review_number']} scheduled "
                                f"(trigger: {trigger_condition})"
                            )
                            return review
            
            return None
            
        except Exception as e:
            self.logger.error(
                f"Failed to check review schedule: {e}",
                exc_info=True
            )
            return None
    
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
        
        # STEP 3.2: AC-SCAFFOLD-003 - Validate orchestrator registration
        is_registered, reg_reason = self._validate_orchestrator_registration(
            match.orchestrator_id
        )
        if not is_registered:
            error_msg = f"Orchestrator registration validation failed: {reg_reason}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # STEP 3.5: Check if holistic review should be triggered (NEW - Phase 6.4)
        review_config = self._check_review_schedule(match.orchestrator_id, enriched_context)
        
        if review_config:
            self.logger.info(
                f"Auto-triggering Holistic Review #{review_config['review_number']} "
                f"before {match.orchestrator_id} execution"
            )
            
            try:
                # Execute holistic review
                review_result = self.execute_orchestrator(
                    orchestrator_id="holistic_review_orchestrator",
                    params={
                        'parent_plan_id': enriched_context.get('parent_plan_id'),
                        'review_number': review_config['review_number'],
                        'review_name': review_config.get('review_name', 'Automated Review'),
                        'document_path': review_config.get('document_path', 'architecture/holistic-review.md'),
                        'scope': review_config.get('scope', 'general'),
                        'completed_phases': review_config.get('completed_phases', [])
                    }
                )
                
                # Inject review insights into context
                if review_result.success and review_result.metadata:
                    insights = review_result.metadata.get('insights', [])
                    enriched_context['review_insights'] = insights
                    
                    self.logger.info(
                        f"Injected {len(insights)} insights from holistic review into context"
                    )
                
            except Exception as e:
                # Review failure is non-blocking
                self.logger.warning(
                    f"Holistic review failed (non-blocking): {e}",
                    exc_info=True
                )
        
        # STEP 4: Execute orchestrator (now with optional review insights)
        exec_result = self.execute_orchestrator(
            orchestrator_id=match.orchestrator_id,
            params={
                'user_request': user_input,
                'context': enriched_context,
                'routing_match': match
            }
        )
        
        # Convert ExecutionResult to expected format
        result = type('Result', (), {
            'success': exec_result.status.value == 'success',
            'message': str(exec_result.output) if exec_result.output else "Execution completed",
            'metadata': {'orchestrator_result': exec_result.output, 'orchestrator_id': match.orchestrator_id},
            'artifacts': [],
            'user_message': None
        })()
        
        # STEP 5: Render user-facing response (NEW - Phase 6.4)
        if result.metadata.get('orchestrator_result'):
            orch_result = result.metadata['orchestrator_result']
            
            # Prepare rendering context
            render_context = {
                'phase': enriched_context.get('current_phase', 'Phase 2'),
                'orchestrator_name': match.orchestrator_id,
                'version': '6.0.0',  # CORTEX version
                'summary': getattr(result, 'message', 'Operation completed successfully.'),
                'session_id': enriched_context.get('session_id'),
                'token_usage_percentage': enriched_context.get('token_usage_percentage', 0),
                'total_tokens': enriched_context.get('total_tokens', 0),
                'security_warnings': enriched_context.get('security_warnings', []),
                'deprecated_features_used': enriched_context.get('deprecated_features_used', []),
                'success_metadata': result.metadata.get('success_metadata', {}),
                'files_modified': result.metadata.get('files_modified', False),
                'multi_phase_operation': result.metadata.get('multi_phase_operation', False),
                'progress': result.metadata.get('progress', {}),
                'next_steps': result.metadata.get('next_steps', []),
                'review_insights': enriched_context.get('review_insights', []),
                'outcomes': result.metadata.get('outcomes', []),
                'in_progress': result.metadata.get('in_progress', []),
                'risks': result.metadata.get('risks', []),
                'impact': result.metadata.get('impact', [])
            }
            
            try:
                # Step 5.1: Render markdown with operation type
                rendered_markdown = self.response_renderer.render(
                    orch_result,
                    tier='auto',
                    context=render_context,
                    operation_type=match.orchestrator_id.replace('_', ' ').title()
                )
                
                # Step 5.2: Inject system messages
                final_markdown = self.response_middleware.inject_system_messages(
                    rendered_markdown,
                    render_context
                )
                
                # Step 5.3: Store in ExecutionResult
                result.user_message = final_markdown
                
                self.logger.debug(
                    f"Rendered user message: {len(final_markdown)} chars, "
                    f"tier=auto, system_messages={(render_context.get('token_usage_percentage', 0) > 80)}"
                )
            except Exception as e:
                # Rendering failure is non-blocking - log and continue
                self.logger.warning(
                    f"Response rendering failed (non-blocking): {e}",
                    exc_info=True
                )
                result.user_message = None
        
        # STEP 6: Record session metadata for future continuations
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
        # Get orchestrator from registry with workspace_root init arg
        init_args = {
            'workspace_root': str(Path.cwd())
        }
        orchestrator = self.registry.instantiate(orchestrator_id, init_args=init_args)
        
        if not orchestrator:
            raise ValueError(f"Orchestrator not found: {orchestrator_id}")
        
        # Begin execution tracking (if supported)
        log_id = None
        if hasattr(self.state_manager, 'begin_execution'):
            log_id = self.state_manager.begin_execution(
                orchestrator_id,
                params
            )
        
        try:
            from src.orchestrators.execution_engine import ExecutionStatus
            from datetime import datetime
            import uuid
            
            # Check if orchestrator has execute method
            if hasattr(orchestrator, 'execute'):
                # Direct execution (for simple orchestrators)
                started_at = datetime.now()
                
                # Pass params to execute method - intelligently map parameters
                if params:
                    import inspect
                    sig = inspect.signature(orchestrator.execute)
                    execute_params = set(sig.parameters.keys())
                    
                    # Map params to execute method signature
                    mapped_params = {}
                    if 'context' in execute_params and 'user_request' in params:
                        # Map user_request to context for orchestrators expecting context dict
                        mapped_params['context'] = {'user_request': params['user_request']}
                    elif 'user_request' in execute_params:
                        # Pass user_request directly
                        mapped_params['user_request'] = params.get('user_request', '')
                    else:
                        # Pass all params as-is
                        mapped_params = params
                    
                    result_data = orchestrator.execute(**mapped_params)
                else:
                    result_data = orchestrator.execute()
                    
                completed_at = datetime.now()
                
                # Wrap in ExecutionResult
                result = ExecutionResult(
                    execution_id=str(uuid.uuid4()),
                    status=ExecutionStatus.SUCCESS,
                    started_at=started_at,
                    completed_at=completed_at,
                    output=result_data,
                    error=None
                )
            elif hasattr(self.execution_engine, 'run'):
                # Execute with engine (for complex orchestrators)
                result = self.execution_engine.run(
                    orchestrator=orchestrator,
                    params=params,
                    hooks=self._get_lifecycle_hooks(orchestrator_id)
                )
            else:
                # Fallback - try direct call
                started_at = datetime.now()
                result_data = orchestrator(**params) if params else orchestrator()
                completed_at = datetime.now()
                
                result = ExecutionResult(
                    execution_id=str(uuid.uuid4()),
                    status=ExecutionStatus.SUCCESS,
                    started_at=started_at,
                    completed_at=completed_at,
                    output=result_data,
                    error=None
                )
            
            # Complete execution tracking (if supported)
            if hasattr(self.state_manager, 'complete_execution'):
                self.state_manager.complete_execution(
                    orchestrator_id,
                    result.to_dict()
                )
            
            return result
            
        except Exception as e:
            # Fail execution tracking (if supported)
            if hasattr(self.state_manager, 'fail_execution'):
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
        
        CORTEX v5 Universal Pattern (C50-20):
        - Phase -2: SetupVerifier (Priority 1)
        - Runtime: GovernanceCheckpoint (Priority 20)
        - Phase N+1: TeardownRefactor (Priority 30)
        
        Args:
            orchestrator_id: Orchestrator identifier
        
        Returns:
            Dictionary of hook lists with priority-ordered middleware
        """
        # CORTEX v5 Universal Pattern Lifecycle Hooks
        return {
            'pre_execution': [
                # Priority 1: Phase -2 Setup Verification
                lambda orch, params: self.setup_verifier.verify_setup(
                    orchestrator_name=orchestrator_id,
                    dependencies=params.get('dependencies', []),
                    cache_check_enabled=True
                ),
                # Priority 20: Runtime Governance Checkpoint
                lambda orch, params: self.governance_checkpoint.checkpoint_phase_start(
                    phase_number=params.get('phase_number', 1),
                    orchestrator=orchestrator_id,
                    context=params
                ),
                # Legacy validation (kept for backwards compatibility)
                self._validate_dependencies,
                self._check_state_conflicts
            ],
            'post_execution': [
                # Priority 30: Phase N+1 Teardown + REFACTOR + Commit
                lambda orch, result: self.teardown_refactor.execute_teardown(
                    orchestrator_name=orchestrator_id,
                    modified_files=result.get('modified_files', []),
                    phase_summary=result.get('phase_summary', 'Execution complete'),
                    skip_git_commit=False
                ),
                # Runtime Governance Checkpoint (completion)
                lambda orch, result: self.governance_checkpoint.checkpoint_phase_complete(
                    phase_number=result.get('phase_number', 1),
                    orchestrator=orchestrator_id,
                    artifacts=result.get('artifacts', {})
                ),
                # Legacy hooks
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
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get Master Orchestrator statistics.
        
        Returns:
            Dictionary with routing, execution, and performance metrics
        """
        # Get component statistics
        router_stats = self.router.get_statistics()
        state_stats = self.state_manager.get_stats()
        engine_metrics = self.execution_engine.get_metrics()
        
        pattern_match_rate = (
            self._pattern_match_count / self._request_count
            if self._request_count > 0 else 0.0
        )
    def governance_to_todo_pipeline(
        self,
        request: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        AC-ORCH-007: Governance-to-Todo Pipeline.
        
        Complete pipeline:
        1. GovernanceMerger.merge_all_tiers() → unified instruction set
        2. MasterOrchestrator.evaluate(request, merged) → required_actions
        3. TodoManager.create_tasks(required_actions) → task_ids
        
        Args:
            request: User request with intent, context
        
        Returns:
            List of created task IDs
        """
        from src.orchestrators.core.governance_merger import GovernanceMerger
        from src.orchestrators.master.todo_manager import TodoManager
        
        self.logger.info(f"Starting governance-to-todo pipeline for request: {request.get('intent')}")
        
        # Step 1: GovernanceMerger.merge_all_tiers()
        merger = GovernanceMerger()
        merged_rules = merger.merge_all_tiers()
        
        self.logger.info(
            f"Governance merged: {merged_rules.get('rule_count', 0)} rules "
            f"from {merged_rules.get('tier_count', 0)} tiers"
        )
        
        # Step 2: MasterOrchestrator.evaluate(request, merged)
        required_actions = self._evaluate_request_against_governance(
            request=request,
            merged_rules=merged_rules
        )
        
        self.logger.info(f"Governance evaluation produced {len(required_actions)} required actions")
        
        # Step 3: TodoManager.create_tasks(required_actions)
        todo_manager = TodoManager()
        task_ids = []
        
        for action in required_actions:
            task = todo_manager.create_task(
                name=f"{action.get('action_type')}: {action.get('target')}",
                metadata=action
            )
            task_ids.append(task.id)
            
            self.logger.debug(f"Created task {task.id} for action: {action.get('action_id')}")
        
        self.logger.info(f"Governance-to-todo pipeline complete: {len(task_ids)} tasks created")
        
        return task_ids
    
    def _evaluate_request_against_governance(
        self,
        request: Dict[str, Any],
        merged_rules: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Evaluate request against merged governance rules.
        
        Produces required_actions that become tasks.
        
        Args:
            request: User request
            merged_rules: Merged governance rules from all tiers
        
        Returns:
            List of required_actions
        """
        intent = request.get('intent', '')
        target = request.get('target', '')
        
        # Map intent to action type
        action_type_map = {
            'implement': 'CREATE_FILE',
            'plan': 'GENERATE_DOC',
            'test': 'RUN_TEST',
            'validate': 'RUN_TEST',
            'build': 'EXECUTE_COMMAND',
            'deploy': 'EXECUTE_COMMAND'
        }
        
        action_type = action_type_map.get(intent, 'EXECUTE_COMMAND')
        
        # Extract applicable governance rules
        rules = merged_rules.get('rules', [])
        applicable_rules = []
        
        # Simple heuristic: TDD enforcement for code implementation
        if action_type == 'CREATE_FILE':
            applicable_rules.extend(['CORE-008', 'CORE-001'])  # TDD, incremental execution
        
        # Build required action
        required_action = {
            'action_id': f"action-{target}",
            'action_type': action_type,
            'target': target,
            'priority': 1 if 'CRITICAL' in str(request.get('priority', '')) else 2,
            'governance_rules_applied': applicable_rules,
            'intent': intent
        }
        
        return [required_action]

        
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
