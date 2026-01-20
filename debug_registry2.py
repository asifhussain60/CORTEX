"""Debug script to check rules file loading"""
from cortex.brain.core.governance_registry import GovernanceRegistry
from cortex.brain.core.path_resolver import resolve_path

r = GovernanceRegistry.instance()
init_res = r.initialize()

if init_res.is_err():
    # Err object - check how to access error
    print(f"Init failed - type: {type(init_res)}")
    print(f"Init result: {init_res}")
else:
    print("Init succeeded")

# Check path resolution
rules_path = resolve_path("cortex_brain", "tier0", "governance", "core-rules.yaml")
print(f"Rules path: {rules_path}")
print(f"Path exists: {rules_path.exists()}")

# Try alternative path
import pathlib
alt_path = pathlib.Path("cortex/core/governance/core-rules.yaml")
print(f"Alt path: {alt_path}")
print(f"Alt exists: {alt_path.exists()}")
