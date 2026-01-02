"""
Integration tests for Master Orchestrator routing and execution.

Tests the complete flow:
    User Input → Pattern Router → Registry → Orchestrator Instantiation → Execution

These tests would have caught all 4 bugs discovered during Vacuum v2 integration:
    1. Module path mismatch (missing .vacuum subpackage)
    2. Config file name mismatch (vacuum-2.0-manifest.yaml vs vacuum-orchestrator-v2.yaml)
    3. Orchestrator ID mismatch (vacuum_orchestrator_v2 vs vacuum)
    4. Method name mismatch (get_orchestrator vs instantiate)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import yaml

from src.orchestrators.master_orchestrator import MasterOrchestrator
from src.orchestrators.pattern_router import PatternRouter, OrchestratorMatch, MatchType
from src.mcp.registry import OrchestratorRegistry
from src.database.planning_state_db import PlanningStateDB


@pytest.fixture
def test_db(tmp_path):
    """Create temporary test database."""
    db_path = tmp_path / "test_planning.db"
    return PlanningStateDB(str(db_path))


@pytest.fixture
def registry():
    """Create registry with actual config."""
    config_path = "cortex-brain/config/mcp-server.yaml"
    if not Path(config_path).exists():
        pytest.skip(f"Registry config not found: {config_path}")
    return OrchestratorRegistry(config_path)


@pytest.fixture
def master_orchestrator(registry, test_db):
    """Create Master Orchestrator with real components."""
    config_path = "cortex-brain/config/master-orchestrator.yaml"
    if not Path(config_path).exists():
        pytest.skip(f"Master Orchestrator config not found: {config_path}")
    
    return MasterOrchestrator(
        config_path=config_path,
        registry=registry,
        state_db=test_db
    )


class TestMasterOrchestratorRouting:
    """Test pattern-based routing to orchestrators."""
    
    def test_vacuum_command_routes_correctly(self, master_orchestrator):
        """
        Verify 'vacuum' command routes to vacuum orchestrator.
        
        This test would have caught Bug #3 (orchestrator ID mismatch).
        """
        match = master_orchestrator.router.match_intent("vacuum /tmp")
        
        assert match.is_matched, "Pattern should match 'vacuum' command"
        assert match.orchestrator_id == "vacuum", \
            f"Expected 'vacuum' but got '{match.orchestrator_id}'"
        assert match.confidence >= 1.0
        assert match.match_type == MatchType.REGEX
    
    def test_deep_clean_routes_to_vacuum(self, master_orchestrator):
        """Verify 'deep clean' alias routes to vacuum orchestrator."""
        match = master_orchestrator.router.match_intent("deep clean /home/user")
        
        assert match.is_matched
        assert match.orchestrator_id == "vacuum"
        assert match.confidence >= 1.0
    
    def test_organize_files_routes_to_vacuum(self, master_orchestrator):
        """Verify 'organize files' alias routes to vacuum orchestrator."""
        match = master_orchestrator.router.match_intent("organize files /projects")
        
        assert match.is_matched
        assert match.orchestrator_id == "vacuum"
        assert match.confidence >= 1.0
    
    def test_plan_command_routes_to_planning(self, master_orchestrator):
        """Verify 'plan' command routes to planning orchestrator."""
        match = master_orchestrator.router.match_intent("plan user authentication")
        
        assert match.is_matched
        assert match.orchestrator_id == "planning_v5"
        assert match.confidence >= 1.0
    
    def test_ado_command_routes_correctly(self, master_orchestrator):
        """Verify 'ado' command routes to ADO orchestrator."""
        match = master_orchestrator.router.match_intent("ado story add user login")
        
        assert match.is_matched
        assert match.orchestrator_id == "ado_orchestrator_v2"
        assert match.confidence >= 1.0


class TestRegistryIntegration:
    """Test registry orchestrator instantiation."""
    
    def test_vacuum_orchestrator_can_be_instantiated(self, registry):
        """
        Verify vacuum orchestrator can be loaded from registry.
        
        This test would have caught Bugs #1, #2, and #4:
            - Module path must be correct to import
            - Config file must exist to instantiate
            - Method name must be 'instantiate' not 'get_orchestrator'
        """
        # This call tests:
        # 1. registry.instantiate() exists (not get_orchestrator)
        # 2. Module path is correct (can import)
        # 3. Config file exists (can load)
        orchestrator = registry.instantiate("vacuum")
        
        assert orchestrator is not None, \
            "Vacuum orchestrator failed to instantiate - check module path and config"
        assert orchestrator.__class__.__name__ == "VacuumOrchestratorV2"
    
    def test_all_routing_rules_map_to_valid_orchestrators(self, master_orchestrator, registry):
        """
        Cross-validate master-orchestrator.yaml vs mcp-server.yaml.
        
        This test would have caught Bug #3 (orchestrator ID mismatch).
        """
        config_path = Path("cortex-brain/config/master-orchestrator.yaml")
        routing_config = yaml.safe_load(config_path.read_text())
        
        errors = []
        for rule in routing_config['routing_rules']:
            orch_id = rule['orchestrator']
            
            # Check 1: Orchestrator exists in registry
            if not registry.exists(orch_id):
                errors.append(f"Routing rule uses '{orch_id}' but not in registry")
                continue
            
            # Check 2: Orchestrator can be instantiated
            try:
                orchestrator = registry.instantiate(orch_id)
                if orchestrator is None:
                    errors.append(f"Orchestrator '{orch_id}' instantiation returned None")
            except Exception as e:
                errors.append(f"Orchestrator '{orch_id}' instantiation failed: {e}")
        
        assert len(errors) == 0, \
            f"Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
    
    def test_registry_definitions_have_valid_paths(self, registry):
        """
        Verify all registry definitions point to existing files.
        
        This test would have caught Bugs #1 and #2:
            - Module file must exist
            - Config file must exist
        """
        errors = []
        
        for orch_name in registry.list_orchestrators():
            definition = registry.get(orch_name)
            
            # Check 1: Module file exists
            module_path = definition.module_path.replace('.', '/') + '.py'
            if not Path(module_path).exists():
                errors.append(
                    f"Orchestrator '{orch_name}': Module file not found: {module_path}"
                )
            
            # Check 2: Config file exists
            if not Path(definition.config_path).exists():
                errors.append(
                    f"Orchestrator '{orch_name}': Config file not found: {definition.config_path}"
                )
        
        assert len(errors) == 0, \
            f"Registry validation failed:\n" + "\n".join(f"  - {e}" for e in errors)


class TestEndToEndExecution:
    """Test complete execution flow from user input to result."""
    
    @pytest.mark.integration
    def test_vacuum_dry_run_executes_successfully(self, master_orchestrator, tmp_path):
        """
        End-to-end smoke test: Verify vacuum command executes without errors.
        
        This is the ultimate integration test - if this passes, all 4 bugs are fixed.
        """
        # Create test directory
        test_dir = tmp_path / "test_vacuum"
        test_dir.mkdir()
        
        # Create some test files
        (test_dir / "temp.log").write_text("temp log")
        (test_dir / "cache.tmp").write_text("cache data")
        
        # Mock the orchestrator execution to avoid actual cleanup
        with patch('src.orchestrators.vacuum.vacuum_orchestrator_v2.VacuumOrchestratorV2.execute') as mock_execute:
            mock_execute.return_value = {
                'success': True,
                'phase': 'COMPLETION',
                'message': 'Dry-run completed',
                'artifacts': []
            }
            
            # Execute through Master Orchestrator
            result = master_orchestrator.handle_request(
                f"vacuum {test_dir} --dry-run"
            )
            
            # Verify execution succeeded
            assert result.success, f"Execution failed: {result.message}"
            assert result.orchestrator_id == "vacuum"
            
            # Verify orchestrator was called
            mock_execute.assert_called_once()
    
    @pytest.mark.integration
    def test_pattern_router_to_registry_to_instantiation_flow(self, master_orchestrator):
        """
        Test the complete flow without mocking:
            PatternRouter → Registry → Instantiation
        
        This validates the entire architecture works as designed.
        """
        # Step 1: Pattern matching
        match = master_orchestrator.router.match_intent("vacuum /tmp")
        assert match.is_matched
        assert match.orchestrator_id == "vacuum"
        
        # Step 2: Registry lookup
        definition = master_orchestrator.registry.get(match.orchestrator_id)
        assert definition is not None
        assert definition.name == "vacuum"
        assert definition.class_name == "VacuumOrchestratorV2"
        
        # Step 3: Instantiation
        orchestrator = master_orchestrator.registry.instantiate(match.orchestrator_id)
        assert orchestrator is not None
        assert orchestrator.__class__.__name__ == "VacuumOrchestratorV2"
        
        # Step 4: Verify orchestrator has execute method
        assert hasattr(orchestrator, 'execute')
        assert callable(orchestrator.execute)


class TestConfigurationValidation:
    """Test configuration cross-validation."""
    
    def test_no_orphaned_routing_rules(self):
        """Verify all routing rules point to orchestrators that exist in registry."""
        routing_config_path = Path("cortex-brain/config/master-orchestrator.yaml")
        registry_config_path = Path("cortex-brain/config/mcp-server.yaml")
        
        if not routing_config_path.exists() or not registry_config_path.exists():
            pytest.skip("Config files not found")
        
        routing_config = yaml.safe_load(routing_config_path.read_text())
        registry_config = yaml.safe_load(registry_config_path.read_text())
        
        orchestrator_ids_in_routing = {
            rule['orchestrator'] for rule in routing_config['routing_rules']
        }
        orchestrator_ids_in_registry = set(registry_config['orchestrators'].keys())
        
        orphaned = orchestrator_ids_in_routing - orchestrator_ids_in_registry
        
        assert len(orphaned) == 0, \
            f"Routing rules reference orchestrators not in registry: {orphaned}"
    
    def test_no_unused_orchestrators_in_registry(self):
        """
        Identify orchestrators in registry but not in routing rules.
        
        This is a warning, not an error (orchestrators may be used programmatically).
        """
        routing_config_path = Path("cortex-brain/config/master-orchestrator.yaml")
        registry_config_path = Path("cortex-brain/config/mcp-server.yaml")
        
        if not routing_config_path.exists() or not registry_config_path.exists():
            pytest.skip("Config files not found")
        
        routing_config = yaml.safe_load(routing_config_path.read_text())
        registry_config = yaml.safe_load(registry_config_path.read_text())
        
        orchestrator_ids_in_routing = {
            rule['orchestrator'] for rule in routing_config['routing_rules']
        }
        orchestrator_ids_in_registry = set(registry_config['orchestrators'].keys())
        
        unused = orchestrator_ids_in_registry - orchestrator_ids_in_routing
        
        # This is just informational - orchestrators may be used directly
        if unused:
            print(f"\nINFO: Orchestrators in registry but not routed: {unused}")


class TestRegressionPrevention:
    """Tests specifically designed to prevent the 4 bugs we found."""
    
    def test_vacuum_module_path_includes_subpackage(self):
        """
        Regression test for Bug #1: Module path must include .vacuum subpackage.
        """
        registry_config_path = Path("cortex-brain/config/mcp-server.yaml")
        if not registry_config_path.exists():
            pytest.skip("Registry config not found")
        
        registry_config = yaml.safe_load(registry_config_path.read_text())
        vacuum_def = registry_config['orchestrators']['vacuum']
        
        # The bug was: "src.orchestrators.vacuum_orchestrator_v2"
        # Correct is: "src.orchestrators.vacuum.vacuum_orchestrator_v2"
        assert vacuum_def['module'] == "src.orchestrators.vacuum.vacuum_orchestrator_v2", \
            "Module path must include .vacuum subpackage"
    
    def test_vacuum_config_file_name_matches_created_file(self):
        """
        Regression test for Bug #2: Config path must match actual file name.
        """
        registry_config_path = Path("cortex-brain/config/mcp-server.yaml")
        if not registry_config_path.exists():
            pytest.skip("Registry config not found")
        
        registry_config = yaml.safe_load(registry_config_path.read_text())
        vacuum_def = registry_config['orchestrators']['vacuum']
        
        # The bug was: "vacuum-2.0-manifest.yaml"
        # Correct is: "vacuum-orchestrator-v2.yaml"
        assert vacuum_def['config'] == "cortex-brain/manifests/orchestrators/vacuum-orchestrator-v2.yaml", \
            "Config path must match actual file name"
        
        # Verify file actually exists
        config_path = Path(vacuum_def['config'])
        assert config_path.exists(), \
            f"Config file must exist: {config_path}"
    
    def test_vacuum_orchestrator_id_matches_registry_key(self):
        """
        Regression test for Bug #3: Routing rule orchestrator ID must match registry key.
        """
        routing_config_path = Path("cortex-brain/config/master-orchestrator.yaml")
        registry_config_path = Path("cortex-brain/config/mcp-server.yaml")
        
        if not routing_config_path.exists() or not registry_config_path.exists():
            pytest.skip("Config files not found")
        
        routing_config = yaml.safe_load(routing_config_path.read_text())
        registry_config = yaml.safe_load(registry_config_path.read_text())
        
        # Find vacuum routing rule
        vacuum_rule = next(
            (rule for rule in routing_config['routing_rules'] 
             if 'vacuum' in rule['pattern']),
            None
        )
        
        assert vacuum_rule is not None, "Vacuum routing rule not found"
        
        # The bug was: orchestrator: "vacuum_orchestrator_v2"
        # Correct is: orchestrator: "vacuum"
        assert vacuum_rule['orchestrator'] == "vacuum", \
            "Routing rule orchestrator ID must be 'vacuum' to match registry key"
        
        # Verify registry has this key
        assert "vacuum" in registry_config['orchestrators'], \
            "Registry must have 'vacuum' key"
    
    def test_master_orchestrator_uses_instantiate_method(self):
        """
        Regression test for Bug #4: Master Orchestrator must use registry.instantiate().
        """
        master_orch_path = Path("src/orchestrators/master_orchestrator.py")
        if not master_orch_path.exists():
            pytest.skip("Master Orchestrator file not found")
        
        source_code = master_orch_path.read_text()
        
        # Verify correct method is used
        assert "registry.instantiate(" in source_code, \
            "Must use registry.instantiate() method"
        
        # Verify incorrect method is NOT used
        assert "registry.get_orchestrator(" not in source_code, \
            "Must NOT use registry.get_orchestrator() (method doesn't exist)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
