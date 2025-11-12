# CORTEX Drift Prevention & Gap Closure Plan

**Date:** 2025-11-10  
**Status:** 🚨 IMPLEMENTATION HALT - Drift Remediation  
**Authority:** TRUTH-SOURCES.yaml enforcement

---

## 🎯 Critical Decision: STOP & FIX FIRST

**Rationale:** Building more features on unstable foundation creates exponential technical debt.

**Discovered Gaps:**
1. 🔴 **560 failing tests** (73.6% pass rate vs >95% target)
2. 🔴 **Knowledge graph dormant** (0 SQLite patterns, 32 YAML patterns)
3. 🟡 **Documentation sprawl** (100+ files, unclear truth source)
4. 🟡 **Dual storage confusion** (JSONL vs SQLite in Tier 1)

---

## 📋 Gap Closure Roadmap

### Phase 1: Establish Truth Authority (DONE ✅)

**Duration:** 2 hours  
**Status:** COMPLETE

**Deliverables:**
- [x] `TRUTH-SOURCES.yaml` - Single source registry
- [x] `.github/hooks/pre-commit-drift-check.py` - Pre-commit validation
- [x] `scripts/migrate_knowledge_patterns.py` - KG migration tool
- [x] `.github/workflows/drift-detection.yml` - CI enforcement

**Outcome:** Framework for preventing future drift in place.

---

### Phase 2: Test Suite Triage & Stabilization (PRIORITY 1)

**Duration:** 8-12 hours  
**Status:** NOT STARTED

**Target:** >95% pass rate (2,040+ passing out of 2,147)

**Approach:**
```
1. Categorize Failures (1 hour)
   - Import errors
   - Fixture issues
   - Assertion failures
   - Integration breakages

2. Fix Blockers (4-6 hours)
   - Critical path test failures
   - Fixture/conftest issues
   - Import errors

3. Fix Integration Tests (3-4 hours)
   - API mismatches
   - Database schema issues
   - Module interface changes

4. Verify & Document (1 hour)
   - Full test suite run
   - Update test count in docs
   - SKULL-001 compliance verified
```

**Success Criteria:**
- ✅ >2,040 tests passing (95%+)
- ✅ No import errors
- ✅ All critical path tests green
- ✅ CI pipeline passes

**Blocker:** Cannot claim ANY feature complete until this is done.

---

### Phase 3: Knowledge Graph Activation (PRIORITY 2)

**Duration:** 4-6 hours  
**Status:** SCRIPT READY, NOT EXECUTED

**Steps:**
```
1. Run Migration (30 minutes)
   python scripts/migrate_knowledge_patterns.py
   - Migrates 32 YAML patterns → SQLite
   - Creates backup
   - Verifies FTS working

2. Integrate with Agent Router (2-3 hours)
   - Add pattern matching to intent router
   - "Similar problem" detection
   - Pattern confidence scoring

3. Test Pattern Retrieval (1 hour)
   - Verify patterns accessible
   - Test FTS queries
   - Validate confidence decay

4. Enable Learning Loop (2 hours)
   - Extract patterns from conversations
   - Auto-populate knowledge graph
   - Test continuous learning
```

**Success Criteria:**
- ✅ 32+ patterns in SQLite
- ✅ FTS queries working
- ✅ Agent router uses patterns
- ✅ New patterns accumulate automatically

---

### Phase 4: Documentation Consolidation (PRIORITY 3)

**Duration:** 6-8 hours  
**Status:** PARTIAL (3 files archived)

**Remaining Work:**
```
1. Archive Historical Docs (1 hour)
   - 10-15 more Phase 2-4 docs → archive/
   - Keep only active references

2. Consolidate Status Tracking (3-4 hours)
   - status-data.yaml as single source
   - Generate STATUS.md + CORTEX2-STATUS.MD
   - Script: scripts/generate_status_docs.py

3. Update Cross-References (2 hours)
   - DOCUMENT-CROSS-REFERENCE-INDEX.md
   - Point all references to truth sources
   - Remove dead links

4. Validate Documentation Hierarchy (1 hour)
   - Tier 1: Entry points (CORTEX.prompt.md)
   - Tier 2: User guides (prompts/shared/*.md)
   - Tier 3: Architecture (CORTEX-UNIFIED-ARCHITECTURE.yaml)
   - Tier 4: Design docs (cortex-2.0-design/*.md)
   - Tier 5: API docs (generated)
```

**Success Criteria:**
- ✅ <50 active design docs (from 100+)
- ✅ TRUTH-SOURCES.yaml governs all references
- ✅ No conflicting claims between docs
- ✅ Clear documentation hierarchy

