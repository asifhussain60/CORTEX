#!/usr/bin/env python3
"""
Test Performance Auditor - Enterprise-Level Test Hanging Detection
=====================================================================

Identifies hanging and slow tests using CORTEX audit logging infrastructure.
Provides real-time tracking of test execution with structured logging.

Features:
  - Real-time test execution monitoring via pytest plugin
  - Enterprise audit logging for all test metrics
  - Automatic detection of slow/hanging tests (configurable thresholds)
  - Detailed performance report with actionable insights
  - Integration with CORTEX governance audit trail

Usage:
  python scripts/test-performance-auditor.py run [options]
  python scripts/test-performance-auditor.py report
  python scripts/test-performance-auditor.py analyze --threshold-seconds 5
"""

import sys
import json
import time
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from enum import Enum


# ============================================================================
# AUDIT INFRASTRUCTURE
# ============================================================================



@dataclass
class TestMetric:
    """Enterprise audit record for a single test."""
    test_id: str  # tests/unit/core/test_something.py::TestClass::test_method
    test_file: str
    test_class: Optional[str]
    test_method: str
    status: str  # PENDING, RUNNING, PASSED, FAILED, ERROR, TIMEOUT, SKIPPED
    start_time: float
    end_time: Optional[float] = None
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    audit_entry_id: Optional[str] = None
    recorded_at: str = None
    
    def __post_init__(self):
        if self.recorded_at is None:
            self.recorded_at = datetime.now().isoformat()
        if self.end_time is not None:
            self.duration_seconds = self.end_time - self.start_time


class TestAuditDB:
    """Enterprise audit database for test performance tracking."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize audit database."""
        if db_path is None:
            db_path = Path(__file__).parent.parent / "cortex_brain" / "state" / "test_audit.db"
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()
    
    def _init_schema(self):
        """Initialize audit database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id TEXT UNIQUE NOT NULL,
                    test_file TEXT NOT NULL,
                    test_class TEXT,
                    test_method TEXT NOT NULL,
                    status TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    duration_seconds REAL,
                    error_message TEXT,
                    recorded_at TEXT NOT NULL,
                    INDEXED (test_id, status, duration_seconds)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    total_tests INTEGER,
                    passed INTEGER DEFAULT 0,
                    failed INTEGER DEFAULT 0,
                    errors INTEGER DEFAULT 0,
                    timeouts INTEGER DEFAULT 0,
                    skipped INTEGER DEFAULT 0,
                    total_duration_seconds REAL DEFAULT 0
                )
            """)
            conn.commit()
    
    def record_test(self, metric: TestMetric) -> str:
        """Record test execution metric."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert or replace test metric
            cursor.execute("""
                INSERT OR REPLACE INTO test_metrics 
                (test_id, test_file, test_class, test_method, status, 
                 start_time, end_time, duration_seconds, error_message, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metric.test_id,
                metric.test_file,
                metric.test_class,
                metric.test_method,
                metric.status,
                metric.start_time,
                metric.end_time,
                metric.duration_seconds,
                metric.error_message,
                metric.recorded_at
            ))
            
            conn.commit()
            cursor_id = cursor.lastrowid
            return f"AUDIT-TEST-{cursor_id:06d}"
    
    def get_slow_tests(self, threshold_seconds: float = 1.0) -> List[Dict]:
        """Retrieve tests exceeding duration threshold."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM test_metrics 
                WHERE duration_seconds > ? 
                ORDER BY duration_seconds DESC
            """, (threshold_seconds,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_hanging_tests(self) -> List[Dict]:
        """Retrieve tests with TIMEOUT status."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM test_metrics 
                WHERE status IN ('TIMEOUT', 'ERROR')
                ORDER BY recorded_at DESC
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_session_stats(self, session_id: str) -> Optional[Dict]:
        """Get statistics for test session."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM audit_sessions WHERE session_id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def create_session(self, session_id: str, total_tests: int) -> str:
        """Create new audit session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO audit_sessions 
                (session_id, started_at, total_tests)
                VALUES (?, ?, ?)
            """, (session_id, datetime.now().isoformat(), total_tests))
            
            conn.commit()
            return session_id


