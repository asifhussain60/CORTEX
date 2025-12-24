# 🧠 CORTEX - File Bloat Prevention System

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Plan ID:** cortex-rearchitecture-v1 / Phase 8  
**Date:** December 15, 2025  
**Status:** 📋 PLANNED

---

## 🎯 Problem Statement

**Current Bloat:**
- `brain-protection-rules.yaml`: 4,385 lines (204KB) - 75 inline rationales
- `planning_orchestrator.py`: 70KB (1,800+ lines)
- `response-templates.yaml`: 50KB+ 
- Multiple large JSON analysis files (50KB+)

**Root Cause:** Inline documentation violates DRY principle

---

## 🏗️ Solution Design

### 1. **Reference Pattern (Already Used)**
```yaml
rationale: '#file:documents/rationales/RULE_NAME.md'
evidence_template: '#file:documents/evidence-templates/category/TEMPLATE.md'
```

### 2. **Automated Bloat Detection**

**File:** `src/operations/modules/quality/bloat_detector.py`

```python
class BloatDetector:
    """Detects and reports file bloat across CORTEX."""
    
    THRESHOLDS = {
        'yaml': {'lines': 2000, 'kb': 100},
        'py': {'lines': 1000, 'kb': 50},
        'md': {'lines': 1500, 'kb': 75},
        'json': {'lines': 500, 'kb': 25}
    }
    
    def scan_codebase(self) -> dict:
        """Returns bloated files with refactoring suggestions."""
        pass
    
    def suggest_refactoring(self, file_path: str) -> list:
        """Returns list of refactoring actions."""
        # For YAML: Extract inline rationales to markdown
        # For Python: Suggest module decomposition
        # For JSON: Compress or archive
        pass
```

### 3. **YAML Refactoring Strategy**

**brain-protection-rules.yaml Decomposition:**
```
cortex-brain/
├── brain-protection-rules.yaml (CORE - rule definitions only)
│   ├── tier0_instincts: [list of rule IDs]
│   ├── rules:
│   │   - rule_id: EXAMPLE
│   │     severity: blocked
│   │     detection: {...}
│   │     alternatives: [...]
│   │     rationale: '#file:documents/rationales/EXAMPLE.md'
│   │     evidence_template: '#file:documents/evidence-templates/EXAMPLE.md'
│
├── documents/
│   ├── rationales/          (NEW - extracted from YAML)
│   │   ├── TDD_ENFORCEMENT.md
│   │   ├── HOLISTIC_DISCOVERY.md
│   │   ├── GIT_ISOLATION.md
│   │   └── ... (75 files)
│   │
│   ├── evidence-templates/  (EXISTING - consolidate)
│   │   ├── planning/
│   │   ├── tdd/
│   │   └── cleanup/
```

**Target:** Reduce `brain-protection-rules.yaml` from 4,385 → ~1,500 lines (65% reduction)

### 4. **Python Module Decomposition**

**planning_orchestrator.py (1,800 lines) → Module Decomposition:**
```
src/operations/modules/orchestration/
├── planning_orchestrator.py (300 lines - orchestration only)
├── planning/
│   ├── __init__.py
│   ├── phase_manager.py (phase lifecycle)
│   ├── validation_engine.py (DoR/DoD checks)
│   ├── progress_tracker.py (visual progress bars)
│   ├── checkpoint_manager.py (git checkpoints)
│   ├── token_optimizer.py (context management)
│   └── autonomous_executor.py (auto-progression logic)
```

**Target:** Main orchestrator ≤ 500 lines, modules ≤ 300 lines each

### 5. **Pre-Commit Hook**

**File:** `.git/hooks/pre-commit` (automated check)

```bash
#!/usr/bin/env python3
from src.operations.modules.quality.bloat_detector import BloatDetector

detector = BloatDetector()
bloated = detector.scan_staged_files()

if bloated:
    print("⚠️ BLOAT DETECTED:")
    for file, metrics in bloated.items():
        print(f"  {file}: {metrics['lines']} lines ({metrics['kb']}KB)")
    print("\nRun: python -m src.operations.modules.quality.bloat_detector --refactor")
    exit(1)
```

---

## 📋 Implementation Phases

### **Phase 8.1: Bloat Detection System** (Day 1)
- [ ] Create `bloat_detector.py` with threshold scanning
- [ ] Add CLI: `python -m src.operations.modules.quality.bloat_detector`
- [ ] Unit tests: Threshold detection, suggestion generation
- [ ] Integration: Add to CI/CD pipeline

