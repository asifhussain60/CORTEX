"""
Test suite for CrawlerOrchestrator class.

TDD RED PHASE: This test is expected to FAIL initially.
Purpose: Verify CrawlerOrchestrator class exists and can be instantiated.
"""

import pytest
from src.crawlers.crawler_orchestrator import CrawlerOrchestrator


class TestCrawlerOrchestratorInitialization:
    """Test CrawlerOrchestrator initialization and basic setup."""
    
    def test_crawler_orchestrator_exists(self):
        """
        TDD RED: Test that CrawlerOrchestrator class can be imported.
        
        Expected to FAIL: Class doesn't exist yet.
        """
        orchestrator = CrawlerOrchestrator()
        assert orchestrator is not None
    
    def test_accepts_scan_level_parameter(self):
        """
        TDD RED: Test that CrawlerOrchestrator accepts scan_level parameter.
        
        Expected to FAIL: scan_level parameter not implemented yet.
        """
        orchestrator = CrawlerOrchestrator(scan_level="overview")
        assert orchestrator.scan_level == "overview"
        
    def test_defaults_to_standard_scan_level(self):
        """
        TDD RED: Test that CrawlerOrchestrator defaults to 'standard' scan level.
        
        Expected to FAIL: Default not implemented yet.
        """
        orchestrator = CrawlerOrchestrator()
        assert orchestrator.scan_level == "standard"


class TestCrawlerOrchestratorScanMethod:
    """Test CrawlerOrchestrator scan() method."""
    
    def test_scan_method_exists(self):
        """
        TDD RED: Test that scan() method exists.
        
        Expected to FAIL: scan() method not implemented yet.
        """
        orchestrator = CrawlerOrchestrator()
        result = orchestrator.scan(root_path="c:\\test")
        assert result is not None
    
    def test_scan_returns_scan_result(self):
        """
        TDD RED: Test that scan() returns ScanResult object.
        
        Expected to FAIL: ScanResult class doesn't exist yet.
        """
        from src.crawlers.scan_result import ScanResult
        
        orchestrator = CrawlerOrchestrator()
        result = orchestrator.scan(root_path="c:\\test")
        assert isinstance(result, ScanResult)


class TestCrawlerOrchestratorIntegration:
    """Test CrawlerOrchestrator with FileSystemWalker integration."""
    
    def test_scan_discovers_files(self, tmp_path):
        """Test scan uses FileSystemWalker to discover files."""
        # Create test files
        (tmp_path / "app.py").write_text("# Python file")
        (tmp_path / "test.js").write_text("// JavaScript file")
        (tmp_path / "README.md").write_text("# Documentation")
        
        # Scan directory
        orchestrator = CrawlerOrchestrator()
        result = orchestrator.scan(str(tmp_path))
        
        # Should find files
        assert result.total_files > 0
        assert result.total_files == 3


class TestCrawlerOrchestratorScanLevels:
    """Test scan level configurations."""
    
    def test_overview_scan_excludes_common_dirs(self, tmp_path):
        """Test overview scan excludes .git, node_modules, etc."""
        # Create files in included and excluded directories
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "app.py").write_text("# App")
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("git config")
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "lib.js").write_text("// lib")
        
        # Scan with overview level
        orchestrator = CrawlerOrchestrator(scan_level="overview")
        result = orchestrator.scan(str(tmp_path))
        
        # Should only find src/app.py, not .git or node_modules files
        assert result.total_files == 1
