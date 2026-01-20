# CORTEX Unified Deployment Strategy: Complete Implementation Plan

**Document Type:** Strategic Phase Plan  
**Authority:** cortex-builder.prompt.md v2.1 SSOT  
**Date:** 2026-01-19  
**Status:** Ready for Implementation  

---

## EXECUTIVE SUMMARY

Replace fragmented, repo-embedded deployment model with **centralized, reference-based architecture**: CORTEX as top-level service consumed via lightweight CORTEX.prompt in any repo. One system, one version, one audit trail. Enables unlimited scalability, unified intelligence distribution, and predictable governance.

---

## ARCHITECTURE DECISION

### Current (WRONG) Model
```
company-repo/
  └── CORTEX/ ← Full system cloned (N repos = N copies)
      ├── cortex CLI
      ├── governance.db
      └── orchestrators
```

**Problems:** Fragmented versioning, O(N) maintenance burden, governance DB split

### Proposed (CORRECT) Model
```
cortex-ai/cortex (TOP-LEVEL REPO - Source of Truth)
  ├── orchestrators/ (Master, LENS, ResponseComposer, etc.)
  ├── mcp-tools/ (all MCP implementations)
  ├── cortex_brain/tier0/tier1/tier2 (governance engine)
  ├── .github/prompts/CORTEX.prompt (THE deployment artifact)
  ├── api/telemetry (feedback collection endpoint)
  └── [Core CORTEX system - single version]

company-repo-1, company-repo-2, ... company-repo-N
  └── .github/prompts/CORTEX.prompt ← One file (reference only)
      (Points to cortex-ai/cortex main branch)
```

**Benefits:** Single version, O(1) overhead, unified governance, automatic updates

---

## PHASE STRUCTURE: UNIFIED DEPLOYMENT (PHASE-UNIFIED-DEPLOY)

### Overview
**10 ACs across 4 sections | ~80 hours | P0 Priority | Future-proofed**

Split implementation across:
- **SECTION A:** Infrastructure & Telemetry (3 ACs) - Server-side architecture
- **SECTION B:** Prompt-Based Distribution (3 ACs) - Client-side reference system  
- **SECTION C:** Intelligence Update Protocol (2 ACs) - Manifest & versioning
- **SECTION D:** Feedback Loop & Auto-Issue Generation (2 ACs) - Operational analytics

---

## DETAILED ACCEPTANCE CRITERIA

### SECTION A: Infrastructure & Telemetry Foundation

#### AC-UNIFIED-DEPLOY-001-01: Centralized CORTEX Repository Setup
**What:** Consolidate CORTEX into cortex-ai/cortex as definitive source

**Acceptance Criteria:**
- cortex-ai/cortex repo has clean separation:
  - `/orchestrators` - Master, LENS, ResponseComposer, all patterns
  - `/mcp-tools` - All MCP tool implementations
  - `/cortex_brain/tierX` - Governance + knowledge tiers
  - `/.github/prompts/CORTEX.prompt` - Distribution artifact
- Single version numbering (semantic versioning: major.minor.patch)
- VERSION file at repo root (read by all consumers)
- Git history retained, no rewriting
- Tests: ✅ 20 tests (repo structure validation, file placement checks)
- Governance: CORE-028 ✓, CORE-011 ✓, CORE-012 ✓
- **Hours:** 8 | **Test Count:** 20

#### AC-UNIFIED-DEPLOY-001-02: Telemetry Endpoint Implementation
**What:** Server-side aggregation pipeline for operational data

**Acceptance Criteria:**
- REST endpoint: `api.cortex-ai.io/v1/telemetry/ingest`
- Accepts batch JSON (event arrays):
  - Execution events (timing, tools, outcomes)
  - Error events (categories, reproducibility)
  - Performance events (memory, CPU, cache)
  - User feedback (optional, explicit consent)
- Data validation:
  - Schema enforcement (no raw user code)
  - PII scrubbing (hashed identifiers)
  - Secret detection (blocked transmission)
- Response: `{ status: "ok", processed: N, rejected: M }`
- Tests: ✅ 25 tests (schema validation, data scrubbing, error handling)
- Governance: CORE-013 ✓ (no bare except), CORE-011 ✓ (typed)
- **Hours:** 12 | **Test Count:** 25

#### AC-UNIFIED-DEPLOY-001-03: Aggregation Engine & Issue Auto-Generation
**What:** Server processes telemetry, generates GitHub issues for patterns

**Acceptance Criteria:**
- Aggregation logic:
  - Deduplicates events (same error_id + environment + 1h window = 1 entry)
  - Computes impact score: (frequency × severity × reproducibility)
  - Identifies patterns (Top 10 errors this week, performance trends)
