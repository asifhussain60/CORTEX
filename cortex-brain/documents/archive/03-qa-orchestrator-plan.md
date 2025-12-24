# 🔍 QA Orchestrator - Sub-Plan

**Purpose:** Unified quality assurance with architectural reviews, code reviews, and security assessments  
**Complexity:** MEDIUM (2 files consolidated, analysis-heavy workflows)  
**LOC:** 800 (from 549 existing → expanded with security + performance analysis)  
**Test Strategy:** SMOKE TEST ONLY (2 tests: initialization + code review workflow)

---

## 📋 Navigation

- **Master Plan:** [orchestration-master-plan.md](../orchestration-master-plan.md)
- **Previous:** [DevOps Orchestrator Plan](02-devops-orchestrator-plan.md)
- **Next:** Planning Orchestrator (Phase 2 Complete)
- **Workflow YAML:** `src/orchestration_3_0/workflows/qa_workflow.yaml`

---

## 1️⃣ Existing State (Current Implementation)

### Current Files Being Consolidated

| File | LOC | Purpose | Key Features |
|------|-----|---------|--------------|
| `src/code_review/code_review_orchestrator.py` | 257 | Tiered code review | 3-depth analysis (QUICK/STANDARD/DEEP), security patterns, DependencyCrawler integration |
| `src/operations/review.py` | 292 | CLI wrapper | User-friendly interface, review operations, report generation |

**Total LOC:** 549 lines across 2 files  
**Target LOC:** 800 lines (46% expansion - adding security scan, performance analysis, architectural review)

**Note:** Master plan originally listed "2 orchestrators (1,580 LOC)" but actual audit finds 2 files (549 LOC). The remaining LOC may have been estimated for planned enhancements (security scan, performance analysis).

### Current QA Workflows

**1. Code Review Workflow**
- **Analysis Depths:**
  - **QUICK:** Only changed files (fast, 1-2 min)
  - **STANDARD:** Changed files + direct dependencies (moderate, 5-10 min)
  - **DEEP:** Changed files + dependencies + tests + indirect deps (thorough, 15-30 min)
- **Issue Categories:** Security, performance, maintainability, style, testing
- **Severity Levels:** CRITICAL, HIGH, MEDIUM, LOW

**2. Security Analysis**
- **Patterns Detected:**
  - SQL injection vulnerabilities
  - Hardcoded secrets/passwords
  - Unsafe deserialization
  - XSS vulnerabilities
  - Command injection
- **Integration:** Runs during code review STANDARD/DEEP analysis

**3. Review Operations (CLI)**
- `create_review`: Start new code review session
- `load_review`: Load existing review by ID
- `analyze_file`: Analyze specific file
- `generate_report`: Generate review report
- `list_reviews`: List all reviews with status

### Current Issues & Pain Points

**Fragmentation:**
- Code review orchestrator separate from CLI wrapper
- Security analysis embedded in code analyzer (not reusable)
- No architectural review capability
- Performance analysis missing

**Reliability:**
- No session persistence (review state lost on crash)
- Manual file selection for review
- No integration with Planning/Execution orchestrators
- Review reports not stored persistently

**Scalability:**
- Single-project focus (no multi-tenant support)
- No RBAC (anyone can trigger review)
- No cross-project review coordination
- Token counting manual (not integrated with metrics)

---

## 2️⃣ New Structure

### Target Architecture

```
src/orchestration_3_0/orchestrators/qa/
├── __init__.py
├── qa_orchestrator.py               # Main orchestrator (250 LOC)
├── code_review_engine.py            # Code review with 3-depth analysis (200 LOC)
├── security_scanner.py              # Security vulnerability scanning (150 LOC)
├── performance_analyzer.py          # Performance bottleneck detection (100 LOC)
└── architecture_reviewer.py         # SOLID principles, design patterns (100 LOC)
```

**Total Target LOC:** 800 lines (46% expansion from 549)

