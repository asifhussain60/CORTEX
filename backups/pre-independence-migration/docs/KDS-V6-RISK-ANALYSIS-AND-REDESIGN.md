# KDS v6.0 - Risk Analysis & Implementation Redesign

**Date:** 2025-11-04  
**Status:** 🎯 RISK-BASED IMPLEMENTATION PLAN  
**Approach:** High-risk validation first, then incremental integration

---

## 🎯 Executive Summary

### Current Plan Issues

**❌ Problems with Current Approach:**
1. **High-risk items at the end** - Database evaluation in Week 7 (too late to pivot)
2. **Complex dependencies** - TDD + Git + Auto-infra all in Phase 0 (too much at once)
3. **No early validation** - Multi-threaded crawlers not tested until Week 5-6
4. **Monolithic phases** - Each phase has 8-12 tasks (violates incremental delivery)
5. **Late failure detection** - Integration testing in Week 8-9 (expensive to fix)

**✅ Redesigned Approach:**
1. **Validate high-risk technical assumptions FIRST** (Weeks 1-2)
2. **Proof-of-concept before full implementation** (MVP pattern)
3. **Independent feature validation** (not bundled)
4. **Continuous integration testing** (after each feature)
5. **Fail-fast strategy** (know by Week 2 if approach is viable)

---

## 🚨 Risk Assessment

### High-Risk Items (Must Validate First)

| Risk Item | Why High Risk | Impact if Failed | Validation Time |
|-----------|---------------|------------------|-----------------|
| **SQLite Performance** | Unproven assumption that DB will be faster than YAML | May stick with files (simpler) | 2-3 days |
| **Multi-threaded PowerShell** | Complexity of parallel jobs, progress tracking, state management | May use sequential with optimizations | 3-4 days |
| **Git as Query Engine** | Git log parsing performance at scale, complex queries | May need hybrid approach | 2-3 days |
| **Git Micro-commits** | Repository bloat, performance degradation | May batch commits differently | 1-2 days |
| **TDD Architectural Blocking** | Agent architecture may not support pre-execution checks | May remain rule-based | 2-3 days |

**Total High-Risk Validation:** 10-15 days (2-3 weeks)

### Medium-Risk Items (Test After Validation)

| Risk Item | Why Medium Risk | Mitigation |
|-----------|-----------------|------------|
| Auto-infrastructure triggers | File system watching, event detection | Start with manual triggers, add auto later |
| Commit message parsing | YAML in git body may be fragile | Start with simple format, enhance later |
| BRAIN sync performance | Git queries during brain updates may slow down | Add caching layer, async updates |

### Low-Risk Items (Safe to Implement)

| Item | Why Low Risk |
|------|--------------|
| Instinct layer folder structure | Just folders, no logic |
| Documentation updates | No technical risk |
| Git-based session commits (basic) | Standard git operations |
| TDD rule enforcement (current) | Already working |

---

## 🏗️ SOLID Principles Analysis

### Current Plan Violations

**❌ Single Responsibility Principle (SRP) Violation:**
```
Phase 0: Instinct Layer Foundation
- TDD enforcement (architectural change)
- Git persistence (storage change)  
- Auto-infrastructure (trigger system)

Problem: 3 different responsibilities in one phase
```

**❌ Open/Closed Principle (OCP) Violation:**
```
Git persistence tightly coupled to session format
- Hard to swap storage mechanisms later
- No abstraction for persistence layer
```

**❌ Dependency Inversion Principle (DIP) Violation:**
```
Brain directly queries git log
- Tight coupling to git implementation
- No abstraction for "knowledge source"
```

### SOLID-Compliant Redesign

**✅ SRP: One responsibility per phase**
```
Phase 1: Validate SQLite performance (database evaluation ONLY)
Phase 2: Validate multi-threaded crawlers (crawling ONLY)
Phase 3: Validate git queries (git integration ONLY)
Phase 4: Implement TDD enforcement (TDD ONLY)
Phase 5: Implement git persistence (persistence ONLY)
```

**✅ OCP: Abstract persistence layer**
```
IPersistenceProvider interface:
  - FilePersistence (current)
  - GitPersistence (new)
  - DatabasePersistence (future)
  
Brain doesn't care which is used
```

**✅ DIP: Abstract knowledge sources**
```
IKnowledgeSource interface:
  - YamlKnowledgeSource (current)
  - GitLogKnowledgeSource (new)
  - DatabaseKnowledgeSource (future)
  
Brain queries abstraction, not implementation
```

