# CORTEX Review System Restructuring - v4.1.2

**Date:** January 23, 2026  
**Status:** ✅ COMPLETE  

## Summary of Changes

The cortex-review.prompt.md has been restructured to properly separate concerns:

### **Before (v4.1.1) - Mixed Structure**
```
All outputs → _workspaces/roadmap/issues/
├─ Gap reports
├─ Finding reports
├─ Audit validations
└─ Remediation plans (embedded)

All remediation in → cortex-impl-map.yaml::remediation
```

### **After (v4.1.2) - Clean Separation**
```
Gap Reports & Findings → _workspaces/roadmap/issues/<YYYY-MM-DD_HHMMSS>/
├─ Phase 0: phase0-validation.yaml
├─ Phase 1: review-gap-inventory.yaml
├─ Phase 2: review-stubs.yaml
├─ Phase 3: Findings-BRIT.yaml, Findings-HALL.yaml, etc.
├─ Phase 4: requirements-analysis.yaml
├─ Phase 5: review-findings-consolidated.yaml
├─ Phase 6: audit-trace-validation.yaml, mcp-toolkit-audit.yaml, cortex-lens-ast-validation.yaml
└─ (timestamped & archived per-review)

Remediation Phases → _workspaces/roadmap/phases/
├─ REM-PHASE-CRITICAL-BLOCKERS.yaml (executable - Week 1, blocking)
├─ REM-PHASE-ARCHITECTURE.yaml (executable - Week 2-3, high priority)
├─ REM-PHASE-TECHNICAL-DEBT.yaml (executable - Week 4, medium priority)
├─ REM-PHASE-IMPROVEMENTS.yaml (executable - continuous, backlog)
└─ (persistent, updated across reviews)

Remediation Reference → cortex-impl-map.yaml::remediation_reference
├─ lightweight reference track
├─ points to phase files
└─ execution_roadmap with timeline & blocking status
```

## Key Improvements

### 1. **Clear Concern Separation**
- **Issues folder:** Timestamped per-review gap analysis & findings (read-only archive)
- **Phases folder:** Persistent, executable remediation roadmaps (active, updated)
- **Impl-map reference:** Lightweight pointer to phases for version control

### 2. **Improved Persistence Model**
- Gap reports are timestamped and archived (immutable record of each review)
- Remediation phases are persistent and can be updated across reviews
- No duplicate data between issues/ and phases/

### 3. **Executable Remediation Phases**
Each phase file is now a complete, executable YAML:
```yaml
remediation_phase:
  phase_id: "REM-PHASE-CRITICAL-BLOCKERS"
  timeline: "Week 1"
  blocking_deployment: true
  items:
    - id: "REM-CRIT-001"
      issue: "..."
      remediation: "..."
      acceptance_tests: [...]
      completion_criterion: "..."
  completion_checklist: [...]
  success_criteria: [...]
```

### 4. **Better Traceability**
- Each remediation item links back to source finding file:
  ```
  source_finding: "BRIT-SPOF-003"
  file: "_workspaces/roadmap/issues/2026-01-23_143022/Findings-BRIT.yaml"
  ```

### 5. **Execution Roadmap is Now a Navigation Tool**
```yaml
cortex-impl-map.yaml::remediation_reference:
  phases:
    critical_blockers:
      file: "_workspaces/roadmap/phases/REM-PHASE-CRITICAL-BLOCKERS.yaml"
      timeline: "Week 1"
      blocking_deployment: true
  execution_roadmap:
    phase_1_blockers:
      file: "..."
      action: "Execute immediately - blocks deployment"
```

## Workflow Changes

### Phase 7 (Remediation Planning) Now:

1. **Analyzes all gap reports** from `_workspaces/roadmap/issues/{TIMESTAMP}/`
2. **Creates 4 phase files** in `_workspaces/roadmap/phases/`:
   - REM-PHASE-CRITICAL-BLOCKERS.yaml
   - REM-PHASE-ARCHITECTURE.yaml
   - REM-PHASE-TECHNICAL-DEBT.yaml
   - REM-PHASE-IMPROVEMENTS.yaml
3. **Updates cortex-impl-map.yaml** with `remediation_reference:` track
   - Lightweight reference (not embedding full remediation data)
   - Points to phase files
   - Includes execution roadmap

## Completion Gates Updated

### Gate 4: Remediation Planning (NEW)
```yaml
- [ ] All phase files exist in _workspaces/roadmap/phases/
- [ ] Each phase YAML is valid and executable
- [ ] All findings mapped to remediation items
- [ ] Dependency ordering correct
- [ ] Acceptance tests defined for critical items
- [ ] remediation_reference added to cortex-impl-map.yaml
- [ ] Phase files reference source findings in issues/
```

### Gate 5: Final Declaration (UPDATED)
Now references phase files instead of embedded remediation data:
```yaml
remediation_phases:
  critical_blockers:
    file: "_workspaces/roadmap/phases/REM-PHASE-CRITICAL-BLOCKERS.yaml"
    timeline: "Week 1"
    status: "PENDING - Execute immediately"
```

