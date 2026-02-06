#!/usr/bin/env python3
"""
Context Efficiency Audit Runner (ENH-046 Phase 1.6)

Purpose: Execute SQL audit queries against governance.db for evidence-based validation
Usage: python cortex/governance/audit_context_efficiency.py [--query QUERY_NUM] [--period DAYS]

Author: CORTEX Architect
Date: 2026-02-06
"""

import argparse
import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json


class ContextEfficiencyAuditor:
    """Executes context efficiency audits against governance.db"""
    
    def __init__(self, db_path: Path):
        """
        Initialize auditor with database path
        
        Args:
            db_path: Path to governance.db
        """
        self.db_path = db_path
        if not db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")
        
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
    
    def run_query(self, query_name: str, period_days: int = 7) -> List[Dict[str, Any]]:
        """
        Execute a named query from context_efficiency_audit.sql
        
        Args:
            query_name: Name of query (e.g., "budget_violations")
            period_days: Number of days to look back
        
        Returns:
            List of result rows as dictionaries
        """
        sql_file = Path(__file__).parent / "sql" / "context_efficiency_audit.sql"
        if not sql_file.exists():
            raise FileNotFoundError(f"SQL file not found: {sql_file}")
        
        # Read SQL file and extract named query
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        
        # Query mapping
        queries = {
            "1": "-- Query 1: Context Synthesis Events",
            "2": "-- Query 2: Budget Violations",
            "3": "-- Query 3: Cache Performance Metrics",
            "4": "-- Query 4: Intent-Specific Token Consumption",
            "5": "-- Query 5: Synthesis Performance Distribution",
            "6": "-- Query 6: Hourly Synthesis Activity",
            "7": "-- Query 7: Summary Statistics"
        }
        
        if query_name not in queries:
            available = ", ".join(queries.keys())
            raise ValueError(f"Unknown query: {query_name}. Available: {available}")
        
        # Extract query by comment marker
        query_marker = queries[query_name]
        query_start = sql_content.find(query_marker)
        if query_start == -1:
            raise ValueError(f"Query not found in SQL file: {query_marker}")
        
        # Find next query marker or end of file
        query_end = len(sql_content)
        for next_marker in queries.values():
            if next_marker == query_marker:
                continue
            next_pos = sql_content.find(next_marker, query_start + 1)
            if next_pos != -1 and next_pos < query_end:
                query_end = next_pos
        
        # Extract query SQL (skip comment lines)
        query_lines = []
        for line in sql_content[query_start:query_end].split('\n'):
            if line.strip() and not line.strip().startswith('--'):
                query_lines.append(line)
        
        query_sql = '\n'.join(query_lines)
        
        # Execute query
        cursor = self.conn.cursor()
        cursor.execute(query_sql)
        
        # Convert rows to dictionaries
        results = []
        for row in cursor.fetchall():
            results.append(dict(row))
        
        return results
    
    def print_results(self, results: List[Dict[str, Any]], query_name: str):
        """
        Print query results in formatted table
        
        Args:
            results: Query results
            query_name: Name of query for header
        """
        if not results:
            print(f"⚠️  No results found for Query {query_name}")
            return
        
        print(f"\n{'═' * 80}")
        print(f"Query {query_name} Results ({len(results)} rows)")
        print(f"{'═' * 80}\n")
        
        # Print as table
        if results:
            headers = list(results[0].keys())
            
            # Calculate column widths
            col_widths = {}
            for header in headers:
                col_widths[header] = len(header)
                for row in results:
                    val_str = str(row[header]) if row[header] is not None else "NULL"
                    col_widths[header] = max(col_widths[header], len(val_str))
            
            # Print header
            header_line = " | ".join(h.ljust(col_widths[h]) for h in headers)
            print(header_line)
            print("-" * len(header_line))
            
            # Print rows
            for row in results:
                row_line = " | ".join(
                    str(row[h]).ljust(col_widths[h]) if row[h] is not None else "NULL".ljust(col_widths[h])
                    for h in headers
                )
                print(row_line)
        
        print(f"\n{'═' * 80}\n")
    
    def run_full_audit(self, period_days: int = 7) -> Dict[str, Any]:
        """
        Run all audit queries and generate comprehensive report
        
        Args:
            period_days: Number of days to look back
        
        Returns:
            Dictionary with audit results and health status
        """
        print(f"\n🔍 Running Context Efficiency Audit (ENH-046 Phase 1.6)")
        print(f"📊 Period: Last {period_days} days")
        print(f"🗄️  Database: {self.db_path}")
        print(f"⏰ Timestamp: {datetime.now().isoformat()}\n")
        
        audit_results = {}
        
        # Query 7: Summary Statistics (overall health)
        print("Running Query 7: Summary Statistics...")
        summary = self.run_query("7", period_days)
        if summary:
            audit_results["summary"] = summary[0]
            self.print_results(summary, "7")
        
        # Query 2: Budget Violations
        print("Running Query 2: Budget Violations...")
        violations = self.run_query("2", period_days)
        audit_results["violations"] = violations
        self.print_results(violations, "2")
        
        # Query 3: Cache Performance
        print("Running Query 3: Cache Performance Metrics...")
        cache_perf = self.run_query("3", period_days)
        audit_results["cache_performance"] = cache_perf
        self.print_results(cache_perf, "3")
        
        # Query 4: Intent Analysis
        print("Running Query 4: Intent-Specific Token Consumption...")
        intent_analysis = self.run_query("4", period_days)
        audit_results["intent_analysis"] = intent_analysis
        self.print_results(intent_analysis, "4")
        
        # Determine health status
        health_status = self._calculate_health_status(audit_results)
        audit_results["health_status"] = health_status
        
        # Print final verdict
        self._print_verdict(health_status)
        
        return audit_results
    
    def _calculate_health_status(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall health status from audit results"""
        summary = results.get("summary", {})
        violations = results.get("violations", [])
        
        status = {
            "overall": "PASS",
            "issues": []
        }
        
        # Check budget compliance
        avg_initial = summary.get("avg_initial_tokens", 0)
        if avg_initial and avg_initial > 250:
            status["overall"] = "FAIL"
            status["issues"].append(f"Initial load avg ({avg_initial}) > 250 tokens")
        
        avg_incremental = summary.get("avg_incremental_tokens", 0)
        if avg_incremental and avg_incremental > 500:
            status["overall"] = "FAIL"
            status["issues"].append(f"Incremental load avg ({avg_incremental}) > 500 tokens")
        
        # Check violation counts
        session_violations = summary.get("session_budget_violations", 0)
        if session_violations and session_violations > 0:
            if status["overall"] == "PASS":
                status["overall"] = "DEGRADED"
            status["issues"].append(f"{session_violations} session budget violations detected")
        
        # Check cache hit rate
        cache_hit_rate = summary.get("overall_cache_hit_rate_pct", 0)
        if cache_hit_rate and cache_hit_rate < 70:
            if status["overall"] == "PASS":
                status["overall"] = "DEGRADED"
            status["issues"].append(f"Cache hit rate ({cache_hit_rate:.1f}%) < 70% target")
        
        return status
    
    def _print_verdict(self, health_status: Dict[str, Any]):
        """Print final audit verdict"""
        print(f"\n{'═' * 80}")
        print("AUDIT VERDICT")
        print(f"{'═' * 80}\n")
        
        status = health_status["overall"]
        if status == "PASS":
            print("✅ Status: PASS - Context efficiency within targets")
        elif status == "DEGRADED":
            print("🟡 Status: DEGRADED - Some metrics below target")
        else:
            print("❌ Status: FAIL - Critical budget violations detected")
        
        issues = health_status.get("issues", [])
        if issues:
            print(f"\n📋 Issues Detected ({len(issues)}):")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("\n🎉 No issues detected - all metrics within targets!")
        
        print(f"\n{'═' * 80}\n")
    
    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Context Efficiency Audit Runner (ENH-046 Phase 1.6)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full audit (last 7 days)
  python cortex/governance/audit_context_efficiency.py
  
  # Run specific query
  python cortex/governance/audit_context_efficiency.py --query 2
  
  # Run audit for last 24 hours
  python cortex/governance/audit_context_efficiency.py --period 1
  
  # Run specific query for last 24 hours
  python cortex/governance/audit_context_efficiency.py --query 3 --period 1
        """
    )
    
    parser.add_argument(
        "--query",
        type=str,
        help="Run specific query (1-7). If omitted, runs full audit."
    )
    
    parser.add_argument(
        "--period",
        type=int,
        default=7,
        help="Number of days to look back (default: 7)"
    )
    
    parser.add_argument(
        "--db",
        type=str,
        default="cortex_brain/state/governance.db",
        help="Path to governance.db (default: cortex_brain/state/governance.db)"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of table"
    )
    
    args = parser.parse_args()
    
    # Find database
    db_path = Path(args.db)
    if not db_path.is_absolute():
        # Try relative to current directory first
        if not db_path.exists():
            # Try relative to script directory
            script_dir = Path(__file__).parent.parent.parent
            db_path = script_dir / args.db
    
    if not db_path.exists():
        print(f"❌ Error: Database not found: {db_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        auditor = ContextEfficiencyAuditor(db_path)
        
        if args.query:
            # Run specific query
            results = auditor.run_query(args.query, args.period)
            if args.json:
                print(json.dumps(results, indent=2, default=str))
            else:
                auditor.print_results(results, args.query)
        else:
            # Run full audit
            results = auditor.run_full_audit(args.period)
            if args.json:
                print(json.dumps(results, indent=2, default=str))
        
        auditor.close()
        
        # Exit with error code if audit failed
        if not args.query:
            health = results.get("health_status", {})
            if health.get("overall") == "FAIL":
                sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
