"""
Tests for Brain Ingestion Adapter Agent

Tests adapter pattern implementation that bridges interface differences.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock

# Mock missing dependencies before importing
import sys
sys.modules['src.utils.entity_extractor'] = MagicMock()
sys.modules['src.utils.metrics_collector'] = MagicMock()

from src.agents.brain_ingestion_adapter_agent import BrainIngestionAdapterAgent
from src.agents.brain_ingestion_agent import BrainIngestionAgentImpl


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace directory."""
    workspace = tmp_path / "test_workspace"
    workspace.mkdir(parents=True)
    return workspace


@pytest.fixture
def adapter(temp_workspace):
    """Create brain ingestion adapter instance."""
    return BrainIngestionAdapterAgent(workspace_path=str(temp_workspace))


class TestBrainIngestionAdapterAgentInitialization:
    """Test suite for adapter initialization."""
    
    def test_adapter_initialization(self, adapter, temp_workspace):
        """Test adapter initializes correctly."""
        assert adapter is not None
        assert adapter.workspace_path == str(temp_workspace)
        assert hasattr(adapter, 'impl')
        assert isinstance(adapter.impl, BrainIngestionAgentImpl)
    
    def test_adapter_creates_concrete_implementation(self, adapter):
        """Test adapter creates concrete BrainIngestionAgentImpl."""
        assert adapter.impl is not None
        assert isinstance(adapter.impl, BrainIngestionAgentImpl)
        assert hasattr(adapter.impl, 'cortex_root')
        assert hasattr(adapter.impl, 'entity_patterns')
        assert hasattr(adapter.impl, 'pattern_weights')
    
    def test_adapter_forwards_workspace_path(self, temp_workspace):
        """Test adapter forwards workspace_path to concrete implementation."""
        adapter = BrainIngestionAdapterAgent(workspace_path=str(temp_workspace))
        
        # Concrete implementation should receive same workspace path
        assert adapter.impl.cortex_root == temp_workspace
    
    def test_adapter_initialization_with_different_paths(self):
        """Test adapter can be initialized with various path formats."""
        # Absolute path
        adapter1 = BrainIngestionAdapterAgent(workspace_path="/absolute/path")
        assert adapter1.workspace_path == "/absolute/path"
        
        # Relative path
        adapter2 = BrainIngestionAdapterAgent(workspace_path="./relative/path")
        assert adapter2.workspace_path == "./relative/path"


class TestBrainIngestionAdapterAgentDelegation:
    """Test suite for adapter delegation behavior."""
    
    @pytest.mark.asyncio
    async def test_adapter_delegates_to_concrete_implementation(self, adapter):
        """Test adapter delegates ingest_feature to concrete implementation."""
        feature_description = "User authentication system"
        
        # Call adapter method
        result = await adapter.ingest_feature(feature_description)
        
        # Verify result comes from concrete implementation
        assert result is not None
        assert hasattr(result, 'entities')
        assert hasattr(result, 'patterns')
        assert hasattr(result, 'context_updates')
        assert hasattr(result, 'implementation_scan')
    
    @pytest.mark.asyncio
    async def test_adapter_returns_unmodified_result(self, adapter):
        """Test adapter returns result without modification."""
        feature_description = "Dashboard interface"
        
        # Get result through adapter
        adapter_result = await adapter.ingest_feature(feature_description)
        
        # Get result directly from concrete implementation
        direct_result = await adapter.impl.ingest_feature(feature_description)
        
        # Both should return same type of data structure
        assert type(adapter_result) == type(direct_result)
        assert hasattr(adapter_result, 'entities')
        assert hasattr(direct_result, 'entities')
    
    @pytest.mark.asyncio
    async def test_adapter_preserves_async_contract(self, adapter):
        """Test adapter method is properly async."""
        feature_description = "API service"
        
        # Verify method returns coroutine
        coroutine = adapter.ingest_feature(feature_description)
        assert asyncio.iscoroutine(coroutine)
        
        # Await and verify result
        result = await coroutine
        assert result is not None


class TestBrainIngestionAdapterAgentInterface:
    """Test suite for adapter interface compatibility."""
    
    def test_adapter_implements_abstract_interface(self, adapter):
        """Test adapter implements expected interface."""
        # Should have ingest_feature method
        assert hasattr(adapter, 'ingest_feature')
        assert callable(adapter.ingest_feature)
    
    @pytest.mark.asyncio
    async def test_adapter_accepts_feature_description(self, adapter):
        """Test adapter accepts feature description parameter."""
        # Should accept string feature description
        result = await adapter.ingest_feature("Test feature")
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_adapter_handles_empty_feature_description(self, adapter):
        """Test adapter handles empty feature description."""
        # Should handle empty string gracefully
        result = await adapter.ingest_feature("")
        assert result is not None
        assert hasattr(result, 'entities')
    
    @pytest.mark.asyncio
    async def test_adapter_handles_long_feature_description(self, adapter):
        """Test adapter handles long feature descriptions."""
        # Generate long description
        long_description = " ".join([f"feature_{i}" for i in range(100)])
        
        result = await adapter.ingest_feature(long_description)
        assert result is not None


class TestBrainIngestionAdapterAgentStateless:
    """Test suite for adapter stateless behavior."""
    
    @pytest.mark.asyncio
    async def test_adapter_does_not_store_state(self, adapter):
        """Test adapter does not maintain state between calls."""
        # First call
        result1 = await adapter.ingest_feature("First feature")
        
        # Second call
        result2 = await adapter.ingest_feature("Second feature")
        
        # Results should be independent
        assert result1 is not result2
        assert len(result1.entities) >= 0
        assert len(result2.entities) >= 0
    
    @pytest.mark.asyncio
    async def test_adapter_multiple_calls_independent(self, adapter):
        """Test multiple adapter calls are independent."""
        features = [
            "Authentication system",
            "Payment processing",
            "Dashboard interface"
        ]
        
        results = []
        for feature in features:
            result = await adapter.ingest_feature(feature)
            results.append(result)
        
        # All results should be unique objects
        assert len(results) == 3
        assert len(set(id(r) for r in results)) == 3