---

## 🎯 Redesigned Implementation Plan

### Design Philosophy

**Fail-Fast Validation:**
> "Validate the riskiest technical assumptions in the first 2 weeks. If any fail, we know early and can pivot without wasting 6-8 weeks."

**Incremental Integration:**
> "Each feature is independently valuable. Don't bundle features together. Ship small, ship often."

**SOLID Compliance:**
> "Every phase has ONE responsibility. Use abstractions for swappable implementations."

---

## 📋 Risk-Based Phase Breakdown

### 🔴 Phase 0: High-Risk Technical Validation (Week 1-2)

**Objective:** Validate or invalidate core technical assumptions  
**Decision Points:** Go/No-Go for each feature  
**Duration:** 10-15 days

#### **Spike 0.1: SQLite Performance Evaluation (2-3 days)**

**Goal:** Determine if SQLite is actually faster than YAML for BRAIN queries

**Tasks:**
- [ ] **Day 1: Baseline YAML performance**
  - [ ] Measure current knowledge-graph.yaml query times
  - [ ] Measure file size at 1000, 5000, 10000 file projects
  - [ ] Identify slowest queries (file relationships, co-modification)
  
- [ ] **Day 2: SQLite schema & migration**
  - [ ] Design minimal SQLite schema (file_relationships, intent_patterns)
  - [ ] Create test migration script (YAML → SQLite)
  - [ ] Populate with sample data (1000+ entries)
  
- [ ] **Day 3: Performance comparison**
  - [ ] Run same queries on YAML vs SQLite
  - [ ] Measure query times (10 iterations each)
  - [ ] Measure storage size
  - [ ] Test concurrent access (multiple queries)

**Success Criteria:**
- ✅ SQLite is 2x+ faster for complex queries
- ✅ Storage size is comparable or smaller
- ✅ Migration is reliable (zero data loss)

**Decision:**
- **GO:** SQLite is faster → Proceed with database implementation
- **NO-GO:** YAML is fast enough → Stay with files, add caching

**Deliverable:** `spike-0.1-sqlite-performance-report.md`

---

#### **Spike 0.2: Multi-threaded Crawler Viability (3-4 days)**

**Goal:** Prove that parallel PowerShell crawlers are faster and manageable

**Tasks:**
- [ ] **Day 1: Single-threaded baseline**
  - [ ] Measure current crawler performance on NoorCanvas (1000+ files)
  - [ ] Time breakdown: File discovery, parsing, relationship mapping
  - [ ] Identify bottlenecks
  
- [ ] **Day 2: Simple parallel implementation**
  - [ ] Create 2 parallel jobs (UI files vs API files)
  - [ ] Implement basic progress tracking
  - [ ] Test job completion detection
  
- [ ] **Day 3: Full 4-way parallelism**
  - [ ] Implement 4 area crawlers (UI, API, Service, Test)
  - [ ] Add progress aggregation
  - [ ] Test error handling (one job fails)
  
- [ ] **Day 4: Performance validation**
  - [ ] Run on NoorCanvas (1000+ files)
  - [ ] Compare: Single-threaded vs Multi-threaded
  - [ ] Measure: Time savings, CPU usage, reliability

**Success Criteria:**
- ✅ 50%+ time reduction (10 min → 5 min for 1000 files)
- ✅ Reliable completion (99%+ success rate)
- ✅ Manageable complexity (maintainable code)

**Decision:**
- **GO:** 50%+ faster → Proceed with multi-threaded
- **NO-GO:** <30% faster or too complex → Optimize single-threaded instead

**Deliverable:** `spike-0.2-parallel-crawler-report.md`

---

#### **Spike 0.3: Git Query Performance (2-3 days)**

**Goal:** Validate that git log queries are fast enough for real-time BRAIN use

**Tasks:**
- [ ] **Day 1: Git log baseline**
  - [ ] Measure `git log` performance on 1000+ commits
  - [ ] Test grep queries (`git log --grep`)
  - [ ] Test file-specific queries (`git log -- file.cs`)
  - [ ] Measure complex queries (co-modification patterns)
  
- [ ] **Day 2: Implement git-to-BRAIN parser**
  - [ ] Parse commit metadata (YAML in body)
  - [ ] Extract file relationships from commit diffs
  - [ ] Calculate co-modification frequencies
  
