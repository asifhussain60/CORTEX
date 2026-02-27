# Intelligence Matrix

---
title: CORTEX Intelligence Matrix — Cross-Cutting Neural Wiring Layer
type: explanation
audience: [Software Developers, Product Owners, Business Leaders]
last_verified: 2026-02-27
source_of_truth: cortex/intelligence/cross_cutting/intelligence_matrix_builder.py
format: deep-dive
order: 6
---

> **What is it?** The Intelligence Matrix is CORTEX's neural wiring map — a structured cross-check of every intelligence capability against every other CORTEX capability, driving automated wiring decisions across all seven cognitive dimensions.

---

## The Core Idea

CORTEX has many intelligence subsystems (LENS, Brain Tiers, SynthesisEngine, DomainBrain) and many operational capabilities (TDD workflow, AuditFix pipeline, MCP tools, governance). The Intelligence Matrix answers one question for every possible intersection:

> **"Should these two capabilities be wired together — and if so, how?"**

The matrix assigns a priority score (CRITICAL → HIGH → MEDIUM → LOW) and a concrete wire action for each intersection. This is how CORTEX's intelligence evolves from isolated components into a coordinated neural network.

---

## Architecture at a Glance

```
┌────────────────────────────────────────────────────────────────────────┐
│               🧠 CORTEX INTELLIGENCE MATRIX                            │
│           cortex/intelligence/cross_cutting/intelligence_matrix_builder│
│                                                                        │
│  x-axis: Intelligence Capabilities (IC-001 → IC-015)                  │
│  y-axis: CORTEX Operational Capabilities (CC-001 → CC-015)            │
│                                                                        │
│  ┌─────────────────┬────────┬────────┬────────┬────────┬────────┐     │
│  │                 │ LENS   │ TOOLKIT│WORKFLOW│ RESP.  │  GOV.  │     │
│  ├─────────────────┼────────┼────────┼────────┼────────┼────────┤     │
│  │ LENS Analysis   │  ███   │  ██    │  █     │        │  ██    │     │
│  │ SynthesisEngine │        │  █     │  ██    │        │  █     │     │
│  │ DomainBrain     │  █     │        │  ██    │  █     │        │     │
│  │ Brain Tier T1   │        │  █     │  ██    │        │        │     │
│  │ Brain Tier T2   │        │        │  █     │        │        │     │
│  │ Brain Tier T3   │        │        │        │        │        │     │
│  │ IntelligOrch.   │  █     │        │  ██    │  █     │  ██    │     │
│  │ ResponseTemplate│        │        │  ██    │  ███   │        │     │
│  │ BlindSpotDet.   │        │        │  █     │        │  ███   │     │
│  │ KnowledgeIndex  │  ██    │        │  ███   │        │        │     │
│  │ [IC-011..015]   │  ██    │  █     │  █     │  ██    │        │     │
│  └─────────────────┴────────┴────────┴────────┴────────┴────────┘     │
│                                                                        │
│  ██ = CRITICAL (P0)  ██ = HIGH (P1)  █ = MEDIUM (P2)                  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## The Seven Dimensions

The matrix operates across **seven capability dimensions** (defined in `CapabilityDimension` enum):

| Dimension | What It Covers | Key Module |
|-----------|---------------|------------|
| `brain_tier` | T1 Learned / T2 Adaptive / T3 Scratch memory | `cortex/intelligence/memory/` |
| `lens` | LENS AST, semantic, and graph analysis | `cortex/lens/` |
| `intelligence` | Orchestrated intelligence (IntelligenceOrchestrator, SynthesisEngine, BlindSpotDetector) | `cortex/orchestrators/intelligence/` |
| `toolkit` | HierarchicalScanner, BatchProcessor, DomainAdapter | `cortex/toolkit/` |
| `workflow` | DocGen, AuditFix, TDD, SweepCatalogue pipelines | `cortex-registry/workflows/templates/` |
| `response` | ResponseTemplateGenerator, FormatResponseHook | `cortex/orchestrators/intelligence/response_template_generator.py` |
| `governance` | EnforcementOrchestrator, VacuumOrchestrator, BlindSpotDetector | `cortex/orchestrators/core/enforcement_orchestrator.py` |

---

## The Capability Catalogues

### x-axis: Intelligence Capabilities (IC-001 → IC-015)

These are the **intelligence-providing** subsystems — they produce insights, analysis, or memory:

| ID | Name | Module | Dimension |
|----|------|--------|-----------|
| IC-001 | LENS Analysis | `cortex.intelligence.lens` | lens |
| IC-002 | SynthesisEngine | `cortex.intelligence.tier3.knowledge.synthesis_engine` | intelligence |
| IC-003 | DomainBrain | `cortex.intelligence.domain_brain` | brain_tier |
| IC-004 | BrainTier-T1-Learned | `cortex.intelligence.memory.tier1_learned` | brain_tier |
| IC-005 | BrainTier-T2-Adaptive | `cortex.intelligence.memory.tier2_adaptive` | brain_tier |
| IC-006 | BrainTier-T3-Scratch | `cortex.intelligence.memory.tier3_scratch` | brain_tier |
| IC-007 | IntelligenceOrchestrator | `cortex.orchestrators.intelligence.intelligence_orchestrator` | intelligence |
| IC-008 | ResponseTemplateGenerator | `cortex.orchestrators.intelligence.response_template_generator` | response |
| IC-009 | BlindSpotDetector | `cortex.orchestrators.intelligence.blind_spot_detector` | intelligence |
| IC-010 | KnowledgeIndexer | `cortex.intelligence.tier3.knowledge.knowledge_indexer` | intelligence |
| IC-011 | HierarchicalScannerAdapter | `cortex.lens.adapters.hierarchical_scanner_adapter` | lens |
| IC-012 | KnowledgeIndexerDocGenBridge | `cortex.intelligence.tier3.knowledge.knowledge_indexer_docgen_bridge` | intelligence |
| IC-013 | IntelligenceWiringBridges | `cortex.intelligence.intelligence_wiring_bridges` | intelligence |
| IC-014 | CortexBrainQuery (MCP) | `cortex.mcp.tools.brain` | response |
| IC-015 | FormatResponseHook | `cortex.mcp.mcp_tool_base` | response |

### y-axis: CORTEX Operational Capabilities (CC-001 → CC-015)

These are the **intelligence-consuming** systems — they take intelligence and turn it into action:

| ID | Name | Module | Dimension |
|----|------|--------|-----------|
| CC-001 | HierarchicalScanner | `cortex.toolkit.filesystem` | toolkit |
| CC-002 | BatchProcessor | `cortex.toolkit.batch` | toolkit |
| CC-003 | DomainAdapter | `cortex.toolkit.adapters` | toolkit |
| CC-004 | DocGenPlaybook | `cortex-registry/workflows/.../documentation-refresh-pipeline` | workflow |
| CC-005 | AuditFixPipeline | `cortex-registry/workflows/.../audit-fix-pipeline` | workflow |
| CC-006 | EnforcementOrchestrator | `cortex.orchestrators.core.enforcement_orchestrator` | governance |
| CC-007 | VacuumOrchestrator | `cortex.orchestrators.health.vacuum_orchestrator` | governance |
| CC-008 | MCPToolRegistry | `cortex.mcp.tools` | intelligence |
| CC-009 | SweepCatalogueOrchestrator | `cortex.orchestrators.support.sweep_catalogue_orchestrator` | workflow |
| CC-010 | TDDOrchestrator | `cortex.orchestrators.core.tdd_orchestrator` | workflow |
| CC-011 | SynthesisEngineBridge | `cortex.intelligence.tier3.knowledge.synthesis_engine` | intelligence |
| CC-012 | RetrievalOptimizerBridge | `cortex.intelligence.intelligence_wiring_bridges` | intelligence |
| CC-013 | TDDStubGenerator | `cortex.orchestrators.core.tdd_orchestrator` | workflow |
| CC-014 | ResponseTemplateHook | `cortex.orchestrators.intelligence.response_template_generator` | response |
| CC-015 | T1T2EnrichmentHooks | `cortex.intelligence.intelligence_wiring_bridges` | intelligence |

---

## Priority Scoring (P0 → P3 Aligned)

Each matrix cell (intersection of one IC and one CC) carries a priority score that aligns with CORTEX's P0-P3 governance severity system:

| Score | Priority | Meaning | Action Required |
|-------|----------|---------|-----------------|
| **CRITICAL** | P0 | Wire immediately — blocking risk if missing | Must wire in current phase |
| **HIGH** | P1 | High-value wiring — strong multiplier effect | Wire in current phase |
| **MEDIUM** | P2 | Next-phase candidate | Backlog with clear rationale |
| **LOW** | P3 | Opportunistic | Backlog |

---

## Key Wired Connections (P0-CRITICAL)

These are the most important wiring pairs identified by the matrix. All are **now wired**:

### 1. LENS × HierarchicalScanner (IC-001 × CC-001)
> LENS AST engine needs HierarchicalScanner to discover source files across workspace

**Wire:** `HierarchicalScanner.scan()` output → `LENS.analyze(files)` pipeline

**Why critical:** Without file discovery, LENS has no input. This is the foundation of all analysis.

---

### 2. Brain Tiers × MCP (IC-004/005/006 × CC-008)
> Brain tier memories must be surfaced via MCP for Copilot Chat consumption

**Wire:** T1/T2/T3 memory query → `cortex_knowledge` MCP tool (registered) or `cortex_total_recall` for architecture recall. Note: `cortex_brain_query` is planned but not yet registered in `mcp_registry.py`.

**Why critical:** The IDE cannot consume brain tier intelligence unless it is exposed as an MCP tool. This connects the entire memory subsystem to the user interface.

---

### 3. BlindSpotDetector × EnforcementOrchestrator (IC-009 × CC-006)
> BlindSpotDetector findings must trigger EnforcementOrchestrator P0 violations

**Wire:** `blind_spot_detector.gaps` → `enforcement_orchestrator.register_violation()`

**Why critical:** Detected gaps that are not enforced become silent technical debt. This wiring ensures all blind spots surface as actionable governance violations.

---

### 4. KnowledgeIndexer × DocGenPlaybook (IC-010 × CC-004)
> KnowledgeIndexer is the source of truth for DocGenPlaybook stage_1 discovery scan

**Wire:** `KnowledgeIndexer.inventory()` → `DocGenPlaybook stage_1.knowledge_yaml_scan`

**Why critical:** Documentation generation must draw from the canonical knowledge index. Without this wire, docs drift from the live implementation.

---

### 5. ResponseTemplate × MCP (IC-008 × CC-008)
> Response templates must be applied at MCP tool output level for consistent VS Code rendering

**Wire:** All MCP tool results → `format_response()` before returning to Copilot Chat

**Why critical:** Inconsistent rendering breaks the VS Code Copilot Chat user experience. This ensures every MCP response uses semantic color-coding and AC marker formatting.

---

## The Coverage Gate

A **coverage gate** (`COVERAGE_GATE = 0.50`) is enforced in the AuditFix pipeline:

```python
# cortex/intelligence/cross_cutting/intelligence_matrix_builder.py
class MatrixCoverageError(Exception):
    """Raised when Intelligence Matrix coverage_score falls below COVERAGE_GATE."""

