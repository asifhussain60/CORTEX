"""
Cross-Session Context Middleware.

Pre-routing enrichment layer that injects lightweight session context
from Tier 1 Working Memory into Master Orchestrator requests.

Part of CORTEX v5 Phase 4.5: Enables continuation across chat sessions
without losing user context.

Architecture:
    User Input → Middleware (continuation detection)
              ↓
          Query Tier 1 (orchestrator sessions OR active projects)
              ↓
          Inject metadata (<200 tokens)
              ↓
          Pass to Master Orchestrator

Option B Enhancement: Supports both orchestrator-level and project-level continuations.
- Orchestrator continuation: "continue" after TDD/Debug/ADO session
- Project continuation: "continue" with active planning project

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import re
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path


class CrossSessionContextMiddleware:
    """
    Middleware for cross-session context injection.
    
    Detects continuation patterns ("continue", "resume", "next phase") and
    enriches routing requests with lightweight session metadata from
    Tier 1 Working Memory.
    
    Token Efficiency: 200 tokens (metadata) vs 50,000 tokens (full conversation)
    = 99.6% reduction
    
    Usage:
        from src.tier1.sessions.session_manager import SessionManager
        
        session_mgr = SessionManager(Path("cortex-brain/tier1/working_memory.db"))
        middleware = CrossSessionContextMiddleware(session_manager=session_mgr)
        
        enriched_context = middleware.enrich_context(
            user_input="continue",
            existing_context={}
        )
        
        master_orch.handle_request(user_input, enriched_context)
    """
    
    # Continuation patterns (aligned with ExecutionModeDetector)
    CONTINUATION_PATTERNS = [
        r'\bcontinue\b',
        r'\bresume\b',
        r'\bkeep going\b',
        r'\bnext phase\b',
        r'\bproceed\b',
        r'\bcontinue with\b',
        r'\bresume execution\b',
        r'\bnext\b'
    ]
    
    def __init__(self, session_manager: Optional[Any] = None, project_tracker: Optional[Any] = None):
        """
        Initialize context middleware.
        
        Args:
            session_manager: Tier 1 SessionManager instance.
                           If None, creates default instance.
            project_tracker: Tier 1 ProjectTracker instance.
                           If None, creates default instance.
        """
        if session_manager is None:
            # Late import to avoid circular dependencies
            from src.tier1.sessions.session_manager import SessionManager
            db_path = Path("cortex-brain/tier1/working_memory.db")
            self.session_manager = SessionManager(db_path)
        else:
            self.session_manager = session_manager
        
        if project_tracker is None:
            # Late import to avoid circular dependencies
            from src.tier1.project_tracker import ProjectTracker
            db_path = Path("cortex-brain/tier1/working_memory.db")
            self.project_tracker = ProjectTracker(db_path)
        else:
            self.project_tracker = project_tracker
        
        self.logger = logging.getLogger("cortex.orchestrators.context_middleware")
        
        # Compile continuation patterns for performance
        self._continuation_regex = re.compile(
            '|'.join(self.CONTINUATION_PATTERNS),
            re.IGNORECASE
        )
        
        self.logger.info("CrossSessionContextMiddleware initialized with project tracking")
    
    def enrich_context(
        self,
        user_input: str,
        existing_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Enrich routing context with cross-session metadata if continuation detected.
        
        Two-tier fallback:
        1. Check for orchestrator session (TDD, Debug, ADO, etc.)
        2. If none, check for active planning project
        
        Args:
            user_input: User's natural language request
            existing_context: Optional existing context dict
        
        Returns:
            Enriched context dict with 'recent_activity' and/or 'active_project'
            if continuation detected, otherwise returns existing_context unchanged
        
        Example Output (Orchestrator Session):
            {
                "recent_activity": [
                    {
                        "session_id": "session-20260102-101500",
                        "orchestrator": "tdd_master",
                        "intent": "run tests for auth module",
                        "artifacts": ["test_results.json"],
                        "timestamp": "2026-01-02T10:15:00Z"
                    }
                ],
                "continuation_detected": true,
                "continuation_type": "orchestrator_session",
                "context_source": "tier1_working_memory"
            }
        
        Example Output (Project Continuation):
            {
                "active_project": {
                    "project_id": "cortex-v5-holistic-refactor",
                    "plan_name": "CORTEX v5 Holistic Refactor",
                    "current_phase": "Phase 5",
                    "current_task": "Task 5.1",
                    "last_completed": "Phase 5.1a",
                    "progress": 40,
                    "next_action": "/CORTEX Plan ADO Orchestrator v2 Migration",
                    "orchestrator": "planning_v5"
                },
                "continuation_detected": true,
                "continuation_type": "active_project",
                "context_source": "tier1_project_tracker"
            }
        """
        context = existing_context.copy() if existing_context else {}
        
        # Check if continuation pattern detected
        if not self._is_continuation(user_input):
            self.logger.debug("No continuation pattern detected")
            return context
        
        self.logger.info("Continuation pattern detected, checking session and project context")
        
        # TIER 1: Check for orchestrator session
        try:
            recent_sessions = self.session_manager.get_recent_session_context(limit=3)
        except Exception as e:
            self.logger.error(f"Failed to query Tier 1 for session context: {e}")
            recent_sessions = []
        
        if recent_sessions:
            # Orchestrator session found - inject session context
            context['recent_activity'] = recent_sessions
            context['continuation_detected'] = True
            context['continuation_type'] = 'orchestrator_session'
            context['context_source'] = 'tier1_working_memory'
            
            last_orch = recent_sessions[0]['orchestrator']
            self.logger.info(
                f"Injected {len(recent_sessions)} orchestrator session(s) metadata "
                f"(last orchestrator: {last_orch})"
            )
            return context
        
        # TIER 2: Check for active planning project
        try:
            project_context = self.project_tracker.get_lightweight_project_context()
        except Exception as e:
            self.logger.error(f"Failed to query Tier 1 for project context: {e}")
            project_context = None
        
        if project_context:
            # Active project found - inject project context
            context['active_project'] = project_context
            context['continuation_detected'] = True
            context['continuation_type'] = 'active_project'
            context['context_source'] = 'tier1_project_tracker'
            
            self.logger.info(
                f"Injected active project context: {project_context['project_id']} "
                f"({project_context['progress']}% complete, next: {project_context.get('current_task', 'N/A')})"
            )
            return context
        
        # No continuation context found
        self.logger.warning("Continuation pattern detected but no session or project context found")
        return context
    
    def _is_continuation(self, user_input: str) -> bool:
        """
        Check if user input matches continuation patterns.
        
        Args:
            user_input: User's natural language request
        
        Returns:
            True if continuation pattern detected, False otherwise
        """
        return bool(self._continuation_regex.search(user_input))
    
    def get_last_orchestrator(
        self,
        user_input: str,
        existing_context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Get last used orchestrator if continuation detected.
        
        Convenience method for Master Orchestrator routing.
        Checks both orchestrator sessions and active projects.
        
        Args:
            user_input: User's natural language request
            existing_context: Optional existing context dict
        
        Returns:
            Orchestrator ID from last session or active project, or None if not continuation
        
        Example:
            middleware.get_last_orchestrator("continue")  # → "planning_v5" (from project)
            middleware.get_last_orchestrator("resume")    # → "tdd_master" (from session)
            middleware.get_last_orchestrator("plan X")    # → None
        """
        enriched = self.enrich_context(user_input, existing_context)
        
        # Check orchestrator session first (higher priority)
        if 'recent_activity' in enriched and enriched['recent_activity']:
            return enriched['recent_activity'][0]['orchestrator']
        
        # Check active project second
        if 'active_project' in enriched and enriched['active_project']:
            return enriched['active_project'].get('orchestrator', 'planning_v5')
        
        return None
    
    def get_context_token_count(self, context: Dict[str, Any]) -> int:
        """
        Estimate token count for injected context.
        
        Used for monitoring token efficiency. Handles both orchestrator
        sessions (recent_activity) and project context (active_project).
        
        Args:
            context: Enriched context dict
        
        Returns:
            Estimated token count (rough approximation: chars / 4)
        """
        import json
        
        # Calculate tokens for orchestrator session context
        session_tokens = 0
        if 'recent_activity' in context:
            context_json = json.dumps(context['recent_activity'])
            session_tokens = len(context_json) // 4
        
        # Calculate tokens for project context
        project_tokens = 0
        if 'active_project' in context:
            project_json = json.dumps(context['active_project'])
            project_tokens = len(project_json) // 4
        
        return session_tokens + project_tokens