### Component Responsibilities

**Main Orchestrator (`qa_orchestrator.py` - 250 LOC)**
- Extends `BaseOrchestrator`
- State machine integration (INITIALIZED → CODE_REVIEW → SECURITY_SCAN → PERFORMANCE_ANALYSIS → ARCHITECTURE_REVIEW → COMPLETED)
- DI container registration
- Session manager persistence
- Review report generation

**Code Review Engine (`code_review_engine.py` - 200 LOC)**
- 3-depth analysis (QUICK/STANDARD/DEEP)
- Issue detection by category (security, performance, maintainability, style, testing)
- DependencyCrawler integration for context-aware review
- Token counting per file
- Severity scoring (CRITICAL/HIGH/MEDIUM/LOW)

**Security Scanner (`security_scanner.py` - 150 LOC)**
- SQL injection detection
- Hardcoded secrets scanning
- Unsafe deserialization patterns
- XSS vulnerability detection
- Command injection patterns
- Compliance checks (OWASP Top 10)

**Performance Analyzer (`performance_analyzer.py` - 100 LOC)**
- N+1 query detection
- Inefficient loops
- Large object creation in loops
- Memory leaks (unclosed resources)
- Algorithmic complexity analysis (O(n²) patterns)

**Architecture Reviewer (`architecture_reviewer.py` - 100 LOC)**
- SOLID principles validation
- Design pattern recognition (Factory, Singleton, Observer, Strategy)
- Dependency inversion check
- Circular dependency detection
- Layer boundary violations (e.g., presentation → database direct access)

---

## 3️⃣ State Machine Design

### QA Workflow States

```
INITIALIZED
  ↓
CODE_REVIEW_VALIDATING_DOR
  ↓ (DoR: files to review specified)
CODE_REVIEW_EXECUTING
  ↓ (analyzes files, detects issues)
CODE_REVIEW_VALIDATING_DOD
  ↓ (DoD: review complete, issues logged)
SECURITY_SCAN_VALIDATING_DOR
  ↓ (DoR: code review complete)
SECURITY_SCAN_EXECUTING
  ↓ (scans for vulnerabilities)
SECURITY_SCAN_VALIDATING_DOD
  ↓ (DoD: security issues logged)
PERFORMANCE_ANALYSIS_VALIDATING_DOR
  ↓ (DoR: security scan complete)
PERFORMANCE_ANALYSIS_EXECUTING
  ↓ (detects bottlenecks)
PERFORMANCE_ANALYSIS_VALIDATING_DOD
  ↓ (DoD: performance issues logged)
ARCHITECTURE_REVIEW_VALIDATING_DOR
  ↓ (DoR: performance analysis complete)
ARCHITECTURE_REVIEW_EXECUTING
  ↓ (validates SOLID, design patterns)
ARCHITECTURE_REVIEW_VALIDATING_DOD
  ↓ (DoD: architecture issues logged)
COMPLETED
```

### Transition Guards

- **CODE_REVIEW → SECURITY_SCAN:** Review complete, issues categorized
- **SECURITY_SCAN → PERFORMANCE_ANALYSIS:** No CRITICAL security issues (or approved to proceed)
- **PERFORMANCE_ANALYSIS → ARCHITECTURE_REVIEW:** Performance issues logged
- **ARCHITECTURE_REVIEW → COMPLETED:** All QA phases complete

---

## 4️⃣ Integration Points

### Planning Orchestrator Integration

**Planning triggers QA review:**
```python
# After feature decomposition, run QA review
qa_orchestrator.execute_phase("CODE_REVIEW", {
    "files": ["src/auth/login.py", "src/auth/password.py"],
    "depth": "DEEP",
    "focus": ["security", "maintainability"]
})
```

### Execution Orchestrator Integration

