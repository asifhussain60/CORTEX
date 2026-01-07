# 🎯 C50-04: AST Scanning Integration for Planning

**Sub-Plan ID:** C50-04  
**Order:** 04  
**Type:** Feature Enhancement  
**Priority:** HIGH  
**Duration:** 3-4 days (32 hours)  
**Status:** 🔄 IN PROGRESS  
**Parent Epic:** C50 (CORTEX v5 Gap Remediation)

---

## 📊 Progress Tracker

**Overall Progress:** `██░░░░░░░░` **10%** 🔄 IN PROGRESS

| Phase | Status | Duration | Progress |
|-------|--------|----------|----------|
| **Phase -2:** Setup Verification | ✅ Complete | 10min | `██████████` 100% |
| **Phase 0:** AST Scanner Implementation | ⏳ In Progress | 1d | `░░░░░░░░░░` 0% |
| **Phase 1:** Injection Point Detection | ⏳ Not Started | 1d | `░░░░░░░░░░` 0% |
| **Phase 2:** Security & Performance Analysis | ⏳ Not Started | 8h | `░░░░░░░░░░` 0% |
| **Phase 3:** Planning Orchestrator Integration | ⏳ Not Started | 8h | `░░░░░░░░░░` 0% |
| **Phase 4:** Testing & Validation | ⏳ Not Started | 4h | `░░░░░░░░░░` 0% |
| **Phase 999:** REFACTOR + Documentation + Commit | ⏳ Not Started | 30min | `░░░░░░░░░░` 0% |

---

## 🎯 Objectives

### Primary Objective
Extend Knowledge Library (C50-03) with intelligent AST scanning for:
- **Injection Point Detection** - Find optimal code insertion locations
- **Security Scanning** - Identify vulnerabilities and anti-patterns
- **Performance Analysis** - Detect bottlenecks and optimization opportunities

### Strategic Impact
Enable Planning Orchestrator v5 to make **intelligent code structure decisions** during Phase -1 by providing:
- Where to inject new code (class, module, function boundaries)
- Security risks to avoid
- Performance implications of planned changes

---

## 📋 Phase Details

### Phase -2: Setup Verification ✅ COMPLETE

**Duration:** 10 minutes  
**Status:** ✅ Complete

**Verified:**
- ✅ C50-03 Knowledge Library operational (608 LOC, 20 tests)
- ✅ Planning v5 tests passing (GATE-2 achieved)
- ✅ Dependencies met: Test coverage at 89% (target: 80%)

---

### Phase 0: AST Scanner Implementation

**Duration:** 1 day  
**Purpose:** Extend Knowledge Library with deep AST analysis

**Tasks:**
1. **Extend `KnowledgeLibrary` class**
   ```python
   # File: src/cortex_agents/knowledge_library.py
   
   class ASTScanner:
       """Enhanced AST scanning with injection point detection"""
       
       def analyze_code_structure(self, file_path: str) -> Dict
       def find_injection_points(self, file_path: str, code_type: str) -> List[InjectionPoint]
       def detect_security_vulnerabilities(self, ast_tree) -> List[SecurityIssue]
       def analyze_performance_patterns(self, ast_tree) -> List[PerformanceIssue]
   ```

2. **Injection Point Data Structure**
   ```python
   @dataclass
   class InjectionPoint:
       file_path: str
       line_number: int
       injection_type: str  # 'class', 'function', 'module_level'
       context: str  # Surrounding code context
       score: float  # Suitability score (0.0-1.0)
       reasoning: str  # Why this is a good injection point
   ```

3. **AST Analysis Features**
   - Detect class boundaries and methods
   - Identify module-level injection points
   - Analyze function complexity (cyclomatic complexity)
   - Track import statements and dependencies
   - Detect duplicate code patterns

**Exit Criteria:**
- `ASTScanner` class implemented (300+ LOC)
- Can parse Python files and extract structure
- Returns structured `InjectionPoint` objects
- Unit tests: 10+ tests, 100% pass rate

---

### Phase 1: Injection Point Detection

