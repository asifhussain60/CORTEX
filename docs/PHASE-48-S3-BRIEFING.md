# 🧠 Phase 48-S3 Briefing: Company Domain Compliance Validation
**Date:** February 9, 2026 | **Status:** Ready for Implementation  
**Previous Phases:** S1 ✅ (15/15 tests) | S2 ✅ (13/13 tests)  
**Combined Status:** 28/28 tests passing ✅  
**Next Phase:** S3 - Company Domain Compliance  

---

## Executive Summary

**Phase 48-S3** adds company-specific governance to the review engine. Code reviews validate against business rules, security standards, architecture patterns, API conventions, and database standards from the company domains system.

### Key Metrics

| Metric | Value |
|--------|-------|
| **Duration** | 1 day |
| **Test Target** | 20 tests |
| **LOC Target** | 500 |
| **Dependencies** | S1 ✅, S2 ✅ |
| **Priority** | P1 (blocks S4+) |

---

## S1 + S2 Foundation (Complete ✅)

### What's Already Implemented

**Phase 48-S1: Core Review Engine**
```python
# Diff parsing
parser = GitDiffParser()
changes = parser.parse(diff_text)  # List[FileChange]

# Review orchestration
orchestrator = CodeReviewOrchestrator()
report = orchestrator.review(context, diff_text)  # ReviewReport
```

**Phase 48-S2: Security Review Engine**
```python
# CWE detection (7 patterns)
security_engine = SecurityReviewEngine()
findings = security_engine.analyze_diff(changes, code_content)
# Returns: List[SecurityFinding] with P0/P1 severity
```

### Combined Test Status
- ✅ GitDiffParser (6/6 tests)
- ✅ ReviewContext (2/2 tests)
- ✅ ReviewReport (3/3 tests)
- ✅ CodeReviewOrchestrator (3/3 tests)
- ✅ SecurityReviewEngine (13/13 tests)
- **Total: 28/28 passing**

---

## S3 Scope: Company Domain Compliance Validation

### Overview
Validate PRs against company-specific standards:
- 🏛️ **Security standards** (PCI-DSS, HIPAA, SOX)
- 🏗️ **Architecture patterns** (microservices, event-driven)
- 📡 **API conventions** (REST, GraphQL)
- 🗄️ **Database standards** (schema naming, indexes)
- 🚀 **Deployment requirements** (12-factor)

### Deliverables

#### 1. CompanyDomainLoader (File-to-Domain Mapping)
**Purpose:** Identify which company domains apply to a file change

**Domain Categories:**
- Payment Processing (PCI-DSS compliance)
- Healthcare (HIPAA/PHI handling)
- Data Protection (GDPR, SOC 2)
- API Services (REST, GraphQL conventions)
- Data Storage (SQL, NoSQL standards)
- Infrastructure (12-factor, containerization)
- Microservices (service mesh, communication)
- Event-Driven (message queue standards)

**Example Usage:**
```python
loader = CompanyDomainLoader()
domains = loader.identify_domains([change])
# Returns: ["payment-processing", "pci-dss", "api-services"]
```

**Tests to Write (5 tests):**
1. Identify payment domain for payment-related files
2. Identify healthcare domain for patient data files
3. Identify API domain based on file path
4. Identify database domain based on SQL file
5. Multiple domains for mixed files

**Implementation Pattern:**
```python
class CompanyDomainLoader:
    """Load company domains for code review validation"""
    
    def __init__(self):
        """Initialize domain mappings"""
        self.domain_mappings = self._load_domain_mappings()
        self.file_patterns = self._initialize_patterns()
    
    def identify_domains(self, changes: List[FileChange]) -> Set[str]:
        """Identify domains based on file paths"""
        domains = set()
        
        for change in changes:
            # Match file path against domain patterns
            for domain, patterns in self.file_patterns.items():
                for pattern in patterns:
                    if re.match(pattern, change.filepath):
                        domains.add(domain)
        
        return domains
    
    def _load_domain_mappings(self) -> Dict[str, Domain]:
        """Load domain config from company/domains/"""
        domains = {}
        domain_dir = Path("company/domains")
        
        for yaml_file in domain_dir.glob("*.yaml"):
            domain = self._parse_domain_yaml(yaml_file)
            domains[domain.id] = domain
        
        return domains
```

