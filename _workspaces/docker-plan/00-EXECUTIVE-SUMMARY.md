# CORTEX Docker-First Architecture Migration
## Executive Summary

**Version:** 2.0  
**Date:** 2026-01-27  
**Author:** Asif Hussain  
**Status:** APPROVED  

> **📋 MASTER PLAN:** See `CORTEX-MIGRATION-MASTER-PLAN.yaml` for complete execution details.

---

## 🎯 Objective

Create a clean, Docker-first CORTEX deployment that:
- Eliminates ALL wiring drift permanently
- Serves 100-500+ users via single MCP server
- Preserves ALL valuable enterprise tooling
- Uses Git-backed YAML as single wiring source
- Entry point remains `/CORTEX` for users
- Runs in new clean git branch

---

## 🔄 Approach: SUBTRACTION (Not Cherry-Pick)

**Why Subtraction is Better:**
- Preserves all import chains automatically
- Validates what you're removing, not gambling on inclusions
- Test suite runs after each deletion batch
- Rollback is trivial (`git checkout`)

---

## 📊 Migration Summary

| Metric | Current Branch | New Clean Branch |
|--------|----------------|------------------|
| **Python Files** | 1,592 | ~500 (essential only) |
| **Test Files** | 500 | ~200 (applicable only) |
| **MD Files** | 753 | ~20 (essential only) |
| **Wiring Systems** | 7 competing | 1 (Git-backed YAML) |
| **Database Files** | 5+ | 0 (ephemeral only) |
| **Docker Ready** | No | Yes |
| **MCP Server** | Exists | Enhanced + Health |
| **Timeline** | - | 10 days |

---

## 📦 What Gets Preserved (Subtraction Approach)

### ✅ KEEP: Enterprise-Grade Tooling
- Enhanced Audit Logger (full chain)
- Circuit Breaker patterns
- Security infrastructure
- Rate limiting
- Prometheus metrics
- Alert manager

### ✅ KEEP: 23 Core Orchestrators
- 6 Core orchestrators
- 6 Domain orchestrators  
- 11 Support orchestrators

### ✅ KEEP: Intelligence Systems
- Intent Router (classifier, fuzzy matching)
- LENS Synthesis
- Challenge Engine
- Knowledge Graph
- Git History Analyzer

### ✅ KEEP: MCP Infrastructure
- MCP Server (enhanced)
- 23 MCP Adapters
- Tool catalog
- Compliance checker

### ✅ KEEP: Governance
- Tier 0 rules (CORE-001 to CORE-040)
- Tier 3 knowledge YAMLs (35+ files)
- Policy enforcement

### ❌ REMOVE: Legacy/Cruft
- 7 competing wiring systems
- All .db files
- All AC-* documentation
- All COMPLETION reports
- _backups/ directory
- _archive/ directories
- Duplicate *_enhanced.py files

---

## 🏗️ New Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  CORTEX Docker Container                    │
│                                                             │
│  Entry Point: /CORTEX (MCP Server on port 8443)            │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Git-Backed Wiring (YAML Specifications)             │   │
│  │ - Loads once at container startup                   │   │
│  │ - Zero drift, zero unwiring possible                │   │
│  │ - All 23 orchestrators wired deterministically      │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ↓                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ MCP Server (FastAPI + Uvicorn)                      │   │
│  │ - /mcp/execute                                       │   │
│  │ - /mcp/tools                                         │   │
│  │ - /health                                            │   │
│  │ - /metrics (Prometheus)                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          ↑
                    100-500 VS Code
                       Clients
```

---

## 📋 Execution Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| 1 | Day 1 | New branch + directory structure |
| 2 | Day 1-2 | Core infrastructure cherry-pick |
| 3 | Day 2 | Orchestrators cherry-pick |
| 4 | Day 2-3 | MCP server enhancement |
| 5 | Day 3 | New Git-backed wiring system |
| 6 | Day 3-4 | Docker infrastructure |
| 7 | Day 4 | Wiring tests (extensive) |
| 8 | Day 4-5 | Integration tests |
| 9 | Day 5 | Documentation + validation |

---

## 🔗 Plan Documents

1. `01-COMPONENT-INVENTORY.md` - Complete list of components to cherry-pick
2. `02-DIRECTORY-STRUCTURE.md` - New clean directory layout
3. `03-WIRING-SYSTEM.md` - Git-backed wiring specification
4. `04-DOCKER-SETUP.md` - Container configuration
5. `05-WIRING-TESTS.md` - Comprehensive wiring test plan
6. `06-MIGRATION-SCRIPT.md` - Automated migration commands
7. `07-VALIDATION-CHECKLIST.md` - Final verification steps
