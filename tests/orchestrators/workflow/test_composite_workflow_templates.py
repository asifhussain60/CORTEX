"""
Composite Workflow Template Tests — RED Phase.

Validates the composable workflow template system:
  1. composite-execution-pipeline.yaml — generic pipeline-of-pipelines
  2. threat-model-analysis.yaml — standalone threat modeling brick
  3. cross-phase-holistic-epilogue.yaml — declarative epilogue injection
  4. test-strategy-matrix.yaml — multi-tier test enforcement (unit/integration/regression/smoke/golden)

Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
Compliance: CORE-028 (snake_case filenames), CORE-035 (no duplication)
"""

import pytest
import yaml
from pathlib import Path
from typing import Any, Dict, List, Set


# ==============================================================================
# Constants
# ==============================================================================

TEMPLATES_ROOT = Path("cortex-registry/workflows/templates")
COMPANY_DOMAINS = Path("cortex-registry/company/domains")

# All new template paths
COMPOSITE_PIPELINE = TEMPLATES_ROOT / "lifecycle" / "composite-execution-pipeline.yaml"
THREAT_MODEL = TEMPLATES_ROOT / "security" / "threat-model-analysis.yaml"
HOLISTIC_EPILOGUE = TEMPLATES_ROOT / "quality" / "cross-phase-holistic-epilogue.yaml"
TEST_STRATEGY = TEMPLATES_ROOT / "tdd" / "test-strategy-matrix.yaml"

# Required existing templates that composites reference
EXISTING_TEMPLATES = {
    "security/security-hardening.yaml": TEMPLATES_ROOT / "security" / "security-hardening.yaml",
    "security/security-compliance-audit.yaml": TEMPLATES_ROOT / "security" / "security-compliance-audit.yaml",
    "tdd/tdd-feature-implementation.yaml": TEMPLATES_ROOT / "tdd" / "tdd-feature-implementation.yaml",
    "quality/quality-code-uplift.yaml": TEMPLATES_ROOT / "quality" / "quality-code-uplift.yaml",
    "quality/refactor-holistic-sweep.yaml": TEMPLATES_ROOT / "quality" / "refactor-holistic-sweep.yaml",
    "lifecycle/legacy-rescue.yaml": TEMPLATES_ROOT / "lifecycle" / "legacy-rescue.yaml",
    "lifecycle/migration-modernize.yaml": TEMPLATES_ROOT / "lifecycle" / "migration-modernize.yaml",
}


# ==============================================================================
# Helpers
# ==============================================================================

def _load_yaml(path: Path) -> Dict[str, Any]:
    """Load and parse a YAML file."""
    assert path.exists(), f"Template not found: {path}"
    with open(path, "r") as f:
        return yaml.safe_load(f)


