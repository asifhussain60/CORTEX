"""
Brain Architecture Renderer for CORTEX LENS Dashboard.

This module renders visualizations of CORTEX's 4-tier brain architecture,
showing the governance structure, orchestrator registry, and knowledge system.

Author: Asif Hussain
Orchestrator: LENSVisualizationOrchestrator
AC-ID: LENS-009
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import yaml


@dataclass
class TierInfo:
    """Information about a brain tier.
    
    Attributes:
        tier_number: Tier number (0-3)
        name: Tier name (e.g., "Governance", "Acceptance")
        description: Tier description
        file_count: Number of files in tier
        rule_count: Number of rules in tier (Tier 0 only)
        location: File system path to tier
    """
    tier_number: int
    name: str
    description: str
    file_count: int
    rule_count: Optional[int] = None
    location: Optional[Path] = None


@dataclass
class OrchestratorInfo:
    """Information about a registered orchestrator.
    
    Attributes:
        name: Orchestrator name
        category: Category (core, domain, support)
        module: Python module path
        status: Wiring status (wired, pending, disabled)
        dependencies: List of orchestrator dependencies
        description: Brief description
    """
    name: str
    category: str
    module: str
    status: str
    dependencies: List[str]
    description: str


@dataclass
class BrainArchitecture:
    """Complete brain architecture data.
    
    Attributes:
        tiers: List of tier information
        orchestrators: List of orchestrator information
        total_rules: Total CORE rules count
        total_orchestrators: Total orchestrators count
        wiring_status: Overall wiring status percentage
    """
    tiers: List[TierInfo]
    orchestrators: List[OrchestratorInfo]
    total_rules: int
    total_orchestrators: int
    wiring_status: float


class BrainArchitectureRenderer:
    """Renderer for CORTEX brain architecture visualizations.
    
    This renderer analyzes the cortex_brain/ directory structure and
    orchestrator registry to generate comprehensive brain architecture
    visualizations showing the 4-tier system and orchestrator constellation.
    """
    
    def __init__(self) -> None:
        """Initialize brain architecture renderer."""
        self.tier_names = {
            0: "Governance",
            1: "Acceptance Criteria",
            2: "Response Templates",
            3: "Knowledge & Best Practices",
        }
    
    def analyze_brain_structure(
        self,
        cortex_brain_path: Path,
    ) -> BrainArchitecture:
        """Analyze CORTEX brain directory structure.
        
        Args:
            cortex_brain_path: Path to cortex_brain/ directory
        
        Returns:
            BrainArchitecture: Complete brain architecture data
        """
        tiers = self._analyze_tiers(cortex_brain_path)
        orchestrators = self._load_orchestrator_registry(cortex_brain_path.parent)
        
        total_rules = sum(tier.rule_count or 0 for tier in tiers)
        total_orchestrators = len(orchestrators)
        wiring_status = self._calculate_wiring_status(orchestrators)
        
        return BrainArchitecture(
            tiers=tiers,
            orchestrators=orchestrators,
            total_rules=total_rules,
            total_orchestrators=total_orchestrators,
            wiring_status=wiring_status,
        )
    
    def _analyze_tiers(self, cortex_brain_path: Path) -> List[TierInfo]:
        """Analyze tier directories.
        
        Args:
            cortex_brain_path: Path to cortex_brain/ directory
        
        Returns:
            List[TierInfo]: List of tier information
        """
        tiers = []
        
        for tier_num, tier_name in self.tier_names.items():
            tier_path = cortex_brain_path / f"tier{tier_num}"
            
            if not tier_path.exists():
                continue
            
            # Count files
            file_count = len(list(tier_path.rglob("*.yaml")))
            file_count += len(list(tier_path.rglob("*.yml")))
            file_count += len(list(tier_path.rglob("*.md")))
            
            # Count rules for Tier 0
            rule_count = None
            if tier_num == 0:
                rule_count = self._count_governance_rules(tier_path)
            
            tier_info = TierInfo(
                tier_number=tier_num,
                name=tier_name,
                description=self._get_tier_description(tier_num),
                file_count=file_count,
                rule_count=rule_count,
                location=tier_path,
            )
            tiers.append(tier_info)
        
        return tiers
    
    def _count_governance_rules(self, tier0_path: Path) -> int:
        """Count CORE governance rules in Tier 0.
        
        Args:
            tier0_path: Path to tier0/ directory
        
        Returns:
            int: Number of CORE rules found
        """
        governance_path = tier0_path / "governance"
        if not governance_path.exists():
            return 0
        
        rule_count = 0
        
        # Count CORE-XXX rules in YAML files
        for yaml_file in governance_path.rglob("*.yaml"):
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    content = yaml.safe_load(f)
                    
                if isinstance(content, dict) and "rules" in content:
                    rule_count += len(content["rules"])
                elif isinstance(content, list):
                    # List of rules
                    rule_count += len(content)
            except Exception:
                # Skip files that can't be parsed
                continue
        
        return rule_count
    
    def _get_tier_description(self, tier_num: int) -> str:
        """Get tier description.
        
        Args:
            tier_num: Tier number (0-3)
        
        Returns:
            str: Tier description
        """
        descriptions = {
            0: "Immutable governance rules (CORE-001 through CORE-040)",
            1: "Phase acceptance criteria and validation specifications",
            2: "Response templates and hallucination prevention boundaries",
            3: "Knowledge repository with 35+ YAML best practices",
        }
        return descriptions.get(tier_num, "Unknown tier")
    
    def _load_orchestrator_registry(
        self,
        cortex_path: Path,
    ) -> List[OrchestratorInfo]:
        """Load orchestrator registry from wiring.yaml.
        
        Args:
            cortex_path: Path to cortex/ directory
        
        Returns:
            List[OrchestratorInfo]: List of orchestrator information
        """
        wiring_path = cortex_path / "wiring" / "specifications" / "wiring.yaml"
        
        if not wiring_path.exists():
            # Fallback to legacy location
            wiring_path = cortex_path / "cortex-registry" / "manifest.yaml"
        
        if not wiring_path.exists():
            return []
        
        try:
            with open(wiring_path, "r", encoding="utf-8") as f:
                wiring_data = yaml.safe_load(f)
        except Exception:
            return []
        
        orchestrators = []
        
        # Parse wiring data
        if "orchestrators" in wiring_data:
            for orch_data in wiring_data["orchestrators"]:
                orchestrator = OrchestratorInfo(
                    name=orch_data.get("name", "Unknown"),
                    category=orch_data.get("category", "unknown"),
                    module=orch_data.get("module", ""),
                    status=orch_data.get("status", "pending"),
                    dependencies=orch_data.get("dependencies", []),
                    description=orch_data.get("description", ""),
                )
                orchestrators.append(orchestrator)
        
        return orchestrators
    
    def _calculate_wiring_status(
        self,
        orchestrators: List[OrchestratorInfo],
    ) -> float:
        """Calculate overall wiring status percentage.
        
        Args:
            orchestrators: List of orchestrators
        
        Returns:
            float: Wiring status percentage (0.0-100.0)
        """
        if not orchestrators:
            return 0.0
        
        wired_count = sum(1 for o in orchestrators if o.status == "wired")
        return (wired_count / len(orchestrators)) * 100.0
    
    def render_tier_hierarchy(
        self,
        brain_architecture: BrainArchitecture,
    ) -> Dict[str, Any]:
        """Render tier hierarchy visualization data.
        
        Args:
            brain_architecture: Brain architecture data
        
        Returns:
            Dict[str, Any]: Mermaid diagram data for tier hierarchy
        """
        # Generate Mermaid flowchart
        mermaid_lines = [
            "graph TB",
            "    %% CORTEX 4-Tier Brain Architecture",
        ]
        
        for tier in brain_architecture.tiers:
            tier_id = f"tier{tier.tier_number}"
            label = f"{tier.name}<br/>{tier.file_count} files"
            
            if tier.rule_count is not None:
                label += f"<br/>{tier.rule_count} rules"
            
            mermaid_lines.append(f'    {tier_id}["{label}"]')
        
        # Add connections
        for i in range(len(brain_architecture.tiers) - 1):
            tier_id = f"tier{i}"
            next_tier_id = f"tier{i + 1}"
            mermaid_lines.append(f"    {tier_id} --> {next_tier_id}")
        
        # Add styling
        mermaid_lines.extend([
            "    classDef tier0 fill:#ef4444,stroke:#991b1b,color:#fff",
            "    classDef tier1 fill:#f97316,stroke:#9a3412,color:#fff",
            "    classDef tier2 fill:#3b82f6,stroke:#1e40af,color:#fff",
            "    classDef tier3 fill:#10b981,stroke:#065f46,color:#fff",
            "    class tier0 tier0",
            "    class tier1 tier1",
            "    class tier2 tier2",
            "    class tier3 tier3",
        ])
        
        return {
            "type": "mermaid",
            "diagram": "\n".join(mermaid_lines),
        }
    
    def render_orchestrator_constellation(
        self,
        brain_architecture: BrainArchitecture,
    ) -> Dict[str, Any]:
        """Render orchestrator constellation visualization data.
        
        Args:
            brain_architecture: Brain architecture data
        
        Returns:
            Dict[str, Any]: D3.js force-directed graph data
        """
        nodes = []
        links = []
        
        # Create nodes for each orchestrator
        for idx, orch in enumerate(brain_architecture.orchestrators):
            # Assign group based on category
            group_map = {"core": 1, "domain": 2, "support": 3}
            group = group_map.get(orch.category, 0)
            
            # Size based on number of dependencies
            size = 10 + (len(orch.dependencies) * 2)
            
            node = {
                "id": orch.name,
                "name": orch.name,
                "group": group,
                "category": orch.category,
                "status": orch.status,
                "size": size,
            }
            nodes.append(node)
        
        # Create links for dependencies
        for orch in brain_architecture.orchestrators:
            for dep_name in orch.dependencies:
                # Check if dependency exists
                if any(o.name == dep_name for o in brain_architecture.orchestrators):
                    link = {
                        "source": orch.name,
                        "target": dep_name,
                        "value": 1,
                    }
                    links.append(link)
        
        return {
            "nodes": nodes,
            "links": links,
            "metadata": {
                "total_orchestrators": len(nodes),
                "total_connections": len(links),
                "categories": {
                    "core": sum(1 for n in nodes if n["category"] == "core"),
                    "domain": sum(1 for n in nodes if n["category"] == "domain"),
                    "support": sum(1 for n in nodes if n["category"] == "support"),
                },
            },
        }
    
    def render_knowledge_graph(
        self,
        brain_architecture: BrainArchitecture,
        knowledge_path: Path,
    ) -> Dict[str, Any]:
        """Render knowledge graph from Tier 3.
        
        Args:
            brain_architecture: Brain architecture data
            knowledge_path: Path to tier3/knowledge/ directory
        
        Returns:
            Dict[str, Any]: Knowledge graph visualization data
        """
        nodes = []
        links = []
        
        if not knowledge_path.exists():
            return {"nodes": nodes, "links": links}
        
        # Parse knowledge YAML files
        knowledge_files = list(knowledge_path.glob("*.yaml"))
        
        for idx, yaml_file in enumerate(knowledge_files):
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    content = yaml.safe_load(f)
                
                if not isinstance(content, dict):
                    continue
                
                # Create node for knowledge file
                node = {
                    "id": yaml_file.stem,
                    "name": yaml_file.stem.replace("_", " ").title(),
                    "group": 1,
                    "size": 8,
                }
                nodes.append(node)
                
                # Extract related topics
                if "related" in content:
                    for related in content["related"]:
                        # Create link to related knowledge
                        link = {
                            "source": yaml_file.stem,
                            "target": related,
                            "value": 1,
                        }
                        links.append(link)
            
            except Exception:
                # Skip files that can't be parsed
                continue
        
        return {
            "nodes": nodes,
            "links": links,
            "metadata": {
                "total_knowledge_files": len(nodes),
                "total_relationships": len(links),
            },
        }
    
    def generate_brain_summary(
        self,
        brain_architecture: BrainArchitecture,
    ) -> Dict[str, Any]:
        """Generate brain architecture summary statistics.
        
        Args:
            brain_architecture: Brain architecture data
        
        Returns:
            Dict[str, Any]: Summary statistics
        """
        return {
            "total_tiers": len(brain_architecture.tiers),
            "total_rules": brain_architecture.total_rules,
            "total_orchestrators": brain_architecture.total_orchestrators,
            "wiring_status": f"{brain_architecture.wiring_status:.1f}%",
            "tier_breakdown": [
                {
                    "tier": tier.tier_number,
                    "name": tier.name,
                    "files": tier.file_count,
                    "rules": tier.rule_count,
                }
                for tier in brain_architecture.tiers
            ],
            "orchestrator_breakdown": {
                "core": sum(1 for o in brain_architecture.orchestrators if o.category == "core"),
                "domain": sum(1 for o in brain_architecture.orchestrators if o.category == "domain"),
                "support": sum(1 for o in brain_architecture.orchestrators if o.category == "support"),
            },
            "wiring_breakdown": {
                "wired": sum(1 for o in brain_architecture.orchestrators if o.status == "wired"),
                "pending": sum(1 for o in brain_architecture.orchestrators if o.status == "pending"),
                "disabled": sum(1 for o in brain_architecture.orchestrators if o.status == "disabled"),
            },
        }
