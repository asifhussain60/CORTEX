"""
CORTEX Tier 1: Working Memory (Modularized)
Short-term memory storage with FIFO queue (20 conversation limit).

This is a facade that coordinates between modular components while maintaining
backward compatibility with the original API.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

# Import modular components
from .conversations import ConversationManager, ConversationSearch, Conversation
from .messages import MessageStore
from .entities import EntityExtractor, EntityType, Entity
from .fifo import QueueManager

# Import Phase 1.5: Token Optimization System
from .ml_context_optimizer import MLContextOptimizer
from .cache_monitor import CacheMonitor
from .token_metrics import TokenMetricsCollector


class WorkingMemory:
    """
    Tier 1: Working Memory (Short-Term Memory) - Modular Facade
    
    Manages recent conversations with FIFO eviction when capacity (20) is reached.
    Stores conversations, messages, and extracted entities in SQLite.
    
    This class acts as a facade, delegating to specialized modules while
    maintaining full backward compatibility with the original API.
    """
    
    MAX_CONVERSATIONS = 20
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize working memory.
        
        Args:
            db_path: Path to SQLite database. If None, uses default location.
        """
        if db_path is None:
            db_path = Path("cortex-brain/tier1/working_memory.db")
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema
        self._init_database()
        
        # Initialize modular components
        self.conversation_manager = ConversationManager(self.db_path)
        self.conversation_search = ConversationSearch(self.db_path)
        self.message_store = MessageStore(self.db_path)
        self.entity_extractor = EntityExtractor(self.db_path)
        self.queue_manager = QueueManager(self.db_path)
        
        # Initialize Phase 1.5: Token Optimization System
        # Note: target_reduction is set via config at optimization time
        self.ml_optimizer = None  # Will be created with config params when needed
        self.cache_monitor = CacheMonitor(self)  # Pass WorkingMemory instance
        self.token_metrics = TokenMetricsCollector(self)  # Pass WorkingMemory instance
        
        # Load configuration
        self.config = self._load_config()
        self.optimization_enabled = self.config.get('token_optimization', {}).get('enabled', True)
    
    def _init_database(self) -> None:
        """Initialize database schema."""
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 0,
                summary TEXT,
                tags TEXT
            )
        """)
        
        # Create entities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,
                entity_name TEXT NOT NULL,
                file_path TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 1,
                UNIQUE(entity_type, entity_name, file_path)
            )
        """)
        
        # Create conversation-entity relationships table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_entities (
                conversation_id TEXT NOT NULL,
                entity_id INTEGER NOT NULL,
                relevance_score REAL DEFAULT 1.0,
                PRIMARY KEY (conversation_id, entity_id),
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id),
                FOREIGN KEY (entity_id) REFERENCES entities(id)
            )
        """)
        
        # Create messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
        """)
        
        # Create eviction log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eviction_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        """)
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_created 
            ON conversations(created_at DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_active 
            ON conversations(is_active)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_entities_type 
            ON entities(entity_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_entities_accessed 
            ON entities(last_accessed DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_conversation 
            ON messages(conversation_id)
        """)
        
        conn.commit()
        conn.close()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load CORTEX configuration from cortex.config.json."""
        config_path = Path("cortex.config.json")
        
        if not config_path.exists():
            # Return default configuration
            return {
                'token_optimization': {
                    'enabled': True,
                    'soft_limit': 40000,
                    'hard_limit': 50000,
                    'target_reduction': 0.6,  # 50-70% reduction
                    'quality_threshold': 0.9,
                    'cache_check_frequency': 5  # Check every 5 requests
                }
            }
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[CORTEX] Warning: Failed to load config: {e}")
            return {'token_optimization': {'enabled': True}}
    
    # ========== Context Optimization (Phase 1.5) ==========
    
    def get_optimized_context(
        self,
        conversation_id: Optional[str] = None,
        pattern_context: Optional[List[Dict[str, Any]]] = None,
        target_reduction: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get optimized context for a request (Phase 1.5 integration).
        
        Retrieves conversation and pattern context, applies ML-based optimization
        to reduce token usage while maintaining quality, and tracks metrics.
        
        Args:
            conversation_id: Optional conversation to optimize. If None, uses active.
            pattern_context: Optional list of knowledge graph patterns to optimize.
            target_reduction: Optional target reduction ratio (0.0-1.0). Uses config default if None.
        
        Returns:
            Dict with:
                - original_context: Original unoptimized context
                - optimized_context: ML-optimized context (if enabled)
                - optimization_stats: Metrics (token counts, reduction rate, quality score)
                - cache_health: Current cache health report
        """
        # Get configuration
        opt_config = self.config.get('token_optimization', {})
        enabled = opt_config.get('enabled', True) and self.optimization_enabled
        
        if target_reduction is None:
            target_reduction = opt_config.get('target_reduction', 0.6)
        
        quality_threshold = opt_config.get('quality_threshold', 0.9)
        
        # Initialize optimizer with target reduction if needed
        if enabled and self.ml_optimizer is None:
            self.ml_optimizer = MLContextOptimizer(
                target_reduction=target_reduction,
                min_quality=quality_threshold
            )
        
        # Build original context
        original_context = self._build_context(conversation_id, pattern_context)
        
        # Check cache health (Phase 1.5)
        cache_health = self.cache_monitor.check_cache_health()
        
        if not enabled:
            # Return original context without optimization
            return {
                'original_context': original_context,
                'optimized_context': original_context,
                'optimization_stats': {
                    'enabled': False,
                    'original_tokens': self._estimate_tokens(original_context),
                    'optimized_tokens': self._estimate_tokens(original_context),
                    'reduction_rate': 0.0,
                    'quality_score': 1.0
                },
                'cache_health': cache_health
            }
        
        # Optimize conversation context
        conversation_opt = None
        conversation_metrics = None
        if original_context.get('conversations'):
            # Use a generic intent for now (could be improved with actual user intent)
            current_intent = "retrieve relevant conversation context"
            optimized_convs, conversation_metrics = self.ml_optimizer.optimize_conversation_context(
                conversations=original_context['conversations'],
                current_intent=current_intent,
                min_conversations=1
            )
            conversation_opt = optimized_convs
        
        # Optimize pattern context
        pattern_opt = None
        pattern_metrics = None
        if original_context.get('patterns'):
            query = "retrieve relevant architectural patterns"
            optimized_patterns, pattern_metrics = self.ml_optimizer.optimize_pattern_context(
                patterns=original_context['patterns'],
                query=query,
                max_patterns=20
            )
            pattern_opt = optimized_patterns
        
        # Build optimized context
        optimized_context = original_context.copy()
        
        if conversation_opt is not None:
            optimized_context['conversations'] = conversation_opt
        
        if pattern_opt is not None:
            optimized_context['patterns'] = pattern_opt
        
        # Calculate combined statistics
        orig_tokens = self._estimate_tokens(original_context)
        opt_tokens = self._estimate_tokens(optimized_context)
        reduction_rate = (orig_tokens - opt_tokens) / orig_tokens if orig_tokens > 0 else 0.0
        
        # Average quality score from both optimizations
        quality_scores = []
        if conversation_metrics:
            quality_scores.append(conversation_metrics.get('quality_score', 1.0))
        if pattern_metrics:
            quality_scores.append(pattern_metrics.get('quality_score', 1.0))
        
        quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 1.0
        
        # Record metrics (Phase 1.5)
        self.token_metrics.record_request(
            original_tokens=orig_tokens,
            optimized_tokens=opt_tokens,
            optimization_method='get_context',
            quality_score=quality_score
        )
        
        return {
            'original_context': original_context,
            'optimized_context': optimized_context,
            'optimization_stats': {
                'enabled': True,
                'original_tokens': orig_tokens,
                'optimized_tokens': opt_tokens,
                'reduction_rate': reduction_rate,
                'quality_score': quality_score,
                'meets_threshold': quality_score >= opt_config.get('quality_threshold', 0.9)
            },
            'cache_health': cache_health
        }
    
    def _build_context(
        self,
        conversation_id: Optional[str],
        pattern_context: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Build unoptimized context from working memory.
        
        Args:
            conversation_id: Conversation to include. If None, uses active or recent.
            pattern_context: Optional knowledge graph patterns.
        
        Returns:
            Dict with conversations and patterns.
        """
        context = {
            'conversations': [],
            'patterns': pattern_context or [],
            'entities': []
        }
        
        # Get conversation(s)
        if conversation_id:
            conv = self.get_conversation(conversation_id)
            if conv:
                messages = self.get_messages(conversation_id)
                entities = self.get_conversation_entities(conversation_id)
                
                context['conversations'].append({
                    'conversation_id': conv.conversation_id,
                    'title': conv.title,
                    'created_at': conv.created_at.isoformat() if hasattr(conv.created_at, 'isoformat') else str(conv.created_at),
                    'messages': messages,
                    'entities': [{'type': e.entity_type, 'name': e.entity_name} for e in entities]
                })
        else:
            # Use active or most recent conversations
            active = self.get_active_conversation()
            if active:
                messages = self.get_messages(active.conversation_id)
                entities = self.get_conversation_entities(active.conversation_id)
                
                context['conversations'].append({
                    'conversation_id': active.conversation_id,
                    'title': active.title,
                    'created_at': active.created_at.isoformat() if hasattr(active.created_at, 'isoformat') else str(active.created_at),
                    'messages': messages,
                    'entities': [{'type': e.entity_type, 'name': e.entity_name} for e in entities]
                })
            else:
                # Get 3 most recent
                recent = self.get_recent_conversations(limit=3)
                for conv in recent:
                    messages = self.get_messages(conv.conversation_id)
                    entities = self.get_conversation_entities(conv.conversation_id)
                    
                    context['conversations'].append({
                        'conversation_id': conv.conversation_id,
                        'title': conv.title,
                        'created_at': conv.created_at.isoformat() if hasattr(conv.created_at, 'isoformat') else str(conv.created_at),
                        'messages': messages,
                        'entities': [{'type': e.entity_type, 'name': e.entity_name} for e in entities]
                    })
        
        return context
    
    def _estimate_tokens(self, context: Dict[str, Any]) -> int:
        """
        Estimate token count for context (simple heuristic: ~4 chars/token).
        
        Args:
            context: Context dictionary.
        
        Returns:
            Estimated token count.
        """
        text = json.dumps(context)
        return len(text) // 4
    
    def get_token_metrics_summary(self) -> Dict[str, Any]:
        """
        Get current token optimization metrics summary (Phase 1.5).
        
        Returns:
            Dict with session metrics, cost savings, and optimization performance.
        """
        return self.token_metrics.get_session_summary()
    
    def get_cache_health_report(self) -> Dict[str, Any]:
        """
        Get current cache health report (Phase 1.5).
        
        Returns:
            Cache health report with token counts, limits, and recommendations.
        """
        return self.cache_monitor.check_cache_health()
    
    # ========== Conversation Management (Delegated) ==========
    
    def add_conversation(
        self,
        conversation_id: str,
        title: str,
        messages: List[Dict[str, str]],
        tags: Optional[List[str]] = None
    ) -> Conversation:
        """
        Add a new conversation to working memory.
        
        Args:
            conversation_id: Unique conversation identifier
            title: Conversation title
            messages: List of message dicts with 'role' and 'content'
            tags: Optional list of tags
        
        Returns:
            Created Conversation object
        """
        # Enforce FIFO limit before adding
        self.queue_manager.enforce_fifo_limit()
        
        # Add conversation
        conversation = self.conversation_manager.add_conversation(
            conversation_id=conversation_id,
            title=title,
            message_count=len(messages),
            tags=tags
        )
        
        # Add messages
        self.message_store.add_messages(conversation_id, messages)
        
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        return self.conversation_manager.get_conversation(conversation_id)
    
    def get_recent_conversations(self, limit: int = 20) -> List[Conversation]:
        """Get recent conversations ordered by creation date (newest first)."""
        return self.conversation_manager.get_recent_conversations(limit)
    
    def set_active_conversation(self, conversation_id: str) -> None:
        """Mark a conversation as active."""
        self.conversation_manager.set_active_conversation(conversation_id)
    
    def get_active_conversation(self) -> Optional[Conversation]:
        """Get the currently active conversation."""
        return self.conversation_manager.get_active_conversation()
    
    def update_conversation(
        self,
        conversation_id: str,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> None:
        """Update conversation properties."""
        self.conversation_manager.update_conversation(conversation_id, title, summary, tags)
    
    def get_conversation_count(self) -> int:
        """Get the total number of conversations in working memory."""
        return self.conversation_manager.get_conversation_count()
    
    # ========== Message Management (Delegated) ==========
    
    def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a conversation."""
        return self.message_store.get_messages(conversation_id)
    
    def add_messages(
        self,
        conversation_id: str,
        messages: List[Dict[str, str]]
    ) -> None:
        """Append new messages to an existing conversation."""
        self.message_store.add_messages(conversation_id, messages)
        self.conversation_manager.increment_message_count(conversation_id, len(messages))
    
    # ========== Entity Extraction (Delegated) ==========
    
    def extract_entities(self, conversation_id: str) -> List[Entity]:
        """Extract entities from a conversation's messages."""
        messages = self.message_store.get_messages(conversation_id)
        
        if not messages:
            return []
        
        # Combine all message content
        text = " ".join(msg['content'] for msg in messages)
        
        return self.entity_extractor.extract_entities(conversation_id, text)
    
    def get_conversation_entities(self, conversation_id: str) -> List[Entity]:
        """Get all entities associated with a conversation."""
        return self.entity_extractor.get_conversation_entities(conversation_id)
    
    def get_entity_statistics(self) -> List[Dict[str, Any]]:
        """Get statistics on entity usage."""
        return self.entity_extractor.get_entity_statistics()
    
    # ========== Search Operations (Delegated) ==========
    
    def search_conversations(self, keyword: str) -> List[Conversation]:
        """Search conversations by keyword in title or messages."""
        return self.conversation_search.search_by_keyword(keyword)
    
    def find_conversations_with_entity(
        self,
        entity_type: EntityType,
        entity_name: str
    ) -> List[Conversation]:
        """Find conversations that mention a specific entity."""
        return self.conversation_search.search_by_entity(entity_type.value, entity_name)
    
    def get_conversations_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Conversation]:
        """Get conversations within a date range."""
        return self.conversation_search.search_by_date_range(start_date, end_date)
    
    # ========== Queue Management (Delegated) ==========
    
    def get_eviction_log(self) -> List[Dict[str, Any]]:
        """Get the eviction log."""
        return self.queue_manager.get_eviction_log()
    
    def _enforce_fifo_limit(self) -> None:
        """Enforce FIFO limit (maintained for compatibility, delegates to QueueManager)."""
        self.queue_manager.enforce_fifo_limit()
    
    # ========== Utility Methods ==========
    
    def close(self) -> None:
        """Close any open connections (for cleanup in tests)."""
        # SQLite connections are per-operation, so nothing to close
        pass
