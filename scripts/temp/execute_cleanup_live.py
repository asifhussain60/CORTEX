"""
Execute CORTEX Cleanup in LIVE mode

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.operations.modules.cleanup.cleanup_orchestrator import CleanupOrchestrator


def main():
    """Execute live cleanup"""
    print("\n" + "=" * 80)
    print("CORTEX CLEANUP ORCHESTRATOR - LIVE EXECUTION")
    print("=" * 80)
    print("\n⚠️  WARNING: This will DELETE files from your project!\n")
    
    response = input("Type 'YES' to confirm live cleanup execution: ")
    if response != 'YES':
        print("\n❌ Cleanup cancelled.")
        return
    
    print("\n🚀 Starting live cleanup...\n")
    
    # Initialize orchestrator
    orchestrator = CleanupOrchestrator(project_root)
    
    # Execute cleanup in LIVE mode
    result = orchestrator.execute({
        'profile': 'standard',
        'dry_run': False  # LIVE MODE
    })
    
    if result.success:
        print("\n" + "=" * 80)
        print("✅ CLEANUP COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
        metrics = result.data.get('metrics', {})
        print(f"\n📊 Summary:")
        print(f"   • Backups deleted: {metrics.get('backups_deleted', 0)}")
        print(f"   • Files reorganized: {metrics.get('files_reorganized', 0)}")
        print(f"   • Root files cleaned: {metrics.get('root_files_cleaned', 0)}")
        print(f"   • Space freed: {metrics.get('space_freed_mb', 0):.2f} MB")
        print(f"   • Duration: {metrics.get('duration_seconds', 0):.2f} seconds")
        
        if metrics.get('warnings'):
            print(f"\n⚠️  Warnings ({len(metrics['warnings'])}):")
            for warning in metrics['warnings'][:5]:  # Show first 5
                print(f"   • {warning}")
        
        if metrics.get('errors'):
            print(f"\n❌ Errors ({len(metrics['errors'])}):")
            for error in metrics['errors'][:5]:  # Show first 5
                print(f"   • {error}")
        
        print("\n✅ Cleanup operation completed!\n")
        
    else:
        print("\n" + "=" * 80)
        print("❌ CLEANUP FAILED")
        print("=" * 80)
        print(f"\nError: {result.message}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
