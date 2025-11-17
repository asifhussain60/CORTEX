#!/usr/bin/env python3
"""
CORTEX Master Migration Runner
Orchestrates all three tier migrations in sequence

Sub-Group 3A: Phase 0.5 - Migration Tools
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
import argparse


def run_command(cmd: list, description: str) -> bool:
    """
    Run a command and return success status
    
    Args:
        cmd: Command to run as list
        description: Description of what's being done
        
    Returns:
        True if successful, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(str(c) for c in cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Run all CORTEX tier migrations'
    )
    parser.add_argument(
        '--brain-dir',
        type=Path,
        help='Path to cortex-brain directory',
        default=Path(__file__).parent.parent.parent.parent / 'cortex-brain'
    )
    parser.add_argument(
        '--skip-tier1',
        action='store_true',
        help='Skip Tier 1 migration'
    )
    parser.add_argument(
        '--skip-tier2',
        action='store_true',
        help='Skip Tier 2 migration'
    )
    parser.add_argument(
        '--skip-tier3',
        action='store_true',
        help='Skip Tier 3 migration'
    )
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip validation step'
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("CORTEX BRAIN MIGRATION")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Brain directory: {args.brain_dir}")
    
    scripts_dir = Path(__file__).parent.parent
    tier1_script = scripts_dir / 'tier1' / 'migrate_tier1.py'
    tier2_script = scripts_dir / 'tier2' / 'migrate_tier2.py'
    tier3_script = scripts_dir / 'tier3' / 'migrate_tier3.py'
    validation_script = Path(__file__).parent / 'test_migration.py'
    
    results = {}
    
    # Tier 1 Migration
    if not args.skip_tier1:
        results['tier1'] = run_command(
            [sys.executable, str(tier1_script)],
            "Tier 1 Migration (Working Memory - JSONL to SQLite)"
        )
    else:
        print("\n⏭️  Skipping Tier 1 migration")
        results['tier1'] = True
    
    # Tier 2 Migration
    if not args.skip_tier2:
        results['tier2'] = run_command(
            [sys.executable, str(tier2_script)],
            "Tier 2 Migration (Knowledge Graph - YAML to SQLite with FTS5)"
        )
    else:
        print("\n⏭️  Skipping Tier 2 migration")
        results['tier2'] = True
    
    # Tier 3 Migration
    if not args.skip_tier3:
        results['tier3'] = run_command(
            [sys.executable, str(tier3_script)],
            "Tier 3 Migration (Development Context - YAML to JSON)"
        )
    else:
        print("\n⏭️  Skipping Tier 3 migration")
        results['tier3'] = True
    
    # Validation
    if not args.skip_validation:
        results['validation'] = run_command(
            [sys.executable, str(validation_script), '--brain-dir', str(args.brain_dir)],
            "Migration Validation (End-to-End)"
        )
    else:
        print("\n⏭️  Skipping validation")
        results['validation'] = True
    
    # Summary
    print("\n" + "="*60)
    print("MIGRATION SUMMARY")
    print("="*60)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for step, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{step.capitalize()}: {status}")
    
    all_success = all(results.values())
    
    if all_success:
        print("\n🎉 All migrations completed successfully!")
        print("\nNext steps:")
        print("  1. Review migration logs above")
        print("  2. Backup original YAML/JSONL files")
        print("  3. Test CORTEX functionality with new databases")
        sys.exit(0)
    else:
        print("\n❌ Some migrations failed - review errors above")
        sys.exit(1)


if __name__ == '__main__':
    main()