- GitHub issue auto-creation:
  - Triggered when impact_score > threshold
  - Issue title: `[TELEMETRY] <Pattern Name> (<Impact Level>)`
  - Issue body: pattern details, affected environments, recommendations
  - Labels: `telemetry-generated`, `p1-critical` (auto-assigned)
- Tests: ✅ 30 tests (aggregation logic, deduplication, scoring, issue payload)
- Governance: CORE-008 ✓ (tests first), CORE-011 ✓
- **Hours:** 14 | **Test Count:** 30

---

### SECTION B: Prompt-Based Distribution System

#### AC-UNIFIED-DEPLOY-002-01: CORTEX.prompt Template & Versioning
**What:** Define standard prompt template consumed by all company repos

**Acceptance Criteria:**
- Template `.github/prompts/CORTEX.prompt`:
  - Loads from `cortex-ai/cortex/main/.github/prompts/CORTEX.prompt`
  - Contains orchestrator definitions (Master, LENS, etc.)
  - Contains MCP tool registry (with refs to cortex-ai/cortex)
  - Contains governance rules (CORE-001 through CORE-037)
  - Contains response templates (formatting, headers, footers)
  - Version hash in header (for cache busting)
- File size: <5KB (gzipped, optimized for Copilot)
- Caching strategy:
  - GitHub raw.githubusercontent.com + 1h TTL
  - Local fallback (cached previous version)
- Tests: ✅ 18 tests (schema validation, size checks, version hashing)
- Governance: CORE-028 ✓ (kebab-case, ≤25 chars)
- **Hours:** 10 | **Test Count:** 18

#### AC-UNIFIED-DEPLOY-002-02: Reference Template for Child Repos
**What:** One-file setup script for adoption in any company repo

**Acceptance Criteria:**
- Template repo available: `cortex-ai/cortex-templates/child-repo-setup.md`
- Instructions:
  1. Copy `.github/prompts/CORTEX.prompt` to target repo
  2. Add `@cortex` to `.github/copilot-instructions.md`
  3. Done (no manual installation)
- Validation script:
  - Checks file in correct location
  - Verifies CORTEX.prompt loads without error
  - Reports CORTEX version
  - Runs basic MCP tool tests
- Tests: ✅ 22 tests (file placement, validation script, error cases)
- Governance: CORE-012 ✓ (docstrings), CORE-028 ✓
- **Hours:** 8 | **Test Count:** 22

#### AC-UNIFIED-DEPLOY-002-03: Multi-Repo Context Switching
**What:** Copilot can analyze code in any repo context, all report to cortex-ai/cortex

**Acceptance Criteria:**
- CORTEX.prompt detects repo context (via `.git/config`)
- Maintains execution state per repo:
  - Separate cache for each repo (no pollution)
  - Shared governance.db (read-only reference from cortex-ai/cortex)
  - Local telemetry batches per repo
- Context switching:
  - User moves to different repo → Copilot automatically switches context
  - No state loss, no manual reset
- Tests: ✅ 20 tests (context detection, state isolation, switching scenarios)
- Governance: CORE-011 ✓ (type hints), CORE-013 ✓
- **Hours:** 12 | **Test Count:** 20

---

### SECTION C: Intelligence Update Protocol

#### AC-UNIFIED-DEPLOY-003-01: Manifest System & Version Management
**What:** Track CORTEX intelligence versions, enable deterministic upgrades

**Acceptance Criteria:**
- Manifest file: `cortex-ai/cortex/manifest.json` (generated on each release)
  - Schema version, release timestamp
  - Orchestrators: [name, version, fingerprint, breaking changes]
  - Workflows: [name, version, dependencies]
  - MCP tools: [name, version, signature changes]
  - Brain tiers: [tier, rules added/modified/removed]
  - Migrations: [required data transformations]
- Manifest validation:
  - JSON schema strict (fail fast on invalid)
  - All orchestrators listed must exist in repo
  - All dependencies resolvable (no circular deps)
- Intelligence diff computation:
  - Compare local vs remote manifest
  - Categorize: breaking, major, minor, patch
  - Impact scoring (user-visible relevance)
- Tests: ✅ 28 tests (schema validation, diff computation, impact scoring)
- Governance: CORE-011 ✓, CORE-012 ✓
- **Hours:** 12 | **Test Count:** 28

#### AC-UNIFIED-DEPLOY-003-02: Copilot Chat Intelligence Display
**What:** Show new intelligence to users inline in chat (no markdown files)

