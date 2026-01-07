---

## ⚠️ MANDATORY Requirements (Auto-Added by Maintenance - Phase 7)

### Visual Progress Tracking
Use `autonomous_execution_progress` template from `response-templates-v4.yaml` (line 863)

**Example Progress Bar:**
```
| # | Phase | Status | Progress | TDD Status |
|---|-------|--------|----------|------------|
| **Overall** | 🟡 | `[░░░░░░░░░░░░░░░░░░░░]` 0% | Phase 0/N | - |
```

### Response Template Helpers
- `generate_progress_bar(percentage, width=20, filled='█', empty='░')`
- `generate_tdd_status(red_done, green_done, refactor_done)`
- `render_autonomous_progress(...)` - Full convenience method

### Final REFACTOR Phase (MANDATORY - SKULL Rule)
Per `REFACTOR_CODE_CLEANUP_ENFORCEMENT`:
- ✅ Whole-file cleanup (not just new code)
- ✅ Complexity ≤30 for all functions
- ✅ SOLID principles enforced
- ✅ Zero dead code/unused imports
- ✅ 100% test pass rate

### copilot_instructions
```yaml
copilot_instructions:
  response_template: "autonomous_execution_progress"
  progress_updates: true
  tdd_enforcement: true
  final_refactor_required: true
  checkpoint_frequency: "per_phase"
```

**Reference:** `planning-system-4.0-manifest.yaml` (lines 118-157, 639-677)
**Maintenance:** Auto-added by Phase 7 (Knowledge Validation) on December 31, 2025
