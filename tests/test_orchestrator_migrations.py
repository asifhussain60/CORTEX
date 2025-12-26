"""
Quick validation tests for migrated orchestrators

Tests basic functionality of all 3 migrated orchestrators:
- ExecutionOrchestrator
- DocumentationOrchestrator
- TDDOrchestrator

Run with: pytest tests/test_orchestrator_migrations.py -v
"""

import pytest
import logging
from pathlib import Path
from unittest.mock import MagicMock

# Import orchestrators
from src.orchestration_4_0.orchestrators.execution.execution_orchestrator import ExecutionOrchestrator
from src.orchestration_4_0.orchestrators.documentation.documentation_orchestrator import (
    DocumentationOrchestrator,
    DocumentationConfig
)
from src.orchestrators.tdd.tdd_orchestrator_migrated import TDDOrchestrator, TDDPhase

logger = logging.getLogger(__name__)


class TestExecutionOrchestratorMigration:
    """Test ExecutionOrchestrator migration to BaseOrchestrator"""
    
    def test_initialization(self):
        """Test orchestrator initializes with adaptive modes"""
        orchestrator = ExecutionOrchestrator(
            logger=logger,
            config={
                "execution_mode": "autonomous",
                "max_retries": 3,
                "enable_rollback": True
            }
        )
        
        assert orchestrator.name == "execution"
        assert orchestrator.execution_mode.value == "autonomous"
        assert orchestrator.enable_rollback is True
        assert orchestrator.phase_manager is not None
        assert orchestrator.error_handler is not None
    
    def test_all_execution_modes(self):
        """Test orchestrator accepts all execution modes"""
        modes = ["autonomous", "supervised", "manual"]
        
        for mode in modes:
            orchestrator = ExecutionOrchestrator(
                logger=logger,
                config={"execution_mode": mode}
            )
            assert orchestrator.execution_mode == mode
    
    def test_setup_with_plan(self):
        """Test setup extracts execution plan correctly"""
        orchestrator = ExecutionOrchestrator(logger=logger)
        
        context = {
            "plan": {
                "name": "test-plan",
                "phases": [
                    {"name": "phase1", "description": "Test phase 1"},
                    {"name": "phase2", "description": "Test phase 2"}
                ]
            },
            "workspace": "/tmp/test"
        }
        
        orchestrator._setup(context)
        
        assert orchestrator.execution_plan is not None
        assert orchestrator.execution_plan["name"] == "test-plan"
        assert orchestrator.workspace == "/tmp/test"
    
    def test_register_phases_from_plan(self):
        """Test phases registered from execution plan"""
        orchestrator = ExecutionOrchestrator(logger=logger)
        
        context = {
            "plan": {
                "name": "test-plan",
                "phases": [
                    {"name": "phase1", "description": "Test phase 1", "required": True},
                    {"name": "phase2", "description": "Test phase 2", "required": False}
                ]
            }
        }
        
        orchestrator._setup(context)
        orchestrator._register_phases()
        
        assert len(orchestrator.phase_manager.phases) == 2
        assert orchestrator.phase_manager.phases[0].name == "phase1"
        assert orchestrator.phase_manager.phases[0].required is True
        assert orchestrator.phase_manager.phases[1].name == "phase2"
        assert orchestrator.phase_manager.phases[1].required is False


class TestDocumentationOrchestratorMigration:
    """Test DocumentationOrchestrator migration to BaseOrchestrator"""
    
    def test_initialization(self):
        """Test orchestrator initializes with adaptive modes"""
        orchestrator = DocumentationOrchestrator(
            logger=logger,
            config={"execution_mode": "CHECKPOINT"}
        )
        
        assert orchestrator.name == "documentation"
        assert orchestrator.execution_mode == "CHECKPOINT"
        assert orchestrator.code_analyzer is not None
        assert orchestrator.type_extractor is not None
    
    def test_setup_with_config(self, tmp_path):
        """Test setup with documentation config"""
        # Create test source file
        test_file = tmp_path / "test.py"
        test_file.write_text("def test_func(): pass")
        
        orchestrator = DocumentationOrchestrator(logger=logger)
        
        context = {
            "config": DocumentationConfig(
                source_paths=[tmp_path],
                output_dir=tmp_path / "docs",
                generate_diagrams=False
            )
        }
        
        orchestrator._setup(context)
        
        assert orchestrator.doc_config is not None
        assert orchestrator.doc_config.source_paths == [tmp_path]
        assert orchestrator.doc_result is not None
    
    def test_register_phases(self, tmp_path):
        """Test documentation phases registered correctly"""
        orchestrator = DocumentationOrchestrator(logger=logger)
        
        context = {
            "config": DocumentationConfig(
                source_paths=[tmp_path],
                generate_diagrams=True
            )
        }
        
        orchestrator._setup(context)
        orchestrator._register_phases()
        
        phase_names = [p.name for p in orchestrator.phase_manager.phases]
        
        assert "analyze" in phase_names
        assert "extract" in phase_names
        assert "generate_docs" in phase_names
        assert "generate_diagrams" in phase_names
        assert "validate" in phase_names
        assert "export" in phase_names


