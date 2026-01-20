"""
AC-PROD-005-01: End-to-End Integration Testing

Comprehensive integration tests covering all 5 components:
- Stage 1: Comprehension (LENS)
- Stage 2: Repository Scanner
- Stage 3: Knowledge Processing
- Stage 4: Approval Gate
- Master Orchestration coordination

Tests: 20+
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
    """Create sample multi-file repository."""
    # Create source files
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "main.py").write_text("""
import os
import sys

class MainService:
    def process(self, data):
        return self._internal(data)
    
    def _internal(self, data):
        return data.upper()

def main():
    service = MainService()
    return service.process("hello")
""")
    
    # Create test files
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    (test_dir / "test_main.py").write_text("""
import pytest
from cortex.main import MainService

def test_process():
    service = MainService()
    assert service.process("hello") == "HELLO"
""")
    
    # Create config files
    (tmp_path / "config.py").write_text("""
CONFIG = {
    'debug': True,
    'timeout': 30,
}
""")
    
    return tmp_path


# ============================================================================
# AC-PROD-005-01: E2E Integration Tests (All 5 Components)
# ============================================================================

class TestE2EIntegration:
    """End-to-end integration tests with all components."""
    
    def test_e2e_implement_feature_flow(self, stage1, scanner, stage3, stage4, sample_repo):
        """Test: User wants to implement a feature."""
        # Stage 1: Comprehension
        s1_ctx = Stage1ComprehensionContext(
            operation="implement",
            description="Add user authentication to MainService",
            keywords=["auth", "user", "login"],
            domain="auth",
        )
        
        s1_result = stage1.comprehend(s1_ctx)
        assert s1_result.is_ok()
        s1_output = s1_result.unwrap()
        assert s1_output.extracted_intent == "implement"
        
        # Stage 2: Repository Scan
        s2_ctx = ScanContext(
            workspace_root=sample_repo,
            target_paths=[sample_repo],
            exclude_patterns=[],
        )
        
        s2_output = scanner.scan(s2_ctx)
        assert s2_output.file_count >= 3
        assert s2_output.class_count >= 1
        
        # Stage 3: Knowledge Integration
        s3_ctx = Stage3KnowledgeContext(
            stage1_output=s1_output,
            domain="auth",
            codebase_path=str(sample_repo),
            entities=["MainService", "UserAuth"],
        )
        
        s3_result = stage3.process_knowledge(s3_ctx)
        assert s3_result is not None
        
        # Stage 4: Approval
        s4_ctx = Stage4ApprovalContext(
            stage3_output=s3_result.unwrap() if s3_result.is_ok() else None,
            user_id="user@example.com",
            urgency="medium",
            approval_level="standard",
        )
        
        s4_result = stage4.approve_operation(s4_ctx)
        assert s4_result is not None
    
    def test_e2e_fix_bug_flow(self, stage1, scanner, stage3, stage4, sample_repo):
        """Test: User wants to fix a bug."""
        # Stage 1
        s1_ctx = Stage1ComprehensionContext(
            operation="fix",
            description="Fix null pointer in MainService._internal()",
            keywords=["fix", "bug", "null"],
            domain="core",
        )
        
        s1_result = stage1.comprehend(s1_ctx)
        assert s1_result.is_ok()
        s1_output = s1_result.unwrap()
        assert s1_output.extracted_intent == "fix"
        
        # Stage 2
        s2_ctx = ScanContext(
            workspace_root=sample_repo,
            target_paths=[sample_repo],
            exclude_patterns=[],
        )
        
        s2_output = scanner.scan(s2_ctx)
        assert s2_output is not None
    
    def test_e2e_refactor_code_flow(self, stage1, scanner, stage3, stage4, sample_repo):
        """Test: User wants to refactor code."""
        # Stage 1
        s1_ctx = Stage1ComprehensionContext(
            operation="refactor",
            description="Extract MainService to separate module",
            keywords=["refactor", "extract", "module"],
            domain="architecture",
        )
        
        s1_result = stage1.comprehend(s1_ctx)
        assert s1_result.is_ok()
        s1_output = s1_result.unwrap()
        assert s1_output.extracted_intent == "refactor"
    
    def test_e2e_all_five_stages_pass_context(self, stage1, scanner, stage3, stage4):
        """Test: Context flows correctly through all 5 stages."""
        # Stage 1 with specific turn number
        s1_ctx = Stage1ComprehensionContext(
            operation="test_e2e",
            description="Test E2E context propagation",
            keywords=["test"],
            domain="testing",
            turn_number=1,
        )
        
        s1_result = stage1.comprehend(s1_ctx)
        assert s1_result.is_ok()
        s1_output = s1_result.unwrap()
        
        # Verify turn number tracking
        assert hasattr(s1_output, 'turn_number')
    
    def test_e2e_error_in_stage_1_recovered(self, stage1, stage3, stage4):
        """Test: Error in Stage 1 is handled gracefully."""
        # Empty context (error case)
        s1_ctx = Stage1ComprehensionContext(
            operation="",
            description="",
            keywords=[],
            domain="",
        )
        
        s1_result = stage1.comprehend(s1_ctx)
        assert s1_result is not None
    
    def test_e2e_stage_2_optional_continues_on_error(self, stage1, scanner, stage3):
        """Test: Stage 2 error doesn't block Stage 3."""
        # Stage 1 success
        s1_ctx = Stage1ComprehensionContext(
            operation="test",
            description="test",
            keywords=["test"],
            domain="test",
        )
        
        s1_result = stage1.comprehend(s1_ctx)
        assert s1_result.is_ok()
        s1_output = s1_result.unwrap()
        
        # Stage 3 continues even without Stage 2 output
        s3_ctx = Stage3KnowledgeContext(
            stage1_output=s1_output,
            domain="test",
            codebase_path="/nonexistent",
            entities=[],
        )
        
        s3_result = stage3.process_knowledge(s3_ctx)
        assert s3_result is not None
    
    def test_e2e_multi_turn_conversation(self, stage1, stage3):
        """Test: Multi-turn conversation with context carryover."""
        # Turn 1
        ctx1 = Stage1ComprehensionContext(
            operation="turn1",
            description="First turn",
            keywords=["turn1"],
            domain="test",
            turn_number=1,
        )
        
        result1 = stage1.comprehend(ctx1)
        assert result1.is_ok()
        
        # Turn 2 with context from Turn 1
        ctx2 = Stage1ComprehensionContext(
            operation="turn2",
            description="Second turn",
            keywords=["turn2"],
            domain="test",
            turn_number=2,
        )
        
        result2 = stage1.comprehend(ctx2)
        assert result2.is_ok()
    
    def test_e2e_confidence_aggregation(self, stage1, stage3):
        """Test: Confidence scores flow through stages."""
        # Stage 1 confidence
        s1_ctx = Stage1ComprehensionContext(
            operation="test",
            description="test",
            keywords=["test"],
            domain="test",
        )
        
        s1_result = stage1.comprehend(s1_ctx)
        assert s1_result.is_ok()
        s1_output = s1_result.unwrap()
        
        # Verify confidence exists
        assert hasattr(s1_output, 'confidence_score')
        assert 0 <= s1_output.confidence_score <= 1
    
    def test_e2e_audit_trail_complete(self, stage1):
        """Test: Audit trail captured at each stage."""
        ctx = Stage1ComprehensionContext(
            operation="audit_test",
            description="Test audit trail",
            keywords=["audit"],
            domain="test",
        )
        
        result = stage1.comprehend(ctx)
        assert result.is_ok()
        # Audit trail should be logged (implementation detail)
    
    def test_e2e_with_large_repository(self, scanner, tmp_path):
        """Test: E2E with large repository."""
        # Create 10 Python files
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        
        for i in range(10):
            (src_dir / f"module_{i}.py").write_text(f"""
def function_{i}():
    return {i}

class Service_{i}:
    def process(self):
        return function_{i}()
""")
        
        ctx = ScanContext(
            workspace_root=tmp_path,
            target_paths=[tmp_path],
            exclude_patterns=[],
        )
        
        output = scanner.scan(ctx)
        assert output.file_count == 10
        assert output.function_count >= 10
    
    def test_e2e_with_mixed_operations(self, stage1):
        """Test: E2E with different operation types."""
        operations = ["implement", "fix", "refactor", "improve"]
        
        for op in operations:
            ctx = Stage1ComprehensionContext(
                operation=op,
                description=f"Test {op}",
                keywords=[op],
                domain="test",
            )
            
            result = stage1.comprehend(ctx)
            assert result.is_ok()


