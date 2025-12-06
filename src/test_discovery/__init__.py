"""
Test Discovery module for CORTEX integration tests.

Provides component discovery, test generation, and manifest management.
"""

from .component_discovery import (
    ComponentDiscoveryEngine,
    Component,
    ComponentSignature,
    IntegrationPoint
)

__all__ = [
    "ComponentDiscoveryEngine",
    "Component",
    "ComponentSignature",
    "IntegrationPoint"
]
