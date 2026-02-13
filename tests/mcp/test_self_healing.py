"""
Tests for MCP self-healing infrastructure (ENH-067).

Authority: CORE-049, ENH-067, Phase 53
Purpose: Validate automatic MCP failure detection and recovery
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import os
import socket
from cortex.mcp.self_healing import MCPSelfHealing, MCPIssue


class TestMCPSelfHealingDetection:
    """Test MCP availability detection methods."""
    
    def test_tool_registry_detection_available(self):
        """RED: Detect MCP via tool registry when available."""
        healer = MCPSelfHealing()
        
        with patch.object(healer, '_check_tool_registry', return_value=True):
            is_available, message = healer.detect_mcp_availability()
            
            assert is_available is True
            assert "tool registry" in message.lower()
    
    def test_tool_registry_detection_unavailable(self):
        """RED: Detect MCP unavailable via tool registry."""
        healer = MCPSelfHealing()
        
        with patch.object(healer, '_check_tool_registry', return_value=False):
            with patch.object(healer, '_check_environment_vars', return_value=False):
                with patch.object(healer, '_check_network_port', return_value=False):
                    is_available, message = healer.detect_mcp_availability()
                    
                    assert is_available is False
                    assert "all detection methods failed" in message.lower()
    
    def test_environment_variable_detection(self):
        """RED: Detect MCP via environment variables."""
        healer = MCPSelfHealing()
        
        with patch.object(healer, '_check_tool_registry', return_value=False):
            with patch.object(healer, '_check_environment_vars', return_value=True):
                is_available, message = healer.detect_mcp_availability()
                
                assert is_available is True
                assert "environment" in message.lower()
    
    def test_network_port_detection(self):
        """RED: Detect MCP via network port check."""
        healer = MCPSelfHealing()
        
        with patch.object(healer, '_check_tool_registry', return_value=False):
            with patch.object(healer, '_check_environment_vars', return_value=False):
                with patch.object(healer, '_check_network_port', return_value=True):
                    is_available, message = healer.detect_mcp_availability()
                    
                    assert is_available is True
                    assert "network" in message.lower()


class TestMCPSelfHealingIssueDetection:
    """Test issue pattern detection from errors."""
    
    def test_detect_known_issue(self):
        """RED: Detect known MCP error pattern."""
        healer = MCPSelfHealing()
        error_msg = "TypeError: r.content is not iterable"
        
        issue = healer.detect_issue(error_msg)
        
        assert issue is not None
        assert issue.issue_id == "MCP-ERR-001"
        assert issue.severity == "CRITICAL"
    
    def test_detect_connection_refused(self):
        """RED: Detect connection refused error."""
        healer = MCPSelfHealing()
        error_msg = "Connection refused"
        
        issue = healer.detect_issue(error_msg)
        
        assert issue is not None
        assert issue.issue_id == "MCP-ERR-002"
        assert issue.fix_strategy == "restart_mcp_server"
    
    def test_detect_timeout_error(self):
        """RED: Detect timeout error pattern."""
        healer = MCPSelfHealing()
        error_msg = "Request timed out after 30 seconds"
        
        issue = healer.detect_issue(error_msg)
        
        assert issue is not None
        assert issue.issue_id == "MCP-ERR-003"
        assert issue.retry_count == 1
    
    def test_detect_module_not_found(self):
        """RED: Detect Python module error."""
        healer = MCPSelfHealing()
        error_msg = "ModuleNotFoundError: No module named 'cortex'"
        
        issue = healer.detect_issue(error_msg)
        
        assert issue is not None
        assert issue.issue_id == "MCP-ERR-004"
        assert issue.fix_strategy == "reconfigure_python_path"
    
    def test_unknown_error_returns_none(self):
        """RED: Unknown error patterns return None."""
        healer = MCPSelfHealing()
        error_msg = "Some random unrelated error"
        
        issue = healer.detect_issue(error_msg)
        
        assert issue is None


class TestMCPSelfHealingAutoFix:
    """Test automatic fix application."""
    
    def test_apply_fix_restart_server(self):
        """RED: Apply MCP server restart fix."""
        healer = MCPSelfHealing()
        issue = MCPIssue(
            issue_id="MCP-ERR-001",
            name="Server Response Error",
            pattern="r.content is not iterable",
            severity="CRITICAL",
            root_cause="MCP server response handling bug",
            fix_strategy="restart_mcp_server",
            auto_fix=True,
            retry_count=1,
            estimated_duration_ms=5000,
            fix_steps=["Restart server", "Retry operation"],
            success_rate=0.95
        )
        
        with patch.object(healer, 'fix_restart_mcp_server', return_value=True):
            success = healer.apply_fix(issue)
            
            assert success is True
    
    def test_apply_fix_reconfigure_python(self):
        """RED: Apply Python path reconfiguration fix."""
        healer = MCPSelfHealing()
        issue = MCPIssue(
            issue_id="MCP-ERR-004",
            name="Module Not Found",
            pattern="ModuleNotFoundError.*cortex",
            severity="CRITICAL",
            root_cause="Python path misconfigured",
            fix_strategy="reconfigure_python_path",
            auto_fix=True,
            retry_count=1,
            estimated_duration_ms=3000,
            fix_steps=["Run setup-mcp.py", "Reload VS Code"],
            success_rate=0.80
        )
        
        with patch.object(healer, 'fix_reconfigure_python_path', return_value=True):
            success = healer.apply_fix(issue)
            
            assert success is True
    
    def test_apply_fix_disabled(self):
        """RED: Auto-fix disabled issues return False."""
        healer = MCPSelfHealing()
        issue = MCPIssue(
            issue_id="MCP-ERR-999",
            name="Manual Intervention Required",
            pattern="manual",
            severity="LOW",
            root_cause="Unknown",
            fix_strategy="manual_intervention",
            auto_fix=False,
            retry_count=0,
            estimated_duration_ms=0,
            fix_steps=["Contact support"],
            success_rate=0.0
        )
        
        success = healer.apply_fix(issue)
        
        assert success is False
    
    def test_apply_fix_logs_event(self):
        """RED: Fix application logs to audit trail."""
        healer = MCPSelfHealing()
        issue = MCPIssue(
            issue_id="MCP-ERR-001",
            name="Server Response Error",
            pattern="r.content is not iterable",
            severity="CRITICAL",
            root_cause="MCP server response handling bug",
            fix_strategy="restart_mcp_server",
            auto_fix=True,
            retry_count=1,
            estimated_duration_ms=5000,
            fix_steps=["Restart server"],
            success_rate=0.95
        )
        
        with patch.object(healer, 'fix_restart_mcp_server', return_value=True):
            with patch.object(healer, '_log_fix_event') as mock_log:
                healer.apply_fix(issue)
                
                mock_log.assert_called_once()


class TestMCPSelfHealingRetry:
    """Test retry mechanism with exponential backoff."""
    
    def test_retry_tool_success_first_attempt(self):
        """RED: Tool succeeds on first retry."""
        healer = MCPSelfHealing()
        mock_tool = Mock(return_value={"status": "success"})
        
        result = healer.retry_mcp_tool(mock_tool, {"param": "value"}, max_retries=2)
        
        assert result["status"] == "success"
        assert mock_tool.call_count == 1
    
    def test_retry_tool_success_after_failure(self):
        """RED: Tool succeeds on second retry."""
        healer = MCPSelfHealing()
        mock_tool = Mock(side_effect=[
            Exception("Temporary failure"),
            {"status": "success"}
        ])
        
        result = healer.retry_mcp_tool(mock_tool, {"param": "value"}, max_retries=2)
        
        assert result["status"] == "success"
        assert mock_tool.call_count == 2
    
    def test_retry_exhausted(self):
        """RED: All retries exhausted returns None."""
        healer = MCPSelfHealing()
        mock_tool = Mock(side_effect=Exception("Persistent failure"))
        
        result = healer.retry_mcp_tool(mock_tool, {"param": "value"}, max_retries=2)
        
        assert result is None
        assert mock_tool.call_count == 2
    
    def test_exponential_backoff(self):
        """RED: Retry uses exponential backoff timing."""
        healer = MCPSelfHealing()
        mock_tool = Mock(side_effect=[
            Exception("Fail 1"),
            Exception("Fail 2"),
            {"status": "success"}
        ])
        
        with patch('time.sleep') as mock_sleep:
            result = healer.retry_mcp_tool(
                mock_tool, 
                {"param": "value"}, 
                max_retries=3,
                backoff_base=1
            )
            
            assert result["status"] == "success"
            # Should sleep 1s, then 2s between retries
            assert mock_sleep.call_count == 2


class TestMCPSelfHealingAuditTrail:
    """Test audit logging for self-healing events."""
    
    def test_audit_log_created(self):
        """RED: Audit log file created on first fix."""
        healer = MCPSelfHealing()
        healer.log_path = "/tmp/mcp-self-healing-test.log"
        healer.telemetry_enabled = True
        
        issue = MCPIssue(
            issue_id="MCP-ERR-001",
            name="Server Error",
            pattern="r.content",
            severity="CRITICAL",
            root_cause="Bug",
            fix_strategy="restart_mcp_server",
            auto_fix=True,
            retry_count=1,
            estimated_duration_ms=5000,
            fix_steps=["Restart"],
            success_rate=0.95
        )
        
        with patch.object(healer, 'fix_restart_mcp_server', return_value=True):
            with patch('builtins.open', create=True) as mock_open:
                healer.apply_fix(issue)
                
                mock_open.assert_called()
    
    def test_audit_log_contains_metadata(self):
        """RED: Audit log includes issue metadata."""
        healer = MCPSelfHealing()
        issue = MCPIssue(
            issue_id="MCP-ERR-001",
            name="Server Error",
            pattern="r.content",
            severity="CRITICAL",
            root_cause="Bug",
            fix_strategy="restart_mcp_server",
            auto_fix=True,
            retry_count=1,
            estimated_duration_ms=5000,
            fix_steps=["Restart"],
            success_rate=0.95
        )
        
        log_entry = healer._build_log_entry(issue, success=True, duration_ms=1234)
        
        assert log_entry["issue_id"] == "MCP-ERR-001"
        assert log_entry["fix_result"] == "SUCCESS"
        assert log_entry["duration_ms"] == 1234
        assert "timestamp" in log_entry
    
    def test_audit_log_failure_recorded(self):
        """RED: Failed fix attempts logged."""
        healer = MCPSelfHealing()
        healer.log_path = "/tmp/mcp-self-healing-test.log"
        healer.telemetry_enabled = True
        
        issue = MCPIssue(
            issue_id="MCP-ERR-001",
            name="Server Error",
            pattern="r.content",
            severity="CRITICAL",
            root_cause="Bug",
            fix_strategy="restart_mcp_server",
            auto_fix=True,
            retry_count=1,
            estimated_duration_ms=5000,
            fix_steps=["Restart"],
            success_rate=0.95
        )
        
        # Mock fix_restart_mcp_server to return False (simulating failure)
        def failing_fix(issue):
            return False
        
        healer.fix_strategies["restart_mcp_server"] = failing_fix
        
        with patch.object(healer, '_log_fix_event') as mock_log:
            healer.apply_fix(issue)
            
            # Verify failure logged
            call_args = mock_log.call_args[0][0]
            assert call_args["fix_result"] == "FAILED"


class TestMCPSelfHealingIntegration:
    """Test end-to-end self-healing workflow."""
    
    def test_handle_tool_error_with_auto_fix(self):
        """RED: Complete error handling with auto-fix."""
        healer = MCPSelfHealing()
        error = Exception("TypeError: r.content is not iterable")
        tool_name = "cortex_process_request"
        params = {"operation": "implement"}
        
        with patch.object(healer, 'detect_issue') as mock_detect:
            with patch.object(healer, 'apply_fix', return_value=True):
                with patch.object(healer, 'retry_mcp_tool') as mock_retry:
                    mock_issue = MCPIssue(
                        issue_id="MCP-ERR-001",
                        name="Server Error",
                        pattern="r.content",
                        severity="CRITICAL",
                        root_cause="Bug",
                        fix_strategy="restart_mcp_server",
                        auto_fix=True,
                        retry_count=1,
                        estimated_duration_ms=5000,
                        fix_steps=["Restart"],
                        success_rate=0.95
                    )
                    mock_detect.return_value = mock_issue
                    mock_retry.return_value = {"status": "success"}
                    
                    result = healer.handle_mcp_tool_error(error, tool_name, params)
                    
                    assert result is not None
                    assert result["status"] == "fix_applied_retry_needed"
    
    def test_handle_unknown_error_escalates(self):
        """RED: Unknown errors escalate to user."""
        healer = MCPSelfHealing()
        error = Exception("Unknown bizarre error")
        tool_name = "cortex_process_request"
        params = {"operation": "implement"}
        
        with patch.object(healer, 'detect_issue', return_value=None):
            result = healer.handle_mcp_tool_error(error, tool_name, params)
            
            assert result is None
    
    def test_handle_fix_failure_escalates(self):
        """RED: Failed fix escalates to user."""
        healer = MCPSelfHealing()
        error = Exception("TypeError: r.content is not iterable")
        tool_name = "cortex_process_request"
        params = {"operation": "implement"}
        
        with patch.object(healer, 'detect_issue') as mock_detect:
            with patch.object(healer, 'apply_fix', return_value=False):
                mock_issue = MCPIssue(
                    issue_id="MCP-ERR-001",
                    name="Server Error",
                    pattern="r.content",
                    severity="CRITICAL",
                    root_cause="Bug",
                    fix_strategy="restart_mcp_server",
                    auto_fix=True,
                    retry_count=1,
                    estimated_duration_ms=5000,
                    fix_steps=["Restart"],
                    success_rate=0.95
                )
                mock_detect.return_value = mock_issue
                
                result = healer.handle_mcp_tool_error(error, tool_name, params)
                
                assert result is None
