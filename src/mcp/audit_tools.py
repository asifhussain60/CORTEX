"""
CORTEX 6.0 MCP Audit Tools

Implements AC-AUDIT-004: MCP tools for audit query, list, and export.

Tools:
- audit_query: Query audit logs with filters
- audit_list: Paginated list view
- audit_export: Export logs to jsonl/csv/json formats

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import csv
from pathlib import Path
from typing import Dict, Any, Optional, List

from src.orchestrators.audit_logger import (
    AuditLevel,
    AuditCategory
)
from src.mcp.mcp_decorator import mcp_tool


@mcp_tool(
    name="cortex_audit_query",
    description="Query CORTEX audit logs with filters (ac_id, component, level, category, time range)",
    category="audit",
    orchestrator_id="audit_orchestrator",
    parameters={
        "db_path": {
            "type": "string",
            "required": True,
            "description": "Path to audit database (governance.db)"
        },
        "filters": {
            "type": "object",
            "required": False,
            "description": "Query filters: ac_id, component, level (INFO/WARNING/ERROR), category, start_time, end_time"
        }
    },
    returns={
        "type": "object",
        "description": "Query result with success, entries list, and count"
    },
    metadata={
        "tags": ["audit", "logging", "debugging", "traceability"],
        "version": "1.0",
        "priority": "P0"
    }
)
def audit_query(
    db_path: str,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Query audit logs via MCP with filters.
    
    Implements AC-AUDIT-004: audit_query MCP tool.
    
    Args:
        db_path: Path to audit database
        filters: Query filters (ac_id, component, level, etc.)
    
    Returns:
        Query result with success status and entries
    """
    try:
        storage = AuditStorage(Path(db_path))
        filters = filters or {}
        
        # Convert string level to enum if present
        if 'level' in filters and isinstance(filters['level'], str):
            filters['level'] = AuditLevel(filters['level'])
        
        # Convert string category to enum if present
        if 'category' in filters and isinstance(filters['category'], str):
            filters['category'] = AuditCategory(filters['category'])
        
        entries = storage.query(**filters)
        
        return {
            "success": True,
            "entries": entries,
            "count": len(entries)
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "entries": []
        }


@mcp_tool(
    name="cortex_audit_list",
    description="Paginated list view of audit logs with sorting",
    category="audit",
    parameters={
        "db_path": {"type": "string", "required": True, "description": "Path to audit database"},
        "page": {"type": "integer", "required": False, "description": "Page number (1-indexed)"},
        "page_size": {"type": "integer", "required": False, "description": "Results per page"},
        "order_by": {"type": "string", "required": False, "description": "Order by field"},
        "order_dir": {"type": "string", "required": False, "description": "Order direction (ASC/DESC)"}
    },
    metadata={"tags": ["audit", "pagination"]}
)
def audit_list(
    db_path: str,
    page: int = 1,
    page_size: int = 100,
    order_by: str = "timestamp",
    order_dir: str = "DESC"
) -> Dict[str, Any]:
    """
    Paginated list view of audit logs.
    
    Implements AC-AUDIT-004: audit_list MCP tool.
    
    Args:
        db_path: Path to audit database
        page: Page number (1-indexed)
        page_size: Results per page
        order_by: Order by field
        order_dir: Order direction (ASC/DESC)
    
    Returns:
        Paginated list with metadata
    """
    try:
        storage = AuditStorage(Path(db_path))
        
        entries = storage.query(
            page=page,
            page_size=page_size,
            order_by=order_by,
            order_dir=order_dir
        )
        
        total_count = storage.count()
        total_pages = (total_count + page_size - 1) // page_size
        
        return {
            "success": True,
            "entries": entries,
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "entries": []
        }


