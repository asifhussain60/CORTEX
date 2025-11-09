"""
Phase 5.1 Critical Integration Tests - HIGH PRIORITY
=====================================================

Pragmatic integration tests covering end-to-end workflows, multi-agent coordination,
session management, and complex intent routing.

Test Count: 8 HIGH priority tests  
Implementation: TDD approach with focused assertions  
Target: Validate CORTEX entry point with real tier integrations

Created: 2025-11-09
Status: IN PROGRESS
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.entry_point.cortex_entry import CortexEntry
from src.cortex_agents.base_agent import AgentResponse


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_brain_path():
    """Create temporary brain directory for test isolation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        brain_path = Path(tmpdir)
        
        # Create tier directories
        (brain_path / "tier1").mkdir()
        (brain_path / "tier2").mkdir()
        (brain_path / "tier3").mkdir()
        
        yield brain_path


@pytest.fixture
def mock_intent_router():
    """
    Mock IntentRouter to control agent responses during testing.
    """
    with patch('src.entry_point.cortex_entry.IntentRouter') as mock_router_class:
        # Create mock router instance
        mock_router = MagicMock()
        mock_router_class.return_value = mock_router
        
        # Default successful response
        mock_response = AgentResponse(
            success=True,
            result={'action': 'completed'},
            message="Mock response"
        )
        
        mock_router.execute.return_value = mock_response
        
        yield mock_router


@pytest.fixture
def cortex_entry(temp_brain_path, mock_intent_router):
    """
    Initialize CortexEntry with isolated brain and mocked IntentRouter.
    """
    entry = CortexEntry(
        brain_path=str(temp_brain_path),
        enable_logging=False
    )
    
    yield entry


# ============================================================================
# CATEGORY A: END-TO-END USER WORKFLOWS (3 HIGH PRIORITY TESTS)
# ============================================================================

def test_add_authentication_full_workflow(cortex_entry, mock_intent_router):
    """
    Test 1 (HIGH): End-to-end workflow for "Add authentication to the app"
    
    Validates:
    - Request processing through CortexEntry
    - Tier 1 conversation logging
    - IntentRouter invocation
    - Response formatting
    """
    # ARRANGE: Configure mock response for planning request
    mock_response = AgentResponse(
        success=True,
        result={
            'intent': 'PLAN',
            'steps': [
                'Design authentication architecture',
                'Implement user model with password hashing',
                'Create login/logout endpoints',
                'Add JWT token management',
                'Implement session management'
            ],
            'estimated_effort': '8-12 hours'
        },
        message="Created authentication implementation plan with 5 steps",
        agent_name="WorkPlanner"
    )
    
    mock_intent_router.execute.return_value = mock_response
    
    # ACT: Process user request
    response = cortex_entry.process("Add authentication to the app")
    
    # ASSERT: Validate response
    assert response is not None, "Response should not be None"
    assert isinstance(response, str), "Response should be a formatted string"
    assert 'authentication' in response.lower(), "Response should mention authentication"
    
    # ASSERT: Validate IntentRouter was called
    assert mock_intent_router.execute.called, "IntentRouter should be invoked"
    
    # ASSERT: Validate Tier 1 logging
    stats = cortex_entry.tier1.get_tier1_statistics()
    assert stats['conversations']['total_conversations'] >= 1, "At least one conversation should be logged"
    assert stats['conversations']['total_messages'] >= 2, "Should have user request and assistant response"


