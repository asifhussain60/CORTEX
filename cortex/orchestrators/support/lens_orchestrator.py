"""
LENS Orchestrator for CORTEX.

Unified orchestrator coordinating GitHistoryAnalyzer, ASTAnalyzer, 
and CommentExtractor for the LENS (Language→Examination→Navigation→Synthesis)
intelligence cycle.

Provides:
- Unified code intelligence API
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


@dataclass
class LENSContext:
    """
    Unified LENS intelligence context.
    
    Compatible with IntentRouter's lens_context parameter (LENS-002).
    
    Attributes:
        git_analysis: Git commit history and patterns
        ast_analysis: AST structure and complexity
        comment_analysis: Comments, TODOs, and docstrings
        metadata: Analysis metadata (timing, cache hits, etc.)
    """
    git_analysis: Dict[str, Any] = field(default_factory=dict)
    ast_analysis: Dict[str, Any] = field(default_factory=dict)
    comment_analysis: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for IntentRouter compatibility."""
        return {
            "git_analysis": self.git_analysis,
            "ast_analysis": self.ast_analysis,
            "comment_analysis": self.comment_analysis,
            "_metadata": self.metadata,
        }


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
