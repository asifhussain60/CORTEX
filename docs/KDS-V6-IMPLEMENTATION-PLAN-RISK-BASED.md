# KDS v6.0 - Implementation Plan (Risk-Based Approach)

**Version:** 6.0.0-RISK-BASED  
**Date:** 2025-11-04  
**Status:** 🎯 READY TO START  
**Approach:** Validate high-risk assumptions FIRST, then build only proven features

**📊 See Also:**
- `KDS/docs/KDS-V6-RISK-ANALYSIS-AND-REDESIGN.md` - Detailed risk analysis & SOLID review
- `KDS/docs/GIT-PERSISTENCE-TDD-INTEGRATION-RECOMMENDATIONS.md` - Git & TDD recommendations
- `KDS/docs/KDS-V6-HOLISTIC-PLAN.md` - Original plan (superseded by this document)

---

## 🎯 Quick Reference

**Total Duration:** 11-12 weeks  
**High-Risk Validation:** Weeks 1-3 (CRITICAL - determines what we build)  
**Implementation:** Weeks 4-11 (build only validated features)  
**Documentation:** Week 12

**Key Milestones:**
- **Week 3:** Go/No-Go decisions for all features
- **Week 7:** Core features complete (git, TDD, abstractions)
- **Week 11:** E2E integration complete
- **Week 12:** Documentation & training ready

---

## 🚨 Why Risk-Based?

### Original Plan Problems

❌ **Database evaluation in Week 7** - Too late to pivot if SQL doesn't work  
❌ **Monolithic phases** - Mixed responsibilities (violates SRP)  
❌ **No fail-fast** - Could waste 6-8 weeks on unviable approach  
❌ **Tight coupling** - Violates DIP (Dependency Inversion Principle)

### Risk-Based Solution

✅ **Validate risky assumptions FIRST** (Weeks 1-3)  
✅ **SOLID-compliant phases** - One responsibility per phase (SRP)  
✅ **Abstraction layers** - Pluggable implementations (DIP, OCP)  
✅ **Fail-fast spikes** - Go/No-Go decisions by Week 3  
✅ **Build only validated features** - No wasted effort

---

## 📋 Implementation Checklist

**Progress:** 0% (0/57 tasks complete) | **Last Updated:** 2025-11-04

---

### 🔴 Phase 0: HIGH-RISK VALIDATION (Weeks 1-3)

**Objective:** Validate or invalidate core assumptions BEFORE building  
**Duration:** 10-15 days  
**Status:** 🚀 READY TO START (HIGHEST PRIORITY)

#### Spike 0.1: SQLite Performance (2-3 days) 🔴

**Question:** Is SQLite actually faster than YAML for BRAIN queries?

- [ ] Day 1: Baseline YAML
  - [ ] Measure `knowledge-graph.yaml` query times
  - [ ] Test at 1000, 5000, 10000 file scales
  - [ ] Identify slowest queries

- [ ] Day 2: SQLite Implementation
  - [ ] Design minimal schema
  - [ ] Create migration script (YAML → SQLite)
  - [ ] Populate with 1000+ test entries

- [ ] Day 3: Performance Comparison
  - [ ] Run same queries (YAML vs SQLite, 10 iterations)
  - [ ] Measure: Query time, storage size, concurrent access
  - [ ] **DECISION: GO (≥2x faster) or NO-GO (stay with YAML)**

**Deliverable:** `spike-0.1-sqlite-performance-report.md`

---

#### Spike 0.2: Multi-Threaded Crawlers (3-4 days) 🔴

**Question:** Are parallel PowerShell crawlers worth the complexity?

- [ ] Day 1: Single-threaded baseline
  - [ ] Measure current crawler on NoorCanvas (1000+ files)
  - [ ] Time breakdown: Discovery, parsing, relationships
  - [ ] Identify bottlenecks

- [ ] Day 2: Simple parallel (2 jobs)
  - [ ] UI files vs API files in parallel
  - [ ] Test progress tracking, completion detection

- [ ] Day 3: Full parallel (4 jobs)
  - [ ] UI, API, Service, Test crawlers
  - [ ] Add progress aggregation, error handling

- [ ] Day 4: Performance Validation
  - [ ] Compare times (single vs multi)
  - [ ] Measure reliability, CPU usage
  - [ ] **DECISION: GO (≥50% faster) or NO-GO (optimize sequential)**

**Deliverable:** `spike-0.2-parallel-crawler-report.md`

---

#### Spike 0.3: Git Query Performance (2-3 days) 🔴

**Question:** Are git log queries fast enough for real-time BRAIN use?

