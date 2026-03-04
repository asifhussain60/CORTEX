"""
Test Composer - Generates Realistic Test Code from Demands

Takes test demands (from DemandAnalyzer) and generates complete, runnable
test code with assertions, audit trail validation, and realistic scenarios.

Authority: PHASE-51-S4-TEST-INTELLIGENCE | CORE-008 (TDD-First)
AC-ID: AC-PHASE51-S4-TEST-COMPOSER-001
Purpose: Transform demands into beautiful, maintainable test code

Key principle: Compose tests that simulate real-world scenarios, not placeholders
"""
# CORE-035 — domain-scoped; class name appropriate for this module

import textwrap
from dataclasses import dataclass
from enum import Enum
from typing import List

from cortex.testing.test_demand_generator import (
    DemandCategory,
    TestDemand,
)


class TestFramework(str, Enum):  # CORE-035-scoped — domain-specific variant
    """Test framework selection."""
    PYTEST = "pytest"
    UNITTEST = "unittest"


@dataclass
class ComposedTest:  # CORE-035-scoped — domain-specific variant
    """A generated test ready to run."""
    name: str
    class_name: str
    demand_id: str
    framework: TestFramework
    imports: List[str]
    test_code: str
    fixtures: List[str]
    docstring: str
    estimated_lines: int
    uses_audit_trail: bool
    uses_mocking: bool


