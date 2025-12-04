"""Naming report generator tests (smoke tests)."""

import pytest


class TestNamingReportGenerator:
    """Test naming report generator."""
    
    def test_generator_exists(self):
        """Should have NamingReportGenerator class."""
        from src.governance.naming_report_generator import NamingReportGenerator
        
        generator = NamingReportGenerator()
        assert generator is not None
    
    def test_can_generate_report(self, tmp_path):
        """Should generate violation report."""
        from src.governance.naming_report_generator import NamingReportGenerator
        
        # Create test files
        (tmp_path / "user_service.py").touch()
        (tmp_path / "userService.py").touch()
        
        generator = NamingReportGenerator()
        report = generator.scan_directory(tmp_path)
        
        assert "total_files" in report
        assert "violations" in report
