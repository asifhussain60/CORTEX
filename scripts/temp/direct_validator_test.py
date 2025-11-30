"""
Direct test of updated TestCoverageValidator to confirm fixes work.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from validation.test_coverage_validator import TestCoverageValidator

validator = TestCoverageValidator(Path.cwd())

print("=" * 80)
print("Direct Validator Test - Post-Fix")
print("=" * 80)

test_cases = [
    ("BrainIngestionAgent", "agent"),
    ("BrainIngestionAdapterAgent", "agent"),
    ("PlanningOrchestrator", "orchestrator"),
]

for feature_name, feature_type in test_cases:
    print(f"\n{feature_name} ({feature_type}):")
    print("-" * 60)
    
    # Find test file
    test_file = validator.find_test_file(feature_name, feature_type)
    print(f"  Test file: {test_file}")
    
    if not test_file:
        print("  ❌ No test file found")
        continue
    
    # Find source module
    source_module = validator._find_source_module(feature_name, feature_type)
    print(f"  Source module: {source_module}")
    
    # Get coverage
    coverage = validator.get_test_coverage(feature_name, feature_type)
    print(f"  Coverage: {coverage['coverage_pct']:.1f}%")
    print(f"  Status: {coverage['status']}")
    print(f"  Test count: {coverage['test_count']}")
    
    if coverage['coverage_pct'] >= 70:
        print("  ✅ PASS (≥70%)")
    else:
        print(f"  ❌ FAIL (need {70 - coverage['coverage_pct']:.1f}% more)")
