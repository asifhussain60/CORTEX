# 🛡️ Sanitization Orchestrator v2 Migration

**Plan ID:** sanitization-v2-migration  
**Feature:** Convert GUIDED Sanitization Orchestrator to AUTONOMOUS Architecture  
**Created:** January 3, 2026  
**Complexity:** TIER 4 (ORCHESTRATOR MIGRATION)  
**Strategy:** Pure autonomous 5-phase pipeline with holistic review integration  
**Estimated Duration:** 3.25 days (2d implementation + 1.25d review system)

---

## 📊 Visual Progress Tracker

**Overall Progress:** `░░░░░░░░░░` **0%** ⏸️ NOT STARTED

| Phase | Name | Progress | Duration | Status |
|-------|------|----------|----------|--------|
| 0 | Context Discovery | `░░░░░░░░░░` | 4h | ⏸️ Not Started |
| 1 | Core Orchestrator Implementation | `░░░░░░░░░░` | 1d | ⏸️ Not Started |
| 2 | Holistic Review Integration | `░░░░░░░░░░` | 1d | ⏸️ Not Started |
| 3 | Master Orchestrator Wiring | `░░░░░░░░░░` | 4h | ⏸️ Not Started |
| 4 | Testing & Validation | `░░░░░░░░░░` | 4h | ⏸️ Not Started |
| 5 | Documentation & REFACTOR | `░░░░░░░░░░` | 2h | ⏸️ Not Started |

**Created:** January 3, 2026  
**Status:** ⏸️ READY TO START

---

## 🎯 Executive Summary

### The Transformation

Convert the current manifest-driven GUIDED Sanitization Orchestrator into a pure autonomous Python implementation that eliminates personal information, credentials, and sensitive data through a deterministic 5-phase pipeline with optional AI-assisted holistic review.

### Why AUTONOMOUS?

**Current Issues (GUIDED):**
- LLM interpretation variability in sanitization rules
- No transactional rollback for failed sanitizations
- Limited state tracking across 5 phases
- Manual holistic review process
- No cross-session resumability

**AUTONOMOUS Benefits:**
- Deterministic regex-based sanitization (consistent results)
- Transaction boundaries with rollback capability
- Database state tracking for each phase
- AI-assisted holistic review (GPT-4 integration)
- Master Orchestrator routing with pattern matching
- Cross-session resumability via PlanningStateDB

### Success Criteria

- ✅ Pure Python implementation (zero natural language in manifest)
- ✅ 5-phase pipeline: Discovery → Analysis → Transformation → Validation → Finalization
- ✅ Config-only manifest (YAML data structures)
- ✅ Holistic review integration (AI-assisted quality check)
- ✅ Master Orchestrator routing operational
- ✅ 95%+ test coverage
- ✅ Database state tracking with rollback
- ✅ Git checkpoint after each phase

---

## 🏗️ Phase 0: Context Discovery (4 hours)

**Goal:** Analyze current GUIDED implementation and plan AUTONOMOUS architecture

### Task 0.1: Analyze Current Sanitization Orchestrator
**Duration:** 2h

**Files to Review:**
- Current GUIDED manifest (if exists)
- Existing sanitization utilities
- Test files for sanitization patterns
- User workflows and examples

**Deliverables:**
- `context/sanitization-v1-analysis.md` - Current implementation review
- `context/sanitization-patterns.md` - Common patterns (PII, credentials, paths)
- `context/brittleness-analysis.md` - Issues with GUIDED approach

### Task 0.2: Design AUTONOMOUS Architecture
**Duration:** 2h

**Architecture Design:**
```
SanitizationOrchestratorV2(BaseOrchestratorV4_1)
├── Phase 0: Discovery - Scan files for sensitive patterns
├── Phase 1: Analysis - Classify sensitivity levels
├── Phase 2: Transformation - Apply sanitization rules
├── Phase 3: Validation - Verify no sensitive data remains
└── Phase 4: Finalization - Generate report + checkpoint

Optional: HolisticReviewEngine (AI-assisted)
├── GPT-4 analysis of sanitized content
├── Semantic similarity checks
└── Quality recommendations
```

**Deliverables:**
- `context/autonomous-architecture.md` - Complete design
- `artifacts/class-diagram.md` - Class structure
- `artifacts/phase-flow-diagram.md` - Execution flow

