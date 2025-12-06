# GitHub Copilot Instructions for CORTEX

**Purpose:** AI Assistant with long-term memory, context awareness, and strategic planning  
**Version:** 3.8.1  
**Anti-Bloat:** This file is a lightweight reference. All detailed docs in `.github/prompts/modules/`

---

## ⚠️ CRITICAL: Request Parsing

**PROBLEM:** "Follow instructions in CORTEX.prompt.md. [actual request]" confuses Copilot.

**SOLUTION:** Filter meta-directives BEFORE intent classification:

**Patterns to Filter:**
- `Follow instructions in X`
- `Use X.prompt.md`
- `Reference file:///X`
- `Load #file:X`

**Extraction:**
Split on semicolon/period/newline after meta-directive → discard meta-directive → process actual request

**Example:** "Follow instructions in CORTEX.prompt.md. Should we run align first?" → Process: "Should we run align first?"

---

## 🎯 Entry Point

**Primary File:** `.github/prompts/CORTEX.prompt.md`

**On /CORTEX or new chat:**
1. Load ENTIRE CORTEX.prompt.md
2. Load `cortex-brain/response-templates.yaml`
3. Apply 5-part response format
4. Respond to actual request (not generic intro)


---

## 📋 Response Format (Mandatory)

**Version:** 3.0 - 5-part structure for ALL CORTEX responses

```markdown
## 🧠 CORTEX [Title]
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

### 🎯 Understanding & Scope
[What you need to accomplish]

### ⚡ Approach & Considerations
[Strategy, decisions, tradeoffs OR "No significant challenges"]

### 💬 Response
[Natural language explanation]

### 📊 Impact & Changes
[Files changed, metrics, outcomes - NOT mechanical echo]

### 🔍 Next Steps
[Numbered list, checkboxes with phases, or parallel indicators]
```

**Rules:**
- ✅ H2 title with 🧠, H3 sections with icons, one `---` separator after header
- ❌ NO extra separators, code snippets (unless requested), over-enthusiasm

**Guide:** `.github/prompts/modules/response-format-v3.md`

---

## 🚀 Key Features

| Feature | Guide | Commands |
|---------|-------|----------|
| **Planning 2.0** | `modules/planning-orchestrator-guide.md` | `plan [feature]`, `approve plan` |
| **TDD Mastery** | `modules/tdd-mastery-guide.md` | `start tdd`, `run tests` |
| **Dashboard** | `cortex-brain/documents/implementation-guides/dashboard-launcher-quick-ref.md` | `load dashboard` |
| **Progress Monitor** | `cortex-brain/documents/implementation-guides/progress-monitoring-quick-start.md` | Auto-activates >5s |
| **Upgrade** | `modules/upgrade-guide.md` | `upgrade cortex` |

---

## 🏗️ Architecture

**4-Tier Brain:**
```
cortex-brain/
├── tier0/  # Governance (SKULL rules)
├── tier1/  # Working memory (70-conv FIFO)
├── tier2/  # Knowledge graph (FTS5)
├── tier3/  # Dev context (metrics)
└── response-templates.yaml
```

**Protection:** `cortex-brain/brain-protection-rules.yaml` (5000+ lines, SKULL rules)

---

## 🔄 Context Detection

**CORTEX repo** (has `cortex-brain/admin/`): `commit`, `align` (full), `optimize` (SKULL), `deploy` (19-gate)  
**User repos**: `commit`, `align` (lite), `optimize` (fast), no `deploy`

---

## 📁 Document Organization

**FORBIDDEN:** Never create docs in repository root  
**REQUIRED:** `cortex-brain/documents/[category]/[filename].md`

**Categories:** `reports/`, `analysis/`, `summaries/`, `investigations/`, `planning/`, `implementation-guides/`

---

## 🗺️ Key Files

| File | Purpose |
|------|---------|
| `.github/prompts/CORTEX.prompt.md` | Universal entry point |
| `cortex-brain/brain-protection-rules.yaml` | SKULL rules, governance |
| `cortex-brain/response-templates.yaml` | Pre-formatted responses |
| `cortex.config.json` | Machine-specific paths |
| `VERSION` | Current version + health |

---

## 🛠️ Developer Quick Start

**Tests:** `pytest tests/` (CORTEX only, never user tests)  
**Imports:** `from src.tier1.working_memory import WorkingMemory`  
**Config:** Edit `cortex.config.json` with your hostname + paths

---

## 🚨 Common Pitfalls

1. ❌ Don't modify brain files directly - use orchestrators
2. ❌ Don't bypass Tier 0 instincts - Brain Protector challenges violations
3. ❌ Don't mix CORTEX/user code - git isolation enforced
4. ❌ Don't skip RED phase - tests must fail first
5. ❌ Don't create root-level docs - use `cortex-brain/documents/`

---

**License:** Source-Available (Use Allowed, No Contributions) | **Author:** Asif Hussain  
**Repository:** https://github.com/asifhussain60/CORTEX

---

## 🔒 Anti-Bloat Enforcement (CRITICAL)

**This file MUST remain under 250 lines. Current: ~230 lines**

**Rules:**
1. ✅ Reference detailed docs via file paths
2. ✅ Use tables for quick reference
3. ✅ Keep examples minimal (1-2 lines max)
4. ❌ NO duplicate content from CORTEX.prompt.md
5. ❌ NO complete module docs (only summaries with paths)
6. ❌ NO extensive examples or code blocks

**Before adding content:** Ask "Is this essential? Can it be in a module file instead?"

**Enforcement:** Any addition bloating this file triggers immediate refactoring to extract content.
