# 🎨 CORTEX Response Format Standards

> **Version:** 2.0 | **Updated:** 2026-02-13 | **Authority:** ENH-028 + ENH-032 + CORE-049 + Concise Decision Mode + Chat01 User Preferences


---


## 📋 Document Purpose

Unified response format for **all CORTEX operations** across modes: PRE-FLIGHT, AUDIT, DESIGN, DIGEST, META-AUDIT, PLAN, QUERY, REFINEMENT.

**Source of Truth:** User-preferred templates extracted from production chat sessions (chat01.md).


**Core Principles:**

| Principle | Implementation |
|-----------|----------------|
| 🤫 **Silent by Default** | Progress bars only during execution |
| 💬 **Chat Optimized** | Renders properly in GitHub Copilot Chat |
| 📐 **Visual Hierarchy** | Generous spacing, semantic headings, emoji icons |
| 📊 **Progressive Disclosure** | Executive → Tactical → Technical layering |
| 🎯 **Icon Consistency** | Precise visual status indicators |
| 🔢 **Numbered Actions** | Easy decision-making format |
| ⚖️ **Adaptive Density** | Complexity matches request scope |
| 🧠 **Intent-Adaptive Templates** | Template auto-selected by operation type (DIGEST/DESIGN/QUERY/IMPLEMENT) |
| 📦 **Structured Deliverables** | Metrics tables, markdown tables for stage results |


---


## � COMPOSABLE CONTENT BLOCKS (NEW)

**Authority:** cortex-registry/interaction/content-blocks.yaml  
**Version:** 1.0 | **Updated:** 2026-02-14

### Purpose

Reusable content sections that compose into situation-specific responses without duplication.

**Principle:** Like LEGO blocks — each block has ONE job, blocks assemble without overlap.

### Block Library (7 Core Blocks)

| Block ID | Purpose | Length | When to Use |
|----------|---------|--------|-------------|
| **BLOCK-INTRO** | Role-based introduction | 150 words | First-time user, "who are you" |
| **BLOCK-CAPABILITIES** | CORTEX overview | 200 words | "What can CORTEX do?" |
| **BLOCK-LENS** | LENS intelligence explanation | 150 words | "Explain LENS" |
| **BLOCK-ORCHESTRATORS** | Orchestrator summary | Variable | "How does orchestration work?" |
| **BLOCK-TUTORIAL** | 5-minute quick start | 100 words | "How do I start?" |
| **BLOCK-ONBOARDING** | First-time setup (MCP + git hooks) | 150 words | New repository, setup issues |
| **BLOCK-NEXT-STEPS** | Context-aware suggestions | 80 words | End of any educational response |

### Assembly Examples

**Scenario 1: First-Time User**
```
COMPOSE: BLOCK-INTRO + BLOCK-CAPABILITIES + BLOCK-TUTORIAL + BLOCK-NEXT-STEPS
RESULT: Complete onboarding (530 words)
```

**Scenario 2: "What can CORTEX do?"**
```
COMPOSE: BLOCK-CAPABILITIES + BLOCK-ORCHESTRATORS + BLOCK-NEXT-STEPS
RESULT: Capability-focused (380 words)
```

**Scenario 3: "Explain LENS"**
```
COMPOSE: BLOCK-LENS + BLOCK-NEXT-STEPS
RESULT: Laser-focused explanation (230 words)
```

**Scenario 4: User says "proceed" (autonomous execution)**
```
USE: Silent Execution Template (NOT composable blocks)
RESULT: Progress bars only, no educational content
```

### Anti-Duplication Rules

**Block Boundaries:**
- Each block covers ONE concept (no overlap)
- INTRO = welcome + personas (STOP before capabilities)
- CAPABILITIES = overview (STOP before LENS details)
- LENS = LENS only (STOP before orchestrators)

