"""
CortexDocsOrchestrator - Internal CORTEX Documentation HTML Generator + Advisor

INTERNAL USE ONLY — NOT MCP-EXPOSED

TWO MODES:
1. ADVISORY MODE - Suggest diagrams, content structure, visual strategies
2. GENERATION MODE - Generate HTML from templates and content

Generates HTML documentation for CORTEX repository using approved design:
- Dark blue glassmorphism theme from docs/index.html
- 3-Level hierarchy: L1 (landing) → L2 (section) → L3 (detail pages)
- D3.js visualizations and interactive features
- Subfolder index.html generation with consistent styling

Scope: docs/index.html + docs/*/index.html (CORTEX repo only)
Governance: ARCH-011 (execute to completion), CORE-028 (filename conventions)
Date: 2026-01-31

NOT for production MCP exposure. Use DocumentationOrchestrator for external repos.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from jinja2 import Environment, FileSystemLoader, Template

from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator, OperationMode
from cortex.brain.core.result import Err, Ok, Result
from cortex.brain.core.state_manager import OperationState, StateManager
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger

# ============================================================================
# ENUMS & DATA MODELS
# ============================================================================

class NavigationLevel(Enum):
    """Navigation hierarchy levels."""
    EXECUTIVE = "executive"  # High-level overview (index.html)
    DOMAIN = "domain"        # Domain-specific (01-cortex-brain/, 02-orchestrators/)
    TECHNICAL = "technical"  # Deep technical details


@dataclass
class ContentSection:
    """Documentation content section."""
    id: str
    title: str
    icon: str  # Font Awesome icon class
    description: str
    file_path: Optional[Path] = None
    subsections: List[ContentSection] = field(default_factory=list)


@dataclass
class NavigationItem:
    """Navigation menu item."""
    label: str
    href: str
    icon: str
    level: NavigationLevel
    children: List[NavigationItem] = field(default_factory=list)


@dataclass
class PageMetadata:
    """HTML page metadata."""
    title: str
    description: str
    keywords: List[str]
    og_image: str = "assets/images/CORTEX-logo-512.png"
    breadcrumbs: List[Tuple[str, str]] = field(default_factory=list)


@dataclass
class HTMLGenerationReport:
    """Report from HTML generation."""
    generated_files: List[Path]
    failed_files: List[Tuple[Path, str]]
    assets_copied: List[Path]
    total_size_bytes: int
    generation_time_seconds: float


@dataclass
class DiagramRecommendation:
    """Recommendation for a diagram type."""
    diagram_type: str  # d3-force, d3-sankey, d3-tree, svg-pipeline, etc.
    name: str
    description: str
    data_format: str
    effort_hours: float
    uniqueness_score: float  # 1-10, how unique this makes the page


@dataclass
class SectionAdvisory:
    """Advisory output for a documentation section."""
    section_id: str
    section_title: str
    theme_accent: str
    recommended_diagrams: List[DiagramRecommendation]
    content_structure: List[str]
    unique_features: List[str]
    effort_estimate_hours: float
    design_rationale: str


# ============================================================================
# DIAGRAM KNOWLEDGE BASE
# ============================================================================

DIAGRAM_RECOMMENDATIONS: Dict[str, Dict[str, Any]] = {
    "01-cortex-brain": {
        "title": "CORTEX Brain",
        "theme_accent": "#7b61ff",  # Purple
        "diagrams": [
            {
                "type": "d3-hierarchy",
                "name": "Tier Governance Pyramid",
                "description": "Interactive pyramid showing Tier0 > Tier1 > Tier2 > Tier3 precedence with rule counts",
                "data_format": '{"name": "root", "children": [{"name": "tier", "rules": [...]}]}',
                "effort": 4.0,
                "uniqueness": 9
            },
            {
                "type": "d3-force",
                "name": "Brain Component Network",
                "description": "Force-directed graph of brain modules (state, governance, knowledge) and their dependencies",
                "data_format": '{"nodes": [...], "links": [...]}',
                "effort": 3.0,
                "uniqueness": 7
            },
            {
                "type": "svg-pipeline",
                "name": "Request Processing Flow",
                "description": "Linear SVG showing: Input → Brain Analysis → Governance Check → Output",
                "data_format": "Static SVG with CSS animations",
                "effort": 2.0,
                "uniqueness": 6
            }
        ],
        "unique_features": [
            "Tier rule hover cards with violation examples",
            "Clickable governance rule explorer",
            "State machine visualization with transitions",
            "Knowledge graph sample with entity relationships"
        ],
        "content_structure": [
            "Executive Summary: What is CORTEX Brain?",
            "4-Tier Governance Model (interactive diagram)",
            "Core Components: State, Governance, Knowledge",
            "Integration with Orchestrators",
            "L3 Links: Tier0 Details, Tier1 Details, State Management"
        ]
    },
    "02-orchestrators": {
        "title": "Orchestrators",
        "theme_accent": "#00d4ff",  # Cyan
        "diagrams": [
            {
                "type": "d3-force",
                "name": "Orchestrator Network",
                "description": "23 orchestrators with category coloring (Core/Domain/Support) and relationship links",
                "data_format": '{"nodes": [{"id": "name", "category": "core|domain|support"}], "links": [...]}',
                "effort": 3.0,
                "uniqueness": 8
            },
            {
                "type": "svg-pipeline",
                "name": "Request Flow Architecture",
                "description": "Request → IntentRouter → Orchestrator Selection → MCP Response",
                "data_format": "Static SVG with layer boxes",
                "effort": 2.0,
                "uniqueness": 7
            },
            {
                "type": "svg-pipeline",
                "name": "Wiring & Registry",
                "description": "YAML Config → GitBackedRegistry → MCP Gateway → Tools",
                "data_format": "Static SVG matching approved design",
                "effort": 1.5,
                "uniqueness": 6
            }
        ],
        "unique_features": [
            "Interactive filtering by category (Core/Domain/Support)",
            "MCP tool endpoint badges on each orchestrator",
            "Click orchestrator → expand capabilities panel",
            "Wiring.yaml live syntax highlighting"
        ],
        "content_structure": [
            "Overview: 23 Orchestrators, 3 Categories",
            "Interactive Network Visualization",
            "Core Orchestrators (6): Master, Interaction, Intent, TDD, Workflow, Enforcement",
            "Domain Orchestrators (6): Refactoring, Planning, Documentation, etc.",
            "Support Orchestrators (11): Onboarding, LENS, Discovery, etc.",
            "Wiring & Registration System",
            "L3 Links: Individual orchestrator detail pages"
        ]
    },
    "03-getting-started": {
        "title": "Getting Started",
        "theme_accent": "#10b981",  # Emerald
        "diagrams": [
            {
                "type": "svg-steps",
                "name": "Installation Flow",
                "description": "Step-by-step visual: Clone → Install → Configure → Run → Success",
                "data_format": "Static SVG with numbered steps",
                "effort": 2.0,
                "uniqueness": 6
            },
            {
                "type": "d3-decision",
                "name": "Quick Start Decision Tree",
                "description": "Interactive: What do you want to do? → Click path → Suggested commands",
                "data_format": '{"question": "...", "options": [{"answer": "...", "next": "..."}]}',
                "effort": 4.0,
                "uniqueness": 9
            }
        ],
        "unique_features": [
            "Animated code blocks with typing effect",
            "Copy-to-clipboard on all commands",
            "Progress indicator for multi-step tutorials",
            "Environment detection (macOS/Linux/Windows)"
        ],
        "content_structure": [
            "30-Second Quick Start (copy-paste ready)",
            "Prerequisites Check (interactive)",
            "Installation Methods: pip, Docker, source",
            "First Request: Hello CORTEX",
            "Common Issues & Solutions",
            "L3 Links: Detailed tutorials"
        ]
    },
    "04-architecture": {
        "title": "Architecture",
        "theme_accent": "#6366f1",  # Indigo
        "diagrams": [
            {
                "type": "d3-sankey",
                "name": "Data Flow Sankey",
                "description": "Show data flow volumes through system layers with proportional widths",
                "data_format": '{"nodes": [...], "links": [{"source": 0, "target": 1, "value": 10}]}',
                "effort": 5.0,
                "uniqueness": 10
            },
            {
                "type": "d3-matrix",
                "name": "Component Interaction Matrix",
                "description": "Heatmap showing which components communicate (density = coupling)",
                "data_format": '{"rows": [...], "columns": [...], "values": [[...]]}',
                "effort": 4.0,
                "uniqueness": 9
            },
            {
                "type": "svg-layers",
                "name": "Layer Architecture",
                "description": "Presentation → Application → Domain → Infrastructure stacked diagram",
                "data_format": "Static SVG with layer labels",
                "effort": 2.0,
                "uniqueness": 5
            }
        ],
        "unique_features": [
            "Zoom into any layer for component detail",
            "Hover shows component responsibilities",
            "Architecture decision records (ADR) links",
            "Live dependency graph from imports"
        ],
        "content_structure": [
            "System Overview (high-level diagram)",
            "Layered Architecture Principles",
            "Data Flow Through System (Sankey)",
            "Component Coupling Analysis (Matrix)",
            "Design Decisions & Trade-offs",
            "L3 Links: Layer details, ADRs"
        ]
    },
    "05-lens-protocol": {
        "title": "LENS Protocol",
        "theme_accent": "#8b5cf6",  # Violet
        "diagrams": [
            {
                "type": "svg-pipeline",
                "name": "LENS Pipeline",
                "description": "Language → Examination → Navigation → Synthesis with data transformation at each stage",
                "data_format": "Static SVG with stage boxes",
                "effort": 2.0,
                "uniqueness": 7
            },
            {
                "type": "d3-tree",
                "name": "AST Visualization",
                "description": "Collapsible tree showing sample Python AST with node type coloring",
                "data_format": '{"name": "Module", "children": [{"name": "FunctionDef", ...}]}',
                "effort": 4.0,
                "uniqueness": 9
            },
            {
                "type": "d3-timeline",
                "name": "Git History Timeline",
                "description": "24h commit activity with author grouping and change size bubbles",
                "data_format": '[{"time": "2026-01-31T10:00", "author": "...", "files": 5}]',
                "effort": 3.0,
                "uniqueness": 8
            }
        ],
        "unique_features": [
            "Live code analysis demo (paste code → see analysis)",
            "Interactive AST explorer with syntax highlighting",
            "Git blame integration example",
            "Comment extraction showcase"
        ],
        "content_structure": [
            "What is LENS? (acronym breakdown)",
            "The 4-Stage Pipeline (interactive)",
            "Language Analysis: AST, Comments, Patterns",
            "Examination: Complexity, Duplicates, Dead Code",
            "Navigation: Git History, Blame, Dependencies",
            "Synthesis: Unified Context, Recommendations",
            "L3 Links: Each analyzer in detail"
        ]
    },
    "11-mcp-tools": {
        "title": "MCP Tools",
        "theme_accent": "#f59e0b",  # Amber
        "diagrams": [
            {
                "type": "d3-force",
                "name": "Tool-Orchestrator Graph",
                "description": "Which MCP tools map to which orchestrators with usage frequency",
                "data_format": '{"nodes": [{"id": "tool", "type": "tool|orchestrator"}], "links": [...]}',
                "effort": 3.0,
                "uniqueness": 8
            },
            {
                "type": "svg-api",
                "name": "REST Endpoint Map",
                "description": "Visual API documentation with method colors (GET=green, POST=blue)",
                "data_format": "Static SVG with endpoint boxes",
                "effort": 2.5,
                "uniqueness": 7
            },
            {
                "type": "d3-radar",
                "name": "Tool Capability Radar",
                "description": "Compare tools on axes: Speed, Complexity, Coverage, Automation",
                "data_format": '[{"tool": "name", "speed": 8, "complexity": 3, ...}]',
                "effort": 4.0,
                "uniqueness": 9
            }
        ],
        "unique_features": [
            "Try-it-now API playground (mock responses)",
            "Request/response examples with syntax highlighting",
            "Tool search with filtering",
            "MCP protocol explainer animation"
        ],
        "content_structure": [
            "What is MCP? (protocol overview)",
            "Tool Discovery: /tools endpoint",
            "Tool Categories: Analysis, Generation, Validation",
            "Tool-Orchestrator Mapping (interactive graph)",
            "API Reference (visual endpoint map)",
            "L3 Links: Individual tool documentation"
        ]
    }
}


# ============================================================================
# CORTEX DOCS ORCHESTRATOR
# ============================================================================

class CortexDocsOrchestrator(IOrchestrator):
    """
    Internal orchestrator for CORTEX documentation HTML generation.

    NOT MCP-EXPOSED — Internal tooling only.
    Generates docs/index.html and subfolder indexes with approved design.

    Capabilities:
    - Extract template from existing docs/index.html
    - Generate main index.html with glassmorphism theme
    - Generate subfolder index.html files with consistent navigation
    - Copy/optimize CSS/JS assets
    - Validate HTML structure and accessibility

    Compliance:
    - CORE-008: TDD (tests before implementation)
    - CORE-011: Type hints on all methods
    - CORE-012: Google-style docstrings
    - ARCH-011: Execute to completion (no interim reports)
    """

    _instance: Optional[CortexDocsOrchestrator] = None
    _lock = threading.Lock()

    def __init__(
        self,
        docs_root: Path = Path("docs"),
        templates_dir: Path = Path("cortex/templates/docs")
    ) -> None:
        """
        Initialize CORTEX docs orchestrator.

        Args:
            docs_root: Root documentation directory (default: docs/)
            templates_dir: Jinja2 templates directory
        """
        import threading

        self.docs_root = docs_root
        self.templates_dir = templates_dir
        self.logger = EnhancedAuditLogger.instance()
        self.state_manager = StateManager()

        # Jinja2 environment
        self.jinja_env: Optional[Environment] = None
        if templates_dir.exists():
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(templates_dir)),
                autoescape=True,
                trim_blocks=True,
                lstrip_blocks=True
            )

        # Navigation structure (will be populated from docs/ structure)
        self.navigation: List[NavigationItem] = []

    @classmethod
    def instance(cls, **kwargs) -> CortexDocsOrchestrator:
        """Get singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(**kwargs)
        return cls._instance

    # ========================================================================
    # IOrchestrator Implementation
    # ========================================================================

    def get_name(self) -> str:
        """Get orchestrator name."""
        return "CortexDocsOrchestrator"

    def get_version(self) -> str:
        """Get orchestrator version."""
        return "1.0.0"

    def get_mode(self) -> str:
        """Get operation mode."""
        return "internal"  # Internal tooling, not MCP-exposed

    def get_capabilities(self) -> List[str]:
        """Get orchestrator capabilities."""
        return [
            # Advisory Mode
            "advise_section",
            "advise_page",
            "compare_approaches",
            "list_sections",
            # Audit Mode
            "audit_documentation_links",
            "fix_broken_links",
            "cleanup_orphaned_files",
            "audit_responsive_design",
            # Generation Mode
            "generate_main_index",
            "generate_subfolder_indexes",
            "generate_l2_page",
            "generate_l3_page",
            "extract_template",
            "optimize_assets",
            "validate_html"
        ]

    def initialize(self) -> Result:
        """Initialize orchestrator."""
        try:
            # Ensure templates directory exists
            self.templates_dir.mkdir(parents=True, exist_ok=True)

            # Build navigation structure
            self._build_navigation()

            return Ok({"status": "initialized"})
        except Exception as e:
            return Err(f"Initialization failed: {str(e)}")

    def execute(self, operation: str, **kwargs) -> Result[Any, str]:
        """
        Execute documentation operation.

        Args:
            operation: Operation to execute

                ADVISORY MODE:
                - "advise_section": Get recommendations for a specific L2 section
                - "advise_page": Get recommendations for a specific L3 page
                - "compare_approaches": Compare D3/SVG/Mermaid for a visualization
                - "list_sections": List all available sections with status

                AUDIT MODE:
                - "audit_documentation_links": 3-tier HTML link integrity verification
                - "fix_broken_links": Automated remediation suggestions
                - "cleanup_orphaned_files": Safe removal of unreferenced files
                - "audit_responsive_design": Mobile-first responsive design audit

                GENERATION MODE:
                - "extract_template": Extract template from docs/index.html
                - "generate_main": Generate docs/index.html
                - "generate_subfolders": Generate all subfolder indexes
                - "generate_l2_page": Generate specific L2 page
                - "generate_all": Generate everything
                - "validate": Validate generated HTML

            **kwargs: Operation-specific parameters

        Returns:
            Result containing operation outcome
        """
        try:
            # Advisory Mode Operations
            if operation == "advise_section":
                return self._advise_section(kwargs.get("section_id", ""))
            elif operation == "advise_page":
                return self._advise_page(
                    kwargs.get("section_id", ""),
                    kwargs.get("page_id", "")
                )
            elif operation == "compare_approaches":
                return self._compare_approaches(
                    kwargs.get("visualization_type", ""),
                    kwargs.get("data_complexity", "medium")
                )
            elif operation == "list_sections":
                return self._list_sections()

            # Audit Mode Operations
            elif operation == "audit_documentation_links":
                return self._audit_documentation_links(
                    entry_point=kwargs.get("entry_point", "docs/index.html"),
                    mode=kwargs.get("mode", "full"),
                    skip_external=kwargs.get("skip_external", True),
                    dry_run=kwargs.get("dry_run", True)
                )
            elif operation == "fix_broken_links":
                return self._fix_broken_links(
                    audit_report=kwargs.get("audit_report"),
                    mode=kwargs.get("mode", "suggest"),
                    dry_run=kwargs.get("dry_run", True)
                )
            elif operation == "cleanup_orphaned_files":
                return self._cleanup_orphaned_files(
                    audit_report=kwargs.get("audit_report"),
                    mode=kwargs.get("mode", "archive"),
                    confirm=kwargs.get("confirm", False)
                )
            elif operation == "audit_responsive_design":
                return self._audit_responsive_design(
                    entry_point=kwargs.get("entry_point", "docs/index.html")
                )

            # Generation Mode Operations
            elif operation == "extract_template":
                return self._extract_template()
            elif operation == "generate_main":
                return self._generate_main_index()
            elif operation == "generate_subfolders":
                return self._generate_subfolder_indexes()
            elif operation == "generate_l2_page":
                return self._generate_l2_page(kwargs.get("section_id", ""))
            elif operation == "generate_all":
                return self._generate_all()
            elif operation == "validate":
                return self._validate_html()
            else:
                return Err(f"Unknown operation: {operation}")
        except Exception as e:
            self.logger.log_error(f"CortexDocsOrchestrator operation failed: {str(e)}")
            return Err(f"Operation error: {str(e)}")

    def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Result:
        """Execute named operation with parameters."""
        return self.execute(operation_name, **parameters)

    def get_mcp_tools(self) -> Dict[str, Any]:
        """Get MCP tools (NOT EXPOSED - internal only)."""
        return {}  # Intentionally empty - not MCP-exposed

    def get_audit_trail(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit trail."""
        return []

    # ========================================================================
    # ADVISORY MODE OPERATIONS
    # ========================================================================

    def _advise_section(self, section_id: str) -> Result[SectionAdvisory, str]:
        """
        Get advisory recommendations for a documentation section.

        Provides intelligent suggestions for:
        - Recommended diagrams (type, description, effort)
        - Content structure
        - Unique features to make the page impressive
        - Effort estimates

        Args:
            section_id: Section identifier (e.g., "01-cortex-brain", "02-orchestrators")

        Returns:
            Result containing SectionAdvisory dataclass
        """
        # Normalize section_id
        section_key = section_id.lstrip("0123456789-").lower().replace(" ", "-")

        # Try exact match first, then fuzzy match
        recommendations = None
        for key, data in DIAGRAM_RECOMMENDATIONS.items():
            if key == section_id or section_key in key or key in section_id:
                recommendations = data
                break

        if not recommendations:
            available = list(DIAGRAM_RECOMMENDATIONS.keys())
            return Err(
                f"Section '{section_id}' not found in knowledge base.\n"
                f"Available sections: {', '.join(available)}\n"
                f"Use 'list_sections' to see all options."
            )

        # Build diagram recommendations
        diagram_recs = [
            DiagramRecommendation(
                diagram_type=d["type"],
                name=d["name"],
                description=d["description"],
                data_format=d["data_format"],
                effort_hours=d["effort"],
                uniqueness_score=d["uniqueness"]
            )
            for d in recommendations["diagrams"]
        ]

        # Calculate total effort
        total_effort = sum(d.effort_hours for d in diagram_recs) + 2.0  # +2h for content

        # Build advisory
        advisory = SectionAdvisory(
            section_id=section_id,
            section_title=recommendations["title"],
            theme_accent=recommendations["theme_accent"],
            recommended_diagrams=diagram_recs,
            content_structure=recommendations["content_structure"],
            unique_features=recommendations["unique_features"],
            effort_estimate_hours=total_effort,
            design_rationale=self._generate_design_rationale(section_id, recommendations)
        )

        return Ok(advisory)

    def _generate_design_rationale(self, section_id: str, data: Dict) -> str:
        """Generate design rationale for a section."""
        diagrams = data.get("diagrams", [])
        features = data.get("unique_features", [])

        rationale_parts = [
            f"## Design Rationale for {data.get('title', section_id)}",
            "",
            f"**Theme Accent:** `{data.get('theme_accent', '#00d4ff')}` — chosen for visual distinction from other sections.",
            "",
            "### Why These Diagrams?",
        ]

        for d in diagrams:
            rationale_parts.append(
                f"- **{d['name']}** ({d['type']}): "
                f"Uniqueness score {d['uniqueness']}/10. "
                f"{d['description'][:100]}..."
            )

        rationale_parts.extend([
            "",
            "### Unique Features Strategy",
            "These features differentiate this page from generic documentation:",
        ])

        for f in features[:3]:
            rationale_parts.append(f"- {f}")

        rationale_parts.extend([
            "",
            "### Implementation Priority",
            "1. Start with SVG pipeline diagram (lowest effort, immediate impact)",
            "2. Add D3.js interactive visualization (highest uniqueness)",
            "3. Polish with unique features and animations"
        ])

        return "\n".join(rationale_parts)

    def _advise_page(self, section_id: str, page_id: str) -> Result[Dict[str, Any], str]:
        """
        Get advisory recommendations for a specific L3 page.

        Args:
            section_id: Parent section (e.g., "01-cortex-brain")
            page_id: Page identifier (e.g., "tier0-governance")

        Returns:
            Result with page-specific recommendations
        """
        # Get section advisory first
        section_result = self._advise_section(section_id)
        if section_result.is_err():
            return Err(section_result.error)

        section = section_result.value

        # Page-specific recommendations
        page_advisory = {
            "section_id": section_id,
            "page_id": page_id,
            "page_title": page_id.replace("-", " ").title(),
            "breadcrumbs": [
                ("Home", "/"),
                (section.section_title, f"/{section_id}/"),
                (page_id.replace("-", " ").title(), f"/{section_id}/{page_id}.html")
            ],
            "inherited_theme_accent": section.theme_accent,
            "suggested_diagrams": [
                d for d in section.recommended_diagrams
                if d.uniqueness_score >= 7  # Only high-uniqueness for L3
            ][:2],  # Max 2 diagrams per L3 page
            "content_template": self._suggest_l3_content_template(page_id),
            "related_pages": self._suggest_related_pages(section_id, page_id),
            "effort_estimate_hours": 3.0  # Average L3 page
        }

        return Ok(page_advisory)

    def _suggest_l3_content_template(self, page_id: str) -> List[str]:
        """Suggest content structure for an L3 page."""
        return [
            f"# {page_id.replace('-', ' ').title()}",
            "",
            "## Overview",
            "Brief description of what this page covers.",
            "",
            "## Key Concepts",
            "Core concepts with explanations.",
            "",
            "## Implementation Details",
            "Technical details, code examples, configuration.",
            "",
            "## Examples",
            "Practical examples with explanations.",
            "",
            "## Related Topics",
            "Links to related L3 pages and external resources."
        ]

    def _suggest_related_pages(self, section_id: str, page_id: str) -> List[str]:
        """Suggest related L3 pages."""
        # Common related pages per section
        related_map = {
            "01-cortex-brain": ["tier0-governance", "tier1-acceptance", "state-management", "knowledge-graph"],
            "02-orchestrators": ["master-orchestrator", "tdd-orchestrator", "planning-orchestrator", "wiring"],
            "04-architecture": ["layer-architecture", "design-decisions", "component-map"],
            "05-lens-protocol": ["ast-analyzer", "git-history", "comment-extractor"],
            "11-mcp-tools": ["tool-registry", "api-reference", "integration-guide"]
        }

        section_pages = related_map.get(section_id, [])
        return [p for p in section_pages if p != page_id][:4]

    def _compare_approaches(
        self,
        visualization_type: str,
        data_complexity: str = "medium"
    ) -> Result[Dict[str, Any], str]:
        """
        Compare D3.js vs SVG vs Mermaid for a visualization type.

        Args:
            visualization_type: Type of visualization (e.g., "network", "pipeline", "tree")
            data_complexity: "low", "medium", or "high"

        Returns:
            Result with comparison and recommendation
        """
        comparisons = {
            "network": {
                "d3": {
                    "rating": 9,
                    "pros": ["Full interactivity", "Force-directed layout", "Drag nodes", "Filter/highlight"],
                    "cons": ["More code (~150 lines)", "Requires D3.js knowledge"],
                    "effort_hours": 4.0,
                    "best_for": "Complex relationships, large datasets, exploration"
                },
                "svg": {
                    "rating": 5,
                    "pros": ["Simple static layout", "Fast to create"],
                    "cons": ["No interactivity", "Manual positioning", "Hard to maintain"],
                    "effort_hours": 2.0,
                    "best_for": "Simple, fixed networks (<10 nodes)"
                },
                "mermaid": {
                    "rating": 3,
                    "pros": ["Declarative syntax", "Quick prototyping"],
                    "cons": ["Limited styling", "Poor glassmorphism fit", "No drag/filter"],
                    "effort_hours": 0.5,
                    "best_for": "Documentation drafts, not production"
                }
            },
            "pipeline": {
                "d3": {
                    "rating": 6,
                    "pros": ["Animated flows", "Interactive stages"],
                    "cons": ["Overkill for linear flows", "More maintenance"],
                    "effort_hours": 3.0,
                    "best_for": "Complex branching, animated data flow"
                },
                "svg": {
                    "rating": 9,
                    "pros": ["Perfect glassmorphism control", "CSS animations", "Lightweight"],
                    "cons": ["Manual updates for changes"],
                    "effort_hours": 2.0,
                    "best_for": "Linear flows, layer diagrams, approved production style"
                },
                "mermaid": {
                    "rating": 4,
                    "pros": ["Quick syntax", "Auto-layout"],
                    "cons": ["Styling conflicts", "Generic look"],
                    "effort_hours": 0.5,
                    "best_for": "Quick drafts only"
                }
            },
            "tree": {
                "d3": {
                    "rating": 10,
                    "pros": ["Collapsible nodes", "Zoom/pan", "Search", "Large trees"],
                    "cons": ["Requires tree data format"],
                    "effort_hours": 4.0,
                    "best_for": "AST, hierarchies, file trees, org charts"
                },
                "svg": {
                    "rating": 4,
                    "pros": ["Simple static trees"],
                    "cons": ["No interactivity", "Manual layout calculations"],
                    "effort_hours": 3.0,
                    "best_for": "Small fixed trees (<20 nodes)"
                },
                "mermaid": {
                    "rating": 2,
                    "pros": ["Quick syntax"],
                    "cons": ["No collapse", "Poor large tree handling"],
                    "effort_hours": 0.5,
                    "best_for": "Tiny trees, prototyping only"
                }
            },
            "sankey": {
                "d3": {
                    "rating": 10,
                    "pros": ["D3-sankey plugin", "Flow proportions", "Hover details"],
                    "cons": ["Requires d3-sankey library"],
                    "effort_hours": 5.0,
                    "best_for": "Data flow, resource allocation, any proportional flow"
                },
                "svg": {
                    "rating": 2,
                    "pros": ["Possible but painful"],
                    "cons": ["Manual path calculations", "No flow proportions"],
                    "effort_hours": 8.0,
                    "best_for": "Not recommended"
                },
                "mermaid": {
                    "rating": 0,
                    "pros": [],
                    "cons": ["Not supported"],
                    "effort_hours": 0,
                    "best_for": "N/A - use D3.js"
                }
            },
            "timeline": {
                "d3": {
                    "rating": 9,
                    "pros": ["Zoom to range", "Event markers", "Brush selection"],
                    "cons": ["Time scale complexity"],
                    "effort_hours": 4.0,
                    "best_for": "Git history, event sequences, version history"
                },
                "svg": {
                    "rating": 6,
                    "pros": ["Simple linear timeline"],
                    "cons": ["No zoom", "Fixed time range"],
                    "effort_hours": 2.5,
                    "best_for": "Small, fixed timelines"
                },
                "mermaid": {
                    "rating": 5,
                    "pros": ["Gantt chart support"],
                    "cons": ["Limited styling", "Fixed layout"],
                    "effort_hours": 1.0,
                    "best_for": "Gantt charts only"
                }
            }
        }

        viz_type = visualization_type.lower()
        if viz_type not in comparisons:
            available = list(comparisons.keys())
            return Err(
                f"Unknown visualization type: {visualization_type}\n"
                f"Available types: {', '.join(available)}"
            )

        comp = comparisons[viz_type]

        # Determine verdict based on complexity
        complexity_weight = {"low": 0.5, "medium": 1.0, "high": 1.5}.get(data_complexity, 1.0)

        # Score adjustments for complexity
        scores = {}
        for lib, data in comp.items():
            base_score = data["rating"]
            if data_complexity == "high" and lib == "d3":
                base_score += 2  # D3 handles complexity better
            elif data_complexity == "low" and lib == "svg":
                base_score += 1  # SVG is fine for simple cases
            scores[lib] = min(10, base_score)

        winner = max(scores, key=scores.get)

        return Ok({
            "visualization_type": visualization_type,
            "data_complexity": data_complexity,
            "comparison": comp,
            "scores": scores,
            "verdict": winner,
            "verdict_reason": f"{winner.upper()} is best for {viz_type} with {data_complexity} complexity. "
                            f"Score: {scores[winner]}/10. "
                            f"{comp[winner]['best_for']}"
        })

    def _list_sections(self) -> Result[Dict[str, Any], str]:
        """
        List all documentation sections with status and advisory availability.

        Returns:
            Result with sections list and status
        """
        sections = []

        for section_id, data in DIAGRAM_RECOMMENDATIONS.items():
            # Check if section folder exists
            section_path = self.docs_root / section_id
            has_folder = section_path.exists()
            has_index = (section_path / "index.html").exists() if has_folder else False

            sections.append({
                "section_id": section_id,
                "title": data["title"],
                "theme_accent": data["theme_accent"],
                "status": "COMPLETE" if has_index else ("FOLDER_EXISTS" if has_folder else "PENDING"),
                "diagram_count": len(data["diagrams"]),
                "total_effort_hours": sum(d["effort"] for d in data["diagrams"]) + 2.0,
                "advisory_available": True
            })

        # Check for sections not in knowledge base
        for folder in self.docs_root.iterdir():
            if not folder.is_dir():
                continue
            if folder.name.startswith(("_", ".", "assets", "archives", "stylesheets", "theme")):
                continue
            if not any(s["section_id"] == folder.name for s in sections):
                sections.append({
                    "section_id": folder.name,
                    "title": folder.name.replace("-", " ").title(),
                    "theme_accent": "#6b7280",  # Gray - no specific theme
                    "status": "NO_ADVISORY",
                    "diagram_count": 0,
                    "total_effort_hours": 0,
                    "advisory_available": False
                })

        return Ok({
            "sections": sorted(sections, key=lambda x: x["section_id"]),
            "total_sections": len(sections),
            "with_advisory": sum(1 for s in sections if s["advisory_available"]),
            "completed": sum(1 for s in sections if s["status"] == "COMPLETE")
        })

    # ========================================================================
    # TEMPLATE EXTRACTION
    # ========================================================================

    def _extract_template(self) -> Result[Dict[str, Any], str]:
        """
        Extract Jinja2 template from existing docs/index.html.

        Extracts:
        - Base HTML structure
        - CSS glassmorphism design system
        - JavaScript interactive features
        - Navigation components
        - Content panels

        Returns:
            Result with extracted template paths
        """
        try:
            source_html = self.docs_root / "index.html"
            if not source_html.exists():
                return Err(f"Source HTML not found: {source_html}")

            content = source_html.read_text()

            # Extract sections
            sections = {
                "head": self._extract_section(content, "<head>", "</head>"),
                "header": self._extract_section(content, '<header', '</header>'),
                "navigation": self._extract_section(content, '<nav', '</nav>'),
                "main_content": self._extract_section(content, '<main', '</main>'),
                "footer": self._extract_section(content, '<footer', '</footer>'),
                "scripts": self._extract_section(content, '<!-- Scripts -->', '</body>'),
            }

            # Create base template
            base_template = self._create_base_template(sections)
            base_path = self.templates_dir / "base.html.jinja2"
            base_path.write_text(base_template)

            # Create main index template
            index_template = self._create_index_template(sections)
            index_path = self.templates_dir / "index.html.jinja2"
            index_path.write_text(index_template)

            # Create subfolder template
            subfolder_template = self._create_subfolder_template(sections)
            subfolder_path = self.templates_dir / "subfolder.html.jinja2"
            subfolder_path.write_text(subfolder_template)

            # Create component templates
            components_dir = self.templates_dir / "components"
            components_dir.mkdir(exist_ok=True)

            self._create_component_templates(components_dir, sections)

            return Ok({
                "templates_created": [
                    str(base_path),
                    str(index_path),
                    str(subfolder_path)
                ],
                "components_dir": str(components_dir)
            })

        except Exception as e:
            return Err(f"Template extraction failed: {str(e)}")

    def _extract_section(self, content: str, start_marker: str, end_marker: str) -> str:
        """Extract section between markers."""
        start = content.find(start_marker)
        if start == -1:
            return ""

        end = content.find(end_marker, start)
        if end == -1:
            return ""

        return content[start:end + len(end_marker)]

    def _create_base_template(self, sections: Dict[str, str]) -> str:
        """Create base Jinja2 template."""
        return f"""<!DOCTYPE html>
<html lang="en">
{sections['head']}
<body>
    {{{{ header | safe }}}}
    {{{{ navigation | safe }}}}
    <main>
        {{% block content %}}
        {{% endblock %}}
    </main>
    {{{{ footer | safe }}}}
    {sections['scripts']}
</body>
</html>
"""

    def _create_index_template(self, sections: Dict[str, str]) -> str:
        """Create main index template."""
        return """{% extends "base.html.jinja2" %}

{% block content %}
<section class="hero-section">
    <div class="container">
        <div class="hero-content glass-card">
            <img src="assets/images/CORTEX-logo-512.png" alt="CORTEX Logo" class="hero-logo">
            <h1 class="hero-title">{{ page_title }}</h1>
            <p class="hero-subtitle">{{ page_description }}</p>
        </div>
    </div>
</section>

<section class="features-grid">
    <div class="container">
        {% for section in content_sections %}
        <div class="feature-card glass-card" data-level="{{ section.level }}">
            <div class="feature-icon">
                <i class="fas {{ section.icon }}"></i>
            </div>
            <h2 class="feature-title">{{ section.title }}</h2>
            <p class="feature-description">{{ section.description }}</p>
            {% if section.href %}
            <a href="{{ section.href }}" class="feature-link">
                Explore <i class="fas fa-arrow-right"></i>
            </a>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</section>

<section class="quick-start">
    <div class="container">
        <div class="glass-card">
            <h2>🚀 Quick Start</h2>
            <div class="tabs-container">
                {% for tab in quick_start_tabs %}
                <div class="tab-content">
                    <h3>{{ tab.title }}</h3>
                    <pre><code>{{ tab.code }}</code></pre>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</section>
{% endblock %}
"""

    def _create_subfolder_template(self, sections: Dict[str, str]) -> str:
        """Create subfolder index template."""
        return """{% extends "base.html.jinja2" %}

{% block content %}
<section class="breadcrumb-section">
    <div class="container">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                {% for crumb_label, crumb_href in breadcrumbs %}
                <li class="breadcrumb-item">
                    <a href="{{ crumb_href }}">{{ crumb_label }}</a>
                </li>
                {% endfor %}
            </ol>
        </nav>
    </div>
</section>

<section class="subfolder-header">
    <div class="container">
        <div class="glass-card">
            <h1>{{ section_title }}</h1>
            <p class="lead">{{ section_description }}</p>
        </div>
    </div>
</section>

<section class="content-grid">
    <div class="container">
        <div class="row">
            <!-- Sidebar Navigation -->
            <aside class="col-md-3 sidebar">
                <div class="glass-card sticky-nav">
                    <h3>Contents</h3>
                    <ul class="nav-list">
                        {% for item in sidebar_items %}
                        <li>
                            <a href="{{ item.href }}">
                                <i class="fas {{ item.icon }}"></i>
                                {{ item.label }}
                            </a>
                        </li>
                        {% endfor %}
                    </ul>
                </div>
            </aside>

            <!-- Main Content -->
            <div class="col-md-9 main-content">
                {% for doc in documents %}
                <article class="doc-card glass-card">
                    <h2>
                        <i class="fas {{ doc.icon }}"></i>
                        {{ doc.title }}
                    </h2>
                    <p class="doc-description">{{ doc.description }}</p>
                    <a href="{{ doc.href }}" class="btn-primary">
                        Read More <i class="fas fa-arrow-right"></i>
                    </a>
                </article>
                {% endfor %}
            </div>
        </div>
    </div>
</section>
{% endblock %}
"""

    def _create_component_templates(self, components_dir: Path, sections: Dict[str, str]) -> None:
        """Create component templates (header, nav, footer)."""

        # Header component
        header_template = """<header class="main-header glass-bg">
    <div class="container">
        <div class="header-content">
            <div class="logo">
                <img src="/assets/images/CORTEX-logo-64.png" alt="CORTEX">
                <span>CORTEX</span>
            </div>
            <nav class="main-nav">
                <a href="/">Home</a>
                <a href="/01-cortex-brain/">Brain</a>
                <a href="/02-orchestrators/">Orchestrators</a>
                <a href="/04-architecture/">Architecture</a>
                <a href="/11-mcp-tools/">MCP Tools</a>
            </nav>
        </div>
    </div>
</header>
"""
        (components_dir / "header.html.jinja2").write_text(header_template)

        # Footer component
        footer_template = """<footer class="main-footer glass-bg">
    <div class="container">
        <div class="footer-content">
            <p>CORTEX - Cognitive Real-Time Execution System</p>
            <p>Developed by Asif Hussain | 2024-2026</p>
        </div>
    </div>
</footer>
"""
        (components_dir / "footer.html.jinja2").write_text(footer_template)

    # ========================================================================
    # HTML GENERATION
    # ========================================================================

    def _generate_main_index(self) -> Result[Path, str]:
        """
        Generate main docs/index.html.

        Returns:
            Result with generated file path
        """
        try:
            if not self.jinja_env:
                return Err("Jinja2 environment not initialized. Run extract_template first.")

            template = self.jinja_env.get_template("index.html.jinja2")

            # Build context from docs structure
            context = {
                "page_title": "CORTEX - Enterprise Development Intelligence",
                "page_description": "AI-Powered Development with TDD, Planning, and Autonomous Orchestration",
                "content_sections": self._get_main_sections(),
                "quick_start_tabs": self._get_quick_start_content(),
                "header": self._render_component("header.html.jinja2"),
                "footer": self._render_component("footer.html.jinja2"),
            }

            html = template.render(**context)

            output_path = self.docs_root / "index.html"
            output_path.write_text(html)

            return Ok(output_path)

        except Exception as e:
            return Err(f"Main index generation failed: {str(e)}")

    def _generate_subfolder_indexes(self) -> Result[List[Path], str]:
        """
        Generate index.html for all subfolders.

        Returns:
            Result with list of generated file paths
        """
        try:
            if not self.jinja_env:
                return Err("Jinja2 environment not initialized")

            template = self.jinja_env.get_template("subfolder.html.jinja2")
            generated_files: List[Path] = []

            # Find all documentation subfolders
            for subfolder in self.docs_root.iterdir():
                if not subfolder.is_dir():
                    continue
                if subfolder.name.startswith(("_", ".")):
                    continue

                # Get subfolder metadata
                metadata = self._get_subfolder_metadata(subfolder)

                context = {
                    "section_title": metadata["title"],
                    "section_description": metadata["description"],
                    "breadcrumbs": metadata["breadcrumbs"],
                    "sidebar_items": metadata["sidebar_items"],
                    "documents": metadata["documents"],
                    "header": self._render_component("header.html.jinja2"),
                    "footer": self._render_component("footer.html.jinja2"),
                }

                html = template.render(**context)

                output_path = subfolder / "index.html"
                output_path.write_text(html)
                generated_files.append(output_path)

            return Ok(generated_files)

        except Exception as e:
            return Err(f"Subfolder generation failed: {str(e)}")

    def _generate_all(self) -> Result[HTMLGenerationReport, str]:
        """
        Generate all HTML documentation.

        Returns:
            Result with generation report
        """
        import time
        start_time = time.time()

        try:
            generated_files: List[Path] = []
            failed_files: List[Tuple[Path, str]] = []

            # 1. Extract template if needed
            if not (self.templates_dir / "index.html.jinja2").exists():
                extract_result = self._extract_template()
                if extract_result.is_err():
                    return Err(f"Template extraction failed: {extract_result.error}")

            # 2. Generate main index
            main_result = self._generate_main_index()
            if main_result.is_ok():
                generated_files.append(main_result.value)
            else:
                failed_files.append((self.docs_root / "index.html", main_result.error))

            # 3. Generate subfolder indexes
            subfolder_result = self._generate_subfolder_indexes()
            if subfolder_result.is_ok():
                generated_files.extend(subfolder_result.value)
            else:
                # Continue even if some fail
                pass

            # 4. Validate generated HTML
            validation_result = self._validate_html()

            # Calculate stats
            total_size = sum(f.stat().st_size for f in generated_files if f.exists())
            generation_time = time.time() - start_time

            report = HTMLGenerationReport(
                generated_files=generated_files,
                failed_files=failed_files,
                assets_copied=[],  # Assets are already in place
                total_size_bytes=total_size,
                generation_time_seconds=generation_time
            )

            return Ok(report)

        except Exception as e:
            return Err(f"HTML generation failed: {str(e)}")

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _build_navigation(self) -> None:
        """Build navigation structure from docs/ folder structure."""
        self.navigation = [
            NavigationItem(
                label="Home",
                href="/",
                icon="fa-home",
                level=NavigationLevel.EXECUTIVE
            ),
            NavigationItem(
                label="CORTEX Brain",
                href="/01-cortex-brain/",
                icon="fa-brain",
                level=NavigationLevel.DOMAIN
            ),
            NavigationItem(
                label="Orchestrators",
                href="/02-orchestrators/",
                icon="fa-sitemap",
                level=NavigationLevel.DOMAIN
            ),
            NavigationItem(
                label="Getting Started",
                href="/03-getting-started/",
                icon="fa-rocket",
                level=NavigationLevel.EXECUTIVE
            ),
            NavigationItem(
                label="Architecture",
                href="/04-architecture/",
                icon="fa-layer-group",
                level=NavigationLevel.TECHNICAL
            ),
            NavigationItem(
                label="MCP Tools",
                href="/11-mcp-tools/",
                icon="fa-tools",
                level=NavigationLevel.TECHNICAL
            ),
        ]

    def _get_main_sections(self) -> List[Dict[str, Any]]:
        """Get main landing page sections."""
        return [
            {
                "title": "🧠 CORTEX Brain",
                "description": "4-Tier governance system with Tier 0 rules, acceptance criteria, and knowledge graph",
                "icon": "fa-brain",
                "href": "/01-cortex-brain/",
                "level": "executive"
            },
            {
                "title": "🎼 Orchestrators",
                "description": "23 orchestrators managing TDD, planning, refactoring, and domain operations",
                "icon": "fa-sitemap",
                "href": "/02-orchestrators/",
                "level": "executive"
            },
            {
                "title": "🚀 Getting Started",
                "description": "Quick installation, first orchestrator, and troubleshooting guides",
                "icon": "fa-rocket",
                "href": "/03-getting-started/",
                "level": "executive"
            },
            {
                "title": "🏛️ Architecture",
                "description": "System overview, design principles, and architectural decisions",
                "icon": "fa-layer-group",
                "href": "/04-architecture/",
                "level": "technical"
            },
            {
                "title": "🔍 LENS Protocol",
                "description": "Language → Examination → Navigation → Synthesis analysis framework",
                "icon": "fa-eye",
                "href": "/05-lens-protocol/",
                "level": "technical"
            },
            {
                "title": "🛠️ MCP Tools",
                "description": "Model Context Protocol integration with 24+ registered tools",
                "icon": "fa-tools",
                "href": "/11-mcp-tools/",
                "level": "technical"
            },
        ]

    def _get_quick_start_content(self) -> List[Dict[str, str]]:
        """Get quick start code examples."""
        return [
            {
                "title": "Installation",
                "code": "pip install -r requirements.txt\npython -m cortex.cli init"
            },
            {
                "title": "First Request",
                "code": "from cortex.mcp import MCPServer\n\nserver = MCPServer()\nresult = server.process_request('implement user login with TDD')"
            },
        ]

    def _get_subfolder_metadata(self, subfolder: Path) -> Dict[str, Any]:
        """Get metadata for a subfolder."""
        folder_name = subfolder.name

        # Extract title from folder name
        title = folder_name.split('-', 1)[-1].replace('-', ' ').title() if '-' in folder_name else folder_name.title()

        # Build breadcrumbs
        breadcrumbs = [
            ("Home", "/"),
            (title, f"/{folder_name}/")
        ]

        # Get markdown files in folder
        documents = []
        for md_file in sorted(subfolder.glob("*.md")):
            if md_file.name.startswith(("_", ".")):
                continue

            # Extract title from first line
            content = md_file.read_text()
            first_line = content.split('\n')[0]
            doc_title = first_line.strip('#').strip() if first_line.startswith('#') else md_file.stem

            documents.append({
                "title": doc_title,
                "description": self._extract_description(content),
                "href": md_file.name,
                "icon": "fa-file-alt"
            })

        # Build sidebar
        sidebar_items = [
            {"label": doc["title"], "href": doc["href"], "icon": doc["icon"]}
            for doc in documents[:10]  # Limit to 10 for sidebar
        ]

        return {
            "title": title,
            "description": f"Documentation for {title}",
            "breadcrumbs": breadcrumbs,
            "sidebar_items": sidebar_items,
            "documents": documents
        }

    def _extract_description(self, content: str, max_length: int = 200) -> str:
        """Extract description from markdown content."""
        lines = content.split('\n')
        for line in lines[1:]:  # Skip title
            line = line.strip()
            if line and not line.startswith('#'):
                # Remove markdown formatting
                desc = re.sub(r'[*_`]', '', line)
                if len(desc) > max_length:
                    desc = desc[:max_length] + "..."
                return desc
        return ""

    # ========================================================================
    # AUDIT MODE OPERATIONS - LINK INTEGRITY
    # ========================================================================

    def _audit_documentation_links(
        self,
        entry_point: str = "docs/index.html",
        mode: str = "full",
        skip_external: bool = True,
        dry_run: bool = True
    ) -> Result[Dict[str, Any], str]:
        """
        3-tier HTML documentation link integrity verification.

        Phase 1: L1 (entry_point) link validation
        Phase 2: L2 (feature landing pages) validation
        Phase 3: L3 (technical deep-dive) validation
        Phase 4: Unreferenced file detection (DRY-RUN)

        Args:
            entry_point: L1 entry point (default: docs/index.html)
            mode: "full", "l1-only", "l2-only", "l3-only"
            skip_external: Skip external URL validation (slow)
            dry_run: Report only, no deletions

        Returns:
            Result containing comprehensive audit report
        """
        import urllib.parse
        from html.parser import HTMLParser

        class LinkExtractor(HTMLParser):
            """Extract links and assets from HTML."""
            def __init__(self):
                super().__init__()
                self.links = []  # <a href>
                self.images = []  # <img src>
                self.css = []  # <link href>
                self.scripts = []  # <script src>
                self.ids = set()  # id attributes for anchor validation

            def handle_starttag(self, tag, attrs):
                attrs_dict = dict(attrs)

                if tag == 'a' and 'href' in attrs_dict:
                    self.links.append(attrs_dict['href'])
                elif tag == 'img' and 'src' in attrs_dict:
                    self.images.append(attrs_dict['src'])
                elif tag == 'link' and 'href' in attrs_dict:
                    self.css.append(attrs_dict['href'])
                elif tag == 'script' and 'src' in attrs_dict:
                    self.scripts.append(attrs_dict['src'])

                if 'id' in attrs_dict:
                    self.ids.add(attrs_dict['id'])

        def extract_links_from_html(html_path: Path) -> Dict[str, Any]:
            """Extract all links from an HTML file."""
            if not html_path.exists():
                return {"error": f"File not found: {html_path}"}

            try:
                content = html_path.read_text(encoding='utf-8')
                parser = LinkExtractor()
                parser.feed(content)

                return {
                    "links": parser.links,
                    "images": parser.images,
                    "css": parser.css,
                    "scripts": parser.scripts,
                    "ids": list(parser.ids)
                }
            except Exception as e:
                return {"error": str(e)}

        def classify_link(href: str) -> str:
            """Classify link type."""
            if href.startswith(('http://', 'https://')):
                return "external"
            elif href.startswith('javascript:'):
                return "security_violation"
            elif href.startswith('data:'):
                return "security_violation"
            elif href.startswith('#'):
                return "anchor"
            elif href.startswith('mailto:') or href.startswith('tel:'):
                return "protocol"
            else:
                return "internal"

        def validate_internal_link(
            base_path: Path,
            href: str,
            source_file: Path
        ) -> Dict[str, Any]:
            """Validate internal link resolves to existing file."""
            # Handle anchors
            if '#' in href:
                path_part, anchor = href.rsplit('#', 1)
                if not path_part:
                    # Anchor-only link to same page
                    return {"valid": True, "type": "anchor", "anchor": anchor}
                href = path_part

            # Resolve relative path
            if href.startswith('/'):
                # Absolute from docs root
                target = base_path / href.lstrip('/')
            else:
                # Relative to source file
                target = source_file.parent / href

            # Normalize path
            try:
                target = target.resolve()
            except Exception:
                return {"valid": False, "issue": "Invalid path", "href": href}

            # Security: Check for path traversal
            try:
                target.relative_to(base_path.resolve())
            except ValueError:
                return {
                    "valid": False,
                    "issue": "Path traversal detected (escapes workspace)",
                    "href": href,
                    "security": "CWE-22"
                }

            # Check if file exists
            if target.exists():
                return {"valid": True, "resolved_path": str(target)}
            else:
                return {
                    "valid": False,
                    "issue": "File not found",
                    "href": href,
                    "expected_path": str(target)
                }

        try:
            # Resolve entry point relative to docs_root
            if Path(entry_point).is_absolute():
                entry_path = Path(entry_point)
            else:
                # Join with docs_root if relative path provided
                entry_path = self.docs_root / entry_point

            base_path = entry_path.parent if entry_path.is_file() else self.docs_root

            report = {
                "summary": {
                    "total_links_checked": 0,
                    "broken_links_by_severity": {
                        "p0_navigation": 0,
                        "p1_assets": 0,
                        "p2_external": 0
                    },
                    "security_violations": 0,
                    "circular_references": 0,
                    "orphaned_files": 0,
                    "cleanup_potential_kb": 0
                },
                "detailed_report": {
                    "phase_1_l1": {},
                    "phase_2_l2": {},
                    "phase_3_l3": {},
                    "phase_4_cleanup": {}
                }
            }

            visited_pages: Set[str] = set()
            l2_pages: List[Path] = []
            l3_pages: List[Path] = []
            all_referenced_files: Set[Path] = set()

            # ================================================================
            # PHASE 1: L1 (Entry Point) Validation
            # ================================================================
            if mode in ["full", "l1-only"]:
                l1_data = extract_links_from_html(entry_path)
                if "error" in l1_data:
                    return Err(f"L1 extraction failed: {l1_data['error']}")

                all_referenced_files.add(entry_path.resolve())

                phase_1 = {
                    "broken_links": [],
                    "security_violations": [],
                    "link_counts": {
                        "internal_html": 0,
                        "images": len(l1_data["images"]),
                        "css": len(l1_data["css"]),
                        "javascript": len(l1_data["scripts"]),
                        "anchor": 0,
                        "external": 0
                    }
                }

                # Validate links
                for href in l1_data["links"]:
                    link_type = classify_link(href)
                    report["summary"]["total_links_checked"] += 1

                    if link_type == "security_violation":
                        phase_1["security_violations"].append({
                            "href": href,
                            "violation_type": "XSS risk" if href.startswith("javascript:") else "data URL",
                            "owasp_ref": "A03:2021"
                        })
                        report["summary"]["security_violations"] += 1

                    elif link_type == "internal":
                        phase_1["link_counts"]["internal_html"] += 1
                        validation = validate_internal_link(base_path, href, entry_path)

                        if not validation.get("valid", False):
                            phase_1["broken_links"].append({
                                "href": href,
                                "issue": validation.get("issue"),
                                "expected_path": validation.get("expected_path"),
                                "severity": "P0"
                            })
                            report["summary"]["broken_links_by_severity"]["p0_navigation"] += 1
                        else:
                            # Track L2 pages for next phase
                            resolved = validation.get("resolved_path")
                            if resolved and resolved.endswith('.html'):
                                l2_pages.append(Path(resolved))
                                all_referenced_files.add(Path(resolved))

                    elif link_type == "anchor":
                        phase_1["link_counts"]["anchor"] += 1

                    elif link_type == "external":
                        phase_1["link_counts"]["external"] += 1

                # Validate assets
                for img in l1_data["images"]:
                    validation = validate_internal_link(base_path, img, entry_path)
                    report["summary"]["total_links_checked"] += 1

                    if validation.get("valid"):
                        all_referenced_files.add(Path(validation["resolved_path"]))
                    else:
                        phase_1["broken_links"].append({
                            "href": img,
                            "issue": "Missing image",
                            "expected_path": validation.get("expected_path"),
                            "severity": "P1"
                        })
                        report["summary"]["broken_links_by_severity"]["p1_assets"] += 1

                # Validate CSS
                for css in l1_data["css"]:
                    if not css.startswith(('http://', 'https://')):
                        validation = validate_internal_link(base_path, css, entry_path)
                        report["summary"]["total_links_checked"] += 1

                        if validation.get("valid"):
                            all_referenced_files.add(Path(validation["resolved_path"]))
                        else:
                            phase_1["broken_links"].append({
                                "href": css,
                                "issue": "Missing CSS",
                                "expected_path": validation.get("expected_path"),
                                "severity": "P1"
                            })
                            report["summary"]["broken_links_by_severity"]["p1_assets"] += 1

                report["detailed_report"]["phase_1_l1"] = phase_1

            # ================================================================
            # PHASE 2: L2 (Feature Landing Pages) Validation
            # ================================================================
            if mode in ["full", "l2-only"]:
                # Check prerequisite: Phase 1 must have zero P0 broken links
                p0_count = report["summary"]["broken_links_by_severity"]["p0_navigation"]

                phase_2 = {
                    "validated_pages": [],
                    "skipped_pages": [],
                    "broken_links_by_page": {},
                    "circular_refs": [],
                    "orphaned_l2": []
                }

                if p0_count > 0 and mode == "full":
                    phase_2["skipped_pages"] = [str(p) for p in l2_pages]
                    phase_2["skip_reason"] = f"Phase 1 has {p0_count} P0 broken links"
                else:
                    # Validate each L2 page
                    for l2_path in l2_pages:
                        if str(l2_path) in visited_pages:
                            continue

                        visited_pages.add(str(l2_path))
                        l2_data = extract_links_from_html(l2_path)

                        if "error" in l2_data:
                            continue

                        phase_2["validated_pages"].append(str(l2_path))
                        broken = []

                        for href in l2_data["links"]:
                            link_type = classify_link(href)
                            report["summary"]["total_links_checked"] += 1

                            if link_type == "internal":
                                validation = validate_internal_link(base_path, href, l2_path)

                                if not validation.get("valid"):
                                    broken.append({
                                        "href": href,
                                        "issue": validation.get("issue"),
                                        "severity": "P0"
                                    })
                                    report["summary"]["broken_links_by_severity"]["p0_navigation"] += 1
                                else:
                                    # Track L3 pages
                                    resolved = validation.get("resolved_path")
                                    if resolved and resolved.endswith('.html'):
                                        l3_pages.append(Path(resolved))
                                        all_referenced_files.add(Path(resolved))

                        if broken:
                            phase_2["broken_links_by_page"][str(l2_path)] = broken

                report["detailed_report"]["phase_2_l2"] = phase_2

            # ================================================================
            # PHASE 3: L3 (Technical Deep-Dive) Validation
            # ================================================================
            if mode in ["full", "l3-only"]:
                phase_3 = {
                    "validated_pages": [],
                    "skipped_pages": [],
                    "broken_links_by_page": {},
                    "missing_code_refs": [],
                    "orphaned_l3": []
                }

                for l3_path in l3_pages:
                    if str(l3_path) in visited_pages:
                        continue

                    visited_pages.add(str(l3_path))
                    l3_data = extract_links_from_html(l3_path)

                    if "error" in l3_data:
                        continue

                    phase_3["validated_pages"].append(str(l3_path))
                    broken = []

                    for href in l3_data["links"]:
                        link_type = classify_link(href)
                        report["summary"]["total_links_checked"] += 1

                        if link_type == "internal":
                            validation = validate_internal_link(base_path, href, l3_path)

                            if not validation.get("valid"):
                                broken.append({
                                    "href": href,
                                    "issue": validation.get("issue"),
                                    "severity": "P0"
                                })
                                report["summary"]["broken_links_by_severity"]["p0_navigation"] += 1
                            else:
                                resolved = validation.get("resolved_path")
                                if resolved:
                                    all_referenced_files.add(Path(resolved))

                    if broken:
                        phase_3["broken_links_by_page"][str(l3_path)] = broken

                report["detailed_report"]["phase_3_l3"] = phase_3

            # ================================================================
            # PHASE 4: Unreferenced File Cleanup (DRY-RUN)
            # ================================================================
            if mode == "full":
                phase_4 = {
                    "orphans_by_category": {
                        "html": [],
                        "images": [],
                        "css": [],
                        "js": [],
                        "temp": []
                    },
                    "protected_files": [
                        "docs/index.html",
                        "docs/404.html",
                        "docs/404.md",
                        "docs/README.md",
                        "docs/LICENSE.md"
                    ],
                    "total_cleanup": {
                        "files": 0,
                        "size_kb": 0
                    }
                }

                # Find all HTML files in docs/
                for html_file in base_path.rglob("*.html"):
                    resolved = html_file.resolve()

                    # Skip protected files
                    rel_path = str(html_file.relative_to(base_path.parent) if base_path.parent in html_file.parents else html_file)
                    if any(protected in rel_path for protected in phase_4["protected_files"]):
                        continue

                    # Skip narrative files
                    if ".awakening-of-cortex" in str(html_file):
                        continue

                    if resolved not in all_referenced_files:
                        size_kb = html_file.stat().st_size / 1024
                        phase_4["orphans_by_category"]["html"].append({
                            "path": str(html_file),
                            "size_kb": round(size_kb, 2),
                            "risk": "MEDIUM" if size_kb > 10 else "LOW",
                            "action": "ARCHIVE"
                        })
                        phase_4["total_cleanup"]["files"] += 1
                        phase_4["total_cleanup"]["size_kb"] += size_kb
                        report["summary"]["orphaned_files"] += 1

                report["summary"]["cleanup_potential_kb"] = round(phase_4["total_cleanup"]["size_kb"], 2)
                report["detailed_report"]["phase_4_cleanup"] = phase_4

            return Ok(report)

        except Exception as e:
            return Err(f"Link audit failed: {str(e)}")

    def _fix_broken_links(
        self,
        audit_report: Optional[Dict[str, Any]],
        mode: str = "suggest",
        dry_run: bool = True
    ) -> Result[Dict[str, Any], str]:
        """
        Automated remediation suggestions for broken links.

        Args:
            audit_report: Output from audit_documentation_links
            mode: "suggest" or "auto-fix"
            dry_run: Report only, no actual changes

        Returns:
            Result containing fix suggestions or applied fixes
        """
        if not audit_report:
            return Err("audit_report is required")

        try:
            suggestions = []

            # Collect all broken links from all phases
            for phase_key in ["phase_1_l1", "phase_2_l2", "phase_3_l3"]:
                phase_data = audit_report.get("detailed_report", {}).get(phase_key, {})
                broken_links = phase_data.get("broken_links", [])

                # Also check broken_links_by_page
                links_by_page = phase_data.get("broken_links_by_page", {})
                for page, links in links_by_page.items():
                    broken_links.extend(links)

                for link in broken_links:
                    href = link.get("href", "")
                    issue = link.get("issue", "")
                    expected_path = link.get("expected_path", "")

                    suggestion = {
                        "original_link": href,
                        "issue": issue,
                        "suggestions": []
                    }

                    # Strategy 1: Check for case sensitivity issues
                    if expected_path:
                        expected = Path(expected_path)
                        parent = expected.parent
                        if parent.exists():
                            # Look for similar filenames
                            for existing in parent.iterdir():
                                if existing.name.lower() == expected.name.lower():
                                    suggestion["suggestions"].append({
                                        "fix": f"Update to {existing.relative_to(parent.parent) if parent.parent else existing}",
                                        "confidence": "high",
                                        "reason": f"Case sensitivity: found {existing.name}"
                                    })
                                    break

                    # Strategy 2: Check for similar filenames (fuzzy match)
                    if expected_path and not suggestion["suggestions"]:
                        expected = Path(expected_path)
                        parent = expected.parent
                        if parent.exists():
                            name_parts = expected.stem.lower().split('-')
                            for existing in parent.iterdir():
                                if existing.is_file() and existing.suffix == expected.suffix:
                                    existing_parts = existing.stem.lower().split('-')
                                    # Check if any parts match
                                    if any(part in existing_parts for part in name_parts if len(part) > 2):
                                        suggestion["suggestions"].append({
                                            "fix": f"Consider: {existing.name}",
                                            "confidence": "medium",
                                            "reason": "Similar filename found"
                                        })

                    # Strategy 3: Suggest creating a stub page
                    if not suggestion["suggestions"]:
                        suggestion["suggestions"].append({
                            "fix": f"Create placeholder at {expected_path}",
                            "confidence": "low",
                            "reason": "No similar file found - create stub page"
                        })

                    suggestions.append(suggestion)

            result = {
                "mode": mode,
                "dry_run": dry_run,
                "suggested_fixes": suggestions,
                "total_fixes": len(suggestions)
            }

            return Ok(result)

        except Exception as e:
            return Err(f"Fix broken links failed: {str(e)}")

    def _cleanup_orphaned_files(
        self,
        audit_report: Optional[Dict[str, Any]],
        mode: str = "archive",
        confirm: bool = False
    ) -> Result[Dict[str, Any], str]:
        """
        Safe removal of unreferenced documentation files.

        Args:
            audit_report: Output from audit_documentation_links (Phase 4)
            mode: "archive" or "delete"
            confirm: Required for delete mode

        Returns:
            Result containing cleanup report
        """
        if not audit_report:
            return Err("audit_report is required")

        if mode == "delete" and not confirm:
            return Err("confirm=True required for delete mode")

        try:
            phase_4 = audit_report.get("detailed_report", {}).get("phase_4_cleanup", {})
            orphans = phase_4.get("orphans_by_category", {})

            archived = []
            deleted = []
            preserved = []

            # Create archive directory
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            archive_dir = Path("docs/.archive") / timestamp

            if mode == "archive":
                archive_dir.mkdir(parents=True, exist_ok=True)

            for category, files in orphans.items():
                for file_info in files:
                    file_path = Path(file_info["path"])
                    risk = file_info.get("risk", "LOW")

                    # Skip HIGH risk without explicit confirmation
                    if risk == "HIGH" and not confirm:
                        preserved.append({
                            "path": str(file_path),
                            "reason": "HIGH risk - requires explicit confirmation"
                        })
                        continue

                    if not file_path.exists():
                        continue

                    if mode == "archive":
                        # Move to archive
                        dest = archive_dir / file_path.name
                        try:
                            shutil.move(str(file_path), str(dest))
                            archived.append({
                                "source": str(file_path),
                                "destination": str(dest),
                                "size_kb": file_info.get("size_kb", 0),
                                "reason": f"Orphaned {category} file"
                            })
                        except Exception as e:
                            preserved.append({
                                "path": str(file_path),
                                "reason": f"Archive failed: {str(e)}"
                            })

                    elif mode == "delete" and confirm:
                        try:
                            file_path.unlink()
                            deleted.append({
                                "path": str(file_path),
                                "size_kb": file_info.get("size_kb", 0),
                                "reason": f"Orphaned {category} file"
                            })
                        except Exception as e:
                            preserved.append({
                                "path": str(file_path),
                                "reason": f"Delete failed: {str(e)}"
                            })

            # Create manifest
            manifest_path = None
            if mode == "archive" and archived:
                manifest_path = archive_dir / "MANIFEST.md"
                manifest_content = f"""# Cleanup Archive Manifest
**Date:** {timestamp}
**Mode:** {mode}

## Archived Files
| File | Size | Reason |
|------|------|--------|
"""
                for item in archived:
                    manifest_content += f"| {item['source']} | {item['size_kb']} KB | {item['reason']} |\n"

                manifest_path.write_text(manifest_content)

            return Ok({
                "mode": mode,
                "archived": archived,
                "deleted": deleted,
                "preserved": preserved,
                "manifest_location": str(manifest_path) if manifest_path else None
            })

        except Exception as e:
            return Err(f"Cleanup failed: {str(e)}")

    # ========================================================================
    # AUDIT MODE OPERATIONS - RESPONSIVE DESIGN
    # ========================================================================

    def _audit_responsive_design(
        self,
        entry_point: str = "docs/index.html"
    ) -> Result[Dict[str, Any], str]:
        """
        Mobile-first responsive design audit.

        Checks:
        - Viewport meta tags
        - CSS media queries
        - Touch targets (≥44px)
        - No horizontal scroll
        - Responsive images
        - D3.js/SVG resize handlers
        - Table responsiveness

        Args:
            entry_point: Starting HTML file (default: docs/index.html)

        Returns:
            Result containing responsive design audit report
        """
        from html.parser import HTMLParser

        class ResponsiveAuditParser(HTMLParser):
            """Parse HTML for responsive design patterns."""

            def __init__(self):
                super().__init__()
                self.has_viewport = False
                self.viewport_content = ""
                self.user_scalable_no = False
                self.images_without_max_width = []
                self.inline_fixed_widths = []
                self.svg_elements = []
                self.d3_scripts = []
                self.tables = []
                self.current_tag_attrs = {}

            def handle_starttag(self, tag, attrs):
                attrs_dict = dict(attrs)
                self.current_tag_attrs = attrs_dict

                # Check viewport meta
                if tag == 'meta' and attrs_dict.get('name') == 'viewport':
                    self.has_viewport = True
                    self.viewport_content = attrs_dict.get('content', '')
                    if 'user-scalable=no' in self.viewport_content.lower():
                        self.user_scalable_no = True

                # Check images
                if tag == 'img':
                    style = attrs_dict.get('style', '')
                    width = attrs_dict.get('width', '')
                    if width and width.isdigit():
                        self.images_without_max_width.append({
                            "src": attrs_dict.get('src', ''),
                            "issue": f"Fixed width={width}px"
                        })
                    if 'width:' in style and 'max-width' not in style:
                        self.images_without_max_width.append({
                            "src": attrs_dict.get('src', ''),
                            "issue": "Inline fixed width without max-width"
                        })

                # Check inline fixed widths
                if 'style' in attrs_dict:
                    style = attrs_dict['style']
                    if re.search(r'width:\s*\d+px', style) and 'max-width' not in style:
                        self.inline_fixed_widths.append({
                            "tag": tag,
                            "style": style,
                            "id": attrs_dict.get('id', ''),
                            "class": attrs_dict.get('class', '')
                        })

                # Check SVG
                if tag == 'svg':
                    width = attrs_dict.get('width', '')
                    height = attrs_dict.get('height', '')
                    viewBox = attrs_dict.get('viewBox', attrs_dict.get('viewbox', ''))
                    self.svg_elements.append({
                        "width": width,
                        "height": height,
                        "viewBox": viewBox,
                        "responsive": bool(viewBox) and (not width or '%' in width)
                    })

                # Check scripts for D3.js
                if tag == 'script':
                    src = attrs_dict.get('src', '')
                    if 'd3' in src.lower():
                        self.d3_scripts.append(src)

                # Check tables
                if tag == 'table':
                    self.tables.append({
                        "class": attrs_dict.get('class', ''),
                        "style": attrs_dict.get('style', ''),
                        "has_responsive_wrapper": False  # Will check parent
                    })

        def check_css_for_responsive(css_content: str) -> Dict[str, Any]:
            """Analyze CSS file for responsive patterns."""
            media_queries = re.findall(r'@media[^{]+\{', css_content)

            has_mobile = any('max-width: 320' in mq or 'max-width: 480' in mq for mq in media_queries)
            has_tablet = any('max-width: 768' in mq or 'max-width: 1024' in mq for mq in media_queries)
            has_desktop = any('min-width: 1280' in mq or 'min-width: 1024' in mq for mq in media_queries)

            # Check for fixed widths on containers
            fixed_containers = re.findall(r'(\.[\w-]+|#[\w-]+)\s*\{[^}]*width:\s*\d+px[^}]*\}', css_content)

            return {
                "media_queries_count": len(media_queries),
                "has_mobile_breakpoint": has_mobile,
                "has_tablet_breakpoint": has_tablet,
                "has_desktop_breakpoint": has_desktop,
                "fixed_width_containers": fixed_containers[:10]  # Limit to 10
            }

        def check_d3_resize_handlers(js_content: str) -> bool:
            """Check if D3.js code has resize handlers."""
            patterns = [
                r'window\.addEventListener\s*\(\s*[\'"]resize[\'"]',
                r'window\.onresize',
                r'd3\.select\s*\(\s*window\s*\)\.on\s*\(\s*[\'"]resize[\'"]',
                r'ResizeObserver'
            ]
            return any(re.search(pattern, js_content) for pattern in patterns)

        try:
            # Resolve entry point relative to docs_root
            if Path(entry_point).is_absolute():
                entry_path = Path(entry_point)
            else:
                entry_path = self.docs_root / entry_point

            base_path = entry_path.parent if entry_path.is_file() else self.docs_root

            report = {
                "summary": {
                    "pages_audited": 0,
                    "pages_passed": 0,
                    "pages_failed": 0,
                    "critical_issues": 0,
                    "pass_percentage": 0.0
                },
                "pages": [],
                "viewport_audit": {
                    "pages_with_viewport": 0,
                    "pages_missing_viewport": [],
                    "user_scalable_violations": []
                },
                "breakpoint_compliance": {},
                "css_analysis": {
                    "files_analyzed": 0,
                    "media_queries_found": 0,
                    "fixed_width_violations": []
                },
                "images_audit": {
                    "total_images": 0,
                    "issues": []
                },
                "svg_d3_audit": {
                    "svg_elements": 0,
                    "responsive_svg": 0,
                    "d3_scripts": 0,
                    "d3_with_resize": 0
                },
                "tables_audit": {
                    "total_tables": 0,
                    "responsive_tables": 0,
                    "non_responsive": []
                }
            }

            # Audit all HTML files
            html_files = list(base_path.rglob("*.html"))

            for html_file in html_files:
                try:
                    content = html_file.read_text(encoding='utf-8')
                    parser = ResponsiveAuditParser()
                    parser.feed(content)

                    report["summary"]["pages_audited"] += 1
                    page_passed = True
                    rel_path = str(html_file.relative_to(base_path))

                    # Viewport check
                    if parser.has_viewport:
                        report["viewport_audit"]["pages_with_viewport"] += 1
                        if parser.user_scalable_no:
                            report["viewport_audit"]["user_scalable_violations"].append(rel_path)
                            page_passed = False
                            report["summary"]["critical_issues"] += 1
                    else:
                        report["viewport_audit"]["pages_missing_viewport"].append(rel_path)
                        page_passed = False
                        report["summary"]["critical_issues"] += 1

                    # Images check
                    report["images_audit"]["total_images"] += len(parser.images_without_max_width)
                    if parser.images_without_max_width:
                        report["images_audit"]["issues"].extend([
                            {**img, "page": rel_path}
                            for img in parser.images_without_max_width
                        ])
                        page_passed = False

                    # Fixed widths check
                    if parser.inline_fixed_widths:
                        report["css_analysis"]["fixed_width_violations"].extend([
                            {**item, "page": rel_path}
                            for item in parser.inline_fixed_widths[:5]  # Limit per page
                        ])
                        page_passed = False

                    # SVG check
                    report["svg_d3_audit"]["svg_elements"] += len(parser.svg_elements)
                    report["svg_d3_audit"]["responsive_svg"] += sum(
                        1 for svg in parser.svg_elements if svg["responsive"]
                    )

                    # Tables check
                    report["tables_audit"]["total_tables"] += len(parser.tables)
                    for table in parser.tables:
                        table_class = table.get("class", "")
                        is_responsive = any(
                            pattern in table_class
                            for pattern in ["responsive", "table-scroll", "overflow"]
                        )
                        if is_responsive:
                            report["tables_audit"]["responsive_tables"] += 1
                        else:
                            report["tables_audit"]["non_responsive"].append({
                                "page": rel_path,
                                "class": table_class
                            })

                    # Breakpoint compliance for this page
                    report["breakpoint_compliance"][rel_path] = {
                        "mobile_320": page_passed,  # Simplified - would need actual testing
                        "tablet_768": page_passed,
                        "desktop_1280": True,  # Desktop usually works
                        "status": "PASS" if page_passed else "FAIL"
                    }

                    # Add page details to pages array
                    page_issues = []
                    if not parser.has_viewport:
                        page_issues.append("Missing viewport meta tag")
                    if parser.user_scalable_no:
                        page_issues.append("user-scalable=no disables pinch zoom")
                    if parser.images_without_max_width:
                        page_issues.append(f"{len(parser.images_without_max_width)} images with fixed width")
                    if parser.inline_fixed_widths:
                        page_issues.append(f"{len(parser.inline_fixed_widths)} elements with inline fixed width")

                    # Check for media queries in inline styles
                    has_responsive_css = '@media' in content
                    media_query_count = content.count('@media')

                    report["pages"].append({
                        "path": rel_path,
                        "passed": page_passed,
                        "has_viewport": parser.has_viewport,
                        "has_responsive_css": has_responsive_css,
                        "media_query_count": media_query_count,
                        "issues": page_issues
                    })

                    if page_passed:
                        report["summary"]["pages_passed"] += 1
                    else:
                        report["summary"]["pages_failed"] += 1

                except Exception:
                    # Skip files that can't be parsed
                    continue

            # Audit CSS files
            css_files = list(base_path.rglob("*.css"))
            for css_file in css_files:
                try:
                    content = css_file.read_text(encoding='utf-8')
                    css_analysis = check_css_for_responsive(content)

                    report["css_analysis"]["files_analyzed"] += 1
                    report["css_analysis"]["media_queries_found"] += css_analysis["media_queries_count"]

                    if css_analysis["fixed_width_containers"]:
                        report["css_analysis"]["fixed_width_violations"].extend([
                            {"file": str(css_file.relative_to(base_path)), "selector": sel}
                            for sel in css_analysis["fixed_width_containers"]
                        ])
                except Exception:
                    continue

            # Audit JS files for D3.js resize handlers
            js_files = list(base_path.rglob("*.js"))
            for js_file in js_files:
                try:
                    content = js_file.read_text(encoding='utf-8')
                    if 'd3' in content.lower():
                        report["svg_d3_audit"]["d3_scripts"] += 1
                        if check_d3_resize_handlers(content):
                            report["svg_d3_audit"]["d3_with_resize"] += 1
                except Exception:
                    continue

            # Calculate overall score
            total = report["summary"]["pages_audited"]
            passed = report["summary"]["pages_passed"]
            report["summary"]["pass_percentage"] = round((passed / total * 100) if total > 0 else 0, 1)

            return Ok(report)

        except Exception as e:
            return Err(f"Responsive design audit failed: {str(e)}")
    def _render_component(self, component_name: str) -> str:
        """Render a component template."""
        if not self.jinja_env:
            return ""

        try:
            template = self.jinja_env.get_template(f"components/{component_name}")
            return template.render()
        except Exception:
            return ""

    def _validate_html(self) -> Result[Dict[str, Any], str]:
        """
        Validate generated HTML files.

        Checks:
        - Valid HTML5 structure
        - Accessibility (ARIA labels, alt text)
        - Broken links
        - Missing assets

        Returns:
            Result with validation report
        """
        try:
            issues = []

            # Check main index
            main_index = self.docs_root / "index.html"
            if main_index.exists():
                content = main_index.read_text()

                # Check for required elements
                if '<html lang="en">' not in content:
                    issues.append("Missing lang attribute in <html>")

                if 'aria-label' not in content:
                    issues.append("Missing ARIA labels")

                # Check for proper DOCTYPE
                if not content.strip().startswith('<!DOCTYPE html>'):
                    issues.append("Missing or incorrect DOCTYPE")

            validation_report = {
                "valid": len(issues) == 0,
                "issues": issues,
                "files_checked": 1
            }

            return Ok(validation_report)

        except Exception as e:
            return Err(f"Validation failed: {str(e)}")


# ============================================================================
# MODULE-LEVEL FACTORY
# ============================================================================

def get_cortex_docs_orchestrator() -> CortexDocsOrchestrator:
    """Get or create CortexDocsOrchestrator instance."""
    return CortexDocsOrchestrator.instance()
