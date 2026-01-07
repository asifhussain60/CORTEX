# CORTEX5 Enhancement Epic - Context Summary

**Source Epic:** `cortex5-enhancement-epic-v2`  
**Version:** 2.1.0  
**Status:** Phase 0 Required (BLOCKING)  
**Created for:** cortex-docs plan

---

## Purpose

Summarize key architecture changes from CORTEX5 Enhancement Epic for documentation update reference.

---

## Epic Overview

**Vision:** Transform CORTEX from single-purpose orchestration to extensible business intelligence platform with pluggable company knowledge, custom orchestrators, and intelligent governance layering.

**Timeline:** Phase 0 (15 min) + 9 weeks (11 phases, 3 parallel tracks)  
**Complexity:** Tier 5 (Architectural Transformation)

---

## Phase 0: Clean Branch Migration (MANDATORY FIRST STEP)

**Purpose:** Create clean CORTEX-5.5 branch with 85% file reduction (1000 → 150 essential files)

**Key Changes:**
- New branch: CORTEX-5.5 (from main, not CORTEX-5.0)
- Essential files only: ~150 (no obsolete directories)
- Pull-on-demand system: `pull-from-cortex-5.0.ps1` (0/20 budget)
- Phase 1 scaffolding: `src/knowledge/` ready for execution
- Validation: 7 GO criteria, 6 NO-GO criteria

**Why Important for Docs:**
- Phase 0 is now the **first step** (not optional)
- All "11 phases" references → "12 phases (Phase 0 + Phases 1-11)"
- Getting started guide MUST include Phase 0 prerequisite
- Home page should highlight "Start Clean: 85% File Reduction"

**Execution Time:** 15 minutes

**Success Criteria:**
- CORTEX-5.5 branch created and pushed
- File count ~150 (verified)
- No obsolete directories (cortex_3_0/, orchestration_4_0/)
- Pull tracking operational (0/20 budget confirmed)

---

## Track 1: Core Intelligence (Phases 1-4)

### Phase 1: Knowledge Extension Layer

**Purpose:** Enable company-specific knowledge without corrupting CORTEX core

**Key Components:**
- **Location:** `cortex-brain/tier2/company-knowledge/{company-id}/`
- **Format:** Markdown + YAML (no databases)
- **Query Priority:** CORTEX Core → Company Override → Merge
- **API:** `CompanyKnowledgeProvider` interface
- **Versioning:** Git-controlled, rollbackable

**Example Use Case:**
- Company: "Use Google Style Guide (not PEP8)"
- CORTEX Planning v5: Applies Google Style Guide to plans
- Override scope: Company projects only (CORTEX core unaffected)

**Doc Impact:**
- Create "Knowledge Extension" architecture section
- API reference for `CompanyKnowledgeProvider`
- Tutorial: "Adding Company-Specific Knowledge"
- Examples on orchestrator detail pages

---

### Phase 2: Orchestrator Registry System

**Purpose:** Allow custom orchestrators without modifying CORTEX core

**Key Components:**
- **Registry:** `cortex-brain/tier0/orchestrator-registry.yaml`
- **Custom Location:** `src/orchestrators/custom/{company-id}/`
- **Registration:** Manifest-based with inheritance
- **Routing:** Master Orchestrator queries registry (no hardcoded patterns)

**Example Use Case:**
- Company: "Migrate Selenium tests to Playwright"
- Register: `selenium-to-playwright` custom orchestrator
- Invoke: "migrate selenium to playwright" (Master Orch routes via registry)

**Doc Impact:**
- Document orchestrator registration process
- Tutorial: "Building Custom Orchestrators"
- Update Master Orchestrator routing documentation
- Add "Custom" filter to orchestrator index (L1)

---

### Phase 3: Rule Layering Architecture

**Purpose:** Intelligent governance with 3-tier priority system

**Key Components:**
- **Tier 1: Core Rules** (Immutable) - TDD, Git Isolation, Planning Isolation
- **Tier 2: Company Rules** (Extends Core) - Coding standards, tech stack
- **Tier 3: Domain Rules** (Scoped) - PCI-DSS, HIPAA, GDPR (specific orchestrators)
- **Conflict Resolution:** Priority-based merging (Core always wins)

