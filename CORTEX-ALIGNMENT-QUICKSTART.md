# CORTEX Alignment - Quick Start Guide

**Date:** November 6, 2025  
**For:** Immediate execution of knowledge boundary implementation

---

## ⚡ TL;DR

**What:** Implement impenetrable boundaries between CORTEX and application knowledge  
**Why:** Currently no isolation - KSESSIONS patterns can contaminate CORTEX intelligence  
**How:** 8 phases, 28-36 hours, database-enforced scope + namespace system  
**Result:** 100% surgical amnesia, multi-app support, zero cross-contamination

---

## 🚀 Execute Now (Copy-Paste Ready)

### Step 1: Review & Prepare (15 minutes)

```bash
# 1. Read the executive summary
#file:CORTEX-ALIGNMENT-SUMMARY.md

# 2. Backup all BRAIN databases
cd d:\PROJECTS\CORTEX
mkdir -p cortex-brain/backups/pre-alignment-$(date +%Y%m%d)
cp cortex-brain/tier1/conversations.db cortex-brain/backups/pre-alignment-$(date +%Y%m%d)/
cp cortex-brain/tier2/knowledge_graph.db cortex-brain/backups/pre-alignment-$(date +%Y%m%d)/
cp cortex-brain/tier3/context.db cortex-brain/backups/pre-alignment-$(date +%Y%m%d)/

# 3. Create feature branch
git checkout -b feature/knowledge-boundaries

# 4. Verify test infrastructure
pytest --version
# If not installed: pip install pytest pytest-cov
```

### Step 2: Execute Phase 1 - Schema Migration (3-4 hours)

```markdown
#file:prompts/user/cortex.md

Execute CORTEX-ALIGNMENT-PLAN.md Phase 1:
- Create migrate_add_boundaries.py
- Add scope and namespaces columns to patterns table
- Classify existing patterns (generic vs application)
- Add 12 boundary validation tests
- Run migration on live database
```

**Success Criteria:**
- ✅ `scope` column exists with CHECK constraint
- ✅ `namespaces` column exists (JSON array)
- ✅ All existing patterns classified
- ✅ 12/12 tests passing

### Step 3: Execute Phase 2 - Boundary Enforcement (4-5 hours)

```markdown
#file:prompts/user/cortex.md

Execute CORTEX-ALIGNMENT-PLAN.md Phase 2:
- Update brain-updater.md with automatic scope detection
- Implement namespace-aware search in knowledge_graph.py
- Update context_injector.py for app detection
- Add 15 namespace search tests
```

**Success Criteria:**
- ✅ New patterns auto-tagged with correct scope/namespace
- ✅ Search queries boost current namespace patterns
- ✅ Generic patterns always included
- ✅ 15/15 tests passing

### Step 4: Execute Phase 3 - Brain Protector (4-6 hours)

```markdown
#file:prompts/user/cortex.md

Execute CORTEX-ALIGNMENT-PLAN.md Phase 3:
- Wire brain-protector.md into intent-router.md
- Create brain_protector.py with 6 protection layers
- Add corpus-callosum logging for challenges
- Implement 18 protection tests
```

**Success Criteria:**
- ✅ CORTEX modifications trigger Brain Protector
- ✅ TDD bypass attempts BLOCKED
- ✅ Tier boundary violations BLOCKED
- ✅ 18/18 tests passing

### Step 5: Execute Phase 4 - Cleanup Automation (6-8 hours)

```markdown
#file:prompts/user/cortex.md

Execute CORTEX-ALIGNMENT-PLAN.md Phase 4:
- Complete cleanup_hook.py (analyze_file, archive_file, decay, consolidation)
- Create cleanup_scheduler.py with auto-triggers
- Implement anomaly_detector.py for suspicious patterns
- Add 20 cleanup automation tests
```

**Success Criteria:**
- ✅ Pattern decay removes confidence <0.30
- ✅ Pattern consolidation merges 60-84% similar
- ✅ Auto-triggers after 50 events or 24 hours
- ✅ 20/20 tests passing

### Step 6: Execute Phase 5 - Enhanced Amnesia (2-3 hours)

