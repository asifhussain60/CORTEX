# PHASE 20.5: Knowledge Synthesis — Quick Reference
**Authority:** AC-KNOWLEDGE-SYNTHESIS-001 | **Status:** APPROVED | **Date:** 2026-02-02  
**Dependency:** PHASE-20 (LENS + Company Knowledge)

---

## 🎯 What We're Building

**One-Liner:** Wire 45+ CORTEX best practices YAMLs into MasterOrchestrator for active synthesis during decision-making.

**Problem:**
- KnowledgeRepository exists but underutilized (passive access)
- Engineers get no proactive guidance during implementation
- Violations caught AFTER execution (too late)
- LENS and Knowledge operate in silos

**Solution:**
- Active knowledge synthesis at Stage 2 (Intent Classification)
- Unified Intelligence Context (LENS + Company + CORTEX)
- Smart citations in routing decisions
- Early violation prevention (not detection)

---

## 🏗️ Architecture: Before vs After

### Before (Phase 20):
```
Stage 2:
  ├─ Intent Classification
  ├─ LENS Context (git, AST, comments)
  └─ Company Knowledge (domains, compliance)

Knowledge Repository (Separate):
  └─ 45+ best practices YAMLs (passive)
  
Problem: Knowledge loaded but not applied
```

### After (Phase 20.5):
```
Stage 2:
  ├─ Intent Classification
  ├─ LENS Context
  ├─ Company Knowledge
  ├─ CORTEX Knowledge (45+ YAMLs) ← NEW
  └─ Synthesis Engine ← NEW
      ├─ Merge all 3 sources
      ├─ Apply precedence (Company > CORTEX)
      ├─ Generate citations
      ├─ Detect violations early
      └─ Create proactive guidance

Unified Intelligence Context:
  ├─ All sources merged
  ├─ Rule citations
  ├─ Violation flags
  └─ Engineer guidance
```

---

## 📊 Unified Intelligence Context

```yaml
UnifiedIntelligenceContext:
  # Phase 20: LENS + Company
  lens:
    git_analysis: {...}
    ast_analysis: {...}
    comment_analysis: {...}
  
  company:
    domain_rules: [...]
    compliance_standards: [...]
    precedence: "OVERRIDE"
  
  # Phase 20.5: CORTEX Knowledge (NEW)
  cortex_knowledge:
    best_practices: [...]  # From 45+ YAMLs
    applicable_patterns: [...]
    anti_patterns: [...]
    domains: ["SECURITY", "ARCHITECTURE", ...]
  
  # Phase 20.5: Synthesis Result (NEW)
  synthesis:
    merged_rules: [...]
    citations: [
      "ACME-SECURITY-001: Use Argon2id (company policy)",
      "SECURITY-042: CORTEX recommends bcrypt/Argon2id",
      "PCI-DSS-3.2.1: Strong cryptography required"
    ]
    violations: [...]
    guidance: [
      "✅ Use Argon2id for password hashing",
      "✅ Implement JWT tokens with refresh",
      "⚠️  Consider 2FA implementation"
    ]
```

---

## 🔄 Request Flow Example

### Scenario: Engineer implements password authentication

