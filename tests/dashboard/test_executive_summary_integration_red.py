"""
Tests for Enhanced Executive Summary Integration

RED PHASE: Write failing tests for 5-source intelligence integration

Tests integration of:
1. Git commit patterns (narrative, velocity, themes)
2. README deep-parsing (purpose, features, capabilities)
3. Docstring mining (code documentation quality)
4. Business domain inference (domains from code structure)
5. Tech stack analysis (existing functionality)

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
import tempfile
import json

# Import will fail until we create the enhanced module (RED phase)
try:
    from src.dashboard.aggregators.enhanced_executive_summary_aggregator import (
        EnhancedExecutiveSummaryAggregator,
        IntelligenceSource
    )
except ImportError:
    EnhancedExecutiveSummaryAggregator = None
    IntelligenceSource = None


@pytest.fixture
def temp_data_dir():
    """Create temporary data directory with mock data files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir) / "test-repo"
        data_dir.mkdir()
        
        # Create minimal data files
        (data_dir / "tech-stack.json").write_text(json.dumps({
            "backend": [{"name": "Python", "version": "3.9"}],
            "frontend": [],
            "database": [{"name": "PostgreSQL", "version": "13"}],
            "summary": {"total_technologies": 2}
        }))
        
        (data_dir / "architecture.json").write_text(json.dumps({
            "application_type": {"type": "web_app"},
            "style": {"name": "Layered Architecture"},
            "summary": {"total_loc": 10000, "total_components": 15}
        }))
        
        (data_dir / "health-data.json").write_text(json.dumps({
            "metrics": {"code_quality_score": 85}
        }))
        
        (data_dir / "security.json").write_text(json.dumps({
            "overall_score": 95
        }))
        
        (data_dir / "code-organization.json").write_text(json.dumps({
            "summary": {"technical_debt_hours": 20}
        }))
        
        yield data_dir


@pytest.fixture
def temp_repo_with_git():
    """Create temporary repository with git history."""
    import subprocess
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=repo_path, check=True, capture_output=True)
        
        # Create README
        readme = repo_path / "README.md"
        readme.write_text("""# Test Project

## Overview
A comprehensive project management platform for distributed teams.

## Features
- Task tracking and management
- Real-time collaboration
- Analytics dashboard
- User authentication
""")
        
        # Create some code files
        src_dir = repo_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text('"""Main application module."""\nprint("hello")')
        
        # Commit
        subprocess.run(['git', 'add', '.'], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'feat: Initial commit'], cwd=repo_path, check=True, capture_output=True)
        
        yield repo_path


class TestEnhancedAggregatorInitialization:
    """Test enhanced aggregator initialization."""
    
    @pytest.mark.skipif(EnhancedExecutiveSummaryAggregator is None, reason="RED phase")
    def test_init_with_repo_path(self, temp_data_dir, temp_repo_with_git):
        """Should initialize with data directory and repository path."""
        aggregator = EnhancedExecutiveSummaryAggregator(temp_data_dir, temp_repo_with_git)
        assert aggregator.data_dir == temp_data_dir
        assert aggregator.repo_path == temp_repo_with_git
    
    @pytest.mark.skipif(EnhancedExecutiveSummaryAggregator is None, reason="RED phase")
    def test_intelligence_sources_available(self, temp_data_dir, temp_repo_with_git):
        """Should have all 5 intelligence sources available."""
        aggregator = EnhancedExecutiveSummaryAggregator(temp_data_dir, temp_repo_with_git)
        sources = aggregator.get_available_sources()
        
        assert IntelligenceSource.GIT_COMMITS in sources
        assert IntelligenceSource.README in sources
        assert IntelligenceSource.DOCSTRINGS in sources
        assert IntelligenceSource.BUSINESS_DOMAINS in sources
        assert IntelligenceSource.TECH_STACK in sources


