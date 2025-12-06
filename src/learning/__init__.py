"""
Learning System for CORTEX

Event-driven learning library that captures milestone events from orchestrators
and agents, generates educational documentation, and serves content through
Docsify-based learning dashboard.

Architecture:
- Event-driven (no orchestrator coupling)
- Milestone-based updates (not continuous)
- 51 total events across 22 components (18 must-have, 33 should-have)
- 15 learning categories

Components:
- event_collector.py: Captures and filters learning events
- event_taxonomy.py: Defines 51 event types across 3 tiers
- document_generator.py: Generates markdown from events (Phase 2)
- resource_database.py: Manages external resource links (Phase 2)

Usage:
    from src.learning.event_collector import LearningEventCollector
    from src.learning.event_taxonomy import EventType, LearningEvent
    
    collector = LearningEventCollector()
    
    # Emit event from orchestrator
    event = LearningEvent(
        event_type=EventType.PLAN_APPROVED,
        component="PlanningOrchestrator",
        metadata={"plan_id": "feature-xyz", "phases": 4}
    )
    collector.capture_event(event)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Version: 1.0.0 (Phase 1 - Event Infrastructure)
"""

__version__ = "1.0.0"
__author__ = "Asif Hussain"

from src.learning.event_collector import LearningEventCollector
from src.learning.event_taxonomy import EventType, EventTier, LearningEvent

__all__ = [
    "LearningEventCollector",
    "EventType",
    "EventTier",
    "LearningEvent",
]
