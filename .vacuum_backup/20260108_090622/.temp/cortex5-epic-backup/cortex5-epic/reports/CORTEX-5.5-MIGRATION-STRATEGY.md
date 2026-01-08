# CORTEX 5.5 Clean Branch Migration Strategy

**Version:** 1.0.0  
**Created:** 2026-01-06  
**Purpose:** Start clean CORTEX-5.5 branch with minimal essential files, pull from CORTEX-5.0 only when needed  
**Author:** Asif Hussain

---

## 🎯 Migration Philosophy

**START CLEAN → PULL AS NEEDED**

- ✅ New branch starts with ONLY essential files for Phase 1 execution
- ✅ CORTEX-5.0 remains reference source (not merged wholesale)
- ✅ Files pulled incrementally as phases progress
- ✅ Zero technical debt carried forward
- ✅ Zero orphaned code, unused dependencies, or obsolete artifacts

---

## 📊 Essential Files Analysis

### Critical Path for Phase 1: Knowledge Extension Layer

**Phase 1 Goal:** Implement `CompanyKnowledgeProvider` with merge logic

**Required Components:**
1. Core orchestration entry point (`src/main.py`)
2. Master Orchestrator routing infrastructure
3. Brain tier structure (tier0/tier1/tier2)
4. Configuration system
5. Response template system
6. Logging and diagnostics
7. Testing framework

---

## 🗂️ Essential Files Manifest (CORTEX-5.5)

### 1. Root Configuration (7 files)

```
✅ .gitignore                      # Git exclusions
✅ requirements.txt                # Python dependencies (minimal)
✅ pytest.ini                      # Test configuration
✅ mypy.ini                        # Type checking
✅ README.md                       # Project overview
✅ LICENSE                         # Legal
✅ cortex.config.template.json    # Configuration template
```

**Rationale:** Essential infrastructure for Python project.

---

### 2. GitHub Prompts (3 files)

```
✅ .github/copilot-instructions.md       # Entry point instructions
✅ .github/prompts/CORTEX.prompt.md      # Master orchestrator gateway
✅ .github/prompts/maintenance/index.prompt.md  # Maintenance orchestrator
```

**Rationale:** GitHub Copilot routing layer.

---

### 3. cortex-brain Core Structure

#### Tier 0: Governance (5 files)

```
✅ cortex-brain/tier0/governance-schema.sql    # Governance DB schema
✅ cortex-brain/brain-protection-rules.yaml    # SKULL rules (61 rules)
✅ cortex-brain/response-templates-v4.yaml     # Response templates
✅ cortex-brain/TRUTH-SOURCES.yaml             # Source of truth registry
✅ cortex-brain/capabilities.yaml              # CORTEX capabilities
```

**Rationale:** Core governance cannot be bypassed.

#### Tier 1: Working Memory (1 folder)

```
✅ cortex-brain/tier1/                         # Session context (empty initially)
```

**Rationale:** Runtime state tracking.

#### Tier 2: Knowledge Graph (2 files + structure)

```
✅ cortex-brain/tier2/schema.sql               # Knowledge graph schema
✅ cortex-brain/tier2/company-knowledge/       # NEW: Company knowledge folder (empty)
```

**Rationale:** Phase 1 creates company knowledge structure.

#### Configuration (8 files - critical configs only)

```
✅ cortex-brain/config/master-orchestrator.yaml        # Routing config
✅ cortex-brain/config/orchestrator-registry.json      # Registry (Phase 2 target)
✅ cortex-brain/config/planning-v5-default.yaml        # Planning defaults
✅ cortex-brain/config/ado-v2-default.yaml             # ADO defaults
✅ cortex-brain/config/cleanup-v2-default.yaml         # Cleanup defaults
✅ cortex-brain/config/intent-classification-rules.yaml # Intent rules
✅ cortex-brain/config/plan-schema.yaml                # Plan validation
✅ cortex-brain/config/shared.config.json              # Shared config
```

**Rationale:** Core orchestrator configurations.

