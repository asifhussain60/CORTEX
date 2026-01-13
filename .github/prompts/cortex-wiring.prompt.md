# 🏥 CORTEX Wiring & Architecture Health Check Prompt (v1.1)

**Purpose:** Validate and repair CORTEX architecture if misalignment occurs from pulls or manual changes.  
**Version:** 1.1.0 | **Date:** 2026-01-13  
**Author:** Asif Hussain  
**Governance:** CORE-001 (incremental), CORE-008 (TDD), CORE-017 (enforcement), CORE-026/27/28 (NEW)  
**AC-ID:** AC-CORTEX-001, AC-CORTEX-002, AC-CORTEX-003, AC-CORTEX-004, AC-CORTEX-005  
**Brittleness Fix Reference:** cortex-brain/tier0/governance/CORTEX-TOOLKIT-SINGLE-PATH-FIX.md

---

## 🎯 Purpose

This prompt provides **architecture health checking and auto-repair** for CORTEX 6.0 across all layers:

- **Tier 0:** Governance rules (core-rules.yaml, MCP tool registry, CORE-026/27/28)
- **Tier 1:** Execution state (progress-tracker.json, AC-INDEX.yaml)
- **SQLite:** Database schemas and integrity
- **MCP:** Registry consistency (orchestrators, tools, capabilities, toolkit singleton)
- **Config:** All YAML files across cortex-brain/
- **Toolkit:** Single path enforcement, no duplicates, singleton validation

**Design philosophy:** All logic delegated to Python orchestrators (HealthCheckOrchestratorV1). This prompt is a thin routing layer only.

---

## 🚀 Quick Start

### Option 1: Health Check Only (Read-Only, No Changes)

```bash
# Check system health and report issues
python3 -m src.main "health check" --format markdown
```

**Output:** Detailed report of all issues found (critical, high, medium, low)

### Option 2: Health Check + Auto-Repair (Safe Fixes)

```bash
# Auto-repair safe issues (MEDIUM/LOW severity, auto-repairable only)
python3 -m src.main "repair cortex" --format markdown
```

**Output:** Report of repairs applied + manual interventions needed

### Option 3: Full Diagnostics with Recommendations

```bash
# Detailed diagnostics with environment info and fix recommendations
python3 -m src.main "diagnose cortex health" --format markdown
```

**Output:** Complete diagnostic report with actionable recommendations

### Option 4: Targeted Health Checks

```bash
# Check specific layer only
python3 -m src.main "health check tier0" --format markdown
python3 -m src.main "health check tier1" --format markdown
python3 -m src.main "health check database" --format markdown
python3 -m src.main "health check mcp" --format markdown
```

---

## 📋 What Gets Checked & Repaired

### Layer 1: Tier 0 Governance

| Check | Issue ID | Severity | Auto-Repair? |
|-------|----------|----------|--------------|
| core-rules.yaml exists | TIER0-001 | CRITICAL | ❌ Manual |
| YAML syntax valid | TIER0-002 | CRITICAL | ❌ Manual |
| ≥23 SKULL rules present | TIER0-003 | HIGH | ❌ Manual |
| MCP registry has no UUID suffix | TIER0-004 | HIGH | ✅ Yes |
| MCP registry valid YAML | TIER0-005 | CRITICAL | ❌ Manual |

**Repairs:** UUID suffix removal from filenames (CORE-026 enforcement)

### Layer 2: Tier 1 Execution

| Check | Issue ID | Severity | Auto-Repair? |
|-------|----------|----------|--------------|
| progress-tracker.json exists | TIER1-001 | CRITICAL | ❌ Manual |
| JSON syntax valid | TIER1-002 | CRITICAL | ❌ Manual |
| AC-INDEX.yaml exists | TIER1-003 | CRITICAL | ❌ Manual |
| AC-INDEX.yaml valid YAML | TIER1-004 | CRITICAL | ❌ Manual |
| Completion ≤ total (no >100%) | TIER1-005 | HIGH | ✅ Yes |

**Repairs:** Cap completion counts at total AC count

### Layer 3: SQLite Databases

| Check | Issue ID | Database | Severity | Auto-Repair? |
|-------|----------|----------|----------|--------------|
| Database integrity | DB-GOVERNANCE-001 | governance.db | CRITICAL | ✅ Rebuild |
| Database accessible | DB-GOVERNANCE-002 | governance.db | HIGH | ❌ Manual |
| Database integrity | DB-AUDIT-001 | audit.db | CRITICAL | ✅ Rebuild |
| Database integrity | DB-PLANNING-001 | planning_state.db | CRITICAL | ✅ Rebuild |

**Repairs:** Rebuild corrupt databases from schema, clean orphaned records

