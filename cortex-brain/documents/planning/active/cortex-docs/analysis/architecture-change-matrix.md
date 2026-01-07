# Architecture Change Matrix

**Plan:** cortex-docs  
**Version:** 1.0.0  
**Date:** 2026-01-06

---

## Purpose

Map CORTEX5 Enhancement Epic architecture changes to documentation sections requiring updates.

**Source Epic:** `cortex5-enhancement-epic-v2` (Phase 0 + Phases 1-11)

---

## Architecture Changes → Documentation Mapping

### 1. Phase 0: Clean Branch Migration

**Epic Changes:**
- CORTEX-5.5 branch with ~150 essential files (85% reduction)
- Pull-on-demand strategy (`pull-from-cortex-5.0.ps1`)
- Budget tracking (0/20 files max)
- 15-minute migration execution
- 7 GO criteria, 6 NO-GO criteria

**Doc Sections Requiring Updates:**

| Doc Section | File | Change Required | Priority |
|-------------|------|-----------------|----------|
| Home Page Hero | `docs/index.html` | Add "Start Clean: Phase 0 Migration" callout | HIGH |
| Getting Started | `docs/quick-start.html` | Add Phase 0 prerequisite section (mandatory first step) | HIGH |
| Architecture Overview | `docs/architecture.html` | Document migration rationale, pull strategy | HIGH |
| Timeline & Milestones | `docs/roadmap.html` | Update to "12 phases (Phase 0 + Phases 1-11)" | HIGH |
| Troubleshooting | `docs/troubleshooting.html` | Add "Phase 0 not complete" error guide | MEDIUM |

**Example Content:**
```markdown
## ⚠️ Phase 0: Mandatory First Step

Before executing ANY CORTEX5 orchestrator, you MUST complete Phase 0 migration:

```powershell
# Execute 15-minute migration
.\create-cortex-5.5-branch.ps1

# Verify completion (7 GO criteria)
# - File count ~150 (not 1000+)
# - No obsolete directories
# - Pull tracking operational (0/20 budget)
```

**Why Phase 0?** CORTEX-5.0 has ~1000 files with technical debt. CORTEX-5.5 starts clean with 150 essential files.
```

---

### 2. Knowledge Extension Layer (Phase 1)

**Epic Changes:**
- Company-specific knowledge in `cortex-brain/tier2/company-knowledge/{company-id}/`
- Query priority: CORTEX Core → Company Override → Merge
- File-based (Markdown + YAML, no databases)
- `CompanyKnowledgeProvider` API
- Version-controlled, rollbackable

**Doc Sections Requiring Updates:**

| Doc Section | File | Change Required | Priority |
|-------------|------|-----------------|----------|
| Architecture Overview | `docs/architecture.html` | Add "Knowledge Extension Layer" section | HIGH |
| API Reference | `docs/api/knowledge-extension.html` | Document `CompanyKnowledgeProvider` interface | HIGH |
| User Guide | `docs/guides/custom-knowledge.html` | Tutorial: "Adding Company-Specific Knowledge" | HIGH |
| Orchestrator Pages (L2) | `docs/orchestrators/*.html` | Add knowledge extension examples | MEDIUM |
| FAQ | `docs/faq.html` | Add Q&A on knowledge override behavior | MEDIUM |

**Example Content:**
```markdown
## Knowledge Extension Layer

**Location:** `cortex-brain/tier2/company-knowledge/{company-id}/`

### Query Priority
1. **CORTEX Core:** Built-in best practices (TDD, Git Isolation)
2. **Company Override:** Your coding standards (Python style, tech stack)
3. **Merge:** Intelligent combination (company extends core)

### Example: Custom Coding Standards

**File:** `cortex-brain/tier2/company-knowledge/acme-corp/coding-standards.yaml`
```yaml
company_id: "acme-corp"
coding_standards:
  python_style: "Google Style Guide (not PEP8)"
  max_line_length: 120  # Override CORTEX default 88
  imports: "isort + black"
```

**Behavior:** Planning orchestrator uses Google Style Guide for Acme Corp projects.
```

---

### 3. Orchestrator Registry System (Phase 2)

