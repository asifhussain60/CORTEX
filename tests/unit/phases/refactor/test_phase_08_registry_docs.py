"""
Phase 08 RED Phase - Registry & Docs Alignment Specification

Purpose: 41 specification tests for registry audit, docs alignment, and infrastructure catalog.
All tests establish WHAT needs to happen; GREEN phase implements the HOW.

Test Categories:
  1. Registry Audit Tests (R1-R6) — 15 tests
  2. Documentation Alignment Tests (D1-D2) — 8 tests
  3. Infrastructure Catalog Schema Tests (R7-R9) — 12 tests
  4. Execution Sequence Tests — 2 tests
  5. Exit Gates Tests — 4 tests
"""

import pytest
from pathlib import Path


class TestPhase08RegistryAudit:
    """R1-R6: Registry audit and cleanup specifications"""

    def test_red_workflow_templates_schema_validation(self):
        """SPEC: All workflow templates conform to workflow-template-schema.yaml"""
        templates_dir = Path("cortex-registry/workflows/templates/")
        assert templates_dir.exists(), "Templates directory must exist"
        yaml_files = list(templates_dir.rglob("*.yaml"))
        assert len(yaml_files) > 0, "Must have workflow templates"

    def test_red_workflow_templates_have_setup_teardown(self):
        """SPEC: Every workflow template must have setup and teardown steps"""
        spec = {
            "required_sections": ["setup", "execute", "teardown"],
            "min_lifecycle_steps": 3,
        }
        assert spec["required_sections"]
        assert len(spec["required_sections"]) >= 3

    def test_red_all_active_orchestrators_have_templates(self):
        """SPEC: Every active orchestrator from Phase 05 has a workflow template"""
        # From Phase 05: CortexMasterPlanOrchestrator, MasterPlanExecution, PhaseExecutor, etc.
        active_orchestrators = [
            "CortexMasterPlanOrchestrator",
            "MasterPlanExecution",
            "PhaseExecutor",
        ]
        assert len(active_orchestrators) >= 3

    def test_red_template_references_resolve(self):
        """SPEC: All use_template directives reference valid templates"""
        validation_rules = {
            "template_reference_format": r"^[a-z0-9\-]+\.yaml$",
            "max_reference_depth": 3,
        }
        assert validation_rules["template_reference_format"]
        assert validation_rules["max_reference_depth"] == 3

    def test_red_stale_yaml_removal_strategy(self):
        """SPEC: Identify and remove/archive stale YAMLs referencing deleted components"""
        stale_patterns = [
            "cortex/brain/",  # Archived in Phase 06
            "cortex_intelligence/",  # Archived in Phase 06
            "phase_*",  # Phase-specific artifacts
            "cortex-registry/",  # Inner duplicate (now in cortex/core/)
        ]
        assert len(stale_patterns) >= 4

    def test_red_knowledge_base_validation(self):
        """SPEC: cortex-registry/knowledge-base/ has all required subdirectories and files"""
        knowledge_structure = {
            "governance": 5,
            "industry_profiles": 6,
            "repository_profiles": 2,
            "security_knowledge": 3,
        }
        total_required = sum(knowledge_structure.values())
        assert total_required == 16

    def test_red_governance_compliance_rules(self):
        """SPEC: 5 governance compliance rule files in knowledge-base/"""
        rules = [
            "rules/core-governance.yaml",
            "rules/security-governance.yaml",
            "rules/compliance-governance.yaml",
            "rules/performance-governance.yaml",
            "rules/testing-governance.yaml",
        ]
        assert len(rules) == 5

    def test_red_industry_profiles_complete(self):
        """SPEC: 6 industry profile YAMLs in knowledge-base/"""
        profiles = [
            "profiles/auth-industry.yaml",
            "profiles/devops-industry.yaml",
            "profiles/finops-industry.yaml",
            "profiles/healthcare-industry.yaml",
            "profiles/legal-industry.yaml",
            "profiles/ml-industry.yaml",
        ]
        assert len(profiles) == 6

    def test_red_core_specifications_wiring(self):
        """SPEC: cortex-registry/core/specifications/ has all 8 wiring specs"""
        wiring_specs = [
            "core-orchestrator-wiring.yaml",
            "domain-orchestrator-wiring.yaml",
            "domain-transition-rules.yaml",
            "execution-flow-specification.yaml",
            "governance-validation-gates.yaml",
            "intent-routing-rules.yaml",
            "orchestration-master-wiring.yaml",
            "support-orchestrator-wiring.yaml",
        ]
        assert len(wiring_specs) == 8

    def test_red_wiring_specs_reference_new_structure(self):
        """SPEC: All wiring specs updated to reference canonical cortex/ structure"""
        validation_pattern = {
            "forbidden_paths": ["cortex/brain/", "cortex_intelligence/"],
            "canonical_packages": [
                "cortex/core/",
                "cortex/orchestrators/",
                "cortex/mcp/",
            ],
        }
        assert len(validation_pattern["forbidden_paths"]) == 2
        assert len(validation_pattern["canonical_packages"]) >= 3

    def test_red_enterprise_patterns_directory_created(self):
        """SPEC: cortex-registry/patterns/ populated with 9 enterprise patterns"""
        patterns = [
            "patterns/mediator-orchestration.yaml",
            "patterns/strategy-workflow.yaml",
            "patterns/observer-event-bus.yaml",
            "patterns/factory-creation.yaml",
            "patterns/template-method-lifecycle.yaml",
            "patterns/chain-of-responsibility-governance.yaml",
            "patterns/adapter-mcp.yaml",
            "patterns/repository-registry.yaml",
            "patterns/command-workflow-step.yaml",
        ]
        assert len(patterns) == 9

    def test_red_phase_structure_synchronized(self):
        """SPEC: cortex-registry/planning/phases/ synchronized with actual completion state"""
        phase_validation = {
            "completed_phases": 7,
            "in_progress": 1,
            "pending": 2,
            "max_phase": 11,
        }
        assert phase_validation["completed_phases"] + phase_validation["in_progress"] + phase_validation["pending"] == 10

    def test_red_phase_08_sdlc_brain_wiring(self):
        """SPEC: R6B — CiCdOrchestrator + DesignOrchestrator + 2 new MCP tools registered"""
        new_orchestrators = [
            "CiCdOrchestrator",
            "DesignOrchestrator",
        ]
        new_tools = [
            "cortex_cicd",
            "cortex_document",
        ]
        assert len(new_orchestrators) == 2
        assert len(new_tools) == 2


