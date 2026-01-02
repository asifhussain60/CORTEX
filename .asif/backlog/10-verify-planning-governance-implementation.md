# ✅ Verify Planning Governance Implementation

**Priority:** HIGH | **Estimated Effort:** 30 min | **Category:** Validation

---

## 🎯 Objective

Verify that planning governance improvements implemented on January 1, 2026 are functioning correctly across all CORTEX planning workflows. Confirm that:
1. Phase -1 (Knowledge Library Consultation) is enforced
2. Comprehensive REFACTOR phase (≥15 tasks) is enforced
3. Orchestrator engagement validation prevents manual plan bypass
4. Validation script correctly detects non-compliant plans

**Source Documents:**
- Gap Analysis: `.asif/backlog/planning-governance-gap-analysis-2026-01-01.md`
- Implementation: `.asif/backlog/planning-governance-implementation-summary-2026-01-01.md`

---

## 📋 Execution Steps

### Step 1: Verify Response Template Updates
```bash
# Check autonomous_execution_progress template includes governance requirements
grep -A 20 "autonomous_execution_progress:" cortex-brain/response-templates-v4.yaml | grep -E "(phase_minus_one|refactor_comprehensiveness|knowledge_library)"
```

**Expected Output:**
- `phase_minus_one: required: true`
- `refactor_comprehensiveness: minimum_tasks: 15`
- `knowledge_library_consultation: true`

**Verification:**
```bash
# Should find governance_requirements section
grep -n "governance_requirements:" cortex-brain/response-templates-v4.yaml
```

### Step 2: Verify CORTEX.prompt.md Orchestrator Enforcement
```bash
# Check for orchestrator engagement validation checklist
grep -A 10 "ORCHESTRATOR ENGAGEMENT ENFORCEMENT" .github/prompts/CORTEX.prompt.md
```

**Expected Output:**
- 5-step validation checklist
- Manual plan rejection protocol
- `## 🛡️🧠 CORTEX Plan Execution` header requirement

**Verification:**
```bash
# Should find explicit enforcement text
grep -c "REJECT.*Re-route to orchestrator" .github/prompts/CORTEX.prompt.md
```
**Expected:** At least 1 occurrence

### Step 3: Verify Recursive Master Plan Updates
```bash
# Check master plan includes Phase -1 and comprehensive REFACTOR
cd cortex-brain/documents/planning/repeatable/level-2-glassmorphism-standardization/

# Verify Phase -1 exists
grep -n "Phase -1.*Knowledge Library" 00-RECURSIVE-MASTER-PLAN.md

# Count REFACTOR phase tasks
grep -E "^\| 10\.[0-9]+ \|" 00-RECURSIVE-MASTER-PLAN.md | wc -l
```

**Expected Output:**
- Phase -1 section found at line ~50-100
- REFACTOR task count ≥18

**Verification:**
```bash
# Check for 5 REFACTOR categories
grep -E "10\.(4|5|6|7|8)" 00-RECURSIVE-MASTER-PLAN.md | head -5
```
**Expected:** Headers for Orphaned Code, Duplication, Dead Code, Formatting, Documentation

### Step 4: Verify copilot-instructions.md SKULL Rules
```bash
# Check MANDATORY Plan Content section
grep -A 15 "MANDATORY Plan Content" .github/copilot-instructions.md | grep -E "(Phase -1|REFACTOR|micro-batch)"
```

**Expected Output:**
- Phase -1 as requirement #1
- Comprehensive REFACTOR (≥15 tasks) mentioned
- Micro-batch strategy mentioned

**Verification:**
```bash
# Count SKULL rules (should be 8, was 5 before)
grep -c "^| \`" .github/copilot-instructions.md | tail -1
```

### Step 5: Verify Validation Script Exists and Works
```bash
# Check script exists
test -f cortex-toolkit/validate_plan_governance.py && echo "✅ Script found" || echo "❌ Script missing"

# Test script on compliant plan
python cortex-toolkit/validate_plan_governance.py \
  cortex-brain/documents/planning/repeatable/level-2-glassmorphism-standardization/00-RECURSIVE-MASTER-PLAN.md
```

**Expected Output:**
```
Status: ✅ PASSED
Compliance Score: ✅ 10.0/10.0 (Threshold: ≥8.0)
```

**Verification:**
```bash
# Check script has all 8 validation checks
grep -c "def validate_" cortex-toolkit/validate_plan_governance.py
```
**Expected:** 6-8 validation methods

### Step 6: Test Validation Script on Non-Compliant Plan
```bash
# Create test plan WITHOUT Phase -1 (should fail)
cat > /tmp/test-plan-invalid.md << 'EOF'
# Test Plan

## Phase 0: Discovery
| 0.1 | Task | Status |

## Phase 10: REFACTOR
| 10.1 | Clean animations | ⬜ |
| 10.2 | Fix typos | ⬜ |
EOF

# Run validator (should FAIL)
python cortex-toolkit/validate_plan_governance.py /tmp/test-plan-invalid.md
```

**Expected Output:**
```
❌ CRITICAL: Phase -1 (Knowledge Library Consultation) missing
❌ CRITICAL: REFACTOR phase incomplete (2 tasks, need ≥15)
❌ Validation failed: 2 errors
```

**Verification:** Exit code should be 1 (failure)

