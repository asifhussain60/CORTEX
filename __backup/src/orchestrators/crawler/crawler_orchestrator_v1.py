"""
Crawler Orchestrator - AC-CRAWLER-001 to AC-CRAWLER-005
Coordinates multi-language code analysis with parallel processing
"""
from pathlib import Path
from typing import Optional, Dict, Any
import logging

from src.orchestrators.base.base_orchestrator_v4 import BaseOrchestratorV4
from src.orchestrators.master.orchestrator_registry import (
    OrchestratorRegistry,
)
from src.crawlers.crawler_orchestrator import CrawlerOrchestrator, ScanLevel
from src.orchestrators.audit_logger import EnterpriseAuditLogger


logger = logging.getLogger(__name__)


@OrchestratorRegistry.register(
    name="crawler",
    patterns=[
        "crawl",
        "analyze code",
        "scan repository",
        "code analysis",
        "extract symbols",
        "dependency",
        "multi-language",
    ],
)
class CrawlerOrchestratorV1(BaseOrchestratorV4):
    """
    Multi-language Code Crawler Orchestrator
    
    AC-CRAWLER-001 to AC-CRAWLER-005:
    - Parallel processing with auto CPU scaling
    - Language-specific AST analyzers (24 languages)
    - Progressive scan levels (OVERVIEW → STANDARD → DEEP)
    - Orchestration with pattern matching
    - Intelligent file discovery
    """

    def __init__(self, workspace_root: Optional[Path] = None):
        """Initialize crawler orchestrator."""
        super().__init__(workspace_root=workspace_root)
        self.audit_logger = EnterpriseAuditLogger()
        self.orchestrator_id = "crawler_orchestrator_v1"
        self.logger = logging.getLogger(__name__)

    def can_handle(self, request: str) -> bool:
        """Check if this orchestrator can handle the request."""
        keywords = [
            "crawl",
            "analyze code",
            "scan repository",
            "code analysis",
            "extract symbols",
            "dependency analysis",
            "code discovery",
            "parallel analysis",
            "multi-language scan",
        ]
        return any(keyword in request.lower() for keyword in keywords)

    def handle(self, request: str) -> Dict[str, Any]:
        """Handle code crawling request."""
        self.logger.info(f"Crawler orchestrator handling: {request}")

        try:
            # Parse request for options
            scan_level = self._extract_scan_level(request)
            include_patterns = self._extract_patterns(request, "include")
            exclude_patterns = self._extract_patterns(request, "exclude")
            languages = self._extract_languages(request)

            # Create crawler
            crawler = CrawlerOrchestrator(
                root_path=str(self.workspace_root),
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
                max_workers=None,  # Auto-detect
                cache_results=True,
            )

            # Execute crawl
            if languages:
                # Crawl specific languages
                results = []
                for language in languages:
                    result = crawler.crawl_language(language, scan_level)
                    results.append(result)
            else:
                # Crawl entire codebase
                result = crawler.crawl(scan_level)
                results = [result]

            # Log to audit trail
            self.audit_logger.log(
                level="INFO",
                category="CRAWLER",
                message=f"Crawl completed: {len(results)} result(s)",
                metadata={
                    "scan_level": scan_level.name,
                    "results": len(results),
                    "languages": languages or ["all"],
                },
            )

            # Export results if requested
            if self._should_export(request):
                export_path = (
                    self.workspace_root
                    / "cortex-brain"
                    / "documents"
                    / "crawl_results.json"
                )
                if results:
                    crawler.export_json(results[0], str(export_path))

            return {
                "success": True,
                "orchestrator": "CrawlerOrchestratorV1",
                "scan_level": scan_level.name,
                "results": len(results),
                "languages_detected": (
                    results[0].languages_detected if results else {}
                ),
                "files_found": (
                    results[0].files_found if results else 0
                ),
                "files_analyzed": (
                    results[0].files_analyzed if results else 0
                ),
            }

        except Exception as e:
            error_msg = f"Crawler orchestrator error: {str(e)}"
            self.logger.error(error_msg)
            self.audit_logger.log(
                level="ERROR",
                category="CRAWLER",
                message=error_msg,
            )
            return {
                "success": False,
                "error": error_msg,
                "orchestrator": "CrawlerOrchestratorV1",
            }

    @staticmethod
    def _extract_scan_level(request: str) -> ScanLevel:
        """Extract scan level from request."""
        request_lower = request.lower()
        if "deep" in request_lower or "full" in request_lower:
            return ScanLevel.DEEP
        elif "overview" in request_lower or "quick" in request_lower:
            return ScanLevel.OVERVIEW
        return ScanLevel.STANDARD

    @staticmethod
    def _extract_patterns(request: str, pattern_type: str) -> Optional[list]:
        """Extract include/exclude patterns from request."""
        # Simple extraction (could be enhanced)
        return None

    @staticmethod
    def _extract_languages(request: str) -> list:
        """Extract languages from request."""
        supported_languages = [
            "python",
            "javascript",
            "typescript",
            "csharp",
            "java",
            "go",
            "rust",
            "ruby",
            "php",
            "cpp",
            "c",
            "sql",
            "oracle",
            "angular",
            "react",
            "vue",
        ]

        languages = []
        request_lower = request.lower()
        for lang in supported_languages:
            if lang in request_lower:
                languages.append(lang)

        return list(set(languages))  # Remove duplicates

    @staticmethod
    def _should_export(request: str) -> bool:
        """Check if results should be exported."""
        return "export" in request.lower() or "save" in request.lower()
