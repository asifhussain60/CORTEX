"""
Mistake Prevention Engine - User Mistake Prevention for Orchestrators.

Implements prevention rules for:
- Blocking direct orchestrator creation
- Preventing duplicate orchestrators  
- Validating orchestrator hierarchy
- Enforcing YAML-first design

Author: CORTEX feat04-core-orchestration Phase 1 Task 1.2
Created: 2026-01-08
Version: 1.0.0
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum
import yaml
import logging


class MistakeType(Enum):
    """Types of mistakes that can be prevented."""
    
    DIRECT_CREATION = "direct_creation"
    DUPLICATE_ORCHESTRATOR = "duplicate_orchestrator"
    INVALID_HIERARCHY = "invalid_hierarchy"
    MISSING_MANIFEST = "missing_manifest"


@dataclass
class OrchestrationIntent:
    """Represents an orchestration intent to be validated."""
    
    action: str  # "create_file", "register_orchestrator", etc.
    target: str  # File path, orchestrator ID, etc.
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PreventionRule:
    """Prevention rule definition."""
    
    id: str
    name: str
    mistake_type: MistakeType
    severity: str  # "blocked", "warning", "info"
    enabled: bool
    message: str
    suggestion: Optional[str] = None


@dataclass
class PreventionResult:
    """Result of mistake prevention validation."""
    
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    mistake_type: Optional[MistakeType] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def format_error_message(self) -> str:
        """
        Format user-friendly error message with suggestions.
        
        Returns:
            Formatted error message
        """
        if not self.errors:
            return "Validation passed"
        
        lines = ["⛔ Cannot proceed with this operation:", ""]
        lines.extend([f"  • {error}" for error in self.errors])
        
        if self.suggestions:
            lines.extend(["", "💡 Suggestions:", ""])
            lines.extend([f"  • {suggestion}" for suggestion in self.suggestions])
        
        return "\n".join(lines)


class MistakePreventionEngine:
    """
    Mistake prevention engine for orchestrator operations.
    
    Validates orchestrator operations before they execute,
    preventing common mistakes like:
    - Creating orchestrators directly (bypass MasterOrchestrator)
    - Duplicate orchestrators with similar functionality
    - Invalid parent-child relationships
    - Missing YAML manifests (violates YAML-first design)
    
    Usage:
        engine = MistakePreventionEngine(
            rules_path="cortex-brain/config/prevention-rules.yaml"
        )
        
        result = engine.validate_intent(intent)
        if not result.is_valid:
            print(result.format_error_message())
    """
    
    def __init__(self, rules_path: str):
        """
        Initialize mistake prevention engine.
        
        Args:
            rules_path: Path to prevention-rules.yaml
        """
        self.rules_path = Path(rules_path)
        self.logger = logging.getLogger("cortex.mistake_prevention")
        
        # Load prevention rules
        self.rules = self._load_rules()
        
        # Registry of existing orchestrators
        self.orchestrators: Dict[str, Any] = {}
        
        self.logger.info(
            f"MistakePreventionEngine initialized with {len(self.rules)} rules"
        )
    
    def _load_rules(self) -> List[PreventionRule]:
        """
        Load prevention rules from YAML configuration.
        
        Returns:
            List of PreventionRule objects
        """
        if not self.rules_path.exists():
            self.logger.warning(f"Rules file not found: {self.rules_path}")
            return []
        
        try:
            with open(self.rules_path, 'r') as f:
                config = yaml.safe_load(f)
            
            rules = []
            for rule_data in config.get('rules', []):
                rule = PreventionRule(
                    id=rule_data['id'],
                    name=rule_data['name'],
                    mistake_type=MistakeType(rule_data['mistake_type']),
                    severity=rule_data['severity'],
                    enabled=rule_data.get('enabled', True),
                    message=rule_data['message'],
                    suggestion=rule_data.get('suggestion')
                )
                rules.append(rule)
            
            self.logger.debug(f"Loaded {len(rules)} rules from {self.rules_path}")
            return rules
        
        except Exception as e:
            self.logger.error(f"Failed to load rules: {e}", exc_info=True)
            return []
    
    def register_orchestrator(self, orchestrator: Any) -> None:
        """
        Register an orchestrator in the engine.
        
        Args:
            orchestrator: Orchestrator object to register
        """
        self.orchestrators[orchestrator.id] = orchestrator
        self.logger.debug(f"Registered orchestrator: {orchestrator.id}")
    
    def validate_intent(self, intent: OrchestrationIntent) -> PreventionResult:
        """
        Validate an orchestration intent against prevention rules.
        
        Args:
            intent: OrchestrationIntent to validate
        
        Returns:
            PreventionResult with validation status
        """
        # Check for direct creation
        if intent.action == "create_file":
            target = intent.target.lower()
            creator = intent.context.get("creator", "user")
            
            # Check if creating orchestrator file
            if "orchestrator" in target:
                # Allow if created by master or CORTEX
                if creator not in ["master_orchestrator", "cortex", "master"]:
                    # Check for approval
                    if not intent.context.get("approved_by_master", False):
                        return PreventionResult(
                            is_valid=False,
                            errors=["Direct orchestrator creation is blocked. Use MasterOrchestrator."],
                            suggestions=["Request: 'create orchestrator for {use_case}'"],
                            mistake_type=MistakeType.DIRECT_CREATION
                        )
        
        return PreventionResult(is_valid=True)
    
    def check_for_duplicates(self, orchestrator: Any) -> PreventionResult:
        """
        Check if orchestrator duplicates existing functionality.
        
        Args:
            orchestrator: Orchestrator to check
        
        Returns:
            PreventionResult indicating if duplicate exists
        """
        for existing_id, existing in self.orchestrators.items():
            if existing_id == orchestrator.id:
                continue
            
            # Check pattern overlap
            pattern_overlap = set(orchestrator.patterns) & set(existing.patterns)
            if pattern_overlap:
                return PreventionResult(
                    is_valid=False,
                    errors=[f"Orchestrator with similar functionality exists: {existing.name}"],
                    suggestions=[
                        f"Consider consolidating with '{existing.name}' orchestrator",
                        "Or provide explicit justification for separate orchestrator"
                    ],
                    mistake_type=MistakeType.DUPLICATE_ORCHESTRATOR,
                    metadata={"existing_id": existing_id, "overlapping_patterns": list(pattern_overlap)}
                )
            
            # Check capability overlap
            capability_overlap = set(orchestrator.capabilities) & set(existing.capabilities)
            if len(capability_overlap) >= 2:  # Significant overlap
                return PreventionResult(
                    is_valid=False,
                    errors=[f"Orchestrator with similar functionality exists: {existing.name}"],
                    suggestions=[
                        f"Consider consolidating with '{existing.name}' orchestrator"
                    ],
                    mistake_type=MistakeType.DUPLICATE_ORCHESTRATOR,
                    metadata={"existing_id": existing_id, "overlapping_capabilities": list(capability_overlap)}
                )
        
        return PreventionResult(is_valid=True)
    
    def validate_hierarchy(self, orchestrator: Any) -> PreventionResult:
        """
        Validate orchestrator parent-child hierarchy.
        
        Args:
            orchestrator: Orchestrator to validate
        
        Returns:
            PreventionResult indicating if hierarchy is valid
        """
        # Check if parent exists
        if orchestrator.parent_id:
            if orchestrator.parent_id not in self.orchestrators:
                return PreventionResult(
                    is_valid=False,
                    errors=[f"Parent orchestrator '{orchestrator.parent_id}' does not exist"],
                    suggestions=["Create parent orchestrator first", "Or set parent_id=None"],
                    mistake_type=MistakeType.INVALID_HIERARCHY
                )
            
            # Check for circular dependencies
            if self._has_circular_dependency(orchestrator.id, orchestrator.parent_id):
                return PreventionResult(
                    is_valid=False,
                    errors=["Circular dependency detected in orchestrator hierarchy"],
                    suggestions=["Remove circular parent-child relationship"],
                    mistake_type=MistakeType.INVALID_HIERARCHY
                )
            
            # Check hierarchy depth
            depth = self._get_hierarchy_depth(orchestrator.parent_id)
            if depth >= 2:  # Master(0) → Parent(1) → Child(2) max, so parent at depth 2 means child would be at 3
                return PreventionResult(
                    is_valid=False,
                    errors=[f"Hierarchy depth exceeds maximum (would be depth: {depth+1}, max: 3)"],
                    suggestions=["Flatten hierarchy or use different parent"],
                    mistake_type=MistakeType.INVALID_HIERARCHY
                )
        
        return PreventionResult(is_valid=True)
    
    def _has_circular_dependency(self, child_id: str, parent_id: str, visited: set = None) -> bool:
        """
        Check if adding this parent would create a circular dependency.
        
        Args:
            child_id: ID of child orchestrator
            parent_id: ID of parent orchestrator
            visited: Set of visited IDs (for recursion)
        
        Returns:
            True if circular dependency exists
        """
        if visited is None:
            visited = set()
        
        if parent_id == child_id:
            return True
        
        if parent_id in visited:
            return False
        
        visited.add(parent_id)
        
        # Check if parent has a parent that leads back to child
        parent = self.orchestrators.get(parent_id)
        if parent and hasattr(parent, 'parent_id') and parent.parent_id:
            return self._has_circular_dependency(child_id, parent.parent_id, visited)
        
        return False
    
    def _get_hierarchy_depth(self, orchestrator_id: str, depth: int = 0) -> int:
        """
        Get depth of orchestrator in hierarchy.
        
        Args:
            orchestrator_id: ID of orchestrator
            depth: Current depth (for recursion)
        
        Returns:
            Depth of orchestrator in hierarchy
        """
        orchestrator = self.orchestrators.get(orchestrator_id)
        if not orchestrator or not hasattr(orchestrator, 'parent_id') or not orchestrator.parent_id:
            return depth
        
        return self._get_hierarchy_depth(orchestrator.parent_id, depth + 1)
    
    def validate_yaml_first(self, orchestrator: Any) -> PreventionResult:
        """
        Validate orchestrator follows YAML-first design.
        
        Args:
            orchestrator: Orchestrator to validate
        
        Returns:
            PreventionResult indicating if YAML-first is followed
        """
        # Check if manifest_path is provided
        if not orchestrator.manifest_path:
            return PreventionResult(
                is_valid=False,
                errors=["YAML manifest required before Python implementation"],
                suggestions=[
                    "Create manifest: cortex-brain/manifests/orchestrators/{name}.yaml",
                    "Then implement Python: src/orchestrators/{category}/{name}.py"
                ],
                mistake_type=MistakeType.MISSING_MANIFEST
            )
        
        # Check if manifest file exists
        manifest_path = Path(orchestrator.manifest_path)
        if not manifest_path.exists():
            return PreventionResult(
                is_valid=False,
                errors=[f"Manifest file not found: {orchestrator.manifest_path}"],
                suggestions=[f"Create manifest file at: {orchestrator.manifest_path}"],
                mistake_type=MistakeType.MISSING_MANIFEST
            )
        
        return PreventionResult(is_valid=True)
