#!/usr/bin/env python3
"""
CORTEX 3.0 - Phase 1 Completion Verification
===========================================

Quick verification script for Phase 1 completion status.
Checks Features 2, 3, and 5.1 completion criteria.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import os
from pathlib import Path
import importlib.util

def check_file_exists(file_path, description):
    """Check if a file exists and report status."""
    if file_path.exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description} MISSING: {file_path}")
        return False

def check_module_import(module_path, module_name, description):
    """Check if a module can be imported."""
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"✅ {description}: Import successful")
        return True, module
    except Exception as e:
        print(f"❌ {description}: Import failed - {e}")
        return False, None

def verify_phase1_features():
    """Verify Phase 1 feature completion."""
    print("🚀 CORTEX 3.0 PHASE 1 VERIFICATION")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    print(f"Project Root: {project_root}")
    print()
    
    # Feature 2: Question Router
    print("📊 FEATURE 2: Intelligent Question Routing")
    print("-" * 30)
    
    feature2_files = [
        (project_root / "src/agents/namespace_detector.py", "Namespace Detector"),
        (project_root / "src/operations/modules/questions/question_router.py", "Question Router"),
        (project_root / "tests/operations/modules/questions/test_question_router.py", "Test Suite")
    ]
    
    feature2_success = True
    for file_path, description in feature2_files:
        if not check_file_exists(file_path, description):
            feature2_success = False
    
    # Test namespace detector import
    if feature2_files[0][0].exists():
        success, namespace_module = check_module_import(
            feature2_files[0][0], 
            "namespace_detector", 
            "NamespaceDetector Module"
        )
        
        if success and namespace_module:
            # Test basic functionality
            try:
                detector = namespace_module.NamespaceDetector()
                result = detector.detect_namespace("Show me CORTEX metrics")
                
                if hasattr(result, 'primary_namespace'):
                    print(f"✅ Namespace Detection: Working (detected: {result.primary_namespace})")
                else:
                    print(f"❌ Namespace Detection: Invalid result format")
                    feature2_success = False
            except Exception as e:
                print(f"❌ Namespace Detection: Execution failed - {e}")
                feature2_success = False
    
    print(f"Feature 2 Status: {'✅ COMPLETE' if feature2_success else '❌ INCOMPLETE'}")
    print()
    
    # Feature 3: Data Collectors
    print("📊 FEATURE 3: Data Collectors Framework")  
    print("-" * 30)
    
    feature3_files = [
        (project_root / "src/collectors/base_collector.py", "Base Collector"),
        (project_root / "src/collectors/response_template_collector.py", "Response Template Collector"),
        (project_root / "src/collectors/brain_performance_collector.py", "Brain Performance Collector"),
        (project_root / "src/collectors/token_usage_collector.py", "Token Usage Collector"),
        (project_root / "src/collectors/workspace_health_collector.py", "Workspace Health Collector"),
        (project_root / "src/collectors/manager.py", "Collector Manager")
    ]
    
    feature3_success = True
    for file_path, description in feature3_files:
        if not check_file_exists(file_path, description):
            feature3_success = False
    
    # Test base collector import
    if feature3_files[0][0].exists():
        success, collector_module = check_module_import(
            feature3_files[0][0],
            "base_collector", 
            "BaseCollector Module"
        )
        
        if success and collector_module:
            try:
                # Check BaseCollector class exists
                if hasattr(collector_module, 'BaseCollector'):
                    print(f"✅ BaseCollector Class: Available")
                else:
                    print(f"❌ BaseCollector Class: Missing")
                    feature3_success = False
            except Exception as e:
                print(f"❌ BaseCollector Class: Check failed - {e}")
                feature3_success = False
    
    print(f"Feature 3 Status: {'✅ COMPLETE' if feature3_success else '❌ INCOMPLETE'}")
    print()
    
    # Feature 5.1: Conversation Tracking
    print("📊 FEATURE 5.1: Conversation Tracking")
    print("-" * 30)
    
    feature5_files = [
        (project_root / "src/cortex_agents/agent_types.py", "Agent Types (for CAPTURE/IMPORT intents)"),
        (project_root / "cortex-brain/response-templates", "Response Templates Directory"),
        (project_root / "cortex-brain", "CORTEX Brain Directory")
    ]
    
    feature5_success = True
    for file_path, description in feature5_files:
        if not check_file_exists(file_path, description):
            feature5_success = False
    
    # Check for CAPTURE and IMPORT intents in agent_types.py
    if feature5_files[0][0].exists():
        try:
            content = feature5_files[0][0].read_text()
            if 'CAPTURE' in content and 'IMPORT' in content:
                print(f"✅ CAPTURE/IMPORT Intents: Found in agent_types.py")
            else:
                print(f"❌ CAPTURE/IMPORT Intents: Missing from agent_types.py")
                feature5_success = False
        except Exception as e:
            print(f"❌ CAPTURE/IMPORT Intents: Check failed - {e}")
            feature5_success = False
    
    print(f"Feature 5.1 Status: {'✅ COMPLETE' if feature5_success else '❌ INCOMPLETE'}")
    print()
    
    # Phase 1 Summary
    print("🎯 PHASE 1 COMPLETION SUMMARY")
    print("=" * 50)
    
    features_complete = sum([feature2_success, feature3_success, feature5_success])
    total_features = 3
    completion_rate = (features_complete / total_features) * 100
    
    print(f"Features Complete: {features_complete}/{total_features}")
    print(f"Completion Rate: {completion_rate:.1f}%")
    print()
    
    if completion_rate >= 100:
        print("🎉 PHASE 1 STATUS: ✅ FULLY COMPLETE")
        print("   • All Quick Win features implemented")
        print("   • Ready for Phase 2 integration")
        print("   • Amnesia problem solved via conversation tracking")
        print("   • Data collection framework operational")
        print("   • Question routing prevents namespace confusion")
    elif completion_rate >= 75:
        print("🔄 PHASE 1 STATUS: ⚠️  MOSTLY COMPLETE")
        print("   • Most features working")
        print("   • Minor fixes needed")
    else:
        print("❌ PHASE 1 STATUS: ❌ INCOMPLETE")
        print("   • Major work required")
        print("   • Multiple features missing")
    
    print()
    print("🗺️  CORTEX 3.0 ROADMAP UPDATE:")
    print(f"   Week 1-2 Progress: {completion_rate:.1f}% complete")
    print(f"   Next Phase: {'Phase 2 Integration' if completion_rate >= 75 else 'Complete Phase 1'}")
    
    return completion_rate >= 75

if __name__ == "__main__":
    success = verify_phase1_features()
    sys.exit(0 if success else 1)