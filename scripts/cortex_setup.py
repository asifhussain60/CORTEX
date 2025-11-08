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


def setup_extension(args):
    """Setup VS Code extension project (Phase 3)"""
    print("\n" + "=" * 60)
    print("CORTEX VS Code Extension Setup (Phase 3)")
    print("=" * 60 + "\n")
    
    print("This will generate a complete VS Code extension project:")
    print("  ✓ TypeScript extension with @cortex chat participant")
    print("  ✓ Python ↔ TypeScript bridge")
    print("  ✓ Automatic conversation capture")
    print("  ✓ Token dashboard sidebar")
    print("  ✓ Lifecycle hooks (focus/blur, checkpoint)")
    print("  ✓ External monitoring (@copilot capture)")
    print("  ✓ Build and package scripts")
    print("  ✓ Complete test infrastructure")
    print()
    
    try:
        # Import plugin system
        from src.plugins.extension_scaffold_plugin import Plugin as ExtensionScaffoldPlugin
        
        # Create plugin instance
        plugin = ExtensionScaffoldPlugin()
        
        # Initialize plugin
        if not plugin.initialize():
            print("❌ Failed to initialize extension scaffold plugin")
            return 1
        
        # Execute scaffolding
        print(f"📦 Generating extension at: {args.extension_dir}\n")
        
        result = plugin.execute({
            "extension_name": "cortex",
            "display_name": "CORTEX - Cognitive Development Partner",
            "publisher": "cortex-team",
            "repository": "https://github.com/asifhussain60/CORTEX",
            "output_dir": args.extension_dir,
            "features": [
                "chat_participant",
                "conversation_capture",
                "lifecycle_hooks",
                "external_monitoring",
                "resume_prompts",
                "checkpoint_system",
                "token_dashboard"
            ]
        })
        
        if result.get("success"):
            print("\n✅ Extension scaffolded successfully!\n")
            print("📁 Output directory:", result["output_dir"])
            print()
            print("📋 Next steps:")
            for i, step in enumerate(result["next_steps"], 1):
                print(f"  {i}. {step}")
            print()
            
            # Offer to install dependencies
            if input("Install npm dependencies now? (y/N): ").lower() == 'y':
                print("\n📦 Installing dependencies...")
                import subprocess
                import os
                
                os.chdir(args.extension_dir)
                subprocess.run(["npm", "install"], check=True)
                print("✅ Dependencies installed!\n")
                
                # Offer to compile
                if input("Compile TypeScript now? (y/N): ").lower() == 'y':
                    print("\n🔨 Compiling TypeScript...")
                    subprocess.run(["npm", "run", "compile"], check=True)
                    print("✅ Compilation successful!\n")
                    
                    # Offer to package
                    if input("Package extension (.vsix)? (y/N): ").lower() == 'y':
                        print("\n📦 Packaging extension...")
                        subprocess.run(["npm", "run", "package"], check=True)
                        print("✅ Extension packaged!\n")
                        
                        # Offer to install
                        if args.install_extension or input("Install to VS Code now? (y/N): ").lower() == 'y':
                            print("\n🚀 Installing extension...")
                            vsix_file = "cortex-1.0.0.vsix"
                            subprocess.run(["code", "--install-extension", vsix_file], check=True)
                            print("✅ Extension installed!\n")
                            print("🔄 Please restart VS Code to activate CORTEX extension.")
            
            print("\n📖 Documentation:")
            print(f"  • README: {args.extension_dir}/README.md")
            print(f"  • Changelog: {args.extension_dir}/CHANGELOG.md")
            print()
            print("🎉 Phase 3 (Extension Scaffold) complete!")
            print("   Run tests with: npm test")
            print("   Debug with: Press F5 in VS Code\n")
            
            return 0
        else:
            print(f"\n❌ Extension scaffolding failed: {result.get('error')}")
            return 1
            
    except ImportError as e:
        print(f"❌ Failed to import extension scaffold plugin: {e}")
        print("   Make sure CORTEX core is properly installed.")
        return 1
    
    except Exception as e:
        print(f"\n❌ Extension setup failed: {e}")
        
        if not args.quiet:
            import traceback
            print("\nFull traceback:")
            traceback.print_exc()
        
        return 1


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
    
    parser.add_argument(
        "--setup-extension",
        action="store_true",
        help="Generate VS Code extension project (Phase 3)"
    )
    
    parser.add_argument(
        "--extension-dir",
        help="Output directory for extension (default: cortex-extension)",
        default="cortex-extension"
    )
    
    parser.add_argument(
        "--install-extension",
        action="store_true",
        help="Install extension to VS Code after generation"
    )
    
    args = parser.parse_args()
    
    # Handle extension scaffolding separately
    if args.setup_extension:
        return setup_extension(args)
    
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
