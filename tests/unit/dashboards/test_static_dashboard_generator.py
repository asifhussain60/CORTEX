"""
Test suite for StaticDashboardGenerator.

Phase: 23.1 - Foundation
TDD: RED phase - Tests written before implementation
"""

import pytest
from pathlib import Path
from datetime import datetime
from company.dashboards.core.static_dashboard_generator import (
    StaticDashboardGenerator,
    DashboardData,
    SizeTier
)


class TestStaticDashboardGenerator:
    """Test StaticDashboardGenerator foundation."""
    
    def test_generator_initialization(self):
        """Test generator can be instantiated."""
        generator = StaticDashboardGenerator()
        assert generator is not None
    
    def test_size_tier_detection_small(self):
        """Test size tier detection for small repos (<100 files)."""
        generator = StaticDashboardGenerator()
        tier = generator.detect_size_tier(file_count=50)
        assert tier == SizeTier.SMALL
    
    def test_size_tier_detection_medium(self):
        """Test size tier detection for medium repos (100-1000 files)."""
        generator = StaticDashboardGenerator()
        tier = generator.detect_size_tier(file_count=500)
        assert tier == SizeTier.MEDIUM
    
    def test_size_tier_detection_large(self):
        """Test size tier detection for large repos (1000-10000 files)."""
        generator = StaticDashboardGenerator()
        tier = generator.detect_size_tier(file_count=5000)
        assert tier == SizeTier.LARGE
    
    def test_size_tier_detection_enterprise(self):
        """Test size tier detection for enterprise repos (>10000 files)."""
        generator = StaticDashboardGenerator()
        tier = generator.detect_size_tier(file_count=15000)
        assert tier == SizeTier.ENTERPRISE
    
    def test_dashboard_data_initialization(self):
        """Test DashboardData dataclass can be created."""
        data = DashboardData(
            repo_name="test-repo",
            generated_at=datetime.now(),
            generator_version="1.0.0",
            size_tier=SizeTier.SMALL,
            metadata={},
            sections={}
        )
        assert data.repo_name == "test-repo"
        assert data.size_tier == SizeTier.SMALL
    
    def test_collect_data_returns_dashboard_data(self, tmp_path):
        """Test collect_data returns DashboardData object."""
        generator = StaticDashboardGenerator()
        
        # Create minimal test repo structure
        test_repo = tmp_path / "test-repo"
        test_repo.mkdir()
        (test_repo / "README.md").write_text("# Test Repo")
        (test_repo / "main.py").write_text("# Python file")
        
        data = generator.collect_data(test_repo)
        assert isinstance(data, DashboardData)
        assert data.repo_name == "test-repo"
    
    def test_render_html_returns_string(self):
        """Test render_html returns HTML string."""
        generator = StaticDashboardGenerator()
        
        data = DashboardData(
            repo_name="test-repo",
            generated_at=datetime.now(),
            generator_version="1.0.0",
            size_tier=SizeTier.SMALL,
            metadata={"file_count": 2},
            sections={"overview": {}}
        )
        
        html = generator.render_html(data)
        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html
        assert "test-repo" in html
    
    def test_embed_assets_inlines_css(self):
        """Test embed_assets inlines CSS into HTML."""
        generator = StaticDashboardGenerator()
        
        html = "<html><head></head><body></body></html>"
        css = ".glass-card { background: rgba(10, 20, 40, 0.7); }"
        js = "console.log('test');"
        
        result = generator.embed_assets(html, css, js)
        assert "<style>" in result
        assert css in result
        assert "<script>" in result
        assert js in result
    
    def test_generate_creates_output_file(self, tmp_path):
        """Test generate creates output HTML file."""
        generator = StaticDashboardGenerator()
        
        # Create test repo
        test_repo = tmp_path / "test-repo"
        test_repo.mkdir()
        (test_repo / "README.md").write_text("# Test")
        
        # Generate dashboard
        output_path = tmp_path / "dashboard.html"
        result_path = generator.generate(test_repo, output_path)
        
        assert result_path.exists()
        assert result_path == output_path
        assert output_path.read_text().startswith("<!DOCTYPE html>")
    
    def test_generate_with_auto_size_tier(self, tmp_path):
        """Test generate with auto size tier detection."""
        generator = StaticDashboardGenerator()
        
        test_repo = tmp_path / "test-repo"
        test_repo.mkdir()
        (test_repo / "file1.py").write_text("# File 1")
        (test_repo / "file2.py").write_text("# File 2")
        
        output_path = tmp_path / "dashboard.html"
        result_path = generator.generate(
            test_repo, 
            output_path, 
            size_tier="auto"
        )
        
        assert result_path.exists()
        html_content = result_path.read_text()
        assert "test-repo" in html_content
