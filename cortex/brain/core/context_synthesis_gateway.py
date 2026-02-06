"""
Context Synthesis Gateway (ENH-046 Phase 1.6)

Purpose: Orchestration layer for incremental context loading + EXIT GATE
Architecture: Coordinates IncrementalContextLoader + TokenDistillationEngine
Integration: Wires into MasterOrchestrator.execute_operation()

EXIT GATE: Before MasterOrchestrator begins, synthesize minimal context
Strategy: Load 250 tokens initially, distill on-demand loads to ≤500 tokens

Author: CORTEX Architect
Created: 2026-02-06
Version: 1.0.0
"""

import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from cortex.brain.core.incremental_context_loader import IncrementalContextLoader
from cortex.brain.core.token_distillation_engine import TokenDistillationEngine
from cortex.brain.core.context_cache_layer import ContextCacheLayer

logger = logging.getLogger(__name__)


@dataclass
class SynthesisSession:
    """Track context synthesis for a single user request"""
    session_id: str
    intent: str
    initial_tokens: int
    incremental_tokens: int
    total_tokens: int
    cache_hits: int
    cache_misses: int
    synthesis_time_ms: float
    budget_remaining: int


class ContextSynthesisGateway:
    """
    Orchestration layer for incremental context loading
    
    Responsibilities:
    - Coordinate IncrementalContextLoader + TokenDistillationEngine
    - Enforce token budgets (250 init, ≤500 per load)
    - Track session metrics (cache hits, synthesis time)
    - Provide EXIT GATE for MasterOrchestrator
    
    Flow:
      1. User request → EXIT GATE (before MasterOrchestrator)
      2. Get minimal initial context (250 tokens)
      3. Determine intent (AUDIT, DESIGN, IMPLEMENT, etc.)
      4. Load on-demand context (≤500 tokens, distilled)
      5. Return synthesized context → MasterOrchestrator
    """
    
    def __init__(
        self,
        workspace_root: Path,
        initial_budget: int = 250,
        incremental_budget: int = 500,
        session_budget: int = 2000
    ):
        """
        Initialize context synthesis gateway
        
        Args:
            workspace_root: Root directory of workspace
            initial_budget: Max tokens for initial context (default 250)
            incremental_budget: Max tokens per incremental load (default 500)
            session_budget: Max tokens per session (default 2000)
        """
        self.workspace_root = workspace_root
        self.initial_budget = initial_budget
        self.incremental_budget = incremental_budget
        self.session_budget = session_budget
        
        # Initialize components
        self._cache = ContextCacheLayer(max_entries=100, default_ttl=600)
        self._loader = IncrementalContextLoader(workspace_root)
        self._distiller = TokenDistillationEngine(workspace_root)
        
        # Session tracking
        self._sessions: Dict[str, SynthesisSession] = {}
        self._session_counter = 0
    
    def synthesize_context(
        self,
        request: str,
        intent: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synthesize context for user request (EXIT GATE entry point)
        
        This is the main entry point called before MasterOrchestrator.execute_operation()
        
        Args:
            request: User request text
            intent: Optional explicit intent (AUDIT, DESIGN, IMPLEMENT, etc.)
            session_id: Optional session ID for tracking
        
        Returns:
            Dict with synthesized context + session metadata
        """
        start_time = time.time()
        
        # Create or retrieve session
        if not session_id:
            session_id = f"session-{self._session_counter}"
            self._session_counter += 1
        
        # Step 1: Get minimal initial context (250 tokens)
        initial_context = self._loader.get_initial_context()
        initial_tokens = self._loader.estimate_tokens(initial_context)
        
        # Step 2: Determine intent if not provided
        if not intent:
            intent = self._infer_intent(request)
        
        # Step 3: Load on-demand context for intent
        incremental_context = self._loader.load_for_intent(intent, request)
        incremental_tokens = self._loader.estimate_tokens(incremental_context)
        
        # Step 4: Distill if over budget
        if incremental_tokens > self.incremental_budget:
            logger.info(
                f"Incremental context {incremental_tokens} tokens > {self.incremental_budget} budget, distilling..."
            )
            distilled = self._distill_context(incremental_context, intent)
            incremental_context = distilled["content"]
            incremental_tokens = distilled["tokens"]
        
        # Step 5: Synthesize final context
        total_tokens = initial_tokens + incremental_tokens
        budget_remaining = self.session_budget - total_tokens
        
        # Track session
        synthesis_time_ms = (time.time() - start_time) * 1000
        cache_stats = self._cache.get_stats()
        session = SynthesisSession(
            session_id=session_id,
            intent=intent,
            initial_tokens=initial_tokens,
            incremental_tokens=incremental_tokens,
            total_tokens=total_tokens,
            cache_hits=cache_stats.hits,
            cache_misses=cache_stats.misses,
            synthesis_time_ms=synthesis_time_ms,
            budget_remaining=budget_remaining
        )
        self._sessions[session_id] = session
        
        logger.info(
            f"Context synthesized: {total_tokens} tokens ({initial_tokens} init + {incremental_tokens} incremental), "
            f"{synthesis_time_ms:.1f}ms, budget remaining: {budget_remaining}"
        )
        
        return {
            "initial_context": initial_context,
            "incremental_context": incremental_context,
            "total_tokens": total_tokens,
            "session": session,
            "intent": intent,
            "budget_remaining": budget_remaining,
            "synthesis_time_ms": synthesis_time_ms
        }
    
    def _infer_intent(self, request: str) -> str:
        """
        Infer intent from request text (simplified LENS classification)
        
        Args:
            request: User request text
        
        Returns:
            Inferred intent (AUDIT, DESIGN, IMPLEMENT, FIX, REFACTOR, ANALYZE, TEST, ONBOARD)
        """
        request_lower = request.lower()
        
        # Intent keywords (simplified)
        intent_keywords = {
            "AUDIT": ["audit", "health", "check", "violations", "p0", "p1", "issues"],
            "DESIGN": ["design", "architecture", "challenge", "alternatives", "approach"],
            "IMPLEMENT": ["implement", "create", "add", "build", "develop", "feature"],
            "FIX": ["fix", "bug", "error", "issue", "problem", "broken"],
            "REFACTOR": ["refactor", "improve", "optimize", "clean", "restructure"],
            "ANALYZE": ["analyze", "metrics", "lens", "insights", "review"],
            "TEST": ["test", "testing", "validate", "verify", "pytest"],
            "ONBOARD": ["onboard", "setup", "initialize", "repository", "scan"]
        }
        
        # Count keyword matches
        intent_scores = {}
        for intent, keywords in intent_keywords.items():
            score = sum(1 for kw in keywords if kw in request_lower)
            if score > 0:
                intent_scores[intent] = score
        
        # Return intent with highest score, default to ANALYZE
        if intent_scores:
            return max(intent_scores.items(), key=lambda x: x[1])[0]
        else:
            return "ANALYZE"
    
    def _distill_context(self, context: Dict[str, Any], intent: str) -> Dict[str, Any]:
        """
        Distill context to fit budget using TokenDistillationEngine
        
        Args:
            context: Context dict with content to distill
            intent: Intent for context-aware distillation
        
        Returns:
            Dict with distilled content + token count
        """
        # Determine content type based on intent
        content_type_map = {
            "AUDIT": "agent",
            "DESIGN": "agent",
            "IMPLEMENT": "source",
            "FIX": "source",
            "REFACTOR": "source",
            "ANALYZE": "yaml",
            "TEST": "source",
            "ONBOARD": "yaml"
        }
        content_type = content_type_map.get(intent, "yaml")
        
        # Extract content to distill
        if isinstance(context, dict):
            # Distill all string values in dict
            distilled_parts = []
            for key, value in context.items():
                if isinstance(value, str) and len(value) > 100:
                    result = self._distiller.distill(value, content_type, key)
                    distilled_parts.append(result.content)
                elif isinstance(value, str):
                    distilled_parts.append(value)
            
            distilled_content = "\n".join(distilled_parts)
        else:
            # Distill string directly
            result = self._distiller.distill(str(context), content_type)
            distilled_content = result.content
        
        return {
            "content": distilled_content,
            "tokens": self._loader.estimate_tokens(distilled_content)
        }
    
    def get_session(self, session_id: str) -> Optional[SynthesisSession]:
        """
        Get session by ID
        
        Args:
            session_id: Session ID
        
        Returns:
            SynthesisSession or None if not found
        """
        return self._sessions.get(session_id)
    
    def get_all_sessions(self) -> List[SynthesisSession]:
        """
        Get all tracked sessions
        
        Returns:
            List of all SynthesisSessions
        """
        return list(self._sessions.values())
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dict with cache stats (hits, misses, hit rate, size)
        """
        stats = self._cache.get_stats()
        return {
            "hits": stats.hits,
            "misses": stats.misses,
            "evictions": stats.evictions,
            "size": stats.size,
            "max_size": stats.max_size,
            "hit_rate": stats.hit_rate()
        }
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear session by ID
        
        Args:
            session_id: Session ID to clear
        
        Returns:
            True if session existed and was cleared
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    def clear_all_sessions(self):
        """Clear all tracked sessions"""
        self._sessions.clear()
        self._session_counter = 0
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get aggregate metrics across all sessions
        
        Returns:
            Dict with aggregate metrics
        """
        if not self._sessions:
            return {
                "total_sessions": 0,
                "average_synthesis_time_ms": 0,
                "average_tokens_per_session": 0,
                "cache_hit_rate": 0
            }
        
        sessions = list(self._sessions.values())
        
        return {
            "total_sessions": len(sessions),
            "average_synthesis_time_ms": sum(s.synthesis_time_ms for s in sessions) / len(sessions),
            "average_tokens_per_session": sum(s.total_tokens for s in sessions) / len(sessions),
            "total_cache_hits": sum(s.cache_hits for s in sessions),
            "total_cache_misses": sum(s.cache_misses for s in sessions),
            "cache_hit_rate": self._cache.get_hit_rate()
        }


def create_exit_gate(workspace_root: Path) -> ContextSynthesisGateway:
    """
    Factory function to create EXIT GATE for MasterOrchestrator
    
    Usage in MasterOrchestrator.execute_operation():
      exit_gate = create_exit_gate(workspace_root)
      context = exit_gate.synthesize_context(request, intent)
      # ... proceed with orchestration using context ...
    
    Args:
        workspace_root: Workspace root directory
    
    Returns:
        Configured ContextSynthesisGateway
    """
    return ContextSynthesisGateway(
        workspace_root=workspace_root,
        initial_budget=250,
        incremental_budget=500,
        session_budget=2000
    )
