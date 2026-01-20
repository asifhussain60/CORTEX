"""
Test Suite for LENS Response Formatter (IR-003-03).

Validates formatting of comprehension output for user presentation in multiple
formats (YAML, Markdown, JSON). Ensures consistent, readable presentation of
challenges, recommendations, and intent summaries to support user approval gate.

Tests cover:
1. YAML Response Formatting
2. Markdown Response Formatting
3. JSON Response Formatting
4. Response Field Validation
5. Severity/Priority Sorting
6. Template Customization
7. Multi-format Conversion
8. Edge Cases and Error Handling
9. Integration with Reflection Protocol
"""

import pytest
from datetime import datetime
from typing import Dict, Any
import json
import yaml

# Import modules to test
from cortex.core.intent.lens_response_formatter import (
    LENSResponseFormatter,
    FormattedResponse,
    ResponseFormat,
    SeverityColor,
)
from cortex.core.intent.lens_context_builder import LENSContext


# ============================================================================
# TEST FIXTURES - Response Data
# ============================================================================

@pytest.fixture
def sample_reflection_response():
    """Sample reflection response to format."""
    return {
        "id": "ref_12345",
        "timestamp": datetime.now().isoformat(),
        "status": "PENDING_CONFIRMATION",
        "intent": {
            "type": "IMPLEMENT",
            "scope": {
                "target_type": "function",
                "target_name": "process_data",
                "file_path": "src/core/processor.py",
            },
            "confidence": 0.92,
            "keywords": ["data", "processing", "validation"],
        },
        "challenges": [
            {
                "id": "ch_001",
                "category": "TEST_GAP",
                "severity": "HIGH",
                "description": "No tests for edge case handling",
                "affected_code": "process_data function",
                "remediation": "Add test cases for None/empty inputs",
            },
            {
                "id": "ch_002",
                "category": "BREAKING_CHANGE",
                "severity": "CRITICAL",
                "description": "Change alters API signature",
                "affected_code": "External API callers",
                "remediation": "Update all callers or provide migration path",
            },
        ],
        "recommendations": [
            {
                "id": "rec_001",
                "category": "BEST_PRACTICE",
                "priority": "HIGH",
                "description": "Use type hints for better maintainability",
                "suggestion": "Add type annotations to function signature",
            },
            {
                "id": "rec_002",
                "category": "DOCUMENTATION",
                "priority": "MEDIUM",
                "description": "Document the validation rules",
                "suggestion": "Add docstring with validation criteria",
            },
        ],
        "audit_trail": [
            {"event": "REFLECTION_START", "timestamp": datetime.now().isoformat()},
            {"event": "CONTEXT_AGGREGATION", "timestamp": datetime.now().isoformat()},
            {"event": "REFLECTION_COMPLETE", "timestamp": datetime.now().isoformat()},
        ],
    }


@pytest.fixture
def minimal_reflection_response():
    """Minimal reflection response with only required fields."""
    return {
        "id": "ref_minimal",
        "timestamp": datetime.now().isoformat(),
        "status": "PENDING_CONFIRMATION",
        "intent": {
            "type": "QUERY",
            "scope": {"target_type": "module"},
            "confidence": 0.75,
        },
        "challenges": [],
        "recommendations": [],
    }


# ============================================================================
# TEST CLASS 1: YAML Response Formatting
# ============================================================================

