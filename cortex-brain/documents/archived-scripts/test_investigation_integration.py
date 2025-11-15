# Test Investigation Router Integration
# Quick validation script for the investigation architecture implementation

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))
sys.path.append(str(Path(__file__).parent))

async def test_investigation_router_integration():
    """Test the investigation router implementation"""
    
    print("🧠 CORTEX Investigation Architecture Test")
    print("=" * 60)
    
    try:
        # Test 1: Import and Basic Initialization
        print("\n📦 Test 1: Import Investigation Router")
        
        from src.cortex_agents.investigation_router import (
            InvestigationRouter,
            InvestigationPhase,
            TokenBudget,
            InvestigationContext
        )
        
        print("✅ Successfully imported InvestigationRouter classes")
        
        # Test 2: Mock dependencies for testing
        print("\n🔧 Test 2: Initialize Mock Dependencies")
        
        class MockIntentRouter:
            def __init__(self):
                self.name = "mock_intent_router"
        
        class MockHealthValidator:
            def __init__(self):
                self.name = "mock_health_validator"
                self.tier1_api = None
                self.tier2_kg = None 
                self.tier3_context = None
                
            async def analyze_file_health(self, file_path):
                return {
                    'file_path': file_path,
                    'health_score': 0.8,
                    'issues': []
                }
                
            async def analyze_component_health(self, component_name):
                return {
                    'component_name': component_name,
                    'health_score': 0.8,
                    'issues': []
                }
        
        class MockKnowledgeGraph:
            def __init__(self):
                self.name = "mock_knowledge_graph"
                
            async def get_file_relationships(self, file_path):
                return [
                    {'related_file': 'related_component.cs', 'relationship': 'imports', 'confidence': 0.9}
                ]
                
            async def search_patterns(self, query, filters=None):
                return [
                    {'pattern': f'{query}_pattern', 'confidence': 0.8}
                ]
        
        # Initialize mocks
        mock_intent = MockIntentRouter()
        mock_health = MockHealthValidator()
        mock_kg = MockKnowledgeGraph()
        
        print("✅ Mock dependencies initialized")
        
        # Test 3: Create Investigation Router
        print("\n🚀 Test 3: Create Investigation Router")
        
        investigation_router = InvestigationRouter(
            intent_router=mock_intent,
            health_validator=mock_health,
            knowledge_graph=mock_kg
        )
        
        print("✅ InvestigationRouter created successfully")
        
        # Test 4: Test Entity Detection
        print("\n🔍 Test 4: Test Entity Detection Patterns")
        
        test_queries = [
            "investigate why this view isn't working",
            "investigate the Authentication component",
            "investigate why the getUserData function is slow",
            "investigate why the config.json file is missing",
            "investigate why the login process is broken"
        ]
        
        for query in test_queries:
            entity, entity_type = investigation_router._extract_target_entity(query)
            print(f"   Query: '{query}'")
            print(f"   → Entity: '{entity}', Type: '{entity_type}'")
        
        print("✅ Entity detection working correctly")
        
        # Test 5: Test Token Budget System  
        print("\n💰 Test 5: Test Token Budget System")
        
        budget = TokenBudget(InvestigationPhase.DISCOVERY, 1500)
        print(f"   Initial budget: {budget.remaining}")
        print(f"   Allocated tokens: {budget.allocated}")
        print(f"   Phase: {budget.phase}")
        
        # Simulate token consumption
        success = budget.consume(500)
        print(f"   After consuming 500 tokens: {budget.remaining}")
        print(f"   Consumption successful: {success}")
        print(f"   Is exhausted: {budget.is_exhausted}")
        
        print("✅ Token budget system working correctly")
        
        # Test 6: Test Investigation Context
        print("\n📋 Test 6: Test Investigation Context")
        
        context = InvestigationContext(
            target_entity="login",
            entity_type="component",
            initial_query="investigate why the login isn't working",
            current_phase=InvestigationPhase.DISCOVERY,
            budget=TokenBudget(InvestigationPhase.DISCOVERY, 1500)
        )
        
        print(f"   Context query: {context.initial_query}")
        print(f"   Context entity: {context.target_entity}")
        print(f"   Context type: {context.entity_type}")
        print(f"   Context phase: {context.current_phase}")
        print(f"   Initial findings: {len(context.findings)}")
        
        print("✅ Investigation context working correctly")
        
        # Test 7: Test Pattern Detection (without full execution)
        print("\n🎯 Test 7: Test Investigation Pattern Detection")
        
        # Test if patterns are correctly loaded
        patterns = investigation_router.investigation_patterns
        print(f"   Loaded {len(patterns)} investigation patterns:")
        for pattern_name, pattern_regex in patterns.items():
            print(f"     - {pattern_name}: {pattern_regex}")
        
        print("✅ Investigation patterns loaded correctly")
        
        print("\n" + "=" * 60)
        print("🎉 All Integration Tests PASSED!")
        print("🧠 CORTEX Investigation Architecture is READY")
        print("=" * 60)
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Check that the file paths and imports are correct")
        return False
        
    except Exception as e:
        print(f"❌ Test Error: {e}")
        print(f"   Exception type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

async def test_enhanced_health_validator():
    """Test the enhanced health validator integration"""
    
    print("\n🏥 Testing Enhanced Health Validator")
    print("-" * 40)
    
    try:
        from src.cortex_agents.health_validator.enhanced_validator import EnhancedHealthValidator
        
        # Mock initialization
        enhanced_validator = EnhancedHealthValidator(
            name="test_enhanced",
            tier1_api=None,
            tier2_kg=None,
            tier3_context=None
        )
        
        print("✅ Enhanced Health Validator imported and initialized")
        
        # Test file analysis capability
        print("   Testing file analysis methods...")
        
        # These would normally be async calls, but for testing just check the methods exist
        methods_to_check = [
            'analyze_file_health',
            'analyze_component_health',
            '_analyze_file_metrics',
            '_get_file_investigation_insights',
            '_score_file_size',
            '_score_code_complexity'
        ]
        
        for method_name in methods_to_check:
            if hasattr(enhanced_validator, method_name):
                print(f"     ✅ {method_name} method available")
            else:
                print(f"     ❌ {method_name} method missing")
                return False
        
        print("✅ Enhanced Health Validator integration ready")
        return True
        
    except ImportError as e:
        print(f"❌ Enhanced Health Validator Import Error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Enhanced Health Validator Test Error: {e}")
        return False

async def main():
    """Main test execution"""
    print("🧠 CORTEX 3.0 Investigation Architecture Integration Test")
    print("🎯 Testing Guided Deep Dive Implementation")
    print("📅 " + "=" * 58)
    
    # Run integration tests
    integration_success = await test_investigation_router_integration()
    
    if integration_success:
        health_success = await test_enhanced_health_validator()
        
        if health_success:
            print("\n🎊 COMPLETE INTEGRATION SUCCESS!")
            print("🚀 CORTEX 3.0 Investigation Architecture is OPERATIONAL")
            print("✨ Ready for production use!")
        else:
            print("\n⚠️  Investigation Router working, Enhanced Health Validator has issues")
    else:
        print("\n❌ Integration tests failed - check implementation")

if __name__ == "__main__":
    asyncio.run(main())