```python
# User request
"Implement user authentication with password storage"

# Stage 2: Intelligence Gathering

# 1. LENS Context (Phase 20)
lens_context = lens_provider.get_context("auth.py")
# → Git: Recent changes to auth.py
# → AST: High complexity (15)
# → Comments: TODO: Implement 2FA

# 2. Company Knowledge (Phase 20)
company_knowledge = company_loader.get_merged_knowledge("SECURITY")
# → ACME-SECURITY-001: Use Argon2id (OVERRIDE)
# → PCI-DSS-3.2.1: Strong cryptography required

# 3. CORTEX Knowledge (Phase 20.5 NEW)
cortex_knowledge = knowledge_repo.get_relevant_knowledge(
    intent="IMPLEMENT",
    domain="SECURITY",
    keywords=["authentication", "password"]
)
# → SECURITY-042: Password hashing best practices
# → ARCHITECTURE-023: JWT authentication pattern
# → SECURITY-ANTI-001: Never plain text passwords

# 4. Synthesis (Phase 20.5 NEW)
unified_context = synthesis_engine.synthesize_intelligence(
    lens=lens_context,
    company=company_knowledge,
    cortex=cortex_knowledge,
    intent="IMPLEMENT"
)

# Result:
unified_context.synthesis.citations = [
    "ACME-SECURITY-001: Use Argon2id (company policy)",
    "SECURITY-042: CORTEX recommends bcrypt/Argon2id",
    "PCI-DSS-3.2.1: Strong cryptography required",
    "ARCHITECTURE-023: Use JWT with refresh tokens"
]

unified_context.synthesis.guidance = [
    "✅ Use Argon2id for password hashing (company policy)",
    "✅ Implement JWT tokens with refresh mechanism",
    "⚠️  Consider implementing 2FA (TODO already exists)",
    "✅ PCI-DSS compliant approach detected"
]

# 5. Enhanced Routing Decision
decision = intent_router._enhance_with_intelligence(
    decision,
    unified_context
)
# → Confidence: 0.92 (high - knowledge + LENS align)
# → Citations: 4 rules cited
# → Violations: 0 blocking, 1 warning (2FA)
# → Guidance: 4 proactive suggestions
```

---

## 💡 Engineer Benefits

### Before Phase 20.5:
```
Engineer: "Implement password authentication"

System:
  ❌ No guidance during planning
  ❌ Violations caught in Stage 4 (after writing code)
  ❌ Must remember all 45+ best practices
  ❌ Company rules hidden until governance check

Engineer:
  ⏰ Writes code with bcrypt
  ⏰ Governance fails: "Company requires Argon2id"
  ⏰ Rewrites code (15 minutes wasted)
```

### After Phase 20.5:
```
Engineer: "Implement password authentication"

System (Stage 2):
  ✅ "Use Argon2id (company policy - ACME-SECURITY-001)"
  ✅ "Implement JWT with refresh (ARCHITECTURE-023)"
  ✅ "Consider 2FA (TODO exists in auth.py)"
  ✅ "PCI-DSS compliance required"

Engineer:
  ✅ Implements Argon2id from the start
  ✅ Adds JWT refresh mechanism
  ✅ Notes 2FA for follow-up
  ✅ Zero violations, governance passes
  ⏱️  Saved 15 minutes
```

---

## 🧩 Components

| Component | File | Purpose |
|-----------|------|---------|
| **UnifiedIntelligenceContext** | `cortex/brain/knowledge/unified_intelligence_context.py` | Single source of truth |
| **KnowledgeSynthesisEngine** | `cortex/brain/knowledge/knowledge_synthesis_engine.py` | Merges all knowledge |
| **KnowledgeRepository** | `cortex/brain/core/knowledge/knowledge_repository.py` | CORTEX knowledge loading (enhanced) |
| **MasterOrchestrator** | `cortex/orchestrators/core/master_orchestrator.py` | Stage 2 synthesis invocation |
| **IntentRouter** | `cortex/orchestrators/core/intent_router.py` | Smart citations in decisions |

---

## ✅ Acceptance Criteria

| AC ID | Title | Tests |
|-------|-------|-------|
| **AC-KNOWLEDGE-SYNTHESIS-001** | Synthesis Engine Integration | 12 tests |
| **AC-KNOWLEDGE-SYNTHESIS-002** | CORTEX Knowledge Loading | 10 tests |
| **AC-KNOWLEDGE-SYNTHESIS-003** | Smart Citations | 8 tests |
| **AC-KNOWLEDGE-SYNTHESIS-004** | Early Violation Prevention | 10 tests |
| **AC-KNOWLEDGE-SYNTHESIS-005** | Proactive Guidance | 8 tests |
| **Total** | | **48 tests** |

