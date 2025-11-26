"""
Unit tests for CodeReviewOrchestrator

Tests cover:
- Orchestrator initialization
- Interactive intake workflow
- Message parsing and info extraction
- Context building strategy
- Report generation
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime

from src.orchestrators.code_review_orchestrator import (
    CodeReviewOrchestrator,
    PRInfo,
    ReviewConfig,
    ReviewDepth,
    FocusArea,
    CodeReviewResult
)


class TestCodeReviewOrchestrator:
    """Test suite for CodeReviewOrchestrator."""
    
    @pytest.fixture
    def temp_cortex_root(self):
        """Create temporary CORTEX root directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            
            # Create required directory structure
            (cortex_root / "cortex-brain" / "documents" / "reports" / "code-review").mkdir(parents=True)
            
            # Create minimal config file
            config = {
                "code_review": {
                    "enabled": True
                }
            }
            with open(cortex_root / "cortex.config.json", 'w') as f:
                json.dump(config, f)
            
            yield str(cortex_root)
    
    @pytest.fixture
    def orchestrator(self, temp_cortex_root):
        """Create orchestrator instance."""
        return CodeReviewOrchestrator(temp_cortex_root)
    
    def test_initialization(self, orchestrator, temp_cortex_root):
        """Test orchestrator initializes correctly."""
        assert orchestrator.cortex_root == Path(temp_cortex_root)
        assert orchestrator.reports_dir.exists()
        assert isinstance(orchestrator.config, dict)
    
    def test_initiate_review_basic(self, orchestrator):
        """Test basic review initiation."""
        result = orchestrator.initiate_review("code review")
        
        assert result["phase"] == "intake"
        assert result["status"] == "awaiting_user_input"
        assert "questions" in result
        assert "pr_information" in result["questions"]
        assert "review_depth" in result["questions"]
        assert "focus_areas" in result["questions"]
    
    def test_extract_pr_id_from_message(self, orchestrator):
        """Test PR ID extraction from user message."""
        # Test PR number extraction
        extracted = orchestrator._extract_info_from_message("Review PR 1234")
        assert extracted["pr_id"] == "1234"
        
        # Test PR with hash
        extracted = orchestrator._extract_info_from_message("Review PR #5678")
        assert extracted["pr_id"] == "5678"
        
        # Test PR with colon
        extracted = orchestrator._extract_info_from_message("Review PR: 9012")
        assert extracted["pr_id"] == "9012"
    
    def test_extract_ado_link_from_message(self, orchestrator):
        """Test ADO link extraction from user message."""
        message = "Review https://dev.azure.com/org/project/_git/repo/pullrequest/1234"
        extracted = orchestrator._extract_info_from_message(message)
        
        assert "pr_link" in extracted
        assert extracted["pr_id"] == "1234"
        assert "dev.azure.com" in extracted["pr_link"]
    
    def test_extract_depth_from_message(self, orchestrator):
        """Test review depth extraction from user message."""
        # Test quick depth
        extracted = orchestrator._extract_info_from_message("Quick review of PR 1234")
        assert extracted["depth"] == "quick"
        
        # Test standard depth
        extracted = orchestrator._extract_info_from_message("Standard review please")
        assert extracted["depth"] == "standard"
        
        # Test deep depth
        extracted = orchestrator._extract_info_from_message("Deep review with security focus")
        assert extracted["depth"] == "deep"
    
    def test_extract_focus_areas_from_message(self, orchestrator):
        """Test focus area extraction from user message."""
        # Test single focus
        extracted = orchestrator._extract_info_from_message("Review with security focus")
        assert "security" in extracted["focus_areas"]
        
        # Test multiple focus
        extracted = orchestrator._extract_info_from_message(
            "Review focusing on security and performance"
        )
        assert "security" in extracted["focus_areas"]
        assert "performance" in extracted["focus_areas"]
        
        # Test all areas
        extracted = orchestrator._extract_info_from_message("Review all areas")
        assert extracted["focus_areas"] == ["all"]
    
    def test_build_context_changed_files_only(self, orchestrator):
        """Test context building with only changed files."""
        pr_info = PRInfo(
            pr_id="1234",
            changed_files=["src/models/user.py", "src/controllers/auth.py"]
        )
        config = ReviewConfig(
            depth=ReviewDepth.QUICK,
            focus_areas=[FocusArea.ALL],
            include_tests=False,
            include_indirect_deps=False
        )
        
        context_files = orchestrator._build_context(pr_info, config)
        
        assert len(context_files) == 2
        assert "src/models/user.py" in context_files
        assert "src/controllers/auth.py" in context_files
    
    def test_build_context_no_duplicates(self, orchestrator):
        """Test context building removes duplicates."""
        pr_info = PRInfo(
            pr_id="1234",
            changed_files=[
                "src/models/user.py",
                "src/models/user.py",  # Duplicate
                "src/controllers/auth.py"
            ]
        )
        config = ReviewConfig(
            depth=ReviewDepth.QUICK,
            focus_areas=[FocusArea.ALL]
        )
        
        context_files = orchestrator._build_context(pr_info, config)
        
        # Should have only 2 unique files
        assert len(context_files) == 2
    
    def test_calculate_risk_score_no_issues(self, orchestrator):
        """Test risk score calculation with no issues."""
        analysis_results = {"issues": []}
        risk_score = orchestrator._calculate_risk_score(analysis_results)
        
        assert risk_score == 0
    
    def test_calculate_risk_score_with_issues(self, orchestrator):
        """Test risk score calculation with issues."""
        analysis_results = {
            "issues": [
                {"severity": "critical", "title": "SQL Injection"},
                {"severity": "critical", "title": "XSS Vulnerability"},
                {"severity": "warning", "title": "Long method"},
                {"severity": "warning", "title": "Duplicate code"},
                {"severity": "info", "title": "Consider refactoring"}
            ]
        }
        risk_score = orchestrator._calculate_risk_score(analysis_results)
        
        # 2 critical (20 each) + 2 warnings (5 each) = 50
        assert risk_score == 50
    
    def test_calculate_risk_score_capped_at_100(self, orchestrator):
        """Test risk score caps at 100."""
        analysis_results = {
            "issues": [
                {"severity": "critical", "title": f"Issue {i}"}
                for i in range(10)  # 10 critical = 200 points
            ]
        }
        risk_score = orchestrator._calculate_risk_score(analysis_results)
        
        assert risk_score == 100  # Capped
    
    def test_generate_executive_summary_high_risk(self, orchestrator):
        """Test executive summary for high risk PR."""
        pr_info = PRInfo(pr_id="1234")
        analysis_results = {
            "issues": [
                {"severity": "critical", "title": "Issue 1"},
                {"severity": "critical", "title": "Issue 2"},
                {"severity": "critical", "title": "Issue 3"}
            ]
        }
        risk_score = 60
        
        summary = orchestrator._generate_executive_summary(
            pr_info, risk_score, analysis_results
        )
        
        assert "PR #1234" in summary
        assert "60/100" in summary
        assert "3 critical issues" in summary
    
    def test_categorize_issues(self, orchestrator):
        """Test issue categorization."""
        issues = [
            {"severity": "critical", "title": "Critical 1"},
            {"severity": "critical", "title": "Critical 2"},
            {"severity": "warning", "title": "Warning 1"},
            {"severity": "info", "title": "Info 1"},
            {"severity": "info", "title": "Info 2"}
        ]
        
        critical, warnings, suggestions = orchestrator._categorize_issues(issues)
        
        assert len(critical) == 2
        assert len(warnings) == 1
        assert len(suggestions) == 2
    
    def test_format_report_markdown(self, orchestrator):
        """Test Markdown report formatting with Phase 4 enhancements."""
        pr_info = PRInfo(pr_id="1234", title="Add authentication")
        config = ReviewConfig(
            depth=ReviewDepth.STANDARD,
            focus_areas=[FocusArea.SECURITY, FocusArea.TESTS]
        )
        result = CodeReviewResult(
            pr_info=pr_info,
            config=config,
            executive_summary="Test summary",
            risk_score=45,
            critical_issues=[
                {
                    "title": "SQL Injection",
                    "description": "User input not sanitized",
                    "file_path": "src/models.py",
                    "line_number": 42,
                    "code_snippet": 'query = "SELECT * FROM users WHERE id = " + user_id',
                    "fix_suggestion": "Use parameterized queries",
                    "confidence_score": 0.95,
                    "risk": "HIGH",
                    "category": "security"
                }
            ],
            warnings=[
                {
                    "title": "Long method",
                    "description": "Method has 150 lines",
                    "file_path": "src/service.py",
                    "line_number": 100
                }
            ],
            suggestions=[
                {
                    "title": "Add docstring",
                    "description": "Missing documentation",
                    "file_path": "src/utils.py"
                }
            ],
            context_files=["file1.py", "file2.py"],
            token_usage=5000,
            analysis_duration_ms=1500.0
        )
        
        markdown = orchestrator._format_report_markdown(result)
        
        # Phase 4 validations
        # Check enhanced header with emojis
        assert "# 🔍 Code Review Report - PR #1234" in markdown
        
        # Priority matrix
        assert "## 📋 Priority Matrix" in markdown
        assert "| 🔴 **Critical** | 1 | Must fix before merge |" in markdown
        assert "| 🟡 **Warning** | 1 | Should fix soon |" in markdown
        assert "| 🔵 **Suggestion** | 1 | Nice to have |" in markdown
        
        # Risk visualization (medium risk)
        assert "## 🎯 Risk Assessment" in markdown
        assert "🟡" in markdown  # Medium risk emoji
        assert "45/100" in markdown
        assert "(Medium Risk)" in markdown
        
        # Collapsible sections
        assert "<details>" in markdown
        assert "Click to expand" in markdown
        
        # Fix template for SQL injection
        assert "💡 Click for copy-paste fix template" in markdown
        assert "```python" in markdown
        assert "# Before (problematic):" in markdown
        assert "# After (fixed):" in markdown
        assert "cursor.execute(query, (user_id,))" in markdown
        
        # Confidence scores
        assert "**Confidence:** 95%" in markdown
        
        # Developer disclaimer
        assert "## ⚠️ Developer Disclaimer" in markdown
        assert "False positives (~15-20% industry standard)" in markdown
        assert "YOU MUST:" in markdown
        
        # Analysis context table
        assert "## 📈 Analysis Context" in markdown
        assert "| Metric | Value |" in markdown
        assert "| Files Analyzed | 2 |" in markdown
        
        # Legacy checks still valid
        assert "SQL Injection" in markdown
        assert "Long method" in markdown
        assert "Add docstring" in markdown
    
    def test_execute_review_end_to_end(self, orchestrator):
        """Test complete review execution."""
        pr_info = PRInfo(
            pr_id="1234",
            changed_files=["src/auth.py", "src/user.py"]
        )
        config = ReviewConfig(
            depth=ReviewDepth.QUICK,
            focus_areas=[FocusArea.ALL]
        )
        
        result = orchestrator.execute_review(pr_info, config)
        
        assert result.pr_info.pr_id == "1234"
        assert result.config.depth == ReviewDepth.QUICK
        assert result.risk_score >= 0
        assert result.risk_score <= 100
        assert len(result.context_files) == 2
        assert result.analysis_duration_ms > 0


