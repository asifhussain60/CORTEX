# 🚀 CORTEX Upgrade System - Pull & Wire Latest Enhancements

**Version:** 2.0.0 | **Status:** ✅ PRODUCTION | **Type:** Automated Upgrade Orchestrator  
**Author:** Asif Hussain | **Last Updated:** January 6, 2026  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🎯 Purpose

Automatically pull the latest CORTEX v5.0 enhancements from the remote branch and wire them into the local installation. This system ensures seamless upgrades across development machines with minimal user intervention.

---

## 🏗️ Architecture

```
Pull → Analyze → Wire → Rebuild → Document → Verify → Report
  ↓        ↓       ↓        ↓          ↓        ↓        ↓
 Git    Changes  Setup   Prompts    Docs    Tests   Summary
```

**Execution Mode:** Python-based autonomous orchestrator invoked via terminal

---

## 🔀 Intent Routing

**Pattern:** `^(upgrade cortex|cortex upgrade|pull enhancements|sync enhancements)`  
**Priority:** 15 (High - System Maintenance)  
**Confidence:** 1.0  
**Mode:** Autonomous

**Invocation:**
```bash
python3 -m src.main "upgrade cortex" --format markdown
```

---

## 📋 Upgrade Phases

### Phase 1: Pre-Flight Validation
**Duration:** 30 seconds  
**Goal:** Ensure system is ready for upgrade

**Checks:**
- Git repository status (clean working directory)
- Current branch = CORTEX-5.0
- Python 3.11+ installed
- Virtual environment active (if used)
- Network connectivity to remote
- Disk space available (minimum 500MB)

**Artifacts:**
- `cortex-brain/documents/upgrades/{timestamp}/pre-flight-report.json`

---

### Phase 2: Remote Analysis
**Duration:** 1 minute  
**Goal:** Analyze what changed in remote branch

**Actions:**
1. Fetch latest from origin/CORTEX-5.0
2. Compare local HEAD with remote HEAD
3. Generate diff summary (files changed, additions, deletions)
4. Identify affected subsystems:
   - Orchestrators (src/orchestrators/)
   - Prompts (.github/prompts/)
   - Documentation (cortex-brain/documents/)
   - Audit Logging (src/logging/)
   - Architecture (src/core/, src/entry_point/)
   - Tests (tests/)

**Artifacts:**
- `cortex-brain/documents/upgrades/{timestamp}/remote-analysis.json`
- `cortex-brain/documents/upgrades/{timestamp}/diff-summary.md`

---

### Phase 3: Backup & Rollback Preparation
**Duration:** 1 minute  
**Goal:** Create safety net for rollback

**Actions:**
1. Create timestamped backup directory
2. Backup critical files:
   - `cortex.config.json`
   - `.github/prompts/CORTEX.prompt.md`
   - `.github/copilot-instructions.md`
   - `cortex-brain/config/master-orchestrator.yaml`
   - Active plans in `cortex-brain/documents/planning/active/` (full structure)
   - Level 1 HTML pages in `docs/` (architecture, orchestrators, features, etc.)
   - Plan templates and standards from `cortex-brain/documents/planning/active/html-glassmorphism-alignment/`
3. Record current commit SHA
4. Create rollback script with plan structure restoration
5. Generate backup manifest:
   - List of backed up files with checksums
   - Plan structure snapshots (folder hierarchy)
   - Documentation site state (HTML/CSS versions)

**Artifacts:**
- `backups/upgrade-{timestamp}/`
- `backups/upgrade-{timestamp}/rollback.sh`
- `backups/upgrade-{timestamp}/rollback.ps1`
- `backups/upgrade-{timestamp}/manifest.json`

---

### Phase 4: Git Pull & Merge
**Duration:** 1 minute  
**Goal:** Pull latest changes from remote

**Actions:**
1. Pull with rebase strategy: `git pull --rebase origin CORTEX-5.0`
2. If conflicts detected:
   - Auto-resolve safe conflicts (prefer remote for prompts/docs)
   - Flag manual conflicts for user review
   - Pause execution if manual intervention needed
3. Verify pull success

**Artifacts:**
- `cortex-brain/documents/upgrades/{timestamp}/git-pull-log.txt`
- `cortex-brain/documents/upgrades/{timestamp}/conflicts.json` (if any)

---

### Phase 5: Dependency Synchronization
**Duration:** 2 minutes  
**Goal:** Update Python packages to match remote requirements

