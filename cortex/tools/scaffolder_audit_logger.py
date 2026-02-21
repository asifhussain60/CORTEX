"""
Scaffolder Audit Logger (AC-WAVE-2-S1-AUDIT-001)

Comprehensive audit trail logging for intelligent test scaffolding operations.
Logs all intelligence decisions with forensic-grade detail for:
- Registry queries (duplicate detection)
- Quality scores per test
- Scaffolder decisions (upgrade/replace/cancel)
- CORE-035 violation attempts

All logs stored in governance.db with AC markers for compliance auditing.
"""

import json
import sqlite3
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class AuditOperation(Enum):
    """Types of auditable scaffolder operations."""
    PRE_SCAFFOLDING_CHECK = "pre_scaffolding_check"
    HOLISTIC_REPLACEMENT = "holistic_replacement"
    INTELLIGENT_TEST_GENERATION = "intelligent_test_generation"
    QUALITY_VALIDATION = "quality_validation"
    SCAFFOLDER_DECISION = "scaffolder_decision"


@dataclass
class RegistryQueryResult:
    """Result of registry query for duplicate detection."""
    found: bool
    location: Optional[str] = None
    capability_overlap: float = 0.0  # 0.0-1.0
    name_collision: bool = False


@dataclass
class QualityScoreBreakdown:
    """Detailed quality score breakdown per test."""
    coverage_score: float
    realism_score: float
    maintainability_score: float
    brittleness_score: float
    composite_score: float
    gate_passed: bool
    brittleness_patterns: List[str] = field(default_factory=list)


@dataclass
class ReplacementAction:
    """Action taken during holistic replacement."""
    action: str  # backup, scaffold, migrate_tests
    path: str
    success: bool
    details: Optional[str] = None


