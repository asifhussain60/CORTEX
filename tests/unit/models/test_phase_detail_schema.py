"""
Tests for Phase Detail Schema
Tests data models for comprehensive phase detail pages

TDD Phase: RED (tests written first)
"""

import pytest
from datetime import datetime
from typing import List, Optional
from pydantic import ValidationError


def test_phase_detail_model_basic_fields():
    """Test PhaseDetail model with basic required fields"""
    from cortex.models.phase_detail_schema import PhaseDetail, PhaseStatus
    
    phase = PhaseDetail(
        phase_id="PHASE-01",
        title="Orchestrator Event Bus",
        status=PhaseStatus.COMPLETED,
        completion_date="2026-02-04"
    )
    
    assert phase.phase_id == "PHASE-01"
    assert phase.title == "Orchestrator Event Bus"
    assert phase.status == PhaseStatus.COMPLETED
    assert phase.completion_date == "2026-02-04"


def test_phase_detail_model_with_overview():
    """Test PhaseDetail with LLM-generated overview"""
    from cortex.models.phase_detail_schema import PhaseDetail, PhaseStatus
    
    overview = """
    Event-driven communication backbone enabling decoupled orchestrator 
    communication without direct imports.
    """
    
    phase = PhaseDetail(
        phase_id="PHASE-01",
        title="Orchestrator Event Bus",
        status=PhaseStatus.COMPLETED,
        overview=overview
    )
    
    assert phase.overview == overview
    assert len(phase.overview) > 50


def test_feature_model():
    """Test Feature nested model"""
    from cortex.models.phase_detail_schema import Feature
    
    feature = Feature(
        name="Event Publishing",
        description="OrchestratorEvent dataclass with type, payload, source",
        status="IMPLEMENTED",
        test_coverage=1.0
    )
    
    assert feature.name == "Event Publishing"
    assert feature.status == "IMPLEMENTED"
    assert feature.test_coverage == 1.0


def test_architecture_section_with_diagrams():
    """Test ArchitectureSection with Mermaid diagrams"""
    from cortex.models.phase_detail_schema import ArchitectureSection, MermaidDiagram
    
    arch_diagram = MermaidDiagram(
        type="architecture",
        title="Event Bus Architecture",
        mermaid_code="graph TD\nA[Publisher] --> B[EventBus]\nB --> C[Subscriber]"
    )
    
    arch = ArchitectureSection(
        overview="Event-driven architecture foundation",
        diagrams=[arch_diagram],
        components=["OrchestratorEventBus", "OrchestratorEvent", "EventHandler"]
    )
    
    assert len(arch.diagrams) == 1
    assert arch.diagrams[0].type == "architecture"
    assert "EventBus" in arch.diagrams[0].mermaid_code


def test_implementation_section():
    """Test ImplementationSection with file details"""
    from cortex.models.phase_detail_schema import ImplementationSection, CodeFile
    
    code_file = CodeFile(
        path="cortex/infrastructure/orchestrator_event_bus.py",
        lines_of_code=304,
        purpose="Event bus implementation",
        language="python"
    )
    
    impl = ImplementationSection(
        files=[code_file],
        total_loc=304,
        tier=3,
        priority=2
    )
    
    assert len(impl.files) == 1
    assert impl.total_loc == 304
    assert impl.files[0].language == "python"


def test_testing_section():
    """Test TestingSection with metrics"""
    from cortex.models.phase_detail_schema import TestingSection
    
    testing = TestingSection(
        test_count=19,
        test_pass_rate=1.0,
        coverage=1.0,
        test_file="tests/infrastructure/test_orchestrator_event_bus.py"
    )
    
    assert testing.test_count == 19
    assert testing.test_pass_rate == 1.0
    assert testing.coverage == 1.0


