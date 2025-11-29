"""Tests for Queries and Query Handlers"""
import pytest
from src.application.queries.conversation_queries import (
    SearchContextQuery,
    GetConversationQualityQuery,
    FindSimilarPatternsQuery,
    GetConversationByIdQuery,
    GetPatternByIdQuery,
    GetRecentConversationsQuery,
    GetPatternsByNamespaceQuery
)
from src.application.queries.conversation_handlers import (
    SearchContextHandler,
    GetConversationQualityHandler,
    FindSimilarPatternsHandler,
    GetConversationByIdHandler,
    GetPatternByIdHandler,
    GetRecentConversationsHandler,
    GetPatternsByNamespaceHandler
)


@pytest.mark.asyncio
class TestSearchContextQuery:
    """Tests for SearchContextQuery"""
    
    async def test_query_creation(self):
        """Test creating search query"""
        query = SearchContextQuery(
            search_text="test query",
            namespace_filter="test.namespace",
            min_relevance=0.70,
            max_results=10
        )
        
        assert query.search_text == "test query"
        assert query.namespace_filter == "test.namespace"
        assert query.min_relevance == 0.70
        assert query.max_results == 10
    
    async def test_query_defaults(self):
        """Test query default values"""
        query = SearchContextQuery(search_text="test")
        
        assert query.namespace_filter is None
        assert query.min_relevance == 0.0
        assert query.max_results == 10


@pytest.mark.asyncio
class TestSearchContextHandler:
    """Tests for SearchContextHandler"""
    
    async def test_handler_success(self):
        """Test handler succeeds"""
        handler = SearchContextHandler()
        query = SearchContextQuery(search_text="test")
        
        result = await handler.handle(query)
        
        assert result.is_success
        assert isinstance(result.value, list)
    
    async def test_handler_with_namespace_filter(self):
        """Test handler with namespace filter"""
        handler = SearchContextHandler()
        query = SearchContextQuery(
            search_text="test",
            namespace_filter="test.namespace"
        )
        
        result = await handler.handle(query)
        
        assert result.is_success
    
    async def test_handler_rejects_empty_search(self):
        """Test handler rejects empty search text"""
        handler = SearchContextHandler()
        query = SearchContextQuery(search_text="")
        
        result = await handler.handle(query)
        
        assert result.is_failure
        assert "search_text" in result.errors[0].lower()
    
    async def test_handler_rejects_invalid_relevance(self):
        """Test handler rejects invalid relevance score"""
        handler = SearchContextHandler()
        query = SearchContextQuery(
            search_text="test",
            min_relevance=1.5  # Out of range
        )
        
        result = await handler.handle(query)
        
        assert result.is_failure
    
    async def test_handler_rejects_negative_max_results(self):
        """Test handler rejects negative max results"""
        handler = SearchContextHandler()
        query = SearchContextQuery(
            search_text="test",
            max_results=-5
        )
        
        result = await handler.handle(query)
        
        assert result.is_failure


@pytest.mark.asyncio
class TestGetConversationQualityQuery:
    """Tests for GetConversationQualityQuery"""
    
    async def test_query_creation(self):
        """Test creating quality query"""
        query = GetConversationQualityQuery(conversation_id="conv-001")
        
        assert query.conversation_id == "conv-001"


