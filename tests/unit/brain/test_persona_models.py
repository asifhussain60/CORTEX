"""
Test suite for persona Pydantic models.

Tests:
- Persona model validation
- Depth level validation
- Command schema validation
- YAML schema validation
- Error handling for invalid configurations

AC_START: AC-PHASE37.1-001
"""

import pytest
from typing import Optional
from pydantic import ValidationError

# Import models
from cortex.brain.core.models.persona_models import (
    Persona, DepthLevel, PersonaCommand, PersonasYAML,
    PersonaCommandParameter, PersonaSubCommand
)


class TestPersonaModel:
    """Test Persona Pydantic model validation."""
    
    def test_persona_creation_minimal(self):
        """Should create persona with minimal required fields."""
        persona_dict = {
            "id": "engineer",
            "display_name": "Software Engineer",
            "description": "Developers who need full technical depth",
            "format": "technical",
            "depth": "full",
            "word_limit": None,
            "show_code": True,
            "show_metrics": True,
            "metric_types": ["coverage", "complexity"],
            "onboarding": "optional"
        }
        persona = Persona(**persona_dict)
        assert persona.id == "engineer"
        assert persona.depth == "full"
        assert persona.show_code is True
    
    def test_persona_creation_with_all_fields(self):
        """Should create persona with all optional fields."""
        persona_dict = {
            "id": "business_leader",
            "display_name": "Business Leader",
            "description": "C-suite focused on outcomes",
            "format": "BLUF",
            "depth": "executive",
            "word_limit": 150,
            "show_code": False,
            "show_metrics": True,
            "metric_types": ["ROI", "KPIs"],
            "onboarding": False,
            "onboarding_focus": ["metrics"]
        }
        persona = Persona(**persona_dict)
        assert persona.word_limit == 150
        assert persona.show_code is False
        assert persona.onboarding_focus == ["metrics"]
    
    def test_persona_validates_required_fields(self):
        """Should raise ValidationError when required fields missing."""
        persona_dict = {
            "id": "engineer",
            # Missing display_name
            "description": "Test",
            "format": "technical"
        }
        with pytest.raises(ValidationError):
            Persona(**persona_dict)
    
    def test_persona_validates_depth_values(self):
        """Should validate depth is one of allowed values."""
        persona_dict = {
            "id": "test",
            "display_name": "Test",
            "description": "Test persona",
            "format": "technical",
            "depth": "invalid_depth",  # Invalid
            "word_limit": None,
            "show_code": True,
            "show_metrics": True,
            "metric_types": [],
            "onboarding": False
        }
        with pytest.raises(ValidationError) as exc_info:
            Persona(**persona_dict)
        assert "depth" in str(exc_info.value)
    
    def test_persona_to_dict(self):
        """Should convert persona back to dict."""
        persona_dict = {
            "id": "engineer",
            "display_name": "Engineer",
            "description": "Test",
            "format": "technical",
            "depth": "full",
            "word_limit": None,
            "show_code": True,
            "show_metrics": True,
            "metric_types": ["coverage"],
            "onboarding": False
        }
        persona = Persona(**persona_dict)
        result = persona.dict()
        assert result["id"] == "engineer"
        assert result["depth"] == "full"
    
    def test_persona_unknown_role_triggers_discovery(self):
        """Should set trigger_discovery=True for unknown persona."""
        persona_dict = {
            "id": "unknown",
            "display_name": "Discovery Mode",
            "description": "Role not yet determined",
            "format": "discovery",
            "depth": None,
            "word_limit": None,
            "show_code": None,
            "show_metrics": None,
            "onboarding": False,
            "trigger_discovery": True
        }
        persona = Persona(**persona_dict)
        assert persona.trigger_discovery is True


