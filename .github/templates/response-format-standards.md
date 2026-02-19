# 🎨 CORTEX Response Format Standards

> **Updated:** 2026-02-17 | **Authority:** ENH-028 + ENH-032 + CORE-049 + Concise Decision Mode + Chat01 User Preferences


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


## 🎯 USER RESPONSE TEMPLATE — GOLDEN FORMAT (SSOT)

**Authority:** CORE-050 User Response Format Standard
**Version:** 4.0 | **Updated:** 2026-02-19
**Scope:** ALL non-autonomous responses in VS Code GitHub Copilot Chat
**Rule:** This is the ONLY user response template. All other files MUST pointer-reference this section — never duplicate.
**Rendering:** ALL feedback inline in Copilot Chat. NEVER create summary, report, or other .md/.txt files (CORE-002).

### Design Principles

| Principle | Implementation |
|-----------|----------------|
| **≤60 second read** | Executive-ready, scannable format |
| **Answer first** | Lead with the bottom line — answer before details |
| **Visual hierarchy** | H2 → H3 → bold → bullets (optimized for Copilot Chat) |
| **Comparison tables** | Side-by-side analysis for decisions |
| **Inline only** | Zero file generation — everything in chat session |
| **Professional icons** | Subtle, semantic — not decorative |

### The 5-Section Structure (MANDATORY)

Every non-autonomous response MUST follow this H2 structure:

```markdown
## 📋 Summary

{1-2 sentences. State the request and the bottom-line answer immediately.}

---

## 🔍 Analysis

{Present the core finding in a formatted panel. Include engineering analysis,
risk assessment, or trade-off summary. Use comparison tables for alternatives.}

### Key Findings

| Finding | Impact | Confidence |
|---------|--------|------------|
| {finding_1} | {impact} | ✅ High |
| {finding_2} | {impact} | 🟡 Medium |

### Alternatives Considered

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| {approach_A} | {pros} | {cons} | ✅ Recommended |
| {approach_B} | {pros} | {cons} | ⚪ Viable |

---

## 💡 Recommendation

**Primary:** {One clear recommended action}

{Brief justification — extensibility, scalability, evidence.}

### Implementation Path

1. {Step 1 — concrete, actionable}
2. {Step 2 — with expected outcome}
3. {Step 3 — verification criteria}

---

## ⚖️ Benefits & Risks

| Dimension | Benefit | Risk | Mitigation |
|-----------|---------|------|------------|
| {dimension_1} | {benefit} | {risk} | {mitigation} |
| {dimension_2} | {benefit} | {risk} | {mitigation} |

---

## 🎯 Next Steps

**Immediate:**
1. {Highest-impact action}
2. {Second priority action}

**Later:**
- {Deferred optimization}
- {Future enhancement}

> **Confidence:** {High · Medium · Low} · Based on {evidence summary}

> **Action required:** Type `proceed` to execute, or reply with modifications.
```

### Section Rules

| Section | Required | Max Length | Key Rule |
|---------|----------|-----------|----------|
| **Summary** | ✅ Always | 2 sentences | Answer first, context second |
| **Analysis** | ✅ Always | 200 words | Tables for findings + alternatives |
| **Recommendation** | ✅ Always | 150 words | ONE primary recommendation, numbered steps |
| **Benefits & Risks** | 🟡 Medium+ | 1 table | 4-column comparison — skip for simple requests |
| **Next Steps** | ✅ Always | 100 words | Split: Immediate (numbered) + Later (bullets) |

### H3 Sub-Sections (Optional Depth)

Each H2 section can contain H3 sub-sections for progressive detail:

```markdown
## 🔍 Analysis

### Key Findings
{table or bullets}

### Root Cause
{1-2 sentences with evidence}

### Alternatives Considered
{comparison table}
```

**Rule:** H3s are optional — use only when the analysis warrants depth. Simple requests skip H3s entirely.

### Adaptive Density (MANDATORY)

