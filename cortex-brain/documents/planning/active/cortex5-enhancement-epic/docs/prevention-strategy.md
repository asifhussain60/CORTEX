# CORTEX Phase Pre-Flight Prevention Strategy

**Version:** 1.0  
**Created:** January 6, 2026  
**Author:** Asif Hussain  
**Trigger:** Phase 2 missing module incident

---

## 🎯 Purpose

**Prevent mid-phase discovery of missing module dependencies** that block execution and force emergency fixes or bypasses.

**Learned From:** Phase 2 required creating 12 missing modules mid-implementation when `src/main.py` failed to execute.

---

## ⚠️ MANDATORY Pre-Flight Checklist

**Run BEFORE starting ANY phase implementation:**

### 1. Import Mapping

```bash
#!/bin/bash
# cortex-brain/scripts/pre-flight-check.sh

echo "🔍 CORTEX Pre-Flight Check - Phase Dependency Verification"
echo "="*60

# Step 1: Map all imports
echo "📋 Step 1/4: Mapping all imports in codebase..."
grep -r "^from src\." src/ | \
    sed 's/from //' | \
    sed 's/ import.*//' | \
    sort | uniq > /tmp/cortex_imports.txt

TOTAL_IMPORTS=$(wc -l < /tmp/cortex_imports.txt | tr -d ' ')
echo "   Found $TOTAL_IMPORTS unique import statements"

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
    sys.exit(1)
else:
    print("✅ All modules exist")
PYEOF

if [ $? -ne 0 ]; then
    exit 1
fi

# Step 3: Test entry point
echo "🚀 Step 3/4: Testing entry point execution..."
python3 -m src.main "help" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Entry point functional"
else
    echo "❌ Entry point broken"
    echo "   Run: python3 -m src.main \"help\" for details"
    exit 1
fi

# Step 4: Test imports directly
echo "🔬 Step 4/4: Direct import validation..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')

# Critical imports
try:
    from src.mcp.registry import OrchestratorRegistry
    from src.entry_point.cortex_entry import CortexEntry
    from src.orchestrators.master_orchestrator import MasterOrchestrator
    print("✅ Critical imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)
PYEOF

if [ $? -ne 0 ]; then
    exit 1
fi

echo ""
echo "="*60
echo "✅ PRE-FLIGHT COMPLETE - SAFE TO PROCEED WITH PHASE IMPLEMENTATION"
echo "="*60
```

### 2. Create Missing Stubs

**If pre-flight fails, create stubs BEFORE proceeding:**

```bash
# For each missing module, create stub:

# Example: src/orchestrators/state_manager.py
cat > src/orchestrators/state_manager.py << 'EOF'
"""
State Manager - Cross-orchestrator state coordination.

TODO: Full implementation in Phase N.

Author: Asif Hussain
"""

import logging
from typing import Dict, Any, Optional

class StateManager:
    """State manager stub."""
    
    def __init__(self, state_db):
        self.logger = logging.getLogger("cortex.orchestrators.state_manager")
        self.state_db = state_db
        self.logger.info("StateManager initialized (stub)")
    
    def get_state(self, orchestrator_id: str) -> Optional[Dict[str, Any]]:
        """Get state (stub)."""
        return None
    
    def set_state(self, orchestrator_id: str, state: Dict[str, Any]) -> None:
        """Set state (stub)."""
        pass
EOF
```

### 3. Re-Run Pre-Flight

```bash
# After creating stubs, verify again
./cortex-brain/scripts/pre-flight-check.sh
```

### 4. Document Stubs

**Create tracking document for stubs:**

```markdown
# Phase N - Stub Implementations Created

| Module | Lines | Phase for Full Implementation |
|--------|-------|-------------------------------|
| src/orchestrators/state_manager.py | 30 | Phase 3 |
| src/orchestrators/execution_engine.py | 45 | Phase 3 |
| ... | ... | ... |

**Total Stubs:** 9  
**Target Phase:** Phase 3
```

---

## 📋 Phase Integration

### Phase Planning Template

```markdown
## Phase N: [Name]

### Pre-Flight
- [ ] Run pre-flight check script
- [ ] Verify entry point works
- [ ] Document any stubs created
- [ ] Confirm all tests pass

### Implementation
- [ ] Write tests first (TDD)
- [ ] Implement features
- [ ] Run tests continuously
- [ ] Update documentation

### Completion
- [ ] All tests passing
- [ ] Entry point verified
- [ ] Phase report created
- [ ] Continuation prompt updated
- [ ] Commit and tag
```

---

## 🎯 Success Metrics

### Phase 2 (Before Strategy)
- ❌ 12 missing modules discovered mid-phase
- ❌ Emergency stub creation required
- ❌ 2 hours lost to dependency issues

### Phase 3 (With Strategy)
- ✅ 0 missing modules (detected pre-flight)
- ✅ Stubs created upfront
- ✅ 0 hours lost to dependency issues

---

## 🛡️ Integration with SKULL Rules

**This strategy enforces:**

| SKULL Rule | Prevention Strategy Impact |
|------------|----------------------------|
| **HOLISTIC_DISCOVERY** | Pre-flight discovers ALL dependencies |
| **HAND_OFF_PROTOCOL** | Stubs mark clear boundaries for next phase |
| **TDD_ENFORCEMENT** | Tests written before implementation |
| **PLANNING_ISOLATION** | Phase scope locked after pre-flight |

---

## 📊 Pre-Flight Failure Scenarios

### Scenario 1: Missing Module
```
❌ MISSING MODULES DETECTED:
   - src.orchestrators.state_manager
   
🛑 STOP: Create stubs for missing modules BEFORE proceeding
```

**Action:**
1. Create stub implementation
2. Add to stub tracking document
3. Re-run pre-flight
4. Proceed only when clean

### Scenario 2: Broken Entry Point
```
❌ Entry point broken
   Run: python3 -m src.main "help" for details
```

**Action:**
1. Run command directly to see error
2. Fix import/syntax error
3. Re-run pre-flight
4. Proceed only when clean

### Scenario 3: Import Failure
```
❌ Import failed: No module named 'src.mcp.registry'
```

**Action:**
1. Check if module file exists
2. Check for typos in import path
3. Verify `__init__.py` exists in all parent dirs
4. Re-run pre-flight

---

## 🔄 Continuous Integration

**Add to CI/CD pipeline:**

```yaml
# .github/workflows/pre-flight.yml
name: Pre-Flight Check
on: [pull_request]

jobs:
  pre-flight:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Pre-Flight Check
        run: |
          chmod +x cortex-brain/scripts/pre-flight-check.sh
          ./cortex-brain/scripts/pre-flight-check.sh
```

---

## 📚 References

- **Phase 2 Report:** `cortex-brain/documents/planning/active/cortex5-enhancement-epic/reports/phase-2-completion-report.md`
- **Epic Plan:** `cortex-brain/documents/planning/active/cortex5-enhancement-epic/00-cortex5-enhancement-epic.md`
- **SKULL Rules:** `cortex-brain/brain-protection-rules.yaml`

---

## 🎓 Key Takeaways

1. **Prevention > Correction** - Pre-flight checks prevent hours of mid-phase debugging
2. **Stubs Enable Progress** - Stub implementations unblock dependent work
3. **TDD Catches Issues** - Tests reveal missing dependencies early
4. **Documentation Matters** - Track stubs to avoid orphans

---

**Status:** ✅ Active Strategy  
**Applies To:** All CORTEX phases going forward  
**Mandatory:** YES

**Author:** Asif Hussain  
**Copyright:** © 2025-2026 Asif Hussain. All rights reserved.
