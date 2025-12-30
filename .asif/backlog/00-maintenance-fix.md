# 🔧 CORTEX Maintenance Prompt Enhancement

**Priority:** CRITICAL | **Estimated Effort:** 30 min | **Category:** Core Infrastructure

---

## 🎯 Objective

Update `cortex-maintenance.prompt.md` to include data preservation rules and ensure maintenance phases are properly sequenced.

---

## 📋 Execution Steps

### Step 1: Load Required Context
```
Read files:
- .github/prompts/cortex-maintenance.prompt.md
- cortex-brain/admin/CORTEX_admin_governance.md (if exists, else admin/*.md)
- cortex-brain/protection/data-preservation-rules.yaml (if exists)
```

### Step 2: Extract Data Preservation Rules
From governance documents, extract:
- Critical user data paths that MUST NOT be deleted
- Preservation patterns for lessons-learned, knowledge-graph, tier1/tier2 data
- Rollback requirements

### Step 3: Update cortex-maintenance.prompt.md
Apply these changes:

1. **Add Data Preservation Section** (after header):
   ```markdown
   ## ⛔ DATA PRESERVATION RULES
   Before ANY cleanup/deletion operation, verify:
   - [ ] cortex-brain/lessons-learned.yaml preserved
   - [ ] cortex-brain/knowledge-graph.yaml preserved
   - [ ] cortex-brain/tier1/*.md preserved
   - [ ] cortex-brain/tier2/*.yaml preserved
   - [ ] User-added documents in cortex-brain/documents/ preserved
   ```

2. **Renumber Phases** sequentially (no fractions):
   - Phase 1: Health Diagnostics
   - Phase 2: Brain Tier Validation
   - Phase 3: Data Preservation Check
   - Phase 4: Cleanup Operations
   - Phase 5: Optimization
   - Phase 6: Verification Report

3. **Remove** any traces of 5-part response templates

4. **Add reference wiring**:
   ```markdown
   **References:**
   - Data Preservation: `cortex-brain/protection/data-preservation-rules.yaml`
   - Brain Protection: `cortex-brain/brain-protection-rules.yaml`
   ```

### Step 4: Verify CORTEX.prompt.md and copilot-instructions.md
Ensure these files:
- Reference the updated maintenance prompt correctly
- Do NOT contain old 5-part response template references
- Include data preservation rule references

### Step 5: Validation
Run command to verify no broken references:
```bash
grep -r "phase.*\." .github/prompts/ | grep -v ".md:" | head -20
```

---

## ✅ Success Criteria
- [ ] cortex-maintenance.prompt.md has sequential phases (1-6)
- [ ] Data preservation rules clearly documented
- [ ] No fractional phase numbers remain
- [ ] No 5-part template references in core prompts
- [ ] All cross-references validated

---

## 🗑️ AUTO-DELETE INSTRUCTION
**After successful execution:** Delete this file with:
```bash
rm -f /Users/asifhussain/PROJECTS/CORTEX/.asif/backlog/00-maintenance-fix.md
```