**Actions:**
1. Compare `requirements.txt` (old vs new)
2. Install new dependencies: `pip install -r requirements.txt --upgrade`
3. Verify critical packages:
   - pytest
   - pydantic
   - PyYAML
   - Jinja2
   - watchdog
   - requests
4. Test imports for audit logger and orchestrators

**Artifacts:**
- `cortex-brain/documents/upgrades/{timestamp}/dependency-changes.json`
- `cortex-brain/documents/upgrades/{timestamp}/pip-install-log.txt`

---

### Phase 6: Orchestrator Wiring Analysis
**Duration:** 2 minutes  
**Goal:** Detect new/modified orchestrators and update registration

**Actions:**
1. Scan `src/orchestrators/` for new orchestrator files
2. Scan `cortex-brain/manifests/orchestrators/` for new manifests
3. Compare with `cortex-brain/config/master-orchestrator.yaml` routing table
4. Identify:
   - New orchestrators to register
   - Modified patterns/priorities
   - New child orchestrator registrations
   - Audit logger integration points
5. Auto-update routing table (with backup)
6. Regenerate orchestrator documentation

**Artifacts:**
- `cortex-brain/documents/upgrades/{timestamp}/orchestrator-changes.json`
- `cortex-brain/config/master-orchestrator.yaml` (updated)
- `cortex-brain/documents/orchestrators-quick-ref.md` (regenerated)

---

### Phase 7: Prompt Rebuilding
**Duration:** 1 minute  
**Goal:** Rebuild CORTEX.prompt.md and copilot-instructions.md

**Actions:**
1. Detect changes in routing patterns
2. Rebuild CORTEX.prompt.md routing table from master-orchestrator.yaml
3. Update copilot-instructions.md with new orchestrators
4. Validate prompt syntax (no broken links)
5. Verify all file references exist

**Artifacts:**
- `.github/prompts/CORTEX.prompt.md` (updated)
- `.github/copilot-instructions.md` (updated)
- `cortex-brain/documents/upgrades/{timestamp}/prompt-changes.md`

---

### Phase 7.5: Plan Structure Validation & Upgrade
**Duration:** 2 minutes  
**Goal:** Validate active plans against latest structure requirements and upgrade/archive as needed

**Actions:**
1. Scan active plans directory:
   - `cortex-brain/documents/planning/active/`
   - Identify all plan folders and master plan files
2. Validate plan structure:
   - **5-Subfolder Structure Required:**
     - `analysis/` - Deep analysis and investigation reports
     - `artifacts/` - Generated artifacts
     - `context/` - Context discovery documents (discovery.md, architecture-analysis.md)
     - `reports/` - Progress reports and validation reports
     - `tracking/` - State tracking (progress-tracker.json, CONTINUATION-PROMPT.md)
   - **Master Plan File Requirements:**
     - Filename pattern: `00-{plan-name}.md` (meaningful name, max 22 chars, kebab-case)
     - Must include: metadata block, phases, tasks, DoR/DoD sections
     - Filename governance: 10-45 characters (excluding extension)
   - **README.md Required:** Quick start guide in plan root
3. Detect invalid plans:
   - Missing subfolder structure (old 4-folder layout)
   - Root-level markdown files (not in `00-{name}.md` format)
   - Excessively long filenames (>45 chars)
   - Missing context discovery documents
   - No progress tracker or continuation prompt
4. Upgrade valid plans:
   - Create missing subfolders (add `context/` if absent)
   - Rename master plan to `00-{name}.md` format (preserve content)
   - Generate missing README.md from plan metadata
   - Create `context/discovery.md` and `context/architecture-analysis.md` stubs
   - Initialize `tracking/progress-tracker.json` if missing
5. Archive invalid plans:
   - Move to `cortex-brain/archives/plans/invalid-{timestamp}/`
   - Create `ARCHIVE-REASON.md` explaining why archived:
     - Non-compliant structure
     - Missing critical components
     - Obsolete format (pre-v5.0)
   - Preserve original for reference
6. Generate upgrade report:
   - Plans validated (compliant vs non-compliant)
   - Plans upgraded (structure fixes applied)
   - Plans archived (moved with reasons)
   - Recommendations for manual review

**Plan Validation Schema:**
```yaml
required_structure:
  subfolders:
    - analysis
    - artifacts
    - context
    - reports
    - tracking
  master_plan:
    pattern: "^00-[a-z0-9-]{10,22}\\.md$"
    max_chars: 22
  readme:
    required: true
    location: "plan-root/README.md"
  context_files:
    - "context/discovery.md"
    - "context/architecture-analysis.md"
  tracking_files:
    - "tracking/progress-tracker.json"
    - "tracking/CONTINUATION-PROMPT.md"

filename_governance:
  min_length: 10
  max_length: 45
  format: "kebab-case"
  pattern: "{TYPE}-{ID}-{SHORT_TITLE}"
```

