"""
UnifiedAnalysisOrchestrator: Consolidated analysis implementation
==============================================================

CONSOLIDATION:
- LENSOrchestrator (L.E.N.S. analysis pipeline)
- ToolDiscoveryOrchestrator (tool discovery + catalog)

Unified API for code analysis and tool discovery.

CORE Governance:
✅ CORE-008: TDD (tests before code)
✅ CORE-011: 100% type hints
✅ CORE-012: 100% docstrings
✅ CORE-013: Specific exception handling
"""

from typing import Dict, List, Optional, Any

from cortex.orchestrators.support.analysis_models import (
    AnalysisType,
    LENSResult,
    ToolInfo,
    DependencyGraph,
)


# ============================================================================
# UnifiedAnalysisOrchestrator
# ============================================================================

class UnifiedAnalysisOrchestrator:
    """
    Unified orchestrator for code analysis and tool discovery.
    
    Consolidates:
    - LENSOrchestrator: L.E.N.S. analysis (Language, Examination, Navigation, Synthesis)
    - ToolDiscoveryOrchestrator: Tool catalog and discovery
    
    Public API:
    - analyze(code, type) → LENSResult
    - discover_tools(query) → List[ToolInfo]
    - analyze_dependencies_graph(deps) → DependencyGraph
    - validate_analysis_result(result) → bool
    """

    def __init__(self) -> None:
        """Initialize UnifiedAnalysisOrchestrator."""
        self._tool_catalog = self._initialize_tool_catalog()
        self._analysis_strategies = {
            "complexity": self._analyze_complexity,
            "security": self._analyze_security,
            "dependencies": self._analyze_dependencies,
            "performance": self._analyze_performance,
        }

    def analyze(self, code: str, analysis_type: str) -> LENSResult:
        """
        Perform code analysis.
        
        Args:
            code: Source code to analyze.
            analysis_type: Type of analysis (complexity, security, dependencies, performance).
            
        Returns:
            LENSResult with analysis findings.
            
        Raises:
            ValueError: If analysis_type is invalid.
        """
        if analysis_type not in self._analysis_strategies:
            raise ValueError(
                f"Invalid analysis type: {analysis_type}. "
                f"Valid options: {list(self._analysis_strategies.keys())}"
            )

        return self._analysis_strategies[analysis_type](code)

    def discover_tools(self, query: str) -> List[ToolInfo]:
        """
        Discover tools matching query.
        
        Args:
            query: Search query (category or tool name).
            
        Returns:
            List of matching ToolInfo objects.
        """
        if not query:
            return list(self._tool_catalog.values())

        query_lower = query.lower()
        return [
            tool for tool in self._tool_catalog.values()
            if query_lower in tool.name.lower()
            or query_lower in tool.category.lower()
        ]

    def analyze_dependencies_graph(self, dependencies: str) -> DependencyGraph:
        """
        Build and analyze dependency graph.
        
        Args:
            dependencies: Dependency string (format: "a,b,c" or "a->b,b->c").
            
        Returns:
            DependencyGraph with analysis.
        """
        nodes, edges = self._parse_dependencies(dependencies)
        cycles = self._detect_cycles(nodes, edges)

        return DependencyGraph(
            nodes=nodes,
            edges=edges,
            has_cycles=len(cycles) > 0,
            unused_dependencies=self._find_unused_dependencies(nodes, edges),
        )

    def validate_analysis_result(self, result: LENSResult) -> bool:
        """
        Validate analysis result.
        
        Args:
            result: LENSResult to validate.
            
        Returns:
            True if valid, False otherwise.
        """
        # Check score is in valid range
        if not (0.0 <= result.score <= 1.0):
            return False

        # Check analysis type is valid
        if not isinstance(result.analysis_type, AnalysisType):
            return False

        # Check findings and recommendations are lists
        if not isinstance(result.findings, list):
            return False

        if not isinstance(result.recommendations, list):
            return False

        return True

    # ========================================================================
    # Private Helpers
    # ========================================================================

    def _initialize_tool_catalog(self) -> Dict[str, ToolInfo]:
        """Initialize tool catalog."""
        return {
            "pytest": ToolInfo(
                name="pytest",
                category="testing",
                description="Python testing framework",
                version="7.4.0",
                installation_command="pip install pytest",
                is_installed=True,
            ),
            "black": ToolInfo(
                name="black",
                category="formatting",
                description="Python code formatter",
                version="23.1.0",
                installation_command="pip install black",
                is_installed=True,
            ),
            "mypy": ToolInfo(
                name="mypy",
                category="linting",
                description="Python type checker",
                version="1.0.0",
                installation_command="pip install mypy",
                is_installed=False,
            ),
            "ruff": ToolInfo(
                name="ruff",
                category="linting",
                description="Fast Python linter",
                version="0.1.0",
                installation_command="pip install ruff",
                is_installed=False,
            ),
            "coverage": ToolInfo(
                name="coverage",
                category="testing",
                description="Code coverage measurement",
                version="7.1.0",
                installation_command="pip install coverage",
                is_installed=True,
            ),
        }

    def _analyze_complexity(self, code: str) -> LENSResult:
        """Analyze code complexity."""
        branch_count = code.count("if ") + code.count("elif ")
        loop_count = code.count("for ") + code.count("while ")
        func_count = code.count("def ")

        # Calculate complexity score
        total_complexity = (branch_count * 0.3 + loop_count * 0.3 + func_count * 0.4) / 10
        score = min(total_complexity, 1.0)

        findings = []
        if branch_count > 5:
            findings.append(f"High branch complexity: {branch_count} branches")
        if loop_count > 3:
            findings.append(f"Multiple nested loops: {loop_count}")

        recommendations = []
        if score > 0.7:
            recommendations.append("Consider simplifying logic")
            recommendations.append("Extract complex functions")

        return LENSResult(
            analysis_type=AnalysisType.COMPLEXITY,
            score=score,
            findings=findings,
            recommendations=recommendations,
            details={
                "branches": branch_count,
                "loops": loop_count,
                "functions": func_count,
            },
        )

    def _analyze_security(self, code: str) -> LENSResult:
        """Analyze code for security issues."""
        findings = []
        score = 1.0

        # Check for security issues
        if "pickle.loads" in code or "pickle.load" in code:
            findings.append("Unsafe pickle deserialization detected")
            score -= 0.3

        if "eval(" in code or "exec(" in code:
            findings.append("Dangerous eval/exec usage detected")
            score -= 0.3

        if "password" in code.lower() and "=" in code:
            findings.append("Potential hardcoded credentials")
            score -= 0.2

        if "SELECT" in code and "f\"" in code:
            findings.append("Potential SQL injection vulnerability")
            score -= 0.2

        recommendations = []
        if score < 0.7:
            recommendations.append("Address security issues before deployment")
            recommendations.append("Use security linter (bandit, semgrep)")

        return LENSResult(
            analysis_type=AnalysisType.SECURITY,
            score=max(0.0, score),
            findings=findings,
            recommendations=recommendations,
            details={"vulnerabilities": len(findings)},
        )

    def _analyze_dependencies(self, path: str) -> LENSResult:
        """Analyze dependencies."""
        # Simplified: just return generic result
        return LENSResult(
            analysis_type=AnalysisType.DEPENDENCIES,
            score=0.8,
            findings=[],
            recommendations=["Keep dependencies updated"],
            details={"dependency_count": 0},
        )

    def _analyze_performance(self, code: str) -> LENSResult:
        """Analyze performance characteristics."""
        findings = []
        score = 1.0

        # Check for performance anti-patterns
        nested_loops = code.count("for ") * code.count("for ")
        if nested_loops > 10:
            findings.append("Deep nested loops detected")
            score -= 0.3

        if code.count("while True") > 0:
            findings.append("Infinite loop pattern detected")
            score -= 0.2

        recommendations = []
        if score < 0.8:
            recommendations.append("Profile code to identify bottlenecks")
            recommendations.append("Consider algorithmic optimization")

        return LENSResult(
            analysis_type=AnalysisType.PERFORMANCE,
            score=max(0.0, score),
            findings=findings,
            recommendations=recommendations,
            details={"issues": len(findings)},
        )

    def _parse_dependencies(self, deps: str) -> tuple:
        """Parse dependency string."""
        nodes = []
        edges = []

        if "->" in deps:
            # Format: a->b,b->c
            for edge in deps.split(","):
                parts = edge.split("->")
                if len(parts) == 2:
                    from_node, to_node = parts[0].strip(), parts[1].strip()
                    nodes.extend([from_node, to_node])
                    edges.append((from_node, to_node))
        else:
            # Format: a,b,c
            nodes = [n.strip() for n in deps.split(",") if n.strip()]

        return list(set(nodes)), edges

    def _detect_cycles(self, nodes: List[str], edges: List[tuple]) -> List[List[str]]:
        """Detect cycles in dependency graph."""
        # Simplified cycle detection
        cycles = []

        for from_node, to_node in edges:
            for edge_from, edge_to in edges:
                if edge_from == to_node and edge_to == from_node:
                    cycles.append([from_node, to_node])

        return cycles

    def _find_unused_dependencies(self, nodes: List[str], edges: List[tuple]) -> List[str]:
        """Find unused dependencies (nodes with no edges)."""
        used_nodes = set()
        for from_node, to_node in edges:
            used_nodes.add(from_node)
            used_nodes.add(to_node)

        return [n for n in nodes if n not in used_nodes]
