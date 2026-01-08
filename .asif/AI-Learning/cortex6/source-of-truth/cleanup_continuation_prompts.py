#!/usr/bin/env python3
"""
Cleanup redundant continuation prompt files.

Problem: Multiple continuation prompt files were created:
- CONTINUATION-PROMPT.md (official, auto-updated by update_continuation_prompt.py)
- CONTINUATION-PROMPT-V2.md (manually created, 728 lines, now obsolete)

Solution:
1. Keep CONTINUATION-PROMPT.md (canonical, auto-updated)
2. Archive CONTINUATION-PROMPT-V2.md to backlog
3. Update all references to point to single file
4. Ensure only update_continuation_prompt.py creates/updates the file

Author: GitHub Copilot
Date: 2026-01-08
"""

import shutil
from pathlib import Path
from datetime import datetime


def cleanup_continuation_prompts():
    """Clean up redundant continuation prompt files."""
    
    base_dir = Path(__file__).parent
    
    # Files
    canonical = base_dir / "CONTINUATION-PROMPT.md"
    v2_file = base_dir / "CONTINUATION-PROMPT-V2.md"
    backlog_dir = base_dir / "backlog"
    
    print("🧹 CONTINUATION PROMPT CLEANUP")
    print("=" * 80)
    print()
    
    # Verify canonical file exists
    if not canonical.exists():
        print("❌ ERROR: CONTINUATION-PROMPT.md not found!")
        print("   This is the canonical file that should always exist.")
        return False
    
    print(f"✅ Canonical file exists: {canonical.name}")
    print(f"   Auto-updated by: update_continuation_prompt.py")
    print()
    
    # Check for V2 file
    if v2_file.exists():
        print(f"⚠️  Found redundant file: {v2_file.name}")
        
        # Create backlog if needed
        backlog_dir.mkdir(exist_ok=True)
        
        # Archive with timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        archived_name = f"CONTINUATION-PROMPT-V2-ARCHIVED-{timestamp}.md"
        archived_path = backlog_dir / archived_name
        
        shutil.move(str(v2_file), str(archived_path))
        print(f"   ✅ Archived to: backlog/{archived_name}")
        print()
    else:
        print(f"✅ No redundant V2 file found")
        print()
    
    # Summary
    print("=" * 80)
    print("📋 SUMMARY")
    print("=" * 80)
    print()
    print("CANONICAL FILE (Keep This):")
    print(f"  📄 {canonical.name}")
    print(f"     - Auto-updated by update_continuation_prompt.py")
    print(f"     - Referenced in tracker YAML")
    print(f"     - Used by 'continue epic' command")
    print()
    
    print("CLEANUP ACTIONS:")
    print(f"  ✅ Removed CONTINUATION-PROMPT-V2.md (archived to backlog)")
    print(f"  ✅ Only one continuation prompt file remains")
    print()
    
    print("PREVENTION:")
    print(f"  ⛔ DO NOT create new continuation prompt files manually")
    print(f"  ✅ Let update_continuation_prompt.py manage the file")
    print(f"  ✅ Run 'python3 update_continuation_prompt.py' after tracker updates")
    print()
    
    print("REFERENCES TO UPDATE:")
    print(f"  • AUTONOMOUS-EXECUTION-V2-SUMMARY.md - Remove V2 references")
    print(f"  • AUTONOMOUS-EXECUTOR-V2.md - Update to canonical name")
    print(f"  • Any docs mentioning CONTINUATION-PROMPT-V2.md")
    print()
    
    return True


if __name__ == "__main__":
    success = cleanup_continuation_prompts()
    if success:
        print("✅ Cleanup complete!")
    else:
        print("❌ Cleanup failed!")
        exit(1)
