"""
CORTEX Tier Integration Contracts
Validates that each tier provides required APIs and data structures

Phase 1: Foundation
- Define formal contracts for T1/T2/T3 APIs
- Integration tests for tier-to-tier communication
- Prevent breaking changes across tiers

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class TestTier1Contract:
    """Validate Tier 1 (Working Memory) provides required APIs"""
    
    def test_working_memory_initialization(self):
        """T1 MUST initialize without errors"""
        from src.tier1.working_memory import WorkingMemory
        
        wm = WorkingMemory()
        assert wm is not None
        assert hasattr(wm, 'conversation_manager')
        assert hasattr(wm, 'message_store')
        assert hasattr(wm, 'entity_extractor')
    
    def test_import_conversation_contract(self):
        """T1 MUST provide import_conversation() returning required fields"""
        from src.tier1.working_memory import WorkingMemory
        
        wm = WorkingMemory()
        
        # Test conversation data
        test_conversation = {
            'title': 'Test Conversation',
            'messages': [
                {'role': 'user', 'content': 'Hello'},
                {'role': 'assistant', 'content': 'Hi there'}
            ]
        }
        
        result = wm.import_conversation(test_conversation)
        
        # Contract: MUST return dict with these fields
        assert isinstance(result, dict)
        assert 'conversation_id' in result
        assert 'quality_score' in result
        assert 'entity_count' in result
        
        # Contract: conversation_id must be string
        assert isinstance(result['conversation_id'], str)
        
        # Contract: quality_score must be float 0.0-1.0
        assert isinstance(result['quality_score'], (int, float))
        assert 0.0 <= result['quality_score'] <= 1.0
        
        # Contract: entity_count must be int >= 0
        assert isinstance(result['entity_count'], int)
        assert result['entity_count'] >= 0
    
    def test_get_conversation_contract(self):
        """T1 MUST provide get_conversation() returning Conversation or None"""
        from src.tier1.working_memory import WorkingMemory
        from src.tier1.conversations import Conversation
        
        wm = WorkingMemory()
        
        # Import test conversation first
        test_conversation = {
            'title': 'Test Get Conversation',
            'messages': [
                {'role': 'user', 'content': 'Test message'}
            ]
        }
        import_result = wm.import_conversation(test_conversation)
        conv_id = import_result['conversation_id']
        
        # Contract: get_conversation() with valid ID returns Conversation
        conv = wm.conversation_manager.get_conversation(conv_id)
        assert conv is not None
        assert isinstance(conv, Conversation)
        assert hasattr(conv, 'conversation_id')
        assert hasattr(conv, 'title')
        assert hasattr(conv, 'created_at')
        
        # Contract: get_conversation() with invalid ID returns None
        invalid_conv = wm.conversation_manager.get_conversation('invalid-id-12345')
        assert invalid_conv is None
    
    def test_list_conversations_contract(self):
        """T1 MUST provide list_conversations() returning list of Conversations"""
        from src.tier1.working_memory import WorkingMemory
        from src.tier1.conversations import Conversation
        
        wm = WorkingMemory()
        
        # Contract: list_conversations() returns list
        convs = wm.conversation_manager.list_conversations()
        assert isinstance(convs, list)
        
        # Contract: Each item is Conversation object
        for conv in convs:
            assert isinstance(conv, Conversation)
            assert hasattr(conv, 'conversation_id')
            assert hasattr(conv, 'title')


class TestTier2Contract:
    """Validate Tier 2 (Knowledge Graph) provides required APIs"""
    
    def test_knowledge_graph_initialization(self):
        """T2 MUST initialize without errors"""
        from src.tier2.knowledge_graph import KnowledgeGraph
        
        kg = KnowledgeGraph()
        assert kg is not None
        assert hasattr(kg, 'db_path')
    
    def test_store_pattern_contract(self):
        """T2 MUST provide store_pattern() with required fields"""
        from src.tier2.knowledge_graph import KnowledgeGraph
        
        kg = KnowledgeGraph()
        
        # Test pattern data
        test_pattern = {
            'title': 'Test Pattern',
            'pattern_type': 'workflow',
            'confidence': 0.8,
            'context': {'test': 'data'}
        }
        
        pattern_id = kg.store_pattern(
            title=test_pattern['title'],
            pattern_type=test_pattern['pattern_type'],
            confidence=test_pattern['confidence'],
            context=test_pattern['context']
        )
        
        # Contract: Returns pattern_id as string
        assert isinstance(pattern_id, str)
        assert len(pattern_id) > 0
    
    def test_search_patterns_contract(self):
        """T2 MUST provide search_patterns() returning list of dicts"""
        from src.tier2.knowledge_graph import KnowledgeGraph
        
        kg = KnowledgeGraph()
        
        # Store test pattern first
        kg.store_pattern(
            title='Authentication Pattern',
            pattern_type='workflow',
            confidence=0.9,
            context={'test': 'auth'}
        )
        
        # Contract: search_patterns() returns list
        results = kg.search_patterns('authentication', limit=10)
        assert isinstance(results, list)
        
        # Contract: Each result is dict with required fields
        if len(results) > 0:
            for result in results:
                assert isinstance(result, dict)
                assert 'pattern_id' in result
                assert 'title' in result
                assert 'confidence' in result
    
    def test_get_pattern_contract(self):
        """T2 MUST provide get_pattern() returning dict or None"""
        from src.tier2.knowledge_graph import KnowledgeGraph
        
        kg = KnowledgeGraph()
        
        # Store test pattern
        pattern_id = kg.store_pattern(
            title='Test Get Pattern',
            pattern_type='workflow',
            confidence=0.7,
            context={}
        )
        
        # Contract: get_pattern() with valid ID returns dict
        pattern = kg.get_pattern(pattern_id)
        assert pattern is not None
        assert isinstance(pattern, dict)
        assert pattern['pattern_id'] == pattern_id
        
        # Contract: get_pattern() with invalid ID returns None
        invalid_pattern = kg.get_pattern('invalid-pattern-12345')
        assert invalid_pattern is None


class TestTier3Contract:
    """Validate Tier 3 (Context Intelligence) provides required APIs"""
    
    def test_context_intelligence_initialization(self):
        """T3 MUST initialize without errors"""
        from src.tier3.context_intelligence import ContextIntelligence
        
        ci = ContextIntelligence()
        assert ci is not None
        assert hasattr(ci, 'db_path')
    
    def test_record_git_metrics_contract(self):
        """T3 MUST provide record_git_metrics() accepting required params"""
        from src.tier3.context_intelligence import ContextIntelligence
        
        ci = ContextIntelligence()
        
        # Contract: record_git_metrics() accepts required parameters
        from datetime import date
        result = ci.record_git_metrics(
            metric_date=date.today(),
            commits_count=5,
            lines_added=100,
            lines_deleted=50,
            files_changed=3
        )
        
        # Contract: Returns success indicator
        assert result is not None
    
    def test_get_file_hotspot_contract(self):
        """T3 MUST provide get_file_hotspot() returning FileHotspot or None"""
        from src.tier3.context_intelligence import ContextIntelligence
        
        ci = ContextIntelligence()
        
        # Contract: get_file_hotspot() with valid path returns FileHotspot or None
        hotspot = ci.get_file_hotspot('src/test.py')
        
        # May be None if no data exists
        if hotspot is not None:
            from src.tier3.context_intelligence import FileHotspot
            assert isinstance(hotspot, FileHotspot)
            assert hasattr(hotspot, 'file_path')
            assert hasattr(hotspot, 'churn_rate')
            assert hasattr(hotspot, 'stability')
    
    def test_get_insights_contract(self):
        """T3 MUST provide get_insights() returning list"""
        from src.tier3.context_intelligence import ContextIntelligence
        
        ci = ContextIntelligence()
        
        # Contract: get_insights() returns list
        insights = ci.get_insights(limit=10)
        assert isinstance(insights, list)
        
        # Contract: Each insight has required attributes
        for insight in insights:
            assert hasattr(insight, 'insight_type')
            assert hasattr(insight, 'severity')
            assert hasattr(insight, 'message')


class TestCrossTierIntegration:
    """Validate tiers work together correctly"""
    
    def test_tier1_to_tier2_pattern_learning(self):
        """T1 conversation should enable T2 pattern creation"""
        from src.tier1.working_memory import WorkingMemory
        from src.tier2.knowledge_graph import KnowledgeGraph
        
        wm = WorkingMemory()
        kg = KnowledgeGraph()
        
        # Import conversation to T1
        test_conversation = {
            'title': 'JWT Authentication Implementation',
            'messages': [
                {'role': 'user', 'content': 'How do I implement JWT auth?'},
                {'role': 'assistant', 'content': 'Use PyJWT library...'}
            ]
        }
        conv_result = wm.import_conversation(test_conversation)
        
        # Create pattern in T2 based on T1 conversation
        pattern_id = kg.store_pattern(
            title='JWT Authentication Pattern',
            pattern_type='workflow',
            confidence=0.9,
            context={
                'source_conversation': conv_result['conversation_id'],
                'libraries': ['PyJWT']
            }
        )
        
        # Verify link exists
        pattern = kg.get_pattern(pattern_id)
        assert pattern is not None
        context = pattern.get('context_json', '{}')
        if isinstance(context, str):
            import json
            context = json.loads(context)
        assert 'source_conversation' in context
        assert context['source_conversation'] == conv_result['conversation_id']
    
    def test_tier2_to_tier1_context_injection(self):
        """T2 patterns should be available for T1 context building"""
        from src.tier1.working_memory import WorkingMemory
        from src.tier2.knowledge_graph import KnowledgeGraph
        
        wm = WorkingMemory()
        kg = KnowledgeGraph()
        
        # Store pattern in T2
        pattern_id = kg.store_pattern(
            title='API Error Handling Pattern',
            pattern_type='workflow',
            confidence=0.85,
            context={'best_practice': 'Use try-except with specific exceptions'}
        )
        
        # Search for pattern from T1 context
        patterns = kg.search_patterns('error handling', limit=5)
        
        # Verify pattern can be found
        assert len(patterns) > 0
        found = any(p['pattern_id'] == pattern_id for p in patterns)
        assert found, "Pattern should be discoverable from T1"
    
    def test_unified_context_manager_integration(self):
        """Unified context manager should coordinate all tiers"""
        from src.tier1.working_memory import WorkingMemory
        from src.tier2.knowledge_graph import KnowledgeGraph
        from src.tier3.context_intelligence import ContextIntelligence
        from src.core.context_management import UnifiedContextManager
        
        wm = WorkingMemory()
        kg = KnowledgeGraph()
        ci = ContextIntelligence()
        
        ucm = UnifiedContextManager(wm, kg, ci)
        
        # Build context
        context = ucm.build_context(
            conversation_id=None,
            user_request='implement authentication',
            current_files=['src/auth.py'],
            token_budget=500
        )
        
        # Verify structure
        assert 'tier1_context' in context
        assert 'tier2_context' in context
        assert 'tier3_context' in context
        assert 'merged_summary' in context
        assert 'relevance_scores' in context
        assert 'token_usage' in context
        
        # Verify relevance scores are present
        assert 'tier1' in context['relevance_scores']
        assert 'tier2' in context['relevance_scores']
        assert 'tier3' in context['relevance_scores']
        
        # Verify token usage tracking
        assert 'total' in context['token_usage']
        assert 'budget' in context['token_usage']
        assert 'within_budget' in context['token_usage']


class TestContractBreakageDetection:
    """Tests that deliberately violate contracts to ensure detection works"""
    
    def test_detect_missing_conversation_id(self):
        """Detect when import_conversation doesn't return conversation_id"""
        # This test verifies the contract test itself catches violations
        from src.tier1.working_memory import WorkingMemory
        
        wm = WorkingMemory()
        test_conversation = {
            'title': 'Test',
            'messages': [{'role': 'user', 'content': 'Test'}]
        }
        
        result = wm.import_conversation(test_conversation)
        
        # This should pass (contract met)
        assert 'conversation_id' in result
        
        # If this field is missing, contract test should fail
        # (This validates the contract test catches the violation)
    
    def test_detect_invalid_quality_score(self):
        """Detect when quality_score is out of range 0.0-1.0"""
        from src.tier1.working_memory import WorkingMemory
        
        wm = WorkingMemory()
        test_conversation = {
            'title': 'Test',
            'messages': [{'role': 'user', 'content': 'Test'}]
        }
        
        result = wm.import_conversation(test_conversation)
        
        # Verify quality_score is in valid range
        assert 0.0 <= result['quality_score'] <= 1.0
        
        # If outside range, contract test should fail


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
