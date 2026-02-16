"""
Tests for semantic response blocks (neurocognitive content architecture).

Authority: ENH-089 | HIGH-LEVEL BRAIN TERMINOLOGY
- Perception: Block discovery and loading from cortex_brain
- Reasoning: Block composition validation and anti-duplication
- Action: Block rendering and personality consistency
"""

import pytest
from pathlib import Path
import yaml
from typing import Dict, List, Set


class TestBlockPerception:
    """Perception layer: Discover and load semantic blocks from registry."""

    def test_load_content_blocks_from_registry(self):
        """Verify all 7 blocks load from registry without errors."""
        blocks_path = (
            Path(__file__).parent.parent.parent
            / "cortex-registry/_cortex-master/core/templates/content-blocks.yaml"
        )
        assert blocks_path.exists(), f"Registry not found: {blocks_path}"

        with open(blocks_path) as f:
            registry = yaml.safe_load(f)

        assert "blocks" in registry, "Registry missing 'blocks' section"
        blocks = registry["blocks"]

        # Verify all 7 core blocks present
        required_blocks = {
            "intro",
            "capabilities",
            "lens",
            "orchestrators",
            "tutorial",
            "onboarding",
            "next_steps",
        }
        loaded_blocks = set(blocks.keys())
        assert required_blocks == loaded_blocks, (
            f"Missing blocks: {required_blocks - loaded_blocks}"
        )

    def test_block_metadata_completeness(self):
        """Verify each block has required metadata."""
        blocks_path = (
            Path(__file__).parent.parent.parent
            / "cortex-registry/_cortex-master/core/templates/content-blocks.yaml"
        )
        with open(blocks_path) as f:
            registry = yaml.safe_load(f)

        blocks = registry["blocks"]

        required_fields = {"id", "name", "length_words", "purpose"}

        for block_name, block_data in blocks.items():
            for field in required_fields:
                assert (
                    field in block_data
                ), f"Block '{block_name}' missing field: {field}"

    def test_block_content_templates_present(self):
        """Verify each block has content_template defined."""
        blocks_path = (
            Path(__file__).parent.parent.parent
            / "cortex-registry/_cortex-master/core/templates/content-blocks.yaml"
        )
        with open(blocks_path) as f:
            registry = yaml.safe_load(f)

        blocks = registry["blocks"]

        for block_name, block_data in blocks.items():
            assert (
                "content_template" in block_data
            ), f"Block '{block_name}' missing content_template"
            assert (
                isinstance(block_data["content_template"], str)
                and len(block_data["content_template"]) > 0
            ), f"Block '{block_name}' has empty content_template"


