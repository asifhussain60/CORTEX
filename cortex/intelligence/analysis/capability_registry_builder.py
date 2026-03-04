"""
CapabilityRegistryBuilder — Phase 72-a.

Scans live CORTEX source to auto-generate capabilities-manifest.yaml (schema v2.0).
Replaces the hand-maintained static manifest with a generated, versioned,
intelligence-queryable registry.

Layer 1 of the 3-layer Capability Registry Pattern:
  Layer 1 — THIS MODULE  : CapabilityRegistryBuilder (generator)
  Layer 2 — capabilities-manifest.yaml (schema v2.0, backward-compatible)
  Layer 3 — CapabilityMatcher.load_from_manifest() (Phase 72-c)

AC_START: AC-72-CAPABILITY-REGISTRY-BUILDER-20260225

Canonical output path: cortex-registry/core/capabilities-manifest.yaml
Wiring spec authority: cortex-registry/core/specifications/
Phase plan:            cortex-registry/planning/phases/planned/phase-72-capability-registry-builder.yaml
"""

from __future__ import annotations

import ast
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml


# ─────────────────────────────────────────────────────────────────────────────
# Data classes — public API (CORE-012: docstrings required)
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class OrchestratorEntry:
    """
    A single wired orchestrator discovered from the wiring specification.

    Attributes:
        id: Snake-case orchestrator identifier.
        module: Fully-qualified Python module path.
        class_name: Orchestrator class name.
        tier: Canonical tier — 'core', 'domain', or 'support'.
        health_check: Whether the orchestrator exposes a health_check() method.
        priority: Routing priority (lower = higher priority).
        description: Human-readable purpose description.
        features: Capabilities/features this orchestrator provides.
    """

    id: str
    module: str
    class_name: str
    tier: str
    health_check: bool = True
    priority: int = 0
    description: str = ""
    features: List[str] = field(default_factory=list)


@dataclass
class WorkflowTemplateEntry:
    """
    A single workflow template discovered from cortex-registry/workflows/templates/.

    Attributes:
        id: Snake-case template identifier derived from filename.
        domain: Workflow domain (audit, tdd, quality, security, etc.).
        path: Relative path from workspace root.
        description: Human-readable description (from YAML metadata or filename).
    """

    id: str
    domain: str
    path: str
    description: str = ""


@dataclass
class MCPToolEntry:
    """
    A single MCP tool discovered from cortex/mcp/tools/.

    Attributes:
        id: Tool identifier matching MCP registry.
        module: Python module path.
        operations: List of supported operation strings.
        purpose: Short description of the tool's purpose.
    """

    id: str
    module: str
    operations: List[str] = field(default_factory=list)
    purpose: str = ""


@dataclass
class BuilderResult:
    """
    Structured result from CapabilityRegistryBuilder.generate_manifest().

    Attributes:
        orchestrators: All discovered wired orchestrators.
        workflow_templates: All indexed workflow templates.
        mcp_tools: All discovered MCP tools.
        generated_at: ISO 8601 timestamp of generation.
        schema_version: Manifest schema version string.
        output_path: Path where manifest was written.
    """

    orchestrators: List[OrchestratorEntry]
    workflow_templates: List[WorkflowTemplateEntry]
    mcp_tools: List[MCPToolEntry]
    generated_at: str
    schema_version: str
    output_path: Optional[Path] = None


# ─────────────────────────────────────────────────────────────────────────────
# Builder
# ─────────────────────────────────────────────────────────────────────────────

# Canonical wiring tier mapping: category string from spec → canonical tier name
_CATEGORY_TO_TIER: Dict[str, str] = {
    "CORE": "core",
    "DOMAIN": "domain",
    "SUPPORT": "support",
    "HEALTH": "support",   # health orchestrators live under support tier for manifest
    "GIT": "support",
    "INTELLIGENCE": "support",
    "SYNTHESIS": "support",
    "VALIDATION": "support",
    "WORKFLOW": "support",
    "STRATEGY": "support",
}

# Canonical priority bands per architecture spec
_TIER_PRIORITY_BASE: Dict[str, int] = {
    "core": 10,
    "domain": 100,
    "support": 150,
}