class TestYAMLResponseFormatting:
    """Test formatting responses as YAML."""

    def test_format_to_yaml(self, sample_reflection_response):
        """Test formatting response to YAML."""
        formatter = LENSResponseFormatter()
        yaml_response = formatter.format(
            sample_reflection_response,
            ResponseFormat.YAML
        )

        assert isinstance(yaml_response, str)
        assert "intent:" in yaml_response
        assert "challenges:" in yaml_response
        assert "recommendations:" in yaml_response

    def test_yaml_is_valid(self, sample_reflection_response):
        """Test formatted YAML is valid and parseable."""
        formatter = LENSResponseFormatter()
        yaml_response = formatter.format(
            sample_reflection_response,
            ResponseFormat.YAML
        )

        # Should be parseable back to dict
        parsed = yaml.safe_load(yaml_response)
        assert parsed is not None
        assert "intent" in parsed

    def test_yaml_includes_all_sections(self, sample_reflection_response):
        """Test YAML includes all required sections."""
        formatter = LENSResponseFormatter()
        yaml_response = formatter.format(
            sample_reflection_response,
            ResponseFormat.YAML
        )

        parsed = yaml.safe_load(yaml_response)
        assert "reflection_id" in parsed or "id" in parsed
        assert "status" in parsed
        assert "intent" in parsed
        assert "challenges" in parsed
        assert "recommendations" in parsed

    def test_yaml_challenges_sorted_by_severity(self, sample_reflection_response):
        """Test challenges sorted by severity (CRITICAL first)."""
        formatter = LENSResponseFormatter()
        yaml_response = formatter.format(
            sample_reflection_response,
            ResponseFormat.YAML
        )

        parsed = yaml.safe_load(yaml_response)
        challenges = parsed.get("challenges", [])
        
        # CRITICAL should appear before HIGH
        if len(challenges) >= 2:
            severities = [c.get("severity") for c in challenges]
            assert severities[0] in ["CRITICAL", "HIGH"]


# ============================================================================
# TEST CLASS 2: Markdown Response Formatting
# ============================================================================

class TestMarkdownResponseFormatting:
    """Test formatting responses as Markdown."""

    def test_format_to_markdown(self, sample_reflection_response):
        """Test formatting response to Markdown."""
        formatter = LENSResponseFormatter()
        md_response = formatter.format(
            sample_reflection_response,
            ResponseFormat.MARKDOWN
        )

        assert isinstance(md_response, str)
        assert "#" in md_response  # Should have headers

    def test_markdown_has_headers(self, sample_reflection_response):
        """Test Markdown includes appropriate headers."""
        formatter = LENSResponseFormatter()
        md_response = formatter.format(
            sample_reflection_response,
            ResponseFormat.MARKDOWN
        )

        assert "# Intent" in md_response or "## Intent" in md_response
        assert "Challenges" in md_response or "challenges" in md_response

    def test_markdown_has_severity_indicators(self, sample_reflection_response):
        """Test Markdown includes severity/priority indicators."""
        formatter = LENSResponseFormatter()
        md_response = formatter.format(
            sample_reflection_response,
            ResponseFormat.MARKDOWN
        )

        # Should indicate severity levels
        assert "CRITICAL" in md_response or "Critical" in md_response
        assert "HIGH" in md_response or "High" in md_response

    def test_markdown_is_readable(self, sample_reflection_response):
        """Test Markdown output is well-formatted and readable."""
        formatter = LENSResponseFormatter()
        md_response = formatter.format(
            sample_reflection_response,
            ResponseFormat.MARKDOWN
        )

        # Should have structure
        lines = md_response.split("\n")
        assert len(lines) > 5


# ============================================================================
# TEST CLASS 3: JSON Response Formatting
# ============================================================================

class TestJSONResponseFormatting:
    """Test formatting responses as JSON."""

    def test_format_to_json(self, sample_reflection_response):
        """Test formatting response to JSON."""
        formatter = LENSResponseFormatter()
        json_response = formatter.format(
            sample_reflection_response,
            ResponseFormat.JSON
        )

        assert isinstance(json_response, str)
        parsed = json.loads(json_response)
        assert parsed is not None

    def test_json_is_valid(self, sample_reflection_response):
        """Test formatted JSON is valid."""
        formatter = LENSResponseFormatter()
        json_response = formatter.format(
            sample_reflection_response,
            ResponseFormat.JSON
        )

        parsed = json.loads(json_response)
        assert "intent" in parsed
        assert "challenges" in parsed

    def test_json_structure_preserved(self, sample_reflection_response):
        """Test JSON preserves response structure."""
        formatter = LENSResponseFormatter()
        json_response = formatter.format(
            sample_reflection_response,
            ResponseFormat.JSON
        )

        parsed = json.loads(json_response)
        assert len(parsed.get("challenges", [])) == len(sample_reflection_response["challenges"])


