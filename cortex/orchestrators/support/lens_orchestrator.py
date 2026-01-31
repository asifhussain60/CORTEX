"""
LENS Orchestrator for CORTEX.

Unified orchestrator coordinating GitHistoryAnalyzer, ASTAnalyzer, 
CommentExtractor, and VisionAnalyzer for the LENS (Language→Examination→Navigation→Synthesis)
intelligence cycle.

Provides:
- Unified code intelligence API
- Vision analysis for image attachments
- Caching for repeated analysis
- Batch file analysis
- IntentRouter-compatible output format

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings), LENS-003
"""

import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from cortex.brain.analysis.git_history_analyzer import GitHistoryAnalyzer
from cortex.brain.analysis.ast_analyzer import ASTAnalyzer
from cortex.brain.analysis.comment_extractor import CommentExtractor
from cortex.brain.analysis.remote_git_adapter import RemoteGitAdapter
from cortex.brain.analysis.branch_comparator import BranchComparator
from cortex.brain.analysis.vision_analyzer import VisionAnalyzer, VisionAnalysisResult


@dataclass
class LENSContext:
    """
    Unified LENS intelligence context.
    
    Compatible with IntentRouter's lens_context parameter (LENS-002).
    
    Attributes:
        git_analysis: Git commit history and patterns
        ast_analysis: AST structure and complexity
        comment_analysis: Comments, TODOs, and docstrings
        vision_analysis: Vision API analysis for images (URLs, elements, issues)
        metadata: Analysis metadata (timing, cache hits, etc.)
    """
    git_analysis: Dict[str, Any] = field(default_factory=dict)
    ast_analysis: Dict[str, Any] = field(default_factory=dict)
    comment_analysis: Dict[str, Any] = field(default_factory=dict)
    vision_analysis: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for IntentRouter compatibility."""
        result = {
            "git_analysis": self.git_analysis,
            "ast_analysis": self.ast_analysis,
            "comment_analysis": self.comment_analysis,
            "_metadata": self.metadata,
        }
        # Only include vision_analysis if present
        if self.vision_analysis:
            result["vision_analysis"] = self.vision_analysis
        return result


class LENSOrchestrator:
    """
    Unified LENS intelligence orchestrator.
    
    Coordinates GitHistoryAnalyzer, ASTAnalyzer, and CommentExtractor
    to provide comprehensive code intelligence for CORTEX operations.
    
    Features:
    - Unified analyze_file() API combining all three analyzers
    - Result caching for performance (avoids repeated analysis)
    - Batch analysis for multiple files
    - IntentRouter-compatible output (LENS-002 integration)
    - Graceful error handling (partial results on analyzer failures)
    
    Example:
        ```python
        orchestrator = LENSOrchestrator(repo_path=Path("/path/to/repo"))
        
        # Analyze single file
        lens_context = orchestrator.analyze_file(Path("src/module.py"))
        
        # Use with IntentRouter
        router = IntentRouter()
        decision = router.route({
            "operation": "refactor",
            "lens_context": lens_context
        })
        
        # Batch analysis
        results = orchestrator.analyze_batch([
            Path("file1.py"),
            Path("file2.py"),
        ])
        ```
    
    Attributes:
        repo_path: Path to git repository root
        git_analyzer: Git history analyzer instance
        ast_analyzer: AST analyzer instance
        comment_extractor: Comment extractor instance
        cache: Result cache (path -> LENSContext)
    """
    
    def __init__(
        self,
        repo_path: Path,
        git_analyzer: Optional[GitHistoryAnalyzer] = None,
        ast_analyzer: Optional[ASTAnalyzer] = None,
        comment_extractor: Optional[CommentExtractor] = None,
    ):
        """
        Initialize LENSOrchestrator.
        
        Args:
            repo_path: Path to git repository root
            git_analyzer: Optional custom GitHistoryAnalyzer (for testing)
            ast_analyzer: Optional custom ASTAnalyzer (for testing)
            comment_extractor: Optional custom CommentExtractor (for testing)
        """
        self.repo_path = repo_path
        
        # Initialize analyzers (use provided or create defaults)
        self.git_analyzer = git_analyzer or GitHistoryAnalyzer(repo_path=repo_path)
        self.ast_analyzer = ast_analyzer or ASTAnalyzer()
        self.comment_extractor = comment_extractor or CommentExtractor()
        
        # Result cache (path -> dict)
        self.cache: Dict[Path, Dict[str, Any]] = {}
    
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a single file using all three LENS analyzers.
        
        Coordinates Git, AST, and Comment analysis to produce unified
        intelligence context. Results are cached for performance.
        
        Output format is compatible with IntentRouter's lens_context
        parameter (LENS-002 integration).
        
        Args:
            file_path: Path to file to analyze
        
        Returns:
            Dict with git_analysis, ast_analysis, comment_analysis, and _metadata.
            Format matches IntentRouter LENS-002 expectations:
            - git_analysis.commits or git_analysis.recent_commits
            - ast_analysis.functions (list) or ast_analysis.function_count
            - ast_analysis.classes (list) or ast_analysis.class_count
            - comment_analysis.todos
        
        Example:
            ```python
            result = orchestrator.analyze_file(Path("module.py"))
            
            # Access git data
            commits = result["git_analysis"]["commits"]
            
            # Access AST data
            functions = result["ast_analysis"]["functions"]
            classes = result["ast_analysis"]["classes"]
            
            # Access comments
            todos = result["comment_analysis"]["todos"]
            ```
        """
        # Check cache first
        if file_path in self.cache:
            return self.cache[file_path]
        
        start_time = time.time()
        
        # Run all three analyzers
        git_result = self._analyze_git(file_path)
        ast_result = self._analyze_ast(file_path)
        comment_result = self._analyze_comments(file_path)
        
        # Calculate analysis time
        analysis_time_ms = int((time.time() - start_time) * 1000)
        
        # Build unified context
        context = {
            "git_analysis": git_result,
            "ast_analysis": ast_result,
            "comment_analysis": comment_result,
            "_metadata": {
                "analysis_time_ms": analysis_time_ms,
                "file_path": str(file_path),
                "analyzers_run": ["git", "ast", "comment"],
            }
        }
        
        # Cache result
        self.cache[file_path] = context
        
        return context
    
    def _analyze_git(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze file with GitHistoryAnalyzer.
        
        Args:
            file_path: Path to file
        
        Returns:
            Dict with git analysis data (commits, error if failed)
        """
        try:
            # Get file path relative to repo
            relative_path = file_path.relative_to(self.repo_path) if file_path.is_absolute() else file_path
            
            result = self.git_analyzer.get_file_history(str(relative_path), max_commits=20)
            
            if result.success:
                # Format for IntentRouter compatibility
                commits = [
                    {
                        "hash": commit.hash,
                        "author": commit.author,
                        "date": commit.date.isoformat() if hasattr(commit.date, 'isoformat') else str(commit.date),
                        "message": commit.message,
                        "files_changed": commit.files_changed,
                    }
                    for commit in result.commits
                ]
                return {
                    "commits": commits,
                    "recent_commits": commits,  # Alias for compatibility
                }
            else:
                return {
                    "commits": [],
                    "recent_commits": [],
                    "error": result.error,
                }
        except Exception as e:
            return {
                "commits": [],
                "recent_commits": [],
                "error": str(e),
            }
    
    def _analyze_ast(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze file with ASTAnalyzer.
        
        Args:
            file_path: Path to file
        
        Returns:
            Dict with AST analysis data (functions, classes, error if failed)
        """
        try:
            result = self.ast_analyzer.analyze_file(file_path)
            
            if result.success:
                # Format for IntentRouter compatibility
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
    
    def _analyze_comments(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze file with CommentExtractor.
        
        Args:
            file_path: Path to file
        
        Returns:
            Dict with comment analysis data (todos, fixmes, error if failed)
        """
        try:
            result = self.comment_extractor.extract_from_file(file_path)
            
            if result.success:
                # Separate TODOs and FIXMEs
                todos = []
                fixmes = []
                
                for comment in result.comments:
                    content = comment.content.lower()
                    comment_dict = {
                        "text": comment.content,
                        "content": comment.content,  # Alias for compatibility
                        "line_number": comment.line_number,
                        "type": comment.comment_type,
                    }
                    
                    if "todo" in content:
                        todos.append(comment_dict)
                    elif "fixme" in content:
                        fixmes.append(comment_dict)
                
                return {
                    "todos": todos,
                    "fixmes": fixmes,
                    "total_comments": len(result.comments),
                }
            else:
                return {
                    "todos": [],
                    "fixmes": [],
                    "total_comments": 0,
                    "error": result.error,
                }
        except Exception as e:
            return {
                "todos": [],
                "fixmes": [],
                "total_comments": 0,
                "error": str(e),
            }
    
    def analyze_image(
        self,
        image_data: Optional[str] = None,
        image_url: Optional[str] = None,
        image_path: Optional[Path] = None,
        image_type: str = "unknown",
        analysis_depth: str = "standard",
    ) -> Dict[str, Any]:
        """
        Analyze an image using VisionAnalyzer.
        
        Extracts UI elements, URLs, issues, and structural information
        from screenshots, diagrams, mockups, and error messages.
        
        Args:
            image_data: Base64-encoded image data
            image_url: URL to image
            image_path: Path to image file
            image_type: Type of image (screenshot/diagram/mockup/error/unknown)
            analysis_depth: Depth of analysis (quick/standard/thorough)
            
        Returns:
            Dict with urls, ui_elements, issues, text_content, structural_map
            
        Example:
            ```python
            # Analyze from base64
            result = orchestrator.analyze_image(image_data=base64_data)
            
            # Analyze from URL
            result = orchestrator.analyze_image(image_url="https://example.com/screenshot.png")
            
            # Analyze from file
            result = orchestrator.analyze_image(image_path=Path("screenshot.png"))
            
            # Access extracted data
            for url in result["urls"]:
                print(f"Found URL: {url['url']}")
            
            for element in result["ui_elements"]:
                print(f"Element: {element['type']} - {element['text']}")
            ```
        """
        from cortex.brain.analysis.vision_analyzer import (
            VisionAnalyzer,
            ImageType,
            AnalysisDepth,
        )
        
        try:
            analyzer = VisionAnalyzer()
            
            # Parse enums
            try:
                img_type = ImageType(image_type.lower())
            except ValueError:
                img_type = ImageType.UNKNOWN
                
            try:
                depth = AnalysisDepth(analysis_depth.lower())
            except ValueError:
                depth = AnalysisDepth.STANDARD
            
            # Analyze based on input type
            if image_path and image_path.exists():
                result = analyzer.analyze_file(
                    file_path=image_path,
                    image_type=img_type,
                    depth=depth,
                )
            elif image_data:
                result = analyzer.analyze_base64(
                    image_data=image_data,
                    image_type=img_type,
                    depth=depth,
                )
            elif image_url:
                result = analyzer.analyze_url(
                    image_url=image_url,
                    image_type=img_type,
                    depth=depth,
                )
            else:
                return {
                    "status": "error",
                    "error": "Must provide image_data, image_url, or image_path",
                }
            
            return result.to_dict()
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
    
    def analyze_with_vision(
        self,
        file_path: Optional[Path] = None,
        image_data: Optional[str] = None,
        image_url: Optional[str] = None,
        image_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Combined LENS + Vision analysis.
        
        Performs standard LENS analysis on a code file (if provided)
        AND Vision analysis on an image (if provided).
        
        Args:
            file_path: Path to code file for LENS analysis
            image_data: Base64-encoded image for Vision analysis
            image_url: URL to image for Vision analysis
            image_path: Path to image file for Vision analysis
            
        Returns:
            Dict with git_analysis, ast_analysis, comment_analysis, vision_analysis
        """
        result: Dict[str, Any] = {
            "git_analysis": {},
            "ast_analysis": {},
            "comment_analysis": {},
            "vision_analysis": {},
            "_metadata": {
                "analyzers_run": [],
            },
        }
        
        # Run LENS analysis on code file
        if file_path and file_path.exists():
            lens_result = self.analyze_file(file_path)
            result["git_analysis"] = lens_result.get("git_analysis", {})
            result["ast_analysis"] = lens_result.get("ast_analysis", {})
            result["comment_analysis"] = lens_result.get("comment_analysis", {})
            result["_metadata"]["analyzers_run"].extend(["git", "ast", "comment"])
        
        # Run Vision analysis on image
        if image_data or image_url or image_path:
            vision_result = self.analyze_image(
                image_data=image_data,
                image_url=image_url,
                image_path=image_path,
            )
            result["vision_analysis"] = vision_result
            result["_metadata"]["analyzers_run"].append("vision")
        
        return result
    
    def clear_cache(self) -> None:
        """
        Clear the result cache.
        
        Forces re-analysis on next analyze_file() call.
        Useful after file modifications or for testing.
        """
        self.cache.clear()
    
    def analyze_batch(self, file_paths: List[Path]) -> Dict[Path, Dict[str, Any]]:
        """
        Analyze multiple files in batch.
        
        Processes each file through analyze_file() (which uses caching).
        
        Args:
            file_paths: List of file paths to analyze
        
        Returns:
            Dict mapping file paths to LENS contexts
        
        Example:
            ```python
            results = orchestrator.analyze_batch([
                Path("file1.py"),
                Path("file2.py"),
                Path("file3.py"),
            ])
            
            for path, context in results.items():
                print(f"{path}: {len(context['git_analysis']['commits'])} commits")
            ```
        """
        results = {}
        
        for file_path in file_paths:
            results[file_path] = self.analyze_file(file_path)
        
        return results
    
    def analyze_remote(
        self,
        remote_adapter: RemoteGitAdapter,
        repo: str,
        file_path: str,
        ref: str = "main",
    ) -> Dict[str, Any]:
        """
        Analyze a remote file using LENS intelligence.
        
        Fetches file content and commit history from remote repository
        and performs AST and comment analysis.
        
        Args:
            remote_adapter: RemoteGitAdapter instance
            repo: Repository identifier (owner/repo)
            file_path: Path to file in repository
            ref: Branch/tag/commit reference (default: "main")
        
        Returns:
            Dict with git_analysis, ast_analysis, comment_analysis, and _metadata.
            Same format as analyze_file() for compatibility.
        
        Example:
            ```python
            from cortex.brain.analysis.remote_git_adapter import create_adapter
            from cortex.brain.analysis.providers import ProviderConfig
            
            config = ProviderConfig(provider="github", token="ghp_...")
            adapter = create_adapter(config)
            
            result = orchestrator.analyze_remote(
                remote_adapter=adapter,
                repo="owner/repo",
                file_path="src/module.py",
                ref="main"
            )
            ```
        """
        start_time = time.time()
        
        # Create remote git analyzer
        git_analyzer = GitHistoryAnalyzer(
            repo_path=None,
            remote_adapter=remote_adapter,
            remote_repo=repo,
            remote_ref=ref,
        )
        
        # Fetch file content
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
                }
            }
        
        # Git analysis
        git_result = self._analyze_git_remote(git_analyzer, file_path)
        
        # AST analysis (analyze content directly)
        ast_result = self._analyze_ast_content(file_content)
        
        # Comment analysis (analyze content directly)
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
            }
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
                        "date": commit.date.isoformat() if hasattr(commit.date, 'isoformat') else str(commit.date),
                        "message": commit.message,
                        "files_changed": commit.files_changed,
                    }
                    for commit in result.commits
                ]
                return {
                    "commits": commits,
                    "recent_commits": commits,
                }
            else:
                return {
                    "commits": [],
                    "recent_commits": [],
                    "error": result.error,
                }
        except Exception as e:
            return {
                "commits": [],
                "recent_commits": [],
                "error": str(e),
            }
    
    def _analyze_ast_content(self, content: str) -> Dict[str, Any]:
        """
        Analyze Python code content with ASTAnalyzer.
        
        Args:
            content: Python source code
        
        Returns:
            Dict with AST analysis data
        """
        try:
            result = self.ast_analyzer.analyze_code(content)
            
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
            result = self.comment_extractor.extract_from_code(content)
            
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
                
                return {
                    "todos": todos,
                    "fixmes": fixmes,
                    "total_comments": len(result.comments),
                }
            else:
                return {
                    "todos": [],
                    "fixmes": [],
                    "total_comments": 0,
                    "error": result.error,
                }
        except Exception as e:
            return {
                "todos": [],
                "fixmes": [],
                "total_comments": 0,
                "error": str(e),
            }
    
    def compare_branches(
        self,
        base_branch: str,
        head_branch: str,
        remote_adapter: Optional[RemoteGitAdapter] = None,
        remote_repo: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Compare two branches using BranchComparator.
        
        Can compare local or remote branches.
        
        Args:
            base_branch: Base branch name
            head_branch: Head branch name to compare against base
            remote_adapter: Optional RemoteGitAdapter for remote comparison
            remote_repo: Optional repository identifier for remote comparison
        
        Returns:
            Dict with branch comparison results (commits, file diffs, conflicts)
        
        Example:
            ```python
            # Local comparison
            result = orchestrator.compare_branches("main", "feature")
            
            # Remote comparison
            result = orchestrator.compare_branches(
                "main",
                "feature",
                remote_adapter=adapter,
                remote_repo="owner/repo"
            )
            ```
        """
        try:
            if remote_adapter and remote_repo:
                # Remote comparison
                comparator = BranchComparator(
                    repo_path=None,
                    remote_adapter=remote_adapter,
                    remote_repo=remote_repo,
                )
            else:
                # Local comparison
                comparator = BranchComparator(repo_path=self.repo_path)
            
            comparison = comparator.compare_branches(base_branch, head_branch)
            
            # Convert to dict
            return {
                "base_branch": comparison.base_branch,
                "head_branch": comparison.head_branch,
                "commits_ahead": comparison.commits_ahead,
                "commits_behind": comparison.commits_behind,
                "commits": [
                    {
                        "hash": commit.hash,
                        "author": commit.author,
                        "date": commit.date.isoformat() if hasattr(commit.date, 'isoformat') else str(commit.date),
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
                ] if comparison.conflicts else [],
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
