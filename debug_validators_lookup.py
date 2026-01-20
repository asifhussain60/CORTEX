"""Debug validator function lookup"""
from cortex.brain.core.governance import rule_validators

rule_ids = ['CORE-001', 'CORE-008', 'CORE-011', 'CORE-013']

for rule_id in rule_ids:
    validator_name = f"validate_{rule_id.lower().replace('-', '_')}"
    validator_func = getattr(rule_validators, validator_name, None)
    print(f"{rule_id} -> {validator_name}: {validator_func is not None}")
    if validator_func:
        print(f"  Function: {validator_func}")
