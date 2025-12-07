# Response Template Format Standardization Guide

**Version:** 1.0  
**Created:** 2025-12-07  
**Purpose:** Standardize header hierarchy across all 68 CORTEX response templates  
**Related:** Phase 6 of template-enhancement-plan-20251207

---

## Standard Format Hierarchy

**Planning Template Style** (proven excellent readability):

```markdown
# Main Title (H1)
**Metadata line**

---

## Section Header (H2)
Content paragraph...

### Subsection (H3)
Content paragraph...

#### Detail Level (H4) - Use sparingly
Content paragraph...
```

---

## Header Level Standards

### H1 (`#`) - Template Title ONLY
- Used once per template
- Format: `# 🧠 CORTEX {Title}`
- No emoji for non-presentation templates
- Examples:
  - `# 🧠 CORTEX Planning System 2.0`
  - `# 🧠 CORTEX Business Value & Capabilities`
  - `## 🧠 CORTEX {operation}` (operational templates start with H2)

### H2 (`##`) - Major Section Headers
- Operational format sections: Understanding, Approach, Response, Impact, Next Steps
- Narrative format sections: What is CORTEX?, Why Built?, Tech Stack, How It Helps
- Examples:
  - `## 🎯 My Understanding Of Your Request`
  - `## What is CORTEX?`
  - `## Planning & Requirements`

### H3 (`###`) - Subsections Within Sections
- Breakdown of major sections
- Feature categories
- Step-by-step breakdowns
- Examples:
  - `### Planning System 2.0`
  - `### Requirements Clarity`
  - `### RED Phase`

### H4 (`####`) - Detailed Breakdowns (Rare)
- Only when absolutely necessary for deep hierarchies
- Prefer using bold text or bullet lists instead
- Example: `#### Input Validation Standards`

---

## Current Template Audit

**Total Templates:** 68 (62 existing + 6 new)

**Already Standardized (Phase 1):**
- ✅ `introduction_professional`
- ✅ `introduction_leadership`
- ✅ `introduction_product`
- ✅ `introduction_engineering`
- ✅ `business_value`
- ✅ `security_posture`

**Need Standardization (62):**
- `autonomous_execution_progress`
- `onboarding`
- `diagram_regeneration`
- `tech_implementation_example`
- `cache_management`
- `help_table`
- `help_detailed`
- `quick_start`
- `hands_on_tutorial`
- `status_check`
- `success_general`
- `error_general`
- `rulebook_welcome_banner`
- `governance_onboarding_complete`
- `introduction_discovery`
- `not_implemented`
- `executor_success`
- `executor_error`
- `tester_success`
- `operation_started`
- `operation_progress`
- `operation_complete`
- `question_documentation_issues`
- `work_planner_success`
- `planning_dor_incomplete`
- `planning_dor_complete`
- `planning_security_review`
- `multi_request_planning`
- `ado_created`
- `ado_resumed`
- `ado_search_results`
- `ado_story_planning`
- `ado_feature_planning`
- `ado_summary_generation`
- `onboarding_introduction`
- `policy_validation`
- `greeting`
- `code_review_planning`
- `ux_enhancement_explanation`
- `cleanup_orchestrator`
- (... and 22+ more)

---

## Standardization Process

### Step 1: Template Classification

**Category A: Operational (5-Part Format)**
- Start with H2 for title
- H3 for major sections (Understanding, Approach, Response, Impact, Next Steps)
- H4 for subsections (rare)

**Category B: Narrative (Direct Address)**
- Start with H1 for title
- H2 for major sections
- H3 for subsections

**Category C: Informational (Help, Status)**
- Start with H1 or H2 depending on context
- H2/H3 for content organization
- Table of contents structure for long templates

### Step 2: Header Audit Per Template

For each template:
1. Read current content structure
2. Identify header levels used (H1-H6)
3. Map to standard hierarchy
4. Check emoji consistency
5. Verify content-to-header ratio

### Step 3: Standardization Edits

