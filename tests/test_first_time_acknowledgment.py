"""
Unit Tests for First-Time Acknowledgment - Sprint 1 Day 3-4

Tests governance acknowledgment flow and user profile integration.

Test Coverage:
- Profile schema (2 tests)
- 3-step flow (3 tests)
- Returning user skip (2 tests)
- Acknowledgment persistence (2 tests)
- Backward compatibility (2 tests)
- Integration (1 test)

Target Coverage: ≥80%

SPRINT 1 DAY 3-4: First-Time Acknowledgment Unit Tests
Author: Asif Hussain (CORTEX Enhancement System)
Date: November 28, 2025
"""

import pytest
import tempfile
import os
import sqlite3
from pathlib import Path

from src.tier1.user_profile_governance import UserProfileGovernance
from src.orchestrators.onboarding_acknowledgment_orchestrator import (
    OnboardingAcknowledgmentOrchestrator,
    OnboardingStep
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    # Initialize basic user_profile table structure
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            interaction_mode TEXT NOT NULL DEFAULT 'guided',
            experience_level TEXT NOT NULL DEFAULT 'mid',
            tech_stack_preference TEXT DEFAULT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            persistent_flag BOOLEAN NOT NULL DEFAULT 1
        )
    """)
    conn.commit()
    conn.close()
    
    yield path
    
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def governance(temp_db):
    """Create UserProfileGovernance instance with temporary database."""
    return UserProfileGovernance(db_path=Path(temp_db))


@pytest.fixture
def orchestrator(temp_db):
    """Create OnboardingAcknowledgmentOrchestrator with temporary database."""
    return OnboardingAcknowledgmentOrchestrator(db_path=temp_db)


# ============================================================================
# PROFILE SCHEMA TESTS (2)
# ============================================================================

def test_governance_columns_migration(governance, temp_db):
    """Test that governance columns are added to user_profile table."""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(user_profile)")
    columns = {row[1] for row in cursor.fetchall()}
    conn.close()
    
    # Verify governance columns exist
    assert "acknowledged_rulebook" in columns
    assert "rulebook_acknowledged_at" in columns
    assert "onboarding_completed" in columns


def test_default_values_for_new_users(governance, temp_db):
    """Test that new users have correct default values."""
    # New user should not have profile yet
    status = governance.get_acknowledgment_status()
    
    assert status["acknowledged"] is False
    assert status["acknowledged_at"] is None
    assert status["onboarding_completed"] is False
    assert status["needs_onboarding"] is True


# ============================================================================
# 3-STEP FLOW TESTS (3)
# ============================================================================

def test_onboarding_step_1_welcome(orchestrator):
    """Test Step 1: Welcome & Introduction."""
    result = orchestrator.execute_step_1_welcome()
    
    assert result["step"] == 1
    assert result["title"] == "Welcome & Introduction"
    assert "CORTEX Enhancement System" in result["content"]
    assert result["next_step"] == "rulebook"
    assert result["progress"] == "1/3"
    assert orchestrator.get_current_step() == OnboardingStep.RULEBOOK


def test_onboarding_step_2_rulebook(orchestrator):
    """Test Step 2: Rulebook Display."""
    result = orchestrator.execute_step_2_rulebook()
    
    assert result["step"] == 2
    assert result["title"] == "Rulebook Overview"
    assert "7 Core Protection Layers" in result["content"]
    assert "Definition of Ready" in result["content"]
    assert "Definition of Done" in result["content"]
    assert result["next_step"] == "acknowledgment"
    assert result["progress"] == "2/3"
    assert orchestrator.get_current_step() == OnboardingStep.ACKNOWLEDGMENT


def test_onboarding_step_3_acknowledgment(orchestrator):
    """Test Step 3: Acknowledgment."""
    result = orchestrator.execute_step_3_acknowledgment()
    
    assert result["step"] == 3
    assert result["title"] == "Acknowledgment & Completion"
    assert "Confirm Your Understanding" in result["content"]
    assert result["next_step"] == "complete"
    assert result["progress"] == "3/3"
    assert orchestrator.get_current_step() == OnboardingStep.COMPLETE


# ============================================================================
# RETURNING USER SKIP TESTS (2)
# ============================================================================

def test_new_user_needs_onboarding(orchestrator):
    """Test that new users need to go through onboarding."""
    assert orchestrator.needs_onboarding() is True
    
    status = orchestrator.get_onboarding_status()
    assert status["needs_onboarding"] is True
    assert status["acknowledged"] is False


def test_returning_user_skips_onboarding(orchestrator, governance):
    """Test that users who have acknowledged skip onboarding."""
    # Mark rulebook as acknowledged
    governance.mark_rulebook_acknowledged()
    
    # User should not need onboarding
    assert orchestrator.needs_onboarding() is False
    
    status = orchestrator.get_onboarding_status()
    assert status["needs_onboarding"] is False
    assert status["acknowledged"] is True
    assert status["acknowledged_at"] is not None


# ============================================================================
# ACKNOWLEDGMENT PERSISTENCE TESTS (2)
# ============================================================================

def test_record_acknowledgment_success(orchestrator, temp_db):
    """Test that acknowledgment is recorded successfully."""
    result = orchestrator.record_acknowledgment()
    
    assert result["success"] is True
    assert "Onboarding completed successfully" in result["message"]
    assert "🎉" in result["content"]
    assert result["acknowledged_at"] is not None
    
    # Verify in database
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT acknowledged_rulebook, rulebook_acknowledged_at, onboarding_completed
        FROM user_profile WHERE id = 1
    """)
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    assert row[0] == 1  # acknowledged_rulebook
    assert row[1] is not None  # rulebook_acknowledged_at
    assert row[2] == 1  # onboarding_completed


