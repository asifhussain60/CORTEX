"""
Phase 24.4 - Layer 4: Architecture Evolution Tracking (DecisionJournal)
TDD RED Phase - Test suite for DecisionJournal

Tests cover:
- Record architecture decision with rationale
- Load decision history from journal
- Challenge verdict capture (PROCEED/PIVOT/BLOCK)
- DoR approval tracking
- Execution outcome recording
- Decision search by criteria
- Edge cases (missing fields, duplicate decisions)
"""

import pytest
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import yaml


@pytest.fixture
def journal_dir(tmp_path):
    """Create temporary journal directory"""
    journal = tmp_path / "decisions"
    journal.mkdir()
    return journal


@pytest.fixture
def sample_decision():
    """Create sample architecture decision"""
    return {
        "decision": "Use PhaseCompletionOrchestrator for auto-sync",
        "rationale": "Eliminate manual phase YAML updates, reduce human error",
        "alternatives": [
            "Manual updates (current state)",
            "Git hooks for auto-detection"
        ],
        "impact": "60 second dashboard sync latency, 100% automation",
        "challenge_verdict": "PROCEED",
        "dor_approved": True,
        "execution_outcome": "SUCCESS"
    }


class TestRecordDecision:
    """Test recording architecture decisions"""
    
    def test_record_decision_creates_file(self, journal_dir, sample_decision):
        """Test that recording a decision creates a journal entry"""
        from cortex.orchestrators.support.decision_journal import DecisionJournal
        
        journal = DecisionJournal(journal_dir)
        decision_id = journal.record_decision(**sample_decision)
        
        assert decision_id is not None
        decision_file = journal_dir / f"{decision_id}.yaml"
        assert decision_file.exists()
    
    def test_record_decision_includes_metadata(self, journal_dir, sample_decision):
        """Test that recorded decision includes timestamp and ID"""
        from cortex.orchestrators.support.decision_journal import DecisionJournal
        
        journal = DecisionJournal(journal_dir)
        decision_id = journal.record_decision(**sample_decision)
        
        decision_file = journal_dir / f"{decision_id}.yaml"
        data = yaml.safe_load(decision_file.read_text())
        
        assert "id" in data
        assert "timestamp" in data
        assert data["id"] == decision_id


class TestLoadDecisionHistory:
    """Test loading decision history"""
    
    def test_load_all_decisions(self, journal_dir, sample_decision):
        """Test loading all decisions from journal"""
        from cortex.orchestrators.support.decision_journal import DecisionJournal
        import time
        
        journal = DecisionJournal(journal_dir)
        # Record multiple decisions with time gap to ensure unique IDs
        journal.record_decision(**sample_decision)
        time.sleep(1.1)  # Ensure timestamp differs (decision-YYYYMMDD-HHMMSS format)
        journal.record_decision(**sample_decision)
        
        decisions = journal.load_all_decisions()
        assert len(decisions) == 2
    
    def test_load_decision_by_id(self, journal_dir, sample_decision):
        """Test loading specific decision by ID"""
        from cortex.orchestrators.support.decision_journal import DecisionJournal
        
        journal = DecisionJournal(journal_dir)
        decision_id = journal.record_decision(**sample_decision)
        
        loaded = journal.load_decision(decision_id)
        assert loaded is not None
        assert loaded["decision"] == sample_decision["decision"]


class TestChallengeVerdictCapture:
    """Test challenge verdict recording"""
    
    def test_record_challenge_verdict(self, journal_dir):
        """Test recording Challenge verdict (PROCEED/PIVOT/BLOCK)"""
        from cortex.orchestrators.support.decision_journal import DecisionJournal
        
        journal = DecisionJournal(journal_dir)
        decision_id = journal.record_decision(
            decision="Implement BrittlenessScanner",
            rationale="Detect circular dependencies early",
            alternatives=["Manual code review"],
            impact="Automated brittleness detection",
            challenge_verdict="PROCEED"
        )
        
        loaded = journal.load_decision(decision_id)
        assert loaded["challenge_verdict"] == "PROCEED"