class TestTDDOrchestratorMigration:
    """Test TDDOrchestrator migration to BaseOrchestrator"""
    
    def test_initialization(self):
        """Test orchestrator initializes with BaseOrchestrator"""
        brain = MagicMock()
        kg = MagicMock()
        mcp = MagicMock()
        
        orchestrator = TDDOrchestrator(
            brain_connector=brain,
            knowledge_graph=kg,
            mcp_gateway=mcp,
            logger=logger,
            config={
                "execution_mode": "AUTONOMOUS",
                "enable_rollback": True
            }
        )
        
        assert orchestrator.name == "tdd"
        assert orchestrator.execution_mode == "AUTONOMOUS"
        assert orchestrator.enable_rollback is True
        assert orchestrator.brain == brain
        assert orchestrator.kg == kg
        assert orchestrator.mcp == mcp
        assert orchestrator.phase_manager is not None
    
    def test_setup_with_feature(self, tmp_path):
        """Test setup extracts feature details"""
        brain = MagicMock()
        kg = MagicMock()
        mcp = MagicMock()
        
        orchestrator = TDDOrchestrator(
            brain_connector=brain,
            knowledge_graph=kg,
            mcp_gateway=mcp,
            logger=logger
        )
        
        context = {
            "feature_name": "test-feature",
            "acceptance_criteria": ["Criterion 1", "Criterion 2"],
            "project_path": str(tmp_path)
        }
        
        orchestrator._setup(context)
        
        assert orchestrator.feature_name == "test-feature"
        assert len(orchestrator.acceptance_criteria) == 2
        assert orchestrator.project_path == tmp_path
    
    def test_register_tdd_phases(self):
        """Test TDD phases registered correctly"""
        brain = MagicMock()
        kg = MagicMock()
        mcp = MagicMock()
        
        orchestrator = TDDOrchestrator(
            brain_connector=brain,
            knowledge_graph=kg,
            mcp_gateway=mcp,
            logger=logger
        )
        
        context = {
            "feature_name": "test",
            "acceptance_criteria": []
        }
        
        orchestrator._setup(context)
        orchestrator._register_phases()
        
        assert len(orchestrator.phase_manager.phases) == 3
        
        phase_names = [p.name for p in orchestrator.phase_manager.phases]
        assert "RED" in phase_names
        assert "GREEN" in phase_names
        assert "REFACTOR" in phase_names
        
        # All phases required for TDD
        for phase in orchestrator.phase_manager.phases:
            assert phase.required is True
    
    def test_strategy_registration(self):
        """Test strategy pattern preserved"""
        brain = MagicMock()
        kg = MagicMock()
        mcp = MagicMock()
        
        orchestrator = TDDOrchestrator(
            brain_connector=brain,
            knowledge_graph=kg,
            mcp_gateway=mcp,
            logger=logger
        )
        
        # Mock strategy
        strategy = MagicMock()
        
        # Register strategy
        orchestrator.register_strategy(TDDPhase.RED, strategy)
        
        assert "RED" in orchestrator.strategies
        assert orchestrator.strategies["RED"] == strategy


# Integration test
class TestOrchestratorsIntegration:
    """Test orchestrators work together"""
    
    def test_all_orchestrators_share_base(self):
        """Test all orchestrators inherit from BaseOrchestrator"""
        from src.orchestration_4_0.base.base_orchestrator import BaseOrchestrator
        
        brain = MagicMock()
        kg = MagicMock()
        mcp = MagicMock()
        
        exec_orch = ExecutionOrchestrator(logger=logger)
        doc_orch = DocumentationOrchestrator(logger=logger)
        tdd_orch = TDDOrchestrator(brain, kg, mcp, logger=logger)
        
        assert isinstance(exec_orch, BaseOrchestrator)
        assert isinstance(doc_orch, BaseOrchestrator)
        assert isinstance(tdd_orch, BaseOrchestrator)
    
    def test_all_orchestrators_have_phase_manager(self):
        """Test all orchestrators have phase management"""
        brain = MagicMock()
        kg = MagicMock()
        mcp = MagicMock()
        
        orchestrators = [
            ExecutionOrchestrator(logger=logger),
            DocumentationOrchestrator(logger=logger),
            TDDOrchestrator(brain, kg, mcp, logger=logger)
        ]
        
        for orch in orchestrators:
            assert hasattr(orch, 'phase_manager')
            assert hasattr(orch, 'error_handler')
            assert hasattr(orch, '_setup')
            assert hasattr(orch, '_register_phases')
            assert hasattr(orch, '_execute_phase')
            assert hasattr(orch, '_teardown')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
