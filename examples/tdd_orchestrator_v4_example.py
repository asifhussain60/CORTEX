"""
TDD Orchestrator v4.0 - Usage Example

Demonstrates how to use the unified TDD orchestrator with adaptive learning.

Version: 4.0.0
Author: CORTEX Development Team
Created: 2025-12-19
"""

import asyncio
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import TDD orchestrator components
from src.orchestrators.tdd import (
    TDDOrchestratorV4,
    TDDPhase
)
from src.orchestrators.tdd.strategies import (
    REDPhaseStrategy,
    GREENPhaseStrategy,
    REFACTORPhaseStrategy
)


async def example_basic_tdd_cycle():
    """
    Example 1: Basic TDD cycle for a simple feature.
    """
    print("\n" + "="*80)
    print("Example 1: Basic TDD Cycle - User Authentication")
    print("="*80 + "\n")
    
    # Mock dependencies (replace with real implementations)
    brain_connector = MockBrainConnector()
    knowledge_graph = MockKnowledgeGraph()
    mcp_gateway = MockMCPGateway()
    
    # Initialize orchestrator
    orchestrator = TDDOrchestratorV4(
        brain_connector=brain_connector,
        knowledge_graph=knowledge_graph,
        mcp_gateway=mcp_gateway
    )
    
    # Initialize and register strategies
    tech_discovery = orchestrator.tech_discovery
    clean_code = orchestrator.clean_code
    
    red_strategy = REDPhaseStrategy(
        mcp_gateway=mcp_gateway,
        brain_connector=brain_connector,
        knowledge_graph=knowledge_graph,
        tech_discovery=tech_discovery
    )
    
    green_strategy = GREENPhaseStrategy(
        mcp_gateway=mcp_gateway,
        brain_connector=brain_connector,
        knowledge_graph=knowledge_graph,
        clean_code_enforcer=clean_code,
        tech_discovery=tech_discovery
    )
    
    refactor_strategy = REFACTORPhaseStrategy(
        mcp_gateway=mcp_gateway,
        brain_connector=brain_connector,
        knowledge_graph=knowledge_graph,
        clean_code_enforcer=clean_code,
        tech_discovery=tech_discovery
    )
    
    orchestrator.register_strategy(TDDPhase.RED, red_strategy)
    orchestrator.register_strategy(TDDPhase.GREEN, green_strategy)
    orchestrator.register_strategy(TDDPhase.REFACTOR, refactor_strategy)
    
    # Execute TDD cycle
    result = await orchestrator.execute_tdd_cycle(
        feature_name="User Authentication",
        acceptance_criteria=[
            "Users can register with email and password",
            "Passwords must be securely hashed",
            "Email validation required",
            "Duplicate emails rejected"
        ],
        project_path=Path("./demo-project"),
        context={
            'author': 'demo-user',
            'priority': 'high'
        }
    )
    
    # Display results
    print("\n" + "-"*80)
    print("TDD Cycle Results:")
    print("-"*80)
    print(f"Success: {result['success']}")
    print(f"Feature: {result['feature']}")
    print(f"Tech Stack: {result['tech_profile'].language} + {result['tech_profile'].frameworks}")
    print("\nPhase Results:")
    
    for phase_name, phase_result in result['phases'].items():
        print(f"\n{phase_name} Phase:")
        print(f"  ✅ Success: {phase_result.success}")
        print(f"  📄 Outputs: {phase_result.outputs}")
        print(f"  📊 Metrics: {phase_result.metrics}")
    
    print("\nCycle Metrics:")
    for key, value in result['metrics'].items():
        print(f"  {key}: {value}")
    
    # Display orchestrator-level metrics
    print("\n" + "-"*80)
    print("Orchestrator Metrics:")
    print("-"*80)
    metrics = orchestrator.get_orchestrator_metrics()
    print(f"Total Cycles: {metrics['total_cycles']}")
    print(f"Successful Cycles: {metrics['successful_cycles']}")
    print(f"Success Rate: {metrics['success_rate']:.1%}")
    print(f"Patterns Learned: {metrics['patterns_learned']}")
    print(f"Technologies Discovered: {metrics['technologies_discovered']}")


