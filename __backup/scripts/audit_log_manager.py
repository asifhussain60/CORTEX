#!/usr/bin/env python3
"""
CORTEX 6.0 Audit Log Manager

Manages audit logs efficiently:
1. Rotation - Archive old logs
2. Compression - Reduce storage
3. Querying - Search and filter logs
4. Cleanup - Remove stale data

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import argparse
import gzip
import json
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
AUDIT_LOG_DIR = PROJECT_ROOT / "cortex-brain" / "audit-logs"
ARCHIVE_DIR = AUDIT_LOG_DIR / "archive"
SESSION_AUDIT = PROJECT_ROOT / ".asif" / "AI-Learning" / "cortex6" / "source-of-truth" / "session-audit.jsonl"


class AuditLogManager:
    """Manages CORTEX audit logs for efficiency."""
    
    def __init__(self):
        self.audit_dir = AUDIT_LOG_DIR
        self.archive_dir = ARCHIVE_DIR
        
    def get_stats(self) -> Dict:
        """Get audit log statistics."""
        stats = {
            "total_files": 0,
            "total_size_kb": 0,
            "total_entries": 0,
            "oldest_log": None,
            "newest_log": None,
            "by_category": {},
            "by_date": {}
        }
        
        if not self.audit_dir.exists():
            return stats
        
        for log_file in self.audit_dir.glob("*.jsonl"):
            stats["total_files"] += 1
            stats["total_size_kb"] += log_file.stat().st_size / 1024
            
            # Extract date from filename (format: YYYYMMDD_HHMMSS_category.jsonl)
            parts = log_file.stem.split("_")
            if len(parts) >= 3:
                date_str = parts[0]
                category = "_".join(parts[2:])
                
                # Track by category
                stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
                
                # Track by date
                stats["by_date"][date_str] = stats["by_date"].get(date_str, 0) + 1
            
            # Count entries
            try:
                with open(log_file) as f:
                    stats["total_entries"] += sum(1 for line in f if line.strip())
            except:
                pass
            
            # Track oldest/newest
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if stats["oldest_log"] is None or mtime < stats["oldest_log"]:
                stats["oldest_log"] = mtime
            if stats["newest_log"] is None or mtime > stats["newest_log"]:
                stats["newest_log"] = mtime
        
        return stats
    
    def rotate_logs(self, days_to_keep: int = 7) -> Dict:
        """Archive logs older than N days."""
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        cutoff = datetime.now() - timedelta(days=days_to_keep)
        archived = []
        kept = []
        
        for log_file in self.audit_dir.glob("*.jsonl"):
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            
            if mtime < cutoff:
                # Compress and move to archive
                archive_name = log_file.name + ".gz"
                archive_path = self.archive_dir / archive_name
                
                with open(log_file, 'rb') as f_in:
                    with gzip.open(archive_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                log_file.unlink()
                archived.append(log_file.name)
            else:
                kept.append(log_file.name)
        
        return {
            "archived": len(archived),
            "kept": len(kept),
            "archived_files": archived
        }
    
    def cleanup_empty(self) -> int:
        """Remove empty log files."""
        removed = 0
        
        for log_file in self.audit_dir.glob("*.jsonl"):
            if log_file.stat().st_size == 0:
                log_file.unlink()
                removed += 1
        
        return removed
    
    def consolidate_by_date(self, date_str: str = None) -> Path:
        """Consolidate logs for a specific date into one file."""
        if date_str is None:
            date_str = datetime.now().strftime("%Y%m%d")
        
        consolidated_path = self.audit_dir / f"consolidated_{date_str}.jsonl"
        entries = []
        
        for log_file in self.audit_dir.glob(f"{date_str}_*.jsonl"):
            try:
                with open(log_file) as f:
                    for line in f:
                        if line.strip():
                            entries.append(json.loads(line))
            except:
                pass
        
        # Sort by timestamp
        entries.sort(key=lambda x: x.get("timestamp", ""))
        
        # Write consolidated file
        with open(consolidated_path, 'w') as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")
        
        return consolidated_path
    
    def query(
        self,
        category: str = None,
        level: str = None,
        component: str = None,
        hours: int = 24,
        search: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """Query audit logs with filters."""
        cutoff = datetime.now() - timedelta(hours=hours)
        results = []
        
        # Search all recent logs
        for log_file in self.audit_dir.glob("*.jsonl"):
            if log_file.stat().st_mtime < cutoff.timestamp():
                continue
            
            try:
                with open(log_file) as f:
                    for line in f:
                        if not line.strip():
                            continue
                        
                        entry = json.loads(line)
                        
                        # Apply filters
                        if category and entry.get("category", "").lower() != category.lower():
                            continue
                        if level and entry.get("level", "").lower() != level.lower():
                            continue
                        if component and component.lower() not in entry.get("component", "").lower():
                            continue
                        if search and search.lower() not in json.dumps(entry).lower():
                            continue
                        
                        results.append(entry)
                        
                        if len(results) >= limit:
                            break
            except:
                pass
            
            if len(results) >= limit:
                break
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return results[:limit]
    
    def export_report(self, output_path: Path = None, hours: int = 24) -> Path:
        """Export audit summary report."""
        if output_path is None:
            output_path = PROJECT_ROOT / "cortex-brain" / "documents" / "reports" / f"audit-report-{datetime.now().strftime('%Y%m%d-%H%M')}.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        stats = self.get_stats()
        entries = self.query(hours=hours, limit=1000)
        
        # Analyze entries
        by_level = {}
        by_category = {}
        by_component = {}
        errors = []
        
        for entry in entries:
            level = entry.get("level", "unknown")
            category = entry.get("category", "unknown")
            component = entry.get("component", "unknown")
            
            by_level[level] = by_level.get(level, 0) + 1
            by_category[category] = by_category.get(category, 0) + 1
            by_component[component] = by_component.get(component, 0) + 1
            
            if level.lower() in ["error", "critical"]:
                errors.append(entry)
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "period_hours": hours,
            "statistics": stats,
            "analysis": {
                "total_entries": len(entries),
                "by_level": by_level,
                "by_category": by_category,
                "by_component": by_component,
                "error_count": len(errors)
            },
            "errors": errors[:10],  # Include first 10 errors
            "health_status": "HEALTHY" if len(errors) == 0 else "NEEDS_ATTENTION"
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return output_path


def main():
    parser = argparse.ArgumentParser(description="CORTEX Audit Log Manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Stats command
    subparsers.add_parser("stats", help="Show audit log statistics")
    
    # Rotate command
    rotate_parser = subparsers.add_parser("rotate", help="Archive old logs")
    rotate_parser.add_argument("--days", type=int, default=7, help="Days to keep (default: 7)")
    
    # Cleanup command
    subparsers.add_parser("cleanup", help="Remove empty log files")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Search audit logs")
    query_parser.add_argument("--category", help="Filter by category")
    query_parser.add_argument("--level", help="Filter by level (info, warning, error)")
    query_parser.add_argument("--component", help="Filter by component")
    query_parser.add_argument("--hours", type=int, default=24, help="Hours to search (default: 24)")
    query_parser.add_argument("--search", help="Text search")
    query_parser.add_argument("--limit", type=int, default=20, help="Max results (default: 20)")
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate audit report")
    report_parser.add_argument("--hours", type=int, default=24, help="Hours to analyze (default: 24)")
    
    # Consolidate command
    consolidate_parser = subparsers.add_parser("consolidate", help="Consolidate logs by date")
    consolidate_parser.add_argument("--date", help="Date to consolidate (YYYYMMDD)")
    
    args = parser.parse_args()
    manager = AuditLogManager()
    
    if args.command == "stats":
        stats = manager.get_stats()
        print("\n📊 Audit Log Statistics")
        print("=" * 50)
        print(f"Total files: {stats['total_files']}")
        print(f"Total size: {stats['total_size_kb']:.1f} KB")
        print(f"Total entries: {stats['total_entries']}")
        print(f"Oldest log: {stats['oldest_log']}")
        print(f"Newest log: {stats['newest_log']}")
        print(f"\nBy category: {stats['by_category']}")
        print(f"By date: {stats['by_date']}")
        
    elif args.command == "rotate":
        result = manager.rotate_logs(days_to_keep=args.days)
        print(f"\n✅ Rotation complete")
        print(f"   Archived: {result['archived']} files")
        print(f"   Kept: {result['kept']} files")
        
    elif args.command == "cleanup":
        removed = manager.cleanup_empty()
        print(f"\n✅ Cleanup complete: Removed {removed} empty files")
        
    elif args.command == "query":
        results = manager.query(
            category=args.category,
            level=args.level,
            component=args.component,
            hours=args.hours,
            search=args.search,
            limit=args.limit
        )
        print(f"\n🔍 Found {len(results)} entries")
        print("-" * 50)
        for entry in results:
            ts = entry.get("timestamp", "")[:19]
            level = entry.get("level", "?")
            cat = entry.get("category", "?")
            msg = entry.get("message", "")[:60]
            print(f"[{ts}] {level.upper():8} {cat:20} {msg}")
            
    elif args.command == "report":
        path = manager.export_report(hours=args.hours)
        print(f"\n✅ Report generated: {path}")
        
    elif args.command == "consolidate":
        path = manager.consolidate_by_date(date_str=args.date)
        print(f"\n✅ Consolidated to: {path}")
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
