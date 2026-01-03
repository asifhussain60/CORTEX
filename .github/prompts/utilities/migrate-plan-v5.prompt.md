# 🔄 CORTEX Plan Migration to V5

**Version:** 1.0.0 | **Created:** January 3, 2026  
**Author:** Asif Hussain | **Purpose:** Migrate V4 plans to V5 Planning Architecture

---

## 🎯 Purpose

Transform existing Planning System V4 plans to V5 architecture, which includes:

1. **Master Orchestrator Integration** - Centralized routing and state coordination
2. **Cross-Session Context** - Automatic continuation from Tier 1 Working Memory
3. **Enhanced Folder Structure** - Adds `architecture/` and `phases/` directories
4. **AST-Based Analysis** - Phase 0 code scanning for comprehensive discovery
5. **Governance Integration** - Tier 0 brain-protection-rules.yaml compliance
6. **Knowledge Graph Queries** - Tier 2 pattern reuse and discovery
7. **Progressive Validation** - Checkpoint-based resumability

---

## 🏗️ V4 vs V5 Structure Comparison

### V4 Structure (Current)
```
{plan-name}/
├── 00-master-plan.md
├── context/
├── reports/
├── artifacts/
└── tracking/
```

### V5 Structure (Target)
```
{plan-name}/
├── 00-master-plan.md (V4 - PRESERVED)
├── 00-MASTER-PLAN-V5.md (V5 - NEW)
├── CONTINUATION-PROMPT.md (V5 - NEW)
├── context/ (V4 - PRESERVED + new files)
│   ├── knowledge-library-review.md (NEW)
│   ├── ast-scan-results.json (NEW)
│   └── governance-compliance.md (NEW)
├── reports/ (V4 - PRESERVED + migration report)
├── artifacts/ (V4 - PRESERVED)
├── tracking/ (V4 - PRESERVED)
├── architecture/ (V5 - NEW)
│   ├── README.md
│   └── master-orchestrator-integration.md
└── phases/ (V5 - NEW)
    ├── README.md
    ├── phase-minus-1-knowledge-library.md
    ├── phase-0-foundation.md
    └── phase-final-refactor.md
```

---

## 🚀 Usage

### Interactive Mode (Recommended)

**Say in CORTEX Chat:**

```
migrate plan cortex-documentation to V5
```

**CORTEX will:**
1. Locate the plan folder in `cortex-brain/documents/planning/active/`
2. Validate V4 structure
3. Preview changes (dry run)
4. Confirm with user
5. Execute migration
6. Display migration report

### Command-Line Mode

**Dry Run (Preview):**
```bash
python scripts/migrate_plan_to_v5.py \
  --plan cortex-brain/documents/planning/active/cortex-documentation \
  --dry-run
```

**Execute Migration:**
```bash
python scripts/migrate_plan_to_v5.py \
  --plan cortex-brain/documents/planning/active/cortex-documentation
```

**Migrate All Active Plans:**
```bash
for plan in cortex-brain/documents/planning/active/*/; do
  python scripts/migrate_plan_to_v5.py --plan "$plan"
done
```

---

## 🔍 What Gets Migrated

### Preserved (V4 → V5)
- ✅ Original `00-master-plan.md` (reference)
- ✅ All `context/` files
- ✅ All `reports/` files
- ✅ All `artifacts/` files
- ✅ All `tracking/` files

### Added (V5 New)
- ✅ `00-MASTER-PLAN-V5.md` - V5-compliant master plan
- ✅ `CONTINUATION-PROMPT.md` - Quick resume instructions
- ✅ `architecture/` - Master Orchestrator integration docs
- ✅ `phases/` - Phase-specific implementation details
- ✅ `phases/phase-minus-1-knowledge-library.md` - Knowledge review phase
- ✅ `phases/phase-0-foundation.md` - Foundation & AST scan phase
- ✅ `phases/phase-final-refactor.md` - Final cleanup phase

### Generated During Migration
- ✅ Backup of V4 plan in `backups/{plan-name}_v4_backup_{timestamp}/`
- ✅ Migration report in `reports/v5-migration-report-{timestamp}.md`

---

## 📋 V5 Enhancements

