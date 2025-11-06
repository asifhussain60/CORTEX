import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "CORTEX"))

from src.entry_point import CortexEntry

# Initialize
cortex = CortexEntry()
print("✓ SUCCESS: CORTEX initialized!")

# Check health
health = cortex.get_health_status()
print(f"✓ Overall Status: {health['overall_status']}")
print(f"✓ Tier 1: {health['tiers']['tier1']['status']}")
print(f"✓ Tier 2: {health['tiers']['tier2']['status']}")
print(f"✓ Tier 3: {health['tiers']['tier3']['status']}")

print("\n✓ CORTEX is ready for simulation testing!")