### Completion Criteria
- ✅ Current implementation understood
- ✅ AUTONOMOUS design documented
- ✅ 5-phase pipeline specified
- ✅ Git checkpoint: `checkpoint-sanitization-v2-phase-0`

---

## 🔧 Phase 1: Core Orchestrator Implementation (1 day)

**Goal:** Build SanitizationOrchestratorV2 with 5-phase pipeline

### Task 1.1: Core Orchestrator Class
**Duration:** 4h

**Files to Create:**
- `src/orchestrators/sanitization/sanitization_orchestrator_v2.py`
- `src/orchestrators/sanitization/__init__.py`
- `src/orchestrators/sanitization/sanitization_engine.py`
- `cortex-brain/manifests/orchestrators/sanitization-v2-manifest.yaml`

**Core Class:**
```python
class SanitizationOrchestratorV2(BaseOrchestratorV4_1):
    """
    Sanitization Orchestrator v2 - Pure AUTONOMOUS implementation.
    
    5-Phase Pipeline:
        Phase 0: Discovery - Scan files for sensitive patterns
        Phase 1: Analysis - Classify sensitivity levels
        Phase 2: Transformation - Apply sanitization rules
        Phase 3: Validation - Verify completeness
        Phase 4: Finalization - Generate reports
    """
    
    def discover_sensitive_content(self, target_path: str) -> DiscoveryResult
    def analyze_sensitivity_levels(self, discovery: DiscoveryResult) -> AnalysisResult
    def apply_sanitization_rules(self, analysis: AnalysisResult) -> TransformResult
    def validate_sanitization(self, transform: TransformResult) -> ValidationResult
    def finalize_sanitization(self, validation: ValidationResult) -> FinalResult
```

### Task 1.2: Sanitization Engine Implementation
**Duration:** 4h

**Sanitization Patterns:**
1. **PII Detection:**
   - Email addresses: `[\w\.-]+@[\w\.-]+\.\w+`
   - Phone numbers: `\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}`
   - SSN: `\d{3}-\d{2}-\d{4}`
   - Names: NLP-based entity recognition

2. **Credentials Detection:**
   - API keys: `[A-Za-z0-9_-]{32,}`
   - Passwords: `password\s*=\s*["\']?[\w!@#$%^&*()]+["\']?`
   - Tokens: `token\s*=\s*["\']?[\w\.-]+["\']?`

3. **Path Sanitization:**
   - Absolute paths: `/Users/[^/]+/` → `/Users/USER/`
   - Windows paths: `C:\\Users\\[^\\]+\\` → `C:\\Users\\USER\\`

**Implementation:**
```python
class SanitizationEngine:
    """Core sanitization logic with regex patterns."""
    
    def detect_pii(self, content: str) -> List[Match]
    def detect_credentials(self, content: str) -> List[Match]
    def sanitize_paths(self, content: str) -> str
    def apply_custom_rules(self, content: str, rules: List[Rule]) -> str
```

### Completion Criteria
- ✅ SanitizationOrchestratorV2 fully functional
- ✅ All 5 phases implemented
- ✅ Regex patterns tested
- ✅ Config-only manifest created
- ✅ Git checkpoint: `checkpoint-sanitization-v2-phase-1`

---

## 🤖 Phase 2: Holistic Review Integration (1 day)

**Goal:** Add AI-assisted quality review using GPT-4

### Task 2.1: Holistic Review Engine
**Duration:** 4h

**Files to Create:**
- `src/orchestrators/sanitization/holistic_review_engine.py`
- `src/orchestrators/sanitization/semantic_analyzer.py`

**Holistic Review Engine:**
```python
class HolisticReviewEngine:
    """
    AI-assisted sanitization quality review.
    
    Features:
        - GPT-4 content analysis for remaining sensitive data
        - Semantic similarity checks (original vs sanitized)
        - Quality recommendations
        - Confidence scoring
    """
    
    def analyze_sanitized_content(self, original: str, sanitized: str) -> ReviewResult
    def check_semantic_similarity(self, original: str, sanitized: str) -> float
    def generate_recommendations(self, analysis: ReviewResult) -> List[str]
```

