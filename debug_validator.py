"""Debug validator execution"""
from cortex.brain.core.rule_evaluator import RuleEvaluator

evaluator = RuleEvaluator()

# Test CORE-001 pass
context1 = {
    "file_path": "cortex/core/example.py",
    "operation_type": "MODIFY",
    "lines_changed": 250
}

result1 = evaluator.evaluate_rules(context1)
print(f"Test 1 (250 lines): {result1.unwrap().passed}")
print(f"Violations: {len(result1.unwrap().violations)}")
for v in result1.unwrap().violations:
    if v.rule_id == "CORE-001":
        print(f"  CORE-001: {v.message}")

# Test CORE-001 fail  
context2 = {
    "file_path": "cortex/core/example.py",
    "operation_type": "MODIFY",
    "lines_changed": 750
}

result2 = evaluator.evaluate_rules(context2)
print(f"\nTest 2 (750 lines): {result2.unwrap().passed}")
print(f"Violations: {len(result2.unwrap().violations)}")
for v in result2.unwrap().violations:
    if v.rule_id == "CORE-001":
        print(f"  CORE-001: {v.message}")
