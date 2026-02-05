#!/usr/bin/env python3
"""
CORTEX Root Cleanup - Organize root-level files and directories
Usage: python run_root_cleanup.py [--dry-run] [--execute]
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cortex.orchestrators.support.vacuum_orchestrator import VacuumOrchestrator


def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print('=' * 70)


def print_recommendations(recommendations: list) -> None:
    """Print recommendations in a formatted way."""
    if not recommendations:
        print("  ✅ No recommendations - root is clean!")
        return
    
    move_recs = [r for r in recommendations if r["action"] == "move"]
    review_recs = [r for r in recommendations if r["action"] == "review"]
    
    if move_recs:
        print(f"\n📦 Files to Move ({len(move_recs)}):")
        for rec in move_recs:
            print(f"  • {rec['file']}")
            print(f"    → {rec['destination']}")
            print(f"    Reason: {rec['reason']}")
    
    if review_recs:
        print(f"\n🔍 Files for Review ({len(review_recs)}):")
        for rec in review_recs:
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                rec.get("priority", "medium"), "⚪"
            )
            print(f"  {priority_icon} {rec['file']}")
            print(f"    Reason: {rec['reason']}")


def print_directories(directories: list) -> None:
    """Print directory analysis."""
    if not directories:
        return
    
    print(f"\n📁 Root Directories ({len(directories)}):")
    for dir_info in sorted(directories, key=lambda x: x["size_bytes"], reverse=True):
        purpose_icon = "🟢" if "Production" in dir_info["purpose"] else "🟡"
        print(f"  {purpose_icon} {dir_info['name']:<20} {dir_info['size_human']:>10}  {dir_info['purpose']}")


def main() -> None:
    """Main execution."""
    dry_run = '--dry-run' in sys.argv
    execute = '--execute' in sys.argv
    
    if not dry_run and not execute:
        print("Usage: python run_root_cleanup.py [--dry-run | --execute]")
        print("  --dry-run   Show what would be done without making changes")
        print("  --execute   Actually perform the cleanup")
        sys.exit(1)
    
    v = VacuumOrchestrator()
    
    print("🧹 CORTEX Root Cleanup - Repository Organization")
    print_section("1️⃣ Scanning Root Level")
    
    scan_result = v.scan_root_level('.')
    
    if scan_result["status"] != "success":
        print(f"  ❌ Scan failed: {scan_result.get('error')}")
        sys.exit(1)
    
    summary = scan_result["summary"]
    print(f"  ✅ Scan complete!")
    print(f"  📊 Found:")
    print(f"     • {summary['utility_scripts_count']} utility scripts")
    print(f"     • {summary['production_files_count']} production files")
    print(f"     • {summary['directories_count']} root directories")
    print(f"     • {summary['total_recommendations']} recommendations")
    
    # Show directories
    print_directories(scan_result.get("directories", []))
    
    # Show recommendations
    print_section("2️⃣ Cleanup Recommendations")
    print_recommendations(scan_result.get("recommendations", []))
    
    # Execute if requested
    if execute and scan_result.get("recommendations"):
        print_section("3️⃣ Executing Cleanup")
        print("  ⚠️  Moving files...")
        
        cleanup_result = v.execute_root_cleanup(scan_result, ".", dry_run=False)
        
        if cleanup_result["success"]:
            print(f"  ✅ Cleanup complete!")
            print(f"     • Files moved: {cleanup_result['files_moved']}")
            print(f"     • Total actions: {cleanup_result['summary']['total_actions']}")
            
            if cleanup_result.get("errors"):
                print(f"\n  ⚠️  Errors encountered:")
                for error in cleanup_result["errors"]:
                    print(f"     • {error}")
        else:
            print(f"  ❌ Cleanup failed!")
            for error in cleanup_result.get("errors", []):
                print(f"     • {error}")
            sys.exit(1)
    
    elif dry_run and scan_result.get("recommendations"):
        print_section("3️⃣ Dry Run - No Changes Made")
        print("  ℹ️  Run with --execute to perform these actions")
        
        # Simulate to show what would happen
        cleanup_result = v.execute_root_cleanup(scan_result, ".", dry_run=True)
        print(f"  📊 Would move: {cleanup_result['files_moved']} files")
        print(f"  📊 Would flag: {cleanup_result['summary']['reviews']} files for review")
    
    else:
        print("\n  ✨ No cleanup needed - root is already organized!")
    
    print("\n" + "=" * 70)
    print("  Cleanup complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
