# Template Visual Standards

**Version:** 1.0  
**Created:** 2025-12-07  
**Purpose:** Standardize visual elements across all CORTEX response templates

---

## Progress Bar Standards

### Dynamic Progress Bars (Preferred)

Use placeholders that render dynamically based on actual progress:

```yaml
**Progress:** [{progress_bar}] {percentage}%
Progress: [{bar}] {percentage}% - Phase {current} of {total} Complete
```

**Rationale:** Prevents false impression of completion, automatically updates

### Static Progress Bars (Examples Only)

When showing examples of completion states, use appropriate fill levels:

- **0% (Not Started):** `[░░░░░░░░░░] 0%`
- **50% (In Progress):** `[█████░░░░░] 50%`
- **100% (Complete):** `[██████████] 100%`

**Characters:**
- Empty: `░` (Light Shade U+2591)
- Filled: `█` (Full Block U+2588)

**Never use:** Filled squares for 0% states in active operations

---

## Checkbox Standards

### Pending Tasks

Use empty checkboxes for tasks not yet complete:

```markdown
- [ ] Task description
☐ Alternative format
```

**Renders as:** ☐ (Ballot Box U+2610)

### Completed Tasks

Use checked boxes only when task actually complete:

```markdown
- [x] Task description
☑ Alternative format
✅ Visual checkmark
```

**Renders as:** ☑ (Ballot Box with Check U+2611) or ✅ (Check Mark Button U+2705)

**Never use:** Checked boxes for pending tasks

---

## Phase Indicators

### Pending Phases

```markdown
☐ Phase 1: Name
☐ Phase 2: Name
```

### Active Phase

```markdown
🔄 Phase 1: Name (In Progress)
☐ Phase 2: Name
```

### Completed Phase

```markdown
✅ Phase 1: Name (Complete)
🔄 Phase 2: Name (In Progress)
☐ Phase 3: Name
```

---

## Status Indicators

### Standard Icons

- ☐ Pending / Not Started
- 🔄 In Progress / Active
- ✅ Complete / Success
- ❌ Failed / Error
- ⏸️ Paused / On Hold
- ⏳ Waiting / Queued

**Consistency rule:** Use same icon for same status across all templates

---

## Common Pitfalls

### ❌ WRONG: Filled bar for 0% progress
```markdown
**Progress:** [██████████] 0%
```

### ✅ CORRECT: Empty bar for 0% progress
```markdown
**Progress:** [░░░░░░░░░░] 0%
```

---

### ❌ WRONG: Checked box for pending task
```markdown
- [x] Install dependencies (Status: PENDING)
```

### ✅ CORRECT: Empty box for pending task
```markdown
- [ ] Install dependencies (Status: PENDING)
```

---

### ❌ WRONG: Hardcoded progress in template
```yaml
content: |
  Phase 1: [██████████] 100%
  Phase 2: [░░░░░░░░░░] 0%
```

### ✅ CORRECT: Dynamic placeholder
```yaml
content: |
  Phase {phase_number}: [{phase_progress}] {phase_percentage}%
```

---

## Implementation Checklist

When creating new templates:

- [ ] Use dynamic placeholders for progress (`{bar}`, `{progress_bar}`)
- [ ] Use `- [ ]` for pending checkboxes
- [ ] Use `- [x]` only for completed items
- [ ] Match icon usage to standard status indicators
- [ ] Avoid hardcoded visual elements that imply state
- [ ] Test rendering in Copilot Chat before deployment

---

## Template Audit Process

1. **Search for hardcoded progress bars:** `grep -E '\[█+\].*0%'`
2. **Search for incorrect checkboxes:** `grep -E '- \[x\].*PENDING'`
3. **Verify dynamic placeholders:** `grep -E '\{(bar|progress'`
4. **Manual review:** Test each template's visual elements
5. **Fix inconsistencies:** Replace hardcoded with dynamic
6. **Document changes:** Update CHANGELOG with visual fixes

---

## References

- Unicode characters: https://unicode-table.com/en/blocks/block-elements/
- Markdown checkbox syntax: https://github.github.com/gfm/#task-list-items
- CORTEX response format: `.github/prompts/modules/response-format-v3.md`

---

**Maintenance:** Review this document when adding new visual elements or status indicators
