"""
Pydantic models for persona configurations.

Provides typed validation for personas.yaml schema including:
- Persona definitions
- Depth levels
- Commands and subcommands
- Natural language triggers

AC_START: AC-PHASE37.1-003
"""

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, validator


class PersonaCommandParameter(BaseModel):
    """Command parameter definition."""

    name: str
    type: str
    required: bool
    values: Optional[List[str]] = None


class PersonaSubCommand(BaseModel):
    """Subcommand definition."""

    usage: str
    description: str


class PersonaCommand(BaseModel):
    """Command schema with parameters and subcommands."""

    command: str
    aliases: List[str] = Field(default_factory=list)
    usage: str
    description: str
    parameters: List[PersonaCommandParameter] = Field(default_factory=list)
    subcommands: Dict[str, PersonaSubCommand] = Field(default_factory=dict)


class Persona(BaseModel):
    """User persona definition with formatting rules."""

    id: str
    display_name: str
    description: str
    format: str
    depth: Optional[str]
    word_limit: Optional[int]
    show_code: Optional[Union[bool, str]]
    show_metrics: Optional[bool]
    metric_types: List[str] = Field(default_factory=list)
    onboarding: Union[bool, str]
    onboarding_focus: Optional[List[str]] = None
    trigger_discovery: bool = False

    @validator('depth')
    def validate_depth(cls, v):
        """Validate depth is one of allowed values."""
        if v is not None:
            allowed = ["executive", "standard", "detailed", "full"]
            if v not in allowed:
                raise ValueError(
                    f"depth must be one of {allowed}, got: {v}"
                )
        return v

    @validator('show_code')
    def validate_show_code(cls, v):
        """Validate show_code is bool or allowed string."""
        if v is not None and not isinstance(v, bool):
            allowed = ["diagrams", "snippets", "relevant", "complete"]
            if v not in allowed:
                raise ValueError(
                    f"show_code must be bool or one of {allowed}, got: {v}"
                )
        return v


class DepthLevel(BaseModel):
    """Detail level definition."""

    id: str
    description: str
    word_limit: Optional[int]
    show_code: Union[bool, str]
    metrics: str

    @validator('show_code')
    def validate_show_code(cls, v):
        """Validate show_code is bool or allowed string."""
        if not isinstance(v, bool):
            allowed = ["snippets", "relevant", "complete"]
            if v not in allowed:
                raise ValueError(
                    f"show_code must be bool or one of {allowed}, got: {v}"
                )
        return v

    @validator('metrics')
    def validate_metrics(cls, v):
        """Validate metrics level."""
        allowed = ["high_level", "relevant", "full", "all"]
        if v not in allowed:
            raise ValueError(
                f"metrics must be one of {allowed}, got: {v}"
            )
        return v


class NaturalLanguageTrigger(BaseModel):
    """Natural language pattern trigger."""

    pattern: str
    action: str


class NaturalLanguageTriggers(BaseModel):
    """Collection of NL triggers."""

    depth_overrides: List[NaturalLanguageTrigger] = Field(default_factory=list)
    persona_overrides: List[NaturalLanguageTrigger] = Field(default_factory=list)


class PersonasYAML(BaseModel):
    """Root schema model for personas.yaml."""

    personas: Dict[str, Persona]
    depth_levels: Dict[str, DepthLevel]
    commands: Dict[str, PersonaCommand]
    nl_triggers: Optional[NaturalLanguageTriggers] = None

    def get_persona(self, persona_id: str) -> Optional[Persona]:
        """Retrieve persona by ID."""
        return self.personas.get(persona_id)

    def list_personas(self) -> List[str]:
        """List all persona IDs."""
        return list(self.personas.keys())

    def get_depth_level(self, depth_id: str) -> Optional[DepthLevel]:
        """Retrieve depth level by ID."""
        return self.depth_levels.get(depth_id)

    def get_command(self, command_name: str) -> Optional[PersonaCommand]:
        """Retrieve command by name."""
        return self.commands.get(command_name)


# AC_COMPLETE: AC-PHASE37.1-003 ✅ Pydantic models defined with validators
