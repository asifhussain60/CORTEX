"""
CORTEX Universal Router

Processes requests from cortex.md entry point with:
- Slash command expansion (optional shortcuts)
- Intent detection via Phase 4 agents
- Context injection from Tiers 1-3
- Workflow routing
- Session management
- Performance optimization (<100ms routing, <200ms context)

Author: CORTEX Development Team
Version: 1.1 (Added command support)
"""

from typing import Dict, Any, Optional
import time
import uuid
import logging
from datetime import datetime

from src.cortex_agents.strategic.intent_router import IntentRouter
from .session_manager import SessionManager
from .context_injector import ContextInjector
from .plugins.command_registry import get_command_registry
from .cortex_help import handle_help_request
from .config import ConfigManager

# Tier imports - using correct class names from CORTEX 2.0 architecture
try:
    from src.tier1.working_memory import WorkingMemory
    TIER1_AVAILABLE = True
except ImportError:
    TIER1_AVAILABLE = False
    logging.getLogger(__name__).warning("Tier1 not available - working memory features disabled")

try:
    from src.tier2.knowledge_graph import KnowledgeGraph
    TIER2_AVAILABLE = True
except ImportError:
    TIER2_AVAILABLE = False

try:
    from src.tier3.context_intelligence import ContextIntelligence
    TIER3_AVAILABLE = True
except ImportError:
    TIER3_AVAILABLE = False

logger = logging.getLogger(__name__)


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
    
    def __init__(self, db_path: str = None):
        """
        Initialize router with database connection
        
        Args:
            db_path: Path to SQLite database (deprecated - use ConfigManager)
        """
        # Use ConfigManager for tier-specific paths (CORTEX 2.0 distributed architecture)
        if db_path is None:
            config = ConfigManager()
            # Router primarily uses Tier 1 for conversations
            db_path = config.get_tier1_conversations_path()
        
        self.db_path = db_path
        self.intent_router = IntentRouter(db_path)
        self.session_manager = SessionManager(db_path)
        self.context_injector = ContextInjector(db_path)
        self.command_registry = get_command_registry()
        
        # Performance tracking
        self._last_routing_time_ms = 0.0
        self._last_context_time_ms = 0.0
    
    def process_request(self, 
                       user_request: str, 
                       conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process request from cortex.md
        
        Steps:
        1. Expand slash commands (if present)
        2. Detect intent (Phase 4: intent-router)
        3. Inject context (Tiers 1-3)
        4. Route to workflow
        5. Log interaction (Tier 1)
        
        Args:
            user_request: User's natural language request or slash command
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
                'command_used': '/mac' or None,
                'next_step': 'Execute workflow...'
            }
        """
        start_time = time.perf_counter()
        
        # Step 0: Expand slash commands to natural language (if present)
        original_request = user_request
        command_used = None
        
        # Handle /help requests immediately
        if user_request.strip().lower() in ['/help', '/h', '/?']:
            help_text = handle_help_request(user_request)
            return {
                'intent': 'HELP',
                'confidence': 1.0,
                'workflow': 'help_display',
                'context': {'help_text': help_text},
                'conversation_id': conversation_id or 'help-session',
                'routing_time_ms': 0.0,
                'context_time_ms': 0.0,
                'total_time_ms': (time.perf_counter() - start_time) * 1000,
                'command_used': user_request.strip(),
                'original_request': original_request,
                'performance_warnings': [],
                'next_step': 'Displaying help information',
                'help_text': help_text  # Include help text in response
            }
        
        if self.command_registry.is_command(user_request.strip()):
            expanded = self.command_registry.expand_command(user_request.strip())
            if expanded:
                command_used = user_request.strip()
                user_request = expanded
                logger.info(f"Command expansion: {command_used} → {user_request}")
        
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
            'command_used': command_used,  # Track if slash command was used
            'original_request': original_request,  # Preserve original for logging
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
        if not TIER1_AVAILABLE:
            logger.debug("Tier1 not available - skipping interaction logging")
            return
        
        wm = WorkingMemory(self.db_path)
        
        # Add user message
        wm.add_message(
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
        
        wm.add_message(
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