#### Manifests (11 files - active orchestrators only)

```
✅ cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml
✅ cortex-brain/manifests/orchestrators/ado-orchestrator-v2.yaml
✅ cortex-brain/manifests/orchestrators/vacuum-orchestrator-v2.yaml
✅ cortex-brain/manifests/orchestrators/cleanup-orchestrator-v2.yaml
✅ cortex-brain/manifests/orchestrators/investigation-orchestrator-v2.yaml
✅ cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml
✅ cortex-brain/manifests/orchestrators/sanitization-orchestrator-v2.yaml
✅ cortex-brain/manifests/orchestrators/debug-orchestrator-manifest.yaml
✅ cortex-brain/manifests/orchestrators/refinement-orchestrator-manifest.yaml
✅ cortex-brain/manifests/orchestrators/holistic-review-orchestrator.yaml
✅ cortex-brain/manifests/orchestrators/manifest-schema.yaml
```

**Rationale:** Active orchestrators referenced in master-orchestrator.yaml.

#### Documents (1 plan - cortex5-enhancement-epic)

```
✅ cortex-brain/documents/planning/active/cortex5-enhancement-epic/  # THIS EPIC
✅ cortex-brain/documents/orchestrators-quick-ref.md                 # Orchestrator docs
✅ cortex-brain/documents/cortex-architecture-quick-ref.md           # Architecture docs
```

**Rationale:** Active epic + reference documentation.

---

### 4. Source Code (src/)

#### Core Entry Point (1 file)

```
✅ src/main.py                                  # Application entry point
```

#### Orchestrators (7 modules - Python implementations only)

```
✅ src/orchestrators/master_orchestrator.py    # Master routing
✅ src/orchestrators/pattern_router.py         # Pattern matching
✅ src/orchestrators/state_manager.py          # State management
✅ src/orchestrators/execution_engine.py       # Lifecycle management
✅ src/orchestrators/planning/                 # Planning v5 (keep structure)
✅ src/orchestrators/ado/                      # ADO v2 (keep structure)
✅ src/orchestrators/investigation/            # Investigation v2 (keep structure)
```

**Rationale:** Core orchestration infrastructure.

#### Knowledge System (NEW - Phase 1 target)

```
🆕 src/knowledge/                              # NEW MODULE
   ├── __init__.py
   ├── company_knowledge_provider.py           # Phase 1 deliverable
   ├── knowledge_merger.py                     # Phase 1 deliverable
   └── cortex_knowledge_provider.py            # Wraps existing Tier 2
```

**Rationale:** Phase 1 implementation target.

#### Core Systems (6 modules)

```
✅ src/config/                                 # Configuration loading
✅ src/database/                               # PlanningStateDB + BrainDB
✅ src/response_templates/                     # Template rendering
✅ src/logging/                                # Logging infrastructure
✅ src/diagnostics/                            # Health checks
✅ src/utils/                                  # Shared utilities
```

**Rationale:** Core infrastructure dependencies.

---

### 5. Tests (Minimal Harness)

```
✅ tests/                                      # Test structure
   ├── __init__.py
   ├── conftest.py                             # Pytest fixtures
   ├── unit/
   │   ├── test_master_orchestrator.py
   │   └── test_pattern_router.py
   └── integration/
       └── test_orchestrator_routing.py
```

**Rationale:** TDD enforcement requires test harness.

---

## ❌ Files EXCLUDED from CORTEX-5.5 (Pull Only If Needed)

### Excluded Categories

1. **Sample Apps** → `cortex-sample-apps/` (not needed for epic)
2. **Backups** → `backups/` (historical, not needed)
3. **Build Artifacts** → `build/`, `htmlcov/`, `*.pyc`, `__pycache__/` (generated)
4. **Archives** → `cortex-brain/archives/` (historical)
5. **Old Versions** → `src/cortex_3_0/`, `src/orchestration_4_0/` (obsolete)
6. **Obsolete Scripts** → `cortex-cleanup.ps1`, `cortex-upgrade.ps1` (pre-v5 tooling)
7. **Orphaned Modules** → `src/agents/`, `src/epmo/`, `src/track_a/` (not in manifest)
8. **Unused Orchestrators** → 17+ manifests not in active registry
9. **Reports/Logs** → `reports/`, `logs/`, `tracking/` (runtime generated)
10. **Documentation Fragments** → `docs/` (outdated, not in TRUTH-SOURCES)