- [ ] **Day 3: Performance validation**
  - [ ] Run on real git history (500+ commits)
  - [ ] Compare: Git queries vs YAML cache
  - [ ] Test hybrid approach (git + cache)

**Success Criteria:**
- ✅ Git queries <500ms for common patterns
- ✅ Parsing is reliable (99%+ success rate)
- ✅ Hybrid approach is transparent to agents

**Decision:**
- **GO:** Queries fast enough → Use git as primary source
- **NO-GO:** Too slow → Use git for sync only, cache in YAML

**Deliverable:** `spike-0.3-git-query-performance-report.md`

---

#### **Spike 0.4: Git Micro-Commit Impact (1-2 days)**

**Goal:** Ensure frequent commits don't bloat repository unacceptably

**Tasks:**
- [ ] **Day 1: Simulation**
  - [ ] Create test repo
  - [ ] Generate 100 micro-commits (session state changes)
  - [ ] Measure repo size growth
  - [ ] Test `git gc` compression
  
- [ ] **Day 2: Real-world test**
  - [ ] Run full session with micro-commits
  - [ ] Measure repo size before/after
  - [ ] Test squashing commits on merge
  - [ ] Measure query performance with 1000+ micro-commits

**Success Criteria:**
- ✅ Repo growth <10 MB/month for typical usage
- ✅ Git operations remain fast (<1s)
- ✅ Squashing works reliably

**Decision:**
- **GO:** Acceptable growth → Proceed with micro-commits
- **NO-GO:** Too much bloat → Batch commits (e.g., per-phase, not per-task)

**Deliverable:** `spike-0.4-git-commit-impact-report.md`

---

#### **Spike 0.5: TDD Architectural Blocking (2-3 days)**

**Goal:** Prove that we can block code execution until tests exist

**Tasks:**
- [ ] **Day 1: Design enforcement mechanism**
  - [ ] Design pre-execution check architecture
  - [ ] Identify where to inject check (code-executor.md)
  - [ ] Design test existence detection
  
- [ ] **Day 2: Implement prototype**
  - [ ] Create `test-enforcer.ps1`
  - [ ] Integrate with code-executor.md
  - [ ] Test blocking (attempt code-first)
  
- [ ] **Day 3: Validation**
  - [ ] Run end-to-end test (should block without test)
  - [ ] Verify automatic test generation trigger
  - [ ] Test RED → GREEN → REFACTOR flow

**Success Criteria:**
- ✅ Code-first attempts are blocked 100%
- ✅ Agents automatically create tests when blocked
- ✅ Workflow is smooth (not annoying)

**Decision:**
- **GO:** Blocking works reliably → Implement as instinct
- **NO-GO:** Too brittle or annoying → Keep as enforced rule (current)

**Deliverable:** `spike-0.5-tdd-blocking-report.md`

---

**Phase 0 Summary:**

| Spike | Duration | Go/No-Go Decision | Risk Mitigation |
|-------|----------|-------------------|-----------------|
| 0.1 SQLite | 2-3 days | DB vs Files | Know by Day 3 if DB worth it |
| 0.2 Parallel Crawlers | 3-4 days | Parallel vs Sequential | Know by Day 7 if complexity justified |
| 0.3 Git Queries | 2-3 days | Git-primary vs Git-sync | Know by Day 10 if git viable |
| 0.4 Git Commits | 1-2 days | Micro vs Batch | Know by Day 12 if bloat acceptable |
| 0.5 TDD Blocking | 2-3 days | Instinct vs Rule | Know by Day 15 if architecture supports |

**Total Time:** 10-15 days  
**Output:** 5 decision reports (GO/NO-GO for each feature)  
**Value:** Know which features to build vs skip BEFORE investing 6-8 weeks

---

### 🟡 Phase 1: Instinct Layer Foundation (Week 3)

**Objective:** Implement core instinct behaviors (based on Phase 0 decisions)  
**Dependencies:** Phase 0 spikes complete  
**Duration:** 5-7 days

**Tasks:**
- [ ] Create instinct layer folder structure
  - [ ] `KDS/brain/instinct/` (main folder)
  - [ ] `KDS/brain/instinct/README.md` (architecture doc)
  - [ ] Define instinct vs knowledge vs working-memory separation
  