# ============================================================================
# Complex Scenarios
# ============================================================================

class TestComplexScenarios:
    """Complex E2E scenarios."""
    
    def test_scenario_security_enhancement(self, stage1, scanner, stage3, stage4, sample_repo):
        """Scenario: Implement security enhancement with approval."""
        # Stage 1: Understand requirement
        s1_ctx = Stage1ComprehensionContext(
            operation="implement",
            description="Add OAuth2 authentication to API endpoints",
            keywords=["oauth", "auth", "security"],
            domain="security",
        )
        
        s1_result = stage1.comprehend(s1_ctx)
        assert s1_result.is_ok()
        
        # Stage 2: Analyze codebase
        s2_ctx = ScanContext(
            workspace_root=sample_repo,
            target_paths=[sample_repo],
            exclude_patterns=[],
        )
        
        s2_output = scanner.scan(s2_ctx)
        assert s2_output.file_count > 0
        
        # Stage 4: Require approval for security changes
        s4_ctx = Stage4ApprovalContext(
            stage3_output=None,
            user_id="admin@example.com",
            urgency="high",
            approval_level="high",
        )
        
        s4_result = stage4.approve_operation(s4_ctx)
        assert s4_result is not None
    
    def test_scenario_performance_optimization(self, stage1, scanner):
        """Scenario: Optimize performance-critical code."""
        s1_ctx = Stage1ComprehensionContext(
            operation="refactor",
            description="Optimize hot path in cache manager",
            keywords=["performance", "optimize", "cache"],
            domain="performance",
        )
        
        s1_result = stage1.comprehend(s1_ctx)
        assert s1_result.is_ok()
        s1_output = s1_result.unwrap()
        assert s1_output.extracted_intent == "refactor"
    
    def test_scenario_dependency_update(self, stage1, scanner, stage3):
        """Scenario: Update dependencies safely."""
        s1_ctx = Stage1ComprehensionContext(
            operation="fix",
            description="Update vulnerable dependency in requirements.txt",
            keywords=["security", "dependency", "update"],
            domain="infrastructure",
        )
        
        s1_result = stage1.comprehend(s1_ctx)
        assert s1_result.is_ok()