### Pull Strategy for Excluded Files

**IF** Phase N requires a file from CORTEX-5.0:
1. Validate it's not obsolete (check last modified date)
2. Check dependencies (AST analysis)
3. Pull minimal subtree (not entire module)
4. Document reason in phase report
5. Update this manifest

**Example:**
```
Phase 5: Custom Orchestrator Framework
→ Needs: src/orchestrators/base_orchestrator.py from CORTEX-5.0
→ Validation: File used by 3 orchestrators, last modified 2026-01-02
→ Action: Pull src/orchestrators/base_orchestrator.py + tests
→ Document: Added to phase-05-custom-orchestrator.md under "Pulled Dependencies"
```

---

## 🛠️ Migration Execution Plan

### Step 1: Create Clean Branch

```bash
# Start from main (clean slate)
git checkout main
git pull origin main

# Create new branch
git checkout -b CORTEX-5.5

# Verify clean state
git status
```

### Step 2: Create Essential Structure

```bash
# Create core directories
mkdir -p .github/prompts/maintenance
mkdir -p cortex-brain/tier0
mkdir -p cortex-brain/tier1
mkdir -p cortex-brain/tier2/company-knowledge
mkdir -p cortex-brain/config
mkdir -p cortex-brain/manifests/orchestrators
mkdir -p cortex-brain/documents/planning/active
mkdir -p src/orchestrators/planning
mkdir -p src/orchestrators/ado
mkdir -p src/orchestrators/investigation
mkdir -p src/knowledge
mkdir -p src/config
mkdir -p src/database
mkdir -p src/response_templates
mkdir -p src/logging
mkdir -p src/diagnostics
mkdir -p src/utils
mkdir -p tests/unit
mkdir -p tests/integration
```

### Step 3: Copy Essential Files from CORTEX-5.0

**Use selective cherry-pick (not merge):**

