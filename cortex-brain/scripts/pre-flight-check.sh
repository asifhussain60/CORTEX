#!/bin/bash
# CORTEX Pre-Flight Check - Phase Dependency Verification
# 
# Run this BEFORE starting any phase implementation to verify
# all module dependencies exist and entry point is functional.
#
# Usage: ./cortex-brain/scripts/pre-flight-check.sh
#
# Author: Asif Hussain
# Copyright © 2025-2026 Asif Hussain. All rights reserved.

set -e

echo "🔍 CORTEX Pre-Flight Check - Phase Dependency Verification"
echo "================================================================"
echo ""

# Step 1: Map all imports
echo "📋 Step 1/4: Mapping all imports in codebase..."
grep -rh "^from src\." src/ 2>/dev/null | \
    sed 's/from //' | \
    sed 's/ import.*//' | \
    sort | uniq > /tmp/cortex_imports.txt

TOTAL_IMPORTS=$(wc -l < /tmp/cortex_imports.txt | tr -d ' ')
echo "   ✅ Found $TOTAL_IMPORTS unique import statements"
echo ""

# Step 2: Verify modules exist
echo "🔍 Step 2/4: Verifying all modules exist..."
python3 << 'PYEOF'
import sys
import importlib
import importlib.util

missing = []
with open('/tmp/cortex_imports.txt', 'r') as f:
    for line in f:
        module = line.strip()
        if not module:
            continue
        try:
            spec = importlib.util.find_spec(module)
            if spec is None:
                missing.append(module)
        except (ImportError, ModuleNotFoundError, ValueError):
            missing.append(module)

if missing:
    print("❌ MISSING MODULES DETECTED:")
    for m in missing:
        print(f"   - {m}")
    print("\n🛑 STOP: Create stubs for missing modules BEFORE proceeding")
    print("   See: cortex-brain/documents/planning/active/cortex5-enhancement-epic/docs/prevention-strategy.md")
    sys.exit(1)
else:
    print("   ✅ All modules exist")
PYEOF

if [ $? -ne 0 ]; then
    exit 1
fi
echo ""

# Step 3: Test entry point
echo "🚀 Step 3/4: Testing entry point execution..."
python3 -m src.main "help" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Entry point functional"
else
    echo "   ❌ Entry point broken"
    echo "   Run: python3 -m src.main \"help\" for details"
    exit 1
fi
echo ""

# Step 4: Test critical imports
echo "🔬 Step 4/4: Validating critical imports..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')

# Critical imports
critical_modules = [
    ('src.mcp.registry', 'OrchestratorRegistry'),
    ('src.entry_point.cortex_entry', 'CortexEntry'),
    ('src.orchestrators.master_orchestrator', 'MasterOrchestrator'),
]

failed = []
for module_path, class_name in critical_modules:
    try:
        module = __import__(module_path, fromlist=[class_name])
        getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        failed.append(f"{module_path}.{class_name}: {e}")

if failed:
    print("❌ Critical imports failed:")
    for f in failed:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("   ✅ Critical imports successful")
PYEOF

if [ $? -ne 0 ]; then
    exit 1
fi
echo ""

echo "================================================================"
echo "✅ PRE-FLIGHT COMPLETE - SAFE TO PROCEED WITH PHASE IMPLEMENTATION"
echo "================================================================"