- [ ] Day 1: Git log baseline
  - [ ] Test `git log` on 1000+ commits
  - [ ] Test grep, file-specific, co-modification queries
  - [ ] Measure performance

- [ ] Day 2: Parser Implementation
  - [ ] Parse commit metadata (YAML in body)
  - [ ] Extract file relationships from diffs
  - [ ] Calculate co-modification frequencies

- [ ] Day 3: Performance Validation
  - [ ] Test on real history (500+ commits)
  - [ ] Compare git queries vs YAML cache
  - [ ] **DECISION: GO (<500ms) or NO-GO (git sync only)**

**Deliverable:** `spike-0.3-git-query-performance-report.md`

---

#### Spike 0.4: Git Micro-Commit Impact (1-2 days) 🔴

**Question:** Will frequent commits bloat the repository?

- [ ] Day 1: Simulation
  - [ ] Create test repo, 100 micro-commits
  - [ ] Measure repo size growth
  - [ ] Test `git gc` compression

- [ ] Day 2: Real-world Test
  - [ ] Full session with micro-commits
  - [ ] Test squashing on merge
  - [ ] Test query performance with 1000+ commits
  - [ ] **DECISION: GO (<10MB/month) or NO-GO (batch commits)**

**Deliverable:** `spike-0.4-git-commit-impact-report.md`

---

#### Spike 0.5: TDD Architectural Blocking (2-3 days) 🔴

**Question:** Can we block code execution until tests exist?

- [ ] Day 1: Design
  - [ ] Design pre-execution check architecture
  - [ ] Identify injection point (code-executor.md)
  - [ ] Plan test existence detection

- [ ] Day 2: Prototype
  - [ ] Create `test-enforcer.ps1`
  - [ ] Integrate with code-executor.md
  - [ ] Test blocking mechanism

- [ ] Day 3: Validation
  - [ ] E2E test (code-first should block)
  - [ ] Verify auto test generation
  - [ ] Test RED → GREEN → REFACTOR
  - [ ] **DECISION: GO (blocking works) or NO-GO (keep rule)**

**Deliverable:** `spike-0.5-tdd-blocking-report.md`

---

**Phase 0 Success Criteria:**
- ✅ All 5 spike reports complete
- ✅ Go/No-Go decision for each feature
- ✅ ≤2 NO-GO decisions (otherwise re-evaluate v6.0)

**CRITICAL MILESTONE:** By end of Week 3, we know what to build

---

### 🟡 Phase 1: Instinct Layer Foundation (Week 4)

**Objective:** SOLID-compliant abstraction layer  
**Duration:** 5-7 days  
**Status:** ⏸️ WAITING (depends on Phase 0)

- [ ] Create folder structure
  - [ ] `KDS/brain/instinct/` with README
  - [ ] Define Instinct vs Knowledge vs Working Memory

- [ ] Persistence abstraction (DIP)
  - [ ] `IPersistenceProvider` interface
  - [ ] `FilePersistence` implementation (current YAML)
  - [ ] `GitPersistence` (if Spike 0.4 = GO)
  - [ ] Factory pattern for selection

- [ ] Knowledge source abstraction (DIP)
  - [ ] `IKnowledgeSource` interface
  - [ ] `YamlKnowledgeSource` (current)
  - [ ] `GitKnowledgeSource` (if Spike 0.3 = GO)
  - [ ] `DatabaseKnowledgeSource` (if Spike 0.1 = GO)

- [ ] Test abstractions
  - [ ] Swap providers (file ↔ git)
  - [ ] Swap sources (yaml ↔ git ↔ db)
  - [ ] Verify agent transparency

**Deliverables:**
- ✅ SOLID DIP compliance
- ✅ Pluggable persistence & knowledge
- ✅ Transparent to agents

---

### 🟢 Phase 2: Git Persistence (Week 5)

**Objective:** Session state commits  
**Duration:** 5-7 days  
**Status:** ⏸️ WAITING (Spike 0.4=GO, Phase 1 done)  
**⚠️ SKIP if Spike 0.4 = NO-GO**

- [ ] Git session persister
  - [ ] `git-session-persister.ps1`
  - [ ] Commit message schema (YAML metadata)
  - [ ] Session lifecycle commits

- [ ] Update session-loader.md
  - [ ] Use `IPersistenceProvider`
  - [ ] Git-based load/save
  - [ ] Test crash recovery

- [ ] Update code-executor.md
  - [ ] Commit after each task
  - [ ] Include metadata (task, duration, status)

- [ ] Integration test
  - [ ] Full session with git
  - [ ] Verify commits, test resume
  - [ ] Performance (<1s overhead)

**Deliverables:**
- ✅ Git persistence working
- ✅ Zero data loss
- ✅ Session history in git