**Duration:** 1 day  
**Purpose:** Intelligent code insertion location discovery

**Algorithm:**
1. **Scan File AST** - Parse target file
2. **Score Locations** - Rate each potential injection point
3. **Context Analysis** - Consider surrounding code
4. **Rank Results** - Sort by suitability

**Scoring Criteria:**
- **+0.3** - Module-level (clean imports section)
- **+0.2** - End of class (follows existing pattern)
- **+0.2** - Between related methods (logical grouping)
- **+0.1** - Follows docstring convention
- **+0.1** - Consistent with file style (spacing, comments)
- **-0.3** - Middle of complex logic
- **-0.2** - Breaking method cohesion
- **-0.4** - Inside try/except/finally blocks

**Example Output:**
```python
injection_points = scanner.find_injection_points(
    file_path="src/orchestrators/planning_orchestrator_v5.py",
    code_type="method"  # or 'class', 'function', 'import'
)

# Returns:
# [
#   InjectionPoint(
#     file_path="...",
#     line_number=245,
#     injection_type="method",
#     score=0.85,
#     reasoning="End of PlanningOrchestrator class, follows method pattern"
#   ),
#   ...
# ]
```

**Exit Criteria:**
- Injection point detection operational
- Scoring algorithm validated on 5+ files
- Returns top 3 ranked injection points
- Unit tests: 8+ tests, 100% pass rate

---

### Phase 2: Security & Performance Analysis

**Duration:** 8 hours  
**Purpose:** Proactive issue detection during AST scanning

**2.1 Security Scanning**

**Detect:**
- Hardcoded credentials/secrets
- SQL injection vulnerabilities (string concatenation in queries)
- Command injection (shell=True in subprocess)
- Unsafe deserialization (pickle.loads)
- Path traversal (user input in file paths)
- Eval/exec usage

**Example:**
```python
security_issues = scanner.detect_security_vulnerabilities(ast_tree)

# Returns:
# [
#   SecurityIssue(
#     severity="HIGH",
#     issue_type="hardcoded_secret",
#     line_number=42,
#     description="Potential API key hardcoded",
#     recommendation="Use environment variables or secrets manager"
#   )
# ]
```

**2.2 Performance Analysis**

**Detect:**
- Cyclomatic complexity > 10 (refactoring candidate)
- Nested loops (O(n²) or worse)
- Inefficient list operations (repeated appends in loop)
- Missing caching opportunities
- Redundant database queries

**Exit Criteria:**
- Security scanner detects 6+ vulnerability types
- Performance analyzer identifies 4+ anti-patterns
- Unit tests: 10+ tests, 100% pass rate
- False positive rate < 10%

---

### Phase 3: Planning Orchestrator Integration

**Duration:** 8 hours  
**Purpose:** Integrate AST scanning into Phase -1 of planning

**Tasks:**
1. **Extend Phase -1 Knowledge Discovery**
   ```python
   # File: src/orchestrators/planning/planning_orchestrator_v5.py
   
   def execute_phase_minus_one(self):
       """Phase -1: Knowledge Discovery (enhanced with AST scanning)"""
       
       # Existing: Knowledge Library scan
       knowledge = self.knowledge_library.scan_workspace(self.target_feature)
       
       # NEW: AST-based injection point discovery
       injection_points = self.knowledge_library.find_injection_points(
           target_files=knowledge["relevant_files"],
           code_type="auto"  # Auto-detect from context
       )
       
       # NEW: Security pre-flight check
       security_issues = self.knowledge_library.scan_security_risks(
           target_files=knowledge["relevant_files"]
       )
       
       # Store in context
       self.context["injection_points"] = injection_points
       self.context["security_pre_flight"] = security_issues
   ```

2. **Update Planning Manifest Schema**
   ```yaml
   # File: cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml
   
   phase_minus_one:
     enabled: true
     knowledge_library:
       ast_scanning: true        # NEW
       injection_detection: true # NEW
       security_scanning: true   # NEW
   ```

3. **Add to Plan Context**
   - Injection points included in plan generation
   - Security issues flagged in Phase 0 (Analysis)
   - Performance implications documented

