"""Test ReviewOrchestrator."""
import pytest
from datetime import datetime
from cortex.orchestrators.core.review_orchestrator import ReviewOrchestrator
from cortex.models.review_models import ReviewStatus, ReviewIssue

def test_review_instantiates():
    review = ReviewOrchestrator()
    assert review is not None

def test_execute_final_review():
    review = ReviewOrchestrator()
    result = review.execute_final_review("task1", {})
    assert result.status == "PASS"

def test_execute_post_phase_review():
    review = ReviewOrchestrator()
    result = review.execute_post_phase_review("phase1")
    assert result.status == ReviewStatus.PASS

def test_gate_next_phase():
    review = ReviewOrchestrator()
    decision = review.gate_next_phase("phase1", {})
    assert decision.approved is True
