"""
Feature 8: Code Review Auto-Suggestion Tests (RED Phase)
CORTEX Orchestrator Enhancement Plan v1.0

Tests for automatic code review suggestions after phase completion.
All tests should FAIL initially (RED phase of TDD).

Author: Asif Hussain
Created: December 13, 2025
"""

import pytest
from pathlib import Path
from typing import Dict, Any, Optional
import json
from datetime import datetime


# ============================================================================
# PHASE 8.1: Suggestion Rules Engine Tests
# ============================================================================

class TestSuggestionTriggers:
    """Test suggestion trigger detection for different phases"""
    
    def test_suggest_after_phase4_controllers(self):
        """Test code review suggestion after Phase 4 (Controllers Implementation)"""
        # Arrange
        from src.operations.utilities.code_review_suggester import CodeReviewSuggester
        
        suggester = CodeReviewSuggester()
        phase_info = {
            'phase': 'phase-4',
            'name': 'Controllers Implementation',
            'status': 'complete',
            'dod_percentage': 100
        }
        
        # Act
        should_suggest = suggester.check_should_suggest(phase_info)
        message = suggester.format_suggestion_message(phase_info)
        
        # Assert
        assert should_suggest is True, "Should suggest review after Phase 4"
        assert "Phase 4 Complete" in message, "Message should mention Phase 4"
        assert "Controllers implemented" in message, "Message should mention controllers"
        assert "🔍 Recommended" in message, "Message should be non-intrusive (recommended)"
        assert "review code" in message.lower(), "Message should mention 'review code' action"
    
    def test_suggest_after_phase5_migration(self):
        """Test code review suggestion after Phase 5 (Legacy Migration)"""
        # Arrange
        from src.operations.utilities.code_review_suggester import CodeReviewSuggester
        
        suggester = CodeReviewSuggester()
        phase_info = {
            'phase': 'phase-5',
            'name': 'Legacy Migration',
            'status': 'complete',
            'dod_percentage': 100
        }
        
        # Act
        should_suggest = suggester.check_should_suggest(phase_info)
        message = suggester.format_suggestion_message(phase_info)
        
        # Assert
        assert should_suggest is True, "Should suggest review after Phase 5"
        assert "Phase 5 Complete" in message, "Message should mention Phase 5"
        assert "Legacy code migrated" in message, "Message should mention migration"
        assert "🔍 Recommended" in message, "Message should be non-intrusive"
        assert "comprehensive review" in message.lower(), "Message should suggest comprehensive review"
    
    def test_require_before_deployment(self):
        """Test code review requirement before deployment"""
        # Arrange
        from src.operations.utilities.code_review_suggester import CodeReviewSuggester
        
        suggester = CodeReviewSuggester()
        event_info = {
            'event': 'before-deployment',
            'name': 'Deployment Preparation',
            'status': 'pending'
        }
        
        # Act
        should_suggest = suggester.check_should_suggest(event_info)
        message = suggester.format_suggestion_message(event_info)
        
        # Assert
        assert should_suggest is True, "Should require review before deployment"
        assert "⚠️" in message, "Deployment message should be more urgent (warning emoji)"
        assert "Required" in message or "required" in message, "Should indicate requirement"
        assert "deployment" in message.lower(), "Message should mention deployment"
        assert "Security audit" in message, "Should mention security audit"
    
    def test_no_suggestion_for_other_phases(self):
        """Test no suggestion for phases without trigger rules"""
        # Arrange
        from src.operations.utilities.code_review_suggester import CodeReviewSuggester
        
        suggester = CodeReviewSuggester()
        phase_info = {
            'phase': 'phase-2',
            'name': 'Domain Layer',
            'status': 'complete',
            'dod_percentage': 100
        }
        
        # Act
        should_suggest = suggester.check_should_suggest(phase_info)
        
        # Assert
        assert should_suggest is False, "Should not suggest for phases without rules"


# ============================================================================
# PHASE 8.2: User Interaction Tests
# ============================================================================

