# PHASE 20: LENS + Company Knowledge — Quick Reference
**Authority:** AC-LENS-COMPANY-001 | **Status:** APPROVED | **Date:** 2026-02-02

---

## 🎯 What We're Building

**One-Liner:** Selective LENS integration with company domain knowledge, cached and intent-aware.

**Problem:** LENS has git/AST/comment intelligence but no company context or compliance awareness.

**Solution:** LENSContextProvider service that:
- ✅ Activates only for IMPLEMENT/FIX/REFACTOR/ANALYZE intents
- ✅ Loads company/domains YAMLs with precedence (Company > CORTEX)
- ✅ Caches results for 5 minutes (200ms → <10ms)
- ✅ Detects PCI-DSS/HIPAA/SOC2 violations automatically
- ✅ Fails gracefully if LENS unavailable

---

## 📐 Architecture at a Glance

```
User Request
    ↓
MasterOrchestrator.execute_operation()
    ↓
Stage 1: Comprehension (InteractionOrchestrator)
    ↓
Stage 2: Intent Classification (IntentRouter)
    ↓
    IF intent IN [IMPLEMENT, FIX, REFACTOR, ANALYZE]
    AND file_path provided
    THEN:
        LENSContextProvider.get_context(file_path, company_name)
            ↓
        [Cache Check] → [Hit: <10ms] → Return cached
            ↓ Miss
        LENSOrchestrator.analyze_with_company_knowledge()
            ├─ Git History (GitHistoryAnalyzer)
            ├─ AST Analysis (ASTAnalyzer)
            ├─ Comments (CommentExtractor)
            ├─ Company Knowledge (CompanyKnowledgeLoader)
            └─ Compliance Detection (Auto-detect PCI/HIPAA/SOC2)
            ↓
        Merge into LENSContext
            ↓
        Cache (5-min TTL)
            ↓
        Return to IntentRouter
    ↓
Stage 3: Governance validation (with company rules)
    ↓
Stage 4: Execution (company-aware)
```

---

## 🧩 Components

| Component | File | Purpose |
|-----------|------|---------|
| **LENSContextProvider** | `cortex/orchestrators/core/lens_context_provider.py` | Service for selective LENS + company knowledge |
| **LENSCache** | Same file | 5-minute TTL cache with LRU eviction |
| **LENSOrchestrator** | `cortex/lens/orchestrator.py` | Enhanced with `analyze_with_company_knowledge()` |
| **IntentRouter** | `cortex/orchestrators/core/intent_router.py` | Auto-fetch LENS when missing |
| **MasterOrchestrator** | `cortex/orchestrators/core/master_orchestrator.py` | Stage 2 LENS injection |

---

## 📊 LENS Context Structure (Enhanced)

```yaml
lens_context:
  # Existing fields
  git_analysis:
    commits: []
    change_patterns: []
    hotspots: []
    
  ast_analysis:
    functions: []
    classes: []
    complexity: 0
    dead_code: []
    
  comment_analysis:
    todos: []
    fixmes: []
    docstrings: []
  
  # NEW: Company knowledge
  company_knowledge:
    domains:
      - name: "FINANCIAL-SERVICES"
        rules: [...]
        patterns: [...]
        precedence: "OVERRIDE"
  
  # NEW: Compliance detection
  compliance_flags:
    detected_standards:
      - standard_id: "PCI-DSS-3.2.1"
        confidence: 0.85
        violations:
          - line: 42
            message: "Unencrypted credit card storage"
  
  # NEW: Precedence tracking
  knowledge_precedence:
    company_overrides: 3
    cortex_base: 12
    compliance_standards: ["PCI-DSS-3.2.1", "SOC2"]
  
  _metadata:
    analysis_time_ms: 187
    cache_hit: false
    company_name: "acme-corp"
```

---

## 🔄 Request Flow Example

### Scenario: User asks to implement payment processing

```python
# 1. User request
request = "Implement payment processing with Stripe"

# 2. MasterOrchestrator receives
master.execute_operation(
    operation_name="implement",
    parameters={"request": request, "file_path": "payment.py"}
)

# 3. Stage 2: Intent classification
intent = intent_router.classify_intent(request)
# → IntentType.IMPLEMENT

# 4. LENS activation check
if intent in [IMPLEMENT, FIX, REFACTOR, ANALYZE]:
    # 5. Fetch LENS context
    lens_context = lens_provider.get_context(
        file_path="payment.py",
        company_name="acme-corp"
    )
    
    # 6. Cache check
    if cache.has("payment.py:acme-corp"):
        return cache.get(...)  # <10ms
    
    # 7. Cache miss - full analysis
    lens_result = lens_orchestrator.analyze_file("payment.py")
    company_knowledge = company_loader.get_merged_knowledge("SECURITY")
    compliance = company_loader.detect_compliance_standards(code)
    
    # 8. Merge
    lens_context = LENSContext(
        git_analysis=lens_result.git,
        ast_analysis=lens_result.ast,
        comment_analysis=lens_result.comments,
        company_knowledge=company_knowledge,
        compliance_flags=compliance
    )
    
    # 9. Cache for 5 minutes
    cache.set("payment.py:acme-corp", lens_context, ttl=300)

# 10. IntentRouter enhancement
decision = intent_router._enhance_with_lens(decision, lens_context)
# → Confidence boost: 0.75 → 0.85 (company rule match)
# → Compliance flag: PCI-DSS violation detected

# 11. Governance validation (with company rules)
governance.validate(decision, lens_context.company_knowledge)

# 12. Execution (company-aware)
result = tdd_orchestrator.execute(
    parameters={
        "target": "payment_processing",
        "lens_context": lens_context  # Includes company rules
    }
)
```

