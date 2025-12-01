import sys
sys.path.insert(0, 'src')

from pathlib import Path
from validation.test_coverage_validator import TestCoverageValidator

v = TestCoverageValidator(Path('.'))

features = [
    ('DiagramRegenerationOrchestrator', 'orchestrator'),
    ('CommitOrchestrator', 'orchestrator'),
    ('OnboardingOrchestrator', 'orchestrator')
]

for name, ftype in features:
    print(f"\n=== {name} ===")
    cov = v.get_test_coverage(name, ftype)
    print(f"Has tests: {cov['has_tests']}")
    print(f"Test file: {cov.get('test_file')}")
    print(f"Test count: {cov.get('test_count')}")
    print(f"Coverage %: {cov.get('coverage_pct')}")
    print(f"Status: {cov.get('status')}")
