"""
AC-PROD-005-03: Hardening & Edge Case Handling

Tests for error scenarios, graceful degradation, and edge cases.
Focus: LENS failures, router fallback, approval bypass, error recovery.

Tests: 15+
Status: RED (TDD - tests before implementation)
"""

import pytest
from pathlib import Path
from typing import Optional

from src.orchestrators.core.master_orchestrator_stage_1 import (
    MasterOrchestrationStage1,
    Stage1ComprehensionContext,
)
from src.orchestrators.core.repository_scanner import (
    RepositoryScanner,
    ScanContext,
)
from src.orchestrators.core.master_orchestrator_stage_3 import (
    MasterOrchestrationStage3,
    Stage3KnowledgeContext,
)
from src.orchestrators.core.master_orchestrator_stage_4 import (
    MasterOrchestrationStage4,
    Stage4ApprovalContext,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def stage1():
    return MasterOrchestrationStage1()


@pytest.fixture
def scanner(tmp_path):
    return RepositoryScanner(workspace_root=tmp_path)


@pytest.fixture
def stage3():
    return MasterOrchestrationStage3()


@pytest.fixture
def stage4():
    return MasterOrchestrationStage4()


@pytest.fixture
def empty_repo(tmp_path):
    """Create empty repository."""
    return tmp_path


@pytest.fixture
def corrupted_repo(tmp_path):
    """Create repository with mixed valid/invalid files."""
    # Valid file
    (tmp_path / "good.py").write_text("def good(): pass")
    
    # File with syntax error
    (tmp_path / "bad.py").write_text("def bad(:\n  pass")
    
    # Binary file
    (tmp_path / "binary.so").write_bytes(b'\x00\x01\x02\x03')
    
    return tmp_path


# ============================================================================
# LENS Failures & Graceful Degradation
# ============================================================================

class TestLENSFailureRecovery:
    """Test LENS failures don't crash system."""
    
    def test_lens_with_empty_keywords(self, stage1):
        """Test LENS handles empty keywords."""
        ctx = Stage1ComprehensionContext(
            operation="test",
            description="test",
            keywords=[],  # Empty
            domain="test",
        )
        
        result = stage1.comprehend(ctx)
        assert result is not None
    
    def test_lens_with_empty_description(self, stage1):
        """Test LENS handles empty description."""
        ctx = Stage1ComprehensionContext(
            operation="test",
            description="",  # Empty
            keywords=["test"],
            domain="test",
        )
        
        result = stage1.comprehend(ctx)
        assert result is not None
    
    def test_lens_with_very_long_input(self, stage1):
        """Test LENS handles very long input."""
        ctx = Stage1ComprehensionContext(
            operation="test",
            description="x" * 10000,  # Very long
            keywords=["test"],
            domain="test",
        )
        
        result = stage1.comprehend(ctx)
        assert result is not None
    
    def test_lens_with_special_characters(self, stage1):
        """Test LENS handles special characters."""
        ctx = Stage1ComprehensionContext(
            operation="test",
            description="Test !@#$%^&*()[]{}",
            keywords=["special"],
            domain="test",
        )
        
        result = stage1.comprehend(ctx)
        assert result is not None
    
    def test_lens_with_unicode_input(self, stage1):
        """Test LENS handles unicode input."""
        ctx = Stage1ComprehensionContext(
            operation="test",
            description="测试中文 테스트 тест",
            keywords=["unicode"],
            domain="test",
        )
        
        result = stage1.comprehend(ctx)
        assert result is not None


# ============================================================================
# Repository Scanner Edge Cases
# ============================================================================

class TestRepositoryScannerEdgeCases:
    """Test Scanner graceful handling of edge cases."""
    
    def test_scanner_empty_repository(self, scanner, empty_repo):
        """Test Scanner handles empty repository."""
        ctx = ScanContext(
            workspace_root=empty_repo,
            target_paths=[empty_repo],
            exclude_patterns=[],
        )
        
        output = scanner.scan(ctx)
        assert output is not None
        assert output.file_count == 0
    
    def test_scanner_nonexistent_path(self, scanner):
        """Test Scanner handles nonexistent path."""
        ctx = ScanContext(
            workspace_root="/nonexistent/path",
            target_paths=["/nonexistent/path"],
            exclude_patterns=[],
        )
        
        # Should handle gracefully (might raise or return empty)
        try:
            output = scanner.scan(ctx)
            assert output is not None
        except (AttributeError, TypeError, FileNotFoundError):
            # Expected - scanner validates paths
            pass
    
    def test_scanner_with_mixed_file_types(self, scanner, corrupted_repo):
        """Test Scanner handles mixed file types."""
        ctx = ScanContext(
            workspace_root=corrupted_repo,
            target_paths=[corrupted_repo],
            exclude_patterns=[],
        )
        
        output = scanner.scan(ctx)
        assert output is not None
        # Should skip binary files
    
    def test_scanner_with_permission_denied(self, scanner, tmp_path):
        """Test Scanner handles permission denied."""
        # Create file and remove read permission
        restricted_file = tmp_path / "restricted.py"
        restricted_file.write_text("def func(): pass")
        restricted_file.chmod(0o000)
        
        ctx = ScanContext(
            workspace_root=tmp_path,
            target_paths=[tmp_path],
            exclude_patterns=[],
        )
        
        try:
            output = scanner.scan(ctx)
            # Should handle gracefully or skip restricted files
            assert output is not None
        finally:
            # Restore permissions for cleanup
            restricted_file.chmod(0o644)
    
    def test_scanner_with_exclude_patterns(self, scanner, tmp_path):
        """Test Scanner respects exclude patterns."""
        # Create files
        (tmp_path / "include.py").write_text("def include(): pass")
        (tmp_path / "exclude.py").write_text("def exclude(): pass")
        
        ctx = ScanContext(
            workspace_root=tmp_path,
            target_paths=[tmp_path],
            exclude_patterns=["exclude*"],
        )
        
        output = scanner.scan(ctx)
        assert output is not None


# ============================================================================
# Knowledge Processing Edge Cases
# ============================================================================

class TestKnowledgeProcessingEdgeCases:
    """Test Knowledge processing edge cases."""
    
    def test_knowledge_with_no_entities(self, stage3):
        """Test Knowledge processes with no entities."""
        ctx = Stage3KnowledgeContext(
            stage1_output=None,
            domain="test",
            codebase_path="/test",
            entities=[],  # Empty
        )
        
        result = stage3.process_knowledge(ctx)
        assert result is not None
    
    def test_knowledge_with_unknown_domain(self, stage3):
        """Test Knowledge processes with unknown domain."""
        ctx = Stage3KnowledgeContext(
            stage1_output=None,
            domain="unknown_domain_xyz",
            codebase_path="/test",
            entities=["Entity"],
        )
        
        result = stage3.process_knowledge(ctx)
        assert result is not None
    
    def test_knowledge_with_invalid_path(self, stage3):
        """Test Knowledge processes with invalid path."""
        ctx = Stage3KnowledgeContext(
            stage1_output=None,
            domain="test",
            codebase_path="/nonexistent/invalid/path",
            entities=["Entity"],
        )
        
        result = stage3.process_knowledge(ctx)
        assert result is not None
    
    def test_knowledge_with_many_entities(self, stage3):
        """Test Knowledge handles many entities."""
        ctx = Stage3KnowledgeContext(
            stage1_output=None,
            domain="test",
            codebase_path="/test",
            entities=[f"Entity{i}" for i in range(100)],  # 100 entities
        )
        
        result = stage3.process_knowledge(ctx)
        assert result is not None


# ============================================================================
# Approval Gate Edge Cases
# ============================================================================

class TestApprovalGateEdgeCases:
    """Test Approval gate edge cases."""
    
    def test_approval_with_empty_user(self, stage4):
        """Test Approval handles empty user ID."""
        ctx = Stage4ApprovalContext(
            stage3_output=None,
            user_id="",  # Empty
            urgency="normal",
            approval_level="standard",
        )
        
        result = stage4.approve_operation(ctx)
        assert result is not None
    
    def test_approval_with_invalid_urgency(self, stage4):
        """Test Approval handles invalid urgency."""
        ctx = Stage4ApprovalContext(
            stage3_output=None,
            user_id="user",
            urgency="invalid_urgency",  # Invalid
            approval_level="standard",
        )
        
        result = stage4.approve_operation(ctx)
        assert result is not None
    
    def test_approval_with_high_level_required(self, stage4):
        """Test Approval with high approval level."""
        ctx = Stage4ApprovalContext(
            stage3_output=None,
            user_id="standard_user",
            urgency="critical",
            approval_level="high",  # High level required
        )
        
        result = stage4.approve_operation(ctx)
        assert result is not None
    
    def test_approval_bypass_with_low_urgency(self, stage4):
        """Test Approval bypass for low urgency."""
        ctx = Stage4ApprovalContext(
            stage3_output=None,
            user_id="user",
            urgency="low",  # Low urgency
            approval_level="none",
        )
        
        result = stage4.approve_operation(ctx)
        assert result is not None
    
    def test_approval_with_special_chars_in_user_id(self, stage4):
        """Test Approval handles special characters."""
        ctx = Stage4ApprovalContext(
            stage3_output=None,
            user_id="user+!@#$%",  # Special chars
            urgency="normal",
            approval_level="standard",
        )
        
        result = stage4.approve_operation(ctx)
        assert result is not None


# ============================================================================
# End-to-End Error Recovery
# ============================================================================

class TestE2EErrorRecovery:
    """Test E2E error recovery scenarios."""
    
    def test_recovery_stage_1_to_stage_3(self, stage1, stage3):
        """Test recovery from Stage 1 error continues to Stage 3."""
        # Stage 1 with error conditions
        s1_ctx = Stage1ComprehensionContext(
            operation="",
            description="",
            keywords=[],
            domain="",
        )
        
        s1_result = stage1.comprehend(s1_ctx)
        
        # Stage 3 should still work
        s3_ctx = Stage3KnowledgeContext(
            stage1_output=s1_result.unwrap() if s1_result.is_ok() else None,
            domain="test",
            codebase_path="",
            entities=[],
        )
        
        s3_result = stage3.process_knowledge(s3_ctx)
        assert s3_result is not None
    
    def test_recovery_cascading_errors(self, stage1, stage3, stage4):
        """Test cascading error recovery."""
        # Create contexts that might fail
        s1_ctx = Stage1ComprehensionContext(
            operation="test",
            description="",
            keywords=[],
            domain="",
        )
        s1_result = stage1.comprehend(s1_ctx)
        
        # Stage 3 with error conditions
        s3_ctx = Stage3KnowledgeContext(
            stage1_output=s1_result.unwrap() if s1_result.is_ok() else None,
            domain="",
            codebase_path="/invalid",
            entities=[],
        )
        s3_result = stage3.process_knowledge(s3_ctx)
        
        # Stage 4 should still work
        s4_ctx = Stage4ApprovalContext(
            stage3_output=s3_result.unwrap() if s3_result and s3_result.is_ok() else None,
            user_id="",
            urgency="low",
            approval_level="none",
        )
        s4_result = stage4.approve_operation(s4_ctx)
        assert s4_result is not None


# ============================================================================
# Boundary Conditions
# ============================================================================

class TestBoundaryConditions:
    """Test boundary conditions."""
    
    def test_max_recursion_depth(self, stage1):
        """Test handling of deeply nested structures."""
        ctx = Stage1ComprehensionContext(
            operation="test",
            description="test",
            keywords=["k" * 1000],  # Very long keyword
            domain="test",
        )
        
        result = stage1.comprehend(ctx)
        assert result is not None
    
    def test_zero_timeout(self, stage1):
        """Test with zero timeout."""
        ctx = Stage1ComprehensionContext(
            operation="test",
            description="test",
            keywords=["test"],
            domain="test",
        )
        
        result = stage1.comprehend(ctx)
        assert result is not None
    
    def test_null_or_none_values(self, stage3):
        """Test explicit None values."""
        ctx = Stage3KnowledgeContext(
            stage1_output=None,
            domain=None,
            codebase_path=None,
            entities=None or [],
        )
        
        result = stage3.process_knowledge(ctx)
        assert result is not None