**GPT-4 Integration:**
```python
def analyze_with_gpt4(self, content: str) -> dict:
    """
    Use GPT-4 to identify missed sensitive data.
    
    Prompt:
        "Analyze the following sanitized content for any remaining:
         - Personal information (names, emails, phones)
         - Credentials (API keys, passwords, tokens)
         - Organization-specific identifiers
         
         Respond with JSON: {found: [...], confidence: 0.0-1.0}"
    """
    # Implementation uses OpenAI API
```

### Task 2.2: Integration with Core Orchestrator
**Duration:** 2h

**Enhancement:**
```python
class SanitizationOrchestratorV2(BaseOrchestratorV4_1):
    def __init__(self, ..., enable_holistic_review: bool = False):
        self.holistic_review = HolisticReviewEngine() if enable_holistic_review else None
    
    def validate_sanitization(self, transform: TransformResult) -> ValidationResult:
        # Standard validation
        result = self._validate_patterns(transform)
        
        # Optional holistic review
        if self.holistic_review:
            review = self.holistic_review.analyze_sanitized_content(
                original=transform.original_content,
                sanitized=transform.sanitized_content
            )
            result.holistic_review = review
        
        return result
```

### Task 2.3: Testing & Validation
**Duration:** 2h

**Test Scenarios:**
- Test GPT-4 detection of missed patterns
- Test semantic similarity scoring
- Test recommendation generation
- Test false positive handling

**Deliverables:**
- `tests/orchestrators/sanitization/test_holistic_review.py`
- `tests/orchestrators/sanitization/test_semantic_analyzer.py`

### Completion Criteria
- ✅ Holistic review engine operational
- ✅ GPT-4 integration functional
- ✅ Semantic analyzer tested
- ✅ Optional enable/disable flag works
- ✅ Git checkpoint: `checkpoint-sanitization-v2-phase-2`

---

## 🔗 Phase 3: Master Orchestrator Wiring (4 hours)

**Goal:** Integrate Sanitization v2 with Master Orchestrator routing

### Task 3.1: Add Routing Patterns
**Duration:** 1h

**Update:** `cortex-brain/config/master-orchestrator.yaml`

```yaml
orchestrators:
  - id: "sanitization_orchestrator_v2"
    name: "Sanitization v2"
    version: "2.0.0"
    type: autonomous
    patterns:
      - pattern: "^(sanitize|make generic|anonymize).*$"
        confidence: 1.0
        match_type: regex
        priority: 40
      - pattern: "^(remove sensitive|clean data).*$"
        confidence: 0.9
        match_type: regex
        priority: 39
    module: "src.orchestrators.sanitization.sanitization_orchestrator_v2"
    class: "SanitizationOrchestratorV2"
    enabled: true
    metadata:
      description: "Sanitization v2 - 5-phase data cleaning with holistic review"
      autonomous: true
      state_tracking: true
      rollback_capable: true
```

### Task 3.2: Register in OrchestratorRegistry
**Duration:** 30min

```python
# In src/orchestrators/master/registry.py
from src.orchestrators.sanitization.sanitization_orchestrator_v2 import SanitizationOrchestratorV2

registry.register(
    orchestrator_id="sanitization_orchestrator_v2",
    orchestrator_class=SanitizationOrchestratorV2,
    metadata={
        "version": "2.0.0",
        "type": "autonomous",
        "requires_state": True,
        "holistic_review_capable": True,
        "rollback_capable": True
    }
)
```

### Task 3.3: Update CORTEX.prompt.md
**Duration:** 30min

**Change Entry:**
```markdown
| `sanitize`, `make generic`, `anonymize` | 🛡️ **Sanitization v2 (AUTONOMOUS)** | `sanitization-v2-manifest.yaml` | 5-phase data cleaning with optional AI review |
```

### Task 3.4: Test Routing
**Duration:** 2h

**Manual Tests:**
```bash
# Test pattern matching
"sanitize tests/sample_sensitive.py"
→ Master Orch routes to Sanitization v2
→ 5-phase pipeline executes
→ Sanitized file generated

# Test holistic review mode
"sanitize docs/private_notes.md --with-review"
→ Sanitization v2 runs with GPT-4 review
→ Quality report generated

# Test rollback
"sanitize critical_data.json" (with error)
→ Transformation fails
→ Rollback to original state
```

### Task 3.5: Create Wiring Report
**Duration:** 30min

