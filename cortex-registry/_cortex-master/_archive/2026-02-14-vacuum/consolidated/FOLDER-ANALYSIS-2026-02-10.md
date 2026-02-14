# Folder Analysis: deployment/, reports/, scripts/

**Date:** 2026-02-10  
**Purpose:** Determine if deployment/, reports/, scripts/ folders should be kept or archived  
**Status:** ANALYSIS COMPLETE

---

## 📁 FOLDER INVENTORY

### 1. deployment/ (Root Level)
**Location:** `/deployment/` (top-level, NOT inside cortex/)

| Content | Status | Use |
|---------|--------|-----|
| `canary_config.yaml` | ✅ NEEDED | Deployment strategy config |
| `health_checks.yaml` | ✅ NEEDED | Service health validation |
| `mcp-gateway-config.yaml` | ✅ NEEDED | MCP gateway configuration |
| `nginx.conf` | ✅ NEEDED | Local dev nginx |
| `nginx.prod.conf` | ✅ NEEDED | Production nginx config |
| `prometheus.yml` | ✅ NEEDED | Metrics collection (local) |
| `prometheus.prod.yml` | ✅ NEEDED | Metrics collection (prod) |
| `requirements.txt` | ✅ NEEDED | Deployment dependencies |
| `docker/` | ✅ NEEDED | Docker configs |
| `grafana-dashboards/` | ✅ NEEDED | Dashboard definitions |
| `hooks/` | ✅ NEEDED | Git hooks |

**Verdict:** ✅ **KEEP** - Infrastructure configuration essential for deployment

---

### 2. cortex/deployment/ (Inside cortex Package)
**Location:** `/cortex/deployment/` (part of CORTEX package)

| File | Status | Usage | Purpose |
|------|--------|-------|---------|
| `deployment_validator.py` | ✅ ACTIVE | 1 import in master_orchestrator | Pre-deployment validation |
| `exit_gate_integration.py` | ✅ ACTIVE | Used by MasterOrchestrator | EXIT GATE for phase 38 |
| `rollback_orchestrator.py` | ⚠️ PARTIAL | Available but not actively used | Rollback strategy |
| `dashboard_api.py` | ⚠️ PARTIAL | Imports analytics/monitor | Dashboard for deployments |
| `analytics.py` | ⚠️ PARTIAL | Imported by dashboard_api | Analytics for deployments |
| `monitor.py` | ⚠️ PARTIAL | Imported by dashboard_api | Deployment monitoring |

**Verdict:** ✅ **KEEP** - Active in MasterOrchestrator EXIT GATE; used by Phase 38

---

### 3. reports/ (Root Level)
**Location:** `/reports/`

| Content | Size | Status | Purpose |
|---------|------|--------|---------|
| `CORTEX-100-PRODUCTION-READY-FINAL.md` | ~50 KB | 📝 DOCUMENTATION | Phase completion report |
| `coverage/` | ~500 KB | 📊 DATA | Test coverage reports |

**Status:** 📖 Read-only historical data  
**Usage:** Not actively imported by code  
**Access Pattern:** Manual review only

**Verdict:** ⚠️ **ARCHIVE** - Historical reports, not needed in active codebase

---

### 4. scripts/ (Root Level)
**Location:** `/scripts/`

| File | Type | Status | Purpose | Active |
|------|------|--------|---------|--------|
| `*.py` (52 files) | Utility | 🔧 TOOLS | Various one-off scripts | Mixed |
| `*.sh` (4 files) | Shell | 🔧 TOOLS | Hook setup, testing | Mixed |
| `governance/` | Subdir | 🔧 TOOLS | Governance utilities | Mixed |
| `test-utilities/` | Subdir | 🔧 TOOLS | Test helpers | Some |
| `utilities/` | Subdir | 🔧 TOOLS | General utilities | Some |
| `diagram-generators/` | Subdir | 🔧 TOOLS | Diagram creation | Rarely |
| `deprecated/` | Subdir | 🔳 DEPRECATED | Legacy scripts | No |

**Key Observations:**
- 52 Python scripts, mostly ad-hoc/one-time use
- No imports from `scripts/` in main codebase
- Script execution via terminal only (manual or CI/CD)
- Many legacy phases (3, 4, 20, 37, 70, etc.)
- No active orchestrator integration