class TestBlockReasoning:
    """Reasoning layer: Validate block composition and anti-duplication rules."""

    def test_assembly_rules_defined(self):
        """Verify assembly rules cover key scenarios."""
        blocks_path = (
            Path(__file__).parent.parent.parent
            / "cortex-registry/_cortex-master/core/templates/content-blocks.yaml"
        )
        with open(blocks_path) as f:
            registry = yaml.safe_load(f)

        assert "assembly_rules" in registry, "Registry missing assembly_rules"
        rules = registry["assembly_rules"]

        required_scenarios = {
            "first_time_user",
            "query_capabilities",
            "query_lens",
            "autonomous_execution",
        }
        defined_scenarios = set(rules.keys())

        # At least these scenarios required
        assert required_scenarios.issubset(
            defined_scenarios
        ), f"Missing scenarios: {required_scenarios - defined_scenarios}"

    def test_composition_validation_rules_enabled(self):
        """Verify anti-duplication validation rules are enabled."""
        blocks_path = (
            Path(__file__).parent.parent.parent
            / "cortex-registry/_cortex-master/core/templates/content-blocks.yaml"
        )
        with open(blocks_path) as f:
            registry = yaml.safe_load(f)

        assert "validation" in registry, "Registry missing validation section"
        validation = registry["validation"]

        required_checks = {
            "no_duplicate_headers",
            "no_repeated_content",
            "max_total_length",
        }

        for check in required_checks:
            assert check in validation, f"Missing validation check: {check}"
            assert (
                validation[check].get("enabled") is True
            ), f"Validation check '{check}' not enabled"

    def test_block_compatibility_matrix(self):
        """Verify compatibility rules prevent problematic pairings."""
        blocks_path = (
            Path(__file__).parent.parent.parent
            / "cortex-registry/_cortex-master/core/templates/content-blocks.yaml"
        )
        with open(blocks_path) as f:
            registry = yaml.safe_load(f)

        assert "compatibility" in registry, "Registry missing compatibility section"
        compat = registry["compatibility"]

        # Verify key problematic pairings are marked as avoid_with
        assert "lens" in compat["intro"]["avoid_with"], (
            "INTRO should avoid LENS (too much info)"
        )
        assert "tutorial" in compat["lens"]["avoid_with"], (
            "LENS should avoid TUTORIAL (different focus)"
        )

    def test_next_steps_appears_once_rule(self):
        """Verify NEXT-STEPS appears only once in assembled responses."""
        blocks_path = (
            Path(__file__).parent.parent.parent
            / "cortex-registry/_cortex-master/core/templates/content-blocks.yaml"
        )
        with open(blocks_path) as f:
            registry = yaml.safe_load(f)

        validation = registry["validation"]

        footer_rule = validation["footer_once"]
        assert (
            footer_rule["enabled"] is True
        ), "NEXT-STEPS once rule not enabled"

    def test_max_word_count_enforcement(self):
        """Verify max total word count is set and reasonable."""
        blocks_path = (
            Path(__file__).parent.parent.parent
            / "cortex-registry/_cortex-master/core/templates/content-blocks.yaml"
        )
        with open(blocks_path) as f:
            registry = yaml.safe_load(f)

        validation = registry["validation"]
        max_check = validation["max_total_length"]

        assert max_check["enabled"] is True, "Max word count check not enabled"
        assert max_check["words"] == 800, "Max should be 800 words"


class TestBlockAction:
    """Action layer: Verify rendering and personality consistency."""

    def test_personality_guidelines_defined(self):
        """Verify personality consistency guardrails are documented."""
        blocks_path = (
            Path(__file__).parent.parent.parent
            / "cortex-registry/_cortex-master/core/templates/content-blocks.yaml"
        )
        with open(blocks_path) as f:
            registry = yaml.safe_load(f)

        # Personality should be enforced across all blocks
        blocks = registry["blocks"]

        for block_name, block_data in blocks.items():
            # Each block should have usage rules or format guidelines
            assert (
                "usage_rules" in block_data or "format" in block_data
            ), f"Block '{block_name}' missing personality/format rules"

    def test_emoji_consistency_across_blocks(self):
        """Verify emoji headers are consistent and non-conflicting."""
        blocks_path = (
            Path(__file__).parent.parent.parent
            / "cortex-registry/_cortex-master/core/templates/content-blocks.yaml"
        )
        with open(blocks_path) as f:
            registry = yaml.safe_load(f)

        blocks = registry["blocks"]
        emoji_map = {}

        for block_name, block_data in blocks.items():
            if "format" in block_data and "icons" in block_data["format"]:
                icons = block_data["format"]["icons"]
                # Extract emoji (rough pattern match)
                if any(
                    char in icons
                    for char in "🧠⚡🔍🎼🚀⚙️🎯"
                ):
                    emoji_map[block_name] = icons

        # Verify we have emoji defined for visual consistency
        assert len(emoji_map) >= 5, "Not enough emoji defined across blocks"

    def test_orchestrator_metadata_links(self):
        """Verify blocks reference orchestrators correctly."""
        blocks_path = (
            Path(__file__).parent.parent.parent
            / "cortex-registry/_cortex-master/core/templates/content-blocks.yaml"
        )
        with open(blocks_path) as f:
            registry = yaml.safe_load(f)

        blocks = registry["blocks"]

        # Orchestrators block should have orchestrator registry
        orch_block = blocks.get("orchestrators")
        assert orch_block is not None, "ORCHESTRATORS block not found"

        assert (
            "orchestrators_registry" in orch_block
        ), "ORCHESTRATORS block missing orchestrators_registry"

        orch_registry = orch_block["orchestrators_registry"]
        assert (
            "core" in orch_registry and "domain" in orch_registry
        ), "Orchestrator registry missing core/domain tiers"

    def test_assembly_word_count_accuracy(self):
        """Verify assembly rules have realistic word counts."""
        blocks_path = (
            Path(__file__).parent.parent.parent
            / "cortex-registry/_cortex-master/core/templates/content-blocks.yaml"
        )
        with open(blocks_path) as f:
            registry = yaml.safe_load(f)

        assembly_rules = registry["assembly_rules"]

        # Sample rule: first_time_user
        first_user_rule = assembly_rules.get("first_time_user")
        assert first_user_rule is not None, "first_time_user assembly rule not found"

        assert "total_words" in first_user_rule, "Assembly rule missing word count"
        word_count = first_user_rule["total_words"]

        # Rough validation: should be under 1000 (sum of block word counts)
        assert 400 < word_count < 900, (
            f"Word count unrealistic: {word_count}"
        )


