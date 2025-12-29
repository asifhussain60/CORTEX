---
mode: agent
description: "CORTEX System Maintenance - Automated health, auto-repair, optimization"
---

# 🩺 CORTEX System Maintenance

**Purpose:** Diagnose AND auto-repair CORTEX system issues automatically.  
**Author:** Asif Hussain | **Version:** 4.0.0 Lean

---

## 🎯 Core Philosophy

**MAINTENANCE = DIAGNOSE + AUTO-REPAIR + VERIFY**

**⚠️ CRITICAL:** Every detected issue MUST have an auto-repair handler. No manual TODOs.

---

## 🔧 10-Phase Pipeline

| Phase | Focus | Auto-Repair Action |
|-------|-------|-------------------|
| **1. DISCOVERY** | Scan system | Generate action report |
| **2. CLEANUP** | Find bloat | Delete backups, old reports |
| **3. SCAFFOLDING** | Verify generators | Create missing tools |
| **4. WIRING** | Detect gaps | Wire all components |
| **5. TESTING** | Run tests | Fix/delete obsolete tests |
| **6. KNOWLEDGE** | Check library | Sync YAML↔MD |
| **7. ORGANIZATION** | Report structure | Archive old reports |
| **8. ROUTING** | Intent router | Fix broken paths |
| **9. PROMPTS** | Measure bloat | Regenerate lean (<200 lines) |
| **10. VERIFICATION** | Health check | Fix critical issues |

---

## 🚀 Execution Workflow

### Phase 1: Discovery
Run: `python scripts/check_wiring_integrity.py`
Output: `cortex-brain/discovery-reports/MASTER-ACTION-PLAN-{date}.md`

### Phase 2: Cleanup
```powershell
# Delete old backups (>7 days)
Get-ChildItem -Recurse | Where-Object {
  $_.Name -match '\.(bak|backup|old)$' -and
  $_.LastWriteTime -lt (Get-Date).AddDays(-7)
} | Remove-Item -Force
```

### Phase 3: Scaffolding
Verify:
- `cortex-toolkit/core/utilities/plan_scaffold_generator.py`
- `cortex-toolkit/core/utilities/orchestrator_scaffold_generator.py`

### Phase 4: Wiring
Run: `python scripts/auto_wire_orchestrators.py`
Targets:
- Interactive planning workflow
- Vision API auto-engagement
- 300+ operation modules
- Agent registry updates

### Phase 5: Testing
```powershell
# Run tests
python -m pytest tests/ -v

# Delete obsolete tests
Get-ChildItem tests/ -Recurse -Filter "*.py" | 
  Select-String -Pattern "DEPRECATED|LEGACY|OBSOLETE" |
  ForEach-Object { # Review and delete }
```

### Phase 6: Knowledge Library
Sync `cortex-brain/knowledge/*.yaml` ↔ `*.md`

### Phase 7: Organization
```powershell
# Archive old reports (>30 days)
$oldReports = Get-ChildItem "cortex-brain/documents/reports" |
  Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) }

# Move to archive
$oldReports | Move-Item -Destination "cortex-brain/documents/reports/archive/"
```

### Phase 8: Routing
Validate: `.github/prompts/CORTEX.prompt.md` manifest paths point to valid files

### Phase 9: Prompts (THIS PHASE)
**Target:** All prompts <200 lines

**Bloated Prompts:**
- `CORTEX_ADMIN_GOVERNOR.prompt.md` (1463 lines → ~180 lines)
- `cortex-maintenance.prompt.md` (1657 lines → ~180 lines)
- `cortex-upgrade.prompt.md` (342 lines → ~150 lines)

**Strategy:**
1. Extract core workflow only
2. Reference detailed docs via links
3. Use tables for condensed info
4. Remove redundant examples
5. Keep essential commands

### Phase 10: Verification
```powershell
# Run health diagnostics
python scripts/health_check.py

# Expected: Health score ≥95%
```

---

## 📊 Success Metrics

| Metric | Before | After | Status |
|--------|--------|-------|--------|
| Wiring Coverage | 33% | 100% | Target |
| Prompt Bloat | 2900 lines | <800 lines | Target |
| Backup Bloat | 500+ KB | 0 KB | Target |
| Test Health | 80% | 100% | Target |
| Health Score | 65% | 95%+ | Target |

---

## 🔍 Critical Wiring Checks

### Interactive Planning
```powershell
# Verify wiring
Select-String -Path "src/orchestrators/planning/planning_orchestrator.py" `
  -Pattern "_should_use_interactive_mode"
# ✅ Should find 2 matches

Select-String -Path "src/cortex_agents/agent_registry.py" `
  -Pattern "InteractivePlanner"
# ✅ Should find import + registration
```

### Vision API
```powershell
# Check auto-detect
Select-String -Path "cortex.config.json" -Pattern "auto_detect_images"
# ⚠️ If not found, add to config
```

---

## 🛠️ Auto-Repair Tools

| Tool | Purpose | Location |
|------|---------|----------|
| Wiring Checker | Find unwired components | `scripts/check_wiring_integrity.py` |
| Auto-Wire | Wire orchestrators/agents | `scripts/auto_wire_orchestrators.py` |
| Backup Cleaner | Remove old backups | `src/operations/modules/cleanup/backup_archiver.py` |
| Test Analyzer | Find obsolete tests | `scripts/analyze_unwired_components.py` |

---

## 📝 Detailed References

For comprehensive phase details:
- **Full Pipeline:** `cortex-brain/documents/implementation-guides/maintenance-wiring-persistence-gap.md`
- **Wiring Patterns:** `cortex-brain/documents/implementation-guides/auto-wire-orchestrators-design.md`
- **Interactive Workflow:** `cortex-brain/documents/implementation-guides/interactive-workflow-wiring-checklist.md`

---

**Maintenance Status:** Run `python scripts/health_check.py` for current system health.
