"""
Tests for cortex_discover MCP tool.

Authority: ENH-047 Pre-Execution Discovery Protocol
Author: Asif Hussain
"""

import pytest
from unittest.mock import Mock, patch
from cortex.mcp.tools.discovery.cortex_discover import (
    cortex_discover,
    DiscoveryReport,
    _extract_keywords,
    _generate_recommendation,
)


class TestCortexDiscover:
    """Test cortex_discover MCP tool."""
    
    def test_discover_blocks_on_duplicates(self):
        """Test that discovery blocks when duplicates detected (CORE-035)."""
        with patch('cortex.mcp.tools.lens_tools.cortex_detect_duplicates') as mock_detect:
            mock_detect.return_value = {
                "status": "success",
                "duplicates": [
                    {"file_path": "dashboard_v2.py", "similarity": 0.95}
                ]
            }
            
            with patch('cortex.mcp.tools.lens_tools.cortex_git_history') as mock_git:
                mock_git.return_value = {"status": "success", "commits": []}
                
                result = cortex_discover(
                    feature_name="dashboard generator",
                    scope="module",
                    intent="IMPLEMENT",
                )
                
                assert result["status"] == "success"
                report = result["report"]
                assert report["recommendation"] == "BLOCKED"
                assert "duplicate" in report["recommendation_rationale"].lower()
                assert len(report["duplicates"]) == 1
    
    def test_discover_recommends_extend_when_features_found(self):
        """Test that discovery recommends EXTEND when existing features found."""
        with patch('cortex.mcp.tools.lens_tools.cortex_detect_duplicates') as mock_detect:
            mock_detect.return_value = {"status": "success", "duplicates": []}
            
            with patch('cortex.mcp.tools.discovery.cortex_discover._semantic_file_search') as mock_search:
                mock_search.return_value = [
                    {"file_path": "dashboard.py", "match_type": "filename"}
                ]
                
                with patch('cortex.mcp.tools.lens_tools.cortex_git_history') as mock_git:
                    mock_git.return_value = {"status": "success", "commits": []}
                    
                    result = cortex_discover(
                        feature_name="dashboard",
                        scope="module",
                        intent="IMPLEMENT",
                    )
                    
                    assert result["status"] == "success"
                    report = result["report"]
                    assert report["recommendation"] == "EXTEND"
                    assert len(report["existing_features"]) > 0
    
    def test_discover_recommends_create_new_when_safe(self):
        """Test that discovery recommends CREATE_NEW when no concerns."""
        with patch('cortex.mcp.tools.lens_tools.cortex_detect_duplicates') as mock_detect:
            mock_detect.return_value = {"status": "success", "duplicates": []}
            
            with patch('cortex.mcp.tools.discovery.cortex_discover._semantic_file_search') as mock_search:
                mock_search.return_value = []
                
                with patch('cortex.mcp.tools.lens_tools.cortex_git_history') as mock_git:
                    mock_git.return_value = {"status": "success", "commits": []}
                    
                    result = cortex_discover(
                        feature_name="new_feature",
                        scope="file",
                        intent="IMPLEMENT",
                    )
                    
                    assert result["status"] == "success"
                    report = result["report"]
                    assert report["recommendation"] == "CREATE_NEW"
                    assert report["confidence"] > 0.8
    
    def test_extract_keywords(self):
        """Test keyword extraction from feature name."""
        keywords = _extract_keywords("KSESSIONS Dashboard Generator v2")
        
        assert "ksessions" in keywords
        assert "dashboard" in keywords
        assert "generator" in keywords
        assert "the" not in keywords  # stop word removed
    
    def test_generate_recommendation_blocks_duplicates(self):
        """Test recommendation generation blocks on duplicates."""
        recommendation, rationale, confidence = _generate_recommendation(
            existing_features=[],
            duplicates=[{"file_path": "test_v2.py"}],
            related_work=[],
            intent="IMPLEMENT",
        )
        
        assert recommendation == "BLOCKED"
        assert "CORE-035" in rationale
        assert confidence == 1.0


class TestDiscoveryReport:
    """Test DiscoveryReport dataclass."""
    
    def test_discovery_report_creation(self):
        """Test DiscoveryReport can be created and converted to dict."""
        report = DiscoveryReport(
            feature_name="test",
            existing_features=[],
            duplicates=[],
            related_work=[],
            recommendation="CREATE_NEW",
            recommendation_rationale="Safe to proceed",
            confidence=0.9,
            metadata={}
        )
        
        assert report.feature_name == "test"
        assert report.recommendation == "CREATE_NEW"
        
        report_dict = report.to_dict()
        assert report_dict["confidence"] == 0.9
