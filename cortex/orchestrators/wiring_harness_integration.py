"""Wiring Harness Integration System.

AC-ID: REMEDIATION-INTENT-005
Auto-discovery and wiring of components into orchestration pipeline.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class WiringStatus(Enum):
    """Wiring operation status."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    NOT_FOUND = "NOT_FOUND"
    ALREADY_WIRED = "ALREADY_WIRED"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"


@dataclass
class ComponentMetadata:
    """Metadata for a wiring component."""

    name: str
    module: str
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    stage: str  # STAGE_1, STAGE_2, STAGE_3, STAGE_4
    dependencies: List[str] = field(default_factory=list)
    description: str = ""
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation of metadata.
        """
        return {
            "name": self.name,
            "module": self.module,
            "priority": self.priority,
            "stage": self.stage,
            "dependencies": self.dependencies,
            "description": self.description,
            "version": self.version,
        }


class ComponentRegistry:
    """Registry for wiring components."""

    def __init__(self) -> None:
        """Initialize component registry."""
        self._components: Dict[str, ComponentMetadata] = {}

    def register(self, metadata: ComponentMetadata) -> None:
        """Register a component.

        Args:
            metadata: Component metadata.
        """
        self._components[metadata.name] = metadata

    def get(self, name: str) -> Optional[ComponentMetadata]:
        """Get component by name.

        Args:
            name: Component name.

        Returns:
            Component metadata or None.
        """
        return self._components.get(name)

    def list_components(self) -> List[ComponentMetadata]:
        """List all registered components.

        Returns:
            List of component metadata.
        """
        return list(self._components.values())


class WiringHarnessIntegration:
    """Wiring harness for component integration."""

    # Known components from REMEDIATION phase
    KNOWN_COMPONENTS = [
        ("ComprehensionSession", "cortex.orchestrators.core.comprehension_session", "CRITICAL", "STAGE_1"),
        ("ChallengeGenerator", "cortex.orchestrators.challenge_generator", "HIGH", "STAGE_3"),
        ("ConfidenceRouter", "cortex.orchestrators.confidence_router", "HIGH", "STAGE_2"),
        ("TurnValidationGate", "cortex.orchestrators.turn_validation_gate", "HIGH", "STAGE_2"),
        ("ResponseChallengeInjector", "cortex.orchestrators.response_challenge_injector", "MEDIUM", "STAGE_4"),
    ]

    def __init__(self) -> None:
        """Initialize wiring harness."""
        self.component_registry = ComponentRegistry()
        self.wiring_status: Dict[str, WiringStatus] = {}
        self.wiring_audit_trail: List[Dict[str, Any]] = []
        self._wired_components: Dict[str, List[Dict[str, Any]]] = {
            "STAGE_1": [],
            "STAGE_2": [],
            "STAGE_3": [],
            "STAGE_4": [],
        }

    def discover_components(self) -> List[ComponentMetadata]:
        """Discover available components.

        Returns:
            List of discovered component metadata.
        """
        discovered = []
        for name, module, priority, stage in self.KNOWN_COMPONENTS:
            metadata = ComponentMetadata(
                name=name,
                module=module,
                priority=priority,
                stage=stage,
            )
            self.component_registry.register(metadata)
            discovered.append(metadata)
        return discovered

    def wire_to_stage(
        self,
        component_name: str,
        stage: str,
    ) -> WiringStatus:
        """Wire component to orchestration stage.

        Args:
            component_name: Name of component to wire.
            stage: Target stage (STAGE_1-4).

        Returns:
            Wiring operation status.
        """
        # Check if component exists
        metadata = self.component_registry.get(component_name)
        if not metadata:
            # Try to discover it
            self.discover_components()
            metadata = self.component_registry.get(component_name)
            if not metadata:
                status = WiringStatus.NOT_FOUND
                self.wiring_audit_trail.append({
                    "timestamp": datetime.now().isoformat(),
                    "component": component_name,
                    "stage": stage,
                    "status": status.value,
                })
                return status

        # Check if already wired to this stage
        stage_components = self._wired_components.get(stage, [])
        if any(c["name"] == component_name for c in stage_components):
            status = WiringStatus.ALREADY_WIRED
            self.wiring_audit_trail.append({
                "timestamp": datetime.now().isoformat(),
                "component": component_name,
                "stage": stage,
                "status": status.value,
            })
            return status

        # Wire the component
        self._wired_components[stage].append(metadata.to_dict())
        status = WiringStatus.SUCCESS
        self.wiring_audit_trail.append({
            "timestamp": datetime.now().isoformat(),
            "component": component_name,
            "stage": stage,
            "status": status.value,
        })
        self.wiring_status[component_name] = status
        return status

    def wire_all(self) -> WiringStatus:
        """Wire all known components.

        Returns:
            Overall wiring status.
        """
        discovered = self.discover_components()
        success_count = 0

        for metadata in discovered:
            status = self.wire_to_stage(metadata.name, metadata.stage)
            if status == WiringStatus.SUCCESS:
                success_count += 1

        if success_count == len(discovered):
            return WiringStatus.SUCCESS
        elif success_count > 0:
            return WiringStatus.PARTIAL_SUCCESS
        else:
            return WiringStatus.FAILED

    def resolve_dependencies(
        self,
        component_name: str,
        visited: Optional[set] = None,
    ) -> List[str]:
        """Resolve component dependencies.

        Args:
            component_name: Component name.
            visited: Set of visited components (for cycle detection).

        Returns:
            List of dependency names in order.
        """
        visited = visited or set()

        if component_name in visited:
            return []  # Cycle detected

        metadata = self.component_registry.get(component_name)
        if not metadata:
            return []

        visited.add(component_name)
        dependencies = []

        for dep in metadata.dependencies:
            sub_deps = self.resolve_dependencies(dep, visited)
            dependencies.extend(sub_deps)
            if dep not in dependencies:
                dependencies.append(dep)

        if component_name not in dependencies:
            dependencies.append(component_name)

        return dependencies

    def get_wired_components(self) -> List[Dict[str, Any]]:
        """Get list of wired components.

        Returns:
            List of wired component information.
        """
        wired = []
        for stage, components in self._wired_components.items():
            wired.extend(components)
        return wired

    def get_stage_components(self, stage: str) -> List[Dict[str, Any]]:
        """Get components wired to a specific stage.

        Args:
            stage: Stage name.

        Returns:
            List of components in stage.
        """
        return self._wired_components.get(stage, [])

    def get_wiring_audit_trail(self) -> List[Dict[str, Any]]:
        """Get wiring audit trail.

        Returns:
            List of wiring operations.
        """
        return self.wiring_audit_trail

    def validate_wiring(self) -> bool:
        """Validate wiring configuration.

        Returns:
            True if wiring is valid.
        """
        # Check that all stages have at least one component (or are optional)
        required_stages = ["STAGE_1", "STAGE_2"]
        for stage in required_stages:
            components = self._wired_components.get(stage, [])
            if not components:
                return False

        return True

    def get_validation_report(self) -> Dict[str, Any]:
        """Get detailed validation report.

        Returns:
            Validation report dictionary.
        """
        report = {
            "valid": self.validate_wiring(),
            "total_components": len(self.get_wired_components()),
            "stages": {},
            "timestamp": datetime.now().isoformat(),
        }

        for stage in ["STAGE_1", "STAGE_2", "STAGE_3", "STAGE_4"]:
            components = self._wired_components.get(stage, [])
            report["stages"][stage] = {
                "component_count": len(components),
                "components": [c.get("name") for c in components],
            }

        return report

    def reset(self) -> None:
        """Reset wiring harness state.

        Used for re-initialization.
        """
        self._wired_components = {
            "STAGE_1": [],
            "STAGE_2": [],
            "STAGE_3": [],
            "STAGE_4": [],
        }
        self.wiring_audit_trail = []
        self.wiring_status = {}
