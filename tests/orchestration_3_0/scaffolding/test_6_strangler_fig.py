"""
Test 6: Strangler Fig Pattern Generation
Verifies incremental migration plan generated.
"""

import pytest

from src.orchestration_3_0.orchestrators.scaffolding.migration_strategist import (
    MigrationStrategist,
    RiskLevel
)


def test_strangler_fig_phased_migration():
    """Verify incremental migration plan generated."""
    assessment = {
        "current_pattern": "mvc_monolith",
        "recommended_pattern": "clean_architecture",
        "service_candidates": [
            {"name": "PaymentService", "files": ["payment.py"], "confidence": 0.85},
            {"name": "UserService", "files": ["user.py"], "confidence": 0.80}
        ],
        "tech_stack": {"framework": "FastAPI", "orm": "SQLAlchemy"}
    }
    
    constraints = {
        "timeline": 6,
        "team_size": 3
    }
    
    strategist = MigrationStrategist()
    strategy = strategist.plan(assessment, constraints)
    
    # Assertions
    assert len(strategy.phases) >= 3  # Infrastructure + Services + Cutover
    
    # First phase should be infrastructure (low risk)
    assert strategy.phases[0].risk == RiskLevel.LOW.value
    assert "infrastructure" in strategy.phases[0].name.lower()
    
    # Last phase should be cutover (high risk)
    assert strategy.phases[-1].risk == RiskLevel.HIGH.value
    assert "cutover" in strategy.phases[-1].name.lower()
    
    # Check deliverables exist
    for phase in strategy.phases:
        assert len(phase.deliverables) > 0
        assert phase.rollback_strategy is not None


def test_strangler_fig_timeline_compression():
    """Verify timeline compression when constrained."""
    assessment = {
        "current_pattern": "mvc_monolith",
        "recommended_pattern": "clean_architecture",
        "service_candidates": [],
        "tech_stack": {"framework": "FastAPI"}
    }
    
    # Very tight timeline
    constraints = {
        "timeline": 4,  # 4 weeks (aggressive)
        "team_size": 2
    }
    
    strategist = MigrationStrategist()
    strategy = strategist.plan(assessment, constraints)
    
    # Should compress to fit timeline
    assert strategy.total_duration_weeks <= constraints["timeline"]


def test_strangler_fig_risk_summary():
    """Verify risk summary calculated correctly."""
    assessment = {
        "current_pattern": "mvc_monolith",
        "recommended_pattern": "clean_architecture",
        "service_candidates": [
            {"name": "Service1", "files": ["s1.py"], "confidence": 0.9},
            {"name": "Service2", "files": ["s2.py"], "confidence": 0.7}
        ],
        "tech_stack": {"framework": "FastAPI"}
    }
    
    strategist = MigrationStrategist()
    strategy = strategist.plan(assessment)
    
    # Check risk summary
    assert "LOW" in strategy.risk_summary
    assert "MEDIUM" in strategy.risk_summary
    assert "HIGH" in strategy.risk_summary
    
    total_phases = sum(strategy.risk_summary.values())
    assert total_phases == len(strategy.phases)
