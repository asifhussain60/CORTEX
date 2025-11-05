# KDS v8 Feature Inventory

**Purpose:** Complete catalog of KDS features requiring CORTEX implementation  
**Date:** 2025-11-05  
**Status:** 📋 BASELINE FOR MIGRATION  
**Source:** KDS v8 (main branch)

---

## 📊 Summary Statistics

| Category | Features | Status | Priority |
|----------|----------|--------|----------|
| **Core Routing** | 7 | Active | P0 (Critical) |
| **Agent System** | 23 | Active | P0 (Critical) |
| **BRAIN Tiers** | 5 | Active | P0 (Critical) |
| **Specialist Agents** | 10 | Active | P1 (High) |
| **Scripts/Automation** | 45+ | Active | P2 (Medium) |
| **Dashboard** | 2 | Active | P2 (Medium) |
| **Protection System** | 6 | Active | P1 (High) |
| **Test Coverage** | ~15% | Fragile | P0 (Critical) |

**Total Features:** 98+  
**Must-Have (P0/P1):** 51  
**Nice-to-Have (P2):** 47+

---

## 🎯 P0: Critical Core Features (Must-Have for v1.0)

### 1. Core Routing System

**Features:**
1. ✅ **Intent Router** - Single entry point, auto-detect user intent
2. ✅ **Universal Entry** - `#file:kds.md` for all interactions
3. ✅ **Conversation Context** - "Make it purple" continuity (3-layer auto-recording)
4. ✅ **Session State Management** - Track active sessions, phases, tasks
5. ✅ **Agent Handoff Protocol** - Standardized context passing
6. ✅ **SOLID Architecture** - 10 specialist agents, single responsibility
7. ✅ **Event Logging** - All agents log to `events.jsonl`

**Implementation Notes:**
- CORTEX: Simplify to 4-tier BRAIN (vs KDS 6-tier)
- CORTEX: Concise routing decisions (summary-first)
- CORTEX: SQLite for faster queries (<100ms)

---

### 2. BRAIN System (Knowledge & Memory)

#### Tier 0: Instinct (Governance)
**Features:**
1. ✅ **22 Governance Rules** (TDD, SOLID, DoR/DoD)
2. ✅ **Immutable Core Principles**
3. ✅ **Test-First Enforcement**
4. ✅ **Definition of Ready/Done**

**Storage:** YAML (22 rules, ~20 KB)  
**Status:** Active, enforced via Brain Protector

#### Tier 1: Conversation History (STM)
**Features:**
1. ✅ **14+ Conversations Tracked**
2. ✅ **3-Layer Auto-Recording** (Copilot 71% auto, Sessions, Manual)
3. ✅ **Context Continuity** ("Make it purple" works)
4. ✅ **FIFO Buffer** (last 20 conversations)
5. ✅ **Entity Extraction** (automatic)
6. ✅ **Cross-Conversation Linking**

**Storage:** `conversation-history.jsonl` + `conversation-context.jsonl`  
**Status:** Active, monitored via `monitor-tier1-health.ps1`

**CORTEX Changes:**
- Migrate to SQLite (indexed queries <50ms)
- Add full-text search (FTS5)
- Automatic FIFO rotation

#### Tier 2: Knowledge Graph (LTM)
**Features:**
1. ✅ **Intent Patterns** (successful phrase mappings)
2. ✅ **File Relationships** (co-modification rates)
3. ✅ **Correction History** (common mistakes)
4. ✅ **Workflow Patterns** (task sequences)
5. ✅ **Validation Insights** (common fixes)
6. ✅ **Feature Components** (file mappings)
7. ✅ **Confidence Thresholds** (min 0.70 for auto-routing)
8. ✅ **Pattern Generalization** (wildcard detection)
9. ✅ **Confidence Decay** (age-based reduction)
10. ✅ **Protection System** (3-phase validation)

**Storage:** `knowledge-graph.yaml` (95% complete)  
**Status:** Active, auto-updates after 50+ events OR 24 hours

**CORTEX Changes:**
- Migrate to SQLite with FTS5 (semantic search)
- Probabilistic pattern matching (0.0-1.0 confidence)
- Pattern consolidation (60-84% similar merged)
- Auto-pruning (<0.30 confidence deleted)

