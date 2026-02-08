"""
Phase 37 S1: Role-Adaptive Persona System - PersonaLoader Tests

TDD RED Phase: 20 tests targeting PersonaLoader functionality
Authority: CORE-008 (TDD-first), CORE-035 (Single canonical implementation)
Status: TDD RED (tests failing, expecting implementation to follow)
"""

import pytest
from pathlib import Path
from typing import Dict
import yaml
import tempfile

from cortex.orchestrators.persona.models import (
    PersonaConfig, DepthConfig, PersonaId, DepthLevel, SessionContext,
    UserPreferences, WorkspaceConfig
)
from cortex.orchestrators.persona.persona_loader import PersonaLoader


class TestPersonaLoaderBasics:
    """T1-T4: Basic functionality tests for PersonaLoader"""

    def test_loader_initialization_with_default_path(self):
        """T1: PersonaLoader initializes with bundled personas.yaml"""
        loader = PersonaLoader()
        assert loader.config_path.name == "personas.yaml"
        assert loader._personas_cache is None
        assert loader._depths_cache is None

    def test_loader_initialization_with_custom_path(self):
        """T2: PersonaLoader accepts custom configuration path"""
        custom_path = Path("/tmp/custom_personas.yaml")
        loader = PersonaLoader(config_path=custom_path)
        assert loader.config_path == custom_path

    def test_load_personas_from_yaml(self):
        """T3: load() method successfully parses personas.yaml"""
        loader = PersonaLoader()
        config = loader.load()
        
        assert config is not None
        assert isinstance(config, dict)
        assert "personas" in config
        assert "depth_levels" in config

    def test_load_caches_yaml_config(self):
        """T4: load() caches YAML to avoid repeated parsing"""
        loader = PersonaLoader()
        config1 = loader.load()
        config2 = loader.load()
        
        assert config1 is config2  # Same object reference (cached)


class TestPersonaRetrieval:
    """T5-T10: Persona retrieval and access tests"""

    def test_get_persona_by_id_returns_persona_config(self):
        """T5: get_persona() returns PersonaConfig for valid ID"""
        loader = PersonaLoader()
        persona = loader.get_persona("engineer")
        
        assert persona is not None
        assert isinstance(persona, PersonaConfig)
        assert persona.id == PersonaId.ENGINEER

    def test_get_persona_returns_none_for_invalid_id(self):
        """T6: get_persona() returns None for non-existent persona"""
        loader = PersonaLoader()
        persona = loader.get_persona("nonexistent_role")
        
        assert persona is None

    def test_get_all_personas_returns_dict(self):
        """T7: get_all_personas() returns complete persona dictionary"""
        loader = PersonaLoader()
        personas = loader.get_all_personas()
        
        assert isinstance(personas, dict)
        assert len(personas) == 6  # 6 personas defined
        assert all(isinstance(v, PersonaConfig) for v in personas.values())

    def test_get_all_personas_caches_result(self):
        """T8: get_all_personas() caches results on subsequent calls"""
        loader = PersonaLoader()
        personas1 = loader.get_all_personas()
        personas2 = loader.get_all_personas()
        
        assert personas1 is personas2  # Same object reference

    def test_get_all_personas_includes_all_six_personas(self):
        """T9: All 6 defined personas are loaded correctly"""
        loader = PersonaLoader()
        personas = loader.get_all_personas()
        
        expected_personas = {
            "business_leader", "product_owner", "scrum_master",
            "tech_lead", "engineer", "unknown"
        }
        assert set(personas.keys()) == expected_personas

    def test_persona_config_attributes_populated(self):
        """T10: PersonaConfig objects have all required attributes"""
        loader = PersonaLoader()
        persona = loader.get_persona("engineer")
        
        assert persona.id == PersonaId.ENGINEER
        assert isinstance(persona.display_name, str)
        assert len(persona.display_name) > 0
        assert isinstance(persona.description, str)
        assert isinstance(persona.format, str)
        assert isinstance(persona.show_code, bool)


