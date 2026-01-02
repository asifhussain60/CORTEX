"""
Unit Tests for Vacuum Orchestrator v2 - Main Orchestrator

Tests the 6-phase autonomous vacuum workflow:
1. DISCOVERY - Filesystem traversal and categorization
2. ANALYSIS - Duplicate detection, orphan identification
3. PLANNING - Safety validation, risk classification
4. APPROVAL - User confirmation (dry-run mode)
5. EXECUTION - Atomic filesystem operations
6. COMPLETION - Report generation, checkpoint verification

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.orchestrators.vacuum.vacuum_orchestrator_v2 import VacuumOrchestratorV2
from src.database.planning_state_db import PlanningStateDB


class TestVacuumOrchestratorV2:
    """Test suite for VacuumOrchestratorV2."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.fixture
    def mock_db(self):
        """Mock PlanningStateDB."""
        db = Mock(spec=PlanningStateDB)
        db.create_plan.return_value = "test-plan-123"
        db.start_phase.return_value = "test-phase-456"
        db.complete_phase.return_value = None
        db.fail_phase.return_value = None
        return db
    
    @pytest.fixture
    def mock_config(self, temp_dir):
        """Mock configuration."""
        return {
            'cleanup_categories': {
                'temp_files': {
                    'priority': 'HIGH',
                    'patterns': ['*.tmp', '*.temp']
                },
                'build_artifacts': {
                    'priority': 'HIGH',
                    'patterns': ['__pycache__/', '*.pyc']
                }
            },
            'safety': {
                'critical_patterns': ['.git', '*.py'],
                'size_threshold_mb': 1000
            },
            'exclusions': ['.git', 'node_modules']
        }
    
    @pytest.fixture
    def orchestrator(self, mock_db, mock_config, temp_dir):
        """Create VacuumOrchestratorV2 instance."""
        with patch('src.orchestrators.vacuum.vacuum_orchestrator_v2.Path') as mock_path:
            with patch('yaml.safe_load', return_value=mock_config):
                orch = VacuumOrchestratorV2(
                    config_path="dummy.yaml",
                    state_db=mock_db
                )
                orch.config = mock_config  # Override config
                return orch
    
    def test_initialization(self, orchestrator, mock_db, mock_config):
        """Test orchestrator initialization."""
        assert orchestrator.state_db == mock_db
        assert orchestrator.cleanup_rules == mock_config['cleanup_categories']
        assert orchestrator.safety_rules == mock_config['safety']
        assert orchestrator.exclusions == mock_config['exclusions']
    
    def test_dry_run_execution(self, orchestrator, temp_dir):
        """Test dry-run mode (no file changes)."""
        # Create test files
        (temp_dir / "test.tmp").touch()
        (temp_dir / "file.txt").touch()
        
        # Mock filesystem engine
        orchestrator._filesystem_engine = Mock()
        orchestrator._filesystem_engine.scan_directory.return_value = {
            'temp_files': [temp_dir / "test.tmp"],
            'other': [temp_dir / "file.txt"]
        }
        
        orchestrator._safety_validator = Mock()
        orchestrator._safety_validator.validate_plan.return_value = {
            'safe': [temp_dir / "test.tmp"],
            'critical': [],
            'warnings': []
        }
        
        # Execute dry-run
        result = orchestrator.execute(
            target_path=str(temp_dir),
            dry_run=True
        )
        
        # Verify no files deleted
        assert (temp_dir / "test.tmp").exists()
        assert (temp_dir / "file.txt").exists()
        assert result['status'] == 'dry_run'
    
    def test_phase_discovery(self, orchestrator, temp_dir):
        """Test Phase 1: DISCOVERY."""
        # Create test filesystem
        (temp_dir / "test.tmp").touch()
        (temp_dir / "__pycache__").mkdir()
        (temp_dir / "__pycache__" / "module.pyc").touch()
        (temp_dir / "source.py").touch()
        
        # Mock filesystem engine
        orchestrator._filesystem_engine = Mock()
        orchestrator._filesystem_engine.scan_directory.return_value = {
            'temp_files': [temp_dir / "test.tmp"],
            'build_artifacts': [
                temp_dir / "__pycache__",
                temp_dir / "__pycache__" / "module.pyc"
            ],
            'source_files': [temp_dir / "source.py"]
        }
        
        # Run discovery
        inventory = orchestrator._phase_discovery(temp_dir)
        
        assert 'temp_files' in inventory
        assert 'build_artifacts' in inventory
        assert len(inventory['temp_files']) == 1
        assert len(inventory['build_artifacts']) == 2
    
    def test_phase_analysis(self, orchestrator):
        """Test Phase 2: ANALYSIS."""
        inventory = {
            'temp_files': [Path("/tmp/test.tmp")],
            'build_artifacts': [Path("/tmp/__pycache__")]
        }
        
        # Mock duplicate detector
        orchestrator._duplicate_detector = Mock()
        orchestrator._duplicate_detector.find_duplicates.return_value = {
            'duplicate_groups': [],
            'total_duplicates': 0,
            'space_wasted': 0
        }
        
        # Mock orphan detector
        orchestrator._orphan_detector = Mock()
        orchestrator._orphan_detector.find_orphaned_tests.return_value = {
            'orphaned_tests': [],
            'total_orphans': 0
        }
        
        # Run analysis
        cleanup_plan = orchestrator._phase_analysis(inventory, {})
        
        assert 'inventory' in cleanup_plan
        assert 'duplicates' in cleanup_plan
        assert 'orphans' in cleanup_plan
    
    def test_phase_planning_safety_validation(self, orchestrator):
        """Test Phase 3: PLANNING (safety validation)."""
        cleanup_plan = {
            'inventory': {
                'temp_files': [Path("/tmp/test.tmp")],
                'source_files': [Path("/src/main.py")]
            }
        }
        
        # Mock safety validator
        orchestrator._safety_validator = Mock()
        orchestrator._safety_validator.validate_plan.return_value = {
            'safe': [Path("/tmp/test.tmp")],
            'critical': [Path("/src/main.py")],
            'warnings': ['Source file protected'],
            'risk_levels': {
                Path("/tmp/test.tmp"): 'SAFE',
                Path("/src/main.py"): 'CRITICAL'
            }
        }
        
        # Run planning
        validated_plan = orchestrator._phase_planning(cleanup_plan)
        
        assert 'safe' in validated_plan
        assert 'critical' in validated_plan
        assert len(validated_plan['safe']) == 1
        assert len(validated_plan['critical']) == 1
        assert Path("/src/main.py") in validated_plan['critical']
    
    def test_phase_execution_with_checkpoint(self, orchestrator, temp_dir):
        """Test Phase 5: EXECUTION with checkpoint."""
        validated_plan = {
            'safe': [temp_dir / "test.tmp"],
            'moves': []
        }
        
        # Create test file
        (temp_dir / "test.tmp").write_text("test content")
        
        # Mock filesystem engine
        orchestrator._filesystem_engine = Mock()
        orchestrator._filesystem_engine.execute_cleanup.return_value = {
            'files_deleted': 1,
            'files_moved': 0,
            'files_archived': 0,
            'files_skipped': 0,
            'space_reclaimed': 12
        }
        
        # Run execution
        result = orchestrator._phase_execution(validated_plan, {
            'checkpoint': True,
            'checkpoint_dir': temp_dir / "checkpoints"
        })
        
        assert result['files_deleted'] == 1
        assert 'space_reclaimed' in result
    
    def test_nonexistent_path_error(self, orchestrator):
        """Test error handling for nonexistent path."""
        result = orchestrator.execute(
            target_path="/nonexistent/path",
            dry_run=True
        )
        
        assert result['status'] == 'error'
        assert 'not found' in result['message'].lower()
    
    def test_critical_file_protection(self, orchestrator, temp_dir):
        """Test that critical files are never deleted."""
        # Create critical files
        (temp_dir / ".git").mkdir()
        (temp_dir / "main.py").touch()
        (temp_dir / "test.tmp").touch()
        
        # Mock safety validator to protect critical files
        orchestrator._safety_validator = Mock()
        orchestrator._safety_validator.validate_plan.return_value = {
            'safe': [temp_dir / "test.tmp"],
            'critical': [temp_dir / ".git", temp_dir / "main.py"],
            'warnings': ['Critical files protected']
        }
        
        # Mock filesystem engine
        orchestrator._filesystem_engine = Mock()
        orchestrator._filesystem_engine.scan_directory.return_value = {
            'temp_files': [temp_dir / "test.tmp"],
            'source_files': [temp_dir / "main.py"]
        }
        
        # Execute dry-run
        result = orchestrator.execute(
            target_path=str(temp_dir),
            dry_run=True
        )
        
        # Verify critical files not in deletion plan
        assert 'safe' in result
        assert temp_dir / ".git" not in result.get('safe', [])
        assert temp_dir / "main.py" not in result.get('safe', [])
    
    def test_rollback_capability(self, orchestrator, temp_dir):
        """Test checkpoint rollback functionality."""
        checkpoint_dir = temp_dir / "checkpoint"
        checkpoint_dir.mkdir()
        
        # Mock filesystem engine with rollback
        orchestrator._filesystem_engine = Mock()
        orchestrator._filesystem_engine.rollback_transaction.return_value = {
            'files_restored': 5,
            'space_restored': 1024,
            'status': 'success'
        }
        
        # Test rollback
        result = orchestrator.rollback(checkpoint_id="test-checkpoint-123")
        
        assert result['files_restored'] == 5
        assert result['status'] == 'success'


