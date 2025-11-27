"""
Direct test of alignment orchestrator with debug output.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.operations.modules.admin.system_alignment_orchestrator import SystemAlignmentOrchestrator
from src.discovery.orchestrator_scanner import OrchestratorScanner

project_root = Path(__file__).parent

# Test orchestrator scanner directly
print("=== Testing OrchestratorScanner ===")
scanner = OrchestratorScanner(project_root)
orchestrators = scanner.discover()

print(f"\nDiscovered {len(orchestrators)} orchestrators:")
for name, metadata in list(orchestrators.items())[:5]:
    print(f"  {name}: has_docstring={metadata.get('has_docstring')}")

# Test system alignment orchestrator
print("\n=== Testing SystemAlignmentOrchestrator ===")
alignment = SystemAlignmentOrchestrator({'project_root': project_root})

# Get integration score for TDDWorkflowOrchestrator specifically
metadata = orchestrators.get("TDDWorkflowOrchestrator")
if metadata:
    print(f"\nTDDWorkflowOrchestrator metadata from scanner:")
    print(f"  has_docstring: {metadata.get('has_docstring')}")
    print(f"  module_path: {metadata.get('module_path')}")
    
    # Calculate integration score
    score = alignment._calculate_integration_score("TDDWorkflowOrchestrator", metadata, "orchestrator")
    
    print(f"\nIntegration score calculation:")
    print(f"  discovered: {score.discovered}")
    print(f"  imported: {score.imported}")
    print(f"  instantiated: {score.instantiated}")
    print(f"  documented: {score.documented}")
    print(f"  tested: {score.tested}")
    print(f"  wired: {score.wired}")
    print(f"  optimized: {score.optimized}")
    print(f"  TOTAL SCORE: {score.score}%")
    print(f"  Issues: {score.issues}")