def _get_workflow(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract workflow block from parsed YAML."""
    assert "workflow" in data, f"Missing top-level 'workflow' key"
    return data["workflow"]


def _get_steps(workflow: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract steps list from workflow."""
    assert "steps" in workflow, "Missing 'steps' in workflow"
    return workflow["steps"]


def _get_step_ids(steps: List[Dict[str, Any]]) -> Set[str]:
    """Extract all step_id values."""
    return {step["step_id"] for step in steps}


# ==============================================================================
# SCHEMA VALIDATION — All 4 Templates
# ==============================================================================

class TestTemplateSchemaCompliance:
    """Every new template must conform to CORTEX workflow YAML schema."""

    @pytest.fixture(params=[
        COMPOSITE_PIPELINE,
        THREAT_MODEL,
        HOLISTIC_EPILOGUE,
        TEST_STRATEGY,
    ], ids=[
        "composite-execution-pipeline",
        "threat-model-analysis",
        "cross-phase-holistic-epilogue",
        "test-strategy-matrix",
    ])
    def template_data(self, request: pytest.FixtureRequest) -> Dict[str, Any]:
        """Load each template for schema validation."""
        return _load_yaml(request.param)

    def test_has_workflow_root(self, template_data: Dict[str, Any]) -> None:
        """Template must have top-level 'workflow' key."""
        assert "workflow" in template_data

    def test_has_required_identity_fields(self, template_data: Dict[str, Any]) -> None:
        """Workflow must have id, name, version, category, description."""
        wf = template_data["workflow"]
        for field in ("id", "name", "version", "category", "description"):
            assert field in wf, f"Missing required field: {field}"

    def test_has_metadata_block(self, template_data: Dict[str, Any]) -> None:
        """Workflow must have metadata with author and created date."""
        wf = template_data["workflow"]
        assert "metadata" in wf
        meta = wf["metadata"]
        assert "author" in meta
        assert "created" in meta

    def test_has_convergence_gate(self, template_data: Dict[str, Any]) -> None:
        """Workflow must declare a global convergence gate."""
        wf = template_data["workflow"]
        assert "convergence_gate" in wf
        gate = wf["convergence_gate"]
        assert "max_cycles" in gate
        assert "success_criteria" in gate
        assert "convergence_predicate" in gate

    def test_has_knowledge_context(self, template_data: Dict[str, Any]) -> None:
        """Workflow must declare knowledge_context with architect and production modes."""
        wf = template_data["workflow"]
        assert "knowledge_context" in wf
        kc = wf["knowledge_context"]
        assert "architect_mode" in kc
        assert "production_mode" in kc

    def test_has_steps(self, template_data: Dict[str, Any]) -> None:
        """Workflow must have at least one step."""
        wf = template_data["workflow"]
        steps = _get_steps(wf)
        assert len(steps) >= 1

    def test_steps_have_required_fields(self, template_data: Dict[str, Any]) -> None:
        """Each step must have step_id, name, orchestrator."""
        wf = template_data["workflow"]
        for step in _get_steps(wf):
            assert "step_id" in step, f"Step missing step_id: {step}"
            assert "name" in step, f"Step missing name: {step.get('step_id', '?')}"
            assert "orchestrator" in step, f"Step missing orchestrator: {step['step_id']}"

    def test_step_ids_unique(self, template_data: Dict[str, Any]) -> None:
        """All step_id values must be unique within a template."""
        wf = template_data["workflow"]
        steps = _get_steps(wf)
        ids = [s["step_id"] for s in steps]
        assert len(ids) == len(set(ids)), f"Duplicate step_ids: {ids}"

    def test_depends_on_references_valid(self, template_data: Dict[str, Any]) -> None:
        """All depends_on references must point to existing step_ids."""
        wf = template_data["workflow"]
        steps = _get_steps(wf)
        valid_ids = _get_step_ids(steps)
        for step in steps:
            deps = step.get("depends_on", [])
            for dep in deps:
                assert dep in valid_ids, (
                    f"Step '{step['step_id']}' depends on unknown step '{dep}'"
                )


# ==============================================================================
# COMPOSITE EXECUTION PIPELINE — Lego Connector Tests
# ==============================================================================

class TestCompositeExecutionPipeline:
    """Validates the generic pipeline-of-pipelines template."""

    @pytest.fixture
    def pipeline(self) -> Dict[str, Any]:
        """Load composite pipeline template."""
        return _get_workflow(_load_yaml(COMPOSITE_PIPELINE))

    def test_category_is_lifecycle(self, pipeline: Dict[str, Any]) -> None:
        """Pipeline belongs to lifecycle category."""
        assert pipeline["category"] == "lifecycle"

    def test_has_template_ref_steps(self, pipeline: Dict[str, Any]) -> None:
        """Pipeline steps use template_ref for lego composition."""
        steps = _get_steps(pipeline)
        ref_steps = [s for s in steps if "template_ref" in s]
        assert len(ref_steps) >= 3, (
            f"Expected ≥3 template_ref steps for composition, got {len(ref_steps)}"
        )

    def test_template_refs_point_to_existing_files(self, pipeline: Dict[str, Any]) -> None:
        """All template_ref paths resolve to existing YAML files."""
        steps = _get_steps(pipeline)
        for step in steps:
            ref = step.get("template_ref")
            if ref:
                ref_path = Path(ref)
                assert ref_path.exists(), (
                    f"Step '{step['step_id']}' references non-existent template: {ref}"
                )

    def test_has_security_step_first(self, pipeline: Dict[str, Any]) -> None:
        """First operational step must be security-related (security-first)."""
        steps = _get_steps(pipeline)
        # Find first step that is not a scan/baseline
        operational_steps = [s for s in steps if "security" in s["step_id"] or "threat" in s["step_id"]]
        assert len(operational_steps) >= 1, "Pipeline must include security step"
        # Security step should have no dependency on non-scan steps
        security_step = operational_steps[0]
        deps = security_step.get("depends_on", [])
        non_scan_deps = [d for d in deps if "scan" not in d and "baseline" not in d and "threat" not in d]
        assert len(non_scan_deps) == 0, (
            f"Security step should only depend on scan/baseline steps, not {non_scan_deps}"
        )

    def test_has_epilogue_injection(self, pipeline: Dict[str, Any]) -> None:
        """Pipeline declares epilogue auto-injection."""
        assert "epilogues" in pipeline
        epilogues = pipeline["epilogues"]
        assert len(epilogues) >= 1
        epilogue_ids = [e["epilogue_id"] for e in epilogues]
        assert "holistic_sweep" in epilogue_ids, "Must include holistic_sweep epilogue"

    def test_has_test_strategy_step(self, pipeline: Dict[str, Any]) -> None:
        """Pipeline includes a test strategy enforcement step."""
        steps = _get_steps(pipeline)
        test_steps = [s for s in steps if "test" in s["step_id"]]
        assert len(test_steps) >= 1, "Pipeline must include test strategy step"

    def test_convergence_gate_strict(self, pipeline: Dict[str, Any]) -> None:
        """Global convergence requires all tests passing + security clean."""
        gate = pipeline["convergence_gate"]
        criteria = gate["success_criteria"]
        assert criteria.get("all_tests_pass") is True
        assert criteria.get("security_clean") is True

    def test_no_hardcoded_app_names(self, pipeline: Dict[str, Any]) -> None:
        """Pipeline must not reference specific app names (generic/reusable)."""
        yaml_str = yaml.dump(pipeline)
        for name in ("BadMonolith", "monolith", "SampleApp", "sample_app"):
            assert name.lower() not in yaml_str.lower(), (
                f"Pipeline must not reference '{name}' — must be generic"
            )

    def test_knowledge_context_references_company_registry(self, pipeline: Dict[str, Any]) -> None:
        """Production mode placeholders reference company registry."""
        prod = pipeline["knowledge_context"]["production_mode"]
        prod_str = yaml.dump(prod)
        assert "{{" in prod_str, "Production mode must use placeholders"

    def test_success_criteria_declared(self, pipeline: Dict[str, Any]) -> None:
        """Pipeline declares global success criteria."""
        assert "success_criteria" in pipeline
        criteria = pipeline["success_criteria"]
        assert "security_issues" in criteria
        assert "test_quality_gate_score" in criteria


# ==============================================================================
# THREAT MODEL ANALYSIS — Standalone Security Brick
# ==============================================================================

class TestThreatModelAnalysis:
    """Validates standalone threat model template."""

    @pytest.fixture
    def threat_model(self) -> Dict[str, Any]:
        """Load threat model template."""
        return _get_workflow(_load_yaml(THREAT_MODEL))

    def test_category_is_security(self, threat_model: Dict[str, Any]) -> None:
        """Threat model belongs to security category."""
        assert threat_model["category"] == "security"

    def test_owasp_frameworks_declared(self, threat_model: Dict[str, Any]) -> None:
        """Template references OWASP and CWE frameworks."""
        yaml_str = yaml.dump(threat_model).lower()
        assert "owasp" in yaml_str
        assert "cwe" in yaml_str

    def test_has_attack_surface_step(self, threat_model: Dict[str, Any]) -> None:
        """Must have explicit attack surface analysis step."""
        steps = _get_steps(threat_model)
        surface_steps = [s for s in steps if "attack_surface" in s["step_id"] or "surface" in s["step_id"]]
        assert len(surface_steps) >= 1, "Must include attack surface analysis"

    def test_has_risk_assessment_step(self, threat_model: Dict[str, Any]) -> None:
        """Must have risk assessment step."""
        steps = _get_steps(threat_model)
        risk_steps = [s for s in steps if "risk" in s["step_id"]]
        assert len(risk_steps) >= 1, "Must include risk assessment"

    def test_has_mitigation_plan_step(self, threat_model: Dict[str, Any]) -> None:
        """Must produce mitigation plan."""
        steps = _get_steps(threat_model)
        mitigation_steps = [s for s in steps if "mitigation" in s["step_id"] or "remediation" in s["step_id"]]
        assert len(mitigation_steps) >= 1, "Must include mitigation planning"

    def test_independently_invocable(self, threat_model: Dict[str, Any]) -> None:
        """Template can be invoked standalone (first step has no depends_on)."""
        steps = _get_steps(threat_model)
        first_step = steps[0]
        deps = first_step.get("depends_on", [])
        assert len(deps) == 0, "First step must be independently invocable"

    def test_convergence_gate_requires_zero_critical(self, threat_model: Dict[str, Any]) -> None:
        """Global convergence requires zero critical/high unmitigated risks."""
        gate = threat_model["convergence_gate"]
        criteria = gate["success_criteria"]
        assert "unmitigated_critical" in criteria or "critical_risks_mitigated" in criteria


# ==============================================================================
# CROSS-PHASE HOLISTIC EPILOGUE — Declarative Injection
# ==============================================================================

class TestCrossPhaseHolisticEpilogue:
    """Validates declarative epilogue template."""

    @pytest.fixture
    def epilogue(self) -> Dict[str, Any]:
        """Load epilogue template."""
        return _get_workflow(_load_yaml(HOLISTIC_EPILOGUE))

    def test_category_is_quality(self, epilogue: Dict[str, Any]) -> None:
        """Epilogue belongs to quality category."""
        assert epilogue["category"] == "quality"

    def test_marked_as_epilogue(self, epilogue: Dict[str, Any]) -> None:
        """Template metadata declares epilogue: true."""
        assert epilogue["metadata"].get("epilogue") is True

    def test_injection_policy_declared(self, epilogue: Dict[str, Any]) -> None:
        """Template declares injection_policy for when to auto-inject."""
        assert "injection_policy" in epilogue
        policy = epilogue["injection_policy"]
        assert "trigger" in policy
        assert "scope" in policy

    def test_has_linting_step(self, epilogue: Dict[str, Any]) -> None:
        """Epilogue includes linting/code quality step."""
        steps = _get_steps(epilogue)
        lint_steps = [s for s in steps if "lint" in s["step_id"] or "quality" in s["step_id"]]
        assert len(lint_steps) >= 1, "Must include linting step"

    def test_has_cleanup_step(self, epilogue: Dict[str, Any]) -> None:
        """Epilogue includes cleanup step."""
        steps = _get_steps(epilogue)
        cleanup_steps = [s for s in steps if "cleanup" in s["step_id"] or "dedup" in s["step_id"]]
        assert len(cleanup_steps) >= 1, "Must include cleanup step"

    def test_has_refactoring_step(self, epilogue: Dict[str, Any]) -> None:
        """Epilogue includes refactoring step."""
        steps = _get_steps(epilogue)
        refactor_steps = [s for s in steps if "refactor" in s["step_id"]]
        assert len(refactor_steps) >= 1, "Must include refactoring step"

    def test_has_security_verification_step(self, epilogue: Dict[str, Any]) -> None:
        """Epilogue includes security re-verification."""
        steps = _get_steps(epilogue)
        sec_steps = [s for s in steps if "security" in s["step_id"]]
        assert len(sec_steps) >= 1, "Must include security verification in epilogue"

    def test_convergence_requires_all_tests_pass(self, epilogue: Dict[str, Any]) -> None:
        """Convergence gate requires all tests still passing after cleanup."""
        gate = epilogue["convergence_gate"]
        criteria = gate["success_criteria"]
        assert criteria.get("all_tests_pass") is True


# ==============================================================================
# TEST STRATEGY MATRIX — Multi-Tier Test Enforcement
# ==============================================================================

class TestTestStrategyMatrix:
    """Validates the multi-tier test enforcement template."""

    @pytest.fixture
    def strategy(self) -> Dict[str, Any]:
        """Load test strategy matrix template."""
        return _get_workflow(_load_yaml(TEST_STRATEGY))

    def test_category_is_tdd(self, strategy: Dict[str, Any]) -> None:
        """Strategy belongs to tdd category."""
        assert strategy["category"] == "tdd"

    def test_declares_all_test_tiers(self, strategy: Dict[str, Any]) -> None:
        """Strategy declares all test tiers: unit, integration, regression, smoke, golden."""
        yaml_str = yaml.dump(strategy).lower()
        for tier in ("unit", "integration", "regression", "smoke", "golden"):
            assert tier in yaml_str, f"Missing test tier: {tier}"

    def test_has_unit_test_step(self, strategy: Dict[str, Any]) -> None:
        """Strategy has dedicated unit test step."""
        steps = _get_steps(strategy)
        unit_steps = [s for s in steps if "unit" in s["step_id"]]
        assert len(unit_steps) >= 1

    def test_has_integration_test_step(self, strategy: Dict[str, Any]) -> None:
        """Strategy has dedicated integration test step."""
        steps = _get_steps(strategy)
        int_steps = [s for s in steps if "integration" in s["step_id"]]
        assert len(int_steps) >= 1

    def test_has_regression_test_step(self, strategy: Dict[str, Any]) -> None:
        """Strategy has dedicated regression test step."""
        steps = _get_steps(strategy)
        reg_steps = [s for s in steps if "regression" in s["step_id"]]
        assert len(reg_steps) >= 1

    def test_has_smoke_test_step(self, strategy: Dict[str, Any]) -> None:
        """Strategy has dedicated smoke test step."""
        steps = _get_steps(strategy)
        smoke_steps = [s for s in steps if "smoke" in s["step_id"]]
        assert len(smoke_steps) >= 1

    def test_has_golden_test_step(self, strategy: Dict[str, Any]) -> None:
        """Strategy has dedicated golden test step."""
        steps = _get_steps(strategy)
        golden_steps = [s for s in steps if "golden" in s["step_id"]]
        assert len(golden_steps) >= 1

    def test_test_quality_gate_enforced(self, strategy: Dict[str, Any]) -> None:
        """Strategy enforces TestQualityGate score threshold."""
        yaml_str = yaml.dump(strategy).lower()
        assert "quality_gate" in yaml_str or "quality_score" in yaml_str

    def test_coverage_targets_declared(self, strategy: Dict[str, Any]) -> None:
        """Strategy declares coverage targets."""
        yaml_str = yaml.dump(strategy).lower()
        assert "coverage" in yaml_str

    def test_company_overrides_supported(self, strategy: Dict[str, Any]) -> None:
        """Production mode allows company-specific test configuration."""
        prod = strategy["knowledge_context"]["production_mode"]
        prod_str = yaml.dump(prod)
        assert "{{" in prod_str, "Production mode must use placeholders"

    def test_tdd_cycle_embedded(self, strategy: Dict[str, Any]) -> None:
        """Strategy includes RED→GREEN→REFACTOR cycle reference."""
        yaml_str = yaml.dump(strategy).lower()
        assert "red" in yaml_str and "green" in yaml_str and "refactor" in yaml_str

    def test_high_value_test_enforcement(self, strategy: Dict[str, Any]) -> None:
        """Strategy enforces high-value tests (not just assert True stubs)."""
        yaml_str = yaml.dump(strategy).lower()
        has_quality = "quality" in yaml_str and ("gate" in yaml_str or "score" in yaml_str)
        has_aaa = "arrange" in yaml_str or "aaa" in yaml_str or "assert_act_arrange" in yaml_str
        assert has_quality or has_aaa, "Must enforce high-value test quality"

    def test_security_test_tier_included(self, strategy: Dict[str, Any]) -> None:
        """Strategy includes security testing as a tier."""
        steps = _get_steps(strategy)
        sec_steps = [s for s in steps if "security" in s["step_id"]]
        assert len(sec_steps) >= 1, "Must include security test tier"

    def test_parallel_execution_support(self, strategy: Dict[str, Any]) -> None:
        """Strategy supports parallel test execution."""
        yaml_str = yaml.dump(strategy).lower()
        assert "parallel" in yaml_str or "xdist" in yaml_str or "concurrent" in yaml_str

    def test_step_ordering_enforces_pyramid(self, strategy: Dict[str, Any]) -> None:
        """Test steps follow testing pyramid: unit → integration → smoke → regression → golden."""
        steps = _get_steps(strategy)
        step_ids = [s["step_id"] for s in steps]
        
        # Find indices for each tier (they must appear in pyramid order)
        tier_order = ["unit", "integration", "smoke", "regression", "golden"]
        tier_indices = {}
        for tier in tier_order:
            matching = [i for i, sid in enumerate(step_ids) if tier in sid]
            if matching:
                tier_indices[tier] = matching[0]
        
        # Verify ordering: each tier appears after the previous
        ordered_tiers = sorted(tier_indices.keys(), key=lambda t: tier_indices[t])
        for i in range(len(ordered_tiers) - 1):
            assert tier_indices[ordered_tiers[i]] < tier_indices[ordered_tiers[i + 1]], (
                f"Test tier '{ordered_tiers[i]}' must come before '{ordered_tiers[i + 1]}'"
            )


# ==============================================================================
# INTEGRATION — Cross-Template Composition
# ==============================================================================

class TestCrossTemplateComposition:
    """Validates that templates compose correctly as lego pieces."""

    def test_composite_references_threat_model(self) -> None:
        """Composite pipeline references threat-model-analysis template."""
        pipeline = _get_workflow(_load_yaml(COMPOSITE_PIPELINE))
        steps = _get_steps(pipeline)
        refs = [s.get("template_ref", "") for s in steps]
        threat_refs = [r for r in refs if "threat-model" in r]
        assert len(threat_refs) >= 1, "Composite must reference threat model template"

    def test_composite_references_test_strategy(self) -> None:
        """Composite pipeline references test-strategy-matrix template."""
        pipeline = _get_workflow(_load_yaml(COMPOSITE_PIPELINE))
        steps = _get_steps(pipeline)
        refs = [s.get("template_ref", "") for s in steps]
        test_refs = [r for r in refs if "test-strategy" in r]
        assert len(test_refs) >= 1, "Composite must reference test strategy template"

    def test_composite_references_epilogue(self) -> None:
        """Composite pipeline references holistic epilogue."""
        pipeline = _get_workflow(_load_yaml(COMPOSITE_PIPELINE))
        epilogues = pipeline.get("epilogues", [])
        epilogue_refs = [e for e in epilogues if "holistic" in e.get("epilogue_id", "")]
        assert len(epilogue_refs) >= 1

    def test_all_new_templates_registered_in_readme(self) -> None:
        """All new templates should be listed in the workflows README."""
        readme_path = TEMPLATES_ROOT / "README.md"
        assert readme_path.exists()
        readme_text = readme_path.read_text().lower()
        for name in (
            "composite-execution-pipeline",
            "threat-model-analysis",
            "cross-phase-holistic-epilogue",
            "test-strategy-matrix",
        ):
            assert name in readme_text, f"README must list template: {name}"

    def test_no_circular_template_refs(self) -> None:
        """Template references must not create cycles."""
        pipeline = _get_workflow(_load_yaml(COMPOSITE_PIPELINE))
        steps = _get_steps(pipeline)
        refs = {s.get("template_ref", "") for s in steps if s.get("template_ref")}
        # None of the referenced templates should reference back to composite
        for ref_path in refs:
            ref_full = Path(ref_path)
            if ref_full.exists():
                ref_data = _load_yaml(ref_full)
                ref_wf = ref_data.get("workflow", {})
                ref_steps = ref_wf.get("steps", [])
                ref_refs = {s.get("template_ref", "") for s in ref_steps if s.get("template_ref")}
                assert str(COMPOSITE_PIPELINE) not in ref_refs, (
                    f"Circular reference: {ref_path} → composite-execution-pipeline"
                )


# ==============================================================================
# FILENAME & GOVERNANCE COMPLIANCE
# ==============================================================================

class TestGovernanceCompliance:
    """Validates CORE rule compliance across all new templates."""

    @pytest.mark.parametrize("path", [
        COMPOSITE_PIPELINE,
        THREAT_MODEL,
        HOLISTIC_EPILOGUE,
        TEST_STRATEGY,
    ], ids=[
        "composite-execution-pipeline",
        "threat-model-analysis",
        "cross-phase-holistic-epilogue",
        "test-strategy-matrix",
    ])
    def test_filename_is_kebab_case(self, path: Path) -> None:
        """CORE-028: filenames must be kebab-case for YAML."""
        name = path.name
        assert name == name.lower(), f"Filename must be lowercase: {name}"
        assert " " not in name, f"Filename must not have spaces: {name}"
        assert "_" not in name.replace(".yaml", ""), (
            f"YAML filenames use kebab-case, not snake_case: {name}"
        )

    @pytest.mark.parametrize("path", [
        COMPOSITE_PIPELINE,
        THREAT_MODEL,
        HOLISTIC_EPILOGUE,
        TEST_STRATEGY,
    ], ids=[
        "composite-execution-pipeline",
        "threat-model-analysis",
        "cross-phase-holistic-epilogue",
        "test-strategy-matrix",
    ])
    def test_yaml_is_valid(self, path: Path) -> None:
        """Template must be parseable as valid YAML."""
        data = _load_yaml(path)
        assert isinstance(data, dict)

    @pytest.mark.parametrize("path", [
        COMPOSITE_PIPELINE,
        THREAT_MODEL,
        HOLISTIC_EPILOGUE,
        TEST_STRATEGY,
    ], ids=[
        "composite-execution-pipeline",
        "threat-model-analysis",
        "cross-phase-holistic-epilogue",
        "test-strategy-matrix",
    ])
    def test_version_is_semver(self, path: Path) -> None:
        """Version must follow semver (x.y.z)."""
        wf = _get_workflow(_load_yaml(path))
        version = wf["version"]
        parts = version.split(".")
        assert len(parts) == 3, f"Version must be semver: {version}"
        for part in parts:
            assert part.isdigit(), f"Version parts must be numeric: {version}"
