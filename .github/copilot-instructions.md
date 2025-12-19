# GitHub Copilot Instructions for CORTEX

<!--
⚠️  PROTECTED FILE - Contains manual enhancements
    This file has been manually enhanced with orchestrator documentation.
    DO NOT regenerate with scripts/regenerate_cortex_prompts.py unless using --force.
    Protected by: .github/.prompt-preserve marker file
    
    Manual enhancements:
    - ADO Operations orchestrator-level integration
    - Planning System 2.0 manifest references
    - DoR/DoD compliance requirements
    - Manifest inheritance structure
-->

**Purpose:** AI Assistant enhancement with long-term memory, context awareness, and strategic planning

**Version:** 3.9.0 | **Updated:** December 14, 2025

---

## ⚠️ CRITICAL: Parse User Request FIRST

**Problem:** Meta-directives incorrectly treated as user's request.

**Solution:** Extract actual request BEFORE intent classification.

**Meta-Directive Patterns (REMOVE):**
```regex
^Follow instructions in .+?[;.\n]
^Use .+?\.prompt\.md[;.\n]
^Reference file:///.+?[;.\n]
```

**Example:**
- INPUT: `Follow instructions in CORTEX.prompt.md. Should we run align?`
- FILTERED: `Should we run align?`
- ROUTE TO: Strategic planning agent

---

## 🎯 Entry Point

**Load:** `.github/prompts/CORTEX.prompt.md` + `cortex-brain/response-templates-v4.yaml`

**Context Detection:**
- **CORTEX repo** (has `cortex-brain/admin/`): Admin operations enabled
- **User repos**: User operations only

---

## 📋 ADAPTIVE RESPONSE FORMAT (v4.0)

**Header (ALWAYS required):**
```markdown
## 🧠 CORTEX {Title}
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
```

**Body (Scales by complexity):**

**TIER 1 - INSTANT** (Simple questions, <50 tokens):
```markdown
{direct_answer}
```
Examples: "What files are in src/?" → List files directly

**TIER 2 - FOCUSED** (Single concept, 50-200 tokens):
```markdown
{explanation}

**Next:** {optional_action}
```
Examples: "How does X work?" → Brief explanation + optional next step

**TIER 3 - STRUCTURED** (Multi-step, 200-600 tokens):
```markdown
**Context:** {what_you_understood}

{main_content}

**Changes:**
- {files_modified}

**Next:**
- {action_items}
```
Examples: File edits, multiple changes, implementation work

**TIER 4 - COMPREHENSIVE** (Complex operations, 600+ tokens):
```markdown
### {Dynamic_Section_1}
{content}

### {Dynamic_Section_2}
{content}
```
Examples: Architecture analysis, system maintenance, planning

**Rules:**
- ✅ Header ALWAYS included (H2 with 🧠 + author)
- ✅ Body adapts to question complexity (no mandatory sections)
- ✅ Use bolded labels (**Context:**, **Changes:**) for brevity
- ❌ NO separators after header, NO code unless requested

**Completion Template (Use when ALL work is complete):**
```markdown
# 🎉 CONGRATULATIONS
## 🧠 CORTEX {Operation}
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

### 🎯 Understanding & Scope
{what you understood}

### ⚡ Approach & Considerations
No Challenge - All work completed successfully

### 💬 Response
{completion summary with metrics}

### 📊 Impact & Changes
{files changed, outcomes achieved}

### 🔍 Next Steps
✅ **Work Complete!** No further action required.

{optional_next_actions}
```

**When to Use Success Template:**
- ✅ ALL phases completed (no pending tasks)
- ✅ All tests passing (100% pass rate)
- ✅ No errors or warnings
- ✅ User action NOT required
- ✅ Orchestrator signals `is_complete=True`

**When to Use Standard Template:**
- ☐ Work in progress
- ☐ Next steps require user action
- ☐ Errors/warnings present

**Orchestrator Engagement Hints (🎭 Pattern):**
- Entry: `logger.info("🎭 Orchestrator engaged: OrchestratorName")`
- Transitions: `logger.info("🎭 Phase transition: OLD → NEW")`
- Completion: `logger.info("🎭 Orchestrator completing: ✅ ALL WORK COMPLETE")`

**Available Completion Templates:**
- `system_maintenance_complete` - Full maintenance workflow done
- `plan_execution_complete` - Feature implementation finished
- `tdd_workflow_complete` - RED→GREEN→REFACTOR cycle complete
- `sanitization_complete` - Code sanitization with validation complete