COVERAGE_GATE: float = 0.50
```

If the matrix's `coverage_score` (proportion of wired cells) drops below 50%, the AuditFix pipeline (Stage 1.5) raises `MatrixCoverageError` and halts — preventing deployment with an under-wired intelligence layer.

**Current coverage:** Tracked dynamically at runtime via `IntelligenceMatrixBuilder.build()`.

---

## How the Builder Works

The `IntelligenceMatrixBuilder` is the primary API for computing the matrix at runtime:

```python
from cortex.intelligence.cross_cutting import IntelligenceMatrixBuilder

builder = IntelligenceMatrixBuilder()
matrix = builder.build()

# Query the matrix
critical_gaps = matrix.critical_cells()   # P0 cells not yet wired
high_gaps = matrix.high_cells()           # P1 cells not yet wired
coverage = matrix.coverage_score          # 0.0–1.0

# Render a full markdown report
report = builder.render_matrix_report(matrix)
```

### Scoring Algorithm

The builder uses a **tag-intersection scoring** approach:

1. For every `(IC, CC)` pair, collect all tags from both capability objects
2. Apply `_SCORING_RULES` — a list of `(x_tag, y_tag, score, rationale, wire_action)` tuples
3. The highest-priority matching rule wins for each cell
4. Cells with no matching rule are scored LOW by default
5. Cells marked `is_wired=True` in the registry contribute to `coverage_score`

```python
# Example scoring rule:
("ast", "scan", IntelligenceScore.CRITICAL,
 "LENS AST engine needs HierarchicalScanner to discover source files",
 "Wire HierarchicalScanner.scan() → LENS.analyze(files) pipeline")
