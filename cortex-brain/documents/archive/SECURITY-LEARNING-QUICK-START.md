# Security Learning Agent - Quick Start Guide

**Status:** 🟢 APPROVED for CORTEX 4.0  
**Start Date:** Week 4 (Current: Week 7)  
**Integration:** Phase 2 (Brain) + Phase 3 (Orchestrators)

---

## 🎯 What This Is

The Security Learning Agent adds **proactive security enforcement** to CORTEX by:
1. Learning from OWASP, CWE, NVD, compliance standards
2. Auto-detecting user's tech stack
3. Validating code during planning, development, and QA
4. Suggesting security test patterns
5. Checking compliance (PCI, HIPAA, GDPR)

**Competitive Advantage:** First AI coding assistant with compliance-aware orchestration.

---

## 📅 Implementation Schedule

### Week 4: Foundation (12 hours)
**Goal:** Security patterns database schema + tech stack profiler

**Tasks:**
- [ ] Create `cortex-brain/tier2/rag_stores/security_patterns.db` schema
- [ ] Create `cortex-brain/tier2/rag_stores/tech_stack_patterns.db` schema
- [ ] Create `cortex-brain/tier2/rag_stores/compliance_rules.db` schema
- [ ] Implement `TechStackProfiler` class
- [ ] Write 10 unit tests

**Deliverables:**
```
cortex-brain/tier2/rag_stores/
├── security_patterns.db (schema only)
├── tech_stack_patterns.db (schema only)
└── compliance_rules.db (schema only)

src/operations/utilities/
└── tech_stack_profiler.py (300 LOC)

tests/utilities/
└── test_tech_stack_profiler.py (10 tests)
```

---

### Week 6: OWASP Integration (8 hours)
**Goal:** Load OWASP Top 10 data + search API

**Tasks:**
- [ ] Download OWASP Top 10 2021 JSON
- [ ] Parse and load into `security_patterns` table
- [ ] Map to code examples (vulnerable vs. secure)
- [ ] Reuse RAG semantic search infrastructure
- [ ] Write 10 unit tests

**Deliverables:**
- 200+ security patterns loaded
- Search API operational
- Query by OWASP ID, CWE ID, category, severity

---

### Week 7: CWE + Compliance (6 hours)
**Goal:** Load CWE database + compliance rules

**Tasks:**
- [ ] Download CWE Top 25
- [ ] Cross-reference with OWASP patterns
- [ ] Load PCI-DSS/HIPAA/GDPR requirements
- [ ] User-configurable enable/disable
- [ ] Write 5 unit tests

**Deliverables:**
- CWE Top 25 integrated
- Compliance rules loaded (disabled by default)

---

### Week 8: Agent Implementation (2 hours)
**Goal:** SecurityLearningAgent core class

**Tasks:**
- [ ] Create `src/cortex_agents/security_learning_agent.py`
- [ ] Implement validation API
- [ ] Connect to Tier 2 security stores
- [ ] DI container integration
- [ ] Write 15 unit tests

**Deliverables:**
```python
SecurityLearningAgent:
  - is_available() -> bool
  - profile_tech_stack() -> Dict
  - validate_security() -> List[Violation]
  - get_security_test_patterns() -> List[str]
  - check_compliance() -> Dict
```

---

### Week 8: Planning Orchestrator Integration (2 hours)
**Goal:** Add security DoR checks (conditional)

**Tasks:**
- [ ] Add `_check_security_requirements()` to PlanningOrchestrator
- [ ] Conditional execution (only if SecurityAgent available)
- [ ] Update DoR validation logic
- [ ] Write 5 integration tests

**Code Change:**
```python
def validate_dor(self, plan):
    checks = [
        self._check_acceptance_criteria(),
        self._check_test_strategy(),
    ]
    
    if SecurityLearningAgent.is_available():
        checks.append(self._check_security_requirements())
    
    return all(checks)
```

---

### Week 10: QA + TDD Orchestrator Integration (6 hours)
**Goal:** Security audit phase + security test suggestions

**Tasks:**
- [ ] Add `run_security_audit()` to QAOrchestrator
- [ ] Add security test patterns to TDDOrchestrator
- [ ] Update SKULL rules (security enforcement)
- [ ] Write 10 integration tests

