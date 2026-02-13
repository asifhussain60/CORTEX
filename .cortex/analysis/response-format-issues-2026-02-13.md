# Response Format Issues Analysis
**Date:** 2026-02-13  
**Issue:** Pasted image shows formatting problems in completion responses  
**Severity:** P1-HIGH (User experience)  
**Scope:** Holistic fix across all response templates

---

## 🔍 Issue Analysis from Pasted Image

### What the Image Shows

```
✅ WAVE-11
Complete: Version Cleanup + Holistic Reprioritization

════════════════════════════════════════════════════

Commits: 24c174e19 → aa67a3d05 Pushed: origin/CORTEX
Duration: ~1.5 hours total

════════════════════════════════════════════════════

## Track 1: Version Cleanup ✅

Files Remediated:
• intent_classifier_v2.py → intent_classifier.py
• dashboard_schema_v3.py → DELETED (kept canonical)
• Updated 1 import in clarification_reducer.py
• Tests: 17/17 passing
```

### Problems Identified

| Issue | Current Behavior | Expected Behavior |
|-------|------------------|-------------------|
| **Box separators missing** | Lines appear as raw text | Should render as continuous boxes |
| **Status indicators incorrect** | Checkmark appears as raw "✅" text | Should be properly formatted emoji |
| **Section headers inconsistent** | Mix of "##" and bold text | Should follow standard format |
| **Spacing irregular** | Inconsistent blank lines | Should follow 3/2/1 line spacing rules |
| **Git commit formatting** | Inline with "Commits:" label | Should be on separate formatted line |
| **Duration placement** | Inline with commits | Should be separate field |
| **Track sections wrong level** | Using ## headers | Should use box format with track label |

---

## 📋 Root Cause Analysis

### Pattern Discovery

Searched all prompt files for completion templates:
- cortex-architect.prompt.md: 63 matches (box separators)
- CORTEX.prompt.md: 407 matches (box separators)
- response-format-standards.md: Format definitions

**Key Finding:** Templates exist but not consistently applied

### Format Inconsistencies

1. **Box Separator Character**: Using `━` (U+2501) but not consistently
2. **Section Nesting**: Mix of headers (`##`) and box formats
3. **Field Labels**: Inconsistent formatting (bold vs plain)
4. **Status Icons**: Mix of checkmarks and text labels
5. **Spacing**: Varying blank line counts between sections

---

## 🎯 Correct Format Standard (SSOT)

### Completion Response Template

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ {WAVE/PHASE NAME} Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Commits:** {hash1} → {hash2}
**Pushed:** origin/CORTEX
**Duration:** ~{time} total

**Metrics:**

| Metric | Before | After | Result |
|--------|--------|-------|--------|
| {metric1} | {val} | {val} | {status} ✅ |
| {metric2} | {val} | {val} | {status} ✅ |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Track 1: {Track Name} ✅

**Files Modified:**
- {file1} → {action}
- {file2} → {action}

**Results:**
- Tests: {n}/{n} passing ✅
- Coverage: {pct}%
- Impact: {description}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Key Rules

1. **Box Separators:**
   - Use exactly 60 `━` characters (U+2501)
   - Always start and end major sections
   - No box separators inside track sections

2. **Headers:**
   - Top-level: Inside box with checkmark emoji
   - Track headers: `### Track N: {Name} {emoji}`
   - No `##` headers after opening box

3. **Field Labels:**
   - Use bold markdown: `**Label:**`
   - Place labels on separate lines from values
   - Consistent spacing: single space after `**Label:**`

4. **Lists:**
   - Use `-` for unordered lists
   - Use table format for metrics
   - Use bullet points for features/deliverables

5. **Status Indicators:**
   - ✅ = Complete
   - 🔵 = In Progress  
   - ⚪ = Pending
   - 🔴 = Blocked
   - 🟡 = Warning

6. **Spacing:**
   - Blank line before/after box separators
   - Blank line before ### headers
   - Blank line after **Field:** labels
   - No blank lines inside lists

---

## 🛠️ Fix Strategy

### Phase 1: Update Response Format Standards (SSOT)

**File:** `.github/prompts/response-format-standards.md`

**Actions:**
1. Create comprehensive "Completion Response Template" section
2. Define box separator rules (character, count, placement)
3. Specify header hierarchy (box > track > field)
4. Document field label formatting
5. Add examples for common scenarios:
   - Single-track completion
   - Multi-track completion
   - Wave completion with metrics
   - Phase completion with deliverables

### Phase 2: Update cortex-architect.prompt.md

**Sections to Update:**
1. Silent Autonomous Execution § Visual Feedback Pattern (lines 36-85)
2. Response Header § Completion Section Format (lines 1350-1450)

