"""
Integration test: Render actual phase detail page.

Authority: PHASE-STORY-SYSTEM-COMPREHENSIVE.yaml (ENH-032)
Phase: Phase 1 - Template System
Purpose: Generate real HTML file from PhaseDetail data
"""

import pytest
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from cortex.models.phase_detail_schema import (
    PhaseDetail, PhaseStatus, ImpactLevel,
    MermaidDiagram, Feature, CodeFile,
    ArchitectureSection, ImplementationSection, TestingSection,
    ComplianceRule, ImpactMetrics, StoryContext,
    TechnicalDecision, Lesson
)


# Paths - resolve from workspace root (go up 2 levels from tests/integration/)
_workspace_root = Path(__file__).parent.parent.parent
TEMPLATE_DIR = _workspace_root / "cortex-registry/_cortex-master/dashboard/templates"
OUTPUT_DIR = _workspace_root / "cortex-registry/_cortex-master/dashboard/phases"


@pytest.fixture
def phase_01_data():
    """Phase 01: Orchestrator Event Bus (actual data)."""
    return PhaseDetail(
        phase_id="phase-01",
        title="Orchestrator Event Bus",
        status=PhaseStatus.COMPLETED,
        completion_date="2026-01-15",
        overview=(
            "Phase 1 established the event-driven communication backbone for CORTEX. "
            "The OrchestratorEventBus enables decoupled orchestrator communication through "
            "a publish-subscribe pattern, eliminating direct dependencies and enabling "
            "event replay for debugging."
        ),
        objectives=[
            "Implement publish-subscribe messaging pattern",
            "Decouple orchestrators via event-driven architecture",
            "Enable event history tracking for debugging",
            "Support dead letter queue for failed events",
            "Achieve zero direct orchestrator dependencies"
        ],
        key_features=[
            Feature(
                name="Event Publishing",
                description="Orchestrators publish typed events to central bus with metadata",
                status="IMPLEMENTED",
                test_coverage=1.0
            ),
            Feature(
                name="Event Subscription",
                description="Pattern-based subscription with filtering and ordering",
                status="IMPLEMENTED",
                test_coverage=0.98
            ),
            Feature(
                name="Event History",
                description="Complete audit trail of all events for replay and debugging",
                status="IMPLEMENTED",
                test_coverage=0.95
            ),
            Feature(
                name="Dead Letter Queue",
                description="Automatic handling of events that fail processing",
                status="IMPLEMENTED",
                test_coverage=0.92
            )
        ],
        architecture=ArchitectureSection(
            overview=(
                "The event bus follows a hub-and-spoke architecture with the EventBus as "
                "the central message broker. Publishers send events without knowing subscribers. "
                "Subscribers register interest in event types and receive notifications asynchronously."
            ),
            diagrams=[
                MermaidDiagram(
                    type="architecture",
                    title="Event Bus Architecture",
                    mermaid_code="""graph TD
    A[InteractionOrchestrator] -->|INTENT_CLASSIFIED| B[EventBus]
    C[PlanningOrchestrator] -->|PLANNING_REQUIRED| B
    D[TDDOrchestrator] -->|IMPLEMENTATION_COMPLETE| B
    B -->|subscribe| E[ReviewOrchestrator]
    B -->|subscribe| F[AuditLogger]
    B -->|subscribe| G[MetricsCollector]
    B --> H[EventHistory]
    B --> I[DeadLetterQueue]"""
                ),
                MermaidDiagram(
                    type="workflow",
                    title="Event Publishing Flow",
                    mermaid_code="""sequenceDiagram
    participant Publisher
    participant EventBus
    participant Subscriber1
    participant Subscriber2
    Publisher->>EventBus: publish(event)
    EventBus->>EventHistory: store(event)
    EventBus->>Subscriber1: notify(event)
    EventBus->>Subscriber2: notify(event)
    Subscriber1-->>EventBus: ACK
    Subscriber2-->>EventBus: ACK"""
                )
            ],
            components=[
                "OrchestratorEventBus",
                "EventPublisher",
                "EventSubscriber",
                "EventHistory",
                "DeadLetterQueue"
            ],
            design_patterns=[
                "Publish-Subscribe",
                "Observer",
                "Message Queue",
                "Dead Letter Queue"
            ]
        ),
        implementation_details=ImplementationSection(
            files=[
                CodeFile(
                    path="cortex/infrastructure/orchestrator_event_bus.py",
                    lines_of_code=520,
                    purpose="Core event bus implementation with pub/sub logic",
                    language="Python",
                    test_file="tests/unit/infrastructure/test_orchestrator_event_bus.py",
                    complexity_score=8.5
                ),
                CodeFile(
                    path="cortex/orchestrators/core/interaction_orchestrator_enhancement.py",
                    lines_of_code=180,
                    purpose="InteractionOrchestrator event subscription integration",
                    language="Python",
                    test_file="tests/unit/orchestrators/core/test_interaction_enhancement.py",
                    complexity_score=6.2
                )
            ],
            total_loc=700,
            tier=1,
            priority=1,
            dependencies=[]
        ),
        testing=TestingSection(
            test_count=32,
            test_pass_rate=1.0,
            coverage=0.94,
            test_file="tests/unit/infrastructure/test_orchestrator_event_bus.py",
            test_scenarios=[
                "Event publishing to multiple subscribers",
                "Subscription filtering by event type",
                "Event history tracking and replay",
                "Dead letter queue for failed events",
                "Concurrent event processing",
                "Subscription ordering guarantees"
            ]
        ),
        compliance=[
            ComplianceRule(
                rule="CORE-008",
                description="TDD-first development: tests written before implementation",
                status="COMPLIANT"
            ),
            ComplianceRule(
                rule="CORE-011",
                description="Type hints mandatory for all public APIs",
                status="COMPLIANT"
            ),
            ComplianceRule(
                rule="CORE-027",
                description="Audit trail via event history",
                status="COMPLIANT"
            )
        ],
        impact=ImpactMetrics(
            extensibility=ImpactLevel.HIGH,
            scalability=ImpactLevel.HIGH,
            maintainability=ImpactLevel.HIGH,
            description=(
                "Event-driven architecture enables future orchestrators to communicate "
                "without code changes. Scalability achieved through async processing. "
                "Maintainability improved by removing direct orchestrator dependencies."
            )
        ),
        story_context=StoryContext(
            previous_phase=None,
            next_phase="phase-02",
            narrative=(
                "Phase 1 marked the foundation of CORTEX's decoupled architecture. "
                "Before this, orchestrators called each other directly, creating tight coupling. "
                "The event bus breakthrough came after realizing the InteractionOrchestrator "
                "needed to coordinate multiple orchestrators without knowing their implementations."
            ),
            related_enhancements=["ENH-013", "ENH-014"],
            theme="Foundation Building"
        ),
        technical_decisions=[
            TechnicalDecision(
                title="Publish-Subscribe over Direct Orchestrator Calls",
                chosen="Publish-Subscribe pattern via centralized EventBus",
                rejected=[
                    "Direct method calls between orchestrators",
                    "REST API calls between orchestrators",
                    "Shared database for coordination"
                ],
                rationale=(
                    "Direct calls created tight coupling and made testing difficult. "
                    "Pub/sub enables future orchestrators to join without modifying existing code. "
                    "Event history provides debugging capabilities impossible with direct calls."
                ),
                tradeoffs=(
                    "Trade slight latency (~5ms per event) for massive flexibility gain. "
                    "Asynchronous processing requires careful handling of event ordering."
                ),
                date="2026-01-10"
            ),
            TechnicalDecision(
                title="In-Memory Event Bus vs Message Broker",
                chosen="In-memory Python implementation",
                rejected=[
                    "Redis pub/sub",
                    "RabbitMQ",
                    "Kafka"
                ],
                rationale=(
                    "CORTEX runs as single process per user workspace. External message broker "
                    "adds deployment complexity without scalability benefit. In-memory provides "
                    "<1ms latency for local orchestrator communication."
                ),
                tradeoffs=(
                    "Events lost on process restart (acceptable for development tool). "
                    "Cannot distribute orchestrators across processes (not a requirement)."
                ),
                date="2026-01-12"
            )
        ],
        lessons_learned=[
            Lesson(
                title="Event Ordering Requires Careful Design",
                description=(
                    "Initially, events arrived out of order when multiple orchestrators published "
                    "simultaneously. Added event sequence numbers and subscription ordering guarantees."
                ),
                category="ARCHITECTURE",
                recommendation=(
                    "Design event schemas with ordering in mind. Use timestamps and sequence numbers. "
                    "Document ordering guarantees in API."
                )
            ),
            Lesson(
                title="Dead Letter Queue Prevents Silent Failures",
                description=(
                    "Early testing showed events silently failing when subscribers raised exceptions. "
                    "Dead letter queue catches failed events for manual retry."
                ),
                category="RELIABILITY",
                recommendation=(
                    "Always implement dead letter queues for async message systems. "
                    "Include retry count and failure reason in dead letter metadata."
                )
            )
        ],
        git_tag="v1.0.0-phase01",
        author="Asif Hussain",
        created_date="2026-01-15"
    )