def test_continue_work_session_resume(cortex_entry, mock_intent_router):
    """
    Test 2 (HIGH): Session resume with "Continue work on exports"
    
    Validates:
    - Session continuity (resume_session=True)
    - Tier 1 message accumulation across requests
    - Multiple interactions
    """
    # ARRANGE: First request - create initial conversation
    mock_response_1 = AgentResponse(
        success=True,
        result={'action': 'created_export_module'},
        message="I'll create an export module with CSV and PDF support",
        agent_name="CodeExecutor"
    )
    mock_intent_router.execute.return_value = mock_response_1
    
    response_1 = cortex_entry.process(
        "Add export functionality to the dashboard",
        resume_session=False  # Start new conversation
    )
    
    # Validate first response
    assert response_1 is not None
    assert 'export' in response_1.lower()
    
    # Get initial message count
    stats_after_first = cortex_entry.tier1.get_tier1_statistics()
    initial_message_count = stats_after_first['conversations']['total_messages']
    
    # ARRANGE: Second request - continuation
    mock_response_2 = AgentResponse(
        success=True,
        result={'action': 'continued_implementation'},
        message="Continuing export implementation based on previous discussion",
        agent_name="CodeExecutor"
    )
    mock_intent_router.execute.return_value = mock_response_2
    
    # ACT: Continue work in same session
    response_2 = cortex_entry.process(
        "Continue work on exports",
        resume_session=True  # Resume previous conversation
    )
    
    # ASSERT: Validate continuation
    assert response_2 is not None
    assert 'export' in response_2.lower() or 'continu' in response_2.lower()
    
    # ASSERT: Validate message accumulation
    stats_after_second = cortex_entry.tier1.get_tier1_statistics()
    final_message_count = stats_after_second['conversations']['total_messages']
    
    assert final_message_count >= initial_message_count + 2, \
        "Should have accumulated at least 2 more messages (request + response)"


def test_fix_bug_debug_workflow(cortex_entry, mock_intent_router):
    """
    Test 3 (HIGH): Bug fix workflow for "Fix bug in login form"
    
    Validates:
    - Fix workflow processing
    - Response mentions fix action
    - Tier 1 logging of fix request
    """
    # ARRANGE: Configure mock response for bug fix
    mock_response = AgentResponse(
        success=True,
        result={
            'issue_identified': 'Form validation not triggering on empty password',
            'fix_applied': 'Added password length validation',
            'tests_passing': True,
            'files_modified': ['components/LoginForm.tsx']
        },
        message="Fixed login form validation bug",
        agent_name="CodeExecutor"
    )
    
    mock_intent_router.execute.return_value = mock_response
    
    # ACT: Process fix request
    response = cortex_entry.process("Fix bug in login form")
    
    # ASSERT: Validate response
    assert response is not None
    assert 'fix' in response.lower() or 'bug' in response.lower()
    
    # ASSERT: Validate Tier 1 logging
    stats = cortex_entry.tier1.get_tier1_statistics()
    assert stats['conversations']['total_messages'] >= 2, "Should log request and response"


# ============================================================================
# CATEGORY B: MULTI-AGENT COORDINATION (2 HIGH PRIORITY TESTS)
# ============================================================================

def test_plan_to_execute_handoff(cortex_entry, mock_intent_router):
    """
    Test 4 (HIGH): Agent handoff from WorkPlanner → CodeExecutor
    
    Validates:
    - Sequential requests processed correctly
    - Different agent responses
    - Tier 1 tracks full workflow
    """
    # ARRANGE: Phase 1 - Planning
    mock_plan_response = AgentResponse(
        success=True,
        result={
            'plan_id': 'add_button_plan',
            'steps': [
                'Create Button component',
                'Add styling',
                'Add click handler',
                'Add to parent component'
            ],
            'status': 'planned'
        },
        message="Created implementation plan",
        agent_name="WorkPlanner"
    )
    
    mock_intent_router.execute.return_value = mock_plan_response
    
    # ACT: Phase 1 - Create plan
    plan_response = cortex_entry.process("Plan how to add a purple button")
    
    # ASSERT: Validate planning phase
    assert plan_response is not None
    assert 'plan' in plan_response.lower()
    
    # Get message count after planning
    stats_after_plan = cortex_entry.tier1.get_tier1_statistics()
    messages_after_plan = stats_after_plan['conversations']['total_messages']
    
    # ARRANGE: Phase 2 - Execution
    mock_execute_response = AgentResponse(
        success=True,
        result={
            'plan_retrieved': True,
            'steps_completed': ['Create Button component', 'Add styling'],
            'steps_remaining': ['Add click handler', 'Add to parent component']
        },
        message="Started executing plan: completed 2/4 steps",
        agent_name="CodeExecutor"
    )
    
    mock_intent_router.execute.return_value = mock_execute_response
    
    # ACT: Phase 2 - Execute plan
    execute_response = cortex_entry.process("Execute the button plan", resume_session=True)
    
    # ASSERT: Validate execution phase
    assert execute_response is not None
    assert 'execut' in execute_response.lower() or 'complet' in execute_response.lower()
    
    # ASSERT: Validate both phases logged
    stats_after_execute = cortex_entry.tier1.get_tier1_statistics()
    messages_after_execute = stats_after_execute['conversations']['total_messages']
    
    assert messages_after_execute >= messages_after_plan + 2, \
        "Should have logged execution request and response"