class TestGitCommitIntegration:
    """Test git commit intelligence integration."""
    
    @pytest.mark.skipif(EnhancedExecutiveSummaryAggregator is None, reason="RED phase")
    def test_extract_git_narrative(self, temp_data_dir, temp_repo_with_git):
        """Should extract development narrative from git commits."""
        aggregator = EnhancedExecutiveSummaryAggregator(temp_data_dir, temp_repo_with_git)
        result = aggregator.aggregate()
        
        assert "what_it_does" in result
        assert "git_insights" in result["what_it_does"]
        assert result["what_it_does"]["git_insights"]["narrative"] is not None
    
    @pytest.mark.skipif(EnhancedExecutiveSummaryAggregator is None, reason="RED phase")
    def test_include_velocity_metrics(self, temp_data_dir, temp_repo_with_git):
        """Should include velocity metrics from git analysis."""
        aggregator = EnhancedExecutiveSummaryAggregator(temp_data_dir, temp_repo_with_git)
        result = aggregator.aggregate()
        
        velocity = result["what_it_does"]["git_insights"]["velocity"]
        assert "total_commits" in velocity
        assert "features_completed" in velocity
        assert "bugs_fixed" in velocity


class TestReadmeIntegration:
    """Test README deep-parsing integration."""
    
    @pytest.mark.skipif(EnhancedExecutiveSummaryAggregator is None, reason="RED phase")
    def test_extract_readme_purpose(self, temp_data_dir, temp_repo_with_git):
        """Should extract business purpose from README."""
        aggregator = EnhancedExecutiveSummaryAggregator(temp_data_dir, temp_repo_with_git)
        result = aggregator.aggregate()
        
        assert "readme_insights" in result["what_it_does"]
        readme = result["what_it_does"]["readme_insights"]
        assert readme["purpose"] is not None
        assert "project management" in readme["purpose"].lower()
    
    @pytest.mark.skipif(EnhancedExecutiveSummaryAggregator is None, reason="RED phase")
    def test_extract_readme_capabilities(self, temp_data_dir, temp_repo_with_git):
        """Should extract key capabilities from README features."""
        aggregator = EnhancedExecutiveSummaryAggregator(temp_data_dir, temp_repo_with_git)
        result = aggregator.aggregate()
        
        capabilities = result["what_it_does"]["readme_insights"]["capabilities"]
        assert len(capabilities) >= 3
        assert any("task tracking" in c.lower() for c in capabilities)


class TestDocstringIntegration:
    """Test docstring mining integration."""
    
    @pytest.mark.skipif(EnhancedExecutiveSummaryAggregator is None, reason="RED phase")
    def test_analyze_documentation_quality(self, temp_data_dir, temp_repo_with_git):
        """Should analyze code documentation quality from docstrings."""
        aggregator = EnhancedExecutiveSummaryAggregator(temp_data_dir, temp_repo_with_git)
        result = aggregator.aggregate()
        
        assert "docstring_insights" in result["what_it_does"]
        docs = result["what_it_does"]["docstring_insights"]
        assert "quality_score" in docs
        assert 0 <= docs["quality_score"] <= 100
    
    @pytest.mark.skipif(EnhancedExecutiveSummaryAggregator is None, reason="RED phase")
    def test_extract_top_documented_modules(self, temp_data_dir, temp_repo_with_git):
        """Should identify top documented modules."""
        aggregator = EnhancedExecutiveSummaryAggregator(temp_data_dir, temp_repo_with_git)
        result = aggregator.aggregate()
        
        docs = result["what_it_does"]["docstring_insights"]
        assert "top_modules" in docs
        assert isinstance(docs["top_modules"], list)