@pytest.mark.asyncio
class TestGetConversationQualityHandler:
    """Tests for GetConversationQualityHandler"""
    
    async def test_handler_success(self):
        """Test handler succeeds"""
        handler = GetConversationQualityHandler()
        query = GetConversationQualityQuery(conversation_id="conv-001")
        
        result = await handler.handle(query)
        
        assert result.is_success
        assert result.value is not None
        assert hasattr(result.value, 'score')
        assert hasattr(result.value, 'quality_level')
    
    async def test_handler_returns_quality_metrics(self):
        """Test handler returns quality metrics"""
        handler = GetConversationQualityHandler()
        query = GetConversationQualityQuery(conversation_id="conv-001")
        
        result = await handler.handle(query)
        
        assert result.is_success
        quality = result.value
        assert quality.conversation_id == "conv-001"
        assert 0.0 <= quality.score <= 1.0
        assert quality.turn_count >= 0
        assert quality.entity_count >= 0
        assert isinstance(quality.should_capture, bool)
    
    async def test_handler_rejects_empty_id(self):
        """Test handler rejects empty conversation ID"""
        handler = GetConversationQualityHandler()
        query = GetConversationQualityQuery(conversation_id="")
        
        result = await handler.handle(query)
        
        assert result.is_failure
        assert "conversation_id" in result.errors[0].lower()


@pytest.mark.asyncio
class TestFindSimilarPatternsQuery:
    """Tests for FindSimilarPatternsQuery"""
    
    async def test_query_creation(self):
        """Test creating find patterns query"""
        query = FindSimilarPatternsQuery(
            context="test context",
            namespace="test.namespace",
            pattern_type="code_structure",
            min_confidence=0.75,
            max_results=5
        )
        
        assert query.context == "test context"
        assert query.namespace == "test.namespace"
        assert query.pattern_type == "code_structure"
        assert query.min_confidence == 0.75
        assert query.max_results == 5


@pytest.mark.asyncio
class TestFindSimilarPatternsHandler:
    """Tests for FindSimilarPatternsHandler"""
    
    async def test_handler_success(self):
        """Test handler succeeds"""
        handler = FindSimilarPatternsHandler()
        query = FindSimilarPatternsQuery(
            context="test context",
            namespace="test.namespace"
        )
        
        result = await handler.handle(query)
        
        assert result.is_success
        assert isinstance(result.value, list)
    
    async def test_handler_with_pattern_type_filter(self):
        """Test handler with pattern type filter"""
        handler = FindSimilarPatternsHandler()
        query = FindSimilarPatternsQuery(
            context="test context",
            namespace="test.namespace",
            pattern_type="architecture"
        )
        
        result = await handler.handle(query)
        
        assert result.is_success
    
    async def test_handler_rejects_empty_context(self):
        """Test handler rejects empty context"""
        handler = FindSimilarPatternsHandler()
        query = FindSimilarPatternsQuery(
            context="",
            namespace="test.namespace"
        )
        
        result = await handler.handle(query)
        
        assert result.is_failure
        assert "context" in result.errors[0].lower()
    
    async def test_handler_rejects_invalid_namespace(self):
        """Test handler rejects invalid namespace"""
        handler = FindSimilarPatternsHandler()
        query = FindSimilarPatternsQuery(
            context="test",
            namespace=""
        )
        
        result = await handler.handle(query)
        
        assert result.is_failure


@pytest.mark.asyncio
class TestGetConversationByIdQuery:
    """Tests for GetConversationByIdQuery"""
    
    async def test_query_creation(self):
        """Test creating get conversation query"""
        query = GetConversationByIdQuery(conversation_id="conv-001")
        
        assert query.conversation_id == "conv-001"


@pytest.mark.asyncio
class TestGetConversationByIdHandler:
    """Tests for GetConversationByIdHandler"""
    
    async def test_handler_success(self):
        """Test handler succeeds"""
        handler = GetConversationByIdHandler()
        query = GetConversationByIdQuery(conversation_id="conv-001")
        
        result = await handler.handle(query)
        
        assert result.is_success
        # May return None if not found, but should succeed
    
    async def test_handler_rejects_empty_id(self):
        """Test handler rejects empty ID"""
        handler = GetConversationByIdHandler()
        query = GetConversationByIdQuery(conversation_id="")
        
        result = await handler.handle(query)
        
        assert result.is_failure


@pytest.mark.asyncio
class TestGetPatternByIdQuery:
    """Tests for GetPatternByIdQuery"""
    
    async def test_query_creation(self):
        """Test creating get pattern query"""
        query = GetPatternByIdQuery(pattern_id="pat-001")
        
        assert query.pattern_id == "pat-001"


