"""
CORTEX Upgrade CLI

Simple command-line interface for CORTEX upgrade system.
Wrapper around upgrade_orchestrator.py for easy invocation.

Usage:
    python cortex-upgrade.py              # Upgrade to latest
    python cortex-upgrade.py --version 5.4.0  # Upgrade to specific version
    python cortex-upgrade.py --dry-run    # Preview upgrade
    python cortex-upgrade.py --help       # Show help

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import sys
from pathlib import Path

# Add operations directory to path
sys.path.insert(0, str(Path(__file__).parent / "operations"))

from upgrade_orchestrator import UpgradeOrchestrator


def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🧠 CORTEX Upgrade System - Safely upgrade your CORTEX installation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cortex-upgrade.py                    # Upgrade to latest version
  python cortex-upgrade.py --dry-run         # Preview upgrade without changes
  python cortex-upgrade.py --version 5.4.0   # Upgrade to specific version
  python cortex-upgrade.py --skip-backup     # Skip backup (not recommended)

For more information, visit: https://github.com/asifhussain60/CORTEX
        """
    )
    
    parser.add_argument(
        "--version",
        type=str,
        metavar="VERSION",
        help="Specific version to upgrade to (e.g., 5.4.0). Default: latest"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview upgrade without making any changes"
    )
    
    parser.add_argument(
        "--skip-backup",
        action="store_true",
        help="Skip backup creation (NOT RECOMMENDED - only use if you have external backup)"
    )
    
    parser.add_argument(
        "--cortex-path",
        type=Path,
        metavar="PATH",
        help="Path to CORTEX installation. Default: auto-detect"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    try:
        # Create orchestrator
        orchestrator = UpgradeOrchestrator(args.cortex_path)
        
        # Run upgrade
        success = orchestrator.upgrade(
            version=args.version,
            dry_run=args.dry_run,
            skip_backup=args.skip_backup
        )
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Upgrade interrupted by user")
        sys.exit(130)  # Standard SIGINT exit code
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"   Use --verbose for detailed error information")
        
        sys.exit(1)


if __name__ == "__main__":
    main()