**Example Use Case:**
- Core: "TDD enforced" (cannot override)
- Company: "Minimum 2 code reviews" (extends core)
- Domain: "HIPAA logging for healthcare orchestrator" (scoped)
- Result: All rules apply (additive, no conflicts)

**Doc Impact:**
- Document 3-tier rule system
- Create conflict resolution examples
- Add D3.js rule priority visualization
- Update brain protection documentation

---

### Phase 4: Intermittent Thoughts Capture System

**Purpose:** Allow users to inject ideas during autonomous execution

**Key Components:**
- **User Interface:** `intermittent-thoughts.txt` (workspace root)
- **System Tracking:** `cortex-brain/tier1/intermittent-thoughts.yaml`
- **Check Points:** Phase transitions
- **Decision Logic:** ≤15% impact = auto-incorporate, >15% = defer
- **Visual Feedback:** 🛡️ shield icon in chat, plan viewer indicator

**Example Use Case:**
- User writes: "Add search bar to orchestrator map" (during Phase 3)
- System checks at Phase 4 start
- Impact: 8% (add 1 feature to existing page)
- Action: Auto-incorporated, search bar added
- Feedback: "💡 Thought incorporated: search bar added"

**Doc Impact:**
- Tutorial: "Using Intermittent Thoughts During Execution"
- Document system behavior (check points, thresholds)
- Add examples (incorporated vs deferred)
- Update plan viewer with thoughts indicator

---

## Track 2: Execution & UX (Phases 5-7)

### Phase 5-7 Overview

**Phase 5:** Goal-Driven Orchestrator (LLM-based goal detection)  
**Phase 6:** Cross-Orchestrator State Manager (shared state across orchestrators)  
**Phase 7:** Plan Viewer Enhancements (narrative story generation, glassmorphism parity)

**Doc Impact (Moderate):**
- Update orchestrator pages with goal-driven examples
- Document state manager API
- Showcase plan viewer enhancements (screenshots, demos)

---

## Track 3: Testing & Optimization (Phases 8-11)

### Phase 8-11 Overview

**Phase 8:** Test-Driven Validation (comprehensive test suite)  
**Phase 9:** Python CLI Tool (standalone CORTEX CLI)  
**Phase 10:** Performance Optimization (caching, profiling)  
**Phase 11:** Documentation & Go-Live (final docs, deployment)

**Doc Impact (High):**
- Document test coverage requirements
- CLI tool reference documentation
- Performance tuning guide
- Deployment procedures

---

## Master Orchestrator v7 Changes

**Routing Architecture:**
- **Pattern Matching:** Case-insensitive regex (10+ patterns)
- **LLM Fallback:** `LLMIntentClassifier` for ambiguous requests
- **Request Transformation:** GitHub Copilot adds domain context before invoking Python
- **Terminal Invocation:** `python3 -m src.main "transformed_request" --format markdown`

**Execution Model:**
- ✅ 100% autonomous (all orchestrators Python-implemented)
- ❌ No GUIDED orchestrators (removed in v5.1.0)
- ✅ GitHub Copilot = Routing proxy (NOT executor)
- ✅ Python orchestrators = Executors (autonomous, self-updating progress)

**Doc Impact:**
- Update Master Orchestrator architecture documentation
- Explain routing: Pattern → Transform → Invoke
- Document request transformation pipeline
- Add terminal invocation examples
- Remove all "GUIDED" orchestrator references

---

## Pull-On-Demand Strategy

**Purpose:** Control file proliferation on CORTEX-5.5

**Key Rules:**
- **Budget:** 20 files max across entire epic (Phases 1-11)
- **Current:** 0/20 (after Phase 0)
- **Justification Required:** Every pull needs: alternatives considered, decision rationale, phase report link
- **Alert Threshold:** 15 pulls (75% budget used)
- **Override:** Requires approval + documented justification

**Tool:** `pull-from-cortex-5.0.ps1`

**Example:**
```powershell
.\pull-from-cortex-5.0.ps1 `
    -Phase 3 `
    -Files @("src/llm/llm_provider.py") `
    -Justification "LLM-based goal detection requires prompt building" `
    -AlternativesConsidered @("Rewrite with OpenAI SDK") `
    -DecisionRationale "Existing provider supports multiple models" `
    -Category "llm_utilities"
```

