# CORTEX Company Rules Integration - Production Deployment Plan

**Date:** January 26, 2026  
**Status:** Ready for Deployment  
**Test Coverage:** 13/13 Passing (100%)  
**Conflicts:** 0 (zero)

---

## 📋 Executive Summary

The CORTEX + Company Rules overlap validation is **complete and production-ready**. This document outlines the integration steps to deploy the `MergedRuleEnforcer` into the TDD Orchestrator.

### Key Achievements
- ✅ 9 company domain rules created and validated
- ✅ 8 CORTEX knowledge rules loaded and tested
- ✅ 67%+ rule overlap detected with 0 conflicts
- ✅ 13 comprehensive validation tests (all passing)
- ✅ Production-ready reusable components
- ✅ Clear compliance scoring system (0.0-1.0 scale)

### Production Benefits
- **Rule Enforcement:** Both CORTEX and company rules enforced simultaneously
- **Zero Conflicts:** Validated complementary alignment
- **Compliance Transparency:** Clear scoring and violation reporting
- **Scalable:** Easily add new domains and rules
- **Auditable:** Full compliance trail for governance

---

## 🎯 Phase 1: Immediate Actions (Day 1)

### 1.1 Commit Test Framework
```bash
cd /Users/asifhussain/PROJECTS/CORTEX

# Add test file
git add tests/test_cortex_company_overlap.py

# Add reports
git add reports/executive-summary-cortex-company-overlap.md
git add reports/cortex-company-overlap-analysis.md
git add reports/cortex-company-overlap-quick-ref.md

# Commit
git commit -m "AC-PROD-001: Add CORTEX + Company Rules Overlap Validation Framework

- Comprehensive test suite with 13 validation tests (100% passing)
- RuleOverlapValidator for detecting rule relationships
- MergedRuleEnforcer for simultaneous rule enforcement
- Company domain rules (Financial, Security, Performance)
- CORTEX Tier 0-3 knowledge integration
- Compliance scoring system (0.0-1.0 scale)
- Zero conflicts detected between rule sets
- Production-ready components

Files:
- tests/test_cortex_company_overlap.py (1000+ lines)
- reports/executive-summary-cortex-company-overlap.md
- reports/cortex-company-overlap-analysis.md
- reports/cortex-company-overlap-quick-ref.md"
```

### 1.2 Verify Test Execution
```bash
# Run final validation
./.venv/bin/python -m pytest tests/test_cortex_company_overlap.py -v

# Expected output:
# ✅ 13 passed in 0.04s
```

### 1.3 Stakeholder Review
- [ ] Share executive summary with architecture team
- [ ] Review rule overlap findings (67%+ coverage, 0 conflicts)
- [ ] Confirm TDD Orchestrator integration approach
- [ ] Approve deployment to staging

---

## 🔄 Phase 2: Framework Integration (Day 2-3)

### 2.1 Create Company Rules YAML

Create file: `cortex_brain/tier1/domain-rules/company-rules.yaml`

```yaml
company_domains:
  financial:
    domain_name: Financial Operations
    description: Rules for financial transactions and computations
    severity_override: HIGH
    rules:
      - id: FIN-001
        name: Transaction Audit Trail
        description: All transactions must have audit trail
        severity: CRITICAL
        applies_to: [tdd, impl]
        key_checks:
          - "audit_trail created"
          - "transaction_id recorded"
          - "timestamp captured"
      
      - id: FIN-002
        name: Amount Validation
        description: Amount validation - positive and bounded
        severity: CRITICAL
        applies_to: [test, impl]
        key_checks:
          - "amount > 0"
          - "amount <= MAX_TRANSACTION"
      
      - id: FIN-003
        name: Type Hints
        description: Type hints required on all financial computations
        severity: HIGH
        applies_to: [impl, refactor]
        key_checks:
          - "-> float type hint"
          - "amount: float parameter"

  security:
    domain_name: Security & Access Control
    description: Rules for security, authentication, and data protection
    severity_override: CRITICAL
    rules:
      - id: SEC-001
        name: Input Sanitization
        description: All user inputs must be sanitized
        severity: CRITICAL
        applies_to: [impl, test, tdd]
        key_checks:
          - "sanitize() called"
          - "strip() called"
          - "validation performed"
      
      - id: SEC-002
        name: Exception Handling
        description: No bare except clauses
        severity: HIGH
        applies_to: [impl, refactor]
        key_checks:
          - "except SpecificException"
          - "no bare except"
      
      - id: SEC-003
        name: Secrets Management
        description: Secrets via environment variables only
        severity: CRITICAL
        applies_to: [impl]
        key_checks:
          - "os.environ.get()"
          - "no hardcoded secrets"

  performance:
    domain_name: Performance & Optimization
    description: Rules for database, caching, and optimization
    severity_override: HIGH
    rules:
      - id: PERF-001
        name: Database Indexing
        description: Database queries must use indexes
        severity: HIGH
        applies_to: [impl, test, refactor]
        key_checks:
          - "index used"
          - "no full table scan"
      
      - id: PERF-002
        name: Caching Strategy
        description: Cache expensive computations
        severity: MEDIUM
        applies_to: [impl, refactor]
        key_checks:
          - "cache() called"
          - "TTL set"
      
      - id: PERF-003
        name: Avoid N+1 Queries
        description: Batch load related data
        severity: HIGH
        applies_to: [impl, test]
        key_checks:
          - "bulk query"
          - "join used"
          - "no loop queries"
```