```bash
# Checkout specific files from CORTEX-5.0 (not entire tree)
git checkout CORTEX-5.0 -- .gitignore
git checkout CORTEX-5.0 -- requirements.txt
git checkout CORTEX-5.0 -- pytest.ini
git checkout CORTEX-5.0 -- mypy.ini
git checkout CORTEX-5.0 -- README.md
git checkout CORTEX-5.0 -- LICENSE

# GitHub Prompts (3 files)
git checkout CORTEX-5.0 -- .github/copilot-instructions.md
git checkout CORTEX-5.0 -- .github/prompts/CORTEX.prompt.md
git checkout CORTEX-5.0 -- .github/prompts/maintenance/index.prompt.md

# Tier 0 Governance (5 files)
git checkout CORTEX-5.0 -- cortex-brain/brain-protection-rules.yaml
git checkout CORTEX-5.0 -- cortex-brain/response-templates-v4.yaml
git checkout CORTEX-5.0 -- cortex-brain/TRUTH-SOURCES.yaml
git checkout CORTEX-5.0 -- cortex-brain/capabilities.yaml
git checkout CORTEX-5.0 -- cortex-brain/tier0/governance-schema.sql

# Tier 2 Schema
git checkout CORTEX-5.0 -- cortex-brain/tier2/schema.sql

# Configuration (8 files)
git checkout CORTEX-5.0 -- cortex-brain/config/master-orchestrator.yaml
git checkout CORTEX-5.0 -- cortex-brain/config/orchestrator-registry.json
git checkout CORTEX-5.0 -- cortex-brain/config/planning-v5-default.yaml
git checkout CORTEX-5.0 -- cortex-brain/config/ado-v2-default.yaml
git checkout CORTEX-5.0 -- cortex-brain/config/cleanup-v2-default.yaml
git checkout CORTEX-5.0 -- cortex-brain/config/intent-classification-rules.yaml
git checkout CORTEX-5.0 -- cortex-brain/config/plan-schema.yaml
git checkout CORTEX-5.0 -- cortex-brain/config/shared.config.json

# Manifests (11 files)
git checkout CORTEX-5.0 -- cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml
git checkout CORTEX-5.0 -- cortex-brain/manifests/orchestrators/ado-orchestrator-v2.yaml
git checkout CORTEX-5.0 -- cortex-brain/manifests/orchestrators/vacuum-orchestrator-v2.yaml
git checkout CORTEX-5.0 -- cortex-brain/manifests/orchestrators/cleanup-orchestrator-v2.yaml
git checkout CORTEX-5.0 -- cortex-brain/manifests/orchestrators/investigation-orchestrator-v2.yaml
git checkout CORTEX-5.0 -- cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml
git checkout CORTEX-5.0 -- cortex-brain/manifests/orchestrators/sanitization-orchestrator-v2.yaml
git checkout CORTEX-5.0 -- cortex-brain/manifests/orchestrators/debug-orchestrator-manifest.yaml
git checkout CORTEX-5.0 -- cortex-brain/manifests/orchestrators/refinement-orchestrator-manifest.yaml
git checkout CORTEX-5.0 -- cortex-brain/manifests/orchestrators/holistic-review-orchestrator.yaml
git checkout CORTEX-5.0 -- cortex-brain/manifests/orchestrators/manifest-schema.yaml

# Documents
git checkout CORTEX-5.0 -- cortex-brain/documents/planning/active/cortex5-enhancement-epic/
git checkout CORTEX-5.0 -- cortex-brain/documents/orchestrators-quick-ref.md
git checkout CORTEX-5.0 -- cortex-brain/documents/cortex-architecture-quick-ref.md

# Source Code - Core Orchestration
git checkout CORTEX-5.0 -- src/main.py
git checkout CORTEX-5.0 -- src/orchestrators/master_orchestrator.py
git checkout CORTEX-5.0 -- src/orchestrators/pattern_router.py
git checkout CORTEX-5.0 -- src/orchestrators/state_manager.py
git checkout CORTEX-5.0 -- src/orchestrators/execution_engine.py

# Source Code - Orchestrator Implementations (directories)
git checkout CORTEX-5.0 -- src/orchestrators/planning/
git checkout CORTEX-5.0 -- src/orchestrators/ado/
git checkout CORTEX-5.0 -- src/orchestrators/investigation/

# Source Code - Core Systems (directories)
git checkout CORTEX-5.0 -- src/config/
git checkout CORTEX-5.0 -- src/database/
git checkout CORTEX-5.0 -- src/response_templates/
git checkout CORTEX-5.0 -- src/logging/
git checkout CORTEX-5.0 -- src/diagnostics/
git checkout CORTEX-5.0 -- src/utils/

# Tests (minimal harness)
git checkout CORTEX-5.0 -- tests/conftest.py
git checkout CORTEX-5.0 -- tests/unit/test_master_orchestrator.py
git checkout CORTEX-5.0 -- tests/unit/test_pattern_router.py
git checkout CORTEX-5.0 -- tests/integration/test_orchestrator_routing.py
```

### Step 4: Strip requirements.txt to Minimal

**Edit requirements.txt to remove unused dependencies:**

```
# Core Dependencies Only
pyyaml>=6.0
jinja2>=3.1.0
pydantic>=2.0
sqlalchemy>=2.0
pytest>=7.4.0
pytest-cov>=4.1.0
mypy>=1.5.0
requests>=2.31.0
python-dotenv>=1.0.0
```

**Remove:**
- Selenium dependencies (custom orchestrator, Phase 6)
- Playwright dependencies (custom orchestrator, Phase 6)
- Dashboard dependencies (not needed for Phase 1-4)
- Visualization dependencies (not in epic scope)

