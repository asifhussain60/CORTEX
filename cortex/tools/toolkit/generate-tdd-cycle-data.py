#!/usr/bin/env python3
"""
Data generator for TDD knowledge cycle visualization.

Generates dynamic data showing the continuous TDD cycle phases,
transitions, and accumulated knowledge.

Usage:
    python generate-tdd-cycle-data.py > tdd-cycle-data.json
"""

import json
from dataclasses import dataclass, asdict
from typing import List
from enum import Enum


class PhaseType(str, Enum):
    """TDD cycle phases."""
    LEARN = "Learn"
    RED = "Red"
    GREEN = "Green"
    REFACTOR = "Refactor"


class MetricType(str, Enum):
    """Metrics tracked through the cycle."""
    TEST_COUNT = "test_count"
    COVERAGE = "coverage"
    CODE_QUALITY = "code_quality"
    KNOWLEDGE = "knowledge"
    VELOCITY = "velocity"


@dataclass
class Phase:
    """Represents a phase in the TDD cycle."""
    name: str
    phase_type: str
    emoji: str
    color: str
    description: str
    key_activities: List[str]
    duration_estimate: str
    success_criteria: List[str]


@dataclass
class Transition:
    """Represents a transition between phases."""
    from_phase: str
    to_phase: str
    action: str
    condition: str


@dataclass
class KnowledgeAccumulation:
    """Tracks knowledge gained through a cycle."""
    iteration: int
    phase: str
    knowledge_gained: str
    metric_improvement: dict


class TDDCycleDataGenerator:
    """Generates TDD knowledge cycle data."""

    PHASES_DATA = [
        {
            "name": "📚 Learn",
            "phase_type": "Learn",
            "emoji": "📚",
            "color": "#1976D2",
            "description": "Understand requirements and design",
            "key_activities": [
                "Read specifications",
                "Understand use cases",
                "Design architecture",
                "Plan test cases"
            ],
            "duration_estimate": "15-30 mins",
            "success_criteria": [
                "Requirements understood",
                "Architecture designed",
                "Test plan documented"
            ]
        },
        {
            "name": "❌ Red",
            "phase_type": "Red",
            "emoji": "❌",
            "color": "#D32F2F",
            "description": "Write failing tests first",
            "key_activities": [
                "Create test skeleton",
                "Define assertions",
                "Run tests (fail)",
                "Understand failure"
            ],
            "duration_estimate": "10-20 mins",
            "success_criteria": [
                "All tests fail",
                "Failure is understood",
                "Test coverage is clear"
            ]
        },
        {
            "name": "✅ Green",
            "phase_type": "Green",
            "emoji": "✅",
            "color": "#4CAF50",
            "description": "Implement to pass tests",
            "key_activities": [
                "Write minimal code",
                "Run tests (pass)",
                "Verify all tests pass",
                "Check coverage"
            ],
            "duration_estimate": "20-40 mins",
            "success_criteria": [
                "All tests pass",
                "Coverage > 80%",
                "No regressions"
            ]
        },
        {
            "name": "🔧 Refactor",
            "phase_type": "Refactor",
            "emoji": "🔧",
            "color": "#FFC107",
            "description": "Improve and optimize code",
            "key_activities": [
                "Remove duplication",
                "Improve clarity",
                "Optimize performance",
                "Update documentation"
            ],
            "duration_estimate": "15-25 mins",
            "success_criteria": [
                "Code quality improved",
                "All tests still pass",
                "Documentation updated"
            ]
        }
    ]

    TRANSITIONS_DATA = [
        {
            "from_phase": "Learn",
            "to_phase": "Red",
            "action": "Create failing tests",
            "condition": "Requirements are clear"
        },
        {
            "from_phase": "Red",
            "to_phase": "Green",
            "action": "Implement functionality",
            "condition": "Tests are failing"
        },
        {
            "from_phase": "Green",
            "to_phase": "Refactor",
            "action": "Improve code quality",
            "condition": "Tests are passing"
        },
        {
            "from_phase": "Refactor",
            "to_phase": "Learn",
            "action": "Start new feature cycle",
            "condition": "Feature is complete"
        }
    ]

    KNOWLEDGE_ACCUMULATION = [
        {
            "iteration": 1,
            "phase": "Red",
            "knowledge_gained": "Understanding of failure modes",
            "metric_improvement": {
                "test_count": 5,
                "coverage": 0,
                "code_quality": 0,
                "knowledge": 20
            }
        },
        {
            "iteration": 1,
            "phase": "Green",
            "knowledge_gained": "Basic implementation patterns",
            "metric_improvement": {
                "test_count": 5,
                "coverage": 60,
                "code_quality": 40,
                "knowledge": 30
            }
        },
        {
            "iteration": 1,
            "phase": "Refactor",
            "knowledge_gained": "Code organization principles",
            "metric_improvement": {
                "test_count": 5,
                "coverage": 85,
                "code_quality": 75,
                "knowledge": 15
            }
        },
        {
            "iteration": 2,
            "phase": "Red",
            "knowledge_gained": "Advanced test patterns",
            "metric_improvement": {
                "test_count": 12,
                "coverage": 85,
                "code_quality": 75,
                "knowledge": 25
            }
        },
        {
            "iteration": 2,
            "phase": "Green",
            "knowledge_gained": "Design pattern application",
            "metric_improvement": {
                "test_count": 12,
                "coverage": 92,
                "code_quality": 85,
                "knowledge": 30
            }
        }
    ]

    def generate(self) -> dict:
        """Generate the complete TDD cycle data structure."""
        phases = [Phase(
            name=p["name"],
            phase_type=p["phase_type"],
            emoji=p["emoji"],
            color=p["color"],
            description=p["description"],
            key_activities=p["key_activities"],
            duration_estimate=p["duration_estimate"],
            success_criteria=p["success_criteria"]
        ) for p in self.PHASES_DATA]

        transitions = [Transition(
            from_phase=t["from_phase"],
            to_phase=t["to_phase"],
            action=t["action"],
            condition=t["condition"]
        ) for t in self.TRANSITIONS_DATA]

        knowledge = [KnowledgeAccumulation(
            iteration=k["iteration"],
            phase=k["phase"],
            knowledge_gained=k["knowledge_gained"],
            metric_improvement=k["metric_improvement"]
        ) for k in self.KNOWLEDGE_ACCUMULATION]

        # Calculate aggregate metrics
        total_iterations = max(k.iteration for k in knowledge)
        total_knowledge = sum(k.metric_improvement["knowledge"] for k in knowledge)
        avg_coverage = sum(k.metric_improvement["coverage"] for k in knowledge) / len(knowledge)

        return {
            "title": "TDD Knowledge Cycle",
            "description": "Continuous learning through Test-Driven Development",
            "metrics": {
                "total_iterations": total_iterations,
                "total_knowledge_gained": total_knowledge,
                "average_coverage": f"{avg_coverage:.1f}%",
                "phases_count": len(phases),
            },
            "phases": [asdict(phase) for phase in phases],
            "transitions": [asdict(t) for t in transitions],
            "knowledge_accumulation": [asdict(k) for k in knowledge],
        }


def main():
    """Generate and output TDD cycle data."""
    generator = TDDCycleDataGenerator()
    data = generator.generate()

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
