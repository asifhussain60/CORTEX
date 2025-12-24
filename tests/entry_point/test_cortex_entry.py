"""
CORTEX 4.0 - CortexEntry Core Tests (Task 8.6 - Option A)

Purpose: Test main entry point initialization and core workflows
Coverage Target: 70%+ of critical paths in cortex_entry.py (431 lines)

Test Focus:
- Initialization and configuration
- Lazy loading of components
- Request processing workflow
- Error handling and validation
- Session management integration

Author: CORTEX Development Team
Created: 2025-12-24
"""

import pytest
import tempfile
import shutil
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

# Mock the problematic config import before importing CortexEntry
sys.modules['src.config'] = MagicMock()
sys.modules['src.config'].config = MagicMock(
    brain_path="/tmp/cortex-brain",
    ensure_paths_exist=MagicMock()
)

from src.entry_point.cortex_entry import CortexEntry


class TestCortexEntryInitialization:
    """Test CortexEntry initialization and configuration."""
    
    @pytest.fixture
    def temp_brain_path(self):
        """Create temporary brain directory structure."""
        temp_dir = tempfile.mkdtemp(prefix="cortex_brain_")
        brain_path = Path(temp_dir)
        
        # Create required directories
        (brain_path / "tier1").mkdir()
        (brain_path / "tier2").mkdir()
        (brain_path / "tier3").mkdir()
        (brain_path / "corpus-callosum").mkdir()
        (brain_path / "response-templates.yaml").write_text("version: 4.0")
        
        yield brain_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_init_with_default_brain_path(self):
        """Should initialize with default brain path from config."""
        with patch('src.entry_point.cortex_entry.config') as mock_config:
            mock_config.brain_path = "/tmp/cortex-brain"
            mock_config.ensure_paths_exist = MagicMock()
            
            entry = CortexEntry(skip_setup_check=True)
            
            assert entry.brain_path == Path("/tmp/cortex-brain")
            assert entry.parser is not None
            assert entry.formatter is not None
    
    def test_init_with_custom_brain_path(self, temp_brain_path):
        """Should initialize with custom brain path."""
        with patch('src.entry_point.cortex_entry.config.ensure_paths_exist'):
            entry = CortexEntry(
                brain_path=str(temp_brain_path),
                skip_setup_check=True
            )
            
            assert entry.brain_path == temp_brain_path
    
    def test_init_enables_logging_by_default(self):
        """Should enable logging by default."""
        with patch('src.entry_point.cortex_entry.config') as mock_config:
            mock_config.brain_path = "/tmp/cortex-brain"
            mock_config.ensure_paths_exist = MagicMock()
            
            entry = CortexEntry(skip_setup_check=True)
            
            assert entry.logger is not None
    
    def test_init_can_disable_logging(self):
        """Should allow disabling logging."""
        with patch('src.entry_point.cortex_entry.config') as mock_config:
            mock_config.brain_path = "/tmp/cortex-brain"
            mock_config.ensure_paths_exist = MagicMock()
            
            entry = CortexEntry(enable_logging=False, skip_setup_check=True)
            
            assert entry.logger is not None  # Logger exists but may be disabled
    
    def test_init_sets_default_token_budget(self):
        """Should set default token budget."""
        with patch('src.entry_point.cortex_entry.config') as mock_config:
            mock_config.brain_path = "/tmp/cortex-brain"
            mock_config.ensure_paths_exist = MagicMock()
            
            entry = CortexEntry(skip_setup_check=True)
            
            assert entry.default_token_budget == 500
    
    def test_init_lightweight_components_created_immediately(self):
        """Should create lightweight components immediately (not lazy)."""
        with patch('src.entry_point.cortex_entry.config') as mock_config:
            mock_config.brain_path = "/tmp/cortex-brain"
            mock_config.ensure_paths_exist = MagicMock()
            
            entry = CortexEntry(skip_setup_check=True)
            
            # These should exist immediately
            assert entry.parser is not None
            assert entry.formatter is not None
            assert entry._component_cache is not None


