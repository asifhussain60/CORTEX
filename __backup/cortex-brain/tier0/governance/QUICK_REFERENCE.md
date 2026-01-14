# 🎯 CORTEX SSOT Toolkit – Quick Reference Card

**Print this. Keep it handy.**

---

## 🚀 Quick Start Commands

```bash
# Check SSOT health (read-only)
python3 src/tools/ssot_integrity_validator.py validate

# Repair corruption (creates backups)
python3 src/tools/ssot_integrity_validator.py repair

# Via toolkit interface
python3 src/mcp/toolkit_ssot_tools.py validate
python3 src/mcp/toolkit_ssot_tools.py repair --auto-fix

# Reconcile after merge
python3 src/mcp/toolkit_ssot_tools.py reconcile

# Update AC status
python3 src/mcp/toolkit_ssot_tools.py update-ac \
  --ac-id AC-AUDIT-001 \
  --status implemented \
  --test-passed 5 \
  --test-total 5
```

---

## 📊 Current Status (2026-01-13)

| Component | Status | Details |
|-----------|--------|---------|
| **Toolkit** | ✅ READY | 5 components, 1040+ lines |
| **Prevention** | ✅ ACTIVE | 2 git hooks blocking corruption |
| **Auto-Repair** | ✅ PARTIAL | 4/10 issues fixed |
| **Manual Fixes** | ⏳ PENDING | ~2 hours to complete |
| **Phase 2** | ⏳ BLOCKED | Unblocks after SSOT repair |

---

## 🔨 Manual Fixes Needed (1-2 hours)

### Step 1: Fix master-plan.yaml (30 mins)
```bash
# View current state
head -30 cortex-brain/cx6-plan/master-plan.yaml

# Rebuild from AC-INDEX (script in MANUAL_SSOT_REPAIR_GUIDE.md Step 3)
# Then validate
python3 -c "import yaml; yaml.safe_load(open('cortex-brain/cx6-plan/master-plan.yaml')); print('✅')"
```

### Step 2: Fix AC-INDEX schema (20 mins)
```bash
# Find orphaned entries
grep -n "^acceptance_criteria:\|^description:\|^last_updated:\|^schema_version:\|^updated_by:" \
  cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml

# Edit AC-INDEX.yaml to move these inside metadata section or delete
# Then validate
python3 -c "import yaml; yaml.safe_load(open('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml')); print('✅')"
```

### Step 3: Re-run repair (5 mins)
```bash
python3 src/tools/ssot_integrity_validator.py repair
```

### Step 4: Verify (5 mins)
```bash
python3 src/tools/ssot_integrity_validator.py validate
# Should show: ✅ NO ISSUES FOUND
```

---

## 📁 Key Files

| File | Purpose | Status |
|------|---------|--------|
| `src/tools/ssot_integrity_validator.py` | Detect & repair | ✅ PROD |
| `src/infrastructure/progress_tracker_manager.py` | Atomic writes | ✅ PROD |
| `.git/hooks/pre-commit` | Prevent corruption | ✅ ACTIVE |
| `.git/hooks/post-merge` | Auto-reconcile | ✅ ACTIVE |
| `cortex-brain/tier1/governance/MANUAL_SSOT_REPAIR_GUIDE.md` | Fix instructions | ✅ READY |
| `cortex-brain/backups/ssot-integrity/` | Recovery backups | ✅ AVAILABLE |

---

## 🛡️ Prevention Active

### Pre-commit Guard (Blocks Invalid Commits)
- ❌ Hardcoded percentages
- ❌ NULL AC counts
- ❌ Invalid YAML
- ❌ Invalid JSON

### Post-merge Hook (Auto-Validates)
- Auto-runs after merge
- Alerts on CRITICAL issues
- Suggests repair if needed

### CORE Rules (New Governance)
- **CORE-029:** Atomic writes required
- **CORE-030:** No hardcoded metrics
- **CORE-031:** Holistic recalculation
- **CORE-032:** SSOT sync gates

---

## 🆘 Common Issues

### "master-plan has no phases"
```bash
# Restore and rebuild (Step 1 in MANUAL_SSOT_REPAIR_GUIDE.md)
# Or restore from backup
cp cortex-brain/backups/ssot-integrity/master-plan.yaml.backup.* \
   cortex-brain/cx6-plan/master-plan.yaml
```

### "115 ACs in AC-INDEX but not in master-plan"
```bash
# Fix master-plan structure first, then
python3 src/tools/ssot_integrity_validator.py repair
```

### "AC entry X is not a dictionary"
```bash
# Edit AC-INDEX.yaml and fix schema (Step 2 in MANUAL_SSOT_REPAIR_GUIDE.md)
# Orphaned keys at root level must move inside metadata
```

