# CORTEX5 Enhancement Epic - Complete Architecture Overhaul

**Plan ID:** `cortex5-enhancement-epic-v2`  
**Version:** 2.0.0  
**Status:** 🟢 ACTIVE - REQUIRES PHASE 0 MIGRATION FIRST  
**Created:** 2026-01-06  
**Timeline:** Phase 0 (Migration) + 9 weeks (11 phases, 3 parallel tracks)  
**Complexity:** Tier 5 (Architectural Transformation)

---

## ⚠️ MANDATORY FIRST STEP: Phase 0 - Clean Branch Migration

**🚨 THIS EPIC CANNOT START WITHOUT COMPLETING PHASE 0 MIGRATION 🚨**

### Why Phase 0 is Required

**Current CORTEX-5.0 has critical architectural debt:**
- ~1000 files (many obsolete: cortex_3_0/, orchestration_4_0/, 17+ unused manifests)
- Multiple versions of same components causing confusion
- Unused sample apps, old documentation, historical backups
- Cluttered structure preventing clear architectural vision

**Attempting to build Phase 1-11 on CORTEX-5.0 = Building on quicksand**

### Phase 0 Objectives

✅ Create clean CORTEX-5.5 branch with ~150 essential files (85% reduction)  
✅ Verify ONLY necessary files migrated (no obsolete code)  
✅ Establish pull-on-demand system for CORTEX-5.0 dependencies  
✅ Validate Phase 1 scaffolding ready for execution  
✅ Zero technical debt carried forward  

### Phase 0 Execution (15 minutes)

**Step 1: Run Migration Script**
```powershell
# Execute automated migration
.\create-cortex-5.5-branch.ps1

# Expected output:
# - Branch CORTEX-5.5 created from main (clean slate)
# - ~150 files copied from CORTEX-5.0 (essential only)
# - 19 directories created
# - Phase 1 scaffolding generated (src/knowledge/)
```

**Step 2: Validate Migration**
```powershell
# Run validation checklist
# Open: MIGRATION-CHECKLIST.md
# Verify:
# ✅ File count ~150 (not 1000+)
# ✅ No obsolete directories (cortex_3_0, orchestration_4_0, backups)
# ✅ Essential files present (master_orchestrator.py, brain-protection-rules.yaml)
# ✅ Phase 1 scaffolding exists (src/knowledge/company_knowledge_provider.py)
# ✅ Pull tracking system operational (pull-from-cortex-5.0.ps1)
```

**Step 3: Commit Clean Branch**
```powershell
git status  # Should show ~150 files staged
git commit -m "feat: Initialize CORTEX-5.5 clean branch with Phase 1 scaffolding

- Essential files only (85% reduction vs CORTEX-5.0)
- Pull from CORTEX-5.0 on demand via pull-from-cortex-5.0.ps1
- Phase 1: Knowledge Extension Layer ready for execution
- Zero technical debt carried forward

Epic: cortex5-enhancement-epic-v2
Phase: 0 (Foundation)"

git push -u origin CORTEX-5.5
```

**Step 4: Verify Pull System**
```powershell
# Verify pull tracking system operational
Test-Path "pull-from-cortex-5.0.ps1"  # Should be True
$tracking = Get-Content "cortex-brain/documents/planning/active/cortex5-enhancement-epic/tracking/pulls-from-cortex-5.0.json" | ConvertFrom-Json
Write-Host "Pull Budget: $($tracking.pull_budget.current_pull_count)/$($tracking.pull_budget.max_pulls_allowed)"
# Should show: Pull Budget: 0/20
```

### Phase 0 Success Criteria (GO/NO-GO)