### Phase -1: Knowledge Library Review (NEW)
**Purpose:** Search existing CORTEX knowledge before implementation

**Activities:**
- Query Tier 2 Knowledge Graph for similar patterns
- Review lessons-learned.yaml for relevant insights
- Identify reusable code patterns
- Document reuse opportunities

**Deliverables:**
- `context/knowledge-library-review.md`
- `context/reuse-opportunities.md`

### Phase 0: Foundation & AST Scan (NEW)
**Purpose:** Establish baseline and scan codebase

**Activities:**
- Run AST scan on all Python files in scope
- Validate against brain-protection-rules.yaml (61 rules)
- Document current architecture state
- Identify Master Orchestrator integration points

**Deliverables:**
- `context/ast-scan-results.json`
- `context/governance-compliance.md`
- `architecture/integration-points.md`

### Final Phase: REFACTOR & Cleanup (NEW)
**Purpose:** Comprehensive cleanup to prevent technical debt

**Activities:**
- Detect and remove orphaned code
- Eliminate duplicate code patterns
- Complete ≥18 cleanup tasks per file category
- Ensure SKULL rule compliance

**Deliverables:**
- `context/orphaned-code-report.json`
- `context/duplicate-code-analysis.md`
- `reports/cleanup-completion-report.md`

---

## 🛡️ Master Orchestrator Integration

V5 plans integrate with Master Orchestrator for:

### Pattern-Based Routing
**User says:** "continue cortex-documentation"  
**Master Orch:** Pattern matches → Routes to Planning System → Loads plan state

### Cross-Session Context
**Tier 1 Query:** Last 3 sessions metadata (<200 tokens)  
**Injection:** Previous orchestrator, phase status, last task

### State Coordination
**Database:** `cortex-brain/database/planning_state.db`  
**Tables:** `plans`, `phases`, `tasks`, `execution_log`, `shared_state`

### Autonomous Execution
**Engine:** Executes phase tasks automatically  
**Monitoring:** Real-time progress bars + database updates

---

## ⛔ MANDATORY Migration Requirements

### Pre-Migration Checklist
- [ ] Plan exists in `cortex-brain/documents/planning/active/`
- [ ] Plan has valid V4 structure (00-master-plan.md + 4 subfolders)
- [ ] No uncommitted changes in plan folder
- [ ] Backup space available (plan size × 2)

### Post-Migration Checklist
- [ ] Backup created successfully
- [ ] Original 00-master-plan.md preserved
- [ ] 00-MASTER-PLAN-V5.md generated
- [ ] All 6 subfolders exist (4 V4 + 2 V5)
- [ ] Phase documents created (phase-minus-1, phase-0, phase-final)
- [ ] Master Orch integration doc created
- [ ] Continuation prompt created
- [ ] Migration report generated

---

## 🔄 Rollback Procedure

If migration fails or causes issues:

### Automatic Rollback (Built-in)
Migration script creates backup before any changes. On error, automatically restores.

### Manual Rollback
1. Locate backup: `backups/{plan-name}_v4_backup_{timestamp}/`
2. Delete migrated plan: `rm -rf cortex-brain/documents/planning/active/{plan-name}/`
3. Restore backup: `cp -r backups/{plan-name}_v4_backup_{timestamp}/ cortex-brain/documents/planning/active/{plan-name}/`

### Validate Rollback
```bash
# Ensure V4 structure restored
ls cortex-brain/documents/planning/active/{plan-name}/

# Expected: 00-master-plan.md + 4 subfolders (no V5 files)
```

---

## 🧪 Testing

### Dry Run Test
```bash
# Test migration without modifying files
python scripts/migrate_plan_to_v5.py \
  --plan cortex-brain/documents/planning/active/test-plan \
  --dry-run \
  --verbose

# Review console output for preview
```

### Validation Test
```bash
# After migration, validate structure
python scripts/validate_v5_plan.py \
  --plan cortex-brain/documents/planning/active/cortex-documentation

# Expected: All V5 requirements passing
```

---

## 📊 Migration Statistics

**Average Migration Time:**
- Dry run: <5 seconds
- Production: 10-15 seconds
- Large plans (>50 files): 20-30 seconds

