"""Debug script to see detailed alignment scores."""
from src.validation.integration_scorer import IntegrationScorer
from src.discovery.agent_scanner import AgentScanner
from src.discovery.orchestrator_scanner import OrchestratorScanner
from src.validation.documentation_validator import DocumentationValidator
from src.validation.test_coverage_validator import TestCoverageValidator
from src.validation.wiring_validator import WiringValidator
from src.discovery.entry_point_scanner import EntryPointScanner
from pathlib import Path

# Initialize
project_root = Path.cwd()
scorer = IntegrationScorer(project_root)
agent_scanner = AgentScanner(project_root)
orch_scanner = OrchestratorScanner(project_root)
doc_validator = DocumentationValidator(project_root)
test_validator = TestCoverageValidator(project_root)
wiring_validator = WiringValidator(project_root)
entry_scanner = EntryPointScanner(project_root)

# Discover
agents = agent_scanner.discover()
orchestrators = orch_scanner.discover()
entry_points = entry_scanner.discover()

# Check critical features
critical_features = [
    "BrainIngestionAgent",
    "BrainIngestionAdapterAgent",
    "PlanningOrchestrator",
    "ViewDiscoveryAgent",
    "LearningCaptureAgent"
]

print("Critical Features Status:\n")
for feature_name in critical_features:
    if feature_name in agents:
        metadata = agents[feature_name]
        feature_type = "agent"
    elif feature_name in orchestrators:
        metadata = orchestrators[feature_name]
        feature_type = "orchestrator"
    else:
        print(f"{feature_name}: NOT FOUND")
        continue
    
    # Check each layer
    doc_validated = doc_validator.validate_documentation(feature_name, feature_type)["has_documentation"]
    test_cov = test_validator.get_test_coverage(feature_name, feature_type)
    
    # Check wiring
    is_wired = False
    for trigger, ep_data in entry_points.items():
        if ep_data.get("expected_orchestrator") == feature_name:
            is_wired = True
            break
    
    score = scorer.calculate_score(
        feature_name,
        metadata,
        feature_type,
        documentation_validated=doc_validated,
        test_coverage_pct=test_cov["coverage_pct"],
        is_wired=is_wired
    )
    
    print(f"{feature_name} ({feature_type}): {score}%")
    print(f"  Documentation: {'✓' if doc_validated else '✗'}")
    print(f"  Test Coverage: {test_cov['coverage_pct']:.1f}% ({test_cov['test_count']} tests) {'✓' if test_cov['coverage_pct'] >= 70 else '✗'}")
    print(f"  Wired: {'✓' if is_wired else '✗'}")
    print()