### "Pre-commit hook blocked my commit"
```bash
# Check what's invalid
python3 src/tools/ssot_integrity_validator.py validate

# Fix issues, then try commit again
# (Or --no-verify to bypass, but not recommended)
```

---

## 📈 Health Check (Run Weekly)

```bash
#!/bin/bash
echo "🔍 CORTEX SSOT Health Check"
echo "=============================="

echo -e "\n1. Validation:"
python3 src/tools/ssot_integrity_validator.py validate | tail -5

echo -e "\n2. Phase Status:"
python3 << 'EOF'
import json
tracker = json.load(open('cortex-brain/tier1/tracking/progress-tracker.json'))
for phase in sorted(tracker.get('phases', {}).keys()):
    p = tracker['phases'][phase]
    total = p.get('total_ac_count', 0)
    done = p.get('completed_ac_count', 0)
    pct = (done/total*100) if total > 0 else 0
    print(f"  {phase}: {done}/{total} ({pct:.0f}%)")
EOF

echo -e "\n✅ Health check complete"
```

---

## 🔄 Integration Points (Ready for Wiring)

### MasterOrchestrator Integration
```python
# In master_orchestrator.py.__init__()
from src.infrastructure.progress_tracker_manager import ProgressTrackerManager
self.tracker_manager = ProgressTrackerManager(...)

# In update_ac_completion()
if not self.tracker_manager.update_ac_completion(ac_id, status):
    return ExecutionResult(success=False, error="State validation failed")
```

### MCP Tool Registration
```python
# In MCP toolkit registry
toolkit = SSoTToolkit(...)
register_tools([
    toolkit.validate_ssot,
    toolkit.repair_ssot,
    toolkit.reconcile_tracker,
    toolkit.update_ac_completion,
    toolkit.mark_phase_complete
])
```

---

## 📋 Backup Recovery

**If corruption detected:**
```bash
# List available backups
ls -lh cortex-brain/backups/ssot-integrity/

# Restore any file
cp cortex-brain/backups/ssot-integrity/{filename}.backup.{YYYYMMDD_HHMMSS} \
   {original_path}

# Verify
python3 src/tools/ssot_integrity_validator.py validate
```

---

## 🎯 Phase 2 Unblock Criteria

- [ ] master-plan.yaml structure valid (11 phases)
- [ ] AC-INDEX schema valid (0 orphaned keys)
- [ ] All 115 ACs mapped to phases
- [ ] Validator shows 0 issues
- [ ] Git commit successful
- [ ] Phase 2 can now execute

**Time to Unblock:** ~2 hours (manual fixes + validation)

---

## 📞 Support

**Documentation:**
- Complete reference: `SSOT-INTEGRITY-TOOLKIT.md`
- Repair guide: `MANUAL_SSOT_REPAIR_GUIDE.md`
- Deployment report: `DEPLOYMENT_REPORT_SSOT_TOOLKIT.md`
- Executive summary: `SSOT_EXECUTIVE_SUMMARY.md`

**Quick Checks:**
```bash
# View recent repairs
ls -lh cortex-brain/backups/ssot-integrity/

# View repair report
cat cortex-brain/backups/REPAIR_REPORT_20260113.md

# Check git hooks
ls -la .git/hooks/pre-commit .git/hooks/post-merge
```

---

## ✨ Success Criteria (Check When Done)

```bash
# Run all checks
echo "✅ Checking SSOT health..."

# 1. Validation
result=$(python3 src/tools/ssot_integrity_validator.py validate 2>&1 | grep "NO ISSUES")
if [ -z "$result" ]; then echo "❌ Issues found"; else echo "✅ SSOT valid"; fi

# 2. Backup exists
if [ -f cortex-brain/backups/ssot-integrity/progress-tracker.json.backup.* ]; then
  echo "✅ Backups created"
else
  echo "❌ No backups"
fi

# 3. Git hooks active
if [ -x .git/hooks/pre-commit ] && [ -x .git/hooks/post-merge ]; then
  echo "✅ Git hooks active"
else
  echo "❌ Git hooks missing"
fi

# 4. Can commit
if git status --short | grep -q "M cortex-brain/"; then
  echo "✅ Ready for commit (changes staged)"
else
  echo "ℹ️  No changes to commit"
fi

echo "🎉 All checks passed! Phase 2 ready to execute."
```

---

## 🚀 Next Steps

1. **Execute manual fixes** (Steps 1-4 in MANUAL_SSOT_REPAIR_GUIDE.md)
2. **Run validation** to confirm 0 issues
3. **Commit changes** (pre-commit hook will validate)
4. **Signal ready** for Phase 2 execution
5. **Phase 2** proceeds autonomously (54 ACs to 100% completion)

---

**Keep this card handy during SSOT repair execution!** 📌