---

## 🧪 Test Files (TDD Order)

```
tests/
  unit/
    brain/
      knowledge/
        test_unified_intelligence_context.py       # 8 tests (Phase 1)
        test_knowledge_repository_enhancement.py   # 10 tests (Phase 2)
        test_synthesis_engine_integration.py       # 12 tests (Phase 3)
  integration/
    test_master_orchestrator_knowledge_synthesis.py  # 10 tests (Phase 4)
  unit/
    orchestrators/
      intent/
        test_intent_router_citations.py            # 8 tests (Phase 5)
  integration/
    test_knowledge_synthesis_e2e.py                # 15 tests (Phase 6)
```

**Total:** 63 tests

---

## 🎯 Implementation Timeline

| Day | Phase | Deliverable |
|-----|-------|-------------|
| **1** | Context + CORTEX Loading | UnifiedIntelligenceContext + enhanced KnowledgeRepository (18 tests) |
| **2** | Synthesis Engine | Integration + precedence resolution (12 tests) |
| **3** | Orchestrator Wiring | MasterOrchestrator + IntentRouter (18 tests) |
| **4** | E2E Integration | Full flow testing (15 tests) |

**Total Duration:** 4 days  
**Total Tests:** 63  
**Dependency:** PHASE-20 complete

---

## ⚡ Performance Impact

| Metric | Current | With Phase 20.5 | Impact |
|--------|---------|-----------------|--------|
| Stage 2 Latency | ~200ms | ~300ms | +50% |
| CORTEX Knowledge Load | N/A | <50ms (cached) | Cached |
| Synthesis | N/A | <40ms | Minimal |
| Total Addition | N/A | ~100ms | Acceptable |

**Trade-off:** +50% latency for 10x better decisions

---

## 🛡️ Precedence Rules

```yaml
Conflict Resolution:
  1. Company Rules (HIGHEST)
     Example: "ACME-SECURITY-001: Use Argon2id"
     
  2. CORTEX Best Practices (MEDIUM)
     Example: "SECURITY-042: Use bcrypt or Argon2id"
     
  3. LENS Evidence (INFORMATIONAL)
     Example: "Git history shows bcrypt usage"

Result:
  Company rule OVERRIDES CORTEX recommendation
  Final decision: "Use Argon2id (company policy)"
  Citation: Both sources cited, company precedence noted
```

---

## 📝 Citation Format

```yaml
Smart Citation Example:
  Rule ID: "ACME-SECURITY-001"
  Source: "Company Policy"
  Precedence: "OVERRIDE"
  Content: "All passwords MUST use Argon2id"
  
Display:
  "ACME-SECURITY-001: Use Argon2id (company policy)"
  
In Routing Decision:
  citations:
    - "ACME-SECURITY-001: Use Argon2id (company policy)"
    - "SECURITY-042: CORTEX recommends bcrypt/Argon2id"
    - "PCI-DSS-3.2.1: Strong cryptography required"
```

---

## 🚨 Violation Prevention

### Before (Detection):
```
Stage 4 (Execution):
  Engineer writes code with bare except
  Governance detects violation
  Execution blocked
  Engineer rewrites code
```

### After (Prevention):
```
Stage 2 (Intent Classification):
  Synthesis engine detects potential bare except
  BLOCKING violation flagged
  Citation: "CORE-013: No bare except clauses"
  Guidance: "Use specific exception types"
  Engineer fixes BEFORE writing code
```

---

## 🎓 Usage Examples

### Example 1: Proactive Guidance

