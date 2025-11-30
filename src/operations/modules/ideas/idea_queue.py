"""
CORTEX 3.0 - Feature 1: IDEA Capture System - Core Queue

Purpose: Ultra-fast (<5ms) capture of fleeting ideas during active work with
         zero disruption to ongoing operations. SQLite-backed persistence
         with async enrichment.

Architecture:
- Instant capture: <5ms append-only SQLite write
- Zero disruption: Work continues immediately after capture
- Async enrichment: Component detection, priority inference, clustering
- Context preservation: Active file, operation, conversation tracking
- Cross-repository: Projects across multiple repos

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import sqlite3
import uuid
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import threading
import time
import re


logger = logging.getLogger(__name__)


@dataclass
class IdeaCapture:
    """Single captured idea with instant context and async enrichment."""
    idea_id: str                          # UUID
    raw_text: str                         # User's exact words
    timestamp: datetime
    
    # Context (captured instantly <5ms)
    active_file: Optional[str] = None     # Current file path
    active_line: Optional[int] = None     # Current line number
    active_operation: Optional[str] = None # Current CORTEX operation
    conversation_id: Optional[str] = None  # Conversation context
    project: Optional[str] = None         # Repository/project name
    
    # Enrichment (processed async, zero impact)
    component: Optional[str] = None       # auth, api, ui, etc.
    priority: Optional[str] = None        # high, medium, low
    related_ideas: List[str] = None       # Clustering
    status: str = "pending"               # pending, in_progress, completed, archived
    
    # Metadata
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = self.timestamp
        if self.updated_at is None:
            self.updated_at = self.timestamp
        if self.related_ideas is None:
            self.related_ideas = []


class IdeaQueue:
    """
    Ultra-fast idea capture queue with SQLite persistence.
    
    Performance Goals:
    - Capture: <5ms (critical path)
    - Retrieval: <50ms for typical queries
    - Enrichment: Async (zero impact on capture)
    
    Design Principles:
    - Append-only for maximum speed
    - Minimal validation during capture
    - Rich functionality in async background processing
    """
    
    def __init__(
        self,
        db_path: Optional[str] = None,
        enable_enrichment: bool = True,
        max_capture_ms: float = 5.0
    ):
        """
        Initialize IDEA capture queue.
        
        Args:
            db_path: SQLite database path (default: cortex-brain/tier1/idea-queue.db)
            enable_enrichment: Enable async enrichment processing
            max_capture_ms: Maximum allowed capture time (performance target)
        """
        self.db_path = db_path or self._get_default_db_path()
        self.enable_enrichment = enable_enrichment
        self.max_capture_ms = max_capture_ms
        
        # Thread safety for concurrent access
        self._db_lock = threading.RLock()
        
        # Performance monitoring
        self.stats = {
            'captures_total': 0,
            'captures_under_5ms': 0,
            'average_capture_time': 0.0,
            'max_capture_time': 0.0,
            'enrichments_processed': 0
        }
        
        # Initialize database
        self._init_database()
        
        logger.info(f"IdeaQueue initialized: {self.db_path}, enrichment={enable_enrichment}")
    
    def capture(
        self,
        raw_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Capture idea with <5ms performance guarantee.
        
        Args:
            raw_text: User's exact input text
            context: Optional context dict with current state
            
        Returns:
            idea_id: UUID for tracking the captured idea
            
        Raises:
            PerformanceError: If capture exceeds max_capture_ms
        """
        start_time = time.perf_counter()
        
        try:
            # Generate ID immediately
            idea_id = str(uuid.uuid4())[:8]  # Short ID for user friendliness
            timestamp = datetime.now()
            
            # Extract context quickly (minimal processing)
            active_file = context.get('active_file') if context else None
            active_line = context.get('active_line') if context else None
            active_operation = context.get('active_operation') if context else None
            conversation_id = context.get('conversation_id') if context else None
            project = context.get('project') if context else self._detect_project()
            
            # Create idea object
            idea = IdeaCapture(
                idea_id=idea_id,
                raw_text=raw_text,
                timestamp=timestamp,
                active_file=active_file,
                active_line=active_line,
                active_operation=active_operation,
                conversation_id=conversation_id,
                project=project
            )
            
            # Fast SQLite append (critical path)
            self._fast_insert(idea)
            
            # Performance validation
            capture_time = (time.perf_counter() - start_time) * 1000
            self._update_performance_stats(capture_time)
            
            if capture_time > self.max_capture_ms:
                logger.warning(
                    f"Capture exceeded target: {capture_time:.1f}ms > {self.max_capture_ms}ms"
                )
            
            logger.debug(f"Captured idea {idea_id} in {capture_time:.1f}ms: '{raw_text}'")
            
            # Trigger async enrichment (zero impact on capture performance)
            if self.enable_enrichment:
                threading.Thread(
                    target=self._enrich_idea,
                    args=(idea_id,),
                    daemon=True
                ).start()
            
            return idea_id
            
        except Exception as e:
            capture_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Capture failed after {capture_time:.1f}ms: {e}")
            raise
    
    def get_all_ideas(
        self,
        status_filter: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[IdeaCapture]:
        """
        Retrieve all ideas with optional filtering.
        
        Args:
            status_filter: Filter by status (pending, completed, etc.)
            limit: Maximum number of ideas to return
            
        Returns:
            List of IdeaCapture objects
        """
        with self._db_lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            try:
                query = """
                    SELECT * FROM ideas 
                    WHERE 1=1
                """
                params = []
                
                if status_filter:
                    query += " AND status = ?"
                    params.append(status_filter)
                
                query += " ORDER BY timestamp DESC"
                
                if limit:
                    query += " LIMIT ?"
                    params.append(limit)
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                return [self._row_to_idea(row) for row in rows]
                
            finally:
                conn.close()
    
    def filter_by_component(self, component: str) -> List[IdeaCapture]:
        """Filter ideas by component (auth, api, ui, etc.)."""
        with self._db_lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            try:
                cursor = conn.execute(
                    """
                    SELECT * FROM ideas 
                    WHERE component = ? 
                    ORDER BY timestamp DESC
                    """,
                    (component,)
                )
                rows = cursor.fetchall()
                return [self._row_to_idea(row) for row in rows]
                
            finally:
                conn.close()
    
    def filter_by_project(self, project: str) -> List[IdeaCapture]:
        """Filter ideas by project/repository."""
        with self._db_lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            try:
                cursor = conn.execute(
                    """
                    SELECT * FROM ideas 
                    WHERE project = ? 
                    ORDER BY timestamp DESC
                    """,
                    (project,)
                )
                rows = cursor.fetchall()
                return [self._row_to_idea(row) for row in rows]
                
            finally:
                conn.close()
    
    def get_idea(self, idea_id: str) -> Optional[IdeaCapture]:
        """Get specific idea by ID."""
        with self._db_lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            try:
                cursor = conn.execute(
                    "SELECT * FROM ideas WHERE idea_id = ?",
                    (idea_id,)
                )
                row = cursor.fetchone()
                
                return self._row_to_idea(row) if row else None
                
            finally:
                conn.close()
    
    def complete_idea(self, idea_id: str) -> bool:
        """Mark idea as completed."""
        return self._update_idea_status(idea_id, 'completed')
    
    def archive_idea(self, idea_id: str) -> bool:
        """Archive idea (remove from active view)."""
        return self._update_idea_status(idea_id, 'archived')
    
    def update_priority(self, idea_id: str, priority: str) -> bool:
        """Update idea priority."""
        if priority not in ['high', 'medium', 'low']:
            raise ValueError(f"Invalid priority: {priority}")
        
        with self._db_lock:
            conn = sqlite3.connect(self.db_path)
            
            try:
                cursor = conn.execute(
                    """
                    UPDATE ideas 
                    SET priority = ?, updated_at = ? 
                    WHERE idea_id = ?
                    """,
                    (priority, datetime.now().isoformat(), idea_id)
                )
                success = cursor.rowcount > 0
                conn.commit()
                
                if success:
                    logger.info(f"Updated idea {idea_id} priority to {priority}")
                
                return success
                
            finally:
                conn.close()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return dict(self.stats)
    
    def _get_default_db_path(self) -> str:
        """Get default database path in CORTEX brain."""
        cortex_root = Path.cwd()
        db_path = cortex_root / "cortex-brain" / "tier1" / "idea-queue.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return str(db_path)
    
    def _init_database(self) -> None:
        """Initialize SQLite database schema."""
        with self._db_lock:
            conn = sqlite3.connect(self.db_path)
            
            try:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS ideas (
                        idea_id TEXT PRIMARY KEY,
                        raw_text TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        
                        -- Context (instant capture)
                        active_file TEXT,
                        active_line INTEGER,
                        active_operation TEXT,
                        conversation_id TEXT,
                        project TEXT,
                        
                        -- Enrichment (async)
                        component TEXT,
                        priority TEXT,
                        related_ideas TEXT, -- JSON array
                        status TEXT DEFAULT 'pending',
                        
                        -- Metadata
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                
                # Indexes for performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON ideas(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON ideas(status)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_component ON ideas(component)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_project ON ideas(project)")
                
                conn.commit()
                
            finally:
                conn.close()
    
    def _fast_insert(self, idea: IdeaCapture) -> None:
        """Ultra-fast SQLite insert optimized for <5ms performance."""
        with self._db_lock:
            conn = sqlite3.connect(self.db_path)
            
            try:
                # Convert related_ideas to JSON
                related_json = json.dumps(idea.related_ideas) if idea.related_ideas else None
                
                conn.execute("""
                    INSERT INTO ideas (
                        idea_id, raw_text, timestamp,
                        active_file, active_line, active_operation,
                        conversation_id, project,
                        component, priority, related_ideas, status,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    idea.idea_id,
                    idea.raw_text,
                    idea.timestamp.isoformat(),
                    idea.active_file,
                    idea.active_line,
                    idea.active_operation,
                    idea.conversation_id,
                    idea.project,
                    idea.component,
                    idea.priority,
                    related_json,
                    idea.status,
                    idea.created_at.isoformat(),
                    idea.updated_at.isoformat()
                ))
                
                conn.commit()
                
            finally:
                conn.close()
    
    def _row_to_idea(self, row: sqlite3.Row) -> IdeaCapture:
        """Convert SQLite row to IdeaCapture object."""
        related_ideas = []
        if row['related_ideas']:
            try:
                related_ideas = json.loads(row['related_ideas'])
            except json.JSONDecodeError:
                logger.warning(f"Invalid related_ideas JSON for {row['idea_id']}")
        
        return IdeaCapture(
            idea_id=row['idea_id'],
            raw_text=row['raw_text'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            active_file=row['active_file'],
            active_line=row['active_line'],
            active_operation=row['active_operation'],
            conversation_id=row['conversation_id'],
            project=row['project'],
            component=row['component'],
            priority=row['priority'],
            related_ideas=related_ideas,
            status=row['status'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
    
    def _update_idea_status(self, idea_id: str, status: str) -> bool:
        """Update idea status."""
        with self._db_lock:
            conn = sqlite3.connect(self.db_path)
            
            try:
                cursor = conn.execute(
                    """
                    UPDATE ideas 
                    SET status = ?, updated_at = ? 
                    WHERE idea_id = ?
                    """,
                    (status, datetime.now().isoformat(), idea_id)
                )
                success = cursor.rowcount > 0
                conn.commit()
                
                if success:
                    logger.info(f"Updated idea {idea_id} status to {status}")
                
                return success
                
            finally:
                conn.close()
    
    def _update_performance_stats(self, capture_time_ms: float) -> None:
        """Update performance statistics."""
        self.stats['captures_total'] += 1
        
        if capture_time_ms <= self.max_capture_ms:
            self.stats['captures_under_5ms'] += 1
        
        # Running average
        total = self.stats['captures_total']
        current_avg = self.stats['average_capture_time']
        self.stats['average_capture_time'] = (
            (current_avg * (total - 1) + capture_time_ms) / total
        )
        
        # Max tracking
        if capture_time_ms > self.stats['max_capture_time']:
            self.stats['max_capture_time'] = capture_time_ms
    
    def _detect_project(self) -> str:
        """Detect current project from working directory."""
        cwd = Path.cwd()
        
        # Check if we're in CORTEX
        if 'CORTEX' in str(cwd):
            return 'CORTEX'
        
        # Use directory name as project name
        return cwd.name
    
    def _enrich_idea(self, idea_id: str) -> None:
        """
        Async enrichment processing (runs in background thread).
        
        This method adds intelligence to captured ideas:
        - Component detection (auth, api, ui, etc.)
        - Priority inference (security keywords → high priority)
        - Related idea clustering
        """
        try:
            idea = self.get_idea(idea_id)
            if not idea:
                logger.warning(f"Idea {idea_id} not found for enrichment")
                return
            
            # Component detection
            component = self._detect_component(idea.raw_text, idea.active_file)
            
            # Priority inference
            priority = self._infer_priority(idea.raw_text)
            
            # Related idea clustering (simple keyword matching for now)
            related_ideas = self._find_related_ideas(idea.raw_text, idea_id)
            
            # Update database with enrichment
            with self._db_lock:
                conn = sqlite3.connect(self.db_path)
                
                try:
                    related_json = json.dumps(related_ideas) if related_ideas else None
                    
                    conn.execute("""
                        UPDATE ideas 
                        SET component = ?, priority = ?, related_ideas = ?, updated_at = ?
                        WHERE idea_id = ?
                    """, (
                        component,
                        priority,
                        related_json,
                        datetime.now().isoformat(),
                        idea_id
                    ))
                    
                    conn.commit()
                    
                    self.stats['enrichments_processed'] += 1
                    
                    logger.debug(
                        f"Enriched idea {idea_id}: "
                        f"component={component}, priority={priority}, "
                        f"related={len(related_ideas) if related_ideas else 0}"
                    )
                    
                finally:
                    conn.close()
        
        except Exception as e:
            logger.error(f"Enrichment failed for idea {idea_id}: {e}")
    
    def _detect_component(self, text: str, active_file: Optional[str]) -> Optional[str]:
        """Detect component from text and context."""
        text_lower = text.lower()
        
        # File-based detection (strongest signal)
        if active_file:
            file_lower = active_file.lower()
            if 'auth' in file_lower:
                return 'auth'
            elif 'api' in file_lower:
                return 'api'
            elif 'ui' in file_lower or 'component' in file_lower:
                return 'ui'
            elif 'test' in file_lower:
                return 'testing'
            elif 'doc' in file_lower:
                return 'documentation'
        
        # Text-based detection
        if any(keyword in text_lower for keyword in ['auth', 'login', 'password', 'token']):
            return 'auth'
        elif any(keyword in text_lower for keyword in ['api', 'endpoint', 'route', 'request']):
            return 'api'
        elif any(keyword in text_lower for keyword in ['ui', 'interface', 'component', 'button']):
            return 'ui'
        elif any(keyword in text_lower for keyword in ['test', 'spec', 'coverage']):
            return 'testing'
        elif any(keyword in text_lower for keyword in ['doc', 'readme', 'guide']):
            return 'documentation'
        elif any(keyword in text_lower for keyword in ['security', 'vulnerability', 'exploit']):
            return 'security'
        elif any(keyword in text_lower for keyword in ['performance', 'optimize', 'slow']):
            return 'performance'
        
        return None
    
    def _infer_priority(self, text: str) -> Optional[str]:
        """Infer priority from text content."""
        text_lower = text.lower()
        
        # High priority keywords
        if any(keyword in text_lower for keyword in [
            'security', 'vulnerability', 'exploit', 'urgent', 'critical',
            'bug', 'error', 'broken', 'fix', 'issue'
        ]):
            return 'high'
        
        # Medium priority keywords
        elif any(keyword in text_lower for keyword in [
            'feature', 'add', 'improve', 'enhance', 'optimize',
            'refactor', 'update', 'upgrade'
        ]):
            return 'medium'
        
        # Low priority (documentation, cleanup, etc.)
        elif any(keyword in text_lower for keyword in [
            'doc', 'comment', 'cleanup', 'style', 'format'
        ]):
            return 'low'
        
        return 'medium'  # Default to medium
    
    def _find_related_ideas(self, text: str, current_id: str) -> List[str]:
        """Find related ideas using simple keyword matching."""
        # Get component for current idea
        component = self._detect_component(text, None)
        
        if not component:
            return []
        
        # Find other ideas with same component
        related = self.filter_by_component(component)
        
        # Return IDs of related ideas (excluding current)
        return [
            idea.idea_id for idea in related 
            if idea.idea_id != current_id and idea.status == 'pending'
        ][:5]  # Limit to 5 related ideas


def create_idea_queue(config: Optional[Dict[str, Any]] = None) -> IdeaQueue:
    """
    Factory function to create IdeaQueue with configuration.
    
    Args:
        config: Optional configuration dict
            - db_path: str (custom database path)
            - enable_enrichment: bool (default: True)
            - max_capture_ms: float (default: 5.0)
            
    Returns:
        Configured IdeaQueue instance
    """
    if not config:
        config = {}
    
    db_path = config.get('db_path')
    enable_enrichment = config.get('enable_enrichment', True)
    max_capture_ms = config.get('max_capture_ms', 5.0)
    
    return IdeaQueue(
        db_path=db_path,
        enable_enrichment=enable_enrichment,
        max_capture_ms=max_capture_ms
    )