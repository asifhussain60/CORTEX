"""AC-PHASE43-016: Repository Context Builder

Validates multi-layer context synthesis for onboarding.

Target: 5/5 tests passing
AC-ID: AC-PHASE43-016
"""

import pytest
from typing import Dict, Any, List


class RepositoryContextBuilder:
    """Synthesize multi-layer repository context (Phase 43: AC-PHASE43-016)."""
    
    def __init__(self):
        """Initialize context builder."""
        self.layers = []
    
    def build_context(self, 
                      repo_path: str,
                      file_tree: Dict[str, Any],
                      git_history: List[Dict[str, Any]],
                      code_metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Build comprehensive repository context.
        
        Args:
            repo_path: Repository path
            file_tree: Repository file structure
            git_history: Recent git commits
            code_metrics: Code metrics (complexity, coverage, etc.)
            
        Returns:
            Multi-layer context dictionary
        """
        return {
            "repository": {
                "path": repo_path,
                "file_count": self._count_files(file_tree),
            },
            "structure": self._analyze_structure(file_tree),
            "history": self._summarize_history(git_history),
            "quality": self._assess_quality(code_metrics),
            "synthesis": self._synthesize_layers(file_tree, git_history, code_metrics),
        }
    
    def _count_files(self, file_tree: Dict[str, Any]) -> int:
        """Count files in tree."""
        count = 0
        for key, val in file_tree.items():
            if isinstance(val, dict) and val:  # Non-empty dict = directory
                count += self._count_files(val)
            elif isinstance(val, dict) and not val:  # Empty dict = file placeholder
                count += 1
            else:
                count += 1
        return count
    
    def _analyze_structure(self, file_tree: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze directory structure."""
        return {
            "root_items": len(file_tree),
            "has_tests": any("test" in k.lower() for k in file_tree.keys()),
            "has_docs": any("doc" in k.lower() for k in file_tree.keys()),
        }
    
    def _summarize_history(self, git_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize git history."""
        return {
            "total_commits": len(git_history),
            "recent_activity": "active" if len(git_history) > 0 else "inactive",
            "authors": len(set(c.get("author", "") for c in git_history)),
        }
    
    def _assess_quality(self, code_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Assess code quality."""
        return {
            "cyclomatic_complexity": code_metrics.get("complexity", 0.0),
            "test_coverage": code_metrics.get("coverage", 0.0),
            "quality_rating": self._rate_quality(code_metrics),
        }
    
    def _rate_quality(self, metrics: Dict[str, float]) -> str:
        """Rate code quality."""
        coverage = metrics.get("coverage", 0.0)
        complexity = metrics.get("complexity", 10.0)
        
        if coverage >= 0.8 and complexity <= 10.0:
            return "High"
        elif coverage >= 0.6 or complexity <= 15.0:
            return "Medium"
        else:
            return "Low"
    
    def _synthesize_layers(self, 
                          file_tree: Dict[str, Any],
                          git_history: List[Dict[str, Any]],
                          code_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Synthesize all layers into coherent context."""
        return {
            "maturity": self._assess_maturity(git_history),
            "stability": self._assess_stability(code_metrics),
            "maintainability": self._assess_maintainability(file_tree, code_metrics),
        }
    
    def _assess_maturity(self, git_history: List[Dict[str, Any]]) -> str:
        """Assess project maturity."""
        commit_count = len(git_history)
        if commit_count > 100:
            return "Mature"
        elif commit_count > 20:
            return "Growing"
        else:
            return "Early"
    
    def _assess_stability(self, code_metrics: Dict[str, float]) -> float:
        """Assess codebase stability (0-1)."""
        coverage = code_metrics.get("coverage", 0.0)
        # Stability: 30% coverage + 70% complexity score
        complexity_score = 1.0 / (1.0 + code_metrics.get("complexity", 10.0) / 10.0)
        return (coverage * 0.3) + (complexity_score * 0.7)
    
    def _assess_maintainability(self, file_tree: Dict[str, Any], 
                               code_metrics: Dict[str, float]) -> float:
        """Assess maintainability (0-1)."""
        file_count = self._count_files(file_tree)
        coverage = code_metrics.get("coverage", 0.0)
        
        # Maintainability: size penalty + coverage bonus
        size_score = 1.0 / (1.0 + file_count / 100.0)
        return min(1.0, (size_score * 0.6) + (coverage * 0.4))


class TestRepositoryContextBuilder:
    """Tests for repository context building."""
    
    def test_builder_initializes(self):
        """Validate builder initializes."""
        builder = RepositoryContextBuilder()
        assert builder is not None
        assert isinstance(builder.layers, list)
    
    def test_builder_synthesizes_context(self):
        """Validate context synthesis."""
        builder = RepositoryContextBuilder()
        
        context = builder.build_context(
            repo_path="/test/repo",
            file_tree={"src": {"file.py": {}}, "tests": {"test.py": {}}},
            git_history=[{"author": "Alice"}, {"author": "Bob"}],
            code_metrics={"coverage": 0.85, "complexity": 8.0},
        )
        
        assert context["repository"]["path"] == "/test/repo"
        assert "structure" in context
        assert "history" in context
        assert "quality" in context
    
    def test_builder_counts_files(self):
        """Validate file counting."""
        builder = RepositoryContextBuilder()
        
        file_tree = {
            "src": {"a.py": {}, "b.py": {}},
            "tests": {"t1.py": {}, "t2.py": {}},
        }
        
        context = builder.build_context(
            repo_path="/test",
            file_tree=file_tree,
            git_history=[],
            code_metrics={},
        )
        
        assert context["repository"]["file_count"] == 4
    
    def test_builder_assesses_quality(self):
        """Validate quality assessment."""
        builder = RepositoryContextBuilder()
        
        context = builder.build_context(
            repo_path="/test",
            file_tree={},
            git_history=[],
            code_metrics={"coverage": 0.85, "complexity": 8.0},
        )
        
        assert context["quality"]["quality_rating"] == "High"
        assert context["quality"]["test_coverage"] == 0.85
    
    def test_builder_synthesizes_maturity_and_stability(self):
        """Validate maturity and stability synthesis."""
        builder = RepositoryContextBuilder()
        
        context = builder.build_context(
            repo_path="/test",
            file_tree={},
            git_history=[{"author": "Alice"}] * 150,  # 150 commits
            code_metrics={"coverage": 0.75, "complexity": 9.0},
        )
        
        synthesis = context["synthesis"]
        assert synthesis["maturity"] == "Mature"
        assert synthesis["stability"] > 0.5  # Good stability