class TestUserInteraction:
    """Test user accept/decline workflow"""
    
    def test_user_accepts_suggestion(self):
        """Test workflow when user accepts code review suggestion"""
        # Arrange
        from src.operations.utilities.code_review_suggester import CodeReviewSuggester
        
        suggester = CodeReviewSuggester()
        phase_info = {'phase': 'phase-4', 'status': 'complete'}
        user_response = "review code"
        
        # Act
        action = suggester.parse_user_response(user_response)
        
        # Assert
        assert action == 'accept', "Should recognize 'review code' as acceptance"
    
    def test_user_declines_suggestion(self):
        """Test workflow when user declines code review suggestion"""
        # Arrange
        from src.operations.utilities.code_review_suggester import CodeReviewSuggester
        
        suggester = CodeReviewSuggester()
        phase_info = {'phase': 'phase-4', 'status': 'complete'}
        user_response = "skip review"
        
        # Act
        action = suggester.parse_user_response(user_response)
        skip_recorded = suggester.track_skip_decision(phase_info, user_response)
        
        # Assert
        assert action == 'decline', "Should recognize 'skip review' as decline"
        assert skip_recorded is True, "Should record skip decision"


# ============================================================================
# PHASE 8.3: Brain Tier 1 Integration Tests
# ============================================================================

class TestSkipTracking:
    """Test skip decision tracking in Brain Tier 1"""
    
    def test_skip_tracking_in_brain(self, tmp_path):
        """Test skip decisions are stored in cortex-brain/tier1/code-review-skip-history.json"""
        # Arrange
        from src.operations.utilities.code_review_suggester import CodeReviewSuggester
        
        brain_path = tmp_path / "cortex-brain" / "tier1"
        brain_path.mkdir(parents=True)
        
        suggester = CodeReviewSuggester(brain_path=brain_path)
        phase_info = {
            'phase': 'phase-4',
            'name': 'Controllers Implementation',
            'status': 'complete',
            'timestamp': datetime.now().isoformat()
        }
        
        # Act
        suggester.track_skip_decision(phase_info, reason="User declined")
        
        # Assert
        skip_file = brain_path / "code-review-skip-history.json"
        assert skip_file.exists(), "Skip history file should be created"
        
        with open(skip_file, 'r') as f:
            skip_data = json.load(f)
        
        assert 'skipped_reviews' in skip_data, "Should have skipped_reviews list"
        assert len(skip_data['skipped_reviews']) == 1, "Should record 1 skip"
        assert skip_data['skipped_reviews'][0]['phase'] == 'phase-4'
        assert skip_data['skipped_reviews'][0]['reason'] == "User declined"
    
    def test_deployment_reminder_if_skipped(self, tmp_path):
        """Test reminder shown before deployment if reviews were skipped"""
        # Arrange
        from src.operations.utilities.code_review_suggester import CodeReviewSuggester
        
        brain_path = tmp_path / "cortex-brain" / "tier1"
        brain_path.mkdir(parents=True)
        
        suggester = CodeReviewSuggester(brain_path=brain_path)
        
        # Record skip
        phase_info = {'phase': 'phase-4', 'status': 'complete'}
        suggester.track_skip_decision(phase_info, reason="User declined")
        
        # Act
        event_info = {'event': 'before-deployment'}
        reminder = suggester.get_deployment_reminder(event_info)
        
        # Assert
        assert reminder is not None, "Should show reminder if reviews skipped"
        assert "skipped" in reminder.lower(), "Reminder should mention skipped reviews"
        assert "phase-4" in reminder.lower(), "Should mention which phases were skipped"


# ============================================================================
# Test Execution Summary
# ============================================================================

def test_suite_summary():
    """Summary of test suite for Feature 8"""
    print("\n" + "="*80)
    print("Feature 8: Code Review Auto-Suggestion - Test Suite")
    print("="*80)
    print("\nTest Coverage:")
    print("  • TestSuggestionTriggers: 4 tests (phase-4, phase-5, deployment, no-trigger)")
    print("  • TestUserInteraction: 2 tests (accept, decline)")
    print("  • TestSkipTracking: 2 tests (brain storage, deployment reminder)")
    print("\nTotal: 8 tests (2 more than planned 6 tests)")
    print("\nExpected Result: ALL TESTS SHOULD FAIL (RED phase)")
    print("="*80)