def test_compliance_rule():
    """Test ComplianceRule model"""
    from cortex.models.phase_detail_schema import ComplianceRule
    
    rule = ComplianceRule(
        rule="CORE-008",
        description="TDD-first development",
        status="COMPLIANT"
    )
    
    assert rule.rule == "CORE-008"
    assert rule.status == "COMPLIANT"


def test_impact_metrics():
    """Test ImpactMetrics model"""
    from cortex.models.phase_detail_schema import ImpactMetrics, ImpactLevel
    
    impact = ImpactMetrics(
        extensibility=ImpactLevel.HIGH,
        scalability=ImpactLevel.HIGH,
        maintainability=ImpactLevel.HIGH,
        description="Enables decoupled orchestrator communication"
    )
    
    assert impact.extensibility == ImpactLevel.HIGH
    assert impact.scalability == ImpactLevel.HIGH


def test_story_context_with_links():
    """Test StoryContext for phase narrative"""
    from cortex.models.phase_detail_schema import StoryContext
    
    context = StoryContext(
        previous_phase="PHASE-00",
        next_phase="PHASE-02",
        narrative="Building on planning foundations, Phase 1 introduces event-driven communication.",
        related_enhancements=["ENH-014"]
    )
    
    assert context.previous_phase == "PHASE-00"
    assert context.next_phase == "PHASE-02"
    assert len(context.related_enhancements) == 1


def test_technical_decision():
    """Test TechnicalDecision model"""
    from cortex.models.phase_detail_schema import TechnicalDecision
    
    decision = TechnicalDecision(
        title="Event Bus vs Direct Imports",
        chosen="Event Bus Architecture",
        rejected=["Direct Orchestrator Imports", "Message Queue"],
        rationale="Enables extensibility without coupling",
        tradeoffs="Slight latency increase for decoupling benefit"
    )
    
    assert decision.chosen == "Event Bus Architecture"
    assert len(decision.rejected) == 2
    assert "extensibility" in decision.rationale


def test_lesson_learned():
    """Test Lesson model"""
    from cortex.models.phase_detail_schema import Lesson
    
    lesson = Lesson(
        title="Async Event Handling Critical",
        description="Synchronous event processing caused blocking",
        category="PERFORMANCE",
        recommendation="Always use async handlers for I/O operations"
    )
    
    assert lesson.category == "PERFORMANCE"
    assert "async" in lesson.recommendation


def test_phase_detail_full_model():
    """Test complete PhaseDetail model with all sections"""
    from cortex.models.phase_detail_schema import (
        PhaseDetail, PhaseStatus, Feature, ArchitectureSection,
        ImplementationSection, TestingSection, ComplianceRule,
        ImpactMetrics, StoryContext, TechnicalDecision, Lesson,
        CodeFile, ImpactLevel
    )
    
    phase = PhaseDetail(
        phase_id="PHASE-01",
        title="Orchestrator Event Bus",
        status=PhaseStatus.COMPLETED,
        completion_date="2026-02-04",
        overview="Event-driven architecture foundation",
        objectives=[
            "Enable event-driven orchestrator communication",
            "Remove direct orchestrator dependencies"
        ],
        key_features=[
            Feature(
                name="Event Publishing",
                description="OrchestratorEvent dataclass",
                status="IMPLEMENTED",
                test_coverage=1.0
            )
        ],
        architecture=ArchitectureSection(
            overview="Event bus architecture",
            diagrams=[],
            components=["OrchestratorEventBus"]
        ),
        implementation_details=ImplementationSection(
            files=[
                CodeFile(
                    path="cortex/infrastructure/orchestrator_event_bus.py",
                    lines_of_code=304,
                    purpose="Event bus implementation",
                    language="python"
                )
            ],
            total_loc=304,
            tier=3,
            priority=2
        ),
        testing=TestingSection(
            test_count=19,
            test_pass_rate=1.0,
            coverage=1.0,
            test_file="tests/infrastructure/test_orchestrator_event_bus.py"
        ),
        compliance=[
            ComplianceRule(
                rule="CORE-008",
                description="TDD-first",
                status="COMPLIANT"
            )
        ],
        impact=ImpactMetrics(
            extensibility=ImpactLevel.HIGH,
            scalability=ImpactLevel.HIGH,
            maintainability=ImpactLevel.HIGH
        ),
        story_context=StoryContext(
            previous_phase=None,
            next_phase="PHASE-02",
            narrative="Foundation for event-driven architecture"
        )
    )
    
    assert phase.phase_id == "PHASE-01"
    assert len(phase.objectives) == 2
    assert len(phase.key_features) == 1
    assert phase.testing.test_count == 19
    assert phase.impact.extensibility == ImpactLevel.HIGH


