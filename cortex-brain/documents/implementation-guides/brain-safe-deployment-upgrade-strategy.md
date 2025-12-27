# Brain-Safe Deployment & Upgrade Strategy

**Version:** 1.0.0  
**Date:** December 27, 2025  
**Author:** Asif Hussain  
**Status:** ✅ IMPLEMENTED

---

## 🎯 Overview

CORTEX now implements a **9-phase brain-safe upgrade system** that guarantees zero data loss while deploying only user-facing features to production. This enhancement addresses the critical need for safe upgrades that preserve learned patterns, knowledge graphs, and user work.

---

## 🚀 Key Features

### 1. **cortex-upgrade.prompt.md** - Packaged Upgrade Assistant
**Location:** `.github/prompts/cortex-upgrade.prompt.md`

**Purpose:** Packaged with CORTEX deployments to guide GitHub Copilot through safe upgrade operations.

**Features:**
- 9-phase upgrade workflow documentation
- Brain data protection rules
- Rollback strategies
- User-facing feature validation criteria
- Emergency recovery procedures

**Usage:** Automatically loaded by Copilot when users invoke `upgrade cortex` command.

### 2. **UpgradeOrchestratorV2** - Brain-Safe Orchestrator
**Location:** `src/orchestrators/upgrade_orchestrator_v2.py`

**Architecture:** 9-phase workflow with rollback on failure

**Phases:**

1. **Pre-Upgrade Health Check**
   - Brain tier validation (Tier 0/1/2/3)
   - Git status check (warn on uncommitted changes)
   - Version baseline recording
   - Disk space verification
   - Network connectivity test

2. **Brain Data Backup**
   - Immutable backup of all brain state
   - Protected paths:
     - `cortex-brain/tier1/working_memory.db` (conversation history)
     - `cortex-brain/tier2/knowledge-graph.yaml` (learned patterns)
     - `cortex-brain/tier2/patterns/` (pattern storage)
     - `cortex-brain/tier3/*.db` (development context)
     - `cortex-brain/conversation-history.db` (full archive)
     - `cortex-brain/documents/` (user documents)
     - `cortex-brain/config/` (user configs)
     - `cortex.config.json` (machine-specific paths)
   - Backup verification with SHA-256 checksums
   - Timestamped backup directory: `.upgrades/backups/YYYYMMDD_HHMMSS/`

3. **Version Check & Pull**
   - Remote version detection
   - Changelog display (if available)
   - Smart git pull with merge strategy
   - **NEVER overwrite:** Brain data files
   - **SAFE overwrite:** Core CORTEX files (src/, scripts/, .github/prompts/)
   - **SMART merge:** Config files (preserve user settings)

4. **Dependency Update**
   - Compare old vs new requirements
   - Install new dependencies
   - Uninstall removed dependencies
   - Import smoke test
   - Breaking change detection

5. **Database Migrations**
   - Schema change detection
   - Per-tier migrations (Tier 1/2/3)
   - Data integrity validation
   - Rollback on first error
   - No destructive operations (only ADD/ALTER)

6. **Feature Validation (User-Facing Only)**
   - **ONLY validate user-facing features:**
     - Planning System
     - TDD Mastery
     - Code Sanitization
     - ADO Operations
     - System Maintenance
     - Help System
     - Architectural Review
   - **EXCLUDE internal modules:**
     - Orchestrators not directly invoked
     - Utility modules
     - Infrastructure components
   - Failure threshold: 50% (rollback if exceeded)

7. **Post-Upgrade Health Check**
   - Re-run brain tier validation
   - Compare to pre-upgrade baseline
   - Check for new errors/warnings
   - Knowledge graph integrity test
   - Working memory operation test

8. **Prompt & Config Sync**
   - Update Copilot prompts (CORTEX.prompt.md, cortex-upgrade.prompt.md)
   - Merge response templates (preserve custom)
   - Update operation registry

9. **Upgrade Report & Cleanup**
   - Comprehensive upgrade summary
   - Files changed report
   - Rollback instructions
   - Backup location
   - Cleanup temporary files

---

## 🛡️ Brain Protection Guarantees