# ============================================================================
# STRUCTURED LOGGING
# ============================================================================

def setup_audit_logger(log_file: Optional[Path] = None) -> logging.Logger:
    """Setup structured logging for test audit."""
    if log_file is None:
        log_file = Path(__file__).parent.parent / "test_performance_audit.log"
    
    logger = logging.getLogger("test_audit")
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in logger.handlers:
        logger.removeHandler(handler)
    
    # File handler with JSON formatting
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)
    
    # Formatter with structured data
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
        datefmt='%Y-%m-%dT%H:%M:%SZ'
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    return logger


# ============================================================================
# PYTEST PLUGIN FOR REAL-TIME TRACKING
# ============================================================================

class TestPerformancePlugin:
    """Pytest plugin for real-time test performance tracking."""
    
    def __init__(self, audit_db: TestAuditDB, logger: logging.Logger, session_id: str):
        """Initialize plugin."""
        self.audit_db = audit_db
        self.logger = logger
        self.session_id = session_id
        self.test_starts: Dict[str, float] = {}
        self.start_time = time.time()
    
    def pytest_sessionstart(self, session):
        """Called when test session starts."""
        total_tests = len(session.items) if hasattr(session, 'items') else 0
        self.audit_db.create_session(self.session_id, total_tests)
        
        self.logger.info(json.dumps({
            "event": "session_start",
            "session_id": self.session_id,
            "total_tests": total_tests
        }))
    
    def pytest_runtest_setup(self, item):
        """Called before test execution."""
        test_id = item.nodeid
        self.test_starts[test_id] = time.time()
        
        self.logger.info(json.dumps({
            "event": "test_start",
            "test_id": test_id,
            "timestamp": datetime.now().isoformat()
        }))
    
    def pytest_runtest_logreport(self, report):
        """Called for each test report phase."""
        if report.when != "call":
            return
        
        test_id = report.nodeid
        start_time = self.test_starts.get(test_id, time.time())
        end_time = time.time()
        duration = end_time - start_time
        
        # Parse test identifiers
        parts = test_id.rsplit("::", 2)
        test_file = parts[0]
        test_class = parts[1] if len(parts) > 1 else None
        test_method = parts[-1] if parts else test_id
        
        # Determine status
        if report.outcome == "passed":
            status = TestStatus.PASSED.value
        elif report.outcome == "failed":
            status = TestStatus.FAILED.value
        elif report.outcome == "skipped":
            status = TestStatus.SKIPPED.value
        else:
            status = TestStatus.ERROR.value
        
        # Extract error message if available
        error_msg = None
        if report.longrepr:
            error_msg = str(report.longrepr)[:500]  # First 500 chars
        
        # Record metric
        metric = TestMetric(
            test_id=test_id,
            test_file=test_file,
            test_class=test_class,
            test_method=test_method,
            status=status,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            error_message=error_msg
        )
        
        audit_id = self.audit_db.record_test(metric)
        
        # Log metric with threshold detection
        is_slow = duration > 1.0
        alert_level = "WARN" if is_slow else "INFO"
        
        self.logger.log(
            logging.WARNING if is_slow else logging.INFO,
            json.dumps({
                "event": "test_complete",
                "audit_id": audit_id,
                "test_id": test_id,
                "status": status,
                "duration_seconds": round(duration, 3),
                "is_slow": is_slow,
                "alert_level": alert_level
            })
        )
    
    def pytest_sessionfinish(self, session, exitstatus):
        """Called when test session finishes."""
        total_duration = time.time() - self.start_time
        
        self.logger.info(json.dumps({
            "event": "session_complete",
            "session_id": self.session_id,
            "total_duration_seconds": round(total_duration, 2),
            "exit_status": exitstatus
        }))


# ============================================================================
# REPORTING
# ============================================================================

