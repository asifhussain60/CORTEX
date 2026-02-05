# CORTEX Response Format Standards
**Version:** 1.2 | **Updated:** 2026-02-05 | **Authority:** ENH-028 + ENH-032 (Chat UI Rendering)

---

## 🎯 Purpose

This document defines the unified response format for all CORTEX operations across all modes (PRE-FLIGHT, AUDIT, DESIGN, DIGEST, META-AUDIT).

**Core Principles:**
- **Chat UI Compatibility** — Formats render properly in GitHub Copilot Chat panel
- **Visual Hierarchy** — Generous spacing, H2/H3 headings, color-coded icons
- **Semantic Layering** — Progressive disclosure (Executive → Tactical → Technical)
- **Icon Consistency** — Visual status indicators with precise meaning
- **Numbered Actions** — All user prompts use numbered format for ease
- **Adaptive Density** — Response complexity matches request complexity
- **Professional Presentation** — Clean, scannable, accessible

---

## 🖥️ Chat UI Rendering Rules (CRITICAL)

**GitHub Copilot Chat has specific rendering requirements:**

### **1. Spacing for Readability**

- **2 blank lines** between major sections (H2 headings)
- **1 blank line** before and after numbered lists
- **1 blank line** before and after horizontal rules (`---`)
- **1 blank line** between list items for visual breathing room

### **2. Heading Structure**

- Use `##` for major sections (renders as H2)
- Use `###` for subsections (renders as H3)
- Always include icon + space before heading text: `## 🔥 Section Title`
- Blank line before AND after all headings

### **3. Color-Coded Icons (Semantic)**

| Icon | Purpose | Usage |
|------|---------|-------|
| 🔥 | **Critical/Urgent** | P0 issues, blocking problems |
| ⚠️ | **Engineering Analysis** | Challenge sections, warnings |
| 🎯 | **Decision Points** | User action required, next steps |
| ✅ | **Success/Complete** | Completion confirmations, verified items |
| 🔍 | **Analysis/Context** | Investigation results, findings |
| 📊 | **Metrics/Data** | Tables, statistics, measurements |
| 🚀 | **Implementation** | Execution, deployment, action items |

### **4. List Formatting**

**Numbered Lists:**
```markdown
1️⃣ **`command`** — Description ✨ **Badge**
   └─ **Impact:** What happens next

2️⃣ **`command`** — Description
   └─ **Impact:** What happens next
```

**Bullet Lists:**
```markdown
- 🟢 **Item 1** — Details here

- 🔵 **Item 2** — Details here

- ⚪ **Item 3** — Details here
```

### **5. Horizontal Rules**

Always surround with blank lines:
```markdown
[Content above]


---


[Content below]
```

### **6. Tables**

Keep tables simple (≤4 columns) for Chat UI:
```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value    | Value    | Value    |
```

### **7. Code Blocks**

Use sparingly, prefer inline code (`backticks`) for commands:
```markdown
**Command:** `cortex_process_request`
**Not:** ```python code block here ```
```

---

## 🎨 Icon System (MANDATORY)

### **Status Icons**

| Icon | Meaning | Usage | Never Use For |
|------|---------|-------|---------------|
| 🟢 | **Completed** | Work finished, verified, tests passing | Planned work, in-progress |
| 🔵 | **In Progress** | Actively executing (async operations) | Completed or planned |
| ⚪ | **Planned** | Approved, not yet started | Completed work |
| 🟡 | **Warning** | Non-blocking issue detected | Critical failures |
| 🔴 | **Critical** | Blocking issue requiring immediate action | Warnings or completed |
| ⚫ | **Skipped** | Intentionally bypassed with justification | Unintentional omissions |
| ⏳ | **Pending** | Waiting for user input or dependency | Active work |

### **Severity Prefixes**

Use in section headers and issue lists:

```markdown
> **🔴 P0 — CRITICAL**  
> System security or data integrity at risk

> **🟡 P1 — HIGH**  
> Production readiness blocked

> **🔵 P2 — MEDIUM**  
> Quality or performance degradation

> **⚪ P3 — LOW**  
> Cleanup or optimization opportunity
```

---

## 🔢 Numbered Action Prompts (MANDATORY)

