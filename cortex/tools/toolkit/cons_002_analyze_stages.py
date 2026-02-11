#!/usr/bin/env python3
"""
TRANSFORM-002: CONS-002 Master Orchestrator Consolidation
Consolidates 4 stage files into unified master_orchestrator.py

This script will:
1. Read all 4 stage implementations
2. Extract key classes and methods
3. Merge into unified master orchestrator
4. Create backward compatibility adapters
5. Test consolidated implementation
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set

# The consolidation will merge:
# - master_orchestrator_stage_1.py (Comprehension)
# - master_orchestrator_stage_2.py (Routing)
# - master_orchestrator_stage_3.py (Knowledge)
# - master_orchestrator_stage_4.py (Approval)
#
# Into: master_orchestrator.py with unified execute() method

CONSOLIDATION_PLAN = """
CONS-002 CONSOLIDATION STRATEGY
================================

Current Architecture (4-Stage):
  execute_stage_1(context) → Stage1Output
  execute_stage_2(stage1_output) → Stage2Output
  execute_stage_3(stage2_output) → Stage3Output
  execute_stage_4(stage3_output) → Stage4Output

New Architecture (Unified):
  execute(context, stages=None) → Dict[str, Any]
    - If stages=None: Execute all 4 stages in sequence
    - If stages=['1', '2']: Execute only stages 1 and 2
    - Internal: Call _execute_stage_1(), _execute_stage_2(), etc.

Backward Compatibility:
  - Keep execute_stage_1(), execute_stage_2(), etc. as public methods
  - These call the unified _execute_stage_N() implementations
  - Existing code continues to work without changes

Implementation Steps:
  1. Copy master_orchestrator.py to master_orchestrator_unified.py (backup)
  2. Enhance execute() method to orchestrate all stages
  3. Move stage files' classes into master_orchestrator.py
  4. Create private _execute_stage_N() methods
  5. Keep public execute_stage_N() as adapters
  6. Delete stage_1.py, stage_2.py, stage_3.py, stage_4.py
  7. Update imports throughout codebase
  8. Create deprecation module for legacy imports
  9. Test consolidated implementation
  10. Update documentation

Files to Merge:
  Source:
    - cortex/orchestrators/core/master_orchestrator_stage_1.py
    - cortex/orchestrators/core/master_orchestrator_stage_2.py
    - cortex/orchestrators/core/master_orchestrator_stage_3.py
    - cortex/orchestrators/core/master_orchestrator_stage_4.py
  Target:
    - cortex/orchestrators/core/master_orchestrator.py (enhanced)

Delete After Merge:
    - master_orchestrator_stage_1.py
    - master_orchestrator_stage_2.py
    - master_orchestrator_stage_3.py
    - master_orchestrator_stage_4.py
"""

print(CONSOLIDATION_PLAN)

# Read the stage files to extract classes
print("\n" + "="*80)
print("ANALYZING STAGE FILES")
print("="*80)

root = Path("/Users/asifhussain/PROJECTS/CORTEX")
stage_files = [
    "cortex/orchestrators/core/master_orchestrator_stage_1.py",
    "cortex/orchestrators/core/master_orchestrator_stage_2.py",
    "cortex/orchestrators/core/master_orchestrator_stage_3.py",
    "cortex/orchestrators/core/master_orchestrator_stage_4.py",
]

classes_by_stage = {}

for stage_file in stage_files:
    path = root / stage_file
    if path.exists():
        with open(path, 'r') as f:
            content = f.read()

        # Extract class names
        import re
        classes = re.findall(r'^class (\w+)', content, re.MULTILINE)

        stage_num = stage_file.split('_')[-1].split('.')[0]
        classes_by_stage[f"Stage {stage_num}"] = classes

        print(f"\n{stage_file}:")
        print(f"  Size: {len(content):,} bytes")
        print(f"  Classes: {', '.join(classes)}")
    else:
        print(f"\n{stage_file}: NOT FOUND")

print("\n" + "="*80)
print("CONSOLIDATION READINESS")
print("="*80)

# Check if master_orchestrator exists
master_path = root / "cortex/orchestrators/core/master_orchestrator.py"
if master_path.exists():
    with open(master_path, 'r') as f:
        content = f.read()
    print("\n✅ master_orchestrator.py exists")
    print(f"   Size: {len(content):,} bytes")
    print(f"   Lines: {len(content.splitlines())}")

    # Check for stage methods
    if "execute_stage_1" in content:
        print("   ✅ Has execute_stage_1() method")
    if "execute_stage_2" in content:
        print("   ✅ Has execute_stage_2() method")
    if "execute_stage_3" in content:
        print("   ✅ Has execute_stage_3() method")
    if "execute_stage_4" in content:
        print("   ✅ Has execute_stage_4() method")
else:
    print("\n❌ master_orchestrator.py NOT FOUND")

print("\n" + "="*80)
print("NEXT STEPS")
print("="*80)
print("""
1. Create unified master_orchestrator.py with:
   - Merge all Stage1Output, Stage2Output, Stage3Output, Stage4Output classes
   - Create unified execute() method
   - Keep execute_stage_1(), execute_stage_2(), etc. for backward compatibility

2. Delete stage files:
   - master_orchestrator_stage_1.py
   - master_orchestrator_stage_2.py
   - master_orchestrator_stage_3.py
   - master_orchestrator_stage_4.py

3. Create deprecation module:
   - cortex/orchestrators/core/master_orchestrator_stage_adapters.py
   - For any code still importing from stage files

4. Update imports in:
   - All files importing from master_orchestrator_stage_*.py
   - Update to import from master_orchestrator.py directly

5. Run tests:
   - Ensure all 4 stages work through unified execute()
   - Verify backward compatibility with stage methods
   - Full regression testing

Estimated Effort: 8 hours
Status: READY TO BEGIN IMPLEMENTATION
""")

print("\n✅ CONS-002 Analysis Complete")
print("Ready to implement consolidation")
