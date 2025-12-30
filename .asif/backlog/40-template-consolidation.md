# 🧹 Response Template Consolidation

**Priority:** MEDIUM | **Estimated Effort:** 20 min | **Category:** Optimization

---

## 🎯 Objective

Streamline response templates by removing redundancy and consolidating similar formats.

---

## 📋 Execution Steps

### Step 1: Audit Current Templates
```
Read files:
- cortex-brain/response-templates.yaml
- cortex-brain/response-templates-v4.yaml
- cortex-brain/response-profile-variants.yaml
- cortex-brain/response-base-components.yaml
```

### Step 2: Identify Redundancies
Create analysis of:
- Duplicate template definitions
- Similar templates with minor variations
- Rarely used or obsolete templates
- Templates not referenced anywhere

### Step 3: Consolidation Strategy

**Keep (Essential):**
- INSTANT response (< 3 lines)
- BRIEF response (3-10 lines)
- STANDARD response (typical operations)
- COMPREHENSIVE response (complex tasks)
- Progress bar template
- Error/Warning templates

**Remove/Merge:**
- Deprecated v3 templates
- Duplicate profile variants
- Overly specific single-use templates
- Templates with < 5% usage

### Step 4: Execute Consolidation
1. Backup current templates:
   ```bash
   cp cortex-brain/response-templates*.yaml cortex-brain/cache/response-templates-backup-$(date +%Y%m%d)/
   ```

2. Merge `response-templates.yaml` and `response-templates-v4.yaml` into single authoritative file

3. Update `response-profile-variants.yaml` to reference consolidated templates

4. Update all manifests referencing old template structure

### Step 5: Update References
Search and update references in:
```bash
grep -r "response-templates.yaml\|response-profile" .github/prompts/ cortex-brain/manifests/
```

### Step 6: Validation
Verify no broken template references:
```bash
python3 -c "import yaml; yaml.safe_load(open('cortex-brain/response-templates-v4.yaml'))"
```

---

## ✅ Success Criteria
- [ ] Single authoritative response template file
- [ ] Maximum 6 response format types
- [ ] All references updated
- [ ] Templates parse without errors
- [ ] No orphaned template files

---

## 🗑️ AUTO-DELETE INSTRUCTION
**After successful execution:** Delete this file with:
```bash
rm -f /Users/asifhussain/PROJECTS/CORTEX/.asif/backlog/02-excessive-templating.md
```
