"""
Tests for Master Orchestrator.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

from src.orchestrators.master_orchestrator import MasterOrchestrator
from src.orchestrators.pattern_router import OrchestratorMatch, MatchType
from src.mcp.registry import OrchestratorRegistry
from src.database.planning_state_db import PlanningStateDB


@pytest.fixture
def temp_config():
    """Create temporary master orchestrator config."""
    config = {
        'schema_version': '5.0',
        'routing_rules': [
            {
                'pattern': '^plan.*$',
                'orchestrator': 'planning_v5',
                'confidence': 1.0,
                'match_type': 'regex',
                'priority': 10
            }
        ],
        'fallback': {
            'enabled': True,
            'confidence_threshold': 0.7
        },
        'lifecycle_hooks': {
            'pre_execution': [],
            'post_execution': [],
            'on_error': []
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config, f)
        yield f.name
    
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def mock_registry():
    """Create mock orchestrator registry."""
    registry = Mock(spec=OrchestratorRegistry)
    
    # Mock orchestrator
    mock_orch = Mock()
    mock_orch.name = 'planning_v5'
    mock_orch.execute = Mock(return_value=Mock(
        success=True,
        artifacts=[],
        errors=[]
    ))
    
    registry.get_orchestrator = Mock(return_value=mock_orch)
    
    return registry


@pytest.fixture
def temp_db():
    """Create temporary database."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    db = PlanningStateDB(db_path=db_path)
    yield db
    
    db.close()
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def master_orch(temp_config, mock_registry, temp_db):
    """Create Master Orchestrator instance."""
    return MasterOrchestrator(
        config_path=temp_config,
        registry=mock_registry,
        state_db=temp_db
    )


class TestMasterOrchestratorInitialization:
    """Test Master Orchestrator initialization."""
    
    def test_init_valid_config(self, master_orch):
        """Test initialization with valid config."""
        assert master_orch.router is not None
        assert master_orch.state_manager is not None
        assert master_orch.execution_engine is not None
    
    def test_init_with_llm_fallback(self, temp_config, mock_registry, temp_db):
        """Test initialization with LLM fallback."""
        mock_llm = Mock()
        
        master = MasterOrchestrator(
            config_path=temp_config,
            registry=mock_registry,
            state_db=temp_db,
            llm_fallback=mock_llm
        )
        
        assert master.llm_fallback == mock_llm


class TestRouting:
    """Test request routing."""
    
    def test_route_request_pattern_match(self, master_orch):
        """Test routing with successful pattern match."""
        match = master_orch.route_request("plan user auth", {})
        
        assert match.is_matched
        assert match.orchestrator_id == 'planning_v5'
    
    def test_route_request_no_match(self, master_orch):
        """Test routing with no pattern match."""
        match = master_orch.route_request("unrelated request", {})
        
        assert not match.is_matched
    
    def test_route_request_with_llm_fallback(self, temp_config, mock_registry, temp_db):
        """Test routing falls back to LLM when pattern confidence low."""
        mock_llm = Mock()
        mock_llm.classify = Mock(return_value=OrchestratorMatch(
            orchestrator_id='planning_v5',
            confidence=0.85,
            match_type=MatchType.FUZZY
        ))
        
        master = MasterOrchestrator(
            config_path=temp_config,
            registry=mock_registry,
            state_db=temp_db,
            llm_fallback=mock_llm
        )
        
        # Request that won't match patterns
        match = master.route_request("ambiguous request", {})
        
        # Should have tried LLM fallback
        mock_llm.classify.assert_called_once()


class TestExecution:
    """Test orchestrator execution."""
    
    def test_execute_orchestrator_success(self, master_orch, mock_registry):
        """Test successful orchestrator execution."""
        result = master_orch.execute_orchestrator(
            'planning_v5',
            {'user_request': 'test'}
        )
        
        assert result is not None
        assert result.orchestrator_id == 'planning_v5'
    
    def test_execute_orchestrator_not_found(self, master_orch, mock_registry):
        """Test execution with non-existent orchestrator."""
        mock_registry.get_orchestrator = Mock(return_value=None)
        
        with pytest.raises(ValueError, match="Orchestrator not found"):
            master_orch.execute_orchestrator('nonexistent', {})
    
    def test_execute_orchestrator_failure(self, master_orch, mock_registry):
        """Test execution when orchestrator raises error."""
        mock_orch = Mock()
        mock_orch.name = 'failing_orch'
        mock_orch.execute = Mock(side_effect=RuntimeError("Test error"))
        
        mock_registry.get_orchestrator = Mock(return_value=mock_orch)
        
        with pytest.raises(RuntimeError, match="Orchestrator execution failed"):
            master_orch.execute_orchestrator('failing_orch', {})


class TestHandleRequest:
    """Test end-to-end request handling."""
    
    def test_handle_request_success(self, master_orch):
        """Test successful request handling."""
        result = master_orch.handle_request("plan user auth")
        
        assert result is not None
        assert result.orchestrator_id == 'planning_v5'
    
    def test_handle_request_no_match(self, master_orch):
        """Test request with no orchestrator match."""
        with pytest.raises(ValueError, match="No orchestrator matched"):
            master_orch.handle_request("unrelated request")
    
    def test_handle_request_with_context(self, master_orch):
        """Test request with execution context."""
        context = {'workspace': '/path/to/workspace'}
        
        result = master_orch.handle_request(
            "plan feature X",
            context=context
        )
        
        assert result is not None


class TestMetrics:
    """Test metrics collection."""
    
    def test_get_metrics_initial(self, master_orch):
        """Test metrics before any requests."""
        metrics = master_orch.get_metrics()
        
        assert metrics['total_requests'] == 0
        assert metrics['pattern_match_count'] == 0
        assert metrics['llm_fallback_count'] == 0
    
    def test_get_metrics_after_requests(self, master_orch):
        """Test metrics after processing requests."""
        # Process some requests
        try:
            master_orch.handle_request("plan test")
        except:
            pass
        
        try:
            master_orch.handle_request("unmatched")
        except:
            pass
        
        metrics = master_orch.get_metrics()
        
        assert metrics['total_requests'] == 2


class TestConfigReload:
    """Test configuration reloading."""
    
    def test_reload_config(self, master_orch, temp_config):
        """Test reloading configuration."""
        # Modify config
        config = {
            'routing_rules': [
                {
                    'pattern': '^new.*$',
                    'orchestrator': 'new_orch',
                    'confidence': 1.0,
                    'match_type': 'regex'
                }
            ],
            'fallback': {'enabled': False}
        }
        
        with open(temp_config, 'w') as f:
            yaml.dump(config, f)
        
        # Reload
        master_orch.reload_config()
        
        # Verify new pattern works
        match = master_orch.route_request("new pattern", {})
        assert match.orchestrator_id == 'new_orch'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