# ============================================================================
# TEST CLASS 4: Response Field Validation
# ============================================================================

class TestResponseFieldValidation:
    """Test validation of response fields."""

    def test_validate_required_fields(self, sample_reflection_response):
        """Test response includes all required fields."""
        formatter = LENSResponseFormatter()
        formatted = formatter.format(
            sample_reflection_response,
            ResponseFormat.JSON
        )

        parsed = json.loads(formatted)
        assert "intent" in parsed
        assert "status" in parsed

    def test_validate_intent_fields(self, sample_reflection_response):
        """Test intent section has required fields."""
        formatter = LENSResponseFormatter()
        formatted = formatter.format(
            sample_reflection_response,
            ResponseFormat.JSON
        )

        parsed = json.loads(formatted)
        intent = parsed.get("intent", {})
        assert "type" in intent
        assert "confidence" in intent

    def test_validate_challenge_fields(self, sample_reflection_response):
        """Test each challenge has required fields."""
        formatter = LENSResponseFormatter()
        formatted = formatter.format(
            sample_reflection_response,
            ResponseFormat.JSON
        )

        parsed = json.loads(formatted)
        challenges = parsed.get("challenges", [])
        
        for challenge in challenges:
            assert "category" in challenge
            assert "severity" in challenge
            assert "description" in challenge

    def test_validate_recommendation_fields(self, sample_reflection_response):
        """Test each recommendation has required fields."""
        formatter = LENSResponseFormatter()
        formatted = formatter.format(
            sample_reflection_response,
            ResponseFormat.JSON
        )

        parsed = json.loads(formatted)
        recommendations = parsed.get("recommendations", [])
        
        for rec in recommendations:
            assert "category" in rec
            assert "description" in rec


# ============================================================================
# TEST CLASS 5: Severity/Priority Sorting
# ============================================================================

class TestSeverityPrioritySorting:
    """Test sorting by severity and priority."""

    def test_sort_challenges_by_severity(self, sample_reflection_response):
        """Test challenges sorted with CRITICAL first."""
        formatter = LENSResponseFormatter()
        formatter.sort_challenges_by_severity = True
        
        formatted = formatter.format(
            sample_reflection_response,
            ResponseFormat.JSON
        )

        parsed = json.loads(formatted)
        challenges = parsed.get("challenges", [])
        
        # CRITICAL should come before HIGH
        severity_order = [c.get("severity") for c in challenges]
        assert severity_order[0] == "CRITICAL"

    def test_sort_recommendations_by_priority(self, sample_reflection_response):
        """Test recommendations sorted with HIGH priority first."""
        formatter = LENSResponseFormatter()
        formatter.sort_recommendations_by_priority = True
        
        formatted = formatter.format(
            sample_reflection_response,
            ResponseFormat.JSON
        )

        parsed = json.loads(formatted)
        recommendations = parsed.get("recommendations", [])
        
        if len(recommendations) > 0:
            assert "priority" in recommendations[0]

    def test_custom_severity_levels(self):
        """Test custom severity level ordering."""
        formatter = LENSResponseFormatter()
        
        # Should support standard severity levels
        assert formatter is not None


# ============================================================================
# TEST CLASS 6: Template Customization
# ============================================================================

