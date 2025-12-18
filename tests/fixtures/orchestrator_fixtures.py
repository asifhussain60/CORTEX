"""
CORTEX 4.0 Orchestrator Test Fixtures

Provides reusable test fixtures for testing CORTEX orchestrators.

⚠️ IMPORTANT: These fixtures are for CORTEX INTERNAL TESTS ONLY.
   Application tests should create their own fixtures in {app_repo}/tests/fixtures/.

Fixtures provided:
- mock_brain: Mock BrainInterface for testing
- mock_template_manager: Mock TemplateManager
- mock_config: Mock ConfigManager
- base_orchestrator_config: Standard orchestrator configuration
- mock_logger: Mock logger for testing

Reference: cortex-brain/brain-protection-rules.yaml
  - TEST_LOCATION_SEPARATION: CORTEX tests in CORTEX repo only
  - GIT_ISOLATION_ENFORCEMENT: No mixing of CORTEX and app code
"""

import logging
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, Mock

import pytest


@pytest.fixture
def mock_brain():
    """
    Mock BrainInterface for testing CORTEX orchestrators.
    
    Returns:
        MagicMock with spec=BrainInterface
    
    Example:
        def test_orchestrator(mock_brain):
            orchestrator = MyOrchestrator(brain=mock_brain)
            mock_brain.tier1.store_conversation.assert_called_once()
    """
    from src.brain.interface import BrainInterface
    
    brain = MagicMock(spec=BrainInterface)
    
    # Mock tier0 (Governance)
    brain.tier0 = MagicMock()
    brain.tier0.check_rule.return_value = {"allowed": True}
    
    # Mock tier1 (Working Memory)
    brain.tier1 = MagicMock()
    brain.tier1.store_conversation.return_value = True
    brain.tier1.get_conversation.return_value = None
    
    # Mock tier2 (Knowledge Graph)
    brain.tier2 = MagicMock()
    brain.tier2.store_pattern.return_value = True
    brain.tier2.query_patterns.return_value = []
    
    # Mock tier3 (Dev Context)
    brain.tier3 = MagicMock()
    brain.tier3.get_git_metrics.return_value = {}
    
    return brain


@pytest.fixture
def mock_template_manager():
    """
    Mock TemplateManager for testing.
    
    Returns:
        MagicMock with common template manager methods
    
    Example:
        def test_rendering(mock_template_manager):
            mock_template_manager.render_template.return_value = "Rendered output"
            result = orchestrator.render_response("template_name", context)
            assert result == "Rendered output"
    """
    manager = MagicMock()
    
    # Default return values
    manager.get_template.return_value = "## Template Content"
    manager.render_template.return_value = "Rendered template"
    manager.list_templates.return_value = ["template1", "template2"]
    
    return manager


@pytest.fixture
def mock_config():
    """
    Mock ConfigManager for testing.
    
    Returns:
        MagicMock with configuration methods
    
    Example:
        def test_config(mock_config):
            mock_config.get.return_value = "test_value"
            value = config_manager.get("some.key")
            assert value == "test_value"
    """
    from src.config import CortexConfig, PathConfig, BrainConfig, LoggingConfig
    
    config_manager = MagicMock()
    
    # Create realistic config
    config = CortexConfig(
        version="4.0",
        paths=PathConfig(
            orchestrators=Path("src/orchestrators"),
            brain=Path("src/brain"),
            templates=Path("src/templates"),
            mcp_gateway=Path("src/mcp"),
            logs=Path("logs"),
            cache=Path(".cortex/cache")
        ),
        brain=BrainConfig(
            tier1_db="{repo}/cortex-brain/tier1/conversations.db",
            tier2_db="~/.cortex/shared/tier2/knowledge-graph.db",
            tier3_db="{repo}/cortex-brain/tier3/metrics.db",
            tier0_rules="~/.cortex/shared/skull_rules.yaml"
        ),
        logging=LoggingConfig(level="DEBUG")
    )
    
    config_manager.config = config
    config_manager.get.return_value = None
    config_manager.get_path.return_value = Path("src/orchestrators")
    config_manager.is_feature_enabled.return_value = False
    
    return config_manager


