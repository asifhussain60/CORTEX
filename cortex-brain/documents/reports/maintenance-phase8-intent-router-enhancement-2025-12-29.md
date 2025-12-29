# Maintenance Prompt Enhancement: Complete Intent Router Wiring

**Date:** December 29, 2025  
**Author:** Asif Hussain  
**Issue:** Maintenance Phase 8 needed enhancement to ensure ALL orchestrators are wired during prompt regeneration

---

## 🎯 Problem Statement

When `system maintenance` recreates `CORTEX.prompt.md` and `copilot-instructions.md`, it was:
1. Missing several orchestrators (Debug, CORTEX Lens)
2. Not systematically discovering all manifests
3. Not enforcing PLANNING_ISOLATION rule
4. Lacking comprehensive validation

This caused incomplete intent routing and potential command failures.

---

## ✅ Solution Implemented

### 1. Enhanced Phase 8: "Regenerate Lean Prompts (WITH COMPLETE INTENT ROUTER WIRING)"

**New Capabilities:**

#### 8a. Pre-Regeneration: Orchestrator Discovery
- **Scans** `cortex-brain/manifests/orchestrators/` for ALL manifests
- **Identifies** minimum 8 required orchestrators
- **Lists** optional but recommended orchestrators

#### 8b. Complete CORTEX.prompt.md Template
- **Full template** with ALL 10 orchestrators wired:
  1. Planning System
  2. TDD Mastery
  3. Debug Orchestrator (NEW)
  4. CORTEX Lens (NEW)
  5. Onboarding
  6. ADO Planning
  7. Code Sanitization
  8. Refinement
  9. System Maintenance
  10. Help

- **Includes:**
  - 🚨 PLANNING DETECTION section (HIGHEST PRIORITY)
  - Complete Intent Router table with ALL orchestrators
  - Planning vs. Implementation clarification
  - PLANNING_ISOLATION in SKULL rules
  - Example detection scenarios
  - All sections from original prompt

#### 8c. Complete copilot-instructions.md Template
- **Mirrors** ALL primary operations from CORTEX.prompt.md
- **Adds** PLANNING_ISOLATION to SKULL section
- **References** all 8 primary orchestrators in routing table
- **Stays** under 150 lines (anti-bloat)

#### 8d. Wiring Rules (8 rules)
1. Single Source of Truth
2. Deference to CORTEX.prompt.md
3. ALL Manifests wired
4. Minimum 3 Triggers per orchestrator
5. Output Specs for all
6. Planning Isolation indicators
7. SKULL Integration
8. Knowledge Library references

#### 8e. Auto-Repair Actions (10 steps)
- Automatic scanning, extraction, population
- Verification of manifest paths
- Line limit enforcement
- Duplicate prevention
- PLANNING_ISOLATION enforcement
- Backup before overwriting

#### 8f. Validation Commands
- Bash scripts to verify all orchestrators wired
- Check for broken paths
- Verify manifest references exist
- Check line counts

---

## 📊 Validation Checklist Enhancements

### Added: Intent Router Completeness Section (17 checks)

```markdown
### Intent Router Completeness 🆕
- [ ] Planning System orchestrator in Intent Router
- [ ] TDD Mastery orchestrator in Intent Router
- [ ] Debug Orchestrator in Intent Router
- [ ] CORTEX Lens orchestrator in Intent Router
- [ ] ADO Planning orchestrator in Intent Router
- [ ] Code Sanitization orchestrator in Intent Router
- [ ] Refinement orchestrator in Intent Router
- [ ] System Maintenance orchestrator in Intent Router
- [ ] Onboarding/Help orchestrator in Intent Router
- [ ] Minimum 8 orchestrators total in Intent Router
- [ ] All orchestrators have 3+ trigger patterns
- [ ] All orchestrators have output specifications
- [ ] Planning commands include "→ STOPS HERE" indicator
- [ ] PLANNING_ISOLATION rule in SKULL (CORTEX.prompt.md)
- [ ] PLANNING_ISOLATION rule in SKULL (copilot-instructions.md)
- [ ] copilot-instructions.md mirrors ALL primary operations
- [ ] No orphaned orchestrator manifests
```

### Updated: Success Criteria Table

Added:
- **Intent Router Completeness**: Minimum 8 orchestrators with 3+ triggers each
- **PLANNING_ISOLATION**: Rule enforced in both prompt files
- **ALL orchestrators wired** in CORTEX.prompt.md