### Layer 4: MCP Registry

| Check | Issue ID | Severity | Auto-Repair? |
|-------|----------|----------|--------------|
| mcp-server.yaml exists | MCP-001 | HIGH | ❌ Manual |
| YAML syntax valid | MCP-003 | HIGH | ❌ Manual |
| Orchestrators loadable | MCP-002 | HIGH | ✅ Validate |
| No duplicate IDs | MCP-004 | HIGH | ✅ Deduplicate |

**Repairs:** Deduplicate orchestrator IDs, validate class imports

### Layer 5: Cross-Layer Consistency

| Check | Issue ID | Severity | Auto-Repair? |
|-------|----------|----------|--------------|
| Tier structure exists | CROSS-001 | HIGH | ✅ Create dirs |
| Registry links valid | CROSS-002 | HIGH | ❌ Manual |
| AC-IDs consistent | CROSS-003 | MEDIUM | ✅ Sync |

**Repairs:** Create missing tier directories, sync AC ID counts

---

## 🔧 Architecture Overview

### Health Check System (AC-CORTEX-001)

```
HealthCheckOrchestratorV1 (src/orchestrators/health/health_check_orchestrator_v1.py)
├─ Layer 1: Validators (detect issues)
│  ├─ TierZeroValidator (governance, core-rules.yaml, MCP registry)
│  ├─ TierOneValidator (progress-tracker.json, AC-INDEX.yaml)
│  ├─ DatabaseValidator (SQLite schemas and integrity)
│  ├─ MCPValidator (mcp-server.yaml, orchestrator registry)
│  └─ CrossLayerValidator (Tier 0-3 consistency)
│
├─ Layer 2: Healers (auto-repair safe issues)
│  ├─ UUID suffix removal (CORE-026 enforcement)
│  ├─ Completion count capping
│  ├─ Tier directory creation
│  ├─ Database integrity repair
│  └─ Atomic transaction wrapper
│
├─ Layer 3: Auditors (track all changes)
│  └─ EnterpriseAuditLogger integration
│      (all repairs logged with timestamp, change details, rationale)
│
└─ Layer 4: Reporters (generate reports)
   ├─ Markdown report generation
   ├─ JSON report generation
   ├─ Severity-based filtering
   └─ Recommendation generation
```

### Integration Points

**Invocation:**
```
User Request
  ↓ (via CORTEX.prompt.md routing)
cortex-wiring.prompt.md
  ↓ (delegates all logic)
HealthCheckOrchestratorV1
  ↓ (runs validators)
5 Validator instances
  ↓ (if repair requested)
Healer functions (atomic transactions)
  ↓ (audit trail)
EnterpriseAuditLogger
  ↓ (generates)
Markdown/JSON report
```

---

## 🎯 Common Scenarios

### Scenario 1: Post-Pull Architecture Misalignment

```bash
# After git pull, something feels broken
python3 -m src.main "diagnose cortex health"

# Expected output:
# ✅ Issue detected: MCP registry has UUID suffix (CORE-026 violation)
# ✅ Recommended: Run "repair cortex" to auto-fix
# ✅ Then run: health check (verify repair successful)
```

### Scenario 2: Database Corruption Recovery

```bash
# After crash or hard shutdown
python3 -m src.main "health check database"

# Expected output:
# 🔴 CRITICAL: governance.db - integrity_check failed
# ⚠️  Recommended: Manual intervention or restore from backup

python3 -m src.main "repair cortex --force"

# Rebuilds databases from schema
```

### Scenario 3: Progress Tracker Inconsistency

```bash
# AC counts don't match reality
python3 -m src.main "health check tier1"

# Expected output:
# 🟠 HIGH: Phase 1 completion (45/30) - exceeds total ACs
# ✅ Auto-repair: Will cap at 30

python3 -m src.main "repair cortex"

# Applied: Capped Phase 1 completion to 30/30
```

### Scenario 4: Pre-Deployment Validation

```bash
# Before deploying to production
python3 -m src.main "diagnose cortex health"

# Must see:
# ✅ HEALTHY: All critical issues resolved
# ✅ All governance rules present
# ✅ All databases accessible
# ✅ All registries valid
```

---

## 📊 Report Interpretation

### Health Status Levels

- **✅ HEALTHY:** No critical or high issues detected
- **⚠️ WARNING:** High-priority issues detected (auto-repairable)
- **🔴 CRITICAL:** Manual intervention required immediately

### Severity Levels

| Level | Meaning | Action Required |
|-------|---------|-----------------|
| **CRITICAL** | System may be non-functional | Fix immediately (manual) |
| **HIGH** | Functional but degraded | Fix soon (auto or manual) |
| **MEDIUM** | Minor issue | Fix when convenient (mostly auto) |
| **LOW** | Information only | No action required |
| **INFO** | Status information | None |