**✅ GO Criteria (All Must Be True):**
- [ ] CORTEX-5.5 branch created and pushed to remote
- [ ] File count is ~150 (85% reduction from CORTEX-5.0's ~1000)
- [ ] NO obsolete directories present (cortex_3_0/, orchestration_4_0/, backups/, docs/)
- [ ] Essential files verified (master_orchestrator.py, brain-protection-rules.yaml, src/main.py)
- [ ] Phase 1 scaffolding exists (src/knowledge/company_knowledge_provider.py, knowledge_merger.py)
- [ ] Pull tracking system operational (pulls-from-cortex-5.0.json shows 0/20 budget)
- [ ] Python syntax check passes (no compilation errors)

**❌ NO-GO Criteria (Any Triggers Block):**
- [ ] File count >200 (insufficient reduction = still carrying bloat)
- [ ] Obsolete directories present (technical debt not eliminated)
- [ ] Essential files missing (broken foundation)
- [ ] Phase 1 scaffolding missing (Phase 1 cannot start)
- [ ] Pull tracking broken (cannot control future pulls)
- [ ] Python syntax errors (broken code migrated)

### Incremental Pull Strategy (Post-Phase 0)

**ONLY after Phase 0 complete, use this system to pull from CORTEX-5.0:**

```powershell
# Example: Phase 3 needs LLM utilities
.\pull-from-cortex-5.0.ps1 `
    -Phase 3 `
    -Files @("src/llm/llm_provider.py", "src/llm/prompt_builder.py") `
    -Justification "LLM-based goal detection requires prompt building utilities" `
    -AlternativesConsidered @("Rewrite with OpenAI SDK", "Use Anthropic Claude API") `
    -DecisionRationale "Existing LLM provider supports multiple models, rewrite not cost-justified" `
    -Category "llm_utilities"

# What this does:
# 1. Validates files exist in CORTEX-5.0
# 2. Checks file age (<90 days preferred)
# 3. Validates pull budget (2/20 used after this pull)
# 4. Pulls files from CORTEX-5.0
# 5. Updates tracking JSON (justification, alternatives, budget)
# 6. Runs tests to validate pulled files work
```

**Pull Budget Enforcement:**
- **Max:** 20 files across entire 11-phase epic
- **Current:** 0/20 (after Phase 0)
- **Alert:** At 15 pulls (75% threshold)
- **Override:** Requires justification + approval

**Pull Decision Criteria (Must Meet ALL):**
1. ✅ File explicitly needed by phase implementation
2. ✅ File has active dependents (AST analysis shows current usage)
3. ✅ File recently modified (<90 days preferred)
4. ✅ File not marked obsolete in CORTEX-5.0
5. ✅ Alternative considered (rewrite vs. pull trade-off)
6. ✅ Pull documented in phase report

### Phase 0 Documentation

**Migration Strategy:** `CORTEX-5.5-MIGRATION-STRATEGY.md` (784 lines - full technical rationale)  
**Execution Guide:** `CORTEX-5.5-EXECUTION-GUIDE.md` (468 lines - step-by-step instructions)  
**Validation Checklist:** `MIGRATION-CHECKLIST.md` (350 lines - GO/NO-GO criteria)  
**Quick Reference:** `QUICK-REF.md` (150 lines - TL;DR summary)  
**Summary:** `MIGRATION-SUMMARY.md` (650 lines - executive overview)

---

## 📋 Executive Summary

**Vision:** Transform CORTEX from single-purpose orchestration system to extensible business intelligence platform with pluggable company knowledge, custom orchestrators, and intelligent governance layering.

### Strategic Objectives

1. **Business Extensibility:** Enable companies to plugin domain-specific knowledge without corrupting CORTEX core
2. **Custom Orchestrators:** Allow registration of business-specific orchestrators (e.g., Selenium→Playwright)
3. **Intelligent Override:** Company knowledge intelligently overrides CORTEX defaults while preserving best practices
4. **Autonomous Execution:** Maximize snowball effect with parallel tracks and self-executing orchestrators
5. **Quality & Performance:** Comprehensive testing, optimization, and documentation

### Key Innovations

**🆕 Knowledge Extension Layer:**
- Company knowledge stored in `cortex-brain/tier2/company-knowledge/{company-id}/`
- Query priority: CORTEX Core → Company Override → Merge
- File-based (Markdown/YAML), no new databases
- Version-controlled, easily rollbackable

**🆕 Orchestrator Registry System:**
- Central registry at `cortex-brain/tier0/orchestrator-registry.yaml`
- Custom orchestrators isolated in `src/orchestrators/custom/{company-id}/`
- Manifest-based registration with inheritance support
- Master Orchestrator routes via registry (no hardcoded patterns)

**🆕 Rule Layering Architecture:**
- Core Rules (TDD, Git Isolation) - highest priority, cannot override
- Company Rules (coding standards, tech stack) - extends core
- Domain Rules (PCI-DSS, HIPAA) - scoped to specific orchestrators
- Conflict resolution via priority system

**🆕 Intermittent Thoughts Capture System:**
- User-facing `intermittent-thoughts.txt` for capturing ideas during autonomous execution
- System tracks via `cortex-brain/tier1/intermittent-thoughts.yaml`
- Checked at phase transitions, auto-incorporated if impact ≤15%
- Visual feedback via shield icon (🛡️) in chat + plan viewer integration
- Incorporated thoughts replaced with concise confirmation messages

**🆕 Generic Vacuum Orchestrator v3:**
- Transform Vacuum v2 from CORTEX-specific to generic, reusable system
- YAML-based rule engine for configurable cleanup (any directory structure)
- 4 pluggable analyzers: Python AST, JavaScript AST, content hash, metadata
- 4 preset templates: cortex-brain, python-project, node-project, generic
- Multi-format reporting: JSON, Markdown, HTML (interactive), CSV
- Safety features: dry-run, archive-before-delete, Git awareness, size thresholds
- Enables user project automation and CI/CD integration

---

## 🔄 CORTEX-5.0 Reference Strategy

**Branch Strategy:** This epic executes on a clean **CORTEX-5.5** branch with minimal essential files. Pull from **CORTEX-5.0** branch only when explicitly needed.

### Clean Start Philosophy

**START CLEAN → PULL AS NEEDED**

- ✅ CORTEX-5.5 begins with ~150 essential files (85% reduction vs CORTEX-5.0)
- ✅ CORTEX-5.0 remains reference source for additional dependencies
- ✅ Files pulled incrementally as phases require them
- ✅ Zero technical debt or orphaned code carried forward
- ✅ Each pull documented with justification in phase reports

### What's Included in CORTEX-5.5

**Essential Infrastructure (~150 files):**
- Core orchestration (src/main.py, master_orchestrator.py, pattern_router.py)
- Active orchestrator implementations (Planning v5, ADO v2, Investigation v2)
- Brain tier structure (tier0 governance, tier1 working memory, tier2 knowledge graph)
- Configuration system (master-orchestrator.yaml, 8 core configs)
- Active orchestrator manifests (11 manifests for registered orchestrators)
- Response template system (response-templates-v4.yaml)
- Logging and diagnostics infrastructure
- Minimal test harness (conftest.py, core routing tests)

**Phase 1 Scaffolding:**
- NEW: `src/knowledge/` module (company_knowledge_provider.py, knowledge_merger.py)
- NEW: `cortex-brain/tier2/company-knowledge/` structure
- NEW: Test structure for knowledge integration

### What's Available in CORTEX-5.0 (Pull On Demand)

**Available for selective pull:**
- Additional orchestrator implementations (Vacuum, Cleanup, Sanitization, Debug, Refinement)
- Additional agent implementations (20+ agents in src/agents/)
- Sample applications (cortex-sample-apps/ - not needed for this epic)
- Historical documentation (docs/ - superseded by in-brain documentation)
- Test fixtures and mocks (tests/fixtures/)
- Utilities and helpers (src/utils/ - additional specialized modules)
- LLM integration utilities (src/llm/ - may need for Phase 3)
- AST parsing tools (src/code_review/ - may need for Phase 6)
- TDD utilities (src/tdd/ - may need for Phase 8)
- HTML/CSS templates (templates/ - may need for Phase 9)

### Pull Command

```bash
# Pull specific file from CORTEX-5.0
git checkout CORTEX-5.0 -- {path/to/needed/file}

# Example: Phase 3 needs LLM utilities
git checkout CORTEX-5.0 -- src/llm/llm_provider.py
git checkout CORTEX-5.0 -- src/llm/prompt_builder.py
```

### Pull Criteria (Must Meet ALL)

1. ✅ **Referenced in phase implementation** - File explicitly called in phase deliverables
2. ✅ **Has active dependents** - AST analysis shows current usage
3. ✅ **Recently modified** - File modified within last 90 days (not obsolete)
4. ✅ **Not marked obsolete** - File not in CORTEX-5.0's cleanup candidates
5. ✅ **Phase lead approval** - Pull decision documented in phase report

### Phase-by-Phase Dependency Forecast

| Phase | Pull Expected? | Likely Dependencies | Alternative |
|-------|----------------|---------------------|-------------|
| **1** | ❌ No | All included in scaffolding | - |
| **2** | ❌ No | All included (routing infra) | - |
| **3** | ⚠️ Maybe | `src/llm/` for LLM-based goal detection | Rewrite with OpenAI SDK |
| **4** | ❌ No | Merge logic built in Phase 1 | - |
| **5** | ⚠️ Maybe | `src/orchestrators/base_orchestrator.py` | Create new base class |
| **6** | ⚠️ Maybe | `src/code_review/` for AST parsing | Use Python `ast` module directly |
| **7** | ❌ No | Brain protection rules already included | - |
| **8** | ⚠️ Maybe | `src/tdd/` for test generation | Rewrite autonomous test generator |
| **9** | ✅ Likely | `templates/plan-viewer/` as reference | Modernize from scratch |
| **10** | ❌ No | response-templates-v4.yaml included | - |
| **11** | ✅ Likely | `tests/integration/` for fixtures | Pull test cases only |

**Decision Rule:** Prefer **rewrite** over **pull** if file has >5 dependencies or >90 days old.

### Pull Tracking

**All pulls must be logged in:**
- Phase report (`reports/phase-{N}-implementation.md`)
- This epic's tracking system (`tracking/pulls-from-cortex-5.0.json`)

**Tracking Format:**
```json
{
  "phase": 3,
  "pull_date": "2026-01-15",
  "files_pulled": ["src/llm/llm_provider.py", "src/llm/prompt_builder.py"],
  "justification": "LLM-based goal detection requires prompt building utilities",
  "alternatives_considered": ["Rewrite with OpenAI SDK", "Use Anthropic Claude API"],
  "decision_rationale": "Existing LLM provider supports multiple models, rewrite not justified",
  "dependencies_analyzed": true,
  "test_coverage": "100%",
  "approved_by": "Phase Lead"
}
```

### Success Metrics

- ✅ **Total pulls <20 files** across entire epic (stay lean)
- ✅ **Pull justification documented** for every file
- ✅ **Zero unused pulls** - All pulled files actively used
- ✅ **85% file reduction maintained** - Don't bloat CORTEX-5.5

**Detailed Migration Plan:** See `CORTEX-5.5-MIGRATION-STRATEGY.md` in this plan folder.

---

## 🏗️ Architecture Overview

### Current State (CORTEX 5.1)

```
User Request
    ↓
Master Orchestrator (hardcoded patterns)
    ↓
10 Core Orchestrators (Planning, TDD, ADO, Vacuum, etc.)
    ↓
CORTEX Knowledge Library (Python-focused)
    ↓
4-Tier Brain System (Governance, Working Memory, Knowledge Graph, Dev Context)
```

**Limitations:**
- ❌ Cannot add custom orchestrators without code changes
- ❌ No company-specific knowledge integration
- ❌ Hardcoded routing patterns (not extensible)
- ❌ Single knowledge source (CORTEX only)

### Target State (CORTEX 5.2)

```
User Request
    ↓
Master Orchestrator v7 (registry-based routing)
    ↓
    ├─ Core Orchestrators (10)
    │   └─ Query: CORTEX Knowledge → Company Knowledge → Merge
    │
    └─ Custom Orchestrators (unlimited)
        └─ Query: Company Knowledge → CORTEX Knowledge → Merge
            └─ Enforce: Core Rules + Company Rules + Domain Rules
    ↓
Knowledge Extension Layer
    ├─ CORTEX Core Knowledge (immutable)
    └─ Company Knowledge (pluggable, per company-id)
    ↓
4-Tier Brain System (extended with company brains)
```

**Capabilities:**
- ✅ Custom orchestrators via manifest registration
- ✅ Company knowledge overrides CORTEX intelligently
- ✅ Registry-based routing (extensible)
- ✅ Multi-source knowledge with merge logic
- ✅ Rule layering (Core + Company + Domain)

---

## 📊 Epic Breakdown

### Phase 0: Foundation - Clean Branch Migration (15 minutes) ⚠️ MANDATORY

**🚨 MUST COMPLETE BEFORE ANY OTHER PHASE 🚨**

| Task | Description | Success Criteria |
|------|-------------|------------------|
| **Migration** | Run `create-cortex-5.5-branch.ps1` | CORTEX-5.5 branch created |
| **Validation** | Verify file count ~150 (not 1000+) | 85% reduction confirmed |
| **Verification** | Check no obsolete dirs (cortex_3_0, orchestration_4_0) | Clean structure validated |
| **Testing** | Python syntax check all files | Zero compilation errors |
| **Commit** | Push CORTEX-5.5 to remote | Branch visible on GitHub |

**Deliverables:**
- ✅ CORTEX-5.5 branch with ~150 essential files
- ✅ Phase 1 scaffolding (src/knowledge/)
- ✅ Pull tracking system (pulls-from-cortex-5.0.json)
- ✅ Zero technical debt (no obsolete code)

**Duration:** 15 minutes  
**Dependencies:** None (clean slate from main)  
**Status:** 🔴 NOT STARTED - BLOCKING ALL OTHER PHASES

**Documentation:**
- `CORTEX-5.5-EXECUTION-GUIDE.md` - Step-by-step migration
- `MIGRATION-CHECKLIST.md` - GO/NO-GO validation
- `CORTEX-5.5-MIGRATION-STRATEGY.md` - Full technical rationale

---

### Track 1: Core Intelligence (Weeks 1-4) - Foundation

**⚠️ CANNOT START UNTIL PHASE 0 COMPLETE**

| Phase | Name | Duration | Dependencies | Deliverables |
|-------|------|----------|--------------|--------------|
| **1** | **Knowledge Extension Layer** | 2 weeks | Phase 0 ✅ | `CompanyKnowledgeProvider`, folder structure, merge logic |
| **2** | **Orchestrator Registry System** | 1 week | Phase 1 | `orchestrator-registry.yaml`, `RegistryManager` |
| **3** | **Intelligent Goal Detection** | 1 week | Phase 2 | LLM-based analysis, dependency graph, goal inheritance |
| **4** | **Knowledge Merge & Override** | 1 week | Phase 1-2 | Priority system, conflict resolution, validation |

**Track Priority:** CRITICAL (blocks Tracks 2-3)

---

### Track 2: Business Extensibility (Weeks 3-6) - Parallel Execution

**⚠️ REQUIRES PHASE 0 + TRACK 1 FOUNDATION**

| Phase | Name | Duration | Dependencies | Deliverables |
|-------|------|----------|--------------|--------------|
| **5** | **Custom Orchestrator Framework** | 2 weeks | Phase 2 | Base classes, manifest schema, lifecycle hooks |
| **6** | **Selenium→Playwright Reference** | 1 week | Phase 5 | Complete custom orchestrator, AST parsing, code generation |
| **7** | **Rule Layering System** | 1 week | Phase 4 | 3-layer governance, conflict resolution, exemption workflow |

**Track Priority:** HIGH (enables business adoption)

---

### Track 3: Quality & UX (Weeks 5-8) - Parallel Execution

| Phase | Name | Duration | Dependencies | Deliverables |
|-------|------|----------|--------------|--------------|
| **8** | **TDD Test Harness** | 1 week | Phase 5 | Autonomous test generation, RED→GREEN→REFACTOR enforcement |
| **9** | **Generic Vacuum Orchestrator v3** | 1 week (5 days) | Phase 1, 4 | Rule engine, pluggable analyzers, 4 presets, multi-format reports |
| **10** | **Plan Viewer Modernization** | 1 week | None | CSS standardization, responsive design, phase navigation |
| **11** | **Response Template Optimization** | 1 week | None | INSTANT/FOCUSED/STRUCTURED/COMPREHENSIVE modes |

**Track Priority:** MEDIUM (quality improvements)

---

### Track 4: Integration & Validation (Weeks 8-9) - Final Validation

| Phase | Name | Duration | Dependencies | Deliverables |
|-------|------|----------|--------------|--------------|
| **12** | **End-to-End Integration** | 1 week | All phases | Integration tests, performance benchmarks, validation reports |

**Track Priority:** CRITICAL (go/no-go decision)

---

## 🎯 Success Criteria

### Phase-Level Success Metrics

**Phase 1 (Knowledge Extension):**
- ✅ Company knowledge folder structure created
- ✅ `CompanyKnowledgeProvider` queries company knowledge after CORTEX
- ✅ Merge logic: Company overrides CORTEX where explicitly defined
- ✅ Validation: Query "API architecture" returns company-specific override

**Phase 2 (Orchestrator Registry):**
- ✅ `orchestrator-registry.yaml` created with 10 core orchestrators
- ✅ `RegistryManager` routes requests via registry (not hardcoded)
- ✅ Adding new orchestrator = YAML edit (no code changes)
- ✅ Validation: Add test orchestrator, verify routing works

**Phase 5 (Custom Orchestrator Framework):**
- ✅ `BaseCustomOrchestrator` class with lifecycle hooks
- ✅ Manifest schema validates orchestrator metadata
- ✅ Custom orchestrators inherit CORTEX rules automatically
- ✅ Validation: Create minimal custom orchestrator, verify execution

**Phase 6 (Selenium→Playwright):**
- ✅ Complete working orchestrator converts Selenium→Playwright
- ✅ Follows TDD (inherits from CORTEX TDD orchestrator)
- ✅ Applies company coding standards (from `rules.yaml`)
- ✅ Validation: Convert sample Selenium test, verify Playwright output

**Phase 9 (Generic Vacuum Orchestrator v3):**
- ✅ Rule engine parses and executes YAML-based vacuum rules
- ✅ 4 pluggable analyzers (Python AST, JavaScript AST, content hash, metadata)
- ✅ 4 preset templates (cortex-brain, python-project, node-project, generic)
- ✅ Multi-format reporting (JSON, Markdown, HTML, CSV)
- ✅ CLI supports 3 modes (cortex-brain, project, custom)
- ✅ Validation: Vacuum 3 different project types successfully

**Phase 12 (Integration):**
- ✅ All 10 core orchestrators + 1 custom orchestrator tested
- ✅ Knowledge merge validated (CORTEX + company)
- ✅ Performance: <50ms overhead for knowledge queries
- ✅ Zero regression: All existing tests pass

### Epic-Level Success Metrics

**Functional:**
- ✅ 3+ companies registered with independent knowledge libraries
- ✅ 2+ custom orchestrators operational (Selenium→Playwright + 1 other)
- ✅ Knowledge merge accuracy >95% (correct overrides)
- ✅ Zero CORTEX core corruption (all changes isolated)

**Performance:**
- ✅ Knowledge query overhead <50ms (95th percentile)
- ✅ Custom orchestrator routing <100ms
- ✅ No performance regression on core orchestrators

**Quality:**
- ✅ 100% test coverage on new components
- ✅ Zero critical bugs in integration testing
- ✅ All SKULL rules enforced (TDD, Git Isolation, etc.)

**Adoption:**
- ✅ 2+ developers trained on custom orchestrator development
- ✅ Documentation complete (architecture, API, deployment)
- ✅ 1+ production custom orchestrator deployed

---

## 🌊 Snowball Effect Strategy

### Phase Dependencies (Visual)

```
Phase 1 (Knowledge Extension) ────────┐
    ↓                                 │
Phase 2 (Orchestrator Registry) ──────┼───→ Phase 5 (Custom Framework)
    ↓                                 │         ↓
Phase 3 (Goal Detection)              │     Phase 6 (Selenium→Playwright)
    ↓                                 │         ↓
Phase 4 (Knowledge Merge) ────────────┘     Phase 7 (Rule Layering)

Phase 8 (TDD Harness) ─────┐
Phase 9 (Plan Viewer) ──────┼─→ Phase 11 (Integration)
Phase 10 (Response Templates)─┘
```

### Parallel Execution Windows

**Weeks 1-2:** Phase 1 only (foundation)  
**Week 3:** Phase 2 + Phase 3 (parallel)  
**Week 4:** Phase 4 only (critical merge logic)  
**Weeks 5-6:** Phase 5 + Phase 8 + Phase 9 (3-way parallel)  
**Week 7:** Phase 6 + Phase 7 + Phase 10 (3-way parallel)  
**Week 8:** Integration prep (all phases complete)  
**Week 9:** Phase 11 (final validation)

### Snowball Momentum

**Week 1-2:** Foundation laid (Knowledge Extension)  
**Week 3-4:** Acceleration (Registry + Goal Detection + Merge Logic)  
**Week 5-7:** Peak velocity (3 tracks parallel execution)  
**Week 8-9:** Validation & stabilization

---

## 🛡️ Brain Protection (SKULL) Compliance

| Rule | How Epic Complies |
|------|-------------------|
| **TDD_ENFORCEMENT** | Phase 8 creates TDD test harness, all code follows RED→GREEN→REFACTOR |
| **HOLISTIC_DISCOVERY** | Phase 1-2 search existing knowledge before creating new structures |
| **GIT_ISOLATION** | Custom orchestrators isolated in `src/orchestrators/custom/`, never modify core |
| **PLANNING_ISOLATION** | This epic creates plan structure, implementation deferred to execution |
| **HAND_OFF_PROTOCOL** | All orchestrators (core + custom) execute autonomously via Python |
| **AUTONOMOUS_ONLY** | Phase 5-6 ensure custom orchestrators follow autonomous execution model |

**Full compliance:** 61 SKULL rules enforced across all phases

---

## 📁 Plan Structure

```
cortex5-enhancement-epic-v2/
├── 00-cortex5-epic.md                    # This master plan
├── README.md                              # Quick start guide
│
├── analysis/
│   ├── gap-analysis.md                    # Current vs. target state gaps
│   ├── architectural-impact.md            # System-wide impact assessment
│   └── risk-assessment.md                 # Risk identification & mitigation
│
├── context/
│   ├── discovery.md                       # Workspace context discovery
│   ├── architecture-analysis.md           # Current architecture deep dive
│   └── dependency-mapping.md              # Phase dependencies & constraints
│
├── phases/
│   ├── phase-01-knowledge-extension.md    # Track 1: Foundation
│   ├── phase-02-orchestrator-registry.md
│   ├── phase-03-goal-detection.md
│   ├── phase-04-knowledge-merge.md
│   ├── phase-05-custom-framework.md       # Track 2: Business Extensibility
│   ├── phase-06-selenium-playwright.md
│   ├── phase-07-rule-layering.md
│   ├── phase-08-tdd-harness.md            # Track 3: Quality & UX
│   ├── phase-09-plan-viewer.md
│   ├── phase-10-response-templates.md
│   └── phase-11-integration.md            # Track 4: Validation
│
├── tracking/
│   ├── progress-tracker.json              # Real-time progress tracking
│   ├── snowball.md                        # Snowball effect tracking
│   └── CONTINUATION-PROMPT.md             # Resume guidance for GitHub Copilot
│
├── artifacts/
│   ├── implementation/                    # Generated code
│   ├── tests/                             # Test suites
│   └── docs/                              # Generated documentation
│
└── reports/
    ├── validation/                        # Validation reports per phase
    ├── performance/                       # Performance benchmark results
    └── integration/                       # Integration test reports
```

---

## 🚀 Getting Started

### ⚠️ CRITICAL: Phase 0 Must Be Completed First

**DO NOT SKIP PHASE 0 - THIS IS NOT OPTIONAL**

**Phase 0 creates the clean foundation required for all other phases. Attempting to execute Phase 1-11 on CORTEX-5.0 will fail due to technical debt and architectural clutter.**

### Step-by-Step Execution

#### Phase 0: Clean Branch Migration (15 minutes) - MANDATORY FIRST STEP

```powershell
# 1. Open execution guide
code "cortex-brain/documents/planning/active/cortex5-enhancement-epic/CORTEX-5.5-EXECUTION-GUIDE.md"

# 2. Run migration script
.\create-cortex-5.5-branch.ps1

# 3. Validate migration (use checklist)
code "cortex-brain/documents/planning/active/cortex5-enhancement-epic/MIGRATION-CHECKLIST.md"

# 4. Verify success criteria
# ✅ File count ~150 (not 1000+)
# ✅ No obsolete directories (cortex_3_0, orchestration_4_0, backups)
# ✅ Phase 1 scaffolding exists (src/knowledge/company_knowledge_provider.py)
# ✅ Pull tracking system operational (pulls-from-cortex-5.0.json shows 0/20)

# 5. Commit and push
git commit -m "feat: Initialize CORTEX-5.5 clean branch"
git push -u origin CORTEX-5.5

# 6. Verify branch on GitHub
# Visit: https://github.com/asifhussain60/CORTEX/tree/CORTEX-5.5
```

**Phase 0 Success = GO to Phase 1**  
**Phase 0 Failure = STOP, debug migration, retry**

---

### For Implementers (After Phase 0 Complete)

1. **Read Phase 1:** Start with `phases/phase-01-knowledge-extension.md`
2. **Check Context:** Review `context/discovery.md` for workspace understanding
3. **Follow Sequence:** Complete phases in order (0→1→2→3→4, then parallelize)
4. **Track Progress:** Update `tracking/progress-tracker.json` after each task
5. **Validate:** Run validation checks after each phase completion
6. **Pull As Needed:** Use `pull-from-cortex-5.0.ps1` for CORTEX-5.0 dependencies

### For Reviewers

1. **Verify Phase 0:** Check CORTEX-5.5 branch exists with ~150 files (not 1000+)
2. **Read Analysis:** Start with `analysis/gap-analysis.md` for high-level understanding
3. **Review Risks:** Check `analysis/risk-assessment.md` for concerns
4. **Validate Snowball:** Ensure `tracking/snowball.md` shows proper momentum
5. **Check Compliance:** Verify SKULL rules enforced in each phase
6. **Monitor Pulls:** Track `pulls-from-cortex-5.0.json` stays under 20-file budget

### For GitHub Copilot

**To start this epic (Phase 0):**
```
Execute Phase 0 migration for CORTEX5 enhancement epic
```

**To resume after Phase 0:**
```
Continue CORTEX5 enhancement epic from phase {current_phase}
```

**To validate progress:**
```
Validate CORTEX5 epic progress for phase {phase_number}
```

**To pull from CORTEX-5.0:**
```
Pull {files} from CORTEX-5.0 for phase {phase_number} with justification {reason}
```

---

## 📚 References

**Architecture Docs:**
- `cortex-brain/documents/cortex-architecture-quick-ref.md` - CORTEX architecture overview
- `cortex-brain/documents/orchestrators-quick-ref.md` - Orchestrator documentation

**Configuration:**
- `cortex-brain/config/master-orchestrator.yaml` - Orchestrator routing config
- `cortex-brain/brain-protection-rules.yaml` - SKULL rules (61 rules)
- `cortex-brain/response-templates-v4.yaml` - Response formatting

**Implementation Guides:**
- `.github/prompts/CORTEX.prompt.md` - Master Orchestrator entry point
- `src/orchestrators/master_orchestrator.py` - Master Orchestrator implementation

---

## ⚠️ Risks & Mitigations

### Critical Risks

**Risk 1: Knowledge merge accuracy <95%**
- **Impact:** Company knowledge fails to override CORTEX correctly
- **Mitigation:** Phase 4 includes comprehensive merge logic testing
- **Contingency:** Fallback to explicit override flags if merge fails

**Risk 2: Custom orchestrator corruption of CORTEX core**
- **Impact:** Custom orchestrators modify core files
- **Mitigation:** Namespace isolation + Git pre-commit hooks
- **Contingency:** Rollback via Git, re-enforce isolation rules

**Risk 3: Performance degradation >50ms**
- **Impact:** Knowledge queries slow down all orchestrators
- **Mitigation:** Phase 11 benchmarks, implement caching if needed
- **Contingency:** Async knowledge loading, lazy evaluation

**Risk 4: Parallel execution conflicts (Weeks 5-7)**
- **Impact:** Phases 5-10 interfere with each other
- **Mitigation:** Clear module boundaries, integration tests
- **Contingency:** Serialize execution if conflicts detected

### Medium Risks

**Risk 5: Custom orchestrator manifest schema changes**
- **Impact:** Breaking changes force rewrite of registered orchestrators
- **Mitigation:** Version manifest schema, support backward compatibility
- **Contingency:** Migration scripts for schema updates

**Risk 6: Company knowledge format inconsistency**
- **Impact:** Different companies use incompatible formats
- **Mitigation:** Phase 1 defines strict Markdown/YAML schema
- **Contingency:** Validation layer rejects non-compliant knowledge

---

## 📊 Timeline & Milestones

| Week | Milestone | Phases | Status |
|------|-----------|--------|--------|
| **0** | 🚨 **CLEAN BRANCH MIGRATION (15 min)** | **Phase 0** | 🔴 **BLOCKING - MUST COMPLETE FIRST** |
| **1-2** | Foundation Complete | Phase 1 | 🟡 Not Started (blocked by Phase 0) |
| **3** | Registry & Goal Detection | Phases 2-3 | 🟡 Not Started |
| **4** | Merge Logic Validated | Phase 4 | 🟡 Not Started |
| **5-6** | Custom Framework + TDD + Viewer | Phases 5, 8-9 | 🟡 Not Started |
| **7** | Selenium→Playwright + Rule Layering | Phases 6-7, 10 | 🟡 Not Started |
| **8** | Integration Prep | All phases | 🟡 Not Started |
| **9** | Final Validation & Go-Live | Phase 11 | 🟡 Not Started |

**Total Duration:** 15 minutes (Phase 0) + 9 weeks (Phases 1-11)  
**Parallel Execution:** Weeks 5-7 (3 tracks)  
**Critical Path:** Phase 0 → Phase 1 → Phase 2 → Phase 4 → Phase 5 → Phase 6 → Phase 11

**⚠️ WARNING:** All phases BLOCKED until Phase 0 complete. File reduction from ~1000 to ~150 is MANDATORY.
**Critical Path:** Phases 1→2→4→5→6→11

---

## 🎉 Success Definition

### Phase 0 Success (MANDATORY - Blocks All Phases)

**Phase 0 is successful when:**

1. ✅ CORTEX-5.5 branch created and pushed to remote
2. ✅ File count ~150 (85% reduction from CORTEX-5.0's ~1000 files)
3. ✅ NO obsolete directories (cortex_3_0, orchestration_4_0, backups, docs)
4. ✅ Essential files verified (master_orchestrator.py, brain-protection-rules.yaml, main.py)
5. ✅ Phase 1 scaffolding exists (src/knowledge/company_knowledge_provider.py, knowledge_merger.py)
6. ✅ Pull tracking system operational (pulls-from-cortex-5.0.json shows 0/20 budget)
7. ✅ Python syntax check passes (zero compilation errors)

**Phase 0 GO-live criteria:** All 7 checkboxes ✅ = Proceed to Phase 1

**Phase 0 NO-GO consequences:** Cannot start Phase 1-11 (foundation broken)

---

### Epic Success (After Phase 0 + Phases 1-11)

**Epic is successful when:**

1. ✅ **Phase 0 complete** - CORTEX-5.5 branch with 85% file reduction
2. ✅ 3+ companies registered with working knowledge libraries
3. ✅ 2+ custom orchestrators deployed (including Selenium→Playwright)
4. ✅ Zero CORTEX core corruption (all changes isolated)
5. ✅ Knowledge merge accuracy >95%
6. ✅ Performance overhead <50ms (knowledge queries)
7. ✅ 100% SKULL rule compliance
8. ✅ Documentation complete (architecture + API + deployment)
9. ✅ 2+ developers trained on custom orchestrator development
10. ✅ All integration tests passing (Phase 11)
11. ✅ Production deployment successful (1+ custom orchestrator live)
12. ✅ **Pull budget maintained** - <20 total pulls from CORTEX-5.0

**Go-live criteria:** All 12 checkboxes ✅ + stakeholder sign-off

---

**Version History:**
- v1.0.0 (2025-12): Original CORTEX5 epic (goal detection focus)
- v2.0.0 (2026-01-06): Complete rewrite with Knowledge Extension + Custom Orchestrator architecture
- v2.1.0 (2026-01-06): Added mandatory Phase 0 (Clean Branch Migration) - BLOCKS all other phases

**Maintained By:** CORTEX Planning System v5  
**Epic Owner:** Asif Hussain  
**Status:** 🟢 ACTIVE - Ready for Phase 1 execution
