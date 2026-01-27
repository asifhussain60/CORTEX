"""
Test suite for Comprehension YAML Generation.

Tests the CanonicalIntentComposer class which transforms canonicalized intents,
challenges, and recommendations into structured YAML comprehension documents
for user approval before execution.

Test Categories:
1. YAML Structure Generation - Verify correct YAML format and hierarchy
2. Content Integration - Combine intent + challenges + recommendations
3. Serialization - Convert objects to YAML-compatible dicts
4. Round-trip Conversion - Parse YAML and reconstruct objects
5. Validation - Ensure YAML structure meets schema requirements
6. Edge Cases - Handle empty challenges, missing recommendations, edge inputs
"""

import pytest
import yaml
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

from cortex.brain.core.intent.comprehension_yaml import (
    CanonicalIntentComposer,
    ComprehensionYAML,
    IntentSection,
    ChallengeSection,
    RecommendationSection,
)


# ============================================================================
# FIXTURES: Intent, Challenge, Recommendation Objects
# ============================================================================

@pytest.fixture
def basic_intent_dict():
    """Basic canonicalized intent fixture."""
    return {
        "intent_type": "IMPLEMENT",
        "scope": {
            "target_type": "function",
            "target_name": "calculate_total",
            "file_path": "src/billing/calculator.py",
        },
        "confidence": 0.95,
        "keywords": ["calculate", "total", "billing"],
        "needs_clarification": False,
        "timestamp": "2026-01-15T10:30:00Z",
    }


@pytest.fixture
def basic_challenge_list():
    """Basic challenge fixtures."""
    return [
        {
            "id": "TEST_GAP_001",
            "category": "TEST_GAP",
            "severity": "HIGH",
            "description": "No tests for error handling in calculate_total",
            "affected_code": "calculate_total() in src/billing/calculator.py",
            "remediation": "Add test cases for edge cases (negative amounts, zero)",
            "confidence": 0.85,
        },
        {
            "id": "GOVERNANCE_001",
            "category": "GOVERNANCE_RISK",
            "severity": "MEDIUM",
            "description": "Missing docstring for public function",
            "affected_code": "calculate_total() in src/billing/calculator.py",
            "remediation": "Add Google-style docstring with Args/Returns/Raises",
            "confidence": 0.90,
        },
    ]


@pytest.fixture
def basic_recommendation_list():
    """Basic recommendation fixtures."""
    return [
        {
            "id": "REC_001",
            "category": "TEST_STRATEGY",
            "priority": "HIGH",
            "title": "Add parametrized tests",
            "description": "Use pytest.mark.parametrize for edge cases",
            "code_context": "def test_calculate_total():",
            "alternative": "@pytest.mark.parametrize('amount,expected', [...])",
            "rationale": "Improves test maintainability and coverage",
        },
        {
            "id": "REC_002",
            "category": "DOCUMENTATION",
            "priority": "MEDIUM",
            "title": "Document return type",
            "description": "Specify if return is Decimal or float",
            "code_context": "def calculate_total(items):",
            "alternative": "-> Decimal:",
            "rationale": "Enables IDE auto-complete and reduces errors",
        },
    ]


@pytest.fixture
def comprehensive_intent_dict():
    """Comprehensive intent with multiple scope types."""
    return {
        "intent_type": "REFACTOR",
        "scope": {
            "target_type": "module",
            "target_name": "billing",
            "file_path": "src/billing/",
            "ac_ids": ["AC-001", "AC-002"],
        },
        "confidence": 0.88,
        "keywords": ["refactor", "billing", "payment", "invoice"],
        "needs_clarification": False,
        "timestamp": "2026-01-15T11:00:00Z",
    }


@pytest.fixture
def empty_challenge_list():
    """Empty challenges list (no issues found)."""
    return []


@pytest.fixture
def critical_challenges():
    """Challenges with CRITICAL severity."""
    return [
        {
            "id": "SECURITY_001",
            "category": "SECURITY_RISK",
            "severity": "CRITICAL",
            "description": "Unvalidated file path in open() call",
            "affected_code": "open(user_path) in src/file_handler.py:42",
            "remediation": "Validate path is within allowed directory",
            "confidence": 0.99,
        },
        {
            "id": "BREAKING_001",
            "category": "BREAKING_CHANGE",
            "severity": "CRITICAL",
            "description": "Function signature change affects 5 call sites",
            "affected_code": "process_order() used in checkout, shipping, billing",
            "remediation": "Update all call sites or deprecate old signature",
            "confidence": 0.92,
        },
    ]