```markdown
#file:prompts/user/cortex.md

Execute CORTEX-ALIGNMENT-PLAN.md Phase 5:
- Update brain-amnesia.md with scope-based deletion
- Update scripts/brain-amnesia.ps1 with SQLite operations
- Add namespace-specific amnesia option
- Implement 8 amnesia tests
```

**Success Criteria:**
- ✅ Amnesia uses `DELETE WHERE scope='application'`
- ✅ Generic patterns preserved
- ✅ Namespace-specific option works
- ✅ 8/8 tests passing

### Step 7: Execute Phase 6 - Testing & Validation (4-5 hours)

```markdown
#file:prompts/user/cortex.md

Execute CORTEX-ALIGNMENT-PLAN.md Phase 6:
- Create 12 integration tests for end-to-end boundary enforcement
- Run performance regression benchmarks
- Generate coverage report (target 95%+)
- Complete manual validation checklist
```

**Success Criteria:**
- ✅ 12/12 integration tests passing
- ✅ Search <150ms, scope overhead <5ms
- ✅ Coverage ≥95%
- ✅ Manual validation complete

### Step 8: Execute Phase 7 - Documentation (3-4 hours)

```markdown
#file:prompts/user/cortex.md

Execute CORTEX-ALIGNMENT-PLAN.md Phase 7:
- Update cortex.md with boundary documentation
- Create ALIGNMENT-IMPLEMENTATION.md summary
- Update Tier 2 README with namespace examples
- Create BOUNDARY-QUICK-REFERENCE.md
```

**Success Criteria:**
- ✅ cortex.md updated
- ✅ Implementation summary complete
- ✅ Quick reference with code examples
- ✅ All tier READMEs updated

### Step 9: Execute Phase 8 - Minor Fixes (2-3 hours)

```markdown
#file:prompts/user/cortex.md

Execute CORTEX-ALIGNMENT-PLAN.md Phase 8:
- Fix governance schema category constraints (uppercase→lowercase)
- Update test expectations (23→27 rules)
- Run KSESSIONS audit and cleanup
- Verify all stragglers complete
```

**Success Criteria:**
- ✅ Governance schema fixed
- ✅ 27/27 governance tests passing
- ✅ KSESSIONS audit complete
- ✅ Zero pending issues

### Step 10: Final Validation & Merge

```bash
# 1. Run full test suite
pytest CORTEX/tests/ -v --cov=CORTEX/src --cov-report=html

# Expected:
# - Total tests: 514 (409 existing + 105 new)
# - Pass rate: 100%
# - Coverage: ≥95%

# 2. Commit alignment implementation
git add .
git commit -m "feat(cortex): Implement knowledge boundary system with namespace isolation

- Add scope (generic/application) and namespaces columns to patterns table
- Implement automatic scope detection in brain-updater.md
- Wire Brain Protector into intent-router for architectural protection
- Complete cleanup automation with pattern decay and consolidation
- Enhance BRAIN amnesia with scope-based surgical deletion
- Add 105 tests for boundary enforcement (100% coverage)

BREAKING CHANGE: Patterns now require scope and namespaces for proper isolation.
Existing patterns auto-classified during migration.

Closes #[issue-number]"

# 3. Push and create merge request
git push origin feature/knowledge-boundaries

# 4. Update IMPLEMENTATION-PROGRESS.md
# Mark alignment phases complete
```

---

## 📋 Pre-Flight Checklist

Before starting Phase 1, verify:

- [ ] ✅ All 409 existing tests passing
- [ ] ✅ Database backups created
- [ ] ✅ Feature branch created
- [ ] ✅ pytest installed and working
- [ ] ✅ Read CORTEX-ALIGNMENT-SUMMARY.md
- [ ] ✅ Allocated 3.5-4.5 days for execution
- [ ] ✅ No critical production work blocking time

---

## 🎯 Quick Reference: What Each Phase Delivers

| Phase | Input | Output | Tests |
|-------|-------|--------|-------|
| **1** | Clean patterns table | + scope + namespaces columns | +12 |
| **2** | Manual tagging | → Automatic scope detection | +15 |
| **3** | No protection | → Brain Protector blocking violations | +18 |
| **4** | Manual cleanup | → Automatic pattern maintenance | +20 |
| **5** | Heuristic amnesia | → Scope-based surgical deletion | +8 |
| **6** | - | → Integration tests + benchmarks | +12 |
| **7** | Code only | → Documentation + user guides | - |
| **8** | Minor bugs | → All stragglers fixed | +20 |

