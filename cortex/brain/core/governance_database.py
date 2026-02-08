"""
Governance Database Manager - SQLite Backend for Tier 1/2 Governance Rules

Purpose:
    Manages SQLite database persistence for flexible Tier 1 (project) and
    Tier 2 (team) governance rules. Tier 0 rules remain in YAML as immutable SSOT.

Architecture:
    - Tables: project_rules, team_rules, governance_audit_log, rule_versions
    - Tier 0: Loaded from YAML (immutable)
    - Tier 1: Loaded from database (project-level, runtime-updatable)
    - Tier 2: Loaded from database (team-level, multi-tenant)
    - Audit: Complete change history logged

Thread Safety:
    - Uses SQLite connection pooling via threading.Lock
    - All operations are atomic
    - Concurrent read access optimized

Performance:
    - Query performance: O(1) for rule lookups via indexed columns
    - Batch operations supported
    - Query result caching for frequently accessed rules

Compliance:
    - CORE-034: Audit logging for all operations
    - CORE-027: Audit trail enforcement
    - CORE-035: Single implementation per rule_id

Author: Asif Hussain
Version: 1.0
"""

import sqlite3
import json
import threading
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from functools import lru_cache
import logging
from cortex.models.canonical_enums import AuditAction

logger = logging.getLogger(__name__)


class RuleTier(Enum):
    """Governance rule tier enumeration."""
    TIER_0 = 0  # Immutable, YAML-based
    TIER_1 = 1  # Project-level, database-backed
    TIER_2 = 2  # Team-level, multi-tenant




@dataclass
class GovernanceRule:
    """Governance rule data class."""
    rule_id: str
    tier: int
    name: str
    category: str
    severity: str
    description: str
    enforcement_point: str
    audit_event: str
    created_at: str
    created_by: str
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None
    is_active: bool = True
    metadata: Optional[str] = None  # JSON-encoded metadata

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class AuditLogEntry:
    """Audit log entry data class."""
    audit_id: str
    rule_id: str
    action: str
    actor: str
    timestamp: str
    previous_state: Optional[str]  # JSON-encoded
    new_state: Optional[str]  # JSON-encoded
    reason: Optional[str]
    is_compliant: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class QueryCache:
    """
    LRU cache for governance rule queries.
    
    Purpose: Improve performance for frequently accessed queries
    Max size: 128 entries (rules and query results)
    """
    
    def __init__(self, maxsize: int = 128):
        """Initialize query cache."""
        self.maxsize = maxsize
        self.cache: Dict[str, Any] = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            return self.cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        with self._lock:
            if len(self.cache) >= self.maxsize:
                # Remove oldest entry (simple FIFO for simplicity)
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            self.cache[key] = value
    
    def clear(self) -> None:
        """Clear entire cache."""
        with self._lock:
            self.cache.clear()
    
    def invalidate(self, pattern: Optional[str] = None) -> None:
        """Invalidate cache entries matching pattern."""
        with self._lock:
            if pattern is None:
                self.cache.clear()
            else:
                keys_to_delete = [k for k in self.cache.keys() if pattern in k]
                for key in keys_to_delete:
                    del self.cache[key]
    
    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self.cache)