@pytest.fixture
def base_orchestrator_config() -> Dict[str, Any]:
    """
    Standard orchestrator configuration for testing.
    
    Returns:
        Dictionary with common orchestrator config
    
    Example:
        def test_init(base_orchestrator_config):
            orchestrator = MyOrchestrator(config=base_orchestrator_config)
            assert orchestrator.config["name"] == "test_orchestrator"
    """
    return {
        "name": "test_orchestrator",
        "version": "4.0",
        "debug": True,
        "timeout": 30,
        "max_retries": 3,
        "phases": [
            {"name": "validate", "order": 1},
            {"name": "execute", "order": 2},
            {"name": "cleanup", "order": 3}
        ]
    }


@pytest.fixture
def mock_logger():
    """
    Mock logger for testing.
    
    Returns:
        Mock logger instance
    
    Example:
        def test_logging(mock_logger):
            orchestrator = MyOrchestrator(logger=mock_logger)
            orchestrator.run()
            mock_logger.info.assert_called()
    """
    logger = Mock(spec=logging.Logger)
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.critical = Mock()
    return logger


@pytest.fixture
def temp_workspace(tmp_path):
    """
    Create temporary workspace for testing file operations.
    
    Args:
        tmp_path: pytest's tmp_path fixture
    
    Returns:
        Path to temporary workspace
    
    Example:
        def test_file_creation(temp_workspace):
            file_path = temp_workspace / "test.txt"
            file_path.write_text("test content")
            assert file_path.exists()
    """
    workspace = tmp_path / "test_workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    
    # Create standard CORTEX structure
    (workspace / "src").mkdir()
    (workspace / "tests").mkdir()
    (workspace / "cortex-brain").mkdir()
    (workspace / "cortex-brain" / "tier1").mkdir()
    (workspace / "cortex-brain" / "tier2").mkdir()
    (workspace / "cortex-brain" / "tier3").mkdir()
    
    return workspace


@pytest.fixture
def mock_phase_manager():
    """
    Mock PhaseManager for testing orchestrator phases.
    
    Returns:
        MagicMock with PhaseManager spec
    
    Example:
        def test_phases(mock_phase_manager):
            mock_phase_manager.get_current_phase.return_value = "execute"
            orchestrator.run()
            mock_phase_manager.transition.assert_called()
    """
    from src.orchestrators.base.phase_manager import PhaseManager
    
    phase_manager = MagicMock(spec=PhaseManager)
    phase_manager.get_current_phase.return_value = "validate"
    phase_manager.execute_phase.return_value = {"status": "success"}
    phase_manager.transition.return_value = True
    phase_manager.registered_phases = ["validate", "execute", "cleanup"]
    
    return phase_manager


@pytest.fixture
def mock_error_handler():
    """
    Mock OrchestratorErrorHandler for testing error handling.
    
    Returns:
        MagicMock with error handler spec
    
    Example:
        def test_error_handling(mock_error_handler):
            mock_error_handler.should_retry.return_value = True
            orchestrator.handle_error(exception)
            mock_error_handler.handle_exception.assert_called()
    """
    from src.orchestrators.base.error_handler import OrchestratorErrorHandler
    
    error_handler = MagicMock(spec=OrchestratorErrorHandler)
    error_handler.handle_exception.return_value = {"error": "handled"}
    error_handler.should_retry.return_value = False
    error_handler.get_recovery_strategy.return_value = "abort"
    
    return error_handler


@pytest.fixture
def sample_orchestrator_result():
    """
    Sample OrchestratorResult for testing.
    
    Returns:
        OrchestratorResult instance
    
    Example:
        def test_result_processing(sample_orchestrator_result):
            assert sample_orchestrator_result.status == "completed"
            assert sample_orchestrator_result.success is True
    """
    from src.orchestrators.base.base_orchestrator import OrchestratorResult, OrchestratorStatus
    
    return OrchestratorResult(
        status=OrchestratorStatus.COMPLETED,
        success=True,
        data={"test": "data"},
        metrics={"duration": 1.5, "phases_executed": 3},
        errors=[],
        warnings=[]
    )