#### Tier 3: Development Context
**Features:**
1. ✅ **Git Activity** (1,249 commits analyzed)
2. ✅ **File Hotspots** (churn rate tracking)
3. ✅ **Change Patterns** (commit size analysis)
4. ✅ **Code Health** (velocity trends)
5. ✅ **Test Coverage Trends**
6. ✅ **Build Success Rates**
7. ✅ **Session Patterns** (time-based success)
8. ✅ **Workflow Effectiveness** (test-first 68% faster)
9. ✅ **Proactive Warnings** (hotspot alerts)
10. ✅ **Throttled Collection** (1/hour max)

**Storage:** `development-context.yaml`  
**Status:** Active, throttled to reduce overhead

**CORTEX Changes:**
- JSON cache (in-memory, <10ms queries)
- Delta updates (5-minute refresh)
- Multi-dimensional metrics

#### Tier 4: Event Stream
**Features:**
1. ✅ **Append-Only Log** (all agent actions)
2. ✅ **Auto-Learning Triggers** (50+ events OR 24h)
3. ✅ **Event Schema Validation**
4. ✅ **SHA256 Checksums** (integrity)
5. ✅ **Duplicate Prevention**

**Storage:** `events.jsonl`  
**Status:** Active, protected

**CORTEX Changes:**
- Merge into Tier 2 (immediate pattern extraction)
- No separate tier needed

---

### 3. Specialist Agents (10 Core)

**Agent List:**

1. **Intent Router** (`intent-router.md`)
   - Purpose: Detect user intent, route to correct agent
   - Features: Pattern matching, BRAIN queries, confidence thresholds
   - Status: ✅ Active

2. **Work Planner** (`work-planner.md`)
   - Purpose: Break features into multi-phase plans
   - Features: Task granularity, DoR enforcement, pattern loading
   - Status: ✅ Active

3. **Code Executor** (`code-executor.md`)
   - Purpose: Implement code with precision
   - Features: File editing, SOLID compliance, related file suggestions
   - Status: ✅ Active

4. **Test Generator** (`test-generator.md`)
   - Purpose: Create tests (unit, integration, E2E)
   - Features: TDD enforcement, visual regression, pattern reuse
   - Status: ✅ Active

5. **Error Corrector** (`error-corrector.md`)
   - Purpose: Fix mistakes immediately
   - Features: Wrong file detection, hallucination override
   - Status: ✅ Active

6. **Health Validator** (`health-validator.md`)
   - Purpose: System health checks
   - Features: Build/test/lint validation, git status
   - Status: ✅ Active

7. **Brain Updater** (`brain-updater.md`)
   - Purpose: Process events, update knowledge graph
   - Features: Pattern extraction, confidence calculation
   - Status: ✅ Active

8. **Brain Protector** (`brain-protector.md`)
   - Purpose: Protect BRAIN integrity
   - Features: Rule enforcement, SOLID challenges, TDD protection
   - Status: ✅ Active

9. **Change Governor** (`change-governor.md`)
   - Purpose: Review KDS self-modifications
   - Features: Validate KDS/ directory changes
   - Status: ✅ Active

10. **Commit Handler** (`commit-handler.md`)
    - Purpose: Validate commits, auto-categorize
    - Features: Baseline comparison, smart validation
    - Status: ✅ Active (V8 Phase 3.5)

**CORTEX Changes:**
- Refactor all agents for concise responses
- Summary-first, code-last approach
- SQLite BRAIN queries (vs YAML parsing)

---

### 4. Protection System (Rule #22)

**Features:**
1. ✅ **Instinct Immutability** (Tier 0 rules protected)
2. ✅ **Tier Boundary Protection** (data in correct tier)
3. ✅ **SOLID Compliance** (single responsibility)
4. ✅ **Hemisphere Specialization** (LEFT/RIGHT routing)
5. ✅ **Knowledge Quality** (confidence thresholds)
6. ✅ **Commit Integrity** (auto-categorize, .gitignore)
7. ✅ **Routing Safety** (3+ occurrences required)
8. ✅ **Data Validation** (YAML structure checks)
9. ✅ **Automatic Backups** (before updates)
10. ✅ **Anomaly Detection** (suspicious patterns flagged)

**Scripts:**
- `protect-brain-update.ps1`
- `protect-event-append.ps1`
- `protect-routing-decision.ps1`
- `manage-anomalies.ps1`

**Impact:**
- Routing accuracy: 80% → 96%
- Data corruption: 1/month → 0/year
- Repeated mistakes: 8% → 2%

