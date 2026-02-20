"""
Phase 08 GREEN Phase — Registry & Docs Alignment Validation

Validates all Phase 08 deliverables are implemented and functional:
  1. Registry structure validation (workflow templates, knowledge base, wiring specs)
  2. Enterprise patterns (9 pattern YAMLs)
  3. Infrastructure catalog (schema, folders, topology)
  4. InfrastructureDetector functionality
  5. cortex_onboard_infrastructure MCP tool
  6. Exit gate validation

Authority: Phase 08 — Registry & Docs Alignment
"""

import pytest
from pathlib import Path


# ==============================================================================
# Registry Structure Validation
# ==============================================================================


class TestRegistryWorkflowTemplates:
    """Validate workflow templates directory and schema."""

    def test_workflow_templates_directory_exists(self) -> None:
        """Workflow templates directory exists with subdirectories."""
        templates_dir = Path("cortex-registry/workflows/templates/")
        assert templates_dir.exists(), "Templates directory must exist"
        subdirs = [d.name for d in templates_dir.iterdir() if d.is_dir()]
        assert len(subdirs) >= 3, f"Expected 3+ template subdirs, got {len(subdirs)}: {subdirs}"

    def test_workflow_templates_have_yaml_files(self) -> None:
        """At least one YAML file per template subdirectory."""
        templates_dir = Path("cortex-registry/workflows/templates/")
        yaml_files = list(templates_dir.rglob("*.yaml"))
        assert len(yaml_files) >= 3, f"Expected 3+ workflow YAML files, got {len(yaml_files)}"

    def test_lifecycle_templates_exist(self) -> None:
        """Lifecycle templates directory contains key orchestrator templates."""
        lifecycle_dir = Path("cortex-registry/workflows/templates/lifecycle/")
        assert lifecycle_dir.exists(), "Lifecycle templates directory must exist"


class TestRegistryKnowledgeBase:
    """Validate knowledge base completeness."""

    def test_governance_rules_complete(self) -> None:
        """5 governance compliance rule files in knowledge base."""
        gov_dir = Path("cortex-registry/knowledge-base/governance/")
        assert gov_dir.exists()
        yaml_files = list(gov_dir.glob("*.yaml"))
        assert len(yaml_files) >= 5, f"Expected 5+ governance rules, got {len(yaml_files)}"

    def test_industry_profiles_complete(self) -> None:
        """6 industry profile YAMLs in knowledge base."""
        profiles_dir = Path("cortex-registry/knowledge-base/profiles/")
        assert profiles_dir.exists()
        yaml_files = list(profiles_dir.glob("*.yaml"))
        assert len(yaml_files) >= 6, f"Expected 6+ profiles, got {len(yaml_files)}"

    def test_repository_profiles_complete(self) -> None:
        """2 repository profile YAMLs in knowledge base."""
        repos_dir = Path("cortex-registry/knowledge-base/repositories/")
        assert repos_dir.exists()
        yaml_files = list(repos_dir.glob("*.yaml"))
        assert len(yaml_files) >= 2, f"Expected 2+ repo profiles, got {len(yaml_files)}"

    def test_security_knowledge_complete(self) -> None:
        """3 security knowledge YAMLs in knowledge base."""
        security_dir = Path("cortex-registry/knowledge-base/security/")
        assert security_dir.exists()
        yaml_files = list(security_dir.glob("*.yaml"))
        assert len(yaml_files) >= 3, f"Expected 3+ security files, got {len(yaml_files)}"

    def test_knowledge_base_total_files(self) -> None:
        """Total knowledge base has 16+ YAML files."""
        kb_dir = Path("cortex-registry/knowledge-base/")
        yaml_files = list(kb_dir.rglob("*.yaml"))
        assert len(yaml_files) >= 16, f"Expected 16+ total KB files, got {len(yaml_files)}"


