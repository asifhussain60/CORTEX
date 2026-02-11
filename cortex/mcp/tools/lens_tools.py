"""
LENS Analysis MCP Tools.

Exposes CORTEX LENS analyzers as MCP tools for SaaS deployment.

MCP Tools:
- cortex_lens_analyze: Unified LENS analysis
- cortex_git_history: Git history analysis (24h context)
- cortex_ast_analyze: AST structure analysis
- cortex_extract_comments: Comment/TODO extraction
- cortex_detect_duplicates: CORE-035 duplicate detection

Author: Asif Hussain
ARCH-007: MCP-first architecture enforcement
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.mcp.decorators import mcp_tool


@mcp_tool(
    name="cortex_lens_analyze",
    description="Unified LENS code intelligence analysis combining git, AST, and comments",
    parameters={
        "file_path": "string",
        "repo_path": "string",
        "include_git": "boolean",
        "include_ast": "boolean",
        "include_comments": "boolean",
    }
)
def cortex_lens_analyze(
    file_path: str,
    repo_path: str = ".",
    include_git: bool = True,
    include_ast: bool = True,
    include_comments: bool = True,
) -> Dict[str, Any]:
    """
    Unified LENS analysis for a file.

    Combines GitHistoryAnalyzer, ASTAnalyzer, and CommentExtractor
    into a single analysis result.

    Args:
        file_path: Path to file to analyze
        repo_path: Path to git repository root
        include_git: Include git history analysis
        include_ast: Include AST analysis
        include_comments: Include comment extraction

    Returns:
        Dict with git_analysis, ast_analysis, comment_analysis, metadata
    """
    try:
        from cortex.lens import LENSOrchestrator

        orchestrator = LENSOrchestrator(repo_path=Path(repo_path))

        # Configure which analyzers to run
        context = orchestrator.analyze_file(
            file_path=Path(file_path),
            include_git=include_git,
            include_ast=include_ast,
            include_comments=include_comments,
        )

        return {
            "status": "success",
            "file_path": file_path,
            **context.to_dict(),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "file_path": file_path,
        }


@mcp_tool(
    name="cortex_git_history",
    description="Analyze git commit history for a file or repository (24h context, blame, patterns)",
    parameters={
        "file_path": "string",
        "repo_path": "string",
        "hours": "integer",
        "include_blame": "boolean",
    }
)
def cortex_git_history(
    file_path: Optional[str] = None,
    repo_path: str = ".",
    hours: int = 24,
    include_blame: bool = False,
) -> Dict[str, Any]:
    """
    Analyze git history for ARCH-001 (24h context).

    Args:
        file_path: Optional specific file to analyze
        repo_path: Path to git repository
        hours: Hours of history to analyze (default 24)
        include_blame: Include blame information

    Returns:
        Dict with commits, patterns, blame (if requested)
    """
    try:
        from cortex.lens.analyzers.git_history_analyzer import GitHistoryAnalyzer

        analyzer = GitHistoryAnalyzer(repo_path=Path(repo_path))

        result: Dict[str, Any] = {
            "status": "success",
            "repo_path": repo_path,
            "hours_analyzed": hours,
        }

        # Get recent commits
        commits = analyzer.get_commits_since(hours=hours)
        result["commits"] = [
            {
                "hash": c.hash[:8],
                "message": c.message,
                "author": c.author,
                "timestamp": c.timestamp.isoformat() if hasattr(c.timestamp, 'isoformat') else str(c.timestamp),
            }
            for c in commits
        ]
        result["commit_count"] = len(commits)

        # Get blame if requested and file provided
        if include_blame and file_path:
            blame = analyzer.get_blame(Path(file_path))
            result["blame"] = blame

        # Detect patterns
        if commits:
            patterns = analyzer.detect_intent_patterns(commits)
            result["patterns"] = patterns

        return result
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


@mcp_tool(
    name="cortex_ast_analyze",
    description="Analyze Python AST structure, complexity, and dead code",
    parameters={
        "file_path": "string",
        "include_complexity": "boolean",
        "include_dead_code": "boolean",
    }
)
def cortex_ast_analyze(
    file_path: str,
    include_complexity: bool = True,
    include_dead_code: bool = True,
) -> Dict[str, Any]:
    """
    AST analysis for ARCH-002 (enhance request).

    Args:
        file_path: Path to Python file
        include_complexity: Calculate complexity metrics
        include_dead_code: Detect potential dead code

    Returns:
        Dict with functions, classes, complexity, dead_code
    """
    try:
        from cortex.lens.analyzers.ast_analyzer import ASTAnalyzer

        analyzer = ASTAnalyzer()

        result: Dict[str, Any] = {
            "status": "success",
            "file_path": file_path,
        }

        # Extract structure
        file_path_obj = Path(file_path)
        if file_path_obj.exists():
            code = file_path_obj.read_text(encoding="utf-8")

            functions = analyzer.extract_functions(code)
            result["functions"] = [
                {"name": f.name, "line": f.line_number, "args": len(f.arguments)}
                for f in functions
            ]
            result["function_count"] = len(functions)

            classes = analyzer.extract_classes(code)
            result["classes"] = [
                {"name": c.name, "line": c.line_number, "methods": len(c.methods)}
                for c in classes
            ]
            result["class_count"] = len(classes)

            if include_complexity:
                complexity = analyzer.calculate_complexity(code)
                result["complexity"] = complexity

            if include_dead_code:
                dead_code = analyzer.detect_dead_code(code)
                result["dead_code"] = dead_code
        else:
            result["status"] = "error"
            result["error"] = f"File not found: {file_path}"

        return result
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "file_path": file_path,
        }


@mcp_tool(
    name="cortex_extract_comments",
    description="Extract comments, TODOs, FIXMEs, and docstrings from Python files",
    parameters={
        "file_path": "string",
        "include_docstrings": "boolean",
    }
)
def cortex_extract_comments(
    file_path: str,
    include_docstrings: bool = True,
) -> Dict[str, Any]:
    """
    Comment extraction for ARCH-002 (enhance request).

    Args:
        file_path: Path to Python file
        include_docstrings: Include docstring analysis

    Returns:
        Dict with todos, fixmes, comments, docstrings
    """
    try:
        from cortex.lens.analyzers.comment_extractor import CommentExtractor

        extractor = CommentExtractor()

        result: Dict[str, Any] = {
            "status": "success",
            "file_path": file_path,
        }

        file_path_obj = Path(file_path)
        if file_path_obj.exists():
            code = file_path_obj.read_text(encoding="utf-8")

            # Extract TODOs and FIXMEs
            todos = extractor.extract_todos(code)
            result["todos"] = [
                {"line": t.line_number, "text": t.text, "priority": t.priority}
                for t in todos
            ]

            fixmes = extractor.extract_fixmes(code)
            result["fixmes"] = [
                {"line": f.line_number, "text": f.text, "priority": f.priority}
                for f in fixmes
            ]

            if include_docstrings:
                docstrings = extractor.extract_docstrings(code)
                result["docstrings"] = docstrings
                result["docstring_coverage"] = extractor.calculate_coverage(code)

            result["total_comments"] = len(todos) + len(fixmes)
        else:
            result["status"] = "error"
            result["error"] = f"File not found: {file_path}"

        return result
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "file_path": file_path,
        }


@mcp_tool(
    name="cortex_detect_duplicates",
    description="Detect CORE-035 duplicate code violations",
    parameters={
        "paths": "list",
        "threshold": "number",
    }
)
def cortex_detect_duplicates(
    paths: Optional[List[str]] = None,
    threshold: float = 0.8,
) -> Dict[str, Any]:
    """
    Duplicate detection for CORE-035 enforcement.

    Args:
        paths: List of paths to scan (default: cortex/, cortex_brain/)
        threshold: Similarity threshold (0.0-1.0)

    Returns:
        Dict with duplicates, violation_count, canonical_locations
    """
    try:
        from cortex.tools.duplicate_detector import DuplicateDetector
        from pathlib import Path as PathLib

        detector = DuplicateDetector(workspace_root=PathLib("."))

        result: Dict[str, Any] = {
            "status": "success",
            "paths_scanned": paths or ["cortex/", "cortex_brain/"],
            "threshold": threshold,
        }

        duplicates = detector.detect_all_duplicates()

        result["duplicates"] = [
            {
                "class_name": d.class_name,
                "paths": [str(p) for p in d.paths],
                "violation_type": d.violation_type,
                "severity": d.severity,
                "action": "consolidate",
            }
            for d in duplicates
        ]
        result["violation_count"] = len(duplicates)

        return result
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


@mcp_tool(
    name="cortex_tools_catalog",
    description="Discover all MCP tools registered in CORTEX",
    parameters={}
)
def cortex_tools_catalog() -> Dict[str, Any]:
    """
    Tool discovery for MCP catalog.

    Returns:
        Dict with all registered MCP tools and their metadata
    """
    try:
        from cortex.mcp.mcp_tools_catalog import MCPToolsCatalog

        catalog = MCPToolsCatalog.instance()

        tools = catalog.list_tools()

        return {
            "status": "success",
            "tool_count": len(tools),
            "tools": [t.to_dict() for t in tools],
            "categories": catalog.list_categories(),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


@mcp_tool(
    name="cortex_vision_analyze",
    description="Analyze images via Vision API for UI elements, URLs, issues, and structural mappings",
    parameters={
        "image_data": "string",
        "image_url": "string",
        "image_type": "string",
        "analysis_depth": "string",
        "extract_urls": "boolean",
        "extract_elements": "boolean",
        "detect_issues": "boolean",
    }
)
def cortex_vision_analyze(
    image_data: Optional[str] = None,
    image_url: Optional[str] = None,
    image_type: str = "unknown",
    analysis_depth: str = "standard",
    extract_urls: bool = True,
    extract_elements: bool = True,
    detect_issues: bool = True,
) -> Dict[str, Any]:
    """
    Analyze images via Vision API.

    Extracts UI elements, URLs, issues, and structural information
    from screenshots, diagrams, mockups, and error messages.

    Args:
        image_data: Base64-encoded image data (provide this OR image_url)
        image_url: URL to image (provide this OR image_data)
        image_type: Type of image (screenshot/diagram/mockup/error/unknown)
        analysis_depth: Depth of analysis (quick/standard/thorough)
        extract_urls: Extract URLs from image
        extract_elements: Extract UI elements (buttons, inputs, etc.)
        detect_issues: Detect visual bugs, accessibility issues, errors

    Returns:
        Dict with urls, ui_elements, issues, text_content, structural_map
    """
    try:
        from cortex.brain.analysis.vision_analyzer import (
            AnalysisDepth,
            ImageType,
            VisionAnalyzer,
        )

        if not image_data and not image_url:
            return {
                "status": "error",
                "error": "Must provide either image_data (base64) or image_url",
            }

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
        if image_data:
            result = analyzer.analyze_base64(
                image_data=image_data,
                image_type=img_type,
                depth=depth,
                extract_urls=extract_urls,
                extract_elements=extract_elements,
                detect_issues=detect_issues,
            )
        else:
            result = analyzer.analyze_url(
                image_url=image_url,
                image_type=img_type,
                depth=depth,
                extract_urls=extract_urls,
                extract_elements=extract_elements,
                detect_issues=detect_issues,
            )

        return result.to_dict()

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


# Export all tools for registration
__all__ = [
    "cortex_lens_analyze",
    "cortex_git_history",
    "cortex_ast_analyze",
    "cortex_extract_comments",
    "cortex_detect_duplicates",
    "cortex_tools_catalog",
    "cortex_vision_analyze",
]