**Epic Changes:**
- Central registry: `cortex-brain/tier0/orchestrator-registry.yaml`
- Custom orchestrators: `src/orchestrators/custom/{company-id}/`
- Manifest-based registration with inheritance
- Master Orchestrator queries registry (no hardcoded patterns)

**Doc Sections Requiring Updates:**

| Doc Section | File | Change Required | Priority |
|-------------|------|-----------------|----------|
| Architecture Overview | `docs/architecture.html` | Document orchestrator registry architecture | HIGH |
| Developer Guide | `docs/guides/custom-orchestrators.html` | Tutorial: "Building Custom Orchestrators" | HIGH |
| Master Orchestrator Docs | `docs/orchestrators/master-orchestrator.html` | Update routing documentation (registry-based) | HIGH |
| API Reference | `docs/api/orchestrator-registry.html` | Registry schema + registration API | HIGH |
| Orchestrator Index (L1) | `docs/orchestrators/index.html` | Add "Custom" filter for company orchestrators | MEDIUM |

**Example Content:**
```markdown
## Orchestrator Registry System

**Registry:** `cortex-brain/tier0/orchestrator-registry.yaml`

### Registering Custom Orchestrators

**Step 1: Create Manifest**
```yaml
# cortex-brain/manifests/orchestrators/custom/acme-corp/selenium-to-playwright.yaml
orchestrator:
  name: "selenium_to_playwright"
  company_id: "acme-corp"
  version: "1.0.0"
  type: "autonomous"
  patterns:
    - "^migrate selenium"
    - "^convert to playwright"
```

**Step 2: Register in Central Registry**
```yaml
# cortex-brain/tier0/orchestrator-registry.yaml
custom_orchestrators:
  - manifest: "manifests/orchestrators/custom/acme-corp/selenium-to-playwright.yaml"
    company_id: "acme-corp"
    status: "active"
```

**Step 3: Invoke**
```bash
# Master Orchestrator routes via registry
migrate selenium tests to playwright
```
```

---

### 4. Rule Layering Architecture (Phase 3)

**Epic Changes:**
- 3-tier rule system: Core → Company → Domain
- Priority-based conflict resolution
- Core rules immutable (TDD, Git Isolation)
- Company/Domain rules extend core

**Doc Sections Requiring Updates:**

| Doc Section | File | Change Required | Priority |
|-------------|------|-----------------|----------|
| Architecture Overview | `docs/architecture.html` | Document 3-tier rule system | HIGH |
| Brain Protection Docs | `docs/brain-protection.html` | Update with rule layering priority | HIGH |
| User Guide | `docs/guides/custom-rules.html` | Tutorial: "Adding Company-Specific Rules" | HIGH |
| Orchestrator Pages (L2) | `docs/orchestrators/*.html` | Explain rule scoping (Domain rules) | MEDIUM |
| Visualizations | `docs/architecture.html` | Add D3.js rule priority visualization | MEDIUM |

**Example Content:**
```markdown
## Rule Layering Architecture

### 3-Tier Priority System

**Tier 1: Core Rules** (Highest Priority - Immutable)
- TDD_ENFORCEMENT: Tests before implementation
- GIT_ISOLATION: CORTEX code never commits to user repos
- PLANNING_ISOLATION: Planning creates plans, not code

**Tier 2: Company Rules** (Extends Core)
- CODING_STANDARDS: Python Google Style Guide
- TECH_STACK: Django + PostgreSQL only
- REVIEW_PROCESS: Minimum 2 approvals

**Tier 3: Domain Rules** (Scoped to Orchestrators)
- PCI_DSS: Payment orchestrators only
- HIPAA: Healthcare data orchestrators only
- GDPR: EU user data orchestrators only

### Conflict Resolution
- Core always wins (cannot override)
- Company extends core (additive)
- Domain scopes to specific orchestrators
```

---

### 5. Intermittent Thoughts Capture System (Phase 4)

**Epic Changes:**
- User interface: `intermittent-thoughts.txt` (workspace root)
- System tracking: `cortex-brain/tier1/intermittent-thoughts.yaml`
- Check points: Phase transitions (≤15% impact auto-incorporated)
- Visual feedback: 🛡️ shield icon in chat + plan viewer