@pytest.mark.asyncio
class TestGetPatternByIdHandler:
    """Tests for GetPatternByIdHandler"""
    
    async def test_handler_success(self):
        """Test handler succeeds"""
        handler = GetPatternByIdHandler()
        query = GetPatternByIdQuery(pattern_id="pat-001")
        
        result = await handler.handle(query)
        
        assert result.is_success
    
    async def test_handler_rejects_empty_id(self):
        """Test handler rejects empty ID"""
        handler = GetPatternByIdHandler()
        query = GetPatternByIdQuery(pattern_id="")
        
        result = await handler.handle(query)
        
        assert result.is_failure


@pytest.mark.asyncio
class TestGetRecentConversationsQuery:
    """Tests for GetRecentConversationsQuery"""
    
    async def test_query_creation(self):
        """Test creating recent conversations query"""
        query = GetRecentConversationsQuery(
            namespace_filter="test.namespace",
            max_results=20
        )
        
        assert query.namespace_filter == "test.namespace"
        assert query.max_results == 20
    
    async def test_query_defaults(self):
        """Test query defaults"""
        query = GetRecentConversationsQuery()
        
        assert query.namespace_filter is None
        assert query.max_results == 20


@pytest.mark.asyncio
class TestGetRecentConversationsHandler:
    """Tests for GetRecentConversationsHandler"""
    
    async def test_handler_success(self):
        """Test handler succeeds"""
        handler = GetRecentConversationsHandler()
        query = GetRecentConversationsQuery()
        
        result = await handler.handle(query)
        
        assert result.is_success
        assert isinstance(result.value, list)
    
    async def test_handler_with_namespace_filter(self):
        """Test handler with namespace filter"""
        handler = GetRecentConversationsHandler()
        query = GetRecentConversationsQuery(
            namespace_filter="test.namespace"
        )
        
        result = await handler.handle(query)
        
        assert result.is_success
    
    async def test_handler_rejects_negative_max_results(self):
        """Test handler rejects negative max results"""
        handler = GetRecentConversationsHandler()
        query = GetRecentConversationsQuery(max_results=-5)
        
        result = await handler.handle(query)
        
        assert result.is_failure


@pytest.mark.asyncio
class TestGetPatternsByNamespaceQuery:
    """Tests for GetPatternsByNamespaceQuery"""
    
    async def test_query_creation(self):
        """Test creating patterns by namespace query"""
        query = GetPatternsByNamespaceQuery(
            namespace="test.namespace",
            min_confidence=0.70,
            max_results=50
        )
        
        assert query.namespace == "test.namespace"
        assert query.min_confidence == 0.70
        assert query.max_results == 50


@pytest.mark.asyncio
class TestGetPatternsByNamespaceHandler:
    """Tests for GetPatternsByNamespaceHandler"""
    
    async def test_handler_success(self):
        """Test handler succeeds"""
        handler = GetPatternsByNamespaceHandler()
        query = GetPatternsByNamespaceQuery(namespace="test.namespace")
        
        result = await handler.handle(query)
        
        assert result.is_success
        assert isinstance(result.value, list)
    
    async def test_handler_rejects_empty_namespace(self):
        """Test handler rejects empty namespace"""
        handler = GetPatternsByNamespaceHandler()
        query = GetPatternsByNamespaceQuery(namespace="")
        
        result = await handler.handle(query)
        
        assert result.is_failure
        assert "namespace" in result.errors[0].lower()
    
    async def test_handler_rejects_invalid_confidence(self):
        """Test handler rejects invalid confidence score"""
        handler = GetPatternsByNamespaceHandler()
        query = GetPatternsByNamespaceQuery(
            namespace="test.namespace",
            min_confidence=1.5  # Out of range
        )
        
        result = await handler.handle(query)
        
        assert result.is_failure
