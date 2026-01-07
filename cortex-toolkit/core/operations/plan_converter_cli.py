#!/usr/bin/env python3
"""
Plan Converter CLI

Command-line interface for Plan Converter Orchestrator.

Usage:
    python plan_converter_cli.py /path/to/plan

Author: CORTEX v5
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.orchestrators.plan_converter.plan_converter_orchestrator import convert_plan


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python plan_converter_cli.py /path/to/plan")
        sys.exit(1)
    
    plan_path = sys.argv[1]
    
    print(f"🔄 Plan Converter Orchestrator")
    print(f"📁 Plan: {plan_path}")
    print(f"{'=' * 60}\n")
    
    result = convert_plan(plan_path)
    
    if result['success']:
        print("✅ Conversion Successful\n")
        print(f"Mode: {result['mode']}")
        print(f"\n📊 Changes:")
        
        changes = result['changes']
        if changes['folders_created']:
            print(f"\n  Folders Created ({len(changes['folders_created'])}):")
            for folder in changes['folders_created']:
                print(f"    + {folder}/")
        
        if changes['features_converted']:
            print(f"\n  Features Converted ({len(changes['features_converted'])}):")
            for feature in changes['features_converted']:
                print(f"    ↻ {feature}")
        
        if changes.get('phase_folders_created'):
            print(f"\n  Features with Phases Populated ({len(changes['phase_folders_created'])}):")
            for feature in changes['phase_folders_created']:
                print(f"    📁 {feature} (phase-0, phase-1, phase-2, phase-3)")
        
        if changes['files_moved']:
            print(f"\n  Files Moved ({len(changes['files_moved'])}):")
            for move in changes['files_moved']:
                print(f"    → {move}")
        
        if changes['files_renamed']:
            print(f"\n  Files Renamed ({len(changes['files_renamed'])}):")
            for rename in changes['files_renamed']:
                print(f"    ✏️  {rename}")
        
        if changes['files_generated']:
            print(f"\n  Files Generated ({len(changes['files_generated'])}):")
            for gen in changes['files_generated']:
                print(f"    ✨ {gen}")
        
        verification = result['verification']
        print(f"\n✅ Verification: PASSED")
        if verification['warnings']:
            print(f"\n⚠️  Warnings ({len(verification['warnings'])}):")
            for warning in verification['warnings']:
                print(f"    • {warning}")
    
    else:
        print("❌ Conversion Failed\n")
        print(f"Error: {result['error']}")
        
        if 'verification' in result and result['verification']['errors']:
            print(f"\n🔍 Verification Errors:")
            for error in result['verification']['errors']:
                print(f"    ✗ {error}")
    
    print(f"\n📝 Conversion Log:")
    for log_entry in result['log']:
        print(f"    {log_entry}")
    
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()
