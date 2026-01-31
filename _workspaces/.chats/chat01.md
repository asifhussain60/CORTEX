asifhussain60: Follow instructions in [cortex-architect.prompt.md](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md).
review #file:docker-plan. Identify what needs to be implemented to complete all phases.

GitHub Copilot: ## 🏗️ CORTEX Architect
**Author:** Asif Hussain | **Mode:** Audit | **Scope:** docker-plan Phases ✅

---

Let me analyze the docker-plan workspace to identify incomplete phases and required implementations. 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/_workspaces/docker-plan)

Searched text for `PHASE-.*COMPLETION|STATUS.*COMPLETE|TODO|PENDING|IN PROGRESS` (`**/_workspaces/docker-plan/*.md`), 20 results

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/_workspaces/docker-plan/docker-plan-index.md#1-1), lines 1 to 100

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/_workspaces/docker-plan/README.md#1-1), lines 1 to 150

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/_workspaces/docker-plan/PHASE-8-QUICK-REFERENCE.md#1-1), lines 1 to 100

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/_workspaces/docker-plan/PHASE-14-LENS-DASHBOARD-IMPLEMENTATION.yaml#1-1), lines 1 to 200

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/_workspaces/docker-plan/PHASE-15-STATIC-REPO-VISUALIZATION.yaml#1-1), lines 1 to 200

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/_workspaces/docker-plan/PHASE-16-REMEDIATION-FRAMEWORK.yaml#1-1), lines 1 to 200

Searched text for `status.*PENDING|status.*IN.?PROGRESS|status.*PLANNED|TODO|INCOMPLETE` (`**/_workspaces/docker-plan/PHASE-*.yaml`), 20 results

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/_workspaces/docker-plan/PHASE-11-13-IMPLEMENTATION-PLAN.md#1-1), lines 1 to 100

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/_workspaces/docker-plan/PHASE-8.2-UNIFIED-ROUTING.yaml#1-1), lines 1 to 100

Searched text for `PHASE.*(11|12|13|14|15|16).*STATUS|NEXT STEPS|TODO|PENDING` (`**/_workspaces/docker-plan/*.md`), 20 results

Now let me check the current implementation status by looking at recent git history and code structure: 

Ran terminal command: git log --oneline --since="24 hours ago" | head -20

Searched text for `Status.*COMPLETE|Status.*PENDING|Status.*PLANNED` (`**/_workspaces/docker-plan/PHASE-11*.md`), 2 results

Searched for files matching `**/cortex/orchestrators/cortical/*.py`, 6 matches

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/orchestrators/cortical/sensory_input_orchestrator.py#1-1), lines 1 to 50

Ran terminal command: find tests -name "*cortical*" -type f | head -10

Ran terminal command: find tests -path "*orchestrators/cortical*" -name "*.py" 2>/dev/null | head -10

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/orchestrators)

Perfect! Now let me create the comprehensive analysis:

## 🏗️ CORTEX Architect
**Author:** Asif Hussain | **Mode:** Audit | **Scope:** docker-plan Phases Completion ✅

---

### 📋 Summary

**Current State:** 10/16 phases COMPLETE (62.5%), 6 phases require implementation  
**Critical Finding:** Phases 0-10 are production-ready. Phases 11-16 are **fully specified** but require execution.  
**Effort Remaining:** 180-250 hours (~5-7 weeks for 3-person team)

---

### 🎯 Incomplete Phases Analysis

#### **PHASE 8.2: Unified Routing System** 🔄 IN PROGRESS
**Status:** 40% complete (specification done, partial implementation)  
**Remaining Work:**
- Complete keyword-based routing layer (ROUTE-001 through ROUTE-006)
- Wire `OrchestratorLookup` to `IntentRouter`
- Implement semantic ranking fallback (Phase 8.3)
- Add NLP synonym expansion (Phase 8.4 - OPTIONAL)

**Effort:** 2 weeks  
**Blockers:** None (can proceed immediately)  
**MCP Exposure:** ✅ Already exposed via `cortex_process_request`

---

