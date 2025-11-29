"""
Integration Tests: Tier Contract Validation (Phase 1 Implementation)

Tests that validate the APIs exposed by each tier and cross-tier communication.
These tests are CRITICAL for preventing breaking changes across tier boundaries.

Contract Tests:
- Tier 1 (Working Memory): conversation management, session tracking
- Tier 2 (Knowledge Graph): pattern storage, search, namespaces
- Tier 3 (Context Intelligence): git metrics, file hotspots, insights
- Cross-Tier: unified context manager, token budgets, quality monitoring

Updated to match actual tier implementations discovered during test execution.
"""

import pytest
from pathlib import Path
from datetime import datetime, date, timedelta
import tempfile
import shutil


# ========== TIER 1 CONTRACTS ==========

class TestTier1Contract:
    """Validate Tier 1 (Working Memory) provides required APIs"""
    
    def test_working_memory_initialization(self):
        """T1 MUST initialize without errors"""
        from src.tier1.working_memory import WorkingMemory
        
        wm = WorkingMemory()
        assert wm is not None
        assert hasattr(wm, 'conversation_manager')
        assert hasattr(wm, 'message_store')
    
    def test_import_conversation_contract(self):
        """T1 MUST provide import_conversation() with conversation_turns + import_source"""
        from src.tier1.working_memory import WorkingMemory
        
        wm = WorkingMemory()
        
        # Actual API requires conversation_turns (list of dicts) and import_source
        test_conversation = [
            {'user': 'How do I create a test?', 'assistant': 'Use pytest...'},
            {'user': 'Thanks!', 'assistant': 'You\'re welcome!'}
        ]
        
        result = wm.import_conversation(
            conversation_turns=test_conversation,
            import_source='test_tier_contracts.py'
        )
        
        # Contract: MUST return dict with these fields
        assert isinstance(result, dict)
        assert 'success' in result
        assert result['success'] is True
        assert 'conversation_id' in result
        assert 'quality_score' in result
        assert 'turns_imported' in result
        
        # Contract: conversation_id must be string
        assert isinstance(result['conversation_id'], str)
        
        # Contract: quality_score must be int
        assert isinstance(result['quality_score'], int)
        
        # Contract: turns_imported must match input
        assert result['turns_imported'] == 2
    
    def test_get_conversation_contract(self):
        """T1 MUST provide get_conversation() returning Conversation or None"""
        from src.tier1.working_memory import WorkingMemory
        from src.tier1.conversations import Conversation
        
        wm = WorkingMemory()
        
        # Import test conversation first
        test_conversation = [
            {'user': 'Test message', 'assistant': 'Test response'}
        ]
        import_result = wm.import_conversation(
            conversation_turns=test_conversation,
            import_source='test_tier_contracts.py'
        )
        conv_id = import_result['conversation_id']
        
        # Contract: get_conversation() with valid ID returns Conversation
        conv = wm.get_conversation(conv_id)
        assert conv is not None
        assert isinstance(conv, Conversation)
        assert hasattr(conv, 'conversation_id')
        assert hasattr(conv, 'title')
        assert hasattr(conv, 'created_at')
        
        # Contract: get_conversation() with invalid ID returns None
        invalid_conv = wm.get_conversation('invalid-id-12345')
        assert invalid_conv is None
    
    def test_get_recent_conversations_contract(self):
        """T1 MUST provide get_recent_conversations() returning list"""
        from src.tier1.working_memory import WorkingMemory
        from src.tier1.conversations import Conversation
        
        wm = WorkingMemory()
        
        # Add a test conversation
        test_conversation = [
            {'user': 'Test', 'assistant': 'Response'}
        ]
        wm.import_conversation(
            conversation_turns=test_conversation,
            import_source='test_tier_contracts.py'
        )
        
        # Contract: get_recent_conversations() returns list
        convs = wm.get_recent_conversations(limit=10)
        assert isinstance(convs, list)
        
        # Contract: Each item is Conversation object
        for conv in convs:
            assert isinstance(conv, Conversation)
            assert hasattr(conv, 'conversation_id')
            assert hasattr(conv, 'title')


# ========== TIER 2 CONTRACTS ==========