#### 2. ComplianceValidator (Rule Matching Engine)
**Purpose:** Match code patterns against domain rules

**Rules Types:**
- File naming conventions (snake_case vs camelCase)
- Function/method naming patterns
- Security requirements (authentication, authorization)
- Error handling requirements
- Logging requirements
- Configuration management (env vars vs hardcoded)
- Schema validation requirements

**Tests to Write (6 tests):**
1. Validate REST API endpoint naming
2. Detect hardcoded secrets (should fail)
3. Validate database naming conventions
4. Check error handling compliance
5. Verify logging levels
6. Validate schema types

**Implementation Pattern:**
```python
class ComplianceValidator:
    """Validate code against domain rules"""
    
    def __init__(self, domains: Dict[str, Domain]):
        """Initialize with company domains"""
        self.domains = domains
    
    def validate_changes(
        self, 
        changes: List[FileChange],
        code_content: Dict[str, str],
        domains: Set[str]
    ) -> List[ReviewFinding]:
        """Validate changes against domain rules"""
        findings = []
        
        for domain_id in domains:
            domain = self.domains[domain_id]
            for rule in domain.rules:
                results = rule.validate(changes, code_content)
                findings.extend(results)
        
        return findings
```

#### 3. Domain Rule Matching Engine
**Purpose:** Apply regex/pattern rules to code

**Rule Types:**
- **Regex Rules:** Match patterns in code
- **Naming Rules:** Validate identifiers (functions, variables, tables)
- **Structural Rules:** Require specific code patterns
- **Config Rules:** Validate configuration file formats
- **Security Rules:** Check for security patterns (secrets, validation)

**Tests to Write (5 tests):**
1. Match endpoint naming: `/api/v1/...`
2. Detect hardcoded credentials
3. Validate table naming: `tbl_*` or `table_*`
4. Check for error handlers in try/catch
5. Validate auth headers in API calls

#### 4. Violation Report Generation
**Purpose:** Create clear, actionable compliance reports

**Report Contents:**
- Which domain rule violated
- Where in code (file:line)
- What the rule expects
- Example of correct code
- Link to domain documentation

**Tests to Write (4 tests):**
1. Generate report for API naming violation
2. Generate report for hardcoded secret
3. Generate report for missing error handling
4. Generate multi-violation report

---

## Implementation Plan

### Phase 1: CompanyDomainLoader (5 hours)
1. Create test cases (5 tests)
2. Implement file-to-domain mapping
3. Load domain YAML configurations
4. Verify 5/5 tests passing

### Phase 2: ComplianceValidator (6 hours)
1. Create test cases (6 tests)
2. Implement rule matching engine
3. Wire domain rules
4. Verify 6/6 tests passing

### Phase 3: Domain Rule Patterns (5 hours)
1. Create test cases (5 tests)
2. Implement regex/naming rules
3. Add security pattern detection
4. Verify 5/5 tests passing

### Phase 4: Violation Reports (4 hours)
1. Create test cases (4 tests)
2. Implement report generation
3. Add contextual information
4. Verify 4/4 tests passing

**Total:** 20 hours ≈ 1 day ✅

---

## File Structure (S3)

```
cortex/orchestrators/code_review/
├── core_review_engine.py           (S1)
├── security_review_engine.py       (S2)
├── company_domain_loader.py        (S3 - NEW)
├── compliance_validator.py         (S3 - NEW)
├── domain_rule_engine.py           (S3 - NEW)
└── __init__.py

tests/unit/orchestrators/code_review/
├── test_phase48_s1_core_review_engine.py
├── test_phase48_s2_security_review_engine.py
├── test_phase48_s3_domain_loader.py         (S3 - NEW)
├── test_phase48_s3_compliance_validator.py  (S3 - NEW)
├── test_phase48_s3_domain_rules.py          (S3 - NEW)
└── test_phase48_s3_violation_reporting.py   (S3 - NEW)
```

