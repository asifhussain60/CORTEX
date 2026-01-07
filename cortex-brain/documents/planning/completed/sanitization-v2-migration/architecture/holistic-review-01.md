# Holistic Review #1: Before Design Phase
# Sanitization v2 Migration - Architectural Analysis

**Review Date:** January 3, 2026  
**Reviewer:** CORTEX Planning System v5  
**Scope:** ADO v2, Cleanup v2, Vacuum v2 completed migrations  
**Purpose:** Extract patterns, identify improvements, inform Sanitization v2 design

---

## 📊 Migration Analysis Summary

### Completed Migrations

| Orchestrator | Type | Components | Lines of Code | Test Coverage | Patterns |
|--------------|------|------------|---------------|---------------|----------|
| **ADO v2** | Dual-mode | 3 core + wizard | ~1,200 | 95%+ | Conversational wizard, phase-based workflow |
| **Cleanup v2** | Autonomous | 4 engines | ~800 | 95%+ | Mode-based routing, category cleaners |
| **Vacuum v2** | Autonomous | 5 engines | ~2,442 | 100% | Progressive hashing, transactional ops |

**Total Implementation:** ~4,442 lines of production code + ~2,500 lines of tests

---

## 🎯 Architectural Patterns Discovered

### 1. **Engine-Based Modular Architecture** ✅ PROVEN

All v2 orchestrators follow a consistent pattern:

```
orchestrator_v2.py          # Orchestrator (inherits BaseOrchestrator v4.1)
├── engine_1.py             # Specialized engine (e.g., filesystem_engine)
├── engine_2.py             # Specialized engine (e.g., safety_validator)
├── engine_3.py             # Specialized engine (e.g., duplicate_detector)
└── ...
```

**Benefits:**
- ✅ Clear separation of concerns
- ✅ Testable in isolation
- ✅ Reusable across orchestrators
- ✅ Easier to maintain and extend

**Recommendation for Sanitization v2:**
- Follow the same pattern with 5 engines:
  1. `code_analyzer_engine.py` - File scanning, terminology extraction
  2. `transformer_engine.py` - AST transformation, file operations
  3. `validator_engine.py` - Build validation, test execution
  4. `report_generator_engine.py` - Audit reports, metrics
  5. `mapping_engine.py` - Domain→generic mapping, conflict resolution

---

### 2. **Transactional Operations Pattern** ✅ CRITICAL FOR SANITIZATION

**Vacuum v2 Implementation:**
```python
class FilesystemTransaction:
    def __init__(self, checkpoint_dir: Path):
        self.operations: List[FileOperation] = []
        self.checkpoint_dir = checkpoint_dir
    
    def commit(self) -> bool:
        """Execute all operations atomically."""
        for op in self.operations:
            self._execute_operation(op)
            self._verify_operation(op)  # SHA256 hash check
    
    def rollback(self) -> bool:
        """Restore from checkpoint."""
        for backup_file in self.checkpoint_dir.glob("**/*"):
            original_path = self._get_original_path(backup_file)
            shutil.copy2(backup_file, original_path)
```

**Why This Matters for Sanitization:**
- Code transformation is **HIGH RISK** (can break builds)
- Must support atomic rollback if validation fails
- Backup creation before any modifications

**Recommendation:**
- Implement `TransformationTransaction` class
- Checkpoint creation before transformation phase
- SHA256 verification of transformed files
- Automatic rollback on validation failure

---

### 3. **Safety Validation Layers** ✅ ESSENTIAL

**Vacuum v2's 5-Level Risk Classification:**
```yaml
SAFE:     Cache files, temp files (<24h old)
LOW:      Build artifacts, log files
MEDIUM:   Duplicates (not in git), orphan tests
HIGH:     Git-uncommitted files, recent files (<24h)
CRITICAL: Brain tier0-3, database, manifests, src/
```

