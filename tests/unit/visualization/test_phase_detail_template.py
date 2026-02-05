"""
Tests for phase detail HTML template rendering.

Authority: PHASE-STORY-SYSTEM-COMPREHENSIVE.yaml (ENH-032)
Phase: Phase 1 - Template System
Purpose: Validate template renders correctly with PhaseDetail data
"""

import pytest
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from cortex.models.phase_detail_schema import (
    PhaseDetail, PhaseStatus, ImpactLevel,
    MermaidDiagram, Feature, CodeFile,
    ArchitectureSection, ImplementationSection, TestingSection,
    ComplianceRule, ImpactMetrics, StoryContext,
    TechnicalDecision, Lesson
)


# Template path
TEMPLATE_DIR = Path(__file__).parent.parent.parent.parent / "cortex-registry/_cortex-master/dashboard/templates"


@pytest.fixture
def jinja_env():
    """Create Jinja2 environment with template directory."""
    return Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


@pytest.fixture
def sample_phase_detail():
    """Create comprehensive PhaseDetail for testing."""
    return PhaseDetail(
        phase_id="phase-01",
        title="Orchestrator Event Bus",
        status=PhaseStatus.COMPLETED,
        completion_date="2026-01-15",
        overview="Event-driven communication backbone for orchestrator decoupling",
        objectives=[
            "Implement publish-subscribe pattern",
            "Decouple orchestrators via events",
            "Enable event replay for debugging"
        ],
        key_features=[
            Feature(
                name="Event Publishing",
                description="Orchestrators publish events to central bus",
                status="IMPLEMENTED",
                test_coverage=1.0
            ),
            Feature(
                name="Event Subscription",
                description="Orchestrators subscribe to event types",
                status="IMPLEMENTED",
                test_coverage=0.95
            )
        ],
        architecture=ArchitectureSection(
            overview="Event-driven architecture with central message bus",
            diagrams=[
                MermaidDiagram(
                    type="architecture",
                    title="Event Bus Architecture",
                    mermaid_code="""graph LR
    A[Publisher] -->|publish| B[EventBus]
    B -->|subscribe| C[Subscriber1]
    B -->|subscribe| D[Subscriber2]"""
                )
            ],
            components=["EventBus", "EventPublisher", "EventSubscriber"],
            design_patterns=["Publish-Subscribe", "Observer", "Message Queue"]
        ),
        implementation_details=ImplementationSection(
            files=[
                CodeFile(
                    path="cortex/infrastructure/orchestrator_event_bus.py",
                    lines_of_code=450,
                    purpose="Core event bus implementation",
                    language="Python",
                    test_file="tests/unit/infrastructure/test_orchestrator_event_bus.py",
                    complexity_score=8.2
                )
            ],
            total_loc=450,
            tier=1,
            priority=1,
            dependencies=[]
        ),
        testing=TestingSection(
            test_count=25,
            test_pass_rate=1.0,
            coverage=0.92,
            test_file="tests/unit/infrastructure/test_orchestrator_event_bus.py",
            test_scenarios=[
                "Event publishing and subscription",
                "Event history tracking",
                "Dead letter queue handling"
            ]
        ),
        compliance=[
            ComplianceRule(
                rule="CORE-008",
                description="TDD-first development",
                status="COMPLIANT"
            )
        ],
        impact=ImpactMetrics(
            extensibility=ImpactLevel.HIGH,
            scalability=ImpactLevel.HIGH,
            maintainability=ImpactLevel.HIGH,
            description="Enables decoupled orchestrator communication"
        ),
        story_context=StoryContext(
            previous_phase=None,
            next_phase="phase-02",
            narrative="Phase 1 established event-driven foundation",
            related_enhancements=["ENH-001"],
            theme="Foundation Building"
        ),
        technical_decisions=[
            TechnicalDecision(
                title="Publish-Subscribe over Direct Calls",
                chosen="Publish-Subscribe pattern via EventBus",
                rejected=["Direct method calls", "REST API calls"],
                rationale="Decouples orchestrators, enables replay",
                tradeoffs="Slight latency vs massive flexibility gain",
                date="2026-01-10"
            )
        ],
        lessons_learned=[
            Lesson(
                title="Event Ordering Matters",
                description="Order of event subscription affects behavior",
                category="ARCHITECTURE",
                recommendation="Document subscription order requirements"
            )
        ],
        git_tag="v1.0.0-phase01",
        author="Asif Hussain",
        created_date="2026-01-15"
    )


def test_template_exists(jinja_env):
    """Test: Template file exists and can be loaded."""
    try:
        template = jinja_env.get_template("phase-detail.html")
        assert template is not None
        assert "phase-detail.html" in template.name
    except TemplateNotFound:
        pytest.fail("phase-detail.html template not found")


