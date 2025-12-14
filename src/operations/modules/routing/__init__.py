"""Routing module for CORTEX Planning System 3.0

This module provides tiered routing for operation classification.

Exports:
    - TieredRouter: Main routing class
    - RoutingDecision: Classification result
    - RoutingTelemetry: Accuracy tracking
    - OperationTier: Tier enum
"""

from .tiered_router import (
    TieredRouter,
    RoutingDecision,
    RoutingTelemetry,
    RoutingFeedback,
    OperationTier,
    RegexFallback
)

__all__ = [
    'TieredRouter',
    'RoutingDecision',
    'RoutingTelemetry',
    'RoutingFeedback',
    'OperationTier',
    'RegexFallback'
]

__version__ = '3.0.0'
__author__ = 'Asif Hussain'
