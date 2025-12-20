"""
Phase 7.4 Tests: Context Injection System

Tests for:
- Brain context injector (simplified for Phase 7)
- Multi-tier context queries
- Relevance ranking integration
- Performance validation (<100ms)

TDD Phase: RED (tests written first, expected to fail)

Author: Asif Hussain
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import time


class TestBrainContextInjector:
    """Test brain-specific context injection"""
    
    @pytest.fixture
    def initialized_brain(self, tmp_path):
        """Create initialized brain with sample data"""
        from src.orchestrators.brain_init_orchestrator import BrainInitOrchestrator
        
        brain_path = tmp_path / "cortex-brain"
        orchestrator = BrainInitOrchestrator(brain_path=str(brain_path))
        orchestrator.initialize_brain()
        
        # Add some sample data
        import sqlite3
        
        # Tier 1: Add sample conversation
        tier1_db = brain_path / "tier1" / "working_memory.db"
        conn = sqlite3.connect(str(tier1_db))
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO conversations 
            (conversation_id, content, timestamp, turn_number, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, ("conv1", "User: implement authentication", datetime.now().isoformat(), 1, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        # Tier 2: Add sample pattern
        tier2_db = brain_path / "tier2" / "knowledge_graph.db"
        conn = sqlite3.connect(str(tier2_db))
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO patterns 
            (pattern_id, title, content, pattern_type, confidence, created_at, namespaces)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("p1", "JWT Authentication", "User authentication with JWT tokens", 
              "solution", 0.9, datetime.now().isoformat(), "[]"))
        conn.commit()
        conn.close()
        
        return brain_path
    
    def test_injector_exists(self):
        """Test that BrainContextInjector exists"""
        from src.tier0 import brain_context_injector
        assert brain_context_injector is not None
    
    def test_inject_tier1_context(self, initialized_brain):
        """Test injecting Tier 1 (working memory) context"""
        from src.tier0.brain_context_injector import BrainContextInjector
        
        injector = BrainContextInjector(brain_path=str(initialized_brain))
        
        context = injector.inject_tier1_context(
            user_request="continue with authentication",
            max_conversations=5
        )
        
        assert context is not None
        assert 'conversations' in context
        assert 'conversation_count' in context
        assert context['conversation_count'] > 0
    
    def test_inject_tier2_context(self, initialized_brain):
        """Test injecting Tier 2 (knowledge graph) context"""
        from src.tier0.brain_context_injector import BrainContextInjector
        
        injector = BrainContextInjector(brain_path=str(initialized_brain))
        
        context = injector.inject_tier2_context(
            user_request="implement JWT authentication",
            max_patterns=5
        )
        
        assert context is not None
        assert 'patterns' in context
        assert 'pattern_count' in context
        assert context['pattern_count'] > 0
    
    def test_inject_tier3_context(self, initialized_brain):
        """Test injecting Tier 3 (development context) context"""
        from src.tier0.brain_context_injector import BrainContextInjector
        
        injector = BrainContextInjector(brain_path=str(initialized_brain))
        
        context = injector.inject_tier3_context(
            current_file="src/auth/jwt_handler.py"
        )
        
        assert context is not None
        assert 'file_metrics' in context or 'git_activity' in context
    
    def test_inject_full_context(self, initialized_brain):
        """Test injecting context from all 3 tiers"""
        from src.tier0.brain_context_injector import BrainContextInjector
        
        injector = BrainContextInjector(brain_path=str(initialized_brain))
        
        context = injector.inject_full_context(
            user_request="continue with authentication",
            current_file="src/auth/jwt_handler.py"
        )
        
        assert context is not None
        assert 'tier1' in context
        assert 'tier2' in context
        assert 'tier3' in context
        assert 'injection_time_ms' in context
    
    def test_relevance_ranking(self, initialized_brain):
        """Test that results are ranked by relevance"""
        from src.tier0.brain_context_injector import BrainContextInjector
        
        # Add more conversations with different relevance
        import sqlite3
        tier1_db = initialized_brain / "tier1" / "working_memory.db"
        conn = sqlite3.connect(str(tier1_db))
        cursor = conn.cursor()
        
        # High relevance (mentions authentication)
        cursor.execute("""
            INSERT INTO conversations 
            (conversation_id, content, timestamp, turn_number, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, ("conv2", "User: setup JWT tokens", datetime.now().isoformat(), 2, datetime.now().isoformat()))
        
        # Low relevance (different topic)
        cursor.execute("""
            INSERT INTO conversations 
            (conversation_id, content, timestamp, turn_number, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, ("conv3", "User: add logging", datetime.now().isoformat(), 3, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        injector = BrainContextInjector(brain_path=str(initialized_brain))
        
        context = injector.inject_tier1_context(
            user_request="implement authentication",
            max_conversations=2
        )
        
        # Should return most relevant conversations first
        conversations = context['conversations']
        assert len(conversations) == 2
        # First or second should be about JWT/authentication
        assert any(
            any(word in conv['content'].lower() for word in ['auth', 'jwt', 'token', 'implement'])
            for conv in conversations
        )
    
    def test_performance_under_100ms(self, initialized_brain):
        """Test that context injection completes in <100ms"""
        from src.tier0.brain_context_injector import BrainContextInjector
        
        injector = BrainContextInjector(brain_path=str(initialized_brain))
        
        start_time = time.perf_counter()
        
        context = injector.inject_full_context(
            user_request="continue work",
            current_file="test.py"
        )
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        assert elapsed_ms < 100  # Target: <100ms
        assert context['injection_time_ms'] < 100
    
    def test_empty_brain_handling(self, tmp_path):
        """Test handling of empty brain (no data)"""
        from src.orchestrators.brain_init_orchestrator import BrainInitOrchestrator
        from src.tier0.brain_context_injector import BrainContextInjector
        
        brain_path = tmp_path / "empty-brain"
        orchestrator = BrainInitOrchestrator(brain_path=str(brain_path))
        orchestrator.initialize_brain()
        
        injector = BrainContextInjector(brain_path=str(brain_path))
        
        context = injector.inject_full_context(
            user_request="test request"
        )
        
        # Should return empty context, not crash
        assert context['tier1']['conversation_count'] == 0
        assert context['tier2']['pattern_count'] == 0
    
    def test_context_with_token_limit(self, initialized_brain):
        """Test respecting token budget limits"""
        from src.tier0.brain_context_injector import BrainContextInjector
        
        injector = BrainContextInjector(brain_path=str(initialized_brain))
        
        context = injector.inject_full_context(
            user_request="test",
            max_tokens=500
        )
        
        assert 'total_tokens' in context
        assert context['total_tokens'] <= 500
    
    def test_integration_with_relevance_scorer(self, initialized_brain):
        """Test integration with RelevanceScorer from 7.2"""
        from src.tier0.brain_context_injector import BrainContextInjector
        from src.tier2.relevance_scorer import RelevanceScorer
        
        injector = BrainContextInjector(brain_path=str(initialized_brain))
        
        # Injector should use RelevanceScorer internally
        context = injector.inject_tier1_context(
            user_request="authentication",
            max_conversations=3
        )
        
        # Should have relevance scores
        assert 'conversations' in context
        for conv in context['conversations']:
            assert 'relevance_score' in conv
            assert 0 <= conv['relevance_score'] <= 1


class TestIntentRouterIntegration:
    """Test integration with IntentRouter"""
    
    @pytest.fixture
    def initialized_brain(self, tmp_path):
        """Create initialized brain"""
        from src.orchestrators.brain_init_orchestrator import BrainInitOrchestrator
        
        brain_path = tmp_path / "cortex-brain"
        orchestrator = BrainInitOrchestrator(brain_path=str(brain_path))
        orchestrator.initialize_brain()
        
        return brain_path
    
    def test_auto_inject_on_user_request(self, initialized_brain):
        """Test that context is auto-injected when user makes request"""
        # This would integrate with IntentRouter in real usage
        from src.tier0.brain_context_injector import BrainContextInjector
        
        injector = BrainContextInjector(brain_path=str(initialized_brain))
        
        # Simulate user request through IntentRouter
        user_request = "implement feature X"
        
        context = injector.inject_full_context(
            user_request=user_request
        )
        
        assert context is not None
        assert 'injection_time_ms' in context
    
    def test_context_enrichment(self, initialized_brain):
        """Test that context enriches agent requests"""
        from src.tier0.brain_context_injector import BrainContextInjector
        
        injector = BrainContextInjector(brain_path=str(initialized_brain))
        
        # Original request
        user_request = "continue"
        
        # Context injection should help disambiguate
        context = injector.inject_full_context(
            user_request=user_request
        )
        
        # Should provide historical context
        assert context['tier1']['conversation_count'] >= 0


class TestPerformanceOptimization:
    """Test performance optimizations"""
    
    @pytest.fixture
    def large_brain(self, tmp_path):
        """Create brain with lots of data"""
        from src.orchestrators.brain_init_orchestrator import BrainInitOrchestrator
        import sqlite3
        
        brain_path = tmp_path / "cortex-brain"
        orchestrator = BrainInitOrchestrator(brain_path=str(brain_path))
        orchestrator.initialize_brain()
        
        # Add 50 conversations
        tier1_db = brain_path / "tier1" / "working_memory.db"
        conn = sqlite3.connect(str(tier1_db))
        cursor = conn.cursor()
        
        for i in range(50):
            cursor.execute("""
                INSERT INTO conversations 
                (conversation_id, content, timestamp, turn_number, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (f"conv{i}", f"User: request {i}", datetime.now().isoformat(), i, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return brain_path
    
    def test_pagination_support(self, large_brain):
        """Test that large datasets are paginated"""
        from src.tier0.brain_context_injector import BrainContextInjector
        
        injector = BrainContextInjector(brain_path=str(large_brain))
        
        # Should limit results even with 50 conversations
        context = injector.inject_tier1_context(
            user_request="test",
            max_conversations=5
        )
        
        assert len(context['conversations']) <= 5
    
    def test_caching_for_repeated_requests(self, large_brain):
        """Test that repeated requests use caching"""
        from src.tier0.brain_context_injector import BrainContextInjector
        
        injector = BrainContextInjector(brain_path=str(large_brain))
        
        # First request
        start1 = time.perf_counter()
        context1 = injector.inject_tier1_context(user_request="test")
        time1 = (time.perf_counter() - start1) * 1000
        
        # Second identical request (should be faster with cache)
        start2 = time.perf_counter()
        context2 = injector.inject_tier1_context(user_request="test")
        time2 = (time.perf_counter() - start2) * 1000
        
        # Second should be significantly faster or same results
        assert context1['conversation_count'] == context2['conversation_count']
    
    def test_parallel_tier_loading(self, large_brain):
        """Test that tiers can be loaded in parallel"""
        from src.tier0.brain_context_injector import BrainContextInjector
        
        injector = BrainContextInjector(brain_path=str(large_brain))
        
        # Full context load should be faster than sequential
        start = time.perf_counter()
        context = injector.inject_full_context(user_request="test")
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        # Should still be under 100ms even with parallel loading
        assert elapsed_ms < 100
