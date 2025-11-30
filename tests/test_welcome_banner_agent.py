"""
Unit Tests for WelcomeBannerAgent - Sprint 1 Day 1

Tests session-based governance banner display functionality.

Test Coverage:
- Session state tracking (3 tests)
- Banner display logic (3 tests)
- Dismissal handling (3 tests)
- Database operations (3 tests)
- Edge cases (3 tests)

Target Coverage: ΓëÑ80%

SPRINT 1 DAY 1: WelcomeBannerAgent Unit Tests
Author: Asif Hussain (CORTEX Enhancement System)
Date: November 28, 2025
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import datetime

from src.cortex_agents.welcome_banner_agent import WelcomeBannerAgent
from src.cortex_agents.base_agent import AgentRequest, AgentResponse


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def banner_agent(temp_db):
    """Create WelcomeBannerAgent instance with temporary database."""
    return WelcomeBannerAgent(db_path=temp_db)


# ============================================================================
# SESSION STATE TRACKING TESTS (3)
# ============================================================================

def test_create_new_session(banner_agent, temp_db):
    """Test that new session is created when no session_id provided."""
    request = AgentRequest(
        intent="check_session",
        context={"session_id": None},
        user_message=""
    )
    
    response = banner_agent.execute(request)
    
    assert response.success is True
    assert response.result["show_banner"] is True
    assert response.result["is_new_session"] is True
    assert response.result["session_id"] is not None
    
    # Verify session exists in database
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT rulebook_banner_shown FROM session_state WHERE session_id = ?",
                   (response.result["session_id"],))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    assert row[0] == 0  # Banner not yet shown


def test_check_existing_session_banner_not_shown(banner_agent):
    """Test checking session where banner hasn't been shown yet."""
    # Create session
    session_id = "test-session-123"
    banner_agent._create_session(session_id)
    
    # Check session
    request = AgentRequest(
        intent="check_session",
        context={"session_id": session_id},
        user_message=""
    )
    
    response = banner_agent.execute(request)
    
    assert response.success is True
    assert response.result["show_banner"] is True
    assert response.result["is_new_session"] is False
    assert response.result["session_id"] == session_id


def test_check_existing_session_banner_already_shown(banner_agent):
    """Test checking session where banner was already shown."""
    # Create session and mark banner as shown
    session_id = "test-session-456"
    banner_agent._create_session(session_id)
    banner_agent._mark_banner_shown(session_id)
    
    # Check session
    request = AgentRequest(
        intent="check_session",
        context={"session_id": session_id},
        user_message=""
    )
    
    response = banner_agent.execute(request)
    
    assert response.success is True
    assert response.result["show_banner"] is False
    assert response.result["is_new_session"] is False
    assert response.result["session_id"] == session_id


# ============================================================================
# BANNER DISPLAY LOGIC TESTS (3)
# ============================================================================

def test_get_banner_content(banner_agent):
    """Test retrieving banner content."""
    request = AgentRequest(
        intent="get_banner_content",
        context={},
        user_message=""
    )
    
    response = banner_agent.execute(request)
    
    assert response.success is True
    assert "banner_text" in response.result
    assert "CORTEX GOVERNANCE RULES" in response.result["banner_text"]
    assert "dismissal_phrases" in response.result
    assert "rulebook_path" in response.result
    assert len(response.result["dismissal_phrases"]) > 0


def test_banner_content_has_required_sections(banner_agent):
    """Test that banner content includes all required sections."""
    request = AgentRequest(
        intent="get_banner_content",
        context={},
        user_message=""
    )
    
    response = banner_agent.execute(request)
    banner_text = response.result["banner_text"]
    
    # Verify key sections
    assert "KEY RULES" in banner_text
    assert "QUICK ACCESS" in banner_text
    assert "DISMISSAL" in banner_text
    assert "Definition of Ready" in banner_text
    assert "Definition of Done" in banner_text
    assert "Git checkpoint" in banner_text


def test_banner_shows_on_first_interaction(banner_agent):
    """Test that banner is displayed on first interaction with new session."""
    # Check new session
    check_request = AgentRequest(
        intent="check_session",
        context={"session_id": None},
        user_message=""
    )
    
    check_response = banner_agent.execute(check_request)
    session_id = check_response.result["session_id"]
    
    assert check_response.result["show_banner"] is True
    
    # Get banner content
    content_request = AgentRequest(
        intent="get_banner_content",
        context={},
        user_message=""
    )
    
    content_response = banner_agent.execute(content_request)
    
    assert content_response.success is True
    assert len(content_response.result["banner_text"]) > 100


# ============================================================================
# DISMISSAL HANDLING TESTS (3)
# ============================================================================

def test_mark_banner_shown(banner_agent, temp_db):
    """Test marking banner as shown for a session."""
    # Create session
    session_id = "test-session-789"
    banner_agent._create_session(session_id)
    
    # Mark banner as shown
    mark_request = AgentRequest(
        intent="mark_shown",
        context={"session_id": session_id},
        user_message=""
    )
    
    mark_response = banner_agent.execute(mark_request)
    
    assert mark_response.success is True
    assert mark_response.result["banner_shown"] is True
    
    # Verify in database
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT rulebook_banner_shown FROM session_state WHERE session_id = ?",
                   (session_id,))
    row = cursor.fetchone()
    conn.close()
    
    assert row[0] == 1  # Banner marked as shown


