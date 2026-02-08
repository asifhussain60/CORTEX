#!/usr/bin/env python3
"""
Comprehensive Phase Artifacts Cleanup Script.

Cleans up CORTEX repository after phase completion:
1. Detects SCREAMING_CASE violations (CORE-028)
2. Archives Integration-First session reports
3. Verifies Integration-First components
4. Moves utility scripts to correct locations
5. Generates cleanup report

PHASE 49 Integration-First Enhancement
AC-ID: AC-VACUUM-PHASE49-001
"""

import json
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from cortex.orchestrators.support.vacuum_orchestrator import (
    CleanupPlan,
    CleanupResult,
    VacuumOrchestrator,
)


def print_header(title: str, width: int = 80) -> None:
    """Print formatted header."""
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width + "\n")


def print_section(title: str) -> None:
    """Print formatted section."""
    print(f"\n📋 {title}")
    print("-" * 70)


def print_violation(violation: Dict[str, Any]) -> None:
    """Print individual violation details."""
    print(f"  ⚠️  {violation['filename']}")
    print(f"      Size: {violation['size_human']} | Category: {violation['category']}")
    print(f"      Pattern: {violation['pattern']}")


def main() -> int:
    """Execute comprehensive cleanup."""
    print_header("🧹 CORTEX Phase Artifacts Cleanup - Phase 49 Integration-First")
    
    orchestrator = VacuumOrchestrator()
    root_path = Path.cwd()
    
    all_success = True
    cleanup_report: Dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "root_path": str(root_path),
        "sections": {},
    }
    
    # ========================================================================
    # SECTION 1: Detect SCREAMING_CASE Violations (CORE-028)
    # ========================================================================
    
    print_section("1. SCREAMING_CASE Violations (CORE-028)")
    
    screaming_case_result = orchestrator.detect_screaming_case_violations(str(root_path))
    cleanup_report["sections"]["screaming_case"] = screaming_case_result
    
    print(f"Status: {screaming_case_result['status'].upper()}")
    print(f"Message: {screaming_case_result.get('message', 'No violations detected')}")
    
    if screaming_case_result["violations"]:
        print(f"\n🎯 Found {screaming_case_result['total_violations']} violations:")
        print(f"   Total size: {screaming_case_result['affected_size_human']}\n")
        
        for violation in screaming_case_result["violations"][:10]:
            print_violation(violation)
        
        if len(screaming_case_result["violations"]) > 10:
            print(f"\n   ... and {len(screaming_case_result['violations']) - 10} more files\n")
    
    # ========================================================================
    # SECTION 2: Verify Integration-First Components
    # ========================================================================
    
    print_section("2. Integration-First Components (Phase 49)")
    
    integration_result = orchestrator.detect_integration_first_files(str(root_path))
    cleanup_report["sections"]["integration_first"] = integration_result
    
    print(f"Status: {integration_result['status'].upper()}")
    print(f"Coverage: {integration_result['coverage_percent']}% ({integration_result['total_expected']} expected)")
    print(f"Message: {integration_result.get('message', 'No status')}")
    
    if integration_result["files_found"]:
        print(f"\n✅ Found {len(integration_result['files_found'])} components:")
        for file_info in integration_result["files_found"]:
            size_kb = file_info["size_bytes"] / 1024
            print(f"   ✓ {file_info['name']} ({size_kb:.1f} KB) [{file_info['type']}]")
    
    if integration_result["files_missing"]:
        print(f"\n❌ Missing {len(integration_result['files_missing'])} components:")
        for missing in integration_result["files_missing"]:
            print(f"   ✗ {missing}")
    
    # ========================================================================
    # SECTION 3: Root-Level File Analysis
    # ========================================================================
    
    print_section("3. Root-Level File Analysis")
    
    root_scan = orchestrator.scan_root_level(str(root_path))
    cleanup_report["sections"]["root_level"] = root_scan
    
    if root_scan["status"] == "success":
        print(f"Utility scripts: {root_scan['summary']['utility_scripts_count']}")
        print(f"Production files: {root_scan['summary']['production_files_count']}")
        print(f"Directories: {root_scan['summary']['directories_count']}")
        print(f"Recommendations: {root_scan['summary']['total_recommendations']}")
        
        if root_scan["utility_scripts"]:
            print(f"\n📦 Utility scripts (should move to scripts/utilities/):")
            for script in root_scan["utility_scripts"]:
                print(f"   • {script}")
    
    # ========================================================================
    # SECTION 4: Generate Cleanup Plan
    # ========================================================================
    
    print_section("4. Cleanup Plan Generation")
    
    # Scan for markdown sprawl
    scan_result = orchestrator.scan_repository(str(root_path))
    print(f"Markdown files found: {scan_result['total_count']}")
    
    # Generate cleanup plan
    plan: CleanupPlan = orchestrator.generate_cleanup_plan(
        scan_result,
        age_threshold_days=0,  # Include all files
        include_conflicting=True,
    )
    
    cleanup_report["sections"]["cleanup_plan"] = {
        "total_files": plan.total_files,
        "archive_base": plan.archive_base_path,
        "files_to_archive": len(plan.files_to_archive),
    }
    
    print(f"Files to archive: {plan.total_files}")
    print(f"Archive destination: {plan.archive_base_path}/")
    
    if plan.files_to_archive:
        print(f"\n📂 Categorization:")
        categories = {}
        for item in plan.files_to_archive:
            cat = item["category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in sorted(categories.items()):
            print(f"   • {cat}: {count} file(s)")
    
    # ========================================================================
    # SECTION 5: Execute Cleanup (Dry-Run First)
    # ========================================================================
    
    print_section("5. Cleanup Execution (Dry-Run)")
    
    if plan.total_files == 0:
        print("✅ No files to archive - repository is clean!")
    else:
        print(f"Ready to archive {plan.total_files} files\n")
        
        # Show sample files
        print("Sample files to archive:")
        for item in plan.files_to_archive[:5]:
            print(f"  • {item['source']} → {item['destination']}")
        
        if len(plan.files_to_archive) > 5:
            print(f"  ... and {len(plan.files_to_archive) - 5} more files")
        
        # Ask for confirmation
        print("\n" + "=" * 70)
        proceed = input("\n🤔 Proceed with cleanup? (yes/no): ").strip().lower()
        
        if proceed in ["yes", "y", "proceed"]:
            print("\n🚀 Executing cleanup...")
            cleanup_result: CleanupResult = orchestrator.execute_cleanup(
                plan, root_path=str(root_path)
            )
            
            cleanup_report["sections"]["cleanup_result"] = {
                "success": cleanup_result.success,
                "files_moved": cleanup_result.files_moved,
                "files_deleted": cleanup_result.files_deleted,
                "conflicts_resolved": cleanup_result.conflicts_resolved,
                "errors": cleanup_result.errors,
            }
            
            print(f"✅ Cleanup complete!")
            print(f"   Files moved: {cleanup_result.files_moved}")
            print(f"   Conflicts resolved: {cleanup_result.conflicts_resolved}")
            
            if cleanup_result.errors:
                print(f"\n⚠️  Errors encountered:")
                for error in cleanup_result.errors:
                    print(f"   • {error}")
                all_success = False
            
            # Verify cleanup
            print("\n🔍 Verifying cleanup...")
            verification = orchestrator.verify_cleanup(cleanup_result, plan)
            
            print(f"   Files preserved: {verification.files_preserved}")
            print(f"   No deletions: {verification.no_deletions}")
            print(f"   Broken links: {verification.broken_links_count}")
            print(f"   Git status clean: {verification.git_status_clean}")
            
            if verification.issues:
                print(f"\n⚠️  Verification issues:")
                for issue in verification.issues:
                    print(f"   • {issue}")
        else:
            print("\n⏭️  Cleanup cancelled - no files modified")
    
    # ========================================================================
    # SECTION 6: Summary & Report
    # ========================================================================
    
    print_section("6. Cleanup Summary")
    
    print(f"✅ SCREAMING_CASE violations: {screaming_case_result['total_violations']} ({screaming_case_result['affected_size_human']})")
    print(f"✅ Integration-First components: {integration_result['coverage_percent']}% complete")
    print(f"✅ Root-level analysis: {root_scan['summary']['total_recommendations']} recommendations")
    
    # Save report
    report_path = root_path / "cleanup-report.json"
    with open(report_path, "w") as f:
        json.dump(cleanup_report, f, indent=2)
    
    print(f"\n📊 Full report saved to: {report_path}")
    
    # ========================================================================
    # Final Status
    # ========================================================================
    
    print_header("Cleanup Complete" if all_success else "Cleanup Complete (With Warnings)")
    
    if all_success:
        print("✅ All checks passed!")
        print("🎉 Repository is clean and ready for the next phase.")
        return 0
    else:
        print("⚠️  Cleanup completed with warnings.")
        print("📋 Review the report and address any issues.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏸️  Cleanup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)