@pytest.fixture
def mixed_priority_recommendations():
    """Recommendations with mixed priority levels."""
    return [
        {
            "id": "REC_HIGH",
            "category": "BEST_PRACTICE",
            "priority": "HIGH",
            "title": "Use context manager",
            "description": "Replace try/finally with 'with' statement",
            "code_context": "try:\n    f = open(file)\n    ...\nfinally:\n    f.close()",
            "alternative": "with open(file) as f:\n    ...",
            "rationale": "Safer, more Pythonic, guaranteed cleanup",
        },
        {
            "id": "REC_LOW",
            "category": "OPTIMIZATION",
            "priority": "LOW",
            "title": "Use list comprehension",
            "description": "More efficient than map() for simple transformations",
            "code_context": "list(map(lambda x: x * 2, items))",
            "alternative": "[x * 2 for x in items]",
            "rationale": "Slightly faster, more readable",
        },
    ]


# ============================================================================
# TEST CATEGORY 1: YAML Structure Generation
# ============================================================================

class TestYAMLStructureGeneration:
    """Verify correct YAML format and hierarchy."""

    def test_composer_initialization(self):
        """Composer should initialize with default settings."""
        composer = CanonicalIntentComposer()
        assert composer is not None

    def test_basic_yaml_generation(self, basic_intent_dict, basic_challenge_list, basic_recommendation_list):
        """Generate basic YAML from intent + challenges + recommendations."""
        composer = CanonicalIntentComposer()
        result = composer.compose(basic_intent_dict, basic_challenge_list, basic_recommendation_list)
        
        assert isinstance(result, ComprehensionYAML)
        assert result.intent is not None
        assert result.challenges is not None
        assert result.recommendations is not None

    def test_yaml_top_level_keys(self, basic_intent_dict, basic_challenge_list, basic_recommendation_list):
        """YAML should have metadata, intent, challenges, recommendations keys."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, basic_challenge_list, basic_recommendation_list)
        yaml_dict = yaml_obj.to_dict()
        
        assert "metadata" in yaml_dict
        assert "intent" in yaml_dict
        assert "challenges" in yaml_dict
        assert "recommendations" in yaml_dict

    def test_metadata_structure(self, basic_intent_dict, basic_challenge_list, basic_recommendation_list):
        """Metadata should include version, timestamp, tool info."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, basic_challenge_list, basic_recommendation_list)
        metadata = yaml_obj.to_dict()["metadata"]
        
        assert "version" in metadata
        assert "generated_at" in metadata
        assert "tool" in metadata
        assert "phase" in metadata

    def test_intent_section_structure(self, basic_intent_dict, basic_challenge_list, basic_recommendation_list):
        """Intent section should include type, scope, confidence."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, basic_challenge_list, basic_recommendation_list)
        intent_dict = yaml_obj.to_dict()["intent"]
        
        assert "type" in intent_dict
        assert "scope" in intent_dict
        assert "confidence" in intent_dict
        assert "keywords" in intent_dict

    def test_challenges_section_hierarchy(self, basic_intent_dict, basic_challenge_list, basic_recommendation_list):
        """Challenges should be grouped by severity/category."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, basic_challenge_list, basic_recommendation_list)
        challenges_dict = yaml_obj.to_dict()["challenges"]
        
        assert "summary" in challenges_dict
        assert "items" in challenges_dict

    def test_recommendations_section_priority_ordering(self, basic_intent_dict, basic_challenge_list, mixed_priority_recommendations):
        """Recommendations should be ordered by priority (HIGH → MEDIUM → LOW)."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, basic_challenge_list, mixed_priority_recommendations)
        recommendations_dict = yaml_obj.to_dict()["recommendations"]
        
        items = recommendations_dict["items"]
        if len(items) > 1:
            for i in range(len(items) - 1):
                priority_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
                assert priority_order[items[i]["priority"]] >= priority_order[items[i + 1]["priority"]]

    def test_yaml_is_valid_format(self, basic_intent_dict, basic_challenge_list, basic_recommendation_list):
        """Generated YAML should be parseable by standard YAML parser."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, basic_challenge_list, basic_recommendation_list)
        yaml_string = composer.to_yaml_string(yaml_obj)
        
        parsed = yaml.safe_load(yaml_string)
        assert parsed is not None
        assert isinstance(parsed, dict)


# ============================================================================
# TEST CATEGORY 2: Content Integration
# ============================================================================

