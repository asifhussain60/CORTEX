# AC_START: AC-MEGA-B-S2-004-SOLID
"""SOLIDOrchestrator - Unified SOLID compliance checking with SQLite audit."""

from __future__ import annotations
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import Result type for proper handling
# AC-FIX-SOLID-IMPORT-001: Removed mock fallback — real analyzers importable now
from cortex.orchestrators.core.solid_analyzers import (
    SRPAnalyzer,
    OCPAnalyzer,
    ISPAnalyzer,
    DIPAnalyzer,
    DRYAnalyzer,
    SolidViolation,
)
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin

# Phase 58-C: DomainBrain wiring (validation decision-making orchestrator)
try:
    from cortex.intelligence.domain_brain import DomainBrainAPI as _SolidDomainBrainAPI  # type: ignore[attr-defined]
except Exception:
    _SolidDomainBrainAPI = None  # type: ignore[assignment,misc]
    """Unified SOLID compliance: SRP + OCP + LSP + ISP + DIP + DRY.
    
    Consolidates:
    - SRPAnalyzer (Single Responsibility Principle)
    - OCPAnalyzer (Open/Closed Principle)
    - ISPAnalyzer (Interface Segregation Principle)
    - DIPAnalyzer (Dependency Inversion Principle)
    - DRYAnalyzer (Don't Repeat Yourself)
    - LSPAnalyzer (Liskov Substitution - future)
    
    Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
    Phase: 23 MEGA-B Stage 2 - Component Registration
    """
    
    def __init__(self, audit_db_path: Optional[Path] = None) -> None:
        """Initialize SOLID orchestrator.
        
        Args:
            audit_db_path: Optional SQLite audit DB path
        """
        self.srp_analyzer = SRPAnalyzer()
        self.ocp_analyzer = OCPAnalyzer()
        self.isp_analyzer = ISPAnalyzer()
        self.dip_analyzer = DIPAnalyzer()
        self.dry_analyzer = DRYAnalyzer()
        
        self._violations: List[SolidViolation] = []
        
        # SQLite audit logging (store in subdirectory to avoid root pollution)
        if audit_db_path:
            self.audit_db_path = audit_db_path
        else:
            db_dir = Path("cortex/intelligence/quality")
            db_dir.mkdir(parents=True, exist_ok=True)
            self.audit_db_path = db_dir / "solid_audit.db"
        self._init_audit_db()
    
    def _init_audit_db(self) -> None:
        """Initialize SQLite audit database."""
        conn = sqlite3.connect(self.audit_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS solid_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                operation TEXT NOT NULL,
                target TEXT NOT NULL,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def _audit_log(
        self,
        operation: str,
        target: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log operation to audit database."""
        conn = sqlite3.connect(self.audit_db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO solid_audit (timestamp, operation, target, metadata) VALUES (?, ?, ?, ?)",
            (
                datetime.now().isoformat(),
                operation,
                target,
                json.dumps(metadata) if metadata else None
            )
        )
        conn.commit()
        conn.close()
    
    def analyze_srp(self, file_path: Path) -> List[SolidViolation]:
        """Analyze Single Responsibility Principle violations.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            List of SRP violations
        """
        result = self.srp_analyzer.analyze(file_path)
        violations = result.unwrap() if result.is_ok() else []
        
        self._violations.extend(violations)
        self._audit_log("ANALYZE_SRP", str(file_path), {"violations": len(violations)})
        
        return violations
    
    def analyze_ocp(self, file_path: Path) -> List[SolidViolation]:
        """Analyze Open/Closed Principle violations."""
        result = self.ocp_analyzer.analyze(file_path)
        violations = result.unwrap() if result.is_ok() else []
        
        self._violations.extend(violations)
        self._audit_log("ANALYZE_OCP", str(file_path), {"violations": len(violations)})
        
        return violations
    
    def analyze_isp(self, file_path: Path) -> List[SolidViolation]:
        """Analyze Interface Segregation Principle violations."""
        result = self.isp_analyzer.analyze(file_path)
        violations = result.unwrap() if result.is_ok() else []
        
        self._violations.extend(violations)
        self._audit_log("ANALYZE_ISP", str(file_path), {"violations": len(violations)})
        
        return violations
    
    def analyze_dip(self, file_path: Path) -> List[SolidViolation]:
        """Analyze Dependency Inversion Principle violations."""
        result = self.dip_analyzer.analyze(file_path)
        violations = result.unwrap() if result.is_ok() else []
        
        self._violations.extend(violations)
        self._audit_log("ANALYZE_DIP", str(file_path), {"violations": len(violations)})
        
        return violations
    
    def analyze_dry(self, file_paths: List[Path]) -> List[SolidViolation]:
        """Analyze Don't Repeat Yourself violations across files."""
        result = self.dry_analyzer.analyze(file_paths)
        violations = result.unwrap() if result.is_ok() else []
        
        self._violations.extend(violations)
        self._audit_log("ANALYZE_DRY", f"{len(file_paths)} files", {"violations": len(violations)})
        
        return violations
    
    def analyze_all(self, file_path: Path) -> Dict[str, List[SolidViolation]]:
        """Analyze all SOLID principles for a file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Dictionary mapping principle to violations
        """
        # Phase 58 — cross-cutting hooks
        self._activate_cross_cutting_hooks(operation="analyze_solid")
        return {
            "srp": self.analyze_srp(file_path),
            "ocp": self.analyze_ocp(file_path),
            "isp": self.analyze_isp(file_path),
            "dip": self.analyze_dip(file_path),
            "dry": self.analyze_dry([file_path])
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all violations.
        
        Returns:
            Summary dictionary with counts by type
        """
        by_type: Dict[str, int] = {}
        for violation in self._violations:
            vtype = violation.violation_type.value
            by_type[vtype] = by_type.get(vtype, 0) + 1
        
        return {
            "total_violations": len(self._violations),
            "by_type": by_type,
            "violations": self._violations
        }
    
    def clear_violations(self) -> None:
        """Clear violation history."""
        self._violations.clear()
        self._audit_log("CLEAR", "all", {})
    
    def query_audit_log(
        self,
        operation: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Query audit log."""
        conn = sqlite3.connect(self.audit_db_path)
        cursor = conn.cursor()
        
        if operation:
            cursor.execute(
                "SELECT * FROM solid_audit WHERE operation = ? ORDER BY timestamp DESC LIMIT ?",
                (operation, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM solid_audit ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": r[0],
                "timestamp": r[1],
                "operation": r[2],
                "target": r[3],
                "metadata": r[4]
            }
            for r in rows
        ]


# AC_COMPLETE: AC-MEGA-B-S2-004-SOLID ✅ Implemented
