"""Test Gate 8 Swagger/OpenAPI validation."""
from pathlib import Path
from src.deployment.deployment_gates import DeploymentGates

# Initialize deployment gates
gates = DeploymentGates(Path('.'))

# Run all gates
result = gates.validate_all_gates()

# Find Gate 8
gate8 = None
for gate in result['gates']:
    if 'Swagger' in gate['name'] or 'OpenAPI' in gate['name']:
        gate8 = gate
        break

if gate8:
    print("=" * 80)
    print("GATE 8: SWAGGER/OPENAPI DOCUMENTATION")
    print("=" * 80)
    print(f"Name: {gate8['name']}")
    print(f"Passed: {gate8['passed']}")
    print(f"Severity: {gate8['severity']}")
    print(f"Message: {gate8['message']}")
    print("\nDetails:")
    if 'details' in gate8:
        if isinstance(gate8['details'], dict):
            for key, value in gate8['details'].items():
                print(f"  {key}: {value}")
        else:
            print(f"  {gate8['details']}")
    print("=" * 80)
else:
    print("Gate 8 not found in validation results")
    print(f"Total gates checked: {len(result['gates'])}")
    print("Gate names:")
    for gate in result['gates']:
        print(f"  - {gate['name']}")