---

## 📁 Supporting Documentation Created

### 1. Orchestrator Inventory (`cortex-brain/documents/analysis/orchestrator-inventory-2025-12-29.md`)

Complete catalog of:
- 8 primary orchestrators
- 2 secondary orchestrators
- Trigger patterns for each
- Output specifications
- Status of each
- Recommended Intent Router table
- Validation checklist

---

## 🔧 Files Modified

1. **`.github/prompts/cortex-maintenance.prompt.md`**
   - Enhanced Phase 8 (8a-8f)
   - Added orchestrator discovery
   - Complete templates for both prompts
   - 10-step auto-repair process
   - Validation commands
   - Intent Router Completeness checklist (17 checks)
   - Updated Success Criteria table

2. **`cortex-brain/documents/analysis/orchestrator-inventory-2025-12-29.md`** (NEW)
   - Complete orchestrator catalog
   - Trigger pattern reference
   - Wiring requirements
   - Validation checklist

---

## 🎯 Impact

### Before Enhancement:
```
system maintenance → Regenerate prompts
- Missing: Debug Orchestrator, CORTEX Lens
- No systematic discovery
- Manual wiring required
- Inconsistent between runs
```

### After Enhancement:
```
system maintenance → Regenerate prompts
✅ Scans all manifests automatically
✅ Wires minimum 8 orchestrators
✅ Includes Debug, CORTEX Lens, ALL others
✅ Enforces PLANNING_ISOLATION
✅ 17-point validation checklist
✅ Idempotent (same result every run)
✅ Complete templates provided
✅ Auto-repair with backups
```

---

## 🧪 Testing Recommendations

### To verify the enhancement works:

1. **Run maintenance:**
   ```
   system maintenance
   ```

2. **Check Phase 8 execution:**
   - Should scan `cortex-brain/manifests/orchestrators/`
   - Should find ALL manifest files
   - Should regenerate both prompts

3. **Validate results:**
   ```bash
   # Check orchestrator count in CORTEX.prompt.md
   grep -c "| \`.*\` |" .github/prompts/CORTEX.prompt.md  # Should be ≥8
   
   # Check line counts
   wc -l .github/prompts/CORTEX.prompt.md        # <200
   wc -l .github/copilot-instructions.md          # <150
   
   # Check for PLANNING_ISOLATION
   grep -c "PLANNING_ISOLATION" .github/prompts/CORTEX.prompt.md  # Should be ≥1
   grep -c "PLANNING_ISOLATION" .github/copilot-instructions.md    # Should be ≥1
   
   # Check for missing orchestrators
   ./cortex-brain/documents/analysis/orchestrator-inventory-2025-12-29.md
   # Compare with CORTEX.prompt.md Intent Router table
   ```

4. **Run intent router completeness checks:**
   - All 17 checklist items should pass

---

## 🔄 Rollback Plan

If issues occur:

1. Restore from backups:
   ```bash
   cp .github/prompts/CORTEX.prompt.md.backup .github/prompts/CORTEX.prompt.md
   cp .github/prompts/cortex-maintenance.prompt.md.backup .github/prompts/cortex-maintenance.prompt.md
   ```

2. Or revert specific section:
   - Locate "Phase 8: Regenerate Lean Prompts"
   - Replace with previous version

---

## 📚 Key Improvements

1. **Systematic Discovery**: Scans manifests, doesn't rely on manual list
2. **Complete Templates**: Full CORTEX.prompt.md and copilot-instructions.md provided
3. **Auto-Repair**: 10-step automated fixing process
4. **Validation**: 17-point Intent Router Completeness checklist
5. **PLANNING_ISOLATION**: Enforced in both files during regeneration
6. **Idempotency**: Same result on repeated runs
7. **Documentation**: Orchestrator inventory reference doc
8. **Safety**: Backups before overwriting

---

## 🎓 Lessons Learned

1. **Discovery > Hardcoding**: Scanning manifests beats maintaining lists
2. **Templates > Instructions**: Full templates prevent interpretation errors
3. **Validation > Hope**: 17-point checklist catches missing wiring
4. **Automation > Manual**: 10-step auto-repair eliminates human error
5. **Idempotency Matters**: Maintenance should be repeatable with same results

---

**Status:** ✅ COMPLETE  
**Next Steps:** Run `system maintenance` to test enhanced Phase 8  
**Success Metric:** All 17 Intent Router Completeness checks pass
