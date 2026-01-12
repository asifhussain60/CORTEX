"""
AC-CRAWLER-003 & AC-CRAWLER-004: Progressive Scan Levels and Crawler Orchestration
Coordinate crawlers with ignore patterns, file type detection, result aggregation
"""
from enum import Enum
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
import json
import logging

from src.crawlers.parallel_processor import ParallelProcessor, ProgressUpdate
from src.crawlers.file_discovery import FileDiscovery
from src.crawlers.analyzers import AnalyzerFactory, AnalysisResult

logger = logging.getLogger(__name__)


class ScanLevel(Enum):
    """Progressive scanning levels - AC-CRAWLER-003"""
    OVERVIEW = 1  # Structure only
    STANDARD = 2  # With basic analysis
    DEEP = 3  # Full AST parsing


@dataclass
class CrawlResult:
    """Result from crawling a codebase"""
    root_path: str
    scan_level: ScanLevel
    files_found: int
    files_analyzed: int
    analyses: List[AnalysisResult] = field(default_factory=list)
    errors: List[Dict[str, str]] = field(default_factory=list)
    languages_detected: Dict[str, int] = field(
        default_factory=dict
    )
    total_symbols: int = 0
    total_dependencies: List[str] = field(default_factory=list)


class CrawlerOrchestrator:
    """
    Coordinate crawlers with ignore patterns, file type detection.
    
    AC-CRAWLER-004 Requirements:
    - Gitignore pattern support
    - Language detection by extension
    - Result merging from multiple analyzers
    - Caching of analysis results
    - Export to JSON/YAML formats
    """

    def __init__(
        self,
        root_path: str,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        max_workers: Optional[int] = None,
        progress_callback: Optional[Callable[[ProgressUpdate], None]] = None,
        cache_results: bool = True,
    ):
        """
        Initialize crawler orchestrator.

        Args:
            root_path: Root directory to crawl
            include_patterns: File patterns to include
            exclude_patterns: File patterns to exclude
            max_workers: Thread count for parallel processing
            progress_callback: Progress update callback
            cache_results: Cache analysis results
        """
        self.root_path = Path(root_path)
        self.file_discovery = FileDiscovery(
            root_path=str(self.root_path),
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            respect_gitignore=True,
        )
        self.parallel_processor = ParallelProcessor(
            max_workers=max_workers,
            progress_callback=progress_callback,
        )
        self.cache = {} if cache_results else None
        self.progress_callback = progress_callback

    def crawl(self, scan_level: ScanLevel = ScanLevel.STANDARD) -> CrawlResult:
        """
        Crawl codebase with specified scan level.

        Args:
            scan_level: OVERVIEW, STANDARD, or DEEP

        Returns:
            CrawlResult with analysis data
        """
        result = CrawlResult(
            root_path=str(self.root_path),
            scan_level=scan_level,
            files_found=0,
            files_analyzed=0,
        )

        # Discover files
        files = self.file_discovery.discover()
        result.files_found = len(files)

        if not files:
            logger.warning(f"No files found in {self.root_path}")
            return result

        # Analyze based on scan level
        if scan_level == ScanLevel.OVERVIEW:
            result = self._crawl_overview(files, result)
        elif scan_level == ScanLevel.STANDARD:
            result = self._crawl_standard(files, result)
        elif scan_level == ScanLevel.DEEP:
            result = self._crawl_deep(files, result)

        return result

    def _crawl_overview(
        self, files: List[str], result: CrawlResult
    ) -> CrawlResult:
        """Quick structure scan only"""
        for file_path in files:
            path = Path(file_path)
            ext = path.suffix.lower()

            lang = self._detect_language(ext)
            if lang:
                result.languages_detected[lang] = (
                    result.languages_detected.get(lang, 0) + 1
                )
                result.files_analyzed += 1

        return result

    def _crawl_standard(
        self, files: List[str], result: CrawlResult
    ) -> CrawlResult:
        """Basic file analysis"""

        def analyze_file(file_path: str) -> Optional[AnalysisResult]:
            if self.cache is not None and file_path in self.cache:
                return self.cache[file_path]

            analyzer = AnalyzerFactory.get_analyzer(file_path)
            analysis = analyzer.analyze()

            if self.cache is not None:
                self.cache[file_path] = analysis

            return analysis

        # Process files in parallel
        process_result = self.parallel_processor.process_files(
            files, analyze_file
        )

        for file_path, analysis in process_result["results"].items():
            if analysis:
                result.analyses.append(analysis)
                result.files_analyzed += 1

                # Track languages
                lang = self._detect_language(
                    Path(file_path).suffix.lower()
                )
                if lang:
                    result.languages_detected[lang] = (
                        result.languages_detected.get(lang, 0) + 1
                    )

                # Aggregate data
                result.total_symbols += len(analysis.symbols)
                result.total_dependencies.extend(
                    analysis.dependencies
                )

        # Track errors
        for error in process_result["errors"]:
            result.errors.append(
                {"file": error.file_path, "error": error.error}
            )

        return result

    def _crawl_deep(
        self, files: List[str], result: CrawlResult
    ) -> CrawlResult:
        """Full AST parsing with symbol extraction"""
        # For now, same as standard (full AST already done by analyzers)
        return self._crawl_standard(files, result)

    def crawl_language(
        self, language: str, scan_level: ScanLevel = ScanLevel.STANDARD
    ) -> CrawlResult:
        """Crawl specific language only"""
        files = self.file_discovery.discover_by_language(language)
        result = CrawlResult(
            root_path=str(self.root_path),
            scan_level=scan_level,
            files_found=len(files),
            files_analyzed=0,
        )

        if scan_level == ScanLevel.STANDARD:
            result = self._crawl_standard(files, result)
        elif scan_level == ScanLevel.DEEP:
            result = self._crawl_deep(files, result)

        return result

    def export_json(
        self, crawl_result: CrawlResult, output_path: str
    ) -> None:
        """Export crawl results to JSON"""
        data = {
            "root_path": crawl_result.root_path,
            "scan_level": crawl_result.scan_level.name,
            "files_found": crawl_result.files_found,
            "files_analyzed": crawl_result.files_analyzed,
            "languages_detected": crawl_result.languages_detected,
            "total_symbols": crawl_result.total_symbols,
            "analyses": [
                {
                    "file": a.file_path,
                    "language": a.language,
                    "symbols": [
                        {
                            "name": s.name,
                            "type": s.type,
                            "line": s.line,
                        }
                        for s in a.symbols
                    ],
                    "imports": a.imports,
                    "metrics": a.metrics,
                }
                for a in crawl_result.analyses
            ],
            "errors": crawl_result.errors,
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Exported crawl results to {output_path}")

    @staticmethod
    def _detect_language(extension: str) -> Optional[str]:
        """Detect language from file extension"""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".cs": "csharp",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".sql": "sql",
            ".sh": "bash",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".xml": "xml",
        }
        return ext_map.get(extension)