**Artifacts:**
- `cortex-brain/documents/upgrades/{timestamp}/plan-validation-report.json`
- `cortex-brain/documents/upgrades/{timestamp}/plan-upgrade-log.md`
- `cortex-brain/documents/upgrades/{timestamp}/archived-plans-manifest.json`
- `cortex-brain/archives/plans/invalid-{timestamp}/` (archived invalid plans)

---

### Phase 8: Documentation Site Regeneration
**Duration:** 3 minutes  
**Goal:** Update Level 0, 1, 2 documentation for architecture changes and ensure Level 1 page uniqueness

**Actions:**
1. Run architecture change detection:
   - Scan src/ for new classes, functions, modules
   - Detect orchestrator architecture changes
   - Identify new middleware/plugins
   - Map audit logger integration points
2. Regenerate documentation:
   - **Level 0** (Overview): `cortex-brain/documents/CORTEX-README.md`
   - **Level 1** (Architecture): `cortex-brain/documents/architecture/CORTEX-ARCHITECTURE-CONTRACT.md`
   - **Level 2** (Technical): 
     - `cortex-brain/documents/orchestrators-quick-ref.md`
     - `cortex-brain/documents/cortex-architecture-quick-ref.md`
     - `cortex-brain/documents/orchestrators/master-child-pattern.md`
     - `cortex-brain/documents/orchestrators/audit-logging-integration.md`
3. **Level 1 Page Uniqueness Validation:**
   - Analyze all Level 1 pages: architecture, orchestrators, features, getting-started, knowledge, story, sts, toolkit-manager, token-optimization
   - **Uniqueness Criteria:**
     - Content focus: Architecture = HOW BUILT (structure), Orchestrators = WHAT DOES (operations)
     - Diagram types: Architecture uses D3.js force-directed/Sankey, Orchestrators uses Mermaid state/sequence
     - Sections: Each page has distinct section structure (no overlap >30%)
     - Visual differentiation: Different glassmorphism color rotation per page
   - **Validation Checks:**
     - Zero orchestrator workflow content on architecture page
     - 9+ architectural diagrams (Mermaid + D3.js) on architecture page
     - 5+ distinct architectural sections (Brain, Components, Execution, SKULL, Modules)
     - Visual overlap score <30% between pages
   - **Auto-Fix Actions:**
     - Remove orchestrator workflow content from architecture page
     - Generate missing architectural diagrams (4-tier brain, system components, execution paths)
     - Inject Mermaid/D3.js diagram placeholders
     - Apply 7-color glassmorphism rotation uniquely per page
4. Update diagrams:
   - **Architecture Page (Structural Focus):**
     - Four-Tier Brain Hierarchy (D3.js sunburst)
     - System Component Overview (D3.js force-directed)
     - Data Flow Pipeline (Mermaid flowchart)
     - Agent Coordination Protocol (Mermaid sequence)
     - Database Schema Relationships (Mermaid ER diagram)
     - Tier Access Patterns (D3.js Sankey)
     - Module Dependency Graph (D3.js chord)
     - Git Checkpoint Architecture (Mermaid flowchart)
     - SKULL Rule Enforcement Points (Mermaid deployment)
   - **Orchestrators Page (Operational Focus):**
     - Orchestrator Lifecycle (Mermaid state)
     - Category Interaction Matrix (D3.js chord)
     - TDD Cycle (Mermaid flowchart)
     - Planning Phases (Mermaid timeline)
     - Execution Pipeline (Mermaid sequence)
5. Regenerate docs site HTML:
   - Run `scripts/standardize_level1_views.py` with uniqueness enforcement
   - Generate diagrams via `scripts/generate_architecture_diagrams.py`
   - Validate against `cortex-brain/documents/planning/active/html-glassmorphism-alignment/standards/approved-panels.yaml`
   - Ensure NO inline styles (CSS classes only)

**Artifacts:**
- `cortex-brain/documents/upgrades/{timestamp}/architecture-changes.json`
- All regenerated documentation files
- `cortex-brain/documents/upgrades/{timestamp}/docs-regeneration-log.txt`

---

### Phase 9: Master/Child Orchestrator Setup
**Duration:** 2 minutes  
**Goal:** Wire child orchestrators to master orchestrators

