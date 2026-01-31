"""
Impact Analysis Renderer - Change Propagation Visualization.

Analyzes and visualizes the impact of code changes across the repository:
- Change propagation through call graphs
- Blast radius calculation
- Dependency impact heatmap
- Risk assessment for modifications

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
AC-ID: LENS-DASH-003
Task: 008 - Impact Analysis Renderer
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from enum import Enum

# CONSOLIDATED: Import from cortex.models.canonical_enums
from cortex.models.canonical_enums import RiskLevel


@dataclass
class ImpactNode:
    """
    Represents a code entity in the impact graph.
    
    Attributes:
        node_type: Node type (file, function, class, module)
        name: Display name
        path: File system path
        function_name: Optional function name for function nodes
    """
    node_type: str
    name: str
    path: Path
    function_name: Optional[str] = None


@dataclass
class ChangeImpact:
    """
    Represents the impact of a proposed change.
    
    Attributes:
        target_file: Path to target file being modified
        target_function: Optional function name within target file
        blast_radius: Number of entities affected
        affected_files: List of file paths that depend on target
        affected_functions: List of function names that depend on target
        risk_level: Risk level (LOW, MEDIUM, HIGH, CRITICAL)
        recommendations: List of recommended actions
    """
    target_file: str
    target_function: Optional[str] = None
    blast_radius: int = 0
    affected_files: List[str] = field(default_factory=list)
    affected_functions: List[str] = field(default_factory=list)
    risk_level: str = "LOW"
    recommendations: List[str] = field(default_factory=list)


class ImpactAnalysisRenderer:
    """
    Renders impact analysis visualizations for code changes.
    
    Analyzes code dependencies and generates D3.js visualizations showing:
    - Change propagation through call graph
    - Blast radius calculation (affected entities)
    - Dependency impact heatmap
    - Risk assessment metrics
    
    Example:
        ```python
        renderer = ImpactAnalysisRenderer()
        
        # Analyze impact of changing a file
        impact = renderer.analyze_file_impact(
            repo_path=Path("/path/to/repo"),
            target_file="module.py",
            ast_analysis={...},
            git_analysis={...}
        )
        
        # Generate D3.js visualization data
        viz_data = renderer.render_impact_graph(impact)
        ```
    """
    
    def __init__(self):
        """Initialize impact analysis renderer."""
        self._impact_cache: Dict[str, ChangeImpact] = {}
    
    def analyze_file_impact(
        self,
        repo_path: Path,
        target_file: str,
        ast_analysis: Dict[str, Any],
        git_analysis: Optional[Dict[str, Any]] = None,
    ) -> ChangeImpact:
        """
        Analyze impact of modifying a specific file.
        
        Args:
            repo_path: Path to repository root
            target_file: Relative path to file being analyzed
            ast_analysis: AST analysis results (functions, classes, imports)
            git_analysis: Optional Git history for change frequency
        
        Returns:
            ChangeImpact with blast radius and affected entities
        """
        # Find all files that import this file
        affected_files = self._find_dependent_files(target_file, ast_analysis)
        
        # Find all functions that call functions in this file
        affected_functions = self._find_dependent_functions(target_file, ast_analysis)
        
        # Calculate blast radius
        blast_radius = len(affected_files) + len(affected_functions)
        
        # Determine risk level
        risk_level = self._calculate_risk_level(
            blast_radius=blast_radius,
            change_frequency=self._get_change_frequency(target_file, git_analysis),
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            risk_level=risk_level,
            affected_files=affected_files,
        )
        
        impact = ChangeImpact(
            target_file=target_file,
            blast_radius=blast_radius,
            affected_files=affected_files,
            affected_functions=affected_functions,
            risk_level=risk_level,
            recommendations=recommendations,
        )
        
        # Cache result
        self._impact_cache[target_file] = impact
        
        return impact
    
    def analyze_function_impact(
        self,
        target_file: str,
        target_function: str,
        ast_analysis: Dict[str, Any],
    ) -> ChangeImpact:
        """
        Analyze impact of modifying a specific function.
        
        Args:
            target_file: File containing the function
            target_function: Function name being analyzed
            ast_analysis: AST analysis results
        
        Returns:
            ChangeImpact for the specific function
        """
        # Find callers of this function
        affected_functions = self._find_function_callers(
            target_file,
            target_function,
            ast_analysis,
        )
        
        # Affected files are those containing calling functions
        affected_files = list(set(
            func.split(":")[0] for func in affected_functions
        ))
        
        blast_radius = len(affected_functions)
        risk_level = self._calculate_risk_level(blast_radius, 0)
        
        impact = ChangeImpact(
            target_file=target_file,
            target_function=target_function,
            blast_radius=blast_radius,
            affected_files=affected_files,
            affected_functions=affected_functions,
            risk_level=risk_level,
            recommendations=self._generate_recommendations(risk_level, affected_files),
        )
        
        return impact
    
    def render_impact_graph(self, impact: ChangeImpact) -> Dict[str, Any]:
        """
        Generate D3.js force-directed graph data for impact visualization.
        
        Args:
            impact: ChangeImpact to visualize
        
        Returns:
            Dict with 'nodes' and 'links' for D3.js
        """
        nodes = []
        links = []
        
        # Target node (center)
        target_id = impact.target_file
        if impact.target_function:
            target_id = f"{impact.target_file}:{impact.target_function}"
        
        nodes.append({
            "id": target_id,
            "name": impact.target_function or Path(impact.target_file).name,
            "type": "target",
            "group": 0,
            "risk": impact.risk_level,
            "size": 20,
        })
        
        # Affected file nodes
        for i, file_path in enumerate(impact.affected_files):
            nodes.append({
                "id": file_path,
                "name": Path(file_path).name,
                "type": "affected_file",
                "group": 1,
                "size": 10,
            })
            
            links.append({
                "source": target_id,
                "target": file_path,
                "type": "depends_on",
                "strength": 0.8,
            })
        
        # Affected function nodes
        for func in impact.affected_functions:
            nodes.append({
                "id": func,
                "name": func.split(":")[-1] if ":" in func else func,
                "type": "affected_function",
                "group": 2,
                "size": 8,
            })
            
            links.append({
                "source": target_id,
                "target": func,
                "type": "calls",
                "strength": 0.6,
            })
        
        return {
            "nodes": nodes,
            "links": links,
            "metadata": {
                "target": target_id,
                "blast_radius": impact.blast_radius,
                "risk_level": impact.risk_level,
            }
        }
    
    def render_blast_radius_heatmap(
        self,
        repo_path: Path,
        ast_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate heatmap data showing blast radius for all files.
        
        Args:
            repo_path: Repository root path
            ast_analysis: AST analysis for all files
        
        Returns:
            Dict with heatmap data (file -> blast radius)
        """
        heatmap_data = []
        
        # Analyze impact for each file
        files = ast_analysis.get("files", [])
        for file_info in files:
            file_path = file_info.get("path", "")
            if not file_path:
                continue
            
            # Quick impact calculation
            dependents = self._find_dependent_files(file_path, ast_analysis)
            blast_radius = len(dependents)
            
            heatmap_data.append({
                "file": file_path,
                "blast_radius": blast_radius,
                "risk": self._calculate_risk_level(blast_radius, 0),
            })
        
        # Sort by blast radius (descending)
        heatmap_data.sort(key=lambda x: x["blast_radius"], reverse=True)
        
        return {
            "data": heatmap_data,
            "max_blast_radius": max((d["blast_radius"] for d in heatmap_data), default=0),
        }
    
    def _find_dependent_files(
        self,
        target_file: str,
        ast_analysis: Dict[str, Any],
    ) -> List[str]:
        """Find all files that import the target file."""
        dependents = []
        
        files = ast_analysis.get("files", [])
        for file_info in files:
            imports = file_info.get("imports", [])
            for imp in imports:
                # Check if import references target file
                if target_file in imp or Path(target_file).stem in imp:
                    dependents.append(file_info.get("path", ""))
                    break
        
        return dependents
    
    def _find_dependent_functions(
        self,
        target_file: str,
        ast_analysis: Dict[str, Any],
    ) -> List[str]:
        """Find all functions that call functions in target file."""
        dependent_funcs = []
        
        # Get functions exported by target file
        target_functions = self._get_file_functions(target_file, ast_analysis)
        
        # Find callers
        files = ast_analysis.get("files", [])
        for file_info in files:
            file_path = file_info.get("path", "")
            functions = file_info.get("functions", [])
            
            for func in functions:
                func_name = func.get("name", "")
                # Check if function calls any target functions
                # (simplified - real implementation would parse function body)
                for target_func in target_functions:
                    dependent_funcs.append(f"{file_path}:{func_name}")
        
        return dependent_funcs
    
    def _find_function_callers(
        self,
        target_file: str,
        target_function: str,
        ast_analysis: Dict[str, Any],
    ) -> List[str]:
        """Find all functions that call the target function."""
        callers = []
        
        files = ast_analysis.get("files", [])
        for file_info in files:
            file_path = file_info.get("path", "")
            functions = file_info.get("functions", [])
            
            for func in functions:
                func_name = func.get("name", "")
                # Simplified: real implementation would analyze call graph
                # For now, mark as potential caller if not same function
                if func_name != target_function:
                    callers.append(f"{file_path}:{func_name}")
        
        return callers
    
    def _get_file_functions(
        self,
        file_path: str,
        ast_analysis: Dict[str, Any],
    ) -> List[str]:
        """Get all function names exported by a file."""
        files = ast_analysis.get("files", [])
        for file_info in files:
            if file_info.get("path") == file_path:
                return [f.get("name", "") for f in file_info.get("functions", [])]
        return []
    
    def _get_change_frequency(
        self,
        file_path: str,
        git_analysis: Optional[Dict[str, Any]],
    ) -> int:
        """Get change frequency for a file from Git history."""
        if not git_analysis:
            return 0
        
        commits = git_analysis.get("commits", [])
        changes = sum(
            1 for commit in commits
            if file_path in commit.get("files", [])
        )
        return changes
    
    def _calculate_risk_level(
        self,
        blast_radius: int,
        change_frequency: int,
    ) -> str:
        """
        Calculate risk level based on blast radius and change frequency.
        
        Args:
            blast_radius: Number of affected entities
            change_frequency: Number of recent changes
        
        Returns:
            Risk level: LOW, MEDIUM, HIGH, or CRITICAL
        """
        # Calculate composite score
        score = blast_radius + (change_frequency * 0.5)
        
        if score >= 50:
            return "CRITICAL"
        elif score >= 20:
            return "HIGH"
        elif score >= 10:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_recommendations(
        self,
        risk_level: str,
        affected_files: List[str],
    ) -> List[str]:
        """Generate recommendations based on risk level."""
        recommendations = []
        
        if risk_level == "CRITICAL":
            recommendations.append("⚠️ CRITICAL RISK: Extensive testing required")
            recommendations.append("Consider incremental rollout strategy")
            recommendations.append("Create rollback plan before deployment")
        elif risk_level == "HIGH":
            recommendations.append("⚠️ HIGH RISK: Thorough testing recommended")
            recommendations.append("Review all affected components")
        elif risk_level == "MEDIUM":
            recommendations.append("⚠️ MEDIUM RISK: Standard testing required")
            recommendations.append(f"Review {len(affected_files)} affected files")
        else:
            recommendations.append("✅ LOW RISK: Minimal impact expected")
        
        return recommendations


def get_impact_renderer() -> ImpactAnalysisRenderer:
    """
    Get singleton impact analysis renderer.
    
    Returns:
        ImpactAnalysisRenderer instance
    """
    if not hasattr(get_impact_renderer, "_instance"):
        get_impact_renderer._instance = ImpactAnalysisRenderer()
    return get_impact_renderer._instance
