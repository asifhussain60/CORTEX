"""
CORTEX Universal Router

Processes requests from cortex.md entry point with:
- Intent detection via Phase 4 agents
- Context injection from Tiers 1-3
- Workflow routing
- Session management
- Performance optimization (<100ms routing, <200ms context)

Author: CORTEX Development Team
Version: 1.0
"""

from typing import Dict, Any, Optional
import time
import uuid
from datetime import datetime

from cortex_agents.strategic.intent_router import IntentRouter
from tier1.working_memory_engine import WorkingMemoryEngine
from tier2.knowledge_graph_engine import KnowledgeGraphEngine
from tier3.dev_context_engine import DevContextEngine
from .session_manager import SessionManager
from .context_injector import ContextInjector


class CortexRouter:
    """
    Universal router for cortex.md entry point
    
    Responsibilities:
    - Extract user request from cortex.md
    - Detect intent via Phase 4 agents
    - Inject context from Tiers 1-3
    - Route to appropriate workflow
    - Log interaction to Tier 1
    
    Performance Targets:
    - Intent detection: <100ms
    - Context injection: <200ms
    - Total routing: <300ms
    """
    
    def __init__(self, db_path: str = "cortex-brain.db"):
        """
        Initialize router with database connection
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.intent_router = IntentRouter(db_path)
        self.session_manager = SessionManager(db_path)
        self.context_injector = ContextInjector(db_path)
        
        # Performance tracking
        self._last_routing_time_ms = 0.0
        self._last_context_time_ms = 0.0
    
    def process_request(self, 
                       user_request: str, 
                       conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process request from cortex.md
        
        Steps:
        1. Detect intent (Phase 4: intent-router)
        2. Inject context (Tiers 1-3)
        3. Route to workflow
        4. Log interaction (Tier 1)
        
        Args:
            user_request: User's natural language request
            conversation_id: Optional existing conversation ID
        
        Returns:
            {
                'intent': 'PLAN',
                'confidence': 0.95,
                'workflow': 'feature_creation',
                'context': {...},
                'conversation_id': 'uuid-here',
                'routing_time_ms': 85.3,
                'context_time_ms': 142.7,
                'total_time_ms': 228.0,
                'next_step': 'Execute workflow...'
            }
        """
        start_time = time.perf_counter()
        
        # Step 1: Detect intent (Performance target: <100ms)
        intent_start = time.perf_counter()
        intent_result = self.intent_router.route_request(user_request)
        intent_time_ms = (time.perf_counter() - intent_start) * 1000
        self._last_routing_time_ms = intent_time_ms
        
        # Step 2: Inject context from Tiers 1-3 (Performance target: <200ms)
        context_start = time.perf_counter()
        
        # Get or create conversation session
        if not conversation_id:
            conversation_id = self.session_manager.get_active_session()
            if not conversation_id:
                # Start new session
                conversation_id = self.session_manager.start_session(
                    intent=intent_result['intent']
                )
        
        context = self.context_injector.inject_context(
            user_request=user_request,
            conversation_id=conversation_id
        )
        context_time_ms = (time.perf_counter() - context_start) * 1000
        self._last_context_time_ms = context_time_ms
        
        # Step 3: Select workflow based on intent
        workflow = self._select_workflow(intent_result, context)
        
        # Step 4: Log interaction to Tier 1 (working memory)
        self._log_interaction(
            conversation_id=conversation_id,
            user_request=user_request,
            intent=intent_result['intent'],
            workflow=workflow
        )
        
        # Calculate total time
        total_time_ms = (time.perf_counter() - start_time) * 1000
        
        # Performance validation
        performance_warnings = []
        if intent_time_ms > 100:
            performance_warnings.append(
                f"⚠️ Intent detection slow: {intent_time_ms:.1f}ms (target: <100ms)"
            )
        if context_time_ms > 200:
            performance_warnings.append(
                f"⚠️ Context injection slow: {context_time_ms:.1f}ms (target: <200ms)"
            )
        if total_time_ms > 300:
            performance_warnings.append(
                f"⚠️ Total routing slow: {total_time_ms:.1f}ms (target: <300ms)"
            )
        
        return {
            'intent': intent_result['intent'],
            'confidence': intent_result['confidence'],
            'workflow': workflow,
            'context': context,
            'conversation_id': conversation_id,
            'routing_time_ms': intent_time_ms,
            'context_time_ms': context_time_ms,
            'total_time_ms': total_time_ms,
            'performance_warnings': performance_warnings,
            'next_step': self._get_next_step(workflow, intent_result)
        }
    
    def _select_workflow(self, 
                        intent_result: Dict[str, Any], 
                        context: Dict[str, Any]) -> str:
        """
        Select appropriate workflow based on intent and context
        
        Args:
            intent_result: Result from intent router
            context: Injected context from Tiers 1-3
        
        Returns:
            Workflow name ('feature_creation', 'tdd_implementation', etc.)
        """
        intent = intent_result['intent']
        
        # Workflow mapping based on intent
        workflow_mapping = {
            'PLAN': 'feature_creation',
            'EXECUTE': 'tdd_implementation',
            'TEST': 'test_validation',
            'FIX': 'bug_fix',
            'QUERY': 'knowledge_query',
            'VALIDATE': 'health_validation'
        }
        
        workflow = workflow_mapping.get(intent, 'feature_creation')
        
        # Context-based workflow refinement
        # If context shows active feature work, prefer TDD workflow
        if context.get('tier3', {}).get('active_files'):
            if intent == 'EXECUTE':
                workflow = 'tdd_implementation'
        
        return workflow
    
    def _log_interaction(self, 
                        conversation_id: str,
                        user_request: str,
                        intent: str,
                        workflow: str) -> None:
        """
        Log interaction to Tier 1 (working memory)
        
        Args:
            conversation_id: Current conversation UUID
            user_request: User's request text
            intent: Detected intent
            workflow: Selected workflow
        """
        from tier1.working_memory_engine import WorkingMemoryEngine
        
        wm_engine = WorkingMemoryEngine(self.db_path)
        
        # Add user message
        wm_engine.add_message(
            conversation_id=conversation_id,
            role='user',
            content=user_request
        )
        
        # Add system message with routing info
        system_message = (
            f"Intent: {intent} (workflow: {workflow})\n"
            f"Routing: {self._last_routing_time_ms:.1f}ms\n"
            f"Context: {self._last_context_time_ms:.1f}ms"
        )
        
        wm_engine.add_message(
            conversation_id=conversation_id,
            role='system',
            content=system_message
        )
    
    def _get_next_step(self, workflow: str, intent_result: Dict[str, Any]) -> str:
        """
        Get human-readable next step description
        
        Args:
            workflow: Selected workflow
            intent_result: Intent detection result
        
        Returns:
            Description of next step
        """
        next_steps = {
            'feature_creation': 'Creating multi-phase plan via work-planner agent...',
            'tdd_implementation': 'Starting TDD cycle (RED → GREEN → REFACTOR)...',
            'test_validation': 'Running test suite and validating coverage...',
            'bug_fix': 'Analyzing error logs and creating fix plan...',
            'knowledge_query': 'Searching knowledge graph and conversations...',
            'health_validation': 'Running health checks and DoD validation...'
        }
        
        return next_steps.get(workflow, 'Processing request...')
    
    def get_performance_stats(self) -> Dict[str, float]:
        """
        Get recent performance statistics
        
        Returns:
            {
                'last_routing_ms': 85.3,
                'last_context_ms': 142.7,
                'routing_target_ms': 100,
                'context_target_ms': 200,
                'total_target_ms': 300
            }
        """
        return {
            'last_routing_ms': self._last_routing_time_ms,
            'last_context_ms': self._last_context_time_ms,
            'routing_target_ms': 100,
            'context_target_ms': 200,
            'total_target_ms': 300,
            'routing_ok': self._last_routing_time_ms < 100,
            'context_ok': self._last_context_time_ms < 200
        }