**Doc Impact:**
- Document pull-on-demand strategy
- Explain budget tracking (0/20)
- Show pull command examples
- Add troubleshooting: "Budget exceeded" error

---

## Timeline & Milestones

| Week | Milestone | Phases | Status |
|------|-----------|--------|--------|
| **0** | 🚨 **CLEAN BRANCH MIGRATION (15 min)** | **Phase 0** | 🔴 **BLOCKING** |
| **1-2** | Foundation Complete | Phase 1 (Knowledge Extension) | 🟡 Blocked by Phase 0 |
| **3-4** | Intelligence Complete | Phases 2-4 (Registry, Rules, Thoughts) | 🟡 Blocked by Phase 0 |
| **5-7** | Execution & UX Complete | Phases 5-7 (Goals, State, Plan Viewer) | 🟡 Blocked by Phase 0 |
| **8-9** | Quality & Tooling Complete | Phases 8-9 (Testing, CLI) | 🟡 Blocked by Phase 0 |

**Key Takeaway:** Phase 0 blocks ALL other phases (cannot start until complete)

---

## Documentation Updates Required

### Home Page (`docs/index.html`)
- Add Phase 0 callout: "Start Clean: 85% File Reduction"
- Update hero: "CORTEX5 with 12-Phase Execution Model"
- Feature cards: Knowledge Extension, Orchestrator Registry, Rule Layering, Intermittent Thoughts

### Architecture Overview (`docs/architecture.html`)
- 4-Tier Brain + Knowledge Extension Layer
- Master Orchestrator v7 routing (pattern → transform → invoke)
- Request transformation pipeline visualization
- Pull-on-demand strategy diagram

### Getting Started (`docs/quick-start.html`)
- **Phase 0 prerequisite section (mandatory)**
- Installation: CORTEX-5.5 branch (not CORTEX-5.0)
- First command examples with transformation
- Intermittent thoughts usage guide

### Orchestrator Index L1 (`docs/orchestrators/index.html`)
- Update D3.js map with all 10+ orchestrators
- Add "Custom" filter for company orchestrators
- Hover tooltips: version, description, example command
- Mobile responsive collapsible map

### Orchestrator Detail Pages L2 (`docs/orchestrators/*.html`)
- Generate from YAML manifests (automated)
- Include knowledge extension examples
- Show terminal invocation commands
- Document rule scoping (Domain rules)

---

## Glassmorphism Theme Context

**Current Implementation:**
- Home page: `docs/index.html` (glassmorphism applied)
- Orchestrator index: `docs/orchestrators/index.html` (glassmorphism applied)
- Technical docs: `docs/technical/` (glassmorphism CSS file exists)

**CSS Properties:**
- Background: `rgba(26, 31, 58, 0.7)`
- Blur: `backdrop-filter: blur(10px)`
- Border: `1px solid rgba(255, 255, 255, 0.1)`
- Shadow: `0 20px 60px rgba(0,0,0,0.3)`
- Radius: `20px` (large cards), `12px` (small cards)

**Admin Dashboard Parity:**
- Color palette consistency
- Typography: Inter font family
- Touch targets: ≥44px (WCAG AA)
- Contrast ratio: ≥4.5:1 (WCAG AA)

**Doc Impact:**
- Standardize glassmorphism across ALL pages
- Create CSS variables for theme tokens
- Apply `.glass-card` utility class consistently
- Remove inline styles (consolidate to `glassmorphism.css`)

---

## Key Files Reference

**Epic Documents:**
- Master Plan: `cortex5-enhancement-epic/00-cortex5-epic.md`
- Phase 0 Summary: `cortex5-enhancement-epic/PHASE-0-INTEGRATION-SUMMARY.md`
- Progress Tracker: `cortex5-enhancement-epic/tracking/progress-tracker.json`

**Manifests:**
- Orchestrators: `cortex-brain/manifests/orchestrators/*.yaml` (46 files)
- Master Orchestrator: `cortex-brain/config/master-orchestrator.yaml`
- Brain Protection: `cortex-brain/brain-protection-rules.yaml`

**Existing Docs:**
- Home: `docs/index.html`
- Orchestrators L1: `docs/orchestrators/index.html`
- Technical: `docs/technical/README.md`

---

**Next Action:** Use this context to inform Phase 1 (Architecture Analysis) and Phase 2 (Content Rewriting)
