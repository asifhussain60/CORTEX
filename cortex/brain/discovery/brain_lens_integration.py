"""
LENS Integration for Discovery System.

Integrates GitHistoryAnalyzer, ASTAnalyzer, and CommentExtractor with the
discovery orchestrator to provide implementation truth verification (CORE-030).

This module enables:
- Git history analysis for config evolution tracking
- AST-based complexity metrics for refactor detection
- Comment extraction for TODO/FIXME/NOTE discovery
- Intent pattern detection from multiple evidence sources

Author: Asif Hussain
Phase: 9.3 - LENS Integration
AC-ID: DISC-008
"""

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set

from cortex.brain.analysis.ast_analyzer import ASTAnalyzer
from cortex.brain.analysis.comment_extractor import CommentExtractor
from cortex.lens.analyzers.git_history_analyzer import GitHistoryAnalyzer

logger = logging.getLogger(__name__)


class IntentPattern(Enum):
    """Detected intent patterns from LENS analysis."""

    REFACTOR = "refactor"
    FIX = "fix"
    FEATURE = "feature"
    DOCUMENTATION = "documentation"
    TEST = "test"
    PERFORMANCE = "performance"


@dataclass
class LENSAnalysisResult:
    """Result of complete LENS analysis on a file.

    Attributes:
        file_path: Path to analyzed file
        git_history: Git commit history analysis
        ast_analysis: AST complexity and structure analysis
        comment_data: Extracted comments (TODO, FIXME, etc.)
        intent_patterns: Detected intent patterns with confidence
    """

    file_path: Path
    git_history: Dict
    ast_analysis: Dict
    comment_data: Dict
    intent_patterns: Dict[IntentPattern, int]