---

## Domain Architecture Integration

### Loading Domains
```yaml
# company/domains/payment-processing.yaml
id: "payment-processing"
name: "Payment Processing"
category: "security"
standards: ["PCI-DSS", "PCI-3.2.1"]
file_patterns:
  - "src/payment/**/*.py"
  - "src/checkout/**/*.py"
  - "cortex/payment/**/*.py"

rules:
  - id: "PAYMENT-001"
    type: "security"
    title: "Never hardcode API keys"
    pattern: '(stripe_key|api_key)\s*=\s*["\']'
    severity: "P0_CRITICAL"
    fix: "Use environment variables: API_KEY = os.getenv('STRIPE_API_KEY')"
```

### Matching Domains
```
PR Changes:
  - src/payment/checkout.py (modified)
  - src/payment/processor.py (modified)

Identified Domains:
  ✅ payment-processing
  ✅ pci-dss (via payment-processing)
  ✅ security (via payment-processing)
```

### Applying Rules
```
Rules for payment-processing domain:
  1. PAYMENT-001: No hardcoded API keys
  2. PAYMENT-002: All transactions logged
  3. PAYMENT-003: PCI-3.2.1 compliant data handling
  4. ...

Violations Found:
  ❌ PAYMENT-001 @ src/payment/checkout.py:45 - Hardcoded Stripe key
  ❌ PAYMENT-002 @ src/payment/processor.py:120 - Missing log statement
```

---

## Acceptance Criteria (S3)

✅ **All Must Pass:**
- [ ] CompanyDomainLoader identifies correct domains from file paths
- [ ] ComplianceValidator applies domain rules correctly
- [ ] Rule patterns detect 95%+ of violations
- [ ] Violation reports include actionable fix suggestions
- [ ] Multi-domain PRs handled correctly
- [ ] False positives minimized (<5%)
- [ ] All 20 tests passing (20/20)
- [ ] No lint errors (black, flake8)
- [ ] Type hints on all public methods
- [ ] Google-style docstrings on all classes
- [ ] Integration with S1+S2 verified
- [ ] Code coverage >90%

---

## Integration with S1+S2

### Review Orchestrator Flow

```
User Submits PR
       ↓
S1: GitDiffParser
  - Parse git diff
  - Extract file changes
       ↓
S2: SecurityReviewEngine
  - Detect CWE vulnerabilities
  - P0/P1 security findings
       ↓
S3: CompanyDomainLoader ← NEW
  - Identify relevant domains
       ↓
S3: ComplianceValidator ← NEW
  - Apply domain rules
  - Generate compliance findings
       ↓
CodeReviewOrchestrator
  - Aggregate all findings
  - Determine review status
       ↓
ReviewReport
  - APPROVED (no issues)
  - CONDITIONAL (P1/P2 issues)
  - REJECTED (P0 issues)
```

### Data Flow Example

```python
# Input: PR diff
diff = """
diff --git a/src/payment/checkout.py
+STRIPE_KEY = "sk_live_abc123..."  # Hardcoded!
+query = f"SELECT * FROM users WHERE id = {id}"  # SQL injection!
"""

# S1: Parse changes
changes = [
    FileChange(
        filepath="src/payment/checkout.py",
        change_type="modified",
        lines_added=2,
        lines_removed=0,
        line_diffs=[
            {"line": 5, "type": "+", "content": 'STRIPE_KEY = "sk_live_abc123..."'},
            {"line": 10, "type": "+", "content": 'query = f"SELECT * FROM users WHERE id = {id}"'},
        ]
    )
]

# S2: Security findings
security_findings = [
    ReviewFinding(..., title="CWE-89: SQL Injection", ...),
]

# S3: Domain compliance findings
domains = loader.identify_domains(changes)  # ["payment-processing", "api-services"]
compliance_findings = validator.validate_changes(changes, code_content, domains)
# Returns: [
#   ReviewFinding(..., title="PAYMENT-001: Hardcoded API Key", ...),
# ]

# Combined: All findings aggregated
report = ReviewReport(
    pr_id="123",
    status="REJECTED",  # P0 issues found
    findings=[
        # S2 security findings
        security_findings[0],  # SQL injection
        # S3 compliance findings
        compliance_findings[0],  # Hardcoded key
    ],
    total_issues=2,
    critical_issues=2
)
```