#### **PHASE 11: Cortical Memory System** 📋 PLANNED
**Status:** TDD tests specified (31 tests), orchestrators stubbed, **NOT implemented**  
**Key Findings:**
- ✅ Files exist: sensory_input_orchestrator.py, cortical_integration_orchestrator.py, memory_consolidation_orchestrator.py
- ❌ **Implementation INCOMPLETE** — files are stubs (389 LOC skeleton in sensory_input_orchestrator.py)
- ✅ Test suite ready: test_sensory_input_orchestrator.py

**Required Components (NOT yet implemented):**
1. **CMS-1:** Sensory Input Layer + Dependency Synapses (12-16 hrs)
   - `GitSensoryReceptor` (webhook processing <5s)
   - `DependencySynapticExtractor` (Python/Node.js/Go)
   - `DependencySynapticNetwork` (CVE mapping)
   
2. **CMS-2:** Compliance Extractor + Compliance Graph (14-18 hrs)
   - `ComplianceExtractor` (parse `company/domains/*.yaml`)
   - `ComplianceSynapticNetwork` (regulation mapping)
   
3. **CMS-3:** API/Service Extractors + Service Graph (12-16 hrs)
   - `APIContractExtractor` (OpenAPI/gRPC/GraphQL)
   - `ServiceTopologySynapticNetwork` (blast radius)
   
4. **CMS-4:** Cortical Integration + LENSSmartFacade (18-22 hrs)
   - `CorticalIntegrationOrchestrator` (federated queries)
   - `LENSSmartFacade` (intelligent routing)

**Effort:** 68-88 hours  
**MCP Exposure:** ❌ VIOLATION (ARCH-007) — needs MCP tools for each extractor

---

#### **PHASE 12: Capacity Planning System** 📋 PLANNED
**Status:** TDD specification complete (27 tests), **NOT implemented**  
**Required Components:**
1. **CAP-1:** Historical Velocity Analyzer (10-14 hrs)
   - Git history analysis for team velocity
   - Pattern detection (complexity → time correlation)
   
2. **CAP-2:** Multi-Model Estimator (14-18 hrs)
   - Historical velocity model
   - Complexity-based estimation (cyclomatic → hours)
   - PERT (3-point estimation)
   - Monte Carlo simulation
   
3. **CAP-3:** Consensus Ranker + DoR Integration (10-14 hrs)
   - Weight models by confidence
   - Augment DoR with effort estimates
   
4. **CAP-4:** Capacity Dashboard (10-14 hrs)
   - D3.js timeline visualization
   - Burndown charts
   - Team capacity matrix

**Effort:** 44-60 hours  
**MCP Exposure:** ❌ VIOLATION — needs `cortex_estimate_effort` tool

---

#### **PHASE 13: Adaptive BLUF Communication** 📋 PLANNED
**Status:** TDD specification complete (16 tests), **NOT implemented**  
**Required Components:**
1. **BLUF-1:** Context Detector (8-12 hrs)
   - Persona detection (developer/manager/executive)
   - Complexity assessment
   - Urgency detection
   
2. **BLUF-2:** Response Formatter (10-14 hrs)
   - Template system (executive summary, technical detail, compliance)
   - Multi-tier formatting
   
3. **BLUF-3:** MasterOrchestrator Integration (10-12 hrs)
   - Wire adaptive formatting to all responses

**Effort:** 28-38 hours  
**MCP Exposure:** ✅ Can extend existing `cortex_process_request`

---

#### **PHASE 14: LENS Dashboard** 📋 APPROVED (Not Implemented)
**Status:** **SUPERSEDED** by Phase 14 V2 (static HTML approach)  
**Critical Issue:** Original spec used FastAPI + Alpine.js SPA. V2 simplifies to static HTML + JSON.  
**Required Implementation:**
1. **Entry Dashboard:** lens-dashboard.html (3 tabs: Repos, Domains, Quick Links)
2. **Repository Dashboards:** 6-tab per-repo analysis (static HTML + D3.js)
3. **Domain Dashboards:** Aggregated cross-repo intelligence
4. **Business Language Generator:** AST → business-friendly descriptions
5. **D3.js Visualizations:** Call graphs, import graphs, heatmaps, timelines

