"""
Discovery Data Models

Core data structures for discovery operations.

Author: Asif Hussain
Version: 1.0.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


class DiscoveryDepth(Enum):
    """Discovery depth levels."""
    QUICK = "quick"          # File metadata only
    MODERATE = "moderate"    # + AST analysis
    FULL = "full"           # + Semantic + Git history


@dataclass
class DiscoveryScope:
    """
    Defines the scope of a discovery operation.
    
    Attributes:
        root_path: Starting directory for discovery
        include_patterns: Glob patterns to include (e.g., ["*.py", "*.cs"])
        exclude_patterns: Glob patterns to exclude (e.g., ["__pycache__", ".git"])
        max_depth: Maximum directory depth to traverse (-1 = unlimited)
        follow_symlinks: Whether to follow symbolic links
        estimated_file_count: Estimated number of files (for progress)
        depth: Discovery depth level
    """
    root_path: Path
    include_patterns: List[str] = field(default_factory=lambda: ["*"])
    exclude_patterns: List[str] = field(default_factory=list)
    max_depth: int = -1
    follow_symlinks: bool = False
    estimated_file_count: int = 0
    depth: DiscoveryDepth = DiscoveryDepth.MODERATE


@dataclass
class FileInfo:
    """
    Metadata for a discovered file.
    
    Attributes:
        path: Absolute path to file
        relative_path: Path relative to discovery root
        language: Detected programming language
        size_bytes: File size in bytes
        line_count: Number of lines
        modified_at: Last modification timestamp
        hash: SHA256 hash of file contents
        encoding: File encoding (e.g., utf-8)
    """
    path: Path
    relative_path: Path
    language: str
    size_bytes: int
    line_count: int
    modified_at: datetime
    hash: str
    encoding: str = "utf-8"


@dataclass
class FileInventory:
    """
    Collection of discovered files with aggregate statistics.
    
    Attributes:
        files: List of discovered files
        total_files: Total number of files
        total_size: Total size in bytes
        total_lines: Total lines of code
        languages: Language distribution (language -> file count)
        discovery_time: Time taken to discover files
    """
    files: List[FileInfo]
    total_files: int
    total_size: int
    total_lines: int
    languages: Dict[str, int]
    discovery_time: float


@dataclass
class CodeElement:
    """
    Represents a code element (class, function, method).
    
    Attributes:
        type: Element type (class, function, method, variable)
        name: Element name
        file_path: Path to containing file
        line_start: Starting line number
        line_end: Ending line number
        signature: Function/method signature (for Phase 3)
        complexity: Cyclomatic complexity score (legacy) or ComplexityMetrics (Phase 3)
        dependencies: List of imported/referenced elements
        docstring: Documentation string (if present)
    """
    type: str
    name: str
    file_path: Path
    line_start: int
    line_end: int
    signature: str = ""
    complexity: Any = 0  # int (legacy) or ComplexityMetrics (Phase 3)
    dependencies: List[str] = field(default_factory=list)
    docstring: Optional[str] = None


@dataclass
class CodeAnalysisResult:
    """
    Results of AST-based code analysis.
    
    Attributes:
        elements: Discovered code elements
        dependency_graph: Dependency relationships (element -> dependencies)
        complexity_metrics: Complexity statistics
        detected_patterns: Design patterns found
        analysis_time: Time taken for analysis
    """
    elements: List[CodeElement]
    dependency_graph: Dict[str, List[str]]
    complexity_metrics: Dict[str, float]
    detected_patterns: List[str]
    analysis_time: float


@dataclass
class SemanticIndex:
    """
    Semantic search index for codebase.
    
    Attributes:
        index_path: Path to FTS5 index database
        indexed_files: Number of indexed files
        index_size_mb: Index size in megabytes
        search_ready: Whether index is ready for queries
    """
    index_path: Path
    indexed_files: int
    index_size_mb: float
    search_ready: bool


@dataclass
class GitHistory:
    """
    Git history analysis results.
    
    Attributes:
        commit_count: Total commits analyzed
        author_count: Number of unique authors
        churn_hotspots: Files with high change frequency
        authorship_map: File ownership mapping
        evolution_timeline: Code evolution over time
    """
    commit_count: int
    author_count: int
    churn_hotspots: List[Dict[str, Any]]
    authorship_map: Dict[str, str]
    evolution_timeline: List[Dict[str, Any]]


@dataclass
class DiscoveryReport:
    """
    Complete discovery operation report.
    
    Attributes:
        summary: High-level summary
        file_inventory: File discovery results
        code_analysis: AST analysis results (if performed)
        semantic_index: Semantic index info (if created)
        git_history: Git analysis results (if performed)
        insights: Extracted insights
        recommendations: Actionable recommendations
        generated_at: Report generation timestamp
        elapsed_time: Total discovery time
    """
    summary: Dict[str, Any]
    file_inventory: FileInventory
    code_analysis: Optional[CodeAnalysisResult] = None
    semantic_index: Optional[SemanticIndex] = None
    git_history: Optional[GitHistory] = None
    insights: List[str] = field(default_factory=list)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)
    elapsed_time: float = 0.0


# ============================================================================
# PHASE 3: AST ANALYSIS MODELS
# ============================================================================

@dataclass
class ASTNode:
    """Represents an Abstract Syntax Tree node"""
    node_type: str
    name: str
    start_line: int
    end_line: int
    children: List['ASTNode'] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplexityMetrics:
    """Complexity metrics for code elements"""
    cyclomatic_complexity: int = 0
    cognitive_complexity: int = 0
    lines_of_code: int = 0
    number_of_parameters: int = 0
    nesting_depth: int = 0
    maintainability_index: float = 0.0


@dataclass
class DependencyGraph:
    """Dependency graph representation"""
    nodes: Dict[str, CodeElement] = field(default_factory=dict)
    edges: List[Tuple[str, str]] = field(default_factory=list)
    cycles: List[List[str]] = field(default_factory=list)
