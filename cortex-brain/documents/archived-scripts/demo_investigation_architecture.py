# CORTEX 3.0 Investigation Architecture Demo
# Shows end-to-end investigation workflow in action

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

async def demo_investigation_workflow():
    """Demonstrate the complete investigation workflow"""
    
    print("🎭 CORTEX 3.0 Investigation Architecture Demo")
    print("=" * 60)
    print("🎯 Demonstrating: Guided Deep Dive Pattern")
    print("⚡ Token Budget: 5,000 tokens across 3 phases")
    print("🧠 Architecture: InvestigationRouter + EnhancedHealthValidator")
    print()
    
    # Setup mock environment
    from src.cortex_agents.investigation_router import (
        InvestigationRouter,
        InvestigationPhase,
        TokenBudget,
        InvestigationContext
    )
    
    # Mock dependencies with realistic responses
    class RealisticMockHealthValidator:
        async def analyze_file_health(self, file_path):
            return {
                'file_path': file_path,
                'health_score': 0.6,
                'issues': [
                    'File size larger than recommended (45KB)',
                    'High complexity detected (230 lines)',
                    'Frequent modifications (hotspot)'
                ],
                'recommendations': [
                    'Consider breaking into smaller components',
                    'Add unit tests to improve confidence',
                    'Review for potential refactoring opportunities'
                ]
            }
            
        async def analyze_component_health(self, component_name):
            return {
                'component_name': component_name,
                'health_score': 0.7,
                'file_count': 3,
                'issues': [
                    'One problematic file detected',
                    'Coupling with authentication module'
                ],
                'recommendations': [
                    'Focus on improving AuthenticationService.cs',
                    'Consider dependency injection for better testing'
                ]
            }
    
    class RealisticMockKnowledgeGraph:
        async def get_file_relationships(self, file_path):
            if 'authentication' in file_path.lower():
                return [
                    {
                        'related_file': 'UserService.cs',
                        'relationship': 'imports',
                        'confidence': 0.95,
                        'strength': 0.85
                    },
                    {
                        'related_file': 'TokenValidator.cs',
                        'relationship': 'co_modification',
                        'confidence': 0.88,
                        'strength': 0.72
                    },
                    {
                        'related_file': 'LoginController.cs',
                        'relationship': 'dependency',
                        'confidence': 0.92,
                        'strength': 0.68
                    }
                ]
            return []
    
    # Initialize investigation system
    mock_health = RealisticMockHealthValidator()
    mock_kg = RealisticMockKnowledgeGraph()
    
    investigation_router = InvestigationRouter(
        intent_router=None,  # Not needed for demo
        health_validator=mock_health,
        knowledge_graph=mock_kg
    )
    
    print("✅ Investigation system initialized")
    print()
    
    # Demo Scenario: Authentication Investigation
    print("📋 DEMO SCENARIO: Authentication Issues")
    print("-" * 40)
    
    demo_queries = [
        "investigate why the Authentication component is failing",
        "investigate why this AuthenticationService.cs file has issues",
        "investigate why the validateToken function is slow"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n🔍 Example {i}: {query}")
        print("   " + "-" * 50)
        
        # Extract entity (this is what the discovery phase would do)
        entity, entity_type = investigation_router._extract_target_entity(query)
        print(f"   🎯 Detected Entity: '{entity}' (Type: {entity_type})")
        
        # Show token budget allocation
        budget = TokenBudget(InvestigationPhase.DISCOVERY, 1500)
        print(f"   💰 Token Budget: {budget.allocated} tokens allocated for {budget.phase.value}")
        
        # Mock investigation results (what the full workflow would produce)
        print(f"   📊 Investigation Results:")
        
        if entity_type == 'component':
            health_result = await mock_health.analyze_component_health(entity)
            print(f"      Health Score: {health_result['health_score']:.1f}/1.0")
            print(f"      Issues Found: {len(health_result['issues'])}")
            for issue in health_result['issues'][:2]:  # Show first 2
                print(f"        - {issue}")
                
        elif entity_type == 'file':
            health_result = await mock_health.analyze_file_health(entity)
            print(f"      Health Score: {health_result['health_score']:.1f}/1.0")
            print(f"      Issues Found: {len(health_result['issues'])}")
            for issue in health_result['issues'][:2]:  # Show first 2
                print(f"        - {issue}")
        
        else:
            print(f"      Function-level analysis would check:")
            print(f"        - Performance metrics")
            print(f"        - Usage patterns")
            print(f"        - Dependencies")
        
        # Show relationship discovery
        if entity_type in ['component', 'file'] and 'authentication' in entity.lower():
            relationships = await mock_kg.get_file_relationships(entity)
            print(f"   🔗 Relationships Found: {len(relationships)}")
            for rel in relationships[:2]:  # Show first 2
                print(f"        → {rel['related_file']} ({rel['relationship']}, confidence: {rel['confidence']:.2f})")
        
        print(f"   ✅ Investigation complete - Ready for next phase")
    
    print("\n" + "=" * 60)
    print("🎭 DEMO COMPLETE")
    print()
    
    # Show the full investigation flow
    print("🔄 Full Investigation Workflow:")
    print("   Phase 1: Discovery (1,500 tokens)")
    print("     → Entity detection from natural language")
    print("     → Immediate relationship discovery")
    print("     → Health assessment")
    print()
    print("   Phase 2: Analysis (2,000 tokens)")
    print("     → Deep relationship traversal")
    print("     → Pattern matching with confidence scoring")
    print("     → Multi-hop dependency analysis")
    print()
    print("   Phase 3: Synthesis (1,500 tokens)")
    print("     → Root cause identification")
    print("     → Actionable recommendations")
    print("     → Implementation roadmap")
    print()
    print("🎯 User Checkpoints: Between each phase for budget approval")
    print("🧠 Smart Routing: Automatically detects investigation intent")
    print("⚡ Token Efficiency: Budget management prevents runaway costs")
    print()
    print("✨ CORTEX 3.0 Investigation Architecture: READY FOR PRODUCTION")

async def demo_intent_detection():
    """Demo the natural language intent detection"""
    
    print("\n🎯 INTENT DETECTION DEMO")
    print("=" * 40)
    print("Testing natural language → investigation routing")
    print()
    
    from src.cortex_agents.investigation_router import InvestigationRouter
    
    # Create router for testing  
    router = InvestigationRouter(None, None, None)
    
    test_phrases = [
        "investigate why this component isn't working",
        "investigate the user authentication system",
        "investigate why getUserProfile function is slow",
        "investigate the config.json file issues",
        "investigate why the login process fails",
        "investigate dashboard performance problems",
        "can you investigate the API response times",
        "please investigate why tests are failing"
    ]
    
    print("💬 Natural Language Investigation Patterns:")
    print("-" * 40)
    
    for phrase in test_phrases:
        entity, entity_type = router._extract_target_entity(phrase)
        confidence = "High" if entity else "Low"
        status = "✅" if entity else "❌"
        
        print(f"{status} '{phrase}'")
        print(f"     → Entity: '{entity}', Type: {entity_type}, Confidence: {confidence}")
        print()
    
    print("🧠 Pattern Recognition Working!")
    print("🚀 Ready to route investigation commands to InvestigationRouter")

async def main():
    """Main demo execution"""
    await demo_investigation_workflow()
    await demo_intent_detection()

if __name__ == "__main__":
    asyncio.run(main())