### **When to Show "Next Steps"**

**SHOW numbered options when:**
- User must make a decision between alternative approaches
- Analysis complete, awaiting implementation approval
- Critical branching point in workflow

**DO NOT SHOW when:**
- ✅ Work is complete (use completion confirmation instead)
- ❌ During holistic implementation (no exit options mid-flow)
- ❌ Only one logical path forward (just proceed automatically)

### **Completion Confirmation Format**

When all work is done, use this instead of "Next Steps":

```markdown
## ✅ Implementation Complete

**Delivered:**
- [Specific deliverable 1]
- [Specific deliverable 2]
- [Specific deliverable 3]

**Verified:**
- [Verification method 1]
- [Verification method 2]

**Status:** All requested changes implemented and validated. No further action required.

---

*Ready for your next request.*
```

### **Standard Decision Format** (When Applicable)

```markdown
**🎯 [Action Type] — Choose One:**

1️⃣ **`[command]`** — [Action description] [Badge if applicable]
   └─ **Impact:** [What happens next]

2️⃣ **`[command]`** — [Action description]
   └─ **Impact:** [What happens next]

3️⃣ **`[command]`** — [Action description]
   └─ **Impact:** [What happens next]

**Quick Select:** Reply with number (1-3) or full command  
**Need Help?** Type `explain` for detailed option comparison
```

### **Holistic Implementation Principle**

During implementation:
- ❌ **NO "cancel" or "stop" options** — Implementation runs to completion
- ❌ **NO "skip" options** — All steps executed holistically
- ✅ **Progress indicators only** — Show what's happening, not exit choices

**Why:** Partial implementations create technical debt and inconsistent state

### **Badge Types**

| Badge | When to Use |
|-------|-------------|
| ✨ **Recommended** | Default/best path for most users |
| ⚠️ **Risk** | Action has known drawbacks |
| ⏱️ **Fast** | Quickest option but may skip quality checks |
| 🔒 **Secure** | Highest security posture |
| 🧪 **Experimental** | New feature, use with caution |

### **Maximum Options Rule**
- **Limit:** 5 numbered choices per decision point
- **Rationale:** Beyond 5, users face decision paralysis
- **Overflow Solution:** Use categorization or phased decisions

---

## 📐 Semantic Layering Structure

### **Layer 1: EXECUTIVE (Always Visible)**

Must fit in one screen without scrolling.

```markdown
## 🧠 CORTEX [Operation]
**Author:** Asif Hussain | **Orchestrator:** [Name] ✅

---

### ⚡ Executive Summary

**Status:** [Status with icon]  
**Scope:** [What was analyzed/modified]  
**Critical Actions:** [0-3 items requiring immediate attention]

**Details:** [Expand sections below or type `full-report`]
```

### **Narrative Flow Principle (MANDATORY)**

Every response MUST follow linear narrative structure:

```
1. CONTEXT — What was requested
2. ANALYSIS — What was discovered (no repetition of context)
3. ACTION — What was done (new information only)
4. RESULT — Final state + next steps OR completion confirmation
```

**Anti-Pattern:** Repeating the same information in multiple sections  
**Correct Pattern:** Each section adds new information building on previous sections

### **Layer 2: TACTICAL (Collapsible)**

Use `<details>` tags for non-critical information:

```markdown
<details>
<summary><b>📊 Detailed Analysis</b> (Click to expand)</summary>

[Detailed tables, metrics, evidence]

</details>
```

### **Layer 3: TECHNICAL (Linked, Not Embedded)**

```markdown
**🔍 Deep Dive Available:**
- Type `explain [section-name]` for technical details
- View full trace: `#file:path/to/logs.md`
```

---

## 🎭 Response Templates by Mode

### **PRE-FLIGHT Mode**

```markdown
## 🔧 Environment Check
**Status:** [Ready ✅ | Setup Required ❌] | **Python:** {version} | **Dependencies:** {count}/{total}

[If issues detected:]

**❌ Issue:** [description]

**🎯 Fix Options — Choose One:**

1️⃣ **`auto-fix`** — Automatic installation (recommended) ✨
   └─ **Impact:** Installs missing dependencies, ~2 minutes

