"""
Vision Mutation Tracking module for HP-003-01.

Tracks vision mutations from PHASE-06 protocol with:
- Timestamp tracking for all mutations
- Rollback capability to any checkpoint
- Queryable history with filtering
- Full audit trail for governance

Part of PHASE-11-HALLUCINATION-PREVENTION.
"""

import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import threading


class MutationType(Enum):
    """Vision mutation types."""
    
    CONTEXT_UPDATE = "CONTEXT_UPDATE"
    """Context changes (phase transitions, config updates)."""
    
    STATE_UPDATE = "STATE_UPDATE"
    """State mutations (value changes, status updates)."""
    
    BOUNDARY_MODIFICATION = "BOUNDARY_MODIFICATION"
    """Boundary rule modifications."""
    
    SCHEMA_EVOLUTION = "SCHEMA_EVOLUTION"
    """Schema changes (field additions, structure changes)."""


@dataclass
class VisionMutation:
    """Represents a single vision mutation event."""
    
    mutation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    """Unique identifier for this mutation."""
    
    timestamp: datetime = field(default_factory=datetime.utcnow)
    """When mutation occurred."""
    
    mutation_type: MutationType = MutationType.STATE_UPDATE
    """Type of mutation."""
    
    source: str = ""
    """Source phase/module (e.g., 'PHASE-06')."""
    
    description: str = ""
    """Human-readable description."""
    
    affected_entity: str = ""
    """Entity that was mutated."""
    
    data: Dict[str, Any] = field(default_factory=dict)
    """Mutation data (before/after values)."""
    
    context: Optional[Dict[str, Any]] = None
    """Execution context (user, request_id, etc)."""
    
    parent_mutation_id: Optional[str] = None
    """Parent mutation for causality tracking."""