def test_template_renders_basic_fields(jinja_env, sample_phase_detail):
    """Test: Template renders basic phase information."""
    template = jinja_env.get_template("phase-detail.html")
    context = sample_phase_detail.to_html_context()
    
    html = template.render(**context)
    
    # Check title renders
    assert "Orchestrator Event Bus" in html
    assert "phase-01" in html
    
    # Check status badge renders
    assert "COMPLETED" in html or "completed" in html.lower()
    
    # Check completion date renders
    assert "2026-01-15" in html


def test_template_renders_overview_tab(jinja_env, sample_phase_detail):
    """Test: Overview tab renders with objectives and features."""
    template = jinja_env.get_template("phase-detail.html")
    context = sample_phase_detail.to_html_context()
    
    html = template.render(**context)
    
    # Check overview text
    assert "Event-driven communication" in html
    
    # Check objectives render
    assert "Implement publish-subscribe" in html
    assert "Decouple orchestrators" in html
    
    # Check features render
    assert "Event Publishing" in html
    assert "Event Subscription" in html


def test_template_renders_architecture_tab(jinja_env, sample_phase_detail):
    """Test: Architecture tab renders with diagrams."""
    template = jinja_env.get_template("phase-detail.html")
    context = sample_phase_detail.to_html_context()
    
    html = template.render(**context)
    
    # Check architecture overview
    assert "Event-driven architecture" in html
    
    # Check components render
    assert "EventBus" in html
    assert "EventPublisher" in html
    
    # Check diagram renders (Mermaid code should be in HTML)
    assert "graph LR" in html  # Mermaid diagram code
    assert "class=\"mermaid\"" in html  # Mermaid container
    
    # Check design patterns
    assert "Publish-Subscribe" in html


def test_template_renders_implementation_tab(jinja_env, sample_phase_detail):
    """Test: Implementation tab renders with file details."""
    template = jinja_env.get_template("phase-detail.html")
    context = sample_phase_detail.to_html_context()
    
    html = template.render(**context)
    
    # Check metrics render
    assert "450" in html  # Total LOC
    assert "Tier 1" in html or "tier 1" in html.lower()
    
    # Check file details render
    assert "orchestrator_event_bus.py" in html
    assert "Core event bus implementation" in html


def test_template_renders_testing_tab(jinja_env, sample_phase_detail):
    """Test: Testing tab renders with test metrics."""
    template = jinja_env.get_template("phase-detail.html")
    context = sample_phase_detail.to_html_context()
    
    html = template.render(**context)
    
    # Check test metrics render
    assert "25" in html  # Test count
    assert "100%" in html  # Pass rate (1.0 * 100)
    assert "92%" in html  # Coverage (0.92 * 100)
    
    # Check test scenarios render
    assert "Event publishing and subscription" in html
    assert "Dead letter queue" in html


def test_template_renders_impact_tab(jinja_env, sample_phase_detail):
    """Test: Impact tab renders with impact metrics."""
    template = jinja_env.get_template("phase-detail.html")
    context = sample_phase_detail.to_html_context()
    
    html = template.render(**context)
    
    # Check impact metrics render
    assert "HIGH" in html  # Should appear 3 times (extensibility, scalability, maintainability)
    
    # Check impact description
    assert "decoupled orchestrator" in html


def test_template_renders_technical_decisions(jinja_env, sample_phase_detail):
    """Test: Technical decisions render in Architecture tab."""
    template = jinja_env.get_template("phase-detail.html")
    context = sample_phase_detail.to_html_context()
    
    html = template.render(**context)
    
    # Check decision renders
    assert "Publish-Subscribe over Direct Calls" in html
    assert "Publish-Subscribe pattern via EventBus" in html
    assert "Direct method calls" in html  # Rejected option
    assert "Decouples orchestrators" in html


def test_template_renders_lessons_learned(jinja_env, sample_phase_detail):
    """Test: Lessons learned render in Testing tab."""
    template = jinja_env.get_template("phase-detail.html")
    context = sample_phase_detail.to_html_context()
    
    html = template.render(**context)
    
    # Check lesson renders
    assert "Event Ordering Matters" in html
    assert "Order of event subscription" in html
    assert "ARCHITECTURE" in html


def test_template_renders_compliance_rules(jinja_env, sample_phase_detail):
    """Test: Compliance rules render in Testing tab."""
    template = jinja_env.get_template("phase-detail.html")
    context = sample_phase_detail.to_html_context()
    
    html = template.render(**context)
    
    # Check compliance renders
    assert "CORE-008" in html
    assert "TDD-first" in html
    assert "COMPLIANT" in html


