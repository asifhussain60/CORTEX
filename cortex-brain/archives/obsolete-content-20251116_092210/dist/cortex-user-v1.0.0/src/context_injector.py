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
import logging

# Tier imports - using correct class names from CORTEX 2.0 architecture
try:
    from src.tier1.working_memory import WorkingMemory
    TIER1_AVAILABLE = True
except ImportError:
    TIER1_AVAILABLE = False

try:
    from src.tier2.knowledge_graph.knowledge_graph import KnowledgeGraph
    TIER2_AVAILABLE = True
except ImportError:
    TIER2_AVAILABLE = False

try:
    from src.tier3.context_intelligence import ContextIntelligence
    TIER3_AVAILABLE = True
except ImportError:
    TIER3_AVAILABLE = False

logger = logging.getLogger(__name__)


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
        
        # Initialize engines only if tiers are available
        self.wm = WorkingMemory(db_path) if TIER1_AVAILABLE else None
        self.kg = KnowledgeGraph() if TIER2_AVAILABLE else None
        self.ci = ContextIntelligence() if TIER3_AVAILABLE else None
        
        # Performance tracking
        self._last_injection_time_ms = 0.0
        
        if not any([TIER1_AVAILABLE, TIER2_AVAILABLE, TIER3_AVAILABLE]):
            logger.warning("No tiers available - context injection will be limited")
    
    def inject_context(self, 
                      user_request: str, 
                      conversation_id: Optional[str] = None,
                      current_file: Optional[str] = None,
                      include_tiers: Optional[Dict[str, bool]] = None) -> Dict:
        """
        Inject context from specified tiers
        
        Args:
            user_request: User's request text
            conversation_id: Current conversation (if exists)
            current_file: Current file being worked on (for namespace detection)
            include_tiers: {'tier1': True, 'tier2': True, 'tier3': True}
        
        Returns:
            {
                'tier1': {...},  # Recent conversations + entities
                'tier2': {...},  # Patterns (namespace-aware)
                'tier3': {...},  # Dev activity
                'injection_time_ms': 142.7
            }
        """
        start_time = time.perf_counter()
        
        if include_tiers is None:
            include_tiers = {'tier1': True, 'tier2': True, 'tier3': True}
        
        context = {}
        
        # Tier 1: Working Memory
        if include_tiers.get('tier1', True) and self.wm:
            context['tier1'] = self._inject_tier1(conversation_id)
        
        # Tier 2: Knowledge Graph (with namespace awareness)
        if include_tiers.get('tier2', True) and self.kg:
            context['tier2'] = self._inject_tier2(user_request, current_file)
        
        # Tier 3: Development Context
        if include_tiers.get('tier3', True) and self.ci:
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
    
    def _inject_tier2(self, user_request: str, current_file: Optional[str] = None) -> Dict:
        """
        Inject Tier 2: Relevant patterns from knowledge graph with namespace awareness
        
        Args:
            user_request: User's request text
            current_file: Current file being worked on (for namespace detection)
        
        Returns:
            {
                'patterns': [...],
                'intent_patterns': [...],
                'workflow_patterns': [...],
                'namespace': str  # Detected namespace context
            }
        """
        tier2_context = {}
        
        # Detect current application namespace from file path
        current_namespace = self._detect_namespace(current_file) if current_file else None
        tier2_context['namespace'] = current_namespace or "CORTEX-core"
        
        # Search for relevant patterns with namespace boosting
        tier2_context['patterns'] = \
            self.kg_engine.search_patterns_with_namespace(
                query=user_request, 
                current_namespace=current_namespace,
                include_generic=True,
                limit=5
            )
        
        # Intent patterns (for validation/refinement)
        tier2_context['intent_patterns'] = \
            self.kg_engine.get_intent_patterns(user_request)
        
        # Workflow patterns (successful task sequences)
        tier2_context['workflow_patterns'] = \
            self.kg_engine.get_workflow_patterns(min_confidence=0.7)
        
        return tier2_context
    
    def _detect_namespace(self, file_path: str) -> Optional[str]:
        """
        Detect application namespace from file path.
        
        Args:
            file_path: Path to current file
        
        Returns:
            Namespace string (e.g., 'KSESSIONS', 'NOOR') or None for CORTEX
        """
        if not file_path:
            return None
        
        file_path_lower = file_path.lower()
        
        # Application-specific paths
        namespace_patterns = {
            "KSESSIONS": ["spa/", "ksessions/", "host", "session", "registration"],
            "NOOR": ["noor/", "canvas", "noor-canvas"],
            "SPA": ["spa/noorcanvas/"]
        }
        
        # Check each pattern
        for namespace, patterns in namespace_patterns.items():
            if any(pattern in file_path_lower for pattern in patterns):
                return namespace
        
        # CORTEX system files
        cortex_indicators = ["cortex/src/", "prompts/", "governance/", "tier0", "tier1", "tier2", "tier3"]
        if any(indicator in file_path_lower for indicator in cortex_indicators):
            return None  # Use default CORTEX-core
        
        # Unknown/ambiguous
        return None
    
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
