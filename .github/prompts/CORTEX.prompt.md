# 🎯 CORTEX 6.0 - Production-Grade Orchestration Gateway

**Version:** 6.0.0 | **Status:** ✅ PRODUCTION | **Architecture:** Python-based autonomous execution  
**Author:** Asif Hussain | **Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🚨 CRITICAL: Context Preservation Protocol

**Before ANY operation, execute this 3-step context check:**

1. **Load Epic State** → Query `cortex-brain/tier1/tracking/` for active epic, phase, todo
2. **Verify Governance** → Load `cortex-brain/tier0/governance/core-rules.yaml` (19 CORE rules)
3. **Check AC Registry** → Reference `cortex-brain/tier1/acceptance-criteria/` for current AC-IDs

**FAILURE TO PRESERVE CONTEXT = WRONG PLAN**. The system has accumulated 970+ deleted files, 13 requirement conflicts, and fragmented truth sources. This prompt enforces single-source-of-truth discipline.

---

## 🔍 Holistic Plan Review & Conflict Resolution

**Before executing any multi-phase plan, perform this 4-step conflict analysis:**

1. **Requirement Conflict Detection** → Scan for contradictory AC-IDs, governance rules, or execution patterns
2. **Ambiguity Resolution** → Identify unclear requirements that could lead to implementation conflicts  
3. **Dependency Validation** → Verify all referenced AC-IDs exist and are properly sequenced
4. **DoR Certification** → Confirm 100% Definition of Ready with zero unresolved ambiguities

**Intelligent Orchestrator Selection Engine (AC-SCORE-001):**
```
Total Score = (Accuracy × 0.4) + (Efficiency × 0.3) + (AC_Success × 0.2) + (Context × 0.1)
```
- **Accuracy Score** → Domain match, intent alignment, context relevance
- **Efficiency Score** → Resource usage, execution time, complexity overhead
- **AC Success Rate** → Historical performance with similar acceptance criteria
- **Context Relevance** → Project phase, dependencies, specialization

**TDD-Master Bi-Directional Gateway (AC-TDD-GATE-001):**
- **Forward:** Clarify work → Generate AC → Provide Final Instruction (F)
- **Backward:** Validate output → Run quality gates → Confirm user intent achieved

**Conflict Resolution Questions (Auto-Generated):**
- Does this plan violate CORE-001 autonomous execution while requiring user interaction?
- Which orchestrator scores highest for accuracy + efficiency + AC compatibility?
- Does TDD-Master gateway pattern maintain quality assurance throughout?
- Are all orchestrator registrations properly enforced with runtime validation?

**Default Resolution Strategy:** Accept balanced accuracy-efficiency solutions that maintain CORE governance compliance with intelligent scoring and bi-directional validation.

---

## 🏗️ Architecture: 4-Tier Governance (CORTEX 6 Design)

| Tier | Category | Precedence | Location | Purpose |
|------|----------|------------|----------|---------|
| **0** | `CORTEX_CORE` | HIGHEST | `tier0/governance/` | Immutable brain protection (SKULL) |
| **1** | `BUSINESS_TIER_0` | HIGH | `tier1/` | Business requirements, compliance, active state |
| **2** | `COMPANY_PRACTICES` | MEDIUM | `tier2/` | Engineering standards, integration contracts |
| **3** | `KNOWLEDGE_PRACTICES` | LOW | `tier3/` | Learned patterns, project-specific insights |

**Conflict Resolution:** Tier 0 wins → Tier 1 → Tier 2 → Tier 3. `GovernanceMerger` enforces precedence.

---

## 📋 Execution Pipeline (4 Steps)

```
[1] Context Load → [2] Pattern Match → [3] Transform + Audit → [4] Execute via Terminal
```

### Step 1: Context Load (MANDATORY)

**Before routing, load these files:**
- `cortex-brain/tier1/tracking/progress-tracker.json` → Current phase, todo, blockers
- `cortex-brain/tier0/governance/core-rules.yaml` → Active SKULL rules
- `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml` → AC-ID registry

**If files missing:** Create them. Do NOT proceed with stale context.

### Step 2: Pattern Matching