**Acceptance Criteria:**
- On Copilot invocation, detect manifest diff
- Display formatted summary:
  ```
  [CORTEX Intelligence Update]
  ✅ CORTEX v2.5 → v2.6 (3 new orchestrators, +12 rules, no breaking changes)
  
  📦 NEW
  • QueryOptimizer (pattern recognition)
  • CacheManager (intelligent caching)
  • AsyncComposer (non-blocking)
  
  🔄 MODIFIED
  • MasterOrchestrator: +15% complexity accuracy
  
  ✖️ DEPRECATED (5-version compat window)
  • LegacyRouter (use MasterOrchestrator)
  ```
- Display once per session, don't spam
- Include: version, count of changes by category, impact summary
- Tests: ✅ 16 tests (formatting, truncation, categorization, de-duplication)
- Governance: CORE-001 ✓ (keep concise)
- **Hours:** 8 | **Test Count:** 16

---

### SECTION D: Feedback Loop & Continuous Improvement

#### AC-UNIFIED-DEPLOY-004-01: Operational Data Collection & Transmission
**What:** Capture deterministic telemetry from all repos, aggregate centrally

**Acceptance Criteria:**
- Local collection (CORTEX.prompt level):
  - Execute events: timing, tools, outcomes (no user code)
  - Error events: category, reproducibility, environment signature
  - Performance events: aggregate metrics (memory, CPU, cache)
  - User feedback: optional, explicit consent, expires 30 days
- Storage: SQLite in user's Copilot cache (expires with cache clear)
- Batching logic:
  - Accumulate 100 events OR 24 hours
  - Auto-transmit when batch threshold met
  - User can also manually: `@cortex telemetry --transmit`
- Transmission:
  - HTTPS POST to cortex-ai/cortex/api/telemetry/ingest
  - User consent verified (stored locally, expires 30 days)
  - Encrypted payload (TLS only)
  - Transmission logged (success/failure, retry logic)
- Tests: ✅ 32 tests (collection accuracy, batching, transmission, retry)
- Governance: CORE-008 ✓ (tests first), CORE-013 ✓ (error handling)
- **Hours:** 16 | **Test Count:** 32

#### AC-UNIFIED-DEPLOY-004-02: Feedback Analysis & Team Action Loop
**What:** Aggregate insights drive CORTEX development prioritization

**Acceptance Criteria:**
- Weekly aggregation run (server-side):
  - Deduplicate error patterns (global view across all repos)
  - Compute trend scores (is error increasing/decreasing?)
  - Map to GitHub issues (new issues for top patterns)
- Insights dashboard (cortex-ai/cortex GitHub project):
  - Top 10 error patterns this week (with trend)
  - Performance degradation alerts (tool X slower by 20%)
  - Capability gaps (user feedback: "need X")
  - Orchestrator effectiveness scores (accuracy per orchestrator)
- Integration:
  - Auto-create issues for high-impact patterns
  - Link issues to telemetry data (reproducibility, environments)
  - Prioritize backlog based on impact (not gut feel)
- Tests: ✅ 26 tests (aggregation logic, dashboard data, issue generation)
- Governance: CORE-011 ✓, CORE-012 ✓
- **Hours:** 14 | **Test Count:** 26

---

## IMPLEMENTATION ROADMAP

### Phase Timeline

| Phase | Timeline | What | ACs |
|-------|----------|------|-----|
| **Infrastructure** | Weeks 1-2 | Centralized repo, telemetry endpoint, aggregation | 001-01 through 001-03 |
| **Distribution** | Weeks 3-4 | CORTEX.prompt, child repo setup, context switching | 002-01 through 002-03 |
| **Intelligence** | Weeks 5-6 | Manifest system, diff engine, chat display | 003-01 through 003-02 |
| **Feedback** | Weeks 7-8 | Data collection, transmission, analysis loop | 004-01 through 004-02 |
| **Testing & Hardening** | Week 9 | End-to-end integration tests, production readiness | 240+ aggregate tests |
| **Launch** | Week 10 | Release, documentation, team training | Go-to-market |

---

## FUTURE-THINKING EXTENSIONS (Not in Scope, But Designed For)

### Phase 2: Multi-Tenant Intelligence (Post-Launch)
- Allow teams to contribute custom orchestrators to cortex-ai/cortex
- Governance approval workflow for new intelligence
- Version-locked orchestrator bundles per team

### Phase 3: AI-Powered Optimization (Post-Launch)
- ML clustering of telemetry patterns (not implemented, designed for)
- Recommendation engine: "Orchestrator X would be 40% faster for your patterns"
- Predictive error detection (early warning, not reactive)

