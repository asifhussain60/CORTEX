"""
CORTEX Tier 0: Governance Engine

Manages immutable governance rules that guide all CORTEX operations.
This is the foundational tier - all other tiers must comply with these rules.

Architecture:
- SQLite database for rule storage
- Immutable rules (cannot be deleted, only deprecated)
- Violation tracking with event correlation
- Rule categories: ARCHITECTURE, DATA, TESTING, WORKFLOW, COMMUNICATION
- Severity levels: CRITICAL, HIGH, MEDIUM, LOW
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path


class GovernanceEngine:
    """
    Core governance engine for CORTEX.
    
    Manages:
    - Rule storage and retrieval
    - Violation detection and logging
    - Compliance checking
    - Immutability enforcement
    """
    
    def __init__(self, db_path: str):
        """
        Initialize governance engine.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
    
    def _init_schema(self) -> None:
        """Create database schema if it doesn't exist."""
        cursor = self.conn.cursor()
        
        # Rules table - immutable governance rules
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rules (
                rule_id TEXT PRIMARY KEY,
                rule_number INTEGER UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                rationale TEXT,
                examples TEXT,
                immutable BOOLEAN DEFAULT TRUE,
                deprecated BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CHECK (category IN ('ARCHITECTURE', 'DATA', 'TESTING', 'WORKFLOW', 'COMMUNICATION', 'OTHER')),
                CHECK (severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW'))
            )
        """)
        
        # Violations table - track rule violations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS violations (
                violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id TEXT NOT NULL,
                event_id TEXT,
                context TEXT NOT NULL,
                severity TEXT NOT NULL,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT FALSE,
                resolved_at TIMESTAMP,
                resolution_notes TEXT,
                FOREIGN KEY (rule_id) REFERENCES rules(rule_id)
            )
        """)
        
        # Indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_rules_category 
            ON rules(category)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_rules_severity 
            ON rules(severity)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_violations_rule 
            ON violations(rule_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_violations_resolved 
            ON violations(resolved)
        """)
        
        self.conn.commit()
    
    def add_rule(self, rule: Dict[str, Any]) -> str:
        """
        Add a new governance rule.
        
        Args:
            rule: Dictionary containing rule details
                Required: rule_id, rule_number, title, description, category, severity
                Optional: rationale, examples, immutable
        
        Returns:
            rule_id of the created rule
        
        Raises:
            ValueError: If required fields are missing or invalid
        """
        required_fields = ['rule_id', 'rule_number', 'title', 'description', 'category', 'severity']
        for field in required_fields:
            if field not in rule:
                raise ValueError(f"Missing required field: {field}")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO rules (
                rule_id, rule_number, title, description, 
                category, severity, rationale, examples, immutable
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rule['rule_id'],
            rule['rule_number'],
            rule['title'],
            rule['description'],
            rule['category'],
            rule['severity'],
            rule.get('rationale'),
            json.dumps(rule.get('examples', [])),
            rule.get('immutable', True)
        ))
        
        self.conn.commit()
        return rule['rule_id']
    
    def get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific rule by ID.
        
        Args:
            rule_id: Unique identifier for the rule
        
        Returns:
            Dictionary containing rule details, or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM rules WHERE rule_id = ?", (rule_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_all_rules(self, include_deprecated: bool = False) -> List[Dict[str, Any]]:
        """
        Retrieve all governance rules.
        
        Args:
            include_deprecated: Whether to include deprecated rules
        
        Returns:
            List of rule dictionaries
        """
        cursor = self.conn.cursor()
        
        if include_deprecated:
            cursor.execute("SELECT * FROM rules ORDER BY rule_number")
        else:
            cursor.execute("SELECT * FROM rules WHERE deprecated = FALSE ORDER BY rule_number")
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_rules_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Retrieve rules by category.
        
        Args:
            category: Rule category (ARCHITECTURE, DATA, TESTING, etc.)
        
        Returns:
            List of rule dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM rules 
            WHERE category = ? AND deprecated = FALSE 
            ORDER BY rule_number
        """, (category,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_rules_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """
        Retrieve rules by severity level.
        
        Args:
            severity: Severity level (CRITICAL, HIGH, MEDIUM, LOW)
        
        Returns:
            List of rule dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM rules 
            WHERE severity = ? AND deprecated = FALSE 
            ORDER BY rule_number
        """, (severity,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def deprecate_rule(self, rule_id: str) -> bool:
        """
        Deprecate a rule (cannot delete - immutability).
        
        Args:
            rule_id: ID of rule to deprecate
        
        Returns:
            True if successful, False if rule not found
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE rules 
            SET deprecated = TRUE, updated_at = CURRENT_TIMESTAMP 
            WHERE rule_id = ?
        """, (rule_id,))
        
        self.conn.commit()
        return cursor.rowcount > 0
    
    def log_violation(
        self, 
        rule_id: str, 
        context: str, 
        event_id: Optional[str] = None
    ) -> int:
        """
        Log a rule violation.
        
        Args:
            rule_id: ID of violated rule
            context: Description of the violation context
            event_id: Optional event ID for correlation
        
        Returns:
            violation_id
        
        Raises:
            ValueError: If rule_id doesn't exist
        """
        # Verify rule exists and get severity
        rule = self.get_rule(rule_id)
        if not rule:
            raise ValueError(f"Rule not found: {rule_id}")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO violations (rule_id, event_id, context, severity)
            VALUES (?, ?, ?, ?)
        """, (rule_id, event_id, context, rule['severity']))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_violations(
        self, 
        rule_id: Optional[str] = None, 
        resolved: Optional[bool] = None,
        severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query violations with optional filters.
        
        Args:
            rule_id: Filter by specific rule
            resolved: Filter by resolution status
            severity: Filter by severity level
        
        Returns:
            List of violation dictionaries
        """
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM violations WHERE 1=1"
        params = []
        
        if rule_id:
            query += " AND rule_id = ?"
            params.append(rule_id)
        
        if resolved is not None:
            query += " AND resolved = ?"
            params.append(resolved)
        
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        
        query += " ORDER BY detected_at DESC"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def resolve_violation(
        self, 
        violation_id: int, 
        resolution_notes: str
    ) -> bool:
        """
        Mark a violation as resolved.
        
        Args:
            violation_id: ID of violation to resolve
            resolution_notes: Description of how it was resolved
        
        Returns:
            True if successful, False if violation not found
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE violations 
            SET resolved = TRUE, 
                resolved_at = CURRENT_TIMESTAMP,
                resolution_notes = ?
            WHERE violation_id = ?
        """, (resolution_notes, violation_id))
        
        self.conn.commit()
        return cursor.rowcount > 0
    
    def check_violation(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check if a given context violates any rules.
        
        This is a placeholder for rule-specific validation logic.
        Subclasses or external validators should implement specific checks.
        
        Args:
            context: Dictionary containing the context to validate
        
        Returns:
            List of violated rules
        """
        # Placeholder - implement specific validation logic as needed
        return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get governance statistics.
        
        Returns:
            Dictionary with counts and metrics
        """
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Total rules
        cursor.execute("SELECT COUNT(*) FROM rules WHERE deprecated = FALSE")
        stats['total_rules'] = cursor.fetchone()[0]
        
        # Rules by category
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM rules 
            WHERE deprecated = FALSE 
            GROUP BY category
        """)
        stats['by_category'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Rules by severity
        cursor.execute("""
            SELECT severity, COUNT(*) as count 
            FROM rules 
            WHERE deprecated = FALSE 
            GROUP BY severity
        """)
        stats['by_severity'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Total violations
        cursor.execute("SELECT COUNT(*) FROM violations")
        stats['total_violations'] = cursor.fetchone()[0]
        
        # Unresolved violations
        cursor.execute("SELECT COUNT(*) FROM violations WHERE resolved = FALSE")
        stats['unresolved_violations'] = cursor.fetchone()[0]
        
        return stats
    
    def close(self) -> None:
        """Close database connection."""
        self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure connection is closed."""
        self.close()
