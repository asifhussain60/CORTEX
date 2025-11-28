"""
CORTEX Compliance Database Manager

Manages SQLite database for tracking governance compliance and protection events.
Part of Sprint 2: Active Compliance Dashboard

Database Schema:
- compliance_status: Tracks overall compliance per rule
- protection_events: Logs individual protection violations
- user_compliance_history: Tracks user-specific compliance patterns

Created: November 28, 2025
Author: Asif Hussain
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import uuid
import yaml


class ComplianceDatabase:
    """
    Manages compliance tracking database for CORTEX governance.
    
    Features:
    - SQLite database for local storage
    - Rule status tracking (compliant/violated)
    - Protection event logging
    - User compliance history
    - Performance-optimized queries (<50ms)
    """
    
    def __init__(self, brain_path: Optional[Path] = None):
        """
        Initialize compliance database manager.
        
        Args:
            brain_path: Path to cortex-brain directory (auto-detects if None)
        """
        if brain_path is None:
            brain_path = self._find_brain_path()
        
        self.brain_path = brain_path
        self.db_path = brain_path / "cortex-compliance.db"
        self.rules_path = brain_path / "brain-protection-rules.yaml"
        
        # Ensure database exists and is initialized
        self._initialize_database()
    
    def _find_brain_path(self) -> Path:
        """Auto-detect cortex-brain directory."""
        current = Path.cwd()
        
        # Check current directory
        if (current / "cortex-brain").exists():
            return current / "cortex-brain"
        
        # Check parent directories (for embedded installations)
        for parent in current.parents:
            if (parent / "cortex-brain").exists():
                return parent / "cortex-brain"
        
        # Check common locations
        common_paths = [
            Path.home() / "PROJECTS" / "CORTEX" / "cortex-brain",
            Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-brain"),
        ]
        
        for path in common_paths:
            if path.exists():
                return path
        
        raise FileNotFoundError("cortex-brain directory not found")
    
    def _initialize_database(self):
        """Create database schema if not exists."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Create compliance_status table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compliance_status (
                rule_id TEXT PRIMARY KEY,
                rule_name TEXT NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                total_checks INTEGER DEFAULT 0,
                violations INTEGER DEFAULT 0,
                last_checked_at TEXT,
                last_violation_at TEXT
            )
        """)
        
        # Create protection_events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS protection_events (
                event_id TEXT PRIMARY KEY,
                rule_id TEXT NOT NULL,
                severity TEXT NOT NULL,
                file_path TEXT,
                description TEXT,
                resolution TEXT,
                created_at TEXT NOT NULL,
                resolved_at TEXT,
                FOREIGN KEY (rule_id) REFERENCES compliance_status(rule_id)
            )
        """)
        
        # Create user_compliance_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_compliance_history (
                user_id TEXT NOT NULL,
                rule_id TEXT NOT NULL,
                acknowledged_at TEXT,
                violations_count INTEGER DEFAULT 0,
                last_violation_at TEXT,
                PRIMARY KEY (user_id, rule_id)
            )
        """)
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_protection_events_created 
            ON protection_events(created_at DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_protection_events_severity 
            ON protection_events(severity)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_compliance_status_category 
            ON compliance_status(category)
        """)
        
        conn.commit()
        
        # Initialize rules from brain-protection-rules.yaml
        self._initialize_rules(conn, cursor)
        
        conn.close()
    
    def _initialize_rules(self, conn: sqlite3.Connection, cursor: sqlite3.Cursor):
        """Load rules from brain-protection-rules.yaml and populate compliance_status."""
        if not self.rules_path.exists():
            return
        
        with open(self.rules_path, 'r') as f:
            rules_config = yaml.safe_load(f)
        
        # Extract all rules from protection layers
        for layer in rules_config.get('protection_layers', []):
            layer_name = layer.get('name', 'Unknown Layer')
            
            for rule in layer.get('rules', []):
                rule_id = rule.get('rule_id')
                rule_name = rule.get('name')
                severity = rule.get('severity', 'warning')
                
                if rule_id and rule_name:
                    # Insert or ignore (avoid duplicates on re-initialization)
                    cursor.execute("""
                        INSERT OR IGNORE INTO compliance_status 
                        (rule_id, rule_name, category, severity, total_checks, violations)
                        VALUES (?, ?, ?, ?, 0, 0)
                    """, (rule_id, rule_name, layer_name, severity))
        
        conn.commit()
    
    def log_violation(
        self, 
        rule_id: str, 
        severity: str, 
        description: str,
        file_path: Optional[str] = None,
        user_id: str = "user"
    ) -> str:
        """
        Log a protection event violation.
        
        Args:
            rule_id: Rule identifier from brain-protection-rules.yaml
            severity: Violation severity (blocked/warning/info)
            description: Description of what happened
            file_path: Optional file path where violation occurred
            user_id: User identifier (default: "user")
        
        Returns:
            event_id: UUID of created protection event
        """
        event_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Insert protection event
        cursor.execute("""
            INSERT INTO protection_events 
            (event_id, rule_id, severity, file_path, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (event_id, rule_id, severity, file_path, description, timestamp))
        
        # Update compliance status
        cursor.execute("""
            UPDATE compliance_status 
            SET total_checks = total_checks + 1,
                violations = violations + 1,
                last_checked_at = ?,
                last_violation_at = ?
            WHERE rule_id = ?
        """, (timestamp, timestamp, rule_id))
        
        # Update user compliance history
        cursor.execute("""
            INSERT INTO user_compliance_history 
            (user_id, rule_id, violations_count, last_violation_at)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(user_id, rule_id) DO UPDATE SET
                violations_count = violations_count + 1,
                last_violation_at = ?
        """, (user_id, rule_id, timestamp, timestamp))
        
        conn.commit()
        conn.close()
        
        return event_id
    
    def log_check(self, rule_id: str):
        """
        Log a successful compliance check (no violation).
        
        Args:
            rule_id: Rule identifier that was checked
        """
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE compliance_status 
            SET total_checks = total_checks + 1,
                last_checked_at = ?
            WHERE rule_id = ?
        """, (timestamp, rule_id))
        
        conn.commit()
        conn.close()
    
    def get_compliance_status(self) -> List[Dict[str, Any]]:
        """
        Get overall compliance status for all rules.
        
        Returns:
            List of dicts with rule status information
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                rule_id,
                rule_name,
                category,
                severity,
                total_checks,
                violations,
                last_checked_at,
                last_violation_at,
                CASE 
                    WHEN violations = 0 THEN 'compliant'
                    WHEN violations > 0 AND violations < total_checks * 0.1 THEN 'warning'
                    ELSE 'violated'
                END as status
            FROM compliance_status
            ORDER BY category, rule_name
        """)
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent protection events.
        
        Args:
            limit: Maximum number of events to return (default: 10)
        
        Returns:
            List of recent protection events
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                pe.event_id,
                pe.rule_id,
                cs.rule_name,
                cs.category,
                pe.severity,
                pe.file_path,
                pe.description,
                pe.created_at,
                pe.resolved_at
            FROM protection_events pe
            JOIN compliance_status cs ON pe.rule_id = cs.rule_id
            ORDER BY pe.created_at DESC
            LIMIT ?
        """, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_compliance_score(self) -> float:
        """
        Calculate overall compliance score (percentage of compliant rules).
        
        Returns:
            Compliance score (0.0 to 100.0)
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_rules,
                SUM(CASE WHEN violations = 0 THEN 1 ELSE 0 END) as compliant_rules
            FROM compliance_status
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0] > 0:
            return (row[1] / row[0]) * 100.0
        return 0.0
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive compliance statistics.
        
        Returns:
            Dict with statistics including scores, counts, trends
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Overall statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_rules,
                SUM(total_checks) as total_checks,
                SUM(violations) as total_violations,
                SUM(CASE WHEN violations = 0 THEN 1 ELSE 0 END) as compliant_rules,
                SUM(CASE WHEN violations > 0 AND violations < total_checks * 0.1 THEN 1 ELSE 0 END) as warning_rules,
                SUM(CASE WHEN violations >= total_checks * 0.1 THEN 1 ELSE 0 END) as violated_rules
            FROM compliance_status
        """)
        
        stats = cursor.fetchone()
        
        # Category breakdown
        cursor.execute("""
            SELECT 
                category,
                COUNT(*) as rules_count,
                SUM(violations) as violations_count
            FROM compliance_status
            GROUP BY category
            ORDER BY violations_count DESC
        """)
        
        category_breakdown = [
            {'category': row[0], 'rules': row[1], 'violations': row[2]}
            for row in cursor.fetchall()
        ]
        
        # Recent trends (last 7 days)
        cursor.execute("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as events_count
            FROM protection_events
            WHERE created_at >= datetime('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        
        trends = [
            {'date': row[0], 'events': row[1]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        compliance_score = (stats[3] / stats[0] * 100.0) if stats[0] > 0 else 0.0
        
        return {
            'total_rules': stats[0],
            'total_checks': stats[1],
            'total_violations': stats[2],
            'compliant_rules': stats[3],
            'warning_rules': stats[4],
            'violated_rules': stats[5],
            'compliance_score': round(compliance_score, 1),
            'category_breakdown': category_breakdown,
            'recent_trends': trends
        }
    
    def resolve_event(self, event_id: str, resolution: str):
        """
        Mark a protection event as resolved.
        
        Args:
            event_id: Event UUID to resolve
            resolution: Description of how it was resolved
        """
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE protection_events 
            SET resolved_at = ?,
                resolution = ?
            WHERE event_id = ?
        """, (timestamp, resolution, event_id))
        
        conn.commit()
        conn.close()
