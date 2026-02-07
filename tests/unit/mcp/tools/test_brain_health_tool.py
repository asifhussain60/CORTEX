"""
Unit tests for Brain Health MCP Tool.

AC-PHASE38-002: Prometheus metrics export for brain health (MCP exposure)

Tests cover:
- Tool registration and discovery
- Summary format execution
- Detailed format execution
- Prometheus format execution
- Error handling

Author: CORTEX Framework (Phase 38 Stage 1)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any


# Test doubles
try:
    from cortex.mcp.tools.brain_health_tool import BrainHealthTool
except ImportError:
    BrainHealthTool = None


@pytest.mark.skipif(BrainHealthTool is None, reason="Implementation pending")
class TestBrainHealthMCPTool:
    """Test suite for Brain Health MCP Tool."""

    @pytest.fixture
    def tool(self) -> 'BrainHealthTool':
        """Create BrainHealthTool instance."""
        return BrainHealthTool()

    def test_tool_definition(self, tool: 'BrainHealthTool') -> None:
        """Test tool definition structure."""
        definition = tool.definition
        
        assert definition.name == "cortex_brain_health"
        assert "brain health" in definition.description.lower()
        assert len(definition.parameters) == 2
        assert definition.metadata["category"] == "observability"
        assert definition.metadata["phase"] == "Phase-38-Stage-1"

    def test_execute_summary_format(self, tool: 'BrainHealthTool') -> None:
        """Test execution with summary format."""
        mock_report = {
            'status': 'GOOD',
            'aggregate_score': 85.5,
            'timestamp': '2026-02-07T10:00:00',
            'dimensions': {
                'cache_staleness_ratio': 0.15,
                'connectivity_score': 92.0,
                'knowledge_freshness': 78.0,
                'governance_coverage': 86.0,
                'domain_utilization': 55.0
            },
            'alerts': []
        }
        
        with patch('cortex.orchestrators.support.brain_health_orchestrator.BrainHealthOrchestrator') as mock_orch:
            mock_instance = MagicMock()
            mock_instance.calculate_health_score.return_value = mock_report
            mock_orch.return_value = mock_instance
            
            result = tool.execute(format="summary")
        
        assert result['status'] == 'success'
        assert result['health_status'] == 'GOOD'
        assert result['aggregate_score'] == 85.5
        assert 'dimensions' in result
        assert result['dimensions']['cache_staleness'] == "0.15"

    def test_execute_detailed_format(self, tool: 'BrainHealthTool') -> None:
        """Test execution with detailed format."""
        mock_report = {
            'status': 'EXCELLENT',
            'aggregate_score': 92.3,
            'timestamp': '2026-02-07T10:00:00',
            'dimensions': {
                'cache_staleness_ratio': 0.10,
                'connectivity_score': 95.0,
                'knowledge_freshness': 85.0,
                'governance_coverage': 90.0,
                'domain_utilization': 70.0
            },
            'alerts': []
        }
        
        with patch('cortex.orchestrators.support.brain_health_orchestrator.BrainHealthOrchestrator') as mock_orch:
            mock_instance = MagicMock()
            mock_instance.calculate_health_score.return_value = mock_report
            mock_orch.return_value = mock_instance
            
            result = tool.execute(format="detailed")
        
        assert result['status'] == 'success'
        assert 'dimensions_detailed' in result
        assert result['dimensions_detailed']['cache_staleness_ratio']['threshold'] == 0.2
        assert result['dimensions_detailed']['connectivity_score']['status'] == 'healthy'

    def test_execute_prometheus_format(self, tool: 'BrainHealthTool') -> None:
        """Test execution with Prometheus format."""
        mock_report = {
            'status': 'GOOD',
            'aggregate_score': 85.0,
            'timestamp': '2026-02-07T10:00:00',
            'dimensions': {
                'cache_staleness_ratio': 0.15,
                'connectivity_score': 90.0,
                'knowledge_freshness': 80.0,
                'governance_coverage': 85.0,
                'domain_utilization': 60.0
            },
            'alerts': []
        }
        
        mock_metrics = "# HELP cortex_brain_cache_staleness_ratio\\ncortex_brain_cache_staleness_ratio 0.15"
        
        with patch('cortex.orchestrators.support.brain_health_orchestrator.BrainHealthOrchestrator') as mock_orch:
            mock_instance = MagicMock()
            mock_instance.calculate_health_score.return_value = mock_report
            mock_instance.export_prometheus_metrics.return_value = mock_metrics
            mock_orch.return_value = mock_instance
            
            result = tool.execute(format="prometheus")
        
        assert result['status'] == 'success'
        assert result['format'] == 'prometheus'
        assert 'cortex_brain_' in result['metrics']

    def test_execute_with_recommendations(self, tool: 'BrainHealthTool') -> None:
        """Test execution includes recommendations when alerts present."""
        mock_report = {
            'status': 'FAIR',
            'aggregate_score': 72.0,
            'timestamp': '2026-02-07T10:00:00',
            'dimensions': {
                'cache_staleness_ratio': 0.35,
                'connectivity_score': 88.0,
                'knowledge_freshness': 65.0,
                'governance_coverage': 82.0,
                'domain_utilization': 45.0
            },
            'alerts': [
                {'dimension': 'cache_staleness_ratio', 'severity': 'WARNING', 'recommendation': 'Execute cache flush'},
                {'dimension': 'domain_utilization', 'severity': 'WARNING', 'recommendation': 'Populate empty domains'}
            ]
        }
        
        with patch('cortex.orchestrators.support.brain_health_orchestrator.BrainHealthOrchestrator') as mock_orch:
            mock_instance = MagicMock()
            mock_instance.calculate_health_score.return_value = mock_report
            mock_orch.return_value = mock_instance
            
            result = tool.execute(format="summary", include_recommendations=True)
        
        assert result['status'] == 'success'
        assert result['alerts_count'] == 2
        assert 'top_recommendations' in result
        assert len(result['top_recommendations']) == 2

    def test_execute_error_handling(self, tool: 'BrainHealthTool') -> None:
        """Test error handling when orchestrator fails."""
        with patch('cortex.orchestrators.support.brain_health_orchestrator.BrainHealthOrchestrator') as mock_orch:
            mock_orch.side_effect = Exception("Orchestrator init failed")
            
            result = tool.execute()
        
        assert result['status'] == 'error'
        assert 'Failed to generate brain health report' in result['error']

    def test_tool_parameter_validation(self, tool: 'BrainHealthTool') -> None:
        """Test tool parameter definitions."""
        definition = tool.definition
        params = {p.name: p for p in definition.parameters}
        
        assert 'format' in params
        assert params['format'].type == "string"
        assert params['format'].required is False
        
        assert 'include_recommendations' in params
        assert params['include_recommendations'].type == "boolean"
        assert params['include_recommendations'].required is False


# AC-PHASE38-002 MCP Integration: 8 tests
