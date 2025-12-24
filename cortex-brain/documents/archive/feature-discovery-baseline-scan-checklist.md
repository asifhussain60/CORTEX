# Feature Discovery Baseline Scan Checklist

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Date:** December 10, 2025  
**Status:** 📋 READY FOR EXECUTION

---

## 🎯 Purpose

After implementing the Feature Discovery Module in Phase 0, run a comprehensive baseline scan to discover ALL orchestrators in the CORTEX codebase. Use results to update the master plan with complete orchestrator inventory before proceeding with consolidation implementation.

---

## 📋 Pre-Scan Checklist

### Prerequisites
- [ ] Feature Discovery Module implementation complete
- [ ] `src/operations/modules/epm/auto_registration_orchestrator.py` functional
- [ ] EPM discovery rules configured
- [ ] Metadata extraction working (docstrings, triggers, LOC)
- [ ] Test scan completed successfully on sample orchestrators

### Scan Configuration
- [ ] Scan scope: Entire CORTEX codebase (`src/`, `cortex-brain/`, `scripts/`)
- [ ] File patterns: `*orchestrator*.py`, `*_workflow*.py`, `*_operations*.py`
- [ ] Metadata fields: name, file path, LOC, triggers, capabilities, dependencies
- [ ] Output format: JSON + Markdown report

---

## 🔍 Scan Execution Steps

### Step 1: Run Baseline Scan (Day 3 of Phase 0)

**Command:**
```bash
python -m src.operations.modules.epm.auto_registration_orchestrator --mode=baseline_scan --output=cortex-brain/documents/reports/
```

**Expected Outputs:**
1. `orchestrator-discovery-baseline-scan.json` - Raw scan data
2. `orchestrator-discovery-baseline-scan.md` - Formatted report
3. Console output with discovered orchestrator count

**Validation:**
- [ ] Scan completed without errors
- [ ] JSON file generated with valid structure
- [ ] Markdown report readable and formatted
- [ ] Orchestrator count displayed: XX orchestrators found

### Step 2: Review Scan Results

**Review Checklist:**
- [ ] **Total orchestrators found:** _____ (compare to baseline 71)
- [ ] **LOC total:** _____ (compare to baseline 40,400)
- [ ] **Orchestrators by directory:**
  - [ ] `src/orchestrators/`: _____
  - [ ] `src/operations/orchestrators/`: _____
  - [ ] `src/cortex_agents/`: _____
  - [ ] Other locations: _____
- [ ] **Orchestrators not in original audit:** _____ (list below)
- [ ] **Orchestrators in audit but not found:** _____ (list below)

**New Orchestrators Found (Not in Original 71):**
1. _____________________________________
2. _____________________________________
3. _____________________________________
(Add more as needed)

**Missing Orchestrators (In Audit but Not Found):**
1. _____________________________________
2. _____________________________________
3. _____________________________________
(Add more as needed)

### Step 3: Generate Gap Analysis Report

**Command:**
```bash
python -m src.operations.utilities.gap_analysis_generator \
  --baseline=cortex-brain/documents/planning/orchestrators/cortex-4.0-complete-orchestrator-audit.md \
  --scan=cortex-brain/documents/reports/orchestrator-discovery-baseline-scan.json \
  --output=cortex-brain/documents/reports/orchestrator-discovery-gap-analysis.md
```

**Gap Analysis Contents:**
- [ ] **Summary:** Total orchestrators (baseline vs found)
- [ ] **New discoveries:** Orchestrators not in baseline audit
- [ ] **Missing items:** Orchestrators in audit but not discovered
- [ ] **Metadata quality:** How many orchestrators have complete metadata
- [ ] **Recommendations:** Adjustments to consolidation strategy
- [ ] **Impact assessment:** Timeline, LOC, test count adjustments

---

## 📝 Master Plan Update Checklist

### Update orchestration-master-plan.md

**Section 1: Executive Summary**
- [ ] Update "71+ orchestrators" to actual count: _____
- [ ] Update "40,400+ LOC" to actual count: _____
- [ ] Update "87%+ reduction" calculation: (_____ → 9) = _____%

**Section 2: Success Metrics Table**
- [ ] Update "Orchestrator count" Current value: _____
- [ ] Update "Total code" Current value: _____
- [ ] Recalculate "Target" values based on actual baseline
- [ ] Update "Impact" percentages

**Section 3: Orchestrator Portfolio**
- [ ] Review Feature Discovery Module description
- [ ] Add any newly discovered orchestrators to appropriate phase
- [ ] Update file counts for each unified orchestrator
- [ ] Update LOC estimates