def test_render_phase_01_html(phase_01_data):
    """Integration test: Render Phase 01 detail page."""
    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("phase-detail.html")
    
    # Render template with Phase 01 data
    context = phase_01_data.to_html_context()
    html = template.render(**context)
    
    # Validate HTML structure
    assert "<!DOCTYPE html>" in html
    assert "<html" in html
    assert "</html>" in html
    
    # Validate title and meta
    assert "Orchestrator Event Bus" in html
    assert "phase-01" in html
    assert "COMPLETED" in html
    
    # Validate all tabs present
    assert "Overview" in html
    assert "Architecture" in html
    assert "Implementation" in html
    assert "Testing" in html
    assert "Impact" in html
    
    # Validate Mermaid diagrams present
    assert "graph TD" in html  # Architecture diagram
    assert "sequenceDiagram" in html  # Workflow diagram
    
    # Write output file (optional - for manual inspection)
    output_path = OUTPUT_DIR / "phase-01"
    output_path.mkdir(parents=True, exist_ok=True)
    
    with open(output_path / "index.html", "w") as f:
        f.write(html)
    
    print(f"\n✅ Phase 01 detail page generated: {output_path / 'index.html'}")
    print(f"   Size: {len(html)} bytes")
    print(f"   Objectives: {len(phase_01_data.objectives)}")
    print(f"   Features: {len(phase_01_data.key_features)}")
    print(f"   Diagrams: {len(phase_01_data.architecture.diagrams)}")
    print(f"   Tests: {phase_01_data.testing.test_count}")
    
    # Validate file was written
    assert (output_path / "index.html").exists()
    assert (output_path / "index.html").stat().st_size > 10000  # At least 10KB


