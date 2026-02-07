# Phase 36 MCP Tools — Response Analysis & Composition

**Document:** MCP Tools Reference  
**Authority:** Phase 36 Plan  
**Tools Count:** 4 new tools  
**Status:** Specification (to be implemented in Stage 9)

---

## 🛠️ Tool Overview

Four new MCP tools expose Phase 36 security-first and multi-role capabilities:

| Tool | Purpose | Domain | Input | Output |
|------|---------|--------|-------|--------|
| `cortex_analyze_security` | P0-P2 threat classification | Security | Code scope | SecurityFirstAnalysis |
| `cortex_analyze_test_quality` | FLUFF test detection | Quality | Test file(s) | TestQualityAnalysis |
| `cortex_detect_hidden_issues` | Issue discovery | Quality | Code scope | HiddenIssueList |
| `cortex_compose_response` | Role-aware composition | Composition | Role, task, context | RoleOptimizedResponse |

---

## 🔐 Tool 1: cortex_analyze_security

**Purpose:** Proactive security analysis with P0-P2 threat classification  
**Exposure Level:** PUBLIC (prompts and MCP clients)  
**Availability:** Always (on every code operation)

### Definition

```yaml
cortex_analyze_security:
  id: "cortex_analyze_security"
  name: "Analyze Code for Security Threats (P0-P2)"
  description: |
    Analyze code scope for security vulnerabilities with priority classification:
    - P0: Critical threats (CWE-94, 89, 22, 78) that hard-gate execution
    - P1: High-risk issues (CWE-327, 502, auth gaps) included in challenges
    - P2: Advisory issues (validation, logging) included in synthesis
    
    Returns comprehensive analysis with:
    - Threat findings by severity
    - Surrounding context (related files)
    - Remediation suggestions
    - OWASP Top 10 coverage report
  
  implementation:
    class: "SecurityFirstAnalyzer"
    module: "cortex.orchestrators.core.security_first_analyzer"
    methods:
      - "analyze(code_scope: str, surrounding_context: bool = True)"
  
  parameters:
    - name: "code_scope"
      type: "string"
      required: true
      description: "Code snippet, file path, or module name to analyze"
      examples:
        - "def process_user_input(user_input): return eval(user_input)"
        - "cortex/orchestrators/core/master_orchestrator.py"
        - "cortex.orchestrators.core"
    
    - name: "surrounding_context"
      type: "boolean"
      required: false
      default: true
      description: "Include analysis of related files for context"
    
    - name: "severity_filter"
      type: "string"
      required: false
      enum: ["ALL", "P0_ONLY", "P0_P1", "P0_P1_P2"]
      default: "ALL"
      description: "Filter results by severity"
  
  response:
    type: "SecurityFirstAnalysis"
    schema:
      p0_blockers:
        type: "array"
        items: "SecurityThreatFinding"
        description: "Critical threats that block execution"
      
      p1_warnings:
        type: "array"
        items: "SecurityThreatFinding"
        description: "High-risk issues for challenges"
      
      p2_advisories:
        type: "array"
        items: "SecurityThreatFinding"
        description: "Advisory issues for synthesis"
      
      surrounding_context:
        type: "object"
        description: "Related files with potential issues"
      
      remediation_suggestions:
        type: "array"
        items: "string"
        description: "Recommended fixes"
      
      owasp_coverage:
        type: "object"
        key_type: "string"
        value_type: "boolean"
        description: "Which OWASP Top 10 items checked"
  
  example_request:
    tool: "cortex_analyze_security"
    parameters:
      code_scope: "cortex/orchestrators/core/challenge_engine.py"
      surrounding_context: true
      severity_filter: "ALL"
  
  example_response:
    p0_blockers: []
    p1_warnings:
      - cwe: "CWE-502"
        severity: "P1"
        finding: "Unsafe deserialization in YAML loading"
        location: "line 42, challenge_engine.py"
        remediation: "Use safe YAML loader"
    p2_advisories:
      - cwe: "CWE-532"
        severity: "P2"
        finding: "Logging sensitive challenge data"
        location: "line 18, challenge_engine.py"
        remediation: "Redact challenge before logging"
    owasp_coverage:
      a1_injection: true
      a2_authentication: true
      a3_sensitive_data: true
      a4_broken_access: false
      a5_broken_auth: true

```