| Request Complexity | Summary | Analysis | Recommendation | Benefits & Risks | Next Steps |
|--------------------|---------|----------|----------------|-----------------|------------|
| **Simple** (1-2 files) | 1 sentence | 2-3 bullets | 1 sentence | ⚪ Skip | 1 action |
| **Medium** (feature) | 2 sentences | Findings table | Numbered steps | 3-row table | 2-3 actions |
| **Complex** (multi-phase) | 2 sentences + scope | Full analysis + alternatives table | Strategy + steps | Full table + mitigations | Immediate + Later split |

### Formatting Standards (Copilot Chat Optimized)

| Element | Format | Why |
|---------|--------|-----|
| **Section dividers** | `---` (markdown HR) | Clean rendering in Copilot Chat |
| **Tables** | Standard markdown, ≤5 columns | Prevents overflow |
| **Status icons** | ✅ 🟡 ⚪ 🔴 | Semantic, not decorative |
| **Code references** | `inline backticks` | Scannable |
| **Evidence** | Bold labels: `**File:** path` | Consistent field formatting |
| **Spacing** | 1 blank line between sections | Readable without waste |

### Suppression List (FORBIDDEN in User Responses)

| Forbidden | Why | Use Instead |
|-----------|-----|-------------|
| ❌ "I'll now proceed to..." | Narration wastes read time | Just do the work silently |
| ❌ "Let me check the registry..." | Tool usage narration | Present findings directly |
| ❌ Creating .md/.txt files | CORE-002 violation | Inline in chat session |
| ❌ >5 column tables | Overflow in Copilot Chat | Split into 2 tables |
| ❌ Repeated information across sections | Cognitive overload | Each section adds NEW info only |
| ❌ Generic phase names | No strategic meaning | Meaningful names always |
| ❌ Log dumps or inventories | Not executive-ready | Themed findings, highest-impact per theme |
| ❌ Ending with open questions | Leaves user uncertain | End with closure + proceed option |
| ❌ `├─ └─` tree characters | Collapse in Copilot Chat | Use tables or bullet lists |

### Response Header (Simplified)

**ONE line, ONE time, top of response:**

```markdown
## {icon} CORTEX {mode}
```

**Icons by mode:** 🔧 PRE-FLIGHT | 🔍 AUDIT/QUERY | 📚 DIGEST | 📋 PLAN | 🎨 DESIGN | ⚡ IMPLEMENT

**Rules:**
- ✅ Appears ONCE at the very top (never repeated)
- ✅ Followed by `---` separator
- ❌ NO author/orchestrator line in user-facing responses (prompt-internal only)
- ❌ NO mid-response headers

---


## 📦 COMPOSABLE CONTENT BLOCKS

**Authority:** cortex-registry/interaction/content-blocks.yaml  
**Updated:** 2026-02-14

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
- ❌ Autonomous execution (`proceed`, `implement`) → Use Silent Execution Template (§ SILENT AUTONOMOUS MODE)
- ❌ Work operations (design, plan, audit, query, implement) → Use 5-Section Golden Format (§ USER RESPONSE TEMPLATE)

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

**Composable blocks complement the two response templates:**

| Template | Purpose | Blocks Relationship |
|----------|---------|-------------------|
| **Silent Execution** (§ SILENT AUTONOMOUS MODE) | Autonomous work | Blocks NOT used (progress bars only) |
| **5-Section Golden Format** (§ USER RESPONSE TEMPLATE) | All work operations | Optional: Add NEXT-STEPS, ORCHESTRATORS as needed |

**Hierarchy:**
1. 5-Section Golden Format = primary for all work operations (adapts via density)
2. Silent execution template = autonomous mode (progress bars only)
3. Composable blocks = educational/onboarding scenarios

### Full Specification

**See:** `cortex-registry/interaction/content-blocks.yaml` for:
- Complete block content templates
- Assembly rules (situation → blocks)
- Validation rules (anti-duplication)
- Compatibility matrix
- Usage statistics tracking

---


## 🤖 SILENT AUTONOMOUS MODE — GOLDEN TEMPLATE (SSOT)

