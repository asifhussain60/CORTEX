#!/usr/bin/env python3
"""
CORTEX Setup Script

Terminal-friendly script for setting up CORTEX in any repository.

Usage:
    # Setup in current directory
    python scripts/cortex_setup.py
    
    # Setup in specific directory
    python scripts/cortex_setup.py --repo /path/to/project
    
    # Custom brain location
    python scripts/cortex_setup.py --brain /path/to/brain
    
    # Quiet mode (minimal output)
    python scripts/cortex_setup.py --quiet
"""

import sys
import argparse
from pathlib import Path

# Add src to path for imports
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.entry_point.cortex_entry import CortexEntry


def main():
    """Main entry point for setup script."""
    parser = argparse.ArgumentParser(
        description="Initialize CORTEX in repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup in current directory
  python scripts/cortex_setup.py
  
  # Setup in specific project
  python scripts/cortex_setup.py --repo /path/to/project
  
  # Custom brain location
  python scripts/cortex_setup.py --brain /path/to/brain
  
  # Quiet mode
  python scripts/cortex_setup.py --quiet

What This Does:
  1. Analyzes repository structure and technologies
  2. Installs Python/Node.js dependencies
  3. Installs MkDocs for documentation
  4. Creates CORTEX brain (4-tier architecture)
  5. Runs crawlers to populate knowledge graph
  6. Shows "Awakening of CORTEX" story and quick start guide
  
Estimated Time: 5-10 minutes
        """
    )
    
    parser.add_argument(
        "--repo",
        help="Repository path (default: current directory)",
        default=None
    )
    
    parser.add_argument(
        "--brain",
        help="Brain path (default: repo/cortex-brain)",
        default=None
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output (only errors and summary)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="CORTEX Setup v5.0.0"
    )
    
    args = parser.parse_args()
    
    # Validate repo path
    if args.repo:
        repo_path = Path(args.repo)
        if not repo_path.exists():
            print(f"❌ Error: Repository path does not exist: {repo_path}")
            return 1
        if not repo_path.is_dir():
            print(f"❌ Error: Repository path is not a directory: {repo_path}")
            return 1
    else:
        repo_path = Path.cwd()
    
    try:
        # Initialize CORTEX entry point
        entry = CortexEntry(
            brain_path=args.brain,
            enable_logging=not args.quiet
        )
        
        # Run setup
        results = entry.setup(
            repo_path=str(repo_path),
            verbose=not args.quiet
        )
        
        # Check results
        if results.get("success"):
            print("\n✅ CORTEX setup completed successfully!")
            
            if results.get("warnings"):
                print(f"\n⚠️  {len(results['warnings'])} warning(s) - see log for details")
            
            return 0
        else:
            print("\n❌ CORTEX setup failed!")
            
            if results.get("errors"):
                print("\nErrors:")
                for error in results["errors"]:
                    print(f"  - {error}")
            
            return 1
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        return 130
    
    except Exception as e:
        print(f"\n❌ Setup failed with unexpected error: {e}")
        
        if not args.quiet:
            import traceback
            print("\nFull traceback:")
            traceback.print_exc()
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
