"""
Shared fixtures for workflow integration tests — Phase 100 Stage 4.

Two-context golden test harness: ARCHITECT + PRODUCTION modes.

AC_START: AC-P100-S4-T1-001
Phase: 100 | Stage: 4 | Priority: P0
Description: Shared fixtures for two-context workflow testing
Requirements: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import pytest
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator

# =============================================================================
# GENERIC PRODUCTION PROFILES (NO repo-specific names)
# =============================================================================


@pytest.fixture
def legacy_dotnet_spa_profile() -> Dict[str, Any]:
    """
    Generic legacy .NET SPA profile.

    Simulates a typical enterprise .NET Framework 4.8 + Angular 8 project.
    NO repo-specific names used (generic pattern).

    Returns:
        Profile dictionary with test_framework, patterns, tech_stack.
    """
    return {
        "name": "legacy_dotnet_spa",
        "test_framework": "xUnit",
        "secondary_test_framework": "Jasmine",
        "tech_stack": {
            "backend": ".NET Framework 4.8",
            "frontend": "Angular 8",
            "database": "SQL Server",
        },
        "patterns": {
            "auth": "Windows Authentication + JWT",
            "api": "RESTful with DataAnnotations",
            "logging": "log4net",
        },
        "detected_from": "*.csproj + angular.json",
    }


@pytest.fixture
def modern_nodejs_api_profile() -> Dict[str, Any]:
    """
    Generic modern Node.js API profile.

    Simulates a modern Express + TypeScript + PostgreSQL microservice.

    Returns:
        Profile dictionary with test_framework, patterns, tech_stack.
    """
    return {
        "name": "modern_nodejs_api",
        "test_framework": "Jest",
        "tech_stack": {
            "runtime": "Node.js 20 LTS",
            "framework": "Express 4.x",
            "language": "TypeScript 5.x",
            "database": "PostgreSQL 16",
        },
        "patterns": {
            "auth": "OAuth2 + JWT",
            "api": "RESTful + OpenAPI 3.0",
            "logging": "Winston",
        },
        "detected_from": "package.json + tsconfig.json",
    }


@pytest.fixture
def python_data_pipeline_profile() -> Dict[str, Any]:
    """
    Generic Python data pipeline profile.

    Simulates a typical data engineering project with Pandas + Airflow.

    Returns:
        Profile dictionary with test_framework, patterns, tech_stack.
    """
    return {
        "name": "python_data_pipeline",
        "test_framework": "pytest",
        "tech_stack": {
            "language": "Python 3.11",
            "orchestration": "Apache Airflow 2.7",
            "processing": "Pandas 2.x",
            "storage": "Parquet + S3",
        },
        "patterns": {
            "auth": "IAM Roles",
            "pipeline": "DAG-based with idempotency",
            "logging": "structlog",
        },
        "detected_from": "requirements.txt + dags/ directory",
    }


# =============================================================================
# ARCHITECT CONTEXT FIXTURE
# =============================================================================


@pytest.fixture
def architect_context() -> Dict[str, Any]:
    """
    Mock ARCHITECT mode knowledge context.

    Simulates CORTEX-internal knowledge loaded when .cortex-runtime/ marker
    detected in workspace.

    Returns:
        CORTEX patterns, test framework, governance rules.
    """
    return {
        "mode": "ARCHITECT",
        "test_framework": "pytest",
        "patterns": {
            "api": "FastAPI",
            "orchestrator": "CORTEX orchestrator pattern",
            "governance": "EnforcementOrchestrator (7 agents)",
        },
        "knowledge_source": "cortex-registry/integration/patterns/",
        "core_rules": [
            "CORE-008: TDD",
            "CORE-011: Type hints",
            "CORE-012: Google docstrings",
        ],
    }


# =============================================================================
# PRODUCTION CONTEXT FIXTURE
# =============================================================================


@pytest.fixture
def production_context(modern_nodejs_api_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mock PRODUCTION mode knowledge context.

    Simulates user's company knowledge loaded from company/domains/.

    Args:
        modern_nodejs_api_profile: Generic modern Node.js API profile.

    Returns:
        Company patterns, test framework, security standards.
    """
    return {
        "mode": "PRODUCTION",
        "onboarded_profile": modern_nodejs_api_profile,
        "test_framework": modern_nodejs_api_profile["test_framework"],
        "patterns": {
            "api": "RESTful + OpenAPI 3.0",
            "auth": "OAuth2 + JWT",
            "logging": "Winston",
        },
        "knowledge_source": "cortex-registry/company/domains/api-design-standards.yaml",
        "security_standards": "cortex-registry/company/domains/security-standards.yaml",
    }


# =============================================================================
# WORKFLOW REGISTRY FIXTURE
# =============================================================================


@pytest.fixture
def workflow_registry() -> Any:
    """
    Mock WorkflowTemplateRegistry for integration tests.

    Returns:
        MagicMock with register_template() and get_template() methods.
    """
    from unittest.mock import MagicMock

    mock_registry = MagicMock()
    mock_registry.get_template.return_value = {
        "workflow": {
            "name": "test-workflow",
            "steps": [
                {
                    "step_id": "step1",
                    "orchestrator": "TDDOrchestrator",
                    "params": {"test_framework": "{{test_framework}}"},
                }
            ],
        }
    }
    return mock_registry


# =============================================================================
# KNOWLEDGE ENGINE FIXTURE
# =============================================================================


@pytest.fixture
def knowledge_engine() -> Any:
    """
    Mock KnowledgeSynthesisEngine for integration tests.

    Returns:
        MagicMock with resolve_placeholders() method.
    """
    from unittest.mock import MagicMock

    mock_engine = MagicMock()
    mock_engine.resolve_placeholders.return_value = {
        "test_framework": "pytest",
        "coverage_target": "95%",
    }
    return mock_engine


# =============================================================================
# STEP FSM FIXTURE
# =============================================================================


@pytest.fixture
def step_fsm() -> Any:
    """
    Mock StepStateMachine for integration tests.

    Returns:
        MagicMock with execute_transition(), is_terminal_state() methods.
    """
    from unittest.mock import MagicMock

    mock_fsm = MagicMock()
    mock_fsm.is_terminal_state.side_effect = [False, False, True]  # 2 cycles
    mock_fsm.current_state = "PASSED"
    return mock_fsm


# =============================================================================
# AUTONOMOUS EXECUTOR FIXTURE
# =============================================================================


@pytest.fixture
def autonomous_executor() -> Any:
    """
    Mock AutonomousWorkflowExecutor for integration tests.

    Returns:
        MagicMock with execute_workflow_autonomously() method.
    """
    from unittest.mock import MagicMock

    mock_executor = MagicMock()
    mock_executor.execute_workflow_autonomously.return_value = {
        "status": "COMPLETED",
        "steps_executed": 3,
        "duration_seconds": 12.5,
    }
    return mock_executor


# =============================================================================
# TEMP WORKFLOW YAML FIXTURE
# =============================================================================


@pytest.fixture
def temp_workflow_yaml() -> Generator[Path, None, None]:
    """
    Create temporary YAML workflow file for tests.

    Yields:
        Path to temporary YAML file (auto-cleaned after test).
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as temp_file:
        temp_file.write(
            """workflow:
  name: test-workflow
  steps:
    - step_id: step1
      orchestrator: test
"""
        )
        temp_path = Path(temp_file.name)

    yield temp_path

    # Cleanup
    temp_path.unlink(missing_ok=True)


# AC_COMPLETE: AC-P100-S4-T1-001 ✅ Shared fixtures for two-context testing
