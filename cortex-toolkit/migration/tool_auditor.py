"""
Tool Auditor - Phase 8: Migration & Cleanup

Analyzes existing tools for overlap, duplication, and issues.
Part of the Toolkit Manager implementation.

Author: Asif Hussain
Version: 1.0.0
"""
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import yaml

logger = logging.getLogger(__name__)


@dataclass
class ToolInfo:
    """Information about a single tool."""
    name: str
    category: str
    script: str
    description: str
    command: Optional[str] = None
    wrapper: Optional[str] = None
    platforms: List[str] = field(default_factory=list)
    requires_admin: bool = False
    execution_method: str = "cli"
    
    # Derived fields
    capabilities: List[str] = field(default_factory=list)
    has_tests: bool = False
    has_docs: bool = False
    script_exists: bool = False


@dataclass
class OverlapGroup:
    """Group of tools with overlapping functionality."""
    group_id: str
    domain: str
    tools: List[str]
    overlap_score: float  # 0.0 - 1.0
    recommendation: str  # "consolidate", "keep_separate", "deprecate_some"
    rationale: str


@dataclass
class AuditReport:
    """Comprehensive audit report for toolkit."""
    timestamp: datetime
    toolkit_root: Path
    total_tools: int
    tools_by_category: Dict[str, int]
    overlap_groups: List[OverlapGroup]
    orphaned_tools: List[str]  # Tools with missing scripts
    missing_tests: List[str]  # Tools without test coverage
    undocumented: List[str]  # Tools without docs
    deprecated_candidates: List[str]  # Tools recommended for deprecation
    consolidation_candidates: List[Tuple[List[str], str]]  # (tools, target_name)
    
    def to_dict(self) -> dict:
        """Convert report to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "toolkit_root": str(self.toolkit_root),
            "summary": {
                "total_tools": self.total_tools,
                "tools_by_category": self.tools_by_category,
                "orphaned_count": len(self.orphaned_tools),
                "untested_count": len(self.missing_tests),
                "undocumented_count": len(self.undocumented),
            },
            "overlap_groups": [
                {
                    "group_id": g.group_id,
                    "domain": g.domain,
                    "tools": g.tools,
                    "overlap_score": g.overlap_score,
                    "recommendation": g.recommendation,
                    "rationale": g.rationale,
                }
                for g in self.overlap_groups
            ],
            "issues": {
                "orphaned_tools": self.orphaned_tools,
                "missing_tests": self.missing_tests,
                "undocumented": self.undocumented,
            },
            "recommendations": {
                "deprecated_candidates": self.deprecated_candidates,
                "consolidation_candidates": [
                    {"tools": tools, "target": target}
                    for tools, target in self.consolidation_candidates
                ],
            },
        }


class ToolAuditor:
    """
    Analyzes existing tools for overlap and issues.
    
    Performs:
    - Tool inventory scanning
    - Overlap detection using capability keywords
    - Orphan detection (missing scripts/wrappers)
    - Test coverage analysis
    - Documentation coverage analysis
    """
    
    # Capability keywords for semantic matching
    CAPABILITY_KEYWORDS = {
        "cleanup": ["clean", "cleanup", "clear", "remove", "delete", "purge", "temp"],
        "validation": ["validate", "verify", "check", "test", "lint", "audit"],
        "documentation": ["doc", "docs", "generate", "markdown", "html", "reference"],
        "migration": ["migrate", "upgrade", "convert", "transform", "schema"],
        "analysis": ["analyze", "profile", "metrics", "visualize", "report"],
        "generation": ["generate", "create", "scaffold", "template", "spec"],
        "maintenance": ["maintain", "fix", "repair", "health", "optimize"],
        "deployment": ["deploy", "publish", "release", "install"],
    }
    
    def __init__(self, toolkit_root: Optional[Path] = None):
        """Initialize auditor with toolkit root path."""
        if toolkit_root is None:
            toolkit_root = Path(__file__).parent.parent
        self.toolkit_root = toolkit_root
        self.manifest_path = toolkit_root / "toolkit-manifest.yaml"
        self._tools: Dict[str, ToolInfo] = {}
        self._load_manifest()
    
    def _load_manifest(self) -> None:
        """Load and parse toolkit manifest."""
        if not self.manifest_path.exists():
            logger.warning(f"Manifest not found: {self.manifest_path}")
            return
        
        with open(self.manifest_path, "r") as f:
            manifest = yaml.safe_load(f)
        
        categories = manifest.get("categories", {})
        for category_name, category_data in categories.items():
            tools = category_data.get("tools", [])
            for tool in tools:
                info = ToolInfo(
                    name=tool.get("name", "unknown"),
                    category=category_name,
                    script=tool.get("script", ""),
                    description=tool.get("description", ""),
                    command=tool.get("command"),
                    wrapper=tool.get("wrapper"),
                    platforms=tool.get("platforms", []),
                    requires_admin=tool.get("requires_admin", False),
                    execution_method=tool.get("execution_method", "cli"),
                )
                # Extract capabilities from description
                info.capabilities = self._extract_capabilities(info.description)
                # Check if script exists
                script_path = self.toolkit_root / info.script
                info.script_exists = script_path.exists()
                
                self._tools[info.name] = info
        
        logger.info(f"Loaded {len(self._tools)} tools from manifest")
    
    def _extract_capabilities(self, description: str) -> List[str]:
        """Extract capability keywords from description."""
        description_lower = description.lower()
        capabilities = []
        
        for capability, keywords in self.CAPABILITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in description_lower:
                    capabilities.append(capability)
                    break
        
        return capabilities
    
    def audit_all_tools(self) -> AuditReport:
        """Generate comprehensive audit report."""
        logger.info("Starting comprehensive tool audit")
        
        # Gather all data
        overlap_groups = self.find_overlaps()
        orphaned = self.find_orphaned()
        untested = self.find_untested()
        undocumented = self.find_undocumented()
        
        # Analyze for recommendations
        deprecated_candidates = self._identify_deprecated_candidates()
        consolidation_candidates = self._identify_consolidation_candidates(overlap_groups)
        
        # Build category counts
        tools_by_category: Dict[str, int] = {}
        for tool in self._tools.values():
            tools_by_category[tool.category] = tools_by_category.get(tool.category, 0) + 1
        
        report = AuditReport(
            timestamp=datetime.now(),
            toolkit_root=self.toolkit_root,
            total_tools=len(self._tools),
            tools_by_category=tools_by_category,
            overlap_groups=overlap_groups,
            orphaned_tools=orphaned,
            missing_tests=untested,
            undocumented=undocumented,
            deprecated_candidates=deprecated_candidates,
            consolidation_candidates=consolidation_candidates,
        )
        
        logger.info(f"Audit complete: {report.total_tools} tools, {len(overlap_groups)} overlap groups")
        return report
    
    def find_overlaps(self) -> List[OverlapGroup]:
        """Find tools with similar capabilities."""
        groups: List[OverlapGroup] = []
        processed: Set[str] = set()
        
        # Group by primary capability
        capability_map: Dict[str, List[str]] = {}
        for name, tool in self._tools.items():
            for cap in tool.capabilities:
                if cap not in capability_map:
                    capability_map[cap] = []
                capability_map[cap].append(name)
        
        # Create overlap groups for capabilities with multiple tools
        group_id = 0
        for capability, tools in capability_map.items():
            if len(tools) > 1:
                # Check if these tools have significant overlap
                overlap_score = self._calculate_overlap_score(tools)
                if overlap_score > 0.5:  # Significant overlap threshold
                    group_id += 1
                    # Determine recommendation
                    recommendation, rationale = self._determine_recommendation(tools, capability)
                    
                    groups.append(OverlapGroup(
                        group_id=f"overlap-{group_id:03d}",
                        domain=capability,
                        tools=tools,
                        overlap_score=overlap_score,
                        recommendation=recommendation,
                        rationale=rationale,
                    ))
        
        return groups
    
    def _calculate_overlap_score(self, tools: List[str]) -> float:
        """Calculate overlap score between tools (0.0-1.0)."""
        if len(tools) < 2:
            return 0.0
        
        # Get all capabilities for each tool
        all_caps: List[Set[str]] = []
        for name in tools:
            tool = self._tools.get(name)
            if tool:
                all_caps.append(set(tool.capabilities))
        
        if not all_caps:
            return 0.0
        
        # Calculate Jaccard similarity between all pairs
        total_similarity = 0.0
        pair_count = 0
        
        for i in range(len(all_caps)):
            for j in range(i + 1, len(all_caps)):
                intersection = len(all_caps[i] & all_caps[j])
                union = len(all_caps[i] | all_caps[j])
                if union > 0:
                    total_similarity += intersection / union
                pair_count += 1
        
        return total_similarity / pair_count if pair_count > 0 else 0.0
    
    def _determine_recommendation(
        self, tools: List[str], domain: str
    ) -> Tuple[str, str]:
        """Determine recommendation for overlap group."""
        tool_infos = [self._tools[t] for t in tools if t in self._tools]
        
        # Check if tools are in same category
        categories = set(t.category for t in tool_infos)
        
        if len(categories) == 1:
            # Same category - likely consolidation candidates
            return (
                "consolidate",
                f"Tools in same category ({list(categories)[0]}) with overlapping {domain} functionality"
            )
        elif "maintenance" in domain or "cleanup" in domain:
            return (
                "consolidate",
                f"Multiple {domain} tools should be unified into single tool with modes"
            )
        else:
            return (
                "keep_separate",
                f"Tools serve different domains despite {domain} overlap"
            )
    
    def find_orphaned(self) -> List[str]:
        """Find tools with missing script files."""
        orphaned = []
        for name, tool in self._tools.items():
            if not tool.script_exists:
                orphaned.append(name)
        return orphaned
    
    def find_untested(self) -> List[str]:
        """Find tools without test coverage."""
        untested = []
        tests_dir = self.toolkit_root.parent / "tests" / "toolkit"
        
        for name, tool in self._tools.items():
            # Look for test file matching tool name
            test_patterns = [
                f"test_{name}.py",
                f"test_{name.replace('-', '_')}.py",
            ]
            
            found_test = False
            if tests_dir.exists():
                for pattern in test_patterns:
                    if (tests_dir / pattern).exists():
                        found_test = True
                        break
            
            tool.has_tests = found_test
            if not found_test:
                untested.append(name)
        
        return untested
    
    def find_undocumented(self) -> List[str]:
        """Find tools without documentation."""
        undocumented = []
        docs_dir = self.toolkit_root / "docs"
        
        for name, tool in self._tools.items():
            # Look for doc file matching tool name
            doc_patterns = [
                f"{name}.md",
                f"{name.replace('-', '_')}.md",
            ]
            
            found_doc = False
            if docs_dir.exists():
                for pattern in doc_patterns:
                    if (docs_dir / pattern).exists():
                        found_doc = True
                        break
            
            tool.has_docs = found_doc
            if not found_doc:
                undocumented.append(name)
        
        return undocumented
    
    def _identify_deprecated_candidates(self) -> List[str]:
        """Identify tools that should be deprecated."""
        candidates = []
        
        # One-time migration tools
        migration_keywords = ["rename", "migrate", "upgrade", "convert"]
        for name, tool in self._tools.items():
            name_lower = name.lower()
            desc_lower = tool.description.lower()
            
            # Check for one-time migration tools
            if any(kw in name_lower for kw in migration_keywords):
                if "version" in name_lower or "planning-system" in name_lower:
                    candidates.append(name)
            
            # Check for legacy tools
            if "legacy" in name_lower or "legacy" in desc_lower:
                candidates.append(name)
        
        return list(set(candidates))
    
    def _identify_consolidation_candidates(
        self, overlap_groups: List[OverlapGroup]
    ) -> List[Tuple[List[str], str]]:
        """Identify tools that should be consolidated."""
        candidates = []
        
        for group in overlap_groups:
            if group.recommendation == "consolidate":
                # Determine target name
                target_name = self._suggest_consolidated_name(group.tools, group.domain)
                candidates.append((group.tools, target_name))
        
        return candidates
    
    def _suggest_consolidated_name(self, tools: List[str], domain: str) -> str:
        """Suggest name for consolidated tool."""
        # Use domain as base
        base_name = domain.replace("_", "-")
        
        # If there's already a tool with short name, use that
        for tool in tools:
            if len(tool) < 15 and domain in tool.lower():
                return tool
        
        return f"cortex-{base_name}"
    
    def get_tool(self, name: str) -> Optional[ToolInfo]:
        """Get tool info by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> List[ToolInfo]:
        """List all tools."""
        return list(self._tools.values())
    
    def list_by_category(self, category: str) -> List[ToolInfo]:
        """List tools by category."""
        return [t for t in self._tools.values() if t.category == category]
    
    def generate_report_markdown(self, report: AuditReport) -> str:
        """Generate markdown report from audit data."""
        lines = [
            "# Toolkit Audit Report",
            "",
            f"**Generated:** {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Toolkit Root:** `{report.toolkit_root}`",
            "",
            "## Summary",
            "",
            f"- **Total Tools:** {report.total_tools}",
            f"- **Orphaned Tools:** {len(report.orphaned_tools)}",
            f"- **Untested Tools:** {len(report.missing_tests)}",
            f"- **Undocumented Tools:** {len(report.undocumented)}",
            "",
            "### Tools by Category",
            "",
            "| Category | Count |",
            "|----------|-------|",
        ]
        
        for category, count in sorted(report.tools_by_category.items()):
            lines.append(f"| {category} | {count} |")
        
        lines.extend([
            "",
            "## Overlap Groups",
            "",
        ])
        
        if report.overlap_groups:
            for group in report.overlap_groups:
                lines.extend([
                    f"### {group.group_id}: {group.domain.title()}",
                    "",
                    f"- **Tools:** {', '.join(group.tools)}",
                    f"- **Overlap Score:** {group.overlap_score:.2f}",
                    f"- **Recommendation:** {group.recommendation}",
                    f"- **Rationale:** {group.rationale}",
                    "",
                ])
        else:
            lines.append("No significant overlap groups detected.")
        
        lines.extend([
            "",
            "## Recommendations",
            "",
            "### Consolidation Candidates",
            "",
        ])
        
        if report.consolidation_candidates:
            for tools, target in report.consolidation_candidates:
                lines.append(f"- Merge `{', '.join(tools)}` → `{target}`")
        else:
            lines.append("No consolidation recommended.")
        
        lines.extend([
            "",
            "### Deprecation Candidates",
            "",
        ])
        
        if report.deprecated_candidates:
            for tool in report.deprecated_candidates:
                lines.append(f"- `{tool}`")
        else:
            lines.append("No tools recommended for deprecation.")
        
        lines.extend([
            "",
            "## Issues",
            "",
            "### Orphaned Tools (Missing Scripts)",
            "",
        ])
        
        if report.orphaned_tools:
            for tool in report.orphaned_tools:
                lines.append(f"- `{tool}`")
        else:
            lines.append("No orphaned tools found.")
        
        lines.extend([
            "",
            "### Missing Tests",
            "",
        ])
        
        if report.missing_tests:
            for tool in report.missing_tests[:10]:  # Limit output
                lines.append(f"- `{tool}`")
            if len(report.missing_tests) > 10:
                lines.append(f"- ... and {len(report.missing_tests) - 10} more")
        else:
            lines.append("All tools have tests.")
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Run audit from command line
    logging.basicConfig(level=logging.INFO)
    
    auditor = ToolAuditor()
    report = auditor.audit_all_tools()
    
    # Print markdown report
    print(auditor.generate_report_markdown(report))
