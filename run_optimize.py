"""
Run CORTEX Optimize Operation Directly

Bypasses the template/routing system to call OptimizeOperation directly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from operations.optimize_operation import OptimizeOperation

def run_optimize():
    """Run optimize operation directly."""
    print("🧠 CORTEX Optimize Operation")
    print("=" * 50)
    
    # Create optimizer instance
    optimizer = OptimizeOperation()
    
    # Validate prerequisites
    print("\n📋 Validating prerequisites...")
    validation_result = optimizer.validate()
    
    if not validation_result.success:
        print(f"   ❌ Validation failed: {validation_result.message}")
        return False
    
    print(f"   ✅ {validation_result.message}")
    
    # Execute optimization
    print("\n🔧 Running optimization...")
    result = optimizer.execute(target='all', aggressive=False)
    
    if result.success:
        print(f"\n✅ {result.message}")
        
        # Show results
        data = result.data
        print("\n📊 Results:")
        print(f"   • Optimizations applied: {len(data['optimizations_applied'])}")
        print(f"   • Space saved: {data['space_saved_mb']:.2f} MB")
        
        if data['optimizations_applied']:
            print("\n   Applied optimizations:")
            for opt in data['optimizations_applied']:
                print(f"      - {opt}")
        
        return True
    else:
        print(f"\n❌ Optimization failed: {result.message}")
        if result.error:
            print(f"   Error: {result.error}")
        return False

if __name__ == "__main__":
    success = run_optimize()
    sys.exit(0 if success else 1)
