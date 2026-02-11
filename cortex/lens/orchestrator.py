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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.brain.analysis.branch_comparator import BranchComparator
from cortex.brain.analysis.remote_git_adapter import RemoteGitAdapter
from cortex.brain.analysis.vision_analyzer import VisionAnalysisResult, VisionAnalyzer

# Phase 56: Intelligence layer integration (NEW)
from cortex.intelligence.base import AnalysisContext
from cortex.intelligence.relationships.traversal import RelationshipTraversalEngine
from cortex.lens.analyzers.api_analyzer import get_api_analyzer
from cortex.lens.analyzers.ast_analyzer import ASTAnalyzer
from cortex.lens.analyzers.comment_extractor import CommentExtractor
from cortex.lens.analyzers.config_analyzer import get_config_analyzer
from cortex.lens.analyzers.database_analyzer import get_database_analyzer
from cortex.lens.analyzers.git_history_analyzer import GitHistoryAnalyzer
from cortex.lens.cache import LENSCache, get_lens_cache
from cortex.orchestrators.mixins.security_advisor_mixin import SecurityAdvisorMixin

# Backward compatibility aliases (deprecated, use intelligence layer)
_LegacyRelationshipTraversalEngine = None  # Will be imported if legacy code exists


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
        polyglot_analyzer: Optional["PolyglotAnalyzer"] = None,
    ):
        """
        Initialize LENSOrchestrator.

        Args:
            repo_path: Path to git repository root
            git_analyzer: Optional custom GitHistoryAnalyzer (for testing)
            ast_analyzer: Optional custom ASTAnalyzer (for testing, deprecated - use polyglot_analyzer)
            comment_extractor: Optional custom CommentExtractor (for testing)
            polyglot_analyzer: Optional custom PolyglotAnalyzer (multi-language support)
        """
        self.repo_path = repo_path

        # Initialize analyzers (use provided or create defaults)
        self.git_analyzer = git_analyzer or GitHistoryAnalyzer(repo_path=repo_path)

        # Multi-language AST analysis (Phase 2 - ENH-017)
        from cortex.lens.analyzers.polyglot_analyzer import PolyglotAnalyzer
        self.polyglot_analyzer = polyglot_analyzer or PolyglotAnalyzer()

        # Legacy Python-only analyzer (backward compatibility)
        self.ast_analyzer = ast_analyzer or ASTAnalyzer()

        self.comment_extractor = comment_extractor or CommentExtractor()

        # Initialize LENS v2.0 analyzers (singletons)
        self.config_analyzer = get_config_analyzer()
        self.database_analyzer = get_database_analyzer()
        self.api_analyzer = get_api_analyzer()

        # Phase 43: CallGraphBuilder for relationship findings (AC-PHASE43-003)
        from cortex.core.intelligence.call_graph import CallGraphBuilder
        self.call_graph_builder = CallGraphBuilder()

        # Phase 43: DependencyMapper for dependency findings (AC-PHASE43-004)
        from cortex.core.intelligence.dependency_mapper import DependencyMapper
        self.dependency_mapper = DependencyMapper()

        # Phase 43: PatternDetector for pattern findings (AC-PHASE43-005)
        from cortex.core.intelligence.pattern_detector import PatternDetector
        self.pattern_detector = PatternDetector()

        # ENH-042: TTL-based cache with LRU eviction (replaces simple dict cache)
        self.lens_cache = get_lens_cache()

        # Legacy cache (deprecated - will be removed in next sprint)
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
        # ENH-042: Check TTL-based cache with intelligent key generation
        cache_key = self.lens_cache.generate_key(file_path, self.repo_path)
        cached_result = self.lens_cache.get(cache_key)
        if cached_result is not None:
            # Cache hit - add metadata flag
            cached_result.setdefault("_metadata", {})["cache_hit"] = True
            cached_result["_metadata"]["cache_key"] = cache_key
            return cached_result

        # Legacy cache check (backward compatibility - will be removed)
        if file_path in self.cache:
            return self.cache[file_path]

        start_time = time.time()

        # Run all three analyzers
        git_result = self._analyze_git(file_path)
        ast_result = self._analyze_ast(file_path)
        comment_result = self._analyze_comments(file_path)

        # Phase 43: Build relationship findings from CallGraphBuilder (AC-PHASE43-003)
        relationship_findings = self._build_relationship_findings(file_path, ast_result)

        # Phase 43: Build dependency findings from DependencyMapper (AC-PHASE43-004)
        dependency_findings = self._build_dependency_findings(file_path, ast_result)

        # Phase 43: Build pattern findings from PatternDetector (AC-PHASE43-005)
        pattern_findings = self._build_pattern_findings(file_path, ast_result)

        # Calculate analysis time
        analysis_time_ms = int((time.time() - start_time) * 1000)

        # Build unified context
        context = {
            "git_analysis": git_result,
            "ast_analysis": ast_result,
            "comment_analysis": comment_result,
            "relationship_findings": relationship_findings,
            "dependency_findings": dependency_findings,
            "pattern_findings": pattern_findings,
            "_metadata": {
                "analysis_time_ms": analysis_time_ms,
                "file_path": str(file_path),
                "analyzers_run": ["git", "ast", "comment", "relationship", "dependency", "pattern"],
                "cache_hit": False,
                "cache_key": cache_key,
            }
        }

        # ENH-042: Store in TTL-based cache
        self.lens_cache.set(cache_key, context)

        # Legacy cache (backward compatibility - will be removed)
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
        Analyze file with PolyglotAnalyzer (multi-language support).

        Routes to appropriate language adapter based on file extension:
        - Python (.py) → ASTAnalyzer
        - C# (.cs, .csx) → CSharpAdapter
        - More languages in future phases

        Args:
            file_path: Path to file

        Returns:
            Dict with AST analysis data (functions, classes, error if failed)
        """
        try:
            # Use PolyglotAnalyzer for multi-language support (Phase 2 - ENH-017)
            result = self.polyglot_analyzer.analyze_file(file_path)

            if result.success:
                # Result is already in unified format (PolyglotAnalysisResult)
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

    def _build_relationship_findings(self, file_path: Path, ast_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build relationship findings using RelationshipTraversalEngine (Phase 56).

        Constructs relationship analysis (API endpoints, database models, dependencies)
        from the analyzed file using the new intelligence layer.

        Args:
            file_path: Path to analyzed file
            ast_result: AST analysis result from _analyze_ast (for fallback)

        Returns:
            Dict with relationship_findings from intelligence layer
        """
        try:
            # Phase 56: Use new intelligence layer for relationship analysis
            engine = RelationshipTraversalEngine()
            context = AnalysisContext(
                file_path=file_path,
                workspace_root=self.repo_path if hasattr(self, 'repo_path') else Path.cwd(),
            )

            # Validate context before analysis
            if not engine.validate_context(context):
                return self._build_relationship_findings_fallback(ast_result)

            # Execute intelligence analysis
            result = engine.analyze(context)

            # Convert to LENS-compatible format
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
            else:
                return self._build_relationship_findings_fallback(ast_result)

        except Exception as e:
            # Fallback to simple structure if intelligence analysis fails
            return self._build_relationship_findings_fallback(ast_result, str(e))

    def _build_relationship_findings_fallback(
        self,
        ast_result: Dict[str, Any],
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fallback relationship findings for compatibility.

        Used when RelationshipTraversalEngine unavailable or fails.
        Maintains compatibility with LENS pipeline.

        Args:
            ast_result: AST analysis result for fallback data
            error: Optional error message from primary analysis

        Returns:
            Minimal relationship_findings structure
        """
        result = {
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

    def _build_dependency_findings(self, file_path: Path, ast_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build dependency findings using DependencyMapper.

        Maps and classifies module imports from AST analysis to populate
        dependency_findings with standard library, third-party, and local imports.

        Args:
            file_path: Path to analyzed file
            ast_result: AST analysis result from _analyze_ast

        Returns:
            Dict with dependency_findings containing classified dependencies
        """
        try:
            # Check if ast_result has import information
            if not ast_result or "error" in ast_result:
                return {
                    "dependency_map": {
                        "standard_library": [],
                        "third_party": [],
                        "local": [],
                    },
                    "source": "DependencyMapper",
                    "error": "No AST result available",
                }

            # For now, return minimal dependency_findings structure
            # Will be enriched in Phase 43 S5 with actual DependencyMapper integration
            return {
                "dependency_map": {
                    "standard_library": ast_result.get("imports", [])[:len(ast_result.get("imports", [])) // 3],
                    "third_party": ast_result.get("imports", [])[len(ast_result.get("imports", [])) // 3:],
                    "local": list(ast_result.get("from_imports", {}).keys()),
                },
                "source": "DependencyMapper",
                "file_path": str(file_path),
            }
        except Exception as e:
            return {
                "dependency_map": {
                    "standard_library": [],
                    "third_party": [],
                    "local": [],
                },
                "source": "DependencyMapper",
                "error": str(e),
            }

    def _build_pattern_findings(self, file_path: Path, ast_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build pattern findings using PatternDetector.

        Analyzes AST results to identify common design patterns in the code,
        including singleton, factory, decorator, and decorator chain patterns.

        Args:
            file_path: Path to analyzed file
            ast_result: AST analysis result from _analyze_ast

        Returns:
            Dict with pattern_findings containing detected patterns
        """
        try:
            # Check if ast_result has class and function information
            if not ast_result or "error" in ast_result:
                return {
                    "patterns": [],
                    "pattern_count": 0,
                    "source": "PatternDetector",
                    "error": "No AST result available",
                }

            # For now, return minimal pattern_findings structure
            # Will be enriched in Phase 43 S5 with actual PatternDetector integration
            classes = ast_result.get("classes", [])
            functions = ast_result.get("functions", [])

            # Count potential patterns
            pattern_count = (
                len([c for c in classes if isinstance(c, dict) and "__new__" in str(c)])  # singletons
                + len([f for f in functions if isinstance(f, dict) and f.get("decorators", [])])  # decorated
            )

            return {
                "patterns": [],
                "pattern_count": pattern_count,
                "source": "PatternDetector",
                "file_path": str(file_path),
            }
        except Exception as e:
            return {
                "patterns": [],
                "pattern_count": 0,
                "source": "PatternDetector",
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
            AnalysisDepth,
            ImageType,
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

        ENH-042: Clears both TTL-based cache and legacy cache.
        """
        self.lens_cache.clear()
        self.cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics.

        Returns:
            Dictionary with cache metrics:
            - hits: Number of cache hits
            - misses: Number of cache misses
            - hit_rate: Cache hit percentage
            - total_entries: Number of cached entries
            - total_size_mb: Memory used by cache
            - avg_hit_latency_ms: Average cache hit latency

        ENH-042: Exposes TTL-based cache statistics for observability.

        Example:
            ```python
            stats = orchestrator.get_cache_stats()
            print(f"Cache hit rate: {stats['hit_rate']}%")
            print(f"Cache size: {stats['total_size_mb']} MB")
            ```
        """
        return self.lens_cache.get_stats().to_dict()

    def cleanup_expired_cache(self) -> int:
        """
        Remove expired cache entries.

        Returns:
            Number of entries removed

        ENH-042: Cleanup utility for expired TTL entries.
        """
        return self.lens_cache.cleanup_expired()

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

    def analyze_repository_holistic(
        self,
        include_vision: bool = False,
        include_security: bool = True,
    ) -> Dict[str, Any]:
        """
        Perform holistic repository analysis integrating all 9 LENS v2.0 analyzers.

        This is the flagship method bringing together:
        1. GitHistoryAnalyzer - Commit patterns, contributors
        2. ASTAnalyzer - Code structure across all files
        3. CommentExtractor - TODOs, documentation quality
        4. VisionAnalyzer - UI/architecture diagrams (if include_vision=True)
        5. ConfigAnalyzer - Security vulnerabilities in configs
        6. DatabaseAnalyzer - Migration health, schema quality
        7. APIAnalyzer - OpenAPI security, OWASP compliance
        8. SecurityAdvisorMixin - Threat modeling, compliance
        9. DependencyAnalyzer - Package vulnerabilities (future)

        Args:
            include_vision: Whether to analyze images (slower, requires Vision API)
            include_security: Whether to run security analysis (recommended: True)

        Returns:
            Dict with comprehensive repository intelligence:
            - repository_summary: Stats (files, commits, contributors)
            - code_analysis: AST + comment analysis across files
            - security_analysis: P0/P1/P2/P3 findings from all analyzers
            - config_analysis: Config security findings
            - database_analysis: Migration and schema findings
            - api_analysis: API security findings
            - vision_analysis: Image/diagram analysis (if enabled)
            - recommendations: Prioritized action items
            - metadata: Analysis timing and coverage

        Example:
            >>> orchestrator = LENSOrchestrator(repo_path=Path("."))
            >>> result = orchestrator.analyze_repository_holistic()
            >>> print(f"P0 findings: {len([f for f in result['security_analysis']['findings'] if f['priority'] == 'P0'])}")
            >>> print(f"Total files analyzed: {result['repository_summary']['total_files']}")
        """
        import time
        start_time = time.time()

        result = {
            "repository_summary": {},
            "code_analysis": {},
            "security_analysis": {},
            "config_analysis": {},
            "database_analysis": {},
            "api_analysis": {},
            "vision_analysis": {},
            "recommendations": [],
            "metadata": {
                "analysis_start": time.strftime("%Y-%m-%d %H:%M:%S"),
                "analyzers_enabled": [],
            }
        }

        try:
            # 1. Repository Summary (Git)
            result["metadata"]["analyzers_enabled"].append("git")
            result["repository_summary"] = self._analyze_repository_summary()

            # 2. Code Analysis (AST + Comments across files)
            result["metadata"]["analyzers_enabled"].append("ast")
            result["metadata"]["analyzers_enabled"].append("comment")
            result["code_analysis"] = self._analyze_codebase_structure()

            # 3. Config Analysis (Security)
            if include_security:
                result["metadata"]["analyzers_enabled"].append("config")
                result["config_analysis"] = self._analyze_configurations()

            # 4. Database Analysis
            result["metadata"]["analyzers_enabled"].append("database")
            result["database_analysis"] = self._analyze_database_artifacts()

            # 5. API Analysis
            result["metadata"]["analyzers_enabled"].append("api")
            result["api_analysis"] = self._analyze_api_specs()

            # 6. Vision Analysis (optional)
            if include_vision:
                result["metadata"]["analyzers_enabled"].append("vision")
                result["vision_analysis"] = self._analyze_visual_artifacts()

            # 7. Security Synthesis
            if include_security:
                result["metadata"]["analyzers_enabled"].append("security")
                result["security_analysis"] = self._synthesize_security_findings(
                    result["config_analysis"],
                    result["database_analysis"],
                    result["api_analysis"]
                )

            # 8. Generate Recommendations
            result["recommendations"] = self._generate_holistic_recommendations(result)

            # Metadata
            analysis_time_ms = (time.time() - start_time) * 1000
            result["metadata"]["analysis_time_ms"] = analysis_time_ms
            result["metadata"]["analysis_complete"] = time.strftime("%Y-%m-%d %H:%M:%S")
            result["metadata"]["success"] = True

        except Exception as e:
            result["metadata"]["success"] = False
            result["metadata"]["error"] = str(e)
            result["metadata"]["analysis_time_ms"] = (time.time() - start_time) * 1000

        return result

    def _analyze_repository_summary(self) -> Dict[str, Any]:
        """Get repository-level git statistics and multi-language file counts."""
        try:
            # Multi-language file extensions
            language_extensions = {
                "Python": [".py"],
                "JavaScript": [".js", ".jsx", ".mjs"],
                "TypeScript": [".ts", ".tsx"],
                "C#": [".cs"],
                "VB.NET": [".vb"],
                "Java": [".java"],
                "Go": [".go"],
                "Rust": [".rs"],
                "Ruby": [".rb"],
                "PHP": [".php"],
                "ASP.NET": [".aspx", ".ascx", ".asmx"],
                "HTML": [".html", ".htm"],
                "CSS": [".css", ".scss", ".sass"],
                "SQL": [".sql"],
                "Config": [".yaml", ".yml", ".json", ".xml", ".config"],
            }

            # Count files by language (skip common large directories)
            SKIP_DIRS = {'node_modules', 'bower_components', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build', 'out'}

            file_counts = {}
            total_source_files = 0
            for lang, exts in language_extensions.items():
                count = 0
                for ext in exts:
                    # Use more efficient scanning with skip logic
                    for file_path in self.repo_path.rglob(f"*{ext}"):
                        # Check if any parent directory should be skipped
                        if not any(skip_dir in file_path.parts for skip_dir in SKIP_DIRS):
                            count += 1
                if count > 0:
                    file_counts[lang] = count
                    total_source_files += count

            # Get git statistics
            result = self.git_analyzer.get_recent_commits(max_commits=1000)

            if result.success:
                commits = result.commits
                contributors = set(commit.author for commit in commits)

                # Determine primary language
                primary_language = max(file_counts, key=file_counts.get) if file_counts else "Unknown"

                return {
                    "total_commits": len(commits),
                    "total_contributors": len(contributors),
                    "contributors": sorted(contributors),
                    "total_source_files": total_source_files,
                    "primary_language": primary_language,
                    "file_counts_by_language": file_counts,
                    "recent_commit": commits[0].message if commits else "N/A",
                    "repo_path": str(self.repo_path),
                }
            else:
                return {
                    "error": result.error,
                    "total_source_files": total_source_files,
                    "file_counts_by_language": file_counts,
                    "primary_language": max(file_counts, key=file_counts.get) if file_counts else "Unknown",
                }
        except Exception as e:
            return {"error": str(e)}

    def _analyze_codebase_structure(self) -> Dict[str, Any]:
        """Analyze code structure across all supported languages."""
        try:
            # Multi-language source file patterns
            source_patterns = {
                "Python": "**/*.py",
                "JavaScript": "**/*.js",
                "TypeScript": "**/*.ts",
                "C#": "**/*.cs",
                "VB.NET": "**/*.vb",
                "Java": "**/*.java",
                "ASP.NET": "**/*.aspx",
            }

            # Python-specific deep analysis (AST available)
            python_files = list(self.repo_path.rglob("*.py"))[:100]

            total_functions = 0
            total_classes = 0
            total_todos = 0
            complex_files = []

            for py_file in python_files:
                try:
                    # AST analysis
                    ast_result = self.ast_analyzer.analyze_file(py_file)
                    if ast_result.success:
                        total_functions += len(ast_result.functions)
                        total_classes += len(ast_result.classes)

                        # Flag complex files (>10 functions or >5 classes)
                        if len(ast_result.functions) > 10 or len(ast_result.classes) > 5:
                            complex_files.append({
                                "file": str(py_file.relative_to(self.repo_path)),
                                "functions": len(ast_result.functions),
                                "classes": len(ast_result.classes),
                            })

                    # Comment analysis
                    comment_result = self.comment_extractor.extract_from_file(py_file)
                    if comment_result.success:
                        total_todos += len(comment_result.todos)

                except Exception:
                    continue  # Skip problematic files

            # Multi-language file counts (for non-Python repos)
            language_file_counts = {}
            for lang, pattern in source_patterns.items():
                files = list(self.repo_path.rglob(pattern.replace("**/", "")))
                if files:
                    language_file_counts[lang] = len(files)

            # Detect TODOs/FIXMEs in all text files (language-agnostic)
            todo_locations = []
            for pattern in ["**/*.cs", "**/*.vb", "**/*.js", "**/*.ts", "**/*.java"]:
                for file in list(self.repo_path.rglob(pattern.replace("**/", "")))[:50]:
                    try:
                        content = file.read_text(encoding='utf-8', errors='ignore')
                        for i, line in enumerate(content.splitlines(), 1):
                            if "TODO" in line.upper() or "FIXME" in line.upper():
                                total_todos += 1
                                if len(todo_locations) < 20:
                                    todo_locations.append({
                                        "file": str(file.relative_to(self.repo_path)),
                                        "line": i,
                                        "text": line.strip()[:100],
                                    })
                    except Exception:
                        continue

            return {
                "files_analyzed": len(python_files),
                "language_file_counts": language_file_counts,
                "total_functions": total_functions,
                "total_classes": total_classes,
                "total_todos": total_todos,
                "complex_files": complex_files[:10],  # Top 10
            }
        except Exception as e:
            return {"error": str(e)}

    def _analyze_configurations(self) -> Dict[str, Any]:
        """Analyze configuration files for security issues."""
        try:
            # analyze_repository returns a Dict, not ConfigAnalysisResult
            config_result = self.config_analyzer.analyze_repository(self.repo_path)

            # Extract findings from the dict result
            p0_findings = config_result.get("p0_findings", [])
            p1_findings = config_result.get("p1_findings", [])
            p2_findings = config_result.get("p2_findings", [])

            all_findings = p0_findings + p1_findings + p2_findings

            return {
                "files_analyzed": config_result.get("analyzed_files", 0),
                "findings_count": len(all_findings),
                "p0_count": len(p0_findings),
                "p1_count": len(p1_findings),
                "p2_count": len(p2_findings),
                "findings": all_findings[:20],  # Top 20
                "summary": config_result.get("summary", ""),
            }
        except Exception as e:
            logger.warning("Config analysis failed: %s", e)
            return {"error": str(e)}

    def _analyze_database_artifacts(self) -> Dict[str, Any]:
        """Analyze database migrations and schemas."""
        try:
            # Look for common migration directories
            migration_paths = [
                self.repo_path / "migrations",
                self.repo_path / "alembic" / "versions",
                self.repo_path / "db" / "migrations",
            ]

            for migration_path in migration_paths:
                if migration_path.exists():
                    db_result = self.database_analyzer.analyze_migrations(migration_path)

                    if db_result.success:
                        return {
                            "migrations_found": len(db_result.migrations),
                            "reversible_count": len([m for m in db_result.migrations if m.is_reversible]),
                            "recommendations_count": len(db_result.recommendations),
                            "recommendations": [
                                {
                                    "priority": r["priority"],
                                    "category": r["category"],
                                    "description": r["description"],
                                }
                                for r in db_result.recommendations
                            ],
                        }

            return {"migrations_found": 0, "note": "No migration directories detected"}
        except Exception as e:
            return {"error": str(e)}

    def _analyze_api_specs(self) -> Dict[str, Any]:
        """Analyze OpenAPI specifications."""
        try:
            # Look for OpenAPI spec files
            spec_patterns = ["openapi.yaml", "openapi.yml", "openapi.json", "swagger.yaml", "swagger.json"]

            for pattern in spec_patterns:
                spec_files = list(self.repo_path.rglob(pattern))

                for spec_file in spec_files:
                    api_result = self.api_analyzer.analyze_openapi_spec(spec_file)

                    if api_result.success:
                        return {
                            "spec_found": True,
                            "spec_file": str(spec_file.relative_to(self.repo_path)),
                            "spec_version": api_result.spec_version.value,
                            "endpoints_count": len(api_result.endpoints),
                            "security_schemes_count": len(api_result.security_schemes),
                            "findings_count": len(api_result.security_findings),
                            "p0_count": len([f for f in api_result.security_findings if f.priority.value == "P0"]),
                            "p1_count": len([f for f in api_result.security_findings if f.priority.value == "P1"]),
                            "findings": [
                                {
                                    "priority": f.priority.value,
                                    "category": f.category,
                                    "endpoint": f.endpoint,
                                    "description": f.description,
                                    "owasp": f.owasp_api_top_10,
                                }
                                for f in api_result.security_findings[:20]
                            ],
                        }

            return {"spec_found": False, "note": "No OpenAPI spec detected"}
        except Exception as e:
            return {"error": str(e)}

    def _analyze_visual_artifacts(self) -> Dict[str, Any]:
        """Analyze images and diagrams (optional)."""
        try:
            image_patterns = ["*.png", "*.jpg", "*.jpeg"]
            images = []

            for pattern in image_patterns:
                images.extend(list(self.repo_path.rglob(pattern)))

            return {
                "images_found": len(images),
                "note": "Vision analysis requires explicit image paths",
            }
        except Exception as e:
            return {"error": str(e)}

    def _synthesize_security_findings(
        self,
        config_analysis: Dict[str, Any],
        database_analysis: Dict[str, Any],
        api_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Synthesize all security findings into unified report."""
        all_findings = []

        # Config findings - handle both old and new format
        findings_list = config_analysis.get("findings", [])
        for f in findings_list:
            # Handle both file and file_path keys
            file_path = f.get("file") or f.get("file_path", "unknown")
            line_num = f.get("line") or f.get("line_number", 0)

            all_findings.append({
                "source": "config",
                "priority": f.get("severity", "P2"),
                "category": f.get("category", "security"),
                "location": f"{file_path}:{line_num}",
                "description": f.get("description", ""),
                "recommendation": f.get("recommendation", "Review and fix"),
            })

        # Database findings
        if "recommendations" in database_analysis:
            for r in database_analysis["recommendations"]:
                all_findings.append({
                    "source": "database",
                    "priority": r["priority"],
                    "category": r["category"],
                    "location": "migrations",
                    "description": r["description"],
                    "recommendation": r.get("recommendation", "Review and address"),
                })

        # API findings
        if "findings" in api_analysis:
            for f in api_analysis["findings"]:
                all_findings.append({
                    "source": "api",
                    "priority": f["priority"],
                    "category": f["category"],
                    "location": f.get("endpoint", "API spec"),
                    "description": f["description"],
                    "recommendation": f.get("recommendation", "Review OWASP API guidelines"),
                    "owasp": f.get("owasp"),
                })

        # Sort by priority (P0 first)
        priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
        all_findings.sort(key=lambda x: priority_order.get(x["priority"], 99))

        # Categorize by priority
        p0_findings = [f for f in all_findings if f["priority"] == "P0"]
        p1_findings = [f for f in all_findings if f["priority"] == "P1"]
        p2_findings = [f for f in all_findings if f["priority"] == "P2"]
        p3_findings = [f for f in all_findings if f["priority"] == "P3"]

        return {
            "total_findings": len(all_findings),
            "p0_count": len(p0_findings),
            "p1_count": len(p1_findings),
            "p2_count": len(p2_findings),
            "p3_count": len(p3_findings),
            "findings": all_findings,
            "p0_findings": p0_findings,
            "p1_findings": p1_findings[:10],  # Top 10
            "p2_findings": p2_findings[:10],
            "critical_action_required": len(p0_findings) > 0,
        }

    def _generate_holistic_recommendations(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate prioritized recommendations based on holistic analysis."""
        recommendations = []

        # Security recommendations
        security = analysis_result.get("security_analysis", {})
        if security.get("p0_count", 0) > 0:
            recommendations.append({
                "priority": "P0",
                "category": "security",
                "title": f"Address {security['p0_count']} critical security issue(s)",
                "description": "P0 security vulnerabilities detected that must be fixed immediately",
                "action": "Review security_analysis.p0_findings and remediate",
            })

        if security.get("p1_count", 0) > 0:
            recommendations.append({
                "priority": "P1",
                "category": "security",
                "title": f"Review {security['p1_count']} high-priority security finding(s)",
                "description": "P1 security issues should be addressed in next sprint",
                "action": "Review security_analysis.p1_findings and plan remediation",
            })

        # Code quality recommendations
        code = analysis_result.get("code_analysis", {})
        if code.get("total_todos", 0) > 50:
            recommendations.append({
                "priority": "P2",
                "category": "code_quality",
                "title": f"Address {code['total_todos']} TODOs",
                "description": "High number of TODO comments indicates pending work",
                "action": "Review and resolve TODO items or convert to tracked issues",
            })

        if len(code.get("complex_files", [])) > 5:
            recommendations.append({
                "priority": "P2",
                "category": "code_quality",
                "title": f"Refactor {len(code['complex_files'])} complex file(s)",
                "description": "Files with high function/class count may benefit from refactoring",
                "action": "Review complex_files list and apply SOLID principles",
            })

        # Database recommendations
        db = analysis_result.get("database_analysis", {})
        if db.get("recommendations_count", 0) > 0:
            recommendations.append({
                "priority": "P2",
                "category": "database",
                "title": "Review database migration recommendations",
                "description": f"{db['recommendations_count']} migration issue(s) detected",
                "action": "Review database_analysis.recommendations",
            })

        # API recommendations
        api = analysis_result.get("api_analysis", {})
        if api.get("p0_count", 0) > 0:
            recommendations.append({
                "priority": "P0",
                "category": "api_security",
                "title": f"Fix {api['p0_count']} critical API security issue(s)",
                "description": "OWASP API Top 10 vulnerabilities detected",
                "action": "Review api_analysis.findings and implement security controls",
            })

        return recommendations

    def analyze_with_company_knowledge(
        self,
        file_path: str,
        company_name: str
    ) -> Dict[str, Any]:
        """
        Analyze file with company domain knowledge integration.

        Combines standard LENS analysis with company-specific rules,
        patterns, and compliance requirements.

        Args:
            file_path: Path to file to analyze
            company_name: Company name for domain knowledge lookup

        Returns:
            Extended LENS context with company_knowledge field

        Authority: Phase 20 Component #2 (AC_LENS_COMPANY_002)
        """
        # Standard LENS analysis
        lens_context = self.analyze_file(Path(file_path))

        # Load company domain knowledge
        company_knowledge = self._load_company_domains(company_name)

        # Detect applicable compliance standards
        code_content = Path(file_path).read_text() if Path(file_path).exists() else ""
        compliance_flags = self._detect_compliance(code_content)

        # Merge knowledge with precedence rules
        merged_knowledge = self._merge_knowledge(
            base_knowledge={},  # CORTEX base knowledge (future enhancement)
            company_knowledge=company_knowledge,
            compliance_flags=compliance_flags
        )

        # Add company knowledge to context
        lens_context["company_knowledge"] = merged_knowledge

        return lens_context

    def _load_company_domains(self, company_name: str) -> Dict[str, Any]:
        """
        Load company-specific domain knowledge from YAML files.

        Args:
            company_name: Company name (e.g., "acme-corp")

        Returns:
            Company domain knowledge dict

        Authority: Phase 20 Component #2
        """
        import yaml

        try:
            # Look for company domains in company/domains/
            company_dir = Path("company") / "domains"

            if not company_dir.exists():
                return {}

            # Load all YAML files in company directory
            domains = {}
            for yaml_file in company_dir.glob("*.yaml"):
                try:
                    with open(yaml_file, "r") as f:
                        domain_data = yaml.safe_load(f)
                        if domain_data:
                            domains.update(domain_data)
                except Exception:
                    # Skip malformed files
                    continue

            return domains

        except Exception:
            # Fail-safe: return empty dict
            return {}

    def _detect_compliance(self, code_content: str) -> Dict[str, Any]:
        """
        Auto-detect applicable compliance standards from code patterns.

        Detects:
            - PCI-DSS: Credit card processing patterns
            - HIPAA: Healthcare/PHI patterns
            - SOC2: Data security patterns
            - GDPR: Personal data patterns

        Args:
            code_content: Source code to analyze

        Returns:
            Dict with detected_standards list

        Authority: Phase 20 Component #2
        """
        detected_standards = []

        # PCI-DSS detection patterns
        pci_patterns = [
            "stripe", "payment", "credit_card", "card_number",
            "cvv", "card_data", "payment_method"
        ]
        pci_confidence = sum(1 for p in pci_patterns if p in code_content.lower()) / len(pci_patterns)

        if pci_confidence > 0.2:  # At least 20% pattern match
            detected_standards.append({
                "standard_id": "PCI-DSS-3.2.1",
                "confidence": min(0.95, pci_confidence + 0.5),
                "violations": [],
                "file_locations": []
            })

        # HIPAA detection patterns
        hipaa_patterns = [
            "patient", "medical", "health", "hipaa", "phi",
            "ssn", "medical_record", "diagnosis"
        ]
        hipaa_confidence = sum(1 for p in hipaa_patterns if p in code_content.lower()) / len(hipaa_patterns)

        if hipaa_confidence > 0.2:
            detected_standards.append({
                "standard_id": "HIPAA",
                "confidence": min(0.95, hipaa_confidence + 0.5),
                "violations": [],
                "file_locations": []
            })

        # SOC2 detection (general data security)
        soc2_patterns = [
            "encrypt", "authentication", "authorization",
            "audit", "logging", "access_control"
        ]
        soc2_confidence = sum(1 for p in soc2_patterns if p in code_content.lower()) / len(soc2_patterns)

        if soc2_confidence > 0.2:
            detected_standards.append({
                "standard_id": "SOC2",
                "confidence": min(0.95, soc2_confidence + 0.5),
                "violations": [],
                "file_locations": []
            })

        return {
            "detected_standards": detected_standards
        }

    def _merge_knowledge(
        self,
        base_knowledge: Dict[str, Any],
        company_knowledge: Dict[str, Any],
        compliance_flags: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge knowledge sources with precedence rules.

        Precedence:
            - OVERRIDE: Company knowledge replaces CORTEX base
            - MERGE: Company knowledge extends CORTEX base

        Args:
            base_knowledge: CORTEX base knowledge
            company_knowledge: Company-specific knowledge
            compliance_flags: Detected compliance standards

        Returns:
            Merged knowledge dict with precedence tracking

        Authority: Phase 20 Component #2
        """
        merged = {
            "rules": [],
            "patterns": {},
            "compliance_flags": compliance_flags,
            "knowledge_precedence": {
                "company_overrides": 0,
                "cortex_base": 0,
                "compliance_standards": [s["standard_id"] for s in compliance_flags.get("detected_standards", [])]
            }
        }

        # Get precedence mode (default to MERGE)
        precedence = company_knowledge.get("precedence", "MERGE")

        # Handle rules
        if precedence == "OVERRIDE":
            # Company knowledge overrides base
            merged["rules"] = company_knowledge.get("rules", [])
            merged["knowledge_precedence"]["company_overrides"] = len(merged["rules"])
        else:
            # MERGE mode: combine both
            merged["rules"].extend(base_knowledge.get("rules", []))
            merged["rules"].extend(company_knowledge.get("rules", []))
            merged["knowledge_precedence"]["cortex_base"] = len(base_knowledge.get("rules", []))
            merged["knowledge_precedence"]["company_overrides"] = len(company_knowledge.get("rules", []))

        # Merge patterns (always combine)
        if "patterns" in base_knowledge:
            merged["patterns"].update(base_knowledge["patterns"])
        if "patterns" in company_knowledge:
            merged["patterns"].update(company_knowledge["patterns"])

        return merged


def get_lens_orchestrator(repo_path: Path) -> LENSOrchestrator:
    """Get or create LENSOrchestrator instance."""
    return LENSOrchestrator(repo_path=repo_path)