class LENSIntegration:
    """Integration layer between LENS analyzers and Discovery System.

    This class provides a unified interface for running LENS analysis
    on code files as part of the discovery process. It combines results
    from Git history, AST analysis, and comment extraction to detect
    implementation patterns and potential issues.

    Examples:
        >>> integration = LENSIntegration(repo_path=Path("/path/to/repo"))
        >>> result = integration.analyze(Path("module.py"))
        >>> if IntentPattern.REFACTOR in result.intent_patterns:
        ...     print(f"Refactor candidate detected")

        >>> # Analyze specific aspect
        >>> git_data = integration.analyze_git_history(Path("service.py"))
        >>> complexity = integration.analyze_ast(Path("service.py"))
    """

    def __init__(self, repo_path: Path):
        """Initialize LENS integration.

        Args:
            repo_path: Root path of the repository to analyze
        """
        self.repo_path = repo_path
        self.git_analyzer = GitHistoryAnalyzer(repo_path=str(repo_path))
        self.ast_analyzer = ASTAnalyzer()
        self.comment_extractor = CommentExtractor()

        logger.info(f"LENS Integration initialized for {repo_path}")

    def get_supported_analyzers(self) -> List[str]:
        """Get list of supported LENS analyzers.

        Returns:
            List of analyzer names

        Examples:
            >>> integration = LENSIntegration(Path("/repo"))
            >>> analyzers = integration.get_supported_analyzers()
            >>> print(analyzers)
            ['git_history', 'ast_analysis', 'comment_extraction']
        """
        return ["git_history", "ast_analysis", "comment_extraction"]

    def analyze_git_history(self, file_path: Path) -> Dict:
        """Analyze Git commit history for a file.

        Args:
            file_path: Path to file to analyze

        Returns:
            Dictionary with commit history data

        Examples:
            >>> integration = LENSIntegration(Path("/repo"))
            >>> history = integration.analyze_git_history(Path("module.py"))
            >>> print(f"Commits: {len(history['commits'])}")
        """
        try:
            history_result = self.git_analyzer.get_file_history(file_path)
            # GitHistoryResult dataclass - extract commits
            commits = history_result.commits if hasattr(history_result, 'commits') else []
            return {
                "commits": [{"commit": c.hash, "message": c.message, "author": c.author} for c in commits],
                "total_commits": len(commits),
            }
        except Exception as e:
            logger.warning(f"Failed to analyze git history for {file_path}: {e}")
            return {"commits": [], "total_commits": 0}

    def analyze_ast(self, file_path: Path) -> Dict:
        """Analyze AST structure and complexity.

        Args:
            file_path: Path to Python file to analyze

        Returns:
            Dictionary with AST analysis data

        Examples:
            >>> integration = LENSIntegration(Path("/repo"))
            >>> ast_data = integration.analyze_ast(Path("complex.py"))
            >>> if ast_data["avg_complexity"] > 10:
            ...     print("High complexity detected")
        """
        try:
            analysis_result = self.ast_analyzer.analyze_file(file_path)
            # ASTAnalysisResult dataclass - extract data
            functions = analysis_result.functions if hasattr(analysis_result, 'functions') else []
            classes = analysis_result.classes if hasattr(analysis_result, 'classes') else []

            return {
                "functions": [{"name": f.name, "complexity": len(f.parameters) + 1} for f in functions],
                "classes": [{"name": c.name, "methods": c.methods} for c in classes],
                "function_count": len(functions),
                "class_count": len(classes),
            }
        except Exception as e:
            logger.warning(f"Failed to analyze AST for {file_path}: {e}")
            return {"functions": [], "classes": [], "function_count": 0, "class_count": 0}

    def extract_comments(self, file_path: Path) -> Dict:
        """Extract TODO, FIXME, and other special comments.

        Args:
            file_path: Path to file to extract comments from

        Returns:
            Dictionary with extracted comments by type

        Examples:
            >>> integration = LENSIntegration(Path("/repo"))
            >>> comments = integration.extract_comments(Path("work.py"))
            >>> print(f"TODOs: {len(comments['todos'])}")
        """
        try:
            extraction_result = self.comment_extractor.extract_comments(file_path)
            # CommentExtractionResult dataclass - extract comments
            comments = extraction_result.comments if hasattr(extraction_result, 'comments') else []

            # Filter by comment type
            todos = [{"line": c.line_number, "text": c.content} for c in comments if 'TODO' in c.content.upper()]
            fixmes = [{"line": c.line_number, "text": c.content} for c in comments if 'FIXME' in c.content.upper()]
            notes = [{"line": c.line_number, "text": c.content} for c in comments if 'NOTE' in c.content.upper()]

            return {
                "todos": todos,
                "fixmes": fixmes,
                "notes": notes,
                "total_comments": len(comments),
            }
        except Exception as e:
            logger.warning(f"Failed to extract comments from {file_path}: {e}")
            return {"todos": [], "fixmes": [], "notes": [], "total_comments": 0}

    def detect_intent_patterns(self, file_path: Path) -> Dict[IntentPattern, int]:
        """Detect intent patterns from combined LENS evidence.

        Analyzes git history, AST complexity, and comments to detect
        patterns like refactoring needs, bug fixes, or documentation gaps.

        Args:
            file_path: Path to file to analyze

        Returns:
            Dictionary mapping IntentPattern to confidence count

        Examples:
            >>> integration = LENSIntegration(Path("/repo"))
            >>> patterns = integration.detect_intent_patterns(Path("legacy.py"))
            >>> if IntentPattern.REFACTOR in patterns:
            ...     print(f"Refactor confidence: {patterns[IntentPattern.REFACTOR]}")
        """
        patterns: Dict[IntentPattern, int] = {}

        # Analyze git history for pattern keywords
        git_data = self.analyze_git_history(file_path)
        for commit in git_data.get("commits", []):
            message = commit.get("message", "").lower()

            if "refactor" in message:
                patterns[IntentPattern.REFACTOR] = patterns.get(IntentPattern.REFACTOR, 0) + 1
            if "fix" in message or "bug" in message:
                patterns[IntentPattern.FIX] = patterns.get(IntentPattern.FIX, 0) + 1
            if "feat" in message or "feature" in message:
                patterns[IntentPattern.FEATURE] = patterns.get(IntentPattern.FEATURE, 0) + 1
            if "docs" in message or "documentation" in message:
                patterns[IntentPattern.DOCUMENTATION] = patterns.get(IntentPattern.DOCUMENTATION, 0) + 1
            if "test" in message:
                patterns[IntentPattern.TEST] = patterns.get(IntentPattern.TEST, 0) + 1
            if "perf" in message or "performance" in message:
                patterns[IntentPattern.PERFORMANCE] = patterns.get(IntentPattern.PERFORMANCE, 0) + 1

        # Analyze AST complexity for refactor candidates
        ast_data = self.analyze_ast(file_path)
        for func in ast_data.get("functions", []):
            complexity = func.get("complexity", 0)
            if complexity > 15:  # High complexity threshold
                patterns[IntentPattern.REFACTOR] = patterns.get(IntentPattern.REFACTOR, 0) + 1

        # Analyze comments for hints
        comment_data = self.extract_comments(file_path)
        for todo in comment_data.get("todos", []):
            todo_text = todo.get("text", "").lower()
            if "refactor" in todo_text:
                patterns[IntentPattern.REFACTOR] = patterns.get(IntentPattern.REFACTOR, 0) + 1
            if "fix" in todo_text:
                patterns[IntentPattern.FIX] = patterns.get(IntentPattern.FIX, 0) + 1

        return patterns

    def analyze(self, file_path: Path) -> LENSAnalysisResult:
        """Perform complete LENS analysis on a file.

        Combines git history, AST analysis, and comment extraction to
        provide comprehensive insights into file state and patterns.

        Args:
            file_path: Path to file to analyze

        Returns:
            LENSAnalysisResult with all analysis data

        Examples:
            >>> integration = LENSIntegration(Path("/repo"))
            >>> result = integration.analyze(Path("service.py"))
            >>> print(f"Commits: {result.git_history['total_commits']}")
            >>> print(f"Functions: {len(result.ast_analysis['functions'])}")
            >>> print(f"TODOs: {len(result.comment_data['todos'])}")
        """
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return LENSAnalysisResult(
                file_path=file_path,
                git_history={},
                ast_analysis={},
                comment_data={},
                intent_patterns={},
            )

        try:
            git_history = self.analyze_git_history(file_path)
            ast_analysis = self.analyze_ast(file_path)
            comment_data = self.extract_comments(file_path)
            intent_patterns = self.detect_intent_patterns(file_path)

            return LENSAnalysisResult(
                file_path=file_path,
                git_history=git_history,
                ast_analysis=ast_analysis,
                comment_data=comment_data,
                intent_patterns=intent_patterns,
            )
        except Exception as e:
            logger.error(f"LENS analysis failed for {file_path}: {e}")
            return LENSAnalysisResult(
                file_path=file_path,
                git_history={},
                ast_analysis={},
                comment_data={},
                intent_patterns={},
            )
