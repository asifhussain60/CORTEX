<!--
CORTEX UPGRADE PROMPT - Packaged for Deployment

This file is packaged with CORTEX deployments to enable safe, zero-loss upgrades.
Loaded by GitHub Copilot to guide upgrade operations with brain preservation.

Version: 1.0.0
Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
-->

# 🚀 CORTEX Upgrade Assistant

**Purpose:** Safe upgrade path preserving brain state, knowledge graphs, and user data

**Version:** 1.0.0 | **Status:** ✅ PRODUCTION

---

## 🎯 Upgrade Philosophy

**ZERO-LOSS GUARANTEE:** No brain data, knowledge graphs, or user work is lost during upgrades.

**Brain Preservation:** All learned patterns, working memory, and user context remain intact.

**Selective Deployment:** Only user-facing features and capabilities are deployed to production.

---

## 📋 Upgrade Workflow (9 Phases)

### Phase 1: Pre-Upgrade Health Check
**Purpose:** Verify system integrity before any changes

**Actions:**
1. Run system healthcheck (validate all brain tiers operational)
2. Check for uncommitted changes (warn if dirty workspace)
3. Validate current version (record baseline)
4. Check disk space (ensure sufficient for backup + new version)
5. Verify network connectivity (for git pull)

**Exit Criteria:**
- ✅ All brain tiers responding
- ✅ No critical errors detected
- ✅ Sufficient disk space available
- ⚠️ Warn on uncommitted changes (user decision to proceed)

---

### Phase 2: Brain Data Backup
**Purpose:** Create immutable backup of all brain state

**Protected Data:**
- `cortex-brain/tier1/working_memory.db` - Conversation history (70-conv FIFO)
- `cortex-brain/tier2/knowledge-graph.yaml` - Learned patterns, relationships
- `cortex-brain/tier2/patterns/` - Pattern storage, decay metrics
- `cortex-brain/tier3/*.db` - Development context, hotspots, metrics
- `cortex-brain/conversation-history.db` - Full conversation archive
- `cortex-brain/documents/` - User-generated documents, planning
- `cortex-brain/config/` - User-specific configurations
- `cortex.config.json` - Machine-specific paths

**Backup Strategy:**
- Timestamped backup directory: `.upgrades/backups/YYYYMMDD_HHMMSS/`
- Backup metadata with file checksums (SHA-256)
- Verification pass (read all backed up files)
- Backup manifest JSON with rollback instructions

**Exit Criteria:**
- ✅ All brain data backed up
- ✅ Backup verified (files readable, checksums match)
- ✅ Backup manifest created
- ✅ Rollback instructions generated

---

### Phase 3: Version Check & Pull
**Purpose:** Fetch latest CORTEX enhancements

**Actions:**
1. Check remote version (`git fetch --tags`)
2. Compare local vs remote version
3. Display changelog/release notes (if available)
4. User confirmation prompt (show what will change)
5. Git pull with merge strategy (preserve local changes)

**Merge Strategy:**
- **NEVER overwrite:** Brain data files (tier1/tier2/tier3 databases)
- **SAFE overwrite:** Core CORTEX files (src/, scripts/, .github/prompts/)
- **SMART merge:** Config files (preserve user settings, add new defaults)
- **CONFLICT resolution:** Manual review required for conflicts

**Exit Criteria:**
- ✅ Remote version fetched
- ✅ Git pull successful (or no updates available)
- ✅ No merge conflicts (or conflicts resolved)
- ✅ Working directory clean

---

### Phase 4: Dependency Update
**Purpose:** Install new/updated Python packages

**Actions:**
1. Compare `requirements.txt` (old vs new)
2. Install new dependencies (`pip install -r requirements.txt --upgrade`)
3. Uninstall removed dependencies (from diff)
4. Validate all imports (import smoke test)
5. Check for breaking changes in major version bumps

**Exit Criteria:**
- ✅ All dependencies installed
- ✅ No import errors
- ✅ No conflicting package versions

---

### Phase 5: Database Migrations
**Purpose:** Migrate brain databases to new schema (if needed)

**Actions:**
1. Detect schema changes (compare DB versions)
2. Run migrations for each brain tier:
   - Tier 1: `working_memory.db` schema updates
   - Tier 2: `knowledge-graph.yaml` format migrations
   - Tier 3: `dev_context.db` schema updates
3. Validate data integrity post-migration
4. Preserve all existing data (no deletion)

**Migration Safety:**
- Pre-migration backup (separate from Phase 2)
- Rollback on first error
- Data validation after each migration
- No destructive operations (only ADD/ALTER, never DROP)

