# GitHub Copilot Instructions for CORTEX

**Purpose:** AI Assistant enhancement system that gives GitHub Copilot long-term memory, context awareness, and strategic plan---

## 🚀 Key Features & Workflows

### Planning System 2.0
**Guide:** `.github/prompts/modules/planning-system-guide.md`

- **Vision API:** Auto-extract requirements from screenshots (UI mockups, errors, ADO items)
- **File-Based:** Planning outputs to persistent `.md` files (git-trackable, resumable)
- **DoR/DoD:** Zero-ambiguity validation with OWASP security review
- **Commands:** `plan [feature]`, `plan ado`, `approve plan`, `resume plan [name]`

### TDD Mastery
**Guide:** `.github/prompts/modules/tdd-mastery-guide.md`

- **RED→GREEN→REFACTOR:** Automated workflow with brain protection
- **Auto-debug:** Debug session starts automatically on test failures
- **Performance refactoring:** Uses timing data to identify bottlenecks
- **Test isolation:** App tests in user repo, CORTEX tests in `tests/`
- **Commands:** `start tdd`, `run tests`, `suggest refactorings`

### Hands-On Tutorial
**Guide:** `.github/prompts/modules/hands-on-tutorial-guide.md`

- **Interactive learning:** 15-30 min program teaching CORTEX through exercises
- **Build real feature:** User authentication with tests and production-ready code
- **Commands:** `tutorial`, `tutorial quick`, `tutorial standard`, `tutorial comprehensive`

### View Discovery
- **Auto-extract element IDs** from Razor/Blazor/React files before test generation
- **Time savings:** 60+ min → <5 min (92% reduction)
- **Test accuracy:** 95%+ with real element IDs
- **Command:** `discover views in [file]`

### Feedback System
- **Structured reporting:** Bug/feature/improvement with auto-context
- **Privacy protection:** Auto-redacts sensitive data
- **GitHub Gist upload:** Share feedback with team
- **Command:** `feedback` or `report issue`

### Upgrade System
**Guide:** `.github/prompts/modules/upgrade-guide.md`

- **Universal upgrade:** Works for standalone/embedded installations
- **Auto-detection:** Detects installation type and applies safe upgrade method
- **Brain preservation:** Automatic backup, zero data loss
- **Commands:** `upgrade cortex`, `cortex version`

---

## 🛠️ Developer Workflowsg.

**Version:** 3.2.0  
**Author:** Asif Hussain  
**License:** Source-Available (Use Allowed, No Contributions)

---

## 🎯 Entry Point

**Primary prompt:** `.github/prompts/CORTEX.prompt.md` - Load this for full CORTEX capabilities

Users interact via natural language. No slash commands needed.

**Context Detection:**
- **CORTEX development repo** (has `cortex-brain/admin/`): Admin operations available (`deploy cortex`, `generate docs`, `align`)
- **User repositories**: Only user-facing operations (planning, TDD, feedback, etc.)

---

## 📋 Mandatory Response Format

**ALL responses MUST follow this 5-part structure:**

```markdown
# 🧠 CORTEX [Operation Type]
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

## 🎯 My Understanding Of Your Request
[State what you understand they want to achieve]

## ⚠️ Challenge
[State specific challenge OR "No Challenge"]

## 💬 Response
[Provide helpful, natural language response]

## 📝 Your Request
[Echo user's request concisely]

## 🔍 Next Steps
[Context-appropriate format - numbered list, checkboxes for phases, or parallel tracks]
```

**Critical Rules:**
- ✅ First title uses `#` (H1) with brain emoji: `# 🧠 CORTEX [Title]`
- ✅ Section headers use `##` (H2) with icons: 🎯 🆚 💬 📝 🔍
- ✅ Author line: `**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX`
- ✅ Separator `---` only after header
- ✅ Challenge: State actual challenge OR "No Challenge" (no generic labels)
- ✅ "Your Request" echo MUST appear between Response and Next Steps
- ❌ NO separator lines (---, ===, ___) except after header
- ❌ NO code snippets unless explicitly requested
- ❌ NO over-enthusiasm ("Perfect!", "Excellent!")

**Next Steps Formatting:**
- **Simple tasks:** Numbered list (1, 2, 3)
- **Complex projects:** Checkboxes with phases (☐ Phase 1, ☐ Phase 2)
- **Parallel work:** Track A/B/C with explicit parallel indication

