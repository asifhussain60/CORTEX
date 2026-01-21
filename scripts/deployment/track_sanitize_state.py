"""Incremental sanitization state tracker.

This module tracks dirty state for governance.db, enabling incremental
sanitization rather than full rebuilds.

PHASE-DEPLOYMENT-001: AC-DEP-001-04
"""

import hashlib
import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class AuditEntry:
    """Represents an audit log entry.
    
    Attributes:
        id: Database row ID.
        ac_id: Acceptance Criteria ID.
        timestamp: Entry timestamp.
        operation: Operation type.
        source: Entry source (dev/production).
        is_production: Whether this is a production entry.
    """
    id: int
    ac_id: str
    timestamp: str
    operation: str = ""
    source: str = ""
    is_production: bool = False


@dataclass
class DeltaResult:
    """Result of delta computation.
    
    Attributes:
        new_entries: Entries added since last sanitize.
        modified_count: Number of modified entries.
        timestamp: When delta was computed.
    """
    new_entries: List[AuditEntry] = field(default_factory=list)
    modified_count: int = 0
    timestamp: str = ""


@dataclass
class IncrementalSanitizeResult:
    """Result of incremental sanitization.
    
    Attributes:
        sanitized_count: Number of entries sanitized.
        preserved_count: Number of entries preserved.
        timestamp: When sanitization occurred.
    """
    sanitized_count: int = 0
    preserved_count: int = 0
    timestamp: str = ""


@dataclass
class PrecommitCheckResult:
    """Result of pre-commit dirty state check.
    
    Attributes:
        should_block: Whether pre-commit should block.
        message: Explanation message.
    """
    should_block: bool = False
    message: str = ""


@dataclass
class DifferentialView:
    """Differential view of audit log changes.
    
    Attributes:
        entries: Entries changed since last sanitize.
        since: Timestamp of last sanitize.
    """
    entries: List[AuditEntry] = field(default_factory=list)
    since: str = ""