### Usage Examples

**From Prompts:**
```
Analyze this code for security issues:

```python
@app.post("/login")
def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = db.execute(query)
    return result
```
```

**From Code:**
```python
# In any orchestrator
analyzer = SecurityFirstAnalyzer()
analysis = analyzer.analyze("app.post('/login')")

if analysis.p0_blockers:
    raise SecurityException(f"P0 threats detected: {analysis.p0_blockers}")
```

---

## 🧪 Tool 2: cortex_analyze_test_quality

**Purpose:** FLUFF test detection (zero-value test identification)  
**Exposure Level:** PUBLIC (engineers and QA)  
**Trigger:** On test review, merge requests, audits

### Definition

```yaml
cortex_analyze_test_quality:
  id: "cortex_analyze_test_quality"
  name: "Analyze Test Quality & Detect FLUFF"
  description: |
    Identify zero-value tests that masquerade as coverage:
    - Tests with no assertions
    - Tests with all dependencies mocked (>80% mocks)
    - Tests with trivial assertions (assert True)
    - Copy-paste tests with >90% similarity
    - Missing edge cases (happy path only)
    - Unreachable code in test
    
    Returns quality metrics and FLUFF detection report with:
    - FLUFF test count and details
    - Effective test count (actual coverage)
    - Missing coverage recommendations
    - Code examples for improvement
  
  implementation:
    class: "TestQualityAnalyzer"
    module: "cortex.orchestrators.support.test_quality_analyzer"
    methods:
      - "analyze(test_file: str, fluff_threshold: float = 0.5)"
  
  parameters:
    - name: "test_file"
      type: "string"
      required: true
      description: "Path to test file or directory"
      examples:
        - "tests/unit/orchestrators/test_master_orchestrator.py"
        - "tests/unit/orchestrators/" (analyze all)
    
    - name: "fluff_threshold"
      type: "number"
      required: false
      default: 0.5
      minimum: 0.0
      maximum: 1.0
      description: "Sensitivity threshold (0.5 = medium)"
    
    - name: "include_recommendations"
      type: "boolean"
      required: false
      default: true
      description: "Include improvement recommendations"
  
  response:
    type: "TestQualityAnalysis"
    schema:
      total_tests:
        type: "integer"
        description: "Total test functions found"
      
      effective_tests:
        type: "integer"
        description: "Tests that actually provide coverage"
      
      fluff_tests:
        type: "integer"
        description: "Zero-value tests"
      
      fluff_percentage:
        type: "number"
        description: "Percentage of tests that are FLUFF"
      
      fluff_details:
        type: "array"
        items:
          type: "object"
          properties:
            test_name: "string"
            issue: "enum: NO_ASSERTIONS|MOCK_EVERYTHING|TRIVIAL_ASSERTIONS|COPY_PASTE|MISSING_EDGE_CASES|UNREACHABLE_CODE"
            severity: "string (P0|P1|P2)"
            location: "string (line number)"
            recommendation: "string"
      
      missing_coverage:
        type: "array"
        items: "string"
        description: "Gap recommendations (error paths, edge cases)"
      
      quality_score:
        type: "number"
        minimum: 0.0
        maximum: 1.0
        description: "Overall test quality (0=poor, 1=excellent)"
  
  example_request:
    tool: "cortex_analyze_test_quality"
    parameters:
      test_file: "tests/unit/orchestrators/test_master_orchestrator.py"
      fluff_threshold: 0.5
      include_recommendations: true
  
  example_response:
    total_tests: 15
    effective_tests: 10
    fluff_tests: 5
    fluff_percentage: 0.33
    quality_score: 0.67
    fluff_details:
      - test_name: "test_orchestrator_init"
        issue: "NO_ASSERTIONS"
        severity: "P0"
        location: "line 42"
        recommendation: "Add assertion: assert orchestrator.mode is not None"
      
      - test_name: "test_process_request"
        issue: "MOCK_EVERYTHING"
        severity: "P1"
        location: "line 58"
        recommendation: "Use real database fixture or integration test"
    
    missing_coverage:
      - "Error path: Invalid request format"
      - "Edge case: Empty payload"
      - "Boundary: Max request size exceeded"

```

