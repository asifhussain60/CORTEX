# Dashboard Schema Validation - Implementation Plan

**Plan ID:** PLAN-20251207-dashboard-schema-validation  
**Created:** December 7, 2025, 4:00 PM  
**Author:** Asif Hussain (via CORTEX Planning Orchestrator)  
**Status:** Active  
**Complexity:** Medium  
**Priority:** HIGH

---

## 📋 Executive Summary

Complete TDD-driven schema validation for CORTEX Dashboard collectors, ensuring all JSON outputs match mock schema exactly. Current progress: 6/20 tests passing (security ✅, health ✅). Remaining work focuses on tech-stack restructure, architecture/code-org/vendors schema additions, and generating 3 cross-collector aggregators (overview, executive-summary, reconciliation). Special attention to project-adaptive tabs: Engineering/Onboarding tab varies by project type, Executive Summary adapts to project nature.

---

## 🎯 Definition of Ready (DoR)

### Requirements Clarity
- ✅ **EXACT Goal:** Achieve 20/20 schema tests passing GREEN
- ✅ **Current State:** 6/20 passing (security 3/3 ✅, health 3/3 ✅, 14 remaining)
- ✅ **Reference Schema:** Mock folder (`cortex-brain/dashboards/data/repositories/mock/`) is authoritative
- ✅ **Test Harness:** `tests/test_collector_schema.py` (391 lines, validates exact key presence)
- ✅ **Validation Logic:** Tests load actual collector output from `repos/luum-fresh/` and compare to mock

### Dependencies
- ✅ **Security Collector:** Enhanced with 32 patterns, GREEN status validated
- ✅ **Health Collector:** Schema compliant with test_coverage, security_score, test_score fields
- ✅ **Test Infrastructure:** Schema validation framework operational
- ✅ **Luum-fresh Data:** Production repository available at `C:\PROJECTS\luum-fresh`
- ✅ **Collection Tooling:** `dashboard_collector.py` orchestrator functional

### Acceptance Criteria (Measurable)
1. ✅ **20/20 schema tests passing** - All collectors produce mock-compliant JSON
2. ✅ **Tech-stack restructure** - Categories: frontend, backend, database, devops (not languages)
3. ✅ **Architecture schema** - Includes patterns, layers, components, dependencies
4. ✅ **Code-organization schema** - Includes file_distribution, complexity_metrics, hotspots
5. ✅ **Vendors schema** - Includes api_integrations, services, summary
6. ✅ **Overview aggregator** - Combines health + tech + security + architecture
7. ✅ **Executive summary** - AI-generated tagline, what_it_does, recent_activity (project-adaptive)
8. ✅ **Reconciliation** - Gap analysis across collectors
9. ✅ **Dashboard validation** - Launch with `?source=luum-fresh`, verify all 8 tabs load
10. ✅ **Engineering tab adaptation** - Onboarding vs Engineering content based on project type

### TDD Requirements (Auto-Injected)
1. ✅ **TDD Mastery workflow** - RED→GREEN→REFACTOR mandatory
2. ✅ **RED phase validation** - Tests MUST fail before implementation
3. ✅ **Git checkpoints** - At RED, GREEN, REFACTOR phases
4. ✅ **Test coverage** - Schema validation for all 9 JSON outputs

### Security Checklist (OWASP Top 10 2025)
- ✅ **A01 Broken Access Control** - N/A (data collection only)
- ✅ **A02 Cryptographic Failures** - N/A (no sensitive data in schema)
- ✅ **A03 Injection** - N/A (no user input in collectors)
- ✅ **A04 Insecure Design** - Mitigated (mock schema as single source of truth)
- ✅ **A05 Security Misconfiguration** - N/A (no external APIs)
- ✅ **A06 Vulnerable Components** - N/A (Python stdlib only)
- ✅ **A07 Auth Failures** - N/A (no authentication)
- ✅ **A08 Data Integrity Failures** - Mitigated (schema validation tests)
- ✅ **A09 Logging Failures** - N/A (collectors log to stdout)
- ✅ **A10 SSRF** - N/A (no external requests)

---

## 🚀 Implementation Phases

### Phase 1: Tech-Stack Schema Restructure (RED→GREEN)
**Duration:** 2 hours  
**Status:** Pending

