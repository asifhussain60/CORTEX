"""Debug script to check registry rules loading"""
from cortex.brain.core.governance_registry import GovernanceRegistry

r = GovernanceRegistry.instance()
init_res = r.initialize()
print(f"Init result: {init_res}")

rules = r.get_all_rules()
print(f"Tier 0 rules: {len(rules['tier0'])}")
print(f"Rule IDs: {[rule.rule_id for rule in rules['tier0']]}")