**CORTEX Changes:**
- Built into Tier 0 (governance enforcement)
- Self-monitoring per tier (no separate layer)

---

### 5. Test Infrastructure

**Current Coverage:** ~15% (fragile)

**Features:**
1. 🔴 **TDD Workflow** (RED → GREEN → REFACTOR)
2. 🔴 **Test-First Enforcement** (DoD requirement)
3. 🟡 **Pattern Reuse** (test templates)
4. 🔴 **Visual Regression** (documented, not implemented)
5. 🔴 **Unit Tests** (minimal coverage)
6. 🔴 **Integration Tests** (minimal coverage)
7. 🔴 **E2E Tests** (Playwright documented)

**CORTEX Target:** 95%+ coverage (370 permanent tests)

**Test Breakdown:**
- **Tier 0 (Instinct):** 15 unit tests
- **Tier 1 (STM):** 50 unit + 8 integration
- **Tier 2 (LTM):** 67 unit + 12 integration
- **Tier 3 (Context):** 38 unit + 6 integration
- **Agents:** 125 unit tests
- **Workflows:** 45 workflow tests
- **Regression:** 30 feature parity tests

**Total:** 396 tests planned

---

## 🎨 P1: High Priority Features (Quality of Life)

### 6. User-Facing Commands

**Direct Entry Points:**

1. **Plan** (`prompts/user/plan.md`)
   - Purpose: Start new feature work
   - Status: ✅ Active

2. **Execute** (`prompts/user/execute.md`)
   - Purpose: Continue active session
   - Status: ✅ Active

3. **Test** (`prompts/user/test.md`)
   - Purpose: Create/run tests
   - Status: ✅ Active

4. **Validate** (`prompts/user/validate.md`)
   - Purpose: System health check
   - Status: ✅ Active

5. **Correct** (`prompts/user/correct.md`)
   - Purpose: Override Copilot mistakes
   - Status: ✅ Active

6. **Govern** (`prompts/user/govern.md`)
   - Purpose: Review KDS changes
   - Status: ✅ Active

**CORTEX Changes:**
- All route through `cortex.md` entry point
- Concise responses by default
- Optional verbose mode

---

### 7. Shared Utilities

**Infrastructure Agents:**

1. **Session Loader** (`prompts/shared/session-loader.md`)
   - Purpose: Abstract session state access
   - Status: ✅ Active (DIP)

2. **File Accessor** (`prompts/shared/file-accessor.md`)
   - Purpose: Abstract file operations
   - Status: ✅ Active (DIP)

3. **Test Runner** (`prompts/shared/test-runner.md`)
   - Purpose: Abstract test execution
   - Status: ✅ Active (DIP)

4. **Brain Query** (`prompts/shared/brain-query.md`)
   - Purpose: Abstract BRAIN queries
   - Status: ✅ Active (DIP)

5. **Validation** (`prompts/shared/validation.md`)
   - Purpose: Reusable validation helpers
   - Status: ✅ Active

6. **Handoff** (`prompts/shared/handoff.md`)
   - Purpose: Standardized agent handoff
   - Status: ✅ Active

7. **Execution Tracer** (`prompts/shared/execution-tracer.md`)
   - Purpose: Structured logging with correlation IDs
   - Status: ✅ Active

**CORTEX Changes:**
- Refactor for SQLite (vs YAML parsing)
- Maintain DIP (Dependency Inversion Principle)

---

### 8. Supplemental Agents

**Additional Functionality:**

1. **Session Resumer** (`session-resumer.md`)
   - Purpose: Resume after interruptions
   - Status: ✅ Active

2. **Conversation Context Manager** (`conversation-context-manager.md`)
   - Purpose: Track recent messages
   - Status: ✅ Active

3. **Development Context Collector** (`development-context-collector.md`)
   - Purpose: Collect git/test/build metrics
   - Status: ✅ Active (throttled)

4. **Metrics Reporter** (`metrics-reporter.md`)
   - Purpose: Performance graphs
   - Status: ✅ Active

5. **Knowledge Retriever** (`knowledge-retriever.md`)
   - Purpose: Query BRAIN for insights
   - Status: ✅ Active

6. **Post-Implementation Reviewer** (`post-implementation-reviewer.md`)
   - Purpose: Quality review after completion
   - Status: ✅ Active

7. **Screenshot Analyzer** (`screenshot-analyzer.md`)
   - Purpose: Visual regression analysis
   - Status: 📋 Documented only