class TestRegistryCoreSpecifications:
    """Validate core wiring specifications."""

    def test_all_8_wiring_specs_exist(self) -> None:
        """All 8 wiring specification files exist."""
        specs_dir = Path("cortex-registry/core/specifications/")
        assert specs_dir.exists()
        expected = [
            "core-orchestrator-wiring.yaml",
            "domain-orchestrator-wiring.yaml",
            "domain-transition-rules.yaml",
            "execution-flow-specification.yaml",
            "governance-validation-gates.yaml",
            "intent-routing-rules.yaml",
            "orchestration-master-wiring.yaml",
            "support-orchestrator-wiring.yaml",
        ]
        for spec_file in expected:
            assert (specs_dir / spec_file).exists(), f"Missing: {spec_file}"


# ==============================================================================
# Enterprise Patterns Validation
# ==============================================================================


class TestEnterprisePatterns:
    """Validate 9 enterprise pattern YAMLs."""

    EXPECTED_PATTERNS = [
        "mediator-orchestration.yaml",
        "strategy-workflow.yaml",
        "observer-event-bus.yaml",
        "factory-creation.yaml",
        "template-method-lifecycle.yaml",
        "chain-of-responsibility-governance.yaml",
        "adapter-mcp.yaml",
        "repository-registry.yaml",
        "command-workflow-step.yaml",
    ]

    def test_patterns_directory_populated(self) -> None:
        """Patterns directory has 9 enterprise pattern YAMLs."""
        patterns_dir = Path("cortex-registry/patterns/")
        assert patterns_dir.exists()
        yaml_files = list(patterns_dir.glob("*.yaml"))
        assert len(yaml_files) >= 9, f"Expected 9+ patterns, got {len(yaml_files)}"

    @pytest.mark.parametrize("pattern_file", EXPECTED_PATTERNS)
    def test_pattern_file_exists(self, pattern_file: str) -> None:
        """Each expected pattern file exists."""
        path = Path("cortex-registry/patterns/") / pattern_file
        assert path.exists(), f"Missing pattern: {pattern_file}"

    def test_pattern_files_are_valid_yaml(self) -> None:
        """All pattern files are parseable YAML."""
        import yaml

        patterns_dir = Path("cortex-registry/patterns/")
        for yaml_file in patterns_dir.glob("*.yaml"):
            content = yaml_file.read_text()
            try:
                data = yaml.safe_load(content)
                assert data is not None, f"Empty YAML: {yaml_file.name}"
                assert "pattern" in data, f"Missing 'pattern' key in {yaml_file.name}"
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in {yaml_file.name}: {e}")

    def test_pattern_files_have_required_fields(self) -> None:
        """Each pattern file has name, type, description, cortex_usage."""
        import yaml

        patterns_dir = Path("cortex-registry/patterns/")
        required = {"name", "type", "description", "cortex_usage"}
        for yaml_file in patterns_dir.glob("*.yaml"):
            data = yaml.safe_load(yaml_file.read_text())
            pattern_data = data.get("pattern", {})
            missing = required - set(pattern_data.keys())
            assert not missing, f"{yaml_file.name} missing fields: {missing}"


# ==============================================================================
# Infrastructure Catalog Validation
# ==============================================================================


