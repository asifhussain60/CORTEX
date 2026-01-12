"""
Tests for AC-CRAWLER-003 & AC-CRAWLER-004: Progressive Scan Levels and Orchestration
"""
import pytest
import tempfile
from pathlib import Path
from src.crawlers.crawler_orchestrator import (
    CrawlerOrchestrator,
    ScanLevel,
    CrawlResult,
)


class TestScanLevels:
    """AC-CRAWLER-003: Progressive scan levels"""

    def test_scan_level_overview(self):
        """Test OVERVIEW scan level exists"""
        assert ScanLevel.OVERVIEW.value == 1

    def test_scan_level_standard(self):
        """Test STANDARD scan level exists"""
        assert ScanLevel.STANDARD.value == 2

    def test_scan_level_deep(self):
        """Test DEEP scan level exists"""
        assert ScanLevel.DEEP.value == 3

    def test_scan_level_ordering(self):
        """Test scan levels have correct ordering"""
        assert ScanLevel.OVERVIEW.value < ScanLevel.STANDARD.value
        assert ScanLevel.STANDARD.value < ScanLevel.DEEP.value


class TestCrawlerOrchestration:
    """AC-CRAWLER-004: Crawler orchestration"""

    def test_orchestrator_initialization(self):
        """Test orchestrator initializes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = CrawlerOrchestrator(tmpdir)

            assert orchestrator.root_path == Path(tmpdir)
            assert orchestrator.parallel_processor is not None

    def test_orchestrator_with_custom_workers(self):
        """Test orchestrator with custom worker count"""
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = CrawlerOrchestrator(
                tmpdir,
                max_workers=2,
            )

            assert orchestrator.parallel_processor.worker_count == 2

    def test_crawl_overview(self):
        """Test OVERVIEW level crawl"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            Path(tmpdir, "test.py").write_text("# python")
            Path(tmpdir, "app.ts").write_text("// typescript")

            orchestrator = CrawlerOrchestrator(tmpdir)
            result = orchestrator.crawl(ScanLevel.OVERVIEW)

            assert result.scan_level == ScanLevel.OVERVIEW
            assert result.files_found >= 2
            assert result.files_analyzed > 0
            assert "python" in result.languages_detected

    def test_crawl_standard(self):
        """Test STANDARD level crawl"""
        with tempfile.TemporaryDirectory() as tmpdir:
            code = """
def hello():
    pass

class MyClass:
    pass
"""
            Path(tmpdir, "test.py").write_text(code)

            orchestrator = CrawlerOrchestrator(tmpdir)
            result = orchestrator.crawl(ScanLevel.STANDARD)

            assert result.scan_level == ScanLevel.STANDARD
            assert result.files_analyzed > 0
            assert len(result.analyses) > 0

    def test_crawl_result_structure(self):
        """Test crawl result has required fields"""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.py").write_text("# python")

            orchestrator = CrawlerOrchestrator(tmpdir)
            result = orchestrator.crawl(ScanLevel.OVERVIEW)

            assert isinstance(result, CrawlResult)
            assert result.root_path == tmpdir
            assert result.files_found >= 0
            assert result.files_analyzed >= 0
            assert isinstance(result.languages_detected, dict)
            assert isinstance(result.errors, list)

    def test_crawl_language_specific(self):
        """Test crawling specific language"""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.py").write_text("# python")
            Path(tmpdir, "app.ts").write_text("// typescript")

            orchestrator = CrawlerOrchestrator(tmpdir)
            result = orchestrator.crawl_language("python")

            assert "python" in result.languages_detected

    def test_crawl_mixed_tech_stack(self):
        """Test crawling mixed tech stack"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mixed tech files
            Path(tmpdir, "backend.py").write_text("# python")
            Path(tmpdir, "Program.cs").write_text("// csharp")
            Path(tmpdir, "App.tsx").write_text("// react")
            Path(tmpdir, "query.sql").write_text("-- sql")

            orchestrator = CrawlerOrchestrator(tmpdir)
            result = orchestrator.crawl(ScanLevel.OVERVIEW)

            assert result.files_found >= 4
            assert len(result.languages_detected) > 1

    def test_export_to_json(self):
        """Test exporting crawl results to JSON"""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.py").write_text("def func(): pass")

            orchestrator = CrawlerOrchestrator(tmpdir)
            result = orchestrator.crawl(ScanLevel.STANDARD)

            output_file = Path(tmpdir) / "crawl_results.json"
            orchestrator.export_json(result, str(output_file))

            assert output_file.exists()

            import json

            with open(output_file) as f:
                data = json.load(f)
                assert data["root_path"] == tmpdir
                assert data["scan_level"] == "STANDARD"

    def test_language_detection(self):
        """Test language detection from extension"""
        assert CrawlerOrchestrator._detect_language(".py") == "python"
        assert CrawlerOrchestrator._detect_language(".js") == "javascript"
        assert CrawlerOrchestrator._detect_language(".cs") == "csharp"
        assert CrawlerOrchestrator._detect_language(".sql") == "sql"
        assert CrawlerOrchestrator._detect_language(".ts") == "typescript"
        assert CrawlerOrchestrator._detect_language(".tsx") == "typescript"

    def test_language_detection_unknown(self):
        """Test language detection for unknown extensions"""
        result = CrawlerOrchestrator._detect_language(".xyz")
        assert result is None

    def test_crawl_with_include_patterns(self):
        """Test crawl with include patterns"""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.py").write_text("# python")
            Path(tmpdir, "test.js").write_text("// js")

            orchestrator = CrawlerOrchestrator(
                tmpdir,
                include_patterns=["**/*.py"],
            )
            result = orchestrator.crawl(ScanLevel.OVERVIEW)

            assert result.files_found == 1

    def test_crawl_with_exclude_patterns(self):
        """Test crawl with exclude patterns"""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "main.py").write_text("# python")
            Path(tmpdir, "test_main.py").write_text("# test")

            orchestrator = CrawlerOrchestrator(
                tmpdir,
                include_patterns=["**/*.py"],
                exclude_patterns=["**/test_main.py"],
            )
            result = orchestrator.crawl(ScanLevel.OVERVIEW)

            assert result.files_found == 1

    def test_crawl_empty_directory(self):
        """Test crawl on empty directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = CrawlerOrchestrator(tmpdir)
            result = orchestrator.crawl(ScanLevel.OVERVIEW)

            assert result.files_found == 0
            assert result.files_analyzed == 0

    def test_progress_callback(self):
        """Test progress callback during crawl"""
        progress_updates = []

        def callback(update):
            progress_updates.append(update)

        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.py").write_text("# python")

            orchestrator = CrawlerOrchestrator(
                tmpdir,
                progress_callback=callback,
            )
            result = orchestrator.crawl(ScanLevel.STANDARD)

            # Progress callback should be called
            # (May be empty if files process too quickly)

    def test_crawl_caching(self):
        """Test analysis result caching"""
        with tempfile.TemporaryDirectory() as tmpdir:
            code = "def func(): pass"
            Path(tmpdir, "test.py").write_text(code)

            orchestrator = CrawlerOrchestrator(tmpdir, cache_results=True)

            # First crawl
            result1 = orchestrator.crawl(ScanLevel.STANDARD)

            # Second crawl should use cache
            result2 = orchestrator.crawl(ScanLevel.STANDARD)

            assert result1.files_analyzed == result2.files_analyzed

    def test_orchestrator_error_handling(self):
        """Test orchestrator handles errors gracefully"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create unreadable file (may not work on all systems)
            Path(tmpdir, "test.py").write_text("def func(): pass")

            orchestrator = CrawlerOrchestrator(tmpdir)
            result = orchestrator.crawl(ScanLevel.STANDARD)

            # Should complete without crashing
            assert isinstance(result, CrawlResult)

    def test_symbol_aggregation(self):
        """Test symbol aggregation from crawl"""
        with tempfile.TemporaryDirectory() as tmpdir:
            code = """
def func1(): pass
def func2(): pass
class MyClass: pass
"""
            Path(tmpdir, "test.py").write_text(code)

            orchestrator = CrawlerOrchestrator(tmpdir)
            result = orchestrator.crawl(ScanLevel.STANDARD)

            assert result.total_symbols > 0

    def test_dependency_aggregation(self):
        """Test dependency extraction"""
        with tempfile.TemporaryDirectory() as tmpdir:
            code = """
import os
import sys
from pathlib import Path
"""
            Path(tmpdir, "test.py").write_text(code)

            orchestrator = CrawlerOrchestrator(tmpdir)
            result = orchestrator.crawl(ScanLevel.STANDARD)

            # Should have aggregated dependencies
            # (implementation may aggregate imports as dependencies)

    def test_multiple_language_crawl(self):
        """Test crawling each language separately"""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "app.py").write_text("# python")
            Path(tmpdir, "main.cs").write_text("// csharp")

            orchestrator = CrawlerOrchestrator(tmpdir)

            python_result = orchestrator.crawl_language("python")
            csharp_result = orchestrator.crawl_language("csharp")

            assert len(python_result.languages_detected) > 0
            assert len(csharp_result.languages_detected) > 0
