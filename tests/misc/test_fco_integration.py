#!/usr/bin/env python3
"""
Feature Completion Orchestrator Integration Test

Quick test to verify the concrete orchestrator implementation works correctly.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.feature_completion_orchestrator_concrete import (
    ConcreteFeatureCompletionOrchestrator,
    FeatureCompletionOrchestratorFactory
)

async def test_orchestrator_initialization():
    """Test basic orchestrator initialization"""
    print("🧪 Testing Orchestrator Initialization...")
    
    workspace_path = "/Users/asifhussain/PROJECTS/CORTEX"
    
    try:
        # Test factory creation
        orchestrator = FeatureCompletionOrchestratorFactory.create_for_workspace(workspace_path)
        print("✅ Factory creation successful")
        
        # Test health check
        health = await orchestrator.health_check()
        print(f"✅ Health check complete: {health['overall']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False

async def test_mock_orchestration():
    """Test mock orchestration workflow"""
    print("\n🧪 Testing Mock Orchestration...")
    
    workspace_path = "/Users/asifhussain/PROJECTS/CORTEX"
    
    try:
        from src.agents.feature_completion_orchestrator_concrete import MockFeatureCompletionOrchestrator
        
        orchestrator = MockFeatureCompletionOrchestrator(workspace_path)
        
        # Test mock workflow
        report = await orchestrator.orchestrate_feature_completion("Test feature implementation")
        print("✅ Mock orchestration successful")
        print(f"📊 Report summary: {report.execution_status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Mock orchestration failed: {e}")
        return False

async def test_feature_detection():
    """Test feature completion detection"""
    print("\n🧪 Testing Feature Detection...")
    
    workspace_path = "/Users/asifhussain/PROJECTS/CORTEX"
    
    try:
        orchestrator = FeatureCompletionOrchestratorFactory.create_orchestrator(
            workspace_path, "mock"
        )
        
        # Test detection patterns
        test_inputs = [
            "Feature implementation complete",
            "Completed the authentication feature",
            "Done with user management system",
            "Just regular conversation"
        ]
        
        for input_text in test_inputs:
            feature_name = orchestrator.detect_feature_completion(input_text)
            result = "detected" if feature_name else "not detected"
            print(f"  '{input_text}' → {result}")
        
        print("✅ Feature detection tests complete")
        return True
        
    except Exception as e:
        print(f"❌ Feature detection failed: {e}")
        return False

async def main():
    """Run all integration tests"""
    print("🚀 Feature Completion Orchestrator Integration Tests\n")
    
    # Configure logging
    logging.basicConfig(
        level=logging.WARNING,  # Reduce noise during testing
        format='%(levelname)s: %(message)s'
    )
    
    tests = [
        test_orchestrator_initialization,
        test_mock_orchestration,
        test_feature_detection
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if await test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))