class TestContentIntegration:
    """Combine intent + challenges + recommendations correctly."""

    def test_intent_preserved_in_yaml(self, basic_intent_dict, empty_challenge_list, basic_recommendation_list):
        """Intent data should be preserved exactly."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, empty_challenge_list, basic_recommendation_list)
        intent_dict = yaml_obj.to_dict()["intent"]
        
        assert intent_dict["type"] == basic_intent_dict["intent_type"]
        assert intent_dict["confidence"] == basic_intent_dict["confidence"]

    def test_all_challenges_included(self, basic_intent_dict, basic_challenge_list, basic_recommendation_list):
        """All challenges should be included in YAML."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, basic_challenge_list, basic_recommendation_list)
        challenges_dict = yaml_obj.to_dict()["challenges"]
        
        assert len(challenges_dict["items"]) == len(basic_challenge_list)

    def test_all_recommendations_included(self, basic_intent_dict, basic_challenge_list, basic_recommendation_list):
        """All recommendations should be included in YAML."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, basic_challenge_list, basic_recommendation_list)
        recommendations_dict = yaml_obj.to_dict()["recommendations"]
        
        assert len(recommendations_dict["items"]) == len(basic_recommendation_list)

    def test_challenge_count_in_summary(self, basic_intent_dict, basic_challenge_list, basic_recommendation_list):
        """Summary should report correct challenge count."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, basic_challenge_list, basic_recommendation_list)
        summary = yaml_obj.to_dict()["challenges"]["summary"]
        
        assert summary["total"] == len(basic_challenge_list)

    def test_severity_distribution_in_summary(self, basic_intent_dict, critical_challenges, basic_recommendation_list):
        """Summary should count challenges by severity."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, critical_challenges, basic_recommendation_list)
        summary = yaml_obj.to_dict()["challenges"]["summary"]
        
        assert summary["critical"] == 2
        assert "by_severity" in summary

    def test_recommendation_count_in_summary(self, basic_intent_dict, basic_challenge_list, basic_recommendation_list):
        """Summary should report correct recommendation count."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, basic_challenge_list, basic_recommendation_list)
        summary = yaml_obj.to_dict()["recommendations"]["summary"]
        
        assert summary["total"] == len(basic_recommendation_list)


# ============================================================================
# TEST CATEGORY 3: Serialization
# ============================================================================