| Pattern (Regex) | Orchestrator | Priority | AC-ID Prefix |
|-----------------|--------------|----------|--------------|
| `^(epic review\|health check\|progress report)` | **Epic Review** | 6 | AC-EPIC-* |
| `^(plan\|create a plan)` | **Planning v5** | 10 | AC-PLAN-* |
| `^(implement\|build\|create\|fix\|refactor)` | **TDD-Master v1** | 15 | AC-TDD-* |
| `^(tdd\|test driven)` | **TDD-Master v1** | 20 | AC-TDD-* |
| `^(ado\|azure devops)` | **ADO v2** | 30 | AC-ADO-* |
| `^(scaffold\|create orchestrator\|new orchestrator)` | **Orchestrator Scaffolder** | 25 | AC-SCAFFOLD-* |
| `^(vacuum\|deep clean)` | **Vacuum v2 (Intelligent)** | 45 | AC-VAC-* |
| `^(cleanup)` | **Cleanup v2** | 55 | AC-CLEAN-* |
| `^(investigate\|root cause)` | **Investigation** | 60 | AC-INV-* |
| `^(git history\|search branches\|find existing\|recover\|did we have)` | **Git History Intel** | 5 | AC-GIT-* |
| `^(crawl\|scan code\|analyze codebase\|knowledge graph)` | **Crawler Orchestrator** | 35 | AC-CRAWLER-* |
| `^(onboard\|setup project\|analyze repo\|build context\|new repo)` | **Onboarding Orchestrator** | 8 | AC-ONBOARD-* |

**Intelligent Selection:** When multiple patterns match, use AC-SCORE-001 scoring engine to select optimal orchestrator based on accuracy, efficiency, AC success rate, and context relevance.

---

## 🚀 Onboarding Orchestrator (New Repo/Project Setup)

**Run onboarding to build comprehensive context for new repositories:**

```bash
# Full project onboarding (AST + git + knowledge graph)
python3 -m src.orchestrators.onboarding.onboarding_orchestrator onboard --path /path/to/repo

# User onboarding (interactive tutorial)
python3 -m src.orchestrators.onboarding.onboarding_orchestrator user --role developer

# Team onboarding (RBAC + shared config)
python3 -m src.orchestrators.onboarding.onboarding_orchestrator team --name "Engineering" --members user1,user2
```