def test_phase_status_enum():
    """Test PhaseStatus enum values"""
    from cortex.models.phase_detail_schema import PhaseStatus
    
    assert PhaseStatus.ACTIVE == "ACTIVE"
    assert PhaseStatus.COMPLETED == "COMPLETED"
    assert PhaseStatus.PLANNED == "PLANNED"


def test_impact_level_enum():
    """Test ImpactLevel enum values"""
    from cortex.models.phase_detail_schema import ImpactLevel
    
    assert ImpactLevel.HIGH == "HIGH"
    assert ImpactLevel.MEDIUM == "MEDIUM"
    assert ImpactLevel.LOW == "LOW"


def test_validation_error_on_invalid_status():
    """Test that invalid status raises validation error"""
    from cortex.models.phase_detail_schema import PhaseDetail
    
    with pytest.raises(ValidationError):
        PhaseDetail(
            phase_id="PHASE-01",
            title="Test",
            status="INVALID_STATUS"  # Should fail
        )


def test_mermaid_diagram_types():
    """Test different Mermaid diagram types"""
    from cortex.models.phase_detail_schema import MermaidDiagram
    
    arch = MermaidDiagram(
        type="architecture",
        title="Component Diagram",
        mermaid_code="graph TD\nA --> B"
    )
    
    workflow = MermaidDiagram(
        type="workflow",
        title="TDD Cycle",
        mermaid_code="sequenceDiagram\nTest->>Code: RED"
    )
    
    data_flow = MermaidDiagram(
        type="data_flow",
        title="Data Pipeline",
        mermaid_code="graph LR\nJSON --> Parser"
    )
    
    assert arch.type == "architecture"
    assert workflow.type == "workflow"
    assert data_flow.type == "data_flow"


def test_code_file_with_metadata():
    """Test CodeFile model with additional metadata"""
    from cortex.models.phase_detail_schema import CodeFile
    
    code_file = CodeFile(
        path="cortex/infrastructure/orchestrator_event_bus.py",
        lines_of_code=304,
        purpose="Event bus implementation",
        language="python",
        test_file="tests/infrastructure/test_orchestrator_event_bus.py",
        complexity_score=2.5
    )
    
    assert code_file.test_file is not None
    assert code_file.complexity_score == 2.5


def test_phase_detail_to_dict():
    """Test PhaseDetail serialization to dict"""
    from cortex.models.phase_detail_schema import PhaseDetail, PhaseStatus
    
    phase = PhaseDetail(
        phase_id="PHASE-01",
        title="Test Phase",
        status=PhaseStatus.COMPLETED
    )
    
    data = phase.model_dump()
    
    assert isinstance(data, dict)
    assert data["phase_id"] == "PHASE-01"
    assert data["status"] == "COMPLETED"


def test_phase_detail_from_dict():
    """Test PhaseDetail deserialization from dict"""
    from cortex.models.phase_detail_schema import PhaseDetail
    
    data = {
        "phase_id": "PHASE-01",
        "title": "Test Phase",
        "status": "COMPLETED"
    }
    
    phase = PhaseDetail(**data)
    
    assert phase.phase_id == "PHASE-01"
    assert phase.title == "Test Phase"
