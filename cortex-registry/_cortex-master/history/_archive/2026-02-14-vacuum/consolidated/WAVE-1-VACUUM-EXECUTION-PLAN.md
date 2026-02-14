# WAVE-1 Documentation Vacuum - Execution Plan
# Authority: cortex-architect.prompt.md § SILENT AUTONOMOUS EXECUTION
# Date: 2026-02-14
# Status: AUTONOMOUS EXECUTION IN PROGRESS

## Baseline Metrics
- **Current Files:** 119 files in _cortex-master root
- **Target Files:** ≤20 files
- **Reduction Needed:** 99 files (83% reduction)
- **Test Suite:** 15,590 tests collected ✅

## Triage Analysis

### Category 1: OBSOLETE - Archive Immediately (47 files)
**Criteria:** Superseded by newer versions, redundant summaries, wave guides

Files:
- AUTONOMOUS-WAVE-EXECUTION-GUIDE-V2-2026-02-12.md → Superseded by VSCODE-AUTONOMOUS-EXECUTION-GUIDE.md
- ALL-WAVES-SUMMARY-TABLE.md → Superseded by master-plan.yaml waves section
- WAVE-STATUS-*-2026-02-*.* → Multiple status files, keep only latest
- WAVE-[0-9]-*.yaml → Old wave plans, superseded by consolidated plan
- SESSION-COMPLETE-*.yaml → Historical, archive for reference
- EXECUTION-GUIDE-*.md → Multiple guides, consolidate into one

Action: Move to _archive/2026-02-14-vacuum/

### Category 2: CONSOLIDATE - Merge into Single Files (35 files)
**Criteria:** Similar content, can be unified into master documents

Groups:
1. **Wave Execution Guides** (12 files) → Single WAVES-EXECUTION-TRACKER.yaml
2. **Master Plans** (8 files) → Keep master-plan.yaml only
3. **Status Updates** (7 files) → Consolidate into master-plan.yaml status section
4. **Quick References** (5 files) → Single QUICK-START.md
5. **Completion Reports** (3 files) → Archive (historical value only)

Action: Merge + archive originals

### Category 3: RETAIN - Keep Active (20 files)
**Criteria:** Active, unique content, cannot be consolidated

Files to Keep:
1. README.md (entry point)
2. master-plan.yaml (authority)
3. VSCODE-AUTONOMOUS-EXECUTION-GUIDE.md (active guide)
4. waves/ (directory - active waves)
5. phases/ (directory - active phases)
6. enhancements/ (directory - active enhancements)
7. governance/ (directory - governance rules)
8. _archive/ (directory - historical)
9. baselines/ (directory - metrics)
10. dashboard/ (directory - status tracking)
11-20: Core specification files (orchestrator_specs.json, execution-queue-config.yaml, etc.)

## Execution Stages

### Stage 1: Create Archive Structure (2 min)
```bash
mkdir -p _archive/2026-02-14-vacuum/{obsolete,consolidated}
```

### Stage 2: Move Obsolete Files (5 min)
Move 47 obsolete files → _archive/2026-02-14-vacuum/obsolete/

### Stage 3: Consolidate & Merge (15 min)
1. Create WAVES-EXECUTION-TRACKER.yaml (consolidate 12 wave guides)
2. Update master-plan.yaml with consolidated status
3. Create QUICK-START.md (consolidate 5 quick refs)
4. Move originals → _archive/2026-02-14-vacuum/consolidated/

### Stage 4: Generate Manifest (3 min)
Create archive-manifest.yaml documenting:
- Files archived
- Consolidation mapping
- Rationale for each decision

### Stage 5: Validation (5 min)
- Count files: ≤25 in root
- Test collection: 15,590 tests pass
- CORE-002 check: No markdown sprawl
- Git commit with AC markers

## Success Criteria
- [  ] ≤25 files in _cortex-master root
- [  ] 15,590 tests still collected
- [  ] Archive manifest created
- [  ] CORE-002 compliant (no sprawl)
- [  ] AC_START → AC_COMPLETE markers in commit

## Token Budget: 80K / 80K (100%)
## Duration: 30 min estimated