@mcp_tool(
    name="cortex_audit_export",
    description="Export audit logs to file (jsonl, csv, or json format)",
    category="audit",
    parameters={
        "db_path": {"type": "string", "required": True, "description": "Path to audit database"},
        "output_path": {"type": "string", "required": True, "description": "Output file path"},
        "format": {"type": "string", "required": False, "description": "Export format (jsonl/csv/json)"},
        "filters": {"type": "object", "required": False, "description": "Query filters"}
    },
    metadata={"tags": ["audit", "export", "reporting"]}
)
def audit_export(
    db_path: str,
    output_path: str,
    format: str = "jsonl",
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Export audit logs to file.
    
    Implements AC-AUDIT-004: audit_export MCP tool.
    
    Args:
        db_path: Path to audit database
        output_path: Output file path
        format: Export format (jsonl, csv, json)
        filters: Optional query filters
    
    Returns:
        Export result with success status
    """
    try:
        storage = AuditStorage(Path(db_path))
        filters = filters or {}
        
        # Convert string enums
        if 'level' in filters and isinstance(filters['level'], str):
            filters['level'] = AuditLevel(filters['level'])
        if 'category' in filters and isinstance(filters['category'], str):
            filters['category'] = AuditCategory(filters['category'])
        
        # Query all matching entries (no pagination for export)
        all_entries = []
        page = 1
        while True:
            entries = storage.query(**filters, page=page, page_size=1000)
            if not entries:
                break
            all_entries.extend(entries)
            page += 1
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "jsonl":
            _export_jsonl(all_entries, output_file)
        elif format == "json":
            _export_json(all_entries, output_file)
        elif format == "csv":
            _export_csv(all_entries, output_file)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return {
            "success": True,
            "output_path": str(output_file),
            "format": format,
            "entry_count": len(all_entries)
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def _export_jsonl(entries: List[Dict[str, Any]], output_path: Path):
    """Export to JSONL format."""
    with open(output_path, 'w') as f:
        for entry in entries:
            f.write(json.dumps(entry, default=str) + '\n')


def _export_json(entries: List[Dict[str, Any]], output_path: Path):
    """Export to JSON format."""
    with open(output_path, 'w') as f:
        json.dump(entries, f, indent=2, default=str)


def _export_csv(entries: List[Dict[str, Any]], output_path: Path):
    """Export to CSV format."""
    if not entries:
        return
    
    # Get all unique fields
    fieldnames = set()
    for entry in entries:
        fieldnames.update(entry.keys())
    fieldnames = sorted(fieldnames)
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for entry in entries:
            # Convert complex types to strings
            row = {}
            for key, value in entry.items():
                if isinstance(value, (dict, list)):
                    row[key] = json.dumps(value, default=str)
                else:
                    row[key] = value
            writer.writerow(row)


def audit_validate(
    db_path: str,
    ac_id: str
) -> Dict[str, Any]:
    """
    Validate an acceptance criterion against audit evidence.
    
    Implements AC-AUDIT-004: audit_validate MCP tool.
    
    This tool queries audit logs for a specific AC-ID and determines:
    - Whether audit traces exist for the AC
    - Validation status based on log levels and coverage
    - Evidence summary for compliance reporting
    
    Args:
        db_path: Path to audit database
        ac_id: Acceptance criteria ID to validate (e.g., "AC-GOV-001")
    
    Returns:
        Validation result with status and evidence
    """
    try:
        storage = AuditStorage(Path(db_path))
        
        # Query all entries for this AC-ID
        entries = storage.query(ac_id=ac_id, page_size=1000)
        
        if not entries:
            return {
                "success": True,
                "ac_id": ac_id,
                "validation_status": "NO_DATA",
                "audit_trace_exists": False,
                "evidence": {
                    "total_entries": 0,
                    "error_count": 0,
                    "warning_count": 0,
                    "info_count": 0,
                    "components": [],
                    "operations": [],
                    "date_range": None
                },
                "message": f"No audit entries found for {ac_id}"
            }
        
        # Analyze entries
        error_count = sum(1 for e in entries if e.get('level') in ('error', 'critical'))
        warning_count = sum(1 for e in entries if e.get('level') == 'warning')
        info_count = sum(1 for e in entries if e.get('level') in ('info', 'debug', 'trace'))
        
        components = list(set(e.get('component', '') for e in entries if e.get('component')))
        operations = list(set(e.get('operation', '') for e in entries if e.get('operation')))
        
        # Determine date range
        timestamps = [e.get('timestamp', '') for e in entries if e.get('timestamp')]
        date_range = {
            "earliest": min(timestamps) if timestamps else None,
            "latest": max(timestamps) if timestamps else None
        }
        
        # Determine validation status
        # FAILED: Has critical/error entries
        # INCOMPLETE: Only warnings or missing required operations
        # VALIDATED: Has successful execution traces without errors
        if error_count > 0:
            validation_status = "FAILED"
            message = f"AC {ac_id} has {error_count} error(s) in audit trail"
        elif warning_count > 0 and info_count == 0:
            validation_status = "INCOMPLETE"
            message = f"AC {ac_id} has warnings but no success traces"
        elif info_count > 0:
            validation_status = "VALIDATED"
            message = f"AC {ac_id} has {info_count} successful execution trace(s)"
        else:
            validation_status = "INCOMPLETE"
            message = f"AC {ac_id} has insufficient audit data"
        
        return {
            "success": True,
            "ac_id": ac_id,
            "validation_status": validation_status,
            "audit_trace_exists": True,
            "evidence": {
                "total_entries": len(entries),
                "error_count": error_count,
                "warning_count": warning_count,
                "info_count": info_count,
                "components": components,
                "operations": operations,
                "date_range": date_range
            },
            "message": message
        }
    
    except Exception as e:
        return {
            "success": False,
            "ac_id": ac_id,
            "validation_status": "ERROR",
            "audit_trace_exists": False,
            "error": str(e)
        }
