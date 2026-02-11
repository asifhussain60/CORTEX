"""
Event Subscription Registration System - Phase 9

Automatically registers event subscriptions for orchestrators based on:
- Event types they emit
- Event types they subscribe to
- Dependency relationships
- Wiring specifications
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


# ============================================================================
# EVENT SUBSCRIPTION MODELS
# ============================================================================

@dataclass
class EventSubscription:
    """Represents an event subscription"""
    orchestrator_name: str
    event_type: str
    handler_method: str
    priority: int = 100
    async_execution: bool = False


@dataclass
class EventEmission:
    """Represents an event emission capability"""
    orchestrator_name: str
    event_type: str
    event_data_schema: Optional[Dict[str, Any]] = None


# ============================================================================
# SUBSCRIPTION REGISTRY
# ============================================================================

class EventSubscriptionRegistry:
    """
    Manages event subscriptions and emissions across orchestrators.
    Provides:
    - Registration of subscriptions
    - Validation of subscription/emission pairs
    - Dependency-based subscription automation
    """

    def __init__(self):
        self.subscriptions: Dict[str, List[EventSubscription]] = {}  # event_type -> [subscriptions]
        self.emissions: Dict[str, List[EventEmission]] = {}  # orchestrator_name -> [emissions]
        self.orchestrator_handlers: Dict[str, Dict[str, Callable]] = {}  # orch_name -> {event_type: handler}

    def register_subscription(self, subscription: EventSubscription) -> None:
        """Register orchestrator subscription to event type"""
        if subscription.event_type not in self.subscriptions:
            self.subscriptions[subscription.event_type] = []
        self.subscriptions[subscription.event_type].append(subscription)
        logger.debug(f"Registered subscription: {subscription.orchestrator_name} → {subscription.event_type}")

    def register_emission(self, emission: EventEmission) -> None:
        """Register orchestrator emission capability"""
        if emission.orchestrator_name not in self.emissions:
            self.emissions[emission.orchestrator_name] = []
        self.emissions[emission.orchestrator_name].append(emission)
        logger.debug(f"Registered emission: {emission.orchestrator_name} → {emission.event_type}")

    def register_handler(self, orchestrator_name: str, event_type: str, handler: Callable) -> None:
        """Register event handler method for orchestrator"""
        if orchestrator_name not in self.orchestrator_handlers:
            self.orchestrator_handlers[orchestrator_name] = {}
        self.orchestrator_handlers[orchestrator_name][event_type] = handler
        logger.debug(f"Registered handler: {orchestrator_name}.{event_type}")

    def validate_subscriptions(self) -> bool:
        """
        Validate that all subscriptions have corresponding emissions.
        Returns True if valid, False otherwise.
        """
        all_valid = True
        all_emitted_events = set()

        # Collect all emitted events
        for orch_name, emissions in self.emissions.items():
            for emission in emissions:
                all_emitted_events.add(emission.event_type)

        # Validate subscriptions
        for event_type, subscriptions in self.subscriptions.items():
            if event_type not in all_emitted_events:
                logger.warning(f"⚠️ No emitter for subscribed event: {event_type}")
                all_valid = False

        if all_valid:
            logger.info(f"✅ All {len(self.subscriptions)} event types have emitters")
        return all_valid

    def get_subscribers(self, event_type: str) -> List[EventSubscription]:
        """Get all subscriptions for an event type"""
        return self.subscriptions.get(event_type, [])

    def get_emissions(self, orchestrator_name: str) -> List[EventEmission]:
        """Get all emissions from an orchestrator"""
        return self.emissions.get(orchestrator_name, [])


# ============================================================================
# SUBSCRIPTION BUILDER
# ============================================================================

class EventSubscriptionBuilder:
    """
    Builds event subscriptions from wiring specifications.
    Converts wiring YAML into EventSubscription objects.
    """

    @staticmethod
    def from_wiring_spec(wiring_spec: Dict[str, Any]) -> EventSubscriptionRegistry:
        """
        Build subscription registry from wiring specification.
        Args:
            wiring_spec: Parsed wiring.yaml as dict
        Returns:
            EventSubscriptionRegistry with all subscriptions registered
        """
        registry = EventSubscriptionRegistry()

        # Get orchestrators from wiring
        orchestrators = {}
        for tier, orch_list in wiring_spec.get('orchestrators', {}).items():
            if isinstance(orch_list, list):
                for orch in orch_list:
                    orchestrators[orch['name']] = orch

        # Register emissions
        for orch_name, orch_spec in orchestrators.items():
            for event_type in orch_spec.get('event_emissions', []):
                emission = EventEmission(
                    orchestrator_name=orch_name,
                    event_type=event_type,
                    event_data_schema=None  # TODO: Extract from spec if available
                )
                registry.register_emission(emission)

        # Register subscriptions
        for orch_name, orch_spec in orchestrators.items():
            for event_type in orch_spec.get('event_subscriptions', []):
                handler_method = f"on_{event_type.lower()}"
                subscription = EventSubscription(
                    orchestrator_name=orch_name,
                    event_type=event_type,
                    handler_method=handler_method,
                    priority=orch_spec.get('priority', 100),
                    async_execution=False  # TODO: Extract from spec if available
                )
                registry.register_subscription(subscription)

        logger.info("✅ Built subscription registry from wiring spec")
        return registry


# ============================================================================
# EVENT SUBSCRIPTION MANAGER
# ============================================================================

class EventSubscriptionManager:
    """
    Manages runtime event subscriptions with orchestrator instances.
    Coordinates subscription registration with event bus and orchestrators.
    """

    def __init__(self, event_bus: Any):
        self.event_bus = event_bus
        self.registry = EventSubscriptionRegistry()
        self.active_subscriptions: Set[str] = set()

    def build_from_wiring(self, wiring_spec: Dict[str, Any]) -> None:
        """Build subscription registry from wiring specification"""
        self.registry = EventSubscriptionBuilder.from_wiring_spec(wiring_spec)

    def register_orchestrator_handlers(self, orchestrator_name: str, instance: Any) -> int:
        """
        Register all event handlers for an orchestrator instance.
        Returns: Number of handlers registered
        """
        handler_count = 0

        # Get subscriptions for this orchestrator
        for event_type, subscriptions in self.registry.subscriptions.items():
            for sub in subscriptions:
                if sub.orchestrator_name == orchestrator_name:
                    # Get handler method
                    if hasattr(instance, sub.handler_method):
                        handler = getattr(instance, sub.handler_method)
                        self.event_bus.subscribe(event_type, handler)
                        self.active_subscriptions.add(f"{orchestrator_name}:{event_type}")
                        handler_count += 1
                        logger.debug(f"Registered handler: {orchestrator_name}.{sub.handler_method}")

        return handler_count

    def register_all_handlers(self, orchestrators: Dict[str, Any]) -> int:
        """
        Register handlers for all orchestrators.
        Returns: Total number of handlers registered
        """
        total_handlers = 0
        for orch_name, instance in orchestrators.items():
            handlers = self.register_orchestrator_handlers(orch_name, instance)
            total_handlers += handlers
            if handlers > 0:
                logger.info(f"✅ Registered {handlers} handlers for {orch_name}")

        logger.info(f"✅ Total {total_handlers} event handlers registered")
        return total_handlers

    def validate_subscriptions(self) -> bool:
        """Validate all subscriptions have corresponding emissions"""
        return self.registry.validate_subscriptions()

    def get_subscription_stats(self) -> Dict[str, Any]:
        """Get subscription statistics"""
        return {
            'total_event_types': len(self.registry.subscriptions),
            'total_subscriptions': sum(len(subs) for subs in self.registry.subscriptions.values()),
            'total_emitters': len(self.registry.emissions),
            'active_subscriptions': len(self.active_subscriptions),
        }


# ============================================================================
# SUBSCRIPTION GRAPH VISUALIZATION
# ============================================================================

class SubscriptionGraph:
    """
    Generates visualization of event subscription graph.
    Helps understand event flow through orchestrators.
    """

    @staticmethod
    def generate_dot_format(registry: EventSubscriptionRegistry) -> str:
        """Generate Graphviz DOT format for subscription graph"""
        lines = ["digraph EventSubscriptions {"]
        lines.append("  rankdir=LR;")
        lines.append("  node [shape=box];")

        # Add edges from emitters to subscribers
        for event_type, subscriptions in registry.subscriptions.items():
            # Find emitter for this event
            emitters = []
            for orch_name, emissions in registry.emissions.items():
                for emission in emissions:
                    if emission.event_type == event_type:
                        emitters.append(orch_name)

            # Add edges
            for emitter in emitters:
                for sub in subscriptions:
                    lines.append(f'  "{emitter}" -> "{sub.orchestrator_name}" [label="{event_type}"];')

        lines.append("}")
        return "\n".join(lines)

    @staticmethod
    def generate_mermaid_format(registry: EventSubscriptionRegistry) -> str:
        """Generate Mermaid format for subscription graph"""
        lines = ["graph LR"]

        # Add edges
        for event_type, subscriptions in registry.subscriptions.items():
            emitters = []
            for orch_name, emissions in registry.emissions.items():
                for emission in emissions:
                    if emission.event_type == event_type:
                        emitters.append(orch_name)

            for emitter in emitters:
                for sub in subscriptions:
                    lines.append(f'  {emitter} -->|{event_type}| {sub.orchestrator_name}')

        return "\n".join(lines)