---

## ✅ Acceptance Criteria Summary

| AC ID | Title | Test Count |
|-------|-------|------------|
| **AC-LENS-COMPANY-001** | LENSContextProvider Service | 15 tests |
| **AC-LENS-COMPANY-002** | Company Knowledge Integration | 12 tests |
| **AC-LENS-COMPANY-003** | IntentRouter Auto-Fetch | 10 tests |
| **AC-LENS-COMPANY-004** | MasterOrchestrator Integration | 8 tests |
| **AC-LENS-COMPANY-005** | Performance and Caching | 12 tests |
| **Total** | | **57 tests** |

---

## 🧪 Test Files (TDD Order)

```
tests/
  unit/
    orchestrators/
      core/
        test_lens_context_provider.py       # 15 tests (Phase 1)
    lens/
      test_company_knowledge_integration.py # 12 tests (Phase 2)
    orchestrators/
      intent/
        test_lens_auto_fetch.py             # 10 tests (Phase 3)
  integration/
    test_master_orchestrator_lens_integration.py  # 8 tests (Phase 4)
    test_lens_company_e2e.py                     # 12 tests (Phase 5)
```

---

## 🎯 Implementation Order (TDD)

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| **Phase 1** | Day 1 | LENSContextProvider + Cache (15 tests passing) |
| **Phase 2** | Day 2 | Company knowledge in LENS (12 tests passing) |
| **Phase 3** | Day 3 | IntentRouter auto-fetch (10 tests passing) |
| **Phase 4** | Day 3 | MasterOrchestrator wiring (8 tests passing) |
| **Phase 5** | Day 4 | E2E integration (12 tests passing) |

---

## ⚡ Performance Targets

| Metric | Target | Current (Before) |
|--------|--------|------------------|
| Cache hit latency | <10ms | N/A |
| Cache miss (LENS only) | <500ms | 500ms |
| Cache miss (LENS + company) | <200ms | N/A |
| Cache hit rate | >80% | N/A |
| Memory usage | <100MB | N/A |

---

## 🛡️ Security Checklist

- [x] File path sanitization (prevent path traversal)
- [x] Company name validation (alphanumeric + hyphen only)
- [x] No secrets in LENS context
- [x] Rate limiting via cache (max 100 entries)
- [x] Fail-safe fallback (continue without LENS)
- [x] Audit trail logging (all LENS invocations)

---

## 🚨 Edge Cases

| Case | Behavior | Test |
|------|----------|------|
| File not in git | Skip git analysis | `test_lens_context_provider_non_git_file` |
| Binary file | Skip AST analysis | `test_lens_context_provider_binary_file` |
| LENS unavailable | Log warning, continue | `test_lens_context_provider_failsafe` |
| Cache stale | Invalidate, refresh | `test_cache_invalidation_on_modification` |
| No company set | CORTEX base only | `test_lens_context_no_company` |
| Rule conflict | Company overrides | `test_knowledge_precedence_conflict` |

---

## 📝 Configuration

```yaml
# cortex/config/lens_config.yaml (NEW FILE)
cache:
  enabled: true
  ttl_seconds: 300  # 5 minutes
  max_entries: 100
  max_size_mb: 100

activation:
  intents: ["IMPLEMENT", "FIX", "REFACTOR", "ANALYZE"]
  require_file_path: true

company_knowledge:
  enabled: true
  domains_path: "company/domains"

performance:
  timeout_ms: 500
  enable_metrics: true
```

---

## 🔗 MCP Tool Updates

```python
@mcp_tool(
    name="cortex_lens_analyze",
    description="Unified LENS analysis with company knowledge",
    parameters={
        "file_path": "string",
        "repo_path": "string",
        "company_name": "string (optional)",  # NEW
        "include_git": "boolean",
        "include_ast": "boolean",
        "include_comments": "boolean",
        "include_company_knowledge": "boolean (default: true)",  # NEW
    }
)
def cortex_lens_analyze(..., company_name=None):
    """Enhanced with company knowledge support."""
    # Auto-fetch company knowledge if company_name provided
    pass
```

