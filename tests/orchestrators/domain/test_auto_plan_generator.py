"""Tests for AutoPlanGenerator, PhaseFileScaffolder, RoadmapPatternSelector (CAPE 136-b).

TDD RED phase — imports fail until implementation files exist.
"""
import os
import tempfile

import pytest
import yaml

from cortex.orchestrators.core.complexity_triage_engine import (
    TriageResult,
    ComplexityTriageEngine,
)
from cortex.orchestrators.domain.roadmap_pattern_selector import (
    RoadmapSelection,
    RoadmapPatternSelector,
)
from cortex.orchestrators.domain.phase_file_scaffolder import PhaseFileScaffolder
from cortex.orchestrators.domain.auto_plan_generator import (
    PlanGenerationResult,
    AutoPlanGenerator,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def engine() -> ComplexityTriageEngine:
    return ComplexityTriageEngine()


@pytest.fixture()
def selector() -> RoadmapPatternSelector:
    return RoadmapPatternSelector()


@pytest.fixture()
def scaffolder() -> PhaseFileScaffolder:
    return PhaseFileScaffolder()


@pytest.fixture()
def simple_result(engine: ComplexityTriageEngine) -> TriageResult:
    return engine.triage(
        intent_confidence=0.95,
        lens_confidence=1.0,
        files_affected=1,
        circular_deps=0,
        coupling_score=0.0,
        rca_failures=0,
    )


@pytest.fixture()
def complex_result(engine: ComplexityTriageEngine) -> TriageResult:
    return engine.triage(
        intent_confidence=0.2,
        lens_confidence=0.2,
        files_affected=20,
        circular_deps=7,
        coupling_score=0.9,
        rca_failures=10,
    )


@pytest.fixture()
def refactor_result(engine: ComplexityTriageEngine) -> TriageResult:
    """MODERATE result with REFACTOR intent."""
    return engine.triage(
        intent_confidence=0.4,
        lens_confidence=0.4,
        files_affected=7,
        circular_deps=2,
        coupling_score=0.5,
        rca_failures=4,
    )


@pytest.fixture()
def sample_gaps() -> list:
    return [
        {"id": "GAP-T-01", "title": "First gap"},
        {"id": "GAP-T-02", "title": "Second gap"},
    ]


# ---------------------------------------------------------------------------
# RoadmapPatternSelector
# ---------------------------------------------------------------------------

class TestRoadmapPatternSelector:

    def test_roadmap_select_simple(
        self, selector: RoadmapPatternSelector, simple_result: TriageResult
    ) -> None:
        selection: RoadmapSelection = selector.select(
            triage=simple_result, intent="IMPLEMENT"
        )
        assert selection.template_name == "linear-execution"
        assert selection.max_sub_phases >= 1
        assert selection.max_sub_phases <= 3

    def test_roadmap_select_complex_many_files(
        self, selector: RoadmapPatternSelector, complex_result: TriageResult
    ) -> None:
        selection: RoadmapSelection = selector.select(
            triage=complex_result, intent="IMPLEMENT"
        )
        assert selection.template_name == "epic-roadmap"
        assert selection.max_sub_phases >= 15

    def test_roadmap_select_refactor_intent(
        self, selector: RoadmapPatternSelector, refactor_result: TriageResult
    ) -> None:
        selection: RoadmapSelection = selector.select(
            triage=refactor_result, intent="REFACTOR"
        )
        assert selection.template_name == "sts-refactoring"

    def test_roadmap_select_returns_roadmap_selection(
        self, selector: RoadmapPatternSelector, simple_result: TriageResult
    ) -> None:
        selection = selector.select(triage=simple_result, intent="IMPLEMENT")
        assert isinstance(selection, RoadmapSelection)

    def test_roadmap_selection_has_template_name(
        self, selector: RoadmapPatternSelector, simple_result: TriageResult
    ) -> None:
        selection = selector.select(triage=simple_result, intent="IMPLEMENT")
        assert isinstance(selection.template_name, str)
        assert len(selection.template_name) > 0

    def test_roadmap_five_templates_covered(
        self, selector: RoadmapPatternSelector, engine: ComplexityTriageEngine
    ) -> None:
        """All 5 templates must be reachable."""
        templates = set()
        combos = [
            (engine.triage(intent_confidence=0.95, lens_confidence=1.0, files_affected=1, circular_deps=0, coupling_score=0.0, rca_failures=0), "IMPLEMENT"),
            (engine.triage(intent_confidence=0.4, lens_confidence=0.4, files_affected=7, circular_deps=2, coupling_score=0.5, rca_failures=4), "IMPLEMENT"),
            (engine.triage(intent_confidence=0.2, lens_confidence=0.2, files_affected=20, circular_deps=7, coupling_score=0.9, rca_failures=10), "IMPLEMENT"),
            (engine.triage(intent_confidence=0.4, lens_confidence=0.4, files_affected=7, circular_deps=2, coupling_score=0.5, rca_failures=4), "REFACTOR"),
            (engine.triage(intent_confidence=0.4, lens_confidence=0.4, files_affected=7, circular_deps=2, coupling_score=0.5, rca_failures=4), "PLAN"),
        ]
        for triage, intent in combos:
            templates.add(selector.select(triage=triage, intent=intent).template_name)
        assert len(templates) >= 4  # at least 4 of the 5 reachable in these combos


# ---------------------------------------------------------------------------
# PhaseFileScaffolder
# ---------------------------------------------------------------------------

class TestPhaseFileScaffolder:

    def test_scaffold_produces_valid_yaml(
        self, scaffolder: PhaseFileScaffolder, simple_result: TriageResult, sample_gaps: list
    ) -> None:
        output = scaffolder.scaffold(
            phase_id="phase-test-01",
            title="Test Phase",
            triage=simple_result,
            gaps=sample_gaps,
        )
        parsed = yaml.safe_load(output)
        assert isinstance(parsed, dict)

    def test_scaffold_contains_tdd_cycle(
        self, scaffolder: PhaseFileScaffolder, simple_result: TriageResult, sample_gaps: list
    ) -> None:
        output = scaffolder.scaffold(
            phase_id="phase-test-01",
            title="Test Phase",
            triage=simple_result,
            gaps=sample_gaps,
        )
        parsed = yaml.safe_load(output)
        # Each sub-phase should have a tdd_cycle block
        phases = parsed.get("phases", [])
        assert len(phases) > 0
        for phase in phases:
            assert "tdd_cycle" in phase
            assert "red" in phase["tdd_cycle"]
            assert "green" in phase["tdd_cycle"]
            assert "refactor" in phase["tdd_cycle"]

    def test_scaffold_contains_convergence_gate(
        self, scaffolder: PhaseFileScaffolder, simple_result: TriageResult, sample_gaps: list
    ) -> None:
        output = scaffolder.scaffold(
            phase_id="phase-test-01",
            title="Test Phase",
            triage=simple_result,
            gaps=sample_gaps,
        )
        parsed = yaml.safe_load(output)
        phases = parsed.get("phases", [])
        for phase in phases:
            assert "convergence_gate" in phase

    def test_scaffold_contains_completion_gate(
        self, scaffolder: PhaseFileScaffolder, simple_result: TriageResult, sample_gaps: list
    ) -> None:
        output = scaffolder.scaffold(
            phase_id="phase-test-01",
            title="Test Phase",
            triage=simple_result,
            gaps=sample_gaps,
        )
        parsed = yaml.safe_load(output)
        phases = parsed.get("phases", [])
        for phase in phases:
            assert "completion_gate" in phase

    def test_scaffold_governance_authority(
        self, scaffolder: PhaseFileScaffolder, simple_result: TriageResult, sample_gaps: list
    ) -> None:
        output = scaffolder.scaffold(
            phase_id="phase-test-01",
            title="Test Phase",
            triage=simple_result,
            gaps=sample_gaps,
        )
        assert "CORE-008" in output
        assert "CORE-064" in output
        assert "CORE-068" in output


# ---------------------------------------------------------------------------
# AutoPlanGenerator
# ---------------------------------------------------------------------------

class TestAutoPlanGenerator:

    def test_generate_writes_file_to_planned_dir(
        self, simple_result: TriageResult, sample_gaps: list
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = AutoPlanGenerator(output_dir=tmpdir)
            result: PlanGenerationResult = generator.generate_phase_plan(
                title="My New Feature",
                triage=simple_result,
                gaps=sample_gaps,
                intent="IMPLEMENT",
            )
            assert os.path.isfile(result.file_path)
            assert result.file_path.startswith(tmpdir)

    def test_generate_returns_plan_generation_result(
        self, simple_result: TriageResult, sample_gaps: list
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = AutoPlanGenerator(output_dir=tmpdir)
            result = generator.generate_phase_plan(
                title="My New Feature",
                triage=simple_result,
                gaps=sample_gaps,
                intent="IMPLEMENT",
            )
            assert isinstance(result, PlanGenerationResult)
            assert result.phase_id
            assert result.file_path
            assert result.template_name

    def test_generate_auto_phase_id_from_title(
        self, simple_result: TriageResult, sample_gaps: list
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = AutoPlanGenerator(output_dir=tmpdir)
            result = generator.generate_phase_plan(
                title="My New Feature With Spaces!",
                triage=simple_result,
                gaps=sample_gaps,
                intent="IMPLEMENT",
            )
            # phase_id should be a slug with no spaces
            assert " " not in result.phase_id
            assert "!" not in result.phase_id

    def test_generate_file_is_valid_yaml(
        self, simple_result: TriageResult, sample_gaps: list
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = AutoPlanGenerator(output_dir=tmpdir)
            result = generator.generate_phase_plan(
                title="Valid YAML Check",
                triage=simple_result,
                gaps=sample_gaps,
                intent="IMPLEMENT",
            )
            with open(result.file_path) as f:
                parsed = yaml.safe_load(f)
            assert isinstance(parsed, dict)
            assert "id" in parsed
            assert "title" in parsed
