"""
Generate Initial AC Test Coverage Report for CORTEX 6.0

Scans all existing CORTEX tests and generates baseline coverage report.
This establishes the "current state" before adding AC-ID markers to existing tests.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from infrastructure.ac_traceability import (
    ACTraceabilitySystem,
    TraceabilityConfig
)

def main():
    """Generate initial coverage report."""
    print("🔍 CORTEX 6.0 - Initial AC Test Coverage Report")
    print("=" * 70)
    
    # Configure traceability system
    project_root = Path(__file__).parent.parent
    config = TraceabilityConfig(
        tests_root=project_root / "tests",
        registry_path=project_root / "cortex-brain" / "registry",
        # No AC definitions file yet - will show 0% coverage initially
    )
    
    print(f"\n📁 Scanning tests directory: {config.tests_root}")
    print(f"📊 Registry output: {config.registry_path}")
    
    # Initialize system
    system = ACTraceabilitySystem(config)
    
    # Scan tests
    print("\n🔍 Scanning test files for @pytest.mark.ac_id() markers...")
    scan_results = system.scan_tests()
    
    print(f"   Found {len(scan_results)} unique AC-IDs referenced")
    
    # Show found AC-IDs
    if scan_results:
        print(f"\n📋 Referenced AC-IDs:")
        for ac_id in sorted(scan_results.keys()):
            test_count = len(scan_results[ac_id])
            print(f"   • {ac_id}: {test_count} test(s)")
    else:
        print("\n⚠️  No AC-ID markers found in existing tests (expected - they haven't been added yet)")
    
    # Generate coverage matrix
    print("\n📊 Generating coverage matrix...")
    matrix = system.generate_coverage_matrix()
    print(f"   Coverage percentage: {matrix.coverage_percentage:.1f}%")
    print(f"   Test files scanned: {matrix.metadata['scan_file_count']}")
    
    # Detect gaps (will show all tests as orphaned since no markers exist yet)
    print("\n🔍 Detecting coverage gaps...")
    gap_report = system.detect_gaps()
    print(f"   Orphaned tests (no AC-ID markers): {len(gap_report.orphaned_tests)}")
    
    # Generate comprehensive report
    output_path = config.registry_path / "ac-test-coverage.yaml"
    print(f"\n💾 Generating comprehensive report: {output_path}")
    system.generate_coverage_report(output_path)
    
    print("\n✅ Report generated successfully!")
    print(f"\n📖 Next Steps:")
    print("   1. Review baseline report in cortex-brain/registry/ac-test-coverage.yaml")
    print("   2. Add @pytest.mark.ac_id() markers to existing tests (390+ tests)")
    print("   3. Re-run this script to see coverage improve")
    print("   4. Aim for 100% coverage (all tests linked to AC-IDs)")
    
    return output_path


if __name__ == "__main__":
    main()
