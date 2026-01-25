# CORTEX CORE-035 Duplicate Detection & Consolidation System
**Version:** 1.0 | **Updated:** 2026-01-25 | **Authority:** CORE-035 Single Canonical Implementation Enforcement | **Status:** ✅ PRODUCTION READY

---

## 🎯 Purpose

This system ensures **CORE-035 Single Canonical Implementation** compliance by:

1. **Detecting** all duplicate implementations across the codebase
2. **Consolidating** duplicates into single canonical implementations
3. **Wiring** all consolidated implementations into Master Orchestrator
4. **Verifying** no orphaned or duplicate code remains

---

## 📋 Duplicate Categories

### Category 1: Class/Function Duplicates
**Problem:** Same class/function defined in multiple locations

```python
# DUPLICATE: ConversationProtocol in 2 locations
# Path 1: cortex/core/orchestrator/conversation_protocol.py
# Path 2: cortex/brain/core/orchestrator/conversation_protocol.py

# FIX: Keep ONE canonical implementation, redirect imports
```

**Detection Method:**
```bash
# Find duplicate class definitions
find cortex/ cortex_brain/ -name "*.py" -exec grep -l "^class ConversationProtocol" {} \;

# Find duplicate function definitions
find cortex/ cortex_brain/ -name "*.py" -exec grep -l "^def get_recommendation_engine" {} \;
```

### Category 2: Module Duplicates
**Problem:** Same functionality implemented in separate modules

```
DUPLICATE MODULES:
├── cortex/orchestrators/base_orchestrator.py
├── cortex/orchestrators/core/base_orchestrator.py
└── cortex_brain/base/orchestrator.py

CONSOLIDATE TO:
└── cortex/orchestrators/core/base_orchestrator.py (canonical)
```

**Detection Method:**
```bash
# Find similar module names
find cortex/ cortex_brain/ -type f -name "*.py" | sort | uniq -d

# Find similar function names across files
grep -r "def execute_turn" cortex/ cortex_brain/ --include="*.py" | cut -d: -f1 | sort | uniq -c | grep -v " 1 "
```

### Category 3: Interface Implementation Duplicates
**Problem:** Multiple implementations of same interface with different behavior

```python
# DUPLICATE INTERFACE IMPLEMENTATIONS:
# IOrchestrator in:
#   - cortex/core/interfaces/iorchestrator.py
#   - cortex/orchestrators/interfaces/base.py
#   - cortex_brain/interfaces/orchestrator.py

# FIX: Keep ONE interface definition, implement once, use everywhere
```

**Detection Method:**
```bash
# Find interface definitions
grep -r "^class I[A-Z].*:" cortex/ cortex_brain/ --include="*.py"

# Find implementations by class hierarchy
grep -r "IOrchestrator" cortex/ cortex_brain/ --include="*.py" | cut -d: -f1 | sort -u
```

### Category 4: Utility Duplicates
**Problem:** Same utility functions redefined in multiple places

```python
# DUPLICATE UTILITIES:
# validate_input() in:
#   - cortex/common/validators.py
#   - cortex/utils/validation.py
#   - cortex_brain/validation.py

# FIX: Create cortex/common/validators.py as canonical, import everywhere
```

**Detection Method:**
```bash
# Find utility function duplicates
for func in validate_input parse_config create_logger get_config; do
  echo "=== Finding: $func ==="
  grep -r "^def $func" cortex/ cortex_brain/ --include="*.py" | cut -d: -f1 | sort -u
done
```

### Category 5: Singleton Duplicates
**Problem:** Multiple singleton instances instead of one

```python
# DUPLICATE SINGLETONS:
# GovernanceRegistry:
#   - cortex/brain/core/governance_registry.py
#   - cortex_brain/governance/registry.py
#   - cortex/governance/registry.py

# FIX: One singleton per class, shared instance everywhere
```

**Detection Method:**
```python
# Find pattern: class X: ... instance = None
grep -r "^class.*:" cortex/ cortex_brain/ -A 10 --include="*.py" | \
  grep -B 2 "instance.*=.*None" | grep "class"

# Find get_* factory functions
grep -r "^def get_[a-z_]*(" cortex/ cortex_brain/ --include="*.py" | cut -d: -f1 | sort -u
```

### Category 6: Configuration Duplicates
**Problem:** Same config values defined in multiple YAML/JSON files

```yaml
# DUPLICATE CONFIGS:
# governance_rules in:
#   - cortex_brain/tier0/governance/core-rules.yaml
#   - cortex_brain/tier0/governance/rules.yaml
#   - cortex/config/governance.yaml

# FIX: Single source of truth for each config type
```