### Usage Examples

**Review Tests Before Merge:**
```
Analyze test quality for the security orchestrator tests.
```

**From Code:**
```python
analyzer = TestQualityAnalyzer()
analysis = analyzer.analyze("tests/unit/orchestrators/test_security_analyzer.py")

if analysis.fluff_percentage > 0.30:
    print(f"WARNING: {analysis.fluff_tests} FLUFF tests detected")
    for fluff in analysis.fluff_details:
        print(f"  - {fluff.test_name}: {fluff.issue}")
```

---

## 🔍 Tool 3: cortex_detect_hidden_issues

**Purpose:** Detect hidden issues (performance, memory, concurrency)  
**Exposure Level:** PUBLIC (engineers, architects)  
**Trigger:** Code review, refactoring, performance concerns

### Definition

```yaml
cortex_detect_hidden_issues:
  id: "cortex_detect_hidden_issues"
  name: "Detect Hidden Issues (Performance, Memory, Concurrency)"
  description: |
    Find issues engineers might not be aware of:
    
    PERFORMANCE:
    - N+1 query patterns (loop + DB query)
    - Unbounded loops (for/while without break)
    - Large object creation in hot paths
    
    MEMORY:
    - Large object retention in cache
    - Circular references
    - Memory accumulator without cleanup
    
    CONCURRENCY:
    - Shared mutable state without synchronization
    - Missing locks in multi-threaded code
    - Double-checked locking antipattern
    
    MAINTAINABILITY:
    - God classes (>500 LOC)
    - Deep nesting (>5 indent levels)
    - Multiple responsibilities
    
    API_CONTRACTS:
    - Breaking changes (removed fields)
    - Unversioned APIs
    - Incompatible type changes
  
  implementation:
    class: "HiddenIssueDetector"
    module: "cortex.orchestrators.support.hidden_issue_detector"
    methods:
      - "detect(code_scope: str, category_filter: str = 'ALL')"
  
  parameters:
    - name: "code_scope"
      type: "string"
      required: true
      description: "Code snippet, file, or module to analyze"
    
    - name: "category_filter"
      type: "string"
      required: false
      enum: ["ALL", "PERFORMANCE", "MEMORY", "CONCURRENCY", "MAINTAINABILITY", "API_CONTRACTS"]
      default: "ALL"
      description: "Filter by issue category"
    
    - name: "severity_threshold"
      type: "string"
      required: false
      enum: ["P0", "P0_P1", "ALL"]
      default: "P0_P1"
      description: "Include only high-severity issues"
  
  response:
    type: "HiddenIssueList"
    schema:
      issues:
        type: "array"
        items:
          type: "object"
          properties:
            category: "enum: PERFORMANCE|MEMORY|CONCURRENCY|MAINTAINABILITY|API_CONTRACTS"
            severity: "string (P0|P1|P2)"
            description: "string"
            location: "string (line/file)"
            example: "string (code snippet)"
            remediation: "string (fix suggestion)"
      
      issue_count:
        type: "integer"
      
      by_category:
        type: "object"
        key_type: "string"
        value_type: "integer"
        description: "Count per category"
  
  example_response:
    issues:
      - category: "PERFORMANCE"
        severity: "P1"
        description: "N+1 query pattern detected"
        location: "line 42, user_service.py"
        example: "for user in users: db.query(f'SELECT * FROM posts WHERE user_id={user.id}')"
        remediation: "Use JOIN or batch load posts"
      
      - category: "CONCURRENCY"
        severity: "P1"
        description: "Shared mutable state without synchronization"
        location: "line 18, cache.py"
        example: "self.cache[key] = expensive_object  # Not thread-safe"
        remediation: "Use threading.Lock() or @synchronized decorator"
    
    issue_count: 2
    by_category:
      PERFORMANCE: 1
      CONCURRENCY: 1

```