**Common fixes:**
- H1 → H2 (operational templates shouldn't start with H1)
- H4 → H3 (reduce hierarchy depth)
- Inconsistent emoji usage → Standardize
- Too many headers → Consolidate with bold text or bullets
- Too few headers → Add H3 subsections for long sections

### Step 4: Token Efficiency Validation

After standardization:
- Measure token count per template
- Target: <500 tokens per template
- If over: Reduce header count, consolidate sections
- Preserve content quality while optimizing structure

### Step 5: YAML Syntax Validation

```bash
python -c "import yaml; yaml.safe_load(open('cortex-brain/response-templates.yaml', 'r', encoding='utf-8').read()); print('✅ Valid YAML')"
```

---

## Examples of Good vs Bad Hierarchy

### ❌ BAD: Too many header levels
```markdown
## Main Thing
### Sub Thing
#### Sub Sub Thing
##### Sub Sub Sub Thing (TOO DEEP!)
```

### ✅ GOOD: Appropriate depth
```markdown
## Main Thing
### Sub Thing
**Bold for emphasis** instead of header
- Bullet list for details
```

---

### ❌ BAD: Inconsistent header levels
```markdown
# Title
### Section 1 (skipped H2!)
## Section 2 (wrong order!)
```

### ✅ GOOD: Consistent hierarchy
```markdown
# Title
## Section 1
### Subsection 1A
## Section 2
### Subsection 2A
```

---

### ❌ BAD: Header noise (too many headers, not enough content)
```markdown
## Understanding
(2 lines of content)
## Approach
(1 line of content)
## Response
(2 lines of content)
```

### ✅ GOOD: Content-to-header ratio
```markdown
## Understanding
(5-8 lines of meaningful content)

## Approach
(4-6 lines explaining strategy)

## Response
(10+ lines of actual response)
```

---

## Automation Opportunities

**Script idea:** `scripts/standardize_template_headers.py`

```python
def standardize_template(template_name, content):
    """
    Auto-fix common header issues:
    1. Downgrade H1 → H2 if operational template
    2. Ensure consistent emoji usage
    3. Validate hierarchy (no skipped levels)
    4. Report token count
    """
    pass
```

**Benefits:**
- Batch process all 62 templates
- Consistent application of rules
- Token count reporting
- YAML syntax preservation

---

## Phase 6 Execution Checklist

- [ ] Audit all 68 templates for current header usage
- [ ] Classify templates (Operational, Narrative, Informational)
- [ ] Create standardization script (optional, can be manual)
- [ ] Apply standard hierarchy to first 10 templates
- [ ] Validate YAML syntax after each batch
- [ ] Apply to next 20 templates
- [ ] Apply to next 20 templates
- [ ] Apply to final 18 templates
- [ ] Measure token efficiency (all templates < 500 tokens?)
- [ ] Update VERSION to 3.8.3
- [ ] Update CHANGELOG with standardization details
- [ ] Git commit
- [ ] Manual validation in Copilot Chat

---

## Success Metrics

**Quantitative:**
- 100% templates follow standard hierarchy
- 0 YAML syntax errors
- All templates < 500 tokens
- Header count reduced by 15-20%

**Qualitative:**
- Consistent visual hierarchy
- Improved readability (planning template style)
- Content-to-header ratio optimized
- Professional presentation across all templates

---

## Timeline Estimate

**62 templates @ 3 min each = 186 min (~3 hours)**

**With automation:**
- Script development: 30 min
- Batch processing: 60 min
- Manual review: 30 min
- Testing: 30 min
- **Total:** ~2.5 hours

---

## Next Actions

1. **Option A:** Execute Phase 6 now (3 hours autonomous)
2. **Option B:** Execute Phase 6 in separate session
3. **Option C:** Create standardization script first, then execute

**Recommendation:** Option B - Phases 0-5 delivered core feature (introduction/business/security templates). Phase 6 is optimization that can be executed independently without blocking usage of new templates.