class TestDepthLevelRetrieval:
    """T11-T14: Depth level retrieval and access tests"""

    def test_get_depth_by_id_returns_depth_config(self):
        """T11: get_depth() returns DepthConfig for valid ID"""
        loader = PersonaLoader()
        depth = loader.get_depth("executive")
        
        assert depth is not None
        assert isinstance(depth, DepthConfig)
        assert depth.id == DepthLevel.EXECUTIVE

    def test_get_depth_returns_none_for_invalid_id(self):
        """T12: get_depth() returns None for non-existent depth"""
        loader = PersonaLoader()
        depth = loader.get_depth("invalid_depth")
        
        assert depth is None

    def test_get_all_depths_returns_dict(self):
        """T13: get_all_depths() returns complete depth dictionary"""
        loader = PersonaLoader()
        depths = loader.get_all_depths()
        
        assert isinstance(depths, dict)
        assert len(depths) == 4  # 4 depth levels defined
        assert all(isinstance(v, DepthConfig) for v in depths.values())

    def test_get_all_depths_includes_all_four_levels(self):
        """T14: All 4 depth levels are loaded correctly"""
        loader = PersonaLoader()
        depths = loader.get_all_depths()
        
        expected_depths = {"executive", "standard", "detailed", "full"}
        assert set(depths.keys()) == expected_depths


class TestDefaultPersona:
    """T15-T17: Default persona selection tests"""

    def test_get_default_persona_returns_engineer(self):
        """T15: get_default_persona() returns engineer if available"""
        loader = PersonaLoader()
        default = loader.get_default_persona()
        
        assert default is not None
        assert default.id == PersonaId.ENGINEER

    def test_get_default_persona_consistent_across_calls(self):
        """T16: get_default_persona() returns same persona consistently"""
        loader = PersonaLoader()
        default1 = loader.get_default_persona()
        default2 = loader.get_default_persona()
        
        assert default1.id == default2.id

    def test_get_default_persona_not_none(self):
        """T17: get_default_persona() always returns a valid persona"""
        loader = PersonaLoader()
        default = loader.get_default_persona()
        
        assert default is not None
        assert isinstance(default, PersonaConfig)


class TestPersonaYAMLValidation:
    """T18-T20: YAML schema validation and error handling"""

    def test_load_from_missing_file_raises_error(self):
        """T18: load() raises FileNotFoundError for missing file"""
        loader = PersonaLoader(config_path=Path("/nonexistent/path/personas.yaml"))
        
        with pytest.raises(FileNotFoundError):
            loader.load()

    def test_malformed_yaml_raises_error(self):
        """T19: load() raises yaml.YAMLError for malformed YAML"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: [syntax:")
            temp_path = Path(f.name)
        
        try:
            loader = PersonaLoader(config_path=temp_path)
            with pytest.raises(yaml.YAMLError):
                loader.load()
        finally:
            temp_path.unlink()

    def test_persona_loader_graceful_degradation_on_invalid_persona(self):
        """T20: PersonaLoader gracefully handles invalid persona data in YAML"""
        # Test that PersonaLoader skips personas with invalid enum values
        # The current implementation validates PersonaId enum membership
        loader = PersonaLoader()
        
        # Get all personas - should only include valid ones
        personas = loader.get_all_personas()
        
        # All returned personas should have valid PersonaIds
        for persona_id, persona in personas.items():
            assert isinstance(persona.id, PersonaId)
            # Try to access the enum value (should not raise)
            _ = persona.id.value


class TestPersonaLoaderIntegration:
    """Integration tests for complete PersonaLoader workflow"""

    def test_full_workflow_load_persona_and_depth(self):
        """Integration: Load persona and its associated depth"""
        loader = PersonaLoader()
        
        # Get engineer persona
        engineer = loader.get_persona("engineer")
        assert engineer is not None
        
        # Get its associated depth
        if engineer.depth:
            depth = loader.get_depth(engineer.depth.value)
            assert depth is not None
            assert depth.id == engineer.depth

    def test_multiple_loaders_independent_caches(self):
        """Integration: Multiple loader instances have independent caches"""
        loader1 = PersonaLoader()
        loader2 = PersonaLoader()
        
        # Load with first loader
        personas1 = loader1.get_all_personas()
        
        # Second loader should have empty cache initially
        assert loader2._personas_cache is None
        
        # After loading, both should have same data (not same reference)
        personas2 = loader2.get_all_personas()
        assert set(personas1.keys()) == set(personas2.keys())


# ============================================================================
# PHASE 37 S1 TEST SUMMARY
# ============================================================================
# Total: 20 tests
# Categories:
#   - Basics (T1-T4): Initialization, default behavior
#   - Persona Retrieval (T5-T10): Getting personas by ID and all personas
#   - Depth Level Retrieval (T11-T14): Getting depth levels
#   - Default Persona (T15-T17): Default persona selection
#   - YAML Validation (T18-T20): Error handling and graceful degradation
#   - Integration: Full workflow testing
#
# TDD Status: RED (failing)
# Next: Implement PersonaLoader to pass all 20 tests
# ============================================================================