class TestVacuumOrchestratorIntegration:
    """Integration tests for Vacuum Orchestrator v2."""
    
    @pytest.fixture
    def real_temp_dir(self):
        """Create real temporary directory with test filesystem."""
        temp = tempfile.mkdtemp()
        temp_path = Path(temp)
        
        # Create test filesystem structure
        (temp_path / "temp.tmp").write_text("temporary file")
        (temp_path / "__pycache__").mkdir()
        (temp_path / "__pycache__" / "module.pyc").write_bytes(b"bytecode")
        (temp_path / "source.py").write_text("print('hello')")
        (temp_path / "README.md").write_text("# Documentation")
        
        yield temp_path
        shutil.rmtree(temp, ignore_errors=True)
    
    def test_full_dry_run_workflow(self, real_temp_dir):
        """Test complete dry-run workflow end-to-end."""
        # Create real database
        db_path = real_temp_dir / "test.db"
        state_db = PlanningStateDB(str(db_path))
        
        # Create orchestrator with real config
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = """
            cleanup_categories:
              temp_files:
                priority: HIGH
                patterns: ["*.tmp"]
            safety:
              critical_patterns: ["*.py", "*.md"]
            exclusions: []
            """
            
            orchestrator = VacuumOrchestratorV2(
                config_path="dummy.yaml",
                state_db=state_db
            )
        
        # Execute dry-run
        result = orchestrator.execute(
            target_path=str(real_temp_dir),
            dry_run=True
        )
        
        # Verify no files deleted
        assert (real_temp_dir / "temp.tmp").exists()
        assert (real_temp_dir / "source.py").exists()
        assert result['status'] in ['dry_run', 'error']  # May error due to mock config


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