#### Tasks

**1.1 - Analyze tech-stack mock schema structure** (0.5h)
- Read `cortex-brain/dashboards/data/repositories/mock/tech-stack.json`
- Document required categories: frontend, backend, database, devops
- Document tech item fields: name, version, latest, status, category, cve_count, eol_date
- Document summary fields: total_technologies, outdated_count, current_count, critical_cves
- **AC:** Schema structure documented in task notes

**1.2 - Update tech-stack tests to load actual files** (0.5h)
- Modify `tests/test_collector_schema.py` lines 225-260
- Replace hardcoded stubs with `load_collector_output("tech-stack.json")`
- Run tests to confirm RED phase (3/3 failing)
- **AC:** Tests fail with clear error messages about missing keys

**1.3 - Restructure TechStackCollector output** (1h)
- Locate `src/orchestrators/enhanced_collectors.py` TechStackCollector class
- Replace `languages` array with 4 category arrays (frontend, backend, database, devops)
- Add detection logic: C#→backend, SQL→database, JavaScript→frontend, Docker→devops
- Add 7 fields to each tech item (version, latest, status, category, cve_count, eol_date)
- Add summary object with 4 aggregate counts
- **AC:** Collector produces mock-compliant structure

**1.4 - Regenerate tech-stack.json and verify GREEN** (0.5h)
- Run: `python -c "from pathlib import Path; from src.orchestrators.enhanced_collectors import TechStackCollector; import json; ..."`
- Run: `pytest tests/test_collector_schema.py::TestTechStackSchema -v`
- **AC:** 3/3 tech-stack tests passing GREEN

**DoD for Phase 1:**
- ✅ 3/3 tech-stack tests passing
- ✅ Collector restructure complete
- ✅ Git checkpoint created: `git add src/orchestrators/enhanced_collectors.py tests/test_collector_schema.py cortex-brain/dashboards/data/repos/luum-fresh/tech-stack.json && git commit -m "feat(dashboard): Tech-stack schema GREEN - 9/20 passing"`

---

### Phase 2: Architecture, Code-Org, Vendors Schema Fixes (RED→GREEN)
**Duration:** 2 hours  
**Status:** Pending

#### Tasks

**2.1 - Fix architecture.json schema** (0.5h)
- Read mock: `cortex-brain/dashboards/data/repositories/mock/architecture.json`
- Add 4 root keys: patterns, layers, components, dependencies
- Update test to load actual file
- Modify `src/dashboard/data/architecture_collector.py` to add missing keys
- Regenerate and verify GREEN (1/1 test passing)
- **AC:** Architecture schema test passing

**2.2 - Fix code-organization.json schema** (0.5h)
- Read mock: `cortex-brain/dashboards/data/repositories/mock/code-organization.json`
- Add 3 root keys: file_distribution, complexity_metrics, hotspots
- Update test to load actual file
- Modify `src/dashboard/data/code_org_collector.py` to add missing keys
- Regenerate and verify GREEN (1/1 test passing)
- **AC:** Code-organization schema test passing

**2.3 - Fix vendors.json schema** (0.5h)
- Read mock: `cortex-brain/dashboards/data/repositories/mock/vendors.json`
- Add 3 root keys: api_integrations, services, summary
- Update test to load actual file
- Modify `src/dashboard/data/vendor_collector.py` to add missing keys
- Regenerate and verify GREEN (1/1 test passing)
- **AC:** Vendors schema test passing

**2.4 - Run full collector suite on luum-fresh** (0.5h)
- Run: `python -m src.orchestrators.dashboard_collector --path "C:\PROJECTS\luum-fresh" --output luum-fresh --skip-consolidation`
- Verify all 6 collectors complete successfully
- **AC:** All collector JSON files updated with compliant schemas

**DoD for Phase 2:**
- ✅ 3/3 additional tests passing (architecture, code-org, vendors)
- ✅ Total progress: 12/20 tests passing
- ✅ Git checkpoint created: `git add src/dashboard/data/*.py tests/test_collector_schema.py cortex-brain/dashboards/data/repos/luum-fresh/*.json && git commit -m "feat(dashboard): Architecture/Code-Org/Vendors schema GREEN - 12/20 passing"`

