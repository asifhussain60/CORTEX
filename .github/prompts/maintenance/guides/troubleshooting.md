# 🔧 Troubleshooting Guide

## Common Issues

### Issue 1: Maintenance Stops at Phase 3

**Symptom:** Maintenance aborts with "Critical checkpoint failed"

**Cause:** Data preservation validation failed - protected data paths missing or corrupted

**Solution:**
```bash
# Check protected data paths exist
ls cortex-brain/tier1/*.db
ls cortex-brain/lessons-learned.yaml
ls cortex-brain/knowledge-graph.yaml

# If missing, restore from backup or re-initialize
git checkout HEAD -- cortex-brain/tier1/
```

---

### Issue 2: Wiring Coverage <100%

**Symptom:** Phase 5 reports wiring coverage <100%

**Cause:** New components added but not registered in manifests

**Solution:**
```bash
# Re-run wiring check to identify unwired components
python scripts/check_wiring_integrity.py

# Phase 5 auto-wires, but if it fails:
python scripts/bulk_wire_components.py --dry-run
python scripts/bulk_wire_components.py  # Apply fixes
```

---

### Issue 3: Tests Failing in Phase 6

**Symptom:** Test suite has failures

**Cause:** Code changes broke existing tests OR obsolete tests need deletion

**Solution:**
```bash
# View test failures
pytest tests/ -v

# Delete obsolete tests (maintenance does this automatically)
# If manual fix needed:
python scripts/delete_obsolete_tests.py
```

---

### Issue 4: Template Validation Errors

**Symptom:** Phase 2 reports broken template references

**Cause:** Template files moved/deleted but references not updated

**Solution:**
```bash
# Maintenance auto-repairs, but to manually check:
python -c "
import yaml
from pathlib import Path

routing = yaml.safe_load(open('cortex-brain/response-templates/response-routing-rules.yaml'))
mappings = routing.get('validation', {}).get('template_file_mappings', {})

for tid, path in mappings.items():
    if not Path(path).exists():
        print(f'❌ {tid} → {path}')
"
```

---

### Issue 5: Cleanup Orchestrator Fails

**Symptom:** Phase 0 exits with error

**Cause:** Cleanup rules YAML invalid OR protected paths misconfigured

**Solution:**
```bash
# Validate cleanup rules syntax
python -c "import yaml; yaml.safe_load(open('cortex-brain/cleanup-rules.yaml'))"

# Check cleanup orchestrator logs
cat cortex-brain/cleanup-logs/cleanup-*.log | tail -50
```

---

### Issue 6: Knowledge Library Sync Fails

**Symptom:** Phase 7 reports broken knowledge references

**Cause:** YAML files moved but markdown refs not updated

**Solution:**
```bash
# Maintenance auto-repairs, but to manually check:
python scripts/sync_knowledge_library.py --dry-run
python scripts/sync_knowledge_library.py  # Apply fixes
```

---

### Issue 7: Maintenance Hangs/Freezes

**Symptom:** Maintenance stops responding mid-phase

**Cause:** Long-running operation OR infinite loop in auto-repair

**Solution:**
```bash
# Check if process is actually running
ps aux | grep python | grep maintenance

# If hung, kill and restart with specific phase:
kill -9 <PID>
system maintenance --phases <next_phase>
```

---

### Issue 8: Health Score <95% After Maintenance

**Symptom:** Phase 11 reports health <95%

**Cause:** Critical issues not auto-repairable (manual intervention needed)

**Solution:**
1. Review health report: `cortex-brain/health-reports/maintenance-report-*.md`
2. Check "Warnings" section for manual fixes needed
3. Apply manual fixes
4. Re-run maintenance to verify

---

## Debug Mode

Enable verbose logging for troubleshooting:

```bash
export CORTEX_DEBUG=1
system maintenance
```

Logs output to: `logs/maintenance-debug-{timestamp}.log`

---

## Emergency Recovery

If maintenance corrupts system:

```bash
# Rollback to last commit before maintenance
git log --oneline -10  # Find pre-maintenance commit
git reset --hard <commit_hash>

# Restore from automated backup (if exists)
cp -r backups/auto_maintenance_<timestamp>/* .
```

---

## Getting Help

1. **Check logs:** `cortex-brain/cleanup-logs/` and `logs/`
2. **Review report:** `cortex-brain/health-reports/maintenance-report-*.md`
3. **Search issues:** Check known issues in this guide
4. **Manual intervention:** See FULL-IMPLEMENTATION-REFERENCE.md for detailed commands