def test_acknowledgment_persists_across_instances(governance, temp_db):
    """Test that acknowledgment persists across governance instances."""
    # First instance: mark as acknowledged
    governance1 = UserProfileGovernance(db_path=Path(temp_db))
    governance1.mark_rulebook_acknowledged()
    
    # Second instance: check acknowledgment
    governance2 = UserProfileGovernance(db_path=Path(temp_db))
    assert governance2.has_acknowledged_rulebook() is True
    
    status = governance2.get_acknowledgment_status()
    assert status["acknowledged"] is True


# ============================================================================
# BACKWARD COMPATIBILITY TESTS (2)
# ============================================================================

def test_existing_user_profile_preserved(temp_db):
    """Test that existing user profile data is preserved during migration."""
    # Create user profile with existing data
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_profile (id, interaction_mode, experience_level)
        VALUES (1, 'autonomous', 'expert')
    """)
    conn.commit()
    conn.close()
    
    # Initialize governance (runs migration)
    governance = UserProfileGovernance(db_path=Path(temp_db))
    
    # Verify existing data preserved
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT interaction_mode, experience_level
        FROM user_profile WHERE id = 1
    """)
    row = cursor.fetchone()
    conn.close()
    
    assert row[0] == "autonomous"
    assert row[1] == "expert"
    
    # Verify governance columns added
    assert governance.has_acknowledged_rulebook() is False


def test_reset_acknowledgment(governance):
    """Test that acknowledgment can be reset (for testing/re-onboarding)."""
    # Mark as acknowledged
    governance.mark_rulebook_acknowledged()
    assert governance.has_acknowledged_rulebook() is True
    
    # Reset
    success = governance.reset_acknowledgment()
    assert success is True
    
    # Verify reset
    assert governance.has_acknowledged_rulebook() is False
    status = governance.get_acknowledgment_status()
    assert status["acknowledged"] is False
    assert status["onboarding_completed"] is False


# ============================================================================
# INTEGRATION TEST
# ============================================================================

def test_full_onboarding_workflow(orchestrator, governance):
    """Test complete onboarding workflow from start to finish."""
    # Step 1: Check new user needs onboarding
    assert orchestrator.needs_onboarding() is True
    
    # Step 2: Execute Step 1 (Welcome)
    step1 = orchestrator.execute_step_1_welcome()
    assert step1["step"] == 1
    assert orchestrator.get_current_step() == OnboardingStep.RULEBOOK
    
    # Step 3: Execute Step 2 (Rulebook)
    step2 = orchestrator.execute_step_2_rulebook()
    assert step2["step"] == 2
    assert orchestrator.get_current_step() == OnboardingStep.ACKNOWLEDGMENT
    
    # Step 4: Execute Step 3 (Acknowledgment prompt)
    step3 = orchestrator.execute_step_3_acknowledgment()
    assert step3["step"] == 3
    assert orchestrator.get_current_step() == OnboardingStep.COMPLETE
    
    # Step 5: Record acknowledgment
    result = orchestrator.record_acknowledgment()
    assert result["success"] is True
    
    # Step 6: Verify user no longer needs onboarding
    assert orchestrator.needs_onboarding() is False
    assert governance.has_acknowledged_rulebook() is True
    
    # Step 7: Verify status
    status = orchestrator.get_onboarding_status()
    assert status["acknowledged"] is True
    assert status["onboarding_completed"] is True
    assert status["needs_onboarding"] is False
    assert status["acknowledged_at"] is not None


# ============================================================================
# TEMPLATE TESTS
# ============================================================================

def test_onboarding_templates_exist():
    """Test that onboarding templates exist in response-templates.yaml."""
    import yaml
    
    template_path = Path(__file__).parent.parent / "cortex-brain" / "response-templates.yaml"
    
    with open(template_path, 'r') as f:
        templates = yaml.safe_load(f)
    
    # Check for governance onboarding templates
    assert "governance_onboarding_step1" in templates.get("templates", {})
    assert "governance_onboarding_step2" in templates.get("templates", {})
    assert "governance_onboarding_step3" in templates.get("templates", {})
    assert "governance_onboarding_complete" in templates.get("templates", {})


def test_onboarding_template_content():
    """Test that onboarding templates have required content."""
    import yaml
    
    template_path = Path(__file__).parent.parent / "cortex-brain" / "response-templates.yaml"
    
    with open(template_path, 'r') as f:
        templates = yaml.safe_load(f)
    
    step1 = templates["templates"]["governance_onboarding_step1"]
    assert "Welcome to CORTEX" in step1["content"]
    assert "[1/3]" in step1["content"] or "1/3" in step1["content"]
    
    step2 = templates["templates"]["governance_onboarding_step2"]
    assert "7 Core Protection Layers" in step2["content"]
    assert "[2/3]" in step2["content"] or "2/3" in step2["content"]
    
    step3 = templates["templates"]["governance_onboarding_step3"]
    assert "Acknowledgment" in step3["content"]
    assert "[3/3]" in step3["content"] or "3/3" in step3["content"]