## File Structure Reference

**Gap Reports (Timestamped Archive):**
```
_workspaces/roadmap/issues/2026-01-23_143022/
├─ review-gap-inventory.yaml
├─ review-stubs.yaml
├─ Findings-BRIT.yaml
├─ Findings-HALL.yaml
├─ Findings-GOV.yaml
├─ Findings-ASM.yaml
├─ Findings-DEBT.yaml
├─ Findings-STATE.yaml
├─ Findings-ARCH.yaml
├─ Findings-INTEG.yaml
├─ audit-trace-validation.yaml
├─ mcp-toolkit-audit.yaml
├─ cortex-lens-ast-validation.yaml
├─ requirements-analysis.yaml
└─ review-findings-consolidated.yaml
```

**Remediation Phases (Persistent):**
```
_workspaces/roadmap/phases/
├─ REM-PHASE-CRITICAL-BLOCKERS.yaml      (Week 1, blocking)
├─ REM-PHASE-ARCHITECTURE.yaml           (Week 2-3, high)
├─ REM-PHASE-TECHNICAL-DEBT.yaml         (Week 4, medium)
└─ REM-PHASE-IMPROVEMENTS.yaml           (continuous, backlog)
```

**Implementation Map Reference:**
```yaml
cortex-impl-map.yaml
├─ implementation_map: {...}
├─ [other tracks...]
└─ remediation_reference:           ← NEW lightweight reference
   ├─ created: "2026-01-23T..."
   ├─ phases:
   │  ├─ critical_blockers: {file: "...", blocking_deployment: true}
   │  ├─ architecture: {file: "...", blocking_deployment: false}
   │  ├─ technical_debt: {file: "...", blocking_deployment: false}
   │  └─ improvements: {file: "...", blocking_deployment: false}
   └─ execution_roadmap:
      ├─ phase_1_blockers: {file: "...", action: "..."}
      ├─ phase_2_architecture: {file: "...", action: "..."}
      ├─ phase_3_technical_debt: {file: "...", action: "..."}
      └─ phase_4_improvements: {file: "...", action: "..."}
```

## Benefits

### 1. **Cleaner Architecture**
- Single Responsibility Principle: Each directory has clear purpose
- Issues = gap analysis (immutable, timestamped)
- Phases = remediation roadmap (mutable, persistent)
- impl-map = reference only (lightweight)

### 2. **Better Auditability**
- Full gap analysis preserved in timestamped issues/
- Remediation phases are executable and trackable
- Version control friendly (small impl-map reference)

### 3. **Easier Execution**
- Teams can simply `cat _workspaces/roadmap/phases/REM-PHASE-*.yaml` to see what to do
- Each phase is self-contained with acceptance tests & success criteria
- No parsing cortex-impl-map.yaml needed for execution

### 4. **Better Progress Tracking**
- Remediation phases can have `status: COMPLETED | IN_PROGRESS | PENDING`
- Teams update phase files as work progresses
- Historical phases/ shows remediation history

### 5. **Simpler Integration**
- Single reference line in cortex-impl-map.yaml (no duplicated data)
- Phase files are the source of truth for execution
- Easier to track which findings were remediated

## Next Steps

### For Execution (cortex-builder.prompt.md):
1. Read `_workspaces/roadmap/phases/REM-PHASE-CRITICAL-BLOCKERS.yaml`
2. For each item:
   - Implement remediation
   - Run acceptance tests
   - Mark `status: COMPLETED`
   - Update cortex-impl-map.yaml phase reference
3. Execute phases in order: CRITICAL → ARCHITECTURE → DEBT → IMPROVEMENTS

### For Next Review Cycle:
1. Previous phase files remain in `_workspaces/roadmap/phases/`
2. Create new timestamped issues/ folder with gap analysis
3. Generate updated phase files (or reuse if no changes needed)
4. Update remediation_reference in cortex-impl-map.yaml

## Validation

To verify the new structure:

```bash
# Check gap reports exist and are timestamped
ls -la _workspaces/roadmap/issues/2026-01-23_*/

# Check phase files are executable YAML
ls -la _workspaces/roadmap/phases/REM-PHASE-*.yaml

# Verify impl-map reference
grep -A 20 "remediation_reference:" cortex-impl-map.yaml

# Parse a phase file
python3 -c "import yaml; print(yaml.safe_load(open('_workspaces/roadmap/phases/REM-PHASE-CRITICAL-BLOCKERS.yaml')))"
```

## Migration Notes

If migrating from v4.1.1 to v4.1.2:

1. ✅ Gap reports can remain in old issues/ folders (timestamped archives)
2. ✅ Move any existing remediation data to new phases/ directory structure
3. ✅ Update cortex-impl-map.yaml to use `remediation_reference:` instead of `remediation:`
4. ✅ Phase files become executable source of truth

---

**Status:** ✅ PROMPT UPDATED  
**Effective:** Immediately upon next review execution  
**Backward Compatibility:** Existing issues/ reports continue to work; new phases/ takes over remediation