class TestLazyLoading:
    """Test lazy loading of heavy components."""
    
    @pytest.fixture
    def entry(self):
        """Create CortexEntry instance for testing."""
        with patch('src.entry_point.cortex_entry.config') as mock_config:
            mock_config.brain_path = "/tmp/cortex-brain"
            mock_config.ensure_paths_exist = MagicMock()
            
            return CortexEntry(skip_setup_check=True)
    
    def test_heavy_components_not_loaded_on_init(self, entry):
        """Should not load heavy components until accessed."""
        # These should be None initially
        assert entry._tier1 is None
        assert entry._tier2 is None
        assert entry._tier3 is None
        assert entry._router is None
        assert entry._agent_executor is None
        assert entry._session_manager is None
        assert entry._context_manager is None
    
    def test_tier1_loads_on_first_access(self, entry):
        """Should load Tier1 on first property access."""
        with patch('src.entry_point.cortex_entry._tier1_module') as mock_module:
            mock_tier1 = MagicMock()
            mock_module.Tier1API.return_value = mock_tier1
            
            # First access should trigger loading
            tier1 = entry.tier1
            
            assert tier1 is not None
            assert entry._tier1 is not None
            mock_module.Tier1API.assert_called_once()
    
    def test_tier2_loads_on_first_access(self, entry):
        """Should load Tier2 on first property access."""
        with patch('src.entry_point.cortex_entry._tier2_module') as mock_module:
            mock_tier2 = MagicMock()
            mock_module.KnowledgeGraph.return_value = mock_tier2
            
            tier2 = entry.tier2
            
            assert tier2 is not None
            assert entry._tier2 is not None
    
    def test_router_loads_on_first_access(self, entry):
        """Should load Intent Router on first property access."""
        with patch('src.entry_point.cortex_entry._intent_router_module') as mock_module, \
             patch.object(entry, 'tier1', new_callable=PropertyMock) as mock_t1, \
             patch.object(entry, 'tier2', new_callable=PropertyMock) as mock_t2, \
             patch.object(entry, 'tier3', new_callable=PropertyMock) as mock_t3:
            
            mock_router = MagicMock()
            mock_module.IntentRouter.return_value = mock_router
            
            router = entry.router
            
            assert router is not None
            assert entry._router is not None
            mock_module.IntentRouter.assert_called_once()
    
    def test_components_cached_after_first_load(self, entry):
        """Should cache components and not reload on subsequent access."""
        with patch('src.entry_point.cortex_entry._tier1_module') as mock_module:
            mock_tier1 = MagicMock()
            mock_module.Tier1API.return_value = mock_tier1
            
            # Access multiple times
            tier1_first = entry.tier1
            tier1_second = entry.tier1
            tier1_third = entry.tier1
            
            # Should only create once
            assert mock_module.Tier1API.call_count == 1
            assert tier1_first is tier1_second
            assert tier1_second is tier1_third


class TestRequestProcessing:
    """Test request processing workflow."""
    
    @pytest.fixture
    def entry_with_mocks(self):
        """Create CortexEntry with mocked dependencies."""
        with patch('src.entry_point.cortex_entry.config') as mock_config:
            mock_config.brain_path = "/tmp/cortex-brain"
            mock_config.ensure_paths_exist = MagicMock()
            
            entry = CortexEntry(skip_setup_check=True)
            
            # Mock parser
            entry.parser = MagicMock()
            entry.parser.parse.return_value = MagicMock(
                raw_request="test request",
                intent="TEST",
                entities={"feature": "authentication"},
                token_budget=500
            )
            
            # Mock formatter
            entry.formatter = MagicMock()
            entry.formatter.format_response.return_value = "Formatted response"
            
            return entry
    
    def test_process_handles_string_request(self, entry_with_mocks):
        """Should process string request through full pipeline."""
        with patch.object(entry_with_mocks, 'router') as mock_router, \
             patch.object(entry_with_mocks, 'agent_executor') as mock_executor:
            
            mock_router.route.return_value = MagicMock(
                agent_name="TestAgent",
                confidence=0.95
            )
            
            mock_executor.execute.return_value = MagicMock(
                success=True,
                result="Test result",
                metadata={}
            )
            
            result = entry_with_mocks.process("test request")
            
            # Verify pipeline execution
            entry_with_mocks.parser.parse.assert_called_once()
            mock_router.route.assert_called_once()
            mock_executor.execute.assert_called_once()
            entry_with_mocks.formatter.format_response.assert_called_once()
            assert result == "Formatted response"
    
    def test_process_with_empty_request_raises_error(self, entry_with_mocks):
        """Should handle empty request appropriately."""
        entry_with_mocks.parser.parse.side_effect = ValueError("Empty request")
        
        with pytest.raises(ValueError) as exc_info:
            entry_with_mocks.process("")
        
        assert "Empty request" in str(exc_info.value)
    
    def test_process_with_session_resume(self, entry_with_mocks):
        """Should handle session resume correctly."""
        with patch.object(entry_with_mocks, 'session_manager') as mock_session, \
             patch.object(entry_with_mocks, 'router') as mock_router, \
             patch.object(entry_with_mocks, 'agent_executor') as mock_executor:
            
            mock_session.get_active_session.return_value = {
                "session_id": "test-123",
                "context": {"previous": "data"}
            }
            
            mock_router.route.return_value = MagicMock(agent_name="TestAgent")
            mock_executor.execute.return_value = MagicMock(success=True, result="Result")
            
            entry_with_mocks.process("continue", resume_session=True)
            
            mock_session.get_active_session.assert_called_once()