- [ ] Implement persistence abstraction (DIP compliance)
  - [ ] Create `IPersistenceProvider` interface
  - [ ] Implement `FilePersistence` (current YAML)
  - [ ] Implement `GitPersistence` (if Spike 0.4 = GO)
  - [ ] Implement provider factory pattern
  
- [ ] Implement knowledge source abstraction (DIP compliance)
  - [ ] Create `IKnowledgeSource` interface
  - [ ] Implement `YamlKnowledgeSource` (current)
  - [ ] Implement `GitKnowledgeSource` (if Spike 0.3 = GO)
  - [ ] Implement `DatabaseKnowledgeSource` (if Spike 0.1 = GO)
  
- [ ] Test abstraction layer
  - [ ] Swap persistence providers (file ↔ git)
  - [ ] Swap knowledge sources (yaml ↔ git ↔ db)
  - [ ] Verify agents don't break (transparent to them)

**Deliverables:**
- ✅ Abstraction layer working
- ✅ Pluggable persistence
- ✅ Pluggable knowledge sources
- ✅ SOLID DIP compliance

---

### 🟢 Phase 2: Git-Based Persistence (Week 4)

**Objective:** Implement git-based session persistence  
**Dependencies:** Phase 0 Spike 0.4 = GO, Phase 1 abstractions ready  
**Duration:** 5-7 days

**Tasks:**
- [ ] Implement git session persister
  - [ ] Create `git-session-persister.ps1`
  - [ ] Design commit message schema (structured metadata)
  - [ ] Implement session lifecycle commits (start, task, phase, pause, complete)
  
- [ ] Update session-loader.md
  - [ ] Use IPersistenceProvider abstraction
  - [ ] Add git-based load/save
  - [ ] Test crash recovery from git log
  
- [ ] Update code-executor.md
  - [ ] Commit after each task completion
  - [ ] Include metadata in commit (task, duration, status)
  
- [ ] Integration testing
  - [ ] Run full session with git persistence
  - [ ] Verify all commits created
  - [ ] Test session resume from git log
  - [ ] Measure performance overhead

**Deliverables:**
- ✅ Git-based session persistence working
- ✅ Zero data loss (crash recovery)
- ✅ Full session history in git log

---

### 🟢 Phase 3: TDD as Instinct (Week 5)

**Objective:** Implement TDD architectural enforcement  
**Dependencies:** Phase 0 Spike 0.5 = GO  
**Duration:** 5-7 days

**Tasks:**
- [ ] Implement TDD enforcement
  - [ ] Create `test-enforcer.ps1` (refined from spike)
  - [ ] Create `tdd-enforcer.md` agent
  - [ ] Implement RED → GREEN → REFACTOR workflow
  
- [ ] Update code-executor.md
  - [ ] Add pre-execution TDD check
  - [ ] Block implementation if no test exists
  - [ ] Trigger test-generator.md automatically
  
- [ ] Integration testing
  - [ ] Attempt code-first (should block)
  - [ ] Verify automatic test generation
  - [ ] Test full RED → GREEN → REFACTOR flow
  - [ ] Measure 100% test-first compliance

**Deliverables:**
- ✅ TDD architecturally enforced
- ✅ 100% test-first compliance
- ✅ Automatic test generation on block

---

### 🟢 Phase 4: Git as Knowledge Source (Week 6)

**Objective:** Use git log as primary knowledge source  
**Dependencies:** Phase 0 Spike 0.3 = GO, Phase 1 abstractions ready  
**Duration:** 5-7 days

**Tasks:**
- [ ] Implement git knowledge source
  - [ ] Create `GitKnowledgeSource` class
  - [ ] Implement commit metadata parsing
  - [ ] Implement file relationship queries
  - [ ] Implement co-modification pattern detection
  
- [ ] Update commit-handler.md
  - [ ] Generate structured metadata in commits
  - [ ] Include learning outcomes
  - [ ] Include architectural patterns
  
- [ ] Update brain-updater.md
  - [ ] Query GitKnowledgeSource after events
  - [ ] Sync YAML cache from git
  - [ ] Make git primary, YAML secondary
  
- [ ] Integration testing
  - [ ] Query file relationships from git
  - [ ] Compare git results vs YAML cache
  - [ ] Test hybrid fallback (git unavailable → YAML)

**Deliverables:**
- ✅ Git as primary knowledge source
- ✅ YAML as cache
- ✅ Hybrid approach working

---

### 🟢 Phase 5: Multi-Threaded Crawlers (Week 7)