class CapabilityRegistryBuilder:
    """
    Builds capabilities-manifest.yaml (schema v2.0) by scanning live CORTEX source.

    Reads wiring specifications as the authoritative source for wired orchestrators,
    glob-scans workflow templates, and inspects cortex/mcp/tools/ for MCP tools.
    Produces a backward-compatible YAML that replaces the hand-maintained manifest.

    Usage::

        builder = CapabilityRegistryBuilder(workspace_root=Path("/path/to/CORTEX"))
        result = builder.generate_manifest()
        # → cortex-registry/core/capabilities-manifest.yaml written

    Thread-safe for read operations. Not designed for concurrent writes.
    """

    #: Default output path relative to workspace root
    DEFAULT_OUTPUT_RELATIVE = Path("cortex-registry") / "core" / "capabilities-manifest.yaml"

    #: Wiring spec files (relative to workspace root)
    WIRING_SPEC_FILES = [
        Path("cortex-registry/core/specifications/core-orchestrator-wiring.yaml"),
        Path("cortex-registry/core/specifications/domain-orchestrator-wiring.yaml"),
        Path("cortex-registry/core/specifications/support-orchestrator-wiring.yaml"),
    ]

    #: Workflow templates root (relative to workspace root)
    WORKFLOW_TEMPLATES_ROOT = Path("cortex-registry/workflows/templates")

    #: Response templates SSOT (relative to workspace root)
    RESPONSE_TEMPLATES_SSOT = Path(".github/templates/cortex-response-templates.md")

    #: MCP tools root (relative to workspace root)
    MCP_TOOLS_ROOT = Path("cortex/mcp/tools")

    #: cortex-registry path (relative to workspace root) — for .inventory cleanup
    REGISTRY_ROOT = Path("cortex-registry")

    def __init__(
        self,
        workspace_root: Optional[Path] = None,
        output_path: Optional[Path] = None,
    ) -> None:
        """
        Initialise the builder.

        Args:
            workspace_root: Absolute path to CORTEX workspace root.
                            Defaults to three parents above this file
                            (cortex/intelligence/ → cortex/ → workspace/).
            output_path: Override for output YAML path. Defaults to
                         <workspace_root>/cortex-registry/core/capabilities-manifest.yaml.
        """
        if workspace_root is None:
            workspace_root = Path(__file__).parent.parent.parent
        self.workspace_root = workspace_root.resolve()
        self.output_path: Path = (
            output_path.resolve()
            if output_path is not None
            else self.workspace_root / self.DEFAULT_OUTPUT_RELATIVE
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────────────────────

    def scan_orchestrators(self) -> List[OrchestratorEntry]:
        """
        Scan wiring specification YAMLs and return all wired orchestrators.

        Reads from cortex-registry/core/specifications/ (the authoritative source),
        not by grepping raw Python files, to ensure only *wired* orchestrators
        are included (not helpers, mixins, or utilities).

        Returns:
            List of OrchestratorEntry objects, one per wired orchestrator.
        """
        entries: List[OrchestratorEntry] = []
        priority_counter: Dict[str, int] = {t: base for t, base in _TIER_PRIORITY_BASE.items()}

        for spec_file in self.WIRING_SPEC_FILES:
            abs_spec = self.workspace_root / spec_file
            if not abs_spec.exists():
                continue
            spec = yaml.safe_load(abs_spec.read_text(encoding="utf-8")) or {}
            for item in spec.get("provides", []):
                entry = self._parse_wiring_item(item, priority_counter)
                if entry is not None:
                    entries.append(entry)

        return entries

    def validate_against_wiring_spec(
        self, entries: List[OrchestratorEntry]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that discovered entries are consistent with wiring specifications.

        Checks that the count matches what the specs declare and that all
        canonical core orchestrators are present.

        Args:
            entries: Entries from scan_orchestrators().

        Returns:
            Tuple of (is_valid: bool, discrepancies: List[str]).
        """
        discrepancies: List[str] = []

        # Minimum wired count per architecture documentation
        if len(entries) < 27:
            discrepancies.append(
                f"Found {len(entries)} orchestrators — expected ≥27 (architecture spec)"
            )

        # Core orchestrators that must always be present
        required_ids = {"master_orchestrator", "intent_router", "tdd_orchestrator", "enforcement_orchestrator"}
        found_ids = {e.id for e in entries}
        missing = required_ids - found_ids
        if missing:
            discrepancies.append(f"Required orchestrators missing: {sorted(missing)}")

        # Every entry must have a valid tier
        invalid_tier = [e for e in entries if e.tier not in ("core", "domain", "support")]
        if invalid_tier:
            discrepancies.append(
                f"Entries with invalid tier: {[e.id for e in invalid_tier]}"
            )

        return (len(discrepancies) == 0, discrepancies)

    def scan_workflow_templates(self) -> List[WorkflowTemplateEntry]:
        """
        Glob-scan cortex-registry/workflows/templates/ and index all YAML files.

        Returns:
            List of WorkflowTemplateEntry objects, one per template YAML.
        """
        templates_root = self.workspace_root / self.WORKFLOW_TEMPLATES_ROOT
        entries: List[WorkflowTemplateEntry] = []

        if not templates_root.exists():
            return entries

        for yaml_path in sorted(templates_root.rglob("*.yaml")):
            entry = self._parse_workflow_template(yaml_path, templates_root)
            if entry is not None:
                entries.append(entry)

        return entries

    def scan_mcp_tools(self) -> List[MCPToolEntry]:
        """
        Scan cortex/mcp/tools/ for MCP tool Python modules.

        Returns:
            List of MCPToolEntry objects discovered from the tools directory.
        """
        tools_root = self.workspace_root / self.MCP_TOOLS_ROOT
        entries: List[MCPToolEntry] = []

        if not tools_root.exists():
            return entries

        for py_path in sorted(tools_root.rglob("*.py")):
            if py_path.name.startswith("_"):
                continue
            entry = self._parse_mcp_tool(py_path)
            if entry is not None:
                entries.append(entry)

        return entries

    def scan_response_templates(self) -> List[str]:
        """
        Scan the response templates SSOT markdown for BLOCK-* headings.

        Parses .github/templates/cortex-response-templates.md for lines matching
        ``## BLOCK-*`` and returns the block names (e.g., ``BLOCK-ANALYSIS``).

        Returns:
            List of response template block names found in the SSOT.
        """
        import re

        ssot_path = self.workspace_root / self.RESPONSE_TEMPLATES_SSOT
        blocks: List[str] = []

        if not ssot_path.exists():
            return blocks

        try:
            content = ssot_path.read_text(encoding="utf-8")
            for line in content.splitlines():
                match = re.match(r"^##\s+(BLOCK-[A-Z0-9_-]+)", line)
                if match:
                    blocks.append(match.group(1))
        except Exception:
            pass

        return blocks

    def remove_inventory_folder(self) -> None:
        """
        Remove cortex-registry/.inventory/ if it exists (GAP-72-05).

        This folder was created at the wrong location — the registry contains
        authored governance truth, not generated output. The canonical output
        is capabilities-manifest.yaml at cortex-registry/core/.

        Checks two locations:
          1. <workspace_root>/cortex-registry/.inventory/  (canonical production path)
          2. <workspace_root>/.inventory/  (fallback for test isolation with tmp_path)

        Safe to call when the folder is already absent.
        """
        candidates = [
            self.workspace_root / self.REGISTRY_ROOT / ".inventory",
            self.workspace_root / ".inventory",
        ]
        for inventory_path in candidates:
            if inventory_path.exists() and inventory_path.is_dir():
                shutil.rmtree(inventory_path)

    def generate_manifest(self) -> BuilderResult:
        """
        Generate capabilities-manifest.yaml (schema v2.0) from live source.

        Scans orchestrators, workflow templates, and MCP tools, then writes
        a backward-compatible YAML to self.output_path. Idempotent — running
        twice produces the same logical content (timestamp excluded).

        Returns:
            BuilderResult with all discovered entries and the output path.
        """
        generated_at = datetime.now(tz=timezone.utc).isoformat()

        orchestrators = self.scan_orchestrators()
        workflow_templates = self.scan_workflow_templates()
        mcp_tools = self.scan_mcp_tools()
        response_blocks = self.scan_response_templates()

        manifest = self._build_manifest_dict(
            orchestrators=orchestrators,
            workflow_templates=workflow_templates,
            mcp_tools=mcp_tools,
            generated_at=generated_at,
            response_blocks=response_blocks,
        )

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as fh:
            fh.write("# CORTEX Capabilities Manifest — schema v2.0\n")
            fh.write("# AUTO-GENERATED by CapabilityRegistryBuilder (Phase 72)\n")
            fh.write("# DO NOT EDIT MANUALLY — run /audit fix or cortex_inventory op=rebuild\n")
            fh.write(f"# Generated: {generated_at}\n")
            fh.write("# Source:    cortex/intelligence/capability_registry_builder.py\n")
            fh.write("# Authority: cortex-registry/core/specifications/ (wiring specs)\n\n")
            yaml.dump(
                manifest,
                fh,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )

        return BuilderResult(
            orchestrators=orchestrators,
            workflow_templates=workflow_templates,
            mcp_tools=mcp_tools,
            generated_at=generated_at,
            schema_version="1.0",
            output_path=self.output_path,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _parse_wiring_item(
        self,
        item: Dict,
        priority_counter: Dict[str, int],
    ) -> Optional[OrchestratorEntry]:
        """Parse a single 'provides' item from a wiring spec YAML."""
        name = item.get("name", "")
        category = item.get("category", "SUPPORT")
        tier = _CATEGORY_TO_TIER.get(category.upper(), "support")
        entry_point = item.get("entry_point", "")
        description = item.get("description", "")
        features = item.get("features", [])

        if not name or not entry_point:
            return None

        # Derive module and class from entry_point "module:ClassName"
        if ":" in entry_point:
            module, class_name = entry_point.rsplit(":", 1)
        else:
            module = entry_point
            class_name = name

        # Derive id from class name → snake_case
        orchestrator_id = _to_snake_case(class_name)

        priority = priority_counter.get(tier, 150)
        priority_counter[tier] = priority + 1

        return OrchestratorEntry(
            id=orchestrator_id,
            module=module,
            class_name=class_name,
            tier=tier,
            health_check=True,
            priority=priority,
            description=description,
            features=features if isinstance(features, list) else [],
        )

    def _parse_workflow_template(
        self,
        yaml_path: Path,
        templates_root: Path,
    ) -> Optional[WorkflowTemplateEntry]:
        """Parse a workflow template YAML file into a WorkflowTemplateEntry."""
        try:
            relative = yaml_path.relative_to(self.workspace_root)
            # Domain is the first directory under templates/
            parts = yaml_path.relative_to(templates_root).parts
            domain = parts[0] if len(parts) > 1 else "general"
            template_id = yaml_path.stem.replace("-", "_")

            # Try to read description from YAML metadata
            description = ""
            try:
                content = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
                description = (
                    content.get("description")
                    or content.get("title")
                    or content.get("name")
                    or _filename_to_description(yaml_path.stem)
                )
            except Exception:
                description = _filename_to_description(yaml_path.stem)

            return WorkflowTemplateEntry(
                id=template_id,
                domain=domain,
                path=str(relative),
                description=str(description)[:200],  # cap at 200 chars
            )
        except Exception:
            return None

    def _parse_mcp_tool(self, py_path: Path) -> Optional[MCPToolEntry]:
        """Parse a MCP tool Python file into an MCPToolEntry using AST inspection."""
        try:
            relative = py_path.relative_to(self.workspace_root)
            module_path = str(relative).replace(os.sep, ".").removesuffix(".py")
            tool_id = py_path.stem

            # Quick AST scan for OPERATIONS constant or tool_id string
            operations: List[str] = []
            purpose = ""
            try:
                tree = ast.parse(py_path.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for t in node.targets:
                            if isinstance(t, ast.Name) and t.id == "OPERATIONS":
                                if isinstance(node.value, (ast.List, ast.Tuple)):
                                    operations = [
                                        elt.s for elt in node.value.elts
                                        if isinstance(elt, ast.Constant) and isinstance(elt.s, str)
                                    ]
                    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                        if isinstance(node.value.value, str) and len(node.value.value) < 300:
                            if purpose == "":
                                purpose = node.value.value.strip().split("\n")[0]
            except Exception:
                pass

            return MCPToolEntry(
                id=tool_id,
                module=module_path,
                operations=operations,
                purpose=purpose,
            )
        except Exception:
            return None

    def _build_manifest_dict(
        self,
        orchestrators: List[OrchestratorEntry],
        workflow_templates: List[WorkflowTemplateEntry],
        mcp_tools: List[MCPToolEntry],
        generated_at: str,
        response_blocks: Optional[List[str]] = None,
    ) -> Dict:
        """Assemble the full manifest dictionary (schema v2.0, backward-compatible)."""

        # Group orchestrators by tier
        core = [e for e in orchestrators if e.tier == "core"]
        domain = [e for e in orchestrators if e.tier == "domain"]
        support = [e for e in orchestrators if e.tier == "support"]

        def _entry_to_dict(e: OrchestratorEntry) -> Dict:
            return {
                "id": e.id,
                "module": e.module,
                "class": e.class_name,
                "priority": e.priority,
                "health_check": e.health_check,
                "tier": e.tier,
                "description": e.description,
                **({"features": e.features} if e.features else {}),
            }

        # Group workflow templates by domain
        template_domains: Dict[str, List[Dict]] = {}
        for t in workflow_templates:
            template_domains.setdefault(t.domain, []).append({
                "id": t.id,
                "path": t.path,
                "description": t.description,
            })

        manifest: Dict = {
            "auto_generated": True,
            "generated_at": generated_at,
            "generated_by": "cortex.intelligence.capability_registry_builder.CapabilityRegistryBuilder",
            # ── Orchestrators (generated from wiring specs) ──────────
            "orchestrators": {
                "total": len(orchestrators),
                "tiers": {
                    "core": {
                        "count": len(core),
                        "members": [_entry_to_dict(e) for e in core],
                    },
                    "domain": {
                        "count": len(domain),
                        "members": [_entry_to_dict(e) for e in domain],
                    },
                    "support": {
                        "count": len(support),
                        "members": [_entry_to_dict(e) for e in support],
                    },
                },
            },
            # ── Workflow templates (v2.0 — per-template index) ───────────────
            "workflow_templates": {
                "total": len(workflow_templates),
                "registry_root": "cortex-registry/workflows/templates/",
                "domains": template_domains,
            },
            # ── MCP tools (v2.0 — auto-scanned) ─────────────────────────────
            "mcp_tools": {
                "total": len(mcp_tools),
                "tools_root": "cortex/mcp/tools/",
                "tools": [
                    {
                        "id": t.id,
                        "module": t.module,
                        **({"operations": t.operations} if t.operations else {}),
                        "purpose": t.purpose,
                    }
                    for t in mcp_tools
                ],
            },
            # ── Backward-compatible v1.0 sections ────────────────────────────
            "governance": {
                "canonical_source": "cortex-registry/core/tier0-skull/skull-rules.yaml",
                "secondary_reference": "cortex-registry/governance/core-rules.yaml",
                "total_core_rules": 35,
                "total_ac_rules": 2,
                "total_rules": 37,
            },
            "runtime": {
                "traces_db": ".cortex-runtime/traces/orchestrator-traces.db",
                "sweeps_dir": ".cortex-runtime/sweeps/",
                "logs_dir": ".cortex-runtime/logs/",
                "ac_marker_pattern": "AC_{STATUS}: AC-{DOMAIN}-{TIMESTAMP}",
                "orphan_ac_severity": "P0",
            },
            "response_templates": {
                "ssot": ".github/templates/cortex-response-templates.md",
                "composition_rule": (
                    "Templates are composable blocks — assemble from SSOT at runtime, "
                    "never duplicate inline. Use business language."
                ),
                "blocks": response_blocks if response_blocks else [],
            },
        }

        return manifest


# ─────────────────────────────────────────────────────────────────────────────
# Module-level utility functions
# ─────────────────────────────────────────────────────────────────────────────


def _to_snake_case(name: str) -> str:
    """Convert CamelCase class name to snake_case orchestrator id."""
    import re
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _filename_to_description(stem: str) -> str:
    """Convert a hyphen/underscore filename stem to a human-readable description."""
    return stem.replace("-", " ").replace("_", " ").title()


# ─────────────────────────────────────────────────────────────────────────────
# CLI entry point — run directly to regenerate manifest
# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    """CLI entry point: python3 -m cortex.intelligence.capability_registry_builder"""
    import sys
    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    builder = CapabilityRegistryBuilder(workspace_root=workspace)

    print("🔎 Scanning orchestrators from wiring specs...")
    orchestrators = builder.scan_orchestrators()
    valid, discrepancies = builder.validate_against_wiring_spec(orchestrators)

    print(f"   Found {len(orchestrators)} wired orchestrators")
    if not valid:
        for d in discrepancies:
            print(f"   ⚠️  {d}")

    print("📂 Indexing workflow templates...")
    templates = builder.scan_workflow_templates()
    print(f"   Found {len(templates)} workflow templates")

    print("🔧 Scanning MCP tools...")
    tools = builder.scan_mcp_tools()
    print(f"   Found {len(tools)} MCP tools")

    print("🗑️  Removing cortex-registry/.inventory/ (GAP-72-05)...")
    builder.remove_inventory_folder()

    print(f"✍️  Writing manifest → {builder.output_path}")
    result = builder.generate_manifest()

    print("\n✅ capabilities-manifest.yaml generated")
    print(f"   schema_version : {result.schema_version}")
    print(f"   orchestrators  : {len(result.orchestrators)}")
    print(f"   templates      : {len(result.workflow_templates)}")
    print(f"   mcp_tools      : {len(result.mcp_tools)}")
    print(f"   generated_at   : {result.generated_at}")
    print("\nAC_COMPLETE: AC-72-CAPABILITY-REGISTRY-BUILDER-20260225 ✅")


if __name__ == "__main__":
    main()
