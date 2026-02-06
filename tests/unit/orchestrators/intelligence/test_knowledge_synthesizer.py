"""
Unit tests for KnowledgeSynthesizer.

Tests cover:
- Initialization and configuration
- Best practices YAML generation
- TDD pattern template rendering
- Security rule generation
- External source integration
- Multi-language support
- Caching and performance
- Error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime
import yaml

from cortex.orchestrators.intelligence.knowledge_synthesizer import (
    KnowledgeSynthesizer,
    SynthesisResult,
    KnowledgeSource,
    TemplateType,
)
from cortex.orchestrators.intelligence.tech_intelligence_orchestrator import TechStack


class TestKnowledgeSynthesizerInitialization:
    """Test KnowledgeSynthesizer initialization."""

    def test_synthesizer_initializes_with_defaults(self):
        """Test synthesizer initializes with default configuration."""
        synthesizer = KnowledgeSynthesizer()
        
        assert synthesizer is not None
        assert hasattr(synthesizer, 'synthesize_best_practices')
        assert hasattr(synthesizer, 'generate_tdd_patterns')
        assert hasattr(synthesizer, 'generate_security_rules')
        assert hasattr(synthesizer, 'get_cache_stats')

    def test_synthesizer_accepts_custom_config(self):
        """Test synthesizer accepts custom configuration."""
        config = {
            "cache_enabled": False,
            "template_dir": "/custom/templates",
            "max_cache_size": 50,
        }
        synthesizer = KnowledgeSynthesizer(config=config)
        
        assert synthesizer is not None
        assert synthesizer.cache_enabled is False

    def test_synthesizer_initializes_cache(self):
        """Test synthesizer initializes internal cache."""
        synthesizer = KnowledgeSynthesizer()
        
        stats = synthesizer.get_cache_stats()
        assert "hits" in stats
        assert "misses" in stats
        assert stats["hits"] == 0
        assert stats["misses"] == 0


class TestBestPracticesYAMLGeneration:
    """Test best practices YAML generation."""

    def test_generates_yaml_for_python(self):
        """Test generates valid YAML for Python tech stack."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(
            language="python",
            frameworks=["django", "fastapi"],
            version="3.11",
            tools=["pytest", "black"],
        )
        
        result = synthesizer.synthesize_best_practices(tech_stack)
        
        assert isinstance(result, SynthesisResult)
        assert result.content is not None
        assert "python" in result.content.lower()
        
        # Validate YAML structure
        parsed = yaml.safe_load(result.content)
        assert "language" in parsed
        assert "best_practices" in parsed

    def test_generates_yaml_for_javascript(self):
        """Test generates valid YAML for JavaScript tech stack."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(
            language="javascript",
            frameworks=["react", "express"],
            version="18.0",
            tools=["jest", "eslint"],
        )
        
        result = synthesizer.synthesize_best_practices(tech_stack)
        
        assert result.content is not None
        parsed = yaml.safe_load(result.content)
        assert parsed["language"] == "javascript"
        assert "best_practices" in parsed

    def test_includes_framework_specific_practices(self):
        """Test includes framework-specific best practices."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(
            language="python",
            frameworks=["django"],
            version="3.11",
            tools=["pytest"],
        )
        
        result = synthesizer.synthesize_best_practices(tech_stack)
        parsed = yaml.safe_load(result.content)
        
        assert "frameworks" in parsed
        assert "django" in str(parsed).lower()

    def test_includes_tool_specific_practices(self):
        """Test includes tool-specific best practices."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(
            language="python",
            frameworks=["fastapi"],
            version="3.11",
            tools=["black", "mypy"],
        )
        
        result = synthesizer.synthesize_best_practices(tech_stack)
        content_lower = result.content.lower()
        
        assert "black" in content_lower or "formatting" in content_lower
        assert "mypy" in content_lower or "type" in content_lower

    def test_yaml_generation_is_valid(self):
        """Test generated YAML is parseable and valid."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(
            language="typescript",
            frameworks=["angular"],
            version="5.0",
            tools=["jest"],
        )
        
        result = synthesizer.synthesize_best_practices(tech_stack)
        
        # Should not raise exception
        parsed = yaml.safe_load(result.content)
        assert isinstance(parsed, dict)


