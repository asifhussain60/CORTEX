"""
Fix deployment gates by running system alignment with interactive remediation.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from operations.modules.admin.system_alignment_orchestrator import SystemAlignmentOrchestrator

def main():
    """Execute system alignment to fix gates."""
    cortex_root = Path(__file__).parent
    orchestrator = SystemAlignmentOrchestrator(cortex_root)
    
    print("🔍 Running system alignment with remediation...")
    print()
    
    # Execute alignment - this will show interactive remediation options
    result = orchestrator.execute({})
    
    if result.success:
        print("\n✅ Alignment complete!")
        print(f"Overall Health: {result.data.get('overall_health', 'N/A')}%")
        print(f"Status: {result.data.get('status', 'N/A')}")
    else:
        print(f"\n❌ Alignment failed: {result.message}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
