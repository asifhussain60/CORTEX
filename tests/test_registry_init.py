#!/usr/bin/env python3
"""
Test script to verify DatabaseBackedRegistry initialization.
"""

import sys
import os
sys.path.append('.')

def test_registry_init():
    """Test clean registry initialization."""
    print("🔍 Testing DatabaseBackedRegistry initialization...")
    
    # Check file system state
    cortex_dir = ".cortex"
    db_file = ".cortex/orchestrator_registry.db"
    
    print(f"📁 .cortex directory exists: {os.path.exists(cortex_dir)}")
    print(f"📁 Database file exists: {os.path.exists(db_file)}")
    
    # Test initialization
    try:
        from cortex.orchestrators import initialize_registry
        
        print("🚀 Running initialize_registry()...")
        result = initialize_registry()
        
        if result.is_ok():
            print("✅ SUCCESS: Registry initialized successfully")
            
            # Get orchestrator count
            from cortex.orchestrators import get_database_registry
            registry = get_database_registry()
            orchestrators = registry.get_all_orchestrators()
            print(f"📊 Total orchestrators registered: {len(orchestrators)}")
            
            # Show sample
            if orchestrators:
                print("\n📋 Sample orchestrators:")
                for i, orch in enumerate(orchestrators[:8]):
                    print(f"  {i+1:2}. {orch.name} ({orch.category.value})")
                    
                if len(orchestrators) > 8:
                    print(f"  ... and {len(orchestrators) - 8} more")
                    
                # Show categories
                from collections import Counter
                categories = Counter(orch.category.value for orch in orchestrators)
                print(f"\n📊 By category: {dict(categories)}")
                
                # Check database file was created
                print(f"\n💾 Database file created: {os.path.exists(db_file)}")
                if os.path.exists(db_file):
                    size = os.path.getsize(db_file)
                    print(f"    Size: {size} bytes")
        else:
            print(f"❌ FAILED: {result.error}")
            return False
            
    except Exception as e:
        import traceback
        print(f"❌ ERROR: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_total_recall():
    """Test TotalRecallAgent after registry is initialized."""
    print("\n🧠 Testing TotalRecallAgent...")
    
    try:
        from cortex.tools.total_recall_agent import TotalRecallAgent, FeatureScope
        
        agent = TotalRecallAgent()
        print("✅ TotalRecallAgent created successfully")
        
        # Test recall for a known feature
        print("🔍 Testing recall for 'circuit breaker'...")
        result = agent.recall("circuit breaker", scope=FeatureScope.INFRASTRUCTURE)
        
        print(f"📋 Recall results: {len(result.matches)} matches")
        if result.matches:
            match = result.matches[0]
            print(f"  Best match: {match.component.name}")
            print(f"  Entry point: {match.component.entry_point}")
            print(f"  Test status: {match.component.test_status}")
        
        return True
        
    except Exception as e:
        import traceback
        print(f"❌ TotalRecallAgent error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 CORTEX Registry Initialization Test")
    print("=" * 60)
    
    success = test_registry_init()
    
    if success:
        success = test_total_recall()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED")
        print("✅ DatabaseBackedRegistry migration verified successfully")
    else:
        print("❌ TESTS FAILED")
        print("🔧 Registry needs debugging")
    print("=" * 60)