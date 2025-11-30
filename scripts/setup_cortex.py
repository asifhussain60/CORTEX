"""
CORTEX Setup Script

Standalone setup script for initializing CORTEX in a repository.

Usage:
    python scripts/setup_cortex.py
    python scripts/setup_cortex.py --repo /path/to/repo
    python scripts/setup_cortex.py --brain /custom/brain/path
    python scripts/setup_cortex.py --quiet

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.entry_point.cortex_entry import CortexEntry


def main():
    """Run CORTEX setup."""
    parser = argparse.ArgumentParser(
        description="CORTEX Setup - Initialize CORTEX AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/setup_cortex.py                    # Setup in current directory
  python scripts/setup_cortex.py --repo ~/myapp    # Setup in specific repo
  python scripts/setup_cortex.py --quiet           # Minimal output
        """
    )
    
    parser.add_argument(
        "--repo",
        type=str,
        help="Repository path to setup (default: current directory)"
    )
    
    parser.add_argument(
        "--brain",
        type=str,
        help="Custom brain path (default: auto-detected)"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output (opposite of verbose)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Detailed output (default)"
    )
    
    args = parser.parse_args()
    
    # Verbose is default unless --quiet specified
    verbose = not args.quiet if not args.verbose else args.verbose
    
    # Initialize CORTEX
    try:
        print("🧠 Initializing CORTEX...")
        entry = CortexEntry(
            brain_path=args.brain,
            enable_logging=verbose
        )
        print("✅ CORTEX initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize CORTEX: {e}")
        return 1
    
    # Run setup
    try:
        print("📦 Running CORTEX setup wizard...\n")
        results = entry.setup(
            repo_path=args.repo,
            verbose=verbose
        )
        
        if results.get("success"):
            print("\n✅ CORTEX setup completed successfully!")
            
            # Show summary
            if verbose and results.get("summary"):
                print("\n📊 Setup Summary:")
                for key, value in results["summary"].items():
                    print(f"  • {key}: {value}")
            
            return 0
        else:
            print("\n❌ CORTEX setup failed!")
            
            if results.get("errors"):
                print("\n❌ Errors:")
                for error in results["errors"]:
                    print(f"  • {error}")
            
            return 1
    
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    finally:
        # Cleanup
        entry.cleanup()


if __name__ == "__main__":
    sys.exit(main())