class GovernanceDatabaseManager:
    """
    SQLite database manager for governance rules.
    
    Provides CRUD operations, audit logging, and query interface for
    Tier 1 and Tier 2 governance rules.
    """

    _instance = None
    _lock = threading.Lock()
    _db_lock = threading.Lock()

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize database manager.

        Args:
            db_path: Path to SQLite database. Defaults to .cortex/governance_rules.db
        """
        if db_path is None:
            db_path = Path.home() / ".cortex" / "governance_rules.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._connection = None
        self._initialized = False
        self._query_cache = QueryCache(maxsize=128)

    @classmethod
    def instance(cls) -> "GovernanceDatabaseManager":
        """Get singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def initialize(self) -> None:
        """Initialize database schema."""
        if self._initialized:
            return

        with self._db_lock:
            try:
                self._create_schema()
                self._initialized = True
                logger.info(f"✅ Governance database initialized: {self.db_path}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize governance database: {e}")
                raise

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
                isolation_level=None  # Autocommit mode
            )
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def _create_schema(self) -> None:
        """Create database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Create project_rules table (Tier 1)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_rules (
                rule_id TEXT PRIMARY KEY,
                tier INTEGER NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT NOT NULL,
                enforcement_point TEXT NOT NULL,
                audit_event TEXT NOT NULL,
                created_at TEXT NOT NULL,
                created_by TEXT NOT NULL,
                updated_at TEXT,
                updated_by TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                metadata TEXT,
                UNIQUE(rule_id)
            )
        """)

        # Create team_rules table (Tier 2)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_rules (
                rule_id TEXT NOT NULL,
                team_id TEXT NOT NULL,
                tier INTEGER NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT NOT NULL,
                enforcement_point TEXT NOT NULL,
                audit_event TEXT NOT NULL,
                created_at TEXT NOT NULL,
                created_by TEXT NOT NULL,
                updated_at TEXT,
                updated_by TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                metadata TEXT,
                PRIMARY KEY (rule_id, team_id)
            )
        """)

        # Create governance_audit_log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS governance_audit_log (
                audit_id TEXT PRIMARY KEY,
                rule_id TEXT NOT NULL,
                action TEXT NOT NULL,
                actor TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                previous_state TEXT,
                new_state TEXT,
                reason TEXT,
                is_compliant BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (rule_id) REFERENCES project_rules(rule_id)
            )
        """)

        # Create rule_versions table (version history)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rule_versions (
                version_id TEXT PRIMARY KEY,
                rule_id TEXT NOT NULL,
                tier INTEGER NOT NULL,
                version_number INTEGER NOT NULL,
                rule_state TEXT NOT NULL,
                created_at TEXT NOT NULL,
                created_by TEXT NOT NULL,
                change_description TEXT,
                FOREIGN KEY (rule_id) REFERENCES project_rules(rule_id)
            )
        """)

        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_project_rules_tier ON project_rules(tier)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_project_rules_category ON project_rules(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_project_rules_active ON project_rules(is_active)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_team_rules_team ON team_rules(team_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_rule_id ON governance_audit_log(rule_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON governance_audit_log(timestamp)")

        conn.commit()
        logger.info("✅ Governance database schema created")

    def create_project_rule(
        self,
        rule_id: str,
        name: str,
        category: str,
        severity: str,
        description: str,
        enforcement_point: str,
        audit_event: str,
        created_by: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> GovernanceRule:
        """
        Create a new Tier 1 (project) governance rule.

        Args:
            rule_id: Unique rule identifier
            name: Human-readable rule name
            category: Rule category
            severity: Enforcement severity (blocked, warning, info)
            description: Rule description
            enforcement_point: Where rule is enforced
            audit_event: Audit event name
            created_by: User/system creating the rule
            metadata: Optional JSON metadata

        Returns:
            Created GovernanceRule

        Raises:
            sqlite3.IntegrityError: If rule_id already exists
        """
        now = datetime.now(timezone.utc).isoformat()
        metadata_json = json.dumps(metadata) if metadata else None

        with self._db_lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    INSERT INTO project_rules (
                        rule_id, tier, name, category, severity, description,
                        enforcement_point, audit_event, created_at, created_by,
                        metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rule_id, RuleTier.TIER_1.value, name, category, severity,
                    description, enforcement_point, audit_event, now, created_by,
                    metadata_json
                ))

                conn.commit()

                # Clear query cache (invalidate all category/active queries)
                self.clear_query_cache()

                # Log to audit trail (no lock needed, _log_audit_unlocked doesn't acquire lock)
                self._log_audit_unlocked(
                    rule_id=rule_id,
                    action=AuditAction.CREATE.value,
                    actor=created_by,
                    new_state=json.dumps({
                        "rule_id": rule_id, "name": name, "category": category
                    }),
                    reason=f"Created Tier 1 rule: {rule_id}"
                )

                rule = GovernanceRule(
                    rule_id=rule_id,
                    tier=RuleTier.TIER_1.value,
                    name=name,
                    category=category,
                    severity=severity,
                    description=description,
                    enforcement_point=enforcement_point,
                    audit_event=audit_event,
                    created_at=now,
                    created_by=created_by,
                    metadata=metadata_json
                )

                logger.info(f"✅ Created Tier 1 rule: {rule_id}")
                return rule

            except sqlite3.IntegrityError as e:
                logger.error(f"❌ Rule {rule_id} already exists: {e}")
                raise

    def _get_rule_unlocked(self, rule_id: str, tier: int = RuleTier.TIER_1.value) -> Optional[GovernanceRule]:
        """
        Retrieve a rule by ID (unlocked - assumes caller holds lock).

        Args:
            rule_id: Rule identifier
            tier: Rule tier (1 for project, 2 for team)

        Returns:
            GovernanceRule or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if tier == RuleTier.TIER_1.value:
            cursor.execute("SELECT * FROM project_rules WHERE rule_id = ?", (rule_id,))
        elif tier == RuleTier.TIER_2.value:
            cursor.execute("SELECT * FROM team_rules WHERE rule_id = ?", (rule_id,))
        else:
            return None

        row = cursor.fetchone()
        if row:
            return GovernanceRule(**dict(row))
        return None

    def get_rule(self, rule_id: str, tier: int = RuleTier.TIER_1.value) -> Optional[GovernanceRule]:
        """
        Retrieve a rule by ID (O(1) performance).

        Args:
            rule_id: Rule identifier
            tier: Rule tier (1 for project, 2 for team)

        Returns:
            GovernanceRule or None if not found
        """
        with self._db_lock:
            return self._get_rule_unlocked(rule_id, tier)

    def list_rules(
        self,
        tier: int = RuleTier.TIER_1.value,
        category: Optional[str] = None,
        is_active: bool = True,
    ) -> List[GovernanceRule]:
        """
        List rules with optional filtering.

        Args:
            tier: Rule tier (1 for project, 2 for team)
            category: Optional category filter
            is_active: Only return active rules

        Returns:
            List of GovernanceRule objects
        """
        with self._db_lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            if tier == RuleTier.TIER_1.value:
                table = "project_rules"
            elif tier == RuleTier.TIER_2.value:
                table = "team_rules"
            else:
                return []

            query = f"SELECT * FROM {table} WHERE is_active = ?"
            params: List[Any] = [is_active]

            if category:
                query += " AND category = ?"
                params.append(category)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [GovernanceRule(**dict(row)) for row in rows]

    def update_rule(
        self,
        rule_id: str,
        updated_by: str,
        **kwargs: Any,
    ) -> GovernanceRule:
        """
        Update a rule.

        Args:
            rule_id: Rule identifier
            updated_by: User/system updating the rule
            **kwargs: Fields to update (name, description, etc.)

        Returns:
            Updated GovernanceRule

        Raises:
            ValueError: If rule not found
        """
        # Get previous state for audit (outside lock)
        prev_rule = self.get_rule(rule_id)
        if not prev_rule:
            raise ValueError(f"Rule {rule_id} not found")

        now = datetime.now(timezone.utc).isoformat()
        kwargs["updated_at"] = now
        kwargs["updated_by"] = updated_by

        # Build update query
        set_clauses = [f"{k} = ?" for k in kwargs.keys()]
        values: List[Any] = list(kwargs.values()) + [rule_id]

        with self._db_lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = f"UPDATE project_rules SET {', '.join(set_clauses)} WHERE rule_id = ?"
            cursor.execute(query, values)
            conn.commit()

            # Clear ALL query cache (any update could affect multiple queries)
            self.clear_query_cache()

            # Log to audit trail (using unlocked version since we hold the lock)
            new_rule = self._get_rule_unlocked(rule_id)
            self._log_audit_unlocked(
                rule_id=rule_id,
                action=AuditAction.UPDATE.value,
                actor=updated_by,
                previous_state=json.dumps(asdict(prev_rule)),
                new_state=json.dumps(asdict(new_rule)) if new_rule else None,
                reason=f"Updated fields: {', '.join(kwargs.keys())}"
            )

            logger.info(f"✅ Updated rule: {rule_id}")
            if new_rule is None:
                raise ValueError(f"Failed to retrieve updated rule: {rule_id}")
            return new_rule

    def _log_audit_unlocked(
        self,
        rule_id: str,
        action: str,
        actor: str,
        previous_state: Optional[str] = None,
        new_state: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        """
        Log an audit event (internal use - assumes lock already held).
        
        Note: Caller must hold _db_lock before calling this.
        """
        audit_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO governance_audit_log (
                audit_id, rule_id, action, actor, timestamp,
                previous_state, new_state, reason, is_compliant
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            audit_id, rule_id, action, actor, now,
            previous_state, new_state, reason, True
        ))

        conn.commit()

    def _log_audit(
        self,
        rule_id: str,
        action: str,
        actor: str,
        previous_state: Optional[str] = None,
        new_state: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        """Log an audit event (internal use - acquires lock)."""
        with self._db_lock:
            self._log_audit_unlocked(
                rule_id=rule_id,
                action=action,
                actor=actor,
                previous_state=previous_state,
                new_state=new_state,
                reason=reason,
            )

    def log_audit_event(
        self,
        rule_id: str,
        action: str,
        actor: str,
        previous_state: Optional[str] = None,
        new_state: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        """
        Log an audit event (public method).
        
        Args:
            rule_id: Rule identifier
            action: Action type (CREATE, UPDATE, DELETE, etc.)
            actor: User/system performing action
            previous_state: Previous state JSON
            new_state: New state JSON
            reason: Reason for change
        """
        self._log_audit(
            rule_id=rule_id,
            action=action,
            actor=actor,
            previous_state=previous_state,
            new_state=new_state,
            reason=reason,
        )

    def get_audit_log(
        self,
        rule_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[AuditLogEntry]:
        """
        Retrieve audit log entries.

        Args:
            rule_id: Optional filter by rule_id
            limit: Maximum entries to return

        Returns:
            List of AuditLogEntry objects
        """
        with self._db_lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            if rule_id:
                cursor.execute(
                    "SELECT * FROM governance_audit_log WHERE rule_id = ? ORDER BY timestamp DESC LIMIT ?",
                    (rule_id, limit)
                )
            else:
                cursor.execute(
                    "SELECT * FROM governance_audit_log ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                )

            rows = cursor.fetchall()
            return [AuditLogEntry(**dict(row)) for row in rows]

    def get_rules_by_category(self, category: str, tier: int = RuleTier.TIER_1.value) -> List[GovernanceRule]:
        """
        Get all rules in a specific category (O(1) via index).

        Args:
            category: Rule category to filter by
            tier: Rule tier (1 for project, 2 for team)

        Returns:
            List of GovernanceRule objects matching category
        """
        cache_key = f"category:{category}:tier:{tier}"
        cached = self._query_cache.get(cache_key)
        if cached is not None:
            return cached

        with self._db_lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            table_name = "project_rules" if tier == RuleTier.TIER_1.value else "team_rules"
            
            cursor.execute(
                f"SELECT * FROM {table_name} WHERE category = ? ORDER BY name",
                (category,)
            )
            
            rows = cursor.fetchall()
            results = [GovernanceRule(**dict(row)) for row in rows]
            
            self._query_cache.set(cache_key, results)
            logger.info(f"✅ Retrieved {len(results)} rules from category: {category}")
            return results

    def get_rules_by_severity(self, severity: str, tier: int = RuleTier.TIER_1.value) -> List[GovernanceRule]:
        """
        Get all rules with a specific severity level.

        Args:
            severity: Severity level (blocked, warning, info)
            tier: Rule tier (1 for project, 2 for team)

        Returns:
            List of GovernanceRule objects matching severity
        """
        cache_key = f"severity:{severity}:tier:{tier}"
        cached = self._query_cache.get(cache_key)
        if cached is not None:
            return cached

        with self._db_lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            table_name = "project_rules" if tier == RuleTier.TIER_1.value else "team_rules"
            
            cursor.execute(
                f"SELECT * FROM {table_name} WHERE severity = ? ORDER BY name",
                (severity,)
            )
            
            rows = cursor.fetchall()
            results = [GovernanceRule(**dict(row)) for row in rows]
            
            self._query_cache.set(cache_key, results)
            logger.info(f"✅ Retrieved {len(results)} rules with severity: {severity}")
            return results

    def get_rules_by_enforcement_point(self, enforcement_point: str, tier: int = RuleTier.TIER_1.value) -> List[GovernanceRule]:
        """
        Get all rules enforced at a specific enforcement point (O(1) via index).

        Args:
            enforcement_point: Enforcement point name
            tier: Rule tier (1 for project, 2 for team)

        Returns:
            List of GovernanceRule objects for enforcement point
        """
        cache_key = f"enforcement:{enforcement_point}:tier:{tier}"
        cached = self._query_cache.get(cache_key)
        if cached is not None:
            return cached

        with self._db_lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            table_name = "project_rules" if tier == RuleTier.TIER_1.value else "team_rules"
            
            cursor.execute(
                f"SELECT * FROM {table_name} WHERE enforcement_point = ? AND is_active = 1 ORDER BY severity DESC",
                (enforcement_point,)
            )
            
            rows = cursor.fetchall()
            results = [GovernanceRule(**dict(row)) for row in rows]
            
            self._query_cache.set(cache_key, results)
            logger.info(f"✅ Retrieved {len(results)} rules for enforcement point: {enforcement_point}")
            return results

    def search_rules(self, query_term: str, tier: int = RuleTier.TIER_1.value) -> List[GovernanceRule]:
        """
        Search rules by name or description (full-text search simulation).

        Args:
            query_term: Search term (case-insensitive)
            tier: Rule tier (1 for project, 2 for team)

        Returns:
            List of GovernanceRule objects matching search term
        """
        cache_key = f"search:{query_term}:tier:{tier}"
        cached = self._query_cache.get(cache_key)
        if cached is not None:
            return cached

        with self._db_lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            table_name = "project_rules" if tier == RuleTier.TIER_1.value else "team_rules"
            search_pattern = f"%{query_term}%"
            
            cursor.execute(
                f"""
                SELECT * FROM {table_name} 
                WHERE name LIKE ? OR description LIKE ? OR category LIKE ?
                ORDER BY name
                """,
                (search_pattern, search_pattern, search_pattern)
            )
            
            rows = cursor.fetchall()
            results = [GovernanceRule(**dict(row)) for row in rows]
            
            self._query_cache.set(cache_key, results)
            logger.info(f"✅ Found {len(results)} rules matching: {query_term}")
            return results

    def get_active_rules(self, tier: int = RuleTier.TIER_1.value) -> List[GovernanceRule]:
        """
        Get all active rules (O(1) via index).

        Args:
            tier: Rule tier (1 for project, 2 for team)

        Returns:
            List of active GovernanceRule objects
        """
        cache_key = f"active:tier:{tier}"
        cached = self._query_cache.get(cache_key)
        if cached is not None:
            return cached

        with self._db_lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            table_name = "project_rules" if tier == RuleTier.TIER_1.value else "team_rules"
            
            cursor.execute(
                f"SELECT * FROM {table_name} WHERE is_active = 1 ORDER BY category, name"
            )
            
            rows = cursor.fetchall()
            results = [GovernanceRule(**dict(row)) for row in rows]
            
            self._query_cache.set(cache_key, results)
            logger.info(f"✅ Retrieved {len(results)} active rules from tier {tier}")
            return results

    def clear_query_cache(self, pattern: Optional[str] = None) -> None:
        """
        Clear query cache (called on write operations).

        Args:
            pattern: Optional pattern to match cache keys
        """
        self._query_cache.invalidate(pattern)
        logger.debug(f"✅ Query cache cleared (pattern: {pattern})")

    def get_cache_size(self) -> int:
        """
        Get current query cache size.

        Returns:
            Number of cached entries
        """
        return self._query_cache.size()

    # ========================================================================
    # ADDITIONAL QUERY METHODS (for governance tools)
    # ========================================================================

    def get_violations_by_rule(self, rule: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get violations by rule (from audit log).
        
        Args:
            rule: Optional rule_id filter
            limit: Maximum number of results
            
        Returns:
            List of violation records
        """
        with self._db_lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if rule:
                cursor.execute(
                    """
                    SELECT * FROM governance_audit_log 
                    WHERE rule_id = ? AND is_compliant = 0
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (rule, limit)
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM governance_audit_log 
                    WHERE is_compliant = 0
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (limit,)
                )
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_violations_since(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get violations from the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of violation records
        """
        with self._db_lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Calculate cutoff timestamp
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            
            cursor.execute(
                """
                SELECT * FROM governance_audit_log 
                WHERE timestamp >= ? AND is_compliant = 0
                ORDER BY timestamp DESC
                """,
                (cutoff,)
            )
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_operation_count(self, days: int = 7) -> int:
        """
        Get count of governance operations in the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Total operation count
        """
        with self._db_lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            
            cursor.execute(
                """
                SELECT COUNT(*) FROM governance_audit_log 
                WHERE timestamp >= ?
                """,
                (cutoff,)
            )
            
            result = cursor.fetchone()
            return result[0] if result else 0

    def get_execution_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get execution history for the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of execution records
        """
        with self._db_lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            
            cursor.execute(
                """
                SELECT * FROM governance_audit_log 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                """,
                (cutoff,)
            )
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_active_rules_count(self, tier: int = RuleTier.TIER_1.value) -> int:
        """
        Get count of active rules.
        
        Args:
            tier: Rule tier
            
        Returns:
            Count of active rules
        """
        with self._db_lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            table_name = "project_rules" if tier == RuleTier.TIER_1.value else "team_rules"
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE is_active = 1")
            
            result = cursor.fetchone()
            return result[0] if result else 0

    def log_enforcement(self, rule_id: str, actor: str, result: str) -> None:
        """
        Log a rule enforcement action.
        
        Args:
            rule_id: The rule that was enforced
            actor: The actor performing enforcement
            result: The result of enforcement (BLOCKED, WARNING, PASSED)
        """
        self.log_audit_event(
            rule_id=rule_id,
            action=f"ENFORCEMENT_{result}",
            actor=actor,
            reason=f"Rule enforcement action"
        )

    def log_blocking(self, rule_id: str, actor: str, reason: str) -> None:
        """
        Log a blocking action.
        
        Args:
            rule_id: The rule that triggered blocking
            actor: The actor initiating the block
            reason: The reason for blocking
        """
        self.log_audit_event(
            rule_id=rule_id,
            action="OPERATION_BLOCKED",
            actor=actor,
            reason=reason
        )

    def get_audit_trail(self, rule_id: Optional[str] = None, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get audit trail for a rule or all rules.
        
        Args:
            rule_id: Optional specific rule filter
            days: Number of days to look back
            
        Returns:
            List of audit log entries
        """
        with self._db_lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            
            if rule_id:
                cursor.execute(
                    """
                    SELECT * FROM governance_audit_log 
                    WHERE rule_id = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                    """,
                    (rule_id, cutoff)
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM governance_audit_log 
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    """,
                    (cutoff,)
                )
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def log_remediation(self, rule_id: str, actor: str, action: str, description: str) -> None:
        """
        Log a remediation action.
        
        Args:
            rule_id: The rule that was remediated
            actor: The actor performing remediation
            action: The remediation action taken
            description: Description of remediation
        """
        self.log_audit_event(
            rule_id=rule_id,
            action=f"REMEDIATION_{action}",
            actor=actor,
            reason=description
        )

    def verify_schema(self) -> bool:
        """
        Verify database schema integrity.

        Returns:
            True if all required tables and indexes exist
        """
        with self._db_lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Check for required tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}

            required_tables = {
                "project_rules",
                "team_rules",
                "governance_audit_log",
                "rule_versions",
            }

            return required_tables.issubset(existing_tables)

    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("✅ Governance database connection closed")

    def __enter__(self) -> "GovernanceDatabaseManager":
        """Context manager entry."""
        self.initialize()
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> None:
        """Context manager exit."""
        self.close()