def test_banner_not_shown_again_in_same_session(banner_agent):
    """Test that banner doesn't appear again after being marked as shown."""
    # Create session
    session_id = "test-session-repeat"
    banner_agent._create_session(session_id)
    
    # First check - should show
    check1 = AgentRequest(
        intent="check_session",
        context={"session_id": session_id},
        user_message=""
    )
    response1 = banner_agent.execute(check1)
    assert response1.result["show_banner"] is True
    
    # Mark as shown
    banner_agent._mark_banner_shown(session_id)
    
    # Second check - should NOT show
    check2 = AgentRequest(
        intent="check_session",
        context={"session_id": session_id},
        user_message=""
    )
    response2 = banner_agent.execute(check2)
    assert response2.result["show_banner"] is False


def test_dismissal_phrases_included(banner_agent):
    """Test that dismissal phrases are provided in banner content."""
    request = AgentRequest(
        intent="get_banner_content",
        context={},
        user_message=""
    )
    
    response = banner_agent.execute(request)
    dismissal_phrases = response.result["dismissal_phrases"]
    
    # Verify common dismissal phrases
    assert "got it" in dismissal_phrases
    assert "show rules" in dismissal_phrases or "rulebook" in dismissal_phrases


# ============================================================================
# DATABASE OPERATIONS TESTS (3)
# ============================================================================

def test_database_initialization(temp_db):
    """Test that session_state table is created on initialization."""
    agent = WelcomeBannerAgent(db_path=temp_db)
    
    # Check table exists
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='session_state'
    """)
    result = cursor.fetchone()
    conn.close()
    
    assert result is not None
    assert result[0] == "session_state"


def test_session_timestamps(banner_agent, temp_db):
    """Test that session timestamps are recorded correctly."""
    session_id = "test-timestamp-session"
    banner_agent._create_session(session_id)
    
    # Verify timestamps in database
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT first_interaction_time, last_updated 
        FROM session_state 
        WHERE session_id = ?
    """, (session_id,))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    assert row[0] is not None  # first_interaction_time
    assert row[1] is not None  # last_updated
    
    # Verify timestamps are valid ISO format
    datetime.fromisoformat(row[0])
    datetime.fromisoformat(row[1])


def test_get_session_stats(banner_agent, temp_db):
    """Test retrieving session statistics."""
    # Create multiple sessions with different states
    banner_agent._create_session("session1")
    banner_agent._create_session("session2")
    banner_agent._mark_banner_shown("session2")
    banner_agent._create_session("session3")
    
    # Get stats
    stats = banner_agent.get_session_stats()
    
    assert stats["total_sessions"] == 3
    assert stats["banners_shown"] == 1  # Only session2 marked
    assert stats["sessions_active"] == 2  # session1 and session3


# ============================================================================
# EDGE CASES TESTS (3)
# ============================================================================

def test_mark_banner_shown_nonexistent_session(banner_agent):
    """Test marking banner as shown for non-existent session raises error."""
    with pytest.raises(ValueError, match="Session .* not found"):
        banner_agent._mark_banner_shown("nonexistent-session")


def test_mark_banner_shown_without_session_id(banner_agent):
    """Test that marking banner without session_id raises error."""
    request = AgentRequest(
        intent="mark_shown",
        context={"session_id": None},
        user_message=""
    )
    
    response = banner_agent.execute(request)
    
    assert response.success is False
    assert "session_id is required" in response.error.lower()


def test_unsupported_intent(banner_agent):
    """Test handling of unsupported intent."""
    request = AgentRequest(
        intent="unsupported_operation",
        context={},
        user_message=""
    )
    
    response = banner_agent.execute(request)
    
    assert response.success is False
    assert "not recognized" in response.message.lower() or "unsupported" in response.message.lower()


# ============================================================================
# INTEGRATION TEST
# ============================================================================

def test_full_workflow(banner_agent):
    """Test complete workflow: create session, show banner, mark shown, verify hidden."""
    # Step 1: Check new session (should show banner)
    check1 = AgentRequest(
        intent="check_session",
        context={"session_id": None},
        user_message=""
    )
    response1 = banner_agent.execute(check1)
    session_id = response1.result["session_id"]
    
    assert response1.result["show_banner"] is True
    assert response1.result["is_new_session"] is True
    
    # Step 2: Get banner content
    content_req = AgentRequest(
        intent="get_banner_content",
        context={},
        user_message=""
    )
    content_resp = banner_agent.execute(content_req)
    
    assert content_resp.success is True
    assert "CORTEX GOVERNANCE" in content_resp.result["banner_text"]
    
    # Step 3: Mark banner as shown
    mark_req = AgentRequest(
        intent="mark_shown",
        context={"session_id": session_id},
        user_message=""
    )
    mark_resp = banner_agent.execute(mark_req)
    
    assert mark_resp.success is True
    
    # Step 4: Check again (should NOT show banner)
    check2 = AgentRequest(
        intent="check_session",
        context={"session_id": session_id},
        user_message=""
    )
    response2 = banner_agent.execute(check2)
    
    assert response2.result["show_banner"] is False
    assert response2.result["is_new_session"] is False
