# CORTEX 6.0 Requirements Collection

**Created:** 2026-01-14  
**Updated:** 2026-01-14 (Enhanced with CORTEX 7.0 Vision)  
**Branch:** CORTEX6  
**Purpose:** Comprehensive requirements gathered for CORTEX 7.0 planning

---

## 📊 Summary Statistics

| Metric | Count |
|--------|-------|
| **Total AC-IDs** | 110 |
| **Governance Rules (SKULL)** | 23 |
| **Phases** | 11 |
| **Orchestrators** | 14 (updated) |
| **Categories** | 17 |
| **CORTEX 7.0 Vision Requirements** | 9 major areas |

---

## 🎯 CORTEX 7.0 Vision Requirements (NEW)

The following major architectural requirements have been captured for CORTEX 7.0:

### 1. Intent Management & Clarification Protocol
- **REQ-INTENT-001**: Echo user intent back before execution
- **REQ-INTENT-002**: Structured intent parsing (action, scope, constraints)
- **REQ-INTENT-003**: Executive summary format for intent confirmation

### 2. MasterOrchestrator Central Control
- **REQ-MASTER-001**: Single entry point enforcement
- **REQ-MASTER-002**: Complete orchestration ownership
- **REQ-MASTER-003**: Governance integration workflow
- **REQ-MASTER-004**: Sub-orchestrator routing

### 3. Comprehensive Intelligence Layer (Phase 4)
- **REQ-INTEL-001**: LLM Intent Classifier for ambiguous routing
- **REQ-INTEL-002**: Intelligence Middleware (mistake prevention)
- **REQ-INTEL-003**: Knowledge Graph integration
- **REQ-INTEL-004**: Vision API for multi-modal input

### 4. CORTEX Toolkit via MCP (Multi-Repo Support)
- **REQ-MCP-001**: MCP Server implementation (tools/list, tools/call)
- **REQ-MCP-002**: Multi-Repository Manager (cross-repo operations)
- **REQ-MCP-003**: 5 MCP tool categories (governance, housekeeping, planning, todo, tdd)
- **REQ-MCP-004**: @mcp_tool decorator enforcement (CORE-024)
- **REQ-MCP-005**: Cross-repo search and analysis
- **REQ-MCP-006**: MCP Server Unity (CORE-026)

### 5. Orchestrator Scaffolding System
- **REQ-SCAFFOLD-001**: CLI-based orchestrator creation
- **REQ-SCAFFOLD-002**: Complete scaffolded structure (impl, tests, docs)
- **REQ-SCAFFOLD-003**: Auto-registration with MasterOrchestrator
- **REQ-SCAFFOLD-004**: Custom Orchestrator Loader for dynamic loading
- **REQ-SCAFFOLD-005**: CORE-021 enforcement

### 6. Interactive Planning with AST Analysis
- **REQ-PLAN-001**: Planning Orchestrator v5 (autonomous)
- **REQ-PLAN-002**: 4 plan types (feature, epic, phase, sub-plan)
- **REQ-PLAN-003**: AST-based code analysis
- **REQ-PLAN-004**: Knowledge Graph query during planning
- **REQ-PLAN-005**: 5-phase execution model
- **REQ-PLAN-006**: Duplicate detection
- **REQ-PLAN-007**: TodoManager integration
- **REQ-PLAN-008**: 5 MCP planning tools

### 7. CORTEX LENS - Intelligent Code Analysis
- **REQ-LENS-001**: Multi-language AST parser (6 languages)
- **REQ-LENS-002**: Dependency graph construction
- **REQ-LENS-003**: Git history intelligence
- **REQ-LENS-004**: Knowledge graph storage (SQLite)
- **REQ-LENS-005**: MCP tool exposure
- **REQ-LENS-006**: D3.js visualization dashboard

### 8. Onboarding Orchestrator
- **REQ-ONBOARD-001**: Project discovery workflow
- **REQ-ONBOARD-002**: Technology stack detection
- **REQ-ONBOARD-003**: Architecture pattern recognition
- **REQ-ONBOARD-004**: Auto documentation generation

### 9. Challenge System (CORE-025)
- **REQ-CHALLENGE-001**: Challenge detection engine
- **REQ-CHALLENGE-002**: 4 response levels (BLOCK/ADVISE/ENHANCE/APPROVE)
- **REQ-CHALLENGE-003**: Learning loop for improvement

---

## 📁 Files in This Directory

| File | Format | Purpose |
|------|--------|---------|
| `cortex6-requirements-comprehensive.yaml` | YAML | Complete requirements specification with all details |
| `cortex6-requirements.json` | JSON | Machine-readable requirements for automation |
| `README.md` | Markdown | This documentation file |

---

## 🏗️ Phases Overview

| Phase | Name | AC Count |
|-------|------|----------|
| 1 | Foundation | 30 |
| 1.5 | Security & Audit Extension | 1 |
| 2 | Orchestration Core | 54 |
| 3 | Feature Orchestrators | 1 |
| 4 | Intelligence & Planning | 1 |
| 4.5 | Extended Intelligence | 1 |
| 5 | Analysis & Knowledge | 1 |
| 10 | Production Readiness | 1 |
| 11 | CORTEX LENS | 20 |

