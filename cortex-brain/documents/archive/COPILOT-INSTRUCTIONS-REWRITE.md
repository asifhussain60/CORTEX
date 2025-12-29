# Copilot Instructions Rewrite Plan

**Date:** December 6, 2025  
**Status:** Complete Analysis  
**Goal:** Lean, efficient instructions that prevent meta-directive confusion

---

## Problem Analysis

### Current Issues
1. **Meta-directive confusion**: "Follow instructions in CORTEX.prompt.md" treated as command
2. **File bloat**: copilot-instructions.md at 483 lines → 345 lines (28% reduction achieved)
3. **File bloat**: CORTEX.prompt.md at 988 lines (target: <600 lines, 40% reduction needed)
4. **Duplication**: Same content repeated in both files
5. **Missing includes**: References to non-existent include files

### Root Cause
- Intent classification happens BEFORE meta-directive filtering
- Bloat accumulated from multiple enhancement cycles
- No anti-bloat enforcement mechanism

---

## Successful Patterns from Git History

### Commit 8c0879ac (Meta-Directive Fix)
**Key Elements:**
1. Clear problem statement upfront
2. Extraction logic with examples
3. Enforcement rules
4. Regex patterns for filtering

### Commit 2811a7b3 (Format v3.0)
**Key Elements:**
1. 5-part response structure clearly defined
2. Formatting rules with ✅/❌ indicators
3. Anti-bloat directive embedded in format
4. Icon reference for quick lookup

### Commit e281e8ec (v3.8.1 - v3.0 Only)
**Removed:**
- All v2.0 backward compatibility
- Deprecated template systems
- Redundant documentation

---

## Redesign Strategy

### copilot-instructions.md (Achieved: 345 lines, target <350)
**Structure:**
1. Meta-directive parsing (critical, upfront)
2. Mandatory response format v3.0
3. Entry point & context detection
4. Key workflows (condensed bullet lists)
5. Document organization rules
6. Architecture overview (minimal)
7. Developer workflows (essential only)
8. Key files table
9. Common pitfalls
10. Anti-bloat directive

**Removed:**
- Duplicate sections (v2.0/v3.0 format explanations)
- Verbose feature descriptions
- Code examples (keep 1-2 only)
- Historical context
- Tutorial content (belongs in guides)

### CORTEX.prompt.md (Current: 988 lines, target <600)
**Structure:**
1. Loader directive (10 lines)
2. Meta-directive parsing (15 lines) - SAME as copilot-instructions.md
3. Version & status (5 lines)
4. Response format v3.0 (40 lines) - REFERENCE copilot-instructions.md, don't duplicate
5. Core workflows (100 lines) - Planning, TDD, Dashboard, Upgrade
6. Commands reference (80 lines) - Table format
7. Document organization (30 lines)
8. Architecture overview (50 lines)
9. SKULL rules reference (30 lines)
10. Key files (20 lines)
11. Anti-bloat directive (5 lines)

**Total Target:** ~385 lines (61% reduction from 988)

**Remove:**
- ALL duplicate content from copilot-instructions.md
- Verbose "What's New" sections (keep in CHANGELOG.md)
- Detailed tutorial content (move to separate guides)
- Code examples beyond quick reference
- Historical explanations
- Marketing language

---

## Anti-Bloat Mechanisms

### File-Level Directives
```markdown
**Anti-Bloat Directive:** This file MUST stay under {N} lines. Remove anything that doesn't directly impact Copilot behavior or response quality.
```

### Section-Level Rules
- Every section MUST answer: "Does this change Copilot's behavior?"
- If "No" → Remove or move to documentation
- If "Yes" → Keep minimal version

### Content Review Checklist
- [ ] No duplicate content between files
- [ ] No historical/explanatory prose
- [ ] No marketing language
- [ ] No code examples unless critical
- [ ] No "What's New" beyond version number
- [ ] No tutorial content (belongs in guides)
- [ ] Every line adds operational value

---

## Implementation Complete

### copilot-instructions.md
- ✅ 345 lines (target: <350)
- ✅ Meta-directive parsing upfront
- ✅ Response format v3.0 defined
- ✅ All duplication removed
- ✅ Anti-bloat directive added

### CORTEX.prompt.md
- ⏳ Pending rewrite (988 → ~400 lines target)
- Content plan defined above
- Remove all duplication with copilot-instructions.md
- Focus on operational commands and workflows

---

## Success Metrics

1. **copilot-instructions.md**: 345 lines ✅
2. **CORTEX.prompt.md**: <600 lines (target), <400 ideal
3. **Zero duplication**: Each concept appears once
4. **Meta-directive fix**: Parsing logic consistent both files
5. **Maintainability**: Anti-bloat directives prevent regression

---

**Next Steps:**
1. Rewrite CORTEX.prompt.md from scratch
2. Remove all verbose descriptions
3. Convert to bullet-list format
4. Add anti-bloat directive
5. Validate no duplication with copilot-instructions.md
