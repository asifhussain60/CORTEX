# 🔧 CORTEX Maintenance Prompt Enhancement

**Priority:** CRITICAL | **Estimated Effort:** 30 min | **Category:** Core Infrastructure

---

## 🎯 Objective

Update `cortex-maintenance.prompt.md` to include data preservation rules and ensure maintenance phases are properly sequenced.

---

## 📋 Execution Steps

### Step 1: Load Required Context
Read the maintenance prompt file:
```bash
cat .github/prompts/cortex-maintenance.prompt.md
```

Check for governance documents (read first one found):
```bash
# Try specific file first
if [ -f "cortex-brain/admin/CORTEX_admin_governance.md" ]; then
    cat cortex-brain/admin/CORTEX_admin_governance.md
else
    # Otherwise read any admin governance file
    find cortex-brain/admin -name "*governance*.md" -o -name "*admin*.md" | head -1 | xargs cat
fi
```

Check for data preservation rules:
```bash
if [ -f "cortex-brain/protection/data-preservation-rules.yaml" ]; then
    cat cortex-brain/protection/data-preservation-rules.yaml
else
    echo "⚠️ No preservation rules file found - will use defaults"
fi
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

### Step 5: Check Toolkit for Existing Preservation Scripts
Before implementing, verify no existing preservation tools:
```bash
# Search toolkit inventory
grep -i "preserv\|protect.*data\|backup" cortex-toolkit/TOOLS-INVENTORY.md

# Search for preservation scripts
find cortex-toolkit -name "*preserv*" -o -name "*protect*" -o -name "*backup*" | grep "\.py$"
```

If existing tools found, integrate them into maintenance prompt instead of creating new rules.

### Step 6: Validation
Verify sequential phase numbering (no decimals):
```bash
grep -E "Phase [0-9]+" .github/prompts/cortex-maintenance.prompt.md | head -10
# Expected: Phase 1, Phase 2, Phase 3... (no Phase 1.5 or Phase 2.1)
```

Verify data preservation section exists:
```bash
grep -A 5 "DATA PRESERVATION" .github/prompts/cortex-maintenance.prompt.md
# Expected: Section header followed by preservation rules
```

Check for broken references:
```bash
grep -r "phase.*\." .github/prompts/ | grep -v ".md:" | head -20
# Expected: No output (no fractional phase numbers)
```

---

## ✅ Success Criteria
- [ ] cortex-maintenance.prompt.md has sequential phases (verify: `grep "^### Phase [1-6]:" .github/prompts/cortex-maintenance.prompt.md | wc -l` returns `6`)
- [ ] Data preservation section exists (verify: `grep -c "DATA PRESERVATION" .github/prompts/cortex-maintenance.prompt.md` returns `> 0`)
- [ ] No fractional phase numbers (verify: `grep -E "Phase [0-9]+\.[0-9]" .github/prompts/cortex-maintenance.prompt.md | wc -l` returns `0`)
- [ ] No 5-part template references (verify: `grep -i "5-part" .github/prompts/*.md | wc -l` returns `0`)
- [ ] File syntax valid (verify: No errors when reading file)

---

## 🗑️ AUTO-DELETE INSTRUCTION
**After successful execution:** Delete this file with:
```bash
rm -f /Users/asifhussain/PROJECTS/CORTEX/.asif/backlog/00-maintenance-fix.md
```