**Execution coordinates pre-deployment QA:**
```python
# Before deployment, run full QA workflow
execution_orchestrator.execute_plan({
    "phases": [
        {"orchestrator": "qa", "phase": "CODE_REVIEW"},
        {"orchestrator": "qa", "phase": "SECURITY_SCAN"},
        {"orchestrator": "qa", "phase": "PERFORMANCE_ANALYSIS"},
        {"orchestrator": "qa", "phase": "ARCHITECTURE_REVIEW"},
        {"orchestrator": "devops", "phase": "DEPLOY"}  # Only if QA passes
    ]
})
```

### DevOps Orchestrator Integration

**DevOps deployment gate:**
```python
# QA review is gate #3 in 19 deployment gates
if qa_orchestrator.has_critical_issues():
    devops_orchestrator.block_deployment("QA review found CRITICAL issues")
```

---

## 5️⃣ Implementation Details

### Code Review Engine Component

**Purpose:** 3-depth code analysis with issue detection

**Key Methods:**
```python
class CodeReviewEngine:
    def analyze_files(
        self,
        files: List[str],
        depth: str,  # QUICK, STANDARD, DEEP
        focus_categories: List[str] = None  # security, performance, maintainability, style, testing
    ) -> Dict[str, Any]:
        """Analyze files with specified depth."""
        
    def detect_issues(self, file_content: str, file_path: str) -> List[ReviewIssue]:
        """Detect issues in file content."""
        
    def categorize_issue(self, issue: ReviewIssue) -> str:
        """Categorize issue by type."""
        
    def calculate_severity(self, issue: ReviewIssue) -> str:
        """Calculate severity (CRITICAL/HIGH/MEDIUM/LOW)."""
```

**Issue Detection Patterns:**
- **Security:** SQL injection, XSS, hardcoded secrets
- **Performance:** Nested loops, inefficient queries, large object creation
- **Maintainability:** Long functions (>50 lines), high complexity (>10 cyclomatic), duplicated code
- **Style:** PEP 8 violations, inconsistent naming, missing docstrings
- **Testing:** Missing tests, low coverage, no assertions

### Security Scanner Component

**Purpose:** Vulnerability scanning with OWASP compliance

**Key Methods:**
```python
class SecurityScanner:
    def scan_for_vulnerabilities(self, files: List[str]) -> List[SecurityIssue]:
        """Scan files for security vulnerabilities."""
        
    def detect_sql_injection(self, code: str) -> List[SecurityIssue]:
        """Detect SQL injection patterns."""
        
    def scan_for_secrets(self, code: str) -> List[SecurityIssue]:
        """Detect hardcoded secrets."""
        
    def check_owasp_compliance(self, issues: List[SecurityIssue]) -> Dict[str, Any]:
        """Check OWASP Top 10 compliance."""
```

**Vulnerability Patterns:**
- **A01: Broken Access Control:** Missing authorization checks
- **A02: Cryptographic Failures:** Weak encryption, plaintext passwords
- **A03: Injection:** SQL, command, XSS injection
- **A04: Insecure Design:** No rate limiting, no input validation
- **A05: Security Misconfiguration:** Debug mode enabled, default credentials

### Performance Analyzer Component

**Purpose:** Bottleneck detection and optimization suggestions

**Key Methods:**
```python
class PerformanceAnalyzer:
    def analyze_performance(self, files: List[str]) -> List[PerformanceIssue]:
        """Analyze performance bottlenecks."""
        
    def detect_n_plus_one_queries(self, code: str) -> List[PerformanceIssue]:
        """Detect N+1 query patterns."""
        
    def detect_inefficient_loops(self, code: str) -> List[PerformanceIssue]:
        """Detect inefficient loops (nested, large iterations)."""
        
    def calculate_algorithmic_complexity(self, code: str) -> str:
        """Calculate Big-O complexity (O(1), O(n), O(n²), O(log n))."""
```