async def example_multi_feature_workflow():
    """
    Example 2: Multiple features with pattern learning.
    """
    print("\n" + "="*80)
    print("Example 2: Multi-Feature Workflow with Learning")
    print("="*80 + "\n")
    
    # Initialize orchestrator (same as example 1)
    brain_connector = MockBrainConnector()
    knowledge_graph = MockKnowledgeGraph()
    mcp_gateway = MockMCPGateway()
    
    orchestrator = TDDOrchestratorV4(
        brain_connector=brain_connector,
        knowledge_graph=knowledge_graph,
        mcp_gateway=mcp_gateway
    )
    
    # Register strategies (abbreviated for example)
    tech_discovery = orchestrator.tech_discovery
    clean_code = orchestrator.clean_code
    
    orchestrator.register_strategy(
        TDDPhase.RED,
        REDPhaseStrategy(mcp_gateway, brain_connector, knowledge_graph, tech_discovery)
    )
    orchestrator.register_strategy(
        TDDPhase.GREEN,
        GREENPhaseStrategy(mcp_gateway, brain_connector, knowledge_graph, clean_code, tech_discovery)
    )
    orchestrator.register_strategy(
        TDDPhase.REFACTOR,
        REFACTORPhaseStrategy(mcp_gateway, brain_connector, knowledge_graph, clean_code, tech_discovery)
    )
    
    # Execute multiple features
    features = [
        {
            'name': 'User Registration',
            'criteria': ['Email validation', 'Password hashing', 'Duplicate check']
        },
        {
            'name': 'User Login',
            'criteria': ['Credential validation', 'Session creation', 'Rate limiting']
        },
        {
            'name': 'Password Reset',
            'criteria': ['Email verification', 'Token generation', 'Secure reset']
        }
    ]
    
    results = []
    for feature in features:
        print(f"\nProcessing: {feature['name']}...")
        result = await orchestrator.execute_tdd_cycle(
            feature_name=feature['name'],
            acceptance_criteria=feature['criteria'],
            project_path=Path("./demo-project")
        )
        results.append(result)
    
    # Display aggregate metrics
    print("\n" + "-"*80)
    print("Aggregate Metrics:")
    print("-"*80)
    metrics = orchestrator.get_orchestrator_metrics()
    print(f"Total Features Implemented: {len(features)}")
    print(f"Success Rate: {metrics['success_rate']:.1%}")
    print(f"Total Patterns Learned: {metrics['patterns_learned']}")
    print(f"Avg Patterns/Cycle: {metrics['avg_patterns_per_cycle']:.1f}")


async def example_technology_discovery():
    """
    Example 3: Technology discovery and adaptation.
    """
    print("\n" + "="*80)
    print("Example 3: Technology Discovery")
    print("="*80 + "\n")
    
    brain_connector = MockBrainConnector()
    knowledge_graph = MockKnowledgeGraph()
    mcp_gateway = MockMCPGateway()
    
    orchestrator = TDDOrchestratorV4(
        brain_connector=brain_connector,
        knowledge_graph=knowledge_graph,
        mcp_gateway=mcp_gateway
    )
    
    # Discover different project types
    projects = [
        Path("./demo-python-project"),
        Path("./demo-javascript-project"),
        Path("./demo-typescript-project")
    ]
    
    for project_path in projects:
        print(f"\nDiscovering: {project_path.name}")
        
        tech_profile = await orchestrator.tech_discovery.discover_project_tech_stack(
            project_path
        )
        
        print(f"  Language: {tech_profile.language}")
        print(f"  Frameworks: {', '.join(tech_profile.frameworks) or 'None'}")
        print(f"  Test Frameworks: {', '.join(tech_profile.test_frameworks) or 'None'}")
        print(f"  Versions: {tech_profile.version_info}")
        print(f"  Confidence: {tech_profile.confidence_score:.2f}")
        
        # Get best practices for this stack
        best_practices = await orchestrator.tech_discovery.get_best_practices(
            language=tech_profile.language,
            framework=tech_profile.frameworks[0] if tech_profile.frameworks else None
        )
        
        print(f"  Best Practices:")
        for practice in best_practices.get('recommendations', [])[:3]:
            print(f"    - {practice}")


# ============================================================================
# Mock Implementations (replace with real implementations)
# ============================================================================

class MockBrainConnector:
    """Mock brain connector for demonstration."""
    async def query(self, query: str):
        return []


class MockKnowledgeGraph:
    """Mock knowledge graph for demonstration."""
    def __init__(self):
        self.patterns = []
    
    async def store_pattern(self, pattern_id: str, pattern: dict):
        self.patterns.append({'id': pattern_id, 'data': pattern})
    
    async def query_patterns(self, filters: dict = None, limit: int = 10):
        return self.patterns[:limit]


class MockMCPGateway:
    """Mock MCP gateway for demonstration."""
    async def call_tool(self, tool_name: str, args: dict):
        return {'status': 'success', 'result': {}}


# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Run all examples."""
    try:
        # Example 1: Basic TDD cycle
        await example_basic_tdd_cycle()
        
        # Example 2: Multi-feature workflow
        await example_multi_feature_workflow()
        
        # Example 3: Technology discovery
        await example_technology_discovery()
        
        print("\n" + "="*80)
        print("All examples completed successfully!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