def test_template_renders_breadcrumb_navigation(jinja_env, sample_phase_detail):
    """Test: Breadcrumb navigation renders correctly."""
    template = jinja_env.get_template("phase-detail.html")
    context = sample_phase_detail.to_html_context()
    
    html = template.render(**context)
    
    # Check breadcrumb elements
    assert "Home" in html
    assert "Phases" in html
    assert "phase-01" in html
    assert "../../index.html" in html  # Link to dashboard


def test_template_renders_phase_navigation(jinja_env, sample_phase_detail):
    """Test: Previous/Next phase navigation renders."""
    template = jinja_env.get_template("phase-detail.html")
    context = sample_phase_detail.to_html_context()
    
    html = template.render(**context)
    
    # Check navigation buttons
    assert "All Phases" in html
    assert "Next Phase" in html
    assert "phase-02" in html  # Next phase link
    
    # Previous phase should not render (it's None)
    # But "Previous Phase" text might still be in template structure


def test_template_renders_tab_navigation(jinja_env, sample_phase_detail):
    """Test: Tab navigation buttons render."""
    template = jinja_env.get_template("phase-detail.html")
    context = sample_phase_detail.to_html_context()
    
    html = template.render(**context)
    
    # Check all 5 tabs render
    assert "Overview" in html
    assert "Architecture" in html
    assert "Implementation" in html
    assert "Testing" in html
    assert "Impact" in html
    
    # Check tab buttons have onclick handlers
    assert "switchTab" in html


def test_template_includes_mermaid_js(jinja_env, sample_phase_detail):
    """Test: Mermaid.js library is included."""
    template = jinja_env.get_template("phase-detail.html")
    context = sample_phase_detail.to_html_context()
    
    html = template.render(**context)
    
    # Check Mermaid.js script tag
    assert "mermaid" in html.lower()
    assert "cdn.jsdelivr.net/npm/mermaid" in html


def test_template_includes_font_awesome(jinja_env, sample_phase_detail):
    """Test: Font Awesome icons are included."""
    template = jinja_env.get_template("phase-detail.html")
    context = sample_phase_detail.to_html_context()
    
    html = template.render(**context)
    
    # Check Font Awesome stylesheet
    assert "font-awesome" in html.lower()
    assert "fa-" in html  # Font Awesome icon classes


def test_template_handles_empty_sections(jinja_env):
    """Test: Template handles phases with minimal data."""
    minimal_phase = PhaseDetail(
        phase_id="phase-99",
        title="Minimal Phase",
        status=PhaseStatus.PLANNED,
        completion_date=None,  # Not completed yet
        overview="Coming soon",
        objectives=[],
        key_features=[],
        architecture=None,
        implementation_details=None,
        testing=None,
        compliance=[],
        impact=None,
        story_context=None,
        technical_decisions=[],
        lessons_learned=[],
        git_tag=None,
        author="Asif Hussain",
        created_date="2026-02-05"
    )
    
    template = jinja_env.get_template("phase-detail.html")
    context = minimal_phase.to_html_context()
    
    # Should render without errors
    html = template.render(**context)
    
    assert "Minimal Phase" in html
    assert "phase-99" in html
    assert "PLANNED" in html or "planned" in html.lower()


def test_template_responsive_design(jinja_env, sample_phase_detail):
    """Test: Template includes responsive CSS."""
    template = jinja_env.get_template("phase-detail.html")
    context = sample_phase_detail.to_html_context()
    
    html = template.render(**context)
    
    # Check for mobile-friendly meta tag
    assert "viewport" in html
    assert "width=device-width" in html
    
    # Check for responsive CSS media queries
    assert "@media" in html
    assert "768px" in html  # Mobile breakpoint


def test_template_glassmorphism_styling(jinja_env, sample_phase_detail):
    """Test: Template uses glassmorphism design."""
    template = jinja_env.get_template("phase-detail.html")
    context = sample_phase_detail.to_html_context()
    
    html = template.render(**context)
    
    # Check for glassmorphism CSS properties
    assert "backdrop-filter" in html
    assert "blur" in html
    assert "linear-gradient" in html


def test_template_renders_with_to_html_context(sample_phase_detail):
    """Test: PhaseDetail.to_html_context() provides correct data."""
    context = sample_phase_detail.to_html_context()
    
    # Validate context structure
    assert context["phase_id"] == "phase-01"
    assert context["title"] == "Orchestrator Event Bus"
    assert context["status"] == "COMPLETED"
    assert len(context["objectives"]) == 3
    assert len(context["features"]) == 2
    assert context["architecture"] is not None
    assert context["implementation"] is not None
    assert context["testing"] is not None
    assert len(context["compliance"]) == 1
    assert context["impact"] is not None
    assert context["story"] is not None
    assert len(context["decisions"]) == 1
    assert len(context["lessons"]) == 1
