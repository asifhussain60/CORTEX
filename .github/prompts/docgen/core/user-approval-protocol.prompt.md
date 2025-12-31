# 🙋 User Approval Protocol

**Parent:** `cortex-docgen.prompt.md`  
**Purpose:** Handle approval workflow for NEW documentation not in index.html

---

## When Discovery Finds Undocumented Features

**If a feature is discovered but NOT in `docs/index.html`:**

1. **DO NOT** generate documentation automatically
2. **PRESENT** the approval template below to user
3. **WAIT** for explicit user selection
4. **ONLY THEN** generate documentation + update index.html

---

## User Approval Response Template

```markdown
## 📋 New Documentation Request

**Discovered Feature:** {feature_name}
**Source:** `{source_file_path}`
**Description:** {brief_description}

---

### 🎯 Action Required

This feature is NOT currently linked from `docs/index.html`. 
Documentation generation requires your approval.

**Select an option:**

| Option | Action | Command |
|--------|--------|---------|
| **A** | ✅ Approve & Add to Key Features | Reply: `approve A` |
| **B** | ✅ Approve as Level 2 under existing section | Reply: `approve B: {parent_section}` |
| **C** | ⏸️ Defer (do not generate now) | Reply: `defer` |
| **D** | ❌ Reject (not needed) | Reply: `reject` |

**Example responses:**
- `approve A` → Adds new tile to KEY FEATURES grid
- `approve B: orchestrators` → Adds as Level 2 under Orchestrators
- `defer` → Skips generation, logs for future
- `reject` → Removes from consideration

---

### 📍 If Approved (Option A or B)

1. Documentation will be generated following glassmorphism standards
2. `docs/index.html` will be updated with new entry point
3. Breadcrumb navigation will be configured
```

---

## Input Validation Rules

**Valid Responses:**
- `approve A` (case-insensitive)
- `approve B: {section}` where section ∈ authorized Level 1 sections
- `defer`
- `reject`

**Invalid Response Handling:**
- Re-prompt with clarification
- Max 3 retries before auto-defer

---

## Post-Approval Workflow

```
User approves → 
  1. Generate doc page (follow design-standards.prompt.md)
  2. Update docs/index.html (add tile or Level 2 link)
  3. Run design_validator.py to verify compliance
  4. Regenerate authorized-entry-points.json
```