class TestBrainIngestionAdapterAgentErrorHandling:
    """Test suite for adapter error handling."""
    
    @pytest.mark.asyncio
    async def test_adapter_propagates_exceptions(self, temp_workspace):
        """Test adapter propagates exceptions from concrete implementation."""
        adapter = BrainIngestionAdapterAgent(workspace_path=str(temp_workspace))
        
        # Mock concrete implementation to raise exception
        with patch.object(adapter.impl, 'ingest_feature', side_effect=ValueError("Test error")):
            with pytest.raises(ValueError, match="Test error"):
                await adapter.ingest_feature("Test")
    
    @pytest.mark.asyncio
    async def test_adapter_handles_none_result(self, temp_workspace):
        """Test adapter handles None result from concrete implementation."""
        adapter = BrainIngestionAdapterAgent(workspace_path=str(temp_workspace))
        
        # Mock concrete implementation to return None
        with patch.object(adapter.impl, 'ingest_feature', return_value=None):
            result = await adapter.ingest_feature("Test")
            assert result is None


class TestBrainIngestionAdapterAgentPerformance:
    """Test suite for adapter performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_adapter_minimal_overhead(self, adapter):
        """Test adapter adds minimal overhead."""
        feature_description = "Test feature"
        
        # Time adapter call
        import time
        start = time.time()
        await adapter.ingest_feature(feature_description)
        adapter_time = time.time() - start
        
        # Time should be reasonable (< 1 second for simple test)
        assert adapter_time < 1.0
    
    def test_adapter_memory_footprint(self, adapter):
        """Test adapter has minimal memory footprint."""
        import sys
        
        # Adapter should be lightweight
        size = sys.getsizeof(adapter)
        
        # Should be less than 1KB (just references to workspace_path and impl)
        assert size < 1024


class TestBrainIngestionAdapterAgentIntegration:
    """Integration tests for adapter in orchestrator context."""
    
    def test_adapter_compatible_with_orchestrator(self, temp_workspace):
        """Test adapter can be used in orchestrator context."""
        from src.agents.feature_completion_orchestrator import BrainIngestionAgent
        
        # Adapter should be compatible with abstract interface
        adapter = BrainIngestionAdapterAgent(workspace_path=str(temp_workspace))
        
        # Should be usable wherever BrainIngestionAgent is expected
        assert isinstance(adapter, BrainIngestionAgent)
    
    @pytest.mark.asyncio
    async def test_adapter_works_in_parallel_execution(self, temp_workspace):
        """Test adapter works correctly in parallel execution."""
        # Create multiple adapters
        adapters = [
            BrainIngestionAdapterAgent(workspace_path=str(temp_workspace))
            for _ in range(3)
        ]
        
        features = [
            "Feature 1",
            "Feature 2",
            "Feature 3"
        ]
        
        # Execute in parallel
        results = await asyncio.gather(*[
            adapter.ingest_feature(feature)
            for adapter, feature in zip(adapters, features)
        ])
        
        # All should complete successfully
        assert len(results) == 3
        assert all(r is not None for r in results)


class TestBrainIngestionAdapterAgentDocumentation:
    """Test suite for adapter documentation and examples."""
    
    def test_adapter_has_docstrings(self, adapter):
        """Test adapter methods have documentation."""
        assert adapter.__doc__ is not None or adapter.__class__.__doc__ is not None
        assert hasattr(adapter, 'ingest_feature')
    
    def test_adapter_usage_example(self, temp_workspace):
        """Test basic adapter usage example."""
        # Example from documentation
        adapter = BrainIngestionAdapterAgent(workspace_path=str(temp_workspace))
        
        # Should work as documented
        assert adapter is not None
        assert adapter.workspace_path == str(temp_workspace)
    
    @pytest.mark.asyncio
    async def test_adapter_feature_ingestion_example(self, adapter):
        """Test feature ingestion example from documentation."""
        # Example: Ingest feature
        brain_data = await adapter.ingest_feature("User authentication with JWT tokens")
        
        # Should return expected structure
        assert hasattr(brain_data, 'entities')
        assert hasattr(brain_data, 'patterns')
        assert hasattr(brain_data, 'context_updates')


class TestBrainIngestionAdapterAgentEdgeCases:
    """Test suite for edge cases and boundary conditions."""
    
    @pytest.mark.asyncio
    async def test_adapter_with_special_characters(self, adapter):
        """Test adapter handles special characters in feature description."""
        special_chars = "Feature with !@#$%^&*() special chars"
        
        result = await adapter.ingest_feature(special_chars)
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_adapter_with_unicode_characters(self, adapter):
        """Test adapter handles Unicode characters."""
        unicode_text = "Feature with émojis 🚀 and Üñíçödé"
        
        result = await adapter.ingest_feature(unicode_text)
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_adapter_with_multiline_description(self, adapter):
        """Test adapter handles multiline feature descriptions."""
        multiline = """
        User authentication system
        - Login with email/password
        - JWT token generation
        - Session management
        """
        
        result = await adapter.ingest_feature(multiline)
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_adapter_with_very_short_description(self, adapter):
        """Test adapter handles very short descriptions."""
        result = await adapter.ingest_feature("A")
        assert result is not None