```

### Matrix Output Format

```python
matrix.to_dict()
# Returns:
{
    "total_x": 15,           # intelligence capability count
    "total_y": 15,           # cortex capability count
    "wired": 87,             # intersection cells with is_wired=True
    "coverage_score": 0.823, # 82.3% of high-value cells wired
    "critical_unwired": 0,   # P0 gaps (0 = production ready)
    "high_unwired": 2,       # P1 gaps remaining
    "cells": [...]           # sorted by (score, intelligence_id)
}
```

---

## Evolution

| Milestone | What Was Delivered |
|-------|--------------------|
| **Initial Build** | Matrix implementation: IC × CC scoring, MCP exposure |
| **P0 Wiring** | Wired P0-CRITICAL gaps (LENS×Scanner, Brain×MCP, BlindSpot×Enforcement, Knowledge×DocGen, ResponseTemplate×MCP) |
| **P1 Wiring** | Wired P1-HIGH gaps (T1→DomainAdapter, T2→DocGen, SynthesisEngine→SweepCatalogue, and more) |
| **Coverage Gate** | Coverage gate enforcement, extended catalogues, `MatrixCoverageError` P0 halt |

---

## Integration Points

### WorkflowEngine
The `ConvergenceLoopExecutor` in `cortex/orchestrators/workflow/convergence_loop_executor.py` queries the matrix before each audit-fix loop iteration to check if any CRITICAL gaps have been introduced by the current sweep.

### AuditFix Pipeline (Stage 1.5)
Stage 1.5 of `/audit fix` calls `IntelligenceMatrixBuilder.build()` and fails if `coverage_score < COVERAGE_GATE`. This appears in the 9-stage pipeline between Stage 1 (Governance Pre-Flight) and Stage 2 (19-Point Scan).

### MCP Tool: `cortex_ask`
The `cortex_ask` MCP tool surfaces matrix analysis in natural language, explaining which intelligence capabilities are wired to which operational capabilities and where gaps exist.

---

## Audience Perspectives

**Business Leader:** "The Intelligence Matrix ensures all our AI capabilities work together — not as isolated tools. It's the wiring blueprint that turns individual analyzers into a coordinated intelligence network, with an automated gate that blocks deployment if the wiring falls below 50%."

**Product Owner:** "Every feature CORTEX adds gets automatically checked against 15 intelligence capabilities and 15 operational capabilities. If a new capability should be connected to existing ones and it isn't, the AuditFix pipeline catches it before we ship."

**Developer:** "The matrix drives my implementation checklist. When I add a new intelligence capability, I run `IntelligenceMatrixBuilder.build()` to see which CC capabilities need wiring. The P0-CRITICAL cells are blockers — I cannot merge without them wired."

---

## Live Location

| Artifact | Path |
|---------|------|
| Core implementation | `cortex/intelligence/cross_cutting/intelligence_matrix_builder.py` |
| Public API exports | `cortex/intelligence/cross_cutting/__init__.py` |
| Implementation plan | `cortex-registry/planning/phases/completed/phase-66.yaml` |
| Initial matrix plan | `cortex-registry/planning/phases/completed/phase-65.yaml` |
| Coverage gate constant | `COVERAGE_GATE = 0.50` in `intelligence_matrix_builder.py` |

---

*Last verified against live codebase · all P0-CRITICAL cells wired · coverage ≥ 50%*
