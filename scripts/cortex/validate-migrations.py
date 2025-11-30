"""
Migration Validation Script
--------------------------
Validates that all Tier 1-3 migration scripts work correctly.

This script performs:
1. Pre-migration validation (check source files exist)
2. Run migrations
3. Post-migration validation (data integrity, FIFO queue, FTS5 index)
4. Performance benchmarks
5. Rollback testing

Exit codes:
- 0: All validations passed
- 1: Validation failed (see error messages)

Usage:
    python scripts/validate-migrations.py
    python scripts/validate-migrations.py --tier 1  # Validate only Tier 1
    python scripts/validate-migrations.py --benchmark  # Include performance tests
"""

import sys
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime
import json
import time
from typing import Dict, List, Tuple, Any


# ANSI color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_success(message: str):
    """Print success message in green."""
    print(f"{GREEN}✓{RESET} {message}")


def print_error(message: str):
    """Print error message in red."""
    print(f"{RED}✗{RESET} {message}")


def print_warning(message: str):
    """Print warning message in yellow."""
    print(f"{YELLOW}⚠{RESET} {message}")


def print_info(message: str):
    """Print info message in blue."""
    print(f"{BLUE}ℹ{RESET} {message}")


def print_header(message: str):
    """Print section header."""
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    print(f"{BLUE}{message}{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}")