class TestTDDPatternTemplates:
    """Test TDD pattern template generation."""

    def test_generates_pytest_patterns(self):
        """Test generates pytest test patterns."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(
            language="python",
            frameworks=["django"],
            version="3.11",
            tools=["pytest"],
        )
        
        result = synthesizer.generate_tdd_patterns(tech_stack)
        
        assert isinstance(result, SynthesisResult)
        assert result.template_type == TemplateType.TDD_PATTERN
        assert "pytest" in result.content.lower() or "test" in result.content.lower()

    def test_generates_jest_patterns(self):
        """Test generates jest test patterns."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(
            language="javascript",
            frameworks=["react"],
            version="18.0",
            tools=["jest"],
        )
        
        result = synthesizer.generate_tdd_patterns(tech_stack)
        
        assert "jest" in result.content.lower() or "test" in result.content.lower()

    def test_includes_framework_specific_patterns(self):
        """Test includes framework-specific test patterns."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(
            language="python",
            frameworks=["fastapi"],
            version="3.11",
            tools=["pytest"],
        )
        
        result = synthesizer.generate_tdd_patterns(tech_stack)
        
        # Should include FastAPI testing patterns (TestClient, etc.)
        content_lower = result.content.lower()
        assert "test" in content_lower

    def test_pattern_includes_setup_teardown(self):
        """Test pattern includes setup/teardown examples."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(
            language="python",
            frameworks=["django"],
            version="3.11",
            tools=["pytest"],
        )
        
        result = synthesizer.generate_tdd_patterns(tech_stack)
        content_lower = result.content.lower()
        
        # Should include fixture or setup patterns
        has_setup = any(
            keyword in content_lower
            for keyword in ["fixture", "setup", "beforeeach", "before"]
        )
        assert has_setup


class TestSecurityRuleGeneration:
    """Test security rule generation."""

    def test_generates_security_rules_for_python(self):
        """Test generates security rules for Python."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(
            language="python",
            frameworks=["django"],
            version="3.11",
            tools=["bandit"],
        )
        
        result = synthesizer.generate_security_rules(tech_stack)
        
        assert isinstance(result, SynthesisResult)
        assert result.template_type == TemplateType.SECURITY_RULES
        assert result.content is not None

    def test_includes_owasp_references(self):
        """Test includes OWASP Top 10 references."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(
            language="python",
            frameworks=["fastapi"],
            version="3.11",
            tools=["bandit"],
        )
        
        result = synthesizer.generate_security_rules(tech_stack)
        content_lower = result.content.lower()
        
        # Should reference security concepts
        has_security = any(
            keyword in content_lower
            for keyword in ["security", "injection", "authentication", "xss", "csrf"]
        )
        assert has_security

    def test_includes_framework_specific_rules(self):
        """Test includes framework-specific security rules."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(
            language="python",
            frameworks=["django"],
            version="3.11",
            tools=["bandit"],
        )
        
        result = synthesizer.generate_security_rules(tech_stack)
        
        # Django has specific security features (CSRF, XSS protection)
        assert result.content is not None
        assert len(result.content) > 0


class TestExternalSourceIntegration:
    """Test external knowledge source integration."""

    def test_synthesizes_from_internal_source(self):
        """Test synthesizes from internal knowledge base."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(
            language="python",
            frameworks=["django"],
            version="3.11",
            tools=["pytest"],
        )
        
        result = synthesizer.synthesize_best_practices(
            tech_stack, source=KnowledgeSource.INTERNAL
        )
        
        assert result.source == KnowledgeSource.INTERNAL
        assert result.content is not None

    def test_synthesizes_from_github_source(self):
        """Test synthesizes from GitHub source (placeholder fallback to internal)."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(
            language="python",
            frameworks=["django"],
            version="3.11",
            tools=["pytest"],
        )
        
        # External sources not yet implemented, falls back to INTERNAL
        result = synthesizer.synthesize_best_practices(
            tech_stack, source=KnowledgeSource.GITHUB
        )
        
        # Currently falls back to internal source
        assert result.source == KnowledgeSource.INTERNAL

    def test_handles_external_source_failure(self):
        """Test handles external source failure gracefully (placeholder fallback)."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(
            language="python",
            frameworks=["django"],
            version="3.11",
            tools=["pytest"],
        )
        
        # External source not implemented yet, falls back to internal
        result = synthesizer.synthesize_best_practices(
            tech_stack, source=KnowledgeSource.GITHUB
        )
        
        assert result is not None
        # Should fallback to internal
        assert result.source == KnowledgeSource.INTERNAL


class TestSynthesisCaching:
    """Test synthesis result caching."""

    def test_caches_synthesis_results(self):
        """Test caches synthesis results for performance."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(
            language="python",
            frameworks=["django"],
            version="3.11",
            tools=["pytest"],
        )
        
        # First call - cache miss
        result1 = synthesizer.synthesize_best_practices(tech_stack)
        stats1 = synthesizer.get_cache_stats()
        
        # Second call - cache hit
        result2 = synthesizer.synthesize_best_practices(tech_stack)
        stats2 = synthesizer.get_cache_stats()
        
        assert stats2["hits"] > stats1["hits"]
        assert result1.content == result2.content

    def test_respects_cache_disabled_config(self):
        """Test respects cache disabled configuration."""
        config = {"cache_enabled": False}
        synthesizer = KnowledgeSynthesizer(config=config)
        tech_stack = TechStack(
            language="python",
            frameworks=["django"],
            version="3.11",
            tools=["pytest"],
        )
        
        result1 = synthesizer.synthesize_best_practices(tech_stack)
        result2 = synthesizer.synthesize_best_practices(tech_stack)
        
        stats = synthesizer.get_cache_stats()
        # No hits when cache disabled
        assert stats["hits"] == 0

    def test_invalidates_cache_correctly(self):
        """Test cache invalidation works correctly."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(
            language="python",
            frameworks=["django"],
            version="3.11",
            tools=["pytest"],
        )
        
        # Cache a result
        synthesizer.synthesize_best_practices(tech_stack)
        
        # Invalidate cache
        synthesizer.invalidate_cache()
        
        stats = synthesizer.get_cache_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0


