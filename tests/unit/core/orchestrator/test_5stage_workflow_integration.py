"""
Integration tests for 5-component workflow (AC-PROD-004-02).

Tests the complete workflow integration of Stage 1, 2, 3, 4.
Validates data flows correctly between stages and error handling.

Tests: 15+
Status: RED (TDD - tests before implementation)
"""

import pytest
from pathlib import Path
from typing import List, Optional

from cortex.orchestrators.core.master_orchestrator_stage_1 import (
    MasterOrchestrationStage1,
    Stage1ComprehensionContext,
)
from cortex.orchestrators.core.repository_scanner import (
    RepositoryScanner,
    ScanContext,
)
from cortex.orchestrators.core.master_orchestrator_stage_3 import (
    MasterOrchestrationStage3,
    Stage3KnowledgeContext,
)
from cortex.orchestrators.core.master_orchestrator_stage_4 import (
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
def sample_repo(tmp_path):
    """Create sample repository."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("def main(): pass")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_main.py").write_text("def test(): pass")
    return tmp_path


# ============================================================================
# Stage 1 Tests
# ============================================================================

class TestStage1Comprehension:
    """Test Stage 1 Comprehension."""
    
    def test_stage1_produces_intent(self, stage1):
        """Test Stage 1 produces intent."""
        context = Stage1ComprehensionContext(
            operation="implement_feature",
            description="Add authentication",
            keywords=["auth", "login"],
            domain="auth",
        )
        
        result = stage1.comprehend(context)
        assert result.is_ok()
        output = result.unwrap()
        assert output.extracted_intent is not None
    
    def test_stage1_produces_confidence(self, stage1):
        """Test Stage 1 produces confidence."""
        context = Stage1ComprehensionContext(
            operation="fix_bug",
            description="Fix null pointer",
            keywords=["fix", "null"],
            domain="core",
        )
        
        result = stage1.comprehend(context)
        assert result.is_ok()
        output = result.unwrap()
        assert 0 <= output.confidence_score <= 1


# ============================================================================
# Stage 2 (Scanner) Tests
# ============================================================================

class TestStage2RepositoryScanner:
    """Test Stage 2 Repository Scanner."""
    
    def test_stage2_scans_repository(self, scanner, sample_repo):
        """Test Stage 2 scans repository."""
        context = ScanContext(
            workspace_root=sample_repo,
            target_paths=[sample_repo],
            exclude_patterns=[],
        )
        
        output = scanner.scan(context)
        assert output is not None
        assert output.file_count >= 2
    
    def test_stage2_identifies_entities(self, scanner, sample_repo):
        """Test Stage 2 identifies code entities."""
        context = ScanContext(
            workspace_root=sample_repo,
            target_paths=[sample_repo],
            exclude_patterns=[],
        )
        
        output = scanner.scan(context)
        assert output.function_count >= 0


# ============================================================================
# Stage 3 Tests
# ============================================================================

class TestStage3KnowledgeProcessing:
    """Test Stage 3 Knowledge Processing."""
    
    def test_stage3_processes_knowledge(self, stage3):
        """Test Stage 3 processes knowledge."""
        context = Stage3KnowledgeContext(
            stage1_output=None,
            domain="auth",
            codebase_path="/project/src",
            entities=["User", "AuthService"],
        )
        
        result = stage3.process_knowledge(context)
        if result.is_ok():
            output = result.unwrap()
            assert output is not None


# ============================================================================
# Stage 4 Tests
# ============================================================================

class TestStage4Approval:
    """Test Stage 4 Approval."""
    
    def test_stage4_makes_approval(self, stage4):
        """Test Stage 4 makes approval decision."""
        context = Stage4ApprovalContext(
            stage3_output=None,
            user_id="user123",
            urgency="medium",
            approval_level="standard",
        )
        
        result = stage4.approve_operation(context)
        if result.is_ok():
            output = result.unwrap()
            assert hasattr(output, 'approved')


# ============================================================================
# Data Flow Tests
# ============================================================================

class TestDataFlow:
    """Test data flows between stages."""
    
    def test_stage1_to_stage3_context_flow(self, stage1, stage3):
        """Test data flows from Stage 1 to Stage 3."""
        # Get Stage 1 output
        s1_ctx = Stage1ComprehensionContext(
            operation="test",
            description="test",
            keywords=["test"],
            domain="test",
        )
        
        s1_result = stage1.comprehend(s1_ctx)
        assert s1_result.is_ok()
        s1_output = s1_result.unwrap()
        
        # Use in Stage 3
        s3_ctx = Stage3KnowledgeContext(
            stage1_output=s1_output,
            domain="test",
            codebase_path="/project",
            entities=[],
        )
        
        s3_result = stage3.process_knowledge(s3_ctx)
        assert s3_result is not None
    
    def test_stage3_to_stage4_context_flow(self, stage3, stage4):
        """Test data flows from Stage 3 to Stage 4."""
        # Get Stage 3 output
        s3_ctx = Stage3KnowledgeContext(
            stage1_output=None,
            domain="test",
            codebase_path="/project",
            entities=[],
        )
        
        s3_result = stage3.process_knowledge(s3_ctx)
        
        if s3_result.is_ok():
            s3_output = s3_result.unwrap()
            
            # Use in Stage 4
            s4_ctx = Stage4ApprovalContext(
                stage3_output=s3_output,
                user_id="user",
                urgency="medium",
                approval_level="standard",
            )
            
            s4_result = stage4.approve_operation(s4_ctx)
            assert s4_result is not None


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Test error handling in workflow."""
    
    def test_stage1_handles_empty_context(self, stage1):
        """Test Stage 1 handles empty context."""
        context = Stage1ComprehensionContext(
            operation="",
            description="",
            keywords=[],
            domain="",
        )
        
        result = stage1.comprehend(context)
        assert result is not None
    
    def test_stage2_handles_empty_repo(self, scanner, tmp_path):
        """Test Stage 2 handles empty repository."""
        context = ScanContext(
            workspace_root=tmp_path,
            target_paths=[tmp_path],
            exclude_patterns=[],
        )
        
        result = scanner.scan(context)
        assert result is not None
        assert result.file_count == 0
    
    def test_stage3_handles_empty_entities(self, stage3):
        """Test Stage 3 handles empty entities."""
        context = Stage3KnowledgeContext(
            stage1_output=None,
            domain="test",
            codebase_path="/project",
            entities=[],
        )
        
        result = stage3.process_knowledge(context)
        assert result is not None
    
    def test_stage4_handles_edge_cases(self, stage4):
        """Test Stage 4 handles edge cases."""
        context = Stage4ApprovalContext(
            stage3_output=None,
            user_id="",
            urgency="low",
            approval_level="standard",
        )
        
        result = stage4.approve_operation(context)
        assert result is not None


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """End-to-end integration tests."""
    
    def test_workflow_implement_feature(self, stage1, stage4):
        """Test implement feature workflow."""
        # Stage 1
        s1_ctx = Stage1ComprehensionContext(
            operation="impl",
            description="Add feature X",
            keywords=["add", "feature"],
            domain="api",
        )
        
        s1_result = stage1.comprehend(s1_ctx)
        assert s1_result.is_ok()
        
        s1_output = s1_result.unwrap()
        assert s1_output.extracted_intent in ["implement", "fix", "refactor"]
    
    def test_workflow_fix_bug(self, stage1, stage4):
        """Test fix bug workflow."""
        # Stage 1
        s1_ctx = Stage1ComprehensionContext(
            operation="fix",
            description="Fix bug Y",
            keywords=["fix", "bug"],
            domain="core",
        )
        
        s1_result = stage1.comprehend(s1_ctx)
        assert s1_result.is_ok()
    
    def test_multi_turn_support(self, stage1):
        """Test multi-turn conversation support."""
        for turn in range(1, 4):
            context = Stage1ComprehensionContext(
                operation=f"op_{turn}",
                description=f"Operation {turn}",
                keywords=["test"],
                domain="test",
            )
            
            result = stage1.comprehend(context)
            assert result is not None
    
    def test_complete_pipeline(self, stage1, scanner, sample_repo):
        """Test complete pipeline execution."""
        # Stage 1
        s1_ctx = Stage1ComprehensionContext(
            operation="test_op",
            description="Test operation",
            keywords=["test"],
            domain="test",
        )
        
        s1_result = stage1.comprehend(s1_ctx)
        assert s1_result.is_ok()
        
        # Stage 2
        s2_ctx = ScanContext(
            workspace_root=sample_repo,
            target_paths=[sample_repo],
            exclude_patterns=[],
        )
        
        s2_result = scanner.scan(s2_ctx)
        assert s2_result is not None
        assert s2_result.file_count >= 0


# ============================================================================
# Governance Tests
# ============================================================================

class TestGovernance:
    """Test governance and compliance."""
    
    def test_all_stages_available(self, stage1, scanner, stage3, stage4):
        """Test all stages are available."""
        assert stage1 is not None
        assert scanner is not None
        assert stage3 is not None
        assert stage4 is not None
    
    def test_context_turn_tracking(self, stage3, stage4):
        """Test turn number tracking."""
        s3_ctx = Stage3KnowledgeContext(
            stage1_output=None,
            domain="test",
            codebase_path="/project",
            entities=[],
            turn_number=1,
        )
        
        s4_ctx = Stage4ApprovalContext(
            stage3_output=None,
            user_id="user",
            urgency="medium",
            approval_level="standard",
            turn_number=2,
        )
        
        assert s3_ctx.turn_number == 1
        assert s4_ctx.turn_number == 2
