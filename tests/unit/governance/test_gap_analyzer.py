"""
Tests for GapAnalyzer - Company domain gap detection and reporting.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 27 specification
"""

import pytest
from cortex.governance.gap_analyzer import (
    GapAnalyzer,
    GapEntry,
    GapReport,
)


class TestGapAnalyzerBasic:
    """Test basic GapAnalyzer functionality."""
    
    def test_analyzer_initializes(self):
        """GapAnalyzer initializes with empty gaps."""
        analyzer = GapAnalyzer()
        
        assert analyzer is not None
        assert len(analyzer.gaps) == 0
    
    def test_gap_entry_dataclass(self):
        """GapEntry captures domain, subdomain, used_by."""
        entry = GapEntry(
            domain="security",
            subdomain="authentication",
            used_by="SecurityCheckpointAgent",
            fallback_source="cortex/knowledge/security/owasp-top-10.yaml",
        )
        
        assert entry.domain == "security"
        assert entry.subdomain == "authentication"
        assert entry.used_by == "SecurityCheckpointAgent"


class TestGapDetection:
    """Test gap detection and logging."""
    
    def test_record_gap(self):
        """Should record gap when company standard missing."""
        analyzer = GapAnalyzer()
        
        analyzer.record_gap(
            domain="security",
            subdomain="authentication",
            used_by="SecurityCheckpointAgent",
            fallback_source="cortex",
        )
        
        assert len(analyzer.gaps) == 1
        assert analyzer.gaps[0].domain == "security"
    
    def test_multiple_gaps_tracked(self):
        """Should track multiple gaps."""
        analyzer = GapAnalyzer()
        
        analyzer.record_gap("security", "auth", "Agent1", "cortex")
        analyzer.record_gap("testing", "patterns", "TDDOrch", "defaults")
        
        assert len(analyzer.gaps) == 2
    
    def test_deduplicates_same_gap(self):
        """Should deduplicate same gap recorded twice."""
        analyzer = GapAnalyzer()
        
        analyzer.record_gap("security", "auth", "Agent1", "cortex")
        analyzer.record_gap("security", "auth", "Agent1", "cortex")
        
        assert len(analyzer.gaps) == 1


class TestGapReportGeneration:
    """Test gap report generation."""
    
    def test_generates_report(self):
        """Should generate markdown report."""
        analyzer = GapAnalyzer()
        
        analyzer.record_gap(
            "security",
            "authentication",
            "SecurityCheckpointAgent",
            "cortex/knowledge/security/owasp.yaml",
        )
        
        report = analyzer.generate_report()
        
        assert isinstance(report, GapReport)
        assert "security/authentication" in report.markdown
        assert "SecurityCheckpointAgent" in report.markdown
    
    def test_report_empty_when_no_gaps(self):
        """Should return empty report when no gaps."""
        analyzer = GapAnalyzer()
        
        report = analyzer.generate_report()
        
        assert report.gap_count == 0
        assert "No gaps detected" in report.markdown
    
    def test_report_includes_recommendations(self):
        """Should include recommendations for each gap."""
        analyzer = GapAnalyzer()
        
        analyzer.record_gap("testing", "patterns", "TDDOrch", "defaults")
        
        report = analyzer.generate_report()
        
        assert "Recommendation:" in report.markdown
        assert "Define company-specific" in report.markdown


class TestGapReportDataclass:
    """Test GapReport dataclass."""
    
    def test_report_stores_metadata(self):
        """GapReport stores gap count and markdown."""
        report = GapReport(
            gap_count=2,
            markdown="# Gap Report\n...",
            timestamp="2026-02-06",
        )
        
        assert report.gap_count == 2
        assert "Gap Report" in report.markdown
        assert report.timestamp == "2026-02-06"