**Actions:**
1. Scan for master orchestrator definitions (orchestrators with `master: true` in manifest)
2. Identify child orchestrator registrations (orchestrators with `parent: <master_id>` in manifest)
3. Build orchestrator hierarchy map
4. Create plugin registry entries for child orchestrators:
   - HTML child orchestrator for TDD-Master
   - C# child orchestrator for TDD-Master
   - Documentation site child orchestrator for TDD-Master
   - Audit logging child orchestrators (event, security, performance)
5. Generate master orchestrator configuration files
6. Update master-orchestrator.yaml with child registrations

**Artifacts:**
- `cortex-brain/config/orchestrator-hierarchy.json`
- `cortex-brain/documents/orchestrators/master-child-pattern.md`
- `cortex-brain/documents/orchestrators/child-orchestrator-registry.json`
- Updated manifests with parent/child relationships

---

### Phase 10: Audit Logger Integration
**Duration:** 2 minutes  
**Goal:** Wire audit logging into all orchestrators

**Actions:**
1. Scan all orchestrators for audit logger integration
2. Inject audit logger imports if missing
3. Add lifecycle hooks for audit logging:
   - `pre_execute`: Log orchestrator start
   - `post_execute`: Log orchestrator completion
   - `on_error`: Log exceptions
   - `on_phase_complete`: Log phase milestones
4. Configure audit log routing:
   - Master orchestrator → `logs/cortex-audit/master/`
   - Child orchestrators → `logs/cortex-audit/child/<child_name>/`
   - TDD orchestrator → `logs/cortex-audit/tdd/`
   - Planning orchestrator → `logs/cortex-audit/planning/`
5. Verify audit logger health check server configuration

**Artifacts:**
- `cortex-brain/documents/upgrades/{timestamp}/audit-logger-wiring.json`
- Updated orchestrator files with audit logging
- `cortex-brain/documents/orchestrators/audit-logging-integration.md`

---

### Phase 11: Integration Testing
**Duration:** 3 minutes  
**Goal:** Verify all upgrades work end-to-end

**Tests:**
1. **Import Tests:**
   - All orchestrators import successfully
   - Audit logger imports without errors
   - No circular dependencies
2. **Routing Tests:**
   - Pattern matching works for all orchestrators
   - LLM fallback functional (if configured)
   - Priority resolution correct
3. **Orchestrator Tests:**
   - Help command: `python3 -m src.main "help"`
   - Planning orchestrator: `python3 -m src.main "plan test feature"`
   - Cleanup orchestrator: `python3 -m src.main "cleanup cache"`
   - TDD orchestrator: `python3 -m src.main "tdd validate email"`
4. **Audit Logger Tests:**
   - Logger writes to correct directories
   - Event types properly classified
   - Log rotation works
   - Health check server responds
5. **Master/Child Tests:**
   - Child orchestrators registered correctly
   - Parent orchestrator can invoke children
   - Audit logging flows through hierarchy

**Artifacts:**
- `cortex-brain/documents/upgrades/{timestamp}/test-results.json`
- `cortex-brain/documents/upgrades/{timestamp}/test-output.log`

---

### Phase 12: Feature Summary & User Guidance
**Duration:** 2 minutes  
**Goal:** Generate executive summary and user-facing guidance

**Actions:**
1. Compile feature summary:
   - New orchestrators added
   - Enhanced orchestrators
   - New master/child patterns available
   - Audit logging improvements
   - Architecture changes
   - Documentation updates
   - Plan structure validation (5-subfolder standard)
   - Level 1 page uniqueness improvements
   - Diagram generation (Mermaid + D3.js)
2. Generate guidance documents:
   - Quick start for new features
   - Migration guide for existing workflows
   - Master/child orchestrator tutorial
   - Audit log viewing guide
   - Plan structure migration guide (4-folder → 5-folder)
   - Level 1 documentation standards guide
3. Create change visualization:
   - Before/after architecture diagram
   - Feature comparison matrix
   - Breaking changes (if any)
   - Plan structure comparison (old vs new)
   - Level 1 page uniqueness matrix
4. **Automated Improvement Recommendations:**
   - **Diagram Generation Script:** If missing architectural diagrams detected, auto-generate via `scripts/generate_architecture_diagrams.py`
   - **Plan Upgrade Script:** If non-compliant plans found, offer to run `scripts/upgrade_plan_structures.py --auto-migrate`
   - **Uniqueness Script:** If Level 1 overlap >30%, run `scripts/standardize_level1_views.py --enforce-uniqueness`
   - **Next Steps Prompt:** Display actionable commands user can run immediately:
     ```bash
     # Recommended actions after upgrade:
     python3 scripts/generate_architecture_diagrams.py --target architecture
     python3 scripts/upgrade_plan_structures.py --validate-all
     python3 scripts/standardize_level1_views.py --check-uniqueness
     ```