---

### Phase 3: Overview Aggregator (Cross-Collector)
**Duration:** 1.5 hours  
**Status:** Pending

#### Tasks

**3.1 - Analyze overview.json mock structure** (0.5h)
- Read mock: `cortex-brain/dashboards/data/repositories/mock/overview.json`
- Document 6 root keys: overall_health, key_metrics, health_categories, critical_issues, composition, trends
- Document data sources: health-data.json + tech-stack.json + security.json + architecture.json
- **AC:** Overview schema documented with source mappings

**3.2 - Create overview aggregator script** (0.5h)
- Create: `src/dashboard/aggregators/overview_aggregator.py`
- Load 4 source files (health, tech, security, architecture)
- Aggregate overall_health (weighted average: security 40%, health 30%, complexity 30%)
- Aggregate key_metrics (6 metrics from sources)
- Aggregate health_categories (3 categories with scores)
- Extract critical_issues (from security + health)
- Build composition (language breakdown from tech-stack)
- Build trends (from health trends)
- **AC:** Aggregator produces mock-compliant overview.json

**3.3 - Update overview tests and verify GREEN** (0.5h)
- Update `tests/test_collector_schema.py` lines 65-120 to load actual file
- Run aggregator to generate overview.json
- Run: `pytest tests/test_collector_schema.py::TestOverviewSchema -v`
- **AC:** 4/4 overview tests passing GREEN

**DoD for Phase 3:**
- ✅ Overview aggregator functional
- ✅ 4/4 overview tests passing
- ✅ Total progress: 16/20 tests passing
- ✅ Git checkpoint created: `git add src/dashboard/aggregators/overview_aggregator.py tests/test_collector_schema.py cortex-brain/dashboards/data/repos/luum-fresh/overview.json && git commit -m "feat(dashboard): Overview aggregator GREEN - 16/20 passing"`

---

### Phase 4: Executive Summary Aggregator (Project-Adaptive)
**Duration:** 2 hours  
**Status:** Pending

#### Tasks

**4.1 - Analyze executive-summary.json mock structure** (0.5h)
- Read mock: `cortex-brain/dashboards/data/repositories/mock/executive-summary.json`
- Document 6 root keys: tagline, what_it_does, recent_activity, composition, tech_stack_summary, health_indicators
- Identify project-adaptive fields: tagline (reflects project type), what_it_does (business domain), recent_activity (commit analysis)
- Document data sources: All collectors + git log analysis
- **AC:** Executive summary schema documented with adaptation rules

**4.2 - Implement project type detection** (0.5h)
- Analyze tech-stack to detect project type:
  - **Web Application:** Frontend + backend frameworks present
  - **API Service:** Backend only, no frontend
  - **Desktop Application:** WinForms/WPF/Electron detected
  - **Mobile Application:** Xamarin/React Native detected
  - **Library/Package:** No main executable, package.json with library keywords
  - **Legacy System:** Old frameworks (.NET Framework, Classic ASP)
- Store project type in context for adaptive rendering
- **AC:** Project type detection function returns correct classification

**4.3 - Create executive summary aggregator** (0.5h)
- Create: `src/dashboard/aggregators/executive_summary_aggregator.py`
- Generate adaptive tagline based on project type + tech stack
- Generate what_it_does from README.md analysis + architecture data
- Generate recent_activity from git log (last 30 days)
- Aggregate composition from tech-stack
- Build tech_stack_summary (5 key technologies)
- Build health_indicators (3 metrics from health + security)
- **AC:** Aggregator produces project-adaptive executive summary

**4.4 - Update executive summary tests and verify GREEN** (0.5h)
- Update `tests/test_collector_schema.py` lines 121-155 to load actual file
- Run aggregator to generate executive-summary.json
- Run: `pytest tests/test_collector_schema.py::TestExecutiveSummarySchema -v`
- **AC:** 2/2 executive summary tests passing GREEN

**DoD for Phase 4:**
- ✅ Executive summary aggregator functional with project adaptation
- ✅ 2/2 executive summary tests passing
- ✅ Total progress: 18/20 tests passing
- ✅ Git checkpoint created: `git add src/dashboard/aggregators/executive_summary_aggregator.py tests/test_collector_schema.py cortex-brain/dashboards/data/repos/luum-fresh/executive-summary.json && git commit -m "feat(dashboard): Executive summary aggregator GREEN with project adaptation - 18/20 passing"`