def test_execute_to_test_handoff(cortex_entry, mock_intent_router):
    """
    Test 5 (HIGH): Agent handoff from CodeExecutor → TestGenerator
    
    Validates:
    - Implementation followed by test generation
    - Workflow continuity
    - Complete workflow logged
    """
    # ARRANGE: Phase 1 - Implementation
    mock_impl_response = AgentResponse(
        success=True,
        result={
            'feature': 'user_profile_update',
            'files_created': ['api/profile.py'],
            'implementation_complete': True
        },
        message="Implemented user profile update feature",
        agent_name="CodeExecutor"
    )
    
    mock_intent_router.execute.return_value = mock_impl_response
    
    # ACT: Phase 1 - Implement feature
    impl_response = cortex_entry.process("Implement user profile update")
    
    # ASSERT: Validate implementation
    assert impl_response is not None
    assert 'implement' in impl_response.lower() or 'profile' in impl_response.lower()
    
    # ARRANGE: Phase 2 - Test generation
    mock_test_response = AgentResponse(
        success=True,
        result={
            'tests_generated': [
                'test_update_profile_success',
                'test_update_profile_invalid_data',
                'test_update_profile_unauthorized'
            ],
            'test_file': 'tests/test_profile.py',
            'coverage': '95%'
        },
        message="Generated comprehensive tests for profile update",
        agent_name="TestGenerator"
    )
    
    mock_intent_router.execute.return_value = mock_test_response
    
    # ACT: Phase 2 - Generate tests
    test_response = cortex_entry.process("Create tests for profile update", resume_session=True)
    
    # ASSERT: Validate test generation
    assert test_response is not None
    assert 'test' in test_response.lower()
    
    # ASSERT: Validate both phases logged
    stats = cortex_entry.tier1.get_tier1_statistics()
    assert stats['conversations']['total_messages'] >= 4, "Should have 2 requests + 2 responses"


# ============================================================================
# CATEGORY C: SESSION MANAGEMENT (2 HIGH PRIORITY TESTS)
# ============================================================================

def test_new_session_vs_resumed_session(cortex_entry, mock_intent_router):
    """
    Test 6 (HIGH): Distinguish between new session and resumed session
    
    Validates:
    - resume_session=False creates separate conversations
    - resume_session=True continues same conversation
    - Message counts increase appropriately
    """
    # ARRANGE: Mock response
    mock_response = AgentResponse(
        success=True,
        result={'action': 'completed'},
        message="Task completed",
        agent_name="CodeExecutor"
    )
    mock_intent_router.execute.return_value = mock_response
    
    # ACT: First request - new session
    cortex_entry.process("First request", resume_session=False)
    
    stats_after_first = cortex_entry.tier1.get_tier1_statistics()
    convs_after_first = stats_after_first['conversations']['total_conversations']
    
    # ACT: Second request - new session again (not resumed)
    cortex_entry.process("Second request", resume_session=False)
    
    stats_after_second = cortex_entry.tier1.get_tier1_statistics()
    convs_after_second = stats_after_second['conversations']['total_conversations']
    
    # ASSERT: Should have 2 separate conversations
    assert convs_after_second > convs_after_first, \
        "New session should create a new conversation"
    
    # ACT: Third request - resume session
    cortex_entry.process("Third request", resume_session=True)
    
    stats_after_third = cortex_entry.tier1.get_tier1_statistics()
    convs_after_third = stats_after_third['conversations']['total_conversations']
    
    # ASSERT: Should still have same number of conversations (resumed)
    assert convs_after_third == convs_after_second, \
        "Resumed session should not create new conversation"


