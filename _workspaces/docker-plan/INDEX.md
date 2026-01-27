# CORTEX Docker-First Migration - Document Index

**Version:** 2.2  
**Date:** 2026-01-27  
**Status:** APPROVED & REVIEWED

---

## 📚 Document Structure

This folder contains the complete migration plan for CORTEX Docker-First Architecture.

### 🎯 Primary Documents

| File | Purpose | Priority |
|------|---------|----------|
| **`CORTEX-MIGRATION-MASTER-PLAN.yaml`** | **SSOT** - Complete migration specification (v2.2) | 🔴 CRITICAL |
| **`wiring.yaml`** | Unified orchestrator wiring specification (v2.1) | 🔴 CRITICAL |
| **`migrate-to-docker-clean.sh`** | Automated migration script | 🟠 HIGH |

### 📋 Supporting Documents

| File | Purpose | Status |
|------|---------|--------|
| `00-EXECUTIVE-SUMMARY.md` | High-level overview | Updated to v2.0 |
| `01-COMPONENT-INVENTORY.md` | Component list (reference) | Legacy v1.0 |
| `02-DIRECTORY-STRUCTURE.md` | Directory layout (reference) | Legacy v1.0 |
| `03-WIRING-SYSTEM.md` | Wiring design (reference) | Legacy v1.0 |
| `04-DOCKER-SETUP.md` | Docker config (reference) | Legacy v1.0 |
| `05-WIRING-TESTS.md` | Test specifications | Current |
| `06-MIGRATION-SCRIPT.md` | Script documentation (reference) | Legacy v1.0 |
| `07-VALIDATION-CHECKLIST.md` | Validation steps | Current |
| `08-HEALTH-RECOVERY-TESTS.md` | Health test specs | Current |

---

## 🆕 What Changed in v2.2 (Docker MCP Gateway Integration)

### NEW Phase 4.5: Docker MCP Gateway Integration
- **Docker MCP Gateway** - Centralized routing and authentication proxy
- **One-click client integrations** - VS Code, Claude Desktop, Cursor, Windsurf
- **Docker MCP Catalog** - CORTEX becomes discoverable (220+ users)
- **cagent compatibility** - Multi-agent YAML workflows supported
- **Secrets management** - Centralized via Docker MCP Toolkit

### Architecture Enhancement
```
BEFORE: Client → Manual Config → CORTEX MCP Server
AFTER:  Client → Docker MCP Toolkit → MCP Gateway → CORTEX MCP Server
```

### Compatibility Verified
| Component | Status | Notes |
|-----------|--------|-------|
| `cortex/mcp/server.py` | ✅ No changes | Gateway proxies to existing endpoints |
| `cortex/mcp/protocol.py` | ✅ No changes | JSON-RPC 2.0 compliant |
| `cortex/mcp/adapters/*` | ✅ No changes | Internal to CORTEX |
| `cortex/wiring/**` | ✅ No changes | Orthogonal system |

### New Files Added
- `deployment/mcp-gateway-config.yaml` - Gateway configuration

---

## 🆕 What Changed in v2.1 (Review Recommendations)

### Team Collaboration Layer (NEW Phase 5.5)
- **User session context** - Propagate user identity through all operations
- **Operation locking** - Prevent concurrent modifications to same resources
- **API key authentication** - Simple auth for team deployments
- **User-attributed audit logs** - Track who did what

### Fixed MCP Adapter Paths
- Changed from `cortex.mcp.adapters.{orchestrator}_adapter` (non-existent)
- To `cortex.mcp.adapters.{core,domain,support}_adapters` (actual structure)

### Persistent Volumes
- `cortex-audit-logs` - Audit trail persistence
- `cortex-state` - Conversation state, pending operations
- `cortex-metrics` - Prometheus metrics data

### Security Configuration
- TLS termination at nginx level (documented)
- API key authentication header: `X-CORTEX-API-KEY`
- Rate limiting: 60 RPM per user

### Test Suite Expanded
- Total new tests: **75** (was 65)
- Added 10 team collaboration tests
- Added 3 new validation checks

---

## 🔄 What Changed in v2.0

### Approach Change: Cherry-Pick → Subtraction

**v1.0 (Cherry-Pick):**
- Start with empty branch
- Manually select 450+ files to include
- Risk: missing dependencies, broken imports

**v2.0 (Subtraction):**
- Start with full current branch
- Remove unwanted files in batches
- Test after each batch
- Safer: validates what's removed, not what's included

### Timeline Change: 5 Days → 10 Days

More realistic timeline with proper validation gates.

### Wiring Change: 3 YAML Files → 1 YAML File

**v1.0:** `core-wiring.yaml`, `domain-wiring.yaml`, `support-wiring.yaml`

**v2.0:** Single `wiring.yaml` with sections:
```yaml
orchestrators:
  core: [...]
  domain: [...]
  support: [...]
```

### New: _workspaces Migration Strategy

Complete strategy for migrating `_workspaces` folders:
- Keep: `roadmap/`, `cortex-vision/` → `vision/`, `config/`
- Rename: `docker-plan/` → `migration/`
- Archive: `awakening-of-cortex/`, `sts/`
- Remove: `ppt/`, `.chats/`

---

## 📊 Production Readiness (v2.1)

| Tier | Users | Status |
|------|-------|--------|
| **Tier 1: Single User** | 1 | ✅ 100% Ready |
| **Tier 2: Team** | 2-10 | 🟡 85% Ready (after v2.1) |
| **Tier 3: Enterprise** | 100-500 | 🟠 70% Ready |

---

## 🚀 Quick Start

### Option 1: Automated Migration

```bash
# Make script executable
chmod +x _workspaces/docker-plan/migrate-to-docker-clean.sh

# Run with dry-run first
./migrate-to-docker-clean.sh --dry-run

# Run for real
./migrate-to-docker-clean.sh
```

### Option 2: Phase-by-Phase

```bash
# Run specific phase
./migrate-to-docker-clean.sh --phase 0  # Pre-flight
./migrate-to-docker-clean.sh --phase 1  # Branch creation
./migrate-to-docker-clean.sh --phase 2  # Legacy removal
./migrate-to-docker-clean.sh --phase 3  # Wiring system
./migrate-to-docker-clean.sh --phase 4  # _workspaces
./migrate-to-docker-clean.sh --phase 5  # Docker
./migrate-to-docker-clean.sh --phase 6  # Validation
```

---

## ✅ Success Criteria

- [ ] 23 orchestrators wired via Git-backed YAML
- [ ] Zero `.db` files in repository
- [ ] Docker container builds and runs
- [ ] Health endpoint returns healthy
- [ ] All 65 wiring tests pass
- [ ] Existing test suite passes
- [ ] `_workspaces` migrated per plan

---

## 📞 Support

For issues with migration, check:
1. Log files in `logs/migration-*.log`
2. Master plan: `CORTEX-MIGRATION-MASTER-PLAN.yaml`
3. Rollback: `git checkout CORTEX` (original branch)