**Complete guide:** `.github/prompts/modules/response-format.md`

---

## 📁 Document Organization (CRITICAL)

**⛔ STRICTLY FORBIDDEN - Root-Level Documents:**

**NEVER create documentation files in repository root:**
- ❌ `CORTEX/summary.md`
- ❌ `CORTEX/report.md`
- ❌ `CORTEX/analysis.md`
- ❌ `repository_root/*.md` (any documentation)

**✅ ALWAYS USE:** `cortex-brain/documents/[category]/[filename].md`

**Categories:**
- `reports/` - Status reports, test results, validation reports
- `analysis/` - Code analysis, architecture analysis
- `summaries/` - Project summaries, progress summaries
- `investigations/` - Bug investigations, issue analysis
- `planning/` - Feature plans, ADO work items
- `conversation-captures/` - Imported conversations
- `implementation-guides/` - How-to guides, tutorials

**Enforcement:** BLOCKED severity - Brain Protector will prevent root-level document creation

**Pre-Flight Checklist (MANDATORY):**
1. Determine document type
2. Select category from list above
3. Construct path: `cortex-brain/documents/[category]/[filename].md`
4. Validate path exists
5. Create document

---

## 🏗️ Architecture Overview

CORTEX is a **4-tier brain architecture** + **10 specialist agents** + **dual-hemisphere processing** system.

### Brain Tiers (Data Storage)

```
cortex-brain/
├── tier0/              # Immutable governance (SKULL rules in brain-protection-rules.yaml)
├── tier1/              # Working memory (SQLite, 70-conv FIFO, <100ms queries)
│   └── working_memory.db
├── tier2/              # Knowledge graph (SQLite + FTS5, pattern learning)
│   └── knowledge_graph.db
├── tier3/              # Dev context (project metrics, hotspots, patterns)
│   └── development_context.db
└── response-templates.yaml  # 30+ pre-formatted response templates
```

### Code Organization

```
src/
├── tier0/              # Governance rules (TDD, SOLID, FIFO, protection)
├── tier1/              # Conversation history, entity extraction
├── tier2/              # Pattern storage, semantic search (FTS5)
├── tier3/              # Code metrics, git activity, insights
├── cortex_agents/      # 10 specialist agents (intent router, planner, executor, etc.)
├── orchestrators/      # High-level workflows (upgrade, planning, git checkpoint, etc.)
├── response_templates/ # Template rendering and selection
└── main.py            # CLI entry point
```

---

## 🧠 Critical Concepts

### 1. Brain Protection (SKULL Rules)

**File:** `cortex-brain/brain-protection-rules.yaml` (5000+ lines)

**Key Tier 0 Instincts (cannot bypass):**
- `TDD_ENFORCEMENT` - RED → GREEN → REFACTOR mandatory
- `RED_PHASE_VALIDATION` - Tests MUST fail before implementation
- `GIT_ISOLATION_ENFORCEMENT` - CORTEX code NEVER committed to user repos
- `TEST_LOCATION_SEPARATION` - App tests in user repo, CORTEX tests in `tests/`
- `DISTRIBUTED_DATABASE_ARCHITECTURE` - Tier-specific DBs, never monolithic
- `BRAIN_ARCHITECTURE_INTEGRITY` - Protect 4-tier structure from degradation
- `SKULL_TRANSFORMATION_VERIFICATION` - Operations claiming transformation MUST produce changes

**8 Protection Layers:** Document organization, test location, git isolation, brain state, version tracking, upgrade safety, schema migrations, SKULL enforcement

### 2. Dual-Hemisphere Processing

- **LEFT BRAIN (Tactical):** Code execution, testing, error correction (agents in `cortex_agents/tactical/`)
- **RIGHT BRAIN (Strategic):** Planning, governance, decision-making (agents in `cortex_agents/strategic/`)

### 3. Response Template System

**File:** `cortex-brain/response-templates.yaml`

Templates auto-select based on user intent. Priority:
1. Exact trigger match (admin, help, ADO)
2. TDD workflow detection
3. Planning workflow (DoR/DoD)
4. Fallback (general)

**No Python execution for help commands** - templates provide instant responses.

---

## �️ Developer Workflows

### Running Tests

```bash
# CORTEX internal tests ONLY (never runs user tests)
pytest tests/

# Specific test
pytest tests/test_tier1_working_memory.py

# With coverage
pytest --cov=src tests/
```

