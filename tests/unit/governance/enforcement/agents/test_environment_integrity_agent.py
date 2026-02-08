"""
Phase 51 S2: EnvironmentIntegrityAgent Tests
Tests for 8th Enforcement Agent (Environment Integrity Validation)

AC-PHASE51-S2-001: MCP availability detection (3 methods)
AC-PHASE51-S2-002: Intent-based blocking logic
AC-PHASE51-S2-003: Error messaging for pre-flight failures
AC-PHASE51-S2-004: Git state validation
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from cortex.governance.enforcement.agents.environment_integrity_agent import (
    EnvironmentIntegrityAgent,
    MCPAvailability,
    ValidationResult,
)
from cortex.models.canonical_enums import IntentType


class TestMCPAvailabilityDetection:
    """Test: MCP server availability detection (3 methods)"""

    def test_ac_phase51_s2_001_method_1_tool_query(self):
        """AC-PHASE51-S2-001: Method 1 - Tool availability query"""
        agent = EnvironmentIntegrityAgent()
        
        # Verify method exists
        assert hasattr(agent, '_check_tool_exists'), "Tool check method required"
        assert callable(agent._check_tool_exists), "Tool check must be callable"

    def test_ac_phase51_s2_001_method_2_env_vars(self):
        """AC-PHASE51-S2-001: Method 2 - Environment variable detection"""
        agent = EnvironmentIntegrityAgent()
        
        # Verify method exists
        assert hasattr(agent, '_check_env_vars'), "Env var check method required"
        
        # Method should return bool
        result = agent._check_env_vars()
        assert isinstance(result, bool), "Env var check must return bool"

    def test_ac_phase51_s2_001_method_3_network_port(self):
        """AC-PHASE51-S2-001: Method 3 - Network port connectivity"""
        agent = EnvironmentIntegrityAgent()
        
        # Verify method exists
        assert hasattr(agent, '_check_port_open'), "Port check method required"
        
        # Method should return bool
        result = agent._check_port_open()
        assert isinstance(result, bool), "Port check must return bool"

    def test_mcp_availability_fallback_chain(self):
        """Test: MCP availability checks in fallback order"""
        agent = EnvironmentIntegrityAgent()
        
        # If all methods fail, should return unavailable
        with patch.object(agent, '_check_tool_exists', return_value=False):
            with patch.object(agent, '_check_env_vars', return_value=False):
                with patch.object(agent, '_check_port_open', return_value=False):
                    result = agent.check_mcp_availability()
                    assert result.available is False
                    assert result.detection_method == 'none'


class TestIntentBasedBlocking:
    """Test: Pre-flight validation based on intent"""

    def test_implement_intent_requires_mcp(self):
        """Test: IMPLEMENT intent blocks without MCP"""
        agent = EnvironmentIntegrityAgent()
        
        with patch.object(agent, 'check_mcp_availability', 
                         return_value=MCPAvailability(available=False, detection_method='none')):
            result = agent.validate_pre_flight(IntentType.IMPLEMENT)
            
            assert result.passed is False
            assert result.severity == 'CRITICAL'
            assert 'MCP' in result.reason

    def test_fix_intent_requires_mcp(self):
        """Test: FIX intent blocks without MCP"""
        agent = EnvironmentIntegrityAgent()
        
        with patch.object(agent, 'check_mcp_availability',
                         return_value=MCPAvailability(available=False, detection_method='none')):
            result = agent.validate_pre_flight(IntentType.FIX)
            
            assert result.passed is False
            assert result.severity == 'CRITICAL'

    def test_refactor_intent_requires_mcp(self):
        """Test: REFACTOR intent blocks without MCP"""
        agent = EnvironmentIntegrityAgent()
        
        with patch.object(agent, 'check_mcp_availability',
                         return_value=MCPAvailability(available=False, detection_method='none')):
            result = agent.validate_pre_flight(IntentType.REFACTOR)
            
            assert result.passed is False

    def test_analyze_intent_allows_no_mcp(self):
        """Test: ANALYZE intent allowed without MCP"""
        agent = EnvironmentIntegrityAgent()
        
        with patch.object(agent, 'check_mcp_availability',
                         return_value=MCPAvailability(available=False, detection_method='none')):
            result = agent.validate_pre_flight(IntentType.ANALYZE)
            
            # ANALYZE should proceed even without MCP (read-only operation)
            assert result.passed is True

    def test_query_intent_allowed_without_mcp(self):
        """Test: QUERY intent allowed without MCP"""
        agent = EnvironmentIntegrityAgent()
        
        with patch.object(agent, 'check_mcp_availability',
                         return_value=MCPAvailability(available=False, detection_method='none')):
            result = agent.validate_pre_flight(IntentType.QUERY)
            
            assert result.passed is True


class TestMCPAvailableOperations:
    """Test: Operations proceed when MCP is available"""

    def test_implement_proceeds_with_mcp(self):
        """Test: IMPLEMENT proceeds when MCP available"""
        agent = EnvironmentIntegrityAgent()
        
        with patch.object(agent, 'check_mcp_availability',
                         return_value=MCPAvailability(available=True, detection_method='network_port')):
            result = agent.validate_pre_flight(IntentType.IMPLEMENT)
            
            assert result.passed is True
            assert result.severity == 'PASSED'

    def test_fix_proceeds_with_mcp(self):
        """Test: FIX proceeds when MCP available"""
        agent = EnvironmentIntegrityAgent()
        
        with patch.object(agent, 'check_mcp_availability',
                         return_value=MCPAvailability(available=True, detection_method='environment_variables')):
            result = agent.validate_pre_flight(IntentType.FIX)
            
            assert result.passed is True

    def test_refactor_proceeds_with_mcp(self):
        """Test: REFACTOR proceeds when MCP available"""
        agent = EnvironmentIntegrityAgent()
        
        with patch.object(agent, 'check_mcp_availability',
                         return_value=MCPAvailability(available=True, detection_method='tool_query')):
            result = agent.validate_pre_flight(IntentType.REFACTOR)
            
            assert result.passed is True


class TestErrorMessaging:
    """Test: Error messages are clear and actionable"""

    def test_ac_phase51_s2_003_error_message_actionable(self):
        """AC-PHASE51-S2-003: Error message includes actionable fix"""
        agent = EnvironmentIntegrityAgent()
        
        with patch.object(agent, 'check_mcp_availability',
                         return_value=MCPAvailability(available=False, detection_method='none')):
            result = agent.validate_pre_flight(IntentType.IMPLEMENT)
            
            # Error message should include actionable fix
            assert 'python -m cortex.mcp.server' in result.action
            assert 'BLOCKED' in result.action

    def test_error_message_not_vague(self):
        """Test: Error messages are specific, not vague"""
        agent = EnvironmentIntegrityAgent()
        
        with patch.object(agent, 'check_mcp_availability',
                         return_value=MCPAvailability(available=False, detection_method='none')):
            result = agent.validate_pre_flight(IntentType.IMPLEMENT)
            
            # Should NOT contain vague suggestions
            assert 'try' not in result.action.lower()
            assert 'maybe' not in result.action.lower()
            assert 'could' not in result.action.lower()

    def test_error_includes_detection_method(self):
        """Test: Error message indicates which method was checked"""
        agent = EnvironmentIntegrityAgent()
        
        with patch.object(agent, 'check_mcp_availability',
                         return_value=MCPAvailability(available=False, detection_method='network_port')):
            result = agent.validate_pre_flight(IntentType.IMPLEMENT)
            
            assert 'network_port' in result.reason


class TestPythonDependencies:
    """Test: Python dependency validation"""

    def test_check_python_dependencies_all_present(self):
        """Test: Passes when all dependencies present"""
        agent = EnvironmentIntegrityAgent()
        
        result = agent.check_python_dependencies(['pathlib', 'os'])
        assert result.passed is True

    def test_check_python_dependencies_missing(self):
        """Test: Fails when dependencies missing"""
        agent = EnvironmentIntegrityAgent()
        
        result = agent.check_python_dependencies(['nonexistent_package_xyz'])
        assert result.passed is False
        assert 'nonexistent_package_xyz' in result.missing_packages

    def test_missing_dependency_error_message(self):
        """Test: Error message includes installation command"""
        agent = EnvironmentIntegrityAgent()
        
        result = agent.check_python_dependencies(['nonexistent_package_xyz'])
        assert 'pip install' in result.action


class TestGitStateValidation:
    """Test: Git state validation"""

    def test_ac_phase51_s2_004_git_clean_check(self):
        """AC-PHASE51-S2-004: Git state validation works"""
        agent = EnvironmentIntegrityAgent()
        
        # Verify method exists
        assert hasattr(agent, 'check_git_clean_state'), "Git check method required"
        result = agent.check_git_clean_state()
        
        assert isinstance(result, ValidationResult)
        assert hasattr(result, 'passed')

    def test_git_clean_state_detection(self):
        """Test: Detects clean git state"""
        agent = EnvironmentIntegrityAgent()
        
        with patch('subprocess.run') as mock_run:
            # Mock clean git state
            mock_run.return_value = Mock(returncode=0, stdout='')
            result = agent.check_git_clean_state()
            
            assert result.passed is True

    def test_git_dirty_state_detection(self):
        """Test: Detects dirty git state"""
        agent = EnvironmentIntegrityAgent()
        
        with patch('subprocess.run') as mock_run:
            # Mock dirty git state
            mock_run.return_value = Mock(
                returncode=0,
                stdout='M cortex/file1.py\nM cortex/file2.py\n'
            )
            result = agent.check_git_clean_state()
            
            assert result.passed is False
            assert 'dirty' in result.reason.lower()

    def test_git_error_handling(self):
        """Test: Handles git command errors gracefully"""
        agent = EnvironmentIntegrityAgent()
        
        with patch('subprocess.run', side_effect=Exception("Git not found")):
            result = agent.check_git_clean_state()
            
            assert result.severity == 'WARNING'


class TestValidationResult:
    """Test: ValidationResult data structure"""

    def test_validation_result_passed_state(self):
        """Test: ValidationResult tracks passed/failed state"""
        result = ValidationResult(
            passed=True,
            severity='PASSED',
            reason='Test passed',
            action='PROCEED'
        )
        
        assert result.passed is True
        assert result.severity == 'PASSED'

    def test_validation_result_critical_state(self):
        """Test: ValidationResult tracks critical failures"""
        result = ValidationResult(
            passed=False,
            severity='CRITICAL',
            reason='Test failed',
            action='BLOCKED'
        )
        
        assert result.passed is False
        assert result.severity == 'CRITICAL'

    def test_validation_result_missing_packages(self):
        """Test: ValidationResult tracks missing packages"""
        result = ValidationResult(
            passed=False,
            severity='CRITICAL',
            reason='Dependencies missing',
            action='Install',
            missing_packages=['pytest', 'pyyaml']
        )
        
        assert len(result.missing_packages) == 2


class TestMCPAvailabilityResult:
    """Test: MCPAvailability data structure"""

    def test_mcp_availability_available(self):
        """Test: MCPAvailability tracks availability"""
        result = MCPAvailability(
            available=True,
            detection_method='network_port',
            details='Server responding'
        )
        
        assert result.available is True

    def test_mcp_availability_unavailable(self):
        """Test: MCPAvailability tracks unavailability"""
        result = MCPAvailability(
            available=False,
            detection_method='none',
            details='All checks failed'
        )
        
        assert result.available is False
        assert result.detection_method == 'none'


class TestPhase51S2Acceptance:
    """Acceptance Tests for Phase 51 S2 completion"""

    def test_ac_phase51_s2_001_mcp_detection_methods(self):
        """AC-PHASE51-S2-001: All 3 MCP detection methods implemented"""
        agent = EnvironmentIntegrityAgent()
        
        # Verify all 3 methods exist
        assert hasattr(agent, '_check_tool_exists')
        assert hasattr(agent, '_check_env_vars')
        assert hasattr(agent, '_check_port_open')

    def test_ac_phase51_s2_002_intent_blocking_logic(self):
        """AC-PHASE51-S2-002: Intent-based blocking logic works"""
        agent = EnvironmentIntegrityAgent()
        
        # MCP-required intents: IMPLEMENT, FIX, REFACTOR
        assert IntentType.IMPLEMENT in agent.mcp_required_intents
        assert IntentType.FIX in agent.mcp_required_intents
        assert IntentType.REFACTOR in agent.mcp_required_intents

    def test_ac_phase51_s2_003_error_messaging(self):
        """AC-PHASE51-S2-003: Error messages are clear and actionable"""
        agent = EnvironmentIntegrityAgent()
        
        with patch.object(agent, 'check_mcp_availability',
                         return_value=MCPAvailability(available=False, detection_method='none')):
            result = agent.validate_pre_flight(IntentType.IMPLEMENT)
            
            # Must have clear action message
            assert len(result.action) > 0
            assert 'BLOCKED' in result.action or 'Start' in result.action

    def test_ac_phase51_s2_004_git_validation(self):
        """AC-PHASE51-S2-004: Git state validation implemented"""
        agent = EnvironmentIntegrityAgent()
        
        result = agent.check_git_clean_state()
        assert isinstance(result, ValidationResult)
        assert result.severity in ['PASSED', 'WARNING', 'CRITICAL']