**Sanitization v2 Risk Classification:**
```yaml
SAFE:     Documentation files, README, comments
LOW:      Variable names, function parameters
MEDIUM:   Class names, module names
HIGH:     File names, directory structure
CRITICAL: Configuration files, database schemas, API contracts
```

**Recommendation:**
- Implement `SanitizationSafetyValidator` class
- Pre-transformation risk assessment
- User approval required for HIGH/CRITICAL changes
- Dry-run mode by default (like Vacuum v2)

---

### 4. **Progressive Computation Strategy** ✅ PERFORMANCE OPTIMIZATION

**Vacuum v2's Three-Phase Hashing:**
```python
# Phase 1: Size grouping (instant)
size_groups = group_by_size(files)

# Phase 2: Quick hash (first 8KB only)
for group in size_groups:
    if len(group) > 1:
        quick_hash_groups = quick_hash(group)

# Phase 3: Full hash (only if quick hash matches)
for quick_group in quick_hash_groups:
    if len(quick_group) > 1:
        full_hash(quick_group)
```

**Benefit:** Avoids expensive full-file hashing (reduced from O(n²) to O(n log n))

**Sanitization v2 Equivalent:**
```python
# Phase 1: File type detection (instant)
python_files, config_files, doc_files = categorize_files()

# Phase 2: AST parsing (only Python files)
ast_cache = parse_python_files(python_files)

# Phase 3: Deep analysis (only files with domain terms)
domain_terms = extract_from_ast(ast_cache)
```

**Recommendation:**
- Implement progressive AST analysis
- Cache parsed ASTs (avoid re-parsing)
- Only deep-analyze files with potential domain terms

---

### 5. **Configuration-Driven Behavior** ✅ FLEXIBILITY

**Common Pattern Across All v2 Orchestrators:**
```yaml
# orchestrator-v2.yaml
execution:
  dry_run_default: true        # Safety first
  auto_approve_threshold: 5    # Auto-approve if <5 files affected
  
safety:
  protected_paths:
    - "cortex-brain/tier0/"
    - "src/database/"
  
patterns:
  user_requests:
    - "^sanitize .*$"
    - "^clean code.*$"
```

**Recommendation for Sanitization v2:**
- YAML config for:
  - Sanitization patterns (domain terms, generic mappings)
  - Protected file types (never transform)
  - Transformation rules (naming conventions)
  - Validation thresholds (build pass/fail criteria)

---

### 6. **Dual-Mode Architecture** (ADO v2 Innovation) 🆕

**ADO v2's Unique Contribution:**
```python
def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
    if self._is_autonomous_context(context):
        return self._execute_autonomous(context)  # Batch mode
    else:
        return self._execute_wizard(context)      # Interactive mode
```

**Why This Could Benefit Sanitization:**
- **Autonomous Mode:** Batch sanitization with pre-approved mappings
- **Wizard Mode:** Interactive mapping approval for complex projects

**Recommendation:**
- Consider dual-mode for Sanitization v2:
  - **Autonomous:** Use existing `sanitization-mappings.json`
  - **Wizard:** Interactive domain term review and approval

---

### 7. **BaseOrchestrator v4.1 Compliance** ✅ MANDATORY

**Standard Implementation Pattern:**
```python
class SanitizationOrchestratorV2(BaseOrchestratorV4_1):
    def __init__(self, config_path, state_db=None, plan_id=None):
        super().__init__(config_path, state_db, plan_id)
        # Initialize engines
    
    def execute(self, user_request: str, **kwargs) -> OrchestratorResult:
        # Phase execution
    
    def _phase_1_analyze(self) -> PhaseResult:
        # Phase logic
```

**Requirements:**
- ✅ Inherit from `BaseOrchestratorV4_1`
- ✅ Use `PlanningStateDB` for state persistence
- ✅ Return `OrchestratorResult` with standardized structure
- ✅ Implement phase methods (`_phase_N_name`)