**Authority:** CORE-049 Silent Autonomous Execution Protocol
**Version:** 2.0 | **Updated:** 2026-02-19
**Scope:** ALL orchestrators (MasterOrchestrator, PlanningOrchestrator, VacuumOrchestrator, TDDOrchestrator, and all others)
**Rule:** This is the ONLY autonomous execution template. All other files MUST pointer-reference this section — never duplicate.

**When user triggers execution ("proceed", "implement", "yes", "continue"):**

### Progress Template (IN-PROGRESS)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 {PHASE_NAME} Stage {N}: {STAGE_TITLE}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[████████░░] 80% Stage {N} In Progress

├─ ✅ S1: {name} ({n} tests)
├─ ✅ S2: {name} ({n} tests)
├─ 🔵 S3: {name} (in progress)
└─ ⚪ S4: {name} (pending)

Tests: {passed}/{total} | Coverage: {pct}%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Completion Template (ALL STAGES DONE)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 {PHASE_NAME} Stage {N}: {STAGE_TITLE}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[██████████] 100% All Stages Complete

├─ ✅ S1: {name} ({n} tests)
├─ ✅ S2: {name} ({n} tests)
├─ ✅ S3: {name} ({n} tests)
├─ ✅ S4: {name} ({n} tests)
└─ ✅ S5: {name} ({n} tests)

Tests: {passed}/{total} | Coverage: {pct}%
Commits: {n} (all pushed to remote)
{ENH_ID}: ✅ COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Error Template (BLOCKED)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 {PHASE_NAME}: BLOCKED at Stage {N}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[████░░░░░░] 40% Stage {N} Blocked

├─ ✅ S1: {name} ({n} tests)
├─ 🔴 S2: {name} (FAILED)
├─ ⚪ S3: {name} (pending)
└─ ⚪ S4: {name} (pending)

Tests: {passed}/{total} | Failures: {n}
Error: {error_message}
Fix: {fix_suggestion}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Status Icons (MANDATORY — all orchestrators)

| Icon | Meaning | When to Use |
|------|---------|-------------|
| ✅ | Complete | Stage finished, tests passing |
| 🔵 | In Progress | Currently executing |
| ⚪ | Pending | Not yet started |
| 🔴 | Failed/Blocked | Error, needs fix |

### Template Rules

1. **Hanging stages:** Each `├─` / `└─` stage on its OWN line (never concatenated)
2. **Progress bar:** `[██████████]` format with 10-block width
3. **Separators:** `━` (U+2501) line, exactly 44 characters
4. **Stage names:** Keep <30 chars to prevent overflow
5. **Metrics line:** Always include Tests + Coverage
6. **Last stage:** Uses `└─` (not `├─`)

### FORBIDDEN in Silent Mode

- ❌ "I'll now proceed to implement..."
- ❌ "Let me check the registry first..."
- ❌ "Here's what I plan to do..."
- ❌ "Should I continue?"
- ❌ Multi-paragraph explanations
- ❌ Approval requests between stages
- ❌ Markdown tables for stage results (use hanging `├─` tree)
- ❌ `<hr>` tags (use `━━━` separator lines)
- ❌ Inline code backticks around progress bar

---


## ✅ COMPLETION RESPONSE TEMPLATE (SSOT)

**Authority:** This section is the SINGLE SOURCE OF TRUTH for completion response formatting.  
**Scope:** All PHASE/STAGE completion responses in **educational/interactive** modes.  
**Note:** For **silent autonomous execution**, use the GOLDEN TEMPLATE above (§ SILENT AUTONOMOUS MODE).  
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

✅ **{PHASE NAME} Complete**

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

### Multi-Track Phase Completion Template

```markdown
<hr>
✅ {PHASE NAME} Complete
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


## 🖥️ Chat UI Rendering Rules

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

### 🔵 Status Icons

| Icon | Status | ✅ Use For | ❌ Never Use For |
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

### When to Show Options

| Show Options | Don't Show Options |
|--------------|-------------------|
| ✅ Decision between alternative approaches | ❌ Work is complete (use completion confirmation) |
| ✅ Analysis complete, awaiting approval | ❌ During holistic implementation (no exit options) |
| ✅ Critical branching point in workflow | ❌ Only one logical path forward (proceed automatically) |


### Completion Confirmation Format

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

*Ready for your next request.*
```