---

### Phase 5: Reconciliation Aggregator & Dashboard Validation
**Duration:** 1.5 hours  
**Status:** Pending

#### Tasks

**5.1 - Create reconciliation aggregator** (0.5h)
- Create: `src/dashboard/aggregators/reconciliation_aggregator.py`
- Read mock: `cortex-brain/dashboards/data/repositories/mock/reconciliation.json`
- Document 3 root keys: status, gaps (array), recommendations (array)
- Compare all collectors for inconsistencies:
  - Health vs Security score discrepancies
  - Tech-stack vs Code-org file count mismatches
  - Architecture components vs Code-org directory structure
- Generate gap array with severity, description, affected_files
- Generate recommendations array with priority, action, rationale
- **AC:** Reconciliation aggregator identifies cross-collector gaps

**5.2 - Update reconciliation test and verify GREEN** (0.5h)
- Update `tests/test_collector_schema.py` lines 370-385 to load actual file
- Run aggregator to generate reconciliation.json
- Run: `pytest tests/test_collector_schema.py::TestReconciliationSchema -v`
- **AC:** 1/1 reconciliation test passing GREEN

**5.3 - Copy validated data to dashboard folder** (0.25h)
- Run: `Copy-Item -Recurse "cortex-brain/dashboards/data/repos/luum-fresh/*" "cortex-brain/dashboards/data/repositories/luum-fresh/"`
- Verify all 9 JSON files present in repositories/luum-fresh/
- **AC:** Dashboard data folder contains complete validated dataset

**5.4 - Launch dashboard and validate all tabs** (0.25h)
- Run: `.\launch-dashboard.ps1` or `python -m src.orchestrators.dashboard_launcher`
- Open: `http://localhost:8080/ui/index.html?source=luum-fresh`
- Verify 8 tabs load without errors:
  - ✅ Overview (overall health, key metrics)
  - ✅ Executive Summary (project-adaptive tagline)
  - ✅ Health (test coverage, code quality)
  - ✅ Security (vulnerabilities, OWASP)
  - ✅ Tech Stack (4 categories, summary)
  - ✅ Architecture (patterns, layers)
  - ✅ Code Organization (hotspots, complexity)
  - ✅ Engineering/Onboarding (adaptive based on project type)
- Take screenshots of key tabs for validation
- **AC:** All 8 dashboard tabs render successfully with luum-fresh data

**DoD for Phase 5:**
- ✅ Reconciliation aggregator functional
- ✅ 1/1 reconciliation test passing GREEN
- ✅ 20/20 schema tests passing (100% GREEN)
- ✅ Dashboard launches successfully with luum-fresh data
- ✅ All 8 tabs validated (including adaptive Engineering/Onboarding)
- ✅ Git checkpoint created: `git add src/dashboard/aggregators/reconciliation_aggregator.py tests/test_collector_schema.py cortex-brain/dashboards/data/ && git commit -m "feat(dashboard): Schema validation 20/20 GREEN + dashboard validated"`

---

## 📊 Definition of Done (DoD)

### Code Quality
- ✅ **20/20 schema tests passing** - Full GREEN status
- ✅ **No hardcoded stubs** - All tests validate actual collector output
- ✅ **Consistent structure** - All collectors follow mock schema exactly
- ✅ **Type safety** - All JSON fields match expected types (dict, list, int, float, str)

### Testing
- ✅ **Schema validation** - 20 tests covering all 9 JSON outputs
- ✅ **Integration tests** - Dashboard loads all tabs without errors
- ✅ **Data quality** - Luum-fresh data displays correctly in UI
- ✅ **Edge cases** - Empty arrays, null values handled gracefully

### Documentation
- ✅ **Schema reference** - Mock folder documented as authoritative
- ✅ **Collector guides** - README updated with schema requirements
- ✅ **Test results** - Screenshot evidence of 20/20 GREEN
- ✅ **Dashboard validation** - Screenshots of all 8 tabs