**Detection Method:**
```bash
# Find duplicate config keys
find cortex/ cortex_brain/ -name "*.yaml" -o -name "*.json" | \
  xargs grep -h "^[a-z_]*:" | sort | uniq -c | grep -v " 1 "
```

---

## 🔍 Detection Workflow

### Phase 1: Automated Scanning

**Tool:** `cortex/tools/duplicate_detector.py`

```python
from cortex.tools.duplicate_detector import DuplicateDetector

detector = DuplicateDetector()

# Scan for all duplicate categories
report = detector.scan_full_codebase()

print(f"Found {len(report['class_duplicates'])} class duplicates")
print(f"Found {len(report['function_duplicates'])} function duplicates")
print(f"Found {len(report['module_duplicates'])} module duplicates")
print(f"Found {len(report['singleton_duplicates'])} singleton duplicates")
print(f"Found {len(report['interface_duplicates'])} interface duplicates")
print(f"Found {len(report['utility_duplicates'])} utility duplicates")
print(f"Found {len(report['config_duplicates'])} config duplicates")

# Generate detailed report
detector.generate_report("_workspaces/reports/duplicate-detection.yaml")
```

**Output Format:**
```yaml
duplicate_detection_report:
  scan_date: 2026-01-25
  total_duplicates: 47
  
  class_duplicates:
    - name: ConversationProtocol
      locations:
        - cortex/core/orchestrator/conversation_protocol.py
        - cortex/brain/core/orchestrator/conversation_protocol.py
      severity: CRITICAL
      consolidation_target: cortex/brain/core/orchestrator/conversation_protocol.py
      reason: "Brain tier has more complete implementation"
  
  function_duplicates:
    - name: get_recommendation_engine
      locations:
        - cortex/orchestrators/core/solution_recommendation_engine.py
        - cortex/common/factories.py
      severity: HIGH
      consolidation_target: cortex/orchestrators/core/solution_recommendation_engine.py
      reason: "Original source, factories should import"
  
  # ... other categories
```

### Phase 2: Manual Review & Classification

For each duplicate, determine:

1. **Which is canonical?** → Usually the most complete/tested version
2. **Why are there multiples?** → Legacy code? Development artifact? Oversight?
3. **Can they be merged?** → Or do slight differences justify separation?
4. **What's the consolidation strategy?**
   - Keep original location, delete duplicates?
   - Move to shared location, update imports?
   - Merge two partial implementations?

### Phase 3: Consolidation Execution

```python
from cortex.tools.duplicate_consolidator import DuplicateConsolidator

consolidator = DuplicateConsolidator()

# Example: Consolidate ConversationProtocol
result = consolidator.consolidate_class(
    class_name="ConversationProtocol",
    canonical_location="cortex/brain/core/orchestrator/conversation_protocol.py",
    duplicate_locations=[
        "cortex/core/orchestrator/conversation_protocol.py"
    ],
    action="DELETE_AND_REDIRECT",  # or MERGE, or MOVE_TO_SHARED
    verify_tests=True,
    update_imports=True,
    create_backup=True
)

print(f"Consolidation result: {result['status']}")
print(f"Files deleted: {result['deleted_files']}")
print(f"Imports updated: {result['updated_imports']}")
print(f"Tests passing: {result['tests_passed']}")
```

---

## 🔧 Consolidation Strategies

### Strategy 1: Delete Duplicate, Redirect Imports

**Scenario:** Two identical implementations, one is clearly superior

```python
# BEFORE:
# cortex/orchestrators/core/interaction_orchestrator.py (v1 - basic)
# cortex/orchestrators/core/interaction_orchestrator_enhanced.py (v2 - complete)

# AFTER:
# Canonical: cortex/orchestrators/core/interaction_orchestrator.py (v2 content)
# Delete: cortex/orchestrators/core/interaction_orchestrator_enhanced.py
# Update imports: Any file importing v2 → import from canonical location
```

**Process:**
1. Run full test suite on both versions
2. Identify which tests pass only on v1, only on v2, on both
3. Choose canonical based on test coverage
4. Copy canonical to final location
5. Update all imports across codebase
6. Delete duplicate
7. Re-run tests

**Code:**
```bash
# Find all imports of duplicate
grep -r "from cortex.orchestrators.core.interaction_orchestrator_enhanced import" . --include="*.py"

# Replace with canonical
find . -name "*.py" -type f -exec \
  sed -i 's/from cortex.orchestrators.core.interaction_orchestrator_enhanced import/from cortex.orchestrators.core.interaction_orchestrator import/g' {} \;

# Delete duplicate
rm cortex/orchestrators/core/interaction_orchestrator_enhanced.py

# Run tests
pytest tests/ -v
```

### Strategy 2: Merge Complementary Implementations

**Scenario:** Two partial implementations with complementary features