class TestInfrastructureCatalog:
    """Validate infrastructure catalog schema and folder structure."""

    def test_schema_file_exists(self) -> None:
        """_schema.yaml exists in infrastructure directory."""
        schema = Path("cortex-registry/company/infrastructure/_schema.yaml")
        assert schema.exists(), "Infrastructure _schema.yaml must exist"

    def test_schema_defines_three_entity_types(self) -> None:
        """Schema defines platform, api, and application schemas."""
        import yaml

        schema = Path("cortex-registry/company/infrastructure/_schema.yaml")
        data = yaml.safe_load(schema.read_text())
        schemas = data.get("schemas", {})
        assert "platform" in schemas, "Missing platform schema"
        assert "api" in schemas, "Missing api schema"
        assert "application" in schemas, "Missing application schema"

    def test_platform_schema_has_required_fields(self) -> None:
        """Platform schema defines 8+ fields."""
        import yaml

        schema = Path("cortex-registry/company/infrastructure/_schema.yaml")
        data = yaml.safe_load(schema.read_text())
        platform_fields = data["schemas"]["platform"]["fields"]
        assert len(platform_fields) >= 8, f"Expected 8+ platform fields, got {len(platform_fields)}"

    def test_api_schema_has_required_fields(self) -> None:
        """API schema defines 11+ fields."""
        import yaml

        schema = Path("cortex-registry/company/infrastructure/_schema.yaml")
        data = yaml.safe_load(schema.read_text())
        api_fields = data["schemas"]["api"]["fields"]
        assert len(api_fields) >= 11, f"Expected 11+ api fields, got {len(api_fields)}"

    def test_application_schema_has_required_fields(self) -> None:
        """Application schema defines 10+ fields."""
        import yaml

        schema = Path("cortex-registry/company/infrastructure/_schema.yaml")
        data = yaml.safe_load(schema.read_text())
        app_fields = data["schemas"]["application"]["fields"]
        assert len(app_fields) >= 10, f"Expected 10+ app fields, got {len(app_fields)}"

    def test_folder_structure_complete(self) -> None:
        """Infrastructure has platforms/, apis/, applications/ subdirectories."""
        base = Path("cortex-registry/company/infrastructure/")
        assert (base / "platforms").is_dir(), "Missing platforms/"
        assert (base / "apis").is_dir(), "Missing apis/"
        assert (base / "applications").is_dir(), "Missing applications/"

    def test_topology_file_exists(self) -> None:
        """topology.yaml exists in infrastructure directory."""
        topology = Path("cortex-registry/company/infrastructure/topology.yaml")
        assert topology.exists(), "topology.yaml must exist"


# ==============================================================================
# InfrastructureDetector Validation
# ==============================================================================


