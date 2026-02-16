"""
Tests for PreFlightRequestTransformer (PFRT).

AC_START: AC-PHASE95-001
Description: Pre-Flight Request Transformer - Stage 0 orchestration layer
"""

import pytest
from cortex.orchestrators.interaction.pfrt import PreFlightRequestTransformer


class TestPFRTDistillation:
    """Test request distillation and clarity transformation."""

    @pytest.fixture
    def pfrt(self):
        """Create PFRT instance."""
        return PreFlightRequestTransformer()

    def test_removes_redundant_phrases(self, pfrt):
        """Should eliminate repetitive statements."""
        verbose = (
            "I need to add caching to LENS. But make sure it doesn't break anything. "
            "Also check if caching already exists. If not, add Redis maybe? "
            "Or something else. Just make sure it's fast and doesn't cause bugs."
        )
        result = pfrt.transform(verbose)
        
        assert "But make sure" not in result
        assert "Also check" not in result
        assert "Just make sure" not in result
        assert len(result) < len(verbose) * 0.6  # At least 40% reduction

    def test_preserves_technical_terms(self, pfrt):
        """Should keep domain-specific terminology intact."""
        request = "Add Redis caching to LENS analysis with TTL=300s"
        result = pfrt.transform(request)
        
        assert "Redis" in result
        assert "LENS" in result
        assert "TTL" in result or "300s" in result

    def test_synthesizes_multiple_concerns(self, pfrt):
        """Should merge related concerns into single intent."""
        verbose = (
            "Add caching. Also make sure no existing cache. "
            "Use Redis if possible. Ensure no regression."
        )
        result = pfrt.transform(verbose)
        
        # Should be single-paragraph, not fragmented
        assert "\n\n" not in result
        assert len(result.split(". ")) <= 2  # Max 2 sentences

    def test_extracts_core_intent(self, pfrt):
        """Should identify primary action verb and target."""
        verbose = "Maybe we could add, or perhaps implement, some kind of caching?"
        result = pfrt.transform(verbose)
        
        assert any(verb in result.lower() for verb in ["add", "implement", "create"])
        assert "caching" in result.lower()

    def test_handles_already_clear_requests(self, pfrt):
        """Should not over-process clear, concise requests."""
        clear = "Implement TDD workflow for LENS adapter validation"
        result = pfrt.transform(clear)
        
        # Should be nearly identical (allow minor refinement)
        assert len(result) <= len(clear) * 1.2

    def test_identifies_constraints_and_requirements(self, pfrt):
        """Should extract and preserve requirements."""
        verbose = (
            "Add caching but don't break anything. "
            "Must be MCP-exposed. Check existing implementations first."
        )
        result = pfrt.transform(verbose)
        
        assert any(word in result.lower() for word in ["validation", "check", "verify", "against"])
        assert "mcp" in result.lower() or "exposed" in result.lower()

    def test_normalizes_uncertainty_markers(self, pfrt):
        """Should convert 'maybe', 'perhaps' to decisive language."""
        uncertain = "Maybe add Redis? Or perhaps use another cache? Not sure."
        result = pfrt.transform(uncertain)
        
        assert "maybe" not in result.lower()
        assert "perhaps" not in result.lower()
        assert "not sure" not in result.lower()

    def test_converts_questions_to_statements(self, pfrt):
        """Should transform interrogative to declarative mode."""
        question = "Can we add caching to LENS? Should we use Redis?"
        result = pfrt.transform(question)
        
        # Should be statement, not question
        assert not result.strip().endswith("?")
        assert result[0].isupper()  # Proper sentence case

    def test_detects_anti_patterns(self, pfrt):
        """Should flag requests violating CORTEX principles."""
        anti_pattern = "Skip tests and just add the feature quickly"
        result = pfrt.transform(anti_pattern)
        
        # Should NOT include anti-pattern directives
        assert "skip" not in result.lower()
        # Should inject governance reminder
        assert "tdd" in result.lower() or "test" in result.lower()

    def test_handles_multi_paragraph_input(self, pfrt):
        """Should consolidate multi-paragraph requests."""
        verbose = """
        I need caching for LENS.
        
        Make sure it doesn't break anything.
        
        Also check if it already exists.
        """
        result = pfrt.transform(verbose)
        
        # Should be single paragraph
        assert result.count("\n\n") == 0

    def test_preserves_code_references(self, pfrt):
        """Should keep file paths and code identifiers."""
        request = "Fix bug in cortex/lens/adapters/typescript_adapter.py line 42"
        result = pfrt.transform(request)
        
        assert "cortex/lens/adapters/typescript_adapter.py" in result
        assert "42" in result

    def test_extracts_success_criteria(self, pfrt):
        """Should identify and preserve outcome expectations."""
        request = "Add caching so LENS runs 50% faster without breaking tests"
        result = pfrt.transform(request)
        
        assert "50%" in result or "faster" in result
        assert "test" in result.lower() or "validation" in result.lower()

    def test_handles_empty_input(self, pfrt):
        """Should gracefully handle empty or whitespace-only input."""
        result = pfrt.transform("   \n\n  ")
        assert result == ""

    def test_handles_single_word_input(self, pfrt):
        """Should handle minimal input without crashing."""
        result = pfrt.transform("cache")
        assert len(result) > 0
        assert "cache" in result.lower()

    def test_classification_context_injection(self, pfrt):
        """Should add hints for IntentRouter classification."""
        request = "Add caching to LENS"
        result = pfrt.transform(request, include_hints=True)
        
        # Should have metadata for Stage 2
        assert hasattr(pfrt, 'last_intent_hint')
        assert pfrt.last_intent_hint in ["IMPLEMENT", "ENHANCE", "FEATURE"]

    def test_detects_fix_vs_implement_intent(self, pfrt):
        """Should distinguish between bug fix and new feature."""
        fix_request = "Fix broken caching in LENS"
        impl_request = "Add new caching to LENS"
        
        fix_result = pfrt.transform(fix_request, include_hints=True)
        impl_result = pfrt.transform(impl_request, include_hints=True)
        
        assert "fix" in fix_result.lower() or "resolve" in fix_result.lower()
        assert "add" in impl_result.lower() or "implement" in impl_result.lower()

    def test_token_count_reduction(self, pfrt):
        """Should achieve minimum 40% token reduction on verbose input."""
        verbose = (
            "So I was thinking, maybe we could add some kind of caching layer, "
            "you know, to make LENS faster. But I'm not sure if we already have "
            "caching somewhere. If we do, we should check that first. If not, "
            "then maybe Redis would be good? Or Memcached? I'm not sure. "
            "Just make sure whatever we do doesn't break anything. That's important. "
            "Oh, and it should be MCP-exposed too. Thanks!"
        )
        result = pfrt.transform(verbose)
        
        # Token approximation: word count / 0.75
        verbose_tokens = len(verbose.split()) / 0.75
        result_tokens = len(result.split()) / 0.75
        
        reduction = (verbose_tokens - result_tokens) / verbose_tokens
        assert reduction >= 0.40  # At least 40% reduction

    def test_output_format_is_markdown_friendly(self, pfrt):
        """Should produce output suitable for inline markdown display."""
        request = "Add caching to LENS with validation"
        result = pfrt.transform(request)
        
        # Should be single line or well-formatted paragraph
        assert not result.startswith("#")  # No markdown headers
        assert not result.startswith("-")  # No list items
        assert not result.startswith("|")  # No tables


class TestPFRTIntegration:
    """Test PFRT integration with orchestration pipeline."""

    @pytest.fixture
    def pfrt(self):
        """Create PFRT instance."""
        return PreFlightRequestTransformer()

    def test_stage_0_handoff_to_stage_1(self, pfrt):
        """Should produce output compatible with InteractionOrchestrator."""
        verbose = "Add caching, check existing, use Redis, no regression"
        result = pfrt.transform(verbose)
        
        # Should be valid input for InteractionOrchestrator
        assert isinstance(result, str)
        assert len(result) > 0
        assert len(result) < 500  # Reasonable length for DoR generation


# AC_COMPLETE: AC-PHASE95-001 ✅ 18/18 tests RED phase
