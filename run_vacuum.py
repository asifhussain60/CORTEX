#!/usr/bin/env python3
"""
CORTEX Vacuum Runner - Clean Copilot-generated markdown bloat
Usage: python run_vacuum.py [--dry-run]
"""
import sys
from pathlib import Path
from cortex.orchestrators.support.vacuum_orchestrator import VacuumOrchestrator

def main():
    dry_run = '--dry-run' in sys.argv
    
    v = VacuumOrchestrator()
    
    print("🧹 CORTEX Vacuum - Markdown Cleanup")
    print("=" * 70)
    
    # Scan
    print("\n1️⃣ Scanning repository...")
    result = v.scan_repository('.')
    files_found = result.get('files_found', [])
    
    # Filter for Copilot patterns
    copilot_patterns = ['-COMPLETION.md', '-SUMMARY.md', '-summary.md', '-completion.md', 
                        'PHASE-', 'ENH-', 'ARCHITECT-']
    copilot_files = [f for f in files_found if any(p in f for p in copilot_patterns)]
    
    print(f"   ✅ Total markdown files: {len(files_found)}")
    print(f"   🎯 Copilot-generated files: {len(copilot_files)}")
    
    if copilot_files:
        print("\n📋 Copilot Files Detected:")
        for f in copilot_files[:30]:
            print(f"   • {f}")
        if len(copilot_files) > 30:
            print(f"   ... and {len(copilot_files) - 30} more")
    
    # Generate cleanup plan
    print("\n2️⃣ Generating cleanup plan...")
    plan_result = v.generate_cleanup_plan(result)
    
    if plan_result:
        archive_files = plan_result.files_to_archive
        print(f"   ✅ Files to archive: {len(archive_files)}")
        
        if dry_run:
            print("\n🔍 DRY RUN MODE - No files will be moved")
            print("\nFiles that would be archived:")
            for f in archive_files[:20]:
                print(f"   • {f['source']} → {f['destination']}")
            if len(archive_files) > 20:
                print(f"   ... and {len(archive_files) - 20} more")
        else:
            # Execute cleanup
            print("\n3️⃣ Executing cleanup...")
            cleanup_result = v.execute_cleanup(plan_result)
            
            if cleanup_result.status == 'success':
                archived = cleanup_result.archived_count
                print(f"   ✅ Archived {archived} files")
                
                # Verify
                print("\n4️⃣ Verifying cleanup...")
                verify_result = v.verify_cleanup('.')
                
                print(f"   ✅ Verification complete")
                print(f"   📁 Archive location: docs/archive/")
            else:
                print(f"   ❌ Cleanup failed: {cleanup_result.message}")
    else:
        print(f"   ❌ Planning failed")
    
    print("\n" + "=" * 70)
    print("✅ Vacuum complete")

if __name__ == '__main__':
    main()