8. **Brain Amnesia** (`brain-amnesia.md`)
   - Purpose: Remove app-specific data
   - Status: ✅ Active

9. **Brain Reset** (`brain-reset.md`)
   - Purpose: Selective BRAIN reset
   - Status: ✅ Active

10. **Brain Crawler** (`brain-crawler.md`)
    - Purpose: Codebase analysis and population
    - Status: 📋 Designed, not implemented

11. **Clear Conversation** (`clear-conversation.md`)
    - Purpose: Clear context buffer
    - Status: ✅ Active

**CORTEX Changes:**
- Consolidate duplicate functionality
- Remove brain-crawler (unnecessary)

---

## 📦 P2: Medium Priority Features (Automation)

### 9. PowerShell Scripts (45+)

**Categories:**

#### BRAIN Management
- ✅ `auto-brain-updater.ps1` - Automatic BRAIN updates
- ✅ `brain-amnesia.ps1` - Remove app-specific data
- ✅ `brain-reset.ps1` - Selective reset
- 📋 `brain-crawler.ps1` - Codebase analysis (designed)

#### Monitoring & Health
- ✅ `monitor-tier1-health.ps1` - STM health tracking
- ✅ `tier1-health-report.ps1` - Detailed reports
- ✅ `verify-system-health.ps1` - Full system check
- ✅ `run-health-checks.ps1` - Automated checks

#### Protection
- ✅ `protect-brain-update.ps1` - Validate/backup/rollback
- ✅ `protect-event-append.ps1` - Event validation
- ✅ `protect-routing-decision.ps1` - Routing safety
- ✅ `manage-anomalies.ps1` - Anomaly management

#### Conversation Tracking
- ✅ `record-session-conversation.ps1` - Manual recording
- ✅ `conversation-stm.ps1` - STM operations
- ✅ `associate-commit-to-conversation.ps1` - Git linking
- ✅ `capture-copilot-chat-work.ps1` - Auto-capture
- ✅ `import-copilot-chats.ps1` - Import history

#### Metrics & Reporting
- ✅ `collect-development-context.ps1` - Tier 3 collection
- ✅ `collect-pr-intelligence.ps1` - PR analysis
- ✅ `generate-metrics-report.ps1` - Performance metrics
- ✅ `efficiency-analyzer.ps1` - Workflow analysis

#### Git & Commits
- ✅ `validate-commit.ps1` - Commit validation
- ✅ `commit-kds-changes.ps1` - Smart commits
- ✅ `setup-kds-branch-protection.ps1` - Branch rules

#### Setup & Maintenance
- ✅ `setup-kds-tooling.ps1` - Initial setup
- ✅ `setup-v6-brain-structure.ps1` - BRAIN structure
- ✅ `run-maintenance.ps1` - Periodic maintenance
- ✅ `backup-kds.ps1` - Backup system
- ✅ `migrate-kds-to-new-repo.ps1` - Migration

#### Utilities
- ✅ `log-event.ps1` - Event logging
- ✅ `file-operations.ps1` - File helpers
- ✅ `validate-kds-references.ps1` - Reference validation
- ✅ `clean-redundant-files.ps1` - Cleanup
- ✅ `fix-github-references.ps1` - Path fixing

#### Dashboard
- ✅ `open-dashboard.ps1` - Launch dashboard
- ✅ `launch-dashboard.ps1` - Server start
- ✅ `dashboard-api-server.ps1` - API backend
- ✅ `generate-monitoring-dashboard.ps1` - Dashboard gen

**CORTEX Changes:**
- Migrate to TypeScript/Node.js where appropriate
- Consolidate duplicate scripts
- Remove Windows-specific dependencies

---

### 10. Dashboard System

**Components:**

#### HTML Dashboard
- **File:** `kds-dashboard.html`
- **Features:**
  - Event stream visualization
  - Conversation history
  - Metrics display
  - Health monitoring
- **Status:** ✅ Active (V8 Phase 1)

#### WPF Dashboard
- **Location:** `dashboard-wpf/`
- **Features:**
  - Real-time data updates
  - Advanced filtering
  - Charts/graphs
  - Export features
- **Status:** 🔄 In Progress (V8 Phase 2)

**CORTEX Changes:**
- Single React/Next.js dashboard
- Real-time WebSocket updates
- Modern UI framework

---

### 11. Git Integration