**Objective:** Implement parallel crawlers for 60% speed improvement  
**Dependencies:** Phase 0 Spike 0.2 = GO  
**Duration:** 5-7 days

**Tasks:**
- [ ] Implement area-specific crawlers (refined from spike)
  - [ ] `ui-crawler.ps1`
  - [ ] `api-crawler.ps1`
  - [ ] `service-crawler.ps1`
  - [ ] `test-crawler.ps1`
  
- [ ] Implement orchestrator
  - [ ] Launch 4 parallel jobs
  - [ ] Aggregate progress
  - [ ] Handle errors gracefully
  
- [ ] Integration testing
  - [ ] Run on NoorCanvas (1000+ files)
  - [ ] Verify 50%+ speed improvement
  - [ ] Test reliability (99%+ success rate)

**Deliverables:**
- ✅ 50-60% faster crawling
- ✅ Reliable parallel execution
- ✅ Real-time progress display

---

### 🟢 Phase 6: Database Integration (Week 8)

**Objective:** Add SQLite as optional knowledge storage  
**Dependencies:** Phase 0 Spike 0.1 = GO  
**Duration:** 5-7 days  
**Note:** SKIP if Spike 0.1 = NO-GO

**Tasks:**
- [ ] Implement DatabaseKnowledgeSource (refined from spike)
  - [ ] Create SQLite schema
  - [ ] Implement migration script (YAML → SQLite)
  - [ ] Add indexes for common queries
  
- [ ] Update brain-updater.md
  - [ ] Support DatabaseKnowledgeSource
  - [ ] Auto-suggest migration when BRAIN >5 MB
  
- [ ] Integration testing
  - [ ] Migrate test BRAIN to SQLite
  - [ ] Verify query performance improvement
  - [ ] Test rollback to YAML

**Deliverables:**
- ✅ SQLite option available
- ✅ Migration script tested
- ✅ Database opt-in (not required)

---

### 🟢 Phase 7: Auto-Infrastructure Triggers (Week 9)

**Objective:** Automatic dashboard/metrics/health updates  
**Dependencies:** All core features working  
**Duration:** 5-7 days

**Tasks:**
- [ ] Implement trigger system
  - [ ] File system change detection
  - [ ] Event-based triggers
  - [ ] Trigger orchestrator
  
- [ ] Implement auto-updaters
  - [ ] `dashboard-updater.ps1`
  - [ ] `metrics-collector.ps1`
  - [ ] `health-check-generator.ps1`
  
- [ ] Integration testing
  - [ ] Create new service → Dashboard updated
  - [ ] Add component → Metrics added
  - [ ] Verify zero manual updates

**Deliverables:**
- ✅ Auto-infrastructure working
- ✅ Zero manual updates needed
- ✅ Fire-and-forget workflow

---

### 🟢 Phase 8: E2E Integration & Testing (Week 10)

**Objective:** Validate complete fire-and-forget workflow  
**Dependencies:** All features complete  
**Duration:** 5-7 days

**Tasks:**
- [ ] Design complex test feature
  - [ ] "Real-time notifications with SignalR"
  - [ ] Multi-file (Hub, Service, Component, Tests)
  - [ ] Expected auto-updates: 15-20
  
- [ ] Execute fire-and-forget
  - [ ] Single command: Add feature
  - [ ] Monitor all automatic behaviors
  - [ ] Measure time savings
  
- [ ] Validate all features
  - [ ] TDD enforcement (100% test-first)
  - [ ] Git persistence (all commits)
  - [ ] Git knowledge (queries working)
  - [ ] Auto-infrastructure (all updates)
  - [ ] Multi-threaded crawl (if applicable)
  - [ ] Database (if applicable)

**Deliverables:**
- ✅ Fire-and-forget validated
- ✅ 40%+ time savings
- ✅ All features integrated

---

### 🟢 Phase 9: Documentation (Week 11)

**Objective:** Complete v6.0 documentation  
**Dependencies:** All implementation complete  
**Duration:** 3-5 days

**Tasks:**
- [ ] Architecture documentation
- [ ] User guides
- [ ] Troubleshooting guides
- [ ] API documentation
- [ ] Decision log (what was GO vs NO-GO)

**Deliverables:**
- ✅ Complete v6.0 docs
- ✅ Team training materials
- ✅ Decision rationale documented

---

