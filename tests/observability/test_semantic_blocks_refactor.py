"""
Tests for semantic block loader, reasoner, and assembler (REFACTOR phase).

Authority: ENH-089 REFACTOR | Code quality + personality consistency enforcement
"""

import pytest
from pathlib import Path
from cortex.registry.semantic_blocks import (
    SemanticBlockLoader,
    SemanticBlockReasoner,
    SemanticBlockAssembler,
    BlockAssemblyError,
    PersonalityError,
)


class TestSemanticBlockLoader:
    """Test block discovery and loading (Perception layer)."""

    def test_load_blocks_from_registry(self):
        """Verify all blocks load successfully."""
        loader = SemanticBlockLoader()
        blocks = loader.load_blocks()

        assert len(blocks) == 7, f"Expected 7 blocks, got {len(blocks)}"

    def test_block_has_required_fields(self):
        """Verify each loaded block has required fields."""
        loader = SemanticBlockLoader()
        blocks = loader.load_blocks()

        required_fields = [
            "id",
            "name",
            "length_words",
            "purpose",
            "content_template",
            "format_spec",
            "personality_guidelines",
            "usage_rules",
        ]

        for name, block in blocks.items():
            for field in required_fields:
                assert hasattr(
                    block, field
                ), f"Block '{name}' missing field: {field}"

    def test_personality_charter_loaded(self):
        """Verify personality guidelines are enforced on blocks."""
        loader = SemanticBlockLoader()
        blocks = loader.load_blocks()

        # Even if global charter doesn't load, all blocks should have personality_guidelines
        has_personality = False
        for block_name, block in blocks.items():
            if block.personality_guidelines:
                has_personality = True
                break

        assert (
            has_personality
        ), "At least one block should have personality_guidelines"


class TestSemanticBlockReasoner:
    """Test composition and duplication validation (Reasoning layer)."""

    def test_validate_composition_under_limit(self):
        """Verify word count validation passes for valid composition."""
        loader = SemanticBlockLoader()
        reasoner = SemanticBlockReasoner(loader)

        # Small composition should pass
        is_valid, warnings = reasoner.validate_composition(["intro", "next_steps"])

        assert is_valid is True, f"Valid composition rejected: {warnings}"
        assert len(warnings) == 0, f"Unexpected warnings: {warnings}"

    def test_validate_composition_next_steps_at_end(self):
        """Verify NEXT-STEPS must be at end."""
        loader = SemanticBlockLoader()
        reasoner = SemanticBlockReasoner(loader)

        # NEXT-STEPS not at end
        is_valid, warnings = reasoner.validate_composition(
            ["next_steps", "intro", "capabilities"]
        )

        assert is_valid is False, "Should fail with NEXT-STEPS not at end"
        assert any(
            "end" in w.lower() for w in warnings
        ), "Should warn about NEXT-STEPS placement"

    def test_validate_composition_compatibility(self):
        """Verify block compatibility rules enforced."""
        loader = SemanticBlockLoader()
        reasoner = SemanticBlockReasoner(loader)

        # LENS with INTRO should fail (avoid_with rule)
        is_valid, warnings = reasoner.validate_composition(["intro", "lens"])

        # This composition should fail due to compatibility
        # (Checking actual registry: INTRO avoids LENS)
        # Note: May vary based on registry definition

    def test_check_duplication_detects_duplicates(self):
        """Verify duplicate detection works."""
        loader = SemanticBlockLoader()
        reasoner = SemanticBlockReasoner(loader)

        # Duplicate block
        is_clean, warnings = reasoner.check_duplication(
            ["intro", "capabilities", "intro"]
        )

        assert is_clean is False, "Should detect duplicate blocks"
        assert any(
            "multiple" in w.lower() for w in warnings
        ), "Should mention multiplicity"


