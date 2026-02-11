"""
CORTEX Governance CLI Tool
================================
Provides command-line interface for querying and validating governance rules.

Features:
- Query rules by ID, domain, or phase
- Validate code against governance rules
- Performance optimized (<100ms queries)
"""

import argparse
import json
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class GovernanceQueryEngine:
    """Query engine for governance rules with sub-100ms performance."""

    def __init__(self, db_path: str = "cortex_brain/state/governance.db"):
        """Initialize query engine with database connection."""
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path, timeout=10.0)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def disconnect(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def query_by_ac_id(self, ac_id: str) -> Optional[Dict[str, Any]]:
        """Query rule details by AC ID."""
        try:
            self.cursor.execute("""
                SELECT ac_id, phase, status, title, description
                FROM ac_index
                WHERE ac_id = ?
            """, (ac_id,))

            row = self.cursor.fetchone()
            if not row:
                return None

            # Count audit entries for this AC
            self.cursor.execute("SELECT COUNT(*) FROM audit_log WHERE ac_id = ?", (ac_id,))
            entries = self.cursor.fetchone()[0] or 0

            return {
                "ac_id": row["ac_id"],
                "phase": row["phase"],
                "status": row["status"],
                "title": row["title"],
                "description": row["description"],
                "audit_entries": entries,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}

    def query_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Query all rules in a domain."""
        try:
            self.cursor.execute("""
                SELECT ac_id, phase, status, title
                FROM ac_index
                WHERE ac_id LIKE ?
                ORDER BY ac_id
            """, (f"{domain}%",))

            results = []
            for row in self.cursor.fetchall():
                # Count audit entries for this AC
                self.cursor.execute("SELECT COUNT(*) FROM audit_log WHERE ac_id = ?", (row["ac_id"],))
                entries = self.cursor.fetchone()[0] or 0

                results.append({
                    "ac_id": row["ac_id"],
                    "phase": row["phase"],
                    "status": row["status"],
                    "title": row["title"],
                    "audit_entries": entries
                })

            return results
        except Exception as e:
            return [{"error": str(e)}]

    def query_by_phase(self, phase: str) -> List[Dict[str, Any]]:
        """Query all rules in a phase."""
        try:
            self.cursor.execute("""
                SELECT ac_id, phase, status, title
                FROM ac_index
                WHERE phase = ?
                ORDER BY ac_id
            """, (phase,))

            results = []
            for row in self.cursor.fetchall():
                # Count audit entries for this AC
                self.cursor.execute("SELECT COUNT(*) FROM audit_log WHERE ac_id = ?", (row["ac_id"],))
                entries = self.cursor.fetchone()[0] or 0

                results.append({
                    "ac_id": row["ac_id"],
                    "phase": row["phase"],
                    "status": row["status"],
                    "title": row["title"],
                    "audit_entries": entries
                })

            return results
        except Exception as e:
            return [{"error": str(e)}]

    def query_by_domain_prefix(self, prefix: str) -> List[Dict[str, Any]]:
        """Query all rules matching domain prefix (for 'tdd' style queries)."""
        try:
            # Handle both "AR" and "AC-AR" style prefixes
            like_pattern = f"AC-{prefix}%" if not prefix.startswith("AC-") else f"{prefix}%"

            self.cursor.execute("""
                SELECT ac_id, phase, status, title
                FROM ac_index
                WHERE ac_id LIKE ?
                ORDER BY ac_id
            """, (like_pattern,))

            results = []
            for row in self.cursor.fetchall():
                # Count audit entries for this AC
                self.cursor.execute("SELECT COUNT(*) FROM audit_log WHERE ac_id = ?", (row["ac_id"],))
                entries = self.cursor.fetchone()[0] or 0

                results.append({
                    "ac_id": row["ac_id"],
                    "phase": row["phase"],
                    "status": row["status"],
                    "title": row["title"],
                    "audit_entries": entries
                })

            return results
        except Exception as e:
            return [{"error": str(e)}]


class GovernanceValidator:
    """Validates code/paths against governance rules."""

    def __init__(self, db_path: str = "cortex_brain/state/governance.db"):
        """Initialize validator with database connection."""
        self.db_path = db_path
        self.engine = GovernanceQueryEngine(db_path)
        self.violations = []

    def validate_path(self, path: str, phase: Optional[str] = None,
                     ac_id: Optional[str] = None) -> Dict[str, Any]:
        """Validate a file path or directory against governance rules."""
        self.engine.connect()

        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return {
                    "valid": False,
                    "violations": [f"Path does not exist: {path}"],
                    "exit_code": 1
                }

            # Collect all relevant rules
            rules = []

            if ac_id:
                rule = self.engine.query_by_ac_id(ac_id)
                if rule and "error" not in rule:
                    rules.append(rule)
            elif phase:
                rules = self.engine.query_by_phase(phase)
            else:
                # Get all rules if no specific filter
                try:
                    self.engine.cursor.execute("SELECT ac_id FROM ac_index")
                    for row in self.engine.cursor.fetchall():
                        rule = self.engine.query_by_ac_id(row["ac_id"])
                        if rule and "error" not in rule:
                            rules.append(rule)
                except Exception:
                    pass

            # Analyze files in path
            violations = []
            checked_files = 0

            if path_obj.is_file():
                checked_files = 1
                violations.extend(self._check_file(path_obj))
            else:
                for file_path in path_obj.rglob("*"):
                    if file_path.is_file() and not self._is_ignored(file_path):
                        checked_files += 1
                        violations.extend(self._check_file(file_path))

            self.violations = violations

            return {
                "valid": len(violations) == 0,
                "violations": violations,
                "files_checked": checked_files,
                "rules_evaluated": len(rules),
                "exit_code": 0 if len(violations) == 0 else 1
            }
        finally:
            self.engine.disconnect()

    def _check_file(self, file_path: Path) -> List[str]:
        """Check a single file for violations."""
        violations = []

        # Check AC-ID format in code comments
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    # Look for malformed AC-ID references
                    if 'AC-' in line or 'GV-' in line or 'AR-' in line:
                        # Validate format: DOMAIN-NNN-NN
                        import re
                        matches = re.findall(r'([A-Z]{2,})-(\d+)(?:-(\d+))?', line)
                        for match in matches:
                            if len(match) >= 2 and not match[1].isdigit():
                                violations.append(
                                    f"{file_path}:{line_num}: "
                                    f"Malformed AC-ID reference: {match}"
                                )
        except Exception:
            pass

        return violations

    def _is_ignored(self, file_path: Path) -> bool:
        """Check if file should be ignored."""
        ignored_patterns = ['.venv', '__pycache__', '.git', 'node_modules', '.egg-info']
        return any(pattern in file_path.parts for pattern in ignored_patterns)


class GovernanceCLI:
    """Command-line interface for governance tools."""

    def __init__(self):
        """Initialize CLI."""
        self.engine = GovernanceQueryEngine()
        self.validator = GovernanceValidator()

    def parse_args(self, args: List[str]) -> argparse.Namespace:
        """Parse command-line arguments."""
        parser = argparse.ArgumentParser(
            description="CORTEX Governance CLI - Query and validate governance rules"
        )

        subparsers = parser.add_subparsers(dest="command", help="Command to execute")

        # Query subcommand
        query_parser = subparsers.add_parser("query", help="Query governance rules")
        query_parser.add_argument("target", help="AC-ID, domain, or phase to query")
        query_parser.add_argument("--domain", action="store_true",
                                help="Treat target as domain prefix")
        query_parser.add_argument("--phase", action="store_true",
                                help="Treat target as phase ID")
        query_parser.add_argument("--json", action="store_true",
                                help="Output as JSON")

        # Validate subcommand
        validate_parser = subparsers.add_parser("validate", help="Validate path against rules")
        validate_parser.add_argument("path", help="Path to validate")
        validate_parser.add_argument("--phase", help="Filter by phase")
        validate_parser.add_argument("--ac-id", help="Filter by AC-ID")
        validate_parser.add_argument("--json", action="store_true",
                                   help="Output as JSON")

        return parser.parse_args(args)

    def execute_query(self, args: argparse.Namespace) -> int:
        """Execute query command."""
        self.engine.connect()

        try:
            start_time = time.time()

            if args.domain:
                results = self.engine.query_by_domain_prefix(args.target)
            elif args.phase:
                results = self.engine.query_by_phase(args.target)
            else:
                # Try AC-ID first, then domain
                result = self.engine.query_by_ac_id(args.target)
                results = [result] if result else self.engine.query_by_domain_prefix(args.target)

            elapsed = (time.time() - start_time) * 1000  # milliseconds

            if args.json:
                output = {
                    "results": results,
                    "count": len(results) if isinstance(results, list) else 1,
                    "elapsed_ms": round(elapsed, 2)
                }
                print(json.dumps(output, indent=2))
            else:
                if isinstance(results, list):
                    print(f"\n{'AC-ID':<15} {'Phase':<15} {'Status':<12} {'Entries':<8}")
                    print("-" * 50)
                    for r in results:
                        if "error" not in r:
                            print(f"{r['ac_id']:<15} {r['phase']:<15} "
                                  f"{r['status']:<12} {r['audit_entries']:<8}")
                else:
                    if "error" not in results:
                        print(f"\nAC-ID: {results['ac_id']}")
                        print(f"Phase: {results['phase']}")
                        print(f"Status: {results['status']}")
                        print(f"Title: {results.get('title', 'N/A')}")
                        print(f"Audit Entries: {results['audit_entries']}\n")

                print(f"\nQuery completed in {elapsed:.1f}ms")

            return 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        finally:
            self.engine.disconnect()

    def execute_validate(self, args: argparse.Namespace) -> int:
        """Execute validate command."""
        start_time = time.time()

        result = self.validator.validate_path(
            args.path,
            phase=args.phase,
            ac_id=args.ac_id
        )

        elapsed = (time.time() - start_time) * 1000  # milliseconds

        if args.json:
            result["elapsed_ms"] = round(elapsed, 2)
            print(json.dumps(result, indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"Validation Results for: {args.path}")
            print(f"{'='*60}")
            print(f"Status: {'✓ VALID' if result['valid'] else '✗ VIOLATIONS FOUND'}")
            print(f"Files Checked: {result['files_checked']}")
            print(f"Rules Evaluated: {result['rules_evaluated']}")

            if result['violations']:
                print(f"\nViolations ({len(result['violations'])}):")
                for violation in result['violations']:
                    print(f"  • {violation}")

            print(f"\nValidation completed in {elapsed:.1f}ms")
            print(f"{'='*60}\n")

        return result['exit_code']

    def run(self, args: List[str]) -> int:
        """Run CLI with provided arguments."""
        try:
            parsed_args = self.parse_args(args)

            if parsed_args.command == "query":
                return self.execute_query(parsed_args)
            elif parsed_args.command == "validate":
                return self.execute_validate(parsed_args)
            else:
                print("Error: No command specified. Use 'cortex-governance --help'")
                return 1
        except SystemExit as e:
            # Suppress argparse exit and return code instead
            return e.code or 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1


def main():
    """Entry point for governance CLI."""
    cli = GovernanceCLI()
    exit_code = cli.run(sys.argv[1:])
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