**Performance Patterns:**
- **N+1 Queries:** Database query inside loop
- **Inefficient Loops:** Nested loops with O(n²) complexity
- **Memory Leaks:** Unclosed file handles, database connections
- **Large Object Creation:** Creating large objects inside loops
- **Synchronous I/O:** Blocking I/O in async context

### Architecture Reviewer Component

**Purpose:** SOLID principles and design pattern validation

**Key Methods:**
```python
class ArchitectureReviewer:
    def review_architecture(self, files: List[str]) -> List[ArchitectureIssue]:
        """Review architecture for SOLID violations."""
        
    def check_solid_principles(self, code: str) -> List[ArchitectureIssue]:
        """Check SOLID principles."""
        
    def detect_design_patterns(self, code: str) -> List[str]:
        """Detect design patterns (Factory, Singleton, Observer, Strategy)."""
        
    def detect_circular_dependencies(self, files: List[str]) -> List[str]:
        """Detect circular dependencies."""
```

**SOLID Violations:**
- **Single Responsibility:** Class has multiple responsibilities
- **Open/Closed:** Modifying class instead of extending
- **Liskov Substitution:** Subclass violates parent contract
- **Interface Segregation:** Fat interfaces with unused methods
- **Dependency Inversion:** High-level modules depend on low-level modules

---

## 6️⃣ Configuration

### QA Workflow YAML

**File:** `src/orchestration_3_0/workflows/qa_workflow.yaml`

```yaml
name: qa_workflow
version: 1.0.0
orchestrator: qa

phases:
  - name: CODE_REVIEW
    description: Tiered code review (QUICK/STANDARD/DEEP)
    dor:
      - files_to_review_specified
      - analysis_depth_selected
    dod:
      - review_complete
      - issues_logged
    timeout: 1800  # 30 minutes
    
  - name: SECURITY_SCAN
    description: Vulnerability scanning (OWASP Top 10)
    dor:
      - code_review_complete
    dod:
      - vulnerabilities_identified
      - severity_scored
    timeout: 600  # 10 minutes
    
  - name: PERFORMANCE_ANALYSIS
    description: Bottleneck detection
    dor:
      - security_scan_complete
    dod:
      - performance_issues_logged
      - complexity_calculated
    timeout: 300  # 5 minutes
    
  - name: ARCHITECTURE_REVIEW
    description: SOLID principles validation
    dor:
      - performance_analysis_complete
    dod:
      - architecture_issues_logged
      - design_patterns_identified
    timeout: 300  # 5 minutes

metrics:
  - total_issues_count
  - critical_issues_count
  - review_duration_seconds
  - files_analyzed_count

validation:
  max_critical_issues: 0  # Block deployment if any CRITICAL issues
  max_high_issues: 5      # Warn if > 5 HIGH issues
  min_coverage_percent: 80
```

---

## 7️⃣ Testing Strategy

### Smoke Tests (2 tests)

**Test 1: Initialization**
```python
def test_qa_orchestrator_initialization():
    """Verify QA orchestrator initializes correctly."""
    state_machine = StateMachine()
    container = DependencyContainer()
    orchestrator = QAOrchestrator(state_machine, container)
    
    assert orchestrator is not None
    assert orchestrator.code_review_engine is not None
    assert orchestrator.security_scanner is not None
    assert orchestrator.performance_analyzer is not None
    assert orchestrator.architecture_reviewer is not None
```

**Test 2: Code Review Workflow**
```python
def test_code_review_workflow():
    """Verify code review workflow executes."""
    orchestrator = QAOrchestrator(state_machine, container)
    
    # Mock code review engine
    orchestrator.code_review_engine.analyze_files = Mock(return_value={
        "issues": [{"severity": "HIGH", "category": "security", "message": "SQL injection"}],
        "total_issues": 1
    })
    
    # Execute code review phase
    result = await orchestrator.execute_phase("CODE_REVIEW", {
        "files": ["test.py"],
        "depth": "STANDARD"
    })
    
    assert result.success
    assert state_machine.current_state == "CODE_REVIEW_VALIDATING_DOD"
    assert len(result.metadata["issues"]) == 1
```