**Changes:**
- Replace inline examples with reference to response-format-standards.md
- Add "SSOT: See response-format-standards.md" note
- Keep only 1-2 minimal examples in prompt
- Remove contradictory examples

### Phase 3: Update CORTEX.prompt.md

**Sections to Update:**
1. Response Header (Mandatory) (lines 358-430)
2. Silent Autonomous Execution examples

**Changes:**
- Mirror cortex-architect.prompt.md structure
- Reference response-format-standards.md as SSOT
- Ensure header-once-per-response rule enforced

### Phase 4: Create Formatting Validator

**File:** `.cortex/scripts/validate_response_format.py`

**Purpose:** Lint AI responses for format compliance

**Checks:**
- Box separator character and length
- Header hierarchy (no ## after opening box)
- Field label formatting (**Label:**)
- Status emoji usage
- Spacing rules compliance

**Usage:**
```bash
# Validate response from clipboard
python .cortex/scripts/validate_response_format.py --clipboard

# Validate response from file
python .cortex/scripts/validate_response_format.py response.md
```

---

## 📊 Impact Analysis

### Files Affected

| File | Section | Lines | Changes |
|------|---------|-------|---------|
| response-format-standards.md | § Completion Templates | 100-300 | **NEW:** Comprehensive completion section |
| cortex-architect.prompt.md | § Visual Feedback | 36-85 | **UPDATE:** Reference SSOT, remove duplicates |
| cortex-architect.prompt.md | § Response Header | 1350-1450 | **UPDATE:** Standardize box format |
| CORTEX.prompt.md | § Response Header | 358-430 | **UPDATE:** Mirror architect format |
| validate_response_format.py | - | - | **NEW:** Formatting linter |

### Governance

**CORE Rules:**
- **CORE-002:** Inline chat response format (no file generation)
- **CORE-029:** Response header mandatory
- **CORE-047:** Instruction files must not auto-load via backticks

**Audit Trail:**
- AC-START: AC-RESPONSE-FORMAT-FIX-001
- Scope: Holistic fix across all prompt files
- Impact: Improved user experience, consistent formatting

---

## 🚀 Implementation Plan

### Track 1: Update Response Format Standards (30 min)

**Stage 1: Add Completion Template Section**
- Create § Completion Response Template
- Define box separator rules
- Document header hierarchy
- Add field label standards
- Include 5 example templates

**Stage 2: Add Validation Rules**
- Create § Format Validation checklist
- Document common violations
- Add fix recommendations

### Track 2: Update Prompt Files (45 min)

**Stage 1: cortex-architect.prompt.md**
- Update § Visual Feedback Pattern
- Update § Response Header § Completion Format
- Add SSOT references
- Remove contradictory examples

**Stage 2: CORTEX.prompt.md**
- Update § Response Header
- Mirror architect format
- Add SSOT references

### Track 3: Create Validation Tool (Optional - 1h)

**Stage 1: Validator Script**
- Create validate_response_format.py
- Implement box separator check
- Implement header hierarchy check
- Implement field label check

**Stage 2: Integration**
- Add to pre-commit hooks (optional)
- Document usage in README
- Add to CI pipeline (future)

---

## ✅ Success Criteria

### Acceptance Criteria

- [ ] response-format-standards.md has comprehensive completion template section
- [ ] All examples follow SSOT format (box separators, headers, fields)
- [ ] cortex-architect.prompt.md references SSOT (no conflicting examples)
- [ ] CORTEX.prompt.md mirrors architect format
- [ ] Box separators render correctly (60 `━` characters)
- [ ] Headers follow hierarchy (box > track > field)
- [ ] Field labels consistent (`**Label:**` format)
- [ ] Status emojis standardized (✅🔵⚪🔴🟡)
- [ ] Spacing rules documented and examples compliant

### Validation

**Manual Tests:**
1. Run `/audit` command → Check completion format
2. Run `/implement {phase}` → Check autonomous progress bars
3. Run `/plan` operation → Check phase completion format

**Expected Output:**
- All responses follow standardized format
- Box separators render as continuous lines
- Headers properly nested
- Field labels bold and consistent
- Status emojis display correctly

---

## 📝 Notes

**Cross-Platform Considerations:**
- Box separator character (━ U+2501) renders in all terminals
- Emoji support may vary (use fallback text when needed)
- Markdown rendering consistent in GitHub Copilot Chat

**Performance:**
- No impact on response time
- Format changes purely visual
- Linting optional (no blocking)

**Maintainability:**
- SSOT in response-format-standards.md reduces duplication
- Prompt files reference SSOT → easier updates
- Validator script catches regressions

---

## 🔗 References

- **Authority:** response-format-standards.md (SSOT)
- **Implementation:** cortex-architect.prompt.md + CORTEX.prompt.md
- **Validation:** validate_response_format.py (future)
- **Governance:** CORE-002, CORE-029, CORE-047
