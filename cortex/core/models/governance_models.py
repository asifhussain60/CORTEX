"""
Pydantic models for governance YAML structures.

Part of ENH-048: Prompt Unbloating System
Provides type-safe models for YAML-based governance files.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EnforcementLevel(str, Enum):
    """Enforcement level for CORE rules."""
    BLOCKED = "BLOCKED"
    WARNING = "WARNING"
    PRE_EXECUTION = "PRE-EXECUTION"
    RUNTIME = "RUNTIME"
    PRINCIPLE = "PRINCIPLE"


class CoreRule(BaseModel):
    """Single CORE rule model."""
    model_config = {'extra': 'allow'}  # Allow extra fields

    id: str
    name: str
    description: str
    enforcement: Optional[str] = None  # YAML uses 'enforcement' not 'enforcement_level'
    rationale: Optional[str] = None  # Optional in YAML
    examples: List[str] = Field(default_factory=list)
    related_rules: List[str] = Field(default_factory=list)
    agent: Optional[str] = None

    @property
    def enforcement_level(self) -> Optional[EnforcementLevel]:
        """Get enforcement level as enum."""
        if self.enforcement:
            try:
                return EnforcementLevel(self.enforcement)
            except ValueError:
                return None
        return None


class CoreRulesYAML(BaseModel):
    """Root model for core-rules.yaml."""
    model_config = {'extra': 'allow'}

    meta: Dict[str, Any]
    core_rules: List[CoreRule]
    special_rules: Optional[List[CoreRule]] = Field(default_factory=list)
    enforcement_levels: Dict[str, Any]  # Can be string or dict


class Priority(str, Enum):
    """Audit check priority levels."""
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class AuditCheck(BaseModel):
    """Single audit check model."""
    model_config = {'extra': 'allow'}

    id: str
    name: str
    description: str
    tool: str
    evidence_required: Optional[bool] = None
    auto_fix: Optional[bool] = None
    severity: Optional[str] = None
    pattern: Optional[str] = None
    analysis_types: Optional[List[str]] = None
    test_pattern: Optional[str] = None
    related_rules: List[str] = Field(default_factory=list)


class PriorityCategory(BaseModel):
    """Priority category with multiple checks."""
    model_config = {'extra': 'allow'}

    name: str
    description: str
    mandatory: Optional[bool] = None
    blocking: Optional[bool] = None
    checks: List[AuditCheck]


class AuditChecklistYAML(BaseModel):
    """Root model for audit-checklist.yaml."""
    model_config = {'extra': 'allow'}

    meta: Dict[str, Any]
    priority_checks: Dict[str, PriorityCategory]  # Changed to use PriorityCategory
    execution_flow: Dict[str, Any]
    tools: Dict[str, Dict[str, Any]]
    evidence_format: Dict[str, Any]
    report_structure: Dict[str, Any]


class ModeDefinition(BaseModel):
    """Single mode definition model."""
    model_config = {'extra': 'allow'}

    name: str
    trigger: str
    description: str
    agent: str
    priority: int
    flow: List[str]
    header_template: Optional[str] = None
    success_criteria: Optional[List[str]] = None
    outputs: Optional[List[str]] = None  # Made optional
    example: Optional[str] = None  # Made optional


class ModesYAML(BaseModel):
    """Root model for modes.yaml."""
    model_config = {'extra': 'allow'}

    meta: Dict[str, Any]
    modes: Dict[str, ModeDefinition]


class ResponseFormatYAML(BaseModel):
    """Root model for response-format.yaml."""
    model_config = {'extra': 'allow'}

    meta: Dict[str, Any]
    header: Dict[str, Any]  # Changed to Any since it has mixed types
    icons: Dict[str, Any]  # Changed to Any since nested structure varies
    structure: Dict[str, Any]
    anti_patterns: Optional[List[Dict[str, str]]] = Field(default_factory=list)  # Made optional
