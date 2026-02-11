"""
Orchestrator Context Injector Decorator

Automatically injects OrchestratorContext into orchestrator operations.
Reads metadata from wiring.yaml for icons, stages, and intelligence flags.

Authority: AC-UX-VISIBILITY-001 (Phase 20.2 Component #2)
Rule: CORE-011 (Type Hints), CORE-035 (Single Implementation)

Usage:
    @inject_orchestrator_context
    def coordinate_operation(self, operation: str, context: Dict) -> Result:
        # Context automatically injected
        # Badge automatically appended to response
        ...
"""

import functools
import logging
from pathlib import Path
from typing import Any, Callable, Dict, Optional, TypeVar, cast

from cortex.core.result import Err, Ok, Result
from cortex.observability.visibility_controller import (
    IntelligenceFlags,
    OrchestratorContext,
    get_visibility_controller,
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


class OrchestratorMetadataRegistry:
    """
    Registry for orchestrator metadata loaded from wiring.yaml.

    Provides icon, stage count, and intelligence configuration
    for orchestrators to enable automatic context creation.

    Authority: AC-UX-VISIBILITY-001
    """

    _instance: Optional['OrchestratorMetadataRegistry'] = None
    _metadata_cache: Dict[str, Dict[str, Any]] = {}

    # Default icons for common orchestrators (fallback)
    DEFAULT_ICONS = {
        "TDDOrchestrator": "🧪",
        "FixOrchestrator": "🔧",
        "RefactoringOrchestrator": "♻️",
        "AnalysisOrchestrator": "🔍",
        "PlanningOrchestrator": "📋",
        "ConversationOrchestrator": "🤝",
        "MasterOrchestrator": "🧠",
        "InteractionOrchestrator": "💬",
        "IntentRouter": "🎯",
        "LENSSynthesis": "🔬",
        "EnforcementOrchestrator": "🛡️",
        "WorkflowOrchestrator": "⚙️",
    }

    @classmethod
    def instance(cls) -> 'OrchestratorMetadataRegistry':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        """Initialize metadata registry."""
        self._load_metadata()

    def _load_metadata(self) -> None:
        """
        Load orchestrator metadata from wiring.yaml.

        Reads metadata section (if exists) or falls back to defaults.
        """
        try:
            import yaml

            # Find wiring.yaml
            wiring_path = Path(__file__).parent.parent.parent / "wiring" / "specifications" / "wiring.yaml"

            if not wiring_path.exists():
                logger.warning(f"Wiring file not found: {wiring_path}, using defaults")
                return

            with open(wiring_path, 'r') as f:
                wiring_data = yaml.safe_load(f)

            # Extract metadata from orchestrators sections
            orchestrators = wiring_data.get("orchestrators", {})

            for category in ["core", "domain", "support"]:
                for orch in orchestrators.get(category, []):
                    name = orch.get("name")
                    if not name:
                        continue

                    # Extract metadata (if present)
                    metadata = orch.get("metadata", {})

                    self._metadata_cache[name] = {
                        "icon": metadata.get("icon", self.DEFAULT_ICONS.get(name, "🤖")),
                        "stages": metadata.get("stages", 4),  # Default 4 stages
                        "intelligence": metadata.get("intelligence", ["lens", "knowledge"]),
                        "category": category,
                    }

            logger.info(f"Loaded metadata for {len(self._metadata_cache)} orchestrators")

        except Exception as e:
            logger.error(f"Failed to load orchestrator metadata: {e}", exc_info=True)
            # Graceful degradation: use defaults

    def get_metadata(self, orchestrator_name: str) -> Dict[str, Any]:
        """
        Get metadata for an orchestrator.

        Args:
            orchestrator_name: Name of orchestrator

        Returns:
            Metadata dictionary with icon, stages, intelligence
        """
        return self._metadata_cache.get(orchestrator_name, {
            "icon": self.DEFAULT_ICONS.get(orchestrator_name, "🤖"),
            "stages": 4,
            "intelligence": ["lens", "knowledge"],
            "category": "unknown",
        })

    def get_icon(self, orchestrator_name: str) -> str:
        """Get icon for orchestrator (with fallback)."""
        return self.get_metadata(orchestrator_name).get("icon", "🤖")

    def get_stage_count(self, orchestrator_name: str) -> int:
        """Get stage count for orchestrator."""
        return self.get_metadata(orchestrator_name).get("stages", 4)

    def get_intelligence_flags(self, orchestrator_name: str) -> IntelligenceFlags:
        """
        Get intelligence flags for orchestrator.

        Returns:
            IntelligenceFlags with lens, knowledge, synthesis enabled
        """
        intelligence = self.get_metadata(orchestrator_name).get("intelligence", [])

        return IntelligenceFlags(
            lens_enabled="lens" in intelligence,
            knowledge_enabled="knowledge" in intelligence,
            synthesis_enabled="synthesis" in intelligence,
        )


def inject_orchestrator_context(func: Callable[..., Result[Dict[str, Any]]]) -> Callable[..., Result[Dict[str, Any]]]:
    """
    Decorator that injects OrchestratorContext into orchestrator operations.

    Automatically:
    1. Extracts orchestrator name from class
    2. Loads metadata from wiring.yaml registry
    3. Creates OrchestratorContext with current stage/progress
    4. Appends badge to response (if ResponseHeaderInjector available)

    Usage:
        class TDDOrchestrator:
            @inject_orchestrator_context
            def coordinate_operation(self, operation: str, context: Dict) -> Result:
                # Context auto-injected
                ...

    Args:
        func: Function to decorate (must return Result[Dict[str, Any]])

    Returns:
        Wrapped function with automatic context injection

    Authority: AC-UX-VISIBILITY-001 (Phase 20.2 Component #2)
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs) -> Result[Dict[str, Any]]:
        """Wrapper function that injects orchestrator context."""

        # Extract orchestrator name from class
        orchestrator_name = self.__class__.__name__

        # Load metadata
        registry = OrchestratorMetadataRegistry.instance()
        metadata = registry.get_metadata(orchestrator_name)

        # Extract current stage from context (if available)
        context_dict = kwargs.get('context', {}) or (args[1] if len(args) > 1 else {})
        current_stage = context_dict.get('current_stage', 1)
        stages_completed = context_dict.get('stages_completed', [])

        # Detect intelligence active (from context or state manager)
        intelligence_flags = registry.get_intelligence_flags(orchestrator_name)

        # Check if synthesis engine active
        if hasattr(self, '_synthesis_engine') and self._synthesis_engine:
            intelligence_flags.synthesis_enabled = True

        # Create OrchestratorContext
        orchestrator_context = OrchestratorContext(
            orchestrator_name=orchestrator_name,
            orchestrator_icon=metadata["icon"],
            current_stage=current_stage,
            stages_completed=stages_completed,
            intelligence_active=intelligence_flags,
            failure_stage=context_dict.get('failure_stage'),
            failure_reason=context_dict.get('failure_reason'),
        )

        # Execute original function
        result = func(self, *args, **kwargs)

        # Inject badge into response (if successful and header_injector available)
        if result.is_ok() and hasattr(self, 'header_injector') and self.header_injector:
            try:
                response = result.unwrap()

                # Extract operation name
                operation = args[0] if args else kwargs.get('operation', 'Operation')

                # Generate header with badge
                header = self.header_injector.inject_header(
                    operation=operation,
                    orchestrator_context=orchestrator_context,
                )

                # Inject header into response (if response has markdown field)
                if isinstance(response, dict):
                    # Prepend header to response markdown
                    if 'markdown' in response:
                        response['markdown'] = f"{header}\n\n{response['markdown']}"
                    elif 'result' in response and isinstance(response['result'], str):
                        response['result'] = f"{header}\n\n{response['result']}"
                    else:
                        # Add header as separate field
                        response['header'] = header

                logger.debug(f"Injected orchestrator badge for {orchestrator_name}")

            except Exception as e:
                # Graceful degradation: log but don't fail
                logger.warning(f"Failed to inject orchestrator badge: {e}")

        return result

    return wrapper


def extract_orchestrator_metadata_from_wiring() -> Dict[str, Dict[str, Any]]:
    """
    Extract all orchestrator metadata from wiring.yaml.

    Used for validation and testing purposes.

    Returns:
        Dictionary mapping orchestrator name to metadata
    """
    registry = OrchestratorMetadataRegistry.instance()
    return registry._metadata_cache
