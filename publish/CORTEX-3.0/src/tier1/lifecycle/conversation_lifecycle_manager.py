"""
Conversation Lifecycle Manager - Handles conversation creation, workflow tracking, and closure.

Implements CORTEX 3.0 session-based conversation lifecycle:
- Auto-creates conversations on session start
- Tracks workflow state progression
- Auto-closes conversations on workflow completion
- Detects explicit user commands (new conversation, continue)
"""

import sqlite3
import re
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class WorkflowState(Enum):
    """Workflow states for conversation progression."""
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    TESTING = "TESTING"
    VALIDATING = "VALIDATING"
    COMPLETE = "COMPLETE"
    ABANDONED = "ABANDONED"


@dataclass
class ConversationLifecycleEvent:
    """Represents a lifecycle event for a conversation."""
    event_type: str  # created, state_changed, closed, abandoned
    conversation_id: str
    session_id: str
    timestamp: datetime
    old_state: Optional[str]
    new_state: Optional[str]
    trigger: str  # auto, explicit_command, workflow_complete, idle_timeout


class ConversationLifecycleManager:
    """Manages conversation lifecycle within sessions."""
    
    # Command patterns for explicit user control
    NEW_CONVERSATION_PATTERNS = [
        r'\bnew conversation\b',
        r'\bstart fresh\b',
        r'\bnew topic\b',
        r'\bfresh start\b',
        r'\bbegin new\b',
        r'\breset conversation\b'
    ]
    
    CONTINUE_PATTERNS = [
        r'\bcontinue\b',
        r'\bkeep going\b',
        r'\bresume\b',
        r'\bgo on\b',
        r'\bkeep working\b'
    ]
    
    # Workflow progression keywords
    WORKFLOW_KEYWORDS = {
        WorkflowState.PLANNING: [
            r'\bplan\b', r'\bdesign\b', r'\barchitect\b', r'\blet\'s plan\b',
            r'\bhow should\b', r'\bwhat if\b', r'\bshould we\b'
        ],
        WorkflowState.EXECUTING: [
            r'\badd\b', r'\bcreate\b', r'\bimplement\b', r'\bbuild\b',
            r'\bwrite\b', r'\bgenerate\b', r'\bmodify\b', r'\bupdate\b'
        ],
        WorkflowState.TESTING: [
            r'\btest\b', r'\brun tests\b', r'\bverify\b', r'\bcheck\b',
            r'\bvalidate\b', r'\bdoes it work\b'
        ],
        WorkflowState.VALIDATING: [
            r'\breview\b', r'\binspect\b', r'\baudit\b', r'\bconfirm\b',
            r'\bverify quality\b', r'\bfinal check\b'
        ]
    }
    
    def __init__(self, db_path: Path):
        """
        Initialize lifecycle manager.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Ensure lifecycle tracking table exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create lifecycle events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_lifecycle_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                conversation_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                old_state TEXT,
                new_state TEXT,
                trigger TEXT NOT NULL
            )
        """)
        
        # Create index for conversation queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_lifecycle_conversation 
            ON conversation_lifecycle_events(conversation_id)
        """)
        
        # Create index for session queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_lifecycle_session 
            ON conversation_lifecycle_events(session_id)
        """)
        
        conn.commit()
        conn.close()
    
    def detect_command_intent(self, user_request: str) -> Tuple[str, float]:
        """
        Detect explicit command intent from user request.
        
        Args:
            user_request: User's message
        
        Returns:
            Tuple of (intent, confidence) where:
                intent: "new_conversation" | "continue" | "none"
                confidence: 0.0-1.0
        """
        user_request_lower = user_request.lower()
        
        # Check for new conversation patterns
        for pattern in self.NEW_CONVERSATION_PATTERNS:
            if re.search(pattern, user_request_lower):
                return ("new_conversation", 0.9)
        
        # Check for continue patterns
        for pattern in self.CONTINUE_PATTERNS:
            if re.search(pattern, user_request_lower):
                return ("continue", 0.85)
        
        return ("none", 0.0)
    
    def infer_workflow_state(self, user_request: str, current_state: Optional[WorkflowState] = None) -> WorkflowState:
        """
        Infer workflow state from user request.
        
        Args:
            user_request: User's message
            current_state: Current workflow state (if any)
        
        Returns:
            Inferred WorkflowState
        """
        user_request_lower = user_request.lower()
        
        # Check each workflow state's keywords
        state_scores = {}
        
        for state, patterns in self.WORKFLOW_KEYWORDS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, user_request_lower):
                    score += 1
            state_scores[state] = score
        
        # Find state with highest score
        if state_scores:
            max_score = max(state_scores.values())
            if max_score > 0:
                inferred_state = max(state_scores.items(), key=lambda x: x[1])[0]
                return inferred_state
        
        # Default progression based on current state
        if current_state:
            state_progression = {
                WorkflowState.PLANNING: WorkflowState.EXECUTING,
                WorkflowState.EXECUTING: WorkflowState.TESTING,
                WorkflowState.TESTING: WorkflowState.VALIDATING,
                WorkflowState.VALIDATING: WorkflowState.COMPLETE
            }
            return state_progression.get(current_state, current_state)
        
        # Default to PLANNING for new conversations
        return WorkflowState.PLANNING
    
    def should_create_conversation(
        self,
        session_id: str,
        user_request: str,
        has_active_conversation: bool
    ) -> Tuple[bool, str]:
        """
        Determine if new conversation should be created.
        
        Args:
            session_id: Current session ID
            user_request: User's message
            has_active_conversation: Whether session has active conversation
        
        Returns:
            Tuple of (should_create, reason)
        """
        # Check explicit command
        intent, confidence = self.detect_command_intent(user_request)
        
        if intent == "new_conversation":
            return (True, "explicit_command")
        
        if intent == "continue" and has_active_conversation:
            return (False, "explicit_continue")
        
        # No active conversation -> create new
        if not has_active_conversation:
            return (True, "no_active_conversation")
        
        # Has active conversation but user said "continue" -> don't create
        if intent == "continue":
            return (False, "explicit_continue")
        
        # Default: continue existing conversation
        return (False, "default_continuation")
    
    def should_close_conversation(
        self,
        conversation_id: str,
        current_state: WorkflowState,
        user_request: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Determine if conversation should be closed.
        
        Args:
            conversation_id: Conversation to check
            current_state: Current workflow state
            user_request: Optional user message
        
        Returns:
            Tuple of (should_close, reason)
        """
        # Workflow complete -> close
        if current_state == WorkflowState.COMPLETE:
            return (True, "workflow_complete")
        
        # Explicit new conversation request -> close current
        if user_request:
            intent, _ = self.detect_command_intent(user_request)
            if intent == "new_conversation":
                return (True, "new_conversation_requested")
        
        # Don't close otherwise
        return (False, "active")
    
    def update_workflow_state(
        self,
        conversation_id: str,
        session_id: str,
        new_state: WorkflowState,
        trigger: str = "auto"
    ) -> None:
        """
        Update conversation workflow state.
        
        Args:
            conversation_id: Conversation to update
            session_id: Associated session
            new_state: New workflow state
            trigger: What triggered the update
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current state
        cursor.execute("""
            SELECT workflow_state FROM conversations 
            WHERE conversation_id = ?
        """, (conversation_id,))
        
        row = cursor.fetchone()
        old_state = row[0] if row else None
        
        # Update state
        cursor.execute("""
            UPDATE conversations
            SET workflow_state = ?,
                last_activity = ?
            WHERE conversation_id = ?
        """, (new_state.value, datetime.now().isoformat(), conversation_id))
        
        # Log event
        cursor.execute("""
            INSERT INTO conversation_lifecycle_events
            (event_type, conversation_id, session_id, timestamp, old_state, new_state, trigger)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "state_changed",
            conversation_id,
            session_id,
            datetime.now().isoformat(),
            old_state,
            new_state.value,
            trigger
        ))
        
        conn.commit()
        conn.close()
    
    def close_conversation(
        self,
        conversation_id: str,
        session_id: str,
        reason: str,
        final_state: WorkflowState = WorkflowState.COMPLETE
    ) -> None:
        """
        Close a conversation.
        
        Args:
            conversation_id: Conversation to close
            session_id: Associated session
            reason: Reason for closure
            final_state: Final workflow state
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update conversation
        cursor.execute("""
            UPDATE conversations
            SET is_active = 0,
                workflow_state = ?,
                last_activity = ?
            WHERE conversation_id = ?
        """, (final_state.value, datetime.now().isoformat(), conversation_id))
        
        # Log event
        cursor.execute("""
            INSERT INTO conversation_lifecycle_events
            (event_type, conversation_id, session_id, timestamp, old_state, new_state, trigger)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "closed",
            conversation_id,
            session_id,
            datetime.now().isoformat(),
            None,
            final_state.value,
            reason
        ))
        
        conn.commit()
        conn.close()
    
    def log_conversation_created(
        self,
        conversation_id: str,
        session_id: str,
        trigger: str,
        initial_state: WorkflowState = WorkflowState.PLANNING
    ) -> None:
        """
        Log conversation creation event.
        
        Args:
            conversation_id: Created conversation
            session_id: Associated session
            trigger: What triggered creation
            initial_state: Initial workflow state
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO conversation_lifecycle_events
            (event_type, conversation_id, session_id, timestamp, old_state, new_state, trigger)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "created",
            conversation_id,
            session_id,
            datetime.now().isoformat(),
            None,
            initial_state.value,
            trigger
        ))
        
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, conversation_id: str) -> List[ConversationLifecycleEvent]:
        """
        Get lifecycle history for a conversation.
        
        Args:
            conversation_id: Conversation to query
        
        Returns:
            List of lifecycle events
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT event_type, conversation_id, session_id, timestamp, 
                   old_state, new_state, trigger
            FROM conversation_lifecycle_events
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
        """, (conversation_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        events = []
        for row in rows:
            events.append(ConversationLifecycleEvent(
                event_type=row[0],
                conversation_id=row[1],
                session_id=row[2],
                timestamp=datetime.fromisoformat(row[3]),
                old_state=row[4],
                new_state=row[5],
                trigger=row[6]
            ))
        
        return events
    
    def get_session_conversation_history(self, session_id: str) -> List[ConversationLifecycleEvent]:
        """
        Get all conversation events for a session.
        
        Args:
            session_id: Session to query
        
        Returns:
            List of lifecycle events
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT event_type, conversation_id, session_id, timestamp,
                   old_state, new_state, trigger
            FROM conversation_lifecycle_events
            WHERE session_id = ?
            ORDER BY timestamp ASC
        """, (session_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        events = []
        for row in rows:
            events.append(ConversationLifecycleEvent(
                event_type=row[0],
                conversation_id=row[1],
                session_id=row[2],
                timestamp=datetime.fromisoformat(row[3]),
                old_state=row[4],
                new_state=row[5],
                trigger=row[6]
            ))
        
        return events