---

## Example Compliance Rules

### Rule 1: Hardcoded Secrets
```yaml
id: "SEC-001"
name: "No Hardcoded Secrets"
severity: "P0_CRITICAL"
domains: ["*"]  # All domains
patterns:
  - '(api_key|secret|password)\s*=\s*["\'](?!.*\{)'
  - 'STRIPE_KEY\s*=\s*["\']'
  - 'AUTH_TOKEN\s*=\s*["\']'
fix_suggestion: "Use environment variables: KEY = os.getenv('STRIPE_KEY')"
```

### Rule 2: REST API Naming
```yaml
id: "API-001"
name: "REST Endpoint Naming Convention"
severity: "P1_HIGH"
domains: ["api-services"]
applies_to: "*.py"  # Python files
pattern: '@app.route\(["\']([^"\']+)'
validation: "Must follow /api/v1/resource/action pattern"
fix_suggestion: "@app.route('/api/v1/payments/create')"
```

### Rule 3: Database Naming
```yaml
id: "DB-001"
name: "Database Table Naming Convention"
severity: "P1_HIGH"
domains: ["database-standards"]
applies_to: "*.sql"  # SQL files
pattern: 'CREATE TABLE\s+(\w+)'
validation: "Table names must be lowercase with underscores: user_accounts, order_items"
fix_suggestion: "Rename table to follow snake_case convention"
```

---

## Testing Strategy

### Unit Tests (20 total)
- **Domain Loader (5 tests):** File-to-domain mapping accuracy
- **Compliance Validator (6 tests):** Rule matching and application
- **Rule Patterns (5 tests):** Pattern detection accuracy
- **Violation Reports (4 tests):** Report generation and clarity

### Integration Tests (via existing S1+S2)
- Verify S1→S2→S3 data flow
- Test with realistic PRs
- Validate multi-domain scenarios

### Coverage Target
- >90% code coverage
- All edge cases handled
- False positive rate <5%

---

## Continuation Context

**Recent Commits:**
```
450b25cbb AC-PHASE48-S2-001: Implement SecurityReviewEngine ✅
c2b188407 AC-PHASE48-S1-001: Implement GitDiffParser ✅
11ace04e8 AC-AUDIT-2026-02-09-001: Fix CORE-013 violations ✅
```

**Active Branch:** CORTEX (on local, pushed to origin)

**Next Steps After Approval:**
1. Create S3 test file: `test_phase48_s3_domain_loader.py`
2. Create S3 implementation: `company_domain_loader.py`
3. Follow TDD: write tests first, implement after
4. Run tests: `pytest tests/unit/orchestrators/code_review/ -v`
5. Commit: `AC-PHASE48-S3-001: Implement CompanyDomainLoader`

---

## Decision Required

**Ready to proceed with Phase 48-S3 implementation?**

Options:
1. **`proceed`** (Recommended) - Start S3 immediately
2. **`plan`** - Create detailed execution plan first
3. **`questions`** - Ask clarifications
4. **`review-s1-s2`** - Review S1+S2 code before S3
5. **`other`** - Different request

**Recommendation:** `proceed` - S1+S2 complete and tested, dependencies satisfied ✅

---

**Total Session Progress:**
- 🟢 Audit: Complete (P0/P1/P2 fixed, 11 commits)
- 🟢 Phase 48-S1: Complete (15/15 tests, 1 commit)
- 🟢 Phase 48-S2: Complete (13/13 tests, 1 commit)
- 🟡 Phase 48-S3: Ready for approval (20 tests planned)
- 📊 **Total Phase 48 Progress:** 28/28 tests passing ✅ + 2 commits