class TestInfrastructureDetector:
    """Validate InfrastructureDetector implementation."""

    def test_detector_importable(self) -> None:
        """InfrastructureDetector can be imported."""
        from cortex.intelligence.infrastructure.detector import InfrastructureDetector

        assert InfrastructureDetector is not None

    def test_detector_init(self, tmp_path: Path) -> None:
        """Detector initializes with repo path."""
        from cortex.intelligence.infrastructure.detector import InfrastructureDetector

        detector = InfrastructureDetector(repo_path=str(tmp_path))
        assert detector.repo_path == tmp_path

    def test_detector_fastapi_detection(self, tmp_path: Path) -> None:
        """Detector identifies FastAPI routes."""
        from cortex.intelligence.infrastructure.detector import InfrastructureDetector

        py_file = tmp_path / "main.py"
        py_file.write_text("from fastapi import FastAPI\napp = FastAPI()\n@app.get('/health')\ndef health(): pass\n")
        detector = InfrastructureDetector(repo_path=str(tmp_path))
        hints = detector.detect_all()
        api_hints = [h for h in hints if h.category == "api"]
        assert len(api_hints) >= 1, "Should detect FastAPI route"
        assert "fastapi" in api_hints[0].details.get("framework", "")

    def test_detector_dockerfile_detection(self, tmp_path: Path) -> None:
        """Detector identifies Dockerfile → containerized."""
        from cortex.intelligence.infrastructure.detector import InfrastructureDetector

        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text("FROM python:3.11\nCOPY . .\n")
        detector = InfrastructureDetector(repo_path=str(tmp_path))
        hints = detector.detect_all()
        platform_hints = [h for h in hints if h.category == "platform"]
        assert len(platform_hints) >= 1, "Should detect Dockerfile"
        assert "containerized" in platform_hints[0].inferred_type

    def test_detector_kubernetes_detection(self, tmp_path: Path) -> None:
        """Detector identifies k8s/ directory → Kubernetes."""
        from cortex.intelligence.infrastructure.detector import InfrastructureDetector

        k8s_dir = tmp_path / "k8s"
        k8s_dir.mkdir()
        (k8s_dir / "deployment.yaml").write_text("apiVersion: apps/v1\n")
        detector = InfrastructureDetector(repo_path=str(tmp_path))
        hints = detector.detect_all()
        k8s_hints = [h for h in hints if "Kubernetes" in h.inferred_type]
        assert len(k8s_hints) >= 1, "Should detect Kubernetes manifests"

    def test_detector_cloud_config_detection(self, tmp_path: Path) -> None:
        """Detector identifies cloud provider configs."""
        from cortex.intelligence.infrastructure.detector import InfrastructureDetector

        gh_dir = tmp_path / ".github" / "workflows"
        gh_dir.mkdir(parents=True)
        (gh_dir / "ci.yaml").write_text("name: CI\n")
        detector = InfrastructureDetector(repo_path=str(tmp_path))
        hints = detector.detect_all()
        cloud_hints = [h for h in hints if h.category == "cloud"]
        assert len(cloud_hints) >= 1, "Should detect GitHub Actions"

    def test_detector_non_blocking_on_failure(self, tmp_path: Path) -> None:
        """Detection failures don't raise — return empty hints."""
        from cortex.intelligence.infrastructure.detector import InfrastructureDetector

        # Non-existent path should not raise
        detector = InfrastructureDetector(repo_path="/nonexistent/path/xyz")
        hints = detector.detect_all()
        assert isinstance(hints, list)

    def test_detector_generate_drafts(self, tmp_path: Path) -> None:
        """Detector generates draft YAML dicts from hints."""
        from cortex.intelligence.infrastructure.detector import (
            InfrastructureDetector,
            InfrastructureHint,
        )

        hints = [
            InfrastructureHint(
                category="api",
                source_file="main.py",
                inferred_type="REST API exposed (fastapi)",
                confidence=0.85,
                details={"framework": "fastapi"},
            )
        ]
        detector = InfrastructureDetector(repo_path=str(tmp_path))
        drafts = detector.generate_drafts(hints, repo_name="test-repo")
        assert "draft-app-test-repo.yaml" in drafts
        assert "draft-api-test-repo.yaml" in drafts
        assert drafts["draft-app-test-repo.yaml"]["status"] == "draft"


# ==============================================================================
# MCP Tool Validation
# ==============================================================================