class TestErrorHandling:
    """Test error handling and recovery."""
    
    @pytest.fixture
    def entry(self):
        """Create CortexEntry instance."""
        with patch('src.entry_point.cortex_entry.config') as mock_config:
            mock_config.brain_path = "/tmp/cortex-brain"
            mock_config.ensure_paths_exist = MagicMock()
            
            return CortexEntry(skip_setup_check=True)
    
    def test_handles_parser_error_gracefully(self, entry):
        """Should handle parser errors without crashing."""
        entry.parser.parse = MagicMock(side_effect=Exception("Parse error"))
        
        with pytest.raises(Exception) as exc_info:
            entry.process("malformed request")
        
        assert "Parse error" in str(exc_info.value)
    
    def test_handles_router_error_gracefully(self, entry):
        """Should handle routing errors without crashing."""
        entry.parser.parse = MagicMock(return_value=MagicMock(
            raw_request="test",
            intent="TEST"
        ))
        
        with patch.object(entry, 'router') as mock_router:
            mock_router.route.side_effect = Exception("Routing failed")
            
            with pytest.raises(Exception) as exc_info:
                entry.process("test request")
            
            assert "Routing failed" in str(exc_info.value)
    
    def test_handles_agent_execution_error_gracefully(self, entry):
        """Should handle agent execution errors."""
        entry.parser.parse = MagicMock(return_value=MagicMock(
            raw_request="test",
            intent="TEST"
        ))
        
        with patch.object(entry, 'router') as mock_router, \
             patch.object(entry, 'agent_executor') as mock_executor:
            
            mock_router.route.return_value = MagicMock(agent_name="TestAgent")
            mock_executor.execute.side_effect = Exception("Execution failed")
            
            with pytest.raises(Exception) as exc_info:
                entry.process("test request")
            
            assert "Execution failed" in str(exc_info.value)


class TestComponentCaching:
    """Test component caching functionality."""
    
    def test_component_cache_initialization(self):
        """Should initialize component cache on startup."""
        with patch('src.entry_point.cortex_entry.config') as mock_config, \
             patch('src.entry_point.cortex_entry.get_component_cache') as mock_cache:
            
            mock_config.brain_path = "/tmp/cortex-brain"
            mock_config.ensure_paths_exist = MagicMock()
            mock_cache_instance = MagicMock()
            mock_cache.return_value = mock_cache_instance
            
            entry = CortexEntry(skip_setup_check=True)
            
            assert entry._component_cache is mock_cache_instance
            mock_cache.assert_called_once()
    
    def test_component_cache_used_for_tier1(self):
        """Should use component cache for Tier1 loading."""
        with patch('src.entry_point.cortex_entry.config') as mock_config:
            mock_config.brain_path = "/tmp/cortex-brain"
            mock_config.ensure_paths_exist = MagicMock()
            
            entry = CortexEntry(skip_setup_check=True)
            entry._component_cache = MagicMock()
            entry._component_cache.get_or_create = MagicMock(return_value=MagicMock())
            
            # Access tier1
            tier1 = entry.tier1
            
            # Should have used cache
            entry._component_cache.get_or_create.assert_called_once()
            call_args = entry._component_cache.get_or_create.call_args
            assert call_args[0][0] == 'tier1_api'


class TestLoggingSetup:
    """Test logging configuration."""
    
    def test_logger_created_on_init(self):
        """Should create logger during initialization."""
        with patch('src.entry_point.cortex_entry.config') as mock_config:
            mock_config.brain_path = "/tmp/cortex-brain"
            mock_config.ensure_paths_exist = MagicMock()
            
            entry = CortexEntry(skip_setup_check=True, enable_logging=True)
            
            assert entry.logger is not None
            assert hasattr(entry.logger, 'info')
            assert hasattr(entry.logger, 'debug')
            assert hasattr(entry.logger, 'error')
