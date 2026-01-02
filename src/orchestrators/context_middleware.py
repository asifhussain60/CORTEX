"""
Cross-Session Context Middleware.

Pre-routing enrichment layer that injects lightweight session context
from Tier 1 Working Memory into Master Orchestrator requests.

Part of CORTEX v5 Phase 4.5: Enables continuation across chat sessions
without losing user context.

Architecture:
    User Input → Middleware (continuation detection)
              ↓
          Query Tier 1 (last 3 sessions)
              ↓
          Inject metadata (<200 tokens)
              ↓
          Pass to Master Orchestrator

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
    
    def __init__(self, session_manager: Optional[Any] = None):
        """
        Initialize context middleware.
        
        Args:
            session_manager: Tier 1 SessionManager instance.
                           If None, creates default instance.
        """
        if session_manager is None:
            # Late import to avoid circular dependencies
            from src.tier1.sessions.session_manager import SessionManager
            db_path = Path("cortex-brain/tier1/working_memory.db")
            self.session_manager = SessionManager(db_path)
        else:
            self.session_manager = session_manager
        
        self.logger = logging.getLogger("cortex.orchestrators.context_middleware")
        
        # Compile continuation patterns for performance
        self._continuation_regex = re.compile(
            '|'.join(self.CONTINUATION_PATTERNS),
            re.IGNORECASE
        )
        
        self.logger.info("CrossSessionContextMiddleware initialized")
    
    def enrich_context(
        self,
        user_input: str,
        existing_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Enrich routing context with cross-session metadata if continuation detected.
        
        Args:
            user_input: User's natural language request
            existing_context: Optional existing context dict
        
        Returns:
            Enriched context dict with 'recent_activity' if continuation detected,
            otherwise returns existing_context unchanged
        
        Example Output:
            {
                "recent_activity": [
                    {
                        "session_id": "session-20260102-101500",
                        "orchestrator": "planning_v5",
                        "intent": "plan user authentication",
                        "artifacts": ["plan-001", "00-master-plan.md"],
                        "timestamp": "2026-01-02T10:15:00Z"
                    }
                ],
                "continuation_detected": true,
                "context_source": "tier1_working_memory"
            }
        """
        context = existing_context.copy() if existing_context else {}
        
        # Check if continuation pattern detected
        if not self._is_continuation(user_input):
            self.logger.debug("No continuation pattern detected")
            return context
        
        self.logger.info("Continuation pattern detected, injecting session context")
        
        # Query Tier 1 for recent sessions
        try:
            recent_sessions = self.session_manager.get_recent_session_context(limit=3)
        except Exception as e:
            self.logger.error(f"Failed to query Tier 1 for session context: {e}")
            return context
        
        if not recent_sessions:
            self.logger.warning("No recent sessions found in Tier 1")
            return context
        
        # Inject lightweight metadata
        context['recent_activity'] = recent_sessions
        context['continuation_detected'] = True
        context['context_source'] = 'tier1_working_memory'
        
        last_orch = recent_sessions[0]['orchestrator']
        self.logger.info(
            f"Injected {len(recent_sessions)} session(s) metadata "
            f"(last orchestrator: {last_orch})"
        )
        
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
        
        Args:
            user_input: User's natural language request
            existing_context: Optional existing context dict
        
        Returns:
            Orchestrator ID from last session, or None if not continuation
        
        Example:
            middleware.get_last_orchestrator("continue")  # → "planning_v5"
            middleware.get_last_orchestrator("plan X")    # → None
        """
        enriched = self.enrich_context(user_input, existing_context)
        
        if 'recent_activity' in enriched and enriched['recent_activity']:
            return enriched['recent_activity'][0]['orchestrator']
        
        return None
    
    def get_context_token_count(self, context: Dict[str, Any]) -> int:
        """
        Estimate token count for injected context.
        
        Used for monitoring token efficiency.
        
        Args:
            context: Enriched context dict
        
        Returns:
            Estimated token count (rough approximation: chars / 4)
        """
        if 'recent_activity' not in context:
            return 0
        
        import json
        context_json = json.dumps(context['recent_activity'])
        
        # Rough token estimate: 1 token ≈ 4 characters
        return len(context_json) // 4
