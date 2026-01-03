"""
Integration Tests for Master Orchestrator with Response Rendering Pipeline

Tests end-to-end flow:
- Request routing → Orchestrator execution → Response rendering → System message injection
- Token warning display
- Error message formatting
- Success metadata enrichment
- Security alert injection

Target: 90% integration coverage

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from dataclasses import dataclass

from src.orchestrators.master_orchestrator import MasterOrchestrator
from src.orchestrators.execution_engine import ExecutionResult
from src.orchestrators.base.base_orchestrator import OrchestratorResult, OrchestratorStatus


@pytest.fixture
def mock_registry():
    """Mock OrchestratorRegistry."""
    registry = Mock()
    return registry


@pytest.fixture
def mock_state_db():
    """Mock PlanningStateDB."""
    state_db = Mock()
    return state_db


@pytest.fixture
def mock_config_path(tmp_path):
    """Create temporary config file."""
    config_file = tmp_path / "master-orchestrator.yaml"
    config_content = """
routing_rules:
  - pattern: "^plan.*"
    orchestrator: "planning_orchestrator"
    confidence: 1.0
    match_type: "regex"
  - pattern: "^vacuum.*"
    orchestrator: "vacuum_orchestrator"
    confidence: 1.0
    match_type: "regex"
"""
    config_file.write_text(config_content)
    return str(config_file)


@pytest.fixture
def master_orchestrator(mock_registry, mock_state_db, mock_config_path):
    """Create MasterOrchestrator instance with rendering pipeline."""
    # Note: ResponseRenderer and ResponseMiddleware are auto-instantiated
    return MasterOrchestrator(
        config_path=mock_config_path,
        registry=mock_registry,
        state_db=mock_state_db
    )


class TestEndToEndRendering:
    """Test complete request → execution → rendering flow."""
    
    def test_successful_request_with_rendering(self, master_orchestrator):
        """Test successful request produces rendered user_message."""
        # Mock orchestrator execution
        orch_result = OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Plan 'user-auth' created successfully",
            data={'plan_id': 'user-auth'},
            execution_time_seconds=2.5
        )
        
        with patch.object(master_orchestrator, 'execute_orchestrator') as mock_execute:
            mock_execute.return_value = ExecutionResult(
                orchestrator_id='planning_orchestrator',
                success=True,
                status='completed',
                started_at=datetime.now(),
                completed_at=datetime.now(),
                duration_seconds=2.5,
                metadata={'orchestrator_result': orch_result}
            )
            
            result = master_orchestrator.handle_request("plan user authentication")
            
            # Verify user_message was rendered
            assert result.user_message is not None
            assert "## 🧠 CORTEX" in result.user_message
            assert "✅" in result.user_message
            assert "Plan 'user-auth' created successfully" in result.user_message
            assert "⏱️ **Duration:** 2.5s" in result.user_message
    
    def test_request_without_orchestrator_result(self, master_orchestrator):
        """Test request without orchestrator_result in metadata doesn't crash."""
        with patch.object(master_orchestrator, 'execute_orchestrator') as mock_execute:
            mock_execute.return_value = ExecutionResult(
                orchestrator_id='planning_orchestrator',
                success=True,
                status='completed',
                started_at=datetime.now(),
                completed_at=datetime.now(),
                duration_seconds=1.0,
                metadata={}  # No orchestrator_result
            )
            
            result = master_orchestrator.handle_request("plan test")
            
            # Should succeed but user_message is None
            assert result.success is True
            assert result.user_message is None