### Step 5: Create Phase 1 Scaffolding

```bash
# Create NEW modules for Phase 1
touch src/knowledge/__init__.py
touch src/knowledge/company_knowledge_provider.py
touch src/knowledge/knowledge_merger.py
touch src/knowledge/cortex_knowledge_provider.py

# Create test structure
touch tests/unit/test_company_knowledge_provider.py
touch tests/unit/test_knowledge_merger.py
touch tests/integration/test_knowledge_integration.py

# Create company knowledge structure
mkdir -p cortex-brain/tier2/company-knowledge/sample_company
touch cortex-brain/tier2/company-knowledge/sample_company/architecture.md
touch cortex-brain/tier2/company-knowledge/sample_company/tech-stack.yaml
touch cortex-brain/tier2/company-knowledge/sample_company/api-catalog.json
touch cortex-brain/tier2/company-knowledge/sample_company/coding-standards.md
touch cortex-brain/tier2/company-knowledge/sample_company/governance.yaml
```

### Step 6: Update Epic with Pull Strategy

**Add to `cortex5-enhancement-epic/00-cortex5-epic.md`:**

```markdown
## 🔄 CORTEX-5.0 Reference Strategy

**Branch Strategy:** CORTEX-5.5 starts clean, pulls from CORTEX-5.0 as needed.

**Available in CORTEX-5.0 (pull on demand):**
- Additional orchestrator implementations (Vacuum, Cleanup, Sanitization, Debug, Refinement)
- Additional agent implementations (20+ agents in src/agents/)
- Sample applications (cortex-sample-apps/)
- Historical documentation (docs/)
- Test fixtures and mocks (tests/fixtures/)
- Utilities and helpers (src/utils/ - additional modules)

**Pull Command:**
```bash
git checkout CORTEX-5.0 -- {path/to/needed/file}
```

**Pull Criteria:**
1. File is referenced in phase implementation
2. File has active dependents (AST check)
3. File modified within last 90 days
4. File not marked as obsolete in CORTEX-5.0
```

### Step 7: Validate New Branch

```bash
# Install dependencies
pip install -r requirements.txt

# Run type checking
mypy src/ --ignore-missing-imports

# Run tests (should pass with minimal harness)
pytest tests/

# Validate structure
python -m src.main --validate-structure

# Generate validation report
python -m src.diagnostics.structure_validator > cortex-brain/documents/planning/active/cortex5-enhancement-epic/reports/CORTEX-5.5-validation-report.md
```

### Step 8: First Commit

```bash
git add .
git commit -m "feat: Initialize CORTEX-5.5 clean branch with Phase 1 scaffolding

- Essential files only (see CORTEX-5.5-MIGRATION-STRATEGY.md)
- Pull from CORTEX-5.0 on demand
- Phase 1: Knowledge Extension Layer ready
- Zero technical debt carried forward

Epic: cortex5-enhancement-epic-v2"

git push -u origin CORTEX-5.5
```

---

## 📊 File Count Comparison