### Standard Decision Format (When Applicable)

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

### Visual Progress Format

For multi-step implementations, use visual ASCII progress bars.

### Format Rules

| Element | Specification | Example |
|---------|---------------|---------|
| **Width** | 10 blocks fixed | `[██████████]` |
| **Filled** | `█` character | Completed portions |
| **Empty** | `░` character | Remaining work |
| **Percentage** | Right-aligned, 3 chars | ` 0%`, ` 40%`, `100%` |
| **Status Icon** | Before description | ✅🔵⚪🔴 |
| **Description** | Clear task name + context | `S1: Core implementation complete` |


### Phase Progress Hierarchy (MANDATORY)

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

### When to Use Progress Bars

| ✅ Use For | ❌ Don't Use For |
|-----------|-----------------|
| Multi-step implementations (>3 steps) | Single-step operations |
| Long-running operations | Analysis/audit results (use tables) |
| Phase/sprint tracking | Conversational responses |
| TDD cycles (RED→GREEN→REFACTOR) | Quick confirmations |


### Badge Types

| Badge | When to Use |
|-------|-------------|
| ✨ **Recommended** | Default/best path for most users |
| ⚠️ **Risk** | Action has known drawbacks |
| ⏱️ **Fast** | Quickest option but may skip quality checks |
| 🔒 **Secure** | Highest security posture |
| 🧪 **Experimental** | New feature, use with caution |

### Maximum Options Rule

| Aspect | Guideline |
|--------|-----------|
| **Limit** | 5 numbered choices per decision point |
| **Rationale** | Beyond 5, users face decision paralysis |
| **Overflow Solution** | Use categorization or phased decisions |


---


## 📐 Semantic Layering Structure

### Layer 1: EXECUTIVE (Always Visible)

Every response follows this narrative flow:

| Step | Purpose | Rule |
|------|---------|------|
| 1️⃣ **CONTEXT** | What was requested | State the question/task |
| 2️⃣ **ANALYSIS** | What was discovered | No repetition of context |
| 3️⃣ **ACTION** | What was done | New information only |
| 4️⃣ **RESULT** | Final state | Next steps OR completion confirmation |

**❌ Anti-Pattern:** Repeating the same information in multiple sections  
**✅ Correct Pattern:** Each section adds new information building on previous


### Layer 2: TACTICAL (Collapsible)

Use `<details>` tags for non-critical information:

```markdown
<details>
<summary><b>📊 Detailed Analysis</b> (Click to expand)</summary>

[Detailed tables, metrics, evidence]

</details>
```

### Layer 3: TECHNICAL (Linked, Not Embedded)

```markdown
**🔍 Deep Dive Available:**
- Type `explain [section-name]` for technical details
- View full trace: #file:path/to/logs.md
```

---

## 🎭 Response Templates by Mode

### Intent-Based Template Selection

All non-autonomous user responses follow the **5-Section Golden Format** defined in:
**§ USER RESPONSE TEMPLATE — GOLDEN FORMAT (SSOT)** (above in this document)

| User Intent | Mode Header | Sections Used | Density |
|-------------|-------------|---------------|---------|
| **DIGEST** | `📚 CORTEX DIGEST` | All 5 sections | Medium |
| **DESIGN/PLAN** | `🎨 CORTEX DESIGN` / `📋 CORTEX PLAN` | All 5 sections + H3 alternatives | Full |
| **QUERY** | `🔍 CORTEX QUERY` | All 5 sections (simple density) | Simple-Medium |
| **AUDIT** | `🔍 CORTEX AUDIT` | All 5 sections + findings table | Full |
| **IMPLEMENT** (pre-approval) | `⚡ CORTEX IMPLEMENT` | All 5 sections (challenge gate) | Medium |
| **IMPLEMENT** (post-approval) | Silent autonomous | Golden autonomous template (§ SILENT AUTONOMOUS MODE) | Progress bars only |
| **COMPLETION** | Inline summary | Summary + deliverables + metrics | Simple |