**Exit Criteria:**
- ✅ All migrations completed successfully
- ✅ Data integrity verified
- ✅ No data loss detected

---

### Phase 6: Feature Validation (User-Facing Only)
**Purpose:** Verify all user-facing features are operational

**User-Facing Features:**
1. **Planning System** - `plan [feature]` command functional
2. **TDD Mastery** - `start tdd` command functional
3. **Code Sanitization** - `sanitize [directory]` command functional
4. **ADO Operations** - `plan ado` command functional
5. **System Maintenance** - `system maintenance` command functional
6. **Help System** - `help` command functional
7. **Architectural Review** - `review` command functional
8. **Response Templates** - Template rendering working

**Validation Tests:**
- Execute each command with dry-run mode
- Verify orchestrators load successfully
- Check response template rendering
- Validate brain tier accessibility

**Exit Criteria:**
- ✅ All user-facing commands operational
- ✅ No orchestrator load failures
- ✅ Response templates rendering correctly
- ⚠️ Internal modules NOT validated (not user-facing)

---

### Phase 7: Post-Upgrade Health Check
**Purpose:** Verify system integrity after upgrade

**Actions:**
1. Re-run system healthcheck (compare to Phase 1 baseline)
2. Verify brain tiers operational (Tier 0/1/2/3)
3. Check for new errors/warnings in logs
4. Validate knowledge graph integrity
5. Test working memory operations

**Exit Criteria:**
- ✅ System health equal or better than pre-upgrade
- ✅ All brain tiers operational
- ✅ No new critical errors
- ✅ Knowledge graph accessible

---

### Phase 8: Prompt & Config Sync
**Purpose:** Update Copilot prompts with latest enhancements

**Actions:**
1. Refresh `.github/prompts/CORTEX.prompt.md` (if updated)
2. Refresh `.github/copilot-instructions.md` (if updated)
3. Sync `cortex-brain/response-templates-v4.yaml` (preserve custom templates)
4. Update operation registry (`cortex-operations.yaml`)