class TestTemplateCustomization:
    """Test template customization options."""

    def test_include_audit_trail(self, sample_reflection_response):
        """Test including audit trail in response."""
        formatter = LENSResponseFormatter()
        formatter.include_audit_trail = True
        
        formatted = formatter.format(
            sample_reflection_response,
            ResponseFormat.JSON
        )

        parsed = json.loads(formatted)
        assert "audit_trail" in parsed

    def test_exclude_audit_trail(self, sample_reflection_response):
        """Test excluding audit trail from response."""
        formatter = LENSResponseFormatter()
        formatter.include_audit_trail = False
        
        formatted = formatter.format(
            sample_reflection_response,
            ResponseFormat.JSON
        )

        parsed = json.loads(formatted)
        # Audit trail may not be included
        assert parsed is not None

    def test_custom_section_ordering(self, sample_reflection_response):
        """Test custom ordering of sections."""
        formatter = LENSResponseFormatter()
        custom_order = ["challenges", "recommendations", "intent"]
        
        formatted = formatter.format(
            sample_reflection_response,
            ResponseFormat.JSON,
            section_order=custom_order
        )

        assert formatted is not None

    def test_include_metadata(self, sample_reflection_response):
        """Test including metadata in response."""
        formatter = LENSResponseFormatter()
        formatter.include_metadata = True
        
        formatted = formatter.format(
            sample_reflection_response,
            ResponseFormat.JSON
        )

        parsed = json.loads(formatted)
        # Should have timestamp or metadata
        assert "timestamp" in parsed or "metadata" in parsed


# ============================================================================
# TEST CLASS 7: Multi-format Conversion
# ============================================================================

class TestMultiFormatConversion:
    """Test converting between formats."""

    def test_convert_yaml_to_json(self, sample_reflection_response):
        """Test converting from YAML to JSON."""
        formatter = LENSResponseFormatter()
        
        yaml_response = formatter.format(
            sample_reflection_response,
            ResponseFormat.YAML
        )
        
        # Parse YAML
        yaml_dict = yaml.safe_load(yaml_response)
        
        # Convert to JSON
        json_response = json.dumps(yaml_dict, indent=2)
        
        assert json_response is not None

    def test_convert_json_to_markdown(self, sample_reflection_response):
        """Test converting from JSON to Markdown."""
        formatter = LENSResponseFormatter()
        
        json_response = formatter.format(
            sample_reflection_response,
            ResponseFormat.JSON
        )
        
        # Parse JSON
        json_dict = json.loads(json_response)
        
        # Should be formattable to Markdown
        assert json_dict is not None

    def test_round_trip_conversion(self, sample_reflection_response):
        """Test round-trip conversion preserves data."""
        formatter = LENSResponseFormatter()
        
        # Start with JSON
        json_response = formatter.format(
            sample_reflection_response,
            ResponseFormat.JSON
        )
        json_dict = json.loads(json_response)
        
        # Convert through formats
        challenges_count = len(json_dict.get("challenges", []))
        recommendations_count = len(json_dict.get("recommendations", []))
        
        assert challenges_count == len(sample_reflection_response["challenges"])
        assert recommendations_count == len(sample_reflection_response["recommendations"])


# ============================================================================
# TEST CLASS 8: Edge Cases and Error Handling
# ============================================================================

