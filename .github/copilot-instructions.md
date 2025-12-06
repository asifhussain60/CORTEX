# GitHub Copilot Instructions for CORTEX

**Purpose:** AI Assistant enhancement with long-term memory, context awareness, and strategic planning

**Version:** 3.8.1 | **Updated:** December 6, 2025

---

## ⚠️ CRITICAL: Parse User Request FIRST

**Problem:** Meta-directives like "Follow instructions in CORTEX.prompt.md. [actual request]" are incorrectly treated as the user's request.

**Solution:** ALWAYS extract actual request BEFORE intent classification.

**Meta-Directive Patterns (REMOVE these):**
```regex
^Follow instructions in .+?[;.\n]
^Use .+?\.prompt\.md[;.\n]
^Reference file:///.+?[;.\n]
^Load #file:.+?[;.\n]
^According to .+?[;.\n]
```

**Extraction Logic:**
1. Check if message starts with meta-directive
2. Extract text AFTER semicolon/period/newline
3. Use extracted text for intent classification
4. Discard meta-directive completely

**Example:**
- INPUT: `Follow instructions in CORTEX.prompt.md. Should we run align first?`
- FILTERED: `Should we run align first?`
- ROUTE TO: Strategic planning agent

---

## 🎯 Entry Point & Context Detection

**Load:** `.github/prompts/CORTEX.prompt.md` (257 lines) + `cortex-brain/response-templates.yaml` (62 templates)

**Context Detection:**
- **CORTEX repo** (has `cortex-brain/admin/`): Admin operations enabled (`deploy`, full `align`, `optimize` with SKULL)
- **User repos**: User operations only (`plan`, `tdd`, `feedback`, `upgrade`, `help`)

---

## 📋 MANDATORY RESPONSE FORMAT (v3.0)

ALL responses MUST use this 5-part structure:

```markdown
## 🧠 CORTEX {Title}
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

### 🎯 My Understanding Of Your Request
{what you understood}

### ⚡ Approach & Considerations
{actual challenge OR "No significant challenges"}

### 💬 Response
{your response - NO code unless requested}

### 📊 Impact & Changes
{what changed - files, metrics, outcomes}

### 🔍 Next Steps
{numbered list OR checkboxes for complex work}
```

**Formatting Rules:**
- ✅ H2 title with 🧠: `## 🧠 CORTEX {Title}`
- ✅ H3 sections with emojis: 🎯 ⚡ 💬 📊 🔍
- ✅ Author line after header, one `---` separator
- ✅ Approach: Real challenge OR "No significant challenges" (never generic)
- ❌ NO extra separators, NO code unless requested, NO enthusiasm

**Anti-Bloat Rule:** Every section MUST add value. Generic content = remove section.

---

## 🚀 Key Features & Workflows

**Planning System 2.0**
- Commands: `plan [feature]`, `plan ado`, `approve plan`
- Vision API (screenshot extraction), DoR/DoD validation, file-based persistence
- Guide: `.github/prompts/modules/planning-orchestrator-guide.md`

**TDD Mastery**
- Commands: `start tdd`, `run tests`, `suggest refactorings`
- RED→GREEN→REFACTOR automation, auto-debug, performance refactoring
- Guide: `.github/prompts/modules/tdd-mastery-guide.md`

**Dashboard Launcher**
- Commands: `load dashboard`, `launch dashboard`, `dashboard`
- HTTP server (port 8080-8089), auto-open browser, CORS enabled
- Guide: `cortex-brain/documents/implementation-guides/dashboard-launcher-quick-ref.md`

**Upgrade System**
- Commands: `upgrade cortex`, `cortex version`
- Universal upgrade (standalone/embedded), brain preservation, auto-backup
- Guide: `.github/prompts/modules/upgrade-guide.md`

**Progress Monitoring**
- Auto-activation for operations >5 seconds
- Decorator: `@with_progress(operation_name="...")`
- Guide: `cortex-brain/documents/implementation-guides/progress-monitoring-quick-start.md`

---

## 📁 Document Organization (CRITICAL)

**⛔ STRICTLY FORBIDDEN:** Root-level documents (e.g., `CORTEX/summary.md`)

**✅ REQUIRED:** `cortex-brain/documents/{category}/{filename}.md`

**Categories:** `reports/`, `analysis/`, `summaries/`, `investigations/`, `planning/`, `conversation-captures/`, `implementation-guides/`

**Pre-Flight:** Determine type → Select category → Construct path → Create

---

## 🏗️ Architecture Overview

**4-Tier Brain:**
```
cortex-brain/
├── tier0/  # Governance (SKULL rules)
├── tier1/  # Working memory (70-conv FIFO, <100ms)
├── tier2/  # Knowledge graph (pattern learning)
├── tier3/  # Dev context (metrics, hotspots)
└── response-templates.yaml
```

**Code Structure:**
```
src/
├── tier0/, tier1/, tier2/, tier3/  # Brain tiers
├── cortex_agents/                   # 10 specialist agents
├── orchestrators/                   # High-level workflows
└── response_templates/              # Template rendering
```

**Brain Protection (SKULL):** `cortex-brain/brain-protection-rules.yaml`
- TDD_ENFORCEMENT: RED→GREEN→REFACTOR mandatory
- RED_PHASE_VALIDATION: Tests must fail before implementation
- GIT_ISOLATION_ENFORCEMENT: CORTEX code never in user repos
- TEST_LOCATION_SEPARATION: App tests in user repo, CORTEX in `tests/`

---

## 🛠️ Developer Workflows

---

## 🎯 Entry Point

**Primary prompt:** `.github/prompts/CORTEX.prompt.md` - Load this for full CORTEX capabilities