class SanitizeStateTracker:
    """Tracks dirty state for incremental sanitization.
    
    Maintains a state file that records:
    - Last sanitization timestamp
    - Hash of entries at last sanitize
    - Entry count at last sanitize
    
    This enables computing a delta of changes since last sanitize,
    allowing incremental sanitization rather than full rebuilds.
    
    Attributes:
        db_path: Path to governance.db.
        state_path: Path to state tracking file.
    """
    
    # Patterns for dev entries
    DEV_PATTERNS = ["TEST%", "DEV%", "DEBUG%", "TEMP%", "MOCK%"]
    
    def __init__(self, db_path: Path, state_path: Path) -> None:
        """Initialize the state tracker.
        
        Args:
            db_path: Path to governance.db file.
            state_path: Path to .cortex-sanitize-state.json file.
        """
        self.db_path = Path(db_path)
        self.state_path = Path(state_path)
    
    def _load_state(self) -> dict:
        """Load the current state from file.
        
        Returns:
            State dictionary or empty dict if not exists.
        """
        if self.state_path.exists():
            return json.loads(self.state_path.read_text())
        return {}
    
    def _save_state(self, state: dict) -> None:
        """Save state to file.
        
        Args:
            state: State dictionary to save.
        """
        self.state_path.write_text(json.dumps(state, indent=2))
    
    def _compute_entries_hash(self) -> str:
        """Compute hash of current audit log entries.
        
        Returns:
            SHA256 hash of entry data.
        """
        if not self.db_path.exists():
            return ""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM audit_log ORDER BY id")
            rows = cursor.fetchall()
            
            data = json.dumps(rows, sort_keys=True)
            return hashlib.sha256(data.encode()).hexdigest()
            
        except sqlite3.OperationalError:
            return ""
        finally:
            conn.close()
    
    def _get_entry_count(self) -> int:
        """Get current entry count.
        
        Returns:
            Number of entries in audit_log.
        """
        if not self.db_path.exists():
            return 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM audit_log")
            return cursor.fetchone()[0]
        except sqlite3.OperationalError:
            return 0
        finally:
            conn.close()
    
    def check_dirty(self) -> bool:
        """Check if database has changed since last sanitize.
        
        Returns:
            True if dirty (changes detected), False if clean.
        """
        state = self._load_state()
        
        if not state:
            # No previous state, consider dirty
            return True
        
        current_hash = self._compute_entries_hash()
        current_count = self._get_entry_count()
        
        # Check if hash or count changed
        if current_hash != state.get("entries_hash", ""):
            return True
        if current_count != state.get("entry_count", 0):
            return True
        
        return False
    
    def update_state(self) -> None:
        """Update state to current database state."""
        state = {
            "last_sanitize": datetime.now().isoformat(),
            "entries_hash": self._compute_entries_hash(),
            "entry_count": self._get_entry_count(),
        }
        self._save_state(state)
    
    def compute_delta(self) -> DeltaResult:
        """Compute delta of changes since last sanitize.
        
        Returns:
            DeltaResult with new entries since last sanitize.
        """
        result = DeltaResult(timestamp=datetime.now().isoformat())
        state = self._load_state()
        
        if not self.db_path.exists():
            return result
        
        last_sanitize = state.get("last_sanitize", "1970-01-01T00:00:00")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get entries newer than last sanitize
            cursor.execute(
                "SELECT id, ac_id, timestamp, operation, source, is_production "
                "FROM audit_log WHERE timestamp > ? ORDER BY timestamp",
                (last_sanitize,)
            )
            
            for row in cursor.fetchall():
                entry = AuditEntry(
                    id=row[0],
                    ac_id=row[1],
                    timestamp=row[2],
                    operation=row[3] if len(row) > 3 else "",
                    source=row[4] if len(row) > 4 else "",
                    is_production=bool(row[5]) if len(row) > 5 else False,
                )
                result.new_entries.append(entry)
            
            result.modified_count = len(result.new_entries)
            
        finally:
            conn.close()
        
        return result
    
    def incremental_sanitize(self) -> IncrementalSanitizeResult:
        """Perform incremental sanitization of dirty entries only.
        
        Returns:
            IncrementalSanitizeResult with counts.
        """
        result = IncrementalSanitizeResult(timestamp=datetime.now().isoformat())
        
        if not self.db_path.exists():
            return result
        
        # Get delta first
        delta = self.compute_delta()
        
        # Find dev entries in delta
        dev_ac_ids = []
        for entry in delta.new_entries:
            for pattern in self.DEV_PATTERNS:
                if entry.ac_id.upper().startswith(pattern.rstrip("%")):
                    if not entry.is_production:
                        dev_ac_ids.append(entry.ac_id)
                        break
        
        if not dev_ac_ids:
            # Nothing to sanitize
            result.preserved_count = len(delta.new_entries)
            self.update_state()
            return result
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Delete dev entries
            placeholders = ",".join("?" * len(dev_ac_ids))
            cursor.execute(
                f"DELETE FROM audit_log WHERE ac_id IN ({placeholders})",
                dev_ac_ids
            )
            conn.commit()
            
            result.sanitized_count = len(dev_ac_ids)
            result.preserved_count = len(delta.new_entries) - len(dev_ac_ids)
            
        finally:
            conn.close()
        
        # Update state after sanitization
        self.update_state()
        
        return result
    
    def precommit_check(self) -> PrecommitCheckResult:
        """Check if pre-commit should block due to dirty state.
        
        Returns:
            PrecommitCheckResult indicating block status.
        """
        result = PrecommitCheckResult()
        
        if not self.check_dirty():
            result.message = "Clean state - no blocking needed"
            return result
        
        # Check if dirty entries include dev patterns
        delta = self.compute_delta()
        
        for entry in delta.new_entries:
            for pattern in self.DEV_PATTERNS:
                if entry.ac_id.upper().startswith(pattern.rstrip("%")):
                    if not entry.is_production:
                        result.should_block = True
                        result.message = f"Dirty state detected: dev entry {entry.ac_id} needs sanitization"
                        return result
        
        result.message = "Dirty state but no dev entries - safe to proceed"
        return result
    
    def get_differential_view(self) -> DifferentialView:
        """Get differential view of changes since last sanitize.
        
        Returns:
            DifferentialView with entries changed since last sanitize.
        """
        state = self._load_state()
        last_sanitize = state.get("last_sanitize", "1970-01-01T00:00:00")
        
        delta = self.compute_delta()
        
        return DifferentialView(
            entries=delta.new_entries,
            since=last_sanitize,
        )


def main() -> int:
    """CLI entry point for state tracking.
    
    Returns:
        Exit code.
    """
    import sys
    
    db_path = Path("cortex_brain/state/governance.db")
    state_path = Path(".cortex-sanitize-state.json")
    
    if "--check" in sys.argv:
        tracker = SanitizeStateTracker(db_path, state_path)
        if tracker.check_dirty():
            print("❌ Database has unsanitized changes")
            return 1
        else:
            print("✅ Database is clean")
            return 0
    
    if "--sanitize" in sys.argv:
        tracker = SanitizeStateTracker(db_path, state_path)
        result = tracker.incremental_sanitize()
        print(f"Sanitized {result.sanitized_count} entries, preserved {result.preserved_count}")
        return 0
    
    if "--update" in sys.argv:
        tracker = SanitizeStateTracker(db_path, state_path)
        tracker.update_state()
        print("State updated")
        return 0
    
    print("Usage: track_sanitize_state.py [--check|--sanitize|--update]")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