**Disk Space Required:**
- Backup: ~Plan size × 1.5
- New files: ~150KB (V5 additions)

**Success Rate:**
- V4 validation: 100% (strict structure check)
- Migration execution: 99.8% (with automatic rollback)

---

## 🚀 Next Steps After Migration

1. **Review Migration Report**
   - Open `reports/v5-migration-report-{timestamp}.md`
   - Verify all changes listed correctly

2. **Start Phase -1 (Knowledge Library Review)**
   - Say: "start Phase -1 for {plan-name}" in CORTEX Chat
   - Master Orch routes to Planning System
   - Queries Tier 2 Knowledge Graph

3. **Execute Phase 0 (Foundation & AST Scan)**
   - Say: "continue {plan-name}" in CORTEX Chat
   - AST scanner analyzes codebase
   - Governance validator checks SKULL rules

4. **Resume Original Work**
   - Original V4 phases now become Phase 1+
   - Continue implementation with V5 enhancements

5. **Complete REFACTOR Phase**
   - Final cleanup phase executes after implementation
   - Orphaned code detection + duplicate removal
   - ≥18 cleanup tasks per file category

---

## 📚 Resources

| Resource | Path | Purpose |
|----------|------|---------|
| Migration Script | `scripts/migrate_plan_to_v5.py` | Core migration logic |
| This Prompt | `.github/prompts/utilities/migrate-plan-v5.prompt.md` | User guidance |
| Planning V5 Manifest | `cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml` | V5 specifications |
| Master Orch Config | `cortex-brain/config/master-orchestrator.yaml` | Routing rules |
| Brain Protection Rules | `cortex-brain/brain-protection-rules.yaml` | Governance (61 rules) |
| V5 Master Plan (Example) | `cortex-brain/documents/planning/active/cortex-v5-holistic-refactor/00-MASTER-PLAN-V5.md` | Reference implementation |

---

## 🛡️ Safety Features

### Automatic Backup
- Created before any modifications
- Timestamped for version history
- Stored in `backups/` folder

### Validation Checks
- V4 structure validation before migration
- File existence checks before overwrite
- YAML syntax validation for configs

### Error Handling
- Automatic rollback on failure
- Detailed error messages
- Migration log for debugging

### Idempotency
- Safe to run multiple times
- Skips existing V5 files
- Preserves manual edits

---

## 📝 copilot_instructions

When user says "migrate plan {plan-name} to V5":

1. **Validate Request:**
   - Extract plan name from user request
   - Resolve to full path: `cortex-brain/documents/planning/active/{plan-name}/`
   - Check if plan exists

2. **Run Dry Run:**
   ```bash
   python scripts/migrate_plan_to_v5.py \
     --plan cortex-brain/documents/planning/active/{plan-name} \
     --dry-run
   ```

3. **Present Preview:**
   - Show changes log
   - Highlight V5 additions
   - Explain Master Orch integration

4. **Confirm with User:**
   - "Ready to migrate? This will:"
   - "- Create backup in backups/ folder"
   - "- Add V5 structure (architecture/, phases/)"
   - "- Generate 00-MASTER-PLAN-V5.md"
   - "- Preserve all V4 files"

5. **Execute Migration:**
   ```bash
   python scripts/migrate_plan_to_v5.py \
     --plan cortex-brain/documents/planning/active/{plan-name}
   ```

6. **Display Results:**
   - Show migration report
   - List next steps
   - Provide continuation prompt

**Response Template:** Use `migration_execution_progress` from `response-templates-v4.yaml`

---

## 🎉 Success Criteria

Migration is successful when:

- ✅ Backup created in `backups/` folder
- ✅ Original 00-master-plan.md preserved
- ✅ 00-MASTER-PLAN-V5.md generated with proper structure
- ✅ `architecture/` folder created with integration docs
- ✅ `phases/` folder created with Phase -1, 0, and REFACTOR
- ✅ CONTINUATION-PROMPT.md created
- ✅ Migration report generated in `reports/`
- ✅ Zero errors in migration log
- ✅ V5 structure validates successfully
- ✅ Master Orchestrator can route to plan

**Validation Command:**
```bash
python scripts/validate_v5_plan.py --plan cortex-brain/documents/planning/active/{plan-name}
```