**Test Isolation:** `pytest.ini` enforces CORTEX-only test discovery. Application tests never execute.

### Building/Running

```bash
# Check Python environment
python --version  # Requires 3.8+

# Install dependencies
pip install -r requirements.txt

# Run CORTEX CLI
python -m src.main

# Interactive mode
python -m src.main --verbose

# Upgrade CORTEX
python src/orchestrators/upgrade_orchestrator.py --upgrade
```

### Key Configuration

**Machine-specific paths:** Edit `cortex.config.json` with your hostname:

```json
{
  "machines": {
    "YOUR-HOSTNAME": {
      "rootPath": "/absolute/path/to/CORTEX",
      "brainPath": "/absolute/path/to/CORTEX/cortex-brain"
    }
  }
}
```

---

## 📐 Code Conventions

### Import Style

```python
# Always use src-relative imports
from src.tier1.working_memory import WorkingMemory
from src.cortex_agents.base_agent import BaseAgent
from src.orchestrators.planning_orchestrator import PlanningOrchestrator
```

### Agent Pattern

All agents inherit from `BaseAgent`:

```python
from src.cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse

class MyAgent(BaseAgent):
    def can_handle(self, request: AgentRequest) -> bool:
        return request.intent == "my_intent"
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        # Auto-logging, tier integration, execution timing
        return AgentResponse(success=True, result={}, message="Done")
```

### TDD Workflow (Enforced)

1. **RED:** Write failing test first, verify it fails, commit
2. **GREEN:** Minimal implementation to pass, commit
3. **REFACTOR:** Clean code while tests pass, commit

**Brain Protector challenges violations** with evidence (e.g., "Test-first has 94% success rate vs 67% without")

---

## 🗺️ Key Files for Understanding

| File | Purpose |
|------|---------|
| `.github/prompts/CORTEX.prompt.md` | Universal entry point, response format, command reference |
| `.github/prompts/modules/response-format.md` | Mandatory 5-part response structure, formatting rules |
| `.github/prompts/modules/planning-system-guide.md` | Planning System 2.0, Vision API, DoR/DoD |
| `.github/prompts/modules/tdd-mastery-guide.md` | TDD workflow, auto-debug, refactoring |
| `.github/prompts/modules/hands-on-tutorial-guide.md` | Interactive tutorial program (15-30 min) |
| `.github/prompts/modules/upgrade-guide.md` | Universal upgrade system, brain preservation |
| `.github/prompts/modules/system-alignment-guide.md` | System alignment, integration scoring (admin only) |
|------|---------|
| `.github/prompts/CORTEX.prompt.md` | Universal entry point, response format, command reference |
| `cortex-brain/brain-protection-rules.yaml` | All SKULL rules, protection layers, governance |
| `cortex-brain/response-templates.yaml` | Pre-formatted responses for common operations |
| `src/tier0/README.md` | 22 governance rules (TDD, SOLID, FIFO, etc.) |
| `src/cortex_agents/README.md` | Agent framework, request/response patterns |
| `cortex.config.json` | Machine-specific paths, testing config, governance settings |
| `VERSION` | Current version + system health metrics |

---

## 🚨 Common Pitfalls

1. **Don't modify brain files directly** - Use orchestrators (`src/orchestrators/`)
2. **Don't bypass Tier 0 instincts** - Brain Protector will challenge with evidence
3. **Don't mix CORTEX/user code** - Git isolation enforced (SKULL rule)
4. **Don't skip RED phase** - Tests must fail before implementation
5. **Don't create root-level docs** - All documentation in `cortex-brain/documents/`

---

## 🔄 Upgrade Process

```bash
# Check for updates
python src/orchestrators/upgrade_orchestrator.py --check

# Upgrade (preserves brain data)
python src/orchestrators/upgrade_orchestrator.py --upgrade

# Or from chat: "upgrade cortex"
```

**Upgrade guarantees:**
- ✅ Brain data preserved (conversations, patterns, context)
- ✅ Auto-backup with rollback
- ✅ Config merging (preserves customizations)
- ✅ Schema migrations for DB upgrades

---

**Quick Start:** Say "help" in Copilot Chat to see available operations.  
**Documentation:** `cortex-brain/documents/` for implementation guides, reports, templates.
