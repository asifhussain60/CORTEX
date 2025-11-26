"""Debug script to understand why coverage not detected"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from validation.test_coverage_validator import TestCoverageValidator

validator = TestCoverageValidator(Path.cwd())

# Test BrainIngestionAgent
print("=" * 80)
print("Testing BrainIngestionAgent")
print("=" * 80)

test_file = validator.find_test_file("BrainIngestionAgent", "agent")
print(f"Test file found: {test_file}")

if test_file:
    coverage = validator.get_test_coverage("BrainIngestionAgent", "agent")
    print(f"Coverage result: {coverage}")

# Test BrainIngestionAdapterAgent
print("\n" + "=" * 80)
print("Testing BrainIngestionAdapterAgent")
print("=" * 80)

test_file = validator.find_test_file("BrainIngestionAdapterAgent", "agent")
print(f"Test file found: {test_file}")

if test_file:
    coverage = validator.get_test_coverage("BrainIngestionAdapterAgent", "agent")
    print(f"Coverage result: {coverage}")

# Test PlanningOrchestrator
print("\n" + "=" * 80)
print("Testing PlanningOrchestrator")
print("=" * 80)

test_file = validator.find_test_file("PlanningOrchestrator", "orchestrator")
print(f"Test file found: {test_file}")

if test_file:
    coverage = validator.get_test_coverage("PlanningOrchestrator", "orchestrator")
    print(f"Coverage result: {coverage}")
