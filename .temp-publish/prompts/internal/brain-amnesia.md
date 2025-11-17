# Brain Amnesia - Application Data Reset

**Version:** 2.0  
**Config:** `#file:cortex-brain/agents/amnesia-config.yaml`  
**Purpose:** Remove application-specific learned data while preserving KDS core intelligence  
**Status:** 🧠 SAFE RESET - Only affects application context

---

## Overview

**Brain amnesia safely resets application-specific data while preserving generic KDS intelligence and governance patterns.**

### What Gets Removed
- ✅ File relationships (application paths)
- ✅ Application-specific workflow patterns
- ✅ Feature components
- ✅ Conversation history
- ✅ Events log
- ✅ Development context metrics
- ✅ Correction history with app paths

### What Gets Preserved
- ✅ Generic intent patterns (templates with [X]/[Y] placeholders)
- ✅ Generic workflow patterns (test_first_id_preparation, etc.)
- ✅ KDS-specific patterns (brain_test_synchronization, kds_health_monitoring)
- ✅ Generic test patterns (id_based_playwright_selectors)
- ✅ Protection configuration (all thresholds)
- ✅ Validation insights structure
- ✅ All KDS prompts and agents

**Full lists:** See `data_categories` in config

---

## Pattern Classification

**Generic Pattern Indicators:**
- Contains `[X]` or `[Y]` placeholders
- No specific file paths
- Applies to any project type
- Named: "generic", "reusable", "pattern"
- Scope: `kds_internal_governance` or undefined

**Application-Specific Indicators:**
- Hardcoded file paths (e.g., "SPA/NoorCanvas/...")
- Specific features (e.g., "fab_button")
- Architecture-specific (e.g., "Blazor + SignalR")
- Scope: NOT `kds_internal_governance`

**Classification rules:** See `classification` in config

---

## Safety Mechanisms

### Pre-Reset Validation
1. Create backup → `kds-brain/backups/pre-amnesia-{timestamp}.zip`
2. Generate amnesia report → Shows what will be removed/preserved
3. Require user confirmation → Show report first
4. Validate BRAIN files writeable
5. Check for active sessions → Warn if exists

### Post-Reset Validation
1. Verify BRAIN structure intact → All files exist
2. Verify generic patterns preserved → Count >= 8
3. Verify KDS patterns preserved → Required patterns exist
4. Verify protection config intact → All settings unchanged
5. Run BRAIN integrity tests → `test-brain-integrity.ps1`
6. Generate completion report

**Full validation steps:** See `safety` in config

---

## Execution Flow

```yaml
step1_backup:
  action: "Create backup of current BRAIN state"
  location: "kds-brain/backups/pre-amnesia-{timestamp}"
  includes: ["*.yaml", "*.jsonl"]

step2_report:
  action: "Generate amnesia report"
  file: "amnesia-report-{timestamp}.yaml"
  sections: ["will_be_removed", "will_be_preserved", "confidence_scores"]

step3_confirm:
  action: "Show report and require explicit user approval"

step4_reset:
  tier1: "Reset conversation-history.jsonl to bootstrap only"
  tier2: "Reset knowledge-graph.yaml (preserve generic, remove app-specific)"
  tier3: "Reset development-context.yaml (zero counters)"
  events: "Reset events.jsonl to single bootstrap event"

step5_verify:
  integrity: "Run all integrity checks"
  patterns: "Verify pattern counts"
  config: "Verify protection settings"

step6_report:
  action: "Generate amnesia-complete-{timestamp}.yaml"
  includes: ["summary", "counts", "health", "next_steps"]
```

**Detailed procedures:** See `reset_procedures` in config

---

## Reset Procedures by Tier

### Tier 1: Conversation History
```yaml
file: conversation-history.jsonl
action: Reset to bootstrap only
result: Single bootstrap conversation documenting reset
```

### Tier 2: Knowledge Graph
```yaml
file: knowledge-graph.yaml
actions:
  intent_patterns: Preserve generic templates, remove app examples
  file_relationships: Completely empty
  workflow_patterns: Keep 6 generic/KDS patterns, remove app-specific
  correction_history: Reset counters to 0
  feature_components: Completely empty
  statistics: Reset counters, preserve structure
```

**Preserved workflow patterns (6):**
- test_first_id_preparation
- single_file_spa_creation
- kds_health_monitoring
- powershell_http_server
- unified_launcher_pattern
- brain_test_synchronization

### Tier 3: Development Context
```yaml
file: development-context.yaml
action: Zero all counters, clear application data
```

### Events Log
```yaml
file: events.jsonl
action: Single bootstrap event
content: Documents the reset with previous_app and new_app fields
```

**Complete procedures:** See `reset_procedures` in config

---

## Implementation

