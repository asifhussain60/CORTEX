"""
RED Phase Tests for CodeReviewOrchestrator
Following TDD methodology: Write failing tests first
"""

import pytest
from pathlib import Path
from typing import List, Dict, Optional
import tempfile
import os

from src.code_review.code_review_orchestrator import (
    AnalysisDepth,
    ReviewIssue,
    CodeReviewReport,
    CodeReviewOrchestrator
)


class TestCodeReviewOrchestrator:
    """Test suite for CodeReviewOrchestrator - RED phase"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            
            # Create sample Python file with issues
            src_dir = workspace / "src"
            src_dir.mkdir()
            
            (src_dir / "example.py").write_text("""
import os
import sys

def process_data(user_input):
    # Security issue: SQL injection risk
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    
    # Performance issue: inefficient loop
    result = []
    for i in range(1000):
        result.append(i * 2)
    
    return query, result

# Maintainability issue: magic number
MAX_RETRIES = 5
""")
            
            yield workspace
    
    def test_orchestrator_initialization(self):
        """Test: CodeReviewOrchestrator initializes with workspace path"""
        # Arrange & Act
        workspace = Path.cwd()
        orchestrator = CodeReviewOrchestrator(workspace)
        
        # Assert
        assert orchestrator is not None
        assert orchestrator.workspace_path == workspace
    
    def test_quick_analysis_depth(self, temp_workspace):
        """Test: Quick analysis only checks changed files (no dependencies)"""
        # Arrange
        orchestrator = CodeReviewOrchestrator(temp_workspace)
        changed_files = [str(temp_workspace / "src" / "example.py")]
        
        # Act
        report = orchestrator.review_pr(
            changed_files=changed_files,
            depth=AnalysisDepth.QUICK
        )
        
        # Assert
        assert report.analysis_depth == AnalysisDepth.QUICK
        assert report.total_files_analyzed == 1  # Only changed file
        assert report.total_issues > 0  # Should detect issues
    
    def test_standard_analysis_depth(self, temp_workspace):
        """Test: Standard analysis includes direct dependencies"""
        # Arrange
        # Create file with dependency
        src_dir = temp_workspace / "src"
        (src_dir / "main.py").write_text("""
from src.example import process_data

def main():
    result = process_data("test")
    print(result)
""")
        
        orchestrator = CodeReviewOrchestrator(temp_workspace)
        changed_files = [str(src_dir / "main.py")]
        
        # Act
        report = orchestrator.review_pr(
            changed_files=changed_files,
            depth=AnalysisDepth.STANDARD
        )
        
        # Assert
        assert report.analysis_depth == AnalysisDepth.STANDARD
        assert report.total_files_analyzed >= 2  # main.py + example.py
    
    def test_deep_analysis_depth(self, temp_workspace):
        """Test: Deep analysis includes test files and indirect dependencies"""
        # Arrange
        # Create test file
        tests_dir = temp_workspace / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_example.py").write_text("""
from src.example import process_data

def test_process_data():
    result = process_data("test")
    assert result is not None
