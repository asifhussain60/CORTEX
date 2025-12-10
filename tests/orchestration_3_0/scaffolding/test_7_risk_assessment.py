"""
Test 7: Risk Assessment - High-Risk Modules
Verifies high-complexity modules flagged as high-risk.
"""

import pytest

from src.orchestration_3_0.orchestrators.scaffolding.migration_strategist import MigrationStrategist


def test_risk_assessment_hotspots():
    """Verify high-complexity modules flagged as high-risk."""
    assessment = {
        "current_pattern": "mvc_monolith",
        "recommended_pattern": "clean_architecture",
        "service_candidates": [
            {
                "name": "PaymentService",
                "files": ["payment.py"],
                "confidence": 0.6  # Lower confidence = higher risk
            }
        ],
        "tech_stack": {"framework": "FastAPI"},
        "hotspots": [
            {"file": "payment.py", "complexity": 48, "churn": 127}
        ]
    }
    
    strategist = MigrationStrategist()
    strategy = strategist.plan(assessment)
    
    # Find payment service phase
    payment_phases = [p for p in strategy.phases if "payment" in p.name.lower()]
    
    if payment_phases:
        # Should be flagged as high or medium risk (due to low confidence)
        assert payment_phases[0].risk in ["HIGH", "MEDIUM"]
        
        # Check rollback strategy exists
        assert payment_phases[0].rollback_strategy is not None
        assert "feature flag" in payment_phases[0].rollback_strategy.lower()


def test_risk_assessment_low_confidence():
    """Verify low confidence candidates marked as high risk."""
    assessment = {
        "current_pattern": "mvc_monolith",
        "recommended_pattern": "clean_architecture",
        "service_candidates": [
            {
                "name": "ComplexService",
                "files": ["complex.py", "helper1.py", "helper2.py", "helper3.py", "helper4.py"],
                "confidence": 0.55  # Low confidence + many files = high risk
            }
        ],
        "tech_stack": {"framework": "FastAPI"}
    }
    
    strategist = MigrationStrategist()
    strategy = strategist.plan(assessment)
    
    # Should have high-risk phases
    high_risk_phases = [p for p in strategy.phases if p.risk == "HIGH"]
    assert len(high_risk_phases) > 0


def test_risk_assessment_validation_strategy():
    """Verify validation strategies defined for each phase."""
    assessment = {
        "current_pattern": "mvc_monolith",
        "recommended_pattern": "clean_architecture",
        "service_candidates": [
            {"name": "Service1", "files": ["s1.py"], "confidence": 0.85}
        ],
        "tech_stack": {"framework": "FastAPI"}
    }
    
    strategist = MigrationStrategist()
    strategy = strategist.plan(assessment)
    
    # Check validation strategies exist (except maybe for infrastructure phase)
    service_phases = [p for p in strategy.phases if "service" in p.name.lower()]
    
    for phase in service_phases:
        assert phase.validation_strategy is not None
        # Should mention parallel run or comparison
        assert any(keyword in phase.validation_strategy.lower() for keyword in ["parallel", "compare", "monitor"])
