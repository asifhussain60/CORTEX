#!/usr/bin/env python3
"""Post-Deployment Gate Validation - Verify production deployment safety"""
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.deployment.deployment_gates import DeploymentGates

print("=" * 80)
print("POST-DEPLOYMENT GATE VALIDATION REPORT")
print("Version: 3.3.0 | Branch: origin/main | Date: 2025-11-30")
print("=" * 80)
print()

gates = DeploymentGates(project_root)
result = gates.validate_all_gates()

print(f"Overall Status: {'✅ PASSED' if result['passed'] else '❌ FAILED'}")
print(f"Total Errors: {result['errors']}")
print(f"Total Warnings: {result['warnings']}")
print()
print("Gate-by-Gate Results:")
print("-" * 80)

for i, gate in enumerate(result['gates'], 1):
    status = '✅ PASSED' if gate['passed'] else '❌ FAILED'
    print(f"Gate {i:2d}: {gate['name']:<50} {status}")
    if not gate['passed'] and gate.get('message'):
        # Print error message if available
        print(f"         └─ {gate['message']}")

print("=" * 80)

# Focus on remediated gates
print()
print("REMEDIATION VERIFICATION:")
print("-" * 80)
gate13 = result['gates'][12]  # Gate 13 (0-indexed)
gate14 = result['gates'][13]  # Gate 14
gate16 = result['gates'][15]  # Gate 16

print(f"Gate 13 (TDD Mastery Integration):     {'✅ PASSED' if gate13['passed'] else '❌ FAILED'}")
print(f"Gate 14 (User Feature Packaging):      {'✅ PASSED' if gate14['passed'] else '❌ FAILED'}")
print(f"Gate 16 (EPM Admin Trigger Removal):   {'✅ PASSED' if gate16['passed'] else '⚠️  WARNING' if not gate16['passed'] else '✅ PASSED'}")
print("=" * 80)

if result['errors'] == 0:
    print()
    print("✅ DEPLOYMENT SAFE: All remediation work validated successfully")
    print("   Production deployment (v3.3.0) confirmed stable")
    sys.exit(0)
else:
    print()
    print(f"❌ DEPLOYMENT AT RISK: {result['errors']} error(s) found")
    print("   Consider rollback or immediate hotfix")
    sys.exit(1)