**Artifacts:**
- `cortex-brain/documents/upgrades/{timestamp}/EXECUTIVE-SUMMARY.md`
- `cortex-brain/documents/upgrades/{timestamp}/NEW-FEATURES.md`
- `cortex-brain/documents/upgrades/{timestamp}/MIGRATION-GUIDE.md`
- `cortex-brain/documents/upgrades/{timestamp}/BREAKING-CHANGES.md` (if applicable)

---

## 📊 Success Criteria

### Functional
- ✅ Git pull successful with no unresolved conflicts
- ✅ All dependencies installed without errors
- ✅ All orchestrators import successfully
- ✅ Routing table updated with new patterns
- ✅ Documentation regenerated and valid
- ✅ Master/child orchestrator wiring complete
- ✅ Audit logging integrated across all orchestrators
- ✅ Integration tests pass (>95% success rate)
- ✅ **Plan structure validation:** All active plans comply with 5-subfolder standard
- ✅ **Level 1 uniqueness:** Architecture vs Orchestrators visual overlap <30%
- ✅ **Diagram generation:** 9+ architectural diagrams deployed

### Quality
- ✅ Zero breaking changes to user workflows (unless documented)
- ✅ Backward compatibility maintained for existing plans
- ✅ Performance not degraded (within 10% of baseline)
- ✅ Documentation clarity score >90% (readability metrics)
- ✅ **Plan compliance rate:** >95% of active plans pass validation
- ✅ **Filename governance:** All new files comply with 10-45 char limit
- ✅ **Level 1 content differentiation:** Each page has unique focus (structure vs operations vs features)

### User Experience
- ✅ Executive summary clear and actionable (<500 words)
- ✅ Migration guide provides step-by-step instructions
- ✅ New features demonstrated with examples
- ✅ Rollback instructions clear and tested

---

## 🔄 Rollback Protocol

If upgrade fails at any phase:

```bash
# macOS/Linux
bash backups/upgrade-{timestamp}/rollback.sh

# Windows
powershell -ExecutionPolicy Bypass -File backups/upgrade-{timestamp}/rollback.ps1
```

**Rollback actions:**
1. Git reset to pre-upgrade commit: `git reset --hard {commit_sha}`
2. Restore backed up config files
3. Reinstall old dependencies (from backup requirements.txt)
4. Restore old prompts and documentation
5. **Restore plan structures:** Move archived plans back to active directory (if upgrade modified structure)
6. **Restore Level 1 pages:** Revert docs site HTML to backup versions
7. Verify system functional with health check

---

## 🛡️ Safety Features

### Atomic Operations
- Each phase is transactional (succeeds completely or rolls back)
- No partial state left behind

### Conflict Resolution
- **Safe conflicts:** Auto-resolve using smart merge strategies
- **Unsafe conflicts:** Pause and request user input
- **Conflict types:**
  - Prompts/Docs → Prefer remote (upstream improvements)
  - Config files → Preserve local unless remote has new fields
  - Active plans → Never auto-merge, always manual review

### Data Protection
- Active plans backed up before any changes
- User configurations preserved
- Custom orchestrators (outside src/) untouched
- Audit logs retained (never deleted)

---

## 📁 Output Structure