---

## 🔍 Reusable Components Identified

### From Vacuum v2

1. **`FilesystemEngine::create_checkpoint()`** - Can be reused for backup creation
2. **`SafetyValidator::is_protected_path()`** - Reusable for brain protection
3. **`FilesystemTransaction` class** - Adapt for transformation operations

### From Cleanup v2

1. **Mode-based routing** - Can adapt for sanitization modes (full/quick/targeted)
2. **Category cleaner pattern** - Similar to engine pattern

### From ADO v2

1. **Wizard conversation flow** - Can adapt for mapping approval workflow
2. **Context completeness detection** - Useful for autonomous vs wizard decision

---

## 🚀 Recommendations for Sanitization v2

### Architecture Decisions

1. **✅ ADOPT: Engine-Based Architecture**
   - 5 specialized engines (analyzer, transformer, validator, reporter, mapper)
   - Each engine 200-400 lines, highly focused

2. **✅ ADOPT: Transactional Operations**
   - `TransformationTransaction` class
   - Checkpoint before transformation
   - Atomic rollback on failure

3. **✅ ADOPT: Progressive Analysis**
   - Quick scan → AST parsing → Deep analysis
   - Cache parsed ASTs to avoid re-parsing

4. **⚠️ CONSIDER: Dual-Mode Architecture**
   - Autonomous mode for batch sanitization
   - Wizard mode for interactive mapping approval
   - Decision: Evaluate complexity vs benefit

5. **✅ ADOPT: 5-Level Risk Classification**
   - SAFE → LOW → MEDIUM → HIGH → CRITICAL
   - User approval for HIGH/CRITICAL transformations

6. **✅ ADOPT: Dry-Run Default**
   - Always preview transformations first
   - Require explicit `--execute` flag

### Code Reuse Opportunities

1. **Checkpoint System** (from Vacuum v2)
   ```python
   # Import and adapt
   from src.orchestrators.vacuum.filesystem_engine import FilesystemEngine
   
   class TransformerEngine:
       def __init__(self):
           self.filesystem = FilesystemEngine(...)
       
       def create_backup(self, files: List[Path]) -> Path:
           return self.filesystem.create_checkpoint(files)
   ```

2. **Safety Validation** (from Vacuum v2)
   ```python
   # Import and extend
   from src.orchestrators.vacuum.safety_validator import SafetyValidator
   
   class SanitizationSafetyValidator(SafetyValidator):
       def classify_transformation_risk(self, file_path, changes):
           # Extend with sanitization-specific rules
   ```

3. **Wizard Flow** (from ADO v2)
   ```python
   # Adapt conversation patterns
   from src.orchestrators.ado.v2.ado_conversational_wizard import ConversationalWizard
   
   class MappingApprovalWizard:
       # Similar phase-based approval workflow
   ```

### New Components to Build

1. **`code_analyzer_engine.py`** - AST parsing, terminology extraction
2. **`transformer_engine.py`** - Code transformation, file renaming
3. **`mapping_engine.py`** - Domain→generic mapping logic (reuse existing utilities)
4. **`validator_engine.py`** - Build validation, test execution
5. **`report_generator_engine.py`** - Audit reports (reuse existing utilities)

---

## 📋 Design Phase Action Items

