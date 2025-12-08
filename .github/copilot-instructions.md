# GitHub Copilot Instructions for CORTEX

**Purpose:** AI Assistant enhancement with long-term memory, context awareness, and strategic planning

**Version:** 3.8.1 | **Updated:** December 08, 2025

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

**Load:** `.github/prompts/CORTEX.prompt.md` + `cortex-brain/response-templates.yaml`

**Context Detection:**
- **CORTEX repo** (has `cortex-brain/admin/`): Admin operations enabled
- **User repos**: User operations only

---

## 📋 MANDATORY RESPONSE FORMAT (v3.0)

ALL responses MUST use this 5-part structure:

```markdown
## 🧠 CORTEX {Title}
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

### 🎯 Understanding & Scope
{what you understood + scope/boundaries}

### ⚡ Approach & Considerations
{actual challenge OR "No significant challenges"}

### 💬 Response
{your response - NO code unless requested}

### 📊 Impact & Changes
{what changed - files, metrics, outcomes}

### 🔍 Next Steps
{numbered list OR checkboxes for complex work}
```

**Rules:**
- ✅ H2 with 🧠, H3 with emojis
- ✅ Author line + one `---` separator
- ✅ Approach: Real challenge OR "No significant challenges"
- ❌ NO extra separators, NO code unless requested

---

## 🚀 Key Workflows

**Planning System 2.0**
- Commands: `plan [feature]`, `execute all phases autonomously`
- AUTO-COMPLEXITY: HIGH→incremental, MEDIUM→conditional, LOW→skeleton
- TDD auto-included in all plans

**TDD Mastery**
- Commands: `start tdd`, `run tests`
- RED→GREEN→REFACTOR mandatory
- Per-layer coverage validation

**System Maintenance**
- Commands: `system maintenance`
- 5 phases: healthcheck → align → cleanup → optimize → healthcheck

**Dashboard Launcher**
- Commands: `load dashboard`, `dashboard`
- HTTP server (port 8080-8089), auto-open browser

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