class TestTokenWarningInjection:
    """Test token warning injection in responses."""
    
    def test_token_warning_displayed_at_threshold(self, master_orchestrator):
        """Test token warning appears when usage >= 80%."""
        orch_result = OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Operation completed",
            execution_time_seconds=1.0
        )
        
        with patch.object(master_orchestrator, 'execute_orchestrator') as mock_execute:
            mock_execute.return_value = ExecutionResult(
                orchestrator_id='vacuum_orchestrator',
                success=True,
                status='completed',
                started_at=datetime.now(),
                completed_at=datetime.now(),
                duration_seconds=1.0,
                metadata={'orchestrator_result': orch_result}
            )
            
            # Simulate high token usage
            context = {
                'token_usage_percentage': 85.0,
                'session_id': 'test-session-123',
                'total_tokens': 85000
            }
            
            result = master_orchestrator.handle_request("vacuum clean", context)
            
            # Verify token warning appears BEFORE response
            assert result.user_message is not None
            assert "⚠️ **Token Warning**" in result.user_message
            assert "85.0% used" in result.user_message
            assert "cortex vacuum" in result.user_message
            assert "cortex continue test-session-123" in result.user_message
            assert "---" in result.user_message  # Separator
            
            # Verify response appears AFTER separator
            warning_pos = result.user_message.index("⚠️ **Token Warning**")
            separator_pos = result.user_message.index("---")
            response_pos = result.user_message.index("## 🧠 CORTEX")
            assert warning_pos < separator_pos < response_pos
    
    def test_no_token_warning_below_threshold(self, master_orchestrator):
        """Test no token warning when usage < 80%."""
        orch_result = OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Operation completed",
            execution_time_seconds=1.0
        )
        
        with patch.object(master_orchestrator, 'execute_orchestrator') as mock_execute:
            mock_execute.return_value = ExecutionResult(
                orchestrator_id='vacuum_orchestrator',
                success=True,
                status='completed',
                started_at=datetime.now(),
                completed_at=datetime.now(),
                duration_seconds=1.0,
                metadata={'orchestrator_result': orch_result}
            )
            
            # Low token usage
            context = {
                'token_usage_percentage': 65.0,
                'session_id': 'test-session-456',
                'total_tokens': 65000
            }
            
            result = master_orchestrator.handle_request("vacuum clean", context)
            
            # No token warning
            assert result.user_message is not None
            assert "Token Warning" not in result.user_message
            assert "---" not in result.user_message


class TestErrorMessageFormatting:
    """Test error message rendering."""
    
    def test_error_response_formatted(self, master_orchestrator):
        """Test failed orchestrator execution produces formatted error."""
        orch_result = OrchestratorResult(
            status=OrchestratorStatus.FAILED,
            success=False,
            message="Validation failed",
            errors=[
                "Invalid plan name: must be kebab-case",
                "Missing required field: description"
            ],
            execution_time_seconds=0.5
        )
        
        with patch.object(master_orchestrator, 'execute_orchestrator') as mock_execute:
            mock_execute.return_value = ExecutionResult(
                orchestrator_id='planning_orchestrator',
                success=False,
                status='failed',
                started_at=datetime.now(),
                completed_at=datetime.now(),
                duration_seconds=0.5,
                errors=['Validation failed'],
                metadata={'orchestrator_result': orch_result}
            )
            
            result = master_orchestrator.handle_request("plan MyPlan")
            
            # Verify error formatting
            assert result.user_message is not None
            assert "## 🧠 CORTEX" in result.user_message
            assert "❌" in result.user_message
            assert "### ❌ Errors" in result.user_message
            assert "Invalid plan name" in result.user_message
            assert "Missing required field" in result.user_message


class TestSecurityAlertInjection:
    """Test security alert message injection."""
    
    def test_security_alerts_displayed(self, master_orchestrator):
        """Test security warnings appear in response."""
        orch_result = OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Operation completed with warnings",
            execution_time_seconds=1.0
        )
        
        with patch.object(master_orchestrator, 'execute_orchestrator') as mock_execute:
            mock_execute.return_value = ExecutionResult(
                orchestrator_id='planning_orchestrator',
                success=True,
                status='completed',
                started_at=datetime.now(),
                completed_at=datetime.now(),
                duration_seconds=1.0,
                metadata={'orchestrator_result': orch_result}
            )
            
            # Add security warnings to context
            context = {
                'security_warnings': [
                    "Unsafe file path detected: ../../../etc/passwd",
                    "Potential command injection in user input"
                ]
            }
            
            result = master_orchestrator.handle_request("plan test", context)
            
            # Verify security alerts appear FIRST (CRITICAL priority)
            assert result.user_message is not None
            assert "🚨 **Security Alert**" in result.user_message
            assert "Unsafe file path" in result.user_message
            assert "command injection" in result.user_message


class TestSuccessMetadataEnrichment:
    """Test success metadata enrichment."""
    
    def test_success_metadata_displayed(self, master_orchestrator):
        """Test success metadata appears in response."""
        orch_result = OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Refactoring complete",
            execution_time_seconds=5.0
        )
        
        with patch.object(master_orchestrator, 'execute_orchestrator') as mock_execute:
            mock_execute.return_value = ExecutionResult(
                orchestrator_id='planning_orchestrator',
                success=True,
                status='completed',
                started_at=datetime.now(),
                completed_at=datetime.now(),
                duration_seconds=5.0,
                metadata={
                    'orchestrator_result': orch_result,
                    'success_metadata': {
                        'files_modified': 12,
                        'tests_passed': 45,
                        'tests_total': 47,
                        'coverage_percentage': 94
                    }
                }
            )
            
            result = master_orchestrator.handle_request("plan refactor")
            
            # Verify metadata enrichment
            assert result.user_message is not None
            assert "ℹ️ **Metadata**" in result.user_message
            assert "📝 Modified 12 file(s)" in result.user_message
            assert "✅ Tests: 45/47 passed" in result.user_message
            assert "📊 Coverage: 94%" in result.user_message


