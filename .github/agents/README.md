# CORTEX Agents

This directory contains all CORTEX agent definitions organized by status.

## 📁 Structure

### `/core` - Active Agents
Current production agents used in CORTEX operations:

- **cortex-review.md** - Code review agent coordinator (v4.0)
- **cortex-review-agents.md** - Review sub-agents detail (8-10 agents)
- **cortex-total-recall.md** - Feature discovery agent (v7.0)
- **cortex-enforcement-agents.md** - Governance enforcement agents
- **cortex-builder.md** - Builder orchestrator agent
- **cortex-planner.md** - Planning agent
- **CORTEX.md** - Master orchestrator agent definition

### `/archived` - Obsolete Agents
Old agent definitions kept for reference only:

- **cortex-vacuum-agents.md** - Vacuum agents (archived post-cleanup)

## 🎯 Agent Catalog

| Agent | File | Purpose |
|-------|------|---------|
| Review Coordinator | cortex-review.md | Coordinates 8+ review sub-agents |
| Review Sub-agents | cortex-review-agents.md | BRIT, HALL, GOV, ASM, DEBT, STATE, ARCH, INTEG |
| Total Recall | cortex-total-recall.md | Feature discovery & recall (4-stage pipeline) |
| Enforcement | cortex-enforcement-agents.md | CORE-030, CORE-035 compliance |
| Builder | cortex-builder.md | Build orchestration |
| Planner | cortex-planner.md | Planning & roadmap |
| Master | CORTEX.md | Master orchestrator (23 orchestrators) |

---

## 🎯 Orchestrator Registry (DatabaseBackedRegistry - SSOT)

**All 23 orchestrators wired via SQLite-backed registry (`.cortex/orchestrator_registry.db`)**

### Core Orchestrators (6/6 Wired)
| Orchestrator | Status | Authority |
|--------------|--------|-----------|
| **MasterOrchestrator** | ✅ WIRED | core |
| **InteractionOrchestrator** | ✅ WIRED | core |
| **IntentRouter** | ✅ WIRED | core |
| **TDDOrchestrator** | ✅ WIRED | core |
| **WorkflowOrchestrator** | ✅ WIRED | core |
| **WrappedTDDOrchestrator** | ✅ WIRED | core |

### Domain Orchestrators (6/6 Wired)
| Orchestrator | Status | Authority |
|--------------|--------|-----------|
| **PlanningOrchestrator** | ✅ WIRED (v2.0 consolidated) | domain |
| **RefactoringOrchestrator** | ✅ WIRED | domain |
| **DomainOrchestrator** | ✅ WIRED | domain |
| **ConversationOrchestrator** | ✅ WIRED | domain |
| **SeleniumPlaywrightOrchestrator** | ✅ WIRED | domain |
| **DocumentationOrchestrator** | ✅ WIRED | domain |

### Support Orchestrators (11/11 Wired)
| Orchestrator | Status | Authority |
|--------------|--------|-----------|
| **OnboardingOrchestrator** | ✅ WIRED | support |
| **ToolDiscoveryOrchestrator** | ✅ WIRED | support |
| **UpgradeOrchestrator** | ✅ WIRED | support |
| **RollbackOrchestrator** | ✅ WIRED | support |
| **SetupOrchestrator** | ✅ WIRED | support |
| **ComposedOrchestrator** | ✅ WIRED | support |
| **OrchestratorBootstrap** | ✅ WIRED | support |
| **DoRApprovalGate** | ✅ WIRED | support |
| **LENSSynthesis** | ✅ WIRED | support |
| **GovernanceRegistry** | ✅ WIRED | support |
| **KnowledgeRepository** | ✅ WIRED | support |

**Registry Authority:** AC-PERMANENT-FIX-009 (DatabaseBackedRegistry)  
**Wiring Entry Point:** `cortex.orchestrators.bootstrap.OrchestratorBootstrap.bootstrap()`  
**Verification:** `cortex/orchestrators/core/database_registry.py:DatabaseBackedRegistry.get_wiring_statistics()`

## 📋 Status

✅ **Deduplication Complete**:
- Single agent definitions per role
- No duplicates (old versions removed/archived)
- Clear hierarchy: Master → Coordinators → Sub-agents

✅ **Organization**:
- `/core/` contains all active agents
- `/archived/` for old versions (currently has vacuum-agents only)

## 🔄 Adding New Agents

1. Create in `/core/` for active agents
2. Add to this README and catalog
3. Old versions → `/archived/` (if needed for reference)
4. Update Master CORTEX.md if adding orchestrator

---
**Last Updated:** 2026-01-25