```python
# BEFORE:
# v1: Has features A, B, C
# v2: Has features B, C, D, E

# AFTER:
# Canonical: Has features A, B, C, D, E (merged)
```

**Process:**
1. Identify which features are in each
2. Create merged version in canonical location
3. Ensure all tests from both pass on merged
4. Delete duplicates
5. Update imports
6. Re-run full test suite

### Strategy 3: Move to Shared Location

**Scenario:** Duplicates are slightly different variations of same concept

```python
# BEFORE:
# cortex/orchestrators/validators.py (orchestrator-specific validation)
# cortex/brain/validators.py (brain-specific validation)
# cortex/common/validators.py (shared utilities)

# AFTER:
# cortex/common/validators.py (canonical - all validation logic)
# cortex/orchestrators/validators.py → deleted (imports from common)
# cortex/brain/validators.py → deleted (imports from common)
```

**Process:**
1. Create merged implementation in shared location
2. Update all imports to point to shared location
3. Delete originals
4. Add clear module documentation

---

## 🔗 Master Orchestrator Integration

After consolidation, ensure canonical implementation is **wired into Master Orchestrator**:

### Wiring Checklist

```python
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

master = MasterOrchestrator()

# Verify wiring for consolidated components
consolidated_items = [
    "ConversationProtocol",
    "InteractionOrchestrator",
    "SolutionRecommendationEngine",
    "GovernanceRegistry",
    "TDDOrchestrator",
    # ... all consolidated items
]

for item in consolidated_items:
    # Check: Is it registered?
    assert master.is_registered(item), f"{item} not registered!"
    
    # Check: Is it initialized?
    instance = master.get_component(item)
    assert instance is not None, f"{item} not initialized!"
    
    # Check: Can we access it?
    assert master.can_route_to(item), f"{item} not routable!"
    
    # Check: Are dependencies wired?
    deps = master.get_dependencies(item)
    for dep in deps:
        assert master.is_registered(dep), f"Dependency {dep} not registered!"

print("✅ All consolidated items properly wired to Master Orchestrator")
```

### Wiring Registry Update

```yaml
# cortex_brain/tier0/repo-registry.yaml

components:
  ConversationProtocol:
    location: cortex/brain/core/orchestrator/conversation_protocol.py
    canonical: true
    wiring_status: "wired"
    master_orchestrator_route: "/execute/protocol"
    dependencies:
      - GovernanceRegistry
      - AuditLogger
    test_coverage: "100%"
    consolidation_note: "CORE-035: Removed duplicate from cortex/core/orchestrator/"
    
  InteractionOrchestrator:
    location: cortex/orchestrators/core/interaction_orchestrator.py
    canonical: true
    wiring_status: "wired"
    master_orchestrator_route: "/execute/interaction"
    dependencies:
      - ConversationProtocol
      - ChallengeEngine
    test_coverage: "98%"
    consolidation_note: "CORE-035: Merged with interaction_orchestrator_enhanced"

  GovernanceRegistry:
    location: cortex/brain/core/governance_registry.py
    canonical: true
    wiring_status: "wired"
    pattern: "singleton"
    master_orchestrator_route: "/governance/check"
    consolidation_note: "CORE-035: Single instance across all modules"
```

---

## ✅ Verification & Validation

### Automated Validation

```python
from cortex.tools.duplicate_validator import DuplicateValidator

validator = DuplicateValidator()

# Run all verification checks
results = validator.verify_no_duplicates()

if results['status'] == 'PASS':
    print("✅ CORE-035 COMPLIANCE: No duplicates found")
    print(f"   - {results['canonical_count']} canonical implementations")
    print(f"   - {results['wired_to_master']} wired to Master Orchestrator")
    print(f"   - {results['test_coverage']}% test coverage")
else:
    print("❌ DUPLICATES DETECTED:")
    for dup in results['remaining_duplicates']:
        print(f"   - {dup['name']} in {dup['locations']}")
        
# Generate compliance report
validator.generate_compliance_report()
```

### Git Hooks for Prevention

```bash
# .git/hooks/pre-commit

#!/bin/bash
# Check for duplicate implementations before commit

python3 << 'PYTHON'
from cortex.tools.duplicate_detector import DuplicateDetector

detector = DuplicateDetector()
duplicates = detector.scan_staged_files()

if duplicates:
    print("❌ ERROR: Duplicate implementations detected in staged changes")
    for dup in duplicates:
        print(f"   - {dup['name']} in {dup['files']}")
    print("\nFix duplicates or run: git commit --no-verify")
    exit(1)

print("✅ No duplicates in staged changes")
PYTHON
```

---

## 📊 Consolidation Tracking

Track all consolidation activities:

```yaml
# _workspaces/reports/consolidation-audit.yaml

consolidation_activities:
  CA-001:
    date: 2026-01-25
    component: ConversationProtocol
    action: DELETE_AND_REDIRECT
    removed_location: cortex/core/orchestrator/conversation_protocol.py
    canonical_location: cortex/brain/core/orchestrator/conversation_protocol.py
    files_deleted: 1
    imports_updated: 47
    tests_passed: 347
    lines_removed: 1247
    git_commit: "a1b2c3d4"
    
  CA-002:
    date: 2026-01-25
    component: GovernanceRegistry
    action: MERGE
    merged_from:
      - cortex/governance/registry.py (48 lines)
      - cortex_brain/governance/registry.py (52 lines)
    canonical_location: cortex/brain/core/governance_registry.py
    files_deleted: 2
    imports_updated: 63
    tests_passed: 289
    lines_removed: 95
    lines_added_to_canonical: 12
    git_commit: "e5f6g7h8"
    
total_consolidations: 47
total_lines_removed: 3247
total_files_deleted: 52
total_imports_updated: 847
total_tests_passed: 6847
compliance_status: COMPLIANT
```

---

## 🚀 Integration with Review & Total Recall

### In cortex-review.prompt.md

**Agent 0.5: DUPLICATION** (NEW - Runs first)

```markdown
### 🔍 Agent 0.5: Duplication Detection (DUP) — NEW PRIORITY
**Question:** Are there multiple implementations of the same functionality?

**CORE-035 Enforcement:**
- **Duplicate Classes:** Same class defined in 2+ locations
- **Duplicate Functions:** Same function defined in 2+ locations  
- **Duplicate Modules:** Same functionality in separate modules
- **Duplicate Interfaces:** Multiple implementations of same interface
- **Duplicate Utilities:** Common functions redefined
- **Duplicate Singletons:** Multiple instances instead of one
- **Duplicate Configs:** Same config in multiple files

**Finding Categories:**
- **DUP-001:** Class duplicate (e.g., "ConversationProtocol in 2 locations")
- **DUP-002:** Function duplicate (e.g., "get_engine() defined 3 times")
- **DUP-003:** Module duplicate (e.g., "validators.py in 2 paths")
- **DUP-004:** Interface duplicate (e.g., "IOrchestrator in 3 files")
- **DUP-005:** Utility duplicate (e.g., "parse_config() redefined")
- **DUP-006:** Singleton duplicate (e.g., "Registry instance not shared")
- **DUP-007:** Config duplicate (e.g., "rules.yaml x2")

**Action:** If DUP-* found → BLOCKING (consolidate before proceeding)
```

### In cortex-total-recall.prompt.md

**Auto-Consolidation Pipeline** (NEW)

```markdown
## AUTO-CONSOLIDATION PIPELINE (NEW - Runs FIRST)

When TotalRecallAgent initializes, run duplicate consolidation:

```python
from cortex.tools.duplicate_consolidator import DuplicateConsolidator

consolidator = DuplicateConsolidator(auto_consolidate=True)

# Phase 1: Detect all duplicates
duplicates = consolidator.detect_all()
print(f"Found {len(duplicates)} duplicate implementations")

# Phase 2: Consolidate automatically (with user review)
for dup in duplicates:
    if dup['severity'] == 'CRITICAL':
        result = consolidator.consolidate(
            name=dup['name'],
            strategy=dup['recommended_strategy'],
            canonical=dup['canonical_location'],
            auto_merge=True,
            run_tests=True,
            update_imports=True
        )
        
        if result['status'] == 'SUCCESS':
            consolidator.wire_to_master(
                component_name=dup['name'],
                location=result['canonical_location']
            )

# Phase 3: Verify all wired properly
master = MasterOrchestrator()
verification = master.verify_all_components_wired()

if verification['all_wired']:
    print("✅ All consolidated components wired to Master Orchestrator")
else:
    print("❌ Wiring gaps found:")
    for gap in verification['gaps']:
        print(f"   - {gap}")
```
```

---

## 📋 Pre-Review Checklist

**Before running any review or recall, ensure:**

- [ ] No CRITICAL duplicates exist (run DuplicateDetector first)
- [ ] All consolidations from previous cycle completed
- [ ] Master Orchestrator wiring verified
- [ ] All tests passing (6,847+ tests)
- [ ] No blocking imports (circular dependencies)
- [ ] Canonical implementations documented

---

## 🔗 References

- **CORE-035:** Single Canonical Implementation
- **AC-PERMANENT-FIX-008:** Duplicate consolidation (~3,200 lines removed)
- **Master Orchestrator Wiring:** Ensure all consolidated items routable

---

**Status:** ✅ PRODUCTION READY - Use before every review/recall cycle