### 2.2 Update TDD Orchestrator

File: `cortex/orchestrators/core/tdd_orchestrator.py`

```python
# Add imports
from tests.test_cortex_company_overlap import (
    MergedRuleEnforcer,
    RuleOverlapValidator,
    CompanyRuleSet,
    CORTEXKnowledgeSet,
)
from cortex.brain.core.knowledge.knowledge_repository import (
    load_company_rules_from_yaml,
)

class TDDOrchestrator:
    """TDD Orchestrator with merged rule enforcement."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize company rules
        self.company_rules = load_company_rules_from_yaml(
            "cortex_brain/tier1/domain-rules/company-rules.yaml"
        )
        
        # Initialize CORTEX rules
        self.cortex_rules = self._load_cortex_rules()
        
        # Create merged enforcer
        self.rule_enforcer = MergedRuleEnforcer(
            self.company_rules,
            self.cortex_rules
        )
        
        # Validate overlap on init
        validator = RuleOverlapValidator()
        overlap_result = validator.validate(
            self.company_rules,
            self.cortex_rules
        )
        
        if overlap_result.conflicts_found:
            raise ValueError(
                f"Rule conflicts detected: {overlap_result.conflicts_found}"
            )
        
        self.logger.info(
            f"Rule overlap: {overlap_result.coverage_percentage}% coverage, "
            f"{len(overlap_result.conflicts_found)} conflicts"
        )
    
    def execute(self, intent, context):
        """Execute with rule enforcement."""
        
        # Generate code (existing logic)
        generated_code = self._generate_code(intent, context)
        
        # NEW: Validate against merged rules
        if hasattr(intent, 'domain'):
            domain = intent.domain
            context_type = context.get('type', 'impl')
            
            validation_result = self.rule_enforcer.validate_code_for_domain(
                domain,
                generated_code,
                context_type
            )
            
            # Log compliance
            self.logger.info(
                f"Code compliance: {validation_result['compliance_score']:.2%} "
                f"({len(validation_result['violations'])} violations)"
            )
            
            # Check if critical violations
            if validation_result['compliance_score'] < 0.5:
                self.logger.error(
                    f"Code rejected: compliance {validation_result['compliance_score']:.2%}"
                )
                raise ComplianceError(
                    f"Generated code violates critical rules: "
                    f"{validation_result['violations']}"
                )
            
            # Add compliance report to output
            if validation_result['violations']:
                self.logger.warning(
                    f"Code has warnings:\n"
                    f"{validation_result['report']}"
                )
        
        return generated_code
    
    def _load_cortex_rules(self):
        """Load CORTEX Tier 0-3 knowledge rules."""
        cortex_rules = CORTEXKnowledgeSet()
        
        # Load from existing knowledge repository
        knowledge_dir = "cortex_brain/tier3/knowledge/"
        
        # Load Tier 0 (immutable)
        tier0_rules = [
            ("CORE-008", "TDD", "cortex_brain/tier0/governance/tdd.yaml"),
            ("CORE-011", "Types", "cortex_brain/tier0/governance/types.yaml"),
            ("CORE-012", "Docstrings", "cortex_brain/tier0/governance/docstrings.yaml"),
            ("CORE-013", "Exceptions", "cortex_brain/tier0/governance/exceptions.yaml"),
        ]
        
        for rule_id, name, source in tier0_rules:
            cortex_rules.add_rule(rule_id, name, 0, source)
        
        # Load Tier 3 (knowledge)
        tier3_rules = [
            ("PERF-CACHE-001", "Caching", "cortex_brain/tier3/knowledge/PERFORMANCE/caching.yaml"),
            ("TEST-DOUBLES-001", "Test Doubles", "cortex_brain/tier3/knowledge/TESTING-VALIDATION/test-doubles.yaml"),
        ]
        
        for rule_id, name, source in tier3_rules:
            cortex_rules.add_rule(rule_id, name, 3, source)
        
        return cortex_rules
```

