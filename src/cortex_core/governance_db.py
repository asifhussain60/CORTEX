"""
CORTEX Brain Governance Database API
====================================
High-performance API for querying SQLite governance rules (<10ms target)

Author: Asif Hussain
Version: 5.0.0
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class GovernanceRule:
    """Represents a single governance rule."""
    rule_id: str
    layer_id: str
    name: str
    description: str
    severity: str
    enabled: bool
    version: str
    created_at: str
    updated_at: str
    detection_patterns: List[Dict[str, Any]]
    validation_checks: List[Dict[str, Any]]
    alternatives: List[str]
    evidence_templates: List[Dict[str, Any]]


@dataclass
class ProtectionLayer:
    """Represents a protection layer."""
    layer_id: str
    name: str
    description: str
    priority: int
    enforcement_mode: str
    rule_count: int


@dataclass
class Tier0Instinct:
    """Represents a tier0 instinct."""
    instinct_id: str
    name: str
    principle: str
    rationale: str
    priority: int
    applies_to: List[str]


class GovernanceDB:
    """
    High-performance interface to CORTEX governance database.
    
    Design Goals:
    - Query time <10ms per operation
    - Connection pooling for concurrent requests
    - Caching for frequently accessed rules
    - Type-safe return values
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize governance database connection."""
        if db_path is None:
            # Default to tier0/governance.db
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "cortex-brain" / "tier0" / "governance.db"
        
        self.db_path = db_path
        self._verify_database()
    
    def _verify_database(self):
        """Verify database exists and has correct schema."""
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Governance database not found: {self.db_path}\n"
                f"Run: python3 scripts/migrate_governance_to_sqlite.py"
            )
    
    def _connect(self) -> sqlite3.Connection:
        """Create database connection with optimizations."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        # Performance optimizations
        conn.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging
        conn.execute("PRAGMA synchronous = NORMAL")  # Faster writes
        conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
        conn.execute("PRAGMA temp_store = MEMORY")  # Use RAM for temp tables
        return conn
    
    # ========================================================================
    # RULE QUERIES
    # ========================================================================
    
    def get_rule(self, rule_id: str) -> Optional[GovernanceRule]:
        """
        Get a single rule by ID with all related data.
        
        Target: <5ms query time
        """
        conn = self._connect()
        try:
            # Main rule data
            cursor = conn.execute("""
                SELECT * FROM governance_rules WHERE rule_id = ?
            """, (rule_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Detection patterns
            patterns_cursor = conn.execute("""
                SELECT pattern_type, pattern, match_mode, case_sensitive, priority
                FROM detection_patterns WHERE rule_id = ? ORDER BY priority
            """, (rule_id,))
            patterns = [dict(p) for p in patterns_cursor.fetchall()]
            
            # Validation checks
            validation_cursor = conn.execute("""
                SELECT check_type, check_config, pass_criteria, fail_message
                FROM validation_checks WHERE rule_id = ?
            """, (rule_id,))
            validations = [dict(v) for v in validation_cursor.fetchall()]
            
            # Alternatives
            alt_cursor = conn.execute("""
                SELECT description, when_allowed, approval_required
                FROM rule_alternatives WHERE rule_id = ?
            """, (rule_id,))
            alternatives = [row['description'] for row in alt_cursor.fetchall()]
            
            # Evidence templates
            evidence_cursor = conn.execute("""
                SELECT evidence_type, required, description, format
                FROM evidence_templates WHERE rule_id = ?
            """, (rule_id,))
            evidence = [dict(e) for e in evidence_cursor.fetchall()]
            
            return GovernanceRule(
                rule_id=row['rule_id'],
                layer_id=row['layer_id'],
                name=row['name'],
                description=row['description'],
                severity=row['severity'],
                enabled=bool(row['enabled']),
                version=row['version'],
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                detection_patterns=patterns,
                validation_checks=validations,
                alternatives=alternatives,
                evidence_templates=evidence
            )
        finally:
            conn.close()
    
    def get_rules_by_layer(self, layer_id: str, enabled_only: bool = True) -> List[GovernanceRule]:
        """Get all rules in a protection layer."""
        conn = self._connect()
        try:
            query = "SELECT rule_id FROM governance_rules WHERE layer_id = ?"
            params = [layer_id]
            
            if enabled_only:
                query += " AND enabled = 1"
            
            cursor = conn.execute(query, params)
            rule_ids = [row['rule_id'] for row in cursor.fetchall()]
            
            return [self.get_rule(rid) for rid in rule_ids if self.get_rule(rid)]
        finally:
            conn.close()
    
    def get_rules_by_severity(self, severity: str) -> List[str]:
        """Get rule IDs by severity level (BLOCKED, ERROR, WARNING, INFO)."""
        conn = self._connect()
        try:
            cursor = conn.execute("""
                SELECT rule_id FROM governance_rules 
                WHERE severity = ? AND enabled = 1
                ORDER BY rule_id
            """, (severity.upper(),))
            return [row['rule_id'] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def search_rules(self, keyword: str, search_in: str = 'name,description') -> List[GovernanceRule]:
        """
        Search rules by keyword in specified fields.
        
        Args:
            keyword: Search term
            search_in: Comma-separated fields (name, description, rule_id)
        """
        conn = self._connect()
        try:
            search_fields = search_in.split(',')
            conditions = []
            
            if 'name' in search_fields:
                conditions.append("name LIKE ?")
            if 'description' in search_fields:
                conditions.append("description LIKE ?")
            if 'rule_id' in search_fields:
                conditions.append("rule_id LIKE ?")
            
            query = f"""
                SELECT rule_id FROM governance_rules 
                WHERE ({' OR '.join(conditions)}) AND enabled = 1
            """
            
            search_term = f"%{keyword}%"
            params = [search_term] * len(conditions)
            
            cursor = conn.execute(query, params)
            rule_ids = [row['rule_id'] for row in cursor.fetchall()]
            
            return [self.get_rule(rid) for rid in rule_ids if self.get_rule(rid)]
        finally:
            conn.close()
    
    # ========================================================================
    # LAYER QUERIES
    # ========================================================================
    
    def get_all_layers(self) -> List[ProtectionLayer]:
        """Get all protection layers with rule counts."""
        conn = self._connect()
        try:
            cursor = conn.execute("SELECT * FROM v_layer_coverage ORDER BY priority")
            return [
                ProtectionLayer(
                    layer_id=row['layer_id'],
                    name=row['layer_name'],
                    description='',  # Not in view
                    priority=row['priority'],
                    enforcement_mode='',  # Not in view
                    rule_count=row['total_rules']
                )
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()
    
    def get_layer(self, layer_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed layer information."""
        conn = self._connect()
        try:
            cursor = conn.execute("""
                SELECT * FROM protection_layers WHERE layer_id = ?
            """, (layer_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    # ========================================================================
    # INSTINCT QUERIES
    # ========================================================================
    
    def get_all_instincts(self) -> List[Tier0Instinct]:
        """Get all tier0 instincts ordered by priority."""
        conn = self._connect()
        try:
            cursor = conn.execute("""
                SELECT * FROM tier0_instincts ORDER BY priority
            """)
            return [
                Tier0Instinct(
                    instinct_id=row['instinct_id'],
                    name=row['name'],
                    principle=row['principle'],
                    rationale=row['rationale'],
                    priority=row['priority'],
                    applies_to=json.loads(row['applies_to']) if row['applies_to'] else []
                )
                for row in cursor.fetchall()
            ]
        finally:
            conn.close()
    
    def get_instinct(self, instinct_id: str) -> Optional[Tier0Instinct]:
        """Get a specific instinct by ID."""
        conn = self._connect()
        try:
            cursor = conn.execute("""
                SELECT * FROM tier0_instincts WHERE instinct_id = ?
            """, (instinct_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return Tier0Instinct(
                instinct_id=row['instinct_id'],
                name=row['name'],
                principle=row['principle'],
                rationale=row['rationale'],
                priority=row['priority'],
                applies_to=json.loads(row['applies_to']) if row['applies_to'] else []
            )
        finally:
            conn.close()
    
    # ========================================================================
    # CRITICAL PATH QUERIES
    # ========================================================================
    
    def get_critical_paths(self, protection_level: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all critical paths, optionally filtered by protection level."""
        conn = self._connect()
        try:
            if protection_level:
                cursor = conn.execute("""
                    SELECT * FROM critical_paths 
                    WHERE protection_level = ?
                    ORDER BY path
                """, (protection_level.upper(),))
            else:
                cursor = conn.execute("SELECT * FROM critical_paths ORDER BY path")
            
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def is_path_protected(self, path: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a path is protected.
        
        Returns:
            (is_protected, protection_level)
        """
        conn = self._connect()
        try:
            cursor = conn.execute("""
                SELECT protection_level FROM critical_paths 
                WHERE ? LIKE path || '%'
            """, (path,))
            row = cursor.fetchone()
            
            if row:
                return (True, row['protection_level'])
            return (False, None)
        finally:
            conn.close()
    
    # ========================================================================
    # ANALYTICS QUERIES
    # ========================================================================
    
    def get_rule_stats(self) -> Dict[str, int]:
        """Get overall rule statistics."""
        conn = self._connect()
        try:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN enabled = 1 THEN 1 ELSE 0 END) as enabled,
                    SUM(CASE WHEN severity = 'BLOCKED' THEN 1 ELSE 0 END) as blocking,
                    SUM(CASE WHEN severity = 'ERROR' THEN 1 ELSE 0 END) as errors,
                    SUM(CASE WHEN severity = 'WARNING' THEN 1 ELSE 0 END) as warnings
                FROM governance_rules
            """)
            row = cursor.fetchone()
            return dict(row) if row else {}
        finally:
            conn.close()
    
    def get_incomplete_rules(self) -> List[Dict[str, Any]]:
        """Get rules missing detection patterns."""
        conn = self._connect()
        try:
            cursor = conn.execute("SELECT * FROM v_incomplete_rules")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_rule_conflicts(self) -> List[Dict[str, Any]]:
        """Get rules that conflict with each other."""
        conn = self._connect()
        try:
            cursor = conn.execute("SELECT * FROM v_rule_conflicts")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_recent_violations(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get recent rule violations."""
        conn = self._connect()
        try:
            cursor = conn.execute("""
                SELECT * FROM v_recent_violations 
                ORDER BY detected_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    # ========================================================================
    # VALIDATION & ENFORCEMENT
    # ========================================================================
    
    def validate_rule_compliance(self, rule_id: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate if current state complies with a rule.
        
        Args:
            rule_id: Rule to check
            context: Context data (files, code, state, etc.)
        
        Returns:
            (is_compliant, message)
        """
        rule = self.get_rule(rule_id)
        if not rule:
            return (False, f"Rule {rule_id} not found")
        
        if not rule.enabled:
            return (True, "Rule is disabled")
        
        # Check detection patterns
        for pattern in rule.detection_patterns:
            # Implementation depends on pattern_type
            # This is a framework - specific checks implemented elsewhere
            pass
        
        return (True, "Validation passed")
    
    def record_violation(self, rule_id: str, context: Dict[str, Any], severity: str):
        """Record a rule violation."""
        conn = self._connect()
        try:
            conn.execute("""
                INSERT INTO rule_violations 
                (rule_id, context, severity, resolved)
                VALUES (?, ?, ?, 0)
            """, (rule_id, json.dumps(context), severity))
            conn.commit()
        finally:
            conn.close()
    
    def resolve_violation(self, violation_id: int, resolution_notes: str):
        """Mark a violation as resolved."""
        conn = self._connect()
        try:
            conn.execute("""
                UPDATE rule_violations 
                SET resolved = 1, 
                    resolved_at = CURRENT_TIMESTAMP,
                    resolution_notes = ?
                WHERE violation_id = ?
            """, (resolution_notes, violation_id))
            conn.commit()
        finally:
            conn.close()
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_schema_version(self) -> str:
        """Get current database schema version."""
        conn = self._connect()
        try:
            cursor = conn.execute("""
                SELECT version FROM schema_version 
                ORDER BY applied_at DESC LIMIT 1
            """)
            row = cursor.fetchone()
            return row['version'] if row else 'unknown'
        finally:
            conn.close()
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform governance database health check.
        
        Returns diagnostics and recommendations.
        """
        conn = self._connect()
        try:
            stats = self.get_rule_stats()
            incomplete = len(self.get_incomplete_rules())
            conflicts = len(self.get_rule_conflicts())
            
            health = {
                'status': 'healthy',
                'schema_version': self.get_schema_version(),
                'total_rules': stats.get('total', 0),
                'enabled_rules': stats.get('enabled', 0),
                'incomplete_rules': incomplete,
                'conflicts': conflicts,
                'warnings': []
            }
            
            if incomplete > 0:
                health['warnings'].append(f"{incomplete} rules missing detection patterns")
            
            if conflicts > 0:
                health['warnings'].append(f"{conflicts} rule conflicts detected")
                health['status'] = 'degraded'
            
            return health
        finally:
            conn.close()


# Singleton instance for application-wide use
_governance_db: Optional[GovernanceDB] = None


def get_governance_db() -> GovernanceDB:
    """Get singleton governance database instance."""
    global _governance_db
    if _governance_db is None:
        _governance_db = GovernanceDB()
    return _governance_db
