"""
Test IntegrationScorer directly to see what's happening.
"""
import sys
import logging
from pathlib import Path

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

sys.path.insert(0, str(Path(__file__).parent))

from src.validation.integration_scorer import IntegrationScorer

project_root = Path(__file__).parent
scorer = IntegrationScorer(project_root)

# Test TDDWorkflowOrchestrator specifically
module_path = "src.workflows.tdd_workflow_orchestrator"
class_name = "TDDWorkflowOrchestrator"

print("=== Testing Import ===")
can_import = scorer.validate_import(module_path)
print(f"Can import: {can_import}\n")

print("=== Testing Instantiation ===")
can_instantiate = scorer.validate_instantiation(module_path, class_name)
print(f"Can instantiate: {can_instantiate}")