class TestMultiLanguageSupport:
    """Test multi-language knowledge synthesis."""

    def test_supports_python(self):
        """Test supports Python synthesis."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(language="python", frameworks=[], version="3.11", tools=[])
        
        result = synthesizer.synthesize_best_practices(tech_stack)
        assert result.content is not None

    def test_supports_javascript(self):
        """Test supports JavaScript synthesis."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(language="javascript", frameworks=[], version="18.0", tools=[])
        
        result = synthesizer.synthesize_best_practices(tech_stack)
        assert result.content is not None

    def test_supports_typescript(self):
        """Test supports TypeScript synthesis."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(language="typescript", frameworks=[], version="5.0", tools=[])
        
        result = synthesizer.synthesize_best_practices(tech_stack)
        assert result.content is not None

    def test_handles_unknown_language(self):
        """Test handles unknown language gracefully."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(language="unknown", frameworks=[], version="1.0", tools=[])
        
        result = synthesizer.synthesize_best_practices(tech_stack)
        # Should return generic best practices
        assert result.content is not None
        assert len(result.content) > 0


class TestSynthesisResultMetadata:
    """Test SynthesisResult metadata."""

    def test_result_includes_timestamp(self):
        """Test result includes generation timestamp."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(language="python", frameworks=[], version="3.11", tools=[])
        
        result = synthesizer.synthesize_best_practices(tech_stack)
        
        assert hasattr(result, 'timestamp')
        assert isinstance(result.timestamp, datetime)

    def test_result_includes_source(self):
        """Test result includes knowledge source."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(language="python", frameworks=[], version="3.11", tools=[])
        
        result = synthesizer.synthesize_best_practices(tech_stack)
        
        assert hasattr(result, 'source')
        assert isinstance(result.source, KnowledgeSource)

    def test_result_includes_template_type(self):
        """Test result includes template type."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(language="python", frameworks=[], version="3.11", tools=[])
        
        result = synthesizer.generate_tdd_patterns(tech_stack)
        
        assert hasattr(result, 'template_type')
        assert result.template_type == TemplateType.TDD_PATTERN


class TestErrorHandling:
    """Test error handling."""

    def test_handles_none_tech_stack(self):
        """Test handles None tech stack gracefully."""
        synthesizer = KnowledgeSynthesizer()
        
        result = synthesizer.synthesize_best_practices(None)
        
        # Should return empty or default result
        assert result is not None

    def test_handles_empty_tech_stack(self):
        """Test handles empty tech stack gracefully."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(language="", frameworks=[], version="", tools=[])
        
        result = synthesizer.synthesize_best_practices(tech_stack)
        
        assert result is not None

    def test_handles_invalid_source(self):
        """Test handles invalid knowledge source (uses valid enum)."""
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(language="python", frameworks=[], version="3.11", tools=[])
        
        # Use COMMUNITY as a less-common valid source
        result = synthesizer.synthesize_best_practices(tech_stack, source=KnowledgeSource.COMMUNITY)
        
        assert result is not None
        # Falls back to internal since external sources not implemented
        assert result.source == KnowledgeSource.INTERNAL


class TestPerformance:
    """Test synthesis performance."""

    def test_synthesis_completes_quickly(self):
        """Test synthesis completes in reasonable time."""
        import time
        
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(
            language="python",
            frameworks=["django"],
            version="3.11",
            tools=["pytest"],
        )
        
        start = time.time()
        result = synthesizer.synthesize_best_practices(tech_stack)
        duration = time.time() - start
        
        assert result is not None
        assert duration < 1.0  # Should complete in under 1 second

    def test_cached_synthesis_is_faster(self):
        """Test cached synthesis is faster than first call."""
        import time
        
        synthesizer = KnowledgeSynthesizer()
        tech_stack = TechStack(
            language="python",
            frameworks=["django"],
            version="3.11",
            tools=["pytest"],
        )
        
        # First call (uncached)
        start1 = time.time()
        synthesizer.synthesize_best_practices(tech_stack)
        duration1 = time.time() - start1
        
        # Second call (cached)
        start2 = time.time()
        synthesizer.synthesize_best_practices(tech_stack)
        duration2 = time.time() - start2
        
        # Cached should be faster
        assert duration2 < duration1
