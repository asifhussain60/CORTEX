"""Orchestrator Consolidation Analyzer

Detects orchestrator sprawl and proposes consolidation strategies.

Author: CORTEX Framework
Phase: PHASE-97 S5
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import ast


@dataclass
class OrchestratorMetadata:
    """Metadata for an orchestrator file.
    
    Attributes:
        file_path: Path to orchestrator file
        class_name: Orchestrator class name
        line_count: Number of lines
        method_count: Number of methods
        dependency_count: Number of dependencies
        last_modified: Last modification timestamp
        usage_count: Number of times used in codebase
    """
    
    file_path: Path
    class_name: str
    line_count: int
    method_count: int
    dependency_count: int
    last_modified: float = 0.0
    usage_count: int = 0


@dataclass
class ConsolidationRecommendation:
    """Recommendation for consolidating orchestrators.
    
    Attributes:
        target_orchestrator: Primary orchestrator to keep
        merge_candidates: Orchestrators to merge into target
        reason: Consolidation rationale
        impact_score: Impact score (0-100, higher = more beneficial)
        effort_hours: Estimated effort in hours
        risk_level: Risk level (low/medium/high)
    """
    
    target_orchestrator: str
    merge_candidates: List[str] = field(default_factory=list)
    reason: str = ""
    impact_score: int = 0
    effort_hours: float = 0.0
    risk_level: str = "low"


@dataclass
class ConsolidationReport:
    """Complete consolidation analysis report.
    
    Attributes:
        total_orchestrators: Total orchestrator count
        target_count: Target orchestrator count after consolidation
        recommendations: List of consolidation recommendations
        sprawl_score: Sprawl severity (0-100)
        estimated_effort: Total estimated effort in hours
    """
    
    total_orchestrators: int
    target_count: int
    recommendations: List[ConsolidationRecommendation] = field(default_factory=list)
    sprawl_score: int = 0
    estimated_effort: float = 0.0
    
    @property
    def reduction_percentage(self) -> float:
        """Calculate reduction percentage.
        
        Returns:
            Percentage reduction in orchestrator count
        """
        if self.total_orchestrators == 0:
            return 0.0
        return (
            (self.total_orchestrators - self.target_count)
            / self.total_orchestrators
            * 100
        )


class ConsolidationAnalyzer:
    """Analyzer for orchestrator sprawl and consolidation.
    
    Detects unnecessary orchestrator proliferation and proposes
    consolidation strategies.
    
    Attributes:
        repo_path: Path to repository root
        orchestrator_dirs: Directories containing orchestrators
    """
    
    def __init__(
        self,
        repo_path: Path,
        orchestrator_dirs: Optional[List[str]] = None,
    ) -> None:
        """Initialize consolidation analyzer.
        
        Args:
            repo_path: Path to repository root
            orchestrator_dirs: Optional list of orchestrator directories
        """
        self.repo_path = repo_path
        self.orchestrator_dirs = orchestrator_dirs or [
            "cortex/orchestrators",
            "cortex/domain_orchestrators",
            "cortex_intelligence/domain",
        ]
    
    def analyze(self) -> ConsolidationReport:
        """Analyze orchestrator sprawl and generate recommendations.
        
        Returns:
            Consolidation report with recommendations
        """
        # Discover all orchestrators
        orchestrators = self._discover_orchestrators()
        
        # Calculate sprawl score
        sprawl_score = self._calculate_sprawl_score(orchestrators)
        
        # Generate consolidation recommendations
        recommendations = self._generate_recommendations(orchestrators)
        
        # Calculate target count
        target_count = len(orchestrators) - sum(
            len(r.merge_candidates) for r in recommendations
        )
        
        # Calculate total effort
        total_effort = sum(r.effort_hours for r in recommendations)
        
        return ConsolidationReport(
            total_orchestrators=len(orchestrators),
            target_count=target_count,
            recommendations=recommendations,
            sprawl_score=sprawl_score,
            estimated_effort=total_effort,
        )
    
    def _discover_orchestrators(self) -> List[OrchestratorMetadata]:
        """Discover all orchestrator files.
        
        Returns:
            List of orchestrator metadata
        """
        orchestrators = []
        
        for dir_name in self.orchestrator_dirs:
            dir_path = self.repo_path / dir_name
            
            if not dir_path.exists():
                continue
            
            for py_file in dir_path.rglob("*.py"):
                if py_file.name.startswith("__"):
                    continue
                
                metadata = self._analyze_file(py_file)
                if metadata:
                    orchestrators.append(metadata)
        
        return orchestrators
    
    def _analyze_file(self, file_path: Path) -> Optional[OrchestratorMetadata]:
        """Analyze single orchestrator file.
        
        Args:
            file_path: Path to file
        
        Returns:
            Orchestrator metadata or None if not an orchestrator
        """
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
            
            # Find orchestrator class
            orchestrator_class = None
            method_count = 0
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if "orchestrator" in node.name.lower():
                        orchestrator_class = node.name
                        method_count = sum(
                            1 for n in node.body if isinstance(n, ast.FunctionDef)
                        )
                        break
            
            if not orchestrator_class:
                return None
            
            # Count dependencies (imports)
            dependency_count = sum(
                1 for node in ast.walk(tree)
                if isinstance(node, (ast.Import, ast.ImportFrom))
            )
            
            return OrchestratorMetadata(
                file_path=file_path,
                class_name=orchestrator_class,
                line_count=len(content.splitlines()),
                method_count=method_count,
                dependency_count=dependency_count,
                last_modified=file_path.stat().st_mtime,
            )
            
        except (SyntaxError, OSError):
            return None
    
    def _calculate_sprawl_score(
        self, orchestrators: List[OrchestratorMetadata]
    ) -> int:
        """Calculate sprawl severity score.
        
        Args:
            orchestrators: List of orchestrator metadata
        
        Returns:
            Sprawl score (0-100, higher = worse sprawl)
        """
        if not orchestrators:
            return 0
        
        # Factors contributing to sprawl:
        # 1. Total count (target: 28, current: len(orchestrators))
        # 2. Small orchestrators (<100 LOC)
        # 3. Low method count (<3 methods)
        
        target_count = 28
        count_factor = min(len(orchestrators) / target_count, 2.0) * 50
        
        small_orchestrators = sum(
            1 for o in orchestrators if o.line_count < 100
        )
        small_factor = (small_orchestrators / len(orchestrators)) * 30
        
        low_method_count = sum(
            1 for o in orchestrators if o.method_count < 3
        )
        method_factor = (low_method_count / len(orchestrators)) * 20
        
        return int(count_factor + small_factor + method_factor)
    
    def _generate_recommendations(
        self, orchestrators: List[OrchestratorMetadata]
    ) -> List[ConsolidationRecommendation]:
        """Generate consolidation recommendations.
        
        Args:
            orchestrators: List of orchestrator metadata
        
        Returns:
            List of consolidation recommendations
        """
        recommendations = []
        
        # Group orchestrators by similarity
        groups = self._group_by_similarity(orchestrators)
        
        for group in groups:
            if len(group) < 2:
                continue
            
            # Select largest as target
            target = max(group, key=lambda o: o.line_count)
            candidates = [o for o in group if o != target]
            
            if not candidates:
                continue
            
            # Calculate impact and effort
            total_loc = sum(o.line_count for o in candidates)
            impact_score = min(int(len(candidates) * 20), 100)
            effort_hours = len(candidates) * 2.0  # 2 hours per merge
            
            # Determine risk level
            if total_loc > 1000:
                risk_level = "high"
            elif total_loc > 500:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            recommendation = ConsolidationRecommendation(
                target_orchestrator=target.class_name,
                merge_candidates=[o.class_name for o in candidates],
                reason=f"Similar functionality, {len(candidates)} candidates",
                impact_score=impact_score,
                effort_hours=effort_hours,
                risk_level=risk_level,
            )
            
            recommendations.append(recommendation)
        
        return sorted(recommendations, key=lambda r: r.impact_score, reverse=True)
    
    def _group_by_similarity(
        self, orchestrators: List[OrchestratorMetadata]
    ) -> List[List[OrchestratorMetadata]]:
        """Group orchestrators by similarity.
        
        Args:
            orchestrators: List of orchestrator metadata
        
        Returns:
            List of orchestrator groups
        """
        # Simple grouping by name prefix/suffix
        groups: Dict[str, List[OrchestratorMetadata]] = {}
        
        for orch in orchestrators:
            # Extract base name (remove suffixes like Orchestrator, Handler, etc.)
            base_name = (
                orch.class_name
                .replace("Orchestrator", "")
                .replace("Handler", "")
                .replace("Manager", "")
            )
            
            if base_name not in groups:
                groups[base_name] = []
            
            groups[base_name].append(orch)
        
        return list(groups.values())