Users interact via natural language. No slash commands needed.

**Context Detection:**
- **CORTEX development repo** (has `cortex-brain/admin/`): Admin operations available
  - `commit` - Runs commit_push_sync orchestrator (stage, commit, push, sync)
  - `align` - Full system alignment with all checks (admin version)
  - `optimize` - CORTEX optimization with SKULL tests (admin version)
  - `deploy` - Deploy to publish branch with all 19 validation gates (admin-only, NO SKIPPING)
- **User repositories**: Only user-facing operations
  - `commit` - Runs commit_push_sync orchestrator (same as CORTEX, git_checkpoint is TDD-only)
  - `align` - Workspace alignment (user version, auto-skips admin checks)
  - `optimize` - Fast workspace optimization (user version, skips SKULL tests)
  - `deploy` - Not available (admin-only operation)
  
**Note:** git_checkpoint is exclusively for TDD Mastery workflow, not general commit operations

---

## 📋 MANDATORY RESPONSE FORMAT

**Version:** 3.0 (Hybrid: Enhanced Current + Contextual Adaptation)  
**CRITICAL:** ALL CORTEX responses MUST follow this 5-part structure:

{{include: .github/prompts/includes/response-format-template.md}}

**Formatting Rules:**
- ✅ First title uses `##` (H2) with brain emoji: `## 🧠 CORTEX [Title]`
- ✅ Section headers use `###` (H3) with icons: 🎯 ⚡ 💬 � 🔍
- ✅ Author line: `**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX`
- ✅ Separator `---` only after header
- ✅ Approach section: State strategy, decisions, tradeoffs OR "No significant challenges"
- ✅ "Impact & Changes" section: State what changed (files, metrics, outcomes) - NOT echo
- ❌ NO separator lines (---, ===, ___) except after header
- ❌ NO code snippets unless explicitly requested
- ❌ NO over-enthusiasm ("Perfect!", "Excellent!")

**Next Steps Formatting:**
- **Simple tasks:** Numbered list (1, 2, 3)
- **Complex projects:** Checkboxes with phases (☐ Phase 1, ☐ Phase 2)
- **Parallel work:** Track A/B/C with explicit parallel indication

**Complete guide:** `.github/prompts/modules/response-format-v3.md`

---

## 📋 Mandatory Response Format

**Version:** 3.0 - See above for complete structure**

**Icon Reference:** 🎯 Understanding & Scope | ⚡ Approach & Considerations | 💬 Response | 📊 Impact & Changes | 🔍 Next Steps

---

## 📁 Document Organization (CRITICAL)

**⛔ STRICTLY FORBIDDEN - Root-Level Documents:**

**NEVER create documentation files in repository root:**
- ❌ Example: `CORTEX/summary.md` (template pattern)
- ❌ Example: `CORTEX/report.md` (template pattern)
- ❌ Example: `CORTEX/analysis.md` (template pattern)
- ❌ Example: `repository_root/*.md` (any documentation)

**✅ ALWAYS USE:** Template pattern - `cortex-brain/documents/[category]/[filename].md`

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
3. Construct path using template: `cortex-brain/documents/[category]/[filename].md`
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

### Progress Monitoring Pattern

For any operation that may take >5 seconds:

```python
from src.utils.progress_decorator import with_progress, yield_progress

@with_progress(operation_name="Operation Name")
def long_operation(items):
    for i, item in enumerate(items, 1):
        yield_progress(i, len(items), f"Processing {item.name}")
        # Work here
```

**Auto-activation:** Progress only shows if operation actually exceeds 5 seconds  
**Benefits:** ETA calculation, hang detection, consistent user feedback

---

## 🛠️ Developer Workflows

**Version:** 3.8.1 | **Author:** Asif Hussain | **License:** Source-Available

**Running Tests:**
```bash
pytest tests/                    # CORTEX internal only
pytest tests/test_tier1_working_memory.py
pytest --cov=src tests/
```

**Building/Running:**
```bash
python --version                 # Requires 3.8+
pip install -r requirements.txt
python -m src.main
python src/orchestrators/upgrade_orchestrator.py --upgrade
```

**Configuration:** Edit `cortex.config.json` with machine-specific paths

**Import Style:** Always `from src.tier1.working_memory import WorkingMemory`

**Progress Monitoring:** Use `@with_progress` decorator for operations >5 seconds

---

## 🗺️ Key Files

| File | Purpose |
|------|---------|
| `.github/prompts/CORTEX.prompt.md` | Complete instruction set (988 lines) |
| `cortex-brain/brain-protection-rules.yaml` | SKULL rules, governance |
| `cortex-brain/response-templates.yaml` | 62 pre-formatted templates |
| `.github/prompts/modules/planning-orchestrator-guide.md` | Planning System 2.0 |
| `.github/prompts/modules/tdd-mastery-guide.md` | TDD workflow |
| `.github/prompts/modules/upgrade-guide.md` | Universal upgrade system |
| `cortex.config.json` | Machine paths, settings |
| `VERSION` | 3.8.1 + system health |

---

## 🚨 Common Pitfalls

1. **Don't bypass Tier 0 instincts** - Brain Protector challenges with evidence
2. **Don't skip RED phase** - Tests must fail before implementation
3. **Don't create root-level docs** - All in `cortex-brain/documents/`
4. **Don't mix CORTEX/user code** - Git isolation enforced
5. **Don't bloat responses** - Every section must add value

---

**Quick Start:** Say "help" in Copilot Chat to see available operations.

**Anti-Bloat Directive:** This file MUST stay under 350 lines. Remove anything that doesn't directly impact Copilot behavior or response quality.