def test_validate_html_structure(phase_01_data):
    """Validate generated HTML has proper structure."""
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("phase-detail.html")
    context = phase_01_data.to_html_context()
    html = template.render(**context)
    
    # Check essential HTML elements
    assert html.count("<head>") == 1
    assert html.count("</head>") == 1
    assert html.count("<body>") == 1
    assert html.count("</body>") == 1
    
    # Check navigation elements
    assert html.count("class=\"breadcrumb\"") >= 1
    assert html.count("class=\"phase-navigation\"") >= 1
    
    # Check tab structure
    assert html.count("class=\"tab-button") >= 5  # 5 tabs
    assert html.count("class=\"tab-content") >= 5  # 5 content sections
    
    # Check Mermaid.js inclusion
    assert "mermaid.initialize" in html
    assert "cdn.jsdelivr.net/npm/mermaid" in html


def test_phase_completion_metrics(phase_01_data):
    """Validate PhaseDetail helper methods work correctly."""
    # Test diagram count
    assert phase_01_data.get_diagram_count() == 2
    
    # Test coverage percentage
    assert phase_01_data.get_test_coverage_percentage() == 94
    
    # Test documentation completeness
    assert phase_01_data.has_complete_documentation() is True
    
    # Test completion percentage (11 sections defined)
    completion = phase_01_data.get_completion_percentage()
    assert completion > 90  # Should be nearly complete


if __name__ == "__main__":
    # Allow running directly for quick testing
    import sys
    from cortex.models.phase_detail_schema import PhaseDetail
    
    # Create phase data
    phase = phase_01_data()
    
    # Render
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("phase-detail.html")
    context = phase.to_html_context()
    html = template.render(**context)
    
    # Write file
    output_path = OUTPUT_DIR / "phase-01"
    output_path.mkdir(parents=True, exist_ok=True)
    with open(output_path / "index.html", "w") as f:
        f.write(html)
    
    print(f"✅ Generated: {output_path / 'index.html'}")
    print(f"   Open: file://{output_path.absolute() / 'index.html'}")