**Why only 2 tests?**
- QA Orchestrator is analysis-heavy but workflow is straightforward
- Smoke tests validate initialization and core code review workflow
- Comprehensive tests would be 40+ tests (excessive for Phase 1 validation)

---

## 8️⃣ Migration Strategy

### Phase 1: Create New QA Orchestrator (Week 1)
- Implement `QAOrchestrator` extending `BaseOrchestrator`
- Create 4 component files (code_review_engine, security_scanner, performance_analyzer, architecture_reviewer)
- Write 2 smoke tests
- Integrate with State Machine, DI Container, Session Manager

### Phase 2: Legacy Orchestrator Deprecation (Week 1)
- Mark old files as deprecated: `code_review_orchestrator.py`, `review.py`
- Add deprecation warnings when old orchestrators called
- Update all references to use new QA Orchestrator

### Phase 3: Legacy Removal (Week 2)
- Delete old orchestrators:
  - `src/code_review/code_review_orchestrator.py` (257 LOC)
  - `src/operations/review.py` (292 LOC)
- Remove old tests, documentation
- Update all integration points

---

## 9️⃣ Extensibility Analysis

**Extensibility Rating: ⭐⭐⭐⭐⭐ (5/5) - Highly extensible**

### Why Highly Extensible?

**1. Review Engine Plugins**
- New issue detectors can be added as plugins
- Example: Add TypeScript linter, C# static analyzer

**2. Security Scanner Rules**
- Custom vulnerability patterns can be registered
- Organization-specific compliance checks

**3. Performance Metrics**
- Custom performance analyzers (database query optimization, API latency)

**4. Architecture Patterns**
- Custom design pattern detection (DDD, Hexagonal, Event-Driven)

### Extension Example: Custom Security Rule

```python
# Add custom security rule
class CustomEncryptionChecker(SecurityRule):
    def check(self, code: str) -> List[SecurityIssue]:
        """Check for weak encryption algorithms."""
        if "DES" in code or "MD5" in code:
            return [SecurityIssue(
                severity="HIGH",
                message="Weak encryption algorithm detected",
                suggestion="Use AES-256 or SHA-256 instead"
            )]
        return []

# Register in SecurityScanner
security_scanner.register_rule("custom_encryption", CustomEncryptionChecker())
```

---

## 🔟 Success Criteria

**Completion Checklist:**
- [ ] QA Orchestrator initialized successfully
- [ ] Code review engine analyzes files with 3-depth support
- [ ] Security scanner detects vulnerabilities (OWASP Top 10)
- [ ] Performance analyzer identifies bottlenecks
- [ ] Architecture reviewer validates SOLID principles
- [ ] Smoke tests passing (2/2 - 100% success rate)
- [ ] Integration with Planning/Execution orchestrators working
- [ ] Session persistence survives crashes
- [ ] State machine validates all transitions
- [ ] Legacy orchestrators deprecated and removed

**Metrics:**
- Code review duration: < 30 minutes (DEEP analysis)
- Security scan duration: < 10 minutes
- Performance analysis: < 5 minutes
- Architecture review: < 5 minutes
- Total QA workflow: < 50 minutes (all phases)

---

## 1️⃣1️⃣ Related Documents

- [Orchestration Master Plan](../orchestration-master-plan.md)
- [Phase 1 Core Infrastructure Complete](../../reports/phase-1-core-infrastructure-complete.md)
- [DevOps Orchestrator Plan](02-devops-orchestrator-plan.md)
- [Planning Orchestrator](src/orchestration_3_0/orchestrators/planning/) - Phase 2 Complete

---

**Next Steps:** Phase 1 sub-plans complete! Ready to implement DevOps + QA orchestrators (Week 1).