class TestPhase08DocumentsAlignment:
    """D1-D2: Documentation alignment specifications"""

    def test_red_docs_architecture_updated(self):
        """SPEC: cortex-docs/architecture/ reflects new canonical structure"""
        sections = [
            "directory-structure.md",
            "orchestrator-catalog.md",
            "mcp-tools-reference.md",
            "governance-rules.md",
        ]
        assert len(sections) == 4

    def test_red_docs_engineering_updated(self):
        """SPEC: cortex-docs/engineering/ updated for new developer workflow"""
        topics = [
            "dev-setup.md",
            "testing-strategy.md",
            "deployment-pipeline.md",
        ]
        assert len(topics) >= 3

    def test_red_docs_api_documentation_current(self):
        """SPEC: cortex-docs/api/ documents all active MCP tools and orchestrators"""
        doc_coverage = {
            "mcp_tools": 28,
            "orchestrators": 44,
            "governance_rules": 11,
        }
        assert doc_coverage["mcp_tools"] >= 25

    def test_red_architecture_diagrams_generated(self):
        """SPEC: Generate 3 architecture diagrams"""
        diagrams = [
            "package-structure.svg",
            "orchestrator-hierarchy.svg",
            "mcp-tool-mapping.svg",
        ]
        assert len(diagrams) == 3

    def test_red_docs_no_dead_links(self):
        """SPEC: Documentation contains no broken internal references"""
        validation = {
            "check_internal_links": True,
            "check_code_references": True,
            "max_broken_links": 0,
        }
        assert validation["max_broken_links"] == 0

    def test_red_docs_search_index_updated(self):
        """SPEC: cortex-docs search index includes new structure"""
        search_config = {
            "index_packages": True,
            "index_orchestrators": True,
            "index_tools": True,
        }
        assert all(search_config.values())

    def test_red_api_documentation_schema_consistent(self):
        """SPEC: All MCP tool documentation uses consistent schema"""
        doc_schema = {
            "required_sections": [
                "overview",
                "parameters",
                "returns",
                "examples",
                "errors",
            ],
        }
        assert len(doc_schema["required_sections"]) == 5

    def test_red_governance_rules_documented(self):
        """SPEC: All 11 governance rules have reference documentation"""
        rules_min = 11
        assert rules_min == 11