**Features:**
1. ✅ **Post-Commit Hook** - Auto-BRAIN update
2. ✅ **Commit Validation** - Baseline comparison
3. ✅ **Smart Categorization** (feat/fix/test/docs)
4. ✅ **Conversation Association** (V8 Phase 3.5)
5. ✅ **Branch Protection** - Setup script
6. ✅ **.gitignore Updates** - BRAIN files excluded

**CORTEX Changes:**
- Cross-platform git hooks (Husky)
- Pre-commit formatting/linting

---

### 12. Documentation System

**Core Docs:**
- ✅ `README.md` - Project overview
- ✅ `kds-brain/README.md` - BRAIN system
- ✅ `dashboard/README.md` - Dashboard guide
- ✅ `docs/` - 50+ design/progress docs

**Quadrant Pattern:**
- 📚 Story (human narratives)
- 🔧 Technical (detailed specs)
- 🎨 Image Prompt (visual representations)
- 🏗️ High-Level Technical (architecture)

**CORTEX Changes:**
- Consolidate design docs (CORTEX-DNA.md)
- Single-file comprehensive guides
- Visual diagrams (Mermaid)

---

## 🚫 Features NOT Migrating

**Removed in CORTEX:**

1. ❌ **6-Tier Architecture** → 4 tiers (simpler)
2. ❌ **Tier 4 (Event Stream)** → Merged into Tier 2
3. ❌ **Tier 5 (Health)** → Built into each tier
4. ❌ **Corpus Callosum Files** → Just function calls
5. ❌ **YAML Storage** → SQLite (10-100x faster)
6. ❌ **Brain Crawler** → Unnecessary complexity
7. ❌ **Verbose Responses** → Concise summaries
8. ❌ **Code-Heavy Answers** → Minimal snippets
9. ❌ **4,500-line kds.md** → Modular docs
10. ❌ **Windows-Only Scripts** → Cross-platform

---

## 📊 Migration Priority Matrix

| Feature Category | KDS Status | CORTEX Target | Priority | Effort |
|------------------|------------|---------------|----------|--------|
| **Core Routing** | ✅ Active | ✅ Enhanced | P0 | Medium |
| **BRAIN Tiers** | ✅ Active (6) | ✅ Simplified (4) | P0 | High |
| **Specialist Agents** | ✅ 10 Active | ✅ 10 Refactored | P0 | High |
| **Test Coverage** | 🔴 15% | ✅ 95%+ | P0 | Very High |
| **Protection System** | ✅ Active | ✅ Built-in | P1 | Medium |
| **User Commands** | ✅ 6 Active | ✅ Unified Entry | P1 | Low |
| **Shared Utilities** | ✅ 7 Active | ✅ SQLite-based | P1 | Medium |
| **Scripts** | ✅ 45+ PS1 | 🟡 Selective (20) | P2 | Medium |
| **Dashboard** | 🔄 2 Systems | ✅ Single React | P2 | High |
| **Git Integration** | ✅ Active | ✅ Enhanced | P1 | Low |
| **Documentation** | ✅ 50+ Docs | ✅ Consolidated | P2 | Medium |

---

## ✅ Feature Parity Checklist

**CORTEX v1.0 MUST have:**

### Core Functionality (P0)
- [ ] Single entry point (`cortex.md`)
- [ ] Intent detection and routing
- [ ] Conversation context ("Make it purple")
- [ ] Session state management
- [ ] Agent handoff protocol
- [ ] Event logging system
- [ ] SOLID agent architecture

### BRAIN System (P0)
- [ ] Tier 0: Instinct (22 governance rules)
- [ ] Tier 1: Working Memory (last 20 conversations, SQLite)
- [ ] Tier 2: Long-Term Knowledge (patterns, SQLite + FTS5)
- [ ] Tier 3: Context Intelligence (git/test metrics, JSON)
- [ ] Automatic learning triggers
- [ ] Confidence-based routing
- [ ] Protection system (built-in)

### Agents (P0)
- [ ] Intent Router (concise routing)
- [ ] Work Planner (strategic planning)
- [ ] Code Executor (precise implementation)
- [ ] Test Generator (TDD enforcement)
- [ ] Error Corrector (mistake fixing)
- [ ] Health Validator (system checks)
- [ ] Brain Updater (pattern extraction)
- [ ] Brain Protector (rule enforcement)
- [ ] Change Governor (KDS protection)
- [ ] Commit Handler (validation)