**What it does:**
1. **AST Analysis** → Run language-specific analyzers (Python, JS, C#, SQL)
2. **Git History** → Analyze commits, contributors, code churn
3. **Tech Detection** → Identify frameworks, dependencies, build tools
4. **Architecture** → Detect patterns (MVC, microservices, layers)
5. **Knowledge Graph** → Build symbol/dependency/call graphs
6. **Store in Tier1** → Save to `cortex-brain/tier1/` for MasterOrchestrator use

**Output Files:**
- `cortex-brain/tier1/knowledge-graph.db` → SQLite graph database
- `cortex-brain/tier1/project-context.yaml` → Project summary
- `cortex-brain/tier1/tech-stack.yaml` → Detected technologies
- `cortex-brain/tier1/architecture.yaml` → Architecture patterns

**AC-IDs:** AC-ONBOARD-001 to AC-ONBOARD-011

**Source References:**
- `commit:4686dc7a8` → OnboardingOrchestrator (560 LOC)
- `CORTEX-4.0:src/cortex_lens/` → Full analyzer suite

---

## 🔄 Git History Intelligence (BEFORE Creating New Code)

**CRITICAL RULE: Before implementing ANY new feature, search git history first.**

```bash
# Search for existing implementations
python3 -m src.tools.git_history_intelligence search "{query}"

# Extract found asset
python3 -m src.tools.git_history_intelligence extract {branch} {path}

# Build searchable index
python3 -m src.tools.git_history_intelligence index
```

**Practical Scenarios:**
- "Do we have auth implementation?" → `search "authentication oauth jwt"`
- "What was original SKULL design?" → `search "skull governance rules" --branch CORTEX-4.0`
- "Did we solve file locking?" → `search "file lock fcntl mutex concurrent"`
- "ADO integration patterns?" → `search "azure devops ado work_item"`

**Output Location:** `cortex-brain/git-history-assets/`
- `index/` → Searchable indexes per branch
- `extracted/` → Recovered code organized by category
- `search-results/` → Query results in JSON/YAML
- `cx6-requirements-integration.yaml` → Ready for AC-INDEX merge

**Available Branches:** CORTEX-5.5, CORTEX-5.0, CORTEX-4.0, CORTEX-3.0, CORTEX-2.0, CORTEX-1.0

---

## 🔍 Codebase Crawlers & Knowledge Graph

**Multi-threaded AST crawlers for building code understanding:**

### Crawler Capabilities (Recovered from CORTEX-4.0):
- **Parallel Processing:** ThreadPoolExecutor with auto CPU detection
- **Progressive Scanning:** 3 levels (overview → standard → deep)
- **Language Analyzers:** Python, JavaScript, C#, ColdFusion, Generic

### Knowledge Graph Features:
- Symbol extraction (classes, functions, variables, imports)
- Dependency graph (who imports what)
- Call graph (who calls whom)
- SQLite-backed persistence with incremental updates

### Usage:
```bash
# Scan codebase with overview level
python3 -m src.crawlers.crawler_orchestrator scan . --level overview

# Deep scan specific directory
python3 -m src.crawlers.crawler_orchestrator scan src/ --level deep

# Build knowledge graph from crawl results
python3 -m src.crawlers.knowledge_graph build --from-crawl latest
```

**AC-IDs:** AC-CRAWLER-001 to AC-CRAWLER-005, AC-GRAPH-001 to AC-GRAPH-004

---

## 🧹 Intelligent Vacuum Orchestrator (Post-Analysis Cleanup)

**CRITICAL: Vacuum runs AFTER knowledge graph analysis to avoid deleting necessary files.**

### Strategic Execution Order

```
[1] Crawler Analysis → [2] Knowledge Graph Build → [3] Intelligent Vacuum → [4] Validation
```

**Why This Order:**
- Crawler identifies **active imports, references, dependencies**
- Knowledge graph maps **file usage, call chains, integration points**
- Vacuum uses graph data to **safely identify unused files**
- Prevents deletion of files that appear unused but are actually referenced

### Vacuum Intelligence Rules

**Safe Deletions (ALWAYS):**
- `*.bak` files (backup files)
- `*.tmp` files (temporary files)
- Files in `archive/` or `archived/` directories
- Duplicate `.md` files (consolidate using kebab-case)
- Unused test fixtures not referenced in any test
- Generated files with corresponding source

**Requires Knowledge Graph Validation:**
- Python files without direct imports (may be CLI entry points)
- Config files (may be loaded dynamically)
- Documentation files (check for README links)
- Script files (check for references in docs or other scripts)

### Duplicate Markdown Consolidation

**Pattern Detection:**
```
README.md  → keep
ReadMe.md  → delete (consolidate to README.md)
read-me.md → keep (different semantic meaning)

Architecture.md      → delete
architecture.md      → keep (kebab-case standard)
ARCHITECTURE.md      → delete (consolidate to architecture.md)

User Guide.md        → delete
user-guide.md        → keep (kebab-case standard)
UserGuide.md         → delete (consolidate to user-guide.md)
```

**Consolidation Strategy:**
1. **Identify duplicates:** Same semantic name, different casing
2. **Choose canonical:** Prefer kebab-case (lowercase with hyphens)
3. **Merge content:** If files differ, merge unique content before deletion
4. **Update references:** Update all links in other files
5. **Delete duplicates:** Remove non-canonical versions

### Usage

```bash
# WRONG: Running vacuum first (may delete necessary files)
python3 -m src.main "vacuum deep clean"

# CORRECT: Analysis → Vacuum sequence
python3 -m src.main "crawl . --level deep"  # Build knowledge graph
python3 -m src.main "vacuum deep clean"      # Then clean with intelligence

# Vacuum with specific targets
python3 -m src.main "vacuum --targets bak,archived,duplicate-md"

# Dry-run to preview deletions
python3 -m src.main "vacuum --dry-run"
```

### Vacuum Categories

| Category | Description | Safety Level | Requires Graph |
|----------|-------------|--------------|----------------|
| **bak-files** | `*.bak` backup files | SAFE | No |
| **archived** | `archived/`, `archive/` dirs | SAFE | No |
| **duplicate-md** | Duplicate markdown files | MEDIUM | Yes (check links) |
| **unused-imports** | Imported but never used | MEDIUM | Yes (AST analysis) |
| **orphaned-tests** | Test files for deleted code | HIGH | Yes (test targets) |
| **unused-scripts** | Scripts not referenced | HIGH | Yes (call graph) |
| **stale-configs** | Configs for removed features | HIGH | Yes (config loaders) |

### Pre-Vacuum Validation Checklist

**Before running vacuum, verify:**
1. ✅ Knowledge graph exists (`cortex-brain/tier1/knowledge-graph.db`)
2. ✅ Recent crawl completed (< 24 hours)
3. ✅ Graph has ≥ 100 nodes (sufficient coverage)
4. ✅ Dependency edges mapped
5. ✅ No pending git commits (clean working directory)

**Vacuum will auto-abort if:**
- ❌ Knowledge graph missing or stale (> 7 days)
- ❌ Workspace has uncommitted changes
- ❌ Critical files flagged for deletion (src/main.py, requirements.txt)

### Continuous Cleanliness Strategy

**Weekly Maintenance:**
```bash
# Monday: Full analysis
python3 -m src.main "crawl . --level deep"

# Tuesday: Intelligent vacuum
python3 -m src.main "vacuum deep clean"

# Consolidate duplicate MD files
python3 -m src.main "vacuum --consolidate-md"
```

**On-Demand Cleanup:**
- **After major refactoring:** Re-crawl → Vacuum unused imports
- **Before releases:** Vacuum → Validate no broken references
- **After branch merges:** Consolidate duplicate docs

### Markdown Naming Standards

**CORTEX Repository Standard:** kebab-case for all markdown files

**Correct:**
- `architecture-overview.md`
- `getting-started.md`
- `api-reference.md`
- `user-guide.md`

**Incorrect (will be consolidated):**
- `Architecture Overview.md` → consolidate to `architecture-overview.md`
- `GettingStarted.md` → consolidate to `getting-started.md`
- `API_Reference.md` → consolidate to `api-reference.md`
- `UserGuide.md` → consolidate to `user-guide.md`

**Exceptions (keep as-is):**
- `README.md` (universal standard)
- `CHANGELOG.md` (universal standard)
- `LICENSE.md` (universal standard)
- `CONTRIBUTING.md` (universal standard)

### Post-Vacuum Validation

**Automated checks after vacuum:**
```bash
# Verify no broken imports
python -m pytest tests/ --collect-only

# Check for broken markdown links
python3 -m src.main "validate markdown-links"

# Audit trail verification
python3 -m src.main "audit query --category VACUUM --last 1h"
```

**Success Criteria:**
- ✅ All tests still pass
- ✅ No broken imports detected
- ✅ Markdown links valid
- ✅ Git status shows only intended deletions
- ✅ Audit trail logged all deletions with reasoning

**AC-IDs:** AC-VAC-001 to AC-VAC-006 (enhanced with intelligence)

---

## 👥 Team Extensibility: Orchestrator Scaffolder

**CORTEX is designed for team environments where domain experts create orchestrators.**

### Design Principle: MasterOrchestrator is IN CHARGE (NEVER BYPASSED)

```
┌─────────────────────────────────────────────────────────────────┐
│                    MasterOrchestrator                           │
│                     (Central Controller)                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ALL requests route through here → GovernanceMerger →     │   │
│  │ TodoManager → Route to appropriate orchestrator          │   │
│  └─────────────────────────────────────────────────────────┘   │
│        ↓              ↓              ↓              ↓          │
│   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐       │
│   │ Finance │   │  Health │   │   HR    │   │  Custom │       │
│   │  Orch   │   │   Orch  │   │  Orch   │   │  Orch   │       │
│   └─────────┘   └─────────┘   └─────────┘   └─────────┘       │
│   (Domain team) (Domain team) (Domain team) (Domain team)      │
└─────────────────────────────────────────────────────────────────┘
```

### Scaffolder Usage:
```bash
# Create a new domain-specific orchestrator
python3 -m src.tools.orchestrator_scaffolder \
  --name "Finance Report" \
  --domain "finance" \
  --category "execution" \
  --owner "finance-team@company.com" \
  --team "Finance Engineering" \
  --patterns "finance" "financial report" "revenue analysis"
```

### What Gets Generated:
1. **Orchestrator Python Class** - Extends `BaseOrchestratorV4`, includes `@register_with_master`
2. **Manifest YAML** - Follows `manifest-schema.yaml`, defines requirements & integrations
3. **Domain Tier3 Patterns** - `cortex-brain/tier3/domains/{domain}-patterns.yaml`
4. **Test Stubs** - pytest structure with registration/governance tests

### CRITICAL Enforcement:
- `@register_with_master` decorator - Orchestrator registers on import
- `@require_master_routing` decorator - execute() BLOCKED without MasterOrchestrator
- `MasterBypassError` - Raised if direct execution attempted
- 4-tier governance automatically injected into generated code

### Team Benefits:
- Domain experts build orchestrators for their specific needs
- CORTEX governance (SKULL + engineering standards) automatically applied
- Company practices (tier1) + learned patterns (tier3) merged
- GitHub Copilot receives accurate domain context for precise code generation

**AC-IDs:** AC-SCAFFOLD-001 to AC-SCAFFOLD-007

---

### Step 3: Transform + Audit

**Transformation adds:**
- Domain context (security, database, API, testing)
- Implicit requirements extracted from request
- Cross-cutting concerns (logging, validation, error handling)
- **AC-ID assignment** for traceability

**Audit logging (wired to `EnterpriseAuditLogger`):**
```
AUDIT: {timestamp} | {correlation_id} | ROUTING | {pattern} → {orchestrator} | AC-ID: {ac_id}
```

### Step 4: Terminal Execution

```bash
python3 -m src.main "{transformed_request}" --format markdown --correlation-id {uuid}
```

**NEVER skip terminal invocation. GitHub Copilot routes; Python executes.**

---

## 🛡️ Governance Enforcement (SKULL Rules)

**19 CORE rules enforced at runtime. Key rules:**

| Rule | Enforcement | Failure Mode |
|------|-------------|--------------|
| **CORE-001** | Operations <500 lines per increment | HTTP 502 token overflow |
| **CORE-008** | TDD: RED→GREEN→REFACTOR | Code without tests = blocked |
| **CORE-009** | Plan files in subfolders only | Root-level plans = blocked |
| **CORE-017** | Governance middleware active | Bypass = audit alert |
| **CORE-019** | TDD-Master for ALL development | Direct coding = blocked |

**Full rules:** `cortex-brain/tier0/governance/core-rules.yaml`

---

## 📊 Incremental Requirements Building

**CORTEX 6 builds requirements incrementally via this cycle:**

```
[1] Accept Request → [2] Generate AC-ID → [3] Define Acceptance Criteria
[4] Implement with TDD → [5] Validate AC → [6] Update Registry → [7] Audit Trail
```

**AC-ID Format:** `AC-{CATEGORY}-{NNN}` (e.g., AC-AUDIT-001, AC-GOV-003)

**Registry Location:** `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml`

**Audit writes to:** `cortex-brain/tier0/governance.db` (SQLite) + `cortex-brain/audit-logs/` (JSONL)

---

## 🔄 CORE WORKFLOW: User → MasterOrchestrator → TDD → Implementation

**This is THE DEFAULT WORKING MECHANISM at the core of CORTEX operations.**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: REQUEST PROCESSING                                                 │
│ User Prompt → Tokenization → MasterOrchestrator                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ PHASE 2: TASK BREAKDOWN                                                     │
│ MasterOrchestrator → Intent Classification → Task Decomposition → TodoMgr  │
├─────────────────────────────────────────────────────────────────────────────┤
│ PHASE 3: TDD ORCHESTRATOR (Software Development)                            │
│ Generate Final Instruction (F) = SKULL + BestPractices + Company + Domain  │
│ Execute: DISCOVERY → RED → GREEN → REFACTOR → VALIDATION                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ PHASE 4: IMPLEMENTATION HANDOFF                                             │
│ TDD → FileCreator / CodeModifier / TestRunner / DocGenerator               │
├─────────────────────────────────────────────────────────────────────────────┤
│ PHASE 5: PERSISTENCE                                                        │
│ TodoManager.persist() → progress-tracker.json → Audit Trail                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Final Instruction Formula (F):
```
F = merge(
    tier0.governance.core_rules,      # SKULL - 19 immutable rules (HIGHEST)
    tier1.company_practices,          # Company rules (HIGH)
    tier2.engineering_standards,      # Best practices (MEDIUM)
    tier3.domain_patterns             # Learned patterns (LOW)
)
```

### Knowledge Files Required:
| File | Tier | Content | AC-ID |
|------|------|---------|-------|
| `tier0/governance/core-rules.yaml` | 0 | 19 SKULL rules | AC-GOV-001 |
| `tier1/company-practices.yaml` | 1 | Compliance, review, deployment | AC-KNOW-003 |
| `tier2/engineering-standards.yaml` | 2 | Code style, testing, clean code | AC-KNOW-001 |
| `tier3/domain-patterns.yaml` | 3 | Auth, DB, API, security patterns | AC-KNOW-002 |

### TDD Phases (Software Development):
1. **DISCOVERY** → Detect language, framework, project structure
2. **RED** → Generate failing tests (functional, edge case, security)
3. **GREEN** → Write MINIMAL code until all tests pass
4. **REFACTOR** → Apply SOLID, DRY, KISS, YAGNI (score ≥ 80)
5. **VALIDATION** → Final test run and report

**TDD-Master Gateway Pattern (AC-TDD-GATE-001):**
- **Forward Direction:** Clarify work → Generate AC → Provide Final Instruction (F) to target orchestrator
- **Backward Direction:** Validate output → Run quality gates → Confirm user intent achieved
- **Flow:** User Request → TDD-Master (clarify) → Target Orchestrator → TDD-Master (validate) → User

**Conflict Resolution:** Tier 0 always wins → Tier 1 → Tier 2 → Tier 3

**Key AC-IDs:** AC-ORCH-006, AC-ORCH-007, AC-TDD-001 to AC-TDD-008, AC-TODO-001 to AC-TODO-004

---

## 🎯 Snowball Implementation Order

**Core infrastructure first, then features that use it:**

### Phase 1: Foundation (MUST complete first)
1. **Audit Infrastructure** (AC-AUDIT-001 to AC-AUDIT-006) → All other systems depend on logging
2. **Governance Merger** (AC-GOV-001 to AC-GOV-005) → Rule enforcement enables safe execution
3. **State Manager** (AC-STATE-001 to AC-STATE-003) → Session persistence enables continuation

### Phase 2: Orchestration Core ⭐ CORE WORKFLOW HERE
4. **MasterOrchestrator** (AC-ORCH-001 to AC-ORCH-008) → Central controller, routing, governance evaluation
5. **TodoManager** (AC-TODO-001 to AC-TODO-004) → Task creation, tracking, persistence
6. **TDD Orchestrator** (AC-TDD-001 to AC-TDD-008) → RED→GREEN→REFACTOR, Final Instruction generation
7. **Knowledge Files** (AC-KNOW-001 to AC-KNOW-003) → Engineering standards, domain patterns, company practices
8. **Planning v5** (AC-PLAN-001 to AC-PLAN-008) → Structured execution plans

### Phase 3: Feature Orchestrators
9. **ADO v2** (AC-ADO-001 to AC-ADO-006) → Work item management
10. **Investigation** (AC-INV-001 to AC-INV-003) → Root cause analysis
11. **Crawler Orchestrator** (AC-CRAWLER-001 to AC-CRAWLER-005) → Code analysis & knowledge graph
12. **Vacuum/Cleanup (Intelligent)** (AC-VAC-001 to AC-VAC-006) → Post-analysis cleanup with safety checks

**CRITICAL ORDERING:** Crawler MUST complete before Vacuum to build knowledge graph for safe deletion decisions.

### Phase 4: Intelligence Layer
10. **LLM Intent Classifier** (AC-LLM-001 to AC-LLM-004) → Fuzzy routing
11. **Vision API** (AC-VIS-001 to AC-VIS-003) → Image analysis
12. **Knowledge Practices** (AC-KNOW-001 to AC-KNOW-005) → Learned patterns

---

## ⚠️ Production Failure Modes

**These failures WILL occur under real load. Design for them:**

| Failure | Runtime Manifestation | Mitigation |
|---------|----------------------|------------|
| **Token overflow** | HTTP 502, context lost | CORE-001: <500 line increments |
| **State corruption** | Wrong phase resumed | SQLite WAL mode, transaction isolation |
| **Concurrent writes** | Race condition in tracking files | File locking via `fcntl`/`msvcrt` |
| **Stale context** | Plan built on deleted epic | Context load step + hash verification |
| **Missing AC-ID** | Untraceable changes | Mandatory AC-ID assignment |
| **Governance bypass** | Invalid code merged | Middleware hooks + audit alerts |
| **Vision API timeout** | Image analysis hangs | 500ms timeout + fallback |

---

## 🔍 Audit Integration

**All operations MUST log to `EnterpriseAuditLogger`:**

**Categories:**
- `GOVERNANCE` → Rule enforcement events
- `ORCHESTRATOR` → Execution start/complete
- `VALIDATION` → AC validation results
- `INFRASTRUCTURE` → System health
- `BRAIN` → Knowledge base operations

**Query interface:**
```bash
python3 -m src.main "audit query --ac-id AC-AUDIT-001 --last 24h"
```

---

## 🚫 Anti-Patterns (BLOCKED)

- ❌ Creating plans without checking existing epic state
- ❌ Implementing without TDD-Master orchestrator
- ❌ Skipping audit logging on state changes
- ❌ Using hardcoded paths (violates CORE-005)
- ❌ Generating summary files (violates CORE-002)
- ❌ Processing >500 lines in single increment (violates CORE-001)
- ❌ **Running Vacuum before Crawler analysis (deletes necessary files)**
- ❌ **Creating non-kebab-case markdown files (violates naming standards)**
- ❌ **Keeping .bak or archived files in active workspace (technical debt)**

---

## 📚 Truth Sources

| Concern | File | Authority Level |
|---------|------|-----------------|
| **SKULL Rules** | `tier0/governance/core-rules.yaml` | Immutable |
| **Active Epic** | `tier1/tracking/progress-tracker.json` | Working state |
| **AC Registry** | `tier1/acceptance-criteria/AC-INDEX.yaml` | Compliance |
| **Engineering Standards** | `tier2/engineering-standards.yaml` | Best practices |
| **Response Templates** | `response-templates-v4.yaml` | Output format |

---

## 🧹 Repository Cleanliness Protocol

**CORTEX maintains a clean, organized repository at all times.**

### Automated Weekly Hygiene

**Monday Morning Routine:**
```bash
# 1. Full codebase analysis
python3 -m src.main "crawl . --level deep"

# 2. Intelligent vacuum with all safety checks
python3 -m src.main "vacuum deep clean"

# 3. Consolidate duplicate markdown files
python3 -m src.main "vacuum --consolidate-md"

# 4. Validate repository health
python3 -m src.main "epic review"
```

### File Naming Standards

**Markdown Files:** kebab-case ONLY
- ✅ `architecture-overview.md`
- ❌ `Architecture Overview.md` (auto-consolidate)
- ❌ `ArchitectureOverview.md` (auto-consolidate)

**Python Files:** snake_case
- ✅ `master_orchestrator.py`
- ❌ `MasterOrchestrator.py`

**Directories:** kebab-case
- ✅ `sharpening-cortex/`
- ❌ `Sharpening_Cortex/`

### Automatic Deletions (Always Safe)

**These file types are ALWAYS deleted on vacuum:**
- `*.bak` - Backup files
- `*.tmp` - Temporary files
- `*.old` - Old versions
- `*.backup` - Backup copies
- `*~` - Editor backup files
- `.DS_Store` - macOS metadata
- `Thumbs.db` - Windows thumbnails
- `desktop.ini` - Windows metadata

**Directories auto-cleaned:**
- `archived/` - Old archived content
- `archive/` - Legacy archives
- `deprecated/` - Deprecated code
- `old/` - Old versions
- `backup/` - Backup directories

### Pre-Commit Hygiene Checks

**Before any commit, automatically:**
1. Check for .bak files → Reject commit if found
2. Validate markdown naming → Flag non-kebab-case
3. Scan for hardcoded paths → Block CORE-005 violations
4. Check for summary files → Block CORE-002 violations

**Git pre-commit hook:**
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check for .bak files
if git diff --cached --name-only | grep -E '\.bak$'; then
    echo "❌ ERROR: .bak files detected. Run vacuum before committing."
    exit 1
fi

# Check markdown naming
if git diff --cached --name-only | grep -E '\.md$' | grep -E '[A-Z]|[_ ]'; then
    echo "⚠️  WARNING: Non-kebab-case markdown files detected."
    echo "   Run: python3 -m src.main 'vacuum --consolidate-md'"
fi

exit 0
```

### Repository Health Metrics

**Target Metrics:**
- ✅ Zero .bak files
- ✅ Zero duplicate markdown files
- ✅ Zero archived directories in active workspace
- ✅ All markdown files use kebab-case
- ✅ Knowledge graph < 7 days old
- ✅ Vacuum last run < 7 days ago

**Check health:**
```bash
python3 -m src.main "audit query --category VACUUM --last 7d"
```

---

**REMEMBER:** You are a routing proxy. Load context → Match pattern → Transform → Execute via terminal. Python orchestrators handle ALL logic. Your role is **context preservation + transformation + terminal invocation + audit trail**.

**Repository Cleanliness:** Always ensure Crawler runs BEFORE Vacuum. Maintain kebab-case markdown naming. Delete .bak and archived files immediately.