class TestBlockIntegration:
    """Integration tests: Full block loading and assembly."""

    def test_all_blocks_load_without_yaml_errors(self):
        """Verify registry YAML is syntactically valid."""
        blocks_path = (
            Path(__file__).parent.parent.parent
            / "cortex-registry/_cortex-master/core/templates/content-blocks.yaml"
        )

        try:
            with open(blocks_path) as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"YAML syntax error: {e}")

    def test_block_ids_are_unique(self):
        """Verify each block has unique ID."""
        blocks_path = (
            Path(__file__).parent.parent.parent
            / "cortex-registry/_cortex-master/core/templates/content-blocks.yaml"
        )
        with open(blocks_path) as f:
            registry = yaml.safe_load(f)

        blocks = registry["blocks"]
        ids: List[str] = []

        for block_name, block_data in blocks.items():
            block_id = block_data.get("id")
            assert block_id is not None, f"Block '{block_name}' missing id"
            ids.append(block_id)

        assert len(ids) == len(
            set(ids)
        ), f"Duplicate block IDs found: {[id for id in ids if ids.count(id) > 1]}"

    def test_assembly_rules_reference_valid_blocks(self):
        """Verify assembly rules only reference blocks that exist."""
        blocks_path = (
            Path(__file__).parent.parent.parent
            / "cortex-registry/_cortex-master/core/templates/content-blocks.yaml"
        )
        with open(blocks_path) as f:
            registry = yaml.safe_load(f)

        blocks = registry["blocks"]
        valid_block_names = set(blocks.keys())

        assembly_rules = registry["assembly_rules"]

        for rule_name, rule_data in assembly_rules.items():
            if "blocks" in rule_data and rule_data["blocks"]:
                for block_ref in rule_data["blocks"]:
                    assert (
                        block_ref in valid_block_names
                    ), f"Assembly rule '{rule_name}' references undefined block: {block_ref}"

    def test_usage_stats_tracking_enabled(self):
        """Verify usage statistics tracking is configured."""
        blocks_path = (
            Path(__file__).parent.parent.parent
            / "cortex-registry/_cortex-master/core/templates/content-blocks.yaml"
        )
        with open(blocks_path) as f:
            registry = yaml.safe_load(f)

        assert "usage_stats" in registry, "Registry missing usage_stats section"
        stats = registry["usage_stats"]

        assert stats.get("enabled") is True, "Usage stats not enabled"
        assert "track" in stats, "Usage stats missing track list"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
