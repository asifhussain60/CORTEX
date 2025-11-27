import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "src"))

from discovery.agent_scanner import AgentScanner
from validation.integration_scorer import IntegrationScorer

scorer = IntegrationScorer(Path.cwd())

print("Testing IntegrationScorer with updated TestCoverageValidator...")
print("=" * 70)

# Test BrainIngestionAgent
score1 = scorer.calculate_score('BrainIngestionAgent', 'agent')
print(f"BrainIngestionAgent: {score1['overall_score']:.0f}%")
print(f"  Testing: {score1['layers']['testing']}pts")
print(f"  Wiring: {score1['layers']['wiring']}pts")

# Test BrainIngestionAdapterAgent
score2 = scorer.calculate_score('BrainIngestionAdapterAgent', 'agent')
print(f"\nBrainIngestionAdapterAgent: {score2['overall_score']:.0f}%")
print(f"  Testing: {score2['layers']['testing']}pts")
print(f"  Wiring: {score2['layers']['wiring']}pts")

# Test PlanningOrchestrator
score3 = scorer.calculate_score('PlanningOrchestrator', 'orchestrator')
print(f"\nPlanningOrchestrator: {score3['overall_score']:.0f}%")
print(f"  Testing: {score3['layers']['testing']}pts")
print(f"  Wiring: {score3['layers']['wiring']}pts")