### Step 7: Verify Knowledge Library Integration in Manifest
```bash
# Check planning manifest has Phase -1 configuration
grep -A 30 "phase_minus_one_knowledge_library" \
  cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml
```

**Expected Output:**
- `enabled: true`
- `mandatory: true`
- 4-5 query definitions
- `output:` fields for context files

**Verification:**
```bash
# Check refactor_phase_comprehensive section
grep -A 20 "refactor_phase_comprehensive" \
  cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml | grep "minimum_tasks"
```
**Expected:** `minimum_tasks: 15`

### Step 8: Verify Documentation Cross-References
```bash
# Check implementation summary references gap analysis
grep -i "planning-governance-gap-analysis" \
  .asif/backlog/planning-governance-implementation-summary-2026-01-01.md

# Verify compliance score improvement documented
grep -E "Compliance Score.*10\.0/10" \
  .asif/backlog/planning-governance-implementation-summary-2026-01-01.md
```

**Expected Output:**
- Reference to gap analysis file found
- Compliance score 10.0/10 documented
- "Before/After" comparison present

---

## ✅ Success Criteria

- [ ] Response template includes `governance_requirements` section
- [ ] CORTEX.prompt.md has orchestrator enforcement checklist (5 steps)
- [ ] Recursive Master Plan has Phase -1 (5 tasks) + comprehensive REFACTOR (≥18 tasks)
- [ ] copilot-instructions.md documents Phase -1 as requirement #1
- [ ] copilot-instructions.md lists 8 SKULL rules (not 5)
- [ ] Validation script exists and runs successfully
- [ ] Validation script correctly detects compliant plans (10.0/10)
- [ ] Validation script correctly rejects non-compliant plans
- [ ] Planning manifest has `phase_minus_one_knowledge_library` section
- [ ] Planning manifest has `refactor_phase_comprehensive` with `minimum_tasks: 15`
- [ ] Implementation summary documents compliance improvement (6.8 → 10.0)

**Overall Success:** All 11 criteria must pass ✅

---

## 🔍 Additional Validation (Optional)

### Verify Template Rendering
```bash
# Check if planning orchestrator uses new template
grep -n "autonomous_execution_progress" \
  src/orchestrators/planning/planning_orchestrator.py
```

### Verify Test Coverage
```bash
# Check for Phase -1 tests in planning orchestrator tests
grep -i "phase.*minus.*one\|knowledge.*library" \
  tests/orchestrators/planning/test_planning_orchestrator_extended.py
```

### Verify Git History
```bash
# Check commits on January 1, 2026 for governance changes
git log --since="2026-01-01" --until="2026-01-02" --oneline \
  --grep="governance\|Phase -1\|REFACTOR" -- \
  cortex-brain/response-templates-v4.yaml \
  .github/prompts/CORTEX.prompt.md \
  .github/copilot-instructions.md
```

---

## 📊 Expected Results Summary

| Component | Change | Verification Command | Expected Output |
|-----------|--------|---------------------|-----------------|
| Response Template | Added governance_requirements | `grep governance_requirements cortex-brain/response-templates-v4.yaml` | Section found |
| CORTEX.prompt.md | Added enforcement checklist | `grep "ORCHESTRATOR ENGAGEMENT" .github/prompts/CORTEX.prompt.md` | 5-step checklist |
| Master Plan | Added Phase -1 | `grep "Phase -1" 00-RECURSIVE-MASTER-PLAN.md` | Phase -1 section |
| Master Plan | Expanded REFACTOR | `grep "10\.[0-9]" 00-RECURSIVE-MASTER-PLAN.md \| wc -l` | ≥18 tasks |
| copilot-instructions | Updated SKULL rules | `grep -c "\`.*_ENFORCEMENT\`" .github/copilot-instructions.md` | 8 rules |
| Validation Script | Created | `test -f cortex-toolkit/validate_plan_governance.py` | File exists |
| Validation Script | Works correctly | `python cortex-toolkit/validate_plan_governance.py {plan}` | 10.0/10 score |
| Planning Manifest | Phase -1 config | `grep phase_minus_one cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml` | Section found |

---

## 🔄 Rollback Instructions (If Issues Found)

If any verification fails, check Git history for changes:

```bash
# View governance implementation commits
git log --since="2026-01-01" --until="2026-01-02" --oneline --all

# If rollback needed
git revert <commit-hash>
```

**DO NOT ROLLBACK** - Instead, create new backlog item to fix specific issue found during verification.

---

## 📝 Next Actions After Verification

**If All Checks Pass:**
1. Update governance implementation summary with verification timestamp
2. Close gap analysis and implementation summary (delete files)
3. Mark planning governance as "PRODUCTION READY"

**If Any Checks Fail:**
1. Create specific backlog item for failed check
2. Prioritize as CRITICAL (00-09)
3. Re-run verification after fix

---

## 🗑️ AUTO-DELETE INSTRUCTION

**After successful verification:** Delete this file AND source documents:
```bash
rm -f /Users/asifhussain/PROJECTS/CORTEX/.asif/backlog/10-verify-planning-governance-implementation.md
rm -f /Users/asifhussain/PROJECTS/CORTEX/.asif/backlog/planning-governance-gap-analysis-2026-01-01.md
rm -f /Users/asifhussain/PROJECTS/CORTEX/.asif/backlog/planning-governance-implementation-summary-2026-01-01.md
```
