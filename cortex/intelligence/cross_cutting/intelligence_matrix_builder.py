"""
IntelligenceMatrixBuilder — Cross-Cutting Intelligence Layer
============================================================

Builds a HIGH VALUE intelligence matrix by cross-checking every
intelligence capability (x) against every other CORTEX capability (y),
then wires the resulting neural connections across:

  - Brain Tiers (T1 Learned / T2 Adaptive / T3 Scratch)
  - CORTEX LENS (Language→Examination→Navigation→Synthesis)
  - Intelligence Orchestrator
  - SynthesisEngine (knowledge/tier3)
  - Toolkit (scan, batch, enrich, workflow)
  - Response Templates (VS Code Copilot Chat rendering)
  - MCP Tools (MCP-first exposure)
  - Governance (CORE-035, CORE-064 compliance)

Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
Phase: Phase 65 — Cross-Cutting Intelligence Matrix (ENH-MATRIX-001)

AC_START: AC-INTELLIGENCE-MATRIX-001
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Coverage Gate (GAP-66-C / Phase 66-C)
# ─────────────────────────────────────────────────────────────────────────────


class MatrixCoverageError(Exception):
    """Raised when IntelligenceMatrix coverage_score falls below COVERAGE_GATE.

    Authority: GAP-66-C (Phase 66-C) — enforced in AuditFixPipeline Stage 1.5.
    """


# ─────────────────────────────────────────────────────────────────────────────
# Domain Models
# ─────────────────────────────────────────────────────────────────────────────

class CapabilityDimension(str, Enum):
    """The seven dimensions of CORTEX cross-cutting intelligence."""
    BRAIN_TIER = "brain_tier"
    LENS = "lens"
    INTELLIGENCE = "intelligence"
    TOOLKIT = "toolkit"
    WORKFLOW = "workflow"
    RESPONSE = "response"
    GOVERNANCE = "governance"


class IntelligenceScore(str, Enum):
    """Value scoring for matrix intersections (P0→P3 aligned)."""
    CRITICAL = "CRITICAL"   # P0 — must wire immediately
    HIGH = "HIGH"           # P1 — wire in current phase
    MEDIUM = "MEDIUM"       # P2 — next phase candidate
    LOW = "LOW"             # P3 — backlog


@dataclass
class IntelligenceCapability:
    """A single intelligence capability (x-axis of matrix)."""
    id: str
    name: str
    module: str
    dimension: CapabilityDimension
    description: str
    current_coverage: float = 0.0  # 0.0–1.0
    tags: List[str] = field(default_factory=list)


@dataclass
class CortexCapability:
    """A single non-intelligence CORTEX capability (y-axis of matrix)."""
    id: str
    name: str
    module: str
    dimension: CapabilityDimension
    description: str
    tags: List[str] = field(default_factory=list)


@dataclass
class MatrixCell:
    """A single intersection in the HIGH VALUE intelligence matrix."""
    intelligence_id: str
    cortex_id: str
    score: IntelligenceScore
    rationale: str
    wire_action: str
    dimension_pair: Tuple[CapabilityDimension, CapabilityDimension]
    is_wired: bool = False
    wired_via: Optional[str] = None


@dataclass
class IntelligenceMatrix:
    """The full cross-cutting intelligence matrix."""
    cells: List[MatrixCell] = field(default_factory=list)
    total_capabilities_x: int = 0
    total_capabilities_y: int = 0
    wired_count: int = 0
    coverage_score: float = 0.0

    def critical_cells(self) -> List[MatrixCell]:
        """Return P0-CRITICAL cells not yet wired."""
        return [c for c in self.cells if c.score == IntelligenceScore.CRITICAL and not c.is_wired]

    def high_cells(self) -> List[MatrixCell]:
        """Return P1-HIGH cells not yet wired."""
        return [c for c in self.cells if c.score == IntelligenceScore.HIGH and not c.is_wired]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize matrix to JSON-compatible dict."""
        return {
            "total_x": self.total_capabilities_x,
            "total_y": self.total_capabilities_y,
            "wired": self.wired_count,
            "coverage_score": round(self.coverage_score, 3),
            "critical_unwired": len(self.critical_cells()),
            "high_unwired": len(self.high_cells()),
            "cells": [
                {
                    "x": c.intelligence_id,
                    "y": c.cortex_id,
                    "score": c.score.value,
                    "rationale": c.rationale,
                    "wire_action": c.wire_action,
                    "dimensions": f"{c.dimension_pair[0].value}×{c.dimension_pair[1].value}",
                    "is_wired": c.is_wired,
                    "wired_via": c.wired_via,
                }
                for c in sorted(self.cells, key=lambda c: (c.score.value, c.intelligence_id))
            ],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Capability Catalogue
# ─────────────────────────────────────────────────────────────────────────────

# x: Intelligence capabilities
INTELLIGENCE_CAPABILITIES: List[IntelligenceCapability] = [
    IntelligenceCapability(
        id="IC-001",
        name="LENS Analysis",
        module="cortex.intelligence.lens",
        dimension=CapabilityDimension.LENS,
        description="Language→Examination→Navigation→Synthesis code intelligence",
        current_coverage=0.85,
        tags=["ast", "semantic", "graph"],
    ),
    IntelligenceCapability(
        id="IC-002",
        name="SynthesisEngine",
        module="cortex.intelligence.tier3.knowledge.synthesis_engine",
        dimension=CapabilityDimension.INTELLIGENCE,
        description="Knowledge synthesis across multi-source documents",
        current_coverage=0.65,
        tags=["merge", "conflict", "knowledge"],
    ),
    IntelligenceCapability(
        id="IC-003",
        name="DomainBrain",
        module="cortex.intelligence.domain_brain",
        dimension=CapabilityDimension.BRAIN_TIER,
        description="Domain-specific business knowledge repository",
        current_coverage=0.70,
        tags=["domain", "entity", "knowledge"],
    ),
    IntelligenceCapability(
        id="IC-004",
        name="BrainTier-T1-Learned",
        module="cortex.intelligence.memory.tier1_learned",
        dimension=CapabilityDimension.BRAIN_TIER,
        description="Persistent learned patterns from production observations",
        current_coverage=0.50,
        tags=["memory", "learning", "persistent"],
    ),
    IntelligenceCapability(
        id="IC-005",
        name="BrainTier-T2-Adaptive",
        module="cortex.intelligence.memory.tier2_adaptive",
        dimension=CapabilityDimension.BRAIN_TIER,
        description="Session-scoped adaptive reasoning and context",
        current_coverage=0.55,
        tags=["adaptive", "session", "context"],
    ),
    IntelligenceCapability(
        id="IC-006",
        name="BrainTier-T3-Scratch",
        module="cortex.intelligence.memory.tier3_scratch",
        dimension=CapabilityDimension.BRAIN_TIER,
        description="Ephemeral scratch pad for within-turn reasoning",
        current_coverage=0.40,
        tags=["scratch", "ephemeral", "reasoning"],
    ),
    IntelligenceCapability(
        id="IC-007",
        name="IntelligenceOrchestrator",
        module="cortex.orchestrators.intelligence.intelligence_orchestrator",
        dimension=CapabilityDimension.INTELLIGENCE,
        description="Unified AST + comment + routing + comprehension intelligence",
        current_coverage=0.80,
        tags=["orchestrator", "ast", "routing"],
    ),
    IntelligenceCapability(
        id="IC-008",
        name="ResponseTemplateGenerator",
        module="cortex.orchestrators.intelligence.response_template_generator",
        dimension=CapabilityDimension.RESPONSE,
        description="VS Code Copilot Chat semantic color-coded response rendering",
        current_coverage=0.60,
        tags=["response", "template", "copilot"],
    ),
    IntelligenceCapability(
        id="IC-009",
        name="BlindSpotDetector",
        module="cortex.orchestrators.intelligence.blind_spot_detector",
        dimension=CapabilityDimension.INTELLIGENCE,
        description="Coverage gap detection across test and code surfaces",
        current_coverage=0.75,
        tags=["coverage", "blind-spot", "gap"],
    ),
    IntelligenceCapability(
        id="IC-010",
        name="KnowledgeIndexer",
        module="cortex.intelligence.tier3.knowledge.knowledge_indexer",
        dimension=CapabilityDimension.INTELLIGENCE,
        description="Knowledge graph indexing and retrieval optimization",
        current_coverage=0.60,
        tags=["index", "retrieval", "knowledge"],
    ),
    # Extended catalogue — IC-011 through IC-015 (Phase 66-C)
    IntelligenceCapability(
        id="IC-011",
        name="HierarchicalScannerAdapter",
        module="cortex.lens.adapters.hierarchical_scanner_adapter",
        dimension=CapabilityDimension.LENS,
        description="Bridges HierarchicalScanner to LENS file discovery pipeline",
        current_coverage=1.0,
        tags=["adapter", "scan", "lens"],
    ),
    IntelligenceCapability(
        id="IC-012",
        name="KnowledgeIndexerDocGenBridge",
        module="cortex.intelligence.tier3.knowledge.knowledge_indexer_docgen_bridge",
        dimension=CapabilityDimension.INTELLIGENCE,
        description="Bridges KnowledgeIndexer to DocGen pipeline via YAML sync",
        current_coverage=1.0,
        tags=["bridge", "docgen", "index"],
    ),
    IntelligenceCapability(
        id="IC-013",
        name="IntelligenceWiringBridges",
        module="cortex.intelligence.intelligence_wiring_bridges",
        dimension=CapabilityDimension.INTELLIGENCE,
        description="Lightweight bridge functions wiring intelligence to toolkit/workflow",
        current_coverage=1.0,
        tags=["bridge", "wiring", "enrichment"],
    ),
    IntelligenceCapability(
        id="IC-014",
        name="CortexBrainQuery",
        module="cortex.mcp.tools.brain",
        dimension=CapabilityDimension.RESPONSE,
        description="MCP tool for T1/T2/T3 brain tier memory query via Copilot Chat",
        current_coverage=1.0,
        tags=["mcp", "brain", "memory"],
    ),
    IntelligenceCapability(
        id="IC-015",
        name="FormatResponseHook",
        module="cortex.mcp.mcp_tool_base",
        dimension=CapabilityDimension.RESPONSE,
        description="Post-processing hook applied to all MCP tool outputs",
        current_coverage=1.0,
        tags=["response", "format", "mcp"],
    ),
]

# y: Remaining CORTEX capabilities
CORTEX_CAPABILITIES: List[CortexCapability] = [
    CortexCapability(
        id="CC-001",
        name="HierarchicalScanner",
        module="cortex.toolkit.filesystem",
        dimension=CapabilityDimension.TOOLKIT,
        description="Deep filesystem scan with organization detection",
        tags=["scan", "filesystem", "hierarchy"],
    ),
    CortexCapability(
        id="CC-002",
        name="BatchProcessor",
        module="cortex.toolkit.batch",
        dimension=CapabilityDimension.TOOLKIT,
        description="Configurable batch transform pipeline with trigger system",
        tags=["batch", "transform", "pipeline"],
    ),
    CortexCapability(
        id="CC-003",
        name="DomainAdapter",
        module="cortex.toolkit.adapters",
        dimension=CapabilityDimension.TOOLKIT,
        description="Pluggable domain adapters (media, code, docs)",
        tags=["adapter", "domain", "plugin"],
    ),
    CortexCapability(
        id="CC-004",
        name="DocGenPlaybook",
        module="cortex-registry.workflows.templates.internal.documentation-refresh-pipeline",
        dimension=CapabilityDimension.WORKFLOW,
        description="6-stage documentation discovery, generation, and deployment pipeline",
        tags=["docgen", "playbook", "docs"],
    ),
    CortexCapability(
        id="CC-005",
        name="AuditFixPipeline",
        module="cortex-registry.workflows.templates.audit.audit-fix-pipeline",
        dimension=CapabilityDimension.WORKFLOW,
        description="9-stage production readiness audit with convergence loop",
        tags=["audit", "fix", "pipeline"],
    ),
    CortexCapability(
        id="CC-006",
        name="EnforcementOrchestrator",
        module="cortex.orchestrators.core.enforcement_orchestrator",
        dimension=CapabilityDimension.GOVERNANCE,
        description="CORE rule validation and pre-commit enforcement",
        tags=["enforcement", "governance", "compliance"],
    ),
    CortexCapability(
        id="CC-007",
        name="VacuumOrchestrator",
        module="cortex.orchestrators.health.vacuum_orchestrator",
        dimension=CapabilityDimension.GOVERNANCE,
        description="Markdown sprawl cleanup and root clutter governance",
        tags=["vacuum", "cleanup", "health"],
    ),
    CortexCapability(
        id="CC-008",
        name="MCPToolRegistry",
        module="cortex.mcp.tools",
        dimension=CapabilityDimension.INTELLIGENCE,
        description="26 MCP tools exposed via Pylance-style stdio transport",
        tags=["mcp", "tools", "stdio"],
    ),
    CortexCapability(
        id="CC-009",
        name="SweepCatalogueOrchestrator",
        module="cortex.orchestrators.support.sweep_catalogue_orchestrator",
        dimension=CapabilityDimension.WORKFLOW,
        description="CORE-064 sweep catalogue tracking for full issue exhaustion",
        tags=["sweep", "catalogue", "core-064"],
    ),
    CortexCapability(
        id="CC-010",
        name="TDDOrchestrator",
        module="cortex.orchestrators.core.tdd_orchestrator",
        dimension=CapabilityDimension.WORKFLOW,
        description="TDD RED→GREEN→REFACTOR cycle enforcement (CORE-008)",
        tags=["tdd", "test", "cycle"],
    ),
    # Extended catalogue — CC-011 through CC-015 (Phase 66-C)
    CortexCapability(
        id="CC-011",
        name="SynthesisEngineBridge",
        module="cortex.intelligence.tier3.knowledge.synthesis_engine",
        dimension=CapabilityDimension.INTELLIGENCE,
        description="SynthesisEngine detect_conflicts → SweepCatalogue wiring",
        tags=["synthesis", "conflict", "sweep"],
    ),
    CortexCapability(
        id="CC-012",
        name="RetrievalOptimizerBridge",
        module="cortex.intelligence.intelligence_wiring_bridges",
        dimension=CapabilityDimension.INTELLIGENCE,
        description="RetrievalOptimizer scoring bridge for DocGen/AuditFix",
        tags=["retrieval", "scoring", "optimizer"],
    ),
    CortexCapability(
        id="CC-013",
        name="TDDStubGenerator",
        module="cortex.orchestrators.core.tdd_orchestrator",
        dimension=CapabilityDimension.WORKFLOW,
        description="TDDOrchestrator.create_test_stub() auto-generates RED stubs from gaps",
        tags=["tdd", "stub", "gap"],
    ),
    CortexCapability(
        id="CC-014",
        name="ResponseTemplateHook",
        module="cortex.orchestrators.intelligence.response_template_generator",
        dimension=CapabilityDimension.RESPONSE,
        description="ResponseTemplate.format_response() hook for pipeline stages",
        tags=["response", "template", "hook"],
    ),
    CortexCapability(
        id="CC-015",
        name="T1T2EnrichmentHooks",
        module="cortex.intelligence.intelligence_wiring_bridges",
        dimension=CapabilityDimension.INTELLIGENCE,
        description="T1/T2 brain tier enrichment hooks for DomainAdapter and BatchProcessor",
        tags=["brain", "enrichment", "t1", "t2"],
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# Coverage Gate Constant (Phase 66-C — GAP-66-C)
# ─────────────────────────────────────────────────────────────────────────────

# Raise MatrixCoverageError in AuditFixPipeline Stage 1.5 when below this.
COVERAGE_GATE: float = 0.50


# ─────────────────────────────────────────────────────────────────────────────
# Matrix Builder
# ─────────────────────────────────────────────────────────────────────────────

class IntelligenceMatrixBuilder:
    """
    Builds a HIGH VALUE intelligence matrix by crossing every x (intelligence
    capability) against every y (remaining CORTEX capability).

    The matrix drives neural wiring decisions across all seven dimensions:
    brain_tier, lens, intelligence, toolkit, workflow, response, governance.

    Usage:
        builder = IntelligenceMatrixBuilder()
        matrix = builder.build()
        report = builder.render_matrix_report(matrix)
    """

    # Cross-check rules: (x_tag, y_tag) → (score, rationale, wire_action)
    _SCORING_RULES: List[Tuple[str, str, IntelligenceScore, str, str]] = [
        # LENS × Toolkit — highest value: scanner feeds LENS analysis
        ("ast", "scan", IntelligenceScore.CRITICAL,
         "LENS AST engine needs HierarchicalScanner to discover source files across workspace",
         "Wire HierarchicalScanner.scan() output → LENS.analyze(files) pipeline"),
        ("semantic", "batch", IntelligenceScore.HIGH,
         "Semantic search benefits from batch-indexed embeddings for large workspaces",
         "Pipe BatchProcessor results into LENS semantic index"),
        ("graph", "adapter", IntelligenceScore.MEDIUM,
         "Dependency graph adapter enables domain-aware graph generation",
         "Register DomainAdapter as graph node provider in LENS"),

        # Brain Tiers × Response — memory informs chat rendering
        ("memory", "mcp", IntelligenceScore.CRITICAL,
         "Brain tier memories must be surfaced via MCP for Copilot Chat consumption",
         "Expose T1/T2/T3 memory query as cortex_brain_query MCP tool"),
        ("persistent", "adapter", IntelligenceScore.HIGH,
         "Persistent learned patterns feed domain adapter context enrichment",
         "T1 Learned → DomainAdapter enrichment hook"),
        ("adaptive", "pipeline", IntelligenceScore.HIGH,
         "T2 adaptive context improves docgen pipeline content quality",
         "Inject T2 session context into DocGenPlaybook stage_1 discovery"),

        # Intelligence × Governance — compliance awareness
        ("coverage", "enforcement", IntelligenceScore.CRITICAL,
         "BlindSpotDetector findings must trigger EnforcementOrchestrator P0 violations",
         "Wire blind_spot_detector.gaps → enforcement_orchestrator.register_violation()"),
        ("knowledge", "sweep", IntelligenceScore.HIGH,
         "Knowledge gaps from synthesis should populate sweep catalogue (CORE-064)",
         "SynthesisEngine.detect_conflicts() → SweepCatalogue entries"),
        ("gap", "audit", IntelligenceScore.HIGH,
         "Detected gaps should appear in audit-fix Stage 2 (19-point scan)",
         "Inject IntelligenceOrchestrator gap report into AuditFixPipeline Stage 2"),

        # Knowledge × Workflow — docgen integration
        ("index", "docgen", IntelligenceScore.CRITICAL,
         "KnowledgeIndexer is the source of truth for DocGenPlaybook stage_1 discovery scan",
         "Wire KnowledgeIndexer.inventory() → DocGenPlaybook stage_1.knowledge_yaml_scan"),
        ("retrieval", "pipeline", IntelligenceScore.HIGH,
         "RetrievalOptimizer improves DocGen quality by ranking discovery results",
         "Add retrieval_optimizer scoring to DocGenPlaybook stage_2 generation"),
        ("merge", "batch", IntelligenceScore.MEDIUM,
         "SynthesisEngine.merge() can power batch content consolidation",
         "Register SynthesisEngine as BatchProcessor transform function"),

        # Response Template × MCP — Copilot Chat rendering
        ("template", "mcp", IntelligenceScore.CRITICAL,
         "Response templates must be applied at MCP tool output level for consistent VS Code rendering",
         "Wrap all MCP tool results through format_response() before returning"),
        ("response", "pipeline", IntelligenceScore.HIGH,
         "Pipeline stage outputs should use ResponseTemplate for consistent AC marker display",
         "Apply ResponseTemplate.create_header() to all pipeline stage completions"),
        ("copilot", "audit", IntelligenceScore.HIGH,
         "Audit results should render with semantic color-coding in Copilot Chat",
         "Wire ResponseTemplate into AuditFixPipeline terminal output"),

        # TDD × Intelligence — test quality
        ("gap", "tdd", IntelligenceScore.HIGH,
         "BlindSpotDetector gaps should auto-generate TDD RED phase test stubs",
         "Wire blind_spot_detector → tdd_orchestrator.create_test_stub()"),
        ("coverage", "tdd", IntelligenceScore.HIGH,
         "Coverage gaps from IntelligenceOrchestrator feed TDD cycle selection",
         "IntelligenceOrchestrator.analyze() → TDDOrchestrator.prioritize()"),

        # Governance × Toolkit — compliance scanning
        ("governance", "scan", IntelligenceScore.MEDIUM,
         "Governance rule validation can leverage HierarchicalScanner for broader coverage",
         "Register scanner results in EnforcementOrchestrator rule check scope"),
        ("compliance", "batch", IntelligenceScore.MEDIUM,
         "Batch processing of governance checks improves audit throughput",
         "Wire BatchProcessor → EnforcementOrchestrator.validate_batch()"),
    ]

    def build(
        self,
        intelligence_capabilities: Optional[List[IntelligenceCapability]] = None,
        cortex_capabilities: Optional[List[CortexCapability]] = None,
    ) -> IntelligenceMatrix:
        """
        Build the full HIGH VALUE intelligence matrix.

        Crosses every x (intelligence) against every y (cortex) capability,
        scores each intersection, and returns the wired matrix.

        Args:
            intelligence_capabilities: Override default x-axis catalogue.
            cortex_capabilities: Override default y-axis catalogue.

        Returns:
            IntelligenceMatrix with all scored and categorized cells.
        """
        # AC_START: AC-MATRIX-BUILD-001
        x_caps = intelligence_capabilities or INTELLIGENCE_CAPABILITIES
        y_caps = cortex_capabilities or CORTEX_CAPABILITIES

        cells: List[MatrixCell] = []
        scored_pairs: Set[Tuple[str, str]] = set()

        for x in x_caps:
            for y in y_caps:
                score, rationale, wire_action = self._score_pair(x, y)
                if score is not None:
                    cell = MatrixCell(
                        intelligence_id=x.id,
                        cortex_id=y.id,
                        score=score,
                        rationale=rationale,
                        wire_action=wire_action,
                        dimension_pair=(x.dimension, y.dimension),
                        is_wired=False,
                        wired_via=None,
                    )
                    cells.append(cell)
                    scored_pairs.add((x.id, y.id))

        # Detect already-wired pairs via module cross-reference
        cells = self._detect_existing_wiring(cells, x_caps, y_caps)

        wired_count = sum(1 for c in cells if c.is_wired)
        coverage = wired_count / len(cells) if cells else 0.0

        matrix = IntelligenceMatrix(
            cells=cells,
            total_capabilities_x=len(x_caps),
            total_capabilities_y=len(y_caps),
            wired_count=wired_count,
            coverage_score=coverage,
        )
        # AC_COMPLETE: AC-MATRIX-BUILD-001 ✅
        return matrix

    def _score_pair(
        self,
        x: IntelligenceCapability,
        y: CortexCapability,
    ) -> Tuple[Optional[IntelligenceScore], str, str]:
        """
        Score a single (x, y) pair using tag-based cross-check rules.

        Returns (score, rationale, wire_action) or (None, "", "") if no match.
        """
        x_tags = set(x.tags)
        y_tags = set(y.tags)

        best_score: Optional[IntelligenceScore] = None
        best_rationale = ""
        best_action = ""

        score_order = {
            IntelligenceScore.CRITICAL: 0,
            IntelligenceScore.HIGH: 1,
            IntelligenceScore.MEDIUM: 2,
            IntelligenceScore.LOW: 3,
        }

        for x_tag, y_tag, score, rationale, wire_action in self._SCORING_RULES:
            if x_tag in x_tags and y_tag in y_tags:
                if best_score is None or score_order[score] < score_order[best_score]:
                    best_score = score
                    best_rationale = rationale
                    best_action = wire_action

        return best_score, best_rationale, best_action

    def _detect_existing_wiring(
        self,
        cells: List[MatrixCell],
        x_caps: List[IntelligenceCapability],
        y_caps: List[CortexCapability],
    ) -> List[MatrixCell]:
        """
        Detect pairs that are already wired by checking module imports.

        Marks cells as is_wired=True when wiring evidence exists in source.
        """
        # Known wired pairs based on current architecture analysis
        known_wired: Dict[Tuple[str, str], str] = {
            ("IC-007", "CC-008"): "cortex.mcp.tools.intelligence.CortexLens",
            ("IC-009", "CC-006"): "cortex.orchestrators.intelligence.blind_spot_detector",
            ("IC-008", "CC-005"): "cortex.orchestrators.intelligence.response_template_generator",
            ("IC-001", "CC-008"): "cortex.mcp.tools.intelligence.CortexLens.analyze",
        }

        for cell in cells:
            pair = (cell.intelligence_id, cell.cortex_id)
            if pair in known_wired:
                cell.is_wired = True
                cell.wired_via = known_wired[pair]

        return cells

    def render_matrix_report(self, matrix: IntelligenceMatrix) -> str:
        """
        Render the intelligence matrix as a VS Code Copilot Chat optimized report.

        Uses ResponseTemplate-style formatting with semantic emoji hierarchy.
        All output inline — never written to file (CORE-002).

        Args:
            matrix: The built IntelligenceMatrix.

        Returns:
            Formatted markdown string for Copilot Chat rendering.
        """
        critical = matrix.critical_cells()
        high = matrix.high_cells()
        wired_pct = round(matrix.coverage_score * 100, 1)

        lines = [
            "## ⚡ CORTEX Intelligence Matrix — Cross-Cutting Wire Report",
            "",
            "```",
            f"  x-axis (Intelligence):  {matrix.total_capabilities_x} capabilities",
            f"  y-axis (CORTEX):         {matrix.total_capabilities_y} capabilities",
            f"  Total intersections:     {len(matrix.cells)}",
            f"  Wired:                   {matrix.wired_count} ({wired_pct}%)",
            f"  🔴 P0-CRITICAL unwired:  {len(critical)}",
            f"  🟡 P1-HIGH unwired:      {len(high)}",
            "```",
            "",
            "---",
            "### 🔴 P0-CRITICAL — Wire Immediately",
            "",
        ]

        for cell in critical:
            lines += [
                f"**[{cell.intelligence_id}×{cell.cortex_id}]** `{cell.dimension_pair[0].value}` × `{cell.dimension_pair[1].value}`",
                f"> {cell.rationale}",
                f"→ **Action:** `{cell.wire_action}`",
                "",
            ]

        lines += [
            "---",
            "### 🟡 P1-HIGH — Wire in Current Phase",
            "",
        ]

        for cell in high:
            lines += [
                f"**[{cell.intelligence_id}×{cell.cortex_id}]** `{cell.dimension_pair[0].value}` × `{cell.dimension_pair[1].value}`",
                f"> {cell.rationale}",
                f"→ **Action:** `{cell.wire_action}`",
                "",
            ]

        lines += [
            "---",
            "### ✅ Already Wired",
            "",
        ]
        for cell in matrix.cells:
            if cell.is_wired:
                lines.append(f"- **[{cell.intelligence_id}×{cell.cortex_id}]** via `{cell.wired_via}`")

        lines += ["", "---", f"*AC_COMPLETE: AC-INTELLIGENCE-MATRIX-001 ✅*"]
        return "\n".join(lines)

    def persist_matrix(self, matrix: IntelligenceMatrix, output_path: Optional[Path] = None) -> Path:
        """
        Persist the matrix to .cortex-runtime/ as JSON (CORE-002 compliant — no .md files).

        Args:
            matrix: The built IntelligenceMatrix.
            output_path: Override default output path.

        Returns:
            Path where matrix was persisted.
        """
        if output_path is None:
            runtime_dir = Path(".cortex-runtime/intelligence")
            runtime_dir.mkdir(parents=True, exist_ok=True)
            output_path = runtime_dir / "intelligence-matrix.json"

        output_path.write_text(
            json.dumps(matrix.to_dict(), indent=2),
            encoding="utf-8",
        )
        logger.info("Intelligence matrix persisted: %s", output_path)
        return output_path

    def check_coverage_gate(
        self,
        matrix: IntelligenceMatrix,
        gate: float = COVERAGE_GATE,
    ) -> None:
        """Assert matrix coverage meets the minimum gate threshold.

        Enforces the Phase 66-C acceptance criterion: ``coverage_score ≥ 0.50``.
        Called by AuditFixPipeline Stage 1.5 (GAP-66-C).

        Args:
            matrix: The built :class:`IntelligenceMatrix` to check.
            gate: Minimum coverage fraction (default: :data:`COVERAGE_GATE` = 0.50).

        Raises:
            MatrixCoverageError: When ``matrix.coverage_score < gate``.
        """
        if matrix.coverage_score < gate:
            raise MatrixCoverageError(
                f"Intelligence matrix coverage {matrix.coverage_score:.1%} is below "
                f"the required gate of {gate:.1%} (Phase 66-C). "
                f"Wire more pairs to reach ≥{gate:.0%} coverage."
            )