@dataclass
class AuditLogEntry:
    """Single audit log entry."""
    timestamp: str
    operation: str
    orchestrator_name: str
    ac_marker: str
    details: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON storage."""
        return {
            "timestamp": self.timestamp,
            "operation": self.operation,
            "orchestrator_name": self.orchestrator_name,
            "ac_marker": self.ac_marker,
            "details": self.details,
        }


class ScaffolderAuditLogger:
    """
    Comprehensive audit logger for scaffolder operations.
    
    Logs all intelligence decisions to governance.db with AC markers
    for forensic analysis and compliance verification.
    """
    
    def __init__(self, db_path: Optional[Path] = None) -> None:
        """
        Initialize audit logger.
        
        Args:
            db_path: Path to governance.db (defaults to .cortex-runtime/governance.db)
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / ".cortex-runtime" / "governance.db"
        
        self.db_path = db_path
        self._ensure_audit_table()
    
    def _ensure_audit_table(self) -> None:
        """Ensure audit table exists in governance.db."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scaffolder_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    orchestrator_name TEXT NOT NULL,
                    ac_marker TEXT NOT NULL,
                    details TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_scaffolder_audit_operation 
                ON scaffolder_audit_log(operation)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_scaffolder_audit_orchestrator 
                ON scaffolder_audit_log(orchestrator_name)
            """)
            conn.commit()
    
    def log_pre_scaffolding_check(
        self,
        orchestrator_name: str,
        query_result: RegistryQueryResult,
        decision: str,
        decision_rationale: str,
        user_override: bool = False,
    ) -> str:
        """
        Log pre-scaffolding registry query and duplicate check.
        
        Args:
            orchestrator_name: Name of orchestrator being scaffolded
            query_result: Result of registry query
            decision: upgrade|replace|create_new|cancel
            decision_rationale: Why this decision was made
            user_override: Whether user overrode recommendation
            
        Returns:
            AC marker for this audit entry
        """
        timestamp = datetime.now().isoformat()
        ac_marker = f"AC-WAVE-2-S1A-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        details = {
            "registry_query_result": {
                "found": query_result.found,
                "location": query_result.location,
                "capability_overlap": query_result.capability_overlap,
                "name_collision": query_result.name_collision,
            },
            "decision": decision,
            "decision_rationale": decision_rationale,
            "user_override": user_override,
        }
        
        entry = AuditLogEntry(
            timestamp=timestamp,
            operation=AuditOperation.PRE_SCAFFOLDING_CHECK.value,
            orchestrator_name=orchestrator_name,
            ac_marker=ac_marker,
            details=details,
        )
        
        self._write_log(entry)
        return ac_marker
    
    def log_holistic_replacement(
        self,
        orchestrator_name: str,
        old_location: str,
        old_version: str,
        collision_type: str,
        user_choice: str,
        actions_taken: List[ReplacementAction],
        registry_updated: bool,
        core_035_violation: bool = False,
    ) -> str:
        """
        Log holistic replacement operation.
        
        Args:
            orchestrator_name: Name of orchestrator
            old_location: Path to old implementation
            old_version: Version of old implementation
            collision_type: name|capability|both
            user_choice: replace|version|cancel
            actions_taken: List of actions performed
            registry_updated: Whether registry was updated
            core_035_violation: Whether CORE-035 was violated
            
        Returns:
            AC marker for this audit entry
        """
        timestamp = datetime.now().isoformat()
        ac_marker = f"AC-WAVE-2-S1B-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        details = {
            "duplicate_details": {
                "old_location": old_location,
                "old_version": old_version,
                "collision_type": collision_type,
            },
            "user_choice": user_choice,
            "actions_taken": [asdict(action) for action in actions_taken],
            "registry_updated": registry_updated,
            "core_035_violation": core_035_violation,
        }
        
        entry = AuditLogEntry(
            timestamp=timestamp,
            operation=AuditOperation.HOLISTIC_REPLACEMENT.value,
            orchestrator_name=orchestrator_name,
            ac_marker=ac_marker,
            details=details,
        )
        
        self._write_log(entry)
        return ac_marker
    
    def log_intelligent_test_generation(
        self,
        orchestrator_name: str,
        stage: str,
        spec_source: str,
        demand_analysis: Dict[str, Any],
        composition: Optional[Dict[str, Any]] = None,
        quality_validation: Optional[QualityScoreBreakdown] = None,
    ) -> str:
        """
        Log intelligent test generation (demand → compose → validate).
        
        Args:
            orchestrator_name: Name of orchestrator
            stage: demand|compose|validate
            spec_source: Path to orchestrator spec file
            demand_analysis: Results of demand generation
            composition: Results of test composition (if stage=compose)
            quality_validation: Quality scores (if stage=validate)
            
        Returns:
            AC marker for this audit entry
        """
        timestamp = datetime.now().isoformat()
        ac_marker = f"AC-WAVE-2-S2-{orchestrator_name.upper()}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        details = {
            "stage": stage,
            "spec_source": spec_source,
            "demand_analysis": demand_analysis,
        }
        
        if composition:
            details["composition"] = composition
        
        if quality_validation:
            details["quality_validation"] = asdict(quality_validation)
        
        entry = AuditLogEntry(
            timestamp=timestamp,
            operation=AuditOperation.INTELLIGENT_TEST_GENERATION.value,
            orchestrator_name=orchestrator_name,
            ac_marker=ac_marker,
            details=details,
        )
        
        self._write_log(entry)
        return ac_marker
    
    def _write_log(self, entry: AuditLogEntry) -> None:
        """Write audit log entry to database."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """
                INSERT INTO scaffolder_audit_log 
                (timestamp, operation, orchestrator_name, ac_marker, details)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    entry.timestamp,
                    entry.operation,
                    entry.orchestrator_name,
                    entry.ac_marker,
                    json.dumps(entry.details),
                ),
            )
            conn.commit()
    
    def query_logs(
        self,
        operation: Optional[str] = None,
        orchestrator_name: Optional[str] = None,
        limit: int = 100,
    ) -> List[AuditLogEntry]:
        """
        Query audit logs with filters.
        
        Args:
            operation: Filter by operation type
            orchestrator_name: Filter by orchestrator name
            limit: Maximum number of entries to return
            
        Returns:
            List of audit log entries
        """
        with sqlite3.connect(str(self.db_path)) as conn:
            query = "SELECT timestamp, operation, orchestrator_name, ac_marker, details FROM scaffolder_audit_log WHERE 1=1"
            params = []
            
            if operation:
                query += " AND operation = ?"
                params.append(operation)
            
            if orchestrator_name:
                query += " AND orchestrator_name = ?"
                params.append(orchestrator_name)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            return [
                AuditLogEntry(
                    timestamp=row[0],
                    operation=row[1],
                    orchestrator_name=row[2],
                    ac_marker=row[3],
                    details=json.loads(row[4]),
                )
                for row in rows
            ]