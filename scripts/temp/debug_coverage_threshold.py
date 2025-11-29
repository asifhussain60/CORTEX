"""Debug alignment orchestrator test coverage logic."""
import sys
from pathlib import Path

cortex_root = Path(__file__).parent
sys.path.insert(0, str(cortex_root / "src"))

from validation.test_coverage_validator import TestCoverageValidator

project_root = cortex_root
validator = TestCoverageValidator(project_root)

critical = [
    "HolisticCleanupOrchestrator",
    "SetupEPMOrchestrator",
    "ADOWorkItemOrchestrator",
    "DemoOrchestrator",
    "UnifiedEntryPointOrchestrator"
]

for name in critical:
    print(f"\n{'='*60}")
    print(f"{name}")
    print('='*60)
    
    coverage = validator.get_test_coverage(name, "orchestrator")
    
    print(f"Has tests: {coverage.get('has_tests', False)}")
    print(f"Coverage %: {coverage.get('coverage_pct', 0)}")
    print(f"Test file: {coverage.get('test_file', 'None')}")
    print(f"Status: {coverage.get('status', 'unknown')}")
    
    # Check if >= 70%
    coverage_pct = coverage.get('coverage_pct', 0)
    meets_threshold = coverage_pct >= 70
    print(f"\n✓ Meets 70% threshold: {meets_threshold}")
    print(f"  Integration Layer 5 (Tested) should be: {meets_threshold}")
