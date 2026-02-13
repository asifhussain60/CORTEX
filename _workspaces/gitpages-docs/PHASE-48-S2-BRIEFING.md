# 🧠 Phase 48-S2 Briefing: LENS Integration + Security Review
**Date:** February 9, 2026 | **Status:** Ready for Implementation  
**Previous Phase:** S1 Complete ✅ (15/15 tests passing)  
**Next Phase:** S2 - LENS Integration & Security  

---

## Executive Summary

**Phase 48-S2** adds deep code intelligence to the review engine via CORTEX LENS integration. This stage implements security vulnerability detection, AST analysis, and git history validation.

### Key Metrics

| Metric | Value |
|--------|-------|
| **Duration** | 1.5 days |
| **Test Target** | 25 tests |
| **LOC Target** | 600 |
| **Dependency** | S1 (Complete ✅) |
| **Priority** | P1 (blocks S3+) |

---

## S1 Foundation (Complete ✅)

### What's Already Implemented
```python
# Diff Parsing Foundation
parser = GitDiffParser()
changes = parser.parse(diff_text)  # List[FileChange]

# Review Orchestration Foundation  
orchestrator = CodeReviewOrchestrator()
report = orchestrator.review(context, diff_text)  # ReviewReport

# Data Models (Ready for S2)
- ReviewSeverity (enum: P0_CRITICAL, P1_HIGH, P2_MEDIUM)
- FileChange (file tracking with line diffs)
- ReviewContext (PR metadata)
- ReviewFinding (single issue)
- ReviewReport (aggregated findings)
```

### Test Status
- ✅ GitDiffParser (6/6 tests passing)
- ✅ ReviewContext (2/2 tests passing)
- ✅ ReviewReport (3/3 tests passing)
- ✅ CodeReviewOrchestrator (3/3 tests passing)
- ✅ Integration tests (1/1 passing)

---

## S2 Scope: LENS Integration

### Overview
Integrate CORTEX LENS for holistic code analysis:
- 🔍 **Security threats** (7 CWE patterns with 95%+ accuracy)
- 🔗 **AST analysis** (function signatures, complexity)
- 📜 **Git history** (commit quality validation)
- 💬 **Comments** (TODO/FIXME extraction)

### Deliverables

#### 1. SecurityReviewEngine (CWE Detection)
**Purpose:** Detect common security vulnerabilities via pattern matching

**CWE Coverage:**
- CWE-89: SQL Injection
- CWE-94: Code Injection  
- CWE-78: Command Injection
- CWE-327: Weak Cryptography (MD5, SHA1)
- CWE-22: Path Traversal
- CWE-79: XSS
- CWE-502: Unsafe Deserialization

**Example Usage:**
```python
security_engine = SecurityReviewEngine()
threats = security_engine.analyze_diff(changes, code_content)
# Returns: List[ReviewFinding] with severity P0/P1
```

**Tests to Write (7 tests):**
1. Detect SQL injection: `query = f"SELECT * FROM users WHERE id = {user_id}"`
2. Detect command injection: `os.system(f"ping {hostname}")`
3. Detect weak crypto: `hashlib.md5(password).hexdigest()`
4. Detect XSS in JS: `innerHTML = userInput`
5. Detect path traversal: `open(os.path.join(base_dir, user_path))`
6. Detect unsafe pickle: `pickle.loads(user_data)`
7. Handle benign code: No false positives

**Implementation Pattern:**
```python
class SecurityReviewEngine:
    """Detects CWE security patterns in code changes"""
    
    def analyze_diff(self, changes: List[FileChange], code_content: Dict[str, str]) -> List[ReviewFinding]:
        """Analyze changed code for security vulnerabilities"""
        findings = []
        
        for change in changes:
            content = code_content.get(change.filepath, "")
            findings.extend(self._check_sql_injection(change, content))
            findings.extend(self._check_command_injection(change, content))
            findings.extend(self._check_weak_crypto(change, content))
            # ... other CWE checks
        
        return findings
    
    def _check_sql_injection(self, change: FileChange, content: str) -> List[ReviewFinding]:
        """Detect SQL injection patterns"""
        findings = []
        # Regex: f"...{...}" or "..." % or .format(...)
        # Skip: parameterized queries, prepared statements
        return findings
```

#### 2. ASTReviewEngine (Code Structure)
**Purpose:** Validate Python code structure via AST analysis

**Analysis Points:**
- Function/method signatures
- Complexity metrics (cyclomatic)
- Type hint coverage
- Docstring presence
- Return type consistency

**Tests to Write (6 tests):**
1. Extract function signatures from modified functions
2. Calculate cyclomatic complexity
3. Detect missing type hints
4. Detect missing docstrings
5. Validate return types
6. Identify overly complex functions (>10 branches)

#### 3. GitHistoryReviewEngine (Commit Quality)
**Purpose:** Validate code history and commit quality

**Checks:**
- Commit message format (conventional commits)
- Author/committer consistency
- File count per commit (avoid mega-commits)
- Line count history (detect reverting commits)