def generate_performance_report(audit_db: TestAuditDB, output_file: Optional[Path] = None):
    """Generate detailed performance report."""
    
    slow_tests = audit_db.get_slow_tests(threshold_seconds=0.5)
    hanging_tests = audit_db.get_hanging_tests()
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_slow_tests": len(slow_tests),
            "total_hanging_tests": len(hanging_tests),
        },
        "slow_tests": slow_tests[:20],  # Top 20
        "hanging_tests": hanging_tests[:10],  # Top 10
    }
    
    if output_file is None:
        output_file = Path(__file__).parent.parent / "test_performance_report.json"
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report


def print_performance_summary(audit_db: TestAuditDB):
    """Print formatted performance summary."""
    
    slow_tests = audit_db.get_slow_tests(threshold_seconds=0.5)
    hanging_tests = audit_db.get_hanging_tests()
    
    print("\n" + "="*80)
    print("TEST PERFORMANCE AUDIT REPORT")
    print("="*80)
    
    if hanging_tests:
        print("\n🚨 HANGING/ERRORED TESTS (Needs Investigation):")
        print("-" * 80)
        for test in hanging_tests[:10]:
            print(f"  • {test['test_id']}")
            print(f"    Status: {test['status']}")
            if test['error_message']:
                print(f"    Error: {test['error_message'][:100]}...")
            print()
    
    if slow_tests:
        print("\n⏱️  SLOW TESTS (> 0.5 seconds):")
        print("-" * 80)
        for test in slow_tests[:15]:
            duration = test['duration_seconds']
            status = test['status']
            print(f"  {duration:6.3f}s  {status:8s}  {test['test_id']}")
    
    print("\n" + "="*80)


# ============================================================================
# CLI
# ============================================================================

def run_audited_tests(test_args: List[str], audit_db: Optional[TestAuditDB] = None):
    """Run tests with audit tracking."""
    import pytest
    from uuid import uuid4
    
    if audit_db is None:
        audit_db = TestAuditDB()
    
    logger = setup_audit_logger()
    session_id = f"session-{uuid4().hex[:12]}"
    plugin = TestPerformancePlugin(audit_db, logger, session_id)
    
    print(f"🔍 Running tests with performance audit (Session: {session_id})")
    print(f"📊 Audit log: {logger.handlers[0].baseFilename}")
    print(f"💾 Database: {audit_db.db_path}")
    
    # Run pytest with plugin
    exit_code = pytest.main(test_args + ["-p", "no:cacheprovider"])
    
    # Generate report
    print("\n📈 Generating performance report...")
    print_performance_summary(audit_db)
    generate_performance_report(audit_db)
    
    return exit_code


def main():
    """Main CLI entry point."""
    import argparse
from cortex.models.canonical_enums import TestStatus
    
    parser = argparse.ArgumentParser(
        description="Enterprise Test Performance Auditor"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run tests with audit tracking")
    run_parser.add_argument(
        "test_args",
        nargs="*",
        default=["tests/"],
        help="Arguments to pass to pytest"
    )
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate performance report")
    report_parser.add_argument(
        "--db",
        type=Path,
        help="Path to audit database"
    )
    report_parser.add_argument(
        "--output",
        type=Path,
        help="Output file for report"
    )
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze test performance")
    analyze_parser.add_argument(
        "--threshold-seconds",
        type=float,
        default=0.5,
        help="Threshold for slow test detection (default: 0.5s)"
    )
    analyze_parser.add_argument(
        "--db",
        type=Path,
        help="Path to audit database"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    audit_db = TestAuditDB(args.db if hasattr(args, 'db') else None)
    
    if args.command == "run":
        return run_audited_tests(args.test_args, audit_db)
    
    elif args.command == "report":
        print("📊 Generating performance report...")
        report = generate_performance_report(audit_db, args.output)
        print(f"✅ Report generated: {report}")
        return 0
    
    elif args.command == "analyze":
        print(f"🔍 Analyzing tests (threshold: {args.threshold_seconds}s)...")
        slow_tests = audit_db.get_slow_tests(args.threshold_seconds)
        
        print(f"\n📈 Found {len(slow_tests)} slow tests:")
        for test in slow_tests[:20]:
            print(f"  {test['duration_seconds']:6.3f}s  {test['test_id']}")
        
        return 0
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