**Assembly Validation:**
- ✅ No duplicate headers (same ## can't appear twice)
- ✅ No repeated content (concept tracking prevents overlap)
- ✅ Max 800 words total (prevents information overload)
- ✅ NEXT-STEPS only once (at end)

**Example Anti-Duplication:**
```
User: "What can CORTEX do? Also explain LENS"

NAIVE: CAPABILITIES + LENS
Problem: CAPABILITIES mentions LENS → duplication

SMART: Render CAPABILITIES (skip LENS mention) → Render LENS block
Result: Zero duplication, 350 words
```

### Block Compatibility Matrix

| Block | Pairs Well With | Avoid With |
|-------|----------------|------------|
| INTRO | CAPABILITIES, TUTORIAL | LENS (too much) |
| CAPABILITIES | ORCHESTRATORS, TUTORIAL | - |
| LENS | NEXT-STEPS | INTRO, CAPABILITIES |
| ORCHESTRATORS | CAPABILITIES | TUTORIAL |
| TUTORIAL | INTRO, ONBOARDING | LENS, ORCHESTRATORS |
| ONBOARDING | TUTORIAL | LENS, ORCHESTRATORS |
| NEXT-STEPS | All blocks | - |

### When NOT to Use Blocks

**Do NOT use composable blocks for:**
- ❌ Autonomous execution (`proceed`, `implement`) → Use Silent Execution Template
- ❌ Design sessions (`/design`, `/plan`) → Use Template B
- ❌ Completion reports → Use Template D
- ❌ Implementation responses → Use Templates A-E

**Composable blocks are for:** Educational/onboarding scenarios only.

### Expansion Strategy

**Start with 7 core blocks.** Add new blocks only when:
- 3+ users need same explanation (evidence-based)
- Existing blocks can't compose to answer
- New CORTEX feature requires introduction

**Future block candidates:**
- BLOCK-REFACTORING (if refactoring questions spike)
- BLOCK-SECURITY (if security questions common)
- BLOCK-DEBUGGING (if debugging becomes frequent)
- BLOCK-TESTING (TDD deep-dive for advanced users)

**Rule:** Don't create blocks speculatively. Add on-demand based on usage.

### Integration with Existing Templates

**Composable blocks complement existing templates:**

| Template | Purpose | Blocks Relationship |
|----------|---------|-------------------|
| **Silent Execution** | Autonomous work | Blocks NOT used (progress bars only) |
| **Template A (DIGEST)** | Session analysis | Optional: Add NEXT-STEPS |
| **Template B (DESIGN/PLAN)** | Strategic planning | Optional: Add ORCHESTRATORS if relevant |
| **Template C (QUERY)** | Q&A structured | Blocks can be answers to questions |
| **Template D (COMPLETION)** | Phase complete | Optional: Add NEXT-STEPS |
| **Template E (ENHANCEMENT)** | Feature enrichment | Blocks NOT used (feature-specific) |

**Hierarchy:**
1. Intent-based templates (A-E) = primary for work operations
2. Silent execution template = autonomous mode
3. Composable blocks = educational/onboarding scenarios

### Full Specification

**See:** `cortex-registry/interaction/content-blocks.yaml` for:
- Complete block content templates
- Assembly rules (situation → blocks)
- Validation rules (anti-duplication)
- Compatibility matrix
- Usage statistics tracking

---


## �🤖 SILENT AUTONOMOUS MODE (DEFAULT)

**When user triggers execution ("proceed", "implement", "yes", "continue"):**

### Progress Bar Format (ONLY OUTPUT)

**CRITICAL:** Use markdown tables for stage results. Tree characters (`├─ └─`) collapse into one line in Copilot Chat.

**SEPARATOR FORMAT:** Use `<hr>` HTML tag to prevent overflow in Copilot Chat (box-drawing characters render too wide).

```markdown
<hr>

📋 **{Phase Name}**

`[████████░░]` 80% {Current Stage}

| # | Status | Stage | Detail |
|---|--------|-------|--------|
| 1 | ✅ | {name} | {n} tests |
| 2 | ✅ | {name} | {n} tests |
| 3 | 🔵 | {name} | in progress |
| 4 | ⚪ | {name} | pending |

**Tests:** {passed}/{total} | **Coverage:** {pct}%

<hr>
```

**Rendering Validation:**
- ✅ CORRECT: Use `<hr>` for box separators
- ❌ WRONG: `────────────────────────────────────────` (overflows in UI)
- ✅ CORRECT: Markdown table for stage results
- ❌ WRONG: `├─ ✅ S1: Name ├─ ✅ S2: Name` (tree chars collapse into one line)
- Stage names: Keep <30 chars to prevent overflow

### Completion Summary (FINAL OUTPUT)

```markdown
<hr>

✅ **{Phase Name}: COMPLETE**

[██████████] 100% | {n}/{n} tests | {pct}% coverage

Git: {commit_hash} "{commit_message}"

<hr>
```

### Error Report (ON FAILURE)

```markdown
<hr>

🔴 **{Phase Name}: BLOCKED at {Stage}**

[████░░░░░░] 40% | {passed}/{total} tests | {failures} failures

Error: {error_message}
  - Expected: {expected}
  - Actual: {actual}

Fix: {fix_suggestion}

<hr>
```

### FORBIDDEN in Silent Mode

- ❌ "I'll now proceed to implement..."
- ❌ "Let me check the registry first..."
- ❌ "Here's what I plan to do..."
- ❌ "Should I continue?"
- ❌ Multi-paragraph explanations
- ❌ Approval requests between stages

---


## � COMPLETION RESPONSE TEMPLATE (SSOT)

**Authority:** This section is the SINGLE SOURCE OF TRUTH for completion response formatting.  
**Scope:** All WAVE/PHASE/TRACK completion responses across all modes.  
**Enforcement:** Prompt files reference this section (no duplicate examples).

### Box Separator Rules (CRITICAL)

**Format:** Use `<hr>` HTML tag for all box separators.

**Why `<hr>` instead of dashes or box-drawing characters:**
- `────────────────────────────────────────` — Overflows in Copilot Chat (box-drawing chars render wide)
- `----------------------------------------` — Can trigger markdown horizontal rule rendering inconsistently
- `<hr>` — Renders as clean thin line, never overflows, semantic HTML

**Example:**
```markdown
<hr>

✅ **Phase Name: COMPLETE**

Content here

<hr>
```

### Header Hierarchy (MANDATORY)

**Structure:**
```
<hr> (top separator)
  ↓
Title (bold or emoji, NO ## header)
  ↓
Content with ### Track headers
  ↓
<hr> (final separator)
```

**Rules:**
1. **NO `##` headers** inside completion box (violates hierarchy)
2. **Track sections** use `###` headers
3. **Field labels** use `**Label:**` format (bold colon)
4. **Single opening box** with title, not multiple ## headers

### Standard Completion Template

```markdown
<hr>

✅ **{WAVE/PHASE NAME} Complete**

**Commits:** {hash1} → {hash2}
**Pushed:** origin/CORTEX
**Duration:** ~{time} total

**Metrics:**

| Metric | Before | After | Result |
|--------|--------|-------|--------|
| {metric1} | {val} | {val} | {status} ✅ |
| {metric2} | {val} | {val} | {status} ✅ |

### Track 1: {Track Name} ✅

**Files Modified:**
- {file1} → {action}
- {file2} → {action}

**Results:**
- Tests: {n}/{n} passing ✅
- Coverage: {pct}%
- Impact: {description}

### Track 2: {Track Name} ✅

**Deliverables:**
- {deliverable1} ({n} lines)
- {deliverable2} ({n} lines)

**Key Changes:**
- {change1}
- {change2}

**Impact:**
- {impact1}
- {impact2}

<hr>
```

### Field Label Standards

**Format:** `**Label:**` (bold with colon, space after colon)

**Examples:**
```markdown
✅ CORRECT:
**Commits:** abc123 → def456
**Pushed:** origin/CORTEX
**Duration:** ~1 hour

❌ WRONG:
Commits: abc123 → def456        (not bold)
**Commits**: abc123 → def456    (colon inside bold)
**Commits:**abc123 → def456     (no space after colon)
Commits - abc123 → def456       (wrong separator)
```

**Standard Labels:**
- `**Commits:**`
- `**Pushed:**`
- `**Duration:**`
- `**Files Modified:**`
- `**Results:**`
- `**Deliverables:**`
- `**Key Changes:**`
- `**Impact:**`
- `**Metrics:**`
- `**Tests:**`
- `**Coverage:**`

### Status Icon Standards

**Emoji Set:**
- ✅ `✅` = Complete / Success / Passing
- 🔵 `🔵` = In Progress / Active
- ⚪ `⚪` = Pending / Planned
- 🔴 `🔴` = Blocked / Failed / Critical
- 🟡 `🟡` = Warning / Degraded

**Usage:**
```markdown
✅ CORRECT:
- Tests: 17/17 passing ✅
- Coverage: 99% ✅
- Track 1: Version Cleanup ✅

❌ WRONG:
- Tests: 17/17 passing (passed)     (text instead of emoji)
- Coverage: 99%                     (no status indicator)
- Track 1: Version Cleanup [done]   (inconsistent format)
```

### Spacing Rules

**Between Sections:**
- 1 blank line before/after box separators
- 1 blank line before `###` track headers
- 1 blank line after `**Field:**` labels before content
- NO blank lines inside bullet lists
- NO blank lines between table rows

**Example:**
```markdown
<hr>
[1 blank line above]
### Track 1: Example ✅
[1 blank line below]
**Files Modified:**
[1 blank line below]
- file1.py
- file2.py
[NO blank lines between bullets]
[1 blank line below before next box]
<hr>
```

### Single-Track Completion Template

```markdown
<hr>
✅ {OPERATION NAME} Complete
<hr>

**Commit:** {hash}
**Pushed:** origin/CORTEX

**Changes:**
- {change1}
- {change2}
- {change3}

**Results:**
- Tests: {n}/{n} passing ✅
- Files: {n} modified
- Impact: {description}

<hr>
```

### Multi-Track Wave Completion Template

```markdown
<hr>
✅ {WAVE NAME} Complete
<hr>

**Commits:** {hash1} → {hash2} → {hash3}
**Pushed:** origin/CORTEX
**Duration:** ~{time} total

<hr>

### Track 1: {Name} ✅

**Summary:** {one-line description}

**Changes:**
- {change1}
- {change2}

**Metrics:**
- Tests: {n}/{n} passing ✅
- Coverage: {pct}%

<hr>

### Track 2: {Name} ✅

**Summary:** {one-line description}

**Deliverables:**
- {deliverable1} ({n} lines)
- {deliverable2} ({n} lines)

**Impact:**
- {impact1}
- {impact2}

<hr>

### Track 3: {Name} ✅

**Summary:** {one-line description}

**ROI Analysis:**

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| {metric1} | {val} | {val} | {pct}% ✅ |
| {metric2} | {val} | {val} | {pct}% ✅ |

<hr>
```

### Common Violations & Fixes

| Violation | Example (WRONG) | Fix (CORRECT) |
|-----------|-----------------|---------------|
| **Box-drawing separator** | `────────────────` | `<hr>` |
| **40-dash separator** | `----------------------------------------` | `<hr>` |
| **## after opening box** | `## Track 1` | `### Track 1: Name ✅` |
| **Field label not bold** | `Commits: abc` | `**Commits:** abc` |
| **No status emoji** | `Track 1: Name` | `Track 1: Name ✅` |
| **Wrong spacing** | 0 or 2+ lines | 1 blank line (per rules) |
| **Inline git info** | `Commits: abc Pushed: origin` | Separate lines with labels |
| **Concatenated stages** | `├─ ✅ S1 ├─ ✅ S2` | Use markdown table instead |

### Validation Checklist

Before marking response complete, verify:

- [ ] Box separators use `<hr>` (not `────` or `----`)
- [ ] Title uses `**bold**` (no ## header inside box)
- [ ] Track sections use ### headers
- [ ] All field labels use `**Label:**` format
- [ ] Status emojis consistent (✅🔵⚪🔴🟡)
- [ ] Spacing follows 1-blank-line rules
- [ ] Tables use proper markdown format
- [ ] Bullet lists use `-` consistently
- [ ] No text descriptions during silent execution
- [ ] Stage results use markdown table (NOT `├─ └─` tree characters)
- [ ] Stage names <30 chars

### Cross-Reference

**Prompt files must reference this section as SSOT:**
- `cortex-architect.prompt.md` § Visual Feedback Pattern
- `cortex-architect.prompt.md` § Response Header § Completion Format
- `CORTEX.prompt.md` § Response Header (Mandatory)

**DO NOT duplicate examples in prompt files.**  
**Reference:** "SSOT: See response-format-standards.md § Completion Response Template"

---


## �🖥️ Chat UI Rendering Rules

### 📏 Spacing Guidelines

| Context | Rule | Example |
|---------|------|---------|
| **Major Sections** | 3 blank lines before `##` | See section breaks in this doc |
| **Subsections** | 2 blank lines before `###` | See subsection breaks |
| **Lists** | 1 blank line before/after | See any bulleted list |
| **Horizontal Rules** | 2 blank lines before/after | `---` separators |
| **Paragraphs** | 1 blank line between | Standard spacing |


### 📐 Heading Hierarchy

```markdown
# 🎨 Document Title
## 🔥 Major Section (##)
### 📊 Subsection (###)
#### 🔹 Sub-subsection (####)
```

**Rules:**
- Always include emoji + space before text
- 1 blank line before AND after all headings
- Use semantic emoji matching section purpose


### 🎨 Icon System (Semantic)

| Ic📝 List Formatting

#### Numbered Lists (Decision Points)
```markdown
1️⃣ **`command`** — Description ✨ **Badge**
   └─ **Impact:** What happens next

2️⃣ **`command`** — Description
   └─ **Impact:** What happens next
```

#### Bullet Lists (Information)
```markdown
- 🟢 **Item 1** — Details here
- 🔵 **Item 2** — Details here
- ⚪ **Item 3** — Details here
```


### 📊 Tables (Maximum 4 Columns)

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value    | Value    | Value    |
```

**Best Practices:**
- ≤4 columns for Chat UI readability
- Bold headers for emphasis
- Use emoji in first column for visual scanning


### 💻 Code Blocks (Use Sparingly)

**Prefer:** `inline code` with backticks  
**Avoid:** Large code blocks in chat responses

```markdown
**Command:** `cortex_process_request`
**Not:** Triple-backtick blocks (breaks flow)
```


---


## 🎨 Icon System

### 🔵 Status Iconsr inline code (`backticks`) for commands:
```markdown
**Command:** `cortex_process_request`
**Not:** ```python code block here ```
```

---
✅ Use For | ❌ Never Use For |
|------|---------|-----------|-----------------|
| 🟢 | **Completed** | Work finished, verified, tests passing | Planned work, in-progress |
| 🔵 | **In Progress** | Actively executing (async operations) | Completed or planned |
| ⚪ | **Planned** | Approved, not yet started | Completed work |
| 🟡 | **Warning** | Non-blocking issue detected | Critical failures |
| 🔴 | **Critical** | Blocking issue requiring immediate action | Warnings or completed |
| ⚫ | **Skipped** | Intentionally bypassed with justification | Unintentional omissions |
| ⏳ | **Pending** | Waiting for user input or dependency | Active work |


### 🚨 Severity Levels

Use in section headers and issue lists:

| Priority | Icon | Meaning | Usage |
|----------|------|---------|-------|
| **P0** | 🔴 | **CRITICAL** | System security or data integrity at risk |
| **P1** | 🟡 | **HIGH** | Production readiness blocked |
| **P2** | 🔵 | **MEDIUM** | Quality or performance degradation |
| **P3** | ⚪ | **LOW** | Cleanup or optimization opportunity |


### 📂 Operation Icons

| Icon | Purpose | When to Use |
|------|---------|-------------|
| 🔥 | **Critical/Urgent** | P0 issues, blocking problems |
| ⚠️ | **Engineering Analysis** | Challenge sections, warnings |
| 🎯 | **Decision Points** | User action required, next steps |
| ✅ | **Success/Complete** | Completion confirmations, verified items |
| 🔍 | **Analysis/Context** | Investigation results, findings |
| 📊 | **Metrics/Data** | Tables, statistics, measurements |
| 🚀 | **Implementation** | Execution, deployment, action items |


---


## 🔢 Numbered Action Prompts
```

---✅ When to Show Options

| Show Options | Don't Show Options |
|--------------|-------------------|
| ✅ Decision between alternative approaches | ❌ Work is complete (use completion confirmation) |
| ✅ Analysis complete, awaiting approval | ❌ During holistic implementation (no exit options) |
| ✅ Critical branching point in workflow | ❌ Only one logical path forward (proceed automatically) |


### 🎉 Completion Confirmation Formatonfirmation instead)
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
🎯 Standard Decision Format
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
   └🏗️ Holistic Implementation Principle

| Rule | Rationale |
|------|-----------|
| ❌ NO "cancel" or "stop" options | Implementation runs to completion |
| ❌ NO "skip" options | All steps executed holistically |
| ✅ Progress indicators only | Show what's happening, not exit choices |

**Why:** Partial implementations create technical debt and inconsistent state


---


## 📊 ASCII Progress Bar Standards

### 📈 Visual Progress Formatns create technical debt and inconsistent state

---

## 📊 ASCII Progress Bar Standards

### **Visual Progress Format**

For multi-step implementations, use visual ASCII progress bars:

```m📏 Format Rules

| Element | Specification | Example |
|---------|---------------|---------|
| **Width** | 10 blocks fixed | `[██████████]` |
| **Filled** | `█` character | Completed portions |
| **Empty** | `░` character | Remaining work |
| **Percentage** | Right-aligned, 3 chars | ` 0%`, ` 40%`, `100%` |
| **Status Icon** | Before description | ✅🔵⚪🔴 |
| **Description** | Clear task name + context | `S1: Core implementation complete` |


### 🎚️ Phase Progress Hierarchy
|---------|---------------|
| **Width** | 10 blocks fixed `[██████████]` |
| **Filled** | `█` character for completed |
| **Empty** | `░` character for remaining |
| **Percentage** | Right-aligned, 3 chars (` 0%`, ` 40%`, `100%`) |
| **Status Icon** | ✅🔵⚪🔴 before description |
| **Description** | Clear task name + context |

### **Phase Progress Hierarchy (MANDATORY)**

**CRITICAL:** Phase title MUST be more prominent than progress bar.

✅ **CORRECT FORMAT** (Phase title in heading):
```markdown
### Phase 25: PLAN MODE Enhancement

**Progress:** [████░░░░░░] 40% - Core Infrastructure Complete

[Content continues...]
```

❌ **WRONG FORMAT** (Title and bar same level):
```markdown
### 🔄 Phase 25 Progress - Stage 1
**[████░░░░░░] 20% - Core PLAN Mode Infrastructure**
```

**Visual Hierarchy Rules:**
1. **Phase Title** = h3 heading (`###`) with phase number + name
2. **Progress Bar** = Bold paragraph below heading with "Progress:" label
3. **Stage Name** = Optional subheading or bold text after title
4. **Always separate** = Progress bar on its own line, not inline with heading

**Alternative Format (Multi-Stage):**
```markdown
### Phase 25: PLAN MODE Enhancement
**Stage 1: Core Infrastructure**

**Progress:** [████░░░░░░] 40%
```
✅ When to Use Progress Bars

| ✅ Use For | ❌ Don't Use For |
|-----------|-----------------|
| Multi-step implementations (>3 steps) | Single-step operations |
| Long-running operations | Analysis/audit results (use tables) |
| Phase/sprint tracking | Conversational responses |
| TDD cycles (RED→GREEN→REFACTOR) | Quick confirmations |


### 🏷️ Badge Types
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
- **⚖️ Maximum Options Rule

| Aspect | Guideline |
|--------|-----------|
| **Limit** | 5 numbered choices per decision point |
| **Rationale** | Beyond 5, users face decision paralysis |
| **Overflow Solution** | Use categorization or phased decisions |


---


## 📐 Semantic Layering Structure

### 📋 Layer 1: EXECUTIVE (Always Visible)
```markdown
## {icon} {title} [Operation]
**Author:** Asif Hussain | **Orchestrator:** [Name] ✅

---

### ⚡ Executive Summary

**Status:** [Status with icon]  
**Scope:** [What was analyzed/modified]  
**Cr📝 Narrative Flow Principle

Every response follows this linear structure:

| Step | Purpose | Rule |
|------|---------|------|
| 1️⃣ **CONTEXT** | What was requested | State the question/task |
| 2️⃣ **ANALYSIS** | What was discovered | No repetition of context |
| 3️⃣ **ACTION** | What was done | New information only |
| 4️⃣ **RESULT** | Final state | Next steps OR completion confirmation |

**❌ Anti-Pattern:** Repeating the same information in multiple sections  
**✅ Correct Pattern:** Each section adds new information building on previous


### 📂 Layer 2: TACTICAL (Collapsible)

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
- View full trace: #file:path/to/logs.md
```

---

## 🎭 Response Templates by Mode

### **CONCISE DECISION Mode (NEW)**

**Trigger:** User asks for review, verification, assessment, synthesis, or "does this address my concerns?"

**Purpose:** Produce executive decision memos (NOT verbose audit logs) for review requests.

**Output Structure (Fixed Order):**

```markdown
## [Decision Title]

### ✅ Verdict
[Yes|No|Partially|Verified with critical gaps] — [one-line reason]


### 🧾 Key Findings
- [Theme 1: highest-impact finding]
- [Theme 2: critical insight]
- [Theme 3: key observation]

[3-6 bullets max, single-sentence preferred]


### 🚨 Gaps & Risks *(only if they exist)*
- [Gap 1: specific issue]
- [Gap 2: specific issue]


### 🧭 Recommendations
**Primary:** [One recommended approach]

**Alternative:** [One viable alternative] *(only if realistic)*

[Brief comparison: extensibility, scalability, accuracy, efficiency]


### 🎯 DoD Confidence
DoD confidence: [X%] — [short reason].


### ⚡ Execute now vs later

**Execute now:**
- [Highest-impact immediate action 1]
- [Highest-impact immediate action 2]

**Plan for later:**
- [Structural/optimization work 1]
- [Structural/optimization work 2]

---

**What was asked:** [brief]  
**What was done:** [brief]  
**What's next:** [brief]
```

**Format Rules:**
- **Verdict:** One line, one of four options (Yes|No|Partially|Verified with critical gaps)
- **Section Headers:** Use h3 headings (`###`) with emoji for Copilot Chat compatibility
- **3-6 Bullets Max:** Per section, prefer single-sentence
- **No Code Blocks:** Decision memos only
- **No Questions:** End with closure, not open questions
- **Themes Over Inventories:** Report highest-impact item per theme
- **Smooth Memo Tone:** Not stitched audit fragments
- **Generous Spacing:** 2 blank lines between sections for readability

**Suppression List (FORBIDDEN):**
- ❌ Tool usage narration ("searched", "read", "ran", "checked")
- ❌ Log dumps, long inventories, exhaustive tables
- ❌ Repeated facts across sections
- ❌ Timelines, hour estimates, theatrical plans
- ❌ Code blocks
- ❌ Ending with questions

**When to Use:**
- Review/verify/assess intents
- "Does this address concerns?" questions
- Synthesis of analysis results
- Final solution validation

**Key Principle:** Decision memos for humans, not engineering diaries for machines.

---

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

## 🧠 USER-PREFERRED RESPONSE TEMPLATES (Chat01 Derived)

**Authority:** Extracted from production chat sessions (chat01.md) — user-validated patterns  
**Purpose:** Intelligent template selection based on operation type  
**Rule:** Auto-select template based on intent classification. Each template is proven effective in live sessions.

### Template Selection Matrix

| User Intent | Template | When to Use |
|-------------|----------|-------------|
| **DIGEST** | Concern-Resolution Analysis | Chat review, session digestion, concern validation |
| **DESIGN/PLAN** | Multi-Wave Roadmap | Wave planning, strategic breakdown, execution scoping |
| **QUERY/REFINEMENT** | Question→Answer Structured | User asks specific questions, needs clear answers |
| **IMPLEMENT (silent)** | ASCII Progress Bar | Active execution after "proceed" trigger |
| **COMPLETION** | Metrics + Deliverables Summary | Wave/phase completion, ready-to-execute handoff |

---

### Template A: DIGEST — Concern-Resolution Analysis

**Trigger:** `/digest`, review requests, "have concerns been addressed?", session analysis  
**Pattern:** Status summary → Concern table → Architecture visualization → Wave breakdown → Metrics

```markdown
## 🏛️ CORTEX Architect DIGEST
**Author:** Asif Hussain | **Orchestrator:** LENSSynthesis ✅

---

<hr>

📋 **{SESSION_ID} DIGEST: COMPLETE ANALYSIS**

`██████████` 100% Chat Review Complete

**Source:** {file} ({line_count} lines)
**Duration:** Full conversation analysis
**Status:** ✅ ALL CONCERNS ADDRESSED

<hr>

## ✅ YOUR {N} ORIGINAL CONCERNS — RESOLVED

| Concern | Challenge You Raised | Solution Delivered | Status |
|---------|---------------------|-------------------|--------|
| **{concern_1}** | {user_challenge} | {solution} | ✅ SOLVED |
| **{concern_2}** | {user_challenge} | {solution} | ✅ SOLVED |
| **{concern_3}** | {user_challenge} | {solution} | ✅ SOLVED |

---

## 🧠 {N}-LAYER SYSTEM (PROVEN)

{Use code tree visualization for architecture layers:}

Layer 1: {Layer Name} [{test_count} tests ✅]
├─ {capability_1}
├─ {capability_2}
└─ Proven: {evidence}

Layer 2: {Layer Name} [{test_count} tests ✅]
├─ {capability_1}
├─ {capability_2}
└─ Proven: {evidence}

TOTAL: {n}/{n} Tests Passing ✅ Foundation Proven ✅

---

## 📁 DIGEST DOCUMENTATION CREATED

| File | Purpose | Status |
|------|---------|--------|
| **{file_1}** | {purpose} | ✅ Created |
| **{file_2}** | {purpose} | ✅ Created |

**All committed:** `{commit_hash}`

---

## ⚡ READY FOR AUTONOMOUS EXECUTION

### Prerequisites All Met ✅
- ✅ {prerequisite_1}
- ✅ {prerequisite_2}
- ✅ {prerequisite_3}

### Next Action
**Type "proceed" to begin {next_action} autonomously.**
```

**Key Rules:**
- Always include concern-resolution table (maps user concerns → solutions)
- Architecture visualization uses code tree format (├─ └─)
- Test counts with pass status embedded in layer names
- Commit hashes referenced inline
- End with clear "proceed" trigger

---

### Template B: DESIGN/PLAN — Multi-Wave Roadmap

**Trigger:** `/plan`, "divide work into waves", strategic planning, execution scoping  
**Pattern:** Scope summary → Named waves with stage trees → Metrics table → Concerns table → Execution command

```markdown
## 🏛️ CORTEX Architect DESIGN
**Author:** Asif Hussain | **Orchestrator:** MasterOrchestrator ✅

---

<hr>

📋 **COMPLETE MASTER WAVE PLAN: {SCOPE}**

`██████████` 100% Comprehensive Analysis Complete

**Scope:** {description}
**Duration:** {total_hours} hours autonomous execution
**Token Budget:** <{total_tokens} total (<{per_wave_tokens} per wave)
**Deliverable:** {primary_deliverable}

<hr>

## 🌊 {N}-WAVE COMPREHENSIVE ROADMAP

### WAVE-1: {Meaningful Name} ({hours}h)

Stage 1: {Stage Name} [{time}, {test_count} tests]
├─ {action_1}
├─ {action_2}
└─ {action_3}

Stage 2: {Stage Name} [{time}, {test_count} tests]
├─ {action_1}
├─ {action_2}
└─ {action_3}

Deliverable: {wave_deliverable}
Success: {test_count}/{test_count} tests passing
Commits: {n} (AC-marked)

**What It Does:** {one_sentence_description}

### WAVE-2: {Meaningful Name} ({hours}h)

{Same stage tree structure...}

---

## 📊 COMPLETE METRICS

| Wave | Duration | Token | Tests | Commits | Scope | Pass Rate |
|------|----------|-------|-------|---------|-------|-----------|
| **1** | {h}h | {k}k | {n} | {n} | {scope} | 100% ✅ |
| **2** | {h}h | {k}k | {n} | {n} | {scope} | 100% ✅ |
| **TOTAL** | **{h}h** | **<{k}k** | **{n}+** | **{n}** | **{scope}** | **100%** |

---

## ✅ ALL CONCERNS ADDRESSED

| Original Concern | Resolution in Wave Plan | Wave | Status |
|------------------|------------------------|------|--------|
| **{concern_1}** | {resolution} | {wave_n} | ✅ Solved |
| **{concern_2}** | {resolution} | {wave_n} | ✅ Solved |

---

## 🎯 EXECUTION MODEL

**Sequential Waves:**
WAVE-1 ({h}h) → WAVE-2 ({h}h) → WAVE-{N} ({h}h)
   ✅           ✅           ✅

**Checkpoint Strategy:**
- Token budget 75% → Commit + continue
- Each wave independent but sequential
- No dependencies between waves

**Non-Breaking:**
- ✅ Existing API unchanged
- ✅ All tests backward compatible
- ✅ Gradual rollout possible

---

## ⚡ EXECUTION COMMAND

/implement {PLAN_ID}: {Title}

Authority: {authority_file}
Mode: Silent autonomous with ASCII progress bars
Total Duration: {hours} hours
Token Budget: <{tokens}

{Wave tree summary}

Result: {expected_deliverable}

---

**Ready to proceed?**
**Type: "proceed {PLAN_ID}" to start autonomous execution**
```

**Key Rules:**
- Every wave has a meaningful name (not generic "WAVE-1")
- Stage trees use consistent format: `Stage N: {Name} [{time}, {test_count} tests]`
- "What It Does" one-liner after each wave
- Metrics table MUST include all waves + TOTAL row
- Concern-resolution table cross-references wave numbers
- Execution command block at bottom (copy-paste ready)
- End with clear "proceed" trigger with plan ID

---

### Template C: QUERY/REFINEMENT — Question→Answer Structured

**Trigger:** User asks specific questions, "what best practices?", "have you created X?", tool audits  
**Pattern:** Questions asked → Answers with evidence → Documents created → Success metrics

```markdown
## 🏛️ CORTEX Architect {OPERATION}
**Author:** Asif Hussain | **Orchestrator:** {orchestrator} ✅

---

## 📋 What You Asked For

You requested {n} specific questions:

1. **{question_1}** ({brief_context})
2. **{question_2}** ({brief_context})
3. **{question_3}** ({brief_context})

---

## ✅ What You Got

### 📚 {N} Comprehensive Documents Created

| Document | Lines | Key Content |
|----------|-------|------------|
| **{doc_1}** | {n} | {content_summary} |
| **{doc_2}** | {n} | {content_summary} |
| **TOTAL** | **{n}+** | Complete package |

All committed: `{commit_hashes}`

---

## 🎯 Your {N} Questions → Our {N} Answers

### ❓ **Question 1:** "{original_question}"

✅ **ANSWER:** {concise_answer}

{Supporting evidence: code trees, tables, formulas, examples}

**Why This Matters:** {one_sentence_significance}

---

### ❓ **Question 2:** "{original_question}"

✅ **ANSWER:** {concise_answer}

| # | Item | Detail | Status |
|---|------|--------|--------|
| 1 | **{item}** | {detail} | ✅ |
| 2 | **{item}** | {detail} | ✅ |

**Each Item Includes:**
- {aspect_1}
- {aspect_2}

---

### ❓ **Question 3:** "{original_question}"

✅ **ANSWER:** {concise_answer}

**Active ✅ ({n} Total)**
{tool_1} ({score}/10)    {tool_2} ({score}/10)

**Underutilized ⚠️ ({n} Total)**
{tool_3} → Activate in {wave} for {benefit}

**Recommended 🔴 ({n} Total)**
{tool_4} ({wave}) → {benefit}

---

## 📊 Complete Documentation Package

### Quick Entry Points

1. **START HERE:** `{file_1}` ({n} lines, quick ref)
2. **Details:** `{file_2}` ({n} lines, deep dive)
3. **Algorithm:** `{file_3}` ({n} lines, specs)

---

## ✅ Validation Status

### All Proven ✅

- ✅ **{validation_1}** ({evidence})
- ✅ **{validation_2}** ({evidence})
- ✅ **{validation_3}** ({evidence})

---

## 📈 Success Metrics

| Metric | Expected | Status |
|--------|----------|--------|
| **{metric_1}** | {expected} | ✅ Complete |
| **{metric_2}** | {expected} | ✅ Complete |

---

## 💡 Key Takeaway

{System/feature} is:
- **Proven** ({evidence} ✅)
- **Documented** ({n}+ lines ✅)
- **Non-Breaking** ({evidence} ✅)
- **Scalable** ({evidence} ✅)
- **Production-Ready** ({evidence} ✅)

**All that's needed:** Your approval to execute.

---

**📍 Location:** {file_location}
**📦 Package:** {n} documents, {n}+ lines, {n} git commits
**✅ Status:** {STATUS} | Ready for execution
**⏱️ Timeline:** {hours} hours, {waves}
```

**Key Rules:**
- Mirror user's questions back explicitly ("What You Asked For")
- Answer each question with ✅ **ANSWER:** prefix
- Use appropriate evidence format per question (tables, trees, formulas)
- "Why This Matters" one-liner after significant answers
- Tool audits use Active/Underutilized/Recommended tiers with scores
- End with Key Takeaway bullet list (Proven/Documented/Non-Breaking/Scalable/Production-Ready)
- Footer with location, package size, status

---

### Template D: COMPLETION — Wave/Phase Complete

**Trigger:** Wave completed, phase finished, work delivered  
**Pattern:** Deliverables summary → What gets delivered per wave → Metrics → Ready confirmation

```markdown
## 🏛️ CORTEX Architect {OPERATION}
**Author:** Asif Hussain | **Orchestrator:** {orchestrator} ✅

---

<hr>

✅ **{WAVE/PHASE NAME}: COMPLETE**

`██████████` 100% | {n}/{n} tests | {pct}% coverage

**Commits:** {hash1} → {hash2}
**Pushed:** origin/{branch}
**Duration:** ~{time} total

<hr>

### What Gets Delivered

**By {Wave/Phase} End:**
- ✅ {deliverable_1}
- ✅ {deliverable_2}
- ✅ {deliverable_3}

### Enhancements to Your Vision

**Your Original Request:**
"{user_original_request}"

**What We Deliver:**

**✅ {Quality_1}**
- {detail_1}
- {detail_2}

**✅ {Quality_2}**
- {detail_1}
- {detail_2}

**✅ {Quality_3}**
- {detail_1}
- {detail_2}

**✅ Non-Breaking**
- {backward_compat_detail}
- {gradual_rollout_detail}

<hr>
```

**Key Rules:**
- Start with completion badge + progress bar at 100%
- "What Gets Delivered" section maps deliverables to user expectations
- "Enhancements to Your Vision" maps back to user's original request
- Qualities listed with ✅ prefix (Automatic, Quality Guaranteed, Future-Proof, Non-Breaking)
- Always confirm non-breaking backward compatibility

---

### Template E: ENHANCEMENT DESCRIPTION — Feature Enrichment

**Trigger:** Describing what an enhancement delivers beyond what was asked  
**Pattern:** Original request → Enhanced delivery → Quality guarantees

```markdown
## 🎯 ENHANCEMENTS TO YOUR VISION

### Your Original Request
"{user_request_verbatim}"

### What We Deliver

**✅ Fully Automatic**
- {auto_capability_1}
- {auto_capability_2}
- {auto_capability_3}

**✅ Quality Guaranteed**
- {quality_gate_1}
- {quality_gate_2}
- {quality_gate_3}

**✅ Future-Proof**
- {scaling_capability_1}
- {scaling_capability_2}
- {scaling_capability_3}

**✅ Non-Breaking**
- {compat_guarantee_1}
- {compat_guarantee_2}
- {compat_guarantee_3}
```

**Key Rules:**
- Quote user's original request verbatim
- Four quality dimensions: Automatic, Quality Guaranteed, Future-Proof, Non-Breaking
- Three evidence points per dimension
- Each point is a concrete capability (not abstract)

---

### Template Selection Logic (Auto-Detect)

```python
def select_response_template(intent: str, context: dict) -> str:
    """
    Auto-select response template based on user intent and context.
    
    Returns template name: A|B|C|D|E
    """
    # Template A: DIGEST
    if intent in ["DIGEST"] or "concerns addressed" in context.get("query", ""):
        return "TEMPLATE_A_DIGEST"
    
    # Template B: DESIGN/PLAN
    if intent in ["DESIGN", "PLAN"] or "wave" in context.get("query", ""):
        return "TEMPLATE_B_WAVE_ROADMAP"
    
    # Template C: QUERY/REFINEMENT
    if intent in ["QUERY"] or context.get("question_count", 0) > 1:
        return "TEMPLATE_C_QUESTION_ANSWER"
    
    # Template D: COMPLETION
    if context.get("is_completion", False):
        return "TEMPLATE_D_COMPLETION"
    
    # Template E: ENHANCEMENT
    if context.get("is_enhancement", False):
        return "TEMPLATE_E_ENHANCEMENT"
    
    # Default: use existing mode templates
    return "DEFAULT"
```

---

### Template Composition Rules

Templates can be **composed** (combined) for complex responses:

| Scenario | Templates Combined | Example |
|----------|--------------------|---------|
| DIGEST + PLAN | A + B | Session analysis → Wave plan (chat01 pattern) |
| PLAN + COMPLETION | B + D | Wave plan → What gets delivered |
| QUERY + PLAN | C + B | Answer questions → Updated wave plan |
| COMPLETION + ENHANCEMENT | D + E | Phase complete → Enhancement description |

**Composition Rule:** When combining, use `---` separator between template sections. Each template retains its own structure — do NOT merge fields.

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
| **Generic wave names (WAVE-1)** | **No strategic meaning, harder to track** | **Meaningful names (Foundation & Bootstrap)** |
| **Answering without mirroring question** | **User unsure if concern was understood** | **Quote user's question → provide answer** |
| **Missing concern-resolution mapping** | **User can't verify all concerns addressed** | **Table: Concern → Solution → Status** |
| **Architecture without visualization** | **Abstract, hard to grasp** | **Code tree format (├─ └─) with test counts** |
| **Missing "What It Does" per wave** | **User can't quickly scan wave purpose** | **One-sentence description after each wave** |
| **No execution command at bottom** | **User must compose command manually** | **Copy-paste ready /implement command** |

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

## � Continuation Prompts (Token-Efficient)

**CRITICAL:** Continuation prompts are ONLY for token budget exhaustion (>90% usage), NOT for session convenience.

### When to Show Continuation Prompt

**ONLY when:**
- Token usage ≥ 90% of budget (e.g., 900k/1M tokens)
- Work is NOT complete
- GitHub Copilot will begin summarizing conversation

**NEVER when:**
- Work is complete (show "Implementation Complete" instead)
- Token budget is healthy (<90%)
- User can simply reply "continue" in same session

### Token-Efficient Format

**BAD (60,000 tokens):**
```markdown
## Phase 38 Continuation Prompt

**Session Context:**
- Completed: Stages 0-2 (OrchestratorInventoryAuditor with 21/21 tests passing)
- Current Branch: CORTEX
[... 50 more lines of session replay ...]

**Remaining Work (High ROI):**

### Stage 3: Baseline Metrics Collector (4 hours, 18 tests)
- Implement BaselineMetricsCollector class
  * Metrics: test_execution_time_p50/p95, orchestrator_latency
[... 40 more lines of detailed stages ...]

**Files to Create/Modify:**
- cortex/testing/baseline_metrics_collector.py
[... 15 more file paths ...]

**Implementation Order:**
1. Create test files FIRST (TDD - CORE-008)
[... 20 more implementation details ...]
```

**GOOD (200 tokens - 99.67% reduction):**
```markdown
---

### 🔄 Continuation Required

**Token budget:** 92% used (920k/1M) — Continue in new session

**#file:cortex-architect.prompt.md**

**Session:** Phase 38 Stage 7.2
**Branch:** CORTEX  
**Context:** exposure_auditor.py ✅

**Next:** Implement tool_spec_generator.py (46 orchestrators)

**Command:** `/implement tool_spec_generator`
```

**Prompt Selection:**
- Use `#file:cortex-architect.prompt.md` if session started with AUDIT/DESIGN/PLAN mode
- Use `#file:CORTEX.prompt.md` if session started with IMPLEMENT/FIX/REFACTOR mode
- **CRITICAL:** Use the ORIGINAL prompt that initiated the session, not the current mode

### Why This Works

| Element | Purpose | Tokens |
|---------|---------|--------|
| **#file: prefix** | Loads prompt automatically | 0 (auto) |
| **Session ID** | GitHub Copilot has chat history | 10 |
| **Branch** | Git context available | 5 |
| **Context** | Last completed item | 15 |
| **Next** | Immediate action | 20 |
| **Command** | Executable intent | 10 |

**Total:** ~60 tokens vs 60,000 tokens = **99.9% reduction**

### GitHub Copilot Context Availability

**DON'T duplicate what GitHub Copilot already has:**
- ❌ Chat history (automatically available)
- ❌ File contents (use #file: references)
- ❌ Implementation details (in git history)
- ❌ Stage specifications (in phase YAMLs)
- ❌ Commands already executed (in terminal history)

**DO provide:**
- ✅ Prompt file reference (#file:)
- ✅ Current phase/stage ID
- ✅ Last completed checkpoint
- ✅ Next immediate action
- ✅ Critical command to resume

---

## �📏 Quality Checklist

Before sending any response, verify:

- [ ] Response header present with correct orchestrator
- [ ] Status icons used correctly (🟢=done, ⚪=planned)
- [ ] **Linear narrative flow: Context → Analysis → Action → Result (no repetition)**
- [ ] **Completion confirmation used instead of "Next Steps" when work is done**
- [ ] **No exit options during holistic implementation**
- [ ] **Continuation prompt ONLY shown when token budget >90% AND work incomplete**
- [ ] **Continuation prompt uses efficient format (<500 tokens) with #file: prefix**
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

- **v2.0** (2026-02-13) — Added 5 user-preferred response templates (A-E) from chat01 production sessions: DIGEST, DESIGN/PLAN, QUERY/REFINEMENT, COMPLETION, ENHANCEMENT. Added template selection matrix, composition rules, auto-detect logic. Extended anti-patterns with 6 new patterns from user feedback.
- **v1.1** (2026-02-05) — Added narrative flow principle, completion confirmation format, holistic implementation principle
- **v1.0** (2026-02-05) — Initial response format standards (ENH-028)

---

**Authority:** This document supersedes all previous formatting guidelines.  
**Enforcement:** All CORTEX prompts and agents MUST comply with these standards.  
**Review:** Format standards reviewed quarterly or when user feedback indicates issues.