```powershell
# Step 1: Create Backup
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = "KDS/kds-brain/backups/pre-amnesia-$timestamp"
New-Item -ItemType Directory -Force -Path $backupDir
Copy-Item -Path "KDS/kds-brain/*.yaml" -Destination $backupDir
Copy-Item -Path "KDS/kds-brain/*.jsonl" -Destination $backupDir

# Step 2: Generate and show report
# (Use amnesia-config.yaml to determine what gets removed/preserved)

# Step 3: Require confirmation
Read-Host "Proceed with amnesia? (Y/N)"

# Step 4: Execute reset
# (Apply reset procedures from config for each tier)

# Step 5: Verify
# (Run integrity checks from config)

# Step 6: Generate completion report
```

---

## Integrity Checks

```yaml
file_structure:
  verify_exist:
    - conversation-history.jsonl
    - knowledge-graph.yaml
    - development-context.yaml
    - events.jsonl
    - protection-rules.yaml
    - schema.sql

pattern_counts:
  min_generic_intent_patterns: 5
  min_workflow_patterns: 6
  min_test_patterns: 1

required_kds_patterns:
  - brain_test_synchronization
  - kds_health_monitoring

protection_config:
  must_have_keys:
    - learning_quality
    - routing_safety
    - correction_memory
    - validation
```

**Full checks:** See `integrity_checks` in config

---

## Safety Guarantees

### Cannot Be Lost (Guaranteed)

**KDS Core Capabilities:**
- Intent routing (8 types)
- 10 specialist agents
- Abstraction layer (4 components)
- Governance rules (17 rules)
- Protection system
- Health dashboard
- All KDS prompts

**Generic Intelligence:**
- "Add [X] button" → plan template
- Test-first ID preparation workflow
- Single-file SPA creation pattern
- ID-based Playwright selectors
- KDS health monitoring patterns
- Brain synchronization governance

### Will Be Lost (Intentional)

**Application-Specific Data:**
- Application file paths (e.g., NoorCanvas)
- Application-specific workflows
- Feature components
- Conversation history
- Git metrics
- Correction history

**Complete guarantees:** See `guarantees` in config

---

## Rollback Procedure

If amnesia needs to be undone:

```powershell
# Restore from backup
$backupDir = "KDS/kds-brain/backups/pre-amnesia-{timestamp}"
Copy-Item -Path "$backupDir/*.yaml" -Destination "KDS/kds-brain/" -Force
Copy-Item -Path "$backupDir/*.jsonl" -Destination "KDS/kds-brain/" -Force

# Verify restoration
# (Run integrity tests, verify counts)
```

**Rollback config:** See `rollback` in config

---

## Usage

**Invoke Amnesia:**
```markdown
#file:KDS/prompts/user/kds.md

Reset BRAIN for new application (amnesia)
```

**Expected Flow:**
1. Router detects "amnesia" or "reset brain"
2. Generate and show amnesia report
3. User confirms
4. Create backup
5. Execute reset (Tier 1 → 2 → 3)
6. Verify integrity
7. Generate completion report
8. User updates `kds.config.json`
9. User runs Setup to learn new application
10. KDS automatically learns from new interactions

---

## Post-Reset Next Steps

1. **Update configuration:** Edit `kds.config.json` with new application details
2. **Run Setup:** Execute Setup command to learn new architecture
3. **Allow learning:** KDS will automatically learn from interactions
4. **Monitor rebuild:** BRAIN rebuilds application knowledge over time

**Next steps details:** See `next_steps` in config

---

## Reports Generated

### Amnesia Report (Pre-Reset)
```yaml
will_be_removed:
  file_relationships: [count]
  workflow_patterns: [count]
  feature_components: [count]
  conversations: [count]
  events: [count]

will_be_preserved:
  intent_patterns: [count]
  workflow_patterns: [count]
  test_patterns: [count]
  protection_config: [yes]

confidence_scores:
  generic_patterns_preserved: 100%
  application_data_removed: 100%
  kds_capabilities_retained: 100%
```

### Completion Report (Post-Reset)
```yaml
amnesia_summary:
  executed: "{timestamp}"
  previous_application: "{app_name}"
  backup_location: "{path}"

removed: {counts}
preserved: {counts}

brain_health:
  structure_intact: true
  generic_intelligence_preserved: true
  application_data_removed: true
  ready_for_new_app: true

validation_passed:
  - ✅ Backup created
  - ✅ Generic patterns preserved
  - ✅ KDS patterns preserved
  - ✅ Application data removed
  - ✅ Protection config intact
  - ✅ File structure valid
  - ✅ Ready for use

next_steps: [...]
```

**Report templates:** See `reports` in config

---

## Configuration Reference

**All configuration in:** `#file:cortex-brain/agents/amnesia-config.yaml`

Includes:
- Data categories (removes/preserves)
- Classification rules (generic vs app-specific)
- Safety mechanisms (pre/post validation)
- Reset procedures (all tiers)
- Preserved patterns baseline (6 workflows, 1 test pattern)
- Integrity checks (files, counts, required patterns)
- Rollback configuration
- Safety guarantees
- Next steps
- Report templates

---

## See Also

- **Config:** `#file:cortex-brain/agents/amnesia-config.yaml`
- **Brain Query:** `prompts/internal/brain-query.md`
- **Brain Updater:** `prompts/internal/brain-updater.md`
- **Protection Rules:** `cortex-brain/brain-protection-rules.yaml`