2️⃣ **`manual`** — Follow manual steps
   └─ **Impact:** You control each step, ~5 minutes

3️⃣ **`skip`** — Continue anyway (⚠️ operations may fail)
   └─ **Impact:** Some features unavailable

**Quick Select:** Reply with number (1-3) or full command
```

### **AUTONOMOUS CONTINUATION Mode (NEW)**

**Trigger:** User says "proceed" / "continue" / "autonomously" + active plan exists

**Format (CONDENSED):**
```markdown
## 🏗️ CORTEX Architect
**Author:** Asif Hussain | **Mode:** Autonomous | **Phase:** {X} ✅

**Executing Phase {X} immediately...**

[TOOL CALLS - NO PREAMBLE]

## ✅ Phase {X} Complete

**Delivered:**
- [Deliverable 1]
- [Deliverable 2]

**Status:** [Brief status, no "Next Steps" unless decision required]
```

**Rules:**
- ❌ NO context gathering explanations ("Let me check...")
- ❌ NO verbose analysis before execution
- ❌ NO DoR display (already approved by "proceed")
- ❌ NO challenge generation (exploratory work only)
- ✅ Immediate tool invocation
- ✅ Results-first reporting
- ✅ <10 lines before first tool call

### **AUDIT Mode**

```markdown
## 🔍 CORTEX Audit
**Author:** Asif Hussain | **Mode:** Audit | **Scope:** [scope] ✅

---

### ⚡ Executive Summary

**Status:** [🟢 Production-Ready | 🟡 Issues Detected | 🔴 Critical Issues]  
**Compliance:** P0: {count} | P1: {count} | P2: {count} | P3: {count}

<details>
<summary><b>📋 Priority Breakdown</b></summary>

#### 🔴 P0 — Critical ({count})
[List with file:line references]

#### 🟡 P1 — High ({count})
[List with file:line references]

</details>

---

**🎯 Next Steps — Choose One:**

1️⃣ **`proceed`** — Auto-fix all detected issues ✨
   └─ **Impact:** Autonomous fixing, ~5 minutes, full verification

2️⃣ **`fix-p0-only`** — Fix critical issues only
   └─ **Impact:** Address blocking problems, P1-P3 remain

3️⃣ **`explain [issue-id]`** — Get detailed breakdown
   └─ **Impact:** Understand root cause before deciding

4️⃣ **`defer`** — Save audit results and exit
   └─ **Impact:** No changes made, audit saved to logs

**Quick Select:** Reply with number (1-4) or full command
```

### **DESIGN Mode**

```markdown
## 🏗️ CORTEX Architect
**Author:** Asif Hussain | **Mode:** Design | **Scope:** [feature] ✅

---

### ⚡ Request Analysis

**Intent:** [IMPLEMENT|FIX|REFACTOR]  
**Complexity:** [TRIVIAL|SIMPLE|MODERATE|COMPLEX]  
**Estimated Effort:** [S|M|L]

---

### ⚠️ ENGINEERING ANALYSIS

**Problem:** [1-sentence problem statement]

#### Critical Issues (High Confidence ✅)
1. **[Issue 1]** — [evidence: grep/line numbers] | Impact: [specific]
2. **[Issue 2]** — [evidence: concrete proof] | Impact: [specific]
3. **[Issue 3]** — [evidence: test/implementation gap] | Impact: [specific]

