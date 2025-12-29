"""
Tests for Phase 5 Enhanced Execution Orchestrator

Tests all Phase 5 enhancements:
- Multi-agent collaboration (sequential, parallel, nested)
- Context validation with auto-retrieval
- Structured output (Pydantic schemas)
- Adaptive execution modes
- Enhanced safety guardrails

Author: Asif Hussain
Version: 1.0
"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from datetime import datetime
from typing import Dict, Any

from src.orchestration_4_0.orchestrators.execution import (
    ExecutionOrchestrator,
    ExecutionResult,
    PhaseResult,
    ExecutionMode,
    ContextValidation,
    Risk,
    RiskSeverity,
    SafetyCheck,
)


# ========================================
# Package 1: Multi-Agent Collaboration Tests
# ========================================

class TestSequentialChatExecution:
    """Tests for sequential chat pattern"""
    
    @pytest.mark.asyncio
    async def test_sequential_chat_success(self):
        """Test successful sequential execution"""
        orchestrator = ExecutionOrchestrator(config={"execution_mode": "autonomous"})
        
        # Mock sub-orchestrators
        mock_orch1 = AsyncMock()
        mock_orch1.execute = AsyncMock(return_value={'success': True, 'output': 'result1'})
        
        mock_orch2 = AsyncMock()
        mock_orch2.execute = AsyncMock(return_value={'success': True, 'output': 'result2'})
        
        orchestrator.sub_orchestrators = {
            'orch1': mock_orch1,
            'orch2': mock_orch2
        }
        
        # Execute
        result = await orchestrator.execute_sequential_chat(
            ['orch1', 'orch2'],
            {'initial': 'context'}
        )
        
        assert isinstance(result, ExecutionResult)
        assert result.success
        assert mock_orch1.execute.called
        assert mock_orch2.execute.called
    
    @pytest.mark.asyncio
    async def test_sequential_chat_stop_on_error(self):
        """Test sequential execution stops on error"""
        orchestrator = ExecutionOrchestrator(config={"execution_mode": "autonomous"})
        
        # Mock orchestrators - second one fails
        mock_orch1 = AsyncMock()
        mock_orch1.execute = AsyncMock(return_value={'success': True})
        
        mock_orch2 = AsyncMock()
        mock_orch2.execute = AsyncMock(return_value={'success': False, 'error': 'Test error'})
        
        mock_orch3 = AsyncMock()
        mock_orch3.execute = AsyncMock(return_value={'success': True})
        
        orchestrator.sub_orchestrators = {
            'orch1': mock_orch1,
            'orch2': mock_orch2,
            'orch3': mock_orch3
        }
        
        # Execute
        result = await orchestrator.execute_sequential_chat(
            ['orch1', 'orch2', 'orch3'],
            {}
        )
        
        assert not result.success
        assert len(result.errors) > 0
        # Third orchestrator should not be called
        assert not mock_orch3.execute.called


class TestParallelGroupChatExecution:
    """Tests for parallel group chat pattern"""
    
    @pytest.mark.asyncio
    async def test_parallel_execution_all_success(self):
        """Test all orchestrators succeed in parallel"""
        orchestrator = ExecutionOrchestrator(config={"execution_mode": "autonomous"})
        
        # Mock orchestrators
        mock_orch1 = AsyncMock()
        mock_orch1.execute = AsyncMock(return_value={'success': True, 'data': 'result1'})
        
        mock_orch2 = AsyncMock()
        mock_orch2.execute = AsyncMock(return_value={'success': True, 'data': 'result2'})
        
        mock_orch3 = AsyncMock()
        mock_orch3.execute = AsyncMock(return_value={'success': True, 'data': 'result3'})
        
        orchestrator.sub_orchestrators = {
            'orch1': mock_orch1,
            'orch2': mock_orch2,
            'orch3': mock_orch3
        }
        
        # Execute
        result = await orchestrator.execute_parallel_group_chat(
            ['orch1', 'orch2', 'orch3'],
            {},
            synthesize=False
        )
        
        assert isinstance(result, ExecutionResult)
        assert result.success
        # All should be called
        assert mock_orch1.execute.called
        assert mock_orch2.execute.called
        assert mock_orch3.execute.called
    
    @pytest.mark.asyncio
    async def test_parallel_execution_partial_failure(self):
        """Test parallel execution with some failures"""
        orchestrator = ExecutionOrchestrator(config={"execution_mode": "autonomous"})
        
        # Mock orchestrators - one fails
        mock_orch1 = AsyncMock()
        mock_orch1.execute = AsyncMock(return_value={'success': True})
        
        mock_orch2 = AsyncMock()
        mock_orch2.execute = AsyncMock(side_effect=Exception("Test error"))
        
        mock_orch3 = AsyncMock()
        mock_orch3.execute = AsyncMock(return_value={'success': True})
        
        orchestrator.sub_orchestrators = {
            'orch1': mock_orch1,
            'orch2': mock_orch2,
            'orch3': mock_orch3
        }
        
        # Execute
        result = await orchestrator.execute_parallel_group_chat(
            ['orch1', 'orch2', 'orch3'],
            {}
        )
        
        # Should not be fully successful
        assert not result.success


class TestNestedChatExecution:
    """Tests for nested chat pattern"""
    
    @pytest.mark.asyncio
    async def test_nested_teams_execution(self):
        """Test nested team execution"""
        orchestrator = ExecutionOrchestrator(config={"execution_mode": "autonomous"})
        
        # Mock orchestrators
        mock_orch1 = AsyncMock()
        mock_orch1.execute = AsyncMock(return_value={'success': True})
        
        mock_orch2 = AsyncMock()
        mock_orch2.execute = AsyncMock(return_value={'success': True})
        
        orchestrator.sub_orchestrators = {
            'team1_orch1': mock_orch1,
            'team2_orch1': mock_orch2
        }
        
        # Execute
        team_structure = {
            'team1': ['team1_orch1'],
            'team2': ['team2_orch1']
        }
        
        result = await orchestrator.execute_nested_chat(
            team_structure,
            {}
        )
        
        assert isinstance(result, ExecutionResult)
        assert result.success


# ========================================
# Package 4: Context Validation Tests
# ========================================

class TestContextValidation:
    """Tests for context validation"""
    
    @pytest.mark.asyncio
    async def test_context_validation_success(self):
        """Test successful context validation"""
        orchestrator = ExecutionOrchestrator()
        
        context = {'workspace': '/path/to/workspace', 'language': 'python'}
        execution_plan = {
            'required_context': ['workspace', 'language'],
            'optional_context': ['framework']
        }
        
        validation = await orchestrator.context_validator.validate_context_sufficiency(
            context, execution_plan
        )
        
        assert isinstance(validation, ContextValidation)
        assert validation.is_valid
        assert len(validation.missing_required) == 0
    
    @pytest.mark.asyncio
    async def test_context_validation_missing_required(self):
        """Test validation fails with missing required context"""
        orchestrator = ExecutionOrchestrator()
        
        context = {'workspace': '/path/to/workspace'}
        execution_plan = {
            'required_context': ['workspace', 'language'],
            'optional_context': []
        }
        
        validation = await orchestrator.context_validator.validate_context_sufficiency(
            context, execution_plan
        )
        
        assert not validation.has_requirements
        assert 'language' in validation.missing_required
    
    @pytest.mark.asyncio
    async def test_context_auto_retrieval(self):
        """Test context auto-retrieval"""
        # Mock knowledge graph
        mock_kg = AsyncMock()
        mock_kg.query = AsyncMock(return_value='retrieved_value')
        
        orchestrator = ExecutionOrchestrator(knowledge_graph=mock_kg)
        
        context = {'workspace': '/path/to/workspace'}
        execution_plan = {
            'required_context': ['workspace', 'language']
        }
        
        validation = await orchestrator.context_validator.validate_context_sufficiency(
            context, execution_plan
        )
        
        # Should have attempted retrieval
        assert mock_kg.query.called


# ========================================
# Package 4: Structured Output Tests
# ========================================

class TestStructuredOutput:
    """Tests for Pydantic schemas"""
    
    def test_execution_result_creation(self):
        """Test ExecutionResult creation"""
        result = ExecutionResult(
            success=True,
            phases_completed=['phase1', 'phase2'],
            phase_results=[],
            total_duration_ms=1000.0,
            context={'test': 'context'},
            execution_mode=ExecutionMode.SUPERVISED
        )
        
        assert isinstance(result, ExecutionResult)
        assert result.success
        assert result.execution_mode == ExecutionMode.SUPERVISED
        assert len(result.phases_completed) == 2
    
    def test_execution_result_to_dict(self):
        """Test ExecutionResult serialization to dict"""
        result = ExecutionResult(
            success=True,
            phases_completed=['phase1'],
            phase_results=[],
            total_duration_ms=500.0,
            context={},
            execution_mode=ExecutionMode.AUTONOMOUS
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict['success'] == True
        assert 'execution_id' in result_dict
    
    def test_execution_result_to_json(self):
        """Test ExecutionResult serialization to JSON"""
        result = ExecutionResult(
            success=True,
            phases_completed=[],
            phase_results=[],
            total_duration_ms=100.0,
            context={},
            execution_mode=ExecutionMode.MANUAL
        )
        
        result_json = result.to_json()
        
        assert isinstance(result_json, str)
        assert '"success": true' in result_json.lower()


# ========================================
# Package 6: Enhanced Guardrails Tests
# ========================================

class TestExecutionSafetyGuardrails:
    """Tests for safety guardrails"""
    
    @pytest.mark.asyncio
    async def test_safety_check_no_risks(self):
        """Test safety check with no risks"""
        orchestrator = ExecutionOrchestrator()
        
        execution_plan = {'phases': [{'name': 'test_phase'}]}
        context = {'environment': 'dev'}
        
        safety_check = await orchestrator.safety_guardrail.check_execution_safety(
            execution_plan, context
        )
        
        assert isinstance(safety_check, SafetyCheck)
        assert safety_check.safe
        assert safety_check.max_risk == RiskSeverity.LOW
    
    @pytest.mark.asyncio
    async def test_safety_check_destructive_operation(self):
        """Test detection of destructive operations"""
        orchestrator = ExecutionOrchestrator()
        
        execution_plan = {'phases': [{'name': 'delete', 'action': 'delete_database'}]}
        context = {}
        
        safety_check = await orchestrator.safety_guardrail.check_execution_safety(
            execution_plan, context
        )
        
        assert not safety_check.safe
        assert safety_check.max_risk == RiskSeverity.CRITICAL
        assert len(safety_check.risks) > 0
    
    @pytest.mark.asyncio
    async def test_safety_check_sensitive_data(self):
        """Test detection of sensitive data exposure"""
        orchestrator = ExecutionOrchestrator()
        
        execution_plan = {'phases': []}
        context = {'password': 'secret123', 'api_key': 'key456'}
        
        safety_check = await orchestrator.safety_guardrail.check_execution_safety(
            execution_plan, context
        )
        
        assert not safety_check.safe
        assert len(safety_check.risks) >= 2
    
    @pytest.mark.asyncio
    async def test_safety_check_production_environment(self):
        """Test detection of production environment"""
        orchestrator = ExecutionOrchestrator()
        
        execution_plan = {}
        context = {'environment': 'production', 'url': 'https://prod.example.com'}
        
        safety_check = await orchestrator.safety_guardrail.check_execution_safety(
            execution_plan, context
        )
        
        assert safety_check.requires_approval
        assert safety_check.max_risk == RiskSeverity.HIGH


# ========================================
# Integration Tests
# ========================================

class TestExecutionOrchestratorIntegration:
    """Integration tests for complete workflows"""
    
    @pytest.mark.asyncio
    async def test_enhanced_setup_with_validation(self):
        """Test enhanced setup with context validation"""
        orchestrator = ExecutionOrchestrator(config={"execution_mode": "supervised"})
        
        context = {
            'plan': {
                'phases': [{'name': 'test_phase'}],
                'required_context': ['workspace'],
                'optional_context': []
            },
            'workspace': '/path/to/workspace'
        }
        
        validation = await orchestrator.enhanced_setup(context)
        
        assert isinstance(validation, ContextValidation)
        assert validation.is_valid
    
    @pytest.mark.asyncio
    async def test_enhanced_setup_fails_on_validation_error(self):
        """Test enhanced setup fails with invalid context"""
        orchestrator = ExecutionOrchestrator()
        
        context = {
            'plan': {
                'phases': [],
                'required_context': ['workspace', 'missing_key']
            },
            'workspace': '/path'
        }
        
        with pytest.raises(ValueError, match="Context validation failed"):
            await orchestrator.enhanced_setup(context)
    
    @pytest.mark.asyncio
    async def test_enhanced_setup_fails_on_safety_error(self):
        """Test enhanced setup fails with critical safety risks"""
        orchestrator = ExecutionOrchestrator(config={"enable_safety_checks": True})
        
        context = {
            'plan': {
                'phases': [{'name': 'delete_all', 'action': 'drop database'}],
                'required_context': []
            }
        }
        
        with pytest.raises(ValueError, match="Safety check failed"):
            await orchestrator.enhanced_setup(context)


# ========================================
# Execution Mode Tests
# ========================================

class TestExecutionModes:
    """Tests for different execution modes"""
    
    def test_autonomous_mode_initialization(self):
        """Test autonomous mode initialization"""
        orchestrator = ExecutionOrchestrator(config={"execution_mode": "autonomous"})
        
        assert orchestrator.execution_mode == ExecutionMode.AUTONOMOUS
    
    def test_supervised_mode_initialization(self):
        """Test supervised mode initialization (default)"""
        orchestrator = ExecutionOrchestrator()
        
        assert orchestrator.execution_mode == ExecutionMode.SUPERVISED
    
    def test_manual_mode_initialization(self):
        """Test manual mode initialization"""
        orchestrator = ExecutionOrchestrator(config={"execution_mode": "manual"})
        
        assert orchestrator.execution_mode == ExecutionMode.MANUAL


# ========================================
# Run Tests
# ========================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
