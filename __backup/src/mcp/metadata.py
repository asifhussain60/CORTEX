"""
Orchestrator Metadata - Type definitions and schemas.

Defines metadata structure for orchestrator registration and discovery.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum


class OrchestratorType(Enum):
    """Orchestrator execution type."""
    AUTONOMOUS = "autonomous"  # Fully autonomous execution
    GUIDED = "guided"  # Step-by-step with user confirmation
    INTERACTIVE = "interactive"  # Real-time user interaction required


class OrchestratorCategory(Enum):
    """Orchestrator functional category."""
    PLANNING = "planning"
    EXECUTION = "execution"
    TESTING = "testing"
    MAINTENANCE = "maintenance"
    VALIDATION = "validation"
    INVESTIGATION = "investigation"
    OPTIMIZATION = "optimization"
    DEPLOYMENT = "deployment"
    INTEGRATION = "integration"  # For ADO, external systems
    ANALYSIS = "analysis"  # For investigation, log analysis
    SECURITY = "security"  # For sanitization, security checks
    WORKFLOW = "workflow"  # For TODO, task orchestration


@dataclass
class OrchestratorMetadata:
    """
    Metadata for orchestrator registration and discovery.

    Attributes:
        id: Unique orchestrator identifier (e.g., "planning_v5")
        name: Human-readable name
        version: Semantic version (e.g., "5.0.0")
        type: Execution type (autonomous/guided/interactive)
        category: Functional category
        description: Brief description
        class_name: Python class name
        module_path: Full module import path
        manifest_path: Path to YAML manifest (optional)
        patterns: Regex patterns for intent matching
        dependencies: List of required orchestrator IDs
        capabilities: List of capability strings
        tags: Additional metadata tags
        enabled: Whether orchestrator is active
    """

    id: str
    name: str
    version: str
    type: OrchestratorType
    category: OrchestratorCategory
    class_name: str
    module_path: str
    description: str = ""
    manifest_path: Optional[str] = None
    patterns: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    tags: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'type': self.type.value,
            'category': self.category.value,
            'class_name': self.class_name,
            'module_path': self.module_path,
            'description': self.description,
            'manifest_path': self.manifest_path,
            'patterns': self.patterns,
            'dependencies': self.dependencies,
            'capabilities': self.capabilities,
            'tags': self.tags,
            'enabled': self.enabled,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrchestratorMetadata':
        """Create metadata from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            version=data['version'],
            type=OrchestratorType(data['type']),
            category=OrchestratorCategory(data['category']),
            class_name=data['class_name'],
            module_path=data['module_path'],
            description=data.get('description', ''),
            manifest_path=data.get('manifest_path'),
            patterns=data.get('patterns', []),
            dependencies=data.get('dependencies', []),
            capabilities=data.get('capabilities', []),
            tags=data.get('tags', {}),
            enabled=data.get('enabled', True),
        )

    def matches_pattern(self, user_input: str) -> bool:
        """Check if user input matches any registered patterns."""
        import re
        for pattern in self.patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return True
        return False
