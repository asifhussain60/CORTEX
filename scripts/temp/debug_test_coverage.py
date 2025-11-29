"""Debug script to test test coverage validator."""
from src.validation.test_coverage_validator import TestCoverageValidator
from pathlib import Path

validator = TestCoverageValidator(Path.cwd())

# Test BrainIngestionAgent
test_file = validator.find_test_file("BrainIngestionAgent", "agent")
print(f"BrainIngestionAgent test file: {test_file}")

# Test BrainIngestionAdapterAgent
test_file2 = validator.find_test_file("BrainIngestionAdapterAgent", "agent")
print(f"BrainIngestionAdapterAgent test file: {test_file2}")

# Test coverage
coverage = validator.get_test_coverage("BrainIngestionAgent", "agent")
print(f"\nBrainIngestionAgent coverage: {coverage}")

coverage2 = validator.get_test_coverage("BrainIngestionAdapterAgent", "agent")
print(f"\nBrainIngestionAdapterAgent coverage: {coverage2}")