```
cortex-brain/documents/upgrades/{timestamp}/
├── 00-upgrade-manifest.yaml           # Full upgrade execution plan
├── 01-pre-flight-report.json          # Pre-upgrade validation results
├── 02-remote-analysis.json            # Remote changes analysis
├── 03-diff-summary.md                 # Human-readable diff summary
├── 04-git-pull-log.txt                # Git pull output
├── 05-conflicts.json                  # Merge conflicts (if any)
├── 06-dependency-changes.json         # Package updates
├── 07-pip-install-log.txt             # Pip install output
├── 07.5-plan-validation-report.json   # 🆕 Plan structure validation results
├── 07.5-plan-upgrade-log.md           # 🆕 Plan upgrade actions taken
├── 07.5-archived-plans-manifest.json  # 🆕 Invalid plans archived
├── 08-orchestrator-changes.json       # Orchestrator additions/modifications
├── 09-prompt-changes.md               # Prompt file updates
├── 10-architecture-changes.json       # Architecture modifications
├── 11-docs-regeneration-log.txt       # Documentation build log
├── 11.5-level1-uniqueness-report.json # 🆕 Level 1 page differentiation analysis
├── 11.5-diagram-generation-log.txt    # 🆕 Architectural diagram generation
├── 12-audit-logger-wiring.json        # Audit logger integration details
├── 13-test-results.json               # Integration test results
├── 14-test-output.log                 # Detailed test output
├── EXECUTIVE-SUMMARY.md               # ⭐ User-facing summary (read this first)
├── NEW-FEATURES.md                    # New capabilities added
├── MIGRATION-GUIDE.md                 # How to use new features
├── PLAN-MIGRATION-GUIDE.md            # 🆕 4-folder → 5-folder plan migration
├── LEVEL1-STANDARDS-GUIDE.md          # 🆕 Level 1 documentation standards
└── BREAKING-CHANGES.md                # Breaking changes (if any)

backups/upgrade-{timestamp}/
├── manifest.json                      # Backup metadata
├── cortex.config.json                 # Backed up config
├── master-orchestrator.yaml           # Backed up routing
├── CORTEX.prompt.md                   # Backed up prompt
├── copilot-instructions.md            # Backed up instructions
├── active-plans/                      # Backed up active plans
├── rollback.sh                        # macOS/Linux rollback script
└── rollback.ps1                       # Windows rollback script
```

---

## 🤖 Automated Action Scripts

The upgrade orchestrator triggers these utility scripts automatically:

### Plan Structure Validation & Migration
```bash
# Validate all active plans against 5-subfolder standard
python3 scripts/validate_plan_structures.py --report-only

# Auto-migrate plans to latest structure (adds missing folders, renames master plan)
python3 scripts/upgrade_plan_structures.py --auto-migrate

# Archive invalid plans (non-compliant with v5.0 standards)
python3 scripts/upgrade_plan_structures.py --archive-invalid
```

### Level 1 Documentation Uniqueness
```bash
# Check Level 1 page overlap percentage
python3 scripts/standardize_level1_views.py --check-uniqueness

# Enforce uniqueness (remove duplicate content, regenerate sections)
python3 scripts/standardize_level1_views.py --enforce-uniqueness

# Validate glassmorphism theme consistency (7-color palette)
python3 scripts/standardize_level1_views.py --validate-theme
```

### Architectural Diagram Generation
```bash
# Generate all architectural diagrams (Mermaid + D3.js)
python3 scripts/generate_architecture_diagrams.py --target all

# Generate only architecture page diagrams (9 structural diagrams)
python3 scripts/generate_architecture_diagrams.py --target architecture

# Generate only orchestrators page diagrams (5 operational diagrams)
python3 scripts/generate_architecture_diagrams.py --target orchestrators
```

### Orchestrator Registration Check
```bash
# Verify all orchestrators registered in master-orchestrator.yaml
python3 scripts/validate_orchestrator_registry.py

# Auto-register new orchestrators (scans src/orchestrators/)
python3 scripts/regenerate_routing_table.py --auto-register
```

### Filename Governance Validation
```bash
# Check all files for filename length compliance (10-45 chars)
python3 scripts/validate_filename_governance.py --strict

# Suggest shorter names for files exceeding 45 chars
python3 scripts/validate_filename_governance.py --suggest-fixes

# Auto-rename files to comply with governance (with backup)
python3 scripts/validate_filename_governance.py --auto-fix --backup
```

**Triggered Automatically During Upgrade:**
- Phase 3 (Backup): All backup operations executed before any modifications
- Phase 7.5 (Plan Validation): `validate_plan_structures.py` + `upgrade_plan_structures.py`
- Phase 8 (Docs Regen): `standardize_level1_views.py` + `generate_architecture_diagrams.py`
- Phase 9 (Orchestrator Wiring): `regenerate_routing_table.py` + `validate_orchestrator_registry.py`
- Phase 12 (Summary): `validate_filename_governance.py` (report mode)

**Manual Invocation After Upgrade:**
User receives recommended commands in EXECUTIVE-SUMMARY.md for optional manual improvements.

---

## 🚀 Usage

### Interactive Mode (Recommended)
```bash
# Invoke upgrade orchestrator
python3 -m src.main "upgrade cortex"
```

**User experience:**
1. Pre-flight checks run automatically
2. Backup created automatically
3. Changes analyzed and displayed
4. User prompted: "Proceed with upgrade? [y/N]"
5. If yes → Executes all phases
6. If no → Exits cleanly
7. Progress shown in real-time
8. Executive summary displayed at completion

