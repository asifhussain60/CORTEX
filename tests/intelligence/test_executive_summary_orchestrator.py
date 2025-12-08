"""
Tests for Executive Summary Orchestrator

RED PHASE: Write failing tests first

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
from src.intelligence.executive_summary_orchestrator import (
    ExecutiveSummaryOrchestrator,
    ExecutiveSummary
)


@pytest.fixture
def test_repo():
    """Create test repository with README and git history."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        
        # Create README
        readme = repo_path / 'README.md'
        readme.write_text("""# Test Project

A test application for validation.

## Purpose

This project demonstrates executive summary generation.

## Features

- Feature 1: Real-time processing
- Feature 2: Scalable architecture
- Feature 3: Easy integration

## Technology Stack

- Python 3.9+
- FastAPI
- PostgreSQL
""")
        
        # Initialize git (optional, may not work in all environments)
        try:
            import subprocess
            subprocess.run(['git', 'init'], cwd=repo_path, capture_output=True, check=True)
            subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=repo_path, capture_output=True)
            subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=repo_path, capture_output=True)
            subprocess.run(['git', 'add', '.'], cwd=repo_path, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'feat: Initial commit'], cwd=repo_path, capture_output=True)
        except:
            pass  # Git not available
        
        yield repo_path


class TestOrchestratorInitialization:
    """Test orchestrator initialization."""
    
    def test_create_orchestrator(self):
        """Should create orchestrator instance."""
        orchestrator = ExecutiveSummaryOrchestrator()
        assert orchestrator is not None
        assert orchestrator.readme_parser is not None
        assert orchestrator.domain_engine is not None


class TestBasicSummaryGeneration:
    """Test basic summary generation."""
    
    def test_generate_summary_with_readme(self, test_repo):
        """Should generate summary from README."""
        orchestrator = ExecutiveSummaryOrchestrator()
        summary = orchestrator.generate_summary(
            test_repo,
            include_git=False,
            include_domains=False
        )
        
        assert summary is not None
        assert summary.repo_name == test_repo.name
        assert summary.has_readme is True
        assert len(summary.title) > 0
    
    def test_summary_includes_description(self, test_repo):
        """Should extract description from README."""
        orchestrator = ExecutiveSummaryOrchestrator()
        summary = orchestrator.generate_summary(test_repo, include_git=False, include_domains=False)
        
        assert summary.description
        assert "test application" in summary.description.lower()
    
    def test_summary_includes_purpose(self, test_repo):
        """Should extract purpose statement."""
        orchestrator = ExecutiveSummaryOrchestrator()
        summary = orchestrator.generate_summary(test_repo, include_git=False, include_domains=False)
        
        assert summary.purpose is not None
        assert "demonstrates" in summary.purpose.lower()


class TestFeatureExtraction:
    """Test feature extraction into summary."""
    
    def test_extracts_features_from_readme(self, test_repo):
        """Should extract feature list."""
        orchestrator = ExecutiveSummaryOrchestrator()
        summary = orchestrator.generate_summary(test_repo, include_git=False, include_domains=False)
        
        assert len(summary.features) >= 3
        assert any("processing" in f.lower() for f in summary.features)
    
    def test_limits_features_to_10(self):
        """Should limit features to top 10."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            readme = repo / 'README.md'
            features_text = "\n".join([f"- Feature {i}" for i in range(20)])
            readme.write_text(f"""# Test