**Doc Sections Requiring Updates:**

| Doc Section | File | Change Required | Priority |
|-------------|------|-----------------|----------|
| User Guide | `docs/guides/intermittent-thoughts.html` | Tutorial: "Capturing Ideas During Execution" | HIGH |
| Architecture Overview | `docs/architecture.html` | Document thought capture workflow | HIGH |
| Plan Viewer Integration | `docs/plan-viewer.html` | Add thoughts integration indicator | MEDIUM |
| Quick Start | `docs/quick-start.html` | Add "Using Intermittent Thoughts" section | MEDIUM |
| Troubleshooting | `docs/troubleshooting.html` | "Thoughts not incorporated" debugging | LOW |

**Example Content:**
```markdown
## Intermittent Thoughts Capture

**Use Case:** During autonomous execution, you have an idea that could improve the plan.

### User Interface

**File:** `intermittent-thoughts.txt` (workspace root)

**Example:**
```
# Intermittent Thoughts - 2026-01-06

## During Phase 3 (Orchestrator L1)
- Add search bar to orchestrator map (filter by name)
- Consider collapsible categories for better mobile UX

## Priority
HIGH - Would improve discoverability
```

### System Behavior

**Check Points:** System checks `intermittent-thoughts.txt` at phase transitions.

**Decision Logic:**
- **≤15% impact:** Auto-incorporated (update plan inline)
- **>15% impact:** Deferred to next planning session

**Visual Feedback:**
- 🛡️ Shield icon in chat: "Thought incorporated"
- Plan viewer: "💡 Thoughts: 2 incorporated, 0 deferred"
```

---

### 6. Master Orchestrator v7

**Epic Changes:**
- Pattern-based routing + LLM classification fallback
- GitHub Copilot transforms request → invokes Python via terminal
- 100% autonomous execution (all orchestrators Python-implemented)
- Request transformation pipeline: strip → match → transform → invoke

**Doc Sections Requiring Updates:**

| Doc Section | File | Change Required | Priority |
|-------------|------|-----------------|----------|
| Architecture Overview | `docs/architecture.html` | Document Master Orchestrator v7 routing | HIGH |
| Developer Guide | `docs/guides/routing.html` | Explain pattern matching + LLM fallback | HIGH |
| API Reference | `docs/api/master-orchestrator.html` | Document transformation pipeline | HIGH |
| Orchestrator Pages (L2) | `docs/orchestrators/*.html` | Update invocation examples (terminal-based) | MEDIUM |
| Quick Start | `docs/quick-start.html` | Add request transformation examples | MEDIUM |

**Example Content:**
```markdown
## Master Orchestrator v7 Routing

### Architecture

**GitHub Copilot Role:** Routing proxy (NOT executor)
1. Strip meta-directives (`Follow instructions in...`)
2. Match pattern (case-insensitive regex)
3. Transform request (add domain context)
4. Invoke Python via terminal (`python3 -m src.main "..."`)

**Python Role:** Executor (orchestrators run here)

### Request Transformation

**Raw Input:** `plan user auth`

**Transformation (Copilot adds context):**
```
plan user authentication with OAuth2, JWT tokens, session management, 
database (users table, roles, permissions), API endpoints (login, logout, 
refresh, validate), testing (unit tests, integration tests, security tests)
```

**Terminal Invocation:**
```bash
python3 -m src.main "plan user authentication with OAuth2..." --format markdown
```

**Result:** Python Planning v5 executes autonomously, creates plan folder.
```

---

## Summary Statistics

**Total Architecture Changes:** 6 major features  
**Documentation Sections Impacted:** 25+ files  
**High Priority Updates:** 18 sections  
**Medium Priority Updates:** 12 sections  
**Low Priority Updates:** 3 sections

**Cross-Cutting Updates:**
- All "11 phases" → "12 phases (Phase 0 + Phases 1-11)"
- All "CORTEX-5.0" → "CORTEX-5.5" (where applicable)
- All orchestrator examples updated with terminal invocation
- All architecture diagrams updated (4-Tier Brain + extensions)

---

**Next Step:** Phase 2 - Content Rewriting (use this matrix as reference for what to update)
