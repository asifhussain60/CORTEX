# Sanitization Orchestrator Implementation Plan

**Purpose:** Complete Week 10 objectives by implementing missing orchestrator class  
**Created:** December 20, 2025  
**Status:** 🟡 In Progress (Planning Phase)  
**Estimated Duration:** 2-3 days  
**Target Completion:** December 23, 2025  

---

## 📋 Overview

### Context
- **Infrastructure Status:** 100% complete (6 utility modules exist)
- **Gap:** Only orchestrator class missing
- **Pattern:** Follow proven ADO Orchestrator architecture (91.44% coverage achieved)
- **Business Value:** Enable portfolio sharing via code sanitization

### Success Criteria
- ✅ 85%+ test coverage (target: match ADO's 91.44%)
- ✅ 25+ tests passing (RED→GREEN→REFACTOR)
- ✅ 5-phase workflow operational
- ✅ CLI integration validated
- ✅ Planning System 2.0 compliance (DoR/DoD)
- ✅ Completion report generated

---

## 🏗️ Architecture

### File Structure
```
src/orchestrators/sanitization/
├── __init__.py              # Package exports
├── sanitization_orchestrator.py  # Main orchestrator (~350 LOC)
└── tests/
    ├── __init__.py
    ├── test_orchestrator_foundation.py   # 9 tests
    ├── test_analyze_phase.py             # 3 tests
    ├── test_mapping_phase.py             # 3 tests
    ├── test_transform_phase.py           # 3 tests
    ├── test_validate_phase.py            # 3 tests
    ├── test_report_phase.py              # 3 tests
    └── test_integration.py               # 3+ tests
```

### Core Components

**SanitizationOrchestrator (inherits BaseOrchestrator):**
```python
class SanitizationOrchestrator(BaseOrchestrator):
    """Code sanitization workflow orchestrator"""
    
    def __init__(self, target_directory: str, dry_run: bool = False):
        self.target = Path(target_directory)
        self.dry_run = dry_run
        self.analyzer = CodeAnalyzer()
        self.mapper = MappingEngine()
        self.transformer = Transformer()
        self.validator = Validator()
        self.reporter = ReportGenerator()
        
    async def execute(self) -> SanitizationResult:
        # 5-phase workflow with 🎭 engagement hints
```

**SanitizationPhase (Enum):**
```python
class SanitizationPhase(Enum):
    ANALYZE = "1_analyze"
    MAPPING = "2_mapping"
    TRANSFORM = "3_transform"
    VALIDATE = "4_validate"
    REPORT = "5_report"
```

**SanitizationResult (Dataclass):**
```python
@dataclass
class SanitizationResult:
    success: bool
    phase: SanitizationPhase
    files_analyzed: int
    mappings_created: int
    files_transformed: int
    validation_passed: bool
    report_path: Path
    duration_seconds: float
    errors: List[str]
```

---

## 🔄 5-Phase Workflow

### Phase 1: ANALYZE (code_analyzer.py)
- Scan target directory for files
- Extract domain-specific terms
- Identify sensitive patterns
- Generate analysis report
- **User Interaction:** Review term extraction

### Phase 2: MAPPING (mapping_engine.py)
- Generate domain→generic mappings
- Detect naming conflicts
- Apply heuristics for natural names
- **User Interaction:** Approve/edit mappings (REQUIRED)

### Phase 3: TRANSFORM (transformer.py)
- Create backup of original code
- Apply AST transformations
- Rename files/directories
- Update imports and references
- **User Interaction:** None (approval already granted)

### Phase 4: VALIDATE (validator.py)
- Run build system (if exists)
- Execute test suite
- Verify functionality preserved
- **User Interaction:** Rollback prompt on failure

### Phase 5: REPORT (report_generator.py)
- Generate audit report
- Document all transformations
- Create mapping artifact
- Calculate metrics
- **User Interaction:** Review completion summary

---

## 🧪 TDD Strategy

### RED → GREEN → REFACTOR Cycle

**Task 1: Foundation (RED)**
```python
# tests/test_orchestrator_foundation.py
def test_inherits_base_orchestrator()
def test_sanitization_phase_enum()
def test_sanitization_result_dataclass()
def test_orchestrator_initialization()
def test_dry_run_mode()
def test_engagement_hints_logged()
def test_phase_transitions()
def test_error_handling()
def test_cleanup_on_failure()
```

**Task 2-6: Phase Testing (RED per phase)**
- 3 tests per phase (setup, execution, error cases)
- Integration with utility modules
- User interaction simulation
- Performance validation

**Task 7: Integration (RED end-to-end)**
```python
# tests/test_integration.py
def test_full_workflow_success()
def test_workflow_with_user_rejection()
def test_workflow_with_validation_failure()
def test_dry_run_workflow()
```

---

## 📊 Integration Points

### Existing Utilities (Already Complete)
- ✅ `code_analyzer.py` - File scanning, term extraction (~300 LOC)
- ✅ `mapping_engine.py` - Mapping generation (~250 LOC)
- ✅ `transformer.py` - AST transformations (~200 LOC)
- ✅ `validator.py` - Build/test validation (~200 LOC)
- ✅ `report_generator.py` - Audit reports
- ✅ `__init__.py` - Package initialization

### CLI Wrapper (Already Exists)
- ✅ `scripts/cli_wrappers/sanitize_wrapper.py` (~150 LOC)
- Expects: `from src.operations.modules.orchestration.sanitization_orchestrator import SanitizationOrchestrator`
- **Action Required:** Update import path after creating orchestrator

### Manifest (Already Complete)
- ✅ `cortex-brain/manifests/orchestrators/code-sanitization-manifest.yaml`
- Defines: 5 phases, triggers, compliance rules, user interactions

---

## 🎯 Implementation Timeline

### Day 1 (December 20, 2025)
- ✅ Task 1: Orchestrator Foundation (3h)
- ✅ Task 2: Analyze Phase Integration (3h)
- ✅ Task 3: Mapping Phase (4h)
- **Target:** 15 tests passing, 3 phases complete

### Day 2 (December 21, 2025)
- ✅ Task 4: Transform Phase (4h)
- ✅ Task 5: Validate Phase (3h)
- ✅ Task 6: Report Phase (2h)
- **Target:** 24 tests passing, all 5 phases complete

### Day 3 (December 22, 2025)
- ✅ Task 7: Integration Tests (3h)
- ✅ Task 8: Documentation (2h)
- ✅ Task 9: Completion Report (1h)
- **Target:** 27+ tests, 85%+ coverage, report generated

---

## ✅ Quality Gates

### Code Quality
- [ ] Inherits BaseOrchestrator correctly
- [ ] Uses 🎭 engagement hints pattern
- [ ] All phases implemented with proper error handling
- [ ] Type hints on all public methods
- [ ] Docstrings follow Google style

### Testing
- [ ] 25+ tests passing (100% pass rate)
- [ ] 85%+ code coverage (target: 91.44% like ADO)
- [ ] RED→GREEN→REFACTOR cycle documented
- [ ] Integration tests validate full workflow

### Documentation
- [ ] Usage guide in cortex-brain/documents/implementation-guides/
- [ ] API documentation updated
- [ ] Manifest compliance validated
- [ ] Completion report generated (follow ADO template)

### Compliance
- [ ] Planning System 2.0 DoR/DoD validated
- [ ] SKULL rules enforced (TDD, code discovery, git isolation)
- [ ] Brain protection validated
- [ ] Status file updated

---

## 📈 Metrics Tracking

### Performance Targets
- **Analyze Phase:** <2s for 100 files
- **Mapping Phase:** <1s generation time
- **Transform Phase:** <3s for 100 files
- **Validate Phase:** <build_time + test_time + 2s
- **Report Phase:** <1s
- **Total Workflow:** <10s + build/test time

### Coverage Targets
- **Orchestrator:** 90%+ (match ADO's 91.44%)
- **Phase Integration:** 85%+
- **Error Paths:** 80%+

---

## 🚀 Next Actions

1. **Create test file:** `tests/test_orchestrator_foundation.py`
2. **Write 9 RED tests** for foundation
3. **Implement minimal orchestrator** (GREEN)
4. **Refactor** phase logic extraction
5. **Repeat** for phases 2-6
6. **Integration tests** end-to-end
7. **Generate completion report**

---

## 📚 References

- **Pattern:** ADO Orchestrator (`src/orchestrators/ado/ado_orchestrator.py`)
- **Utilities:** `src/operations/utilities/sanitization/`
- **Manifest:** `cortex-brain/manifests/orchestrators/code-sanitization-manifest.yaml`
- **CLI:** `scripts/cli_wrappers/sanitize_wrapper.py`
- **Completion Template:** ADO-ORCHESTRATOR-COMPLETION-REPORT.md

---

**Status Legend:**
- 🔴 Blocked
- 🟡 In Progress
- 🟢 Complete
- ⚪ Not Started
