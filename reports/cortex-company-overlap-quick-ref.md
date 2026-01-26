# CORTEX + Company Rules Overlap - Quick Reference Guide

**Purpose:** Understanding and using the validated rule overlap framework

---

## 🚀 Quick Start

### View Test Results
```bash
cd /Users/asifhussain/PROJECTS/CORTEX

# Run all validation tests (13/13 passing)
./.venv/bin/python -m pytest tests/test_cortex_company_overlap.py -v

# Run specific test
./.venv/bin/python -m pytest tests/test_cortex_company_overlap.py::TestCORTEXCompanyOverlap::test_rule_overlap_detection -v
```

### View Reports
```bash
# Executive summary (2-minute read)
cat reports/executive-summary-cortex-company-overlap.md

# Detailed analysis (10-minute read)
cat reports/cortex-company-overlap-analysis.md

# Comprehensive findings (30-minute read)
cat reports/test-cortex-company-overlap-validation-report.md
```

---

## 📋 Domain Rules Quick Reference

### Financial Domain (FIN-*)
```yaml
FIN-001: Transaction Audit Trail
  Severity: CRITICAL
  Applies: tdd, impl
  Overlap: CORE-008 (TDD) - 65%
  
FIN-002: Amount Validation
  Severity: CRITICAL
  Applies: test, impl
  Overlap: CORE-008 (TDD) - 60%
  
FIN-003: Type Hints
  Severity: HIGH
  Applies: impl, refactor
  Overlap: CORE-011 (Types) - 95%
```

### Security Domain (SEC-*)
```yaml
SEC-001: Input Sanitization
  Severity: CRITICAL
  Applies: impl, test, tdd
  Overlap: None (complementary)
  
SEC-002: Exception Handling
  Severity: HIGH
  Applies: impl, refactor
  Overlap: CORE-013 (Exceptions) - 85%
  
SEC-003: Secrets Management
  Severity: CRITICAL
  Applies: impl
  Overlap: None (complementary)
```

### Performance Domain (PERF-*)
```yaml
PERF-001: Database Indexing
  Severity: HIGH
  Applies: impl, test, refactor
  Overlap: None (complementary)
  
PERF-002: Caching Strategy
  Severity: MEDIUM
  Applies: impl, refactor
  Overlap: PERF-CACHE-001 - 80%
  
PERF-003: Avoid N+1 Queries
  Severity: HIGH
  Applies: impl, test
  Overlap: None (complementary)
```

---

## 🔍 CORTEX Rules Quick Reference

### Tier 0 Immutable (Always Enforced)
```yaml
CORE-008: TDD (RED → GREEN → REFACTOR)
CORE-011: Type Hints MANDATORY
CORE-012: Docstrings (Google style)
CORE-013: No Bare Except Clauses
```

### Tier 1 Domain Rules
```yaml
ARCH-001: SOLID Principles
```

### Tier 3 Knowledge
```yaml
PERF-CACHE-001: Caching Strategies
TEST-DOUBLES-001: Mock Pattern
```

---

## 📊 Key Statistics

| Metric | Value |
|--------|-------|
| Company Rules | 9 (3 domains) |
| CORTEX Rules | 8 (Tier 0-3) |
| Overlaps | 6 mapped rules |
| Coverage | 67%+ |
| Conflicts | 0 (zero) |
| Test Pass Rate | 13/13 (100%) |
| Execution Time | 0.04s |

---

## 💻 Using the Framework

### Create Company Rules
```python
from tests.test_cortex_company_overlap import CompanyRule, RuleSeverity

rule = CompanyRule(
    rule_id="FIN-001",
    domain="financial",
    description="All transactions must have audit trail",
    severity=RuleSeverity.CRITICAL,
    applies_to=["tdd", "impl"]
)
```

### Detect Overlaps
```python
from tests.test_cortex_company_overlap import RuleOverlapValidator

validator = RuleOverlapValidator()
overlaps = validator.validate(company_rules, cortex_rules)

print(f"Coverage: {overlaps.coverage_percentage}%")
print(f"Conflicts: {overlaps.conflicts_found}")
```

### Validate Code
```python
from tests.test_cortex_company_overlap import MergedRuleEnforcer

enforcer = MergedRuleEnforcer(company_rules, cortex_rules)
result = enforcer.validate_code_for_domain("financial", code, "impl")

print(f"Compliant: {result['is_compliant']}")
print(f"Score: {result['compliance_score']}")
print(f"Violations: {result['violations']}")
```

---

## 🎯 Compliance Scoring Guide

### Score Interpretation
```
1.0     : Perfect compliance
0.85+   : Excellent (pass with minor notes)
0.70+   : Good (pass with review)
0.50+   : Fair (remediation needed)
< 0.50  : Fail (blocking issues)
```

### Deduction Table
```
Tier 0 Violation:    -0.30 (CRITICAL - blocks code)
Company Violation:   -0.15 (HIGH - requires fix)
Tier 3 Violation:    -0.05 (LOW - suggestion)
```