### Non-Interactive Mode (CI/CD)
```bash
# Auto-approve upgrade (use with caution)
python3 -m src.main "upgrade cortex --auto-approve" --format json
```

### Dry Run Mode
```bash
# Analyze without making changes
python3 -m src.main "upgrade cortex --dry-run"
```

**Output:**
- Shows what would change
- No git pull
- No file modifications
- Reports potential conflicts

---

## 🔍 Troubleshooting

### Issue: Merge Conflicts
**Symptoms:** Upgrade pauses with "Manual conflict resolution required"  
**Solution:**
1. Review conflicts: `cat cortex-brain/documents/upgrades/{timestamp}/conflicts.json`
2. Resolve manually: `git status` → edit files → `git add` → `git rebase --continue`
3. Resume upgrade: `python3 -m src.main "continue upgrade"`

### Issue: Dependency Installation Fails
**Symptoms:** pip install errors during Phase 5  
**Solution:**
1. Check Python version: `python3 --version` (must be 3.11+)
2. Upgrade pip: `python3 -m pip install --upgrade pip`
3. Clear pip cache: `pip cache purge`
4. Retry: `python3 -m src.main "upgrade cortex"`

### Issue: Import Errors After Upgrade
**Symptoms:** `ModuleNotFoundError` when running orchestrators  
**Solution:**
1. Verify PYTHONPATH: `echo $PYTHONPATH` (should include CORTEX root)
2. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
3. Restart terminal session (reload environment variables)
4. Test: `python3 -c "from src.orchestrators.master_orchestrator import MasterOrchestrator"`

### Issue: Orchestrator Not Found After Upgrade
**Symptoms:** "No orchestrator matched pattern" errors  
**Solution:**
1. Check routing table: `cat cortex-brain/config/master-orchestrator.yaml | grep pattern`
2. Regenerate routing: `python3 scripts/regenerate_routing_table.py`
3. Clear pattern cache: `rm -rf cortex-brain/cache/routing/*.json`
4. Test: `python3 -m src.main "help"`

### Issue: Plan Structure Validation Failures
**Symptoms:** Plans archived during upgrade, "non-compliant structure" warnings  
**Solution:**
1. Review archived plans: `cat cortex-brain/documents/upgrades/{timestamp}/archived-plans-manifest.json`
2. Check what caused archival: `cat cortex-brain/archives/plans/invalid-{timestamp}/ARCHIVE-REASON.md`
3. Manually migrate plan if needed:
   ```bash
   # Create 5-subfolder structure
   cd cortex-brain/documents/planning/active/{plan-name}
   mkdir -p analysis artifacts context reports tracking
   
   # Rename master plan
   mv {old-name}.md 00-{short-name}.md
   
   # Generate required files
   touch README.md
   touch context/discovery.md
   touch context/architecture-analysis.md
   touch tracking/progress-tracker.json
   touch tracking/CONTINUATION-PROMPT.md
   ```
4. Re-validate: `python3 scripts/validate_plan_structures.py --plan {plan-name}`

### Issue: Level 1 Page Overlap Detected
**Symptoms:** Warning: "Architecture page contains orchestrator workflow content (>30% overlap)"  
**Solution:**
1. Review overlap report: `cat cortex-brain/documents/upgrades/{timestamp}/level1-uniqueness-report.json`
2. Run uniqueness enforcement: `python3 scripts/standardize_level1_views.py --enforce-uniqueness`
3. Manually review architecture page: Remove sections like "Orchestrator Workflows", "TDD Cycle", "Planning Phases"
4. Re-validate: `python3 scripts/standardize_level1_views.py --check-uniqueness`

### Issue: Missing Architectural Diagrams
**Symptoms:** Architecture page has <9 diagrams, placeholder divs visible  
**Solution:**
1. Check diagram generation log: `cat cortex-brain/documents/upgrades/{timestamp}/diagram-generation-log.txt`
2. Regenerate diagrams: `python3 scripts/generate_architecture_diagrams.py --target architecture --force`
3. Verify Mermaid CLI installed: `mermaid --version` (if not: `npm install -g @mermaid-js/mermaid-cli`)
4. Check diagram injection: `grep -r "mermaid" docs/architecture/index.html`

### Issue: Filename Too Long Warnings
**Symptoms:** Files flagged with "exceeds 45 character limit"  
**Solution:**
1. Review violations: `python3 scripts/validate_filename_governance.py --report-only`
2. Get suggested names: `python3 scripts/validate_filename_governance.py --suggest-fixes`
3. Auto-rename with backup: `python3 scripts/validate_filename_governance.py --auto-fix --backup`
4. Verify: Check `backups/filename-renames-{timestamp}/` for backup copies

