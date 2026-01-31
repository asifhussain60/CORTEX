"""
Complexity Renderer for CORTEX Visualization System.

Generates complexity visualizations including scatter plots and heatmaps
for identifying refactoring candidates based on cyclomatic complexity
and lines of code metrics.

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
Task: 007 - Complexity Renderer
AC-ID: LENS-DASH-003
"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class ComplexityMetrics:
    """
    Complexity metrics for a single function or method.
    
    Attributes:
        name: Function name
        file_path: Relative path to file containing function
        line_number: Starting line number
        loc: Lines of code (excluding comments/blanks)
        complexity: Cyclomatic complexity score
        parameters: Number of parameters
        returns_count: Number of return statements
        risk_level: Color-coded risk (green/yellow/red)
    """
    name: str
    file_path: str
    line_number: int
    loc: int
    complexity: int
    parameters: int
    returns_count: int
    risk_level: str


@dataclass
class ComplexityVisualization:
    """
    Data structure for D3.js complexity visualization.
    
    Attributes:
        scatter_data: List of complexity metrics for scatter plot
        heatmap_data: Nested dict for file-based heatmap
        refactor_candidates: List of high-risk functions
        statistics: Summary statistics
    """
    scatter_data: List[Dict]
    heatmap_data: Dict[str, List[Dict]]
    refactor_candidates: List[Dict]
    statistics: Dict[str, float]


class ComplexityRenderer:
    """
    Renders complexity visualizations from AST analysis.
    
    Generates:
    - Scatter plot: X=LOC, Y=Complexity
    - Heatmap: File-grouped complexity visualization
    - Refactor candidates: Functions exceeding thresholds
    
    Example:
        >>> renderer = ComplexityRenderer()
        >>> ast_data = {"functions": [...]}
        >>> viz = renderer.render_complexity_scatter(ast_data)
        >>> json_output = renderer.format_for_d3(viz)
    """
    
    # Risk thresholds (industry standards)
    COMPLEXITY_THRESHOLDS = {
        "low": 10,      # Green: Complexity < 10
        "medium": 10,   # Yellow: 10 <= Complexity < 20
        "high": 20,     # Red: Complexity >= 20
    }
    
    LOC_THRESHOLDS = {
        "low": 50,      # Small functions
        "medium": 100,  # Medium functions
        "high": 100,    # Large functions
    }
    
    def __init__(self, repo_path: Optional[Path] = None) -> None:
        """
        Initialize complexity renderer.
        
        Args:
            repo_path: Optional repository path for relative file paths
        """
        self.repo_path = repo_path or Path.cwd()
    
    def render_complexity_scatter(
        self,
        ast_analysis: Dict
    ) -> ComplexityVisualization:
        """
        Generate scatter plot data from AST analysis.
        
        Args:
            ast_analysis: AST analysis dict with 'functions' key
        
        Returns:
            ComplexityVisualization with scatter plot data
        
        Example:
            >>> ast_data = {"functions": [{"name": "foo", "complexity": 15}]}
            >>> viz = renderer.render_complexity_scatter(ast_data)
            >>> len(viz.scatter_data) == 1
            True
        """
        functions = ast_analysis.get("functions", [])
        
        scatter_data = []
        for func in functions:
            metrics = self._extract_metrics(func)
            scatter_data.append(asdict(metrics))
        
        # Generate heatmap grouped by file
        heatmap_data = self._generate_heatmap(scatter_data)
        
        # Identify refactor candidates
        candidates = self.identify_refactor_candidates(
            scatter_data,
            complexity_threshold=self.COMPLEXITY_THRESHOLDS["medium"]
        )
        
        # Calculate statistics
        stats = self._calculate_statistics(scatter_data)
        
        return ComplexityVisualization(
            scatter_data=scatter_data,
            heatmap_data=heatmap_data,
            refactor_candidates=candidates,
            statistics=stats
        )
    
    def identify_refactor_candidates(
        self,
        metrics_list: List[Dict],
        complexity_threshold: int = 20,
        loc_threshold: int = 100
    ) -> List[Dict]:
        """
        Identify functions exceeding complexity or LOC thresholds.
        
        Args:
            metrics_list: List of complexity metric dicts
            complexity_threshold: Maximum acceptable complexity
            loc_threshold: Maximum acceptable LOC
        
        Returns:
            List of refactor candidate dicts sorted by risk
        
        Example:
            >>> data = [{"complexity": 25, "loc": 50, "risk_level": "red"}]
            >>> candidates = renderer.identify_refactor_candidates(data, 20, 40)
            >>> len(candidates) == 1
            True
        """
        candidates = []
        
        for metric in metrics_list:
            if (
                metric["complexity"] >= complexity_threshold
                or metric["loc"] >= loc_threshold
            ):
                candidate = metric.copy()
                candidate["reason"] = self._determine_refactor_reason(
                    metric["complexity"],
                    metric["loc"],
                    complexity_threshold,
                    loc_threshold
                )
                candidates.append(candidate)
        
        # Sort by combined risk score (complexity + LOC normalized)
        candidates.sort(
            key=lambda x: (x["complexity"] + x["loc"] / 10),
            reverse=True
        )
        
        return candidates
    
    def generate_complexity_heatmap(
        self,
        ast_analysis: Dict
    ) -> Dict[str, List[Dict]]:
        """
        Generate file-grouped complexity heatmap data.
        
        Args:
            ast_analysis: AST analysis dict with 'functions' key
        
        Returns:
            Dict mapping file paths to complexity metrics
        
        Example:
            >>> ast_data = {"functions": [{"file": "main.py", "complexity": 5}]}
            >>> heatmap = renderer.generate_complexity_heatmap(ast_data)
            >>> "main.py" in heatmap
            True
        """
        functions = ast_analysis.get("functions", [])
        scatter_data = [
            asdict(self._extract_metrics(func))
            for func in functions
        ]
        return self._generate_heatmap(scatter_data)
    
    def format_for_d3(self, visualization: ComplexityVisualization) -> str:
        """
        Format visualization data as JSON for D3.js consumption.
        
        Args:
            visualization: ComplexityVisualization instance
        
        Returns:
            JSON string for D3.js
        
        Example:
            >>> viz = ComplexityVisualization([], {}, [], {})
            >>> json_str = renderer.format_for_d3(viz)
            >>> '"scatter_data"' in json_str
            True
        """
        return json.dumps(asdict(visualization), indent=2)
    
    # Private methods
    
    def _extract_metrics(self, func_data: Dict) -> ComplexityMetrics:
        """Extract complexity metrics from function AST data."""
        name = func_data.get("name", "unknown")
        file_path = func_data.get("file", "unknown")
        line_number = func_data.get("line_number", 0)
        loc = func_data.get("loc", 0)
        complexity = func_data.get("complexity", 1)
        parameters = len(func_data.get("parameters", []))
        returns_count = func_data.get("returns_count", 0)
        
        risk_level = self._calculate_risk_level(complexity, loc)
        
        return ComplexityMetrics(
            name=name,
            file_path=file_path,
            line_number=line_number,
            loc=loc,
            complexity=complexity,
            parameters=parameters,
            returns_count=returns_count,
            risk_level=risk_level
        )
    
    def _calculate_risk_level(self, complexity: int, loc: int) -> str:
        """Determine risk level based on thresholds."""
        if complexity >= self.COMPLEXITY_THRESHOLDS["high"]:
            return "red"
        elif complexity >= self.COMPLEXITY_THRESHOLDS["medium"]:
            return "yellow"
        elif loc >= self.LOC_THRESHOLDS["high"]:
            return "yellow"
        else:
            return "green"
    
    def _generate_heatmap(
        self,
        scatter_data: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """Group metrics by file for heatmap visualization."""
        heatmap: Dict[str, List[Dict]] = {}
        
        for metric in scatter_data:
            file_path = metric["file_path"]
            if file_path not in heatmap:
                heatmap[file_path] = []
            heatmap[file_path].append(metric)
        
        # Sort functions within each file by complexity
        for file_path in heatmap:
            heatmap[file_path].sort(
                key=lambda x: x["complexity"],
                reverse=True
            )
        
        return heatmap
    
    def _calculate_statistics(self, scatter_data: List[Dict]) -> Dict[str, float]:
        """Calculate summary statistics for complexity metrics."""
        if not scatter_data:
            return {
                "mean_complexity": 0.0,
                "median_complexity": 0.0,
                "max_complexity": 0,
                "mean_loc": 0.0,
                "total_functions": 0,
                "high_risk_count": 0,
            }
        
        complexities = [d["complexity"] for d in scatter_data]
        locs = [d["loc"] for d in scatter_data]
        high_risk = sum(
            1 for d in scatter_data
            if d["risk_level"] == "red"
        )
        
        sorted_complexities = sorted(complexities)
        n = len(sorted_complexities)
        median = (
            sorted_complexities[n // 2]
            if n % 2 == 1
            else (sorted_complexities[n // 2 - 1] + sorted_complexities[n // 2]) / 2
        )
        
        return {
            "mean_complexity": sum(complexities) / len(complexities),
            "median_complexity": median,
            "max_complexity": max(complexities),
            "mean_loc": sum(locs) / len(locs),
            "total_functions": len(scatter_data),
            "high_risk_count": high_risk,
        }
    
    def _determine_refactor_reason(
        self,
        complexity: int,
        loc: int,
        complexity_threshold: int,
        loc_threshold: int
    ) -> str:
        """Determine why function is a refactor candidate."""
        reasons = []
        
        if complexity >= complexity_threshold:
            reasons.append(f"High complexity ({complexity})")
        
        if loc >= loc_threshold:
            reasons.append(f"Large function ({loc} LOC)")
        
        return ", ".join(reasons) if reasons else "Unknown"