""")
        
        orchestrator = CodeReviewOrchestrator(temp_workspace)
        changed_files = [str(temp_workspace / "src" / "example.py")]
        
        # Act
        report = orchestrator.review_pr(
            changed_files=changed_files,
            depth=AnalysisDepth.DEEP
        )
        
        # Assert
        assert report.analysis_depth == AnalysisDepth.DEEP
        assert report.total_files_analyzed >= 2  # example.py + test file
    
    def test_detect_security_issues(self, temp_workspace):
        """Test: Orchestrator detects security vulnerabilities"""
        # Arrange
        orchestrator = CodeReviewOrchestrator(temp_workspace)
        changed_files = [str(temp_workspace / "src" / "example.py")]
        
        # Act
        report = orchestrator.review_pr(
            changed_files=changed_files,
            depth=AnalysisDepth.QUICK
        )
        
        # Assert
        security_issues = [i for i in report.issues if i.category == "security"]
        assert len(security_issues) > 0  # Should detect SQL injection
        assert any("injection" in i.message.lower() for i in security_issues)
    
    def test_detect_performance_issues(self, temp_workspace):
        """Test: Orchestrator detects performance problems"""
        # Arrange
        orchestrator = CodeReviewOrchestrator(temp_workspace)
        changed_files = [str(temp_workspace / "src" / "example.py")]
        
        # Act
        report = orchestrator.review_pr(
            changed_files=changed_files,
            depth=AnalysisDepth.QUICK
        )
        
        # Assert
        performance_issues = [i for i in report.issues if i.category == "performance"]
        assert len(performance_issues) > 0  # Should detect inefficient loop
    
    def test_detect_maintainability_issues(self, temp_workspace):
        """Test: Orchestrator detects maintainability problems"""
        # Arrange
        orchestrator = CodeReviewOrchestrator(temp_workspace)
        changed_files = [str(temp_workspace / "src" / "example.py")]
        
        # Act
        report = orchestrator.review_pr(
            changed_files=changed_files,
            depth=AnalysisDepth.QUICK
        )
        
        # Assert
        maintainability_issues = [i for i in report.issues if i.category == "maintainability"]
        assert len(maintainability_issues) > 0  # Should detect magic number
    
    def test_issue_severity_classification(self, temp_workspace):
        """Test: Issues are classified by severity (CRITICAL, HIGH, MEDIUM, LOW)"""
        # Arrange
        orchestrator = CodeReviewOrchestrator(temp_workspace)
        changed_files = [str(temp_workspace / "src" / "example.py")]
        
        # Act
        report = orchestrator.review_pr(
            changed_files=changed_files,
            depth=AnalysisDepth.QUICK
        )
        
        # Assert
        assert "CRITICAL" in report.issues_by_severity or "HIGH" in report.issues_by_severity
        assert all(issue.severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"] for issue in report.issues)
    
    def test_report_includes_suggestions(self, temp_workspace):
        """Test: Review issues include actionable suggestions"""
        # Arrange
        orchestrator = CodeReviewOrchestrator(temp_workspace)
        changed_files = [str(temp_workspace / "src" / "example.py")]
        
        # Act
        report = orchestrator.review_pr(
            changed_files=changed_files,
            depth=AnalysisDepth.QUICK
        )
        
        # Assert
        issues_with_suggestions = [i for i in report.issues if i.suggestion is not None]
        assert len(issues_with_suggestions) > 0  # At least some issues should have suggestions
    
    def test_token_count_estimation(self, temp_workspace):
        """Test: Report includes accurate token count estimation"""
        # Arrange
        orchestrator = CodeReviewOrchestrator(temp_workspace)
        changed_files = [str(temp_workspace / "src" / "example.py")]
        
        # Act
        report = orchestrator.review_pr(
            changed_files=changed_files,
            depth=AnalysisDepth.QUICK
        )
        
        # Assert
        assert report.token_count > 0
        assert report.token_count < 10000  # Should be reasonable for small file
    
    def test_execution_time_tracking(self, temp_workspace):
        """Test: Report includes execution time"""
        # Arrange
        orchestrator = CodeReviewOrchestrator(temp_workspace)
        changed_files = [str(temp_workspace / "src" / "example.py")]
        
        # Act
        report = orchestrator.review_pr(
            changed_files=changed_files,
            depth=AnalysisDepth.QUICK
        )
        
        # Assert
        assert report.execution_time_seconds > 0
        assert report.execution_time_seconds < 60  # Should complete in reasonable time
    
    def test_empty_changed_files_list(self, temp_workspace):
        """Test: Handle empty changed files list gracefully"""
        # Arrange
        orchestrator = CodeReviewOrchestrator(temp_workspace)
        
        # Act
        report = orchestrator.review_pr(
            changed_files=[],
            depth=AnalysisDepth.QUICK
        )
        
        # Assert
        assert report.total_files_analyzed == 0
        assert report.total_issues == 0
        assert len(report.issues) == 0
    
    def test_nonexistent_file_handling(self, temp_workspace):
        """Test: Handle nonexistent files gracefully"""
        # Arrange
        orchestrator = CodeReviewOrchestrator(temp_workspace)
        changed_files = [str(temp_workspace / "nonexistent.py")]
        
        # Act
        report = orchestrator.review_pr(
            changed_files=changed_files,
            depth=AnalysisDepth.QUICK
        )
        
        # Assert
        assert report.total_files_analyzed == 0  # Should skip nonexistent files
    
    def test_integrates_with_dependency_crawler(self, temp_workspace):
        """Test: Orchestrator integrates with DependencyCrawler"""
        # Arrange
        # Create file with dependency
        src_dir = temp_workspace / "src"
        (src_dir / "utils.py").write_text("""
