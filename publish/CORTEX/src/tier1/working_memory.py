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
import sqlite3

# Import modular components
from .conversations import ConversationManager, ConversationSearch, Conversation
from .messages import MessageStore
from .entities import EntityExtractor, EntityType, Entity
from .fifo import QueueManager
from .sessions import SessionManager, Session
from .lifecycle import ConversationLifecycleManager, WorkflowState
from .session_correlation import SessionAmbientCorrelator

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
        
        # Load configuration first (needed for session manager)
        self.config = self._load_config()
        
        # Initialize session manager (CORTEX 3.0)
        idle_threshold = self.config.get('tier1', {}).get('conversation_boundaries', {}).get('idle_gap_threshold_seconds', 7200)
        self.session_manager = SessionManager(self.db_path, idle_threshold_seconds=idle_threshold)
        
        # Initialize lifecycle manager (CORTEX 3.0)
        self.lifecycle_manager = ConversationLifecycleManager(self.db_path)
        
        # Initialize session-ambient correlator (CORTEX 3.0 Phase 3)
        self.session_correlator = SessionAmbientCorrelator(self.db_path)
        
        # Initialize Phase 1.5: Token Optimization System
        # Note: target_reduction is set via config at optimization time
        self.ml_optimizer = None  # Will be created with config params when needed
        self.cache_monitor = CacheMonitor(self)  # Pass WorkingMemory instance
        self.token_metrics = TokenMetricsCollector(self)  # Pass WorkingMemory instance
        
        self.optimization_enabled = self.config.get('token_optimization', {}).get('enabled', True)
        
        # Initialize database on creation
        self._init_database()
    
    def initialize(self) -> bool:
        """
        Initialize the working memory system.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Database already initialized in __init__
            
            # Verify database is accessible
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM conversations")
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Failed to initialize working memory: {e}")
            return False
    
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
                tags TEXT,
                session_id TEXT,
                last_activity TIMESTAMP,
                workflow_state TEXT,
                conversation_type TEXT DEFAULT 'interactive',
                import_source TEXT,
                quality_score REAL DEFAULT 0.0,
                semantic_elements TEXT DEFAULT '{}'
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
        
        # Migrate existing databases to add missing columns
        # Check if columns exist and add them if they don't
        cursor.execute("PRAGMA table_info(conversations)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        migrations = [
            ("conversation_type", "ALTER TABLE conversations ADD COLUMN conversation_type TEXT DEFAULT 'interactive'"),
            ("import_source", "ALTER TABLE conversations ADD COLUMN import_source TEXT"),
            ("quality_score", "ALTER TABLE conversations ADD COLUMN quality_score REAL DEFAULT 0.0"),
            ("semantic_elements", "ALTER TABLE conversations ADD COLUMN semantic_elements TEXT DEFAULT '{}'")
        ]
        
        for column_name, alter_sql in migrations:
            if column_name not in existing_columns:
                cursor.execute(alter_sql)
        
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
            CREATE INDEX IF NOT EXISTS idx_conversations_session 
            ON conversations(session_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_last_activity 
            ON conversations(last_activity DESC)
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
    
    # ========== Session Management (CORTEX 3.0) ==========
    
    def detect_or_create_session(self, workspace_path: str) -> Session:
        """
        Detect or create workspace session (CORTEX 3.0).
        
        Creates new session if:
        - No active session for workspace
        - Idle gap exceeds threshold (default 2 hours)
        - Previous session ended
        
        Args:
            workspace_path: Absolute path to workspace
        
        Returns:
            Active Session object
        """
        return self.session_manager.detect_or_create_session(workspace_path)
    
    def get_active_session(self, workspace_path: str) -> Optional[Session]:
        """Get active session for workspace."""
        return self.session_manager.get_active_session(workspace_path)
    
    def end_session(self, session_id: str, reason: str = "manual") -> None:
        """
        End a workspace session.
        
        Args:
            session_id: Session to end
            reason: Reason for ending (manual, idle_timeout, workspace_close)
        """
        self.session_manager.end_session(session_id, reason)
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        return self.session_manager.get_session(session_id)
    
    def get_recent_sessions(self, workspace_path: Optional[str] = None, limit: int = 10) -> List[Session]:
        """Get recent sessions, optionally filtered by workspace."""
        return self.session_manager.get_recent_sessions(workspace_path, limit)
    
    # ========== Lifecycle Management (CORTEX 3.0) ==========
    
    def handle_user_request(
        self,
        user_request: str,
        workspace_path: str,
        assistant_response: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle user request with full session-based lifecycle management.
        
        This is the primary entry point for CORTEX 3.0 session-based conversations.
        Automatically:
        - Detects or creates session
        - Creates new conversation or continues existing
        - Tracks workflow state progression
        - Closes conversations when workflow complete
        - Respects explicit user commands ("new conversation", "continue")
        
        Args:
            user_request: User's message
            workspace_path: Absolute path to workspace
            assistant_response: Optional assistant's response
            context: Optional additional context
        
        Returns:
            Dict with:
                - session_id: Active session ID
                - conversation_id: Active conversation ID
                - is_new_conversation: Whether conversation was just created
                - is_new_session: Whether session was just created
                - workflow_state: Current workflow state
                - lifecycle_event: Lifecycle event that occurred
        """
        # Step 1: Detect or create session
        session = self.session_manager.detect_or_create_session(workspace_path)
        is_new_session = session.conversation_count == 0
        
        # Step 2: Get active conversation for session (if any)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT conversation_id, workflow_state
            FROM conversations
            WHERE session_id = ? AND is_active = 1
            ORDER BY created_at DESC
            LIMIT 1
        """, (session.session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        active_conversation_id = row[0] if row else None
        current_workflow_state = WorkflowState(row[1]) if row and row[1] else None
        
        # Step 3: Determine if new conversation should be created
        should_create, create_reason = self.lifecycle_manager.should_create_conversation(
            session_id=session.session_id,
            user_request=user_request,
            has_active_conversation=active_conversation_id is not None
        )
        
        # Step 4: Close current conversation if needed
        if active_conversation_id and should_create and create_reason == "new_conversation_requested":
            self.lifecycle_manager.close_conversation(
                conversation_id=active_conversation_id,
                session_id=session.session_id,
                reason="new_conversation_requested",
                final_state=current_workflow_state or WorkflowState.ABANDONED
            )
            active_conversation_id = None
        
        # Step 5: Create new conversation if needed
        is_new_conversation = False
        if should_create or not active_conversation_id:
            # Generate conversation ID
            from datetime import datetime
            now = datetime.now()
            import hashlib
            hash_suffix = hashlib.md5(user_request.encode()).hexdigest()[:6]
            conversation_id = f"conv_{now.strftime('%Y%m%d_%H%M%S')}_{hash_suffix}"
            
            # Infer initial workflow state
            initial_state = self.lifecycle_manager.infer_workflow_state(user_request)
            
            # Create conversation
            conversation = self.add_conversation(
                conversation_id=conversation_id,
                title=user_request[:100],  # First 100 chars as title
                messages=[{"role": "user", "content": user_request}],
                tags=[]
            )
            
            # Link to session and set workflow state
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE conversations
                SET session_id = ?,
                    workflow_state = ?,
                    last_activity = ?,
                    is_active = 1
                WHERE conversation_id = ?
            """, (
                session.session_id,
                initial_state.value,
                datetime.now().isoformat(),
                conversation_id
            ))
            conn.commit()
            conn.close()
            
            # Log creation
            self.lifecycle_manager.log_conversation_created(
                conversation_id=conversation_id,
                session_id=session.session_id,
                trigger=create_reason,
                initial_state=initial_state
            )
            
            # Update session conversation count
            self.session_manager.increment_conversation_count(session.session_id)
            
            active_conversation_id = conversation_id
            current_workflow_state = initial_state
            is_new_conversation = True
        
        else:
            # Step 6: Continue existing conversation
            # Add message to existing conversation
            self.message_store.add_messages(
                active_conversation_id,
                [{"role": "user", "content": user_request}]
            )
            
            # Infer and update workflow state
            new_state = self.lifecycle_manager.infer_workflow_state(
                user_request,
                current_state=current_workflow_state
            )
            
            if new_state != current_workflow_state:
                self.lifecycle_manager.update_workflow_state(
                    conversation_id=active_conversation_id,
                    session_id=session.session_id,
                    new_state=new_state,
                    trigger="auto"
                )
                current_workflow_state = new_state
        
        # Step 7: Add assistant response if provided
        if assistant_response:
            self.message_store.add_messages(
                active_conversation_id,
                [{"role": "assistant", "content": assistant_response}]
            )
        
        # Step 8: Check if conversation should close
        should_close, close_reason = self.lifecycle_manager.should_close_conversation(
            conversation_id=active_conversation_id,
            current_state=current_workflow_state,
            user_request=user_request
        )
        
        if should_close:
            self.lifecycle_manager.close_conversation(
                conversation_id=active_conversation_id,
                session_id=session.session_id,
                reason=close_reason,
                final_state=current_workflow_state
            )
        
        return {
            "session_id": session.session_id,
            "conversation_id": active_conversation_id,
            "is_new_conversation": is_new_conversation,
            "is_new_session": is_new_session,
            "workflow_state": current_workflow_state.value,
            "lifecycle_event": create_reason if is_new_conversation else "continuation",
            "conversation_closed": should_close
        }
    
    def get_conversation_lifecycle_history(self, conversation_id: str):
        """Get lifecycle history for a conversation."""
        return self.lifecycle_manager.get_conversation_history(conversation_id)
    
    def get_session_lifecycle_history(self, session_id: str):
        """Get all conversation lifecycle events for a session."""
        return self.lifecycle_manager.get_session_conversation_history(session_id)
    
    # ========== Session-Ambient Correlation (CORTEX 3.0 Phase 3) ==========
    
    def log_ambient_event(
        self,
        session_id: str,
        event_type: str,
        file_path: Optional[str] = None,
        pattern: Optional[str] = None,
        score: Optional[int] = None,
        summary: Optional[str] = None,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Log ambient capture event linked to session.
        
        Use this to record file changes, terminal commands, git operations
        that occur during a development session.
        
        Args:
            session_id: Active workspace session ID
            event_type: Type of event (file_change, terminal_command, git_operation)
            file_path: Path to affected file
            pattern: Detected pattern (FEATURE, BUGFIX, REFACTOR, etc.)
            score: Activity score (0-100)
            summary: Natural language summary
            conversation_id: Optional active conversation ID
            metadata: Additional event metadata
            
        Returns:
            Event ID
        """
        return self.session_correlator.log_ambient_event(
            session_id=session_id,
            event_type=event_type,
            file_path=file_path,
            pattern=pattern,
            score=score,
            summary=summary,
            conversation_id=conversation_id,
            metadata=metadata
        )
    
    def get_session_events(
        self,
        session_id: str,
        event_type: Optional[str] = None,
        min_score: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all ambient events for a session.
        
        Args:
            session_id: Session ID to query
            event_type: Optional filter by event type
            min_score: Optional minimum activity score
            
        Returns:
            List of events with metadata
        """
        return self.session_correlator.get_session_events(
            session_id=session_id,
            event_type=event_type,
            min_score=min_score
        )
    
    def get_conversation_events(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get all ambient events that occurred during a conversation.
        
        This shows what actually happened (file changes, commands, git ops)
        while the conversation was active.
        
        Args:
            conversation_id: Conversation ID to query
            
        Returns:
            List of events with metadata
        """
        return self.session_correlator.get_conversation_events(conversation_id)
    
    def generate_session_narrative(self, session_id: str) -> str:
        """
        Generate complete development narrative for a session.
        
        Combines conversations + ambient events into a coherent story
        of what happened during the development session.
        
        Args:
            session_id: Session ID to narrate
            
        Returns:
            Natural language narrative (Markdown format)
        """
        return self.session_correlator.generate_session_narrative(session_id)
    
    # ========== Conversation Import (CORTEX 3.0 Dual-Channel Memory) ==========
    
    def import_conversation(
        self,
        conversation_turns: List[Dict[str, str]],
        import_source: str,
        workspace_path: Optional[str] = None,
        import_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Import a manually captured conversation to CORTEX brain.
        
        Part of CORTEX 3.0's dual-channel memory system:
        - Channel 1: Ambient daemon (execution-focused, automatic)
        - Channel 2: Manual import (strategy-focused, user-driven)
        
        Args:
            conversation_turns: List of conversation turns with 'user' and 'assistant' keys
            import_source: Source file path or identifier
            workspace_path: Optional workspace path to link conversation to session
            import_date: Optional import timestamp (defaults to now)
            
        Returns:
            Dict with import results: {
                'success': bool,
                'conversation_id': str,
                'session_id': str,
                'quality_score': int,
                'quality_level': str,
                'semantic_elements': dict,
                'turns_imported': int
            }
        """
        import_date = import_date or datetime.now()
        
        # VALIDATION: Check for valid conversation turns
        if not isinstance(conversation_turns, list):
            return {
                'success': False,
                'error': 'conversation_turns must be a list',
                'conversation_id': None,
                'session_id': None,
                'quality_score': 0,
                'quality_level': 'INVALID',
                'semantic_elements': {},
                'turns_imported': 0
            }
        
        # EDGE CASE: Handle empty conversation gracefully (test_07)
        if len(conversation_turns) == 0:
            # Generate conversation ID inline
            import hashlib
            now = import_date or datetime.now()
            hash_suffix = hashlib.md5(b'empty_conversation').hexdigest()[:6]
            conversation_id = f"conv_{now.strftime('%Y%m%d_%H%M%S')}_{hash_suffix}"
            
            session_id = None
            if workspace_path:
                try:
                    active_session = self.session_manager.get_active_session(workspace_path)
                    session_id = active_session.session_id if active_session else None
                except Exception:
                    session_id = None  # Gracefully handle session errors in tests
            
            # Store empty conversation with LOW quality
            timestamp = now.isoformat()
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO conversations 
                    (conversation_id, session_id, title, message_count, tags, created_at, updated_at,
                     conversation_type, import_source, quality_score, semantic_elements)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    conversation_id,
                    session_id,
                    "Empty conversation",
                    0,
                    json.dumps(['empty']),
                    timestamp,
                    timestamp,
                    'imported',
                    import_source,
                    0,  # quality_score (LOW = 0 points)
                    json.dumps({})
                ))
                conn.commit()
                conn.close()
                return {
                    'success': True,
                    'conversation_id': conversation_id,
                    'session_id': session_id,
                    'quality_score': 0,
                    'quality_level': 'LOW',
                    'semantic_elements': {},
                    'turns_imported': 0
                }
            except Exception as e:
                print(f"[DEBUG] Database insert failed: {e}")  # DEBUG
                return {
                    'success': False,
                    'error': f'Failed to store empty conversation: {e}',
                    'conversation_id': None,
                    'session_id': None,
                    'quality_score': 0,
                    'quality_level': 'INVALID',
                    'semantic_elements': {},
                    'turns_imported': 0
                }
        
        # VALIDATION: Check each turn has valid structure
        for i, turn in enumerate(conversation_turns):
            if not isinstance(turn, dict):
                return {
                    'success': False,
                    'error': f'Turn {i} is not a dictionary',
                    'conversation_id': None,
                    'session_id': None,
                    'quality_score': 0,
                    'quality_level': 'INVALID',
                    'semantic_elements': {},
                    'turns_imported': 0
                }
            
            # Check for required keys and non-empty values
            # EDGE CASE: Allow incomplete turns (test_08) - save user message even without assistant
            user_msg = turn.get('user', '').strip()
            assistant_msg = turn.get('assistant', '').strip()
            
            if not user_msg:
                return {
                    'success': False,
                    'error': f'Turn {i} missing user message',
                    'conversation_id': None,
                    'session_id': None,
                    'quality_score': 0,
                    'quality_level': 'INVALID',
                    'semantic_elements': {},
                    'turns_imported': 0
                }
            
            # Assistant message is optional - incomplete turns are allowed
            # They will be stored with empty assistant response
        
        # Quality analysis using CORTEX 3.0 analyzer
        from .conversation_quality import ConversationQualityAnalyzer
        
        analyzer = ConversationQualityAnalyzer(show_hint_threshold="GOOD")
        
        # Analyze all turns
        turns_for_analysis = [
            (turn.get('user', ''), turn.get('assistant', ''))
            for turn in conversation_turns
        ]
        quality_score = analyzer.analyze_multi_turn_conversation(turns_for_analysis)
        
        # Get or create session if workspace provided
        session_id = None
        if workspace_path:
            active_session = self.session_manager.get_active_session(workspace_path)
            if active_session:
                session_id = active_session.session_id
            else:
                # Create import session using detect_or_create
                new_session = self.session_manager.detect_or_create_session(workspace_path)
                session_id = new_session.session_id
        
        # START TRANSACTION for ACID compliance
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Generate conversation ID (modular ConversationManager expects us to provide it)
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            import random
            conversation_id = f"imported-conv-{timestamp}-{random.randint(1000, 9999)}"
            
            # Count actual messages (each turn has user + assistant message)
            total_messages = len(conversation_turns) * 2
            
            # Add conversation to database
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO conversations 
                (conversation_id, title, message_count, tags, created_at, updated_at,
                 conversation_type, import_source, quality_score, semantic_elements)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                conversation_id,
                f"Imported from {Path(import_source).name}",
                total_messages,
                json.dumps(['imported', quality_score.level]),
                now,
                now,
                'imported',
                import_source,
                quality_score.total_score,
                json.dumps(quality_score.elements.__dict__)
            ))
            
            # CRITICAL: Enforce FIFO limit BEFORE adding messages
            # This ensures we maintain exactly 20 conversations maximum
            conv_count = cursor.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
            if conv_count >= self.MAX_CONVERSATIONS:
                # Remove oldest conversation(s) to make room
                conversations_to_remove = conv_count - self.MAX_CONVERSATIONS + 1
                oldest_convos = cursor.execute("""
                    SELECT conversation_id FROM conversations 
                    ORDER BY created_at ASC 
                    LIMIT ?
                """, (conversations_to_remove,)).fetchall()
                
                for (old_conv_id,) in oldest_convos:
                    # Log eviction
                    cursor.execute("""
                        INSERT INTO eviction_log (conversation_id, event_type, details)
                        VALUES (?, 'evicted', 'fifo_limit')
                    """, (old_conv_id,))
                    
                    # Remove conversation and cascade delete messages/entities
                    cursor.execute("DELETE FROM conversation_entities WHERE conversation_id = ?", (old_conv_id,))
                    cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (old_conv_id,))
                    cursor.execute("DELETE FROM conversations WHERE conversation_id = ?", (old_conv_id,))
            
            # Store conversation turns as messages
            for turn in conversation_turns:
                # User message
                if 'user' in turn:
                    cursor.execute("""
                        INSERT INTO messages (conversation_id, role, content, timestamp)
                        VALUES (?, ?, ?, ?)
                    """, (conversation_id, 'user', turn['user'], now))
                
                # Assistant message  
                if 'assistant' in turn:
                    cursor.execute("""
                        INSERT INTO messages (conversation_id, role, content, timestamp)
                        VALUES (?, ?, ?, ?)
                    """, (conversation_id, 'assistant', turn['assistant'], now))
            
            # COMMIT transaction - all operations succeeded
            conn.commit()
            
            return {
                'success': True,
                'conversation_id': conversation_id,
                'session_id': session_id,
                'quality_score': quality_score.total_score,
                'quality_level': quality_score.level,
                'semantic_elements': quality_score.elements.__dict__,
                'reasoning': quality_score.reasoning,
                'turns_imported': len(conversation_turns)
            }
            
        except Exception as e:
            # ROLLBACK transaction on any error
            conn.rollback()
            return {
                'success': False,
                'error': f'Transaction failed: {str(e)}',
                'conversation_id': None,
                'session_id': None,
                'quality_score': 0,
                'quality_level': 'ERROR',
                'semantic_elements': {},
                'turns_imported': 0
            }
        finally:
            conn.close()
    
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
    
    def store_conversation(
        self,
        user_message: str,
        assistant_response: str,
        intent: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a conversation with user message and assistant response.
        Convenience method for external integrations (like conversation capture).
        
        Args:
            user_message: User's message content
            assistant_response: Assistant's response content
            intent: Detected intent (EXECUTE, PLAN, FIX, etc.)
            context: Optional context metadata
            
        Returns:
            Generated conversation ID
        """
        # Generate conversation ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        conversation_id = f"conv_{timestamp}_{hash(user_message + assistant_response) & 0xfff:03x}"
        
        # Create title from user message (first 50 chars)
        title = user_message[:50] + "..." if len(user_message) > 50 else user_message
        
        # Format messages
        messages = [
            {
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().isoformat()
            },
            {
                'role': 'assistant', 
                'content': assistant_response,
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        # Create tags from intent and context
        tags = [intent.lower()]
        if context:
            if context.get('manual_import'):
                tags.append('manual_import')
            if context.get('entities'):
                tags.append(f"entities_{len(context['entities'])}")
        
        # Store conversation
        conversation = self.add_conversation(
            conversation_id=conversation_id,
            title=title,
            messages=messages,
            tags=tags
        )
        
        # Store context as metadata if provided
        if context:
            # Store entities if available
            if context.get('entities'):
                for entity in context['entities']:
                    self.entity_extractor.add_entity(
                        conversation_id=conversation_id,
                        entity_type=EntityType.FILE if entity['type'] == 'file' else EntityType.VARIABLE,
                        value=entity['value'],
                        context=entity.get('context', 'captured from conversation')
                    )
        
        return conversation_id
    
    def close(self) -> None:
        """Close any open connections (for cleanup in tests)."""
        # SQLite connections are per-operation, so nothing to close
        pass
