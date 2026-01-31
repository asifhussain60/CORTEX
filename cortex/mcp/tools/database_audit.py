"""
Database Audit MCP Tool.

Exposes SQLite database integrity checks as MCP tool for SaaS deployment.

MCP Tools:
- cortex_db_audit: SQLite integrity audit (orphan tables, duplicates, stale data)

Author: Asif Hussain
AC-ID: ARCH-012
ARCH-007: MCP-first architecture enforcement
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from cortex.mcp.decorators import mcp_tool


@mcp_tool(
    name="cortex_db_audit",
    description="Audit SQLite databases for integrity: orphan tables, duplicate data, stale caches",
    parameters={
        "db_path": "string",
        "check_orphans": "boolean",
        "check_duplicates": "boolean",
        "check_stale": "boolean",
        "stale_days": "integer",
    }
)
def cortex_db_audit(
    db_path: str = "cortex_brain/state/governance.db",
    check_orphans: bool = True,
    check_duplicates: bool = True,
    check_stale: bool = True,
    stale_days: int = 30,
) -> Dict[str, Any]:
    """
    Audit SQLite database for integrity issues.
    
    Checks for:
    - Orphan tables (not referenced by any code)
    - Duplicate data patterns
    - Stale data older than threshold
    
    Args:
        db_path: Path to SQLite database file
        check_orphans: Check for orphan/unused tables
        check_duplicates: Check for duplicate rows
        check_stale: Check for stale data
        stale_days: Days threshold for stale data
        
    Returns:
        Dict with audit results: tables, issues, recommendations
    """
    db_file = Path(db_path)
    
    if not db_file.exists():
        return {
            "status": "success",
            "db_path": str(db_path),
            "exists": False,
            "message": "Database file not found - clean state",
            "issues": [],
            "recommendations": [],
        }
    
    try:
        conn = sqlite3.connect(str(db_file))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        results: Dict[str, Any] = {
            "status": "success",
            "db_path": str(db_path),
            "exists": True,
            "tables": [],
            "issues": [],
            "recommendations": [],
        }
        
        # Get all tables
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]
        
        for table_name in tables:
            table_info = _analyze_table(cursor, table_name, check_duplicates, check_stale, stale_days)
            results["tables"].append(table_info)
            
            # Collect issues
            if table_info.get("issues"):
                results["issues"].extend(table_info["issues"])
        
        # Check for orphan tables (known CORTEX tables)
        if check_orphans:
            orphan_issues = _check_orphan_tables(tables)
            results["issues"].extend(orphan_issues)
        
        # Generate recommendations
        results["recommendations"] = _generate_recommendations(results["issues"])
        
        # Summary
        results["summary"] = {
            "total_tables": len(tables),
            "total_issues": len(results["issues"]),
            "total_rows": sum(t.get("row_count", 0) for t in results["tables"]),
            "health": "healthy" if len(results["issues"]) == 0 else "needs_attention",
        }
        
        conn.close()
        return results
        
    except sqlite3.Error as e:
        return {
            "status": "error",
            "db_path": str(db_path),
            "error": str(e),
            "issues": [{"type": "connection_error", "message": str(e)}],
            "recommendations": ["Check database file integrity", "Verify file permissions"],
        }


def _analyze_table(
    cursor: sqlite3.Cursor,
    table_name: str,
    check_duplicates: bool,
    check_stale: bool,
    stale_days: int,
) -> Dict[str, Any]:
    """Analyze a single table for issues."""
    issues: List[Dict[str, Any]] = []
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    
    # Get column info
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    
    table_info = {
        "name": table_name,
        "row_count": row_count,
        "columns": columns,
        "issues": [],
    }
    
    # Skip system tables
    if table_name.startswith("sqlite_"):
        return table_info
    
    # Check for duplicates (if table has enough rows)
    if check_duplicates and row_count > 0:
        dup_issues = _check_duplicates(cursor, table_name, columns)
        issues.extend(dup_issues)
    
    # Check for stale data (if table has timestamp column)
    if check_stale and row_count > 0:
        stale_issues = _check_stale_data(cursor, table_name, columns, stale_days)
        issues.extend(stale_issues)
    
    table_info["issues"] = issues
    return table_info


def _check_duplicates(
    cursor: sqlite3.Cursor,
    table_name: str,
    columns: List[str],
) -> List[Dict[str, Any]]:
    """Check for duplicate rows in a table."""
    issues = []
    
    # Look for exact duplicates (excluding id columns)
    non_id_cols = [c for c in columns if not c.lower().endswith("id") and c.lower() != "id"]
    
    if len(non_id_cols) < 2:
        return issues
    
    col_list = ", ".join(non_id_cols)
    
    try:
        query = f"""
            SELECT {col_list}, COUNT(*) as cnt
            FROM {table_name}
            GROUP BY {col_list}
            HAVING cnt > 1
        """
        cursor.execute(query)
        duplicates = cursor.fetchall()
        
        if duplicates:
            issues.append({
                "type": "duplicate_rows",
                "table": table_name,
                "count": len(duplicates),
                "message": f"Found {len(duplicates)} duplicate row patterns in {table_name}",
            })
    except sqlite3.Error:
        pass  # Skip if query fails (e.g., incompatible column types)
    
    return issues


def _check_stale_data(
    cursor: sqlite3.Cursor,
    table_name: str,
    columns: List[str],
    stale_days: int,
) -> List[Dict[str, Any]]:
    """Check for stale data older than threshold."""
    issues = []
    
    # Look for timestamp columns
    timestamp_cols = [
        c for c in columns
        if any(ts in c.lower() for ts in ["timestamp", "created", "updated", "date", "time"])
    ]
    
    if not timestamp_cols:
        return issues
    
    cutoff_date = (datetime.now() - timedelta(days=stale_days)).isoformat()
    
    for ts_col in timestamp_cols:
        try:
            query = f"""
                SELECT COUNT(*) FROM {table_name}
                WHERE {ts_col} < ?
            """
            cursor.execute(query, (cutoff_date,))
            stale_count = cursor.fetchone()[0]
            
            if stale_count > 0:
                issues.append({
                    "type": "stale_data",
                    "table": table_name,
                    "column": ts_col,
                    "count": stale_count,
                    "threshold_days": stale_days,
                    "message": f"Found {stale_count} rows older than {stale_days} days in {table_name}.{ts_col}",
                })
        except sqlite3.Error:
            pass  # Skip if query fails (e.g., non-date format)
    
    return issues


def _check_orphan_tables(tables: List[str]) -> List[Dict[str, Any]]:
    """Check for tables not in the known CORTEX schema."""
    issues = []
    
    # Known CORTEX tables
    known_tables = {
        "audit_log",
        "governance_audit_trail",
        "governance_audit_trail_archive",
        "operation_logs",
        "wiring_status_history",
        "component_health_snapshots",
        "sqlite_sequence",  # System table
    }
    
    for table in tables:
        if table not in known_tables and not table.startswith("sqlite_"):
            issues.append({
                "type": "orphan_table",
                "table": table,
                "message": f"Unknown table '{table}' not in CORTEX schema - potential orphan",
            })
    
    return issues


def _generate_recommendations(issues: List[Dict[str, Any]]) -> List[str]:
    """Generate recommendations based on issues found."""
    recommendations = []
    
    issue_types = {issue.get("type") for issue in issues}
    
    if "duplicate_rows" in issue_types:
        recommendations.append("Run deduplication: DELETE duplicates keeping latest entry")
    
    if "stale_data" in issue_types:
        recommendations.append("Run log rotation: python -m cortex.infrastructure.database_log_rotation")
    
    if "orphan_table" in issue_types:
        recommendations.append("Review orphan tables and DROP if unused after code verification")
    
    if not issues:
        recommendations.append("Database is healthy - no action required")
    
    return recommendations
