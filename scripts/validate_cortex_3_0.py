#!/usr/bin/env python3
"""
CORTEX 3.0 Infrastructure Validation Script
===========================================

Quick validation of CORTEX 3.0 readiness without complex dependencies.
Tests core architecture elements, validates roadmap assumptions.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_cortex_3_0_structure():
    """Test CORTEX 3.0 directory structure and core files"""
    print("🔍 CORTEX 3.0 Infrastructure Validation")
    print("=" * 50)
    
    results = {}
    
    # Check core 3.0 directory exists
    cortex_3_0_dir = project_root / "src" / "cortex_3_0"
    results['cortex_3_0_dir'] = cortex_3_0_dir.exists()
    print(f"✅ CORTEX 3.0 Directory: {cortex_3_0_dir.exists()}")
    
    if cortex_3_0_dir.exists():
        # Check core files
        core_files = [
            "unified_interface.py",
            "enhanced_agents.py", 
            "dual_channel_memory.py",
            "smart_context_intelligence.py"
        ]
        
        for file in core_files:
            file_path = cortex_3_0_dir / file
            exists = file_path.exists()
            size = file_path.stat().st_size if exists else 0
            results[f'file_{file}'] = {'exists': exists, 'size': size}
            status = "✅" if exists else "❌"
            print(f"{status} {file}: {exists} ({size:,} bytes)")
    
    # Check roadmap document
    roadmap_path = project_root / "cortex-brain" / "cortex-3.0-design" / "CORTEX-3.0-ROADMAP.yaml"
    results['roadmap'] = roadmap_path.exists()
    roadmap_size = roadmap_path.stat().st_size if roadmap_path.exists() else 0
    print(f"✅ Fast Track Roadmap: {roadmap_path.exists()} ({roadmap_size:,} bytes)")
    
    # Check design documents
    design_dir = project_root / "cortex-brain" / "cortex-3.0-design"
    if design_dir.exists():
        design_files = list(design_dir.glob("*.md")) + list(design_dir.glob("*.yaml"))
        results['design_docs'] = len(design_files)
        print(f"✅ Design Documents: {len(design_files)} files")
    
    # Calculate infrastructure completion percentage
    core_files_present = sum(1 for key in results if key.startswith('file_') and results[key]['exists'])
    total_core_files = 4
    completion_percentage = (core_files_present / total_core_files) * 100
    
    print("\n" + "=" * 50)
    print(f"📊 Infrastructure Completion: {completion_percentage:.0f}%")
    
    if completion_percentage >= 70:
        print("✅ CORTEX 3.0 READY FOR IMPLEMENTATION")
    elif completion_percentage >= 50:
        print("⚠️ CORTEX 3.0 PARTIALLY READY - Some setup needed")
    else:
        print("❌ CORTEX 3.0 NOT READY - Significant setup required")
    
    return results

def validate_roadmap_readiness():
    """Validate Fast Track roadmap assumptions"""
    print("\n🎯 Fast Track Roadmap Validation")
    print("=" * 50)
    
    roadmap_path = project_root / "cortex-brain" / "cortex-3.0-design" / "CORTEX-3.0-ROADMAP.yaml"
    
    if not roadmap_path.exists():
        print("❌ Roadmap not found")
        return False
    
    # Read roadmap size and basic validation
    with open(roadmap_path, 'r') as f:
        content = f.read()
    
    lines = len(content.splitlines())
    chars = len(content)
    
    print(f"✅ Roadmap Size: {lines:,} lines, {chars:,} characters")
    
    # Check for key roadmap elements
    key_elements = [
        "fast_track_execution",
        "phase_1_quick_wins", 
        "phase_2_high_value_features",
        "11 weeks",
        "Feature 1",
        "Feature 2", 
        "Feature 3"
    ]
    
    found_elements = []
    for element in key_elements:
        if element in content:
            found_elements.append(element)
            print(f"✅ Found: {element}")
        else:
            print(f"❌ Missing: {element}")
    
    readiness = len(found_elements) / len(key_elements) * 100
    print(f"\n📊 Roadmap Readiness: {readiness:.0f}%")
    
    return readiness >= 80

def main():
    """Main validation function"""
    print("CORTEX 3.0 Infrastructure Validation")
    print("Date:", os.environ.get('date', 'Unknown'))
    print()
    
    # Test infrastructure
    infra_results = test_cortex_3_0_structure()
    
    # Test roadmap readiness
    roadmap_ready = validate_roadmap_readiness()
    
    print("\n" + "=" * 50)
    print("🎯 FINAL ASSESSMENT")
    print("=" * 50)
    
    # Calculate overall readiness
    core_files = [k for k in infra_results if k.startswith('file_')]
    core_complete = sum(1 for k in core_files if infra_results[k]['exists'])
    infra_percentage = (core_complete / len(core_files)) * 100 if core_files else 0
    
    if infra_percentage >= 70 and roadmap_ready:
        print("✅ CORTEX 3.0 READY FOR FAST TRACK EXECUTION")
        print("   Recommendation: Proceed with Week 1-2 Quick Wins")
        return 0
    elif infra_percentage >= 50:
        print("⚠️ CORTEX 3.0 PARTIALLY READY")
        print("   Recommendation: Address missing components first")
        return 1
    else:
        print("❌ CORTEX 3.0 NOT READY")
        print("   Recommendation: Complete foundational setup")
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)