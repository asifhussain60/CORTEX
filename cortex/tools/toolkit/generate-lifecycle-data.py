#!/usr/bin/env python3
"""
Data generator for request lifecycle Sankey diagram.

Generates dynamic flow data showing requests through CORTEX processing
stages with volume and outcome distributions.

Usage:
    python generate-lifecycle-data.py > lifecycle-data.json
"""

import json
from dataclasses import asdict, dataclass
from enum import Enum
from typing import List, Optional


class StageType(str, Enum):
    """Processing stages in the request lifecycle."""
    INTAKE = "Intake"
    VALIDATION = "Validation"
    CLASSIFICATION = "Classification"
    APPROVAL = "Approval"
    EXECUTION = "Execution"
    RESULTS = "Results"
    FINAL = "Final"


class OutcomeType(str, Enum):
    """Possible outcomes at each stage."""
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"
    RETRY = "retry"


@dataclass
class Node:
    """Represents a node in the Sankey diagram."""
    id: int
    name: str
    stage: str
    color: str
    volume: Optional[int] = None


@dataclass
class Link:
    """Represents a link between nodes in the Sankey."""
    source: int
    target: int
    value: int


class LifecycleDataGenerator:
    """Generates request lifecycle flow data."""

    NODES_DATA = [
        # Intake Stage (0)
        (0, "📥 Request", StageType.INTAKE, "#1976D2", 1000),

        # Validation Stage (1-2)
        (1, "✅ Validated", StageType.VALIDATION, "#1976D2", 950),
        (2, "❌ Invalid Input", StageType.VALIDATION, "#D32F2F", 50),

        # Classification Stage (3-4)
        (3, "🧭 Classified", StageType.CLASSIFICATION, "#0097A7", 900),
        (4, "❓ Ambiguous", StageType.CLASSIFICATION, "#FFA000", 50),

        # Approval Stage (5-7)
        (5, "⏳ Awaiting Approval", StageType.APPROVAL, "#0097A7", 945),
        (6, "✅ Approved", StageType.APPROVAL, "#388E3C", 850),
        (7, "❌ Rejected", StageType.APPROVAL, "#D32F2F", 50),

        # Execution Stage (8-9)
        (8, "⚙️ Executing", StageType.EXECUTION, "#0097A7", 800),
        (9, "⚠️ In Progress", StageType.EXECUTION, "#FFA000", 50),

        # Results Stage (10-13)
        (10, "✅ Completed", StageType.RESULTS, "#388E3C", 750),
        (11, "⚠️ Partial Success", StageType.RESULTS, "#FFA000", 60),
        (12, "❌ Failed", StageType.RESULTS, "#D32F2F", 22),
        (13, "🔄 Retry Queue", StageType.RESULTS, "#FFA000", 20),

        # Final Stage (14-15)
        (14, "📤 Delivered", StageType.FINAL, "#388E3C", 750),
        (15, "📧 Notified", StageType.FINAL, "#0097A7", 172),
    ]

    LINKS_DATA = [
        # Validation flows
        (0, 1, 950),
        (0, 2, 50),

        # Classification flows
        (1, 3, 900),
        (1, 4, 50),

        # Re-validation of ambiguous
        (4, 3, 45),
        (4, 2, 5),

        # Approval flows
        (3, 5, 900),

        # Approval decisions
        (5, 6, 850),
        (5, 7, 50),

        # Execution
        (6, 8, 800),
        (6, 9, 50),

        # Execution outcomes
        (8, 10, 750),
        (8, 11, 30),
        (8, 12, 20),

        (9, 11, 30),
        (9, 13, 20),

        # Retries
        (13, 8, 18),
        (13, 12, 2),

        # Final delivery
        (10, 14, 750),
        (11, 15, 60),
        (12, 15, 22),
        (2, 15, 50),
        (7, 15, 50),
    ]

    def generate(self) -> dict:
        """Generate the complete lifecycle data structure."""
        nodes = [Node(id=n[0], name=n[1], stage=n[2].value, color=n[3], volume=n[4])
                 for n in self.NODES_DATA]

        links = [Link(source=l[0], target=l[1], value=l[2])
                for l in self.LINKS_DATA]

        # Calculate statistics
        total_volume = sum(link.value for link in links if link.source == 0)
        success_volume = sum(link.value for link in links if link.target == 14)
        failure_volume = sum(link.value for link in links if "Failed" in nodes[link.target].name)

        return {
            "title": "Request Lifecycle Sankey Diagram",
            "description": "Flow of requests through CORTEX processing stages",
            "metadata": {
                "total_requests": total_volume,
                "successful_requests": success_volume,
                "failed_requests": failure_volume,
                "success_rate": f"{(success_volume / total_volume * 100):.1f}%",
                "stages": [stage.value for stage in StageType],
            },
            "nodes": [asdict(node) for node in nodes],
            "links": [asdict(link) for link in links],
        }


def main():
    """Generate and output lifecycle data."""
    generator = LifecycleDataGenerator()
    data = generator.generate()

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
