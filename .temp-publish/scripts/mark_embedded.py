"""
Mark CORTEX Installation as Embedded

Creates a .cortex-embedded marker file to explicitly indicate
that CORTEX is embedded within another project. This ensures
the upgrade system uses safe file-copy method instead of git merge.

Usage:
    python scripts/mark_embedded.py
    python scripts/mark_embedded.py --parent "NOOR-CANVAS"

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime


def mark_as_embedded(cortex_path: Path, parent_project: str = None) -> bool:
    """
    Create .cortex-embedded marker file.
    
    Args:
        cortex_path: Path to CORTEX installation
        parent_project: Name of parent project (auto-detected if None)
        
    Returns:
        True if marker created successfully
    """
    # Auto-detect parent project name
    if parent_project is None:
        parent_project = cortex_path.parent.name
    
    # Create marker content
    marker_content = f"""# CORTEX Embedded Installation Marker
#
# This file indicates that CORTEX is embedded within another project.
# The upgrade system will use safe file-copy method instead of git merge
# to prevent files from escaping the CORTEX directory.
#
# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Parent Project: {parent_project}
# CORTEX Path: {cortex_path}
#
# DO NOT DELETE THIS FILE unless you convert to standalone installation.
#
# For more information, see:
# .github/prompts/modules/upgrade-guide.md (Embedded Installation Safety)
"""
    
    # Write marker file
    marker_path = cortex_path / ".cortex-embedded"
    
    try:
        marker_path.write_text(marker_content, encoding='utf-8')
        print(f"✅ Created embedded installation marker")
        print(f"   Path: {marker_path}")
        print(f"   Parent Project: {parent_project}")
        print(f"\n📋 Next Steps:")
        print(f"   1. Add to git: git add .cortex-embedded")
        print(f"   2. Commit: git commit -m 'Mark CORTEX as embedded installation'")
        print(f"   3. Test upgrade: /CORTEX upgrade --dry-run")
        return True
    except Exception as e:
        print(f"❌ Failed to create marker: {e}")
        return False


def verify_embedded_detection(cortex_path: Path) -> bool:
    """
    Verify that CORTEX is detected as embedded.
    
    Args:
        cortex_path: Path to CORTEX installation
        
    Returns:
        True if detected as embedded
    """
    try:
        sys.path.insert(0, str(cortex_path / "scripts" / "operations"))
        from upgrade_orchestrator import UpgradeOrchestrator
        
        orchestrator = UpgradeOrchestrator(cortex_path)
        return orchestrator.is_embedded
    except Exception as e:
        print(f"⚠️  Could not verify detection: {e}")
        return False


def remove_marker(cortex_path: Path) -> bool:
    """
    Remove embedded marker (convert to standalone).
    
    Args:
        cortex_path: Path to CORTEX installation
        
    Returns:
        True if marker removed successfully
    """
    marker_path = cortex_path / ".cortex-embedded"
    
    if not marker_path.exists():
        print(f"ℹ️  No embedded marker found")
        return True
    
    try:
        marker_path.unlink()
        print(f"✅ Removed embedded marker")
        print(f"   CORTEX will now be treated as standalone")
        return True
    except Exception as e:
        print(f"❌ Failed to remove marker: {e}")
        return False


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="🔒 Mark CORTEX installation as embedded for safe upgrades",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/mark_embedded.py                           # Create marker with auto-detection
  python scripts/mark_embedded.py --parent "NOOR-CANVAS"   # Specify parent project
  python scripts/mark_embedded.py --verify                  # Check detection status
  python scripts/mark_embedded.py --remove                  # Convert to standalone

What does this do?
  Creates a .cortex-embedded marker file that tells the upgrade system
  to use safe file-copy method instead of git merge. This prevents files
  from escaping the CORTEX directory during upgrades.

When to use?
  Use when CORTEX is embedded in another project (e.g., NOOR-CANVAS/CORTEX/)
  to ensure upgrades don't pollute your parent project with files.
        """
    )
    
    parser.add_argument(
        "--cortex-path",
        type=Path,
        default=Path(__file__).parent.parent,
        metavar="PATH",
        help="Path to CORTEX installation (default: auto-detect)"
    )
    
    parser.add_argument(
        "--parent",
        type=str,
        metavar="PROJECT",
        help="Name of parent project (default: auto-detect from directory name)"
    )
    
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify embedded detection without creating marker"
    )
    
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Remove embedded marker (convert to standalone)"
    )
    
    args = parser.parse_args()
    
    cortex_path = args.cortex_path.resolve()
    
    # Verify path exists
    if not cortex_path.exists():
        print(f"❌ CORTEX path not found: {cortex_path}")
        sys.exit(1)
    
    # Handle verify mode
    if args.verify:
        print(f"🔍 Checking embedded detection...")
        print(f"   CORTEX Path: {cortex_path}")
        
        is_embedded = verify_embedded_detection(cortex_path)
        marker_exists = (cortex_path / ".cortex-embedded").exists()
        
        print(f"\n📊 Detection Results:")
        print(f"   Marker File: {'✅ Exists' if marker_exists else '❌ Not Found'}")
        print(f"   Detected As: {'🔒 Embedded' if is_embedded else '🔓 Standalone'}")
        
        if is_embedded:
            print(f"\n✅ CORTEX is detected as embedded installation")
            print(f"   Upgrades will use safe file-copy method")
        else:
            print(f"\n⚠️  CORTEX is NOT detected as embedded")
            print(f"   Run without --verify to create marker")
        
        sys.exit(0 if is_embedded else 1)
    
    # Handle remove mode
    if args.remove:
        success = remove_marker(cortex_path)
        sys.exit(0 if success else 1)
    
    # Create marker
    print(f"🔒 Marking CORTEX as Embedded Installation")
    print(f"=" * 60)
    print(f"   CORTEX Path: {cortex_path}")
    print(f"   Parent Project: {args.parent or cortex_path.parent.name}")
    print()
    
    success = mark_as_embedded(cortex_path, args.parent)
    
    if success:
        # Verify detection
        print(f"\n🔍 Verifying detection...")
        if verify_embedded_detection(cortex_path):
            print(f"✅ Embedded detection confirmed")
        else:
            print(f"⚠️  Detection verification failed (may need system restart)")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
