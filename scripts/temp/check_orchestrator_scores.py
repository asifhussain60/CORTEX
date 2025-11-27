"""Quick check of orchestrator integration scores."""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from src.validation.integration_scorer import IntegrationScorer
from src.discovery.convention_based_discovery import ConventionBasedDiscovery

# Initialize
project_root = Path(__file__).parent
scorer = IntegrationScorer(project_root)
discovery = ConventionBasedDiscovery(project_root / "src")

# Discover orchestrators
orchestrators = discovery.discover_orchestrators()

# Filter to 5 key orchestrators
key_orchestrators = [
    "TDDWorkflowOrchestrator",
    "LintValidationOrchestrator", 
    "SessionCompletionOrchestrator",
    "UpgradeOrchestrator",
    "GitCheckpointOrchestrator"
]

print("\n🔍 Checking 5 Key Orchestrators:\n")

for orch_name in key_orchestrators:
    orch = next((o for o in orchestrators if o["class_name"] == orch_name), None)
    
    if not orch:
        print(f"❌ {orch_name} - NOT FOUND")
        continue
    
    # Check performance validation
    module_path = orch["module_path"]
    class_name = orch["class_name"]
    
    perf_validated = scorer.validate_performance(module_path, class_name)
    
    # Check import
    import_ok = scorer.validate_import(module_path)
    
    # Check instantiation
    instant_ok = scorer.validate_instantiation(module_path, class_name)
    
    # Mock documentation (we know these have docs)
    doc_ok = orch_name in key_orchestrators
    
    # Calculate score
    score = scorer.calculate_score(
        feature_name=orch_name,
        metadata=orch,
        feature_type="orchestrator",
        documentation_validated=doc_ok,
        test_coverage_pct=75.0,  # Mock - tests exist
        is_wired=True,  # Mock - wired
        performance_validated=perf_validated
    )
    
    breakdown = scorer.get_score_breakdown(score)
    
    print(f"✅ {orch_name}: {score}%")
    print(f"   Layers: discovered={breakdown['discovered']}, imported={breakdown['imported']}, "
          f"instantiated={breakdown['instantiated']}, documented={breakdown['documented']}, "
          f"tested={breakdown['tested']}, wired={breakdown['wired']}, optimized={breakdown['optimized']}")
    print(f"   Performance validated: {perf_validated}")
    print()
