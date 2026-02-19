#!/usr/bin/env python3
"""
Phase 8.2: Batch Update GovernanceRegistry Imports
Updates 19 files from brain.core.governance_registry to orchestrators.core.governance_registry
"""

import re
from pathlib import Path

files_to_update = [
    "cortex/brain/core/governance_registry_database_integration.py",
    "cortex/brain/core/input_validator.py",
    "cortex/brain/core/orchestrator/conversation_protocol.py",
    "cortex/brain/core/rule_evaluator.py",
    "cortex/brain/core/tier_resolver.py",
    "cortex/brain/mcp/server.py",
    "cortex/execution/gateway_exec_full.py",
    "cortex/orchestrators/core/enforcement_orchestrator.py",
    "cortex/orchestrators/core/master_orchestrator.py",
    "cortex/orchestrators/support/context_assembly_orchestrator.py",
    "cortex/testing/auto_initialization_suite.py",
    "tests/integration/test_governance_persistence_option_c.py",
    "tests/test_governance_edge_cases.py",
    "tests/test_governance_integration.py",
    "tests/test_governance_performance.py",
    "tests/test_governance_registry_loading.py",
    "tests/unit/governance/test_core_002_artifact_validation.py",
    "tests/unit/orchestrators/test_module_dependencies.py",
    "tests/unit/test_governance_registry.py",
]

repo_root = Path("/Users/asifhussain/PROJECTS/CORTEX")
updated = 0
failed = []

print("=" * 80)
print("PHASE 8.2: Updating GovernanceRegistry Imports (19 files)")
print("=" * 80)
print()

for file_path in files_to_update:
    full_path = repo_root / file_path

    if not full_path.exists():
        print(f"❌ NOT FOUND: {file_path}")
        failed.append(file_path)
        continue

    try:
        content = full_path.read_text()
        original = content

        # Replace import statement
        content = content.replace(
            "from cortex.brain.core.governance_registry import",
            "from cortex.orchestrators.core.governance_registry import"
        )

        if content != original:
            full_path.write_text(content)
            print(f"✅ UPDATED: {file_path}")
            updated += 1
        else:
            print(f"⚠️  NO CHANGES: {file_path}")

    except Exception as e:
        print(f"❌ ERROR: {file_path} - {e}")
        failed.append(file_path)

print()
print("=" * 80)
print(f"RESULTS: {updated}/19 files updated")
if failed:
    print(f"FAILED: {len(failed)} files")
    for f in failed:
        print(f"  - {f}")
else:
    print("✅ ALL FILES UPDATED SUCCESSFULLY")
print("=" * 80)