---

## 🎓 Usage Examples

### Example 1: Auto LENS Injection (Transparent)

```python
# Before (user doesn't need to change anything)
master.execute_operation(
    operation_name="implement",
    parameters={"target": "payment_feature", "file_path": "payment.py"}
)

# LENS automatically injected in Stage 2
# Company knowledge loaded from company/domains/acme-corp/
# Compliance detection runs automatically
# Result includes company rule citations
```

### Example 2: Explicit LENS Request

```python
# Request LENS analysis with company knowledge
lens_context = lens_provider.get_context(
    file_path="payment.py",
    company_name="acme-corp"
)

print(f"Company rules: {len(lens_context.company_knowledge['rules'])}")
print(f"Compliance flags: {lens_context.compliance_flags}")
```

### Example 3: Company Knowledge Precedence

```python
# CORTEX base: "Use bcrypt for passwords"
# Company override: "Use Argon2id for passwords (company policy)"

# Result: Company rule takes precedence
merged_knowledge = knowledge_repo.get_merged_knowledge_with_overrides(
    domain="SECURITY",
    code_content="def hash_password(pwd): ..."
)

# merged_knowledge["password_hashing"] → "Argon2id" (company wins)
```

---

## 📚 Documentation Updates

| File | Update |
|------|--------|
| `docs/05-lens-protocol/06-company-knowledge-integration.md` | **NEW** — Full integration guide |
| `docs/02-orchestrators/01-master-orchestrator.md` | Document Stage 2 LENS injection |
| `docs/02-orchestrators/03-intent-router.md` | Document auto-fetch behavior |

---

## 🚀 Rollout Strategy

```yaml
Phase 1: Development (Days 1-4)
  - Implement all 5 phases
  - 57 tests passing
  - Performance benchmarks met

Phase 2: Validation (Day 5)
  - Full test suite
  - Security audit
  - Performance validation

Phase 3: Canary Deployment
  - Deploy with lens_enabled=False
  - Enable for 10% of requests
  - Monitor metrics (latency, errors)
  - Increase to 50% if healthy
  - Full rollout if no issues

Rollback Plan:
  - Trigger: Performance >20% degradation OR error rate >5%
  - Action: Set lens_enabled=False globally
  - Recovery: Investigate, fix, redeploy
```

---

## 📊 Success Metrics

| Metric | Target |
|--------|--------|
| Adoption rate | >80% of IMPLEMENT intents |
| Company knowledge usage | >50% of analyses |
| Compliance detection accuracy | >90% of violations caught |
| Average latency | <100ms (with cache) |
| Cache hit rate | >80% |
| Production incidents | Zero |

---

## 🔮 Future Enhancements (Phase 21+)

| Enhancement | Benefit |
|-------------|---------|
| **Batch Analysis** | Analyze multiple files in one call |
| **Async Loading** | Non-blocking LENS with progress updates |
| **ML Compliance** | LLM-enhanced compliance detection |
| **LENS Dashboard** | Analytics and optimization insights |

---

## 🎯 Quick Commands

```bash
# Run all LENS + company knowledge tests
pytest tests/unit/orchestrators/core/test_lens_context_provider.py -v
pytest tests/unit/lens/test_company_knowledge_integration.py -v
pytest tests/integration/test_lens_company_e2e.py -v

# Check performance benchmarks
pytest tests/integration/test_lens_company_e2e.py::test_cache_performance -v

# Verify company knowledge loading
python -c "
from cortex.brain.core.knowledge.company_knowledge_loader import CompanyKnowledgeLoader
loader = CompanyKnowledgeLoader()
knowledge = loader.get_merged_knowledge('SECURITY')
print(f'Loaded {len(knowledge)} security rules')
"

# Clear LENS cache
python -c "
from cortex.orchestrators.core.lens_context_provider import LENSContextProvider
provider = LENSContextProvider()
provider.cache.clear()
print('Cache cleared')
"
```

---

## ✅ Completion Checklist

- [ ] 57 tests written and passing (TDD)
- [ ] Test coverage >95%
- [ ] Performance benchmarks met
- [ ] Security audit passed
- [ ] Documentation complete
- [ ] Wiring.yaml updated
- [ ] MCP tools enhanced
- [ ] E2E tests passing
- [ ] Backward compatibility verified
- [ ] Edge cases handled
- [ ] Fail-safe mechanisms tested
- [ ] Audit trail logging verified

---

**Status:** Ready for implementation (approved 2026-02-02)  
**Estimated Duration:** 5 days  
**Total Tests:** 57  
**Risk Level:** Medium (mitigated with caching and fail-safe)

---

*For full details, see [PHASE-20-LENS-COMPANY-INTEGRATION.yaml](./PHASE-20-LENS-COMPANY-INTEGRATION.yaml)*