### Usage Examples

**Detect Issues During Code Review:**
```
Detect hidden issues in the master orchestrator.
```

**From Code:**
```python
detector = HiddenIssueDetector()
issues = detector.detect("cortex/orchestrators/core/master_orchestrator.py")

for issue in issues:
    print(f"{issue.severity} {issue.category}: {issue.description}")
    print(f"  Location: {issue.location}")
    print(f"  Fix: {issue.remediation}")
```

---

## 🎨 Tool 4: cortex_compose_response

**Purpose:** Compose role-aware responses with automatic template selection  
**Exposure Level:** PUBLIC (all users)  
**Trigger:** Every response generation (internal use)

### Definition

```yaml
cortex_compose_response:
  id: "cortex_compose_response"
  name: "Compose Role-Aware Response"
  description: |
    Compose responses adapted to user role and task type.
    
    Automatically selects and composes template blocks based on:
    - User role (ENGINEER, PM, BUSINESS, ARCHITECT, SECURITY)
    - Task type (IMPLEMENT, AUDIT, QUERY, PLAN, DEBUG, SECURITY)
    - Context (code scope, request details)
    
    Returns complete, role-optimized response ready for user.
  
  implementation:
    class: "MultiRoleResponseEngine"
    module: "cortex.orchestrators.response.multi_role_response_engine"
    methods:
      - "compose_response(role: str, task: str, context: dict)"
  
  parameters:
    - name: "role"
      type: "string"
      required: true
      enum: ["ENGINEER", "PM", "BUSINESS", "ARCHITECT", "SECURITY"]
      description: "User role (auto-detected if not specified)"
      examples:
        - "ENGINEER"
        - "PM"
        - "BUSINESS"
    
    - name: "task"
      type: "string"
      required: true
      enum: ["IMPLEMENT", "AUDIT", "QUERY", "PLAN", "DEBUG", "SECURITY"]
      description: "Task type"
    
    - name: "context"
      type: "object"
      required: true
      description: "Request context"
      properties:
        content: "string (main request content)"
        scope: "string (code/module scope)"
        code: "string (code snippet if applicable)"
        metadata: "object (additional context)"
  
  response:
    type: "RoleOptimizedResponse"
    schema:
      role: "string (detected/provided role)"
      task: "string (task type)"
      response: "string (formatted response)"
      blocks_used: "array (template blocks composed)"
      verbosity_level: "string (HIGH|MEDIUM|LOW)"
      estimated_tokens: "integer"
  
  example_request:
    tool: "cortex_compose_response"
    parameters:
      role: "ENGINEER"
      task: "IMPLEMENT"
      context:
        content: "Add caching layer to user service"
        scope: "cortex/orchestrators/core/user_service.py"
        code: "def get_user(user_id): return db.query(f'SELECT * FROM users WHERE id={user_id}')"
  
  example_response:
    role: "ENGINEER"
    task: "IMPLEMENT"
    blocks_used:
      - "HeaderBlock"
      - "SecurityBlock"
      - "TDDPhaseBlock"
      - "MetricsBlock"
      - "VerdictBlock"
    verbosity_level: "HIGH"
    estimated_tokens: 1850
    response: |
      ## 🧠 CORTEX IMPLEMENT
      **Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅
      
      ---
      
      ### 🔒 Security Analysis (P0-P2)
      
      | CWE | Severity | Finding | Remediation |
      |-----|----------|---------|------------|
      | CWE-89 | P1 | SQL Injection risk in query | Use parameterized queries |
      
      ### 🎯 Implementation Plan (TDD)
      
      **RED Phase:**
      - Test: `test_get_user_uses_cache()`
      - Test: `test_cache_key_format()`
      
      **GREEN Phase:**
      - Implement: `CacheLayer` class
      - Add: TTL configuration
      
      **REFACTOR Phase:**
      - Extract: Cache strategy to policy
      - Add: Metrics logging
      
      ...

```

