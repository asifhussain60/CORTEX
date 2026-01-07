# Phase 0: Cleanup Orchestrator Execution 🧹

**SMART CLEANUP**

---

## 🎯 Purpose

Execute the intelligent cleanup orchestrator as the FIRST step to remove bloat, backups, and temporary files while preserving all critical data.

**Orchestrator:** `src/plugins/cleanup_orchestrator.py`  
**Rules:** `cortex-brain/cleanup-rules.yaml`  
**Manifest:** `cortex-brain/manifests/orchestrators/aggressive-cleanup-rules.yaml`

---

## 🚀 Execution

```powershell
# Run cleanup orchestrator
python src/plugins/cleanup_orchestrator.py

# Verify success
if ($LASTEXITCODE -eq 0) {
    # Parse manifest for metrics
    $manifest = Get-Content "cortex-brain/cleanup-manifests/cleanup-manifest-*.json" | ConvertFrom-Json | Select-Object -Last 1
    
    Write-Host "✅ Cleanup complete"
    Write-Host "  📊 Deleted: $($manifest.actions.deleted.Count)"
    Write-Host "  💾 Space Freed: $($manifest.summary.space_freed_mb) MB"
}
```

---

## 🛡️ Data Preservation

Cleanup orchestrator NEVER deletes:
- `cortex-brain/tier{1,2,3}/*.db` (brain databases)
- `cortex-brain/lessons-learned.yaml`
- `cortex-brain/knowledge-graph.yaml`
- `cortex-brain/user-dictionary.yaml`
- `cortex-brain/documents/` (user content)
- `.git/` directory
- Active plan folders with `copilot_instructions`
- `named_templates` in response-templates-v4.yaml

---

## ✅ Success Criteria

- Cleanup orchestrator executes without errors
- Cleanup manifest generated
- Zero backups remain
- All protected data paths intact
- Space freed ≥100MB (typical)
