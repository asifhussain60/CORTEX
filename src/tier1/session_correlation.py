"""
CORTEX 3.0 - Session-Ambient Correlation Layer

Links session-based conversations with ambient capture events to create
complete development narratives.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class SessionAmbientCorrelator:
    """Correlates session-based conversations with ambient capture events."""
    
    def __init__(self, db_path: str):
        """
        Initialize correlator.
        
        Args:
            db_path: Path to Tier 1 working memory database
        """
        self.db_path = db_path
        self._init_schema()
    
    def _init_schema(self):
        """Ensure correlation tables exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Add ambient_events table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ambient_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                conversation_id TEXT,
                event_type TEXT NOT NULL,
                file_path TEXT,
                pattern TEXT,
                score INTEGER,
                summary TEXT,
                timestamp TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        # Indexes for fast queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ambient_session 
            ON ambient_events(session_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ambient_conversation 
            ON ambient_events(conversation_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ambient_timestamp 
            ON ambient_events(timestamp)
        """)
        
        conn.commit()
        conn.close()
    
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
        
        Args:
            session_id: Active workspace session ID
            event_type: Type of event (file_change, terminal_command, git_operation)
            file_path: Path to affected file
            pattern: Detected pattern (FEATURE, BUGFIX, etc.)
            score: Activity score (0-100)
            summary: Natural language summary
            conversation_id: Optional active conversation ID
            metadata: Additional event metadata
            
        Returns:
            Event ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        import json
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute("""
            INSERT INTO ambient_events 
            (session_id, conversation_id, event_type, file_path, pattern, score, summary, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            conversation_id,
            event_type,
            file_path,
            pattern,
            score,
            summary,
            datetime.now().isoformat(),
            metadata_json
        ))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return event_id
    
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
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT id, session_id, conversation_id, event_type, file_path, 
                   pattern, score, summary, timestamp, metadata
            FROM ambient_events
            WHERE session_id = ?
        """
        params = [session_id]
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        if min_score is not None:
            query += " AND score >= ?"
            params.append(min_score)
        
        query += " ORDER BY timestamp ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        import json
        events = []
        for row in rows:
            events.append({
                "id": row[0],
                "session_id": row[1],
                "conversation_id": row[2],
                "event_type": row[3],
                "file_path": row[4],
                "pattern": row[5],
                "score": row[6],
                "summary": row[7],
                "timestamp": row[8],
                "metadata": json.loads(row[9]) if row[9] else None
            })
        
        return events
    
    def get_conversation_events(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get all ambient events that occurred during a conversation.
        
        Args:
            conversation_id: Conversation ID to query
            
        Returns:
            List of events with metadata
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Simple query: get all events with this conversation_id
        # (Events can be tagged with conversation_id when logged)
        cursor.execute("""
            SELECT id, session_id, conversation_id, event_type, file_path, 
                   pattern, score, summary, timestamp, metadata
            FROM ambient_events
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
        """, (conversation_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        import json
        events = []
        for row in rows:
            events.append({
                "id": row[0],
                "session_id": row[1],
                "conversation_id": row[2],
                "event_type": row[3],
                "file_path": row[4],
                "pattern": row[5],
                "score": row[6],
                "summary": row[7],
                "timestamp": row[8],
                "metadata": json.loads(row[9]) if row[9] else None
            })
        
        return events
    
    def generate_session_narrative(self, session_id: str) -> str:
        """
        Generate complete development narrative for a session.
        
        Combines conversations + ambient events into coherent story.
        
        Args:
            session_id: Session ID to narrate
            
        Returns:
            Natural language narrative
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get session info
        cursor.execute("""
            SELECT workspace_path, start_time, end_time, conversation_count
            FROM sessions
            WHERE session_id = ?
        """, (session_id,))
        
        session_result = cursor.fetchone()
        if not session_result:
            conn.close()
            return f"Session {session_id} not found"
        
        workspace, start, end, conv_count = session_result
        
        # Get all conversations in session
        cursor.execute("""
            SELECT conversation_id, title, workflow_state, created_at, updated_at
            FROM conversations
            WHERE session_id = ?
            ORDER BY created_at ASC
        """, (session_id,))
        
        conversations = cursor.fetchall()
        
        # Get all ambient events
        events = self.get_session_events(session_id)
        
        conn.close()
        
        # Build narrative
        narrative = []
        narrative.append(f"# Development Session: {session_id}")
        narrative.append(f"**Workspace:** {workspace}")
        narrative.append(f"**Started:** {start}")
        narrative.append(f"**Duration:** {self._format_duration(start, end)}")
        narrative.append(f"**Conversations:** {conv_count}")
        narrative.append("")
        
        if conversations:
            narrative.append("## Conversations")
            for conv in conversations:
                conv_id, title, state, created, updated = conv
                narrative.append(f"### {title or conv_id}")
                narrative.append(f"- **State:** {state or 'ACTIVE'}")
                narrative.append(f"- **Timeline:** {created} → {updated}")
                
                # Get events during this conversation
                conv_events = self.get_conversation_events(conv_id)
                if conv_events:
                    narrative.append(f"- **Activity:** {len(conv_events)} events")
                    for event in conv_events[:5]:  # Top 5
                        narrative.append(f"  - {event['summary']} ({event['pattern']}, score: {event['score']})")
                narrative.append("")
        
        if events:
            narrative.append("## All Session Activity")
            narrative.append(f"**Total Events:** {len(events)}")
            
            # Group by pattern
            by_pattern = {}
            for event in events:
                pattern = event.get('pattern', 'UNKNOWN')
                by_pattern.setdefault(pattern, []).append(event)
            
            for pattern, pattern_events in by_pattern.items():
                narrative.append(f"### {pattern} ({len(pattern_events)} events)")
                for event in pattern_events[:10]:  # Top 10
                    narrative.append(f"- {event['summary']} (score: {event['score']})")
                narrative.append("")
        
        return "\n".join(narrative)
    
    def _format_duration(self, start: str, end: Optional[str]) -> str:
        """Format session duration."""
        from datetime import datetime
        
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end) if end else datetime.now()
        
        duration = end_dt - start_dt
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