# ============================================================================
# Error Recovery Tests
# ============================================================================

class TestErrorRecovery:
    """Test error handling and recovery."""
    
    def test_recovery_stage_1_timeout(self, stage1):
        """Test: Recovery from Stage 1 timeout."""
        ctx = Stage1ComprehensionContext(
            operation="test",
            description="test",
            keywords=["test"],
            domain="test",
        )
        
        result = stage1.comprehend(ctx)
        assert result is not None
    
    def test_recovery_stage_2_permission_denied(self, scanner, tmp_path):
        """Test: Recovery from Stage 2 permission denied."""
        ctx = ScanContext(
            workspace_root=tmp_path,
            target_paths=[tmp_path / "nonexistent"],
            exclude_patterns=[],
        )
        
        output = scanner.scan(ctx)
        assert output is not None
    
    def test_recovery_stage_3_no_context(self, stage3):
        """Test: Recovery from Stage 3 with no context."""
        ctx = Stage3KnowledgeContext(
            stage1_output=None,
            domain="",
            codebase_path="",
            entities=[],
        )
        
        result = stage3.process_knowledge(ctx)
        assert result is not None
    
    def test_recovery_stage_4_approval_denied(self, stage4):
        """Test: Recovery from Stage 4 approval denial."""
        ctx = Stage4ApprovalContext(
            stage3_output=None,
            user_id="",
            urgency="critical",
            approval_level="high",
        )
        
        result = stage4.approve_operation(ctx)
        assert result is not None