class TestPRInfo:
    """Test PRInfo data class."""
    
    def test_pr_info_creation(self):
        """Test creating PRInfo instance."""
        pr_info = PRInfo(
            pr_id="1234",
            pr_link="https://dev.azure.com/org/project/_git/repo/pullrequest/1234",
            title="Add authentication"
        )
        
        assert pr_info.pr_id == "1234"
        assert "dev.azure.com" in pr_info.pr_link
        assert pr_info.title == "Add authentication"
        assert isinstance(pr_info.timestamp, datetime)


class TestReviewConfig:
    """Test ReviewConfig data class."""
    
    def test_review_config_defaults(self):
        """Test ReviewConfig default values."""
        config = ReviewConfig(
            depth=ReviewDepth.STANDARD,
            focus_areas=[FocusArea.ALL]
        )
        
        assert config.depth == ReviewDepth.STANDARD
        assert config.max_files == 50
        assert config.token_budget == 10000
        assert config.include_tests is True
        assert config.include_indirect_deps is False


class TestEnums:
    """Test enum definitions."""
    
    def test_review_depth_enum(self):
        """Test ReviewDepth enum values."""
        assert ReviewDepth.QUICK.value == "quick"
        assert ReviewDepth.STANDARD.value == "standard"
        assert ReviewDepth.DEEP.value == "deep"
    
    def test_focus_area_enum(self):
        """Test FocusArea enum values."""
        assert FocusArea.SECURITY.value == "security"
        assert FocusArea.PERFORMANCE.value == "performance"
        assert FocusArea.MAINTAINABILITY.value == "maintainability"
        assert FocusArea.TESTS.value == "tests"
        assert FocusArea.ARCHITECTURE.value == "architecture"
        assert FocusArea.ALL.value == "all"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