class TestSerialization:
    """Convert objects to YAML-compatible dicts."""

    def test_to_dict_produces_valid_dict(self, basic_intent_dict, basic_challenge_list, basic_recommendation_list):
        """to_dict() should produce valid Python dict."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, basic_challenge_list, basic_recommendation_list)
        result_dict = yaml_obj.to_dict()
        
        assert isinstance(result_dict, dict)
        assert len(result_dict) > 0

    def test_to_yaml_string_produces_valid_yaml(self, basic_intent_dict, basic_challenge_list, basic_recommendation_list):
        """to_yaml_string() should produce valid YAML string."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, basic_challenge_list, basic_recommendation_list)
        yaml_string = composer.to_yaml_string(yaml_obj)
        
        assert isinstance(yaml_string, str)
        assert len(yaml_string) > 0
        # Should be parseable
        parsed = yaml.safe_load(yaml_string)
        assert parsed is not None

    def test_nested_structures_serializable(self, comprehensive_intent_dict, basic_challenge_list, basic_recommendation_list):
        """Complex nested structures should serialize correctly."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(comprehensive_intent_dict, basic_challenge_list, basic_recommendation_list)
        yaml_string = composer.to_yaml_string(yaml_obj)
        parsed = yaml.safe_load(yaml_string)
        
        assert "scope" in parsed["intent"]
        assert isinstance(parsed["intent"]["scope"], dict)

    def test_special_characters_escaped(self, basic_challenge_list, basic_recommendation_list):
        """Special characters in strings should be properly escaped."""
        intent_with_special = {
            "intent_type": "IMPLEMENT",
            "scope": {
                "target_type": "function",
                "target_name": "test_func",
                "file_path": "src/test.py",
            },
            "confidence": 0.9,
            "keywords": ["fix: broken", "issue/bug"],
            "needs_clarification": False,
        }
        
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(intent_with_special, basic_challenge_list, basic_recommendation_list)
        yaml_string = composer.to_yaml_string(yaml_obj)
        
        # Should not raise exceptions
        parsed = yaml.safe_load(yaml_string)
        assert ":" in str(parsed)


# ============================================================================
# TEST CATEGORY 4: Round-trip Conversion
# ============================================================================

class TestRoundTripConversion:
    """Parse YAML and reconstruct objects."""

    def test_yaml_to_dict_to_yaml_consistency(self, basic_intent_dict, basic_challenge_list, basic_recommendation_list):
        """YAML → dict → YAML should produce equivalent YAML."""
        composer = CanonicalIntentComposer()
        yaml_obj1 = composer.compose(basic_intent_dict, basic_challenge_list, basic_recommendation_list)
        yaml_string1 = composer.to_yaml_string(yaml_obj1)
        
        # Parse and re-compose
        parsed_dict = yaml.safe_load(yaml_string1)
        yaml_obj2 = ComprehensionYAML.from_dict(parsed_dict)
        yaml_string2 = composer.to_yaml_string(yaml_obj2)
        
        # Both should parse to equivalent dicts
        dict1 = yaml.safe_load(yaml_string1)
        dict2 = yaml.safe_load(yaml_string2)
        
        assert dict1["intent"]["type"] == dict2["intent"]["type"]
        assert dict1["challenges"]["summary"]["total"] == dict2["challenges"]["summary"]["total"]

    def test_round_trip_preserves_challenge_data(self, basic_intent_dict, basic_challenge_list, basic_recommendation_list):
        """Challenge data should survive round-trip conversion."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, basic_challenge_list, basic_recommendation_list)
        yaml_string = composer.to_yaml_string(yaml_obj)
        
        parsed = yaml.safe_load(yaml_string)
        challenges = parsed["challenges"]["items"]
        
        assert len(challenges) == len(basic_challenge_list)
        assert challenges[0]["id"] == basic_challenge_list[0]["id"]

    def test_round_trip_preserves_recommendation_data(self, basic_intent_dict, basic_challenge_list, basic_recommendation_list):
        """Recommendation data should survive round-trip conversion."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, basic_challenge_list, basic_recommendation_list)
        yaml_string = composer.to_yaml_string(yaml_obj)
        
        parsed = yaml.safe_load(yaml_string)
        recommendations = parsed["recommendations"]["items"]
        
        assert len(recommendations) == len(basic_recommendation_list)
        assert recommendations[0]["id"] == basic_recommendation_list[0]["id"]


# ============================================================================
# TEST CATEGORY 5: Validation
# ============================================================================

class TestValidation:
    """Ensure YAML structure meets schema requirements."""

    def test_required_metadata_fields(self, basic_intent_dict, basic_challenge_list, basic_recommendation_list):
        """All required metadata fields must be present."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, basic_challenge_list, basic_recommendation_list)
        metadata = yaml_obj.to_dict()["metadata"]
        
        required = ["version", "generated_at", "tool", "phase", "intent_id"]
        for field in required:
            assert field in metadata

    def test_required_intent_fields(self, basic_intent_dict, basic_challenge_list, basic_recommendation_list):
        """All required intent fields must be present."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, basic_challenge_list, basic_recommendation_list)
        intent = yaml_obj.to_dict()["intent"]
        
        required = ["type", "scope", "confidence", "keywords"]
        for field in required:
            assert field in intent

    def test_required_challenge_fields(self, basic_intent_dict, basic_challenge_list, basic_recommendation_list):
        """Each challenge must have required fields."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, basic_challenge_list, basic_recommendation_list)
        challenges = yaml_obj.to_dict()["challenges"]["items"]
        
        required = ["id", "category", "severity", "description", "remediation"]
        for challenge in challenges:
            for field in required:
                assert field in challenge

    def test_required_recommendation_fields(self, basic_intent_dict, basic_challenge_list, basic_recommendation_list):
        """Each recommendation must have required fields."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, basic_challenge_list, basic_recommendation_list)
        recommendations = yaml_obj.to_dict()["recommendations"]["items"]
        
        required = ["id", "category", "priority", "title", "description"]
        for rec in recommendations:
            for field in required:
                assert field in rec

    def test_confidence_in_valid_range(self, basic_intent_dict, basic_challenge_list, basic_recommendation_list):
        """Confidence scores should be between 0 and 1."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, basic_challenge_list, basic_recommendation_list)
        intent = yaml_obj.to_dict()["intent"]
        
        assert 0 <= intent["confidence"] <= 1

    def test_severity_values_valid(self, basic_intent_dict, critical_challenges, basic_recommendation_list):
        """Severity should be one of LOW, MEDIUM, HIGH, CRITICAL."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, critical_challenges, basic_recommendation_list)
        challenges = yaml_obj.to_dict()["challenges"]["items"]
        
        valid_severities = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        for challenge in challenges:
            assert challenge["severity"] in valid_severities

    def test_priority_values_valid(self, basic_intent_dict, basic_challenge_list, mixed_priority_recommendations):
        """Priority should be one of LOW, MEDIUM, HIGH."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, basic_challenge_list, mixed_priority_recommendations)
        recommendations = yaml_obj.to_dict()["recommendations"]["items"]
        
        valid_priorities = {"LOW", "MEDIUM", "HIGH"}
        for rec in recommendations:
            assert rec["priority"] in valid_priorities