class TestTier2Contract:
    """Validate Tier 2 (Knowledge Graph) provides required APIs"""
    
    def test_knowledge_graph_initialization(self):
        """T2 MUST initialize without errors"""
        from src.tier2.knowledge_graph import KnowledgeGraph
        
        kg = KnowledgeGraph()
        assert kg is not None
        # NOTE: KnowledgeGraph uses connection_manager, not db_path attribute
        assert hasattr(kg, 'pattern_store')
        assert hasattr(kg, 'pattern_search')
    
    def test_store_pattern_contract(self):
        """T2 MUST provide store_pattern() with required fields"""
        from src.tier2.knowledge_graph import KnowledgeGraph
        import uuid
        
        kg = KnowledgeGraph()
        
        # FIXED: PatternStore requires pattern_id parameter
        result = kg.store_pattern(
            pattern_id=str(uuid.uuid4()),
            title='Test Pattern',
            content='Test pattern content',
            pattern_type='workflow',
            confidence=0.8,
            scope='application'
        )
        
        # Contract: MUST return dict with pattern_id
        assert isinstance(result, dict)
        assert 'pattern_id' in result
    
    def test_search_patterns_contract(self):
        """T2 MUST provide search_patterns() returning list"""
        from src.tier2.knowledge_graph import KnowledgeGraph
        import uuid
        
        kg = KnowledgeGraph()
        
        # Store a test pattern first
        kg.store_pattern(
            pattern_id=str(uuid.uuid4()),
            title='Search Test Pattern',
            content='This is test content for searching',
            pattern_type='workflow',
            confidence=0.9,
            scope='application'
        )
        
        # Contract: search_patterns() returns list
        results = kg.search_patterns(query='test')
        assert isinstance(results, list)
        
        # Contract: Each result has pattern_id and title
        for pattern in results:
            assert 'pattern_id' in pattern
            assert 'title' in pattern
    
    def test_get_pattern_contract(self):
        """T2 MUST provide get_pattern() returning pattern dict or None"""
        from src.tier2.knowledge_graph import KnowledgeGraph
        import uuid
        
        kg = KnowledgeGraph()
        
        # Store a test pattern
        store_result = kg.store_pattern(
            pattern_id=str(uuid.uuid4()),
            title='Get Pattern Test',
            content='Content for retrieval test',
            pattern_type='workflow',
            confidence=0.85,
            scope='application'
        )
        pattern_id = store_result['pattern_id']
        
        # Contract: get_pattern() with valid ID returns dict
        pattern = kg.get_pattern(pattern_id)
        assert pattern is not None
        assert isinstance(pattern, dict)
        assert 'pattern_id' in pattern
        assert 'title' in pattern
        assert pattern['title'] == 'Get Pattern Test'
        
        # Contract: get_pattern() with invalid ID returns None
        invalid_pattern = kg.get_pattern('invalid-pattern-12345')
        assert invalid_pattern is None


# ========== TIER 3 CONTRACTS ==========

class TestTier3Contract:
    """Validate Tier 3 (Context Intelligence) provides required APIs"""
    
    def test_context_intelligence_initialization(self):
        """T3 MUST initialize without errors"""
        from src.tier3.context_intelligence import ContextIntelligence
        
        ci = ContextIntelligence()
        assert ci is not None
        assert hasattr(ci, 'db_path')
    
    def test_collect_git_metrics_contract(self):
        """T3 MUST provide collect_git_metrics() returning list"""
        from src.tier3.context_intelligence import ContextIntelligence, GitMetric
        
        ci = ContextIntelligence()
        
        # Contract: collect_git_metrics() returns list (may be empty if not git repo)
        metrics = ci.collect_git_metrics(days=7)
        assert isinstance(metrics, list)
        
        # Contract: Each metric is GitMetric object
        for metric in metrics:
            assert isinstance(metric, GitMetric)
            assert hasattr(metric, 'metric_date')
            assert hasattr(metric, 'commits_count')
    
    def test_analyze_file_hotspots_contract(self):
        """T3 MUST provide analyze_file_hotspots() returning list"""
        from src.tier3.context_intelligence import ContextIntelligence, FileHotspot
        
        ci = ContextIntelligence()
        
        # Contract: analyze_file_hotspots() returns list (may be empty if not git repo)
        hotspots = ci.analyze_file_hotspots(days=30)
        assert isinstance(hotspots, list)
        
        # Contract: Each hotspot is FileHotspot object
        for hotspot in hotspots:
            assert isinstance(hotspot, FileHotspot)
            assert hasattr(hotspot, 'file_path')
            assert hasattr(hotspot, 'churn_rate')
            assert hasattr(hotspot, 'stability')
    
    def test_generate_insights_contract(self):
        """T3 MUST provide generate_insights() returning list"""
        from src.tier3.context_intelligence import ContextIntelligence, Insight
        
        ci = ContextIntelligence()
        
        # Contract: generate_insights() returns list (may be empty)
        insights = ci.generate_insights()
        assert isinstance(insights, list)
        
        # Contract: Each insight is Insight object
        for insight in insights:
            assert isinstance(insight, Insight)
            assert hasattr(insight, 'insight_type')
            assert hasattr(insight, 'severity')
            assert hasattr(insight, 'title')


# ========== CROSS-TIER INTEGRATION ==========