### Usage Examples

**Internal Usage (Orchestrators):**
```python
# In any orchestrator
engine = MultiRoleResponseEngine()
response = engine.compose_response(
    role="ENGINEER",
    task="IMPLEMENT",
    context={
        "content": user_request,
        "scope": "cortex/orchestrators/core/master_orchestrator.py",
        "code": code_snippet
    }
)
```

**Prompt Usage:**
```
Compose response for this ENGINEER wanting to implement a caching layer.
```

---

## 🔌 Integration Points

### Orchestrator Integration

```python
# In InteractionOrchestrator
from cortex.orchestrators.response.multi_role_response_engine import MultiRoleResponseEngine
from cortex.orchestrators.core.security_first_analyzer import SecurityFirstAnalyzer
from cortex.orchestrators.support.test_quality_analyzer import TestQualityAnalyzer
from cortex.orchestrators.support.hidden_issue_detector import HiddenIssueDetector

class InteractionOrchestrator:
    def __init__(self):
        self.mrle = MultiRoleResponseEngine()
        self.security_analyzer = SecurityFirstAnalyzer()
        self.test_analyzer = TestQualityAnalyzer()
        self.issue_detector = HiddenIssueDetector()
    
    def handle_request(self, user_request, context):
        # 1. Analyze security
        security_analysis = self.security_analyzer.analyze(context.code_scope)
        
        # 2. If P0 threats, block
        if security_analysis.p0_blockers:
            raise SecurityException(security_analysis.p0_blockers)
        
        # 3. Detect test quality issues
        test_analysis = self.test_analyzer.analyze(context.test_scope)
        
        # 4. Detect hidden issues
        hidden_issues = self.issue_detector.detect(context.code_scope)
        
        # 5. Compose response
        response = self.mrle.compose_response(
            role=context.user_role,
            task=context.task_type,
            context={
                "security": security_analysis,
                "test_quality": test_analysis,
                "hidden_issues": hidden_issues,
                "user_request": user_request
            }
        )
        
        return response
```

### Wiring Configuration

```yaml
# cortex/wiring/specifications/wiring.yaml
mcp_tools:
  cortex_analyze_security:
    class: "SecurityFirstAnalyzer"
    module: "cortex.orchestrators.core.security_first_analyzer"
    orchestrator: "SecurityOrchestrator"
    exposure: "PUBLIC"
  
  cortex_analyze_test_quality:
    class: "TestQualityAnalyzer"
    module: "cortex.orchestrators.support.test_quality_analyzer"
    orchestrator: "QualityOrchestrator"
    exposure: "PUBLIC"
  
  cortex_detect_hidden_issues:
    class: "HiddenIssueDetector"
    module: "cortex.orchestrators.support.hidden_issue_detector"
    orchestrator: "QualityOrchestrator"
    exposure: "PUBLIC"
  
  cortex_compose_response:
    class: "MultiRoleResponseEngine"
    module: "cortex.orchestrators.response.multi_role_response_engine"
    orchestrator: "InteractionOrchestrator"
    exposure: "PUBLIC"
```

---

## ✅ Success Criteria

**All 4 Tools:**
- ✅ Exposed via MCP gateway
- ✅ Callable from prompts and external clients
- ✅ Fully tested (20+ tests per tool)
- ✅ Documented with examples
- ✅ Backward compatible with legacy systems
- ✅ <500ms response time

---

**Status:** SPECIFICATION (to be implemented in Phase 36, Stage 9)