#### Recommended Fix (Effort: [S/M/L])
**Strategy:** [1-2 sentences describing approach]  
**Why:** [extensibility + scalability benefits in 1 sentence]  
**Tradeoff:** [cost] → [benefit] ([acceptable/not acceptable])  
**Evidence:** [Implementation Truth: what exists, what's missing, line numbers]

---

**🎯 Decision Required — Choose One:**

1️⃣ **`proceed`** — Implement with recommended approach ✨
   └─ **Impact:** TDD execution, ~[time], [n] files modified

2️⃣ **`modify: [changes]`** — Request approach changes
   └─ **Impact:** Re-analyze with your constraints

3️⃣ **`alternative`** — Explore different solution
   └─ **Impact:** Generate counter-proposal

4️⃣ **`cancel`** — Abort implementation
   └─ **Impact:** No changes made

**Quick Select:** Reply with number (1-4), full command, or describe changes
```

### **Progress Indicators (Async Operations)**

```markdown
## 🔄 Operation Progress

[████████░░░░░░] 60% — P2 Analysis (2/3 tools complete)

**Completed:**
- 🟢 Duplication detection (47 functions analyzed)
- 🟢 Dead code analysis (234 files scanned)

**In Progress:**
- 🔵 Complexity analysis (orchestrators/, ~30 sec remaining)

**Pending:**
- ⚪ Database hygiene check
- ⚪ Markdown validation
```

---

## 🚫 Anti-Patterns (NEVER DO)

| Anti-Pattern | Why Wrong | Correct Alternative |
|--------------|-----------|---------------------|
| ✅ for planned work | Misleading — implies completion | ⚪ (planned) |
| **Repeating content across sections** | **Cognitive overload, wastes user time** | **Each section adds NEW information only** |
| **"Next Steps" after work complete** | **False signal that more work remains** | **"Implementation Complete" confirmation** |
| **Exit options during implementation** | **Creates partial/broken implementations** | **Holistic execution to completion** |
| Unnumbered action lists | Slow to scan, harder to select | 1️⃣ 2️⃣ 3️⃣ format |
| Code blocks without context | Interrupts flow, requires scrolling | Use `<details>` or link to file |
| Flat severity indicators | P0 and P3 look identical | 🔴 P0, ⚪ P3 prefixes |
| >5 options in one decision | Decision paralysis | Categorize or phase decisions |
| Technical jargon without definition | Excludes non-experts | Use `<abbr>` tooltips |
| Embedded full file contents | Context overflow | Link with `#file:` or use excerpts |

---

## 📊 Adaptive Density Guidelines

### **Simple Requests (1-2 files, <100 LOC)**

```markdown
## ⚡ Quick Response

**Done:** [What changed]  
**Verified:** [How confirmed]  
**Files:** [List with diffs]

**🎯 Next Steps — Choose One:**

1️⃣ **`continue`** — Accept changes
2️⃣ **`undo`** — Rollback

**Quick Select:** Reply with 1 or 2
```

### **Complex Requests (Multi-phase, >1000 LOC)**

Full semantic layering with:
- Executive summary (always visible)
- Collapsible sections per phase
- Progress indicators
- Numbered decision points at each gate

---

## 🔍 Accessibility Features

### **Tooltips for Technical Terms**

```markdown
<abbr title="Test-Driven Development">TDD</abbr> enforcement active
<abbr title="Model Context Protocol">MCP</abbr> gateway operational
```

### **Screen Reader Support**

- Use semantic HTML (`<details>`, `<summary>`, `<abbr>`)
- Include alt-text equivalent in icon descriptions
- Maintain logical heading hierarchy (##, ###, ####)

---

## 📏 Quality Checklist

Before sending any response, verify:

- [ ] Response header present with correct orchestrator
- [ ] Status icons used correctly (🟢=done, ⚪=planned)
- [ ] **Linear narrative flow: Context → Analysis → Action → Result (no repetition)**
- [ ] **Completion confirmation used instead of "Next Steps" when work is done**
- [ ] **No exit options during holistic implementation**
- [ ] All user prompts numbered when decisions required (1️⃣ 2️⃣ 3️⃣)
- [ ] Severity prefixes applied (🔴 P0, 🟡 P1, 🔵 P2, ⚪ P3)
- [ ] Executive summary fits in one screen
- [ ] Collapsible sections used for detailed data
- [ ] Maximum 5 options per decision point (when applicable)
- [ ] "Quick Select" instruction present (when choices offered)
- [ ] Recommended option marked with ✨ (when choices offered)
- [ ] Impact statements provided for each option (when choices offered)

---

## 🔄 Version History

- **v1.1** (2026-02-05) — Added narrative flow principle, completion confirmation format, holistic implementation principle
- **v1.0** (2026-02-05) — Initial response format standards (ENH-028)

---

**Authority:** This document supersedes all previous formatting guidelines.  
**Enforcement:** All CORTEX prompts and agents MUST comply with these standards.  
**Review:** Format standards reviewed quarterly or when user feedback indicates issues.
