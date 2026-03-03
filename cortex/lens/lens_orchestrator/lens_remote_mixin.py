"""
LensRemoteMixin — remote repository and branch analysis for LENSOrchestrator.

Covers:
  - analyze_remote
  - _analyze_git_remote
  - _analyze_ast_content
  - _analyze_comments_content
  - compare_branches

Extracted from lens_orchestrator.py (Phase 103-d, GAP-103-04).
Authority: CORE-008, CORE-011, CORE-012, LENS-003
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, Optional

from cortex.lens.analyzers.git_history_analyzer import GitHistoryAnalyzer
from cortex.lens.analysis.remote_git_adapter import RemoteGitAdapter
from cortex.lens.analysis.branch_comparator import BranchComparator

__all__ = ["LensRemoteMixin"]


class LensRemoteMixin:
    """
    Mixin providing remote repository and branch comparison analysis.

    Requires the host class to have:
        self.repo_path: Path
        self.ast_analyzer: ASTAnalyzer
        self.comment_extractor: CommentExtractor
    """

    def analyze_remote(
        self,
        remote_adapter: RemoteGitAdapter,
        repo: str,
        file_path: str,
        ref: str = "main",
    ) -> Dict[str, Any]:
        """
        Analyze a remote file using LENS intelligence.

        Args:
            remote_adapter: RemoteGitAdapter instance
            repo: Repository identifier (owner/repo)
            file_path: Path to file in repository
            ref: Branch/tag/commit reference (default: "main")

        Returns:
            Dict with git_analysis, ast_analysis, comment_analysis, and _metadata.
        """
        start_time = time.time()

        git_analyzer = GitHistoryAnalyzer(
            repo_path=None,
            remote_adapter=remote_adapter,
            remote_repo=repo,
            remote_ref=ref,
        )

        try:
            remote_file = remote_adapter.fetch_file(repo, file_path, ref)
            file_content = remote_file.content
        except Exception as e:
            return {
                "git_analysis": {"commits": [], "error": str(e)},
                "ast_analysis": {"functions": [], "classes": [], "error": str(e)},
                "comment_analysis": {"todos": [], "fixmes": [], "error": str(e)},
                "_metadata": {
                    "analysis_time_ms": 0,
                    "mode": "remote",
                    "error": str(e),
                },
            }

        git_result = self._analyze_git_remote(git_analyzer, file_path)
        ast_result = self._analyze_ast_content(file_content)
        comment_result = self._analyze_comments_content(file_content)
        analysis_time_ms = int((time.time() - start_time) * 1000)

        return {
            "git_analysis": git_result,
            "ast_analysis": ast_result,
            "comment_analysis": comment_result,
            "_metadata": {
                "analysis_time_ms": analysis_time_ms,
                "file_path": file_path,
                "repo": repo,
                "ref": ref,
                "mode": "remote",
                "analyzers_run": ["git", "ast", "comment"],
            },
        }

    def _analyze_git_remote(
        self,
        git_analyzer: GitHistoryAnalyzer,
        file_path: str,
    ) -> Dict[str, Any]:
        """
        Analyze file with remote GitHistoryAnalyzer.

        Args:
            git_analyzer: GitHistoryAnalyzer with remote configuration
            file_path: Path to file in repository

        Returns:
            Dict with git analysis data
        """
        try:
            result = git_analyzer.get_file_history(file_path, max_commits=20)
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

    def _analyze_ast_content(self, content: str) -> Dict[str, Any]:
        """
        Analyze Python code content with ASTAnalyzer.

        Args:
            content: Python source code

        Returns:
            Dict with AST analysis data
        """
        try:
            result = self.ast_analyzer.analyze_code(content)  # type: ignore[attr-defined]
            if result.success:
                functions = [
                    {
                        "name": func.name,
                        "line_number": func.line_number,
                        "parameters": func.parameters,
                        "is_async": func.is_async,
                    }
                    for func in result.functions
                ]
                classes = [
                    {
                        "name": cls.name,
                        "line_number": cls.line_number,
                        "methods": cls.methods,
                        "bases": cls.bases,
                    }
                    for cls in result.classes
                ]
                return {
                    "functions": functions,
                    "function_count": len(functions),
                    "classes": classes,
                    "class_count": len(classes),
                }
            else:
                return {
                    "functions": [],
                    "function_count": 0,
                    "classes": [],
                    "class_count": 0,
                    "error": result.error,
                }
        except Exception as e:
            return {
                "functions": [],
                "function_count": 0,
                "classes": [],
                "class_count": 0,
                "error": str(e),
            }

    def _analyze_comments_content(self, content: str) -> Dict[str, Any]:
        """
        Analyze comments in Python code content.

        Args:
            content: Python source code

        Returns:
            Dict with comment analysis data
        """
        try:
            result = self.comment_extractor.extract_from_code(content)  # type: ignore[attr-defined]
            if result.success:
                todos = []
                fixmes = []
                for comment in result.comments:
                    content_lower = comment.content.lower()
                    comment_dict = {
                        "text": comment.content,
                        "content": comment.content,
                        "line_number": comment.line_number,
                        "type": comment.comment_type,
                    }
                    if "todo" in content_lower:
                        todos.append(comment_dict)
                    elif "fixme" in content_lower:
                        fixmes.append(comment_dict)
                return {"todos": todos, "fixmes": fixmes, "total_comments": len(result.comments)}
            else:
                return {"todos": [], "fixmes": [], "total_comments": 0, "error": result.error}
        except Exception as e:
            return {"todos": [], "fixmes": [], "total_comments": 0, "error": str(e)}

    def compare_branches(
        self,
        base_branch: str,
        head_branch: str,
        remote_adapter: Optional[RemoteGitAdapter] = None,
        remote_repo: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Compare two branches using BranchComparator.

        Args:
            base_branch: Base branch name
            head_branch: Head branch name to compare against base
            remote_adapter: Optional RemoteGitAdapter for remote comparison
            remote_repo: Optional repository identifier for remote comparison

        Returns:
            Dict with branch comparison results (commits, file diffs, conflicts)
        """
        try:
            if remote_adapter and remote_repo:
                comparator = BranchComparator(
                    repo_path=None,
                    remote_adapter=remote_adapter,
                    remote_repo=remote_repo,
                )
            else:
                comparator = BranchComparator(repo_path=self.repo_path)  # type: ignore[attr-defined]

            comparison = comparator.compare_branches(base_branch, head_branch)

            return {
                "base_branch": comparison.base_branch,
                "head_branch": comparison.head_branch,
                "commits_ahead": comparison.commits_ahead,
                "commits_behind": comparison.commits_behind,
                "commits": [
                    {
                        "hash": commit.hash,
                        "author": commit.author,
                        "date": (
                            commit.date.isoformat()
                            if hasattr(commit.date, "isoformat")
                            else str(commit.date)
                        ),
                        "message": commit.message,
                    }
                    for commit in (comparison.commits or [])
                ],
                "file_diffs": [
                    {
                        "file_path": diff.file_path,
                        "status": diff.status,
                        "additions": diff.additions,
                        "deletions": diff.deletions,
                    }
                    for diff in (comparison.file_diffs or [])
                ],
                "conflicts": [
                    {
                        "file_path": conflict.file_path,
                        "conflict_type": conflict.conflict_type,
                        "description": conflict.description,
                    }
                    for conflict in (comparison.conflicts or [])
                ]
                if comparison.conflicts
                else [],
                "total_additions": comparison.total_additions,
                "total_deletions": comparison.total_deletions,
                "is_mergeable": comparison.is_mergeable,
                "metadata": comparison.metadata,
            }
        except Exception as e:
            return {
                "base_branch": base_branch,
                "head_branch": head_branch,
                "error": str(e),
                "is_mergeable": False,
            }