**Effort:** 15.5-19.5 days (3 developers)  
**MCP Exposure:** ✅ Can use existing `cortex_lens_analyze` tool  
**Critical Decision Required:** Static HTML (Phase 14 V2) vs. SPA (Phase 14 V1)?

---

#### **PHASE 15: Static Repository Visualization** 📋 APPROVED (Not Implemented)
**Status:** Full specification ready, depends on Phase 14  
**Key Architecture:**
- Tabbed entry: `lens-dashboard.html` (Repos | Domains | Quick Links)
- Multi-persona pages: `developers/`, `managers/`, `executives/`, `regulatory/`, `product/`
- Domain knowledge accumulation: `company/domains/{domain}/*.yaml`
- **NO Mermaid** (failed in Phase 14), **D3.js ONLY**
- Glassmorphism CSS (reference-architecture pattern)

**Effort:** 18-24 days  
**Blocker:** Requires Phase 14 completion  
**MCP Exposure:** ✅ Can extend LENS tools

---

#### **PHASE 16: Remediation Framework** 📋 ESTABLISHED (Partially Implemented)
**Status:** 3/7 permanent fixes implemented, prevention scripts ready  
**Completed:**
- ✅ AC-PERMANENT-FIX-010 (Business Principles in DoR)
- ✅ REM-001 (Documentation-Code Sync Check)
- ✅ REM-002 (Mock Target Verification)
- ✅ Pre-commit hooks integrated

**Pending:**
- AC-PERMANENT-FIX-011 (Emoji removal from prompts)
- AC-PERMANENT-FIX-012 (Governance rule enforcement)
- Comprehensive lessons-learned registry
- CI gate integration

**Effort:** 1-2 weeks  
**MCP Exposure:** ✅ Already covered

---

### ⚡ Challenge (MANDATORY)

**Your Implied Approach:** Execute all phases sequentially (11 → 12 → 13 → 14 → 15 → 16)  

**Counter-Proposal:** **Vertical Slice Strategy** — Implement ONE critical user journey end-to-end:

**Priority 1: Repository Analysis Journey (Phases 8.2 + 14 + 15 subset)**
1. Complete Phase 8.2 routing (2 weeks) → **UNBLOCKS user request flow**
2. Implement Phase 14 V2 static dashboard (3 weeks) → **DELIVERS user-facing value**
3. Defer Phases 11-13 (Cortical Memory, Capacity Planning, BLUF) → **NOT critical for MVP**
4. Implement Phase 15 Tier 1 only (repo dashboards, not domain aggregation) → **Reduces scope by 60%**

**Why Counter is Superior:**
1. **Faster Time-to-Value:** Users get working dashboards in 5 weeks vs. 12 weeks
2. **Risk Mitigation:** Vertical slice validates architecture before scaling
3. **MCP-First Compliance:** Surfaces ARCH-007 violations early (Phases 11-12 need MCP exposure)
4. **Incremental Validation:** Can test with CORTEX repo first, then expand
5. **Deferrable Complexity:** Cortical Memory (Phase 11) is over-engineered for current needs

**MCP Exposure Check:**
- ✅ Phase 8.2: Routing exposed via `cortex_process_request`
- ❌ Phase 11: **VIOLATION** — Extractors not MCP-exposed (needs 4 new tools)
- ❌ Phase 12: **VIOLATION** — Estimator not MCP-exposed (needs `cortex_estimate_effort`)
- ✅ Phase 13: Can extend existing tools
- ✅ Phase 14-15: Can use existing LENS tools

**Verdict:** **PIVOT to Vertical Slice** — Phases 11-13 are premature optimization. Ship user-facing dashboards first.

---

### ✅ Complete Fix (Vertical Slice Strategy)

#### **Sprint 1-2: Phase 8.2 Unified Routing (2 weeks)**
**Goal:** Route ALL user requests to orchestrator instances

**Tasks:**
1. Extend `intent-routing.yaml` with orchestrator references + keywords
2. Implement `OrchestratorLookup` (wiring.yaml → instances)
3. Enhance `IntentRouter.route()` with keyword extraction
4. Add `RoutingDecision.orchestrator_instance` field
5. Wire semantic ranking fallback (Phase 8.3 lite)
6. Execute integration tests (19 existing tests)