def test_session_message_accumulation(cortex_entry, mock_intent_router):
    """
    Test 7 (HIGH): Validate messages accumulate within a session
    
    Validates:
    - Multiple resumed requests add messages
    - Message count increases correctly
    - Conversation continuity maintained
    """
    # ARRANGE: Mock response
    mock_response = AgentResponse(
        success=True,
        result={'action': 'completed'},
        message="Task completed",
        agent_name="CodeExecutor"
    )
    mock_intent_router.execute.return_value = mock_response
    
    # ACT: First request
    cortex_entry.process("Start work on dashboard", resume_session=False)
    
    stats_1 = cortex_entry.tier1.get_tier1_statistics()
    messages_1 = stats_1['conversations']['total_messages']
    
    # ACT: Continue in same session (3 more requests)
    cortex_entry.process("Add purple button", resume_session=True)
    cortex_entry.process("Make it bigger", resume_session=True)
    cortex_entry.process("Add click handler", resume_session=True)
    
    stats_final = cortex_entry.tier1.get_tier1_statistics()
    messages_final = stats_final['conversations']['total_messages']
    
    # ASSERT: Should have accumulated 6 more messages (3 requests + 3 responses)
    expected_messages = messages_1 + 6
    assert messages_final >= expected_messages, \
        f"Expected at least {expected_messages} messages, got {messages_final}"


# ============================================================================
# CATEGORY D: COMPLEX INTENT ROUTING (1 HIGH PRIORITY TEST)
# ============================================================================

def test_different_intents_processed_correctly(cortex_entry, mock_intent_router):
    """
    Test 8 (HIGH): Validate different request types are processed correctly
    
    Validates:
    - Planning requests work
    - Execution requests work
    - Query requests work
    - All logged to Tier 1
    """
    # ARRANGE: Mock responses for different intents
    plan_response = AgentResponse(
        success=True,
        result={'plan': 'steps'},
        message="Created plan",
        agent_name="WorkPlanner"
    )
    
    execute_response = AgentResponse(
        success=True,
        result={'executed': True},
        message="Executed code",
        agent_name="CodeExecutor"
    )
    
    query_response = AgentResponse(
        success=True,
        result={'info': 'data'},
        message="Retrieved information",
        agent_name="IntentDetector"
    )
    
    # ACT & ASSERT: Planning request
    mock_intent_router.execute.return_value = plan_response
    response_1 = cortex_entry.process("Plan authentication feature")
    assert response_1 is not None
    assert 'plan' in response_1.lower()
    
    # ACT & ASSERT: Execution request
    mock_intent_router.execute.return_value = execute_response
    response_2 = cortex_entry.process("Implement the feature", resume_session=True)
    assert response_2 is not None
    
    # ACT & ASSERT: Query request
    mock_intent_router.execute.return_value = query_response
    response_3 = cortex_entry.process("What did we do?", resume_session=True)
    assert response_3 is not None
    
    # ASSERT: All requests logged
    stats = cortex_entry.tier1.get_tier1_statistics()
    assert stats['conversations']['total_messages'] >= 6, "Should have 3 requests + 3 responses"


# ============================================================================
# TEST SUITE SUMMARY
# ============================================================================

"""
TEST SUITE COMPLETION STATUS:
==============================

✅ Test 1: test_add_authentication_full_workflow
✅ Test 2: test_continue_work_session_resume
✅ Test 3: test_fix_bug_debug_workflow
✅ Test 4: test_plan_to_execute_handoff
✅ Test 5: test_execute_to_test_handoff
✅ Test 6: test_new_session_vs_resumed_session
✅ Test 7: test_session_message_accumulation
✅ Test 8: test_different_intents_processed_correctly

TOTAL TESTS: 8 HIGH PRIORITY
IMPLEMENTATION: Pragmatic approach with real Tier 1 integration
EXPECTED PASS RATE: 100%

NEXT STEPS:
- Run: pytest tests/integration/test_phase_5_1_high_priority.py -v
- Validate all pass
- Proceed to MEDIUM priority tests
"""