**Verdict:** ⚠️ **ARCHIVE** - Utilities and one-off scripts, not part of core system

---

## 🔍 CODEBASE DEPENDENCY ANALYSIS

### What Actually Uses These Folders

#### cortex/deployment/ - ACTIVE USAGE
```python
# In cortex/orchestrators/core/master_orchestrator.py (line 2042)
from cortex.deployment.exit_gate_integration import create_deployment_gate

# Used in EXIT GATE for production deployment validation
deployment_gate = create_deployment_gate(fail_safe=True)
gate_result = deployment_gate.validate_deployment_gate(...)
```

**Status:** ✅ **ESSENTIAL** - Phase 38 Stage 10 integration

---

#### deployment/ (root) - ESSENTIAL INFRASTRUCTURE
```
Used by:
- Docker containers (docker/ configs)
- Kubernetes (canary_config.yaml)
- Nginx reverse proxy (nginx.conf, nginx.prod.conf)
- Prometheus monitoring (prometheus.yml, *.prod.yml)
- Grafana dashboards (grafana-dashboards/)
- Git hooks (hooks/)
```

**Status:** ✅ **ESSENTIAL** - Infrastructure backbone

---

#### reports/ - NO ACTIVE IMPORTS
```
- Zero imports in cortex/ package
- Zero imports in tests/
- Zero imports in orchestrators
- Only referenced in documentation
```

**Status:** 📦 **ARCHIVED** - Historical data only

---

#### scripts/ - NO PACKAGE IMPORTS
```
- Zero imports from scripts/ in cortex/ package
- Zero imports from scripts/ in tests/
- Executed directly via:
  - Terminal: python scripts/foo.py
  - CI/CD: Called by workflow files
  - Manual: Developer runs for one-off tasks
```

**Status:** 🧹 **TOOLS ONLY** - Utilities, not framework

---

## 📊 RECOMMENDATION MATRIX

| Folder | Keep? | Reason | Action |
|--------|-------|--------|--------|
| **deployment/** | ✅ YES | Infrastructure (nginx, prometheus, docker, k8s configs) | KEEP in root |
| **cortex/deployment/** | ✅ YES | Used by MasterOrchestrator EXIT GATE (Phase 38 S10) | KEEP in package |
| **reports/** | ⚠️ MAYBE | Historical reports, no active code dependency | ARCHIVE to docs/archive/ |
| **scripts/** | ⚠️ MAYBE | Utilities, one-off scripts, not part of framework | ARCHIVE to docs/archive/scripts/ or .tools/ |

---

## 🎯 FINAL DECISION

### YES, Keep:
1. ✅ **deployment/** (root) - Infrastructure configs
2. ✅ **cortex/deployment/** - MasterOrchestrator integration

### NO, Archive:
1. ⚠️ **reports/** → Move to `docs/archive/reports/`
2. ⚠️ **scripts/** → Move to `docs/archive/scripts/` (or `.tools/` if CLI utilities)

---

## 📋 CLEANUP PLAN (Optional)

If implementing cleanup:

```bash
# Archive historical reports
mkdir -p docs/archive/reports
mv reports/* docs/archive/reports/
git add docs/archive/reports/
git commit -m "archive: Move historical reports to docs/archive"

# Archive legacy scripts (if not actively used)
mkdir -p docs/archive/scripts
mv scripts/* docs/archive/scripts/
git add docs/archive/scripts/
git commit -m "archive: Move utility scripts to docs/archive"

# Update .gitignore to track archive
echo "docs/archive/" >> .gitignore
git add .gitignore
git commit -m "docs: Track archived reports and scripts"
```

---

## 🔗 RELATED ANALYSIS

See also:
- Phase 73: Deployment Orchestrator (uses cortex/deployment/)
- Phase 38 S10: EXIT GATE Integration (uses deployment_validator)
- MasterOrchestrator wiring (uses deployment module)

---

**Conclusion:** Keep infrastructure folders (deployment/, cortex/deployment/). Archive historical reports and utility scripts to docs/archive/ to clean up root directory.

AC-ID: AC-FOLD-ANAL-001