**Exit Criteria:**
- Phase -1 calls AST scanning automatically
- Injection points stored in plan context
- Security issues surfaced in planning output
- Integration test passes

---

### Phase 4: Testing & Validation

**Duration:** 4 hours  
**Purpose:** Comprehensive test coverage

**Test Categories:**

1. **Unit Tests** (20+ tests)
   - AST parsing (5 tests)
   - Injection point detection (8 tests)
   - Security scanning (6 tests)
   - Performance analysis (4 tests)

2. **Integration Tests** (5+ tests)
   - Planning orchestrator Phase -1 integration
   - Real file AST scanning
   - Multi-file project analysis

3. **Validation Tests**
   - Test on CORTEX codebase (100+ files)
   - Verify injection point accuracy
   - Validate security detection (known test cases)

**Exit Criteria:**
- 25+ tests total
- 100% pass rate
- Code coverage ≥90% for new code
- No regressions in existing Knowledge Library tests

---

### Phase 999: REFACTOR + Documentation + Commit

**Duration:** 30 minutes  
**Purpose:** SKULL rule enforcement (whole-file cleanup)

**Tasks:**
1. **Code Cleanup**
   - Remove debug statements
   - Optimize imports
   - Format with Black
   - Add type hints
   - Update docstrings

2. **Documentation**
   - Update Knowledge Library README
   - Add AST scanning examples
   - Document injection point scoring
   - Create usage guide

3. **Integration Verification**
   - Run full test suite (all CORTEX tests)
   - Verify no regressions
   - Check planning_orchestrator_v5.py integration

4. **Git Checkpoint**
   ```bash
   git add src/cortex_agents/knowledge_library.py
   git add src/orchestrators/planning/planning_orchestrator_v5.py
   git add tests/cortex_agents/test_ast_scanning.py
   git commit -m "feat(C50-04): AST scanning integration for planning - injection point detection, security scanning, performance analysis"
   ```

**Exit Criteria:**
- All files cleaned up (SKULL rules enforced)
- Documentation complete
- Test suite passes (100%)
- Git checkpoint created

---

## 📈 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **LOC Added** | 400+ | AST scanner implementation |
| **Test Coverage** | ≥90% | New code coverage |
| **Tests Created** | 25+ | Unit + integration tests |
| **Test Pass Rate** | 100% | All tests passing |
| **Injection Accuracy** | ≥85% | Top-3 injection points relevant |
| **Security Detection** | 6+ types | Vulnerability patterns |
| **False Positives** | <10% | Security scanner accuracy |
| **Performance** | <2s | AST scan of 1000-line file |

---

## 🔗 Dependencies

### Input Dependencies (Must Complete First)
- ✅ **C50-03** Knowledge Library implemented (608 LOC)
- ✅ **C50-00C** Test coverage ≥80% (GATE-2)

### Output Dependencies (Unblocks)
- **C50-11** CORTEX-LENS Admin Dashboard (displays AST analysis)
- **C50-06** Visual Progress Generation (uses injection point visualization)

---

## 🚨 Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| AST parsing failures | High | Graceful error handling, fallback to basic scanning |
| False positive security alerts | Medium | Tunable severity thresholds, whitelisting |
| Injection point inaccuracy | Medium | Scoring algorithm refinement, user override |
| Performance (large files) | Low | Async scanning, file size limits, caching |

---

## 📚 References

**Knowledge Library Foundation:**
- `src/cortex_agents/knowledge_library.py` (C50-03)
- `tests/cortex_agents/test_knowledge_library.py`

**Planning Integration:**
- `src/orchestrators/planning/planning_orchestrator_v5.py`
- `cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml`

**AST Resources:**
- Python `ast` module documentation
- AST NodeVisitor patterns
- Security scanning patterns (Bandit library)

---

**Created:** 2026-01-04  
**Author:** CORTEX Autonomous Execution Engine  
**Epic:** C50 (CORTEX v5 Gap Remediation)  
**Estimated Completion:** 2026-01-07

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
