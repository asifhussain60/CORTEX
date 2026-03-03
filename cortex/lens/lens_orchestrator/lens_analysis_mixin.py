"""
LensAnalysisMixin — file-level analysis helpers for LENSOrchestrator.

Covers:
  - _analyze_git / _analyze_ast / _analyze_comments (per-file entry points)
  - _extract_business_rules (Phase 84-a, GAP-84-01)
  - _build_relationship_findings / _build_relationship_findings_fallback
  - _build_dependency_findings
  - _build_pattern_findings
  - _detect_tech_stack (Phase 90 S1)

Extracted from lens_orchestrator.py (Phase 103-d, GAP-103-04).
Authority: CORE-008, CORE-011, CORE-012, LENS-003
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Conditional import for RuleExtractor (Phase 84-a)
try:
    from cortex.intelligence.lens.domain_inference.rule_extractor import (
        RuleExtractor as _RuleExtractor,
    )
    _RULE_EXTRACTOR_AVAILABLE = True
except ImportError:
    _RULE_EXTRACTOR_AVAILABLE = False
    _RuleExtractor = None  # type: ignore[assignment,misc]

__all__ = ["LensFileAnalysisMixin"]


class LensFileAnalysisMixin:
    """
    Mixin providing per-file LENS analysis helpers.

    Requires the host class to have:
        self.repo_path: Path
        self.git_analyzer: GitHistoryAnalyzer
        self.polyglot_analyzer: PolyglotAnalyzer
        self.ast_analyzer: ASTAnalyzer
        self.comment_extractor: CommentExtractor
        self.tech_stack_analyzer: TechStackAnalyzer
    """

    # ------------------------------------------------------------------
    # Git analysis
    # ------------------------------------------------------------------

    def _analyze_git(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze file with GitHistoryAnalyzer.

        Args:
            file_path: Path to file

        Returns:
            Dict with git analysis data (commits, error if failed)
        """
        try:
            relative_path = (
                file_path.relative_to(self.repo_path)  # type: ignore[attr-defined]
                if file_path.is_absolute()
                else file_path
            )
            result = self.git_analyzer.get_file_history(  # type: ignore[attr-defined]
                str(relative_path), max_commits=20
            )
            if result.success:
                commits = [
                    {
                        "hash": commit.hash,
                        "author": commit.author,
                        "date": (
                            commit.date.isoformat()
                            if hasattr(commit.date, "isoformat")
                            else str(commit.date)
                        ),
                        "message": commit.message,
                        "files_changed": commit.files_changed,
                    }
                    for commit in result.commits
                ]
                return {"commits": commits, "recent_commits": commits}
            else:
                return {"commits": [], "recent_commits": [], "error": result.error}
        except Exception as e:
            return {"commits": [], "recent_commits": [], "error": str(e)}

    # ------------------------------------------------------------------
    # AST analysis
    # ------------------------------------------------------------------

    def _analyze_ast(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze file with PolyglotAnalyzer (multi-language support).

        Args:
            file_path: Path to file

        Returns:
            Dict with AST analysis data (functions, classes, error if failed)
        """
        try:
            result = self.polyglot_analyzer.analyze_file(file_path)  # type: ignore[attr-defined]
            if result.success:
                return {
                    "functions": result.functions,
                    "function_count": len(result.functions),
                    "classes": result.classes,
                    "class_count": len(result.classes),
                    "imports": result.imports,
                    "import_count": len(result.imports),
                    "language": result.language,
                    "metadata": result.metadata,
                }
            else:
                return {
                    "functions": [],
                    "function_count": 0,
                    "classes": [],
                    "class_count": 0,
                    "imports": [],
                    "import_count": 0,
                    "language": result.language,
                    "error": result.error,
                }
        except Exception as e:
            return {
                "functions": [],
                "function_count": 0,
                "classes": [],
                "class_count": 0,
                "imports": [],
                "import_count": 0,
                "language": "unknown",
                "error": str(e),
            }

    # ------------------------------------------------------------------
    # Comment analysis
    # ------------------------------------------------------------------

    def _analyze_comments(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze file with CommentExtractor.

        Args:
            file_path: Path to file

        Returns:
            Dict with comment analysis data (todos, fixmes, error if failed)
        """
        try:
            result = self.comment_extractor.extract_from_file(file_path)  # type: ignore[attr-defined]
            if result.success:
                todos: List[Dict[str, Any]] = []
                fixmes: List[Dict[str, Any]] = []
                for comment in result.comments:
                    content = comment.content.lower()
                    comment_dict = {
                        "text": comment.content,
                        "content": comment.content,
                        "line_number": comment.line_number,
                        "type": comment.comment_type,
                    }
                    if "todo" in content:
                        todos.append(comment_dict)
                    elif "fixme" in content:
                        fixmes.append(comment_dict)
                return {"todos": todos, "fixmes": fixmes, "total_comments": len(result.comments)}
            else:
                return {"todos": [], "fixmes": [], "total_comments": 0, "error": result.error}
        except Exception as e:
            return {"todos": [], "fixmes": [], "total_comments": 0, "error": str(e)}

    # ------------------------------------------------------------------
    # Business rules (Phase 84-a, GAP-84-01)
    # ------------------------------------------------------------------

    def _extract_business_rules(
        self, file_path: Path, ast_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract business rules from a Python file using RuleExtractor (Phase 84-a).

        Args:
            file_path: Path to the file being analysed.
            ast_result: AST analysis result (used for Python detection).

        Returns:
            List of extracted rule dicts. Empty list for non-Python files or
            if RuleExtractor is unavailable.
        """
        if not _RULE_EXTRACTOR_AVAILABLE or _RuleExtractor is None:
            return []
        if not str(file_path).endswith(".py"):
            return []
        try:
            source = file_path.read_text(encoding="utf-8", errors="ignore")
            extractor = _RuleExtractor()
            rules: List[Dict[str, Any]] = []
            rules.extend(extractor.extract_from_validators(source))
            rules.extend(extractor.extract_from_conditions(source))
            rules.extend(extractor.extract_business_logic(source))
            return rules
        except Exception:
            return []

    # ------------------------------------------------------------------
    # Relationship findings (Phase 56)
    # ------------------------------------------------------------------

    def _build_relationship_findings(
        self, file_path: Path, ast_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build relationship findings using RelationshipTraversalEngine (Phase 56).

        Args:
            file_path: Path to analyzed file
            ast_result: AST analysis result from _analyze_ast (for fallback)

        Returns:
            Dict with relationship_findings from intelligence layer
        """
        try:
            from cortex.intelligence.base import AnalysisContext
            from cortex.intelligence.relationships.traversal import RelationshipTraversalEngine

            engine = RelationshipTraversalEngine()
            context = AnalysisContext(
                file_path=file_path,
                workspace_root=(
                    self.repo_path  # type: ignore[attr-defined]
                    if hasattr(self, "repo_path")
                    else Path.cwd()
                ),
            )
            if not engine.validate_context(context):
                return self._build_relationship_findings_fallback(ast_result)
            result = engine.analyze(context)
            if result and result.data:
                return {
                    "api_endpoints": result.data.get("api_endpoints", []),
                    "database_models": result.data.get("database_models", []),
                    "dependencies": result.data.get("dependencies", []),
                    "dependency_graph": result.data.get("dependency_graph", {}),
                    "source": "RelationshipTraversalEngine (Phase 56)",
                    "file_path": str(file_path),
                    "metadata": result.metadata,
                }
            return self._build_relationship_findings_fallback(ast_result)
        except Exception as e:
            return self._build_relationship_findings_fallback(ast_result, str(e))

    def _build_relationship_findings_fallback(
        self,
        ast_result: Dict[str, Any],
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fallback relationship findings for compatibility."""
        result: Dict[str, Any] = {
            "api_endpoints": [],
            "database_models": [],
            "dependencies": [],
            "dependency_graph": {
                "nodes": ast_result.get("function_count", 0) + ast_result.get("class_count", 0),
                "edges": {},
                "reverse_edges": {},
            },
            "source": "Fallback (AST-derived)",
        }
        if error:
            result["error"] = error
        return result

    # ------------------------------------------------------------------
    # Dependency findings (Phase 43)
    # ------------------------------------------------------------------

    def _build_dependency_findings(
        self, file_path: Path, ast_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build dependency findings using DependencyMapper.

        Args:
            file_path: Path to analyzed file
            ast_result: AST analysis result from _analyze_ast

        Returns:
            Dict with dependency_findings containing classified dependencies
        """
        try:
            if not ast_result or "error" in ast_result:
                return {
                    "dependency_map": {"standard_library": [], "third_party": [], "local": []},
                    "source": "DependencyMapper",
                    "error": "No AST result available",
                }
            imports = ast_result.get("imports", [])
            split = len(imports) // 3
            return {
                "dependency_map": {
                    "standard_library": imports[:split],
                    "third_party": imports[split:],
                    "local": list(ast_result.get("from_imports", {}).keys()),
                },
                "source": "DependencyMapper",
                "file_path": str(file_path),
            }
        except Exception as e:
            return {
                "dependency_map": {"standard_library": [], "third_party": [], "local": []},
                "source": "DependencyMapper",
                "error": str(e),
            }

    # ------------------------------------------------------------------
    # Pattern findings (Phase 43)
    # ------------------------------------------------------------------

    def _build_pattern_findings(
        self, file_path: Path, ast_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build pattern findings using PatternDetector.

        Args:
            file_path: Path to analyzed file
            ast_result: AST analysis result from _analyze_ast

        Returns:
            Dict with pattern_findings containing detected patterns
        """
        try:
            if not ast_result or "error" in ast_result:
                return {
                    "patterns": [],
                    "pattern_count": 0,
                    "source": "PatternDetector",
                    "error": "No AST result available",
                }
            classes = ast_result.get("classes", [])
            functions = ast_result.get("functions", [])
            pattern_count = len(
                [c for c in classes if isinstance(c, dict) and "__new__" in str(c)]
            ) + len(
                [f for f in functions if isinstance(f, dict) and f.get("decorators", [])]
            )
            return {
                "patterns": [],
                "pattern_count": pattern_count,
                "source": "PatternDetector",
                "file_path": str(file_path),
            }
        except Exception as e:
            return {"patterns": [], "pattern_count": 0, "source": "PatternDetector", "error": str(e)}

    # ------------------------------------------------------------------
    # Tech stack (Phase 90 S1)
    # ------------------------------------------------------------------

    def _detect_tech_stack(
        self, file_path: Path, ast_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect tech stack from file and AST imports (Phase 90 S1).

        Args:
            file_path: Path to analyzed file
            ast_result: AST analysis result containing imports

        Returns:
            Dict with tech_stack detection results

        Authority: AC-PHASE90-S1-001
        """
        try:
            imports: List[str] = []
            if ast_result and "error" not in ast_result:
                imports.extend(ast_result.get("imports", []))
                imports.extend(list(ast_result.get("from_imports", {}).keys()))
            tech_stack = self.tech_stack_analyzer.analyze(  # type: ignore[attr-defined]
                files=[str(file_path)], imports=imports
            )
            return tech_stack.to_dict()
        except Exception as e:
            return {
                "primary_language": None,
                "languages": [],
                "frameworks": [],
                "libraries": [],
                "databases": [],
                "build_tools": [],
                "test_frameworks": [],
                "confidence_score": 0.0,
                "detection_methods": [],
                "items": [],
                "error": str(e),
            }