class TestDoRApprovalTracking:
    """Test DoR approval tracking"""
    
    def test_record_dor_approval(self, journal_dir):
        """Test recording DoR approval status"""
        from cortex.orchestrators.support.decision_journal import DecisionJournal
        
        journal = DecisionJournal(journal_dir)
        decision_id = journal.record_decision(
            decision="Implement PhaseCompletionOrchestrator",
            rationale="Automate sync workflow",
            alternatives=[],
            impact="60s sync latency",
            dor_approved=True
        )
        
        loaded = journal.load_decision(decision_id)
        assert loaded["dor_approved"] is True


class TestExecutionOutcome:
    """Test execution outcome recording"""
    
    def test_record_execution_outcome(self, journal_dir):
        """Test recording execution outcome (SUCCESS/FAILURE)"""
        from cortex.orchestrators.support.decision_journal import DecisionJournal
        
        journal = DecisionJournal(journal_dir)
        decision_id = journal.record_decision(
            decision="Test implementation",
            rationale="Validate approach",
            alternatives=[],
            impact="Learning outcome",
            execution_outcome="SUCCESS"
        )
        
        loaded = journal.load_decision(decision_id)
        assert loaded["execution_outcome"] == "SUCCESS"
    
    def test_update_execution_outcome(self, journal_dir):
        """Test updating execution outcome after implementation"""
        from cortex.orchestrators.support.decision_journal import DecisionJournal
        
        journal = DecisionJournal(journal_dir)
        decision_id = journal.record_decision(
            decision="Pending implementation",
            rationale="Test update",
            alternatives=[],
            impact="Test",
            execution_outcome="PENDING"
        )
        
        # Update outcome
        journal.update_decision(decision_id, execution_outcome="SUCCESS")
        
        loaded = journal.load_decision(decision_id)
        assert loaded["execution_outcome"] == "SUCCESS"


class TestDecisionSearch:
    """Test decision search by criteria"""
    
    def test_search_by_challenge_verdict(self, journal_dir, sample_decision):
        """Test searching decisions by challenge verdict"""
        from cortex.orchestrators.support.decision_journal import DecisionJournal
        import time
        
        journal = DecisionJournal(journal_dir)
        journal.record_decision(**sample_decision)
        time.sleep(1.1)  # Ensure unique timestamp
        sample_decision_copy = sample_decision.copy()
        sample_decision_copy["challenge_verdict"] = "BLOCK"
        journal.record_decision(**sample_decision_copy)
        
        proceed_decisions = journal.search_decisions(challenge_verdict="PROCEED")
        assert len(proceed_decisions) == 1
    
    def test_search_by_outcome(self, journal_dir, sample_decision):
        """Test searching decisions by execution outcome"""
        from cortex.orchestrators.support.decision_journal import DecisionJournal
        import time
        
        journal = DecisionJournal(journal_dir)
        sample_decision_copy1 = sample_decision.copy()
        sample_decision_copy1["execution_outcome"] = "SUCCESS"
        journal.record_decision(**sample_decision_copy1)
        time.sleep(1.1)
        sample_decision_copy2 = sample_decision.copy()
        sample_decision_copy2["execution_outcome"] = "FAILURE"
        journal.record_decision(**sample_decision_copy2)
        
        success_decisions = journal.search_decisions(execution_outcome="SUCCESS")
        assert len(success_decisions) == 1


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_missing_required_fields(self, journal_dir):
        """Test handling of missing required fields"""
        from cortex.orchestrators.support.decision_journal import DecisionJournal
        
        journal = DecisionJournal(journal_dir)
        
        # Missing 'decision' field should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            journal.record_decision(
                decision="",  # Empty string should trigger ValueError
                rationale="Test",
                alternatives=[],
                impact="None"
            )
        assert "decision" in str(exc_info.value).lower()
    
    def test_load_nonexistent_decision(self, journal_dir):
        """Test loading non-existent decision"""
        from cortex.orchestrators.support.decision_journal import DecisionJournal
        
        journal = DecisionJournal(journal_dir)
        loaded = journal.load_decision("nonexistent-id")
        
        assert loaded is None
    
    def test_empty_journal_directory(self, journal_dir):
        """Test loading from empty journal directory"""
        from cortex.orchestrators.support.decision_journal import DecisionJournal
        
        journal = DecisionJournal(journal_dir)
        decisions = journal.load_all_decisions()
        
        assert len(decisions) == 0