```python
# Engineer request
request = "Implement payment processing"

# Stage 2 synthesis provides guidance BEFORE execution
unified_context.synthesis.guidance = [
    "✅ Use PCI-DSS compliant payment gateway",
    "✅ Never store CVV (PCI-DSS-3.2.1)",
    "✅ Implement retry logic (ARCHITECTURE-015)",
    "⚠️  Consider tokenization (ACME-FINANCE-003)"
]

# Engineer sees guidance in routing decision
# Implements correctly from the start
# Zero violations
```

### Example 2: Company Precedence

```python
# Conflict: CORTEX says "bcrypt", Company says "Argon2id"

synthesis_result = synthesis_engine.synthesize_intelligence(...)

# Precedence resolution:
synthesis_result.merged_rules = [
    {
        "id": "MERGED-001",
        "rule": "Use Argon2id for password hashing",
        "sources": [
            {"id": "ACME-SECURITY-001", "precedence": "OVERRIDE"},
            {"id": "SECURITY-042", "precedence": "BASE", "note": "overridden"}
        ],
        "final_rule": "Argon2id (company precedence)"
    }
]

# Result: Company rule wins, both cited
```

---

## 📊 Success Metrics

| Metric | Target |
|--------|--------|
| Knowledge synthesis adoption | >90% of IMPLEMENT intents |
| Smart citations displayed | >95% of routing decisions |
| Violations prevented (vs detected) | >80% |
| Engineer satisfaction | >85% rate guidance helpful |
| CORE rule violations reduction | >60% decrease |
| Company policy compliance | >95% |

---

## 🔗 Integration Points

```yaml
MasterOrchestrator.execute_operation():
  Stage 1: Comprehension
  Stage 2: Intent Classification
    ├─ IntentRouter.classify_intent()
    ├─ LENSContextProvider.get_context() [Phase 20]
    ├─ KnowledgeRepository.get_relevant_knowledge() [Phase 20.5 NEW]
    └─ KnowledgeSynthesisEngine.synthesize() [Phase 20.5 NEW]
        └─ Returns UnifiedIntelligenceContext
  Stage 3: Governance (with synthesized knowledge)
  Stage 4: Execution (with full context)
```

---

## 🚀 Quick Commands

```bash
# Run all knowledge synthesis tests
pytest tests/unit/brain/knowledge/test_unified_intelligence_context.py -v
pytest tests/unit/brain/knowledge/test_synthesis_engine_integration.py -v
pytest tests/integration/test_knowledge_synthesis_e2e.py -v

# Verify CORTEX knowledge loading
python -c "
from cortex.brain.core.knowledge.knowledge_repository import KnowledgeRepository
repo = KnowledgeRepository()
knowledge = repo.get_relevant_knowledge(
    intent='IMPLEMENT',
    domain='SECURITY',
    keywords=['authentication']
)
print(f'Loaded {len(knowledge)} applicable practices')
"

# Test synthesis engine
python -c "
from cortex.brain.knowledge.knowledge_synthesis_engine import KnowledgeSynthesisEngine
engine = KnowledgeSynthesisEngine()
# ... test synthesis
"
```

---

## ✅ Completion Checklist

- [ ] 63 tests written and passing (TDD)
- [ ] UnifiedIntelligenceContext dataclass
- [ ] KnowledgeRepository.get_relevant_knowledge()
- [ ] KnowledgeSynthesisEngine integration
- [ ] MasterOrchestrator Stage 2 wiring
- [ ] IntentRouter smart citations
- [ ] Early violation detection
- [ ] Proactive guidance generation
- [ ] E2E tests passing
- [ ] Performance benchmarks met
- [ ] Documentation complete

---

**Status:** Ready for implementation after Phase 20  
**Dependency:** PHASE-20 (LENS + Company Knowledge)  
**Duration:** 4 days  
**Tests:** 63  
**Impact:** 10x better engineer decisions, +50% latency (acceptable)

---

*For full details, see [PHASE-20.5-KNOWLEDGE-SYNTHESIS.yaml](./PHASE-20.5-KNOWLEDGE-SYNTHESIS.yaml)*