class TestCrossTierIntegration:
    """Validate cross-tier communication works correctly"""
    
    def test_tier1_to_tier2_pattern_learning(self):
        """Test T1 conversation can inform T2 pattern learning"""
        from src.tier1.working_memory import WorkingMemory
        from src.tier2.knowledge_graph import KnowledgeGraph
        
        wm = WorkingMemory()
        kg = KnowledgeGraph()
        
        # Simulate conversation about a coding pattern
        conv_result = wm.import_conversation(
            conversation_turns=[
                {'user': 'How do I implement retry logic?', 
                 'assistant': 'Use exponential backoff with max retries...'}
            ],
            import_source='test_tier_contracts.py'
        )
        
        # Extract pattern from conversation and store in T2
        import uuid
        pattern_result = kg.store_pattern(
            pattern_id=str(uuid.uuid4()),
            title='Retry Logic Pattern',
            content='Exponential backoff implementation',
            pattern_type='workflow',
            confidence=0.9,
            scope='application',
            metadata={'learned_from_conversation': conv_result['conversation_id']}
        )
        
        # Verify cross-tier link exists
        assert pattern_result['pattern_id'] is not None
        
        # Verify pattern can be retrieved
        pattern = kg.get_pattern(pattern_result['pattern_id'])
        assert pattern is not None
        assert pattern['metadata']['learned_from_conversation'] == conv_result['conversation_id']
    
    def test_tier2_to_tier1_context_injection(self):
        """Test T2 patterns can be injected into T1 conversation context"""
        from src.tier1.working_memory import WorkingMemory
        from src.tier2.knowledge_graph import KnowledgeGraph
        
        wm = WorkingMemory()
        kg = KnowledgeGraph()
        
        # Store a relevant pattern
        import uuid
        pattern_result = kg.store_pattern(
            pattern_id=str(uuid.uuid4()),
            title='Testing Best Practices',
            content='Always write unit tests before integration tests',
            pattern_type='workflow',
            confidence=0.95,
            scope='application'
        )
        
        # Create conversation that should reference this pattern
        conv_result = wm.import_conversation(
            conversation_turns=[
                {'user': 'How should I structure my tests?', 
                 'assistant': 'Follow testing best practices...'}
            ],
            import_source='test_tier_contracts.py'
        )
        
        # Search for relevant patterns
        patterns = kg.search_patterns(query='testing best practices')
        assert len(patterns) > 0
        
        # Verify pattern can inform conversation
        found_pattern = next(p for p in patterns if p['pattern_id'] == pattern_result['pattern_id'])
        assert found_pattern is not None
    
    def test_unified_context_manager_integration(self):
        """Test UnifiedContextManager orchestrates all tiers"""
        from src.core.context_management import UnifiedContextManager
        from src.tier1.working_memory import WorkingMemory
        from src.tier2.knowledge_graph import KnowledgeGraph
        from src.tier3.context_intelligence import ContextIntelligence
        
        # Initialize all tiers
        tier1 = WorkingMemory()
        tier2 = KnowledgeGraph()
        tier3 = ContextIntelligence()
        
        # Initialize unified manager
        ucm = UnifiedContextManager(tier1, tier2, tier3)
        
        # Build unified context
        context = ucm.build_context(
            conversation_id=None,
            user_request='How do I write a test?',
            current_files=['test_example.py'],
            token_budget=5000
        )
        
        # Verify context structure
        assert isinstance(context, dict)
        assert 'tier1_context' in context
        assert 'tier2_context' in context
        assert 'tier3_context' in context
        assert 'merged_summary' in context
        assert 'token_usage' in context


# ========== CONTRACT BREAKAGE DETECTION ==========

class TestContractBreakageDetection:
    """Tests that detect when tier contracts are violated"""
    
    def test_detect_missing_conversation_id(self):
        """Detect if T1 import_conversation stops returning conversation_id"""
        from src.tier1.working_memory import WorkingMemory
        
        wm = WorkingMemory()
        
        result = wm.import_conversation(
            conversation_turns=[
                {'user': 'Test', 'assistant': 'Response'}
            ],
            import_source='test_tier_contracts.py'
        )
        
        # This test will FAIL if contract is broken
        assert 'conversation_id' in result, "BREAKING CHANGE: conversation_id missing from import_conversation"
    
    def test_detect_invalid_quality_score(self):
        """Detect if T1 quality_score format changes"""
        from src.tier1.working_memory import WorkingMemory
        
        wm = WorkingMemory()
        
        result = wm.import_conversation(
            conversation_turns=[
                {'user': 'Test', 'assistant': 'Response'}
            ],
            import_source='test_tier_contracts.py'
        )
        
        # This test will FAIL if contract is broken
        assert isinstance(result['quality_score'], int), "BREAKING CHANGE: quality_score must be int"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