---

### 🟢 Phase 3: TDD as Instinct (Week 6)

**Objective:** Architectural TDD enforcement  
**Duration:** 5-7 days  
**Status:** ⏸️ WAITING (Spike 0.5=GO)  
**⚠️ SKIP if Spike 0.5 = NO-GO**

- [ ] TDD enforcement
  - [ ] `test-enforcer.ps1` (refined)
  - [ ] `tdd-enforcer.md` agent
  - [ ] RED → GREEN → REFACTOR workflow

- [ ] Update code-executor.md
  - [ ] Pre-execution TDD check
  - [ ] Block if no test
  - [ ] Auto-trigger test-generator.md

- [ ] Integration test
  - [ ] Code-first blocked
  - [ ] Auto test generation
  - [ ] Full TDD flow
  - [ ] 100% compliance

**Deliverables:**
- ✅ TDD enforced (cannot skip)
- ✅ 100% test-first
- ✅ Auto test generation

---

### 🟢 Phase 4: Git as Knowledge Source (Week 7)

**Objective:** Git log as primary knowledge  
**Duration:** 5-7 days  
**Status:** ⏸️ WAITING (Spike 0.3=GO, Phase 1 done)  
**⚠️ Use sync-only if Spike 0.3 = NO-GO**

- [ ] Git knowledge source
  - [ ] `GitKnowledgeSource` class
  - [ ] Commit metadata parsing
  - [ ] File relationship queries
  - [ ] Co-modification detection

- [ ] Update commit-handler.md
  - [ ] Structured metadata in commits
  - [ ] Learning outcomes, patterns

- [ ] Update brain-updater.md
  - [ ] Query git after events
  - [ ] Sync YAML cache from git
  - [ ] Git primary, YAML secondary

- [ ] Integration test
  - [ ] Query relationships from git
  - [ ] Compare git vs YAML accuracy
  - [ ] Test hybrid fallback

**Deliverables:**
- ✅ Git as primary source
- ✅ YAML as cache
- ✅ Hybrid working

---

### 🟢 Phase 5: Multi-Threaded Crawlers (Week 8)

**Objective:** 50-60% speed improvement  
**Duration:** 5-7 days  
**Status:** ⏸️ WAITING (Spike 0.2=GO)  
**⚠️ SKIP if Spike 0.2 = NO-GO**

- [ ] Area crawlers (refined)
  - [ ] `ui-crawler.ps1`
  - [ ] `api-crawler.ps1`
  - [ ] `service-crawler.ps1`
  - [ ] `test-crawler.ps1`

- [ ] Orchestrator
  - [ ] Launch 4 parallel jobs
  - [ ] Real-time progress aggregation
  - [ ] Error handling

- [ ] Integration test
  - [ ] Run on NoorCanvas (1000+ files)
  - [ ] Verify ≥50% faster
  - [ ] Test reliability (≥99%)

**Deliverables:**
- ✅ 50-60% faster
- ✅ Reliable parallel execution
- ✅ Real-time progress

---

### 🟢 Phase 6: Database Integration (Week 9)

**Objective:** SQLite as option  
**Duration:** 5-7 days  
**Status:** ⏸️ WAITING (Spike 0.1=GO)  
**⚠️ ENTIRE PHASE SKIPPED if Spike 0.1 = NO-GO**

- [ ] Database source (refined)
  - [ ] SQLite schema
  - [ ] Migration script (YAML → SQLite)
  - [ ] Indexes for queries

- [ ] Update brain-updater.md
  - [ ] Support `DatabaseKnowledgeSource`
  - [ ] Auto-suggest when BRAIN >5MB

- [ ] Integration test
  - [ ] Migrate test BRAIN
  - [ ] Verify ≥2x faster
  - [ ] Test rollback to YAML

**Deliverables:**
- ✅ SQLite option (opt-in)
- ✅ Migration tested
- ✅ Performance validated

---

### 🟢 Phase 7: Auto-Infrastructure (Week 10)

**Objective:** Auto dashboard/metrics/health  
**Duration:** 5-7 days  
**Status:** ⏸️ WAITING (core features done)

- [ ] Trigger system
  - [ ] File system change detection
  - [ ] Event-based triggers
  - [ ] Trigger orchestrator

- [ ] Auto-updaters
  - [ ] `dashboard-updater.ps1`
  - [ ] `metrics-collector.ps1`
  - [ ] `health-check-generator.ps1`

- [ ] Integration test
  - [ ] New service → Dashboard updated
  - [ ] Add component → Metrics added
  - [ ] Verify zero manual updates

**Deliverables:**
- ✅ Auto-infrastructure working
- ✅ Zero manual updates
- ✅ Fire-and-forget enabled