**Zero-Loss Guarantee:**
- ✅ No brain data overwritten during upgrade
- ✅ All learned patterns preserved
- ✅ Knowledge graph integrity maintained
- ✅ User configs survive upgrades
- ✅ Conversation history intact

**Protected Paths (NEVER overwritten):**
```yaml
brain_protected_paths:
  - cortex-brain/tier1/working_memory.db
  - cortex-brain/tier2/knowledge-graph.yaml
  - cortex-brain/tier2/patterns/
  - cortex-brain/tier3/*.db
  - cortex-brain/conversation-history.db
  - cortex-brain/documents/
  - cortex-brain/config/
  - cortex.config.json
  - .cortex/workspace-id.txt
```

**Rollback Strategy:**
- Automatic rollback on Phase 5+ failures
- Manual rollback command available
- Backup retention: Last 5 upgrades (automatic)
- Rollback time: <60 seconds

---

## 📋 User-Facing Release Criteria

**Features MUST meet ALL criteria:**

1. ✅ **Invocable via Copilot Chat**
   - User can trigger with natural language
   - Registered in `cortex-operations.yaml`
   - Has `deployment_tier: user`

2. ✅ **Documented in CORTEX.prompt.md**
   - Listed in command reference
   - Examples provided
   - Expected behavior documented

3. ✅ **End-to-End Tested**
   - Validated in Phase 6
   - No critical failures
   - Below 50% failure threshold

4. ✅ **No Admin Dependencies**
   - Doesn't require admin access
   - Available to all users
   - No system-level operations

5. ✅ **Execution Method Classified**
   - `copilot_chat`: Interactive workflows
   - `cli_wrapper`: System operations
   - **NOT** `internal`: Infrastructure only

**EXCLUDE from user deployments:**
- Internal orchestrators (`execution_method: internal`)
- Admin-only operations (`deployment_tier: admin`)
- Utility modules not directly invoked
- Experimental features (`status: experimental`)

---

## 🔧 Implementation Details

### cortex-operations.yaml Enhancement

```yaml
upgrade:
  name: Upgrade
  description: Brain-safe CORTEX upgrade with 9-phase workflow and zero data loss guarantee
  deployment_tier: user
  execution_method: cli_wrapper
  orchestrator: src.orchestrators.upgrade_orchestrator_v2:UpgradeOrchestratorV2
  prompt_file: .github/prompts/cortex-upgrade.prompt.md
  brain_protection:
    enabled: true
    protected_paths: [...]
    zero_loss_guarantee: true
  profiles:
    standard:
      description: "Full 9-phase upgrade"
      modules:
        - upgrade_utility
        - upgrade_orchestrator_v2
    rollback:
      description: "Rollback to previous version"
      modules:
        - upgrade_utility
```

### CLI Wrapper Integration

**File:** `scripts/cli_wrappers/upgrade_wrapper.py`

**Commands:**
- `upgrade cortex` - Full 9-phase upgrade
- `upgrade cortex --check-only` - Version check without upgrade
- `upgrade cortex --rollback <backup_id>` - Rollback to backup
- `upgrade cortex --dry-run` - Preview upgrade without changes

---

## 📊 Success Metrics

**Upgrade Success:**
- ✅ Zero data loss (all brain data intact)
- ✅ All user-facing features operational (8/8)
- ✅ System health equal or better than pre-upgrade
- ✅ No rollback required
- ✅ Upgrade time: <5 minutes

**Upgrade Failure Triggers:**
- ❌ Data loss detected (immediate rollback)
- ❌ >50% user-facing features broken (rollback)
- ❌ Critical brain tier failure (rollback)
- ❌ Schema migration failed (rollback)

**Phase Success Rate (Target):**
- Phase 1: 100% (health check must pass)
- Phase 2: 100% (backup critical)
- Phase 3: 95% (network dependency)
- Phase 4: 98% (dependency conflicts possible)
- Phase 5: 99% (migrations tested)
- Phase 6: 95% (feature failures expected)
- Phase 7: 100% (health must match baseline)
- Phase 8: 90% (non-critical)
- Phase 9: 100% (report generation)

---

## 🎓 User Experience