class TestBusinessDomainIntegration:
    """Test business domain inference integration."""
    
    @pytest.mark.skipif(EnhancedExecutiveSummaryAggregator is None, reason="RED phase")
    def test_identify_business_domains(self, temp_data_dir, temp_repo_with_git):
        """Should identify business domains from code structure."""
        aggregator = EnhancedExecutiveSummaryAggregator(temp_data_dir, temp_repo_with_git)
        result = aggregator.aggregate()
        
        assert "domain_insights" in result["what_it_does"]
        domains = result["what_it_does"]["domain_insights"]["domains"]
        assert isinstance(domains, list)
    
    @pytest.mark.skipif(EnhancedExecutiveSummaryAggregator is None, reason="RED phase")
    def test_domain_confidence_scoring(self, temp_data_dir, temp_repo_with_git):
        """Should include confidence scores for domains."""
        aggregator = EnhancedExecutiveSummaryAggregator(temp_data_dir, temp_repo_with_git)
        result = aggregator.aggregate()
        
        domains = result["what_it_does"]["domain_insights"]["domains"]
        if domains:
            assert "confidence" in domains[0]
            assert domains[0]["confidence"] in ["high", "medium", "low"]


class TestSummaryQuality:
    """Test overall summary quality improvement."""
    
    @pytest.mark.skipif(EnhancedExecutiveSummaryAggregator is None, reason="RED phase")
    def test_summary_more_specific_than_template(self, temp_data_dir, temp_repo_with_git):
        """Enhanced summary should be more specific than template."""
        aggregator = EnhancedExecutiveSummaryAggregator(temp_data_dir, temp_repo_with_git)
        result = aggregator.aggregate()
        
        summary = result["what_it_does"]["summary"]
        
        # Should NOT contain generic template phrases
        assert "software application" not in summary.lower()
        assert "this system" not in summary.lower()
        
        # Should contain specific information
        assert len(summary) > 200  # At least 200 chars
    
    @pytest.mark.skipif(EnhancedExecutiveSummaryAggregator is None, reason="RED phase")
    def test_quality_score_calculated(self, temp_data_dir, temp_repo_with_git):
        """Should calculate and include quality score."""
        aggregator = EnhancedExecutiveSummaryAggregator(temp_data_dir, temp_repo_with_git)
        result = aggregator.aggregate()
        
        assert "quality_score" in result
        assert 0 <= result["quality_score"] <= 10
        assert result["quality_score"] >= 5  # Should be reasonable quality


class TestSourcePrioritization:
    """Test intelligence source prioritization logic."""
    
    @pytest.mark.skipif(EnhancedExecutiveSummaryAggregator is None, reason="RED phase")
    def test_readme_prioritized_when_detailed(self, temp_data_dir, temp_repo_with_git):
        """Should prioritize README when it's detailed (>200 chars)."""
        aggregator = EnhancedExecutiveSummaryAggregator(temp_data_dir, temp_repo_with_git)
        result = aggregator.aggregate()
        
        priority = result["what_it_does"]["source_priority"]
        assert priority[0] == "readme"  # README should be first
    
    @pytest.mark.skipif(EnhancedExecutiveSummaryAggregator is None, reason="RED phase")
    def test_fallback_when_readme_missing(self, temp_data_dir):
        """Should fall back to other sources when README missing."""
        # Create repo without README
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            
            aggregator = EnhancedExecutiveSummaryAggregator(temp_data_dir, repo_path)
            result = aggregator.aggregate()
            
            priority = result["what_it_does"]["source_priority"]
            assert "readme" not in priority or priority.index("readme") > 2


class TestPerformance:
    """Test aggregation performance."""
    
    @pytest.mark.skipif(EnhancedExecutiveSummaryAggregator is None, reason="RED phase")
    def test_aggregate_under_30_seconds(self, temp_data_dir, temp_repo_with_git):
        """Should complete aggregation in <30 seconds."""
        import time
        
        aggregator = EnhancedExecutiveSummaryAggregator(temp_data_dir, temp_repo_with_git)
        
        start = time.time()
        result = aggregator.aggregate()
        elapsed = time.time() - start
        
        assert elapsed < 30.0
        assert result is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
