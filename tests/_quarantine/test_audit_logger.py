"""
Test Audit Logger - Governance Audit Trail Integration for Tests

Integrates with pytest to automatically generate audit log entries as tests execute.
Each test generates AC_START, AC_EXECUTE, and AC_COMPLETE entries in the governance database.

This ensures that all phases generate their own audit trail evidence through their test execution,
addressing CORE-027 Audit Logging requirement naturally as a byproduct of testing.

Features:
- Automatic AC detection from test names and markers
- AC lifecycle tracking (START → EXECUTE → COMPLETE)
- Hash chain integrity for audit entries
- Pytest plugin integration with hooks
- Batch processing for performance
- Graceful degradation if database unavailable

Usage:
1. Mark tests with @pytest.mark.ac("AC-XXX-001-01") decorator
2. Or follow naming convention: test_ac_xxx_001_01_*
3. Audit entries automatically generated on test execution

Author: Asif Hussain
"""

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
from pathlib import Path

import pytest

from cortex.infrastructure.database import DatabaseManager
from cortex.infrastructure.enhanced_audit_logger import AuditEntry


class TestAuditLogger:
    """
    Pytest plugin for automatic audit logging.
    
    Generates AC lifecycle entries as tests execute, creating the audit trail
    naturally as a side effect of testing.
    """
    
    def __init__(self):
        """Initialize audit logger."""
        self.db_manager: Optional[DatabaseManager] = None
        self.pending_entries: List[AuditEntry] = []
        self.ac_test_map: Dict[str, Set[str]] = {}  # AC-ID -> {test names}
        self.test_results: Dict[str, bool] = {}  # test name -> passed
        self.last_hash = "0" * 64  # Initial hash
        
    def pytest_configure(self, config: Any) -> None:
        """
        Initialize database connection at pytest startup.
        
        Args:
            config: Pytest config object
        """
        try:
            self.db_manager = DatabaseManager()
            self.db_manager.initialize()
            # Load last hash from database for chain continuity
            self._load_last_hash()
        except Exception as e:
            print(f"⚠️  Failed to initialize audit logging: {e}")
            self.db_manager = None
    
    def pytest_collection_modifyitems(self, items: List[Any]) -> None:
        """
        Analyze collected tests and extract AC-IDs.
        
        This runs before tests execute and identifies which ACs are being tested.
        
        Args:
            items: List of collected test items
        """
        if not self.db_manager:
            return
        
        for item in items:
            ac_id = self._extract_ac_id(item)
            if ac_id:
                if ac_id not in self.ac_test_map:
                    self.ac_test_map[ac_id] = set()
                self.ac_test_map[ac_id].add(item.nodeid)
    
    def pytest_runtest_setup(self, item: Any) -> None:
        """
        Generate AC_START entry when test begins.
        
        Args:
            item: Test item being setup
        """
        if not self.db_manager:
            return
        
        ac_id = self._extract_ac_id(item)
        if not ac_id:
            return
        
        # Create AC_START entry
        entry = AuditEntry(
            timestamp=self._now(),
            operation="AC_START",
            component=self._component_name(item),
            level="INFO",
            message=f"Starting test for {ac_id}",
            ac_id=ac_id,
            correlation_id=self._correlation_id(item),
            metadata=self._test_metadata(item, "START"),
        )
        self._add_entry(entry)
    
    def pytest_runtest_makereport(self, item: Any, call: Any) -> None:
        """
        Generate AC_EXECUTE and AC_COMPLETE entries during test execution.
        
        Args:
            item: Test item
            call: Test call info (setup, call, teardown)
        """
        if not self.db_manager or call.when != "call":
            return
        
        ac_id = self._extract_ac_id(item)
        if not ac_id:
            return
        
        # Record test result
        test_nodeid = item.nodeid
        self.test_results[test_nodeid] = call.excinfo is None
        
        # Generate AC_EXECUTE entry
        execute_entry = AuditEntry(
            timestamp=self._now(),
            operation="AC_EXECUTE",
            component=self._component_name(item),
            level="INFO",
            message=f"Executing test for {ac_id}",
            ac_id=ac_id,
            correlation_id=self._correlation_id(item),
            metadata=self._test_metadata(item, "EXECUTE", call),
        )
        self._add_entry(execute_entry)
        
        # Generate AC_COMPLETE entry if test passed
        if call.excinfo is None:
            complete_entry = AuditEntry(
                timestamp=self._now(),
                operation="AC_COMPLETE",
                component=self._component_name(item),
                level="INFO",
                message=f"Test for {ac_id} completed successfully",
                ac_id=ac_id,
                correlation_id=self._correlation_id(item),
                metadata=self._test_metadata(item, "COMPLETE", call),
            )
            self._add_entry(complete_entry)
        else:
            # Test failed - generate failure record
            failure_entry = AuditEntry(
                timestamp=self._now(),
                operation="AC_EXECUTE_FAILED",
                component=self._component_name(item),
                level="ERROR",
                message=f"Test for {ac_id} failed: {str(call.excinfo.value)}",
                ac_id=ac_id,
                correlation_id=self._correlation_id(item),
                metadata=self._test_metadata(item, "FAILED", call),
            )
            self._add_entry(failure_entry)
    
    def pytest_sessionfinish(self, session: Any, exitstatus: int) -> None:
        """
        Flush all pending audit entries to database at session end.
        
        Args:
            session: Pytest session
            exitstatus: Exit code
        """
        if not self.db_manager or not self.pending_entries:
            return
        
        try:
            self._flush_entries()
            print(f"\n✅ Audit logging: {len(self.pending_entries)} entries recorded")
        except Exception as e:
            print(f"⚠️  Failed to flush audit entries: {e}")
    
    def _extract_ac_id(self, item: Any) -> Optional[str]:
        """
        Extract AC-ID from test item.
        
        Checks:
        1. pytest.mark.ac("AC-XXX-001-01") decorator
        2. Test function name: test_ac_xxx_001_01_*
        
        Args:
            item: Pytest test item
            
        Returns:
            AC-ID string or None
        """
        # Check for explicit marker
        ac_marker = item.get_closest_marker("ac")
        if ac_marker:
            return ac_marker.args[0]
        
        # Extract from test name
        # Pattern: test_ac_xxx_001_01 or test_ac_xxx_001 or test_xxx_001_01
        test_name = item.name.lower()
        
        # Match AC-XXX-NNN-NN or AC-XXX-NNN patterns
        patterns = [
            r"test_ac_([a-z]+)_(\d{3})_(\d{2})",  # test_ac_xxx_001_01
            r"test_ac_([a-z]+)_(\d{3})",           # test_ac_xxx_001
            r"test_([a-z]+)_(\d{3})_(\d{2})",     # test_xxx_001_01
        ]
        
        for pattern in patterns:
            match = re.search(pattern, test_name)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    prefix = groups[0].upper()
                    num1 = groups[1]
                    num2 = groups[2]
                    return f"AC-{prefix}-{num1}-{num2}"
                elif len(groups) == 2:
                    prefix = groups[0].upper()
                    num1 = groups[1]
                    return f"AC-{prefix}-{num1}"
        
        return None
    
    def _component_name(self, item: Any) -> str:
        """Extract component name from test item."""
        return item.module.__name__ if hasattr(item, 'module') else item.nodeid
    
    def _correlation_id(self, item: Any) -> str:
        """Generate correlation ID for test session."""
        # Use test nodeid hash as correlation ID
        import hashlib
        return hashlib.md5(item.nodeid.encode()).hexdigest()[:16]
    
    def _test_metadata(
        self,
        item: Any,
        stage: str,
        call: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Generate metadata for audit entry."""
        metadata = {
            "test_name": item.name,
            "test_nodeid": item.nodeid,
            "stage": stage,
            "test_file": str(item.fspath),
        }
        
        if call:
            metadata["duration_seconds"] = call.duration
            if stage == "FAILED":
                metadata["error_type"] = type(call.excinfo.value).__name__
        
        return metadata
    
    def _add_entry(self, entry: AuditEntry) -> None:
        """
        Add audit entry to pending list with hash chain.
        
        Args:
            entry: Audit entry to add
        """
        # Calculate hash chain
        entry.previous_hash = self.last_hash
        entry_data = f"{entry.timestamp}{entry.operation}{entry.ac_id}{entry.message}"
        entry.entry_hash = hashlib.sha256(
            (entry_data + entry.previous_hash).encode()
        ).hexdigest()
        
        self.pending_entries.append(entry)
        self.last_hash = entry.entry_hash
    
    def _flush_entries(self) -> None:
        """Write all pending entries to database."""
        if not self.db_manager or not self.pending_entries:
            return
        
        try:
            conn = self.db_manager._connection
            
            for entry in self.pending_entries:
                conn.execute("""
                    INSERT INTO audit_log (
                        timestamp, operation, component, level, message,
                        ac_id, correlation_id, metadata,
                        previous_hash, entry_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.timestamp,
                    entry.operation,
                    entry.component,
                    entry.level,
                    entry.message,
                    entry.ac_id,
                    entry.correlation_id,
                    self._serialize_metadata(entry.metadata),
                    entry.previous_hash,
                    entry.entry_hash,
                ))
            
            conn.commit()
            self.pending_entries.clear()
        except Exception as e:
            print(f"⚠️  Error writing audit entries: {e}")
    
    def _load_last_hash(self) -> None:
        """Load the last hash from database for chain continuity."""
        try:
            if not self.db_manager:
                return
            
            conn = self.db_manager._connection
            result = conn.execute(
                "SELECT entry_hash FROM audit_log ORDER BY id DESC LIMIT 1"
            ).fetchone()
            
            if result:
                self.last_hash = result[0]
        except Exception:
            pass  # Use default if error
    
    @staticmethod
    def _now() -> str:
        """Get current timestamp in ISO format."""
        return datetime.now(timezone.utc).isoformat()
    
    @staticmethod
    def _serialize_metadata(metadata: Optional[Dict[str, Any]]) -> Optional[str]:
        """Serialize metadata to JSON string."""
        if not metadata:
            return None
        
        import json
        try:
            return json.dumps(metadata)
        except Exception:
            return None


# Pytest hook for automatic registration - should be module variable, not function
# pytest_plugins is automatically loaded from test modules
pytest_plugins = []  # Not needed here - plugin registered via conftest.py