class TestMessagePriorityOrdering:
    """Test system message priority ordering."""
    
    def test_all_message_types_ordered_correctly(self, master_orchestrator):
        """Test CRITICAL → HIGH → MEDIUM → LOW priority ordering."""
        orch_result = OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Multi-warning operation completed",
            execution_time_seconds=2.0
        )
        
        with patch.object(master_orchestrator, 'execute_orchestrator') as mock_execute:
            mock_execute.return_value = ExecutionResult(
                orchestrator_id='planning_orchestrator',
                success=True,
                status='completed',
                started_at=datetime.now(),
                completed_at=datetime.now(),
                duration_seconds=2.0,
                metadata={
                    'orchestrator_result': orch_result,
                    'success_metadata': {'files_modified': 5}  # LOW
                }
            )
            
            # Context with all message types
            context = {
                'security_warnings': ["Security issue"],  # CRITICAL
                'token_usage_percentage': 85.0,  # HIGH
                'session_id': 'test',
                'total_tokens': 85000,
                'deprecated_features_used': [{  # MEDIUM
                    'name': 'old_api',
                    'replacement': 'new_api',
                    'deprecated_in': 'v5.0',
                    'removal_in': 'v6.0'
                }]
            }
            
            result = master_orchestrator.handle_request("plan test", context)
            
            # Find positions of each message type
            assert result.user_message is not None
            security_pos = result.user_message.index("🚨 **Security Alert**")
            token_pos = result.user_message.index("⚠️ **Token Warning**")
            deprecation_pos = result.user_message.index("⚠️ **Deprecation Notice**")
            metadata_pos = result.user_message.index("ℹ️ **Metadata**")
            
            # Verify correct order: CRITICAL < HIGH < MEDIUM < LOW
            assert security_pos < token_pos < deprecation_pos < metadata_pos


class TestArtifactRendering:
    """Test artifact list rendering."""
    
    def test_artifacts_displayed(self, master_orchestrator):
        """Test artifacts appear in changes block."""
        orch_result = OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Files created successfully",
            data={
                'artifacts': [
                    'cortex-brain/documents/planning/user-auth/00-master-plan.md',
                    'cortex-brain/documents/planning/user-auth/tracking/progress.json'
                ]
            },
            execution_time_seconds=1.5
        )
        
        with patch.object(master_orchestrator, 'execute_orchestrator') as mock_execute:
            mock_execute.return_value = ExecutionResult(
                orchestrator_id='planning_orchestrator',
                success=True,
                status='completed',
                started_at=datetime.now(),
                completed_at=datetime.now(),
                duration_seconds=1.5,
                artifacts=['00-master-plan.md', 'progress.json'],
                metadata={'orchestrator_result': orch_result}
            )
            
            result = master_orchestrator.handle_request("plan user-auth")
            
            # Verify artifacts block
            assert result.user_message is not None
            assert "### 📁 Artifacts Created" in result.user_message
            assert "00-master-plan.md" in result.user_message
            assert "progress.json" in result.user_message


class TestRenderingErrorHandling:
    """Test error handling in rendering pipeline."""
    
    def test_rendering_failure_graceful(self, master_orchestrator):
        """Test graceful handling when rendering fails."""
        orch_result = OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Test operation",
            execution_time_seconds=1.0
        )
        
        with patch.object(master_orchestrator, 'execute_orchestrator') as mock_execute:
            with patch.object(master_orchestrator.response_renderer, 'render') as mock_render:
                mock_render.side_effect = Exception("Rendering error")
                
                mock_execute.return_value = ExecutionResult(
                    orchestrator_id='planning_orchestrator',
                    success=True,
                    status='completed',
                    started_at=datetime.now(),
                    completed_at=datetime.now(),
                    duration_seconds=1.0,
                    metadata={'orchestrator_result': orch_result}
                )
                
                # Should not crash - rendering errors are caught
                result = master_orchestrator.handle_request("plan test")
                
                # Execution should succeed even if rendering fails
                assert result.success is True