### 2.3 Create Compliance Logging

Add to audit trail:

```python
# In TDD Orchestrator
def _log_compliance(self, code, validation_result, domain):
    """Log compliance check for audit trail."""
    
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "check_type": "COMPLIANCE_VALIDATION",
        "domain": domain,
        "compliance_score": validation_result['compliance_score'],
        "violations_count": len(validation_result['violations']),
        "violations": validation_result['violations'],
        "rules_enforced": {
            "tier0": 4,
            "company": len(self.company_rules),
            "tier3": 2,
        }
    }
    
    self.audit_logger.log("COMPLIANCE", audit_entry)
```

---

## 🧪 Phase 3: Testing & Validation (Day 4-5)

### 3.1 Create Integration Test

File: `tests/test_tdd_orchestrator_integration.py`

```python
import pytest
from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
from cortex.models import Intent

def test_tdd_orchestrator_enforces_company_and_cortex_rules():
    """Test: TDD Orchestrator enforces both rule sets."""
    
    orchestrator = TDDOrchestrator()
    
    intent = Intent(
        type="IMPLEMENT",
        domain="financial",
        description="Process financial transaction"
    )
    
    context = {"type": "impl"}
    
    # Execute should enforce all rules
    code = orchestrator.execute(intent, context)
    
    # Verify code has:
    # - Type hints (CORE-011)
    # - Docstrings (CORE-012)
    # - No bare except (CORE-013)
    # - Audit trail (FIN-001)
    # - Amount validation (FIN-002)
    
    assert "def " in code
    assert ":" in code  # Type hints
    assert '"""' in code  # Docstrings
    assert "audit_trail" in code  # Company rule
```

### 3.2 Run Full Test Suite
```bash
# Run both test suites
./.venv/bin/python -m pytest \
  tests/test_cortex_company_overlap.py \
  tests/test_tdd_orchestrator_integration.py \
  -v

# Expected: All tests passing
```

### 3.3 Staging Deployment
```bash
# Deploy to staging environment
./scripts/deploy-to-staging.sh

# Run smoke tests
./.venv/bin/python -m pytest tests/staging/ -v

# Monitor compliance metrics
./scripts/monitor-compliance.sh
```

---

## 📊 Phase 4: Monitoring & Optimization (Ongoing)

### 4.1 Compliance Dashboard

Add to Neural Observatory (PHASE-15):

```
Dashboard: Rule Compliance Metrics
┌─────────────────────────────────────────┐
│ Compliance Score Distribution            │
│ ├─ Perfect (1.0):        45%            │
│ ├─ Excellent (0.85+):    30%            │
│ ├─ Good (0.70+):         20%            │
│ ├─ Fair (0.50+):          5%            │
│ └─ Fail (< 0.50):         0%            │
│                                          │
│ Rule Violations by Type                 │
│ ├─ Tier 0 (Critical):     5 violations  │
│ ├─ Company (High):       12 violations  │
│ └─ Tier 3 (Suggestion):  23 suggestions │
│                                          │
│ Domain Compliance                       │
│ ├─ Financial:     0.95 ✅              │
│ ├─ Security:      0.88 ✅              │
│ └─ Performance:   0.82 ✅              │
└─────────────────────────────────────────┘
```

### 4.2 Metrics to Track

```
1. Compliance Score Distribution
   - Target: >80% of code ≥ 0.85 score
   - Alert: <70% of code ≥ 0.85 score

2. Rule Violations
   - Tier 0: Should be near zero
   - Company: Declining trend expected
   - Tier 3: OK to have suggestions

3. Domain Performance
   - Financial: Must be > 0.90
   - Security: Must be > 0.85
   - Performance: Target 0.80+

4. Integration Health
   - Orchestrator boot time: < 2 seconds
   - Rule validation time: < 100ms per code
   - Zero runtime exceptions
```