## 📊 Redesigned Progress Summary

| Phase | Focus | Duration | Risk Level | Dependencies | Fail-Fast? |
|-------|-------|----------|------------|--------------|------------|
| **0** | High-Risk Validation | 2-3 weeks | 🔴 High | None | ✅ YES |
| **1** | Instinct Foundation | 1 week | 🟢 Low | Phase 0 | No |
| **2** | Git Persistence | 1 week | 🟡 Medium | Phase 0.4, Phase 1 | No |
| **3** | TDD Enforcement | 1 week | 🟡 Medium | Phase 0.5 | No |
| **4** | Git Knowledge | 1 week | 🟡 Medium | Phase 0.3, Phase 1 | No |
| **5** | Multi-threaded Crawl | 1 week | 🟡 Medium | Phase 0.2 | No |
| **6** | Database (Optional) | 1 week | 🟢 Low | Phase 0.1 | No |
| **7** | Auto-Infrastructure | 1 week | 🟢 Low | All core | No |
| **8** | E2E Testing | 1 week | 🟢 Low | All features | No |
| **9** | Documentation | 3-5 days | 🟢 Low | Phase 8 | No |

**Total Duration:** 10-11 weeks (conservative estimate)  
**High-Risk Window:** Weeks 1-3 (know if viable early)  
**Implementation Window:** Weeks 4-10 (build validated features)

---

## ✅ Key Improvements Over Original Plan

### 1. Risk Management

**Before:**
- Database evaluation in Week 7 (too late to pivot)
- No early validation of technical assumptions

**After:**
- All high-risk items validated in Weeks 1-3
- Go/No-Go decisions before heavy investment

### 2. SOLID Compliance

**Before:**
- Phases mixed multiple responsibilities
- Tight coupling to implementation details

**After:**
- Each phase = One responsibility (SRP)
- Abstractions for persistence/knowledge (DIP)
- Pluggable implementations (OCP)

### 3. Incremental Delivery

**Before:**
- Monolithic phases (8-12 tasks each)
- Late integration testing

**After:**
- Small phases (5-7 days each)
- Continuous integration after each phase

### 4. Efficiency

**Before:**
- Potential to waste 6-8 weeks on unviable approach

**After:**
- Know by Week 3 which features to build vs skip
- Only build validated features

### 5. Lean Thinking

**Before:**
- Build everything, test at end

**After:**
- Validate assumptions first (spikes)
- Build only validated features (lean)
- Test continuously (agile)

---

## 🎯 Success Criteria

### Phase 0 (Validation)

- [ ] 5 spike reports completed
- [ ] Go/No-Go decision for each feature
- [ ] No more than 2 NO-GO decisions (otherwise re-evaluate entire approach)

### Phases 1-9 (Implementation)

- [ ] All GO features implemented
- [ ] NO-GO features skipped or replaced
- [ ] E2E fire-and-forget validated
- [ ] 40%+ time savings achieved

---

## 📋 Decision Log Template

After each spike, document:

```markdown
# Spike X.Y Decision Log

**Feature:** [Feature Name]
**Duration:** [Actual days]
**Outcome:** GO / NO-GO

**Performance Results:**
- Baseline: [metric]
- New approach: [metric]
- Improvement: [percentage]

**Decision Rationale:**
[Why GO or NO-GO]

**Next Steps:**
- If GO: Proceed to Phase [N]
- If NO-GO: Alternative approach [description]
```

---

## 🚀 Immediate Next Steps

### Week 1 Actions

1. **Day 1-3:** Spike 0.1 - SQLite Performance
2. **Day 4-7:** Spike 0.2 - Multi-threaded Crawlers

### Week 2 Actions

3. **Day 8-10:** Spike 0.3 - Git Query Performance
4. **Day 11-12:** Spike 0.4 - Git Commit Impact
5. **Day 13-15:** Spike 0.5 - TDD Blocking

### Week 3 Decision Meeting

- Review all 5 spike reports
- Make Go/No-Go decisions
- Adjust Phases 1-9 based on decisions
- Approve implementation plan

---

**Status:** 📋 READY FOR SPIKE PHASE  
**Timeline:** 11 weeks (with risk mitigation)  
**Risk Level:** LOW (fail-fast in first 3 weeks)  
**SOLID Compliance:** HIGH (abstracted, single-responsibility phases)  
**Lean/Agile:** HIGH (validate → build → test → integrate)