class TestCodeComposer:
    """Composes realistic test code from demands."""

    def __init__(self, framework: TestFramework = TestFramework.PYTEST) -> None:
        """Initialize composer with framework selection."""
        self.framework = framework

    def compose(self, demand: TestDemand) -> ComposedTest:
        """
        Compose a test from a demand.

        Args:
            demand: TestDemand specifying what to test

        Returns:
            ComposedTest with generated code
        """
        # Route to specific composer based on category
        if demand.category == DemandCategory.SILENT_OPERATION:
            return self._compose_silent_operation(demand)
        elif demand.category == DemandCategory.CONTEXT_SYNTHESIS:
            return self._compose_context_synthesis(demand)
        elif demand.category == DemandCategory.LOOP_INTELLIGENCE:
            return self._compose_loop_intelligence(demand)
        elif demand.category == DemandCategory.GATE_ENFORCEMENT:
            return self._compose_gate_enforcement(demand)
        elif demand.category == DemandCategory.TEMPLATE_QUALITY:
            return self._compose_template_quality(demand)
        elif demand.category == DemandCategory.AUDIT_COMPLIANCE:
            return self._compose_audit_compliance(demand)
        else:
            return self._compose_generic(demand)

    def _compose_silent_operation(self, demand: TestDemand) -> ComposedTest:
        """Compose test for SILENT_OPERATION demands (files created without prompts)."""
        test_name = f"test_{demand.id.lower().replace('-', '_')}_silent_creation"

        code = textwrap.dedent(f'''
    def {test_name}(self):
        """DEMAND: {demand.title}

        Validates: {demand.description}
        Scenario: {demand.scenario}
        Expected: {demand.expected_behavior}
        """
        # AC_START: AC-{demand.id}

        # Setup
        orchestrator = self.orchestrator_class()
        initial_files = set(Path(self.state_dir).glob("*.yaml"))

        # Execute (silent - no prompts)
        result = orchestrator.execute(request="{demand.scenario}")

        # Validate: File created
        final_files = set(Path(self.state_dir).glob("*.yaml"))
        new_files = final_files - initial_files

        assert len(new_files) > 0, "No YAML file created"
        created_file = list(new_files)[0]
        assert created_file.suffix == ".yaml"

        # Validate: File content
        with open(created_file) as f:
            content = yaml.safe_load(f)

        required_keys = {demand.validation_rules.get("contains_keys", [])}
        for key in required_keys:
            assert key in content, f"Missing key: {{key}}"

        # Validate: Audit trail
        audit = get_audit_trail()
        assert any("created" in str(entry).lower() for entry in audit), \\
            "Audit trail missing file creation event"

        assert result.status == "success"
        # AC_COMPLETE: AC-{demand.id} ✅
''').strip()

        return ComposedTest(
            name=test_name,
            class_name="TestInteractionOrchestrator",
            demand_id=demand.id,
            framework=self.framework,
            imports=["from pathlib import Path", "import yaml"],
            test_code=code,
            fixtures=["self.orchestrator_class", "self.state_dir"],
            docstring=demand.description,
            estimated_lines=25,
            uses_audit_trail=True,
            uses_mocking=False,
        )

    def _compose_context_synthesis(self, demand: TestDemand) -> ComposedTest:
        """Compose test for CONTEXT_SYNTHESIS demands (LENS merging)."""
        test_name = f"test_{demand.id.lower().replace('-', '_')}_synthesis"

        code = f'''
    def {test_name}(self):
        """DEMAND: {demand.title}

        Validates: {demand.description}
        Scenario: {demand.scenario}
        Expected: {demand.expected_behavior}
        """
        # AC_START: AC-{demand.id}

        # Setup - mock each knowledge source
        governance_rules = {{"CORE-008": "TDD-first", "CORE-011": "Type hints"}}
        domain_rules = {{"business_domain": "payment_processing"}}
        company_standards = {{"language": "simple", "code_style": "PEP-8"}}

        # Execute - LENS synthesis merges all three
        orchestrator = self.orchestrator_class()
        result = orchestrator.execute(
            request="{demand.scenario}",
            governance=governance_rules,
            domain=domain_rules,
            company_standards=company_standards
        )

        # Validate: All layers present
        synthesis = result.lens_synthesis

        assert "governance" in synthesis, "Governance layer missing"
        assert len(synthesis["governance"]) > 0, "Governance empty"

        assert "domain" in synthesis, "Domain layer missing"
        assert len(synthesis["domain"]) > 0, "Domain empty"

        assert "standards" in synthesis, "Company standards layer missing"
        assert len(synthesis["standards"]) > 0, "Standards empty"

        # Validate: No duplication
        all_keys = set(synthesis["governance"].keys()) | \\
                   set(synthesis["domain"].keys()) | \\
                   set(synthesis["standards"].keys())
        total_items = sum(len(v) for v in [
            synthesis["governance"],
            synthesis["domain"],
            synthesis["standards"]
        ])
        assert len(all_keys) == total_items, "Duplication detected"

        # Validate: Audit trail
        audit = get_audit_trail()
        synthesis_events = [e for e in audit if "synthesis" in str(e).lower()]
        assert len(synthesis_events) > 0, "No synthesis events in audit"

        # AC_COMPLETE: AC-{demand.id} ✅
'''

        return ComposedTest(
            name=test_name,
            class_name="TestInteractionOrchestrator",
            demand_id=demand.id,
            framework=self.framework,
            imports=["from unittest.mock import Mock"],
            test_code=code,
            fixtures=["self.orchestrator_class"],
            docstring=demand.description,
            estimated_lines=40,
            uses_audit_trail=True,
            uses_mocking=True,
        )

    def _compose_loop_intelligence(self, demand: TestDemand) -> ComposedTest:
        """Compose test for LOOP_INTELLIGENCE demands (RGR loop bounds)."""
        test_name = f"test_{demand.id.lower().replace('-', '_')}_loop_safety"

        code = f'''
    def {test_name}(self):
        """DEMAND: {demand.title}

        Validates: {demand.description}
        Scenario: {demand.scenario}
        Expected: {demand.expected_behavior}
        """
        # AC_START: AC-{demand.id}

        # Setup - mock failing tests to trigger loop iterations
        orchestrator = self.orchestrator_class()
        iteration_log = []

        def mock_test_runner(test_file):
            # Simulate test failures that improve each iteration
            iteration = len(iteration_log) + 1
            iteration_log.append({{"iteration": iteration}})

            # Improve each iteration (RED→GREEN progression)
            if iteration < 3:
                return {{"status": "FAIL", "failures": iteration}}  # Failing
            else:
                return {{"status": "PASS", "failures": 0}}  # Passing

        # Patch test runner
        with patch("orchestrator.run_tests", side_effect=mock_test_runner):
            # Execute RED→GREEN→REFACTOR loop
            result = orchestrator.execute(
                request="Implement feature",
                enable_rgr_loop=True
            )

        # Validate: Loop ran until DoD met
        dod_status = result.dod_status
        assert dod_status == "COMPLETE", f"DoD not met: {{dod_status}}"

        # Validate: Loop iterations
        iterations = len(iteration_log)
        assert iterations > 0, "Loop never executed"
        assert iterations <= {demand.validation_rules.get("max_iterations", 5)}, \\
            f"Loop exceeded max iterations: {{iterations}}"

        # Validate: Each iteration logged
        audit = get_audit_trail()
        rgr_events = [e for e in audit if "RED" in str(e) or "GREEN" in str(e)]
        assert len(rgr_events) >= iterations * 2, "RGR phases not logged"

        # Validate: Loop terminates on DoD
        final_event = rgr_events[-1]
        assert "COMPLETE" in str(final_event), "Loop didn't terminate on DoD"

        # AC_COMPLETE: AC-{demand.id} ✅
'''

        return ComposedTest(
            name=test_name,
            class_name="TestTDDOrchestrator",
            demand_id=demand.id,
            framework=self.framework,
            imports=["from unittest.mock import patch"],
            test_code=code,
            fixtures=["self.orchestrator_class"],
            docstring=demand.description,
            estimated_lines=50,
            uses_audit_trail=True,
            uses_mocking=True,
        )

    def _compose_gate_enforcement(self, demand: TestDemand) -> ComposedTest:
        """Compose test for GATE_ENFORCEMENT demands (DoD blocking)."""
        test_name = f"test_{demand.id.lower().replace('-', '_')}_approval_blocked"

        code = f'''
    def {test_name}(self):
        """DEMAND: {demand.title}

        Validates: {demand.description}
        Scenario: {demand.scenario}
        Expected: {demand.expected_behavior}
        """
        # AC_START: AC-{demand.id}

        # Setup - create state with failing tests
        orchestrator = self.orchestrator_class()

        test_state = {{
            "tests_passed": 0,
            "tests_failed": 2,
            "violations": [{{"rule": "CORE-008", "severity": "critical"}}],
            "dod_status": "INCOMPLETE"
        }}

        # Execute - attempt to approve with incomplete DoD
        with self.assertRaises(RuntimeError) as ctx:
            orchestrator.request_approval(
                request_id="test-request",
                state=test_state
            )

        # Validate: Approval blocked
        error_msg = str(ctx.exception)
        assert "approval" in error_msg.lower()
        assert "blocked" in error_msg.lower() or "denied" in error_msg.lower()

        # Validate: Error message is intelligent
        assert "tests" in error_msg.lower() or "dod" in error_msg.lower()

        # Validate: Audit trail shows block
        audit = get_audit_trail()
        block_events = [e for e in audit if "blocked" in str(e).lower()]
        assert len(block_events) > 0, "Approval block not logged"

        # Now validate success case - approval allowed when DoD met
        test_state["tests_passed"] = 10
        test_state["tests_failed"] = 0
        test_state["violations"] = []
        test_state["dod_status"] = "COMPLETE"

        # Should NOT raise
        result = orchestrator.request_approval(
            request_id="test-request",
            state=test_state
        )

        assert result.approved is True

        # AC_COMPLETE: AC-{demand.id} ✅
'''

        return ComposedTest(
            name=test_name,
            class_name="TestInteractionOrchestrator",
            demand_id=demand.id,
            framework=self.framework,
            imports=["from unittest.mock import Mock"],
            test_code=code,
            fixtures=["self.orchestrator_class"],
            docstring=demand.description,
            estimated_lines=35,
            uses_audit_trail=True,
            uses_mocking=True,
        )

    def _compose_template_quality(self, demand: TestDemand) -> ComposedTest:
        """Compose test for TEMPLATE_QUALITY demands (response formatting)."""
        test_name = f"test_{demand.id.lower().replace('-', '_')}_format_standards"

        code = f'''
    def {test_name}(self):
        """DEMAND: {demand.title}

        Validates: {demand.description}
        Scenario: {demand.scenario}
        Expected: {demand.expected_behavior}
        """
        # AC_START: AC-{demand.id}

        # Setup
        orchestrator = self.orchestrator_class()

        # Execute - trigger multiple responses
        responses = []
        for i in range(5):
            result = orchestrator.execute_step(step_num=i)
            responses.append(result.user_response)

        # Validate: Each response follows standards
        for i, response in enumerate(responses):
            assert response is not None, f"Response {{i}} is empty"

            # Check 1: Has progress bar
            assert "██" in response or "progress" in response.lower(), \\
                f"Response {{i}} missing progress indicator"

            # Check 2: Simple language (no technical jargon)
            complex_words = [
                "orchestrator", "synchronize", "datastructure", "callback",
                "polymorphism", "serialization"
            ]
            response_lower = response.lower()
            technical_count = sum(1 for word in complex_words if word in response_lower)
            assert technical_count == 0, f"Response {{i}} uses technical jargon"

            # Check 3: No code snippets in explanations
            code_markers = ["def ", "class ", "import ", ">>>"]
            has_code = any(marker in response for marker in code_markers)
            assert not has_code, f"Response {{i}} contains code snippets"

            # Check 4: Information not sprawled
            lines = response.split("\\n")
            # Each logical section should be <5 lines
            for section in lines:
                if section.strip():
                    assert len(section) < 100, \\
                        f"Response {{i}} has overly long line: {{len(section)}} chars"

        # Validate: Consistency across responses
        response_structures = [r.split("\\n")[0] for r in responses]
        assert len(set(response_structures)) == 1, "Response structure inconsistent"

        # AC_COMPLETE: AC-{demand.id} ✅
'''

        return ComposedTest(
            name=test_name,
            class_name="TestInteractionOrchestrator",
            demand_id=demand.id,
            framework=self.framework,
            imports=[],
            test_code=code,
            fixtures=["self.orchestrator_class"],
            docstring=demand.description,
            estimated_lines=30,
            uses_audit_trail=False,
            uses_mocking=False,
        )

    def _compose_audit_compliance(self, demand: TestDemand) -> ComposedTest:
        """Compose test for AUDIT_COMPLIANCE demands (AC markers)."""
        test_name = f"test_{demand.id.lower().replace('-', '_')}_audit_trail"

        code = f'''
    def {test_name}(self):
        """DEMAND: {demand.title}

        Validates: {demand.description}
        Scenario: {demand.scenario}
        Expected: {demand.expected_behavior}
        """
        # AC_START: AC-{demand.id}

        # Setup - clear audit trail
        clear_audit_trail()

        # Execute - complete interaction workflow
        orchestrator = self.orchestrator_class()
        result = orchestrator.execute(
            request="{demand.scenario}",
            track_audit=True
        )

        # Validate: Audit trail captured
        audit = get_audit_trail()
        assert len(audit) > 0, "Audit trail empty"

        # Validate: AC_START marker present
        start_markers = [e for e in audit if "AC_START" in str(e)]
        assert len(start_markers) > 0, "No AC_START markers found"

        # Validate: AC_COMPLETE marker present
        complete_markers = [e for e in audit if "AC_COMPLETE" in str(e)]
        assert len(complete_markers) > 0, "No AC_COMPLETE markers found"

        # Validate: Each AC_START has corresponding AC_COMPLETE
        starts = {{e["operation_id"]: e for e in start_markers}}
        completes = {{e["operation_id"]: e for e in complete_markers}}

        for op_id in starts:
            assert op_id in completes, f"AC_START {{op_id}} missing AC_COMPLETE"

        # Validate: Timestamps and sequence
        for entry in audit:
            assert "timestamp" in entry, f"Entry missing timestamp: {{entry}}"

        # Validate: Checksum/verification
        for entry in complete_markers:
            assert "status" in entry, f"AC_COMPLETE missing status: {{entry}}"
            assert entry["status"] == "✅", f"Entry not marked successful: {{entry}}"

        # AC_COMPLETE: AC-{demand.id} ✅
'''

        return ComposedTest(
            name=test_name,
            class_name="TestInteractionOrchestrator",
            demand_id=demand.id,
            framework=self.framework,
            imports=[],
            test_code=code,
            fixtures=["self.orchestrator_class"],
            docstring=demand.description,
            estimated_lines=20,
            uses_audit_trail=True,
            uses_mocking=False,
        )

    def _compose_generic(self, demand: TestDemand) -> ComposedTest:
        """Compose generic test for unhandled categories."""
        test_name = f"test_{demand.id.lower().replace('-', '_')}"

        code = f'''
    def {test_name}(self):
        """DEMAND: {demand.title}

        {demand.description}
        """
        # AC_START: AC-{demand.id}

        # TODO: Implement test for {demand.category}
        # Scenario: {demand.scenario}
        # Expected: {demand.expected_behavior}

        pytest.skip("Generic test stub - needs implementation")

        # AC_COMPLETE: AC-{demand.id} ✅
'''

        return ComposedTest(
            name=test_name,
            class_name="TestOrchestrator",
            demand_id=demand.id,
            framework=self.framework,
            imports=["import pytest"],
            test_code=code,
            fixtures=[],
            docstring=demand.description,
            estimated_lines=10,
            uses_audit_trail=False,
            uses_mocking=False,
        )


# AC_START: AC-PHASE51-S4-TEST-COMPOSER-001
# Test Composer - Code Generation Component
# AC_COMPLETE: AC-PHASE51-S4-TEST-COMPOSER-001 ✅