| Category | CORTEX-5.0 | CORTEX-5.5 | Reduction |
|----------|------------|------------|-----------|
| **Root Files** | 25+ | 7 | 72% |
| **cortex-brain** | 150+ | 35 | 77% |
| **src/** | 500+ | 80 | 84% |
| **tests/** | 200+ | 10 | 95% |
| **Total** | ~1000+ | ~150 | **85% reduction** |

---

## 🎯 Success Criteria

### Branch Creation Success

✅ CORTEX-5.5 branch created from main (clean slate)  
✅ Essential files copied (150 files)  
✅ requirements.txt stripped to minimal dependencies  
✅ Phase 1 scaffolding created (src/knowledge/ + tests)  
✅ All tests pass (minimal harness)  
✅ mypy type checking passes  
✅ Structure validation passes  

### Epic Execution Success

✅ Phase 1 executes without needing CORTEX-5.0 files  
✅ Pull from CORTEX-5.0 only when dependency explicitly needed  
✅ Pull decisions documented in phase reports  
✅ Zero orphaned files at Phase 11 completion  
✅ 85% file reduction maintained through entire epic  

---

## 🔍 Phase-by-Phase Dependency Forecast

### Phase 1: Knowledge Extension Layer
**Needs:** ✅ All included in essential files  
**Pull from CORTEX-5.0:** ❌ None

### Phase 2: Orchestrator Registry System
**Needs:** ✅ All included (master_orchestrator.py, pattern_router.py)  
**Pull from CORTEX-5.0:** ❌ None

### Phase 3: Intelligent Goal Detection
**Needs:** LLM integration utilities  
**Pull from CORTEX-5.0:** `src/llm/` (⚠️ check if needed or rewrite)

### Phase 4: Knowledge Merge & Override Logic
**Needs:** ✅ All included in Phase 1 scaffolding  
**Pull from CORTEX-5.0:** ❌ None

### Phase 5: Custom Orchestrator Framework
**Needs:** Base orchestrator classes  
**Pull from CORTEX-5.0:** `src/orchestrators/base_orchestrator.py` (if exists)

### Phase 6: Selenium→Playwright Reference
**Needs:** AST parsing, code generation utilities  
**Pull from CORTEX-5.0:** Check `src/code_review/` for AST tools (⚠️ validate first)

### Phase 7: Rule Layering System
**Needs:** ✅ brain-protection-rules.yaml already included  
**Pull from CORTEX-5.0:** ❌ None

### Phase 8: TDD Test Harness
**Needs:** Test generation utilities  
**Pull from CORTEX-5.0:** `src/tdd/` (⚠️ check if needed or rewrite)

### Phase 9: Plan Viewer Modernization
**Needs:** HTML/CSS templates  
**Pull from CORTEX-5.0:** `templates/` + `cortex-brain/documents/planning/active/*/plan-viewer.html` (as reference)

### Phase 10: Response Template Optimization
**Needs:** ✅ response-templates-v4.yaml already included  
**Pull from CORTEX-5.0:** ❌ None

### Phase 11: End-to-End Integration
**Needs:** Integration test fixtures  
**Pull from CORTEX-5.0:** `tests/integration/` (additional test cases)

---

## ⚠️ Risk Analysis

### Risk 1: Missing Critical Dependency

**Scenario:** Phase N requires file not in essential manifest  
**Mitigation:**
1. Check CORTEX-5.0 for file (git checkout)
2. Run dependency analysis (AST)
3. Pull minimal subtree (not entire module)
4. Document pull reason in phase report
5. Update this manifest

**Likelihood:** Medium | **Impact:** Low (pull strategy addresses)

### Risk 2: Breaking Change in CORTEX-5.0

**Scenario:** File in CORTEX-5.0 depends on refactored code  
**Mitigation:**
1. Test pulled file in isolation
2. Run integration tests
3. If tests fail, pull dependencies or rewrite
4. Document decision

**Likelihood:** Low | **Impact:** Medium (may require rewrite)

### Risk 3: Epic Scope Creep

**Scenario:** Phases expand, need more CORTEX-5.0 files than forecasted  
**Mitigation:**
1. Strict phase validation (no scope creep)
2. Pull decisions require phase lead approval
3. Track pull count per phase (alert if >5 pulls)

**Likelihood:** Medium | **Impact:** Low (tracking prevents bloat)

---

## 📚 Related Documents

- **Epic Master Plan:** `00-cortex5-epic.md`
- **Phase 1 Implementation:** `phases/phase-01-knowledge-extension.md`
- **Progress Tracking:** `tracking/progress-tracker.json`
- **Orchestrator Docs:** `cortex-brain/documents/orchestrators-quick-ref.md`
- **Architecture Guide:** `cortex-brain/documents/cortex-architecture-quick-ref.md`

---

**Last Updated:** 2026-01-06  
**Next Review:** After Phase 1 completion (validate pull strategy effectiveness)  
**Maintained By:** CORTEX Planning System v5
