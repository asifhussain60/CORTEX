"""
Test script for ArchitectureCollectorV2 - validates universal architecture collection.

Tests the complete Phase 4 implementation by analyzing the CORTEX codebase itself.
"""

import sys
from pathlib import Path

# Add project root to path
# This file is in src/dashboard/collectors/, so parent.parent.parent gets to CORTEX root
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.dashboard.collectors import ArchitectureCollectorV2
import json


def test_cortex_analysis():
    """Test ArchitectureCollectorV2 by analyzing CORTEX itself."""
    
    print("\n" + "="*80)
    print("🧪 Testing ArchitectureCollectorV2 on CORTEX Repository")
    print("="*80 + "\n")
    
    # Initialize collector
    root_path = project_root
    collector = ArchitectureCollectorV2(
        root_path=root_path,
        project_name="CORTEX",
        max_workers=4,
        enable_cache=True
    )
    
    # Run collection
    result = collector.collect()
    
    # Validate results
    print("\n" + "="*80)
    print("📋 Validation Results")
    print("="*80)
    
    validations = []
    
    # Check basic fields
    validations.append(("Project name set", result.project_name == "CORTEX"))
    validations.append(("Project path set", result.project_path != ""))
    validations.append(("Scan timestamp set", result.scan_timestamp != ""))
    
    # Check file discovery
    validations.append(("Files discovered", result.total_files > 0))
    validations.append(("Python files found", 'python' in result.languages))
    
    # Check aggregation
    validations.append(("Total lines calculated", result.total_lines > 0))
    validations.append(("Components counted", len(result.components) > 0))
    
    # Check architecture detection
    validations.append(("Architecture type detected", result.architecture_type != "Unknown"))
    validations.append(("Layers identified", len(result.layers) > 0))
    
    # Check tech stack
    validations.append(("Dependencies tracked", len(result.dependencies) > 0))
    
    # Print validation results
    passed = 0
    failed = 0
    
    for check_name, check_result in validations:
        status = "✅ PASS" if check_result else "❌ FAIL"
        print(f"{status:12} {check_name}")
        if check_result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*80}")
    print(f"Total: {passed} passed, {failed} failed out of {len(validations)} checks")
    print(f"{'='*80}\n")
    
    # Display summary
    print("\n" + "="*80)
    print("📊 Architecture Summary")
    print("="*80)
    print(f"Project: {result.project_name}")
    print(f"Architecture: {result.architecture_type}")
    print(f"Layers: {', '.join(result.layers)}")
    print(f"Patterns: {', '.join(result.patterns)}")
    print(f"\nFiles: {result.total_files}")
    print(f"Lines of Code: {result.total_lines:,}")
    print(f"\nLanguages:")
    for lang, count in sorted(result.languages.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {lang}: {count} files")
    
    print(f"\nComponents:")
    for comp_type, count in sorted(result.components.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {comp_type}: {count}")
    
    print(f"\nComplexity:")
    print(f"  - Average: {result.complexity.get('average', 0)}")
    print(f"  - Total: {result.complexity.get('total', 0)}")
    
    if result.errors:
        print(f"\nErrors: {len(result.errors)}")
        for error in result.errors[:5]:  # Show first 5
            print(f"  - {error}")
    
    if result.warnings:
        print(f"\nWarnings: {len(result.warnings)}")
        for warning in result.warnings[:5]:  # Show first 5
            print(f"  - {warning}")
    
    print(f"\n{'='*80}\n")
    
    # Save to file
    output_path = project_root / 'cortex-brain' / 'dashboards' / 'CORTEX' / 'architecture-v2.json'
    collector.save_to_json(result, output_path)
    
    return passed == len(validations)


def test_small_project():
    """Test with just the analyzers directory (smaller scope)."""
    
    print("\n" + "="*80)
    print("🧪 Testing ArchitectureCollectorV2 on Analyzers Module")
    print("="*80 + "\n")
    
    # Analyze just the analyzers directory
    analyzers_path = project_root / 'src' / 'dashboard' / 'analyzers'
    
    collector = ArchitectureCollectorV2(
        root_path=analyzers_path,
        project_name="Dashboard Analyzers",
        max_workers=2,
        enable_cache=False
    )
    
    result = collector.collect()
    
    print("\n" + "="*80)
    print("📊 Analyzers Module Summary")
    print("="*80)
    print(f"Files: {result.total_files}")
    print(f"Languages: {list(result.languages.keys())}")
    print(f"Total Lines: {result.total_lines:,}")
    print(f"Components: {dict(result.components)}")
    print(f"{'='*80}\n")
    
    return result.total_files > 0


if __name__ == "__main__":
    print("\n🚀 Starting ArchitectureCollectorV2 Test Suite\n")
    
    try:
        # Test 1: Full CORTEX analysis
        test1_passed = test_cortex_analysis()
        
        # Test 2: Small module analysis
        test2_passed = test_small_project()
        
        # Summary
        print("\n" + "="*80)
        print("🏁 Test Suite Complete")
        print("="*80)
        print(f"Test 1 (Full CORTEX): {'✅ PASSED' if test1_passed else '❌ FAILED'}")
        print(f"Test 2 (Analyzers Module): {'✅ PASSED' if test2_passed else '❌ FAILED'}")
        
        if test1_passed and test2_passed:
            print(f"\n✅ All tests passed!")
            sys.exit(0)
        else:
            print(f"\n❌ Some tests failed")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
