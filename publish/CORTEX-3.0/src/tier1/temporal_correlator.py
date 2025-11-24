"""
CORTEX 3.0 Milestone 2 - Temporal Correlation Layer

Implements the fusion layer that cross-references conversations with daemon events
to create complete development narratives. This is the core component of
dual-channel memory that links strategic discussions with tactical execution.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import sqlite3
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class CorrelationResult:
    """Result of temporal correlation between conversation and event."""
    conversation_id: str
    event_id: int
    correlation_type: str  # 'temporal', 'file_mention', 'plan_verification'
    confidence_score: float  # 0.0 to 1.0
    time_diff_seconds: int
    match_details: Dict[str, Any]


@dataclass
class ConversationTurn:
    """Represents a single conversation turn for correlation."""
    turn_id: str
    conversation_id: str
    content: str
    timestamp: datetime
    files_mentioned: List[str]
    phases_mentioned: List[str]


@dataclass
class AmbientEvent:
    """Represents an ambient daemon event for correlation."""
    event_id: int
    session_id: str
    event_type: str
    file_path: Optional[str]
    timestamp: datetime
    pattern: Optional[str]
    score: Optional[int]
    summary: str
    metadata: Dict[str, Any]


class TemporalCorrelator:
    """
    Core temporal correlation algorithm for CORTEX 3.0 dual-channel memory.
    
    Matches conversation turns with ambient daemon events using:
    1. Temporal proximity (±1 hour window)
    2. File mention matching (backtick paths in conversations)
    3. Plan verification (multi-phase tracking)
    """
    
    DEFAULT_TIME_WINDOW_SECONDS = 3600  # ±1 hour
    
    def __init__(self, db_path: str, time_window_seconds: int = None):
        """
        Initialize temporal correlator.
        
        Args:
            db_path: Path to Tier 1 working memory database
            time_window_seconds: Correlation time window (default: 3600 = 1 hour)
        """
        self.db_path = db_path
        self.time_window = time_window_seconds or self.DEFAULT_TIME_WINDOW_SECONDS
        self._init_schema()
    
    def _init_schema(self):
        """Ensure correlation tables exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ambient events table to store ambient daemon events
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ambient_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                file_path TEXT,
                pattern TEXT,
                score INTEGER,
                summary TEXT,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
        """)
        
        # Correlations table to store temporal matches
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS temporal_correlations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                event_id INTEGER NOT NULL,
                correlation_type TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                time_diff_seconds INTEGER NOT NULL,
                match_details TEXT,  -- JSON
                created_at TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id),
                FOREIGN KEY (event_id) REFERENCES ambient_events(id)
            )
        """)
        
        # Indexes for fast correlation queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_correlation_conversation 
            ON temporal_correlations(conversation_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_correlation_event 
            ON temporal_correlations(event_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_correlation_type 
            ON temporal_correlations(correlation_type)
        """)
        
        # Indexes for ambient events
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ambient_timestamp 
            ON ambient_events(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ambient_file 
            ON ambient_events(file_path)
        """)
        
        conn.commit()
        conn.close()
    
    def correlate_conversation(
        self, 
        conversation_id: str,
        force_recalculate: bool = False
    ) -> List[CorrelationResult]:
        """
        Find temporal correlations for a conversation with ambient events.
        
        Args:
            conversation_id: ID of imported conversation to correlate
            force_recalculate: If True, recalculate even if correlations exist
            
        Returns:
            List of correlation results ordered by confidence score
        """
        # Check if correlations already exist
        if not force_recalculate:
            existing = self._get_existing_correlations(conversation_id)
            if existing:
                logger.info(f"Found {len(existing)} existing correlations for {conversation_id}")
                return existing
        
        logger.info(f"Calculating temporal correlations for conversation {conversation_id}")
        
        # Get conversation turns
        turns = self._get_conversation_turns(conversation_id)
        if not turns:
            logger.warning(f"No turns found for conversation {conversation_id}")
            return []
        
        # Get ambient events in time window around conversation
        all_correlations = []
        for turn in turns:
            events = self._get_ambient_events_in_window(turn.timestamp, self.time_window)
            
            for event in events:
                correlations = self._calculate_correlations(turn, event)
                all_correlations.extend(correlations)
        
        # Sort by confidence score (highest first)
        all_correlations.sort(key=lambda x: x.confidence_score, reverse=True)
        
        # Store correlations in database
        self._store_correlations(all_correlations)
        
        logger.info(f"Found {len(all_correlations)} correlations for conversation {conversation_id}")
        return all_correlations
    
    def _get_conversation_turns(self, conversation_id: str) -> List[ConversationTurn]:
        """Extract conversation turns from imported conversation.
        
        Only returns assistant messages as they contain implementation details
        and file mentions that are relevant for temporal correlation.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get only assistant messages (they contain implementation details)
        cursor.execute("""
            SELECT id, role, content, timestamp
            FROM messages
            WHERE conversation_id = ? AND role = 'assistant'
            ORDER BY timestamp ASC
        """, (conversation_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        turns = []
        for msg_id, role, content, timestamp_str in rows:
            timestamp = datetime.fromisoformat(timestamp_str)
            
            # Extract file mentions (backtick paths)
            files_mentioned = self._extract_file_mentions(content)
            
            # Extract phase mentions
            phases_mentioned = self._extract_phase_mentions(content)
            
            turn = ConversationTurn(
                turn_id=f"{conversation_id}-{msg_id}",
                conversation_id=conversation_id,
                content=content,
                timestamp=timestamp,
                files_mentioned=files_mentioned,
                phases_mentioned=phases_mentioned
            )
            turns.append(turn)
        
        return turns
    
    def _get_ambient_events_in_window(
        self, 
        center_time: datetime, 
        window_seconds: int
    ) -> List[AmbientEvent]:
        """Get ambient events within time window of center_time."""
        start_time = center_time - timedelta(seconds=window_seconds)
        end_time = center_time + timedelta(seconds=window_seconds)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, session_id, event_type, file_path, pattern, score, 
                   summary, timestamp, metadata
            FROM ambient_events
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        """, (start_time.isoformat(), end_time.isoformat()))
        
        rows = cursor.fetchall()
        conn.close()
        
        events = []
        for row in rows:
            event_id, session_id, event_type, file_path, pattern, score, summary, timestamp_str, metadata_json = row
            
            events.append(AmbientEvent(
                event_id=event_id,
                session_id=session_id,
                event_type=event_type,
                file_path=file_path,
                timestamp=datetime.fromisoformat(timestamp_str),
                pattern=pattern,
                score=score,
                summary=summary,
                metadata=json.loads(metadata_json) if metadata_json else {}
            ))
        
        return events
    
    def _calculate_correlations(
        self, 
        turn: ConversationTurn, 
        event: AmbientEvent
    ) -> List[CorrelationResult]:
        """Calculate all possible correlations between a turn and event."""
        correlations = []
        
        # 1. Temporal correlation (always present if in window)
        time_diff = abs((event.timestamp - turn.timestamp).total_seconds())
        temporal_correlation = self._calculate_temporal_correlation(turn, event, time_diff)
        if temporal_correlation:
            correlations.append(temporal_correlation)
        
        # 2. File mention correlation
        file_correlation = self._calculate_file_mention_correlation(turn, event, time_diff)
        if file_correlation:
            correlations.append(file_correlation)
        
        # 3. Plan verification correlation
        plan_correlation = self._calculate_plan_verification_correlation(turn, event, time_diff)
        if plan_correlation:
            correlations.append(plan_correlation)
        
        return correlations
    
    def _calculate_temporal_correlation(
        self, 
        turn: ConversationTurn, 
        event: AmbientEvent, 
        time_diff: float
    ) -> Optional[CorrelationResult]:
        """Calculate basic temporal correlation score."""
        # Base score based on temporal proximity
        max_time_diff = self.time_window  # Maximum time difference
        temporal_score = 1.0 - (time_diff / max_time_diff)
        
        # Boost for high-score events
        if event.score and event.score > 70:
            temporal_score *= 1.2
        
        # Boost for certain event types
        if event.event_type in ['file_change', 'git_operation']:
            temporal_score *= 1.1
        
        # Cap at 1.0
        temporal_score = min(1.0, temporal_score)
        
        # Only create correlation if score is meaningful
        if temporal_score < 0.1:
            return None
        
        return CorrelationResult(
            conversation_id=turn.conversation_id,
            event_id=event.event_id,
            correlation_type='temporal',
            confidence_score=temporal_score,
            time_diff_seconds=int(time_diff),
            match_details={
                'event_type': event.event_type,
                'event_pattern': event.pattern,
                'event_score': event.score,
                'event_summary': event.summary
            }
        )
    
    def _calculate_file_mention_correlation(
        self, 
        turn: ConversationTurn, 
        event: AmbientEvent, 
        time_diff: float
    ) -> Optional[CorrelationResult]:
        """Calculate file mention correlation score."""
        if not turn.files_mentioned or not event.file_path:
            return None
        
        # Check for file path matches
        event_file = Path(event.file_path)
        matched_files = []
        
        for mentioned_file in turn.files_mentioned:
            mentioned_path = Path(mentioned_file)
            
            # Exact match
            if event_file == mentioned_path:
                matched_files.append({
                    'mentioned': mentioned_file,
                    'actual': event.file_path,
                    'match_type': 'exact'
                })
            # Name match (same filename, different path)
            elif event_file.name == mentioned_path.name:
                matched_files.append({
                    'mentioned': mentioned_file,
                    'actual': event.file_path,
                    'match_type': 'filename'
                })
            # Parent directory match
            elif str(mentioned_path) in str(event_file) or str(event_file) in str(mentioned_path):
                matched_files.append({
                    'mentioned': mentioned_file,
                    'actual': event.file_path,
                    'match_type': 'partial'
                })
        
        if not matched_files:
            return None
        
        # Calculate confidence based on match quality and temporal proximity
        base_score = 0.8  # High base score for file matches
        
        # Adjust based on match type
        best_match = max(matched_files, key=lambda x: {
            'exact': 1.0, 'filename': 0.7, 'partial': 0.4
        }[x['match_type']])
        
        match_multiplier = {
            'exact': 1.0,
            'filename': 0.8, 
            'partial': 0.6
        }[best_match['match_type']]
        
        # Temporal proximity bonus
        temporal_bonus = 1.0 - (time_diff / self.time_window) * 0.3
        
        confidence_score = base_score * match_multiplier * temporal_bonus
        confidence_score = min(1.0, confidence_score)
        
        return CorrelationResult(
            conversation_id=turn.conversation_id,
            event_id=event.event_id,
            correlation_type='file_mention',
            confidence_score=confidence_score,
            time_diff_seconds=int(time_diff),
            match_details={
                'matched_files': matched_files,
                'best_match': best_match,
                'event_summary': event.summary
            }
        )
    
    def _calculate_plan_verification_correlation(
        self, 
        turn: ConversationTurn, 
        event: AmbientEvent, 
        time_diff: float
    ) -> Optional[CorrelationResult]:
        """Calculate plan verification correlation score."""
        if not turn.phases_mentioned:
            return None
        
        # Look for plan execution indicators in event
        plan_indicators = [
            'phase', 'step', 'milestone', 'implementation', 
            'feature', 'refactor', 'test', 'deploy'
        ]
        
        event_text = (event.summary or '').lower()
        pattern_text = (event.pattern or '').lower()
        
        plan_matches = []
        for indicator in plan_indicators:
            if indicator in event_text or indicator in pattern_text:
                plan_matches.append(indicator)
        
        if not plan_matches:
            return None
        
        # Base score for plan correlation
        base_score = 0.6
        
        # Boost for high-score events (likely important)
        if event.score and event.score > 80:
            base_score *= 1.3
        
        # Boost for multiple plan indicators
        if len(plan_matches) > 1:
            base_score *= 1.2
        
        # Temporal proximity factor
        temporal_factor = 1.0 - (time_diff / self.time_window) * 0.4
        
        confidence_score = base_score * temporal_factor
        confidence_score = min(1.0, confidence_score)
        
        return CorrelationResult(
            conversation_id=turn.conversation_id,
            event_id=event.event_id,
            correlation_type='plan_verification',
            confidence_score=confidence_score,
            time_diff_seconds=int(time_diff),
            match_details={
                'phases_mentioned': turn.phases_mentioned,
                'plan_indicators_found': plan_matches,
                'event_pattern': event.pattern,
                'event_summary': event.summary
            }
        )
    
    def _extract_file_mentions(self, content: str) -> List[str]:
        """Extract file paths mentioned in conversation content."""
        files = []
        
        # Pattern 1: Backtick file paths: `path/to/file.ext`
        pattern1 = r'`([^`]+\.[a-zA-Z0-9]{1,6})`'
        matches1 = re.findall(pattern1, content)
        files.extend(matches1)
        
        # Pattern 2: List items with file paths: - Create path/to/file.ext
        pattern2 = r'[-•*]\s*(?:Create|Update|Modify|Add|Delete)?\s*([a-zA-Z0-9_/-]+\.[a-zA-Z0-9]{1,6})'
        matches2 = re.findall(pattern2, content, re.IGNORECASE)
        files.extend(matches2)
        
        # Pattern 3: Plain file paths in text: path/to/file.ext (but not URLs)
        pattern3 = r'\b([a-zA-Z0-9_/-]+\.[a-zA-Z0-9]{1,6})\b'
        matches3 = re.findall(pattern3, content)
        # Filter out URLs and overly generic matches
        for match in matches3:
            # Skip if it's part of a URL
            if 'http://' + match in content or 'https://' + match in content:
                continue
            if '/' in match or any(match.endswith(ext) for ext in ['.py', '.js', '.ts', '.html', '.css']):
                files.append(match)
        
        # Filter by valid file extensions
        file_extensions = {
            '.py', '.js', '.ts', '.html', '.css', '.md', '.yaml', '.yml', 
            '.json', '.txt', '.sh', '.sql', '.xml', '.log', '.conf', '.cs'
        }
        
        valid_files = []
        for file_path in files:
            if any(file_path.endswith(ext) for ext in file_extensions):
                # Clean up the path (remove leading spaces/dashes)
                clean_path = file_path.strip(' -•*')
                if clean_path and clean_path not in valid_files:
                    valid_files.append(clean_path)
        
        return valid_files
    
    def _extract_phase_mentions(self, content: str) -> List[str]:
        """Extract phase mentions from conversation content."""
        # Match "Phase 1:", "Phase 2:", etc.
        pattern = r'Phase\s+(\d+)'
        matches = re.findall(pattern, content, re.IGNORECASE)
        return [f"Phase {match}" for match in matches]
    
    def _get_existing_correlations(self, conversation_id: str) -> List[CorrelationResult]:
        """Get existing correlations for a conversation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT conversation_id, event_id, correlation_type, confidence_score,
                   time_diff_seconds, match_details
            FROM temporal_correlations
            WHERE conversation_id = ?
            ORDER BY confidence_score DESC
        """, (conversation_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        correlations = []
        for row in rows:
            conv_id, event_id, corr_type, score, time_diff, details_json = row
            
            correlations.append(CorrelationResult(
                conversation_id=conv_id,
                event_id=event_id,
                correlation_type=corr_type,
                confidence_score=score,
                time_diff_seconds=time_diff,
                match_details=json.loads(details_json) if details_json else {}
            ))
        
        return correlations
    
    def _store_correlations(self, correlations: List[CorrelationResult]):
        """Store correlations in database."""
        if not correlations:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing correlations for these conversations
        conversation_ids = list(set(c.conversation_id for c in correlations))
        placeholders = ','.join('?' * len(conversation_ids))
        cursor.execute(f"""
            DELETE FROM temporal_correlations
            WHERE conversation_id IN ({placeholders})
        """, conversation_ids)
        
        # Insert new correlations
        for correlation in correlations:
            cursor.execute("""
                INSERT INTO temporal_correlations 
                (conversation_id, event_id, correlation_type, confidence_score,
                 time_diff_seconds, match_details, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                correlation.conversation_id,
                correlation.event_id,
                correlation.correlation_type,
                correlation.confidence_score,
                correlation.time_diff_seconds,
                json.dumps(correlation.match_details),
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Stored {len(correlations)} correlations in database")
    
    def get_conversation_timeline(self, conversation_id: str) -> Dict[str, Any]:
        """
        Generate a unified timeline of conversation turns and correlated events.
        
        Args:
            conversation_id: ID of conversation to analyze
            
        Returns:
            Timeline data with conversation turns and correlated events
        """
        # Get conversation turns (always include these)
        turns = self._get_conversation_turns(conversation_id)
        
        # Get correlations for this conversation
        correlations = self.correlate_conversation(conversation_id)
        
        # Build timeline starting with conversation turns
        timeline = []
        
        # Add conversation turns (always present)
        for turn in turns:
            timeline.append({
                'type': 'conversation_turn',
                'timestamp': turn.timestamp,
                'content': turn.content[:200] + '...' if len(turn.content) > 200 else turn.content,
                'files_mentioned': turn.files_mentioned,
                'phases_mentioned': turn.phases_mentioned
            })

        # Add correlated events if any exist
        if correlations:
            # Get correlated events
            event_ids = [c.event_id for c in correlations]
            events_by_id = {}
            
            if event_ids:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                placeholders = ','.join('?' * len(event_ids))
                cursor.execute(f"""
                    SELECT id, session_id, event_type, file_path, pattern, score,
                           summary, timestamp, metadata
                    FROM ambient_events
                    WHERE id IN ({placeholders})
                """, event_ids)
                
                for row in cursor.fetchall():
                    event_id = row[0]
                    events_by_id[event_id] = AmbientEvent(
                        event_id=row[0],
                        session_id=row[1],
                        event_type=row[2],
                        file_path=row[3],
                        timestamp=datetime.fromisoformat(row[7]),
                        pattern=row[4],
                        score=row[5],
                        summary=row[6],
                        metadata=json.loads(row[8]) if row[8] else {}
                    )
                
                conn.close()

            # Add correlated events to timeline
            for correlation in correlations:
                event = events_by_id.get(correlation.event_id)
                if event:
                    timeline.append({
                        'type': 'ambient_event',
                        'timestamp': event.timestamp,
                        'event_type': event.event_type,
                        'file_path': event.file_path,
                        'summary': event.summary,
                        'pattern': event.pattern,
                        'score': event.score,
                        'correlation_type': correlation.correlation_type,
                        'confidence_score': correlation.confidence_score
                    })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'])
        
        # Generate summary
        if correlations:
            high_confidence = [c for c in correlations if c.confidence_score > 0.7]
            summary = f"Found {len(correlations)} correlations ({len(high_confidence)} high-confidence)"
        else:
            summary = 'No correlations found, showing conversation only'

        return {
            'conversation_id': conversation_id,
            'timeline': timeline,
            'correlations_count': len(correlations),
            'high_confidence_count': len([c for c in correlations if c.confidence_score > 0.7]),
            'summary': summary
        }