class TestOnboardInfrastructureTool:
    """Validate cortex_onboard_infrastructure MCP tool."""

    def test_tool_importable(self) -> None:
        """onboard_infrastructure module is importable."""
        from cortex.mcp.tools.onboard_infrastructure import onboard_infrastructure

        assert callable(onboard_infrastructure)

    def test_create_platform_yaml(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Tool creates platform YAML in correct directory."""
        from cortex.mcp.tools import onboard_infrastructure as mod

        infra_dir = tmp_path / "infrastructure"
        monkeypatch.setattr(mod, "INFRASTRUCTURE_DIR", infra_dir)
        result = mod.onboard_infrastructure(
            entity_type="platform",
            name="azure-aks-prod",
            data={"type": "kubernetes", "provider": "azure"},
        )
        assert result["status"] == "success"
        assert (infra_dir / "platforms" / "azure-aks-prod.yaml").exists()

    def test_create_api_yaml(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Tool creates API YAML in correct directory."""
        from cortex.mcp.tools import onboard_infrastructure as mod

        infra_dir = tmp_path / "infrastructure"
        monkeypatch.setattr(mod, "INFRASTRUCTURE_DIR", infra_dir)
        result = mod.onboard_infrastructure(
            entity_type="api",
            name="user-service-api",
            data={"type": "rest", "version": "2.1.0"},
        )
        assert result["status"] == "success"
        assert (infra_dir / "apis" / "user-service-api.yaml").exists()

    def test_create_application_yaml(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Tool creates application YAML in correct directory."""
        from cortex.mcp.tools import onboard_infrastructure as mod

        infra_dir = tmp_path / "infrastructure"
        monkeypatch.setattr(mod, "INFRASTRUCTURE_DIR", infra_dir)
        result = mod.onboard_infrastructure(
            entity_type="application",
            name="frontend-spa",
            data={"type": "web-spa", "repository": "frontend-repo"},
        )
        assert result["status"] == "success"
        assert (infra_dir / "applications" / "frontend-spa.yaml").exists()

    def test_schema_validation_rejects_invalid(self) -> None:
        """Tool rejects invalid entity_type."""
        from cortex.mcp.tools.onboard_infrastructure import onboard_infrastructure

        result = onboard_infrastructure(
            entity_type="invalid",
            name="test",
            data={},
        )
        assert result["status"] == "error"
        assert len(result["errors"]) > 0

    def test_schema_validation_rejects_missing_fields(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Tool rejects data missing required fields."""
        from cortex.mcp.tools import onboard_infrastructure as mod

        infra_dir = tmp_path / "infrastructure"
        monkeypatch.setattr(mod, "INFRASTRUCTURE_DIR", infra_dir)
        result = mod.onboard_infrastructure(
            entity_type="platform",
            name="test",
            data={},  # Missing type and provider
        )
        assert result["status"] == "error"
        assert any("type" in e for e in result["errors"])

    def test_repo_cross_reference(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Tool adds repo cross-reference when link_to_repo provided."""
        from cortex.mcp.tools import onboard_infrastructure as mod

        infra_dir = tmp_path / "infrastructure"
        monkeypatch.setattr(mod, "INFRASTRUCTURE_DIR", infra_dir)
        result = mod.onboard_infrastructure(
            entity_type="application",
            name="my-app",
            data={"type": "api-service", "repository": "my-repo"},
            link_to_repo="my-repo",
        )
        assert result["status"] == "success"
        content = (infra_dir / "applications" / "my-app.yaml").read_text()
        assert "my-repo" in content

    def test_topology_regeneration(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Tool regenerates topology.yaml after entity creation."""
        from cortex.mcp.tools import onboard_infrastructure as mod

        infra_dir = tmp_path / "infrastructure"
        monkeypatch.setattr(mod, "INFRASTRUCTURE_DIR", infra_dir)
        mod.onboard_infrastructure(
            entity_type="platform",
            name="test-cluster",
            data={"type": "kubernetes", "provider": "aws"},
        )
        topology = infra_dir / "topology.yaml"
        assert topology.exists(), "topology.yaml should be regenerated"
        content = topology.read_text()
        assert "test-cluster" in content


# ==============================================================================
# Exit Gates
# ==============================================================================


class TestPhase08ExitGates:
    """Phase 08 exit gate validation."""

    def test_exit_gate_patterns_populated(self) -> None:
        """Exit gate: patterns directory has 9 enterprise patterns."""
        patterns_dir = Path("cortex-registry/patterns/")
        yaml_files = list(patterns_dir.glob("*.yaml"))
        assert len(yaml_files) >= 9

    def test_exit_gate_knowledge_base_complete(self) -> None:
        """Exit gate: knowledge base has 16+ YAML files."""
        kb_dir = Path("cortex-registry/knowledge-base/")
        yaml_files = list(kb_dir.rglob("*.yaml"))
        assert len(yaml_files) >= 16

    def test_exit_gate_infrastructure_catalog_functional(self) -> None:
        """Exit gate: infrastructure catalog schema and folders exist."""
        base = Path("cortex-registry/company/infrastructure/")
        assert (base / "_schema.yaml").exists()
        assert (base / "topology.yaml").exists()
        assert (base / "platforms").is_dir()
        assert (base / "apis").is_dir()
        assert (base / "applications").is_dir()

    def test_exit_gate_wiring_specs_complete(self) -> None:
        """Exit gate: all 8 core wiring specifications exist."""
        specs_dir = Path("cortex-registry/core/specifications/")
        yaml_files = list(specs_dir.glob("*.yaml"))
        assert len(yaml_files) >= 8
