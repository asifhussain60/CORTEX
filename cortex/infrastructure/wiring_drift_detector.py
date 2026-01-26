"""
MCP Drift Detector - AC-PERMANENT-FIX-016

Asynchronous health-check loop that detects orchestrator wiring drift every 60 seconds.

This runs independently of user operations and:
1. Compares current runtime state against wiring contract
2. Logs drift to audit trail
3. Sets global flag for pre-op gates
4. Performs safe auto-remediation (missing orchestrators)

Key: Drift detection is EXTERNAL to runtime (MCP process), not internal.
This prevents silent divergence.
"""

import json
import logging
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable

logger = logging.getLogger(__name__)


@dataclass
class DriftEvent:
    """A drift detection event."""
    detected_at: str
    expected_count: int
    actual_count: int
    added: List[str]
    removed: List[str]
    remediation_applied: str  # "NONE", "AUTO", "MANUAL_REQUIRED"
    remediation_details: str


class WiringDriftDetector:
    """
    Detects wiring drift between contract and runtime.
    
    Runs as a background thread (60s interval).
    """

    _instance: Optional['WiringDriftDetector'] = None
    _running = False
    _thread: Optional[threading.Thread] = None
    _drift_flag = False
    _last_drift_event: Optional[DriftEvent] = None
    _audit_callback: Optional[Callable[[DriftEvent], None]] = None
    _remediation_callback: Optional[Callable[[List[str]], None]] = None

    CHECK_INTERVAL_SECONDS = 60
    RETRY_INTERVAL_SECONDS = 5

    @classmethod
    def instance(cls) -> 'WiringDriftDetector':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset singleton (for testing)."""
        if cls._instance is not None:
            cls._instance.stop()
        cls._instance = None
        cls._drift_flag = False
        cls._last_drift_event = None

    def start(
        self,
        audit_callback: Optional[Callable[[DriftEvent], None]] = None,
        remediation_callback: Optional[Callable[[List[str]], None]] = None,
    ) -> None:
        """
        Start background health-check loop.
        
        Args:
            audit_callback: Function to call when drift detected (logs to audit trail)
            remediation_callback: Function to call with list of orchestrators to remediate
        """
        if self._running:
            logger.debug("Drift detector already running")
            return

        self._audit_callback = audit_callback
        self._remediation_callback = remediation_callback
        self._running = True

        # Start background thread
        self._thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self._thread.start()

        logger.info("✅ Drift detector started (60s interval)")

    def stop(self) -> None:
        """Stop background health-check loop."""
        if not self._running:
            return

        self._running = False

        if self._thread is not None:
            self._thread.join(timeout=5)

        logger.info("⛔ Drift detector stopped")

    def has_drift(self) -> bool:
        """Check if drift was detected (for pre-op gates)."""
        return self._drift_flag

    def get_last_event(self) -> Optional[DriftEvent]:
        """Get last drift event details."""
        return self._last_drift_event

    def clear_drift_flag(self) -> None:
        """Clear drift flag after remediation (called by pre-op gate)."""
        self._drift_flag = False
        logger.debug("Drift flag cleared")

    def _health_check_loop(self) -> None:
        """Background thread: runs health-check every 60 seconds."""
        logger.debug("Drift detector loop started")

        while self._running:
            try:
                self._run_health_check()
            except Exception as e:
                logger.error(f"Health-check error: {e}", exc_info=True)

            # Sleep for next interval
            for _ in range(self.CHECK_INTERVAL_SECONDS):
                if not self._running:
                    break
                threading.Event().wait(1)  # Sleep 1s at a time (allows responsive shutdown)

    def _run_health_check(self) -> None:
        """Execute single health-check iteration."""
        try:
            # Get wiring contract
            from cortex.infrastructure.wiring_contract_manager import WiringContractManager

            manager = WiringContractManager.instance()
            contract = manager.get_contract()

            # Get current runtime state
            from cortex.orchestrators.core.database_registry import get_database_registry

            registry = get_database_registry()
            runtime_orchestrators = list(registry.get_all_orchestrators().keys())

            # Compare
            comparison = manager.compare_with_runtime_state(runtime_orchestrators)

            if comparison["drift_detected"]:
                self._handle_drift_detected(comparison, contract.checksum)
            else:
                self._handle_drift_clear(comparison)

        except Exception as e:
            logger.warning(f"Failed to run health-check: {e}")

    def _handle_drift_detected(self, comparison: Dict[str, Any], contract_checksum: str) -> None:
        """Handle case where drift is detected."""
        added = comparison.get("added", [])
        removed = comparison.get("removed", [])

        logger.warning(
            f"⚠️  Wiring drift detected: "
            f"expected {comparison['expected_count']}, got {comparison['actual_count']} "
            f"(+{len(added)}/-{len(removed)})"
        )

        # Create drift event
        event = DriftEvent(
            detected_at=datetime.now(timezone.utc).isoformat(),
            expected_count=comparison["expected_count"],
            actual_count=comparison["actual_count"],
            added=added,
            removed=removed,
            remediation_applied="PENDING",
            remediation_details="",
        )

        self._last_drift_event = event
        self._drift_flag = True

        # Log to audit trail
        if self._audit_callback:
            self._audit_callback(event)

        # Attempt auto-remediation for removed orchestrators
        if removed:
            logger.info(f"Attempting auto-remediation for: {removed}")

            if self._remediation_callback:
                self._remediation_callback(removed)

            event.remediation_applied = "AUTO"
            event.remediation_details = f"Auto-remediated: {json.dumps(removed)}"

    def _handle_drift_clear(self, comparison: Dict[str, Any]) -> None:
        """Handle case where no drift detected."""
        if self._drift_flag:
            logger.info(
                f"✅ Drift cleared: all {comparison['expected_count']} orchestrators verified"
            )
            self._drift_flag = False

    def validate_health(self) -> Dict[str, Any]:
        """
        Get current health status (for monitoring).
        
        Returns:
            Health status dict
        """
        try:
            from cortex.infrastructure.wiring_contract_manager import WiringContractManager
            from cortex.orchestrators.core.database_registry import get_database_registry

            manager = WiringContractManager.instance()
            registry = get_database_registry()

            contract = manager.get_contract()
            runtime = list(registry.get_all_orchestrators().keys())

            comparison = manager.compare_with_runtime_state(runtime)

            return {
                "detector_running": self._running,
                "drift_detected": self._drift_flag,
                "last_check": self._last_drift_event.detected_at if self._last_drift_event else None,
                "expected_orchestrators": comparison["expected_count"],
                "actual_orchestrators": comparison["actual_count"],
                "missing": comparison["removed"],
                "extra": comparison["added"],
                "contract_checksum": contract.checksum[:8],
                "status": "HEALTHY" if not self._drift_flag else "DRIFT_DETECTED",
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e),
            }


class AuditTrailLogger:
    """Logs drift events to audit trail."""

    def __init__(self, audit_db_path: Optional[Path] = None):
        """Initialize with audit database path."""
        if audit_db_path is None:
            audit_db_path = Path.home() / ".cortex" / "audit_trail.db"

        self.audit_db_path = audit_db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self) -> None:
        """Ensure audit database and tables exist."""
        try:
            import sqlite3

            self.audit_db_path.parent.mkdir(parents=True, exist_ok=True)

            conn = sqlite3.connect(self.audit_db_path)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS drift_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    detected_at TEXT NOT NULL,
                    expected_count INTEGER,
                    actual_count INTEGER,
                    added TEXT,
                    removed TEXT,
                    remediation_applied TEXT,
                    remediation_details TEXT,
                    logged_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            conn.close()

            logger.debug(f"Audit database ready: {self.audit_db_path}")

        except Exception as e:
            logger.error(f"Failed to initialize audit database: {e}")

    def log_drift_event(self, event: DriftEvent) -> None:
        """Log a drift event to audit trail."""
        try:
            import sqlite3

            conn = sqlite3.connect(self.audit_db_path)
            conn.execute("""
                INSERT INTO drift_events (
                    detected_at, expected_count, actual_count,
                    added, removed, remediation_applied, remediation_details
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                event.detected_at,
                event.expected_count,
                event.actual_count,
                json.dumps(event.added),
                json.dumps(event.removed),
                event.remediation_applied,
                event.remediation_details,
            ))
            conn.commit()
            conn.close()

            logger.debug(f"Logged drift event to audit trail")

        except Exception as e:
            logger.error(f"Failed to log drift event: {e}")

    def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent drift events from audit trail."""
        try:
            import sqlite3

            conn = sqlite3.connect(self.audit_db_path)
            cursor = conn.execute("""
                SELECT detected_at, expected_count, actual_count,
                       added, removed, remediation_applied, remediation_details,
                       logged_at
                FROM drift_events
                ORDER BY logged_at DESC
                LIMIT ?
            """, (limit,))

            events: List[Dict[str, Any]] = []
            for row in cursor.fetchall():
                event_dict: Dict[str, Any] = {
                    "detected_at": row[0],
                    "expected_count": row[1],
                    "actual_count": row[2],
                    "added": json.loads(row[3] or "[]"),
                    "removed": json.loads(row[4] or "[]"),
                    "remediation": row[5],
                    "details": row[6],
                    "logged_at": row[7],
                }
                events.append(event_dict)

            conn.close()
            return events

        except Exception as e:
            logger.error(f"Failed to retrieve audit events: {e}")
            return []
