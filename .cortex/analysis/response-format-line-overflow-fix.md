"""
Response Format Fix: Line Overflow in Stage Trees

AC_START: AC-RESPONSE-FORMAT-FIX-001
Date: 2026-02-13
Issue: Stage tree lines concatenating on single line in Copilot Chat
Authority: response-format-standards.md § Completion Response Template
"""

## Problem Identified

In Copilot Chat, stage tree lines are rendering as:

```
├─ ✅ S1: Scaffolder Intelligence Adapter (20 tests) |─── ✅ S2: Batch Generation (174 tests) └─── ✅ S3: Scaffolder Integration (4 tests)
```

**Expected:**
```
├─ ✅ S1: Scaffolder Intelligence Adapter (20 tests)
├─ ✅ S2: Batch Generation (174 tests)
└─ ✅ S3: Scaffolder Integration (4 tests)
```

## Root Cause

The stage tree uses proper line breaks in templates, but when AI generates output,
it may not preserve newlines correctly in Copilot Chat rendering context.

## Solution

### 1. Use HTML `<hr>` Tag for Box Separators

**Root Cause:** Box-drawing characters (`U+2500 ─`) render visually wider in Copilot Chat than ASCII, causing horizontal overflow.

**Solution:** Replace all box separators with HTML `<hr>` tag which renders as a thin line that doesn't overflow.

**Before (overflow issue):**
```markdown
────────────────────────────────────────
📋 WAVE-R Stage 1: Implementation
────────────────────────────────────────
```

**After (no overflow):**
```markdown
<hr>

📋 **WAVE-R Stage 1: Implementation**

<hr>
```

**Benefits:**
- ✅ Renders as thin horizontal line (doesn't overflow)
- ✅ Semantic HTML (proper separator element)
- ✅ Consistent width across all markdown renderers
- ✅ No character counting needed (40 chars vs `<hr>`)

### 2. Enforce Explicit Line Breaks for Stage Trees

**Current template (cortex-architect.prompt.md:56-60):**
```markdown
<hr>

📋 **Stage Name**

├─ ✅ S1: DebuggerOrchestrator (24 tests)
├─ ✅ S2: MarkerInjectionEngine (17 tests)
├─ ✅ S3: AutoCleanupManager (9 tests)
├─ ✅ S4: Integration (8 tests)
└─ ✅ S5: MCP Tools (10 tests)

<hr>
```

**Enhanced with blank line guidance:**
```markdown
├─ ✅ S1: DebuggerOrchestrator (24 tests)
├─ ✅ S2: MarkerInjectionEngine (17 tests)
├─ ✅ S3: AutoCleanupManager (9 tests)
├─ ✅ S4: Integration (8 tests)
└─ ✅ S5: MCP Tools (10 tests)

[EACH LINE ABOVE MUST BE ON ITS OWN LINE - NO CONCATENATION]
```

### 2. Add Rendering Instructions

Add to cortex-architect.prompt.md § Visual Feedback Pattern:

```markdown
**CRITICAL RENDERING RULES:**

1. **Stage Tree Lines:** Each stage MUST be on its own line
   - ✅ CORRECT:
     ```
     ├─ ✅ S1: Name (n tests)
     ├─ ✅ S2: Name (n tests)
     └─ ✅ S3: Name (n tests)
     ```
   
   - ❌ WRONG (concatenated):
     ```
     ├─ ✅ S1: Name (n tests) ├─ ✅ S2: Name (n tests) └─ ✅ S3: Name (n tests)
     ```

2. **Box Separator Length:** Exactly 40 `─` characters
   - ✅ CORRECT: `────────────────────────────────────────` (40 chars)
   - ❌ WRONG: `─────────────────────────────────────────────────────────` (too long)

3. **Progress Bar Format:** Use inline code block to prevent link parsing
   - ✅ CORRECT: `` `██████████` 100% ``
   - ❌ WRONG: `██████████ 100%` (may render as link)
```

### 3. Update response format standards

**Location:** `.github/prompts/SILENT-EXECUTION-RESPONSE-TEMPLATE.md`

**Key Points:**
- Progress bar format: `` `██████████` `` (inline code)
- Use markdown tables (NOT tree characters)
- Separators: `<hr>` HTML tag (NOT `─────`)
- Completion reporting: Include test counts + coverage %

**Add after line 44 (Stage Tree section):**

```markdown
### Box Separator Format (CRITICAL)

**Use HTML `<hr>` tag** instead of box-drawing characters to prevent UI overflow.

**Why `<hr>` instead of `────────────────────────────────────────`:**
- Box-drawing character (U+2500) renders wider than ASCII in Copilot Chat
- Creates horizontal scrolling and visual overflow
- HTML `<hr>` renders as thin line that fits display width
- Semantic HTML (proper separator element)

**Template:**
```markdown
<hr>

📋 **{Section Title}**

{Content}

<hr>
```

**Character Limits:**
- Stage names: <30 chars
- Line length: <70 chars total
- NO box-drawing characters (`────`)
- NO long dash sequences (`----------------------------------------`)
```

### 4. Enforcement Checklist

Add to prompt files:

```markdown
**Before generating completion response, verify:**

- [ ] All box separators use `<hr>` tag (NO `────` or `----`)
- [ ] Each stage tree line on separate line (no concatenation)
- [ ] Stage names abbreviated if >30 chars
- [ ] Progress bar in inline code blocks: `` `██████` ``
- [ ] Total line length <70 chars
- [ ] No `##` headers inside completion boxes
- [ ] Field labels use `**Label:**` format
```

## Implementation Plan

1. ✅ Document issue and solution (this file)
2. ✅ Update cortex-architect.prompt.md with `<hr>` separator format
3. ✅ Update response-format-standards.md with `<hr>` format
4. ✅ Update copilot-instructions.md with `<hr>` format
5. ⚪ Test with next completion response
6. ⚪ Commit changes with AC marker

## Testing

**Next completion response should render as:**

```markdown
<hr>

📋 **WAVE-3 Stage 1: Feature Implementation**

`██████████` 100% Complete

├─ ✅ S1: Core Logic (15 tests)
├─ ✅ S2: Integration (8 tests)
└─ ✅ S3: Validation (12 tests)

Tests: 35/35 | Coverage: 98%

<hr>
```

**Verify in Copilot Chat:**
- Horizontal lines render as thin separators (no overflow)
- Each stage line appears on its own line
- No horizontal scrolling required
- Tree connectors aligned vertically
- Separator fits display width

# AC_COMPLETE: AC-RESPONSE-FORMAT-FIX-001 ✅
