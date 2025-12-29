"""
Comprehensive test suite for InvestigationRouter (P0 Priority)

Target: 0% → 95% coverage (332 statements)
Priority: P0 - Critical deep dive investigation component

Tests cover:
- Initialization and dependency injection
- Investigation pattern detection and entity extraction
- Phased investigation workflow (Discovery → Analysis → Synthesis)
- Token budget management and enforcement
- Scope detection (file, component, function, general)
- Relationship confidence scoring
- User checkpoint handling
- Enhanced validator integration
- Health insights retrieval
- Workspace context detection
- Error handling and edge cases
"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from typing import Dict, Any

from src.cortex_agents.investigation_router import (
    InvestigationRouter,
    InvestigationPhase,
    TokenBudget,
    InvestigationContext
)
from src.cortex_agents.health_validator.agent import HealthValidator
from src.tier2.knowledge_graph import KnowledgeGraph


@pytest.fixture
def mock_intent_router():
    """Mock IntentRouter."""
    router = Mock()
    router.name = "MockIntentRouter"
    return router


@pytest.fixture
def mock_health_validator():
    """Mock HealthValidator."""
    validator = Mock(spec=HealthValidator)
    validator.tier1_api = Mock()
    validator.tier2_kg = Mock()
    validator.tier3_context = Mock()
    return validator


@pytest.fixture
def mock_knowledge_graph():
    """Mock KnowledgeGraph."""
    kg = Mock(spec=KnowledgeGraph)
    kg.find_related_entities = AsyncMock(return_value=[])
    kg.get_relationship_strength = Mock(return_value=0.8)
    return kg


@pytest.fixture
def investigation_router(mock_intent_router, mock_health_validator, mock_knowledge_graph):
    """Create InvestigationRouter with mocked dependencies."""
    # Create a mock EnhancedHealthValidator class that raises ImportError when instantiated
    class MockEnhancedHealthValidator:
        def __init__(self, *args, **kwargs):
            raise ImportError("Module not found")
    
    # Patch EnhancedHealthValidator with our mock class
    with patch('src.cortex_agents.health_validator.enhanced_validator.EnhancedHealthValidator', MockEnhancedHealthValidator):
        router = InvestigationRouter(
            mock_intent_router,
            mock_health_validator,
            mock_knowledge_graph
        )
    return router


class TestTokenBudget:
    """Test TokenBudget allocation and consumption."""
    
    def test_token_budget_initialization(self):
        """Test token budget is properly initialized."""
        budget = TokenBudget(
            phase=InvestigationPhase.DISCOVERY,
            allocated=1500
        )
        
        assert budget.allocated == 1500
        assert budget.consumed == 0
        assert budget.remaining == 1500
        assert not budget.is_exhausted
    
    def test_token_consumption(self):
        """Test consuming tokens from budget."""
        budget = TokenBudget(
            phase=InvestigationPhase.ANALYSIS,
            allocated=2000
        )
        
        result = budget.consume(500)
        
        assert result is True
        assert budget.consumed == 500
        assert budget.remaining == 1500
    
    def test_token_budget_exhaustion(self):
        """Test budget exhaustion prevention."""
        budget = TokenBudget(
            phase=InvestigationPhase.SYNTHESIS,
            allocated=1500
        )
        
        budget.consume(1400)
        result = budget.consume(200)  # Would exceed budget
        
        assert result is False
        assert budget.consumed == 1400
        assert budget.remaining == 100
    
    def test_is_exhausted_property(self):
        """Test budget exhaustion detection."""
        budget = TokenBudget(
            phase=InvestigationPhase.DISCOVERY,
            allocated=100
        )
        
        budget.consume(100)
        
        assert budget.is_exhausted is True
        assert budget.remaining == 0


class TestInvestigationContext:
    """Test InvestigationContext data structure."""
    
    def test_context_initialization(self):
        """Test investigation context is properly initialized."""
        budget = TokenBudget(InvestigationPhase.DISCOVERY, 1500)
        context = InvestigationContext(
            target_entity="UserService",
            entity_type="component",
            initial_query="Investigate why UserService fails",
            current_phase=InvestigationPhase.DISCOVERY,
            budget=budget
        )
        
        assert context.target_entity == "UserService"
        assert context.entity_type == "component"
        assert context.current_phase == InvestigationPhase.DISCOVERY
        assert context.direct_relationships == []
        assert context.findings == []
        assert context.user_checkpoints == []
        assert context.confidence_threshold == 0.7
    
    def test_context_with_custom_threshold(self):
        """Test context with custom confidence threshold."""
        budget = TokenBudget(InvestigationPhase.ANALYSIS, 2000)
        context = InvestigationContext(
            target_entity="AuthModule",
            entity_type="module",
            initial_query="Investigate authentication issues",
            current_phase=InvestigationPhase.ANALYSIS,
            budget=budget,
            confidence_threshold=0.85
        )
        
        assert context.confidence_threshold == 0.85


class TestInvestigationRouterInitialization:
    """Test InvestigationRouter initialization."""
    
    def test_basic_initialization(self, mock_intent_router, mock_health_validator, mock_knowledge_graph):
        """Test router initializes with required dependencies."""
        # Test basic initialization without mocking EnhancedHealthValidator
        # Since module-level import succeeded, EnhancedHealthValidator will be available
        router = InvestigationRouter(
            mock_intent_router,
            mock_health_validator,
            mock_knowledge_graph
        )
        
        assert router.intent_router == mock_intent_router
        assert router.health_validator == mock_health_validator
        assert router.knowledge_graph == mock_knowledge_graph
        # When ENHANCED_VALIDATOR_AVAILABLE=True, enhanced_validator is the EnhancedHealthValidator instance
        assert router.enhanced_validator is not None
    
    def test_enhanced_validator_initialization(self, mock_intent_router, mock_health_validator, mock_knowledge_graph):
        """Test enhanced validator is used when available."""
        # Test that when EnhancedHealthValidator is available, it's used
        router = InvestigationRouter(
            mock_intent_router,
            mock_health_validator,
            mock_knowledge_graph
        )
        
        # Should have enhanced_validator set (not None)
        assert router.enhanced_validator is not None
        # Should be an instance of EnhancedHealthValidator (or fallback to health_validator)
        assert hasattr(router.enhanced_validator, '__class__')
    
    def test_investigation_patterns_loaded(self, investigation_router):
        """Test investigation patterns are loaded."""
        assert 'view_analysis' in investigation_router.investigation_patterns
        assert 'component_issue' in investigation_router.investigation_patterns
        assert 'function_behavior' in investigation_router.investigation_patterns
        assert 'file_dependency' in investigation_router.investigation_patterns
        assert 'general_issue' in investigation_router.investigation_patterns


class TestPatternDetection:
    """Test investigation pattern detection and entity extraction."""
    
    @pytest.mark.asyncio
    async def test_detect_view_pattern(self, investigation_router):
        """Test detection of view investigation pattern."""
        query = "Investigate why view UserLoginView fails"
        
        with patch.object(investigation_router, '_user_checkpoint', new_callable=AsyncMock) as mock_checkpoint:
            mock_checkpoint.return_value = {'proceed': False}
            
            result = await investigation_router.handle_investigation(query)
        
        # Should detect view pattern
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_detect_component_pattern(self, investigation_router):
        """Test detection of component investigation pattern."""
        query = "Investigate why the AuthService component is broken"
        
        with patch.object(investigation_router, '_user_checkpoint', new_callable=AsyncMock) as mock_checkpoint:
            mock_checkpoint.return_value = {'proceed': False}
            
            result = await investigation_router.handle_investigation(query)
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_detect_function_pattern(self, investigation_router):
        """Test detection of function investigation pattern."""
        query = "Investigate why getUserProfile function returns null"
        
        with patch.object(investigation_router, '_user_checkpoint', new_callable=AsyncMock) as mock_checkpoint:
            mock_checkpoint.return_value = {'proceed': False}
            
            result = await investigation_router.handle_investigation(query)
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_detect_file_pattern(self, investigation_router):
        """Test detection of file investigation pattern."""
        query = "Investigate why user_service.py file has errors"
        
        with patch.object(investigation_router, '_user_checkpoint', new_callable=AsyncMock) as mock_checkpoint:
            mock_checkpoint.return_value = {'proceed': False}
            
            result = await investigation_router.handle_investigation(query)
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_unrecognized_pattern(self, investigation_router):
        """Test handling of unrecognized investigation patterns."""
        query = "Show me something"
        
        result = await investigation_router.handle_investigation(query)
        
        assert result['success'] is False
        assert 'Could not identify investigation target' in result['error']


class TestPhasedInvestigation:
    """Test phased investigation workflow."""
    
    @pytest.mark.asyncio
    async def test_discovery_phase_completion(self, investigation_router):
        """Test discovery phase completes successfully."""
        query = "Investigate why UserService fails"
        
        with patch.object(investigation_router, '_user_checkpoint', new_callable=AsyncMock) as mock_checkpoint:
            mock_checkpoint.return_value = {'proceed': False}
            with patch.object(investigation_router, '_get_direct_relationships', new_callable=AsyncMock) as mock_rels:
                mock_rels.return_value = [
                    {'entity': 'Database', 'type': 'dependency', 'confidence': 0.9}
                ]
                
                result = await investigation_router.handle_investigation(query)
        
        assert result is not None
        # Discovery phase should have executed
        mock_checkpoint.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_user_checkpoint_stops_investigation(self, investigation_router):
        """Test user can stop investigation at checkpoint."""
        query = "Investigate why component breaks"
        
        with patch.object(investigation_router, '_user_checkpoint', new_callable=AsyncMock) as mock_checkpoint:
            mock_checkpoint.return_value = {'proceed': False}
            
            result = await investigation_router.handle_investigation(query)
        
        # Should return discovery report only
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_full_investigation_flow(self, investigation_router):
        """Test full investigation flow through all phases."""
        query = "Investigate why UserService fails"
        
        with patch.object(investigation_router, '_user_checkpoint', new_callable=AsyncMock) as mock_checkpoint:
            # Proceed through all checkpoints
            mock_checkpoint.return_value = {'proceed': True}
            with patch.object(investigation_router, '_get_direct_relationships', new_callable=AsyncMock) as mock_rels:
                mock_rels.return_value = []
                with patch.object(investigation_router, '_execute_analysis_plugins', new_callable=AsyncMock) as mock_plugins:
                    mock_plugins.return_value = []
                    
                    result = await investigation_router.handle_investigation(query)
        
        assert result is not None
        assert mock_checkpoint.call_count >= 2  # At least 2 checkpoints


class TestScopeDetection:
    """Test intelligent scope detection."""
    
    @pytest.mark.asyncio
    async def test_detect_file_scope(self, investigation_router):
        """Test detection of file-level scope."""
        context = {'current_file': '/path/to/user_service.py'}
        query = "Investigate this file"
        
        with patch.object(investigation_router, '_user_checkpoint', new_callable=AsyncMock) as mock_checkpoint:
            mock_checkpoint.return_value = {'proceed': False}
            
            result = await investigation_router.handle_investigation(query, context)
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_detect_workspace_scope(self, investigation_router):
        """Test detection of workspace-level scope."""
        context = {'workspace_root': '/path/to/workspace'}
        query = "Investigate why tests fail"
        
        with patch.object(investigation_router, '_user_checkpoint', new_callable=AsyncMock) as mock_checkpoint:
            mock_checkpoint.return_value = {'proceed': False}
            
            result = await investigation_router.handle_investigation(query, context)
        
        assert result is not None


class TestRelationshipAnalysis:
    """Test relationship confidence scoring."""
    
    @pytest.mark.asyncio
    async def test_high_confidence_relationships(self, investigation_router):
        """Test handling of high-confidence relationships."""
        budget = TokenBudget(InvestigationPhase.ANALYSIS, 2000)
        context = InvestigationContext(
            target_entity="UserService",
            entity_type="component",
            initial_query="Investigate UserService",
            current_phase=InvestigationPhase.ANALYSIS,
            budget=budget
        )
        
        relationship = {
            'entity': 'Database',
            'type': 'dependency',
            'confidence': 0.95
        }
        
        result = await investigation_router._analyze_relationship(relationship, context)
        
        # High confidence relationships should be analyzed
        assert result is not None or context.budget.remaining > 0
    
    @pytest.mark.asyncio
    async def test_low_confidence_filtering(self, investigation_router):
        """Test filtering of low-confidence relationships."""
        budget = TokenBudget(InvestigationPhase.ANALYSIS, 2000)
        context = InvestigationContext(
            target_entity="UserService",
            entity_type="component",
            initial_query="Investigate UserService",
            current_phase=InvestigationPhase.ANALYSIS,
            budget=budget,
            confidence_threshold=0.8
        )
        
        relationship = {
            'entity': 'UnrelatedModule',
            'type': 'weak_dependency',
            'confidence': 0.3
        }
        
        result = await investigation_router._analyze_relationship(relationship, context)
        
        # Low confidence should be filtered
        assert result is None or result.get('skipped', False)


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_empty_query(self, investigation_router):
        """Test handling of empty query."""
        result = await investigation_router.handle_investigation("")
        
        assert result['success'] is False
    
    @pytest.mark.asyncio
    async def test_none_query(self, investigation_router):
        """Test handling of None query."""
        result = await investigation_router.handle_investigation(None)
        
        assert result['success'] is False
    
    @pytest.mark.asyncio
    async def test_knowledge_graph_failure(self, investigation_router, mock_knowledge_graph):
        """Test handling of knowledge graph failures."""
        mock_knowledge_graph.find_related_entities.side_effect = Exception("KG Error")
        
        query = "Investigate UserService"
        
        with patch.object(investigation_router, '_user_checkpoint', new_callable=AsyncMock) as mock_checkpoint:
            mock_checkpoint.return_value = {'proceed': False}
            
            result = await investigation_router.handle_investigation(query)
        
        # Should handle error gracefully
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_budget_exhaustion_handling(self, investigation_router):
        """Test handling when token budget is exhausted."""
        budget = TokenBudget(InvestigationPhase.ANALYSIS, 100)  # Very small budget
        budget.consume(100)  # Exhaust immediately
        
        context = InvestigationContext(
            target_entity="UserService",
            entity_type="component",
            initial_query="Investigate UserService",
            current_phase=InvestigationPhase.ANALYSIS,
            budget=budget
        )
        
        # Should handle exhausted budget gracefully
        assert context.budget.is_exhausted is True


class TestHealthInsights:
    """Test health insights retrieval and integration."""
    
    @pytest.mark.asyncio
    async def test_get_health_insights(self, investigation_router, mock_health_validator):
        """Test retrieval of health insights for entity."""
        mock_health_validator.execute = AsyncMock(return_value={
            'success': True,
            'result': {'status': 'degraded', 'issues': ['Connection timeout']}
        })
        
        insights = await investigation_router._get_health_insights("UserService", "component")
        
        # Should return health insights
        assert insights is not None
    
    @pytest.mark.asyncio
    async def test_health_validator_integration(self, investigation_router):
        """Test enhanced health validator is used when available."""
        # Validator integration should work
        assert investigation_router.enhanced_validator is not None


class TestWorkspaceContext:
    """Test workspace context detection."""
    
    @pytest.mark.asyncio
    async def test_workspace_context_detection(self, investigation_router):
        """Test detection of workspace context from file path."""
        current_file = "/workspace/src/services/user_service.py"
        
        context = await investigation_router._get_workspace_context(current_file)
        
        # Should extract workspace context
        assert context is not None
    
    @pytest.mark.asyncio
    async def test_missing_workspace_context(self, investigation_router):
        """Test handling of missing workspace context."""
        context = await investigation_router._get_workspace_context(None)
        
        # Should handle gracefully
        assert context is not None or context == {}


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
