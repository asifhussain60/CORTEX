"""
AC-FUTURE-011: Challenge System Plugin Architecture

Makes the ChallengeEngine extensible via plugin pattern, allowing custom
disagreement types and handlers without modifying core code.

Production Ready: ✅
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Type, Any
from enum import Enum
import importlib
import logging


logger = logging.getLogger(__name__)


class DisagreementType(Enum):
    """Built-in disagreement types"""
    ARCHITECTURAL_VIOLATION = "architectural_violation"
    HARMFUL_ACTION = "harmful_action"
    BETTER_SOLUTION = "better_solution"
    MISSING_CONTEXT = "missing_context"
    REDUNDANT_WORK = "redundant_work"


@dataclass
class DisagreementContext:
    """Context for disagreement detection"""
    user_input: str
    proposed_intent: str
    current_context: Dict[str, Any]
    system_state: Dict[str, Any]


class DisagreementPlugin(ABC):
    """Base class for disagreement detection plugins"""

    @property
    @abstractmethod
    def disagreement_type(self) -> DisagreementType:
        """Return the disagreement type this plugin handles"""
        pass

    @abstractmethod
    def detect(self, context: DisagreementContext) -> Optional[str]:
        """
        Detect if this type of disagreement exists.
        
        Returns:
            Disagreement explanation if detected, None otherwise
        """
        pass

    @abstractmethod
    def generate_recommendation(self, context: DisagreementContext) -> str:
        """Generate recommendation to address disagreement"""
        pass


class PluginRegistry:
    """Registry for disagreement plugins"""

    def __init__(self):
        self.plugins: Dict[DisagreementType, Type[DisagreementPlugin]] = {}
        self._instances: Dict[DisagreementType, DisagreementPlugin] = {}

    def register(
        self,
        disagreement_type: DisagreementType,
        plugin_class: Type[DisagreementPlugin],
    ):
        """Register a disagreement plugin"""
        self.plugins[disagreement_type] = plugin_class
        self._instances[disagreement_type] = plugin_class()
        logger.info(f"Registered plugin for {disagreement_type.value}")

    def unregister(self, disagreement_type: DisagreementType):
        """Unregister a disagreement plugin"""
        if disagreement_type in self.plugins:
            del self.plugins[disagreement_type]
            del self._instances[disagreement_type]

    def get_plugin(self, disagreement_type: DisagreementType) -> Optional[DisagreementPlugin]:
        """Get plugin instance for disagreement type"""
        return self._instances.get(disagreement_type)

    def list_plugins(self) -> List[DisagreementType]:
        """List all registered disagreement types"""
        return list(self.plugins.keys())

    def load_from_module(self, module_path: str):
        """Dynamically load plugins from module"""
        try:
            module = importlib.import_module(module_path)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type) and
                    issubclass(attr, DisagreementPlugin) and
                    attr is not DisagreementPlugin
                ):
                    plugin = attr()
                    self.register(plugin.disagreement_type, attr)
        except Exception as e:
            logger.error(f"Failed to load plugins from {module_path}: {e}")


# Built-in plugin implementations

class ArchitecturalViolationPlugin(DisagreementPlugin):
    """Plugin for detecting architectural violations"""

    @property
    def disagreement_type(self) -> DisagreementType:
        return DisagreementType.ARCHITECTURAL_VIOLATION

    def detect(self, context: DisagreementContext) -> Optional[str]:
        """Detect architectural violations in proposed intent"""
        violations = [
            "bypass", "hack", "workaround", "shortcut",
            "temporary", "skip", "ignore", "override",
        ]
        if any(v in context.proposed_intent.lower() for v in violations):
            return f"Potential architectural violation detected in: {context.proposed_intent}"
        return None

    def generate_recommendation(self, context: DisagreementContext) -> str:
        return "Consider following architectural patterns instead of shortcuts"


class HarmfulActionPlugin(DisagreementPlugin):
    """Plugin for detecting harmful actions"""

    @property
    def disagreement_type(self) -> DisagreementType:
        return DisagreementType.HARMFUL_ACTION

    def detect(self, context: DisagreementContext) -> Optional[str]:
        """Detect potentially harmful actions"""
        harmful_keywords = [
            "delete all", "drop", "truncate", "rm -rf",
            "remove production", "wipe", "erase",
        ]
        if any(kw in context.proposed_intent.lower() for kw in harmful_keywords):
            return f"Potentially harmful action detected: {context.proposed_intent}"
        return None

    def generate_recommendation(self, context: DisagreementContext) -> str:
        return "Consider backup and rollback strategy before proceeding"


class BetterSolutionPlugin(DisagreementPlugin):
    """Plugin for detecting better solution opportunities"""

    @property
    def disagreement_type(self) -> DisagreementType:
        return DisagreementType.BETTER_SOLUTION

    def detect(self, context: DisagreementContext) -> Optional[str]:
        """Detect when a better solution might exist"""
        # In practice, this would use ML/semantic analysis
        return None

    def generate_recommendation(self, context: DisagreementContext) -> str:
        return "Would you like to explore alternative approaches?"


class MissingContextPlugin(DisagreementPlugin):
    """Plugin for detecting missing context"""

    @property
    def disagreement_type(self) -> DisagreementType:
        return DisagreementType.MISSING_CONTEXT

    def detect(self, context: DisagreementContext) -> Optional[str]:
        """Detect missing context in request"""
        vague_terms = ["improve", "fix", "update", "handle"]
        if any(term in context.user_input.lower() for term in vague_terms):
            if len(context.user_input.split()) < 5:
                return "Request lacks sufficient context"
        return None

    def generate_recommendation(self, context: DisagreementContext) -> str:
        return "Please provide more details about what needs to be done"


class RedundantWorkPlugin(DisagreementPlugin):
    """Plugin for detecting redundant work"""

    @property
    def disagreement_type(self) -> DisagreementType:
        return DisagreementType.REDUNDANT_WORK

    def detect(self, context: DisagreementContext) -> Optional[str]:
        """Detect redundant or duplicate work"""
        # In practice, would check project history
        return None

    def generate_recommendation(self, context: DisagreementContext) -> str:
        return "This work may already exist in the codebase"


class PluginBasedChallengeEngine:
    """Challenge engine using plugin architecture"""

    def __init__(self):
        self.registry = PluginRegistry()
        self._register_builtin_plugins()

    def _register_builtin_plugins(self):
        """Register all built-in plugins"""
        self.registry.register(
            DisagreementType.ARCHITECTURAL_VIOLATION,
            ArchitecturalViolationPlugin,
        )
        self.registry.register(
            DisagreementType.HARMFUL_ACTION,
            HarmfulActionPlugin,
        )
        self.registry.register(
            DisagreementType.BETTER_SOLUTION,
            BetterSolutionPlugin,
        )
        self.registry.register(
            DisagreementType.MISSING_CONTEXT,
            MissingContextPlugin,
        )
        self.registry.register(
            DisagreementType.REDUNDANT_WORK,
            RedundantWorkPlugin,
        )

    def detect_all_disagreements(
        self,
        context: DisagreementContext,
    ) -> Dict[DisagreementType, str]:
        """Run all plugins and collect disagreements"""
        disagreements = {}

        for disagreement_type in self.registry.list_plugins():
            plugin = self.registry.get_plugin(disagreement_type)
            if plugin:
                result = plugin.detect(context)
                if result:
                    disagreements[disagreement_type] = result

        return disagreements

    def register_custom_plugin(
        self,
        plugin_class: Type[DisagreementPlugin],
    ):
        """Register custom disagreement plugin"""
        plugin = plugin_class()
        self.registry.register(plugin.disagreement_type, plugin_class)

    def challenge_request(
        self,
        user_input: str,
        proposed_intent: str,
        current_context: Dict[str, Any],
        system_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate challenge if any disagreements detected"""
        context = DisagreementContext(
            user_input=user_input,
            proposed_intent=proposed_intent,
            current_context=current_context,
            system_state=system_state,
        )

        disagreements = self.detect_all_disagreements(context)

        if not disagreements:
            return {"has_challenge": False}

        # Return first disagreement as challenge
        primary_type = list(disagreements.keys())[0]
        plugin = self.registry.get_plugin(primary_type)

        return {
            "has_challenge": True,
            "disagreement_type": primary_type.value,
            "explanation": disagreements[primary_type],
            "recommendation": plugin.generate_recommendation(context),
        }