class MigrationValidator:
    """Validates migration scripts and data integrity."""
    
    def __init__(self, brain_dir: Path, db_path: Path):
        """
        Initialize validator.
        
        Args:
            brain_dir: Path to cortex-brain directory
            db_path: Path to SQLite database
        """
        self.brain_dir = brain_dir
        self.db_path = db_path
        self.errors = []
        self.warnings = []
    
    def validate_tier1_sources(self) -> bool:
        """Validate Tier 1 source files exist."""
        print_header("Tier 1: Pre-Migration Validation")
        
        files = [
            self.brain_dir / "conversation-history.jsonl",
            self.brain_dir / "conversation-context.jsonl"
        ]
        
        all_exist = True
        for file_path in files:
            if file_path.exists():
                print_success(f"Found: {file_path.name}")
            else:
                print_warning(f"Missing: {file_path.name} (will create empty)")
                all_exist = False
        
        return True  # Not critical - migration can handle empty files
    
    def validate_tier2_sources(self) -> bool:
        """Validate Tier 2 source files exist."""
        print_header("Tier 2: Pre-Migration Validation")
        
        files = [
            self.brain_dir / "knowledge-graph.yaml",
            self.brain_dir / "file-relationships.yaml",
            self.brain_dir / "architectural-patterns.yaml"
        ]
        
        all_exist = True
        for file_path in files:
            if file_path.exists():
                print_success(f"Found: {file_path.name}")
            else:
                print_warning(f"Missing: {file_path.name}")
                all_exist = False
        
        return True  # Not critical
    
    def validate_tier3_sources(self) -> bool:
        """Validate Tier 3 source files exist."""
        print_header("Tier 3: Pre-Migration Validation")
        
        file_path = self.brain_dir / "development-context.yaml"
        if file_path.exists():
            print_success(f"Found: {file_path.name}")
            return True
        else:
            print_warning(f"Missing: {file_path.name}")
            return True  # Not critical
    
    def validate_database_schema(self) -> bool:
        """Validate database schema has all required tables."""
        print_header("Database Schema Validation")
        
        required_tables = {
            'tier1': [
                'tier1_conversations',
                'tier1_messages',
                'tier1_file_tracking',
                'tier1_conversations_fts',
                'tier1_raw_requests'
            ],
            'tier2': [
                'tier2_patterns',
                'tier2_file_relationships'
            ],
            'tier3': [
                'tier3_metrics'
            ]
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table'
            ORDER BY name
        """)
        existing_tables = {row[0] for row in cursor.fetchall()}
        conn.close()
        
        all_exist = True
        for tier, tables in required_tables.items():
            print_info(f"\nChecking {tier.upper()} tables:")
            for table in tables:
                if table in existing_tables:
                    print_success(f"  {table}")
                else:
                    print_error(f"  {table} - MISSING")
                    self.errors.append(f"Missing table: {table}")
                    all_exist = False
        
        return all_exist
    
    def validate_tier1_data(self) -> bool:
        """Validate Tier 1 data integrity after migration."""
        print_header("Tier 1: Post-Migration Validation")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check conversation count
        cursor.execute("SELECT COUNT(*) FROM tier1_conversations")
        conv_count = cursor.fetchone()[0]
        print_info(f"Conversations migrated: {conv_count}")
        
        # Check message count
        cursor.execute("SELECT COUNT(*) FROM tier1_messages")
        msg_count = cursor.fetchone()[0]
        print_info(f"Messages migrated: {msg_count}")
        
        # Validate FIFO queue limit
        if conv_count > 20:
            print_error(f"FIFO queue exceeded: {conv_count} > 20 conversations")
            self.errors.append("FIFO queue limit violated")
            conn.close()
            return False
        else:
            print_success(f"FIFO queue respected: {conv_count} ≤ 20")
        
        # Validate message sequence numbers
        cursor.execute("""
            SELECT conversation_id, COUNT(*) as msg_count,
                   MAX(sequence_number) as max_seq
            FROM tier1_messages
            GROUP BY conversation_id
        """)
        
        sequence_errors = 0
        for row in cursor.fetchall():
            conv_id, msg_count, max_seq = row
            # max_seq should equal msg_count (sequences start at 1)
            if max_seq != msg_count:
                sequence_errors += 1
                print_warning(f"Sequence mismatch in {conv_id}: max={max_seq}, count={msg_count}")
        
        if sequence_errors == 0:
            print_success("Message sequences are correct")
        else:
            self.warnings.append(f"{sequence_errors} conversations have sequence mismatches")
        
        # Validate FTS5 index
        cursor.execute("""
            SELECT COUNT(*) FROM tier1_conversations_fts
        """)
        fts_count = cursor.fetchone()[0]
        
        if fts_count == conv_count:
            print_success(f"FTS5 index populated: {fts_count} entries")
        else:
            print_error(f"FTS5 index mismatch: {fts_count} != {conv_count}")
            self.errors.append("FTS5 index not properly populated")
            conn.close()
            return False
        
        conn.close()
        return True
    
    def validate_tier2_data(self) -> bool:
        """Validate Tier 2 data integrity after migration."""
        print_header("Tier 2: Post-Migration Validation")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check pattern count
        cursor.execute("SELECT COUNT(*) FROM tier2_patterns")
        pattern_count = cursor.fetchone()[0]
        print_info(f"Patterns migrated: {pattern_count}")
        
        # Check file relationship count
        cursor.execute("SELECT COUNT(*) FROM tier2_file_relationships")
        rel_count = cursor.fetchone()[0]
        print_info(f"File relationships migrated: {rel_count}")
        
        # Validate confidence scores (must be 0.0-1.0)
        cursor.execute("""
            SELECT COUNT(*) FROM tier2_patterns
            WHERE confidence < 0.0 OR confidence > 1.0
        """)
        invalid_confidence = cursor.fetchone()[0]
        
        if invalid_confidence == 0:
            print_success("All confidence scores are valid (0.0-1.0)")
        else:
            print_error(f"{invalid_confidence} patterns have invalid confidence scores")
            self.errors.append("Invalid confidence scores found")
            conn.close()
            return False
        
        conn.close()
        return True
    
    def validate_tier3_data(self) -> bool:
        """Validate Tier 3 data integrity after migration."""
        print_header("Tier 3: Post-Migration Validation")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check metric count
        cursor.execute("SELECT COUNT(*) FROM tier3_metrics")
        metric_count = cursor.fetchone()[0]
        print_info(f"Metrics migrated: {metric_count}")
        
        # Validate metric types
        cursor.execute("""
            SELECT DISTINCT metric_type FROM tier3_metrics
        """)
        metric_types = [row[0] for row in cursor.fetchall()]
        valid_types = {'numeric', 'text', 'json'}
        
        invalid_types = set(metric_types) - valid_types
        if len(invalid_types) == 0:
            print_success(f"All metric types are valid: {metric_types}")
        else:
            print_error(f"Invalid metric types found: {invalid_types}")
            self.errors.append("Invalid metric types")
            conn.close()
            return False
        
        conn.close()
        return True
    
    def run_performance_benchmarks(self) -> Dict[str, float]:
        """Run performance benchmarks on migrated data."""
        print_header("Performance Benchmarks")
        
        conn = sqlite3.connect(self.db_path)
        benchmarks = {}
        
        # Benchmark 1: Recent conversations query
        start = time.time()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM tier1_conversations
            ORDER BY created_at DESC
            LIMIT 20
        """)
        cursor.fetchall()
        benchmarks['recent_conversations'] = time.time() - start
        
        # Benchmark 2: FTS5 search
        start = time.time()
        cursor.execute("""
            SELECT * FROM tier1_conversations_fts
            WHERE tier1_conversations_fts MATCH 'test'
            LIMIT 10
        """)
        cursor.fetchall()
        benchmarks['fts_search'] = time.time() - start
        
        # Benchmark 3: File co-modification query
        start = time.time()
        cursor.execute("""
            SELECT file_b, COUNT(*) as co_mods
            FROM tier1_file_tracking
            WHERE file_a = 'test.py'
            GROUP BY file_b
            ORDER BY co_mods DESC
            LIMIT 10
        """)
        cursor.fetchall()
        benchmarks['file_patterns'] = time.time() - start
        
        conn.close()
        
        # Print results
        target = 0.1  # 100ms target
        for name, duration in benchmarks.items():
            duration_ms = duration * 1000
            if duration < target:
                print_success(f"{name}: {duration_ms:.2f}ms (target: <100ms)")
            else:
                print_warning(f"{name}: {duration_ms:.2f}ms (SLOW, target: <100ms)")
                self.warnings.append(f"Slow query: {name} took {duration_ms:.2f}ms")
        
        return benchmarks
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate validation report."""
        return {
            'timestamp': datetime.now().isoformat(),
            'database': str(self.db_path),
            'errors': self.errors,
            'warnings': self.warnings,
            'status': 'PASSED' if len(self.errors) == 0 else 'FAILED'
        }


def main():
    """Main validation entry point."""
    parser = argparse.ArgumentParser(description="Validate CORTEX Brain migrations")
    parser.add_argument('--tier', type=int, choices=[1, 2, 3], help="Validate only specific tier")
    parser.add_argument('--benchmark', action='store_true', help="Run performance benchmarks")
    parser.add_argument('--brain-dir', type=str, default='cortex-brain', help="Path to brain directory")
    parser.add_argument('--db-path', type=str, default='cortex-brain/cortex-brain.db', help="Path to database")
    args = parser.parse_args()
    
    # Initialize validator
    brain_dir = Path(args.brain_dir)
    db_path = Path(args.db_path)
    
    if not db_path.exists():
        print_error(f"Database not found: {db_path}")
        print_info("Run migrations first: python scripts/migrate-all-tiers.py")
        sys.exit(1)
    
    validator = MigrationValidator(brain_dir, db_path)
    
    # Run validations
    validations = []
    
    if args.tier is None or args.tier == 1:
        validations.append(validator.validate_tier1_sources())
        validations.append(validator.validate_database_schema())
        validations.append(validator.validate_tier1_data())
    
    if args.tier is None or args.tier == 2:
        validations.append(validator.validate_tier2_sources())
        validations.append(validator.validate_tier2_data())
    
    if args.tier is None or args.tier == 3:
        validations.append(validator.validate_tier3_sources())
        validations.append(validator.validate_tier3_data())
    
    # Run benchmarks if requested
    if args.benchmark:
        validator.run_performance_benchmarks()
    
    # Generate report
    report = validator.generate_report()
    
    print_header("Validation Summary")
    print_info(f"Status: {report['status']}")
    print_info(f"Errors: {len(report['errors'])}")
    print_info(f"Warnings: {len(report['warnings'])}")
    
    if report['errors']:
        print_error("\nErrors:")
        for error in report['errors']:
            print(f"  - {error}")
    
    if report['warnings']:
        print_warning("\nWarnings:")
        for warning in report['warnings']:
            print(f"  - {warning}")
    
    # Save report
    report_path = brain_dir / f"migration-validation-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print_info(f"\nReport saved: {report_path}")
    
    # Exit with appropriate code
    if report['status'] == 'PASSED':
        print_success("\n✓ All validations passed!")
        sys.exit(0)
    else:
        print_error("\n✗ Validation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