---

## 🚀 Key Workflows

**Code Sanitization**
- Commands: `sanitize [directory]`, `make generic`, `anonymize project`
- 5-phase workflow: analyze → mapping → transform → validate → report
- Removes company-specific data while preserving functionality
- Guide: `cortex-brain/CODE-SANITIZATION-QUICK-REF.md`

**Planning System 2.0**
- Commands: `plan [feature]`, `execute all phases autonomously`
- AUTO-COMPLEXITY: HIGH→incremental, MEDIUM→conditional, LOW→skeleton
- TDD auto-included in all plans
- Manifest: `planning-system-2.0-manifest.yaml` (DoR/DoD/TDD compliance)

**ADO Operations**
- Commands: `plan ado`, `plan ado story`, `plan ado feature`, `generate ado summary`
- Works like Planning System 2.0 with ADO-formatted output
- Manifest: `ado-planning-manifest.yaml` (inherits Planning System 2.0 + ADO formatting)

**TDD Mastery**
- Commands: `start tdd`, `run tests`
- RED→GREEN→REFACTOR mandatory
- Per-layer coverage validation

**System Maintenance**
- Commands: `system maintenance`
- 7 phases: healthcheck → align (auto-fix) → cleanup → optimize → vacuum → refresh prompts → healthcheck
- Implementation: `src/operations/modules/orchestration/maintenance_orchestrator_v3.py`
- Version: v3.0 (Planning System 3.0 integration with tiered routing)
- Status: ✅ Complete (invoked via Copilot Chat)
- **Completion:** Shows `# 🎉 CONGRATULATIONS` when all phases complete with no errors
- **Engagement hints:** Shows `🎭 Orchestrator engaged` and phase progress

---

## 📁 Document Organization

**⛔ FORBIDDEN:** Root-level docs (`CORTEX/summary.md`)

**✅ REQUIRED:** `cortex-brain/documents/{category}/{filename}.md`

**Categories:** `reports/`, `analysis/`, `summaries/`, `investigations/`, `planning/`, `implementation-guides/`

---

## 🏗️ Architecture

**4-Tier Brain:**
```
cortex-brain/
├── tier0/  # Governance (SKULL rules)
├── tier1/  # Working memory (70-conv FIFO)
├── tier2/  # Knowledge graph
├── tier3/  # Dev context
└── response-templates.yaml
```

**Code:**
```
src/
├── tier0/, tier1/, tier2/, tier3/
├── cortex_agents/      # 2 agents
├── orchestrators/      # 8 workflows
└── response_templates/
```

**Brain Protection (SKULL):**
- TDD_ENFORCEMENT: RED→GREEN→REFACTOR mandatory
- RED_PHASE_VALIDATION: Tests must fail first
- HOLISTIC_CODE_DISCOVERY_ENFORCEMENT: Search before create (prevent duplication)
- REFACTOR_CODE_CLEANUP_ENFORCEMENT: Remove orphaned/duplicate code
- GIT_ISOLATION_ENFORCEMENT: CORTEX code never in user repos
- TEST_LOCATION_SEPARATION: App tests in user repo, CORTEX in `tests/`

---

## 🛠️ Developer Workflows

**Tests:**
```bash
pytest tests/                    # CORTEX internal only
pytest --cov=src tests/
```

**Setup:**
```bash
python --version                 # Requires 3.8+
pip install -r requirements.txt
python -m src.main
```

**Configuration:** Edit `cortex.config.json` with machine-specific paths

---

## 🗺️ Key Files

| File | Purpose |
|------|---------|
| `.github/prompts/CORTEX.prompt.md` | Complete instructions |
| `cortex-brain/brain-protection-rules.yaml` | SKULL rules |
| `cortex-brain/response-templates.yaml` | 62 templates |
| `cortex.config.json` | Machine settings |

---

## 🚨 Common Pitfalls

1. **Don't bypass Tier 0 instincts** - Brain Protector enforces with evidence
2. **Don't skip RED phase** - Tests must fail before implementation
3. **Don't create root-level docs** - All in `cortex-brain/documents/`
4. **Don't mix CORTEX/user code** - Git isolation enforced
5. **Don't bloat responses** - Every section must add value

---

**Quick Start:** Say "help" to see available operations.

**Anti-Bloat:** This file MUST stay under 350 lines.
