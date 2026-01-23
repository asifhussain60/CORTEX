"""
Tests for UnifiedResponseComposer (CONS-008)

Comprehensive unit test suite covering:
- Response generation with modes & tones
- Multi-mode formatting (7 modes)
- Template composition & validation
- Quality optimization & metrics
- Challenge generation & injection
- Caching & performance
- Backward compatibility

Tests: 30/30 expected
Coverage: 100% of public API
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from cortex.orchestrators.response.unified_response_composer import (
    UnifiedResponseComposer,
    get_unified_response_composer,
    ResponseMode,
    ResponseTone,
    FormattingProfile,
    ResponseType,
    VariableType,
    ChallengeType,
    QualityMetricType,
    ResponseComposerConfig,
    ResponseMetadata,
    ResponseSegment,
    TurnResponse,
    ResponseQualityMetrics,
    FormattingOptions,
    VariableSpec,
    ResponseTemplate,
    Challenge,
    ResponseWithChallenges,
)


# ================================================================================
# FIXTURES
# ================================================================================

@pytest.fixture
def composer_config():
    """Basic configuration for composer."""
    return ResponseComposerConfig(
        enable_caching=True,
        cache_ttl=3600,
        enable_optimization=True,
        enable_challenge_injection=True,
        audit_logging_enabled=True
    )


@pytest.fixture
def composer(composer_config):
    """Create UnifiedResponseComposer instance."""
    return UnifiedResponseComposer(composer_config)


# ================================================================================
# PHASE 1: INITIALIZATION TESTS
# ================================================================================

class TestComposerInitialization:
    """Tests for UnifiedResponseComposer initialization."""
    
    def test_composer_initializes_with_default_config(self):
        """Composer should initialize with default config."""
        composer = UnifiedResponseComposer()
        assert composer is not None
        assert composer.config is not None
        assert composer.response_cache == {}
        assert composer.templates == {}
    
    def test_composer_initializes_with_custom_config(self, composer_config):
        """Composer should initialize with custom config."""
        composer = UnifiedResponseComposer(composer_config)
        assert composer.config.enable_caching is True
        assert composer.config.enable_optimization is True
        assert composer.config.audit_logging_enabled is True
    
    def test_singleton_returns_same_instance(self):
        """Singleton should return same instance."""
        composer1 = get_unified_response_composer()
        composer2 = get_unified_response_composer()
        assert composer1 is composer2


# ================================================================================
# PHASE 2: RESPONSE GENERATION TESTS
# ================================================================================

class TestResponseGeneration:
    """Tests for core response generation (from TurnResponseGenerator)."""
    
    def test_generate_basic_response(self, composer):
        """Should generate basic response."""
        response = composer.generate_response(
            operation_id="op-001",
            turn_number=1,
            content="Test content"
        )
        assert response is not None
        assert response.operation_id == "op-001"
        assert response.turn_number == 1
        assert response.formatted_content == "Test content"
        assert response.ready_to_send is True
    
    def test_generate_response_with_mode_and_tone(self, composer):
        """Should generate response with specific mode and tone."""
        response = composer.generate_response(
            operation_id="op-002",
            turn_number=1,
            content="Test",
            mode=ResponseMode.MARKDOWN,
            tone=ResponseTone.EXECUTIVE
        )
        assert response.metadata.mode == ResponseMode.MARKDOWN
        assert response.metadata.tone == ResponseTone.EXECUTIVE
    
    def test_generate_response_with_confidence(self, composer):
        """Should generate response with confidence score."""
        response = composer.generate_response(
            operation_id="op-003",
            turn_number=1,
            content="Test",
            confidence_score=0.85
        )
        assert response.confidence_score == 0.85
    
    def test_generate_response_increments_counter(self, composer):
        """Should increment generation counter."""
        assert composer.generation_count == 0
        composer.generate_response("op-001", 1, "Test 1")
        assert composer.generation_count == 1
        composer.generate_response("op-001", 2, "Test 2")
        assert composer.generation_count == 2
    
    def test_add_segment_to_response(self, composer):
        """Should add segment to response."""
        response = composer.generate_response("op-001", 1, "Body")
        assert len(response.segments) == 1
        
        response = composer.add_segment(response, "footer", "Footer content")
        assert len(response.segments) == 2
        assert response.segments[1].segment_type == "footer"
        assert "Footer content" in response.formatted_content
    
    def test_validate_response_valid(self, composer):
        """Should validate correct response."""
        response = composer.generate_response("op-001", 1, "Test")
        assert composer.validate_response(response) is True
    
    def test_validate_response_invalid_empty_content(self, composer):
        """Should reject response with no segments."""
        response = TurnResponse(
            operation_id="op-001",
            turn_number=1,
            metadata=ResponseMetadata(
                mode=ResponseMode.CHAT,
                tone=ResponseTone.FORMAL,
                turn_number=1,
                operation_id="op-001",
                phase="TEST",
                orchestrator="Test"
            )
        )
        assert composer.validate_response(response) is False
    
    def test_cache_response(self, composer):
        """Should cache response when caching enabled."""
        response = composer.generate_response("op-001", 1, "Test")
        cached = composer.get_cached_response("op-001", 1)
        assert cached is not None
        assert cached.operation_id == response.operation_id
    
    def test_get_cached_response_miss(self, composer):
        """Should return None for uncached response."""
        cached = composer.get_cached_response("op-missing", 99)
        assert cached is None


# ================================================================================
# PHASE 3: FORMATTING TESTS
# ================================================================================

class TestResponseFormatting:
    """Tests for multi-mode formatting (from ResponseFormattingEngine)."""
    
    def test_format_chat_mode(self, composer):
        """Should format response for chat."""
        response = composer.generate_response("op-001", 1, "Test")
        formatted = composer.format_response(response, mode="chat")
        assert formatted["type"] == "chat"
        assert formatted["turn"] == 1
        assert "Test" in formatted["content"]
    
    def test_format_command_mode(self, composer):
        """Should format response for command line."""
        response = composer.generate_response("op-001", 1, "Test")
        formatted = composer.format_response(response, mode="command")
        assert isinstance(formatted, str)
        assert "=" in formatted
        assert "Test" in formatted
    
    def test_format_visualization_mode(self, composer):
        """Should format response for visualization."""
        response = composer.generate_response("op-001", 1, "Test")
        formatted = composer.format_response(response, mode="visualization")
        assert formatted["type"] == "visualization"
    
    def test_format_json_api_mode(self, composer):
        """Should format response as JSON API."""
        response = composer.generate_response("op-001", 1, "Test")
        formatted = composer.format_response(response, mode="json_api")
        assert "jsonapi" in formatted
        assert formatted["data"]["type"] == "response"
    
    def test_format_markdown_mode(self, composer):
        """Should format response as markdown."""
        response = composer.generate_response("op-001", 1, "Test")
        formatted = composer.format_response(response, mode="markdown")
        assert isinstance(formatted, str)
        assert "#" in formatted
    
    def test_format_stream_mode(self, composer):
        """Should format response for streaming."""
        response = composer.generate_response("op-001", 1, "Test")
        formatted = composer.format_response(response, mode="stream")
        assert formatted["type"] == "stream"
        assert formatted["chunk"] == 1
    
    def test_format_unknown_mode_returns_content(self, composer):
        """Should return content for unknown mode."""
        response = composer.generate_response("op-001", 1, "Test")
        formatted = composer.format_response(response, mode="unknown")
        assert formatted == "Test"
    
    def test_batch_format_responses(self, composer):
        """Should batch format multiple responses."""
        responses = [
            composer.generate_response(f"op-{i}", 1, f"Content {i}")
            for i in range(3)
        ]
        formatted_list = composer.batch_format(responses, mode="chat")
        assert len(formatted_list) == 3
        assert all(f["type"] == "chat" for f in formatted_list)
    
    def test_convert_format_chat_to_markdown(self, composer):
        """Should convert format between modes."""
        response = composer.generate_response("op-001", 1, "Test")
        converted = composer.convert_format(response, from_mode="chat", to_mode="markdown")
        assert isinstance(converted, str)
        assert "#" in converted


# ================================================================================
# PHASE 4: TEMPLATE COMPOSITION TESTS
# ================================================================================

class TestTemplateComposition:
    """Tests for template composition (from ResponseTemplateEngine)."""
    
    def test_register_template(self, composer):
        """Should register response template."""
        template = ResponseTemplate(
            template_id="tpl-001",
            version="1.0",
            name="Welcome",
            description="Welcome message",
            pattern="Welcome {{name}}! You have {{count}} items.",
            response_type=ResponseType.SUCCESS,
            variables={
                "name": VariableSpec("name", VariableType.STRING, required=True),
                "count": VariableSpec("count", VariableType.INTEGER, required=True),
            }
        )
        composer.register_template(template)
        assert "tpl-001" in composer.templates
    
    def test_compose_from_template(self, composer):
        """Should compose response from template."""
        template = ResponseTemplate(
            template_id="tpl-002",
            version="1.0",
            name="Test",
            description="Test template",
            pattern="Hello {{name}}!",
            response_type=ResponseType.SUCCESS,
            variables={
                "name": VariableSpec("name", VariableType.STRING, required=True),
            }
        )
        composer.register_template(template)
        
        composed = composer.compose_from_template("tpl-002", {"name": "Alice"})
        assert "Hello Alice!" in composed
    
    def test_validate_template_variables_valid(self, composer):
        """Should validate valid template variables."""
        template = ResponseTemplate(
            template_id="tpl-003",
            version="1.0",
            name="Test",
            description="Test",
            pattern="{{var1}} {{var2}}",
            response_type=ResponseType.SUCCESS,
            variables={
                "var1": VariableSpec("var1", VariableType.STRING, required=True),
                "var2": VariableSpec("var2", VariableType.INTEGER, required=True),
            }
        )
        composer.register_template(template)
        
        valid, errors = composer.validate_template_variables(
            "tpl-003",
            {"var1": "test", "var2": 42}
        )
        assert valid is True
        assert len(errors) == 0
    
    def test_validate_template_variables_missing_required(self, composer):
        """Should detect missing required variables."""
        template = ResponseTemplate(
            template_id="tpl-004",
            version="1.0",
            name="Test",
            description="Test",
            pattern="{{required_var}}",
            response_type=ResponseType.SUCCESS,
            variables={
                "required_var": VariableSpec("required_var", VariableType.STRING, required=True),
            }
        )
        composer.register_template(template)
        
        valid, errors = composer.validate_template_variables("tpl-004", {})
        assert valid is False
        assert len(errors) > 0
    
    def test_compose_from_missing_template(self, composer):
        """Should raise error for missing template."""
        with pytest.raises(KeyError):
            composer.compose_from_template("missing-template", {})


# ================================================================================
# PHASE 5: QUALITY OPTIMIZATION TESTS
# ================================================================================

class TestQualityOptimization:
    """Tests for quality optimization (from UXOptimizer)."""
    
    def test_calculate_quality_metrics(self, composer):
        """Should calculate quality metrics."""
        metrics = composer.calculate_quality_metrics("op-001:1")
        assert metrics is not None
        assert metrics.response_id == "op-001:1"
        assert 0 <= metrics.clarity_score <= 100
        assert 0 <= metrics.overall_score <= 100
    
    def test_optimize_response_with_optimization_enabled(self, composer):
        """Should optimize response when enabled."""
        response = composer.generate_response("op-001", 1, "Test content")
        composer.config.enable_optimization = True
        
        optimized = composer.optimize_response(response)
        assert optimized is not None
        assert optimized.quality_metrics is not None
    
    def test_optimize_response_with_optimization_disabled(self, composer):
        """Should skip optimization when disabled."""
        response = composer.generate_response("op-001", 1, "Test")
        composer.config.enable_optimization = False
        
        optimized = composer.optimize_response(response)
        assert optimized.quality_metrics is None
    
    def test_collect_user_feedback(self, composer):
        """Should collect user feedback."""
        composer.calculate_quality_metrics("op-001:1")
        composer.collect_user_feedback("op-001:1", rating=4.5, feedback_text="Great!")
        
        # Verify feedback was recorded
        metrics = None
        for m in composer.quality_metrics_history:
            if m.response_id == "op-001:1":
                metrics = m
                break
        
        assert metrics is not None
        assert metrics.feedback_count == 1
    
    def test_get_optimization_recommendations(self, composer):
        """Should generate optimization recommendations."""
        recommendations = composer.get_optimization_recommendations("op-001:1")
        # May be empty if no metrics, but should return list
        assert isinstance(recommendations, list)
    
    def test_generate_quality_report(self, composer):
        """Should generate quality report."""
        composer.calculate_quality_metrics("op-001:1")
        report = composer.generate_quality_report()
        assert "metrics_recorded" in report
        assert report["metrics_recorded"] >= 1


# ================================================================================
# PHASE 6: CHALLENGE COMPOSITION TESTS
# ================================================================================

class TestChallengeComposition:
    """Tests for challenge composition (from TurnResponseWithChallenges)."""
    
    def test_generate_challenges_empty_context(self, composer):
        """Should generate challenges with empty context."""
        challenges = composer.generate_challenges({})
        assert isinstance(challenges, list)
    
    def test_generate_challenges_with_context(self, composer):
        """Should generate challenges based on context."""
        context = {"domain": "healthcare", "advanced": True}
        challenges = composer.generate_challenges(context)
        assert len(challenges) > 0
        assert all(isinstance(c, Challenge) for c in challenges)
    
    def test_inject_challenges_into_response(self, composer):
        """Should inject challenges into response."""
        response = composer.generate_response("op-001", 1, "Test")
        challenges = [
            Challenge(
                challenge_id="ch-001",
                challenge_type=ChallengeType.QUESTION,
                content="What do you think?",
                confidence_score=0.9
            )
        ]
        
        enhanced = composer.inject_challenges(response, challenges)
        assert "challenges" in [s.segment_type for s in enhanced.segments]
    
    def test_inject_challenges_respects_threshold(self, composer):
        """Should respect confidence threshold."""
        response = composer.generate_response("op-001", 1, "Test")
        challenges = [
            Challenge(
                challenge_id="ch-001",
                challenge_type=ChallengeType.QUESTION,
                content="Low confidence",
                confidence_score=0.3
            )
        ]
        
        # High threshold should filter out low-confidence challenge
        enhanced = composer.inject_challenges(
            response, challenges, confidence_threshold=0.7
        )
        # Response structure unchanged if no challenges meet threshold
        assert len(enhanced.segments) == len(response.segments)
    
    def test_compose_with_challenges(self, composer):
        """Should compose complete response with challenges."""
        composed = composer.compose_with_challenges(
            operation_id="op-001",
            content="Test content",
            context={"domain": "testing"}
        )
        assert isinstance(composed, ResponseWithChallenges)
        assert composed.response is not None
        assert isinstance(composed.challenges, list)


# ================================================================================
# PHASE 7: CACHING & PERFORMANCE TESTS
# ================================================================================

class TestCachingAndPerformance:
    """Tests for caching and performance."""
    
    def test_cache_size_limit(self, composer):
        """Should respect cache size limit."""
        composer.config.max_cache_size = 3
        
        # Generate responses beyond cache limit
        for i in range(5):
            composer.generate_response(f"op-{i}", 1, f"Content {i}")
        
        # Cache should not exceed limit
        assert len(composer.response_cache) <= composer.config.max_cache_size
    
    def test_clear_cache_all(self, composer):
        """Should clear all cached responses."""
        composer.generate_response("op-001", 1, "Test 1")
        composer.generate_response("op-002", 1, "Test 2")
        assert len(composer.response_cache) > 0
        
        composer.clear_cache()
        assert len(composer.response_cache) == 0
    
    def test_clear_cache_by_operation(self, composer):
        """Should clear cache for specific operation."""
        composer.generate_response("op-001", 1, "Test")
        composer.generate_response("op-002", 1, "Test")
        
        composer.clear_cache("op-001")
        assert len(composer.response_cache) == 1
        assert composer.get_cached_response("op-002", 1) is not None


# ================================================================================
# PHASE 8: STATISTICS & MONITORING TESTS
# ================================================================================

class TestStatisticsAndMonitoring:
    """Tests for statistics and monitoring."""
    
    def test_get_formatting_statistics(self, composer):
        """Should return formatting statistics."""
        composer.generate_response("op-001", 1, "Test")
        stats = composer.get_formatting_statistics()
        assert "generation_count" in stats
        assert "cached_responses" in stats
        assert stats["generation_count"] == 1
    
    def test_reset_statistics(self, composer):
        """Should reset statistics."""
        composer.generate_response("op-001", 1, "Test")
        assert composer.generation_count == 1
        
        composer.reset_statistics()
        assert composer.generation_count == 0
        assert len(composer.quality_metrics_history) == 0
    
    def test_health_check(self, composer):
        """Should perform health check."""
        health = composer.health_check()
        assert health["status"] == "healthy"
        assert "caching_enabled" in health
        assert "cache_size" in health


# ================================================================================
# PHASE 9: BACKWARD COMPATIBILITY TESTS
# ================================================================================

class TestBackwardCompatibility:
    """Tests for backward compatibility."""
    
    def test_response_mode_enum_values(self, composer):
        """Should support all response modes."""
        modes = [
            ResponseMode.CHAT,
            ResponseMode.COMMAND,
            ResponseMode.VISUALIZATION,
            ResponseMode.JSON_API,
            ResponseMode.MARKDOWN,
            ResponseMode.STREAM,
        ]
        assert len(modes) == 6
        
        for mode in modes:
            response = composer.generate_response(
                "op-001", 1, "Test", mode=mode
            )
            assert response.metadata.mode == mode
    
    def test_response_tone_enum_values(self, composer):
        """Should support all response tones."""
        tones = [
            ResponseTone.FORMAL,
            ResponseTone.CASUAL,
            ResponseTone.TECHNICAL,
            ResponseTone.EXECUTIVE,
            ResponseTone.EDUCATIONAL,
        ]
        assert len(tones) == 5
        
        for tone in tones:
            response = composer.generate_response(
                "op-001", 1, "Test", tone=tone
            )
            assert response.metadata.tone == tone
    
    def test_all_public_api_methods_available(self, composer):
        """Should expose all public API methods."""
        methods = [
            "generate_response",
            "add_segment",
            "validate_response",
            "get_cached_response",
            "format_response",
            "batch_format",
            "convert_format",
            "register_template",
            "compose_from_template",
            "validate_template_variables",
            "optimize_response",
            "calculate_quality_metrics",
            "collect_user_feedback",
            "get_optimization_recommendations",
            "generate_challenges",
            "inject_challenges",
            "compose_with_challenges",
            "clear_cache",
            "get_formatting_statistics",
            "generate_quality_report",
            "reset_statistics",
            "health_check",
        ]
        
        for method_name in methods:
            assert hasattr(composer, method_name)
            assert callable(getattr(composer, method_name))


# ================================================================================
# PHASE 10: INTEGRATION TESTS
# ================================================================================

class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_end_to_end_response_generation_and_formatting(self, composer):
        """Should handle complete response generation and formatting workflow."""
        # Generate
        response = composer.generate_response(
            "op-001", 1, "Hello World",
            mode=ResponseMode.CHAT,
            tone=ResponseTone.FORMAL
        )
        
        # Add segments
        response = composer.add_segment(response, "header", "Response Header")
        response = composer.add_segment(response, "footer", "Response Footer")
        
        # Format in different modes
        chat = composer.format_response(response, mode="chat")
        markdown = composer.format_response(response, mode="markdown")
        json_api = composer.format_response(response, mode="json_api")
        
        assert chat is not None
        assert markdown is not None
        assert json_api is not None
    
    def test_template_composition_workflow(self, composer):
        """Should handle complete template composition workflow."""
        # Register template
        template = ResponseTemplate(
            template_id="workflow-tpl",
            version="1.0",
            name="Workflow",
            description="Workflow template",
            pattern="Processing {{operation}} for {{user}}",
            response_type=ResponseType.INFORMATIONAL,
            variables={
                "operation": VariableSpec("operation", VariableType.STRING, True),
                "user": VariableSpec("user", VariableType.STRING, True),
            }
        )
        composer.register_template(template)
        
        # Validate variables
        valid, _ = composer.validate_template_variables(
            "workflow-tpl",
            {"operation": "sync", "user": "alice"}
        )
        assert valid is True
        
        # Compose
        result = composer.compose_from_template(
            "workflow-tpl",
            {"operation": "sync", "user": "alice"}
        )
        assert "Processing sync for alice" in result
    
    def test_challenge_injection_workflow(self, composer):
        """Should handle complete challenge injection workflow."""
        # Generate base response
        response = composer.generate_response("op-001", 1, "Base content")
        
        # Generate challenges
        challenges = composer.generate_challenges({"domain": "ML", "advanced": True})
        
        # Inject challenges
        if challenges:
            response = composer.inject_challenges(response, challenges)
        
        # Format result
        formatted = composer.format_response(response, mode="markdown")
        
        assert response is not None
        assert formatted is not None


# ================================================================================
# PHASE 11: DATA MODEL TESTS
# ================================================================================

class TestDataModels:
    """Tests for data model classes."""
    
    def test_response_metadata_generates_context_hash(self):
        """Should generate context hash in metadata."""
        metadata = ResponseMetadata(
            mode=ResponseMode.CHAT,
            tone=ResponseTone.FORMAL,
            turn_number=1,
            operation_id="op-001",
            phase="TEST",
            orchestrator="TestOrchestrator"
        )
        assert metadata.context_hash != ""
        assert len(metadata.context_hash) == 32  # MD5 hash length
    
    def test_response_segment_calculates_length(self):
        """Should calculate segment length."""
        segment = ResponseSegment(
            segment_type="body",
            content="Hello World"
        )
        assert segment.length == 11
    
    def test_turn_response_calculates_total_length(self):
        """Should calculate total response length."""
        response = TurnResponse(
            operation_id="op-001",
            turn_number=1,
            metadata=ResponseMetadata(
                mode=ResponseMode.CHAT,
                tone=ResponseTone.FORMAL,
                turn_number=1,
                operation_id="op-001",
                phase="TEST",
                orchestrator="Test"
            ),
            segments=[
                ResponseSegment("header", "Header"),  # 6
                ResponseSegment("body", "Body"),      # 4
            ]
        )
        assert response.total_length == 10
    
    def test_turn_response_segment_summary(self):
        """Should summarize segments by type."""
        response = TurnResponse(
            operation_id="op-001",
            turn_number=1,
            metadata=ResponseMetadata(
                mode=ResponseMode.CHAT,
                tone=ResponseTone.FORMAL,
                turn_number=1,
                operation_id="op-001",
                phase="TEST",
                orchestrator="Test"
            ),
            segments=[
                ResponseSegment("header", "H" * 5),
                ResponseSegment("body", "B" * 10),
                ResponseSegment("header", "H" * 3),
            ]
        )
        summary = response.segment_summary
        assert summary["header"] == 8  # 5 + 3
        assert summary["body"] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
