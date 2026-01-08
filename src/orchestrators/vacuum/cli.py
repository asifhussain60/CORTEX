"""
Vacuum CLI Integration - feat08-cleanup Phase 1

Command-line interface for Enhanced Vacuum Orchestrator

Usage:
    python3 -m src.orchestrators.vacuum.cli scan <workspace>
    python3 -m src.orchestrators.vacuum.cli preview <workspace>
    python3 -m src.orchestrators.vacuum.cli cleanup <workspace> [--dry-run] [--backup]
    python3 -m src.orchestrators.vacuum.cli multi-preview <repo1> <repo2> ...
    python3 -m src.orchestrators.vacuum.cli multi-cleanup <repo1> <repo2> ... [--dry-run]

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-08
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List

from src.orchestrators.vacuum.enhanced_vacuum import (
    VacuumOrchestrator,
    MultiRepoVacuum,
    generate_cleanup_report
)
from src.orchestrators.vacuum.structure_validator import (
    RepositoryStructureValidator,
    generate_structure_report
)


def scan_command(args):
    """Execute scan command"""
    workspace = Path(args.workspace)
    vacuum = VacuumOrchestrator(workspace)
    
    print(f"Scanning: {workspace}")
    items = vacuum.scan()
    
    print(f"\nFound {len(items)} items to clean:")
    
    # Group by category
    by_category = {}
    for item in items:
        cat = item.category.value
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(item)
    
    for category, category_items in sorted(by_category.items()):
        total_size = sum(item.size_bytes for item in category_items)
        size_mb = total_size / (1024 * 1024)
        print(f"  {category}: {len(category_items)} items ({size_mb:.2f} MB)")


def preview_command(args):
    """Execute preview command"""
    workspace = Path(args.workspace)
    vacuum = VacuumOrchestrator(workspace)
    
    print(f"Previewing cleanup: {workspace}\n")
    preview = vacuum.preview()
    
    print(f"╔══════════════════════════════════════════════════════════════╗")
    print(f"║            VACUUM PREVIEW                                    ║")
    print(f"╚══════════════════════════════════════════════════════════════╝")
    print(f"\nWorkspace: {preview['workspace']}")
    print(f"Timestamp: {preview['timestamp']}")
    print(f"\nTotal Items: {preview['total_items']}")
    print(f"Total Size: {preview['total_size_mb']:.2f} MB")
    
    print(f"\nBy Category:")
    for category, cat_data in sorted(preview['by_category'].items()):
        print(f"\n  {category}:")
        print(f"    Count: {cat_data['count']}")
        print(f"    Size: {cat_data['size_mb']:.2f} MB")
        
        if cat_data['items']:
            print(f"    Sample items:")
            for item in cat_data['items'][:3]:
                print(f"      - {item['path']} ({item['size_mb']:.2f} MB)")
    
    if args.json:
        output_file = Path(args.json)
        output_file.write_text(json.dumps(preview, indent=2))
        print(f"\n✅ Preview saved to: {output_file}")


def cleanup_command(args):
    """Execute cleanup command"""
    workspace = Path(args.workspace)
    vacuum = VacuumOrchestrator(workspace)
    
    dry_run = args.dry_run
    create_backup = args.backup
    
    mode = "DRY-RUN" if dry_run else "EXECUTE"
    print(f"Running cleanup ({mode}): {workspace}\n")
    
    if create_backup and not dry_run:
        print("⚠️  Backup enabled - files will be backed up before deletion")
    
    if dry_run:
        print("ℹ️  DRY-RUN mode - no files will be deleted\n")
    else:
        print("⚠️  LIVE mode - files WILL BE DELETED")
        confirm = input("Continue? (yes/no): ")
        if confirm.lower() != "yes":
            print("Cancelled.")
            return
        print()
    
    result = vacuum.cleanup(dry_run=dry_run, create_backup=create_backup)
    
    # Generate report
    report = generate_cleanup_report(result)
    print(report)
    
    if args.report:
        output_file = Path(args.report)
        output_file.write_text(report)
        print(f"\n✅ Report saved to: {output_file}")
    
    if create_backup and not dry_run and vacuum.backup_dir:
        print(f"\n💾 Backup location: {vacuum.backup_dir}")
        print(f"   To rollback: vacuum.rollback()")


def multi_preview_command(args):
    """Execute multi-repo preview"""
    repos = [Path(repo) for repo in args.repos]
    
    print(f"Previewing {len(repos)} repositories:\n")
    for repo in repos:
        print(f"  - {repo}")
    print()
    
    multi = MultiRepoVacuum(repos)
    preview = multi.preview_all()
    
    print(f"╔══════════════════════════════════════════════════════════════╗")
    print(f"║         MULTI-REPO VACUUM PREVIEW                            ║")
    print(f"╚══════════════════════════════════════════════════════════════╝")
    print(f"\nTotal Repositories: {preview['total_repos']}")
    print(f"Total Items: {preview['total_items']}")
    print(f"Total Size: {preview['total_size_mb']:.2f} MB")
    
    print(f"\nPer Repository:")
    for repo_path, repo_preview in preview['repositories'].items():
        print(f"\n  {repo_path}:")
        print(f"    Items: {repo_preview['total_items']}")
        print(f"    Size: {repo_preview['total_size_mb']:.2f} MB")
    
    if args.json:
        output_file = Path(args.json)
        output_file.write_text(json.dumps(preview, indent=2))
        print(f"\n✅ Preview saved to: {output_file}")


def multi_cleanup_command(args):
    """Execute multi-repo cleanup"""
    repos = [Path(repo) for repo in args.repos]
    dry_run = args.dry_run
    
    mode = "DRY-RUN" if dry_run else "EXECUTE"
    print(f"Multi-repo cleanup ({mode}):\n")
    for repo in repos:
        print(f"  - {repo}")
    print()
    
    if not dry_run:
        print("⚠️  LIVE mode - files WILL BE DELETED from ALL repositories")
        confirm = input("Continue? (yes/no): ")
        if confirm.lower() != "yes":
            print("Cancelled.")
            return
        print()
    
    multi = MultiRepoVacuum(repos)
    results = multi.cleanup_all(dry_run=dry_run)
    
    print(f"╔══════════════════════════════════════════════════════════════╗")
    print(f"║         MULTI-REPO CLEANUP RESULTS                           ║")
    print(f"╚══════════════════════════════════════════════════════════════╝\n")
    
    total_found = 0
    total_deleted = 0
    total_freed = 0
    
    for repo_path, result in results.items():
        print(f"{repo_path}:")
        print(f"  Items Found: {result.items_found}")
        print(f"  Items Deleted: {result.items_deleted}")
        print(f"  Space Freed: {result.total_freed_mb:.2f} MB")
        
        if result.errors:
            print(f"  Errors: {len(result.errors)}")
        
        print()
        
        total_found += result.items_found
        total_deleted += result.items_deleted
        total_freed += result.total_freed_bytes
    
    total_freed_mb = total_freed / (1024 * 1024)
    print(f"Overall Total:")
    print(f"  Items Found: {total_found}")
    print(f"  Items Deleted: {total_deleted}")
    print(f"  Space Freed: {total_freed_mb:.2f} MB")


def validate_command(args):
    """Execute structure validation"""
    workspace = Path(args.workspace)
    
    print(f"Validating structure: {workspace}\n")
    
    validator = RepositoryStructureValidator(workspace)
    report = validator.validate()
    
    # Generate and display report
    report_text = generate_structure_report(report)
    print(report_text)
    
    # Save to file if requested
    if args.json:
        json_file = Path(args.json)
        json_file.write_text(report.to_json())
        print(f"\n✅ JSON report saved to: {json_file}")
    
    if args.report:
        txt_file = Path(args.report)
        txt_file.write_text(report_text)
        print(f"✅ Text report saved to: {txt_file}")
    
    # Exit with error code if invalid
    if not report.valid:
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Enhanced Vacuum Orchestrator v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan for cleanable items")
    scan_parser.add_argument("workspace", help="Workspace directory")
    
    # Preview command
    preview_parser = subparsers.add_parser("preview", help="Preview cleanup operation")
    preview_parser.add_argument("workspace", help="Workspace directory")
    preview_parser.add_argument("--json", help="Save preview to JSON file")
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Execute cleanup")
    cleanup_parser.add_argument("workspace", help="Workspace directory")
    cleanup_parser.add_argument("--dry-run", action="store_true", help="Simulate without deleting")
    cleanup_parser.add_argument("--backup", action="store_true", help="Create backup before deletion")
    cleanup_parser.add_argument("--report", help="Save report to file")
    
    # Multi-repo preview
    multi_preview_parser = subparsers.add_parser("multi-preview", help="Preview multi-repo cleanup")
    multi_preview_parser.add_argument("repos", nargs="+", help="Repository directories")
    multi_preview_parser.add_argument("--json", help="Save preview to JSON file")
    
    # Multi-repo cleanup
    multi_cleanup_parser = subparsers.add_parser("multi-cleanup", help="Execute multi-repo cleanup")
    multi_cleanup_parser.add_argument("repos", nargs="+", help="Repository directories")
    multi_cleanup_parser.add_argument("--dry-run", action="store_true", help="Simulate without deleting")
    
    # Validate structure
    validate_parser = subparsers.add_parser("validate", help="Validate repository structure")
    validate_parser.add_argument("workspace", help="Workspace directory")
    validate_parser.add_argument("--json", help="Save JSON report to file")
    validate_parser.add_argument("--report", help="Save text report to file")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "scan":
            scan_command(args)
        elif args.command == "preview":
            preview_command(args)
        elif args.command == "cleanup":
            cleanup_command(args)
        elif args.command == "multi-preview":
            multi_preview_command(args)
        elif args.command == "multi-cleanup":
            multi_cleanup_command(args)
        elif args.command == "validate":
            validate_command(args)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