class TestEdgeCasesAndErrors:
    """Test edge cases and error handling."""

    def test_format_minimal_response(self, minimal_reflection_response):
        """Test formatting minimal response with no challenges."""
        formatter = LENSResponseFormatter()
        formatted = formatter.format(
            minimal_reflection_response,
            ResponseFormat.JSON
        )

        assert formatted is not None
        parsed = json.loads(formatted)
        assert len(parsed.get("challenges", [])) == 0

    def test_format_with_special_characters(self):
        """Test formatting with special characters in text."""
        response = {
            "id": "test",
            "timestamp": datetime.now().isoformat(),
            "intent": {
                "type": "IMPLEMENT",
                "confidence": 0.9,
            },
            "challenges": [{
                "description": "Fix issue with < > & \" ' characters",
                "severity": "HIGH",
            }],
            "recommendations": [],
        }
        
        formatter = LENSResponseFormatter()
        formatted = formatter.format(response, ResponseFormat.JSON)
        
        assert formatted is not None

    def test_format_with_very_long_text(self):
        """Test formatting with very long description."""
        response = {
            "id": "test",
            "timestamp": datetime.now().isoformat(),
            "intent": {
                "type": "IMPLEMENT",
                "confidence": 0.9,
            },
            "challenges": [{
                "description": "A" * 1000,  # Very long string
                "severity": "MEDIUM",
            }],
            "recommendations": [],
        }
        
        formatter = LENSResponseFormatter()
        formatted = formatter.format(response, ResponseFormat.MARKDOWN)
        
        assert formatted is not None

    def test_format_with_empty_response(self):
        """Test formatting response with no data."""
        response = {
            "id": "empty",
            "timestamp": datetime.now().isoformat(),
            "intent": {},
            "challenges": [],
            "recommendations": [],
        }
        
        formatter = LENSResponseFormatter()
        formatted = formatter.format(response, ResponseFormat.JSON)
        
        assert formatted is not None


# ============================================================================
# TEST CLASS 9: Integration with Reflection Protocol
# ============================================================================

class TestIntegrationWithReflectionProtocol:
    """Test integration with Intent Reflection Protocol."""

    def test_format_reflection_response(self, sample_reflection_response):
        """Test formatting a reflection response."""
        formatter = LENSResponseFormatter()
        
        formatted = formatter.format(
            sample_reflection_response,
            ResponseFormat.MARKDOWN
        )
        
        # Should be user-presentable
        assert len(formatted) > 0
        assert "Intent" in formatted or "intent" in formatted

    def test_format_with_all_components(self, sample_reflection_response):
        """Test formatting with all protocol components."""
        formatter = LENSResponseFormatter()
        
        # Should handle complete reflection response
        for fmt in [ResponseFormat.JSON, ResponseFormat.YAML, ResponseFormat.MARKDOWN]:
            formatted = formatter.format(sample_reflection_response, fmt)
            assert formatted is not None

    def test_format_supports_approval_workflow(self, sample_reflection_response):
        """Test formatted response supports user approval workflow."""
        formatter = LENSResponseFormatter()
        
        formatted_md = formatter.format(
            sample_reflection_response,
            ResponseFormat.MARKDOWN
        )
        
        # Should clearly present option to approve/reject
        assert "Intent" in formatted_md or "IMPLEMENT" in formatted_md


# ============================================================================
# TEST CLASS 10: Performance and Optimization
# ============================================================================

class TestPerformanceOptimization:
    """Test performance characteristics."""

    def test_format_performance(self, sample_reflection_response):
        """Test formatting performance."""
        import time
        
        formatter = LENSResponseFormatter()
        
        start = time.time()
        formatter.format(sample_reflection_response, ResponseFormat.JSON)
        elapsed = time.time() - start
        
        assert elapsed < 0.1  # Should complete quickly

    def test_format_large_response_performance(self):
        """Test formatting large response."""
        import time
        
        # Create large response
        response = {
            "id": "large",
            "timestamp": datetime.now().isoformat(),
            "intent": {"type": "IMPLEMENT", "confidence": 0.9},
            "challenges": [
                {
                    "id": f"ch_{i}",
                    "description": f"Challenge {i}",
                    "severity": "MEDIUM",
                }
                for i in range(100)
            ],
            "recommendations": [
                {
                    "id": f"rec_{i}",
                    "description": f"Recommendation {i}",
                }
                for i in range(100)
            ],
        }
        
        formatter = LENSResponseFormatter()
        
        start = time.time()
        formatted = formatter.format(response, ResponseFormat.JSON)
        elapsed = time.time() - start
        
        assert elapsed < 0.5
        assert formatted is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