### Mode-Specific H3 Extensions

**DIGEST mode** — add under Analysis:
- `### Concern Resolution` — table mapping concerns → solutions → status

**DESIGN/PLAN mode** — add under Recommendation:
- `### Phase Breakdown` — numbered phases with scope + duration
- `### Metrics Forecast` — expected tests, coverage, effort

**AUDIT mode** — add under Analysis:
- `### Priority Breakdown` — P0/P1/P2/P3 findings with file:line references

**QUERY mode** — keep simple:
- Skip H3 sub-sections unless question requires deep analysis

### CONCISE DECISION Mode

**Trigger:** Review, verification, assessment, synthesis, "does this address my concerns?"

Uses the same 5-section structure but with executive-memo density:
- **Summary:** 1 sentence
- **Analysis → Key Findings:** 3-6 bullets max, single-sentence preferred
- **Recommendation:** Primary + one alternative (brief comparison)
- **Benefits & Risks:** DoD confidence score
- **Next Steps:** Execute now vs plan for later

---

### PRE-FLIGHT Mode

Uses 5-section format (simple density):
- **Summary:** "Environment readiness check"
- **Analysis:** Status table (Ready ✅ / Setup Required ❌)
- **Recommendation:** Auto-fix or manual steps
- **Benefits & Risks:** Skip (simple request)
- **Next Steps:** 1-3 numbered fix options

### Post-Approval Autonomous Mode

**Reference:** § SILENT AUTONOMOUS MODE — GOLDEN TEMPLATE (progress bars + hanging stages)

---

## 🧠 INTENT-BASED TEMPLATE SELECTION (Unified)

**Authority:** All user-facing responses use the 5-Section Golden Format (§ USER RESPONSE TEMPLATE above).

Templates A-E are **retired** — replaced by the single 5-section structure with mode-specific H3 extensions.
The golden format adapts via **Adaptive Density** (simple/medium/complex) rather than separate templates per intent.

### Classification → Format Mapping

```python
def select_response_format(intent: str) -> str:
    """All intents use the 5-section golden format with adaptive density."""
    if intent in ["IMPLEMENT", "FIX", "REFACTOR"] and user_said_proceed:
        return "SILENT_AUTONOMOUS_MODE"  # § SILENT AUTONOMOUS MODE — GOLDEN TEMPLATE
    return "FIVE_SECTION_GOLDEN_FORMAT"  # § USER RESPONSE TEMPLATE — GOLDEN FORMAT
```

### CLASSIFY (Conversational Mode)

**Trigger:** `cortex_classify` MCP tool with `format='conversational'`
**Purpose:** Pre-implementation intent reflection (≤60 tokens, 4-second scan)

```markdown
**You want to {mirror user vocabulary}.**
This involves {scope}-level changes with {impact} impact.
**Confidence:** {High/Medium/Low} confidence ({pct}%)
```

**Rules:**
- ✅ First sentence mirrors user vocabulary (not technical jargon)
- ✅ Second sentence describes scope + impact
- ✅ Total output ≤60 tokens
- ✅ Validation data in background (not user-facing)

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
| **Creating .md/.txt report files** | **CORE-002 violation** | **All output inline in Copilot Chat** |
| **Tool usage narration** | **Wastes read time ("I searched...", "I read...")** | **Present findings directly** |
| **>60 second read time** | **Not executive-ready** | **Answer first, tables for data, ≤5 sections** |
| **Answering without mirroring question** | **User unsure if concern was understood** | **"Summary" mirrors user's words** |
| **Generic phase names (PHASE-1)** | **No strategic meaning, harder to track** | **Meaningful names (Foundation & Bootstrap)** |

---

## 📊 Adaptive Density Guidelines

### Simple Requests (1-2 files, <100 LOC)

Use 5-section format at **simple density** — each section 1-2 sentences max.

### Complex Requests (Multi-phase, >1000 LOC)

Use 5-section format at **full density** — with H3 sub-sections, comparison tables, and numbered implementation steps.

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

## 🔄 Continuation Prompts (Token-Efficient)

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

## 📏 Quality Checklist

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