---

### Phase 5: Tier 1 Storage Strategy (PRIORITY 4)

**Duration:** 4-6 hours  
**Status:** NOT STARTED

**Decision Required:** Consolidate or document hybrid approach?

**Option A: Consolidate to JSONL**
- Remove SQLite conversations.db
- JSONL as single source
- Simpler, proven to work

**Option B: Consolidate to SQLite**
- Migrate JSONL → SQLite
- Better querying, performance
- More complex

**Option C: Document Hybrid (RECOMMENDED)**
- JSONL = primary (proven)
- SQLite = secondary (caching)
- Document strategy in TRUTH-SOURCES.yaml

**Success Criteria:**
- ✅ Clear strategy documented
- ✅ No confusion about which source to query
- ✅ Backup strategy in place

---

## 🛡️ Drift Prevention Mechanisms (ACTIVE)

### 1. Pre-Commit Hooks ✅
```bash
# Install hook
cp .github/hooks/pre-commit-drift-check.py .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Blocks commits if:**
- Module counts mismatch
- Status files updated individually
- Critical tests failing (optional, slow)

### 2. CI Validation ✅
**Workflow:** `.github/workflows/drift-detection.yml`

**Runs on:** Every push to CORTEX-2.0, main

**Checks:**
- Module count consistency
- Knowledge graph sync
- Status document sync
- Smoke test health

### 3. TRUTH-SOURCES.yaml ✅
**Authority:** Single registry of truth sources

**Enforces:**
- One authoritative source per domain
- Derived sources must update together
- Known drift tracked and remediated

### 4. Documentation Reviews
**Frequency:** Weekly during active development

**Agenda:**
- Check TRUTH-SOURCES.yaml for new drift
- Verify resolution log up to date
- Archive obsolete docs
- Update cross-reference index

---

## 📊 Success Metrics

### Before Remediation (2025-11-10)
- **Test Health:** 73.6% pass rate (560 failures)
- **Knowledge Graph:** 0 SQLite patterns, 32 YAML
- **Doc Sprawl:** 100+ design docs, 3 status files
- **Drift Awareness:** Low (manual checks)

### After Remediation (Target)
- **Test Health:** >95% pass rate (<110 failures)
- **Knowledge Graph:** 32+ SQLite patterns, learning active
- **Doc Sprawl:** <50 active docs, clear hierarchy
- **Drift Awareness:** High (automated checks)

---

## 🚀 Implementation Schedule

**Week 1 (Nov 11-15):**
- Day 1-3: Test suite triage & fix (Phase 2)
- Day 4: Knowledge graph migration (Phase 3, step 1-3)
- Day 5: Agent integration (Phase 3, step 4)

**Week 2 (Nov 18-22):**
- Day 1-2: Documentation consolidation (Phase 4)
- Day 3: Tier 1 strategy decision (Phase 5)
- Day 4-5: Validation & testing

**Week 3 (Nov 25-29):**
- Resume Phase 7 documentation work
- Resume Phase 8 deployment planning
- Continue with normal development

---

## 🎯 Definition of "Drift Resolved"

**Criteria for resuming feature development:**
1. ✅ Test pass rate >95%
2. ✅ Knowledge graph active (patterns in SQLite)
3. ✅ TRUTH-SOURCES.yaml enforced (CI + pre-commit)
4. ✅ <50 active design docs
5. ✅ All truth sources documented
6. ✅ Drift prevention mechanisms working

**Approval Authority:** Must pass ALL 6 criteria

---

## 💡 Lessons Learned

**What caused drift:**
1. **Rapid development** without truth enforcement
2. **Multiple storage approaches** tried in parallel
3. **Documentation-driven design** without implementation follow-through
4. **Test failures ignored** during feature rush

**How to prevent:**
1. **TRUTH-SOURCES.yaml** as contract
2. **Pre-commit hooks** catch issues early
3. **CI validation** prevents drift merge
4. **Weekly reviews** surface accumulating drift
5. **SKULL-001** enforcement (test before claim)

---

## 📖 Related Documents

- **TRUTH-SOURCES.yaml** - Authority registry
- **SKULL-PROTECTION-LAYER.md** - Quality gates
- **ARCHITECTURE-REVIEW-2025-11-10.md** - Gap analysis
- **CORTEX2-STATUS.MD** - Current phase status

---

**Status:** 🚨 IMPLEMENTATION HALT  
**Next Action:** Begin Phase 2 (Test Suite Triage)  
**Owner:** Windows Environment  
**ETA for Resume:** 2025-11-22 (2 weeks)

---

*"Fix the foundation before building the skyscraper."*