---

## 🎓 Master/Child Orchestrator Guide

### What Are Master/Child Orchestrators?

**Master Orchestrator:**
- Coordinates a domain (e.g., TDD, Planning, Cleanup)
- Routes requests to specialized child orchestrators
- Aggregates results from children
- Provides unified audit logging

**Child Orchestrator:**
- Handles specific technology/scenario (e.g., HTML testing, C# testing)
- Registered with parent master orchestrator
- Inherits audit logging from parent
- Can be dynamically added without modifying master

### Creating a Child Orchestrator

**1. Create child orchestrator file:**
```python
# src/orchestrators/tdd_html_orchestrator.py
from src.orchestrators.base.child_orchestrator import ChildOrchestrator

class TDDHTMLOrchestrator(ChildOrchestrator):
    def get_parent_id(self) -> str:
        return "tdd_master"
    
    def can_handle(self, context: Dict[str, Any]) -> bool:
        return context.get("language") == "html"
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # HTML-specific TDD logic
        return {"status": "success", "tests_created": 5}
```

**2. Create manifest:**
```yaml
# cortex-brain/manifests/orchestrators/tdd-html-child.yaml
orchestrator_id: tdd_html_child
name: "TDD HTML Child Orchestrator"
parent_id: tdd_master
version: "1.0.0"
description: "Test-Driven Development for HTML files"

capabilities:
  - "HTML syntax validation"
  - "Accessibility testing (WCAG AA)"
  - "Cross-browser compatibility checks"
  - "Performance testing (Lighthouse)"

audit_logging:
  enabled: true
  inherit_from_parent: true
  log_directory: "logs/cortex-audit/tdd/html/"

patterns:
  - "tdd.*html"
  - "test.*\\.html$"
  - "html.*test"
```

**3. Register with parent:**
```python
# src/orchestrators/tdd_master_orchestrator.py
def register_children(self):
    self.register_child("html", TDDHTMLOrchestrator())
    self.register_child("csharp", TDDCSharpOrchestrator())
    self.register_child("python", TDDPythonOrchestrator())
```

**4. Verify registration:**
```bash
python3 -m src.main "tdd generate html tests for login.html"
# Should route to TDD Master → HTML Child
```

---

## 📚 References

- **Upgrade Manifest:** `cortex-brain/manifests/orchestrators/upgrade-orchestrator.yaml`
- **Master Orchestrator Config:** `cortex-brain/config/master-orchestrator.yaml`
- **Audit Logger Docs:** `cortex-brain/documents/orchestrators/audit-logging-integration.md`
- **Architecture Contract:** `cortex-brain/documents/architecture/CORTEX-ARCHITECTURE-CONTRACT.md`

---

## 📝 Changelog

### v2.0.0 (2026-01-06)
- **🆕 Phase 7.5:** Plan structure validation & upgrade (5-subfolder standard)
- **🆕 Automated Actions:** Plan migration, Level 1 uniqueness enforcement, diagram generation
- **🆕 Filename Governance:** Validate 10-45 character filename limit
- **🆕 Level 1 Uniqueness:** Ensure architecture vs orchestrators differentiation (HOW vs WHAT)
- **🆕 Diagram Generation:** 9+ architectural diagrams (Mermaid + D3.js) for architecture page
- **🆕 Invalid Plan Archival:** Auto-detect and archive non-compliant plan structures
- **🆕 Backup Enhancement:** Include plan structures, Level 1 HTML, and documentation standards
- **🆕 Rollback Enhancement:** Restore plan structures and documentation site state
- **🆕 Troubleshooting:** Plan validation, Level 1 overlap, diagram generation, filename governance
- **Enhancement:** Phase 8 now validates Level 1 page uniqueness and auto-fixes overlap
- **Enhancement:** Phase 12 includes automated action recommendations with copy-paste commands
- **Enhancement:** Success criteria include plan compliance rate and Level 1 visual differentiation

### v1.0.0 (2026-01-06)
- Initial upgrade system implementation
- Master/child orchestrator wiring support
- Audit logger integration across all orchestrators
- Documentation site regeneration
- Cross-platform support (Windows/macOS/Linux)
- Rollback capabilities
- Dry-run mode

---

**Last Updated:** January 6, 2026  
**Maintainer:** Asif Hussain  
**Status:** Production Ready
