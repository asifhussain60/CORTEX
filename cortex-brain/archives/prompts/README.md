# Archived Prompts - Migration to Master Orchestrator

**Date:** January 6, 2026  
**Reason:** Consolidated into single CORTEX.prompt.md entry point with orchestrator-based routing

---

## 📋 Archived Prompts

### 1. `cortex-docs-v2.0-archived.prompt.md`

**Original Purpose:** State-aware HTML glassmorphism standardization

**Archived Because:**
- ✅ Functionality moved to `documentation_orchestrator` (manifest-based)
- ✅ Registered in `master-orchestrator.yaml` at priority 25
- ✅ Pattern: `^(standardize|apply glassmorphism|docs standardization).*$`
- ✅ All intelligence now in orchestrator manifest + Python implementation

**New Workflow:**
```bash
# Old (2 prompts)
User: "Follow instructions in cortex-docs.prompt.md"
User: "Apply glassmorphism to architecture page"

# New (1 prompt)
User: "standardize architecture/index.html"
# Routes via CORTEX.prompt.md → documentation_orchestrator
```

**Reference:**
- Orchestrator manifest: `cortex-brain/manifests/orchestrators/documentation-orchestrator.yaml`
- Design doc: `cortex-brain/documents/orchestrators/documentation-orchestrator-v2-design.md`

---

### 2. `cortex-backlog-v5.0-archived.prompt.md`

**Original Purpose:** YAML-first backlog processing with archival workflow

**Archived Because:**
- ❌ Not registered in `master-orchestrator.yaml`
- ❌ No orchestrator implementation
- ❌ Functionality can be integrated into planning orchestrator if needed
- ⚠️ Low usage (no evidence of active use in recent commits)

**Status:** Archived pending decision on backlog management strategy

**Future Options:**
1. Integrate into Planning Orchestrator v5 (backlog → plan conversion)
2. Create dedicated Backlog Orchestrator (if demand exists)
3. Keep archived (manual YAML conversion workflow)

---

## ✅ Prompts Kept Active

These prompts correspond to registered orchestrators in `master-orchestrator.yaml`:

| Prompt File | Orchestrator | Priority | Pattern |
|-------------|--------------|----------|---------|
| `cortex-upgrade.prompt.md` | `upgrade_orchestrator` | 15 | `^(upgrade cortex\|cortex upgrade).*$` |
| `cortex-vacuum.prompt.md` | `vacuum` | 45 | `^(vacuum\|deep clean).*$` |
| `cortex-investigate.prompt.md` | Investigation (implicit) | 60 | `^(investigate\|find root cause).*$` |
| `cortex-maintenance.prompt.md` | `maintenance_orchestrator` | 50 (disabled) | `^(maintenance\|health check).*$` |
| `cortex-git-commit.prompt.md` | Special handler | N/A | `/cortex-git-commit` |
| `cortex-refactor.prompt.md` | `refinement_orchestrator_v2` | 60 | `^(refine\|improve\|optimize).*$` |
| `cortex-plan-upgrade.prompt.md` | Plan upgrade utility | N/A | Manual invocation |

**Note:** These prompts provide detailed implementation guidance but ALL routing goes through `CORTEX.prompt.md` first.

---

## 🔄 Migration Strategy

**Principle:** One universal entry point (`CORTEX.prompt.md`), intelligence in routing layer.

**Decision Tree for Future Prompts:**

```
New functionality needed?
  ↓
Does orchestrator exist?
  ├─ YES → Update orchestrator manifest
  │         Add pattern to master-orchestrator.yaml
  │         Archive standalone prompt
  │
  └─ NO → Create orchestrator manifest first
            Register in master-orchestrator.yaml
            Use CORTEX.prompt.md for routing
```

**Archive Criteria:**
1. ✅ Orchestrator manifest exists
2. ✅ Pattern registered in `master-orchestrator.yaml`
3. ✅ Routing through `CORTEX.prompt.md` confirmed working
4. ✅ No unique functionality lost

---

## 📚 References

- **Master Orchestrator Config:** `cortex-brain/config/master-orchestrator.yaml`
- **Universal Entry Point:** `.github/prompts/CORTEX.prompt.md`
- **Orchestrator Manifests:** `cortex-brain/manifests/orchestrators/`
- **Archive Location:** `cortex-brain/archives/prompts/`

---

**Last Updated:** January 6, 2026  
**Maintainer:** Asif Hussain