**Generate:** `cortex-brain/documents/reports/wiring-sanitization-v2.md`

**Content:**
- Wiring date: January 3, 2026
- Commit hash: [PENDING]
- Routing tests: All passed
- Master Orch coverage: ~38% (5/13 orchestrators)
- Holistic review: Tested and operational

### Completion Criteria
- ✅ Routing patterns added to master-orchestrator.yaml
- ✅ Registered in OrchestratorRegistry
- ✅ CORTEX.prompt.md updated (GUIDED → AUTONOMOUS)
- ✅ Manual routing tests passed
- ✅ Wiring report generated
- ✅ Git checkpoint: `checkpoint-sanitization-v2-phase-3`

---

## ✅ Phase 4: Testing & Validation (4 hours)

**Goal:** Comprehensive testing of all sanitization scenarios

### Task 4.1: Unit Tests
**Duration:** 2h

**Test Files:**
- `tests/orchestrators/sanitization/test_sanitization_orchestrator_v2.py`
- `tests/orchestrators/sanitization/test_sanitization_engine.py`
- `tests/orchestrators/sanitization/test_holistic_review_engine.py`

**Test Coverage:**
- All 5 phases individually
- Regex pattern detection (PII, credentials, paths)
- Sanitization rule application
- Validation logic
- Holistic review with mocked GPT-4
- Rollback scenarios

**Target:** 95%+ coverage

### Task 4.2: Integration Tests
**Duration:** 1h

**Scenarios:**
1. Full pipeline: Discovery → Finalization
2. Holistic review enabled/disabled modes
3. Master Orchestrator routing
4. State tracking in PlanningStateDB
5. Cross-session resumability
6. Error handling and rollback

### Task 4.3: End-to-End Validation
**Duration:** 1h

**Real-World Tests:**
- Sanitize actual CORTEX files with sensitive data
- Test on multiple file types (Python, Markdown, JSON, YAML)
- Verify semantic similarity preservation
- Validate holistic review recommendations
- Test rollback on intentional failure

### Completion Criteria
- ✅ 95%+ test coverage achieved
- ✅ All unit tests passing
- ✅ Integration tests passing
- ✅ End-to-end validation successful
- ✅ Git checkpoint: `checkpoint-sanitization-v2-phase-4`

---

## 📚 Phase 5: Documentation & REFACTOR (2 hours)

**Goal:** Comprehensive documentation and code cleanup

### Task 5.1: Documentation
**Duration:** 1h

**Files to Create/Update:**
- `cortex-brain/documents/orchestrators-quick-ref.md` - Add Sanitization v2
- `docs/orchestrators/sanitization-v2-guide.md` - User guide
- `docs/architecture/sanitization-pipeline.md` - Technical architecture
- README updates for new orchestrator

### Task 5.2: REFACTOR & Cleanup
**Duration:** 1h

**SKULL Rule Enforcement:**
- Remove orphaned code from GUIDED version
- Consolidate duplicate sanitization utilities
- Ensure consistent naming conventions
- Remove debugging statements
- Optimize regex patterns

**Cleanup Tasks:**
- Remove old GUIDED manifest (if exists)
- Archive deprecated utilities
- Update import statements
- Verify no circular dependencies

### Completion Criteria
- ✅ All documentation complete
- ✅ REFACTOR cleanup done
- ✅ No orphaned code remains
- ✅ Git checkpoint: `checkpoint-sanitization-v2-complete`

---

## 🎉 Completion Summary

Upon completing all phases:

**Deliverables:**
- ✅ Pure AUTONOMOUS Sanitization Orchestrator v2
- ✅ 5-phase deterministic pipeline
- ✅ AI-assisted holistic review (optional)
- ✅ Master Orchestrator integration
- ✅ 95%+ test coverage
- ✅ Comprehensive documentation

**System Status:**
- ✅ 5/10 CORTEX v5 components production-ready (was 4/10)
- ✅ Master Orchestrator coverage: 38% (5/13 orchestrators)
- ✅ Sanitization v2 routed via pattern matching
- ✅ Cross-session resumability operational

**Next Steps:**
→ Proceed to Debug Orchestrator v2 Migration (Phase 6.5)

---

**Plan Created:** January 3, 2026  
**Author:** CORTEX Planning System v5  
**Status:** ✅ READY TO EXECUTE
