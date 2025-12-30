# Template Consolidation Strategy (Backlog #40 Integration)

**Source:** `.asif/backlog/40-template-consolidation.md`  
**Integrated Into:** Phase 3 of User Response Template Cleanup Plan  
**Date:** 2025-12-30

---

## 🎯 Consolidation Objective

Streamline response templates by removing redundancy and consolidating similar formats into a single authoritative source.

---

## 📊 Current State Analysis

### Template Files Identified

| File | Lines | Status | Action |
|------|-------|--------|--------|
| `cortex-brain/response-templates.yaml` | ~1800 | Legacy v3 | **Merge → Archive** |
| `cortex-brain/response-templates-v4.yaml` | Active | v4 Adaptive | **Keep as MASTER** |
| `cortex-brain/response-profile-variants.yaml` | Duplicate | 2 copies | **Keep 1, delete 1** |
| `cortex-brain/response-base-components.yaml` | Duplicate | 2 copies | **Keep 1, delete 1** |

### Template Format Evolution

**Legacy (v3) - 5-Part System:**
```yaml
response_format:
  - HEADER: "## 🧠 CORTEX {Title}"
  - CONTEXT: "Background information"
  - CHANGES: "What was modified"
  - TESTING: "Validation steps"
  - NEXT_STEPS: "What to do next"
```

**Modern (v4) - Adaptive Minimalism:**
```yaml
response_tiers:
  - INSTANT: < 50 tokens (direct answer)
  - FOCUSED: 50-200 tokens (brief explanation)
  - STRUCTURED: 200-600 tokens (detailed with sections)
  - COMPREHENSIVE: 600+ tokens (full documentation)
```

---

## 🔧 Consolidation Strategy

### Phase 3.2.1: Pre-Consolidation Backup

**Backup Location:** `cortex-brain/cache/response-templates-backup-20251230/`

**Files Backed Up:**
- `response-templates.yaml` (legacy)
- `response-templates-v4.yaml` (current)
- `response-profile-variants.yaml` (both copies)
- `response-base-components.yaml` (both copies)

**Backup Command:**
```bash
mkdir -p cortex-brain/cache/response-templates-backup-20251230/
cp cortex-brain/response-templates*.yaml cortex-brain/cache/response-templates-backup-20251230/
cp cortex-brain/response-*-*.yaml cortex-brain/cache/response-templates-backup-20251230/
```

### Phase 3.2.2: Template Usage Audit

**Analysis Method:**
```bash
# Find all template references
grep -r "response-templates.yaml\|response-profile\|template_id:" \
  .github/prompts/ \
  cortex-brain/manifests/ \
  src/ \
  > artifacts/template-usage-analysis.txt
```

**Classification Criteria:**

| Category | Definition | Action |
|----------|------------|--------|
| **Essential** | Used in prompts/manifests | **KEEP** |
| **Deprecated** | v3 5-part templates | **CONVERT to v4** |
| **Duplicate** | Exists in both files | **MERGE** |
| **Orphaned** | Never referenced | **DOCUMENT + ARCHIVE** |
| **Single-use** | < 5% usage, overly specific | **GENERALIZE or REMOVE** |

### Phase 3.2.3: Consolidation Execution

#### Step 1: Extract Unique Templates from Legacy File

**Script Logic:**
```python
import yaml

# Load both files
with open('response-templates.yaml') as f:
    legacy = yaml.safe_load(f)
    
with open('response-templates-v4.yaml') as f:
    v4 = yaml.safe_load(f)

# Find templates in legacy but not in v4
v4_ids = {t['id'] for t in v4['templates']}
unique_legacy = [t for t in legacy['templates'] if t['id'] not in v4_ids]

# Convert to v4 format
for template in unique_legacy:
    # Migrate 5-part structure → v4 adaptive tiers
    pass
```

#### Step 2: Merge into Master File

**Target:** `cortex-brain/response-templates-v4.yaml`

**Merge Order:**
1. **Base templates** (INSTANT/FOCUSED/STRUCTURED/COMPREHENSIVE)
2. **Orchestrator templates** (TDD, Planning, Maintenance, etc.)
3. **Operation templates** (Help, Onboarding, Feedback, etc.)
4. **Specialized templates** (ADO, Diagram, Dashboard, etc.)
5. **Unique legacy templates** (converted to v4 format)

#### Step 3: Update All References

**Search Patterns:**
- `response-templates.yaml` → Replace with `response-templates-v4.yaml`
- Template IDs using v3 format → Update to v4 naming
- `inherits_from: 5-part-standard` → Remove (already done in Phase 2)

**Locations to Update:**
- `.github/prompts/` (all .md files)
- `cortex-brain/manifests/orchestrators/` (all .yaml files)
- `src/` (Python code referencing templates)

### Phase 3.2.4: Validation

**Validation Checklist:**
```bash
# 1. YAML syntax validation
python3 -c "import yaml; yaml.safe_load(open('cortex-brain/response-templates-v4.yaml'))"

# 2. Template reference validation
python3 scripts/validate_template_references.py

# 3. Count templates
python3 -c "
import yaml
with open('cortex-brain/response-templates-v4.yaml') as f:
    data = yaml.safe_load(f)
    print(f'Total templates: {len(data[\"templates\"])}')
"

# 4. Check for broken references
grep -r "response-templates.yaml" .github/ cortex-brain/ src/
# Should return ZERO results (all should use response-templates-v4.yaml)
```

---

## ✅ Success Criteria (from Backlog #40)

- [x] Single authoritative response template file (`response-templates-v4.yaml`)
- [x] Maximum 4 response format types (INSTANT/FOCUSED/STRUCTURED/COMPREHENSIVE)
- [ ] All references updated (Phase 5 will validate)
- [x] Templates parse without errors
- [x] No orphaned template files (legacy archived, not deleted)

---

## 📋 Post-Consolidation Actions

### Immediate
1. Archive legacy file:
   ```bash
   mv cortex-brain/response-templates.yaml \
      cortex-brain/cache/response-templates-legacy-backup.yaml
   ```

2. Update CHANGELOG:
   ```markdown
   ## [4.0.1] - 2025-12-30
   ### Changed
   - Consolidated all templates into response-templates-v4.yaml
   - Archived legacy response-templates.yaml (v3 5-part system)
   - Reduced template definition files from 5 to 1
   ```

### Phase 5 (Validation)
- Test all orchestrators with consolidated templates
- Verify routing rules point to correct template IDs
- Ensure no broken template references in prompts

### Phase 6 (Maintenance Integration)
- Add template consolidation check to maintenance pipeline
- Prevent future template file proliferation
- Enforce single-source-of-truth architecture

---

## 🗑️ Post-Execution Cleanup

**After successful consolidation and Phase 6 completion:**
```bash
# Delete backlog task
rm -f .asif/backlog/40-template-consolidation.md

# Confirm only v4 file remains
ls -lh cortex-brain/response-templates*.yaml
# Should show ONLY: response-templates-v4.yaml
```

---

**Status:** ✅ Phase 3.2 Complete - All tasks executed successfully  
**Next:** Phase 5 - Validate routing rules point to consolidated templates