Based on this holistic review, the Design Phase (Task #4) should:

1. ✅ **Create architecture diagram** showing 5 engines + orchestrator
2. ✅ **Define transactional operation flow** (backup → transform → validate → commit/rollback)
3. ✅ **Specify risk classification rules** (5 levels with examples)
4. ✅ **Design progressive analysis pipeline** (quick scan → AST → deep analysis)
5. ⚠️ **Evaluate dual-mode architecture** (autonomous vs wizard) - cost/benefit analysis
6. ✅ **Document code reuse strategy** (which components to import vs adapt vs build new)
7. ✅ **Define YAML configuration structure** (patterns, rules, thresholds)

---

## 🎯 Success Criteria for Sanitization v2

Based on v2 migration patterns:

1. **Code Quality:**
   - ✅ ~2,000-2,500 lines production code
   - ✅ ~1,500-2,000 lines test code
   - ✅ 95%+ test coverage

2. **Architecture:**
   - ✅ BaseOrchestrator v4.1 compliant
   - ✅ 5 specialized engines
   - ✅ Transactional operations with rollback
   - ✅ State persistence in PlanningStateDB

3. **Safety:**
   - ✅ Dry-run mode by default
   - ✅ 5-level risk classification
   - ✅ CORTEX brain protection
   - ✅ Checkpoint/rollback system

4. **Integration:**
   - ✅ Master Orchestrator routing (priority 57)
   - ✅ Pattern-based request detection
   - ✅ Template-driven reporting

5. **Documentation:**
   - ✅ Completion report (like Vacuum v2)
   - ✅ Migration guide
   - ✅ Architecture documentation

---

## 🔄 Cross-Phase Recommendations

### For Configuration Phase (Task #9)

- **Pattern from Vacuum v2:** Comprehensive YAML with nested structures
- **Improvement:** Add JSON Schema validation for config files
- **New Idea:** Shared config validation utility (`src/utils/config_validator.py`)

### For Testing Phase (Task #10)

- **Pattern from Vacuum v2:** 95 test cases, ~1,550 lines
- **Improvement:** Parameterized tests for transformation scenarios
- **New Idea:** Test fixture generator for sample codebases

### For Integration Phase (Task #12)

- **Pattern from All v2:** Priority-based routing in `master-orchestrator.yaml`
- **Improvement:** Routing pattern validation during CI/CD
- **New Idea:** Orchestrator discovery tool (lists all registered orchestrators)

---

## 📊 Complexity Estimate

Based on completed migrations:

| Component | Estimated Lines | Complexity | Reuse Potential |
|-----------|-----------------|------------|-----------------|
| `sanitization_orchestrator_v2.py` | 600-700 | MEDIUM | 30% (BaseOrch v4.1 pattern) |
| `code_analyzer_engine.py` | 400-500 | HIGH | 50% (existing utilities) |
| `transformer_engine.py` | 500-600 | HIGH | 20% (AST complexity) |
| `validator_engine.py` | 300-400 | MEDIUM | 40% (existing utilities) |
| `report_generator_engine.py` | 200-300 | LOW | 60% (existing utilities) |
| `mapping_engine.py` | 300-400 | MEDIUM | 70% (existing utilities) |
| **Total Production Code** | **~2,300-2,900** | **MEDIUM-HIGH** | **~45% reuse** |
| **Test Code** | **~1,500-2,000** | **MEDIUM** | **40% pattern reuse** |

**Total Implementation Effort:** ~4,000-5,000 lines (2 days realistic)

---

## ✅ Holistic Review Conclusion

**Key Insights:**
1. ✅ Engine-based architecture is proven and should be adopted
2. ✅ Transactional operations are critical for safe code transformation
3. ✅ Progressive analysis will optimize performance
4. ⚠️ Dual-mode architecture needs evaluation (complexity vs benefit)
5. ✅ ~45% code reuse from existing utilities is achievable

**Recommended Design Approach:**
- Start with **single-mode autonomous** (simplest)
- Add wizard mode later if user feedback indicates need
- Focus on transactional safety and rollback capability
- Leverage existing utilities aggressively

**Next Step:**
- Proceed to Task #4 (Design Phase) with these insights
- Create detailed architecture document
- Define component interfaces
- Plan code reuse strategy

---

**Review Status:** ✅ Complete  
**Approved for Design Phase:** YES  
**Architecture Complexity:** MEDIUM-HIGH (justified by safety requirements)  
**Implementation Risk:** LOW (proven patterns from 3 successful migrations)
