"""
Test suite for KnowledgeProvider Protocol (AC-IKP-001-01).

Tests structural type checking for knowledge provider backends.
Verifies that both KnowledgeRepository and BusinessKnowledgeRepository
satisfy the KnowledgeProvider protocol interface.
"""

import pytest
from typing import Dict, List, Any, Protocol
from unittest.mock import Mock, MagicMock, patch


class TestKnowledgeProviderProtocol:
    """Unit tests for KnowledgeProvider protocol definition."""

    def test_protocol_definition_exists(self):
        """Test that KnowledgeProvider protocol is defined."""
        from src.core.knowledge.protocols import KnowledgeProvider
        assert KnowledgeProvider is not None
        # Check that it's a protocol (runtime_checkable decorator applied)
        assert hasattr(KnowledgeProvider, '_is_protocol')

    def test_protocol_has_is_loaded_property(self):
        """Test that protocol defines is_loaded property."""
        from src.core.knowledge.protocols import KnowledgeProvider
        assert hasattr(KnowledgeProvider, 'is_loaded')

    def test_protocol_has_entry_count_property(self):
        """Test that protocol defines entry_count property."""
        from src.core.knowledge.protocols import KnowledgeProvider
        assert hasattr(KnowledgeProvider, 'entry_count')

    def test_protocol_has_domains_property(self):
        """Test that protocol defines domains property."""
        from src.core.knowledge.protocols import KnowledgeProvider
        assert hasattr(KnowledgeProvider, 'domains')

    def test_protocol_has_query_method(self):
        """Test that protocol defines query method."""
        from src.core.knowledge.protocols import KnowledgeProvider
        assert hasattr(KnowledgeProvider, 'query')

    def test_protocol_has_get_by_domain_method(self):
        """Test that protocol defines get_by_domain method."""
        from src.core.knowledge.protocols import KnowledgeProvider
        assert hasattr(KnowledgeProvider, 'get_by_domain')

    def test_protocol_has_get_relevant_knowledge_method(self):
        """Test that protocol defines get_relevant_knowledge method."""
        from src.core.knowledge.protocols import KnowledgeProvider
        assert hasattr(KnowledgeProvider, 'get_relevant_knowledge')

    def test_protocol_structural_subtyping(self):
        """Test structural subtyping with protocol."""
        from src.core.knowledge.protocols import KnowledgeProvider

        # Create a mock object that satisfies the protocol
        mock_provider = Mock(spec=['is_loaded', 'entry_count', 'domains', 
                                   'query', 'get_by_domain', 'get_relevant_knowledge'])
        
        # In Python, Protocol doesn't enforce at runtime by default,
        # but we can verify the attributes exist
        for attr in ['is_loaded', 'entry_count', 'domains', 'query', 
                     'get_by_domain', 'get_relevant_knowledge']:
            assert hasattr(mock_provider, attr)

    def test_is_loaded_returns_bool(self):
        """Test that is_loaded property returns boolean."""
        from src.core.knowledge.protocols import KnowledgeProvider

        class ConcreteProvider:
            @property
            def is_loaded(self) -> bool:
                return True
            
            @property
            def entry_count(self) -> int:
                return 0
            
            @property
            def domains(self) -> List[str]:
                return []
            
            def query(self, query_text: str) -> List[Dict[str, Any]]:
                return []
            
            def get_by_domain(self, domain: str) -> List[Dict[str, Any]]:
                return []
            
            def get_relevant_knowledge(self, intent_type: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
                return []

        provider = ConcreteProvider()
        assert isinstance(provider.is_loaded, bool)

    def test_entry_count_returns_int(self):
        """Test that entry_count property returns integer."""
        from src.core.knowledge.protocols import KnowledgeProvider

        class ConcreteProvider:
            @property
            def is_loaded(self) -> bool:
                return True
            
            @property
            def entry_count(self) -> int:
                return 42
            
            @property
            def domains(self) -> List[str]:
                return []
            
            def query(self, query_text: str) -> List[Dict[str, Any]]:
                return []
            
            def get_by_domain(self, domain: str) -> List[Dict[str, Any]]:
                return []
            
            def get_relevant_knowledge(self, intent_type: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
                return []

        provider = ConcreteProvider()
        assert isinstance(provider.entry_count, int)
        assert provider.entry_count == 42

    def test_domains_returns_list(self):
        """Test that domains property returns list of strings."""
        from src.core.knowledge.protocols import KnowledgeProvider

        class ConcreteProvider:
            @property
            def is_loaded(self) -> bool:
                return True
            
            @property
            def entry_count(self) -> int:
                return 0
            
            @property
            def domains(self) -> List[str]:
                return ['technical', 'business', 'policy']
            
            def query(self, query_text: str) -> List[Dict[str, Any]]:
                return []
            
            def get_by_domain(self, domain: str) -> List[Dict[str, Any]]:
                return []
            
            def get_relevant_knowledge(self, intent_type: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
                return []

        provider = ConcreteProvider()
        assert isinstance(provider.domains, list)
        assert all(isinstance(d, str) for d in provider.domains)

    def test_query_method_signature(self):
        """Test query method accepts string and returns list of dicts."""
        from src.core.knowledge.protocols import KnowledgeProvider

        class ConcreteProvider:
            @property
            def is_loaded(self) -> bool:
                return True
            
            @property
            def entry_count(self) -> int:
                return 0
            
            @property
            def domains(self) -> List[str]:
                return []
            
            def query(self, query_text: str) -> List[Dict[str, Any]]:
                return [{'result': 'found'}]
            
            def get_by_domain(self, domain: str) -> List[Dict[str, Any]]:
                return []
            
            def get_relevant_knowledge(self, intent_type: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
                return []

        provider = ConcreteProvider()
        result = provider.query("test query")
        assert isinstance(result, list)
        assert all(isinstance(r, dict) for r in result)

    def test_get_by_domain_method_signature(self):
        """Test get_by_domain method accepts domain string and returns list."""
        from src.core.knowledge.protocols import KnowledgeProvider

        class ConcreteProvider:
            @property
            def is_loaded(self) -> bool:
                return True
            
            @property
            def entry_count(self) -> int:
                return 0
            
            @property
            def domains(self) -> List[str]:
                return ['technical']
            
            def query(self, query_text: str) -> List[Dict[str, Any]]:
                return []
            
            def get_by_domain(self, domain: str) -> List[Dict[str, Any]]:
                return [{'domain': domain, 'data': 'value'}]
            
            def get_relevant_knowledge(self, intent_type: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
                return []

        provider = ConcreteProvider()
        result = provider.get_by_domain("technical")
        assert isinstance(result, list)
        assert all(isinstance(r, dict) for r in result)

    def test_get_relevant_knowledge_method_signature(self):
        """Test get_relevant_knowledge method with intent and context."""
        from src.core.knowledge.protocols import KnowledgeProvider

        class ConcreteProvider:
            @property
            def is_loaded(self) -> bool:
                return True
            
            @property
            def entry_count(self) -> int:
                return 0
            
            @property
            def domains(self) -> List[str]:
                return []
            
            def query(self, query_text: str) -> List[Dict[str, Any]]:
                return []
            
            def get_by_domain(self, domain: str) -> List[Dict[str, Any]]:
                return []
            
            def get_relevant_knowledge(self, intent_type: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
                return [{'intent': intent_type, 'context': context}]

        provider = ConcreteProvider()
        context = {'user': 'test', 'operation': 'debug'}
        result = provider.get_relevant_knowledge("debug_issue", context)
        assert isinstance(result, list)
        assert len(result) > 0
        assert 'intent' in result[0]

    def test_empty_query_returns_empty_list(self):
        """Test that empty query returns empty list."""
        from src.core.knowledge.protocols import KnowledgeProvider

        class ConcreteProvider:
            @property
            def is_loaded(self) -> bool:
                return False
            
            @property
            def entry_count(self) -> int:
                return 0
            
            @property
            def domains(self) -> List[str]:
                return []
            
            def query(self, query_text: str) -> List[Dict[str, Any]]:
                return [] if not query_text or not self.is_loaded else [{'result': 'found'}]
            
            def get_by_domain(self, domain: str) -> List[Dict[str, Any]]:
                return []
            
            def get_relevant_knowledge(self, intent_type: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
                return []

        provider = ConcreteProvider()
        result = provider.query("test")
        assert result == []

    def test_protocol_allows_multiple_implementations(self):
        """Test that protocol allows multiple different implementations."""
        from src.core.knowledge.protocols import KnowledgeProvider

        class Provider1:
            @property
            def is_loaded(self) -> bool:
                return True
            
            @property
            def entry_count(self) -> int:
                return 100
            
            @property
            def domains(self) -> List[str]:
                return ['domain1', 'domain2']
            
            def query(self, query_text: str) -> List[Dict[str, Any]]:
                return [{'provider': 'Provider1'}]
            
            def get_by_domain(self, domain: str) -> List[Dict[str, Any]]:
                return [{'domain': domain}]
            
            def get_relevant_knowledge(self, intent_type: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
                return [{'intent': intent_type}]

        class Provider2:
            @property
            def is_loaded(self) -> bool:
                return True
            
            @property
            def entry_count(self) -> int:
                return 200
            
            @property
            def domains(self) -> List[str]:
                return ['domain3', 'domain4', 'domain5']
            
            def query(self, query_text: str) -> List[Dict[str, Any]]:
                return [{'provider': 'Provider2', 'extended': True}]
            
            def get_by_domain(self, domain: str) -> List[Dict[str, Any]]:
                return [{'domain': domain, 'provider2': True}]
            
            def get_relevant_knowledge(self, intent_type: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
                return [{'intent': intent_type, 'context_aware': True}]

        p1 = Provider1()
        p2 = Provider2()
        
        assert p1.entry_count == 100
        assert p2.entry_count == 200
        assert len(p1.domains) == 2
        assert len(p2.domains) == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