## Features
{features_text}
""")
            
            orchestrator = ExecutiveSummaryOrchestrator()
            summary = orchestrator.generate_summary(repo, include_git=False, include_domains=False)
            
            assert len(summary.features) <= 10


class TestTechnologyExtraction:
    """Test technology stack extraction."""
    
    def test_extracts_technologies(self, test_repo):
        """Should extract technology list."""
        orchestrator = ExecutiveSummaryOrchestrator()
        summary = orchestrator.generate_summary(test_repo, include_git=False, include_domains=False)
        
        assert len(summary.technologies) >= 2
        assert any("python" in t.lower() for t in summary.technologies)


class TestQualityScoring:
    """Test summary quality score calculation."""
    
    def test_readme_increases_score(self, test_repo):
        """Should have higher score with README."""
        orchestrator = ExecutiveSummaryOrchestrator()
        summary = orchestrator.generate_summary(test_repo, include_git=False, include_domains=False)
        
        assert summary.summary_quality_score >= 3.0  # README presence
    
    def test_purpose_increases_score(self, test_repo):
        """Should score higher with purpose statement."""
        orchestrator = ExecutiveSummaryOrchestrator()
        summary = orchestrator.generate_summary(test_repo, include_git=False, include_domains=False)
        
        # Has README (3) + purpose (1) + features (1) = 5
        assert summary.summary_quality_score >= 4.0
    
    def test_empty_repo_low_score(self):
        """Should have low score for empty repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = ExecutiveSummaryOrchestrator()
            summary = orchestrator.generate_summary(
                Path(tmpdir),
                include_git=False,
                include_domains=False
            )
            
            assert summary.summary_quality_score < 3.0


class TestSerialization:
    """Test summary serialization."""
    
    def test_to_dict_conversion(self, test_repo):
        """Should convert summary to dictionary."""
        orchestrator = ExecutiveSummaryOrchestrator()
        summary = orchestrator.generate_summary(test_repo, include_git=False, include_domains=False)
        result = orchestrator.to_dict(summary)
        
        assert isinstance(result, dict)
        assert 'repo_name' in result
        assert 'title' in result
        assert 'summary_quality_score' in result
    
    def test_to_json_conversion(self, test_repo):
        """Should convert summary to JSON."""
        orchestrator = ExecutiveSummaryOrchestrator()
        summary = orchestrator.generate_summary(test_repo, include_git=False, include_domains=False)
        json_str = orchestrator.to_json(summary)
        
        assert isinstance(json_str, str)
        assert '"repo_name"' in json_str
        assert '"title"' in json_str
    
    def test_to_markdown_conversion(self, test_repo):
        """Should convert summary to markdown."""
        orchestrator = ExecutiveSummaryOrchestrator()
        summary = orchestrator.generate_summary(test_repo, include_git=False, include_domains=False)
        markdown = orchestrator.to_markdown(summary)
        
        assert isinstance(markdown, str)
        assert '# ' in markdown  # Title
        assert '## Purpose' in markdown
        assert '## Features' in markdown


class TestGitIntegration:
    """Test git history integration (if available)."""
    
    def test_detects_git_repository(self, test_repo):
        """Should detect git repository if present."""
        orchestrator = ExecutiveSummaryOrchestrator()
        summary = orchestrator.generate_summary(test_repo, include_readme=False, include_domains=False)
        
        # Git may or may not be available
        if (test_repo / '.git').exists():
            assert summary.has_git_history is True
    
    def test_handles_no_git_gracefully(self):
        """Should handle repositories without git."""
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = ExecutiveSummaryOrchestrator()
            summary = orchestrator.generate_summary(
                Path(tmpdir),
                include_readme=False,
                include_domains=False
            )
            
            assert summary.has_git_history is False


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_handles_missing_readme(self):
        """Should handle repositories without README."""
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = ExecutiveSummaryOrchestrator()
            summary = orchestrator.generate_summary(Path(tmpdir))
            
            assert summary.has_readme is False
            assert summary.repo_name == Path(tmpdir).name
    
    def test_handles_malformed_readme(self):
        """Should handle malformed README gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            readme = repo / 'README.md'
            readme.write_text("Malformed content with **unclosed markdown")
            
            orchestrator = ExecutiveSummaryOrchestrator()
            summary = orchestrator.generate_summary(repo)
            
            # Should not crash
            assert summary is not None


class TestKnowledgeGraphIntegration:
    """Test knowledge graph updates."""
    
    def test_knowledge_graph_update_attempt(self, test_repo):
        """Should attempt to update knowledge graph without failing."""
        orchestrator = ExecutiveSummaryOrchestrator()
        
        # Should not raise exception even if knowledge graph unavailable
        summary = orchestrator.generate_summary(test_repo)
        assert summary is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