**Smart Merge Strategy:**
- **System prompts:** Overwrite with latest (user doesn't customize these)
- **Response templates:** Merge (preserve user custom templates)
- **Operations registry:** Add new operations, preserve user customizations

**Exit Criteria:**
- ✅ Latest prompts loaded
- ✅ Response templates merged
- ✅ Operation registry updated

---

### Phase 9: Upgrade Report & Cleanup
**Purpose:** Document upgrade and cleanup temporary files

**Report Includes:**
- Upgrade summary (versions, duration, outcome)
- Files changed (additions, modifications, deletions)
- Features added/enhanced
- Breaking changes (if any)
- Rollback instructions (if needed)
- Backup location and retention policy

**Cleanup:**
- Remove temporary upgrade files
- Compress backup (reduce disk usage)
- Log upgrade event to brain (Tier 3 metrics)
- Update VERSION file

**Exit Criteria:**
- ✅ Upgrade report generated
- ✅ Temporary files cleaned up
- ✅ Backup compressed and archived
- ✅ VERSION file updated

---

## 🛡️ Rollback Strategy

**When to Rollback:**
- Phase 5 (Database Migrations) fails
- Phase 6 (Feature Validation) fails critically (>50% features broken)
- Phase 7 (Post-Upgrade Health Check) shows degraded health
- User requests rollback

**Rollback Procedure:**
1. Stop all CORTEX operations
2. Restore brain data from Phase 2 backup
3. Git reset to previous version (`git reset --hard <previous_tag>`)
4. Reinstall old dependencies (`pip install -r requirements.txt`)
5. Restore old prompts and configs
6. Run healthcheck to verify rollback success

**Rollback Guarantee:**
- ✅ All brain data restored to pre-upgrade state
- ✅ No data loss
- ✅ System operational at previous version

---

## 🎯 User-Facing Release Criteria

**ONLY deploy features/capabilities that are:**
1. ✅ **Invocable via Copilot Chat** - User can trigger with natural language
2. ✅ **Documented in CORTEX.prompt.md** - Listed in command reference
3. ✅ **Registered in cortex-operations.yaml** - Has `deployment_tier: user`
4. ✅ **Tested end-to-end** - Validated in Phase 6
5. ✅ **No admin-only dependencies** - Doesn't require admin access

**EXCLUDE from user deployments:**
- Internal orchestrators (`execution_method: internal`)
- Admin-only operations (`deployment_tier: admin`)
- Utility modules not directly invoked by users
- Experimental features (marked `status: experimental`)

---

## 🔧 Configuration Preservation

**Never Overwrite:**
- `cortex.config.json` - Machine-specific paths
- `cortex-brain/config/` - User preferences
- `cortex-brain/user-dictionary.yaml` - Custom terminology
- `.cortex/workspace-id.txt` - Workspace identity

**Safe to Overwrite:**
- `src/` - CORTEX core code
- `scripts/` - Utility scripts
- `.github/workflows/` - CI/CD pipelines
- `tests/` - Test suite

**Smart Merge:**
- `cortex-operations.yaml` - Add new operations, preserve custom
- `requirements.txt` - Add new deps, preserve custom
- `.gitignore` - Merge ignore patterns

---

## 📊 Success Metrics

**Upgrade Success:**
- ✅ Zero data loss (all brain data intact)
- ✅ All user-facing features operational
- ✅ System health equal or better than pre-upgrade
- ✅ No rollback required

**Upgrade Failure:**
- ❌ Data loss detected (trigger immediate rollback)
- ❌ >50% user-facing features broken (trigger rollback)
- ❌ Critical brain tier failure (trigger rollback)
- ❌ Schema migration failed (trigger rollback)

---

## 🤝 User Experience

**During Upgrade:**
- Show progress spinner with phase names
- Estimated time remaining (based on prior upgrades)
- Real-time status updates
- Pause/abort option (with safe exit)

**After Upgrade:**
- Show changelog (What's New)
- Highlight new features
- Show rollback instructions (if needed)
- Prompt to test new features

**Upgrade Frequency:**
- Check for updates: Weekly (automatic, non-intrusive)
- Prompt to upgrade: Only for feature releases (not patches)
- Auto-upgrade: Never (user consent always required)

---

## 🚨 Emergency Recovery

**If Upgrade Fails Catastrophically:**

1. **Immediate Actions:**
   - Stop all operations
   - Locate backup: `.upgrades/backups/<latest>/`
   - Read backup manifest: `backup_metadata.json`

2. **Manual Rollback:**
   ```bash
   # Navigate to CORTEX root
   cd /path/to/CORTEX
   
   # Restore brain data
   python -m src.operations.modules.upgrade.upgrade_utility --restore <backup_id>
   
   # Reset git
   git reset --hard <previous_version_tag>
   
   # Reinstall dependencies
   pip install -r requirements.txt
   
   # Verify health
   python -m src.operations.healthcheck
   ```

3. **Verify Recovery:**
   - Run healthcheck
   - Test core commands (help, healthcheck)
   - Verify brain data accessible

4. **Report Issue:**
   - Create GitHub issue with upgrade logs
   - Attach backup manifest
   - Describe failure point

---

## 🧠 Brain Protection (SKULL) Compliance

**Upgrade MUST respect Brain Protection Rules:**

1. **TDD_ENFORCEMENT:** New features must have tests (validated in Phase 6)
2. **HOLISTIC_CODE_DISCOVERY_ENFORCEMENT:** Search before adding duplicates
3. **REFACTOR_CODE_CLEANUP_ENFORCEMENT:** Remove orphaned code during upgrade
4. **GIT_ISOLATION_ENFORCEMENT:** CORTEX code never in user repos
5. **TEST_LOCATION_SEPARATION:** Tests in `tests/`, not user workspaces

**Upgrade-Specific Rules:**
- **BRAIN_DATA_PRESERVATION:** Never overwrite brain databases
- **KNOWLEDGE_GRAPH_INTEGRITY:** Validate graph after migrations
- **WORKING_MEMORY_CONTINUITY:** Preserve conversation history
- **CONFIG_PERSISTENCE:** User configs survive upgrades

---

## 📝 Upgrade Command Examples

**Check for updates (non-destructive):**
```
upgrade cortex
check for updates
is there a new version
```

**Upgrade to latest version:**
```
upgrade cortex
upgrade to latest version
pull latest changes
```

**Rollback to previous version:**
```
rollback upgrade
restore backup <backup_id>
undo upgrade
```

**View upgrade history:**
```
show upgrade history
list backups
upgrade status
```

---

## 🎓 Best Practices

**Before Upgrading:**
1. Commit/push any uncommitted work in user repos
2. Note current version (for rollback reference)
3. Ensure backups are up to date
4. Close any active CORTEX operations

**After Upgrading:**
1. Test new features (guided by What's New)
2. Review changelog for breaking changes
3. Update any custom integrations (if affected)
4. Report issues promptly

**Backup Retention:**
- Keep last 5 backups (automatic)
- Manual backups never auto-deleted
- Compress backups older than 30 days

---

**Anti-Bloat:** This file MUST stay under 600 lines. Focus on upgrade workflow, brain preservation, and user safety.

**Version:** This is v1.0.0 - will evolve with CORTEX upgrade system.
