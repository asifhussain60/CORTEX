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

from src.infrastructure.enhanced_audit_logger import (
    AuditStorage,
    AuditLevel,
    AuditCategory
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
