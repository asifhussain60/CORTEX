"""Debug script to check CommitOrchestrator scoring"""
import sys
sys.path.insert(0, 'src')

from pathlib import Path
from validation.integration_scorer import IntegrationScorer
from validation.test_coverage_validator import TestCoverageValidator
from validation.wiring_validator import WiringValidator
import yaml

# Initialize validators
scorer = IntegrationScorer(Path('.'))
test_validator = TestCoverageValidator(Path('.'))
wiring_validator = WiringValidator(Path('.'))

# Get validation data
feature_name = 'CommitOrchestrator'
metadata = {
    'module_path': 'src.orchestrators.commit_orchestrator',  # Dotted path for import
    'class_name': 'CommitOrchestrator'
}

# Check documentation manually
guide_path = Path('.github/prompts/modules/commit-orchestrator-guide.md')
has_doc = guide_path.exists()

# Check test coverage
coverage_data = test_validator.get_test_coverage(feature_name, 'orchestrator')

# Check wiring - need to load entry points from response-templates.yaml
templates_path = Path('cortex-brain/response-templates.yaml')
entry_points = {}
if templates_path.exists():
    with open(templates_path, 'r', encoding='utf-8') as f:
        templates_data = yaml.safe_load(f)
        routing = templates_data.get('routing', {})
        # Build entry points dict from routing triggers
        for key, triggers in routing.items():
            if key.endswith('_triggers') and 'commit' in key.lower():
                entry_points['commit_operation'] = {
                    'triggers': triggers,
                    'expected_orchestrator': 'CommitOrchestrator'
                }

is_wired = wiring_validator.check_orchestrator_wired(feature_name, entry_points)

print(f"=== {feature_name} Validation ===\n")
print(f"Documentation Guide: {guide_path}")
print(f"  Exists: {has_doc}")
print(f"\nTest Coverage: {coverage_data.get('coverage_pct', 0):.1f}% (threshold: 70%)")
print(f"  Has Tests: {coverage_data.get('has_tests', False)}")
print(f"  Test File: {coverage_data.get('test_file', 'Not found')}")
print(f"\nWiring:")
print(f"  Entry Points Found: {len(entry_points)}")
print(f"  Is Wired: {is_wired}")

# Calculate score
print(f"\n=== Calculating Score ===")
print(f"  feature_name: {feature_name}")
print(f"  metadata: {metadata}")
print(f"  feature_type: orchestrator")
print(f"  documentation_validated: {has_doc}")
print(f"  test_coverage_pct: {coverage_data.get('coverage_pct', 0)}")
print(f"  is_wired: {is_wired}")

score = scorer.calculate_score(
    feature_name,
    metadata,
    'orchestrator',
    documentation_validated=has_doc,
    test_coverage_pct=coverage_data.get('coverage_pct', 0),
    is_wired=is_wired
)

print(f"\n=== Final Score: {score}% ===")
print("\nLayer-by-Layer Breakdown:")
breakdown = scorer.get_score_breakdown(score)
for layer, passed in breakdown.items():
    status = "✅" if passed else "❌"
    print(f"  {status} {layer}")
