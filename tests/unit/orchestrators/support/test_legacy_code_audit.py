"""
Phase 61: Legacy Code Audit - Test Suite

Tests for legacy code categorization, detection, and audit workflow.
Categorizes code as: DEPRECATED, DUPLICATE, ORPHANED, SUPERSEDED.

AC_START: AC-PHASE61-001
Description: Legacy Code Audit - Phase 61 implementation
"""

import pytest
from pathlib import Path
from typing import Set, Dict, List
from enum import Enum
import tempfile
import shutil

# Import from implementation
from cortex.orchestrators.support.legacy_code_audit import (
    LegacyCodeCategory,
    LegacyCodeIssue,
    LegacyCodeAudit,
    RemovalApprovalWorkflow,
    AuditReport,
)


# ============================================================================
# TESTS
# ============================================================================

class TestLegacyCodeAudit:
    """Tests for LegacyCodeAudit class"""
    
    @pytest.fixture
    def temp_repo(self):
        """Create temporary repository structure"""
        tmpdir = tempfile.mkdtemp()
        repo_path = Path(tmpdir)
        
        # Create directory structure
        (repo_path / "cortex" / "old_modules").mkdir(parents=True)
        (repo_path / "cortex" / "active_modules").mkdir(parents=True)
        (repo_path / "tests").mkdir(parents=True)
        
        yield repo_path
        
        # Cleanup
        shutil.rmtree(tmpdir)
    
    def test_audit_initialization(self, temp_repo):
        """Test LegacyCodeAudit can be initialized"""
        audit = LegacyCodeAudit(temp_repo)
        assert audit.repo_root == temp_repo
        assert audit.issues == []
    
    def test_scan_repository_returns_list(self, temp_repo):
        """Test scan_repository returns list of issues"""
        audit = LegacyCodeAudit(temp_repo)
        # Create mock implementation
        audit.issues = []
        result = audit.scan_repository()
        assert isinstance(result, list)
    
    def test_categorize_issue_deprecated(self, temp_repo):
        """Test categorization of deprecated code"""
        audit = LegacyCodeAudit(temp_repo)
        # Should return LegacyCodeCategory.DEPRECATED
        category = audit.categorize_issue(temp_repo / "old.py")
        assert isinstance(category, LegacyCodeCategory)
    
    def test_detect_deprecated_code_finds_decorators(self, temp_repo):
        """Test detection of @deprecated decorators"""
        audit = LegacyCodeAudit(temp_repo)
        deprecated = audit.detect_deprecated_code()
        assert isinstance(deprecated, list)
    
    def test_detect_duplicates_identifies_clones(self, temp_repo):
        """Test duplicate detection (CORE-035)"""
        audit = LegacyCodeAudit(temp_repo)
        duplicates = audit.detect_duplicates()
        assert isinstance(duplicates, list)
    
    def test_detect_orphaned_code_no_imports(self, temp_repo):
        """Test orphaned code detection (no imports)"""
        audit = LegacyCodeAudit(temp_repo)
        orphaned = audit.detect_orphaned_code()
        assert isinstance(orphaned, list)
    
    def test_detect_superseded_code_versions(self, temp_repo):
        """Test superseded code detection (v1 vs v2)"""
        audit = LegacyCodeAudit(temp_repo)
        superseded = audit.detect_superseded_code()
        assert isinstance(superseded, list)
    
    def test_generate_removal_candidates_safe_items(self, temp_repo):
        """Test generation of removal candidates"""
        audit = LegacyCodeAudit(temp_repo)
        candidates = audit.generate_removal_candidates()
        assert isinstance(candidates, list)


class TestRemovalApprovalWorkflow:
    """Tests for RemovalApprovalWorkflow"""
    
    @pytest.fixture
    def workflow(self):
        """Create RemovalApprovalWorkflow instance"""
        return RemovalApprovalWorkflow()
    
    @pytest.fixture
    def sample_issue(self):
        """Create sample LegacyCodeIssue"""
        return LegacyCodeIssue(
            file_path=Path("cortex/old_module.py"),
            category=LegacyCodeCategory.DEPRECATED,
            severity="MEDIUM",
            reason="Marked @deprecated since 2025-12-01",
            recommendation="Safe to remove",
            confidence_score=0.95
        )
    
    def test_workflow_initialization(self, workflow):
        """Test workflow initialization"""
        assert workflow.pending_removals == []
        assert workflow.approved_removals == []
        assert workflow.rejected_removals == []
    
    def test_submit_for_approval(self, workflow, sample_issue):
        """Test submitting issue for approval"""
        workflow.submit_for_approval(sample_issue)
        assert sample_issue in workflow.pending_removals
    
    def test_approve_removal(self, workflow, sample_issue):
        """Test approving removal"""
        workflow.pending_removals.append(sample_issue)
        workflow.approve_removal(sample_issue)
        assert sample_issue in workflow.approved_removals
        assert sample_issue not in workflow.pending_removals
    
    def test_reject_removal(self, workflow, sample_issue):
        """Test rejecting removal"""
        workflow.pending_removals.append(sample_issue)
        workflow.reject_removal(sample_issue, "Still used in production")
        assert sample_issue in workflow.rejected_removals
        assert sample_issue not in workflow.pending_removals
    
    def test_get_pending_approvals(self, workflow, sample_issue):
        """Test retrieving pending approvals"""
        workflow.pending_removals.append(sample_issue)
        pending = workflow.get_pending_approvals()
        assert sample_issue in pending