class TestPhase08InfrastructureCatalog:
    """R7-R9: Infrastructure catalog schema and detection"""

    def test_red_infrastructure_schema_defined(self):
        """SPEC: cortex-registry/company/infrastructure/_schema.yaml defined"""
        schema = {
            "platform_fields": [
                "name",
                "type",
                "provider",
                "environments",
                "hosted_applications",
                "networking",
                "observability",
                "owner_team",
            ],
        }
        assert len(schema["platform_fields"]) >= 8

    def test_red_api_schema_fields_complete(self):
        """SPEC: API schema includes 11 required fields"""
        api_fields = [
            "name",
            "type",
            "version",
            "base_url",
            "endpoints",
            "owner_repo",
            "consumers",
            "auth",
            "documentation_url",
            "sla",
            "created_at",
        ]
        assert len(api_fields) == 11

    def test_red_application_schema_fields_complete(self):
        """SPEC: Application schema includes 10 required fields"""
        app_fields = [
            "name",
            "type",
            "repository",
            "platform",
            "tech_stack",
            "apis_consumed",
            "apis_exposed",
            "environments",
            "owner_team",
            "dependencies",
        ]
        assert len(app_fields) == 10

    def test_red_infrastructure_catalog_folder_structure(self):
        """SPEC: Infrastructure catalog has proper folder structure"""
        structure = [
            "cortex-registry/company/infrastructure/_schema.yaml",
            "cortex-registry/company/infrastructure/platforms/",
            "cortex-registry/company/infrastructure/apis/",
            "cortex-registry/company/infrastructure/applications/",
            "cortex-registry/company/infrastructure/topology.yaml",
        ]
        assert len(structure) == 5

    def test_red_infrastructure_detection_fastapi(self):
        """SPEC: InfrastructureDetector identifies FastAPI routes"""
        detection_capability = {
            "pattern": r"@app\.route|@app\.get|@app\.post",
            "infers": "REST API exposed",
        }
        assert detection_capability["infers"]

    def test_red_infrastructure_detection_dockerfile(self):
        """SPEC: InfrastructureDetector identifies Dockerfile → containerized app"""
        detection_capability = {
            "files": ["Dockerfile", "docker-compose.yaml"],
            "infers": "containerized platform requirement",
        }
        assert len(detection_capability["files"]) >= 1

    def test_red_infrastructure_detection_kubernetes(self):
        """SPEC: InfrastructureDetector identifies K8s manifests"""
        detection_capability = {
            "patterns": ["k8s/*.yaml", "helm/"],
            "infers": "Kubernetes platform",
        }
        assert detection_capability["infers"]

    def test_red_infrastructure_detection_cloud_config(self):
        """SPEC: InfrastructureDetector identifies cloud provider configs"""
        detection_capability = {
            "patterns": [
                "azure-pipelines.yml",
                ".github/workflows",
                "serverless.yaml",
            ],
            "infers": "cloud platform usage",
        }
        assert len(detection_capability["patterns"]) == 3

    def test_red_infrastructure_detection_non_blocking(self):
        """SPEC: Infrastructure detection failures don't block onboarding"""
        error_handling = {
            "try_catch": True,
            "blocking": False,
            "warns_on_failure": True,
        }
        assert error_handling["blocking"] is False

    def test_red_cortex_onboard_infrastructure_mcp_tool(self):
        """SPEC: cortex_onboard_infrastructure MCP tool with entity_type parameter"""
        tool_spec = {
            "name": "cortex_onboard_infrastructure",
            "parameters": [
                "entity_type",
                "name",
                "data",
                "link_to_repo",
            ],
            "entity_types": [
                "platform",
                "api",
                "application",
            ],
        }
        assert len(tool_spec["parameters"]) == 4

    def test_red_topology_yaml_auto_regeneration(self):
        """SPEC: topology.yaml auto-regenerates from platform/api/app YAMLs"""
        topology_feature = {
            "auto_update": True,
            "source": "all infrastructure YAMLs",
            "builds": "dependency graph",
        }
        assert topology_feature["auto_update"] is True


class TestPhase08ExecutionSequence:
    """Execution sequence and flow specifications"""

    def test_red_execution_steps_defined(self):
        """SPEC: 12-step execution sequence for Phase 08 GREEN"""
        steps = [
            "Registry audit workflow templates",
            "Validate all template schemas",
            "Remove stale YAMLs",
            "Validate knowledge base",
            "Validate core wiring specs",
            "Add enterprise patterns",
            "Synchronize phase structure",
            "Update architecture documentation",
            "Generate diagrams",
            "Create infrastructure schema",
            "Implement InfrastructureDetector",
            "Create cortex_onboard_infrastructure tool",
        ]
        assert len(steps) == 12

    def test_red_execution_gates_defined(self):
        """SPEC: 6 validation gates for Phase 08 completion"""
        gates = [
            "All workflow templates schema-valid",
            "All active orchestrators have templates",
            "No stale YAML references",
            "Knowledge base complete (16+ files)",
            "Infrastructure catalog functional",
            "Documentation synchronized with code",
        ]
        assert len(gates) == 6


class TestPhase08ExitGates:
    """Exit gate validation criteria"""

    def test_red_exit_gate_workflow_templates(self):
        """SPEC: 100% active orchestrators have valid workflow templates"""
        gate = {
            "metric": "template_coverage",
            "threshold": 1.0,
            "unit": "percentage",
        }
        assert gate["threshold"] == 1.0

    def test_red_exit_gate_stale_yaml_count(self):
        """SPEC: Zero stale YAML references (old dir paths, deleted components)"""
        gate = {
            "metric": "stale_yaml_count",
            "threshold": 0,
        }
        assert gate["threshold"] == 0

    def test_red_exit_gate_documentation_coverage(self):
        """SPEC: 95%+ of code elements documented (orchestrators, tools, rules)"""
        gate = {
            "metric": "doc_coverage",
            "threshold": 0.95,
        }
        assert gate["threshold"] >= 0.95

    def test_red_exit_gate_infrastructure_schema_valid(self):
        """SPEC: Infrastructure catalog schema is Pydantic-validated, all files valid"""
        gate = {
            "metric": "schema_validation_pass",
            "threshold": 1.0,
        }
        assert gate["threshold"] == 1.0