### Issue Categories

| Category | Impact | Examples |
|----------|--------|----------|
| **TIER_0_GOVERNANCE** | Governance integrity at risk | Missing SKULL rules, corrupt core-rules.yaml |
| **TIER_1_EXECUTION** | Execution state invalid | Invalid progress tracker, AC count mismatch |
| **DATABASE_SCHEMA** | Data integrity at risk | Corrupt SQLite, schema mismatch |
| **MCP_REGISTRY** | Orchestrator discovery broken | Missing modules, unloadable classes |
| **CONFIG_FILES** | Configuration invalid | Syntax errors in YAML files |
| **CROSS_LAYER** | Consistency broken | Missing tier directories, orphaned AC-IDs |

---

## 🛠️ Troubleshooting

### Health check hangs or times out

```bash
# Run with timeout
timeout 30s python3 -m src.main "health check"

# If timeout reached, there's likely:
# - File system permission issue
# - Database locked (another process)
# - Corrupted YAML/JSON causing parsing hang
```

### "Cannot import HealthCheckOrchestratorV1" error

```bash
# Verify file exists
ls -la src/orchestrators/health/health_check_orchestrator_v1.py

# Verify Python path includes src/
export PYTHONPATH=/Users/asifhussain/PROJECTS/CORTEX:$PYTHONPATH
```

### Repair fails with "permission denied"

```bash
# Check file permissions
ls -la cortex-brain/tier0/governance/
ls -la cortex-brain/database/

# Fix if needed
chmod u+w cortex-brain/database/*.db
```

### Auto-repair applied but issue persists

```bash
# Run diagnostic to see root cause
python3 -m src.main "diagnose cortex health"

# Manual intervention may be needed
# Review the "manual_interventions" section
```

---

## 🔐 Safety Guarantees

### Auto-Repair Safety

✅ **Read-only validation first:** Always run health check before repair  
✅ **Atomic transactions:** All changes applied atomically (all-or-nothing)  
✅ **Backup before repair:** Database backups created before schema changes  
✅ **Audit trail:** Every repair logged with timestamp, change details, rationale  
✅ **Rollback capable:** All repairs reversible via git history  
✅ **Conservative approach:** Only fixes MEDIUM/LOW severity auto-repairable issues  

### Critical Issues Manual-Only

🔴 **Never auto-repair:** CRITICAL severity issues (governance, execution state)  
🔴 **Human review required:** Changes to core-rules.yaml, progress-tracker.json  
🔴 **Explicit confirmation:** Manual command required for dangerous repairs  

---

## 📈 Performance

| Operation | Typical Duration |
|-----------|-----------------|
| Health check (all layers) | 2-5 seconds |
| Repair (safe fixes only) | 3-8 seconds |
| Diagnostics (detailed) | 5-10 seconds |
| Database integrity check | 1-2 seconds per DB |
| MCP registry validation | <1 second |

**Notes:**
- Duration depends on system load and disk speed
- Database size affects integrity check time
- Parallel validation across layers (not sequential)

---

## 🔄 Integration with Other Systems

### MasterOrchestrator Integration

HealthCheckOrchestratorV1 is automatically invoked:
1. At MasterOrchestrator startup (health pre-check)
2. After state modifications (post-check)
3. Before phase transitions (gate validation)

### EnterpriseAuditLogger Integration

All repairs logged to audit trail:
```
{
  "timestamp": "2026-01-13T...",
  "category": "ORCHESTRATOR_REPAIR",
  "orchestrator": "HealthCheckOrchestratorV1",
  "issue_id": "TIER0-004",
  "repair_type": "remove_uuid_suffix",
  "status": "applied",
  "changes": {
    "old_filename": "mcp-tools-registry-6160caae.yaml",
    "new_filename": "mcp-tools-registry.yaml"
  },
  "user": "system",
  "correlation_id": "..."
}
```

### CI/CD Integration

Add to pre-deployment validation:
```bash
#!/bin/bash
echo "Running CORTEX health check..."
python3 -m src.main "diagnose cortex health" > /tmp/health-report.md

if grep -q "CRITICAL" /tmp/health-report.md; then
  echo "❌ Deployment blocked: Critical health issues detected"
  cat /tmp/health-report.md
  exit 1
fi

echo "✅ Health check passed - deployment approved"
```

---

## 🚀 Future Enhancements

### Planned AC-IDs

- **AC-CORTEX-006:** Real-time health monitoring (continuous background check)
- **AC-CORTEX-007:** Performance profiling (detect slow registries)
- **AC-CORTEX-008:** Capacity planning (predict when tier limits reached)
- **AC-CORTEX-009:** Drift history tracking (timeline of misalignments)
- **AC-CORTEX-010:** Health webhooks (notify on critical issues)

