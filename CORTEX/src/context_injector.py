"""
CORTEX Context Injector

Injects relevant context from Tiers 1-3 into workflows:
- Tier 1: Recent conversations + entities (working memory)
- Tier 2: Patterns from knowledge graph
- Tier 3: Development activity and metrics

Performance Target: <200ms total injection time

Author: CORTEX Development Team
Version: 1.0
"""

from typing import Dict, List, Optional
import time

from tier1.working_memory_engine import WorkingMemoryEngine
from tier2.knowledge_graph_engine import KnowledgeGraphEngine
from tier3.dev_context_engine import DevContextEngine


class ContextInjector:
    """
    Inject context from Tiers 1-3 into workflows
    
    Responsibilities:
    - Load recent conversations (Tier 1)
    - Load relevant patterns (Tier 2)
    - Load development metrics (Tier 3)
    - Selective tier inclusion
    - Performance optimization (<200ms)
    
    Performance Target: <200ms total
    """
    
    def __init__(self, db_path: str = "cortex-brain.db"):
        """
        Initialize context injector
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.wm_engine = WorkingMemoryEngine(db_path)
        self.kg_engine = KnowledgeGraphEngine(db_path)
        self.dc_engine = DevContextEngine(db_path)
        
        # Performance tracking
        self._last_injection_time_ms = 0.0
    
    def inject_context(self, 
                      user_request: str, 
                      conversation_id: Optional[str] = None,
                      include_tiers: Optional[Dict[str, bool]] = None) -> Dict:
        """
        Inject context from specified tiers
        
        Args:
            user_request: User's request text
            conversation_id: Current conversation (if exists)
            include_tiers: {'tier1': True, 'tier2': True, 'tier3': True}
        
        Returns:
            {
                'tier1': {...},  # Recent conversations + entities
                'tier2': {...},  # Patterns
                'tier3': {...},  # Dev activity
                'injection_time_ms': 142.7
            }
        """
        start_time = time.perf_counter()
        
        if include_tiers is None:
            include_tiers = {'tier1': True, 'tier2': True, 'tier3': True}
        
        context = {}
        
        # Tier 1: Working Memory
        if include_tiers.get('tier1', True):
            context['tier1'] = self._inject_tier1(conversation_id)
        
        # Tier 2: Knowledge Graph
        if include_tiers.get('tier2', True):
            context['tier2'] = self._inject_tier2(user_request)
        
        # Tier 3: Development Context
        if include_tiers.get('tier3', True):
            context['tier3'] = self._inject_tier3()
        
        # Calculate injection time
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        self._last_injection_time_ms = elapsed_ms
        
        context['injection_time_ms'] = elapsed_ms
        context['performance_ok'] = elapsed_ms < 200
        
        if elapsed_ms > 200:
            context['performance_warning'] = (
                f"Context injection slow: {elapsed_ms:.1f}ms (target: <200ms)"
            )
        
        return context
    
    def _inject_tier1(self, conversation_id: Optional[str] = None) -> Dict:
        """
        Inject Tier 1: Recent conversations + entities
        
        Args:
            conversation_id: Current conversation UUID
        
        Returns:
            {
                'current_conversation': {...},
                'recent_entities': [...],
                'recent_conversations': [...]
            }
        """
        tier1_context = {}
        
        # Current conversation (if exists)
        if conversation_id:
            tier1_context['current_conversation'] = \
                self.wm_engine.get_conversation(conversation_id)
        
        # Recent entities (files, components, rules mentioned in last 20 conversations)
        tier1_context['recent_entities'] = \
            self.wm_engine.extract_entities_from_recent(limit=20)
        
        # Recent conversations (summary of last 5)
        tier1_context['recent_conversations'] = \
            self.wm_engine.get_recent_conversations(limit=5)
        
        return tier1_context
    
    def _inject_tier2(self, user_request: str) -> Dict:
        """
        Inject Tier 2: Relevant patterns from knowledge graph
        
        Args:
            user_request: User's request text
        
        Returns:
            {
                'patterns': [...],
                'intent_patterns': [...],
                'workflow_patterns': [...]
            }
        """
        tier2_context = {}
        
        # Search for relevant patterns based on request
        tier2_context['patterns'] = \
            self.kg_engine.search_patterns(user_request, limit=5)
        
        # Intent patterns (for validation/refinement)
        tier2_context['intent_patterns'] = \
            self.kg_engine.get_intent_patterns(user_request)
        
        # Workflow patterns (successful task sequences)
        tier2_context['workflow_patterns'] = \
            self.kg_engine.get_workflow_patterns(min_confidence=0.7)
        
        return tier2_context
    
    def _inject_tier3(self) -> Dict:
        """
        Inject Tier 3: Recent development activity and metrics
        
        Returns:
            {
                'recent_activity': {...},
                'active_files': [...],
                'performance_trends': {...}
            }
        """
        tier3_context = {}
        
        # Recent activity (last 24 hours)
        tier3_context['recent_activity'] = \
            self.dc_engine.get_recent_activity(hours=24)
        
        # Active files (last 48 hours)
        tier3_context['active_files'] = \
            self.dc_engine.get_active_files(hours=48)
        
        # Performance trends (last 7 days)
        tier3_context['performance_trends'] = \
            self.dc_engine.get_performance_trends(days=7)
        
        return tier3_context
    
    def get_injection_stats(self) -> Dict:
        """
        Get recent injection performance statistics
        
        Returns:
            {
                'last_injection_ms': 142.7,
                'target_ms': 200,
                'performance_ok': True
            }
        """
        return {
            'last_injection_ms': self._last_injection_time_ms,
            'target_ms': 200,
            'performance_ok': self._last_injection_time_ms < 200
        }