**Deliverables:**
- QA orchestrator runs OWASP checks
- TDD suggests SQL injection, XSS, auth tests
- SKULL enforces security patterns

---

## 🔧 Key Files to Create/Modify

### New Files (7 total)
```
cortex-brain/tier2/rag_stores/
├── security_patterns.db
├── tech_stack_patterns.db
└── compliance_rules.db

src/cortex_agents/
└── security_learning_agent.py (800 LOC)

src/operations/utilities/
└── tech_stack_profiler.py (300 LOC)

tests/agents/
└── test_security_learning_agent.py (30 tests)

tests/utilities/
└── test_tech_stack_profiler.py (10 tests)
```

### Modified Files (4 total)
```
cortex-brain/brain-protection-rules.yaml (add SECURITY_FIRST_ENFORCEMENT)
src/orchestrators/planning_orchestrator_v2.py (add DoR security check)
src/orchestrators/qa_orchestrator.py (add security audit phase)
src/orchestrators/tdd_orchestrator.py (add security test patterns)
```

---

## 🧪 Testing Checklist

### Unit Tests (30 tests)
- [ ] Tech stack profiler detects Python frameworks
- [ ] Tech stack profiler detects JavaScript frameworks
- [ ] Tech stack profiler detects Java frameworks
- [ ] Security agent detects SQL injection
- [ ] Security agent detects XSS vulnerabilities
- [ ] Security agent suggests auth tests
- [ ] Compliance checker validates PCI-DSS
- [ ] Graceful degradation when DB missing

### Integration Tests (15 tests)
- [ ] PlanningOrchestrator uses security checks
- [ ] QA orchestrator runs security audit
- [ ] TDD orchestrator suggests security tests
- [ ] SKULL enforces security rules
- [ ] End-to-end workflow with security validation

---

## 📊 Success Metrics

### Phase 2 (Week 8 End)
- [ ] 200+ security patterns loaded
- [ ] 10+ frameworks detected
- [ ] 30/30 unit tests passing
- [ ] <100ms search response time

### Phase 3 (Week 13 End)
- [ ] Planning rejects insecure plans (auth/data features)
- [ ] QA audit finds vulnerabilities
- [ ] TDD suggests 3+ security tests per feature
- [ ] 15/15 integration tests passing
- [ ] <5% false positive rate

---

## ⚠️ Important Notes

1. **Parallel Work:** All security work runs alongside RAG implementation
2. **Conditional Execution:** Security checks only run if Phase 2 complete
3. **Graceful Degradation:** Orchestrators work without security agent
4. **No Timeline Impact:** 40 hours spread over 10 weeks = 4 hours/week average
5. **Auto-Update Deferred:** Self-learning pipeline is Phase 6 (optional)

---

## 🚀 Getting Started (Week 4)

### Step 1: Create DB Schema
```bash
cd cortex-brain/tier2/rag_stores
sqlite3 security_patterns.db < schema.sql
```

### Step 2: Implement Tech Stack Profiler
```bash
cd src/operations/utilities
touch tech_stack_profiler.py
# Implement TechStackProfiler class
```

### Step 3: Write Tests
```bash
cd tests/utilities
touch test_tech_stack_profiler.py
pytest tests/utilities/test_tech_stack_profiler.py
```

---

## 📚 Documentation References

- **Full Integration Spec:** `SECURITY-LEARNING-INTEGRATION-SPEC.md`
- **Approval Summary:** `SECURITY-LEARNING-AGENT-APPROVAL.md`
- **Master Plan:** `MASTER-PLAN.md` (updated with security milestones)
- **Feasibility Report:** Chat conversation Dec 18, 2025

---

## 🎯 Next Action (RIGHT NOW)

**Start Week 4 work:**
1. Create security patterns DB schema file
2. Set up directory structure
3. Implement TechStackProfiler skeleton
4. Write first 5 unit tests

**Command:**
```bash
# Create directory structure
mkdir -p cortex-brain/tier2/rag_stores
mkdir -p src/operations/utilities
mkdir -p tests/utilities

# Create schema file
touch cortex-brain/tier2/rag_stores/security_patterns_schema.sql
```

---

**Status:** 🟢 Ready to begin implementation (Week 4 onwards)