def helper():
    return "helper"
""")
        
        (src_dir / "main.py").write_text("""
from src.utils import helper

def main():
    return helper()
""")
        
        orchestrator = CodeReviewOrchestrator(temp_workspace)
        changed_files = [str(src_dir / "main.py")]
        
        # Act
        report = orchestrator.review_pr(
            changed_files=changed_files,
            depth=AnalysisDepth.STANDARD  # Should use DependencyCrawler
        )
        
        # Assert
        assert report.total_files_analyzed >= 2  # main.py + utils.py


class TestAnalysisDepth:
    """Test suite for AnalysisDepth enum"""
    
    def test_analysis_depth_enum_values(self):
        """Test: AnalysisDepth has correct enum values"""
        assert AnalysisDepth.QUICK.value == "quick"
        assert AnalysisDepth.STANDARD.value == "standard"
        assert AnalysisDepth.DEEP.value == "deep"
    
    def test_analysis_depth_from_string(self):
        """Test: Can create AnalysisDepth from string"""
        assert AnalysisDepth("quick") == AnalysisDepth.QUICK
        assert AnalysisDepth("standard") == AnalysisDepth.STANDARD
        assert AnalysisDepth("deep") == AnalysisDepth.DEEP


class TestReviewIssue:
    """Test suite for ReviewIssue dataclass"""
    
    def test_review_issue_creation(self):
        """Test: ReviewIssue can be created with all fields"""
        issue = ReviewIssue(
            severity="HIGH",
            category="security",
            file_path="/path/to/file.py",
            line_number=42,
            message="SQL injection vulnerability",
            suggestion="Use parameterized queries"
        )
        
        assert issue.severity == "HIGH"
        assert issue.category == "security"
        assert issue.file_path == "/path/to/file.py"
        assert issue.line_number == 42
        assert issue.message == "SQL injection vulnerability"
        assert issue.suggestion == "Use parameterized queries"
    
    def test_review_issue_optional_fields(self):
        """Test: ReviewIssue works with optional fields as None"""
        issue = ReviewIssue(
            severity="LOW",
            category="style",
            file_path="/path/to/file.py",
            line_number=None,
            message="Missing docstring",
            suggestion=None
        )
        
        assert issue.line_number is None
        assert issue.suggestion is None


class TestCodeReviewReport:
    """Test suite for CodeReviewReport dataclass"""
    
    def test_code_review_report_creation(self):
        """Test: CodeReviewReport can be created with all fields"""
        issues = [
            ReviewIssue("HIGH", "security", "/file.py", 10, "Issue 1", "Fix 1"),
            ReviewIssue("MEDIUM", "performance", "/file.py", 20, "Issue 2", "Fix 2"),
        ]
        
        report = CodeReviewReport(
            analysis_depth=AnalysisDepth.STANDARD,
            total_files_analyzed=5,
            total_issues=2,
            issues_by_severity={"HIGH": 1, "MEDIUM": 1},
            issues=issues,
            token_count=1500,
            execution_time_seconds=2.5
        )
        
        assert report.analysis_depth == AnalysisDepth.STANDARD
        assert report.total_files_analyzed == 5
        assert report.total_issues == 2
        assert report.issues_by_severity == {"HIGH": 1, "MEDIUM": 1}
        assert len(report.issues) == 2
        assert report.token_count == 1500
        assert report.execution_time_seconds == 2.5