**Deliverable:** `cortex_process_request` routes to actual orchestrators, not generic handlers

**MCP Exposure:** `cortex_process_request` (already exists)

---

#### **Sprint 3-5: Phase 14 V2 Static Dashboard (3 weeks)**
**Goal:** Ship first working repository dashboard

**Tasks:**
1. Create lens-dashboard.html (tabbed entry point)
2. Generate static HTML dashboards for CORTEX repo
3. Implement `BusinessLanguageGenerator` (AST → business description)
4. Bundle D3.js locally (call graph, import graph, timeline, heatmap)
5. Build repository tile grid (Tab 1: Repositories)
6. Implement offline-first architecture (no CDN)
7. Add multi-persona navigation (developers/, managers/, executives/)

**Deliverable:** Working dashboard at `file:///path/to/CORTEX/cortex-lens/lens-dashboard.html`

**MCP Exposure:** `cortex_lens_analyze` (already exists), `cortex_generate_dashboard` (NEW)

---

#### **Sprint 6-7: Phase 15 Tier 1 — Repo Dashboards Only (2 weeks)**
**Goal:** Scale to multiple repositories, defer domain aggregation

**Tasks:**
1. Implement `cortex lens onboard /path/to/repo` CLI command
2. Generate per-repo dashboards in `cortex-lens/data/repos/{slug}/`
3. Update `repos.json` registry dynamically
4. Add empty state for "No repositories onboarded"
5. **DEFER:** Domain aggregation (Tab 2), Quick Links (Tab 3)
6. **DEFER:** domains knowledge accumulation

**Deliverable:** Multi-repo portfolio browser, 1-click onboarding

**MCP Exposure:** `cortex_onboard_repository` (NEW)

---

#### **Sprint 8: Phase 16 Remediation Completion (1 week)**
**Goal:** Close permanent fixes, integrate CI gates

**Tasks:**
1. Complete AC-PERMANENT-FIX-011 (remove emoji prompts)
2. Integrate REM-001/REM-002 into GitHub Actions
3. Document lessons-learned registry
4. Add pre-commit hook enforcement

**Deliverable:** Zero regression risk for routing + dashboard work

**MCP Exposure:** N/A (governance layer)

---

### 📊 Metrics

| Phase | Status | Effort | MCP Exposure | Priority |
|-------|--------|--------|--------------|----------|
| **8.2** | 40% | 2 weeks | ✅ Exists | **P0** |
| **11** | 5% (stubs) | 68-88 hrs | ❌ VIOLATION | P2 (defer) |
| **12** | 0% (spec only) | 44-60 hrs | ❌ VIOLATION | P2 (defer) |
| **13** | 0% (spec only) | 28-38 hrs | ✅ Extendable | P1 (defer) |
| **14** | 0% (superseded) | 3 weeks | ✅ Exists | **P0** |
| **15** | 0% (spec only) | 18-24 days | ✅ Exists | **P0** (Tier 1 only) |
| **16** | 43% | 1-2 weeks | ✅ Covered | P1 |

**Vertical Slice Total:** 8 weeks (vs. 12 weeks for sequential execution)

---

### ⏱️ Effort Breakdown

**Original Sequential Plan:**
- Phase 8.2: 2 weeks
- Phase 11: 2.5 weeks
- Phase 12: 1.5 weeks
- Phase 13: 1 week
- Phase 14: 3 weeks
- Phase 15: 4 weeks
- Phase 16: 1.5 weeks
- **Total: 15.5 weeks**

**Vertical Slice Plan:**
- Phase 8.2: 2 weeks
- Phase 14 V2: 3 weeks
- Phase 15 Tier 1: 2 weeks
- Phase 16: 1 week
- **Total: 8 weeks (48% faster)**
- **Deferred (Phases 11-13 + 15 Tier 2): 7.5 weeks**

---

**Autonomous execution note:** Per `cortex-architect.prompt.md`, no "proceed" gate. Analysis complete. Awaiting user decision: **Sequential** or **Vertical Slice**?