### Violation Examples
```
CORE-008 (TDD):     "No test code detected" (-0.30)
CORE-011 (Types):   "Missing return type hint" (-0.30)
CORE-013 (Except):  "Bare except clause found" (-0.30)
FIN-001 (Audit):    "No audit trail created" (-0.15)
FIN-002 (Valid):    "Validation missing" (-0.15)
PERF-001 (Index):   "Consider using indexes" (-0.05)
```

---

## 🔧 Integration Checklist

### For TDD Orchestrator Integration
- [ ] Load `MergedRuleEnforcer` class
- [ ] Import company rules from YAML
- [ ] Call `validate_code_for_domain()` in code generation
- [ ] Include compliance score in output
- [ ] Log violations to audit trail
- [ ] Report compliance metrics

### For Company Rules Extension
- [ ] Define new domain (e.g., "compliance", "devops")
- [ ] Create 3-5 rules per domain
- [ ] Assign severity levels (CRITICAL/HIGH/MEDIUM/LOW)
- [ ] Map context (tdd/test/impl/refactor)
- [ ] Test with `RuleOverlapValidator`
- [ ] Document in company rules YAML

### For Production Deployment
- [ ] Run test suite (target: 13/13 passing)
- [ ] Review compliance reports
- [ ] Test with staging code
- [ ] Monitor violation patterns
- [ ] Adjust thresholds if needed
- [ ] Deploy to production

---

## 📂 File Locations

### Test Code
```
tests/test_cortex_company_overlap.py          [Main test framework]
```

### Reports
```
reports/executive-summary-...md               [2-minute summary]
reports/cortex-company-overlap-analysis.md    [Detailed findings]
reports/test-cortex-company-...report.md      [Comprehensive analysis]
reports/cortex-company-overlap-quick-ref.md   [This file]
```

### CORTEX Knowledge (Source Rules)
```
cortex_brain/tier0/governance/                [Tier 0 rules]
cortex_brain/tier1/domain-rules/              [Tier 1 rules]
cortex_brain/tier3/knowledge/                 [Tier 3 knowledge]
```

---

## 🐛 Troubleshooting

### Tests Not Running
```bash
# Ensure venv is activated
cd /Users/asifhussain/PROJECTS/CORTEX
source .venv/bin/activate

# Run tests
python -m pytest tests/test_cortex_company_overlap.py -v
```

### Import Errors
```python
# Ensure working from project root
import sys
sys.path.insert(0, '/Users/asifhussain/PROJECTS/CORTEX')

# Then import
from tests.test_cortex_company_overlap import CompanyRule
```

### Compliance Score Too Low
```
1. Check for Tier 0 violations (CORE-* rules)
2. Check for company domain violations
3. Review specific violation messages
4. Use error messages to fix code
5. Re-run validation
```

---

## 📞 Quick Command Reference

```bash
# Run all tests
pytest tests/test_cortex_company_overlap.py -v

# Run specific test
pytest tests/test_cortex_company_overlap.py::test_rule_overlap_detection -v

# Run with coverage
pytest tests/test_cortex_company_overlap.py --cov=. -v

# Run and show output
pytest tests/test_cortex_company_overlap.py -v -s

# Run and stop on first failure
pytest tests/test_cortex_company_overlap.py -x

# List available tests
pytest tests/test_cortex_company_overlap.py --collect-only
```

---

## 🎓 Learning Resources

### Understanding Rule Overlap
Read: `reports/cortex-company-overlap-analysis.md`
Section: "Rule Overlap Detection"

### Understanding Compliance Scoring
Read: `reports/test-cortex-company-overlap-validation-report.md`
Section: "Compliance Scoring Methodology"

### Implementation Examples
Read: `tests/test_cortex_company_overlap.py`
Section: "Code Validation Examples"

### Integration Guide
Read: `reports/cortex-company-overlap-analysis.md`
Section: "Production Recommendations"

---

## ✅ Validation Checklist

Before using in production:

- [ ] All 13 tests passing (run: `pytest tests/test_cortex_company_overlap.py -v`)
- [ ] Reviewed executive summary (`reports/executive-summary-...md`)
- [ ] Reviewed compliance scoring guide (this document)
- [ ] Tested with sample code
- [ ] Verified TDD enforcement working
- [ ] Verified domain-specific rules working
- [ ] Verified conflict detection (should be 0)

---

## 🎉 Success Criteria

Your implementation is successful if:

✅ All company domain rules are enforced
✅ All CORTEX Tier 0 rules are enforced
✅ No conflicts detected between rule sets
✅ Compliance score 0.70+ for compliant code
✅ Compliance score < 0.50 for non-compliant code
✅ Clear violation messages provided
✅ Integration with TDD Orchestrator working

---

**Last Updated:** January 26, 2026  
**Framework Status:** Production Ready  
**Test Status:** 13/13 Passing
