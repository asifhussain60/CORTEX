"""
Run Cleanup Plugin

Simple script to execute the CORTEX cleanup plugin.

Usage:
    python run_cleanup.py [--dry-run] [--verbose]

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from plugins.cleanup_plugin import Plugin as CleanupPlugin
from plugins.base_plugin import HookPoint


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/cleanup.log', mode='a')
        ]
    )


def load_config() -> dict:
    """Load CORTEX configuration"""
    config_path = project_root / 'cortex.config.json'
    
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        sys.exit(1)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    """Main execution"""
    # Parse arguments
    dry_run = '--dry-run' in sys.argv
    verbose = '--verbose' in sys.argv
    force = '--force' in sys.argv
    
    # Setup logging
    logs_dir = project_root / 'logs'
    logs_dir.mkdir(exist_ok=True)
    setup_logging(verbose)
    
    logger = logging.getLogger(__name__)
    
    # Load configuration
    logger.info("Loading configuration...")
    config = load_config()
    
    # Override dry_run if specified in command line
    if '--dry-run' in sys.argv or not force:
        if 'plugins' not in config:
            config['plugins'] = {}
        if 'cleanup_plugin' not in config['plugins']:
            config['plugins']['cleanup_plugin'] = {}
        config['plugins']['cleanup_plugin']['dry_run'] = True
    
    if force and '--no-dry-run' in sys.argv:
        config['plugins']['cleanup_plugin']['dry_run'] = False
    
    # Print header
    print("\n" + "="*80)
    print("  CORTEX CLEANUP PLUGIN")
    print("="*80)
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Mode: {'DRY RUN (no files will be deleted)' if config['plugins']['cleanup_plugin']['dry_run'] else 'LIVE (files will be deleted)'}")
    print(f"  Root Path: {config['application']['rootPath']}")
    print("="*80 + "\n")
    
    # Confirm if not dry run
    if not config['plugins']['cleanup_plugin']['dry_run']:
        print("⚠️  WARNING: This will DELETE files from your project!")
        response = input("Are you sure you want to continue? Type 'YES' to confirm: ")
        if response != 'YES':
            print("Aborted.")
            sys.exit(0)
        print()
    
    # Initialize plugin
    logger.info("Initializing cleanup plugin...")
    plugin = CleanupPlugin()
    
    if not plugin.initialize(config):
        print("❌ Failed to initialize cleanup plugin")
        sys.exit(1)
    
    print("✅ Plugin initialized successfully\n")
    
    # Run cleanup
    logger.info("Running cleanup operations...")
    print("🧹 Running cleanup operations...\n")
    
    try:
        result = plugin.execute({'hook': HookPoint.ON_STARTUP.value})
        
        if result['success']:
            print("\n" + "="*80)
            print("  CLEANUP SUMMARY")
            print("="*80)
            
            stats = result['stats']
            print(f"  Files Scanned:       {stats['files_scanned']}")
            print(f"  Files Deleted:       {stats['files_deleted']}")
            print(f"  Files Archived:      {stats['files_archived']}")
            print(f"  Files Compressed:    {stats['files_compressed']}")
            print(f"  Directories Removed: {stats['directories_removed']}")
            print(f"  Duplicates Found:    {stats['duplicates_found']}")
            print(f"  Space Freed:         {stats['space_freed_mb']:.2f} MB ({stats['space_freed_gb']:.4f} GB)")
            print(f"  Actions Taken:       {result['actions']}")
            
            if stats['warnings']:
                print(f"\n  ⚠️  Warnings:         {len(stats['warnings'])}")
            
            if stats['errors']:
                print(f"  ❌ Errors:           {len(stats['errors'])}")
            
            print("="*80)
            
            # Print recommendations
            if result['recommendations']:
                print("\n📋 RECOMMENDATIONS:\n")
                for i, rec in enumerate(result['recommendations'], 1):
                    print(f"  {i}. {rec}")
            
            # Print report location
            print(f"\n📄 Detailed report saved to: {result['report_path']}")
            
            if config['plugins']['cleanup_plugin']['dry_run']:
                print("\n💡 This was a dry run. No files were actually deleted.")
                print("   To perform actual cleanup, run with: python run_cleanup.py --force --no-dry-run")
            else:
                print("\n✅ Cleanup completed successfully!")
            
            print()
            
        else:
            print(f"❌ Cleanup failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        logger.exception("Cleanup execution failed")
        print(f"\n❌ Cleanup failed with exception: {e}")
        sys.exit(1)
    
    # Cleanup plugin resources
    plugin.cleanup()


if __name__ == '__main__':
    main()
