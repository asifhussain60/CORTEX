"""Dashboard Orchestrator for LENS Dashboard.

Coordinates visualization generation by routing to the appropriate
renderers in cortex/visualization/. This orchestrator integrates
with the existing CORTEX orchestrator infrastructure and can be
invoked via MCP tools.

Integration:
    - Consumes LENS analysis from cortex.brain.analysis.*
    - Uses renderers from cortex.visualization.renderers.*
    - Outputs managed by CacheManager
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import logging

# CORTEX imports
from cortex.visualization.repository_detector import (
    RepositoryDetector,
    is_cortex_repository,
)
from cortex.visualization.dashboard_configuration import (
    DashboardConfiguration,
    DashboardTab,
)
from cortex.visualization.output_manager import (
    DashboardOutputManager,
    get_output_path,
)
from cortex.visualization.business_language_generator import (
    BusinessLanguageGenerator,
    get_business_description,
)
from cortex.visualization.renderers.complexity_renderer import ComplexityRenderer
from cortex.visualization.renderers.author_network_renderer import AuthorNetworkRenderer
from cortex.visualization.renderers.mermaid_renderer import MermaidRenderer
from cortex.visualization.renderers.d3_git_timeline_renderer import D3GitTimelineRenderer
from cortex.visualization.renderers.d3_call_graph_renderer import render_call_graph
from cortex.visualization.renderers.d3_import_graph_renderer import render_import_graph

from cortex_lens.backend.cache_manager import CacheManager, get_cache_manager


logger = logging.getLogger(__name__)


@dataclass
class TabData:
    """Data for a single dashboard tab.
    
    Attributes:
        tab_id: Unique tab identifier
        tab_name: Display name
        data: Tab-specific visualization data
        metadata: Additional metadata (render time, etc.)
    """
    tab_id: str
    tab_name: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "tab_id": self.tab_id,
            "tab_name": self.tab_name,
            "data": self.data,
            "metadata": self.metadata,
        }


@dataclass
class DashboardData:
    """Complete dashboard data for a repository.
    
    Attributes:
        repo_path: Path to the analyzed repository
        repo_name: Name of the repository
        is_cortex: Whether this is CORTEX self-analysis
        tabs: List of tab data
        overview: Repository overview (business language)
        generated_at: ISO timestamp of generation
    """
    repo_path: str
    repo_name: str
    is_cortex: bool
    tabs: List[TabData]
    overview: Dict[str, Any]
    generated_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "repo_path": self.repo_path,
            "repo_name": self.repo_name,
            "is_cortex": self.is_cortex,
            "tabs": [t.to_dict() for t in self.tabs],
            "overview": self.overview,
            "generated_at": self.generated_at,
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class DashboardOrchestrator:
    """Orchestrates LENS Dashboard generation.
    
    This class coordinates the various renderers and analyzers to
    produce a complete dashboard for a repository. It integrates
    with the CORTEX MCP infrastructure.
    
    Example:
        >>> orchestrator = DashboardOrchestrator()
        >>> data = orchestrator.generate_dashboard(Path("/my/repo"))
        >>> orchestrator.save_dashboard(data)
    """
    
    def __init__(
        self,
        cache_manager: Optional[CacheManager] = None,
    ) -> None:
        """Initialize DashboardOrchestrator.
        
        Args:
            cache_manager: Optional CacheManager instance.
                          Uses global instance if not provided.
        """
        self.cache_manager = cache_manager or get_cache_manager()
        self.repo_detector = RepositoryDetector()
        self.dashboard_config = DashboardConfiguration()
        self.output_manager = DashboardOutputManager()
        
        # Renderers
        self.complexity_renderer = ComplexityRenderer()
        self.author_renderer = AuthorNetworkRenderer()
        self.mermaid_renderer = MermaidRenderer()
        self.timeline_renderer = D3GitTimelineRenderer()
        self.business_generator = BusinessLanguageGenerator()
    
    def generate_dashboard(
        self,
        repo_path: Path,
        force_refresh: bool = False,
    ) -> DashboardData:
        """Generate complete dashboard for a repository.
        
        Args:
            repo_path: Path to the repository to analyze
            force_refresh: If True, ignore cache and regenerate
            
        Returns:
            DashboardData containing all tab data
        """
        from datetime import datetime
        
        repo_path = repo_path.resolve()
        logger.info(f"Generating dashboard for {repo_path}")
        
        # Check cache unless force refresh
        if not force_refresh:
            cached = self.cache_manager.get_cached(repo_path)
            if cached:
                logger.info(f"Using cached dashboard for {repo_path}")
                # Load cached data
                cache_path = Path(cached.output_path) / "dashboard_data.json"
                if cache_path.exists():
                    with open(cache_path) as f:
                        data = json.load(f)
                    return self._dict_to_dashboard_data(data)
        
        # Detect repository type
        is_cortex = self.repo_detector.is_cortex_repository(repo_path)
        logger.info(f"Repository type: {'CORTEX' if is_cortex else 'external'}")
        
        # Get applicable tabs
        tabs = self.dashboard_config.get_tabs_for_repo(repo_path)
        logger.info(f"Generating {len(tabs)} tabs")
        
        # Generate overview (Tab 1)
        overview = self._generate_overview(repo_path)
        
        # Generate tab data
        tab_data_list = []
        for tab in tabs:
            try:
                tab_data = self._generate_tab_data(repo_path, tab, is_cortex)
                tab_data_list.append(tab_data)
            except Exception as e:
                logger.warning(f"Failed to generate tab {tab.id}: {e}")
                # Add placeholder for failed tab
                tab_data_list.append(TabData(
                    tab_id=tab.id,
                    tab_name=tab.name,
                    data={"error": str(e)},
                    metadata={"status": "error"},
                ))
        
        # Build dashboard data
        dashboard = DashboardData(
            repo_path=str(repo_path),
            repo_name=repo_path.name,
            is_cortex=is_cortex,
            tabs=tab_data_list,
            overview=overview,
            generated_at=datetime.now().isoformat(),
        )
        
        return dashboard
    
    def _generate_overview(self, repo_path: Path) -> Dict[str, Any]:
        """Generate repository overview (business language).
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            Dictionary containing overview data
        """
        try:
            description = self.business_generator.generate_description(repo_path)
            return {
                "summary": description.summary,
                "capabilities": [c.to_dict() for c in description.capabilities],
                "tech_stack": description.tech_stack.to_dict() if description.tech_stack else {},
                "architecture": description.architecture.to_dict() if description.architecture else {},
                "confidence": description.confidence,
            }
        except Exception as e:
            logger.warning(f"Failed to generate overview: {e}")
            return {
                "summary": f"Repository at {repo_path.name}",
                "capabilities": [],
                "tech_stack": {},
                "architecture": {},
                "confidence": 0.0,
                "error": str(e),
            }
    
    def _generate_tab_data(
        self,
        repo_path: Path,
        tab: DashboardTab,
        is_cortex: bool,
    ) -> TabData:
        """Generate data for a specific tab.
        
        Args:
            repo_path: Path to the repository
            tab: Tab configuration
            is_cortex: Whether this is CORTEX repository
            
        Returns:
            TabData for the tab
        """
        from datetime import datetime
        import time
        
        start_time = time.time()
        data: Dict[str, Any] = {}
        
        if tab.id == "overview":
            # Overview is handled separately
            data = {"message": "See overview field in dashboard data"}
            
        elif tab.id == "dependencies":
            # Dependency graph (call graph + import graph)
            data = self._generate_dependency_data(repo_path)
            
        elif tab.id == "classes":
            # Class diagrams (Mermaid)
            data = self._generate_class_data(repo_path)
            
        elif tab.id == "temporal":
            # Temporal analysis (Git timeline)
            data = self._generate_temporal_data(repo_path)
            
        elif tab.id == "impact":
            # Impact analysis
            data = self._generate_impact_data(repo_path)
            
        elif tab.id == "brain" and is_cortex:
            # Brain architecture (CORTEX-specific)
            data = self._generate_brain_data(repo_path)
            
        elif tab.id == "governance" and is_cortex:
            # Governance heatmap (CORTEX-specific)
            data = self._generate_governance_data(repo_path)
            
        elif tab.id == "orchestrators" and is_cortex:
            # Orchestrator constellation (CORTEX-specific)
            data = self._generate_orchestrator_data(repo_path)
        
        render_time = time.time() - start_time
        
        return TabData(
            tab_id=tab.id,
            tab_name=tab.name,
            data=data,
            metadata={
                "render_time_ms": int(render_time * 1000),
                "generated_at": datetime.now().isoformat(),
            },
        )
    
    def _generate_dependency_data(self, repo_path: Path) -> Dict[str, Any]:
        """Generate dependency graph data."""
        try:
            # Use existing renderers
            call_graph = render_call_graph(repo_path)
            import_graph = render_import_graph(repo_path)
            
            return {
                "call_graph": call_graph,
                "import_graph": import_graph,
            }
        except Exception as e:
            logger.warning(f"Dependency data generation failed: {e}")
            return {"error": str(e), "call_graph": {}, "import_graph": {}}
    
    def _generate_class_data(self, repo_path: Path) -> Dict[str, Any]:
        """Generate class diagram data (Mermaid)."""
        try:
            # Get Python files
            py_files = list(repo_path.rglob("*.py"))[:50]  # Limit for performance
            
            diagrams = []
            for py_file in py_files:
                try:
                    # Parse and generate diagram
                    diagram = self.mermaid_renderer.generate_class_diagram({
                        "classes": self._extract_classes(py_file),
                    })
                    if diagram.content:
                        diagrams.append({
                            "file": str(py_file.relative_to(repo_path)),
                            "diagram": diagram.content,
                            "metadata": diagram.metadata,
                        })
                except Exception:
                    pass
            
            return {"diagrams": diagrams}
        except Exception as e:
            logger.warning(f"Class data generation failed: {e}")
            return {"error": str(e), "diagrams": []}
    
    def _extract_classes(self, py_file: Path) -> List[Dict[str, Any]]:
        """Extract class definitions from a Python file."""
        import ast
        
        try:
            with open(py_file) as f:
                tree = ast.parse(f.read())
        except Exception:
            return []
        
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                attributes = []
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append({
                            "name": item.name,
                            "params": [arg.arg for arg in item.args.args],
                        })
                    elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        attributes.append(item.target.id)
                
                classes.append({
                    "name": node.name,
                    "bases": [
                        base.id if isinstance(base, ast.Name) else str(base)
                        for base in node.bases
                    ],
                    "methods": methods,
                    "attributes": attributes,
                })
        
        return classes
    
    def _generate_temporal_data(self, repo_path: Path) -> Dict[str, Any]:
        """Generate temporal analysis data (Git timeline)."""
        try:
            timeline = self.timeline_renderer.render_from_repo(repo_path)
            
            # Also get author network
            author_network = self.author_renderer.render_author_network({
                "commits": timeline.get("commits", []),
            })
            
            return {
                "timeline": timeline,
                "author_network": self.author_renderer.format_for_d3(author_network),
            }
        except Exception as e:
            logger.warning(f"Temporal data generation failed: {e}")
            return {"error": str(e), "timeline": {}, "author_network": {}}
    
    def _generate_impact_data(self, repo_path: Path) -> Dict[str, Any]:
        """Generate impact analysis data."""
        # Placeholder - requires specific file selection
        return {
            "message": "Select a file to analyze impact",
            "files": [str(f.relative_to(repo_path)) for f in repo_path.rglob("*.py")][:20],
        }
    
    def _generate_brain_data(self, repo_path: Path) -> Dict[str, Any]:
        """Generate CORTEX brain architecture data."""
        brain_path = repo_path / "cortex_brain"
        
        if not brain_path.exists():
            return {"error": "cortex_brain/ not found"}
        
        tiers = []
        for tier_num in range(4):
            tier_path = brain_path / f"tier{tier_num}"
            if tier_path.exists():
                files = list(tier_path.rglob("*.yaml")) + list(tier_path.rglob("*.py"))
                tiers.append({
                    "tier": tier_num,
                    "name": f"Tier {tier_num}",
                    "files": len(files),
                    "path": str(tier_path.relative_to(repo_path)),
                })
        
        return {
            "tiers": tiers,
            "total_files": sum(t["files"] for t in tiers),
        }
    
    def _generate_governance_data(self, repo_path: Path) -> Dict[str, Any]:
        """Generate governance compliance heatmap data."""
        governance_path = repo_path / "cortex_brain" / "tier0" / "governance"
        
        if not governance_path.exists():
            return {"error": "governance/ not found"}
        
        rules = []
        for rule_file in governance_path.glob("CORE-*.yaml"):
            rules.append({
                "id": rule_file.stem,
                "path": str(rule_file.relative_to(repo_path)),
                "status": "active",
            })
        
        return {
            "rules": rules,
            "total_rules": len(rules),
            "compliance_score": 100.0,  # Placeholder
        }
    
    def _generate_orchestrator_data(self, repo_path: Path) -> Dict[str, Any]:
        """Generate orchestrator constellation data."""
        orchestrators_path = repo_path / "cortex" / "orchestrators"
        
        if not orchestrators_path.exists():
            return {"error": "orchestrators/ not found"}
        
        categories = {
            "core": [],
            "domain": [],
            "support": [],
        }
        
        for category in categories:
            category_path = orchestrators_path / category
            if category_path.exists():
                for py_file in category_path.glob("*.py"):
                    if py_file.name != "__init__.py":
                        categories[category].append({
                            "name": py_file.stem,
                            "path": str(py_file.relative_to(repo_path)),
                        })
        
        total = sum(len(v) for v in categories.values())
        
        return {
            "categories": categories,
            "total_orchestrators": total,
            "wiring_status": "active",
        }
    
    def save_dashboard(
        self,
        dashboard: DashboardData,
        output_path: Optional[Path] = None,
    ) -> Path:
        """Save dashboard data to output location.
        
        Args:
            dashboard: Dashboard data to save
            output_path: Optional override for output path
            
        Returns:
            Path where dashboard was saved
        """
        repo_path = Path(dashboard.repo_path)
        
        if output_path is None:
            output_path = self.output_manager.get_output_path(
                repo_path,
                is_cortex=dashboard.is_cortex,
            )
        
        # Ensure output directory exists
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save dashboard data as JSON
        data_file = output_path / "dashboard_data.json"
        with open(data_file, "w") as f:
            f.write(dashboard.to_json())
        
        # Register in cache
        self.cache_manager.register_cache(
            repo_path,
            output_path,
            is_cortex=dashboard.is_cortex,
        )
        
        # Ensure gitignore for local repos
        self.cache_manager.ensure_gitignore(output_path)
        
        logger.info(f"Dashboard saved to {output_path}")
        return output_path
    
    def _dict_to_dashboard_data(self, data: Dict[str, Any]) -> DashboardData:
        """Convert dictionary to DashboardData."""
        return DashboardData(
            repo_path=data["repo_path"],
            repo_name=data["repo_name"],
            is_cortex=data["is_cortex"],
            tabs=[
                TabData(
                    tab_id=t["tab_id"],
                    tab_name=t["tab_name"],
                    data=t["data"],
                    metadata=t.get("metadata", {}),
                )
                for t in data["tabs"]
            ],
            overview=data["overview"],
            generated_at=data["generated_at"],
        )


def get_dashboard_orchestrator() -> DashboardOrchestrator:
    """Get a singleton DashboardOrchestrator instance.
    
    Returns:
        Global DashboardOrchestrator instance
    """
    global _dashboard_orchestrator
    if "_dashboard_orchestrator" not in globals():
        _dashboard_orchestrator = DashboardOrchestrator()
    return _dashboard_orchestrator
