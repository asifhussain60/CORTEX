"""
MCP Middleware Package (Phase 28)

Middleware components for MCP server request processing.

Components:
- onboarding_gate: Enforces onboarding-first policy for external repos
"""

from cortex.mcp.middleware.intelligence_gate import IntelligenceGate
from cortex.mcp.middleware.onboarding_gate import (
    OnboardingGate,
    create_onboarding_gate,
)

__all__ = [
    "OnboardingGate",
    "create_onboarding_gate",
    "IntelligenceGate",
]