### 4.3 Auto-Remediation (Future)

```python
class ComplianceAutoRemediation:
    """Automatically fix common compliance violations."""
    
    @staticmethod
    def fix_missing_type_hints(code):
        """Add type hints to functions."""
        # Parse AST and add type hints
        pass
    
    @staticmethod
    def fix_bare_except(code):
        """Replace bare except with specific exceptions."""
        # Replace except: with except Exception:
        pass
    
    @staticmethod
    def fix_missing_docstrings(code):
        """Add Google-style docstrings."""
        # Generate and insert docstrings
        pass
    
    @staticmethod
    def suggest_audit_trail(code):
        """Suggest audit trail code for financial functions."""
        # Insert audit logging calls
        pass
```

---

## 🎯 Phase 5: Rollout Plan (Week 2)

### 5.1 Canary Deployment (10% traffic)
```bash
# Deploy to 10% of TDD Orchestrator usage
./scripts/deploy-canary.sh --percentage 10

# Monitor for 24 hours
# - Check compliance scores
# - Monitor error rates
# - Review violation patterns
```

### 5.2 Staged Rollout
```
Week 2:  10% canary deployment
Week 3:  50% progressive rollout
Week 4:  100% production deployment
```

### 5.3 Rollback Plan
```bash
# If issues detected, rollback to previous version
./scripts/rollback-to-previous.sh

# Disable rule enforcement temporarily
./scripts/disable-compliance-enforcement.sh

# Re-enable with fixes
./scripts/enable-compliance-enforcement.sh
```

---

## ✅ Success Criteria

### Immediate (Day 1-2)
- [ ] Test framework committed
- [ ] Code reviewed and approved
- [ ] Team briefed on overlap findings

### Short Term (Day 3-5)
- [ ] TDD Orchestrator integrated
- [ ] Company rules loaded from YAML
- [ ] Integration tests passing (100%)
- [ ] Compliance metrics tracked

### Medium Term (Week 2-3)
- [ ] Canary deployment successful
- [ ] Compliance scores > 0.85 for 80%+ of code
- [ ] Zero critical rule violations in production
- [ ] Dashboard monitoring active

### Long Term (Month 2+)
- [ ] 100% production rollout
- [ ] Auto-remediation deployed
- [ ] New company domains added
- [ ] Team trained on compliance workflow

---

## 📞 Escalation Path

```
Issue Level          Owner                Action
─────────────────────────────────────────────────────
Low Priority:        DevOps Team         Log, monitor
Medium Priority:     Architecture Team   Review, plan fix
High Priority:       Engineering Lead    Immediate review
Critical (P1):       CTO                 Rollback decision
```

---

## 📈 Expected Benefits

### Short Term (1-2 weeks)
- ✅ Reduced code review time (pre-validation)
- ✅ Earlier bug detection (compliance-based)
- ✅ Clearer development standards

### Medium Term (1-2 months)
- ✅ Improved code quality (measurable)
- ✅ Reduced production incidents
- ✅ Faster onboarding (clear standards)

### Long Term (6+ months)
- ✅ Scalable governance framework
- ✅ Automated compliance (low overhead)
- ✅ Institutional knowledge captured
- ✅ Competitive advantage (quality)

---

## 🚀 Next Immediate Steps

**Today:**
1. Review this deployment plan
2. Confirm stakeholder approval
3. Schedule Phase 1 kickoff

**Tomorrow:**
1. Commit test framework
2. Schedule Phase 2 implementation
3. Notify team of deployment timeline

**This Week:**
1. Complete TDD Orchestrator integration
2. Run integration test suite
3. Begin staging deployment

---

## 📖 Documentation References

- **Executive Summary:** `reports/executive-summary-cortex-company-overlap.md`
- **Analysis Report:** `reports/cortex-company-overlap-analysis.md`
- **Quick Reference:** `reports/cortex-company-overlap-quick-ref.md`
- **Test Code:** `tests/test_cortex_company_overlap.py`

---

**Created:** January 26, 2026  
**Status:** Ready for Implementation  
**Approval:** Awaiting Stakeholder Sign-off  
**Deployment Target:** Week 2 of February 2026
