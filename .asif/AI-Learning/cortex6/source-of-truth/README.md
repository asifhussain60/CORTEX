# CORTEX 6.0 - Final Source of Truth

**Version:** 6.0.0 | **Created:** 2026-01-07 | **Author:** Asif Hussain  
**Status:** ✅ ACTIVE - Canonical reference for CORTEX 6.0 greenfield build

---

## 📚 Document Index

This folder contains the complete, authoritative specifications for building CORTEX 6.0 from scratch.

### Core Documents

| File | Purpose | Audience |
|------|---------|----------|
| `00-CORTEX6-MASTER-SOURCE-OF-TRUTH.yaml` | Master spec (governance, architecture, requirements) | Human + Machine |
| `01-EXECUTIVE-OVERVIEW.md` | Business summary, goals, success criteria | Humans |
| `02-COPILOT-BUILD-PROMPT.md` | Clean slate prompt for GitHub Copilot | Machine |

### Human-Readable Documentation (`human-readable/`)

| File | Purpose |
|------|---------|
| `01-governance-framework.md` | 4-category governance explained with examples |
| `02-architecture-overview.md` | System architecture with Mermaid diagrams |
| `03-component-catalog.md` | All 20 components explained |
| `04-multi-repo-strategy.md` | MCP integration, cross-repo workflows |
| `05-todo-intelligence.md` | DAG algorithms, smart scheduling |
| `06-test-harness-guide.md` | Testing strategy, coverage targets |
| `07-deployment-guide.md` | One-click deployment (KISS) |
| `08-implementation-roadmap.md` | 74-day timeline, phases, milestones |

### Machine-Readable Specifications (`machine-readable/`)

| File | Purpose |
|------|---------|
| `01-folder-structure.yaml` | Exact directory tree for empty folder build |
| `02-component-specs.yaml` | 20 components with class signatures, methods |
| `03-database-schema.sql` | SQLite schema (14 tables) |
| `04-interface-contracts.yaml` | APIs, protocols, message formats |
| `05-governance-rules.yaml` | 4-category merge logic, complete rule set |
| `06-mcp-server-spec.yaml` | JSON-RPC 2.0 MCP Server specification |
| `07-test-specifications.yaml` | Test cases, coverage targets |
| `08-deployment-automation.yaml` | One-click deployment scripts |

### Implementation Plan (`implementation-plan/`)

| File | Purpose |
|------|---------|
| `00-BACKUP-MIGRATION.ps1` | PowerShell script to backup existing CORTEX |
| `01-BACKUP-MIGRATION.sh` | Bash script to backup existing CORTEX (macOS/Linux) |
| `02-phase-checklist.md` | 9-phase implementation checklist |
| `03-validation-criteria.yaml` | Success gates per phase |

### Diagrams (`diagrams/`)

| File | Purpose |
|------|---------|
| `01-governance-merge-flow.mmd` | 4-source governance merging |
| `02-system-architecture.mmd` | 6-layer architecture |
| `03-multi-repo-topology.mmd` | MCP Server + repos |
| `04-todo-dag-example.mmd` | DAG visualization |

---

## 🎯 Quick Start

### For Humans
1. Start with `01-EXECUTIVE-OVERVIEW.md` for business context
2. Read `human-readable/01-governance-framework.md` for 4-category governance
3. Review `human-readable/02-architecture-overview.md` for system design

### For GitHub Copilot (Building from Scratch)
1. Run backup script: `implementation-plan/00-BACKUP-MIGRATION.ps1` (Windows) or `.sh` (macOS)
2. Load the build prompt: `02-COPILOT-BUILD-PROMPT.md`
3. Execute 9 phases per `implementation-plan/02-phase-checklist.md`
4. Validate per `implementation-plan/03-validation-criteria.yaml`

---

## 📊 Document Relationships

```
00-CORTEX6-MASTER-SOURCE-OF-TRUTH.yaml    ← CANONICAL (all docs defer to this)
         │
         ├── 01-EXECUTIVE-OVERVIEW.md       ← Human summary
         ├── 02-COPILOT-BUILD-PROMPT.md     ← Machine prompt
         │
         ├── human-readable/                ← Detailed explanations
         │       └── (8 documents)
         │
         ├── machine-readable/              ← Executable specs
         │       └── (8 documents)
         │
         ├── implementation-plan/           ← Build instructions
         │       └── (4 documents)
         │
         └── diagrams/                      ← Visual aids
                 └── (4 Mermaid diagrams)
```

---

## ✅ Completeness Checklist

- [x] Master Source of Truth (governance, architecture, requirements)
- [ ] Executive Overview (in progress)
- [ ] Copilot Build Prompt (in progress)
- [ ] Human-Readable Documentation (8 docs)
- [ ] Machine-Readable Specifications (8 docs)
- [ ] Implementation Plan (4 docs)
- [ ] Diagrams (4 Mermaid files)

**Progress:** 1/25 documents complete

---

## 🔒 Document Authority

**Canonical Source:** `00-CORTEX6-MASTER-SOURCE-OF-TRUTH.yaml`

All other documents in this folder are derived from or support the master source of truth. In case of conflict, the master YAML file takes precedence.

**Change Control:**
- All changes to master source of truth require review
- Version bumps follow semantic versioning
- Change history tracked in document metadata

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
