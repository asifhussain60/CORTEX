"""
CORTEX 4.0 Orchestration Test Infrastructure
Pytest configuration and shared fixtures for orchestration_3_0 tests
"""

import pytest
import tempfile
import os
from pathlib import Path
from typing import Generator
from unittest.mock import Mock

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from orchestration_3_0.core.state_machine import StateMachine, create_basic_orchestrator_fsm
from orchestration_3_0.core.dependency_container import DependencyContainer, get_container
from orchestration_3_0.session.session_manager import SessionManager, get_session_manager


@pytest.fixture
def temp_db_path() -> Generator[str, None, None]:
    """Provide temporary SQLite database path for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def fresh_session_manager(temp_db_path: str) -> Generator[SessionManager, None, None]:
    """Provide fresh SessionManager with temporary database."""
    sm = SessionManager(db_path=temp_db_path)
    yield sm
    # Force garbage collection to close any open connections
    import gc
    gc.collect()


@pytest.fixture
def fresh_container() -> Generator[DependencyContainer, None, None]:
    """Provide fresh DependencyContainer for isolated tests."""
    container = DependencyContainer()
    yield container
    # Clear services (singletons are stored in ServiceRegistration.instance)
    container.services.clear()
    container.scoped_instances.clear()


@pytest.fixture
def basic_fsm() -> StateMachine:
    """Provide basic orchestrator FSM for testing."""
    return create_basic_orchestrator_fsm("TestOrchestrator")


@pytest.fixture
def sample_workflow_context() -> dict:
    """Provide sample workflow context for testing."""
    return {
        "tenant_id": "test-tenant",
        "project_id": "test-project",
        "user_id": "test-user",
        "inputs": {
            "feature": "authentication",
            "complexity": "high"
        }
    }


@pytest.fixture
def mock_logger() -> Mock:
    """Provide mock logger for testing."""
    logger = Mock()
    logger.info = Mock()
    logger.debug = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    return logger


@pytest.fixture
def mock_llm_service() -> Mock:
    """Provide mock LLM service for testing Intelligence Orchestrator."""
    service = Mock()
    service.complete = Mock(return_value={"code": "def hello(): pass", "confidence": 0.85})
    service.is_available = Mock(return_value=True)
    return service


@pytest.fixture
def mock_git_service() -> Mock:
    """Provide mock Git service for testing DevOps Orchestrator."""
    service = Mock()
    service.checkpoint = Mock(return_value={"commit_id": "abc123", "branch": "main"})
    service.is_clean = Mock(return_value=True)
    return service


# Test data constants
TEST_TENANT_ID = "test-tenant-001"
TEST_PROJECT_ID = "test-project-001"
TEST_USER_ID = "test-user-001"
TEST_SESSION_ID = "test-session-001"

# Test orchestrator names
TEST_ORCHESTRATOR_NAMES = [
    "TDDOrchestrator",
    "DevOpsOrchestrator",
    "QAOrchestrator",
    "PlanningOrchestrator",
    "ExecutionOrchestrator",
    "DocumentationOrchestrator",
    "IntelligenceOrchestrator",
    "ObservabilityOrchestrator",
    "OnboardingOrchestrator"
]