### **Phase 8.2: YAML Refactoring** (Day 2-3)
- [ ] Extract 75 inline rationales to `documents/rationales/*.md`
- [ ] Update `brain-protection-rules.yaml` with `#file:` references
- [ ] Validate YAML parsing still works
- [ ] Run all SKULL protection tests

### **Phase 8.3: Python Module Decomposition** (Day 4-5)
- [ ] Extract `planning_orchestrator.py` modules
- [ ] Update imports across codebase
- [ ] Run all 50+ autonomous execution tests
- [ ] Performance benchmarking (ensure no regression)

### **Phase 8.4: Pre-Commit Hook** (Day 6)
- [ ] Install bloat detector as pre-commit hook
- [ ] Test with intentionally bloated files
- [ ] Document bypass procedure (`git commit --no-verify`)
- [ ] Update CONTRIBUTING.md

### **Phase 8.5: JSON Cleanup** (Day 7)
- [ ] Archive duplicate-analysis-*.json files (20+ files)
- [ ] Compress large JSON with metadata only
- [ ] Update document organization rules

---

## 🎯 Success Metrics

**File Size Reduction:**
- `brain-protection-rules.yaml`: 4,385 → 1,500 lines (65% ↓)
- `planning_orchestrator.py`: 1,800 → 500 lines (72% ↓)
- `documents/analysis/`: Remove 15+ duplicate JSON files

**Code Quality:**
- ✅ No module > 1,000 lines
- ✅ No YAML file > 2,000 lines
- ✅ All rationales in markdown (DRY principle)
- ✅ Pre-commit hook prevents future bloat

**Performance:**
- ✅ YAML parsing time < 100ms (vs current ~200ms)
- ✅ All tests still passing (0 regressions)
- ✅ Import time unchanged (module decomposition)

---

## 🔒 SKULL Protection

**New Rule:** `FILE_BLOAT_PREVENTION_ENFORCEMENT`

```yaml
- rule_id: FILE_BLOAT_PREVENTION_ENFORCEMENT
  name: File Bloat Prevention (DRY Principle)
  severity: warning  # Not blocked - allows manual overrides
  description: "Prevents files from exceeding size thresholds. Suggests refactoring when limits exceeded."
  detection:
    thresholds:
      yaml: {lines: 2000, kb: 100}
      py: {lines: 1000, kb: 50}
      md: {lines: 1500, kb: 75}
      json: {lines: 500, kb: 25}
  alternatives:
    - Extract inline content to separate files (DRY)
    - Use #file: references for documentation
    - Decompose large modules into packages
    - Archive historical analysis files
  test_requirements:
    - Threshold detection accuracy
    - Suggestion generation for each file type
    - Pre-commit hook integration
    minimum_coverage: 85
```

---

## 📊 Impact Analysis

**Before:**
- 4,385-line YAML (hard to navigate, slow parsing)
- 1,800-line Python module (violates SRP)
- 20+ duplicate JSON files (wasted storage)
- No automated bloat detection

**After:**
- 1,500-line YAML (65% smaller, faster parsing)
- 7 focused Python modules (300 lines each, testable)
- Cleaned analysis folder (5 files kept, 15 archived)
- Automated bloat prevention (pre-commit hook)

**Developer Experience:**
- ⏱️ Faster file loading in IDEs
- 🔍 Easier navigation (smaller files)
- 🧪 Better testability (module isolation)
- 📚 Clear documentation (markdown rationales)

---

## 🔗 Dependencies

**Requires:**
- Phase 1-7 complete (folder organization stable)
- Git checkpoint integration working
- All existing tests passing

**Blocks:**
- Nothing (quality improvement, non-blocking)

**Enables:**
- Easier onboarding (smaller, focused files)
- Faster CI/CD (less parsing overhead)
- Better maintainability (DRY principle)

---

## 📝 Notes

- **Conservative Approach:** Start with YAML (biggest impact), then Python
- **Backward Compatibility:** All `#file:` references must work
- **Performance:** Benchmark before/after to ensure no regression
- **Documentation:** Update architecture docs with new structure

**Estimated Duration:** 7 days (1 week)  
**Risk Level:** LOW (refactoring only, no logic changes)  
**Priority:** MEDIUM (quality improvement, not critical)