**Total:** 105 new tests, 12 new files, 18 modified files

---

## ⚠️ If Something Goes Wrong

### Rollback Immediately

```bash
# 1. Restore database backup
cp cortex-brain/backups/pre-alignment-*/knowledge_graph.db \
   cortex-brain/tier2/knowledge_graph.db

# 2. Revert code changes
git reset --hard origin/cortex-migration

# 3. Verify rollback
pytest CORTEX/tests/tier0/ CORTEX/tests/tier1/ CORTEX/tests/tier2/ -v

# 4. Document failure
echo "Rollback reason: [describe issue]" >> alignment-rollback.log
```

### Common Issues

**Issue:** "no such column: scope"  
**Fix:** Run Phase 1 migration script first

**Issue:** "CHECK constraint failed"  
**Fix:** Verify scope value is 'generic' or 'application' (lowercase)

**Issue:** "namespace boost not working"  
**Fix:** Check namespace JSON format: `["CORTEX-core"]` not `"CORTEX-core"`

**Issue:** "Brain Protector not triggering"  
**Fix:** Verify intent-router.md detects CORTEX modification patterns

---

## 📊 Progress Tracking

### Daily Updates

Update IMPLEMENTATION-PROGRESS.md after each phase:

```markdown
## CORTEX Alignment Progress

**Date:** [Today]
**Phases Complete:** [N/8]
**Tests Passing:** [409 + completed tests]
**Current Phase:** [Phase name]
**Blockers:** [None / List]
**ETA:** [Days remaining]
```

### Milestones

**Milestone 1: Boundary System Live** (After Phase 2)
- [ ] Schema migrated
- [ ] Auto-tagging working
- [ ] Namespace search operational
- [ ] 27 tests added

**Milestone 2: Protection Active** (After Phase 4)
- [ ] Brain Protector integrated
- [ ] Cleanup automation running
- [ ] 38 additional tests added

**Milestone 3: Production Ready** (After Phase 8)
- [ ] Enhanced amnesia operational
- [ ] All 105 tests passing
- [ ] Documentation complete
- [ ] Zero pending issues

---

## 🎉 Success Criteria (Final)

### Code Quality
- [x] 105 new tests written
- [x] All tests passing (514/514)
- [x] Coverage ≥95%
- [x] No linting errors
- [x] All files documented

### Functionality
- [x] Scope/namespaces columns exist
- [x] Auto-tagging operational
- [x] Namespace search working
- [x] Brain Protector blocking violations
- [x] Cleanup automation running
- [x] Amnesia scope-based

### Performance
- [x] Search <150ms
- [x] Scope overhead <5ms
- [x] Pattern decay <500ms
- [x] Zero degradation

### Documentation
- [x] cortex.md updated
- [x] ALIGNMENT-IMPLEMENTATION.md complete
- [x] Quick reference created
- [x] All READMEs updated

---

## 🔗 Key Documents

**Planning:**
- `CORTEX-ALIGNMENT-PLAN.md` - Full 48-page plan with detailed tasks
- `CORTEX-ALIGNMENT-SUMMARY.md` - Executive summary
- `CORTEX-ALIGNMENT-QUICKSTART.md` - This document

**Progress:**
- `IMPLEMENTATION-PROGRESS.md` - Overall implementation status

**Reference:**
- `cortex-design/CORTEX-DNA.md` - Design philosophy
- `prompts/internal/brain-protector.md` - Protection design
- `CORTEX/src/tier0/cleanup_hook.py` - Cleanup design

---

## 🚀 Ready? Let's Go!

```markdown
#file:prompts/user/cortex.md

I'm ready. Execute CORTEX-ALIGNMENT-PLAN.md Phase 1 - Schema Migration.

Create migrate_add_boundaries.py and add scope/namespaces columns to the patterns table.
```

**Estimated Time:** 3-4 hours for Phase 1  
**After Phase 1:** 7 more phases, 24-32 hours remaining  
**Total Duration:** 28-36 hours (3.5-4.5 days)

**You got this! 💪**

---

**Document Version:** 1.0  
**Created:** November 6, 2025  
**Status:** READY FOR EXECUTION
