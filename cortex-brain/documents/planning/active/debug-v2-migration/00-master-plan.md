# 🛡️ Debug Orchestrator v2 Migration

**Plan ID:** debug-v2-migration  
**Feature:** Convert GUIDED Debug Orchestrator to AUTONOMOUS Architecture  
**Created:** January 3, 2026  
**Complexity:** TIER 4 (ORCHESTRATOR MIGRATION)  
**Strategy:** Pure autonomous root cause analysis + automated fix generation  
**Estimated Duration:** 3 days

---

## 📊 Visual Progress Tracker

**Overall Progress:** `░░░░░░░░░░` **0%** ⏸️ NOT STARTED

| Phase | Name | Progress | Duration | Status |
|-------|------|----------|----------|--------|
| 0 | Context Discovery | `░░░░░░░░░░` | 4h | ⏸️ Not Started |
| 1 | Core Orchestrator + Root Cause Engine | `░░░░░░░░░░` | 1d | ⏸️ Not Started |
| 2 | Fix Generation + Marker Injection | `░░░░░░░░░░` | 1d | ⏸️ Not Started |
| 3 | Master Orchestrator Wiring | `░░░░░░░░░░` | 4h | ⏸️ Not Started |
| 4 | Testing & Validation | `░░░░░░░░░░` | 4h | ⏸️ Not Started |
| 5 | Documentation & REFACTOR | `░░░░░░░░░░` | 2h | ⏸️ Not Started |

**Created:** January 3, 2026  
**Status:** ⏸️ READY TO START

---

## 🎯 Executive Summary

### The Transformation

Convert the current manifest-driven GUIDED Debug Orchestrator into a pure autonomous Python implementation that performs root cause analysis, generates automated fixes, and injects error markers for comprehensive debugging workflows.

### Why AUTONOMOUS?

**Current Issues (GUIDED):**
- LLM-dependent error analysis (inconsistent results)
- Manual marker injection process
- No automated fix generation
- Limited state tracking for multi-step debugging
- No fix history or rollback capability

**AUTONOMOUS Benefits:**
- Deterministic AST-based error analysis
- Automated fix generation with validation
- Programmatic marker injection system
- Database state tracking for debugging sessions
- Fix history with rollback capability
- Master Orchestrator routing with pattern matching

### Success Criteria