---

### 🟢 Phase 8: E2E Integration (Week 11)

**Objective:** Validate fire-and-forget  
**Duration:** 5-7 days  
**Status:** ⏸️ WAITING (all features done)

- [ ] Design test feature
  - [ ] "SignalR notifications"
  - [ ] Multi-file, 15-20 auto-updates

- [ ] Execute fire-and-forget
  - [ ] Single command
  - [ ] Monitor all automation
  - [ ] Measure time savings

- [ ] Validate ALL features
  - [ ] TDD (if Phase 3 done)
  - [ ] Git persistence (if Phase 2 done)
  - [ ] Git knowledge (if Phase 4 done)
  - [ ] Crawlers (if Phase 5 done)
  - [ ] Database (if Phase 6 done)
  - [ ] Auto-infrastructure

**Deliverables:**
- ✅ Fire-and-forget validated
- ✅ ≥40% time savings
- ✅ All features integrated

---

### 🟢 Phase 9: Documentation (Week 12)

**Objective:** Complete v6.0 docs  
**Duration:** 3-5 days  
**Status:** ⏸️ WAITING (Phase 8 done)

- [ ] Architecture docs
  - [ ] Update KDS-DESIGN.md
  - [ ] Document 3-layer brain
  - [ ] Document SOLID abstractions

- [ ] Decision log
  - [ ] All Go/No-Go decisions from Phase 0
  - [ ] Why features included/excluded

- [ ] User guides
  - [ ] Fire-and-forget workflow
  - [ ] Git session recovery
  - [ ] TDD instinct (if implemented)

- [ ] Troubleshooting
  - [ ] Common issues
  - [ ] Performance tips

- [ ] API docs
  - [ ] IPersistenceProvider
  - [ ] IKnowledgeSource

- [ ] Training
  - [ ] Quick start
  - [ ] Best practices

**Deliverables:**
- ✅ Complete documentation
- ✅ Decision rationale
- ✅ Team training ready

---

## 📊 Phase Summary

| Phase | Focus | Duration | Risk | Skippable? | Dependencies |
|-------|-------|----------|------|------------|--------------|
| 0 | Validation | 2-3 weeks | 🔴 High | ❌ CRITICAL | None |
| 1 | Abstractions | 1 week | 🟢 Low | ❌ Required | Phase 0 |
| 2 | Git Persist | 1 week | 🟡 Medium | ✅ If 0.4=NO | Phase 0.4, 1 |
| 3 | TDD Instinct | 1 week | 🟡 Medium | ✅ If 0.5=NO | Phase 0.5 |
| 4 | Git Knowledge | 1 week | 🟡 Medium | ✅ If 0.3=NO | Phase 0.3, 1 |
| 5 | Crawlers | 1 week | 🟡 Medium | ✅ If 0.2=NO | Phase 0.2 |
| 6 | Database | 1 week | 🟢 Low | ✅ If 0.1=NO | Phase 0.1 |
| 7 | Auto-Infra | 1 week | 🟢 Low | ❌ Required | Phases 1-6 |
| 8 | E2E Test | 1 week | 🟢 Low | ❌ Required | Phase 7 |
| 9 | Docs | 3-5 days | 🟢 Low | ❌ Required | Phase 8 |

**Total:** 11-12 weeks  
**Flexible:** Phases 2-6 adjust based on validation  
**Fixed:** Phases 0, 1, 7, 8, 9 always run

---

## ✅ Success Criteria

### Phase 0 (Validation)
- [ ] 5 spike reports complete
- [ ] Go/No-Go decision for each
- [ ] ≤2 NO-GO (else re-evaluate)

### End of v6.0
- [ ] All GO features implemented
- [ ] NO-GO features skipped/replaced
- [ ] Fire-and-forget validated
- [ ] ≥40% time savings
- [ ] Complete documentation

---

## 🎯 Next Steps

### This Week (Week 1)
1. **Day 1-3:** Spike 0.1 - SQLite Performance
2. **Day 4-7:** Spike 0.2 - Multi-threaded Crawlers

### Next Week (Week 2)
3. **Day 8-10:** Spike 0.3 - Git Queries
4. **Day 11-12:** Spike 0.4 - Git Commits
5. **Day 13-15:** Spike 0.5 - TDD Blocking

### Week 3
- Review all spike reports
- Make Go/No-Go decisions
- Adjust Phases 1-9
- Approve implementation plan

---

**Status:** 📋 READY TO START PHASE 0  
**Approach:** RISK-FIRST (fail-fast)  
**SOLID Compliance:** ✅ HIGH  
**Timeline:** 11-12 weeks (flexible based on validation)