# ============================================================================
# TEST CATEGORY 6: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Handle empty challenges, missing recommendations, edge inputs."""

    def test_empty_challenges_list(self, basic_intent_dict, empty_challenge_list, basic_recommendation_list):
        """Handle case with no challenges."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, empty_challenge_list, basic_recommendation_list)
        challenges_dict = yaml_obj.to_dict()["challenges"]
        
        assert challenges_dict["summary"]["total"] == 0
        assert len(challenges_dict["items"]) == 0

    def test_empty_recommendations_list(self, basic_intent_dict, basic_challenge_list):
        """Handle case with no recommendations."""
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, basic_challenge_list, [])
        recommendations_dict = yaml_obj.to_dict()["recommendations"]
        
        assert recommendations_dict["summary"]["total"] == 0
        assert len(recommendations_dict["items"]) == 0

    def test_single_challenge(self, basic_intent_dict, basic_recommendation_list):
        """Handle case with single challenge."""
        single_challenge = [
            {
                "id": "SINGLE_001",
                "category": "TEST_GAP",
                "severity": "MEDIUM",
                "description": "Single challenge",
                "affected_code": "test_func()",
                "remediation": "Add tests",
                "confidence": 0.8,
            }
        ]
        
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, single_challenge, basic_recommendation_list)
        challenges = yaml_obj.to_dict()["challenges"]["items"]
        
        assert len(challenges) == 1

    def test_very_high_confidence(self, basic_challenge_list, basic_recommendation_list):
        """Handle intent with very high confidence (0.99)."""
        high_confidence_intent = {
            "intent_type": "FIX",
            "scope": {
                "target_type": "function",
                "target_name": "bug_fix",
                "file_path": "src/bug.py",
            },
            "confidence": 0.99,
            "keywords": ["fix"],
            "needs_clarification": False,
        }
        
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(high_confidence_intent, basic_challenge_list, basic_recommendation_list)
        intent = yaml_obj.to_dict()["intent"]
        
        assert intent["confidence"] == 0.99

    def test_very_long_descriptions(self, basic_intent_dict, basic_challenge_list, basic_recommendation_list):
        """Handle very long description strings."""
        long_description_challenge = basic_challenge_list.copy()
        long_description_challenge[0]["description"] = "x" * 1000
        
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(
            intent_dict=basic_intent_dict,
            challenges=long_description_challenge,
            recommendations=basic_recommendation_list
        )
        
        challenges = yaml_obj.to_dict()["challenges"]["items"]
        assert len(challenges[0]["description"]) == 1000

    def test_unicode_in_content(self, basic_challenge_list, basic_recommendation_list):
        """Handle unicode characters in content."""
        unicode_intent = {
            "intent_type": "IMPLEMENT",
            "scope": {
                "target_type": "function",
                "target_name": "função_teste",  # Portuguese
                "file_path": "src/café.py",
            },
            "confidence": 0.9,
            "keywords": ["测试", "тест"],  # Chinese, Russian
            "needs_clarification": False,
        }
        
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(unicode_intent, basic_challenge_list, basic_recommendation_list)
        yaml_string = composer.to_yaml_string(yaml_obj)
        
        # Should parse without errors
        parsed = yaml.safe_load(yaml_string)
        assert parsed is not None

    def test_multiple_challenges_with_duplicate_categories(self, basic_intent_dict, basic_recommendation_list):
        """Handle multiple challenges with same category."""
        duplicate_category_challenges = [
            {
                "id": "TEST_001",
                "category": "TEST_GAP",
                "severity": "HIGH",
                "description": "First test gap",
                "affected_code": "func1()",
                "remediation": "Add tests",
                "confidence": 0.8,
            },
            {
                "id": "TEST_002",
                "category": "TEST_GAP",
                "severity": "MEDIUM",
                "description": "Second test gap",
                "affected_code": "func2()",
                "remediation": "Add tests",
                "confidence": 0.7,
            },
        ]
        
        composer = CanonicalIntentComposer()
        yaml_obj = composer.compose(basic_intent_dict, duplicate_category_challenges, basic_recommendation_list)
        challenges = yaml_obj.to_dict()["challenges"]["items"]
        
        assert len(challenges) == 2
        assert all(c["category"] == "TEST_GAP" for c in challenges)