- ✅ Pure Python implementation (zero natural language in manifest)
- ✅ Root cause analysis engine with AST parsing
- ✅ Automated fix generation system
- ✅ Error marker injection (# TODO, # FIXME, # BUG)
- ✅ Master Orchestrator routing operational
- ✅ 95%+ test coverage
- ✅ Fix history tracking with rollback
- ✅ Git checkpoint after each phase

---

## 🏗️ Phase 0: Context Discovery (4 hours)

**Goal:** Analyze current GUIDED implementation and plan AUTONOMOUS architecture

### Task 0.1: Analyze Current Debug Orchestrator
**Duration:** 2h

**Files to Review:**
- Current GUIDED manifest (if exists)
- Existing debugging utilities
- Error analysis patterns
- Test files for debugging workflows

**Deliverables:**
- `context/debug-v1-analysis.md` - Current implementation review
- `context/error-patterns.md` - Common error types and causes
- `context/brittleness-analysis.md` - Issues with GUIDED approach

### Task 0.2: Design AUTONOMOUS Architecture
**Duration:** 2h

**Architecture Design:**
```
DebugOrchestratorV2(BaseOrchestratorV4_1)
├── Phase 0: Error Collection - Gather error traces
├── Phase 1: Root Cause Analysis - AST parsing + pattern matching
├── Phase 2: Fix Generation - Automated solution generation
├── Phase 3: Validation - Test generated fixes
└── Phase 4: Marker Injection - Add TODO/FIXME/BUG markers

Components:
├── RootCauseAnalysisEngine
│   ├── AST parser
│   ├── Error pattern matcher
│   └── Stack trace analyzer
├── FixGenerationEngine
│   ├── Template-based fix generation
│   ├── AI-assisted fix suggestions
│   └── Fix validation
└── MarkerInjectionEngine
    ├── Marker type detection
    ├── Code injection
    └── Comment formatting
```

**Deliverables:**
- `context/autonomous-architecture.md` - Complete design
- `artifacts/class-diagram.md` - Class structure
- `artifacts/phase-flow-diagram.md` - Execution flow

### Completion Criteria
- ✅ Current implementation understood
- ✅ AUTONOMOUS design documented
- ✅ 5-phase pipeline specified
- ✅ Git checkpoint: `checkpoint-debug-v2-phase-0`

---

## 🔧 Phase 1: Core Orchestrator + Root Cause Engine (1 day)

**Goal:** Build DebugOrchestratorV2 with root cause analysis capabilities

### Task 1.1: Core Orchestrator Class
**Duration:** 3h

**Files to Create:**
- `src/orchestrators/debug/debug_orchestrator_v2.py`
- `src/orchestrators/debug/__init__.py`
- `src/orchestrators/debug/root_cause_engine.py`
- `cortex-brain/manifests/orchestrators/debug-v2-manifest.yaml`

**Core Class:**
```python
class DebugOrchestratorV2(BaseOrchestratorV4_1):
    """
    Debug Orchestrator v2 - Pure AUTONOMOUS implementation.
    
    5-Phase Pipeline:
        Phase 0: Error Collection - Gather traces and context
        Phase 1: Root Cause Analysis - Determine error source
        Phase 2: Fix Generation - Create automated solutions
        Phase 3: Validation - Test fixes
        Phase 4: Marker Injection - Add debugging markers
    """
    
    def collect_error_context(self, error: Exception, file_path: str) -> ErrorContext
    def analyze_root_cause(self, context: ErrorContext) -> RootCauseResult
    def generate_fix(self, root_cause: RootCauseResult) -> FixResult
    def validate_fix(self, fix: FixResult) -> ValidationResult
    def inject_markers(self, validation: ValidationResult) -> MarkerResult
```

### Task 1.2: Root Cause Analysis Engine
**Duration:** 5h

**Root Cause Engine:**
```python
class RootCauseAnalysisEngine:
    """
    AST-based error analysis with pattern matching.
    
    Features:
        - Stack trace parsing
        - AST node analysis for error location
        - Pattern matching for common errors
        - Variable state analysis
        - Dependency chain analysis
    """
    
    def parse_stack_trace(self, trace: str) -> List[StackFrame]
    def analyze_ast_node(self, node: ast.AST, error_line: int) -> ASTAnalysis
    def match_error_patterns(self, error: Exception) -> List[ErrorPattern]
    def analyze_variable_state(self, context: ErrorContext) -> StateAnalysis
```

**Common Error Patterns:**
```python
ERROR_PATTERNS = {
    'AttributeError': [
        {'pattern': r"'NoneType' object has no attribute", 'cause': 'null_pointer'},
        {'pattern': r"module '.*' has no attribute", 'cause': 'missing_import'},
    ],
    'TypeError': [
        {'pattern': r"unsupported operand type", 'cause': 'type_mismatch'},
        {'pattern': r"missing \d+ required positional argument", 'cause': 'missing_argument'},
    ],
    'ImportError': [
        {'pattern': r"No module named", 'cause': 'missing_dependency'},
        {'pattern': r"cannot import name", 'cause': 'circular_import'},
    ],
    # ... more patterns
}
```

### Completion Criteria
- ✅ DebugOrchestratorV2 core operational
- ✅ Root cause engine functional
- ✅ AST parsing working
- ✅ Error pattern matching implemented
- ✅ Config-only manifest created
- ✅ Git checkpoint: `checkpoint-debug-v2-phase-1`

---

## 🛠️ Phase 2: Fix Generation + Marker Injection (1 day)

**Goal:** Automated fix generation and error marker injection

### Task 2.1: Fix Generation Engine
**Duration:** 4h

**Files to Create:**
- `src/orchestrators/debug/fix_generation_engine.py`
- `src/orchestrators/debug/fix_templates.py`

**Fix Generation Engine:**
```python
class FixGenerationEngine:
    """
    Automated fix generation based on root cause analysis.
    
    Strategies:
        1. Template-based fixes (common patterns)
        2. AI-assisted suggestions (GPT-4 for complex cases)
        3. Fix validation with tests
    """
    
    def generate_template_fix(self, root_cause: RootCauseResult) -> Fix
    def generate_ai_fix(self, root_cause: RootCauseResult) -> Fix
    def validate_fix_syntax(self, fix: Fix) -> bool
    def test_fix(self, fix: Fix) -> TestResult
```

**Fix Templates:**
```python
FIX_TEMPLATES = {
    'null_pointer': """
# Add null check before attribute access
if {var} is not None:
    {original_code}
else:
    # Handle None case
    {default_action}
""",
    'missing_import': """
# Add missing import
from {module} import {name}
""",
    'type_mismatch': """
# Convert type
{var} = {target_type}({var})
""",
    # ... more templates
}
```

### Task 2.2: Marker Injection Engine
**Duration:** 4h

**Files to Create:**
- `src/orchestrators/debug/marker_injection_engine.py`

**Marker Injection Engine:**
```python
class MarkerInjectionEngine:
    """
    Inject debugging markers into code (TODO, FIXME, BUG).
    
    Marker Types:
        - # TODO: Feature to implement
        - # FIXME: Code that needs improvement
        - # BUG: Known issue with reproduction steps
        - # HACK: Temporary workaround
    """
    
    def inject_marker(
        self, 
        file_path: str, 
        line_number: int, 
        marker_type: MarkerType, 
        description: str
    ) -> InjectionResult
    
    def format_marker(self, marker_type: MarkerType, description: str) -> str
    def detect_existing_markers(self, file_path: str) -> List[Marker]
```

**Marker Format:**
```python
# TODO: [CORTEX-DEBUG-2026-01-03] Implement null check for user object
# FIXME: [CORTEX-DEBUG-2026-01-03] Type mismatch - convert string to int
# BUG: [CORTEX-DEBUG-2026-01-03] AttributeError when user is None - repro: call get_user(invalid_id)
```

### Completion Criteria
- ✅ Fix generation engine operational
- ✅ Template-based fixes working
- ✅ AI-assisted fixes functional (optional)
- ✅ Marker injection engine working
- ✅ All marker types supported
- ✅ Git checkpoint: `checkpoint-debug-v2-phase-2`

---

## 🔗 Phase 3: Master Orchestrator Wiring (4 hours)

**Goal:** Integrate Debug v2 with Master Orchestrator routing

### Task 3.1: Add Routing Patterns
**Duration:** 1h

**Update:** `cortex-brain/config/master-orchestrator.yaml`

```yaml
orchestrators:
  - id: "debug_orchestrator_v2"
    name: "Debug v2"
    version: "2.0.0"
    type: autonomous
    patterns:
      - pattern: "^(debug|fix bug|troubleshoot).*$"
        confidence: 1.0
        match_type: regex
        priority: 50
      - pattern: "^(analyze error|root cause).*$"
        confidence: 0.9
        match_type: regex
        priority: 49
    module: "src.orchestrators.debug.debug_orchestrator_v2"
    class: "DebugOrchestratorV2"
    enabled: true
    metadata:
      description: "Debug v2 - Root cause analysis + automated fix generation"
      autonomous: true
      state_tracking: true
      fix_history: true
```

### Task 3.2: Register in OrchestratorRegistry
**Duration:** 30min

```python
# In src/orchestrators/master/registry.py
from src.orchestrators.debug.debug_orchestrator_v2 import DebugOrchestratorV2

registry.register(
    orchestrator_id="debug_orchestrator_v2",
    orchestrator_class=DebugOrchestratorV2,
    metadata={
        "version": "2.0.0",
        "type": "autonomous",
        "requires_state": True,
        "fix_history_tracking": True,
        "marker_injection": True
    }
)
```

### Task 3.3: Update CORTEX.prompt.md
**Duration:** 30min

**Change Entry:**
```markdown
| `debug`, `fix bug`, `troubleshoot` | 🛡️ **Debug v2 (AUTONOMOUS)** | `debug-v2-manifest.yaml` | Root cause analysis + automated fixes + marker injection |
```

### Task 3.4: Test Routing
**Duration:** 2h

**Manual Tests:**
```bash
# Test error analysis
"debug src/module.py --error AttributeError"
→ Master Orch routes to Debug v2
→ Root cause analysis executes
→ Fix generated and validated

# Test marker injection
"debug src/buggy_code.py --inject-markers"
→ Debug v2 analyzes errors
→ Injects TODO/FIXME/BUG markers
→ Report generated

# Test fix history
"debug rollback fix-12345"
→ Debug v2 rolls back specific fix
→ State restored from history
```

### Task 3.5: Create Wiring Report
**Duration:** 30min

**Generate:** `cortex-brain/documents/reports/wiring-debug-v2.md`

**Content:**
- Wiring date: January 3, 2026
- Commit hash: [PENDING]
- Routing tests: All passed
- Master Orch coverage: ~46% (6/13 orchestrators)
- Fix generation: Tested and operational

### Completion Criteria
- ✅ Routing patterns added to master-orchestrator.yaml
- ✅ Registered in OrchestratorRegistry
- ✅ CORTEX.prompt.md updated (GUIDED → AUTONOMOUS)
- ✅ Manual routing tests passed
- ✅ Wiring report generated
- ✅ Git checkpoint: `checkpoint-debug-v2-phase-3`

---

## ✅ Phase 4: Testing & Validation (4 hours)

**Goal:** Comprehensive testing of all debugging scenarios

### Task 4.1: Unit Tests
**Duration:** 2h

**Test Files:**
- `tests/orchestrators/debug/test_debug_orchestrator_v2.py`
- `tests/orchestrators/debug/test_root_cause_engine.py`
- `tests/orchestrators/debug/test_fix_generation_engine.py`
- `tests/orchestrators/debug/test_marker_injection_engine.py`

**Test Coverage:**
- All 5 phases individually
- Stack trace parsing
- AST node analysis
- Error pattern matching
- Template-based fix generation
- AI-assisted fix generation (mocked)
- Marker injection for all types
- Fix validation and rollback

**Target:** 95%+ coverage

### Task 4.2: Integration Tests
**Duration:** 1h

**Scenarios:**
1. Full pipeline: Error Collection → Marker Injection
2. Root cause analysis for common error types
3. Master Orchestrator routing
4. Fix history tracking in PlanningStateDB
5. Cross-session resumability
6. Rollback scenarios

### Task 4.3: End-to-End Validation
**Duration:** 1h

**Real-World Tests:**
- Debug actual CORTEX errors
- Test on multiple error types (AttributeError, TypeError, ImportError)
- Verify fix generation quality
- Validate marker injection formatting
- Test fix history and rollback

### Completion Criteria
- ✅ 95%+ test coverage achieved
- ✅ All unit tests passing
- ✅ Integration tests passing
- ✅ End-to-end validation successful
- ✅ Git checkpoint: `checkpoint-debug-v2-phase-4`

---

## 📚 Phase 5: Documentation & REFACTOR (2 hours)

**Goal:** Comprehensive documentation and code cleanup

### Task 5.1: Documentation
**Duration:** 1h

**Files to Create/Update:**
- `cortex-brain/documents/orchestrators-quick-ref.md` - Add Debug v2
- `docs/orchestrators/debug-v2-guide.md` - User guide
- `docs/architecture/root-cause-analysis.md` - Technical architecture
- `docs/guides/marker-injection.md` - Marker usage guide
- README updates for new orchestrator

### Task 5.2: REFACTOR & Cleanup
**Duration:** 1h

**SKULL Rule Enforcement:**
- Remove orphaned code from GUIDED version
- Consolidate duplicate debugging utilities
- Ensure consistent naming conventions
- Remove debugging statements
- Optimize AST parsing

**Cleanup Tasks:**
- Remove old GUIDED manifest (if exists)
- Archive deprecated utilities
- Update import statements
- Verify no circular dependencies

### Completion Criteria
- ✅ All documentation complete
- ✅ REFACTOR cleanup done
- ✅ No orphaned code remains
- ✅ Git checkpoint: `checkpoint-debug-v2-complete`

---

## 🎉 Completion Summary

Upon completing all phases:

**Deliverables:**
- ✅ Pure AUTONOMOUS Debug Orchestrator v2
- ✅ Root cause analysis engine with AST parsing
- ✅ Automated fix generation system
- ✅ Error marker injection (TODO/FIXME/BUG)
- ✅ Master Orchestrator integration
- ✅ 95%+ test coverage
- ✅ Comprehensive documentation

**System Status:**
- ✅ 6/10 CORTEX v5 components production-ready (was 5/10)
- ✅ Master Orchestrator coverage: 46% (6/13 orchestrators)
- ✅ Debug v2 routed via pattern matching
- ✅ Fix history tracking operational

**Next Steps:**
→ Update CORTEX v5.0 plan progress (Phase 6.4 & 6.5 complete)
→ System integration testing
→ Final documentation update

---

**Plan Created:** January 3, 2026  
**Author:** CORTEX Planning System v5  
**Status:** ✅ READY TO EXECUTE