### Phase 4: Cross-Company Intelligence Marketplace (Future)
- Secure, federated telemetry from external partners
- Privacy-preserving pattern sharing (aggregate only)
- Competitive intelligence: "Industry best practices for your use case"

---

## GOVERNANCE COMPLIANCE

### Core Rules Applied
- ✅ **CORE-001:** Response format concise (this document is reference-level)
- ✅ **CORE-008:** Tests defined before implementation (24 test files to create)
- ✅ **CORE-011:** All functions type-hinted (enforced in all code)
- ✅ **CORE-012:** Google docstrings on all public APIs
- ✅ **CORE-013:** No bare `except:` clauses (error handling strict)
- ✅ **CORE-027:** AC lifecycle: AC_START → AC_EXECUTE → AC_COMPLETE (audit trail per AC)
- ✅ **CORE-028:** Kebab-case filenames, ≤25 characters

### Audit Trail
- Each AC will log: AC_START (init), AC_EXECUTE (per test), AC_COMPLETE (final)
- Global hash chain verified at end of phase
- Governance.db updated with all AC-IDs

### Phase Lock Criteria
- ALL 10 ACs completed (status: COMPLETED)
- 100% test pass rate (240+ tests passing)
- Hash chain integrity verified (unbroken)
- Zero governance violations
- Documentation updated (phase markdown only, no docs/)

---

## RISKS & MITIGATIONS

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| CORTEX.prompt becomes too large | Medium | Copilot context bloat | Size limit enforced (5KB), compression |
| GitHub API rate limits on issue auto-creation | Low | Telemetry processing stalls | Queue system, batch window >1h |
| Users disable telemetry entirely | Medium | Feedback loop breaks | Transparent value messaging, opt-in window |
| Manifest version skew (local vs remote) | Low | Orchestrator mismatch | Validation tests, rollback procedure |
| Network outage blocks Copilot invocation | Low | Cascading failures | Local fallback (previous manifest cached) |

---

## SUCCESS METRICS

### Quantitative
- **Deployment friction:** <5 minutes per repo (vs. 30+ currently)
- **Adoption rate:** 80%+ of company repos within 90 days
- **Update latency:** <1h from cortex-ai/cortex push to user availability
- **Telemetry quality:** 95%+ of events parseable, <1% data loss
- **Mean time to issue:** <4h from pattern detection to GitHub issue creation

### Qualitative
- **User satisfaction:** "CORTEX updates are automatic and invisible"
- **Team efficiency:** "We prioritize development based on real impact, not guesses"
- **Governance confidence:** "All users run same version, audit trail is unified"

---

## DELIVERABLES

### Code Artifacts
- `cortex-ai/cortex/.github/prompts/CORTEX.prompt` (distribution template)
- `cortex-ai/cortex/api/telemetry/` (endpoint + aggregation)
- `cortex-ai/cortex/manifest.json` (released with each version)
- `cortex-ai/cortex/lib/manifest-diff.py` (diff engine)
- `cortex-ai/cortex/tests/telemetry/` (240+ test suite)

### Documentation
- `cortex-ai/cortex/docs/DEPLOYMENT-UNIFIED.md` (this plan + implementation notes)
- `cortex-ai/cortex/docs/ADOPTION-GUIDE.md` (one-file setup for child repos)
- `cortex-ai/cortex/docs/TELEMETRY-PRIVACY.md` (data handling, compliance)

### Process
- GitHub project board: "CORTEX Unified Deployment"
- Weekly standup schedule (Tuesdays 10am PT)
- Telemetry insights dashboard (live after AC-001-03)

---

## TRANSITION PLAN: OLD → NEW

### For Existing CORTEX Deployments
1. **No forced migration:** Old CORTEX CLI still works (5-version compat)
2. **Gradual adoption:** Teams can switch to .github/prompts/CORTEX.prompt anytime
3. **Data migration:** Old governance.db → new central DB (one-time, non-breaking)
4. **Rollback:** Always possible (run old version, local .git history intact)

### End-of-Life
- CORTEX CLI deprecated (announce at launch, sunset in 6 months)
- All orchestrators moved to cortex-ai/cortex (automatic for new users)
- Old CORTEX/ folders can be safely deleted (no longer needed)

---

## FINAL RECOMMENDATION

This unified deployment strategy is **production-ready to implement**, **future-proof for multi-tenant / marketplace extensions**, and **compliant with all governance rules**. It replaces a broken O(N) model with a sustainable O(1) architecture.

**Proceed with implementation? YES** ✅