**Tests to Write (4 tests):**
1. Validate commit message format
2. Detect author with many reverts
3. Flag commits with >500 line changes
4. Identify cherry-pick conflicts

#### 4. CommentExtractionEngine (TODO Analysis)
**Purpose:** Extract and prioritize TODO/FIXME comments

**Analysis:**
- TODO vs FIXME distinction
- Priority tagging (@High, @Low)
- Stale comment detection (>30 days)
- Assignment tracking (@assignee)

**Tests to Write (4 tests):**
1. Extract TODO from Python code
2. Extract FIXME with priority tags
3. Detect stale comments
4. Identify unassigned TODOs

#### 5. LENS Orchestration Integration
**Purpose:** Coordinate all engines via CORTEX LENS

**Integration Points:**
- `cortex_lens_analyze` MCP tool (AST + security)
- `cortex_git_history` MCP tool (commit analysis)
- `cortex_detect_duplicates` MCP tool (CORE-035)

**Tests to Write (4 tests):**
1. Call cortex_lens_analyze for security
2. Call cortex_git_history for history
3. Aggregate findings from all engines
4. Deduplicate findings across engines

---

## Implementation Plan

### Phase 1: SecurityReviewEngine Setup (4 hours)
1. Create test file with 7 security test cases
2. Implement CWE detection patterns
3. Verify 7/7 tests passing

### Phase 2: ASTReviewEngine (5 hours)
1. Create 6 AST test cases
2. Implement AST analysis via `ast` module
3. Verify 6/6 tests passing

### Phase 3: GitHistoryReviewEngine (3 hours)
1. Create 4 git history test cases
2. Implement commit analysis
3. Verify 4/4 tests passing

### Phase 4: CommentExtraction (3 hours)
1. Create 4 comment extraction tests
2. Implement TODO/FIXME regex parsing
3. Verify 4/4 tests passing

### Phase 5: LENS Integration (4 hours)
1. Create 4 MCP integration tests
2. Wire engines via CodeReviewOrchestrator
3. Verify 4/4 tests passing

**Total:** 19 hours ≈ 1.5 days ✅

---

## File Structure (S2)

```
cortex/orchestrators/code_review/
├── core_review_engine.py         (S1 - existing)
├── security_review_engine.py     (S2 - NEW)
├── ast_review_engine.py          (S2 - NEW)
├── git_history_review_engine.py  (S2 - NEW)
├── comment_extraction_engine.py  (S2 - NEW)
└── __init__.py

tests/unit/orchestrators/code_review/
├── test_phase48_s1_core_review_engine.py      (S1 - existing)
├── test_phase48_s2_security_review_engine.py  (S2 - NEW)
├── test_phase48_s2_ast_review_engine.py       (S2 - NEW)
├── test_phase48_s2_git_history_review_engine.py (S2 - NEW)
├── test_phase48_s2_comment_extraction_engine.py (S2 - NEW)
└── test_phase48_s2_lens_integration.py        (S2 - NEW)
```

---

## Acceptance Criteria (S2)

✅ **All Must Pass:**
- [ ] SecurityReviewEngine detects 7 CWE patterns with 95%+ accuracy
- [ ] ASTReviewEngine extracts function signatures and complexity
- [ ] GitHistoryReviewEngine validates commit message quality
- [ ] CommentExtractionEngine identifies TODO/FIXME with priority
- [ ] LENS analyzers integrate via MCP tools
- [ ] All 25 tests passing (25/25)
- [ ] No lint errors (black, flake8)
- [ ] Type hints on all public methods
- [ ] Google-style docstrings on all classes
- [ ] Code coverage >90%

---

## Decision Required

**Ready to proceed with Phase 48-S2 implementation?**

Options:
1. `proceed` - Start S2 immediately (estimated 1.5 days)
2. `plan` - Create detailed phase plan first
3. `questions` - Ask clarification questions
4. `skip-s2` - Move to different phase

**Recommendation:** `proceed` - S1 complete, dependencies satisfied, clear scope ✅

---

## Continuation Context

**Previous Commits:**
```
c2b188407 (HEAD) AC-PHASE48-S1-001: Implement GitDiffParser ✅
52c6ad85b Add test suite expansions
71cefa787 AC-AUDIT-2026-02-09-001: Final completion report
```

**Active Branch:** CORTEX (on local, pushed to origin)

**Next Steps After Approval:**
1. Create S2 test file: `test_phase48_s2_security_review_engine.py`
2. Create S2 implementation: `security_review_engine.py`
3. Follow TDD: write tests first, implement after
4. Run tests: `pytest tests/unit/orchestrators/code_review/ -v`
5. Commit: `AC-PHASE48-S2-001: Implement SecurityReviewEngine`

---

**Total Session Progress:**
- ✅ Audit Session: 3/3 P0 fixed, 11 commits
- ✅ Phase 48-S1: 15/15 tests passing, 1 commit
- ⏳ Phase 48-S2: Ready for approval (25 tests planned)
