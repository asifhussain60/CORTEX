# CONTINUATION PROMPT - C150 Remediation Plan

**Use this prompt to resume execution if session is interrupted due to token limits.**

---

## 📍 Quick Resume Command

```
Continue C150 Remediation Plan execution.

Current status: Check tracking/progress-tracker.json for latest phase completion.

Plan location: cortex-brain/documents/planning/active/c150-remediation-plan/
Master plan: 00-c150-remediation-plan.yaml

Resume from: [NEXT_INCOMPLETE_PHASE]
```

---

## 🎯 Plan Context (Quick Reference)

**Plan ID:** c150-remediation  
**Purpose:** Fix critical gaps from C150 (HTML Glassmorphism Alignment) plan  
**Total Phases:** 17 (including Phase -2 and Phase 999)  
**Estimated Duration:** 96 hours (12 business days)

**Key Gaps Being Fixed:**
1. 6 orchestrators broken (cannot instantiate)
2. Runtime governance missing (SKULL compliance gap)
3. CORTEX-5.0 docs incomplete
4. Deployment validation missing
5. Dead code not removed (1,009 CSS classes)
6. Dual-source brittleness (YAML + DB)
7. 82 unit tests blocked

---

## 📊 Phase Checklist

Use `tracking/progress-tracker.json` for detailed status. Quick checklist:

- [ ] Phase -2: Setup Verification (0.5 hours)
- [ ] Phase 0: Context Discovery (1.0 hours)
- [ ] Phase 1: Acceptance Criteria Cross-Check (1.5 hours)
- [ ] Phase 2: Fix planning_v5 Orchestrator (2.0 hours)
- [ ] Phase 3: Fix StateManager Interface (4.0 hours)
- [ ] Phase 4: Fix Python 3.9/3.10 Compatibility (3.0 hours)
- [ ] Phase 5: Implement Runtime Governance (10.0 hours)
- [ ] Phase 6: Resolve Dual-Source Brittleness (3.0 hours)
- [ ] Phase 7: Write Refinement Docs (6.0 hours)
- [ ] Phase 8: Write Debug Docs (6.0 hours)
- [ ] Phase 9: Document Features + Diagrams (10.0 hours)
- [ ] Phase 10: Execute Dead Code Removal (4.0 hours)
- [ ] Phase 11: Deployment Validation (48.0 hours)
- [ ] Phase 12: Update C150 Certificate (1.0 hours)
- [ ] Phase 13: Automate Acceptance Validation (8.0 hours)
- [ ] Phase 14: Automate Brittleness Checking (6.0 hours)
- [ ] Phase 999: Teardown + REFACTOR + Commit (2.0 hours)

---

## 🔍 Finding Your Place

### Check Current Status
```bash
cat cortex-brain/documents/planning/active/c150-remediation-plan/tracking/progress-tracker.json | grep '"status"'
```

### View Latest Report
```bash
ls -lt cortex-brain/documents/planning/active/c150-remediation-plan/reports/
```

### Check Outputs Created
```bash
find cortex-brain/documents/planning/active/c150-remediation-plan/ -type f -name "*.md" -o -name "*.json" -o -name "*.patch"
```

---

## 🚀 Resume Execution Patterns

### If in Middle of Phase
```
Continue Phase [N] ([PHASE_NAME]) for C150 Remediation Plan.

Last completed task: [CHECK_REPORTS]
Remaining tasks: [CHECK_YAML_PHASE_DEFINITION]
```

### If Phase Just Completed
```
Begin Phase [N+1] ([NEXT_PHASE_NAME]) for C150 Remediation Plan.

Previous phase artifacts: [CHECK_OUTPUTS_IN_PROGRESS_TRACKER]
```

### If Need Context Refresh
```
Review C150 Remediation Plan progress.

Plan: cortex-brain/documents/planning/active/c150-remediation-plan/
Status: tracking/progress-tracker.json
Master YAML: 00-c150-remediation-plan.yaml

Provide: Summary of completed phases, next phase to execute, any blockers.
```

---

## 📚 Key Files Reference

| File | Purpose |
|------|---------|
| `00-c150-remediation-plan.yaml` | Master plan (all phase definitions) |
| `README.md` | Quick start guide |
| `tracking/progress-tracker.json` | Real-time execution status |
| `analysis/` | Gap analysis, validation reports |
| `artifacts/` | Patches, fixes, generated code |
| `context/` | Context discovery, background |
| `reports/` | Progress, completion reports |

---

## ⚠️ Important Notes

- **Python Execution:** Each phase has a `python_executor` script path in YAML
- **State Tracking:** Always update `progress-tracker.json` after phase completion
- **Validation:** Every phase has validation criteria in YAML
- **Dependencies:** Check `phase_dependencies` in YAML before starting a phase
- **SKULL Compliance:** Enforced via Phase 5 (governance middleware)

---

## 🛠️ Troubleshooting

### Session Lost Progress
- Progress tracker should have latest status
- Check `reports/` folder for last completion report
- Review `artifacts/` for last generated files

### Phase Failed Validation
- Check validation criteria in YAML phase definition
- Review phase-specific error logs
- May need to rerun phase with fixes

### Dependencies Missing
- Run Phase -2 (Setup Verification) to validate dependencies
- Check `analysis/setup-verification-report.md`

---

**Plan Created:** January 4, 2026  
**Continuation Prompt Version:** 1.0  
**Last Updated:** [AUTO-UPDATED-BY-ORCHESTRATOR]
