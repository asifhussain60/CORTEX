#!/usr/bin/env python3
"""
CORTEX Configuration Wizard CLI

Author: Syed Asif Hussain
Copyright: © 2024-2025 Syed Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

Progressive configuration tool for adding databases, APIs, and other
resources AFTER initial CORTEX setup.

Usage:
    # Full interactive wizard
    python scripts/cortex_config_wizard.py
    
    # Add single database
    python scripts/cortex_config_wizard.py --add-database
    
    # Add single API
    python scripts/cortex_config_wizard.py --add-api
    
    # Auto-discover only (no prompts)
    python scripts/cortex_config_wizard.py --discover
    
    # Specify config location
    python scripts/cortex_config_wizard.py --config cortex.config.json
"""

import sys
import argparse
from pathlib import Path

# Add src to path for imports
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.plugins.configuration_wizard_plugin import Plugin as ConfigWizardPlugin


def main():
    """Main entry point for configuration wizard CLI."""
    parser = argparse.ArgumentParser(
        description="CORTEX Configuration Wizard - Progressive Setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full wizard (recommended)
  python scripts/cortex_config_wizard.py
  
  # Add single database
  python scripts/cortex_config_wizard.py --add-database
  
  # Add single API
  python scripts/cortex_config_wizard.py --add-api
  
  # Auto-discover only
  python scripts/cortex_config_wizard.py --discover

What This Does:
  1. Auto-discovers database connections (tnsnames.ora, environment, code)
  2. Auto-discovers REST APIs (OpenAPI specs, environment, code)
  3. Prompts to confirm discovered items
  4. Allows manual additions
  5. Validates connections before saving
  6. Updates cortex.config.json

Non-Blocking: Runs AFTER initial setup, no pressure to complete immediately.
        """
    )
    
    parser.add_argument(
        "--add-database",
        action="store_true",
        help="Add a single database connection"
    )
    
    parser.add_argument(
        "--add-api",
        action="store_true",
        help="Add a single API endpoint"
    )
    
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Auto-discover only (no prompts, no saving)"
    )
    
    parser.add_argument(
        "--config",
        help="Path to cortex.config.json (default: ./cortex.config.json)",
        default="cortex.config.json"
    )
    
    parser.add_argument(
        "--repo",
        help="Repository path (default: current directory)",
        default=None
    )
    
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Non-interactive mode (auto-discover and save without prompts)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="CORTEX Configuration Wizard v1.0.0"
    )
    
    args = parser.parse_args()
    
    # Determine mode
    if args.add_database:
        mode = 'add-database'
    elif args.add_api:
        mode = 'add-api'
    elif args.discover:
        mode = 'discover'
    else:
        mode = 'wizard'
    
    # Determine paths
    repo_path = Path(args.repo or Path.cwd())
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = repo_path / config_path
    
    try:
        # Initialize plugin
        plugin = ConfigWizardPlugin()
        
        if not plugin.initialize():
            print("❌ Failed to initialize configuration wizard plugin")
            return 1
        
        # Execute wizard
        result = plugin.execute({
            'mode': mode,
            'repo_path': str(repo_path),
            'config_path': str(config_path),
            'interactive': not args.non_interactive
        })
        
        # Check results
        if result.get("success"):
            print("\n" + "="*76)
            print("  Configuration Wizard Complete")
            print("="*76)
            print(f"\n✅ Databases discovered: {result.get('databases_discovered', 0)}")
            print(f"✅ Databases added: {result.get('databases_added', 0)}")
            print(f"✅ APIs discovered: {result.get('apis_discovered', 0)}")
            print(f"✅ APIs added: {result.get('apis_added', 0)}")
            
            if result.get('databases_added', 0) > 0:
                print(f"\n📋 Next steps:")
                print(f"  1. Run crawlers: cortex crawler:run")
                print(f"  2. Or test specific crawler: cortex crawler:test oracle")
            
            print()
            return 0
        else:
            print("\n❌ Configuration wizard failed!")
            
            if result.get("errors"):
                print("\nErrors:")
                for error in result["errors"]:
                    print(f"  - {error}")
            
            return 1
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Wizard interrupted by user")
        return 130
    
    except Exception as e:
        print(f"\n❌ Wizard failed with unexpected error: {e}")
        
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