**Section 4: Implementation Timeline**
- [ ] Adjust Phase 1-7 timelines if needed (>10 new orchestrators = +1 week)
- [ ] Update deliverables to reflect actual orchestrator counts
- [ ] Adjust test counts proportionally

**Section 5: Test Coverage Strategy**
- [ ] Update "Migration Tests" count: 600 → _____ (10 tests per orchestrator)
- [ ] Update "Total Test Suite" count: 2,300 → _____
- [ ] Update test distribution table

**Section 6: Removal Timeline**
- [ ] Update "Total Deletions" count: 71+ → _____
- [ ] Update batch sizes (distribute evenly across 5 batches)
- [ ] Update LOC deletion estimate: 40,400+ → _____

**Section 7: Sub-Plans**
- [ ] Create additional sub-plan documents for new orchestrators (if any)
- [ ] Update sub-plan tracker with new orchestrator count

---

## 🚦 Decision Points

### If NO New Orchestrators Found (Count = 71)
✅ **Action:** Proceed with current plan, mark all metrics as final
- Update master plan to remove "+" qualifiers (71+ → 71)
- Proceed directly to Phase 1 implementation
- No timeline adjustments needed

### If 1-10 New Orchestrators Found (Count = 72-81)
⚠️ **Action:** Minor plan adjustments
- [ ] Categorize new orchestrators into existing 9 unified orchestrators
- [ ] Update LOC and test counts proportionally
- [ ] Add 1-2 days to Phase 0 for planning finalization
- [ ] Update master plan metrics
- [ ] Proceed to Phase 1

### If >10 New Orchestrators Found (Count > 81)
🚨 **Action:** Significant plan review required
- [ ] Schedule stakeholder meeting to review findings
- [ ] Assess if new orchestrators require separate unified orchestrator
- [ ] Recalculate timeline (may need +1-2 weeks)
- [ ] Update consolidation strategy
- [ ] Create additional sub-plans
- [ ] Get approval before Phase 1

---

## 📊 Output Documents

### Required Documents to Generate

1. **orchestrator-discovery-baseline-scan.md**
   - Location: `cortex-brain/documents/reports/`
   - Contents: Complete list of all discovered orchestrators with metadata
   - Format: Markdown table with columns (Name, File, LOC, Triggers, Capabilities)

2. **orchestrator-discovery-gap-analysis.md**
   - Location: `cortex-brain/documents/reports/`
   - Contents: Comparison with original audit, recommendations
   - Format: Markdown with sections (Summary, Gaps, Recommendations, Impact)

3. **orchestration-master-plan.md (UPDATED)**
   - Location: `cortex-brain/documents/planning/`
   - Contents: Updated metrics, counts, timelines based on scan results
   - Format: Updated existing document with actual counts

4. **orchestrators/README.md (UPDATED)**
   - Location: `cortex-brain/documents/planning/orchestrators/`
   - Contents: Updated sub-plan status dashboard with actual orchestrator count
   - Format: Updated existing tracker

---

## ✅ Completion Criteria

**Phase 0 Feature Discovery baseline scan is complete when:**
- [x] Scan executed successfully
- [x] All orchestrators discovered and cataloged
- [x] Gap analysis report generated
- [x] Master plan updated with actual counts
- [x] Sub-plan tracker updated
- [x] Stakeholders approve updated plan
- [x] Timeline adjustments (if any) approved
- [x] Ready to proceed with Phase 1 implementation

---

## 📞 Approval & Sign-Off

**Technical Lead Review:**
- [ ] Scan results reviewed
- [ ] Gap analysis validated
- [ ] Master plan updates approved
- Signature: _________________ Date: _________

**Architect Review:**
- [ ] Consolidation strategy remains valid
- [ ] No additional unified orchestrators needed
- [ ] Timeline adjustments reasonable
- Signature: _________________ Date: _________

**Stakeholder Approval:**
- [ ] Updated metrics approved
- [ ] Timeline approved
- [ ] Ready to proceed with Phase 1
- Signature: _________________ Date: _________

---

## 🚀 Next Steps After Completion

1. **Create Additional Sub-Plans** - For any newly discovered orchestrators
2. **Finalize Phase 1 Timeline** - Confirm start date for TDD/DevOps implementation
3. **Assign Development Teams** - Based on updated orchestrator inventory
4. **Begin Phase 1 Implementation** - TDD Orchestrator (RED phase)

---

**Status:** Ready for execution after Feature Discovery Module implementation complete.
