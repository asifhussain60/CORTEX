"""
interaction_workflow_composer.py — Guided Interaction Workflow Composer.

Selects the correct guided workflow template for the current user request
and advances the interaction step-by-step toward DoR = 100%.

This is the INTERACTION-layer equivalent of the WorkflowComposer used for
code-touching operations.  This composer NEVER triggers execution — it only
selects templates, maps readiness criteria, and returns the next guided step
for the user-facing response.

Architecture:
    InteractionOrchestrator
        └─► InteractionWorkflowComposer   ← this module
              ├── InteractionWorkflowTemplate (YAML-backed descriptor)
              ├── InteractionWorkflowState    (mutable session state)
              └── select_workflow()           (deterministic routing)

Template resolution order:
    1. Exact keyword match on template trigger_keywords
    2. Intent-category fallback map
    3. Default: ``general-inquiry`` template

Governance:
    - Deterministic — no hidden heuristics; routing table is the SSOT
    - No execution — never invokes orchestrators or modifies state
    - Extensible — add new templates without changing this module
    - CORE-011: all methods fully type-annotated
    - CORE-012: all public classes/methods documented

AC_START: AC-INTERACTION-WORKFLOW-COMPOSER-001
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from cortex.orchestrators.core.interaction_readiness_tracker import (
    InteractionReadinessTracker,
    ReadinessState,
)

# ---------------------------------------------------------------------------
# Constants — Workflow category routing table (SSOT)
# ---------------------------------------------------------------------------

#: Maps intent / keyword signals → workflow template IDs
_WORKFLOW_ROUTING_TABLE: list[tuple[list[str], str]] = [
    # (trigger_keywords, template_id)
    (["feature", "implement", "add", "build", "create"], "feature-planning"),
    (["bug", "fix", "broken", "error", "fail", "crash", "issue", "defect"], "bug-investigation"),
    (["refactor", "clean", "restructure", "reorganise", "reorganize", "rename"], "refactor-planning"),
    (["architect", "architecture", "design", "adr", "decision", "structure"], "architecture-review"),
    (["test", "testing", "coverage", "tdd", "spec", "e2e", "integration"], "test-strategy"),
    (["onboard", "explore", "understand", "analyse", "analyze", "overview", "repo"], "onboarding"),
    (["doc", "document", "readme", "write up", "guide", "explain"], "documentation-request"),
    (["workflow", "compose", "pipeline", "orchestrate", "chain"], "workflow-design"),
]

#: Per-template required readiness dimensions and recommended question order
_TEMPLATE_REGISTRY: dict[str, "_TemplateDescriptor"] = {}


@dataclass
class _TemplateDescriptor:
    """Internal descriptor for a guided interaction workflow template.

    Attributes:
        template_id: Machine-readable template identifier.
        display_name: Human-readable workflow name.
        required_dimensions: Ordered list of readiness dimension keys to fill.
        questioning_order: Ordered list of dimension keys for questioning sequence.
        decision_checkpoints: Dimensions that represent explicit decision points.
        completion_criteria: Description of what DoR = 100% means for this workflow.
        opening_statement: First question/prompt to ask the user.
        dimension_questions: Mapping of dimension key → question to ask user.
    """

    template_id: str
    display_name: str
    required_dimensions: list[str]
    questioning_order: list[str]
    decision_checkpoints: list[str]
    completion_criteria: str
    opening_statement: str
    dimension_questions: dict[str, str]


def _register_template(descriptor: _TemplateDescriptor) -> None:
    """Register a template descriptor (called at module load)."""
    _TEMPLATE_REGISTRY[descriptor.template_id] = descriptor


# ---------------------------------------------------------------------------
# Template registry — built at module load
# ---------------------------------------------------------------------------

_register_template(_TemplateDescriptor(
    template_id="feature-planning",
    display_name="Feature Planning",
    required_dimensions=[
        "objective_clarity", "scope_clarity", "acceptance_criteria",
        "dependencies", "inputs", "risks", "testing_expectations",
        "rollout_considerations", "ownership", "constraints",
    ],
    questioning_order=[
        "objective_clarity", "scope_clarity", "acceptance_criteria",
        "inputs", "dependencies", "constraints", "risks",
        "testing_expectations", "rollout_considerations", "ownership",
    ],
    decision_checkpoints=["scope_clarity", "acceptance_criteria", "risks"],
    completion_criteria=(
        "All 10 readiness dimensions at 100%: feature objective, scope boundary, "
        "acceptance criteria, inputs, dependencies, constraints, risk plan, "
        "test strategy, rollout plan, and owner confirmed."
    ),
    opening_statement=(
        "To plan this feature properly I need to understand it fully before any "
        "implementation begins. Let's start: **What is the primary objective of "
        "this feature, and what problem does it solve for the user?**"
    ),
    dimension_questions={
        "objective_clarity": (
            "What is the primary objective of this feature? "
            "What user or system problem does it solve?"
        ),
        "scope_clarity": (
            "What is explicitly in scope for this feature? "
            "What is explicitly out of scope?"
        ),
        "acceptance_criteria": (
            "What are the concrete acceptance criteria? "
            "How will we verify the feature is done?"
        ),
        "inputs": (
            "What existing data, APIs, services, or context does this feature depend on? "
            "What inputs must be provided at runtime?"
        ),
        "dependencies": (
            "Are there any blocking external dependencies (teams, systems, libraries, "
            "or integrations) that must be resolved first?"
        ),
        "constraints": (
            "Are there technical or business constraints we must work within? "
            "(e.g., performance budgets, security requirements, backwards compatibility)"
        ),
        "risks": (
            "What are the main risks if this feature is implemented incorrectly or "
            "incompletely?  Are there any rollback concerns?"
        ),
        "testing_expectations": (
            "What testing approach is expected? "
            "(unit, integration, e2e, golden tests, performance tests?)"
        ),
        "rollout_considerations": (
            "How should this feature be rolled out? "
            "(feature flag, canary, full release, behind an approval gate?)"
        ),
        "ownership": (
            "Who owns this feature? Who must approve the implementation before it ships?"
        ),
    },
))

_register_template(_TemplateDescriptor(
    template_id="bug-investigation",
    display_name="Bug Investigation",
    required_dimensions=[
        "objective_clarity", "scope_clarity", "inputs", "dependencies",
        "constraints", "risks", "acceptance_criteria", "testing_expectations",
        "rollout_considerations", "ownership",
    ],
    questioning_order=[
        "objective_clarity", "inputs", "scope_clarity", "acceptance_criteria",
        "constraints", "dependencies", "risks", "testing_expectations",
        "rollout_considerations", "ownership",
    ],
    decision_checkpoints=["objective_clarity", "scope_clarity", "risks"],
    completion_criteria=(
        "Bug fully characterised: reproduction steps, symptoms, scope, root-cause "
        "hypothesis, fix acceptance criteria, test coverage plan, and owner confirmed."
    ),
    opening_statement=(
        "Let's establish what we're dealing with before any fix begins. "
        "**Can you describe the bug clearly — what is the symptom, "
        "when does it occur, and what is the expected behaviour?**"
    ),
    dimension_questions={
        "objective_clarity": (
            "Describe the bug: what is the symptom, when does it occur, "
            "and what is the expected behaviour?"
        ),
        "inputs": (
            "What are the steps to reproduce this bug? "
            "What environment, data, or conditions trigger it?"
        ),
        "scope_clarity": (
            "Which systems, components, or code paths are affected? "
            "Is this isolated or widespread?"
        ),
        "acceptance_criteria": (
            "How will we confirm the bug is fixed? "
            "What outcome or test proves resolution?"
        ),
        "constraints": (
            "Are there any constraints on the fix? "
            "(e.g., must not change public API, must remain backwards compatible)"
        ),
        "dependencies": (
            "Does the fix depend on any external teams, data migrations, "
            "or third-party library updates?"
        ),
        "risks": (
            "What is the blast radius if the bug remains unfixed? "
            "What is the risk of the proposed fix?"
        ),
        "testing_expectations": (
            "What tests must be added or updated to prevent regression?"
        ),
        "rollout_considerations": (
            "Does this fix need a hotfix release, a feature flag, or a standard release?"
        ),
        "ownership": (
            "Who owns the fix? Who must sign off before it is merged?"
        ),
    },
))

_register_template(_TemplateDescriptor(
    template_id="refactor-planning",
    display_name="Refactor Planning",
    required_dimensions=[
        "objective_clarity", "scope_clarity", "constraints", "inputs",
        "dependencies", "risks", "acceptance_criteria", "testing_expectations",
        "rollout_considerations", "ownership",
    ],
    questioning_order=[
        "objective_clarity", "scope_clarity", "constraints", "acceptance_criteria",
        "inputs", "dependencies", "risks", "testing_expectations",
        "rollout_considerations", "ownership",
    ],
    decision_checkpoints=["scope_clarity", "constraints", "risks"],
    completion_criteria=(
        "Refactor fully scoped: motivation, boundaries, constraints, "
        "safety baseline, acceptance criteria, test plan, and owner confirmed."
    ),
    opening_statement=(
        "Before refactoring begins I need to understand the motivation and boundaries. "
        "**What is the primary motivation for this refactor, and what quality "
        "or structural problem does it address?**"
    ),
    dimension_questions={
        "objective_clarity": (
            "What is the primary motivation for this refactor? "
            "What quality or structural problem does it solve?"
        ),
        "scope_clarity": (
            "Which modules, classes, or files are in scope? "
            "What must not be changed?"
        ),
        "constraints": (
            "What constraints apply? (e.g., public API must remain stable, "
            "no behaviour changes allowed, must pass all existing tests)"
        ),
        "acceptance_criteria": (
            "How will we verify the refactor succeeded without breaking anything?"
        ),
        "inputs": (
            "What is the baseline? Are there existing tests or coverage reports "
            "we can use as a safety net?"
        ),
        "dependencies": (
            "Are there downstream consumers or dependents that could break?"
        ),
        "risks": (
            "What is the risk of this refactor? "
            "What could go wrong and what is the rollback plan?"
        ),
        "testing_expectations": (
            "Are all existing tests passing before we start? "
            "What new tests are needed?"
        ),
        "rollout_considerations": (
            "Should this refactor ship in one PR or be broken into safer increments?"
        ),
        "ownership": (
            "Who owns this refactor? Who must approve before merging?"
        ),
    },
))

_register_template(_TemplateDescriptor(
    template_id="architecture-review",
    display_name="Architecture Review",
    required_dimensions=[
        "objective_clarity", "scope_clarity", "constraints", "dependencies",
        "inputs", "risks", "acceptance_criteria", "rollout_considerations",
        "ownership", "testing_expectations",
    ],
    questioning_order=[
        "objective_clarity", "scope_clarity", "inputs", "constraints",
        "dependencies", "risks", "acceptance_criteria", "rollout_considerations",
        "testing_expectations", "ownership",
    ],
    decision_checkpoints=["scope_clarity", "constraints", "risks"],
    completion_criteria=(
        "Architecture review fully scoped: area under review, decision under "
        "consideration, constraints, trade-offs, acceptance criteria, and reviewer confirmed."
    ),
    opening_statement=(
        "Let's frame the architecture review properly. "
        "**What area or decision is under review, and what question or concern "
        "is driving this review?**"
    ),
    dimension_questions={
        "objective_clarity": (
            "What area or architectural decision is under review, "
            "and what specific concern or question is driving it?"
        ),
        "scope_clarity": (
            "Which components, layers, or systems are in scope for this review?"
        ),
        "inputs": (
            "What existing documentation, ADRs, or code should inform this review?"
        ),
        "constraints": (
            "What constraints must the architecture conform to? "
            "(performance, security, scalability, team ownership)"
        ),
        "dependencies": (
            "What downstream systems or teams depend on the components under review?"
        ),
        "risks": (
            "What risks does the current architecture carry? "
            "What would be the impact of the proposed change?"
        ),
        "acceptance_criteria": (
            "How will we determine whether the review has produced an acceptable outcome?"
        ),
        "rollout_considerations": (
            "If changes are recommended, how should they be sequenced and rolled out?"
        ),
        "testing_expectations": (
            "What validation or proof-of-concept work is needed to validate the conclusion?"
        ),
        "ownership": (
            "Who is responsible for the architectural decision and who must approve it?"
        ),
    },
))

_register_template(_TemplateDescriptor(
    template_id="test-strategy",
    display_name="Test Strategy",
    required_dimensions=[
        "objective_clarity", "scope_clarity", "acceptance_criteria",
        "inputs", "constraints", "dependencies", "risks",
        "testing_expectations", "rollout_considerations", "ownership",
    ],
    questioning_order=[
        "objective_clarity", "scope_clarity", "inputs", "acceptance_criteria",
        "constraints", "risks", "dependencies", "testing_expectations",
        "rollout_considerations", "ownership",
    ],
    decision_checkpoints=["scope_clarity", "acceptance_criteria"],
    completion_criteria=(
        "Test strategy fully specified: coverage targets, test types, "
        "tooling, ownership, and quality gates confirmed."
    ),
    opening_statement=(
        "Let's define the test strategy clearly. "
        "**What is the goal of this testing effort — what are we trying to validate "
        "or what gap are we trying to close?**"
    ),
    dimension_questions={
        "objective_clarity": (
            "What is the goal of this testing effort? "
            "What gap or risk are we trying to address?"
        ),
        "scope_clarity": (
            "What components, code paths, or user scenarios must be covered?"
        ),
        "inputs": (
            "What exists already? What is the current test coverage baseline?"
        ),
        "acceptance_criteria": (
            "What coverage targets or quality gates define 'done' for this effort?"
        ),
        "constraints": (
            "Are there constraints on test type, runtime, or tooling? "
            "(e.g., no slow e2e in CI, must use pytest)"
        ),
        "risks": (
            "What risks remain if certain scenarios are not tested?"
        ),
        "dependencies": (
            "Are there test infrastructure or data dependencies to resolve first?"
        ),
        "testing_expectations": (
            "What specific test types are expected? "
            "(unit, integration, golden, contract, performance, security?)"
        ),
        "rollout_considerations": (
            "Should the test suite be added incrementally or in one PR?"
        ),
        "ownership": (
            "Who owns the test strategy and who must approve the coverage plan?"
        ),
    },
))

_register_template(_TemplateDescriptor(
    template_id="onboarding",
    display_name="Repository Onboarding",
    required_dimensions=[
        "objective_clarity", "scope_clarity", "inputs", "constraints",
        "ownership", "acceptance_criteria", "dependencies",
        "risks", "testing_expectations", "rollout_considerations",
    ],
    questioning_order=[
        "objective_clarity", "scope_clarity", "inputs", "constraints",
        "dependencies", "ownership", "acceptance_criteria",
        "risks", "testing_expectations", "rollout_considerations",
    ],
    decision_checkpoints=["scope_clarity", "ownership"],
    completion_criteria=(
        "Onboarding fully scoped: repository context, exploration goals, "
        "audience, key questions, and primary contact confirmed."
    ),
    opening_statement=(
        "Happy to help you onboard. Let me understand what you're exploring. "
        "**What is your goal — are you trying to understand the architecture, "
        "find a specific component, or prepare to contribute?**"
    ),
    dimension_questions={
        "objective_clarity": (
            "What is your onboarding goal? "
            "Are you trying to understand the architecture, find a component, "
            "or prepare to contribute?"
        ),
        "scope_clarity": (
            "Which part of the repository or codebase is your focus?"
        ),
        "inputs": (
            "What prior knowledge do you bring? "
            "What documentation have you already reviewed?"
        ),
        "constraints": (
            "Are there time constraints or a specific area you must focus on?"
        ),
        "dependencies": (
            "Are there specific people, teams, or systems you need to understand "
            "as part of this onboarding?"
        ),
        "ownership": (
            "Who is your primary contact or guide for this area of the codebase?"
        ),
        "acceptance_criteria": (
            "How will you know when you are sufficiently onboarded?"
        ),
        "risks": (
            "Are there any risks or anti-patterns in this codebase we should "
            "surface early?"
        ),
        "testing_expectations": (
            "Do you need to understand the test strategy as part of onboarding?"
        ),
        "rollout_considerations": (
            "Is there a deadline by which you need to be fully onboarded?"
        ),
    },
))

_register_template(_TemplateDescriptor(
    template_id="documentation-request",
    display_name="Documentation Request",
    required_dimensions=[
        "objective_clarity", "scope_clarity", "inputs", "acceptance_criteria",
        "ownership", "constraints", "dependencies", "risks",
        "testing_expectations", "rollout_considerations",
    ],
    questioning_order=[
        "objective_clarity", "scope_clarity", "inputs", "acceptance_criteria",
        "constraints", "ownership", "dependencies", "risks",
        "testing_expectations", "rollout_considerations",
    ],
    decision_checkpoints=["scope_clarity", "acceptance_criteria"],
    completion_criteria=(
        "Documentation request fully scoped: purpose, target audience, style, "
        "scope, acceptance criteria, and owner confirmed."
    ),
    opening_statement=(
        "Let me understand what documentation is needed. "
        "**Who is the target audience and what should they be able to do "
        "after reading this documentation?**"
    ),
    dimension_questions={
        "objective_clarity": (
            "Who is the target audience and what should they be able to do "
            "after reading this documentation?"
        ),
        "scope_clarity": (
            "What specific topics or components must the documentation cover?"
        ),
        "inputs": (
            "What existing documentation, code, or specifications can inform this content?"
        ),
        "acceptance_criteria": (
            "How will we validate the documentation is complete and accurate?"
        ),
        "constraints": (
            "Are there style, format, or length constraints? "
            "(e.g., must use existing templates, max 2 pages)"
        ),
        "ownership": (
            "Who owns and maintains this documentation after it is written?"
        ),
        "dependencies": (
            "Does any code or system need to be finalised before documentation can be written?"
        ),
        "risks": (
            "What is the risk if this documentation is incomplete or incorrect?"
        ),
        "testing_expectations": (
            "How will we verify the documentation remains accurate over time?"
        ),
        "rollout_considerations": (
            "Where will this documentation be published and when?"
        ),
    },
))

_register_template(_TemplateDescriptor(
    template_id="workflow-design",
    display_name="Workflow Design",
    required_dimensions=[
        "objective_clarity", "scope_clarity", "inputs", "constraints",
        "dependencies", "acceptance_criteria", "risks",
        "testing_expectations", "rollout_considerations", "ownership",
    ],
    questioning_order=[
        "objective_clarity", "scope_clarity", "inputs", "constraints",
        "dependencies", "risks", "acceptance_criteria",
        "testing_expectations", "rollout_considerations", "ownership",
    ],
    decision_checkpoints=["scope_clarity", "constraints", "risks"],
    completion_criteria=(
        "Workflow design fully scoped: process goal, steps, triggers, "
        "actors, success criteria, and owner confirmed."
    ),
    opening_statement=(
        "Let's design this workflow properly. "
        "**What process or capability should this workflow implement, "
        "and what problem does it solve?**"
    ),
    dimension_questions={
        "objective_clarity": (
            "What process or capability should this workflow implement? "
            "What problem does it solve?"
        ),
        "scope_clarity": (
            "What are the workflow boundaries — where does it start and end?"
        ),
        "inputs": (
            "What inputs, triggers, or events initiate this workflow?"
        ),
        "constraints": (
            "Are there technical or governance constraints on how steps must be sequenced?"
        ),
        "dependencies": (
            "What orchestrators, systems, or external APIs does this workflow depend on?"
        ),
        "risks": (
            "What could go wrong if this workflow fails mid-execution? "
            "Is there a rollback or compensation strategy?"
        ),
        "acceptance_criteria": (
            "How will we verify this workflow is correct and complete?"
        ),
        "testing_expectations": (
            "What test coverage is expected for this workflow?"
        ),
        "rollout_considerations": (
            "How should this workflow be introduced? "
            "(behind a feature flag, phased rollout, immediate activation?)"
        ),
        "ownership": (
            "Who owns this workflow and who must approve it before activation?"
        ),
    },
))

_register_template(_TemplateDescriptor(
    template_id="general-inquiry",
    display_name="General Inquiry",
    required_dimensions=[
        "objective_clarity", "scope_clarity", "inputs", "constraints",
        "acceptance_criteria", "ownership", "dependencies",
        "risks", "testing_expectations", "rollout_considerations",
    ],
    questioning_order=[
        "objective_clarity", "scope_clarity", "inputs", "acceptance_criteria",
        "constraints", "ownership", "dependencies", "risks",
        "testing_expectations", "rollout_considerations",
    ],
    decision_checkpoints=["objective_clarity", "scope_clarity"],
    completion_criteria=(
        "Request fully understood: goal, scope, inputs, constraints, "
        "and acceptance criteria confirmed."
    ),
    opening_statement=(
        "I want to make sure I understand your request fully before proceeding. "
        "**Can you describe in more detail what you're trying to achieve "
        "and what a successful outcome looks like?**"
    ),
    dimension_questions={
        "objective_clarity": (
            "What are you trying to achieve? "
            "What does a successful outcome look like?"
        ),
        "scope_clarity": (
            "What is the scope of this request — "
            "what is included and what is excluded?"
        ),
        "inputs": (
            "What context, data, or existing work should I take into account?"
        ),
        "acceptance_criteria": (
            "How will you know the result is correct and complete?"
        ),
        "constraints": (
            "Are there any constraints — technical, timeline, or process — I should know about?"
        ),
        "ownership": (
            "Who is responsible for the outcome and who needs to approve it?"
        ),
        "dependencies": (
            "Are there dependencies on other work, people, or systems?"
        ),
        "risks": (
            "What concerns or risks do you have about this request?"
        ),
        "testing_expectations": (
            "Should the result be verifiable or testable? How?"
        ),
        "rollout_considerations": (
            "Are there any timing or phasing considerations?"
        ),
    },
))


# ---------------------------------------------------------------------------
# State dataclass
# ---------------------------------------------------------------------------


@dataclass
class InteractionWorkflowState:
    """Mutable state for a guided interaction session.

    Attributes:
        template_id: Selected workflow template ID.
        display_name: Human-readable workflow name.
        current_step_index: Index into the questioning_order list.
        completed_steps: Dimension keys that have been fully resolved.
        readiness_tracker: The DoR tracker for this session.
    """

    template_id: str
    display_name: str
    current_step_index: int = 0
    completed_steps: list[str] = field(default_factory=list)
    readiness_tracker: Optional[InteractionReadinessTracker] = None


# ---------------------------------------------------------------------------
# Composer
# ---------------------------------------------------------------------------


class InteractionWorkflowComposer:
    """Selects and advances guided interaction workflows.

    Deterministically maps a user request to the correct workflow template,
    tracks progress through the readiness questioning sequence, and returns
    the next guided step for rendering.

    This composer NEVER triggers execution — it is a pure guidance engine.

    Usage::

        composer = InteractionWorkflowComposer()
        state = composer.select_workflow("I want to build a new auth feature")
        print(state.template_id)   # "feature-planning"
        print(state.display_name)  # "Feature Planning"

        # Advance after the user answers the first question
        state = composer.advance_step(state)
        next_q = composer.get_next_question(state)

    AC_START: AC-INTERACTION-WORKFLOW-COMPOSER-001
    """

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def select_workflow(
        self,
        user_request: str,
        intent: str = "UNKNOWN",
    ) -> InteractionWorkflowState:
        """Select the best-fit guided workflow template for the request.

        Uses keyword routing first, then intent fallback, then default.

        Args:
            user_request: The raw user request string.
            intent: Classified intent label (e.g. ``"IMPLEMENT"``).

        Returns:
            A fresh InteractionWorkflowState for the selected template.
        """
        template_id = self._resolve_template_id(user_request, intent)
        descriptor = _TEMPLATE_REGISTRY[template_id]
        tracker = InteractionReadinessTracker()
        # Seed open questions from the template's dimension_questions
        for dim_key in descriptor.questioning_order:
            question = descriptor.dimension_questions.get(dim_key)
            if question:
                tracker.update_dimension(
                    dimension=dim_key,
                    score=0,
                    evidence="",
                    open_question=question,
                )
        return InteractionWorkflowState(
            template_id=template_id,
            display_name=descriptor.display_name,
            readiness_tracker=tracker,
        )

    def _resolve_template_id(self, user_request: str, intent: str) -> str:
        """Resolve the template ID from registered routing rules.

        Args:
            user_request: Raw user request text.
            intent: Classified intent label (uppercase).

        Returns:
            Template ID string; falls back to ``"general-inquiry"``.
        """
        lower = user_request.lower()

        # Pick the template with the most keyword matches (most specific wins).
        # Ties are broken by routing-table order (first entry wins).
        best_template: Optional[str] = None
        best_count: int = 0
        for keywords, template_id in _WORKFLOW_ROUTING_TABLE:
            count = sum(1 for kw in keywords if kw in lower)
            if count > best_count:
                best_count = count
                best_template = template_id

        if best_template:
            return best_template

        # Intent-based fallback
        intent_map: dict[str, str] = {
            "IMPLEMENT": "feature-planning",
            "FIX": "bug-investigation",
            "REFACTOR": "refactor-planning",
            "DEBUG": "bug-investigation",
            "AUDIT": "architecture-review",
        }
        return intent_map.get(intent.upper(), "general-inquiry")

    # ------------------------------------------------------------------
    # Advancement
    # ------------------------------------------------------------------

    def advance_step(
        self,
        state: InteractionWorkflowState,
        answered_dimension: Optional[str] = None,
        score: int = 100,
        evidence: str = "",
    ) -> InteractionWorkflowState:
        """Mark the current dimension as answered and advance to the next.

        Args:
            state: Current workflow state.
            answered_dimension: Dimension key that was just answered.
                If None, advances the current_step_index without updating tracker.
            score: Readiness score to apply to the answered dimension (0–100).
            evidence: Evidence text captured from the user's answer.

        Returns:
            Updated state (mutated in-place; same object returned for chaining).
        """
        descriptor = _TEMPLATE_REGISTRY.get(state.template_id)
        if descriptor is None:
            return state

        if answered_dimension and state.readiness_tracker:
            state.readiness_tracker.update_dimension(
                dimension=answered_dimension,
                score=score,
                evidence=evidence,
                open_question=None,  # resolved
            )
            if answered_dimension not in state.completed_steps:
                state.completed_steps.append(answered_dimension)

        # Advance the step pointer
        if state.current_step_index < len(descriptor.questioning_order) - 1:
            state.current_step_index += 1

        return state

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def get_next_question(
        self,
        state: InteractionWorkflowState,
    ) -> Optional[str]:
        """Return the next question to ask the user.

        Args:
            state: Current workflow state.

        Returns:
            The next unanswered question string, or None when all resolved.
        """
        descriptor = _TEMPLATE_REGISTRY.get(state.template_id)
        if descriptor is None:
            return None

        order = descriptor.questioning_order
        for dim_key in order[state.current_step_index:]:
            question = descriptor.dimension_questions.get(dim_key)
            if question and (state.readiness_tracker is None or
                             dim_key not in state.completed_steps):
                return question

        return None

    def get_opening_statement(self, state: InteractionWorkflowState) -> str:
        """Return the template's configured opening statement.

        Args:
            state: Current workflow state.

        Returns:
            Opening statement string, or a generic fallback.
        """
        descriptor = _TEMPLATE_REGISTRY.get(state.template_id)
        if descriptor is None:
            return (
                "I need to understand your request fully before proceeding. "
                "Can you describe what you're trying to achieve?"
            )
        return descriptor.opening_statement

    def get_completion_criteria(self, state: InteractionWorkflowState) -> str:
        """Return the DoR = 100% completion criteria for this workflow.

        Args:
            state: Current workflow state.

        Returns:
            Completion criteria string.
        """
        descriptor = _TEMPLATE_REGISTRY.get(state.template_id)
        if descriptor is None:
            return "All readiness dimensions at 100%."
        return descriptor.completion_criteria

    def is_at_decision_checkpoint(self, state: InteractionWorkflowState) -> bool:
        """Return True if the current step is a decision checkpoint.

        Args:
            state: Current workflow state.

        Returns:
            True if the current dimension is a decision checkpoint.
        """
        descriptor = _TEMPLATE_REGISTRY.get(state.template_id)
        if descriptor is None:
            return False
        order = descriptor.questioning_order
        if state.current_step_index >= len(order):
            return False
        current_dim = order[state.current_step_index]
        return current_dim in descriptor.decision_checkpoints

    def list_available_templates(self) -> list[dict[str, str]]:
        """Return all registered template IDs and display names.

        Returns:
            List of dicts with ``template_id`` and ``display_name`` keys.
        """
        return [
            {"template_id": tid, "display_name": desc.display_name}
            for tid, desc in _TEMPLATE_REGISTRY.items()
        ]


# AC_COMPLETE: AC-INTERACTION-WORKFLOW-COMPOSER-001