---

## 📂 Source Files Reviewed

### Primary SSOT Files
- `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml` - 1006 lines, 110 AC-IDs
- `cortex-brain/cx6-plan/master-plan.yaml` - Phase definitions
- `cortex-brain/tier0/governance/core-rules.yaml` - 1602 lines, 23 SKULL rules
- `cortex-brain/tier1/tracking/progress-tracker.json` - Execution state

### Backup/Analysis Files
- `cortex-brain/cx6-plan-cleanup-backup/analysis/FINAL-RECONCILIATION-SUMMARY.md`
- `cortex-brain/cx6-plan-cleanup-backup/analysis/implementation-inventory.json`
- `cortex-brain/cx6-plan-cleanup-backup/validation/holistic-review.yaml`
- `cortex-brain/cx6-plan-cleanup-backup/validation/phase1-verification-report.yaml`
- `cortex-brain/cx6-plan-cleanup-backup/validation/cx6-requirements-gap-analysis.md`

### Architecture Documentation
- `cortex-brain/cx6-plan/SSOT-ARCHITECTURE.md`
- `.github/copilot-instructions.md`

---

## 📋 Categories by AC Count

| Category | AC Count | Description |
|----------|----------|-------------|
| VALIDATE | 10 | Input validation and hallucination prevention |
| TDD | 10 | Test-Driven Development enforcement |
| SECURITY | 8 | Security layer requirements |
| AUDIT-EVIDENCE | 8 | Audit trail completeness per phase |
| ORCH | 8 | MasterOrchestrator requirements |
| PLAN | 8 | Planning v5 orchestrator |
| ONBOARD | 8 | Onboarding orchestrator |
| AUDIT | 7 | Audit infrastructure |
| LENS | 6 | CORTEX LENS code analysis |
| GOV | 5 | Governance merger |
| METRICS | 5 | Metrics collection |
| ROUTE | 5 | Deterministic routing |
| TODO | 4 | Task management |
| CHALLENGE | 3 | Challenge system |
| EVIDENCE | 3 | Evidence bundler |
| LIFECYCLE | 3 | Orchestrator lifecycle |
| STATE | 3 | State management |
| STS | 3 | Semantic Test Suite |
| TEMPLATE | 3 | Template system |

---

## 🛡️ Governance Rules (SKULL)

All 23 CORE rules enforce production-grade quality:

### Orchestration Lifecycle
- CORE-001: Small Incremental Autonomous Operations
- CORE-006: Phase -2 Setup Verification
- CORE-007: Phase N+1 Teardown + REFACTOR

### Response Formatting
- CORE-002: No Summary File Creation
- CORE-003: Visual Progress Bars Required
- CORE-004: Minimal Continuation Prompt
- CORE-020: No Markdown Work Products

### Portability
- CORE-005: Portable Path Resolution

### Development Workflow
- CORE-008: TDD Mandatory
- CORE-019: TDD-Master Required

### Architecture Integrity
- CORE-009: Plan File Organization
- CORE-010: Script Consolidation
- CORE-014: SOLID Principles
- CORE-018: YAML-First Design
- CORE-021: Orchestrator Scaffolder
- CORE-022: Kebab-Case File Naming
- CORE-024: MCP Tool Decorator
- CORE-026: MCP Server Unity

### Quality Gates
- CORE-011: Type Hints
- CORE-012: Docstrings
- CORE-013: Error Handling
- CORE-015: Import Organization
- CORE-016: Black Formatting
- CORE-023: File-Type Validation

### Security/Privacy
- CORE-017: Strict Governance Enforcement

---

## 🔄 Git History Analysis

Git history from CORTEX6 branch was analyzed:
- **Total commits reviewed:** 100+
- **Feature commits:** Multiple AC implementation commits
- **Key milestones:**
  - Phase 1 Foundation Complete (30/30 ACs)
  - Phase 2 Orchestration Core Complete (54/54 ACs)
  - Phase 11 CORTEX LENS Complete (20/20 ACs)
  - Overall: 110/110 ACs implemented (100%)

---

## 🎯 Usage for CORTEX 7.0

These requirements files serve as the foundation for CORTEX 7.0 planning:

1. **Review AC-IDs** - Identify which requirements carry forward vs. deprecated
2. **Governance Evolution** - Determine new SKULL rules needed
3. **Phase Restructuring** - Reorganize phases for new architecture
4. **Gap Analysis** - Identify missing capabilities for v7.0

---

## 📚 References

- **SSOT Architecture:** `cortex-brain/cx6-plan/SSOT-ARCHITECTURE.md`
- **Copilot Instructions:** `.github/copilot-instructions.md`
- **Core Rules:** `cortex-brain/tier0/governance/core-rules.yaml`
- **AC Registry:** `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml`
