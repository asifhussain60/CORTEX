"""
Test 4: Pattern Recognition - MVC to Clean Architecture
Verifies MVC pattern recognized and Clean Architecture recommended.
"""

import pytest

from src.orchestration_3_0.orchestrators.scaffolding.architecture_intelligence import (
    ArchitectureIntelligence,
    ArchitecturalPattern
)


def test_architecture_pattern_mvc_to_clean():
    """Verify MVC pattern recognized and Clean Architecture recommended."""
    # Mock code report (from CodeAnalyzer)
    analyzer_report = {
        "language": "python",
        "framework": "Flask",
        "modules": 15,
        "classes": 20,
        "functions": 50,
        "dependencies": {"internal": 10, "external": 5},
        "anti_patterns": [],
        "hotspots": []
    }
    
    intelligence = ArchitectureIntelligence()
    assessment = intelligence.assess(analyzer_report)
    
    # Assertions
    assert assessment.current_pattern == ArchitecturalPattern.MVC_MONOLITH.value
    assert assessment.recommended_pattern == ArchitecturalPattern.CLEAN_ARCHITECTURE.value
    assert assessment.current_confidence >= 0.6
    
    # Check layers are identified
    assert "layers" in intelligence.to_dict(assessment)
    layers = assessment.layers
    assert len(layers) == 4  # Presentation, Business Logic, Data Access, Infrastructure
    assert "presentation" in layers
    assert "business_logic" in layers
    assert "data_access" in layers
    assert "infrastructure" in layers


def test_architecture_pattern_spaghetti_to_layered():
    """Verify spaghetti code detected and layered architecture recommended."""
    analyzer_report = {
        "language": "python",
        "framework": None,
        "modules": 8,
        "classes": 5,
        "functions": 30,
        "dependencies": {"internal": 3, "external": 2},
        "anti_patterns": [
            {"type": "god_object", "confidence": 0.9},
            {"type": "god_object", "confidence": 0.85},
            {"type": "god_object", "confidence": 0.8},
            {"type": "tight_coupling", "confidence": 0.75},
            {"type": "hardcoded_value", "confidence": 0.7}
        ],
        "hotspots": [
            {"complexity": 50, "confidence": 0.9},
            {"complexity": 45, "confidence": 0.85},
            {"complexity": 42, "confidence": 0.8}
        ]
    }
    
    intelligence = ArchitectureIntelligence()
    assessment = intelligence.assess(analyzer_report)
    
    # Should detect spaghetti code (high anti-patterns + hotspots)
    assert assessment.current_pattern == ArchitecturalPattern.SPAGHETTI_CODE.value
    assert assessment.recommended_pattern == ArchitecturalPattern.LAYERED_MONOLITH.value


def test_architecture_pattern_unknown_small_codebase():
    """Verify small codebases classified as procedural."""
    analyzer_report = {
        "language": "python",
        "framework": None,
        "modules": 3,
        "classes": 1,
        "functions": 10,
        "dependencies": {"internal": 1, "external": 1},
        "anti_patterns": [],
        "hotspots": []
    }
    
    intelligence = ArchitectureIntelligence()
    assessment = intelligence.assess(analyzer_report)
    
    # Small codebase should be classified as procedural
    assert assessment.current_pattern == ArchitecturalPattern.PROCEDURAL.value
    assert assessment.recommended_pattern == ArchitecturalPattern.DOMAIN_DRIVEN_DESIGN.value
