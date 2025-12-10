"""
Test 5: Service Decomposition - Bounded Contexts
Verifies service candidates identified from AST analysis.
"""

import pytest

from src.orchestration_3_0.orchestrators.scaffolding.architecture_intelligence import ArchitectureIntelligence


def test_service_decomposition_bounded_contexts():
    """Verify service candidates identified from AST analysis."""
    analyzer_report = {
        "language": "python",
        "framework": "Flask",
        "modules": 25,
        "classes": 30,
        "functions": 100,
        "dependencies": {"internal": 15, "external": 8},
        "anti_patterns": [],
        "hotspots": []
    }
    
    intelligence = ArchitectureIntelligence()
    assessment = intelligence.assess(analyzer_report)
    
    # Should identify service candidates
    assert len(assessment.service_candidates) >= 2
    
    # Check service candidate structure
    for candidate in assessment.service_candidates:
        assert hasattr(candidate, 'name')
        assert hasattr(candidate, 'files')
        assert hasattr(candidate, 'confidence')
        assert hasattr(candidate, 'rationale')
        assert candidate.confidence > 0.5
        assert len(candidate.files) > 0


def test_service_decomposition_no_candidates_small_codebase():
    """Verify small codebases don't suggest microservices."""
    analyzer_report = {
        "language": "python",
        "framework": "Flask",
        "modules": 8,  # Too small for microservices
        "classes": 10,
        "functions": 30,
        "dependencies": {"internal": 5, "external": 3},
        "anti_patterns": [],
        "hotspots": []
    }
    
    intelligence = ArchitectureIntelligence()
    assessment = intelligence.assess(analyzer_report)
    
    # Should recommend Clean Architecture (not microservices)
    assert assessment.recommended_pattern != "microservices"


def test_service_decomposition_tech_stack_recommendations():
    """Verify technology stack recommendations align with target pattern."""
    analyzer_report = {
        "language": "python",
        "framework": "Flask",
        "modules": 20,
        "classes": 25,
        "functions": 80,
        "dependencies": {"internal": 12, "external": 6},
        "anti_patterns": [],
        "hotspots": []
    }
    
    constraints = {
        "target_framework": "FastAPI"
    }
    
    intelligence = ArchitectureIntelligence()
    assessment = intelligence.assess(analyzer_report, constraints)
    
    # Check tech stack recommendations
    assert assessment.tech_stack['framework'] == 'FastAPI'
    assert 'orm' in assessment.tech_stack
    assert 'testing' in assessment.tech_stack
