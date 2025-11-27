"""
Debug score calculation to see why alignment shows 50% instead of expected scores.
"""

from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.operations.modules.admin.system_alignment_orchestrator import IntegrationScore

# Test score calculation with different combinations
def test_score_calculation():
    print("Score Calculation Debug")
    print("=" * 70)
    
    # Scenario 1: BrainIngestionAgent - should be ~80%
    print("\nBrainIngestionAgent (Expected: 80-90%):")
    score1 = IntegrationScore(
        feature_name="BrainIngestionAgent",
        feature_type="agent",
        discovered=True,      # +20
        imported=True,        # +20
        instantiated=True,    # +20
        documented=False,     # +0  (missing guide file?)
        tested=True,          # +10 (has 87% coverage)
        wired=False,          # +0  (not wired)
        optimized=False       # +0  (no performance benchmarks)
    )
    print(f"  discovered={score1.discovered} imported={score1.imported} instantiated={score1.instantiated}")
    print(f"  documented={score1.documented} tested={score1.tested} wired={score1.wired} optimized={score1.optimized}")
    print(f"  SCORE: {score1.score}% - {score1.status}")
    print(f"  Issues: {', '.join(score1.issues)}")
    
    # Scenario 2: What if only discovered+imported+instantiated?
    print("\nScenario: Only Layer 1-3 (50%):")
    score2 = IntegrationScore(
        feature_name="Test",
        feature_type="agent",
        discovered=True,      # +20
        imported=True,        # +20
        instantiated=True,    # +20
        documented=False,     # +0
        tested=False,         # +0
        wired=False,          # +0
        optimized=False       # +0
    )
    print(f"  SCORE: {score2.score}% - {score2.status}")
    
    # Scenario 3: What if tested=False?
    print("\nBrainIngestionAgent WITHOUT tested flag:")
    score3 = IntegrationScore(
        feature_name="BrainIngestionAgent",
        feature_type="agent",
        discovered=True,      # +20
        imported=True,        # +20
        instantiated=False,   # +0  ← Maybe instantiation failed?
        documented=False,     # +0
        tested=False,         # +0
        wired=False,          # +0
        optimized=False       # +0
    )
    print(f"  SCORE: {score3.score}% - {score3.status}")
    print(f"  Issues: {', '.join(score3.issues)}")

if __name__ == "__main__":
    test_score_calculation()
