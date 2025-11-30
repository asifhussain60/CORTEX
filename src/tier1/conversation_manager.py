"""
CORTEX Tier 1: Conversation Manager
Manages conversation storage and retrieval in SQLite

Task 1.2: ConversationManager Class
Duration: 2 hours
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from contextlib import contextmanager
import json
import logging

# Import planning doc sync engine
try:
    from .planning_doc_sync import PlanningDocSyncEngine
    PLANNING_SYNC_AVAILABLE = True
except ImportError:
    PLANNING_SYNC_AVAILABLE = False
    logging.warning("PlanningDocSyncEngine not available - planning doc sync disabled")


class ConversationManager:
    """
    Manages conversation data in Tier 1 Working Memory
    
    Responsibilities:
    - CRUD operations for conversations
    - Message management
    - Entity tracking
    - File modification tracking
    - Active conversation management
    - FIFO queue enforcement (20 conversation limit)
    - Planning document synchronization (auto-sync to markdown)
    """
    
    MAX_CONVERSATIONS = 20
    
    def __init__(self, db_path: Path, enable_planning_sync: bool = True):
        """
        Initialize conversation manager
        
        Args:
            db_path: Path to conversations.db SQLite database
            enable_planning_sync: Enable auto-sync to planning documents
        """
        self.db_path = db_path
        self._ensure_schema()
        
        # Initialize planning doc sync engine
        self.sync_engine = None
        if enable_planning_sync and PLANNING_SYNC_AVAILABLE:
            try:
                self.sync_engine = PlanningDocSyncEngine()
                logging.info("Planning doc sync engine initialized")
            except Exception as e:
                logging.warning(f"Failed to initialize planning doc sync engine: {e}")
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def _ensure_schema(self):
        """Ensure database schema exists"""
        # Schema is created by migration script
        # For testing, create schema automatically if it doesn't exist
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='conversations'
            """)
            if not cursor.fetchone():
                # Create schema (same as in migrate_tier1.py)
                self._create_schema(conn)
    
    def _create_schema(self, conn):
        """Create database schema"""
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                goal TEXT,
                outcome TEXT,
                status TEXT DEFAULT 'active',
                message_count INTEGER DEFAULT 0,
                context TEXT
            )
        """)
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
        """)
        
        # Entities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_value TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
        """)
        
        # Files modified table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files_modified (
                file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                operation TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
        """)
        
        # Interactive Planning Sessions table (CORTEX 2.1)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS planning_sessions (
                session_id TEXT PRIMARY KEY,
                user_request TEXT NOT NULL,
                confidence REAL NOT NULL,
                state TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                final_plan TEXT,
                metadata TEXT
            )
        """)
        
        # Planning Questions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS planning_questions (
                question_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                question_text TEXT NOT NULL,
                question_type TEXT NOT NULL,
                options TEXT,
                default_answer TEXT,
                priority INTEGER,
                context TEXT,
                FOREIGN KEY (session_id) REFERENCES planning_sessions(session_id)
            )
        """)
        
        # Planning Answers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS planning_answers (
                answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                question_id TEXT NOT NULL,
                value TEXT NOT NULL,
                skipped INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL,
                additional_context TEXT,
                FOREIGN KEY (session_id) REFERENCES planning_sessions(session_id),
                FOREIGN KEY (question_id) REFERENCES planning_questions(question_id)
            )
        """)
        
        # Create indices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conv_agent ON conversations(agent_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conv_status ON conversations(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_msg_conv ON messages(conversation_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_conv ON entities(conversation_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_conv ON files_modified(conversation_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_planning_session ON planning_sessions(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_planning_q_session ON planning_questions(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_planning_a_session ON planning_answers(session_id)")
        
        conn.commit()
    
    def create_conversation(
        self,
        agent_id: str,
        goal: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> str:
        """
        Create a new conversation
        
        Args:
            agent_id: Agent identifier
            goal: Conversation goal (optional)
            context: Additional context (optional)
            
        Returns:
            conversation_id: Generated conversation ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Generate conversation ID
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            import random
            conv_id = f"conv-{timestamp}-{random.randint(1000, 9999)}"
            
            # Check if we need to enforce FIFO
            self._enforce_fifo(cursor)
            
            # Insert conversation
            cursor.execute("""
                INSERT INTO conversations (
                    conversation_id, agent_id, start_time, 
                    goal, status, context
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                conv_id,
                agent_id,
                datetime.now().isoformat(),
                goal,
                'active',
                json.dumps(context) if context else None
            ))
            
            conn.commit()
            return conv_id
    
    def _enforce_fifo(self, cursor: sqlite3.Cursor):
        """
        Enforce FIFO queue (max 20 conversations)
        Deletes oldest completed conversation if limit reached
        """
        # Count total conversations
        cursor.execute("SELECT COUNT(*) FROM conversations")
        count = cursor.fetchone()[0]
        
        if count >= self.MAX_CONVERSATIONS:
            # Delete oldest completed conversation
            cursor.execute("""
                DELETE FROM conversations
                WHERE conversation_id = (
                    SELECT conversation_id 
                    FROM conversations
                    WHERE status = 'completed'
                    ORDER BY start_time ASC
                    LIMIT 1
                )
            """)
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str
    ) -> str:
        """
        Add a message to a conversation
        
        Args:
            conversation_id: Conversation to add message to
            role: user, assistant, or system
            content: Message text
            
        Returns:
            message_id: Generated message ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Generate message ID
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            import random
            msg_id = f"msg-{timestamp}-{random.randint(1000, 9999)}"
            
            # Insert message
            cursor.execute("""
                INSERT INTO messages (
                    message_id, conversation_id, role, content, timestamp
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                msg_id,
                conversation_id,
                role,
                content,
                datetime.now().isoformat()
            ))
            
            # Update conversation message count
            cursor.execute("""
                UPDATE conversations
                SET message_count = message_count + 1
                WHERE conversation_id = ?
            """, (conversation_id,))
            
            conn.commit()
            
            # Auto-sync planning document (if available)
            if self.sync_engine:
                try:
                    self.sync_engine.sync_planning_doc(conversation_id, self)
                except Exception as e:
                    logging.warning(f"Planning doc sync failed for {conversation_id}: {e}")
            
            return msg_id
    
    def add_entity(
        self,
        conversation_id: str,
        entity_type: str,
        entity_value: str
    ):
        """
        Add an entity to a conversation
        
        Args:
            conversation_id: Conversation to add entity to
            entity_type: Type of entity (file, intent, term, feature)
            entity_value: Entity value
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert entity
            cursor.execute("""
                INSERT INTO entities (conversation_id, entity_type, entity_value, timestamp)
                VALUES (?, ?, ?, ?)
            """, (conversation_id, entity_type, entity_value, datetime.now().isoformat()))
            
            conn.commit()
    
    def add_file(
        self,
        conversation_id: str,
        file_path: str,
        operation: str = 'modified'
    ):
        """
        Add a modified file to a conversation
        
        Args:
            conversation_id: Conversation to add file to
            file_path: Path to modified file
            operation: Operation type (created, modified, deleted)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert file
            cursor.execute("""
                INSERT INTO files_modified (conversation_id, file_path, operation, timestamp)
                VALUES (?, ?, ?, ?)
            """, (conversation_id, file_path, operation, datetime.now().isoformat()))
            
            conn.commit()
    
    def end_conversation(
        self,
        conversation_id: str,
        outcome: Optional[str] = None
    ):
        """
        Mark a conversation as ended
        
        Args:
            conversation_id: Conversation to end
            outcome: Final outcome description
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE conversations
                SET status = 'completed',
                    end_time = ?,
                    outcome = ?
                WHERE conversation_id = ?
            """, (
                datetime.now().isoformat(),
                outcome,
                conversation_id
            ))
            
            conn.commit()
            
            # Final sync of planning document with completed status
            if self.sync_engine:
                try:
                    self.sync_engine.sync_planning_doc(conversation_id, self, force=True)
                except Exception as e:
                    logging.warning(f"Final planning doc sync failed for {conversation_id}: {e}")
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """
        Get conversation by ID
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation data with messages, entities, and files
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM conversations
                WHERE conversation_id = ?
            """, (conversation_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            conv = dict(row)
            
            # Get messages
            cursor.execute("""
                SELECT * FROM messages
                WHERE conversation_id = ?
                ORDER BY timestamp ASC
            """, (conversation_id,))
            conv['messages'] = [dict(r) for r in cursor.fetchall()]
            
            # Get entities
            cursor.execute("""
                SELECT entity_type, entity_value, timestamp FROM entities
                WHERE conversation_id = ?
                ORDER BY timestamp DESC
            """, (conversation_id,))
            conv['entities'] = [dict(r) for r in cursor.fetchall()]
            
            # Get files
            cursor.execute("""
                SELECT file_path, operation, timestamp FROM files_modified
                WHERE conversation_id = ?
                ORDER BY timestamp DESC
            """, (conversation_id,))
            conv['files'] = [dict(r) for r in cursor.fetchall()]
            
            return conv
    
    def get_active_conversation(self, agent_id: str) -> Optional[Dict]:
        """
        Get the currently active conversation for an agent
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Active conversation data or None
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT conversation_id FROM conversations
                WHERE agent_id = ? AND status = 'active'
                ORDER BY start_time DESC
                LIMIT 1
            """, (agent_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return self.get_conversation(row['conversation_id'])
    
    def get_active_conversations(self) -> List[str]:
        """
        Get all currently active conversation IDs
        
        Returns:
            List of active conversation IDs
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT conversation_id FROM conversations
                WHERE status = 'active'
                ORDER BY start_time DESC
            """)
            
            return [row['conversation_id'] for row in cursor.fetchall()]
    
    def get_messages(self, conversation_id: str) -> List[Dict]:
        """
        Get all messages for a conversation
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of messages
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM messages
                WHERE conversation_id = ?
                ORDER BY timestamp ASC
            """, (conversation_id,))
            
            return [dict(r) for r in cursor.fetchall()]
    
    def get_entities(
        self,
        conversation_id: str,
        entity_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Get entities for a conversation
        
        Args:
            conversation_id: Conversation ID
            entity_type: Filter by entity type (optional)
            
        Returns:
            List of entities
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if entity_type:
                cursor.execute("""
                    SELECT * FROM entities
                    WHERE conversation_id = ? AND entity_type = ?
                    ORDER BY timestamp DESC
                """, (conversation_id, entity_type))
            else:
                cursor.execute("""
                    SELECT * FROM entities
                    WHERE conversation_id = ?
                    ORDER BY timestamp DESC
                """, (conversation_id,))
            
            return [dict(r) for r in cursor.fetchall()]
    
    def get_files(self, conversation_id: str) -> List[Dict]:
        """
        Get files modified for a conversation
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of files with operations
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM files_modified
                WHERE conversation_id = ?
                ORDER BY timestamp DESC
            """, (conversation_id,))
            
            return [dict(r) for r in cursor.fetchall()]
    
    def get_statistics(self) -> Dict:
        """
        Get conversation statistics
        
        Returns:
            Statistics dictionary
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Total conversations
            cursor.execute("SELECT COUNT(*) as total FROM conversations")
            total = cursor.fetchone()['total']
            
            # Active conversations
            cursor.execute("SELECT COUNT(*) as active FROM conversations WHERE status = 'active'")
            active = cursor.fetchone()['active']
            
            # Completed conversations
            cursor.execute("SELECT COUNT(*) as completed FROM conversations WHERE status = 'completed'")
            completed = cursor.fetchone()['completed']
            
            # Total messages
            cursor.execute("SELECT COUNT(*) as total FROM messages")
            total_messages = cursor.fetchone()['total']
            
            return {
                'total_conversations': total,
                'active_conversations': active,
                'completed_conversations': completed,
                'total_messages': total_messages
            }
    
    def get_recent_conversations(self, limit: int = 20) -> List[Dict]:
        """
        Get recent conversations (most recent first)
        
        Args:
            limit: Maximum number to retrieve
            
        Returns:
            List of conversation dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT conversation_id, goal as title, start_time as started, end_time as ended, 
                       message_count, status as active, agent_id as intent, outcome
                FROM conversations
                ORDER BY start_time DESC
                LIMIT ?
            """, (limit,))
            
            return [dict(r) for r in cursor.fetchall()]
    
    def search_conversations(
        self,
        agent_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        has_goal: Optional[bool] = None
    ) -> List[Dict]:
        """
        Search conversations by criteria
        
        Args:
            agent_id: Filter by agent
            start_date: Start date filter
            end_date: End date filter
            has_goal: Filter by presence of goal
            
        Returns:
            List of matching conversations
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            conditions = []
            params = []
            
            if agent_id:
                conditions.append("agent_id = ?")
                params.append(agent_id)
            
            if start_date:
                conditions.append("start_time >= ?")
                params.append(start_date.isoformat())
            
            if end_date:
                conditions.append("start_time <= ?")
                params.append(end_date.isoformat())
            
            if has_goal is not None:
                if has_goal:
                    conditions.append("goal IS NOT NULL AND goal != ''")
                else:
                    conditions.append("(goal IS NULL OR goal = '')")
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            sql = f"""
                SELECT * FROM conversations
                WHERE {where_clause}
                ORDER BY start_time DESC
            """
            
            cursor.execute(sql, params)
            return [dict(r) for r in cursor.fetchall()]
    
    def get_conversation_count(self) -> int:
        """Get total number of conversations"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM conversations")
            return cursor.fetchone()['count']
    
    def get_message_count(self, conversation_id: Optional[str] = None) -> int:
        """
        Get message count
        
        Args:
            conversation_id: Specific conversation or None for all
            
        Returns:
            Message count
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if conversation_id:
                cursor.execute("""
                    SELECT COUNT(*) as count FROM messages
                    WHERE conversation_id = ?
                """, (conversation_id,))
            else:
                cursor.execute("SELECT COUNT(*) as count FROM messages")
            
            return cursor.fetchone()['count']
    
    def export_conversation_jsonl(self, conversation_id: str) -> str:
        """
        Export conversation as JSONL line
        
        Args:
            conversation_id: Conversation to export
            
        Returns:
            JSON string
        """
        conv = self.get_conversation(conversation_id)
        if not conv:
            raise ValueError(f"Conversation not found: {conversation_id}")
        
        return json.dumps(conv, ensure_ascii=False)
    
    def export_to_jsonl(self, conversation_id: str, output_path: Path):
        """
        Export conversation to JSONL file
        
        Args:
            conversation_id: Conversation to export
            output_path: Path to output file
        """
        conv = self.get_conversation(conversation_id)
        if not conv:
            raise ValueError(f"Conversation not found: {conversation_id}")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(conv, f, ensure_ascii=False, indent=2)
    
    # Interactive Planning Session Management (CORTEX 2.1)
    
    def save_planning_session(self, session_data: Dict) -> bool:
        """
        Save interactive planning session to Tier 1.
        
        Args:
            session_data: Session data including questions, answers, plan
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Save session
                cursor.execute("""
                    INSERT OR REPLACE INTO planning_sessions 
                    (session_id, user_request, confidence, state, started_at, 
                     completed_at, final_plan, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_data['session_id'],
                    session_data['user_request'],
                    session_data['confidence'],
                    session_data['state'],
                    session_data['started_at'],
                    session_data.get('completed_at'),
                    json.dumps(session_data.get('final_plan')) if session_data.get('final_plan') else None,
                    json.dumps(session_data.get('metadata', {}))
                ))
                
                # Save questions
                for question in session_data.get('questions', []):
                    cursor.execute("""
                        INSERT OR REPLACE INTO planning_questions
                        (question_id, session_id, question_text, question_type,
                         options, default_answer, priority, context)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        question['id'],
                        session_data['session_id'],
                        question['text'],
                        question['type'],
                        json.dumps(question.get('options', [])),
                        question.get('default'),
                        question.get('priority', 3),
                        json.dumps(question.get('context', {}))
                    ))
                
                # Save answers
                for answer in session_data.get('answers', []):
                    cursor.execute("""
                        INSERT INTO planning_answers
                        (session_id, question_id, value, skipped, timestamp, additional_context)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        session_data['session_id'],
                        answer['question_id'],
                        answer['value'],
                        1 if answer.get('skipped', False) else 0,
                        answer['timestamp'],
                        json.dumps(answer.get('additional_context', {}))
                    ))
                
                conn.commit()
                return True
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error saving planning session: {e}")
            return False
    
    def load_planning_session(self, session_id: str) -> Optional[Dict]:
        """
        Load interactive planning session from Tier 1.
        
        Args:
            session_id: Session ID to load
            
        Returns:
            Session data dictionary or None if not found
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Load session
                cursor.execute("""
                    SELECT * FROM planning_sessions WHERE session_id = ?
                """, (session_id,))
                
                session_row = cursor.fetchone()
                if not session_row:
                    return None
                
                session_data = dict(session_row)
                
                # Parse JSON fields
                if session_data.get('final_plan'):
                    session_data['final_plan'] = json.loads(session_data['final_plan'])
                if session_data.get('metadata'):
                    session_data['metadata'] = json.loads(session_data['metadata'])
                
                # Load questions
                cursor.execute("""
                    SELECT * FROM planning_questions WHERE session_id = ?
                    ORDER BY priority DESC
                """, (session_id,))
                
                questions = []
                for q_row in cursor.fetchall():
                    q_dict = dict(q_row)
                    q_dict['options'] = json.loads(q_dict['options']) if q_dict.get('options') else []
                    q_dict['context'] = json.loads(q_dict['context']) if q_dict.get('context') else {}
                    questions.append(q_dict)
                
                session_data['questions'] = questions
                
                # Load answers
                cursor.execute("""
                    SELECT * FROM planning_answers WHERE session_id = ?
                    ORDER BY timestamp ASC
                """, (session_id,))
                
                answers = []
                for a_row in cursor.fetchall():
                    a_dict = dict(a_row)
                    a_dict['skipped'] = bool(a_dict['skipped'])
                    a_dict['additional_context'] = json.loads(a_dict['additional_context']) if a_dict.get('additional_context') else {}
                    answers.append(a_dict)
                
                session_data['answers'] = answers
                
                return session_data
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error loading planning session: {e}")
            return None
    
    def list_planning_sessions(
        self, 
        state: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        List planning sessions.
        
        Args:
            state: Filter by state (optional)
            limit: Maximum number to return
            
        Returns:
            List of session summaries
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                if state:
                    cursor.execute("""
                        SELECT session_id, user_request, confidence, state,
                               started_at, completed_at
                        FROM planning_sessions
                        WHERE state = ?
                        ORDER BY started_at DESC
                        LIMIT ?
                    """, (state, limit))
                else:
                    cursor.execute("""
                        SELECT session_id, user_request, confidence, state,
                               started_at, completed_at
                        FROM planning_sessions
                        ORDER BY started_at DESC
                        LIMIT ?
                    """, (limit,))
                
                return [dict(r) for r in cursor.fetchall()]
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error listing planning sessions: {e}")
            return []
    
    def _update_conversation_context(self, conversation_id: str, context: Dict[str, Any]):
        """
        Update conversation context (internal helper for planning doc sync)
        
        Args:
            conversation_id: Conversation to update
            context: Updated context dictionary
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE conversations
                SET context = ?
                WHERE conversation_id = ?
            """, (json.dumps(context), conversation_id))
            
            conn.commit()