### TDD Requirements (Auto-Injected)
- ✅ **Tests pass** - 20/20 schema validation tests GREEN
- ✅ **Code reviewed** - Self-review of all aggregator implementations
- ✅ **Documentation complete** - Plan updated with completion notes
- ✅ **Git checkpoints** - 5 checkpoints across all phases

---

## 🎯 Success Metrics

### Quantitative
- **Test Coverage:** 20/20 schema tests passing (100%)
- **Collector Compliance:** 9/9 JSON outputs match mock schema
- **Dashboard Functionality:** 8/8 tabs load successfully
- **Data Quality:** 0 schema validation errors in luum-fresh dataset
- **Performance:** Dashboard loads <2 seconds for all tabs

### Qualitative
- **Project Adaptation:** Executive summary accurately reflects luum-fresh project type (.NET SOAP service)
- **Engineering Tab:** Adapts content based on legacy project nature
- **Schema Consistency:** All collectors use identical key naming conventions
- **Developer Experience:** Schema tests provide clear error messages for debugging

---

## 🔧 Technical Notes

### Project-Adaptive Rendering

**Engineering/Onboarding Tab:**
- **Modern Projects:** Shows onboarding wizard, setup guides, contribution workflow
- **Legacy Projects (like luum-fresh):** Shows engineering notes, architecture diagrams, refactoring opportunities
- **Detection Logic:** Legacy if .NET Framework <4.8, Classic ASP, SOAP services, or avg file age >5 years

**Executive Summary Tagline:**
- **Web App:** "Modern web application built with [framework]"
- **API Service:** "RESTful API service powering [domain]"
- **Legacy System:** "Enterprise-grade [technology] system serving [business domain]"
- **Luum-fresh Example:** "Enterprise-grade .NET SOAP service serving benefits management"

### Schema Validation Strategy
1. **RED Phase:** Update tests to load actual files, verify failures
2. **GREEN Phase:** Fix collectors to add missing fields, verify passes
3. **REFACTOR Phase:** Consolidate duplicate logic, optimize performance

### File Organization
```
cortex-brain/dashboards/data/
├── repositories/mock/          # Authoritative schema (9 files)
├── repos/luum-fresh/           # Actual collector output (9 files)
└── repositories/luum-fresh/    # Dashboard-ready data (copy of repos/)
```

---

## 🚨 Risks & Mitigation

### Risk 1: Tech-Stack Restructure Complexity
**Impact:** HIGH  
**Likelihood:** MEDIUM  
**Mitigation:** Incremental approach - update one category at a time, test after each change

### Risk 2: Aggregator Data Source Mismatches
**Impact:** MEDIUM  
**Likelihood:** MEDIUM  
**Mitigation:** Validate source file presence before aggregation, use defensive defaults

### Risk 3: Dashboard UI Breaks with New Schema
**Impact:** HIGH  
**Likelihood:** LOW  
**Mitigation:** Schema matches mock folder which dashboard UI already consumes

### Risk 4: Luum-fresh Collection Time
**Impact:** LOW  
**Likelihood:** MEDIUM  
**Mitigation:** Use `--skip-consolidation` flag, run individual collectors as needed

---

## 📅 Timeline

**Total Duration:** 9 hours  
**Target Completion:** December 8, 2025

- **Phase 1:** 2 hours (Tech-stack restructure)
- **Phase 2:** 2 hours (Architecture/Code-org/Vendors)
- **Phase 3:** 1.5 hours (Overview aggregator)
- **Phase 4:** 2 hours (Executive summary with adaptation)
- **Phase 5:** 1.5 hours (Reconciliation + validation)

---

## 🔍 Approval & Next Steps

### Plan Approval
- [ ] Review all 5 phases for completeness
- [ ] Verify DoR/DoD criteria are measurable
- [ ] Confirm timeline is realistic
- [ ] Approve plan for execution

### Immediate Next Action
Once approved, execute Phase 1, Task 1.1:
```bash
# Analyze tech-stack mock schema
cat cortex-brain/dashboards/data/repositories/mock/tech-stack.json | python -m json.tool
```

---

**Plan Status:** ACTIVE - Awaiting Approval  
**Last Updated:** December 7, 2025, 4:00 PM
