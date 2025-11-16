#!/usr/bin/env python3
"""
Track B Phase B1: Foundation Fixes - Obsolete Test Cleanup
Part of CORTEX 3.0 Track 2 (System Optimization)

This script safely removes 36 obsolete test files identified by the optimizer.
Critical path for Track 1 unlock.
"""

import json
import os
import shutil
from pathlib import Path

def cleanup_obsolete_tests():
    """Remove obsolete tests based on manifest"""
    
    # Load the manifest
    manifest_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/obsolete-tests-manifest.json")
    
    if not manifest_path.exists():
        print("❌ Manifest not found. Run optimizer first.")
        return False
    
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    print(f"🧹 Track B Phase B1: Foundation Fixes")
    print(f"📋 Found {len(manifest['tests'])} obsolete tests to remove")
    print()
    
    # Create backup directory
    backup_dir = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/backups/obsolete-tests-2025-11-16")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    removed_count = 0
    skipped_count = 0
    
    for test_info in manifest['tests']:
        file_path = Path("/Users/asifhussain/PROJECTS/CORTEX") / test_info['file_path']
        
        if file_path.exists():
            # Backup first
            backup_path = backup_dir / test_info['file_path'].replace('/', '_')
            shutil.copy2(file_path, backup_path)
            
            # Remove the obsolete test
            file_path.unlink()
            print(f"✅ Removed: {test_info['file_path']}")
            removed_count += 1
        else:
            print(f"⏭️  Skipped: {test_info['file_path']} (already removed)")
            skipped_count += 1
    
    print()
    print(f"📊 Summary:")
    print(f"   Removed: {removed_count} files")
    print(f"   Skipped: {skipped_count} files")
    print(f"   Backup: {backup_dir}")
    print()
    print(f"✅ Phase B1 Step 1 Complete: Obsolete tests cleaned up")
    
    return True

if __name__ == "__main__":
    cleanup_obsolete_tests()