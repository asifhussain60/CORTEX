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

### 1. Enforce Explicit Line Breaks

**Current template (cortex-architect.prompt.md:56-60):**
```markdown
├─ ✅ S1: DebuggerOrchestrator (24 tests)
├─ ✅ S2: MarkerInjectionEngine (17 tests)
├─ ✅ S3: AutoCleanupManager (9 tests)
├─ ✅ S4: Integration (8 tests)
└─ ✅ S5: MCP Tools (10 tests)
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

### 3. Update response-format-standards.md

**Location:** `.github/prompts/.archive/phase-docs/response-format-standards.md`

**Add after line 44 (Stage Tree section):**

```markdown
### Stage Tree Rendering (CRITICAL)

**Each stage MUST appear on its own line** to prevent overflow in Copilot Chat.

**Template Structure:**
```markdown
├─ {status} S{n}: {name} ({tests} tests)
├─ {status} S{n}: {name} ({tests} tests)
└─ {status} S{n}: {name} ({tests} tests)
```

**Character Breakdown:**
- `├─` or `└─` : Tree connector (2 chars)
- ` ` : Space (1 char)
- `✅` or `🔵` or `⚪` : Status emoji
- ` S{n}: ` : Stage label with space
- `{name}` : Stage name (keep concise, <30 chars)
- ` ({tests} tests)` : Test count in parentheses

**Line Length Targets:**
- Ideal: 50-60 characters per stage line
- Maximum: 70 characters (to fit in Copilot Chat display)
- If stage name >30 chars, abbreviate or split

**Examples:**

✅ **CORRECT:**
```
├─ ✅ S1: Adapter Creation (20 tests)
├─ ✅ S2: Batch Generation (174 tests)
└─ ✅ S3: Integration (4 tests)
```

❌ **WRONG (too long):**
```
├─ ✅ S1: ScaffolderIntelligenceAdapter with full wiring integration (20 tests)
```

✅ **FIXED (abbreviated):**
```
├─ ✅ S1: Scaffolder Adapter (20 tests)
```

**Validation Regex:**
```python
import re

# Each line should match this pattern
pattern = r'^[├└]─ [✅🔵⚪🔴] S\d+: .{1,40} \(\d+ tests\)$'

lines = [
    "├─ ✅ S1: Adapter Creation (20 tests)",
    "├─ ✅ S2: Batch Generation (174 tests)",
    "└─ ✅ S3: Integration (4 tests)",
]

for line in lines:
    assert re.match(pattern, line), f"Invalid format: {line}"
```
```

### 4. Enforcement Checklist

Add to prompt files:

```markdown
**Before generating completion response, verify:**

- [ ] Each stage tree line on separate line (no concatenation)
- [ ] Stage names abbreviated if >30 chars
- [ ] Box separators exactly 40 `─` characters
- [ ] Progress bar in inline code blocks
- [ ] Total line length <100 chars (for Copilot Chat width)
- [ ] No `##` headers inside completion boxes
- [ ] Field labels use `**Label:**` format
```

## Implementation Plan

1. ✅ Document issue and solution (this file)
2. ⚪ Update cortex-architect.prompt.md with rendering rules
3. ⚪ Update response-format-standards.md with line length targets
4. ⚪ Add validation checklist to both prompt files
5. ⚪ Test with next completion response
6. ⚪ Commit changes with AC marker

## Testing

**Next completion response should render as:**

```
────────────────────────────────────────
📋 WAVE-3 Stage 1: Feature Implementation
────────────────────────────────────────

`██████████` 100% Complete

├─ ✅ S1: Core Logic (15 tests)
├─ ✅ S2: Integration (8 tests)
└─ ✅ S3: Validation (12 tests)

Tests: 35/35 | Coverage: 98%
────────────────────────────────────────
```

**Verify in Copilot Chat:**
- Each stage line appears on its own line
- No horizontal scrolling required
- Tree connectors aligned vertically
- Box separators fit display width

# AC_COMPLETE: AC-RESPONSE-FORMAT-FIX-001 ✅
