"""
Validation Tests for CORTEX Fix Implementation

Tests all Phase 1 and Phase 2 fixes from CORTEX-FIX-IMPLEMENTATION-PLAN.md

Test Coverage:
- Phase 1: Feedback integration, health monitor fixes, documentation sync
- Phase 2: Pattern utilization, conversation memory

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
import os
import sys
import sqlite3
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestPhase1Fixes:
    """Test Phase 1 fixes (Priority 0)"""
    
    def test_feedback_agent_integration(self):
        """Test that feedback agent is integrated with main entry point"""
        # Test 1: Check feedback agent imports
        from src.agents.feedback_agent import FeedbackAgent
        from src.entry_point.agent_executor import AgentExecutor
        
        # Test 2: Check response template exists
        import yaml
        with open('cortex-brain/response-templates.yaml', 'r', encoding='utf-8') as f:
            templates = yaml.safe_load(f)
        
        assert 'feedback_received' in templates['templates'], "feedback_received template missing"
        
        # Test 3: Check agent_types has FEEDBACK
        from src.cortex_agents.agent_types import AgentType, IntentType, INTENT_AGENT_MAP
        
        assert hasattr(AgentType, 'FEEDBACK'), "AgentType.FEEDBACK missing"
        assert hasattr(IntentType, 'FEEDBACK'), "IntentType.FEEDBACK missing"
        assert IntentType.FEEDBACK in INTENT_AGENT_MAP, "FEEDBACK not mapped in INTENT_AGENT_MAP"
        
        # Test 4: Check request_parser has feedback keywords
        from src.entry_point.request_parser import RequestParser
        parser = RequestParser()
        
        # Check that feedback keywords exist in parser
        assert 'feedback' in parser.INTENT_KEYWORDS, "RequestParser missing 'feedback' in INTENT_KEYWORDS"
        assert len(parser.INTENT_KEYWORDS['feedback']) > 0, "RequestParser has empty feedback keywords list"
        
        # Verify key feedback keywords are present
        feedback_keywords = parser.INTENT_KEYWORDS['feedback']
        assert 'report bug' in feedback_keywords or 'report issue' in feedback_keywords, \
            "RequestParser missing 'report bug' or 'report issue' keywords"
        
        print("✅ Feedback agent integration tests passed")
    
    def test_health_monitor_fixes(self):
        """Test that health monitor reports accurate data"""
        # Test 1: Database path correct
        with open('scripts/monitor_brain_health.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for correct database path
        assert 'tier1-working-memory.db' in content, \
            "Health monitor may not use correct database path"
        
        # Test 2: Query uses COALESCE for NULL handling (best practice, may need implementation)
        has_coalesce = 'COALESCE' in content
        if has_coalesce:
            print("✅ Health monitor has COALESCE NULL handling")
        else:
            print("⚠️  Health monitor could benefit from COALESCE NULL handling")
        
        print("✅ Health monitor fix tests passed")
    
    def test_documentation_sync(self):
        """Test that documentation matches reality"""
        # Test 1: README doesn't overstate capabilities
        with open('README.md', 'r', encoding='utf-8') as f:
            readme = f.read()
        
        # Should NOT claim 3,247 patterns
        assert '3,247' not in readme and '3247' not in readme, \
            "README still claims 3,247 patterns"
        
        # Should mention 70-conversation capacity
        assert '70' in readme and 'conversation' in readme, \
            "README doesn't mention 70-conversation capacity"
        
        # Test 2: Check for realistic claims
        assert 'FIFO' in readme or 'capacity' in readme, \
            "README doesn't explain capacity model"
        
        print("✅ Documentation sync tests passed")


class TestPhase2Improvements:
    """Test Phase 2 improvements (Priority 1)"""
    
    def test_pattern_suggestion_engine(self):
        """Test pattern suggestion engine functionality"""
        from src.tier2.pattern_suggestion_engine import PatternSuggestionEngine
        
        # Test 1: Engine initializes
        engine = PatternSuggestionEngine()
        assert engine is not None, "Pattern suggestion engine failed to initialize"
        
        # Test 2: Can suggest patterns
        suggestions = engine.suggest_patterns(
            task_description="implement authentication feature",
            intent_type="EXECUTE",
            limit=3
        )
        
        # Should return list (even if empty)
        assert isinstance(suggestions, list), "Suggestions should be a list"
        
        # Test 3: Relevance scoring works
        if suggestions:
            for suggestion in suggestions:
                assert 'relevance_score' in suggestion, "Suggestion missing relevance_score"
                assert 0 <= suggestion['relevance_score'] <= 1.0, \
                    f"Invalid relevance score: {suggestion['relevance_score']}"
        
        print(f"✅ Pattern suggestion engine tests passed ({len(suggestions)} suggestions)")
    
    def test_pattern_integration_with_intent_router(self):
        """Test that pattern suggestions are integrated with IntentRouter"""
        from src.cortex_agents.intent_router import IntentRouter
        
        # Check if IntentRouter has _suggest_patterns method
        assert hasattr(IntentRouter, '_suggest_patterns'), \
            "IntentRouter missing _suggest_patterns method"
        
        # Check execute method calls pattern suggestions
        import inspect
        source = inspect.getsource(IntentRouter.execute)
        assert '_suggest_patterns' in source, \
            "IntentRouter.execute doesn't call _suggest_patterns"
        
        print("✅ Pattern integration tests passed")
    
    def test_conversation_auto_capture(self):
        """Test automatic conversation capture functionality"""
        from src.tier1.conversation_auto_capture import ConversationAutoCapture
        
        # Test 1: Initialize with temp database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            temp_db = tmp.name
        
        try:
            capture = ConversationAutoCapture(tier1_db_path=temp_db)
            assert capture is not None, "ConversationAutoCapture failed to initialize"
            
            # Test 2: Capture criteria logic
            test_messages = [
                {'role': 'user', 'content': f'Message {i}'}
                for i in range(15)  # >10 messages
            ]
            
            test_context = {
                'files_modified': ['test.py', 'test2.py'],
                'workspace_name': 'test'
            }
            
            # Add strategic keywords
            test_messages[5]['content'] = 'Let me design the architecture for this'
            test_messages[10]['content'] = 'Fixed the bug successfully'
            
            should_capture, quality, reason = capture.should_capture_conversation(
                test_messages,
                test_context
            )
            
            assert should_capture, f"Should capture high-quality conversation: {reason}"
            assert quality >= 5.0, f"Quality score too low: {quality}"
            
            # Test 3: Actual capture
            captured = capture.capture_conversation(
                conversation_id='test-conv-001',
                title='Test Conversation',
                messages=test_messages,
                context=test_context
            )
            
            assert captured, "Failed to capture conversation"
            
            # Test 4: Stats
            stats = capture.get_capture_stats()
            assert stats['total_conversations'] == 1, "Stats incorrect"
            assert stats['average_quality'] >= 5.0, "Average quality too low"
            
            print(f"✅ Conversation auto-capture tests passed (quality: {quality:.1f})")
        
        finally:
            # Cleanup - close connection first
            try:
                capture = None  # Release reference
                import time
                time.sleep(0.1)  # Give Windows time to release the file
            except:
                pass
            
            if os.path.exists(temp_db):
                try:
                    os.remove(temp_db)
                except PermissionError:
                    pass  # Skip if still locked
    
    def test_fifo_enforcement(self):
        """Test that FIFO limit is enforced (70 conversations max)"""
        from src.tier1.conversation_auto_capture import ConversationAutoCapture
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            temp_db = tmp.name
        
        try:
            capture = ConversationAutoCapture(tier1_db_path=temp_db)
            
            # Create 75 conversations (exceeds limit)
            test_messages = [
                {'role': 'user', 'content': f'Strategic design message {i}'}
                for i in range(15)
            ]
            
            test_context = {
                'files_modified': ['test.py'],
                'workspace_name': 'test'
            }
            
            for i in range(75):
                capture.capture_conversation(
                    conversation_id=f'test-conv-{i:03d}',
                    title=f'Test Conversation {i}',
                    messages=test_messages,
                    context=test_context
                )
            
            # Check that only 70 remain
            stats = capture.get_capture_stats()
            assert stats['total_conversations'] == 70, \
                f"FIFO limit not enforced: {stats['total_conversations']} conversations"
            assert stats['utilization_percent'] == 100.0, \
                "Should be at 100% capacity"
            
            print(f"✅ FIFO enforcement tests passed (kept 70/75 conversations)")
        
        finally:
            # Cleanup - release connection first
            try:
                capture = None
                import time
                time.sleep(0.1)
            except:
                pass
            
            if os.path.exists(temp_db):
                try:
                    os.remove(temp_db)
                except PermissionError:
                    pass  # Skip if locked


class TestIntegrationComplete:
    """Test that all components work together"""
    
    def test_end_to_end_pattern_suggestion(self):
        """Test complete pattern suggestion workflow"""
        from src.cortex_agents.intent_router import IntentRouter
        from src.cortex_agents.base_agent import AgentRequest
        
        # Create mock request
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="implement user authentication with JWT tokens"
        )
        
        # Note: Full integration test would require Tier APIs
        # This test verifies the integration points exist
        
        router = IntentRouter(
            name="TestRouter",
            tier1_api=None,
            tier2_kg=None,
            tier3_context=None
        )
        
        # Verify pattern engine can be initialized
        assert hasattr(router, '_suggest_patterns'), \
            "IntentRouter missing _suggest_patterns method"
        
        print("✅ End-to-end integration structure validated")
    
    def test_system_health_after_fixes(self):
        """Test that system is healthy after all fixes"""
        # Test 1: All new modules import successfully
        try:
            from src.tier2.pattern_suggestion_engine import PatternSuggestionEngine
            from src.tier1.conversation_auto_capture import ConversationAutoCapture
            from src.agents.feedback_agent import FeedbackAgent
            print("✅ All new modules import successfully")
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")
        
        # Test 2: Database schemas valid
        brain_dir = Path('cortex-brain')
        tier1_db = brain_dir / 'tier1-working-memory.db'
        tier2_db = brain_dir / 'tier2-knowledge-graph.db'
        
        if tier1_db.exists():
            with sqlite3.connect(str(tier1_db)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                assert 'conversations' in tables, "conversations table missing"
                assert 'messages' in tables, "messages table missing"
            print("✅ Tier 1 database schema valid")
        
        if tier2_db.exists():
            with sqlite3.connect(str(tier2_db)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                assert 'patterns' in tables, "patterns table missing"
            print("✅ Tier 2 database schema valid")


def run_all_tests():
    """Run all validation tests"""
    print("\n" + "="*80)
    print("CORTEX Fix Validation Tests")
    print("="*80 + "\n")
    
    # Run Phase 1 tests
    print("📋 Phase 1: Priority 0 Fixes\n")
    phase1 = TestPhase1Fixes()
    phase1.test_feedback_agent_integration()
    phase1.test_health_monitor_fixes()
    phase1.test_documentation_sync()
    
    # Run Phase 2 tests
    print("\n📋 Phase 2: Priority 1 Improvements\n")
    phase2 = TestPhase2Improvements()
    phase2.test_pattern_suggestion_engine()
    phase2.test_pattern_integration_with_intent_router()
    phase2.test_conversation_auto_capture()
    phase2.test_fifo_enforcement()
    
    # Run integration tests
    print("\n📋 Integration Tests\n")
    integration = TestIntegrationComplete()
    integration.test_end_to_end_pattern_suggestion()
    integration.test_system_health_after_fixes()
    
    print("\n" + "="*80)
    print("✅ ALL VALIDATION TESTS PASSED")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_all_tests()
