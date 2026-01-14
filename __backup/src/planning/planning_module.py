"""
PlanningModule: Optional module for phase-based planning and orchestration

This module is OPTIONAL and only loaded when users explicitly enable planning features.
The core CORTEX orchestrators function completely independently of this module.

Responsibility: Manage phase lifecycle, state transitions, and planning artifacts.

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class PhaseLifecycle(Enum):
    """Phase states"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass
class PhaseDefinition:
    """Definition of a single phase"""
    number: int
    name: str
    description: str
    duration_weeks: int
    ac_ids: List[str]
    dependencies: List[int]  # Phase numbers this depends on
    gate_threshold: float  # Completion percentage required to progress


class PlanningModule:
    """Optional planning and phase management for CORTEX"""

    # Phase definitions (isolated from core orchestrators)
    phase_lifecycle = {
        1: PhaseDefinition(
            number=1,
            name="Foundation Enhancement",
            description="Build core infrastructure",
            duration_weeks=2,
            ac_ids=["AC-AUDIT-001", "AC-GOV-001", "AC-STATE-001", "AC-LIFECYCLE-001", "AC-EVIDENCE-001", "AC-SECURITY-001"],
            dependencies=[],
            gate_threshold=0.88
        ),
        2: PhaseDefinition(
            number=2,
            name="Orchestration Core",
            description="Implement default working mechanism",
            duration_weeks=2,
            ac_ids=["AC-ORCH-001", "AC-TODO-001", "AC-TDD-001", "AC-PLAN-001"],
            dependencies=[1],
            gate_threshold=0.85
        ),
        3: PhaseDefinition(
            number=3,
            name="Feature Orchestrators",
            description="Build specialized orchestrators",
            duration_weeks=2,
            ac_ids=["AC-ADO-001", "AC-VAC-001", "AC-INV-001"],
            dependencies=[2],
            gate_threshold=0.80
        ),
        4: PhaseDefinition(
            number=4,
            name="Intelligence Layer",
            description="Add intelligence and learning",
            duration_weeks=2,
            ac_ids=["AC-LLM-001", "AC-VISION-001", "AC-KNOW-001"],
            dependencies=[3],
            gate_threshold=0.75
        ),
        5: PhaseDefinition(
            number=5,
            name="CORTEX Cleanup & Decommission",
            description="Remove scaffolding",
            duration_weeks=2,
            ac_ids=["AC-CLEAN-301", "AC-CLEAN-302", "AC-CLEAN-303"],
            dependencies=[4],
            gate_threshold=1.0
        ),
    }

    # Phase gates and completion criteria
    phase_gates = {
        1: {
            'name': 'Foundation Verification',
            'threshold': 0.88,
            'criteria': [
                'All audit tests passing',
                'Governance rules enforced',
                'State manager operational',
                '30+/34 AC-IDs verified'
            ]
        },
        2: {
            'name': 'Orchestration Readiness',
            'threshold': 0.85,
            'criteria': [
                'MasterOrchestrator functional',
                'TodoManager tracking tasks',
                'TDD-Master implementation complete',
                'Planning system initialized'
            ]
        },
        3: {
            'name': 'Feature Completeness',
            'threshold': 0.80,
            'criteria': [
                'All feature orchestrators deployed',
                'Cross-orchestrator integration verified',
                'CLI tooling operational'
            ]
        },
        4: {
            'name': 'Intelligence Validation',
            'threshold': 0.75,
            'criteria': [
                'LLM integration tested',
                'Knowledge graph built',
                'Pattern recognition working'
            ]
        },
        5: {
            'name': 'Decommission Verification',
            'threshold': 1.0,
            'criteria': [
                'Zero phase references in production code',
                'All scaffolding removed',
                'Performance baseline met'
            ]
        },
    }

    # State transition rules
    state_transitions = {
        'phase_1_to_2': {
            'trigger': 'foundation_complete',
            'required_gates': [1],
            'actions': ['initialize_orchestration', 'load_core_workflow']
        },
        'phase_2_to_3': {
            'trigger': 'orchestration_complete',
            'required_gates': [1, 2],
            'actions': ['initialize_features', 'deploy_orchestrators']
        },
        'phase_3_to_4': {
            'trigger': 'features_complete',
            'required_gates': [1, 2, 3],
            'actions': ['initialize_intelligence', 'build_knowledge_graph']
        },
        'phase_4_to_5': {
            'trigger': 'intelligence_complete',
            'required_gates': [1, 2, 3, 4],
            'actions': ['initialize_cleanup', 'extract_phase_logic']
        },
    }

    @classmethod
    def get_current_phase(cls, phase_number: int) -> Optional[PhaseDefinition]:
        """Get definition for a specific phase"""
        return cls.phase_lifecycle.get(phase_number)

    @classmethod
    def get_phase_gate(cls, phase_number: int) -> Optional[Dict]:
        """Get gate criteria for a phase"""
        return cls.phase_gates.get(phase_number)

    @classmethod
    def check_phase_completion(cls, phase_number: int, completion_rate: float) -> bool:
        """Check if phase completion rate meets gate threshold"""
        phase = cls.phase_lifecycle.get(phase_number)
        if not phase:
            return False
        return completion_rate >= phase.gate_threshold

    @classmethod
    def get_transition_rule(cls, from_phase: int, to_phase: int) -> Optional[Dict]:
        """Get state transition rules between phases"""
        key = f'phase_{from_phase}_to_{to_phase}'
        return cls.state_transitions.get(key)