**During Upgrade:**
```
🚀 Starting brain-safe CORTEX upgrade...
📋 Phase 1/9: Pre-Upgrade Health Check ✅
💾 Phase 2/9: Brain Data Backup ✅ (backup_20251227_143000)
🔄 Phase 3/9: Version Check & Pull ✅ (3.9.0 → 4.0.0)
📦 Phase 4/9: Dependency Update ✅
🗄️ Phase 5/9: Database Migrations ✅ (0 migrations)
✅ Phase 6/9: Feature Validation ✅ (8/8 features operational)
🏥 Phase 7/9: Post-Upgrade Health Check ✅
📝 Phase 8/9: Prompt & Config Sync ✅
📊 Phase 9/9: Upgrade Report & Cleanup ✅

🎉 Upgrade completed successfully with zero data loss!
Report: cortex-brain/documents/reports/upgrade-report-20251227-143500.json
```

**After Upgrade:**
```
📢 What's New in CORTEX 4.0:
   - Enhanced Planning System with auto-complexity detection
   - TDD Mastery with 11+ language support
   - Improved ADO Operations with manifest inheritance
   - System Refinement orchestrator (7 phases)
   
✅ All user-facing features operational
📁 Backup available at: .upgrades/backups/20251227_143000
🔄 Rollback command: upgrade cortex --rollback 20251227_143000
```

---

## 🚨 Emergency Recovery

**If Upgrade Fails:**

1. **Automatic Rollback** (triggered by orchestrator)
   - Detects failure in Phase 5+
   - Restores brain data from backup
   - Resets git to previous version
   - Reinstalls old dependencies
   - Verifies rollback success

2. **Manual Rollback** (user-initiated)
   ```bash
   # List available backups
   upgrade cortex --list-backups
   
   # Rollback to specific backup
   upgrade cortex --rollback 20251227_143000
   
   # Verify health
   cortex healthcheck
   ```

3. **Emergency Manual Recovery**
   ```bash
   cd /path/to/CORTEX
   python -m src.operations.modules.upgrade.upgrade_utility --restore <backup_id>
   git reset --hard <previous_version_tag>
   pip install -r requirements.txt
   python -m src.operations.healthcheck
   ```

---

## 🔮 Future Enhancements

**Phase 1: Current Implementation**
- ✅ 9-phase upgrade workflow
- ✅ Brain data protection
- ✅ User-facing feature validation
- ✅ Automatic rollback

**Phase 2: Planned**
- ⏳ Differential upgrades (only changed files)
- ⏳ Background upgrades (non-blocking)
- ⏳ Multi-version rollback (not just previous)
- ⏳ Upgrade scheduling (weekly/monthly)

**Phase 3: Future**
- ⏳ A/B testing for upgrades
- ⏳ Gradual rollout (canary deployments)
- ⏳ Upgrade analytics (success rates, failure patterns)
- ⏳ Auto-upgrade for patch releases

---

## 📚 Related Documentation

**Core Files:**
- `.github/prompts/cortex-upgrade.prompt.md` - Upgrade assistant prompt
- `src/orchestrators/upgrade_orchestrator_v2.py` - Orchestrator implementation
- `src/operations/modules/upgrade/upgrade_utility.py` - Utility functions
- `cortex-operations.yaml` - Upgrade operation definition

**Guides:**
- `cortex-brain/brain-protection-rules.yaml` - SKULL rules
- `cortex-brain/response-templates-v4.yaml` - Response templates
- `.github/prompts/CORTEX.prompt.md` - Core instructions

**Reports:**
- `cortex-brain/documents/reports/upgrade-report-*.json` - Upgrade history

---

## ✅ Completion Checklist

- [x] Create cortex-upgrade.prompt.md (packaged upgrade assistant)
- [x] Implement UpgradeOrchestratorV2 (9-phase workflow)
- [x] Update cortex-operations.yaml (brain protection config)
- [x] Document brain-safe deployment strategy
- [x] Define user-facing release criteria
- [x] Implement rollback strategy
- [x] Add emergency recovery procedures

---

**Next:** Test upgrade workflow end-to-end with simulated version bump

**Status:** ✅ Implementation complete - ready for integration testing