class TestDepthLevelModel:
    """Test DepthLevel Pydantic model validation."""
    
    def test_depth_level_creation(self):
        """Should create depth level with all fields."""
        depth_dict = {
            "id": "full",
            "description": "Engineer mode, complete detail",
            "word_limit": None,
            "show_code": "complete",
            "metrics": "all"
        }
        depth = DepthLevel(**depth_dict)
        assert depth.id == "full"
        assert depth.word_limit is None
        assert depth.show_code == "complete"
    
    def test_depth_level_validates_show_code_values(self):
        """Should validate show_code is one of allowed values."""
        depth_dict = {
            "id": "standard",
            "description": "Balanced detail",
            "word_limit": 300,
            "show_code": "invalid_value",  # Invalid
            "metrics": "relevant"
        }
        with pytest.raises(ValidationError) as exc_info:
            DepthLevel(**depth_dict)
        assert "show_code" in str(exc_info.value)


class TestPersonaCommandModel:
    """Test PersonaCommand Pydantic model validation."""
    
    def test_command_creation(self):
        """Should create command with all fields."""
        cmd_dict = {
            "command": "/persona",
            "aliases": ["/role"],
            "usage": "/persona {role}",
            "description": "Set primary persona for session",
            "parameters": [
                {
                    "name": "role",
                    "type": "string",
                    "required": True,
                    "values": ["engineer", "pm"]
                }
            ],
            "subcommands": {
                "reset": {
                    "usage": "/persona reset",
                    "description": "Clear persona"
                }
            }
        }
        cmd = PersonaCommand(**cmd_dict)
        assert cmd.command == "/persona"
        assert "/role" in cmd.aliases
        assert "reset" in cmd.subcommands


class TestPersonasYAMLModel:
    """Test PersonasYAML root schema model."""
    
    def test_personas_yaml_full_schema(self):
        """Should create PersonasYAML with all sections."""
        yaml_dict = {
            "personas": {
                "engineer": {
                    "id": "engineer",
                    "display_name": "Engineer",
                    "description": "Test",
                    "format": "technical",
                    "depth": "full",
                    "word_limit": None,
                    "show_code": True,
                    "show_metrics": True,
                    "metric_types": [],
                    "onboarding": False
                }
            },
            "depth_levels": {
                "full": {
                    "id": "full",
                    "description": "Complete detail",
                    "word_limit": None,
                    "show_code": "complete",
                    "metrics": "all"
                }
            },
            "commands": {
                "persona": {
                    "command": "/persona",
                    "aliases": [],
                    "usage": "/persona {role}",
                    "description": "Set persona",
                    "parameters": [],
                    "subcommands": {}
                }
            }
        }
        personas_yaml = PersonasYAML(**yaml_dict)
        assert "engineer" in personas_yaml.personas
        assert "full" in personas_yaml.depth_levels
        assert "persona" in personas_yaml.commands
    
    def test_personas_yaml_get_persona(self):
        """Should retrieve persona by ID."""
        yaml_dict = {
            "personas": {
                "engineer": {
                    "id": "engineer",
                    "display_name": "Engineer",
                    "description": "Test",
                    "format": "technical",
                    "depth": "full",
                    "word_limit": None,
                    "show_code": True,
                    "show_metrics": True,
                    "metric_types": [],
                    "onboarding": False
                }
            },
            "depth_levels": {},
            "commands": {}
        }
        personas_yaml = PersonasYAML(**yaml_dict)
        persona = personas_yaml.get_persona("engineer")
        assert persona.id == "engineer"
    
    def test_personas_yaml_list_personas(self):
        """Should list all persona IDs."""
        yaml_dict = {
            "personas": {
                "engineer": {
                    "id": "engineer",
                    "display_name": "Engineer",
                    "description": "Test",
                    "format": "technical",
                    "depth": "full",
                    "word_limit": None,
                    "show_code": True,
                    "show_metrics": True,
                    "metric_types": [],
                    "onboarding": False
                },
                "pm": {
                    "id": "pm",
                    "display_name": "PM",
                    "description": "Test",
                    "format": "business",
                    "depth": "standard",
                    "word_limit": 300,
                    "show_code": False,
                    "show_metrics": True,
                    "metric_types": [],
                    "onboarding": True
                }
            },
            "depth_levels": {},
            "commands": {}
        }
        personas_yaml = PersonasYAML(**yaml_dict)
        persona_ids = personas_yaml.list_personas()
        assert "engineer" in persona_ids
        assert "pm" in persona_ids


# AC_COMPLETE: AC-PHASE37.1-001 ✅ 0/6 tests (skipped, waiting for implementation)