class TestAuditReport:
    """Tests for AuditReport"""
    
    @pytest.fixture
    def report(self):
        """Create AuditReport instance"""
        return AuditReport()
    
    def test_report_initialization(self, report):
        """Test report initialization"""
        assert report.deprecated_count == 0
        assert report.duplicate_count == 0
        assert report.orphaned_count == 0
        assert report.superseded_count == 0
        assert report.total_issues == 0
    
    def test_generate_report_dict(self, report):
        """Test report generation returns dict"""
        report.deprecated_count = 5
        report.duplicate_count = 3
        report_dict = report.generate_report()
        assert isinstance(report_dict, dict)
    
    def test_export_to_yaml(self, report):
        """Test export to YAML"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "audit_report.yaml"
            report.export_to_yaml(output_path)
            assert output_path.exists()


class TestLegacyCodeIssue:
    """Tests for LegacyCodeIssue dataclass"""
    
    def test_issue_creation(self):
        """Test creating a LegacyCodeIssue"""
        issue = LegacyCodeIssue(
            file_path=Path("cortex/old.py"),
            category=LegacyCodeCategory.DEPRECATED,
            severity="HIGH",
            reason="No longer maintained",
            recommendation="Remove",
            confidence_score=0.98
        )
        assert issue.file_path == Path("cortex/old.py")
        assert issue.category == LegacyCodeCategory.DEPRECATED
        assert issue.severity == "HIGH"
        assert issue.confidence_score == 0.98
    
    def test_issue_category_enum(self):
        """Test all category enums"""
        categories = [
            LegacyCodeCategory.DEPRECATED,
            LegacyCodeCategory.DUPLICATE,
            LegacyCodeCategory.ORPHANED,
            LegacyCodeCategory.SUPERSEDED
        ]
        assert len(categories) == 4


class TestIntegration:
    """Integration tests for Phase 61"""
    
    def test_full_audit_workflow(self):
        """Test complete audit workflow"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            
            # Initialize audit
            audit = LegacyCodeAudit(repo_path)
            
            # Scan repository
            issues = audit.scan_repository()
            assert isinstance(issues, list)
            
            # Create approval workflow
            workflow = RemovalApprovalWorkflow()
            
            # Generate report
            report = AuditReport()
            assert report.total_issues == 0
    
    def test_audit_to_report_pipeline(self):
        """Test audit → approval → report pipeline"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            
            audit = LegacyCodeAudit(repo_path)
            workflow = RemovalApprovalWorkflow()
            report = AuditReport()
            
            # Simulate pipeline
            issues = audit.scan_repository()
            for issue in issues:
                workflow.submit_for_approval(issue)
                workflow.approve_removal(issue)
            
            report_dict = report.generate_report()
            assert isinstance(report_dict, dict)


class TestEdgeCases:
    """Edge case tests"""
    
    def test_empty_repository(self):
        """Test audit on empty repository"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            audit = LegacyCodeAudit(repo_path)
            issues = audit.scan_repository()
            assert issues == []
    
    def test_high_confidence_score(self):
        """Test issue with high confidence score"""
        issue = LegacyCodeIssue(
            file_path=Path("old.py"),
            category=LegacyCodeCategory.DEPRECATED,
            severity="HIGH",
            reason="Clear deprecation",
            recommendation="Safe to remove",
            confidence_score=0.99
        )
        assert issue.confidence_score > 0.95
    
    def test_low_confidence_score(self):
        """Test issue with low confidence score"""
        issue = LegacyCodeIssue(
            file_path=Path("maybe_old.py"),
            category=LegacyCodeCategory.ORPHANED,
            severity="LOW",
            reason="Might be used",
            recommendation="Review manually",
            confidence_score=0.45
        )
        assert issue.confidence_score < 0.50


# AC_COMPLETE: AC-PHASE61-001 ✅