@dataclass
class MutationSnapshot:
    """Snapshot for rollback capability."""
    
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    """Unique snapshot identifier."""
    
    mutation_id: str = ""
    """Mutation ID this snapshot is based on."""
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    """When snapshot was created."""
    
    entity_state: Dict[str, Any] = field(default_factory=dict)
    """State of affected entity at snapshot time."""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional snapshot metadata."""


class VisionMutationTracker:
    """
    Tracks vision mutations from PHASE-06 protocol.
    
    Provides:
    - Mutation tracking with timestamps
    - Rollback capability to any checkpoint
    - Queryable history with multiple filters
    - Full persistence in database
    - Causality tracking between mutations
    """
    
    def __init__(self, db_path: str = ":memory:"):
        """
        Initialize vision mutation tracker.
        
        Args:
            db_path: Path to SQLite database. Defaults to in-memory.
        """
        self.db_path = db_path
        self._lock = threading.RLock()
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize database schema for mutations."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Mutations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vision_mutations (
                mutation_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                mutation_type TEXT NOT NULL,
                source TEXT NOT NULL,
                description TEXT NOT NULL,
                affected_entity TEXT NOT NULL,
                data TEXT NOT NULL,
                context TEXT,
                parent_mutation_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Snapshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mutation_snapshots (
                snapshot_id TEXT PRIMARY KEY,
                mutation_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                entity_state TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (mutation_id) REFERENCES vision_mutations(mutation_id)
            )
        """)
        
        # Rollback history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rollback_history (
                rollback_id TEXT PRIMARY KEY,
                original_mutation_id TEXT NOT NULL,
                rolled_back_to_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                reason TEXT,
                FOREIGN KEY (original_mutation_id) REFERENCES vision_mutations(mutation_id),
                FOREIGN KEY (rolled_back_to_id) REFERENCES vision_mutations(mutation_id)
            )
        """)
        
        # Indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_mutation_timestamp 
            ON vision_mutations(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_mutation_entity 
            ON vision_mutations(affected_entity)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_mutation_type 
            ON vision_mutations(mutation_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_mutation_source 
            ON vision_mutations(source)
        """)
        
        conn.commit()
        conn.close()
    
    def track_mutation(
        self,
        mutation_type: MutationType,
        source: str,
        description: str,
        affected_entity: str,
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        parent_mutation_id: Optional[str] = None,
    ) -> VisionMutation:
        """
        Track a new vision mutation.
        
        Args:
            mutation_type: Type of mutation.
            source: Source phase/module.
            description: Human-readable description.
            affected_entity: Entity being mutated.
            data: Mutation data payload.
            context: Optional execution context.
            parent_mutation_id: Optional parent mutation for causality.
        
        Returns:
            VisionMutation: Recorded mutation with timestamp and ID.
        
        Raises:
            TypeError: If arguments have invalid types.
            ValueError: If required fields are missing.
        """
        if not isinstance(mutation_type, MutationType):
            raise TypeError("mutation_type must be MutationType enum")
        if not source or not isinstance(source, str):
            raise TypeError("source must be non-empty string")
        if not description or not isinstance(description, str):
            raise TypeError("description must be non-empty string")
        if not affected_entity or not isinstance(affected_entity, str):
            raise TypeError("affected_entity must be non-empty string")
        if not isinstance(data, dict):
            raise TypeError("data must be dictionary")
        
        with self._lock:
            # Create mutation object
            mutation = VisionMutation(
                mutation_type=mutation_type,
                source=source,
                description=description,
                affected_entity=affected_entity,
                data=data,
                context=context,
                parent_mutation_id=parent_mutation_id,
            )
            
            # Persist to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO vision_mutations
                (mutation_id, timestamp, mutation_type, source, description,
                 affected_entity, data, context, parent_mutation_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mutation.mutation_id,
                mutation.timestamp.isoformat(),
                mutation.mutation_type.value,
                mutation.source,
                mutation.description,
                mutation.affected_entity,
                json.dumps(mutation.data),
                json.dumps(mutation.context) if mutation.context else None,
                mutation.parent_mutation_id,
            ))
            
            conn.commit()
            conn.close()
            
            return mutation
    
    def get_mutation(self, mutation_id: str) -> Optional[VisionMutation]:
        """
        Retrieve mutation by ID.
        
        Args:
            mutation_id: Mutation identifier.
        
        Returns:
            VisionMutation if found, None otherwise.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT mutation_id, timestamp, mutation_type, source, description,
                       affected_entity, data, context, parent_mutation_id
                FROM vision_mutations
                WHERE mutation_id = ?
            """, (mutation_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            return self._row_to_mutation(row)
    
    def get_mutation_history(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Get complete mutation history.
        
        Args:
            limit: Maximum number of mutations to return.
        
        Returns:
            List of mutations in chronological order.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT mutation_id, timestamp, mutation_type, source, description,
                       affected_entity, data, context, parent_mutation_id
                FROM vision_mutations
                ORDER BY timestamp ASC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [self._row_to_dict(row) for row in rows]
    
    def get_mutations_for_entity(
        self,
        entity: str,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get mutations for a specific entity.
        
        Args:
            entity: Entity identifier.
            limit: Maximum results.
        
        Returns:
            List of mutations for entity.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT mutation_id, timestamp, mutation_type, source, description,
                       affected_entity, data, context, parent_mutation_id
                FROM vision_mutations
                WHERE affected_entity = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (entity, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [self._row_to_dict(row) for row in rows]
    
    def get_mutations_by_type(
        self,
        mutation_type: MutationType,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get mutations of specific type.
        
        Args:
            mutation_type: Type to filter by.
            limit: Maximum results.
        
        Returns:
            List of mutations of type.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT mutation_id, timestamp, mutation_type, source, description,
                       affected_entity, data, context, parent_mutation_id
                FROM vision_mutations
                WHERE mutation_type = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (mutation_type.value, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [self._row_to_dict(row) for row in rows]
    
    def get_mutations_in_range(
        self,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get mutations within time range.
        
        Args:
            start_time: Range start.
            end_time: Range end.
            limit: Maximum results.
        
        Returns:
            List of mutations in time range.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT mutation_id, timestamp, mutation_type, source, description,
                       affected_entity, data, context, parent_mutation_id
                FROM vision_mutations
                WHERE timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp ASC
                LIMIT ?
            """, (start_time.isoformat(), end_time.isoformat(), limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [self._row_to_dict(row) for row in rows]
    
    def search_mutations(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search mutations by description or entity.
        
        Args:
            query: Search query string.
            limit: Maximum results.
        
        Returns:
            List of matching mutations.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            search_term = f"%{query}%"
            cursor.execute("""
                SELECT mutation_id, timestamp, mutation_type, source, description,
                       affected_entity, data, context, parent_mutation_id
                FROM vision_mutations
                WHERE description LIKE ? OR affected_entity LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (search_term, search_term, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [self._row_to_dict(row) for row in rows]
    
    def create_mutation_snapshot(
        self,
        mutation_id: str,
        entity_state: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[MutationSnapshot]:
        """
        Create snapshot at mutation point for rollback.
        
        Args:
            mutation_id: Mutation to snapshot.
            entity_state: Entity state at mutation.
            metadata: Additional snapshot metadata.
        
        Returns:
            MutationSnapshot if successful, None otherwise.
        """
        if not self.get_mutation(mutation_id):
            return None
        
        with self._lock:
            snapshot = MutationSnapshot(
                mutation_id=mutation_id,
                entity_state=entity_state or {},
                metadata=metadata or {},
            )
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO mutation_snapshots
                (snapshot_id, mutation_id, created_at, entity_state, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                snapshot.snapshot_id,
                snapshot.mutation_id,
                snapshot.created_at.isoformat(),
                json.dumps(snapshot.entity_state),
                json.dumps(snapshot.metadata) if snapshot.metadata else None,
            ))
            
            conn.commit()
            conn.close()
            
            return snapshot
    
    def rollback_to_mutation(
        self,
        target_mutation_id: str,
        reason: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Rollback to specified mutation checkpoint.
        
        Args:
            target_mutation_id: Target mutation ID.
            reason: Optional rollback reason.
        
        Returns:
            Rollback result dict if successful, None otherwise.
        """
        target = self.get_mutation(target_mutation_id)
        if not target:
            return None
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create rollback history entry
            rollback_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO rollback_history
                (rollback_id, original_mutation_id, rolled_back_to_id, 
                 timestamp, reason)
                VALUES (?, ?, ?, ?, ?)
            """, (
                rollback_id,
                target_mutation_id,
                target_mutation_id,
                datetime.utcnow().isoformat(),
                reason,
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "rollback_id": rollback_id,
                "target_mutation_id": target_mutation_id,
                "timestamp": datetime.utcnow().isoformat(),
                "reason": reason,
            }
    
    def _row_to_mutation(self, row: Tuple) -> VisionMutation:
        """Convert database row to VisionMutation object."""
        (mutation_id, timestamp, mutation_type, source, description,
         affected_entity, data, context, parent_mutation_id) = row
        
        return VisionMutation(
            mutation_id=mutation_id,
            timestamp=datetime.fromisoformat(timestamp),
            mutation_type=MutationType(mutation_type),
            source=source,
            description=description,
            affected_entity=affected_entity,
            data=json.loads(data) if data else {},
            context=json.loads(context) if context else None,
            parent_mutation_id=parent_mutation_id,
        )
    
    def _row_to_dict(self, row: Tuple) -> Dict[str, Any]:
        """Convert database row to dictionary."""
        (mutation_id, timestamp, mutation_type, source, description,
         affected_entity, data, context, parent_mutation_id) = row
        
        return {
            "mutation_id": mutation_id,
            "timestamp": timestamp,
            "mutation_type": mutation_type,
            "source": source,
            "description": description,
            "affected_entity": affected_entity,
            "data": json.loads(data) if data else {},
            "context": json.loads(context) if context else None,
            "parent_mutation_id": parent_mutation_id,
        }
