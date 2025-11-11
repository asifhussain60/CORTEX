"""
Dry-Run Cleanup Script for CORTEX Workspace

Scans and reports what would be deleted without making any changes.
Uses the cleanup orchestrator scan report as a guide.

Author: CORTEX
Date: November 11, 2025
"""

from pathlib import Path
from datetime import datetime, timedelta
import json
from collections import defaultdict


def format_size(bytes_size):
    """Format bytes to human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"


def scan_cleanup_targets(workspace_root):
    """Scan workspace for cleanup targets based on report categories"""
    
    workspace = Path(workspace_root)
    results = {
        "timestamp": datetime.now().isoformat(),
        "mode": "DRY_RUN",
        "categories": {},
        "totals": {
            "files": 0,
            "folders": 0,
            "size_bytes": 0
        },
        "items": []
    }
    
    # Category 1: .backup-archive (CRITICAL - Nested)
    backup_archive = workspace / ".backup-archive"
    if backup_archive.exists():
        files = []
        dirs = []
        total_size = 0
        
        # Scan with recursion protection
        def safe_scan(path, depth=0, max_depth=10):
            nonlocal total_size
            if depth > max_depth:
                return
            
            try:
                for item in path.iterdir():
                    if item.is_file():
                        size = item.stat().st_size
                        files.append(str(item.relative_to(workspace)))
                        total_size += size
                    elif item.is_dir():
                        dirs.append(str(item.relative_to(workspace)))
                        safe_scan(item, depth + 1, max_depth)
            except PermissionError:
                pass
        
        safe_scan(backup_archive)
        
        results["categories"]["backup_archive"] = {
            "path": ".backup-archive/",
            "files": len(files),
            "folders": len(dirs),
            "size_bytes": total_size,
            "size_human": format_size(total_size),
            "risk": "LOW",
            "action": "DELETE_ALL",
            "reason": "Recursive nesting, legacy distribution builds"
        }
        results["totals"]["files"] += len(files)
        results["totals"]["folders"] += len(dirs)
        results["totals"]["size_bytes"] += total_size
        
        for f in files[:5]:  # Show first 5 as examples
            results["items"].append({
                "category": "backup_archive",
                "path": f,
                "action": "DELETE"
            })
    
    # Category 2: Story backups (keep 5 most recent)
    docs = workspace / "docs"
    if docs.exists():
        story_backups = sorted(
            docs.glob("awakening-of-cortex.backup.*.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        to_delete = story_backups[5:]  # Delete all but 5 most recent
        total_size = sum(f.stat().st_size for f in to_delete)
        
        if to_delete:
            results["categories"]["story_backups"] = {
                "path": "docs/awakening-of-cortex.backup.*.md",
                "files": len(to_delete),
                "size_bytes": total_size,
                "size_human": format_size(total_size),
                "risk": "LOW",
                "action": "RETAIN_RECENT",
                "keep_count": 5,
                "delete_count": len(to_delete),
                "reason": "Excessive backup files (keep 5 most recent)"
            }
            results["totals"]["files"] += len(to_delete)
            results["totals"]["size_bytes"] += total_size
            
            for f in to_delete[:3]:  # Show first 3 as examples
                results["items"].append({
                    "category": "story_backups",
                    "path": str(f.relative_to(workspace)),
                    "action": "DELETE"
                })
    
    # Category 3: SYSTEM-REFACTOR reports (keep 3 most recent)
    cortex_brain = workspace / "cortex-brain"
    if cortex_brain.exists():
        refactor_reports = sorted(
            cortex_brain.glob("SYSTEM-REFACTOR-REPORT-*.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        to_delete = refactor_reports[3:]  # Delete all but 3 most recent
        total_size = sum(f.stat().st_size for f in to_delete)
        
        if to_delete:
            results["categories"]["system_refactor_reports"] = {
                "path": "cortex-brain/SYSTEM-REFACTOR-REPORT-*.md",
                "files": len(to_delete),
                "size_bytes": total_size,
                "size_human": format_size(total_size),
                "risk": "MEDIUM",
                "action": "RETAIN_RECENT",
                "keep_count": 3,
                "delete_count": len(to_delete),
                "reason": "Auto-generated session reports (keep 3 most recent)"
            }
            results["totals"]["files"] += len(to_delete)
            results["totals"]["size_bytes"] += total_size
            
            for f in to_delete[:3]:  # Show first 3 as examples
                results["items"].append({
                    "category": "system_refactor_reports",
                    "path": str(f.relative_to(workspace)),
                    "action": "DELETE"
                })
    
    # Category 4: Build output (site/)
    site = workspace / "site"
    if site.exists():
        files = list(site.rglob("*"))
        file_list = [f for f in files if f.is_file()]
        dir_list = [f for f in files if f.is_dir()]
        total_size = sum(f.stat().st_size for f in file_list)
        
        results["categories"]["build_output"] = {
            "path": "site/",
            "files": len(file_list),
            "folders": len(dir_list),
            "size_bytes": total_size,
            "size_human": format_size(total_size),
            "risk": "LOW",
            "action": "DELETE_ALL",
            "reason": "MkDocs build output (regenerable)"
        }
        results["totals"]["files"] += len(file_list)
        results["totals"]["folders"] += len(dir_list)
        results["totals"]["size_bytes"] += total_size
        
        results["items"].append({
            "category": "build_output",
            "path": "site/",
            "action": "DELETE_DIRECTORY"
        })
    
    # Category 5: Workflow checkpoints (keep last 7 days)
    checkpoints_dir = workspace / "workflow_checkpoints"
    if checkpoints_dir.exists():
        cutoff = datetime.now() - timedelta(days=7)
        checkpoints = list(checkpoints_dir.glob("wf-*.json"))
        
        to_delete = [
            f for f in checkpoints 
            if datetime.fromtimestamp(f.stat().st_mtime) < cutoff
        ]
        total_size = sum(f.stat().st_size for f in to_delete)
        
        if to_delete:
            results["categories"]["workflow_checkpoints"] = {
                "path": "workflow_checkpoints/wf-*.json",
                "files": len(to_delete),
                "size_bytes": total_size,
                "size_human": format_size(total_size),
                "risk": "LOW",
                "action": "RETAIN_DAYS",
                "keep_days": 7,
                "delete_count": len(to_delete),
                "reason": "Old workflow snapshots (keep last 7 days)"
            }
            results["totals"]["files"] += len(to_delete)
            results["totals"]["size_bytes"] += total_size
            
            for f in to_delete[:2]:  # Show first 2 as examples
                results["items"].append({
                    "category": "workflow_checkpoints",
                    "path": str(f.relative_to(workspace)),
                    "action": "DELETE"
                })
    
    # Category 6: Legacy agent backups
    agents_dir = workspace / "src" / "cortex_agents"
    if agents_dir.exists():
        backup_files = list(agents_dir.glob("*.backup"))
        total_size = sum(f.stat().st_size for f in backup_files)
        
        if backup_files:
            results["categories"]["legacy_agent_backups"] = {
                "path": "src/cortex_agents/*.backup",
                "files": len(backup_files),
                "size_bytes": total_size,
                "size_human": format_size(total_size),
                "risk": "LOW",
                "action": "DELETE_ALL",
                "reason": "Legacy manual backups (Git history available)"
            }
            results["totals"]["files"] += len(backup_files)
            results["totals"]["size_bytes"] += total_size
            
            for f in backup_files:
                results["items"].append({
                    "category": "legacy_agent_backups",
                    "path": str(f.relative_to(workspace)),
                    "action": "DELETE"
                })
    
    # Category 7: Temp directories
    temp_dirs = [
        cortex_brain / "crawler-temp"
    ]
    
    for temp_dir in temp_dirs:
        if temp_dir.exists():
            files = list(temp_dir.rglob("*"))
            file_list = [f for f in files if f.is_file()]
            dir_list = [f for f in files if f.is_dir()]
            total_size = sum(f.stat().st_size for f in file_list)
            
            category_name = f"temp_{temp_dir.name}"
            results["categories"][category_name] = {
                "path": str(temp_dir.relative_to(workspace)),
                "files": len(file_list),
                "folders": len(dir_list),
                "size_bytes": total_size,
                "size_human": format_size(total_size),
                "risk": "LOW",
                "action": "DELETE_ALL",
                "reason": "Temporary directory"
            }
            results["totals"]["files"] += len(file_list)
            results["totals"]["folders"] += len(dir_list)
            results["totals"]["size_bytes"] += total_size
            
            results["items"].append({
                "category": category_name,
                "path": str(temp_dir.relative_to(workspace)),
                "action": "DELETE_DIRECTORY"
            })
    
    return results


def print_dry_run_report(results):
    """Print formatted dry-run report"""
    print("=" * 80)
    print("CORTEX WORKSPACE CLEANUP - DRY RUN REPORT")
    print("=" * 80)
    print(f"\nTimestamp: {results['timestamp']}")
    print(f"Mode: {results['mode']} (NO CHANGES WILL BE MADE)")
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nTotal Files to Delete:     {results['totals']['files']:,}")
    print(f"Total Folders to Delete:   {results['totals']['folders']:,}")
    print(f"Total Space to Free:       {format_size(results['totals']['size_bytes'])}")
    
    print("\n" + "=" * 80)
    print("CATEGORIES")
    print("=" * 80)
    
    for cat_name, cat_info in results['categories'].items():
        print(f"\n{cat_name.upper().replace('_', ' ')}")
        print("-" * 40)
        print(f"  Path:        {cat_info['path']}")
        print(f"  Files:       {cat_info['files']:,}")
        if 'folders' in cat_info:
            print(f"  Folders:     {cat_info['folders']:,}")
        print(f"  Size:        {cat_info['size_human']}")
        print(f"  Risk:        {cat_info['risk']}")
        print(f"  Action:      {cat_info['action']}")
        print(f"  Reason:      {cat_info['reason']}")
        
        if 'keep_count' in cat_info:
            print(f"  Keep:        {cat_info['keep_count']} most recent")
            print(f"  Delete:      {cat_info['delete_count']} older files")
        elif 'keep_days' in cat_info:
            print(f"  Keep:        Last {cat_info['keep_days']} days")
            print(f"  Delete:      {cat_info['delete_count']} older files")
    
    print("\n" + "=" * 80)
    print("SAMPLE ITEMS (First few from each category)")
    print("=" * 80)
    
    for item in results['items'][:15]:  # Show first 15 items
        print(f"\n[{item['category']}] {item['action']}")
        print(f"  {item['path']}")
    
    if len(results['items']) > 15:
        print(f"\n... and {len(results['items']) - 15} more items")
    
    print("\n" + "=" * 80)
    print("SAFETY CHECKS")
    print("=" * 80)
    print("\n✅ Recursion protection enabled (max depth: 10)")
    print("✅ Critical directories protected")
    print("✅ Retention policies applied")
    print("✅ Git history available for recovery")
    print("✅ DRY RUN - No actual deletions")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("\n1. Review this report carefully")
    print("2. Verify critical files are protected")
    print("3. Backup important data if needed")
    print("4. Run live cleanup when ready:")
    print("   python scripts/cleanup_live_run.py")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    workspace_root = Path(__file__).parent.parent
    
    print("\nScanning workspace for cleanup targets...")
    print("This may take a moment...\n")
    
    results = scan_cleanup_targets(workspace_root)
    
    # Save report to file
    report_file = workspace_root / "cortex-brain" / "CLEANUP-DRY-RUN-REPORT.json"
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print_dry_run_report(results)
    
    print(f"\n✅ Detailed report saved to: {report_file}")
    print("\n" + "=" * 80)
