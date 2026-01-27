"""
Conversation state persistence for multi-turn orchestration.

Stores conversation history, context aggregation, and turn metadata
in SQLite database for recovery and audit.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import sqlite3
import json
from uuid import uuid4, UUID


@dataclass
class TurnRecord:
    """Record of a single turn in a conversation."""
    
    turn_number: int
    user_input: str
    orchestrator_output: Dict[str, Any]
    context_state: Dict[str, Any]
    timestamp: datetime
    duration_ms: float
    tokens_used: int
    continuation_reason: str


@dataclass
class ConversationState:
    """Persistent state for a multi-turn conversation."""
    
    conversation_id: UUID
    turn_history: List[TurnRecord] = field(default_factory=list)
    context_state: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    orchestrator_name: str = ""
    total_turns: int = 0
    total_tokens: int = 0
    is_complete: bool = False


class ConversationStateManager:
    """Manages conversation state persistence to SQLite."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize state manager.
        
        Args:
            db_path: Path to SQLite database. Defaults to cortex_brain/state/conversations.db
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent.parent.parent / "cortex_brain" / "state" / "conversations.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self) -> None:
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    orchestrator_name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    total_turns INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    is_complete BOOLEAN DEFAULT 0,
                    context_state TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS turn_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    turn_number INTEGER NOT NULL,
                    user_input TEXT NOT NULL,
                    orchestrator_output TEXT NOT NULL,
                    context_state TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    duration_ms REAL NOT NULL,
                    tokens_used INTEGER NOT NULL,
                    continuation_reason TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id),
                    UNIQUE (conversation_id, turn_number)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_updated 
                ON conversations(updated_at DESC)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_turn_records_conversation 
                ON turn_records(conversation_id, turn_number)
            """)
            
            conn.commit()
    
    def create_conversation(self, orchestrator_name: str) -> UUID:
        """
        Create a new conversation.
        
        Args:
            orchestrator_name: Name of the orchestrator
            
        Returns:
            UUID of the new conversation
        """
        conversation_id = uuid4()
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO conversations 
                (conversation_id, orchestrator_name, created_at, updated_at, context_state)
                VALUES (?, ?, ?, ?, ?)
            """, (str(conversation_id), orchestrator_name, now, now, "{}"))
            conn.commit()
        
        return conversation_id
    
    def save_turn(
        self,
        conversation_id: UUID,
        turn_record: TurnRecord
    ) -> None:
        """
        Save a turn record to the database.
        
        Args:
            conversation_id: UUID of the conversation
            turn_record: Turn record to save
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO turn_records 
                (conversation_id, turn_number, user_input, orchestrator_output, 
                 context_state, timestamp, duration_ms, tokens_used, continuation_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(conversation_id),
                turn_record.turn_number,
                turn_record.user_input,
                json.dumps(turn_record.orchestrator_output),
                json.dumps(turn_record.context_state),
                turn_record.timestamp.isoformat(),
                turn_record.duration_ms,
                turn_record.tokens_used,
                turn_record.continuation_reason
            ))
            conn.commit()
    
    def update_conversation(self, state: ConversationState) -> None:
        """
        Update conversation metadata.
        
        Args:
            state: Conversation state to update
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE conversations
                SET updated_at = ?,
                    total_turns = ?,
                    total_tokens = ?,
                    is_complete = ?,
                    context_state = ?
                WHERE conversation_id = ?
            """, (
                datetime.now().isoformat(),
                state.total_turns,
                state.total_tokens,
                1 if state.is_complete else 0,
                json.dumps(state.context_state),
                str(state.conversation_id)
            ))
            conn.commit()
    
    def load_conversation(self, conversation_id: UUID) -> Optional[ConversationState]:
        """
        Load conversation state from database.
        
        Args:
            conversation_id: UUID of the conversation
            
        Returns:
            ConversationState if found, None otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM conversations WHERE conversation_id = ?
            """, (str(conversation_id),))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Load turn records
            turn_cursor = conn.execute("""
                SELECT * FROM turn_records 
                WHERE conversation_id = ?
                ORDER BY turn_number
            """, (str(conversation_id),))
            
            turn_records = []
            for turn_row in turn_cursor.fetchall():
                turn_records.append(TurnRecord(
                    turn_number=turn_row["turn_number"],
                    user_input=turn_row["user_input"],
                    orchestrator_output=json.loads(turn_row["orchestrator_output"]),
                    context_state=json.loads(turn_row["context_state"]),
                    timestamp=datetime.fromisoformat(turn_row["timestamp"]),
                    duration_ms=turn_row["duration_ms"],
                    tokens_used=turn_row["tokens_used"],
                    continuation_reason=turn_row["continuation_reason"]
                ))
            
            return ConversationState(
                conversation_id=UUID(row["conversation_id"]),
                orchestrator_name=row["orchestrator_name"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
                total_turns=row["total_turns"],
                total_tokens=row["total_tokens"],
                is_complete=bool(row["is_complete"]),
                context_state=json.loads(row["context_state"]),
                turn_history=turn_records
            )
    
    def list_conversations(
        self,
        limit: int = 50,
        include_completed: bool = True
    ) -> List[ConversationState]:
        """
        List recent conversations.
        
        Args:
            limit: Maximum number of conversations to return
            include_completed: Whether to include completed conversations
            
        Returns:
            List of conversation states
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            query = """
                SELECT * FROM conversations
                WHERE is_complete = ? OR ? = 1
                ORDER BY updated_at DESC
                LIMIT ?
            """
            
            cursor = conn.execute(
                query,
                (0, 1 if include_completed else 0, limit)
            )
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append(ConversationState(
                    conversation_id=UUID(row["conversation_id"]),
                    orchestrator_name=row["orchestrator_name"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                    total_turns=row["total_turns"],
                    total_tokens=row["total_tokens"],
                    is_complete=bool(row["is_complete"]),
                    context_state=json.loads(row["context_state"]),
                    turn_history=[]  # Don't load full history for listings
                ))
            
            return conversations