### Planned Features

- 🔄 Continuous monitoring daemon (background health check)
- 📊 Dashboard integration (real-time health metrics)
- 🔔 Alert system (email/Slack notifications)
- 📈 Historical trending (health degradation tracking)
- 🎯 Predictive repair (anticipate issues before they happen)

---

## 📞 Support & Escalation

### Health Check Fails Unexpectedly

1. **Gather diagnostics:** `python3 -m src.main "diagnose cortex health"`
2. **Check logs:** `tail -50 cortex-brain/audit-logs/*.log`
3. **Git state:** `git status` (any uncommitted changes?)
4. **Escalate:** File issue with diagnostic output

### Repair Fails / Partial Application

1. **Review audit trail:** `cat cortex-brain/audit-logs/recent.log`
2. **Check git diff:** `git diff cortex-brain/`
3. **Attempt rollback:** `git checkout -- cortex-brain/`
4. **Retry after fix:** `python3 -m src.main "repair cortex"`

### Manual Intervention Guide

For CRITICAL issues that require manual intervention:

1. **Read the issue description carefully**
2. **Check the evidence/context** provided in diagnostic output
3. **Review relevant CORTEX documentation** (cortex-brain/documents/)
4. **Make minimal, targeted fix** (not broad changes)
5. **Verify with health check** after fix
6. **Commit with proper message** referencing issue ID

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-13 | Initial release: 5 validators, 4 healers, full audit integration |
| (planned) | 2026-02-* | Real-time monitoring daemon + dashboard integration |
| (planned) | 2026-03-* | Predictive repair + capacity planning |

---

## ✅ Intent Routing Table Entry

Add to CORTEX.prompt.md Intent Routing Table:

```yaml
- pattern: "health check|wiring|architecture|repair cortex|diagnose cortex"
  orchestrator: HealthCheckOrchestratorV1
  priority: 5
  mode: autonomous
  ac_ids: ["AC-CORTEX-001", "AC-CORTEX-002", "AC-CORTEX-003", "AC-CORTEX-004", "AC-CORTEX-005"]
  description: "CORTEX architecture health validation and auto-repair"
  quick_start:
    - "python3 -m src.main 'health check'"
    - "python3 -m src.main 'repair cortex'"
    - "python3 -m src.main 'diagnose cortex health'"
```

---

## 🎓 Architecture Philosophy

This health check system embodies CORTEX 6.0 principles:

✅ **Governance-First:** All rules in core-rules.yaml (Tier 0)  
✅ **SSOT Architecture:** Single source of truth validated against actual state  
✅ **Incremental Execution:** Small validation tasks (not monolithic check)  
✅ **Audit-Driven:** Every repair logged and auditable  
✅ **Self-Healing:** Auto-repairs common issues automatically  
✅ **TDD-Ready:** Orchestrator designed for test-driven development  
✅ **Cross-Platform:** Works on MAC/WIN/Linux (CORE-005 compliant)  
✅ **Scalable:** New validators can be added without refactoring  

---

## 🔨 Extending the Health Check System

To add new validators or enhance health check:

See `.github/prompts/ORCHESTRATOR-DEVELOPMENT.md` for orchestrator patterns:
- Adding new validation methods
- Smart parameter passing
- Report generation with recommendations
- Integration with MasterOrchestrator

**Example: Adding a new Tier 4 Validator**
```python
class Tier4Validator(BaseValidator):
    """Example: Custom validation logic."""
    
    def validate(self) -> List[Issue]:
        """Add your validation logic here."""
        issues = []
        # Check something
        if something_wrong:
            issues.append(Issue(
                id="TIER4-001",
                severity="MEDIUM",
                description="...",
                auto_repairable=True
            ))
        return issues

# Add to HealthCheckOrchestratorV1.check()
tier4_validator = Tier4Validator()
all_issues.extend(tier4_validator.validate())
```

---

## 🎯 Success Criteria

Health check system is successful when:

- ✅ All CRITICAL governance issues detected and surfaced
- ✅ 80% of MEDIUM/LOW issues auto-repaired
- ✅ Full audit trail of all repairs
- ✅ Zero manual intervention for auto-repairable issues
- ✅ <5 second check runtime
- ✅ Cross-platform validation (MAC/WIN/Linux)
- ✅ Integrated with MasterOrchestrator lifecycle

---

**Status:** ✅ Ready for production use  
**Deployment:** Add to Intent Routing Table + MasterOrchestrator lifecycle  
**Owner:** Asif Hussain  
**Governance:** AC-CORTEX-001 through AC-CORTEX-005