### Testing (P0)
- [ ] 370+ permanent tests
- [ ] 95%+ coverage
- [ ] TDD workflow enforcement
- [ ] Continuous regression suite
- [ ] Zero degradation guarantee

### Quality of Life (P1)
- [ ] User-facing commands (plan/execute/test/validate)
- [ ] Shared utilities (DIP maintained)
- [ ] Session resume capability
- [ ] Metrics reporting
- [ ] Git commit association
- [ ] Protection scripts

### Nice-to-Have (P2)
- [ ] Dashboard system (single React app)
- [ ] 20 essential scripts (TypeScript/Node.js)
- [ ] Consolidated documentation
- [ ] Visual diagrams (Mermaid)
- [ ] Cross-platform compatibility

---

## 🎯 Success Criteria

**CORTEX v1.0 is successful when:**

### Functional Parity
- ✅ 100% of P0 features implemented
- ✅ 80%+ of P1 features implemented
- ✅ 370+ tests passing (95%+ coverage)
- ✅ Zero KDS feature regressions

### Performance Improvements
- ✅ Query latency: <100ms (vs KDS 500-1000ms)
- ✅ Storage size: <270 KB (vs KDS 380-570 KB)
- ✅ Learning cycle: <2 min (vs KDS 5-10 min)
- ✅ Response length: <10 lines (vs KDS 30-50)

### Quality Metrics
- ✅ Code snippets: <20% responses (vs KDS 60%+)
- ✅ User comprehension: <30 sec per response
- ✅ Test coverage: 95%+ (vs KDS 15%)
- ✅ Documentation: Single source of truth

---

## 📅 Migration Timeline

**Total Estimated Time:** 15-23 days (3-5 weeks)

| Phase | Features | Days | Cumulative |
|-------|----------|------|------------|
| **Phase 0** | Tier 0 (Instinct) | 1 | 1 |
| **Phase 1** | Tier 1 (STM) | 2-3 | 3-4 |
| **Phase 2** | Tier 2 (LTM) | 3-4 | 6-8 |
| **Phase 3** | Tier 3 (Context) | 2-3 | 8-11 |
| **Phase 4** | Agents (10) | 4-5 | 12-16 |
| **Phase 5** | Entry/Workflows | 2-3 | 14-19 |
| **Phase 6** | Feature Parity | 1-2 | 15-21 |
| **Buffer** | Polish/Docs | 0-2 | 15-23 |

---

## 📂 Feature Location Map

**For reference during migration:**

### Prompts
- `prompts/user/` - 6 user-facing commands + kds.md (4,420 lines)
- `prompts/internal/` - 23 specialist agents
- `prompts/shared/` - 7 shared utilities
- `prompts/core/` - 1 config loader

### BRAIN
- `kds-brain/knowledge-graph.yaml` - Tier 2 data
- `kds-brain/events.jsonl` - Event stream
- `kds-brain/conversation-history.jsonl` - Tier 1 data
- `kds-brain/conversation-context.jsonl` - Tier 1 context
- `kds-brain/development-context.yaml` - Tier 3 data

### Scripts
- `scripts/*.ps1` - 45+ PowerShell automation scripts

### Documentation
- `docs/` - 50+ design/progress documents
- `dashboard/` - Dashboard documentation
- `cortex-design/` - CORTEX design docs

### Dashboard
- `kds-dashboard.html` - HTML dashboard
- `dashboard-wpf/` - WPF dashboard project

---

## 📝 Notes for Implementation

### Key Considerations
1. **Test coverage is critical** - KDS's 15% coverage is a major weakness
2. **SQLite migration is high-effort** - But essential for performance
3. **Response format changes** - All agents need refactoring for concision
4. **Scripts can be selective** - Only migrate essential 20-25
5. **Dashboard can wait** - P2 priority, implement after core

### Migration Risks
- ⚠️ **Data migration** - YAML → SQLite conversion must be lossless
- ⚠️ **Feature regression** - Comprehensive test suite required
- ⚠️ **Learning curve** - Team must adapt to new concise style
- ⚠️ **Rollback complexity** - Must maintain KDS v8 on main branch

### Mitigation Strategies
- ✅ Feature branch isolation (`cortex-migration`)
- ✅ 370-test regression suite
- ✅ Parallel system validation (KDS + CORTEX)
- ✅ Documented rollback procedure

---

**Last Updated:** 2025-11-05  
**Next Step:** Begin Phase 0 (Instinct layer implementation)  
**Version:** 1.0 (Baseline)