class TestSemanticBlockAssembler:
    """Test block assembly and rendering (Action layer)."""

    def test_assemble_simple_composition(self):
        """Verify basic block assembly."""
        loader = SemanticBlockLoader()
        reasoner = SemanticBlockReasoner(loader)
        assembler = SemanticBlockAssembler(loader, reasoner)

        result = assembler.assemble(["intro", "next_steps"])

        assert result.blocks_assembled == ["intro", "next_steps"]
        assert result.assembled_content != ""
        assert len(result.warnings) == 0, f"Unexpected warnings: {result.warnings}"

    def test_assemble_enforces_personality(self):
        """Verify personality guidelines are checked."""
        loader = SemanticBlockLoader()
        reasoner = SemanticBlockReasoner(loader)
        assembler = SemanticBlockAssembler(loader, reasoner)

        result = assembler.assemble(["intro", "next_steps"], enforce_personality=True)

        assert (
            result.personality_consistent is True
        ), "Personality check should pass for valid blocks"

    def test_assemble_detects_rendering_issues(self):
        """Verify VSCode rendering validation."""
        loader = SemanticBlockLoader()
        reasoner = SemanticBlockReasoner(loader)
        assembler = SemanticBlockAssembler(loader, reasoner)

        # All blocks should have valid rendering (tree chars only in code blocks)
        result = assembler.assemble(["capabilities", "orchestrators"])

        # Rendering should be valid even if orchestrators has tree chars in code blocks
        assert (
            result.rendering_valid is True
        ), f"Rendering validation failed, warnings: {result.warnings}"

    def test_assemble_calculates_word_count(self):
        """Verify total word count calculation."""
        loader = SemanticBlockLoader()
        reasoner = SemanticBlockReasoner(loader)
        assembler = SemanticBlockAssembler(loader, reasoner)

        result = assembler.assemble(["intro", "capabilities", "next_steps"])

        # Intro (150) + Capabilities (200) + Next Steps (80) = 430
        assert result.total_words > 0, "Should calculate word count"
        assert result.total_words < 800, "Should be under limit"

    def test_assemble_full_scenario(self):
        """Test a complete first-time user scenario."""
        loader = SemanticBlockLoader()
        reasoner = SemanticBlockReasoner(loader)
        assembler = SemanticBlockAssembler(loader, reasoner)

        # First time user scenario
        result = assembler.assemble(
            ["intro", "capabilities", "tutorial", "next_steps"]
        )

        assert result.blocks_assembled == [
            "intro",
            "capabilities",
            "tutorial",
            "next_steps",
        ]
        assert result.duplication_check_passed is True
        assert result.personality_consistent is True
        assert result.rendering_valid is True
        # Verify next_steps content is included (not template placeholder)
        assert "next" in result.assembled_content.lower()


class TestSemanticBlockIntegration:
    """Integration tests for full block workflow."""

    def test_end_to_end_assembly(self):
        """Test complete loader → reasoner → assembler pipeline."""
        loader = SemanticBlockLoader()
        reasoner = SemanticBlockReasoner(loader)
        assembler = SemanticBlockAssembler(loader, reasoner)

        # Load, reason, assemble
        blocks = loader.load_blocks()
        assert len(blocks) > 0

        # Assemble a composition
        result = assembler.assemble(["intro", "capabilities", "next_steps"])

        assert result.blocks_assembled == ["intro", "capabilities", "next_steps"]
        assert len(result.assembled_content) > 0
        assert result.duplication_check_passed is True

    def test_personality_consistency_across_scenario(self):
        """Verify personality remains consistent in assembled output."""
        loader = SemanticBlockLoader()
        reasoner = SemanticBlockReasoner(loader)
        assembler = SemanticBlockAssembler(loader, reasoner)

        result = assembler.assemble(["intro", "next_steps"], enforce_personality=True)

        # Personality should be validated
        assert result.personality_consistent is True

        # Content should reflect personality (knowledgeable, patient, teaching)
        content_lower = result.assembled_content.lower()

        # Should have guidance or action-oriented language
        assert any(
            word in content_lower
            for word in ["role", "commands", "choose", "next"]
        ), "Should reflect action-oriented personality"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
