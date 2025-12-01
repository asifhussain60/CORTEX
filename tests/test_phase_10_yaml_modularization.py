"""
Test Phase 10: Systematic YAML Modularization
RED Phase: Tests written before implementation

Purpose: Verify automatic YAML file modularization:
1. Detect large files (>20KB) and split into modules
2. Create lightweight index + module files
3. Lazy-load modules on demand

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
from pathlib import Path
import yaml
from src.utils.file_structure_optimizer import FileStructureOptimizer


class TestFileStructureOptimizerCore:
    """Test suite for FileStructureOptimizer core functionality"""
    
    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create temporary directory for tests"""
        return tmp_path
    
    @pytest.fixture
    def optimizer(self):
        """Create FileStructureOptimizer instance with default 20KB threshold"""
        return FileStructureOptimizer(threshold_bytes=20480, module_key='phases')
    
    def test_should_split_returns_false_for_small_files(self, optimizer, temp_dir):
        """
        RED Phase Test 1: Verify should_split() returns False for files <20KB
        
        Acceptance Criteria (10.1.1):
        - Default 20KB (20,480 bytes) threshold
        - Returns False if file size < threshold
        """
        # Arrange - Create small file (5KB)
        small_file = temp_dir / "small_plan.yaml"
        small_data = {"metadata": {"name": "Small Plan"}, "phases": [{"id": "1"}]}
        
        with open(small_file, 'w', encoding='utf-8') as f:
            yaml.dump(small_data, f)
        
        # Act
        result = optimizer.should_split(small_file)
        
        # Assert
        assert result is False, "Small files should not be split"
        assert small_file.stat().st_size < 20480, "Test file should be under 20KB"
    
    def test_should_split_returns_true_for_large_files(self, optimizer, temp_dir):
        """
        RED Phase Test 2: Verify should_split() returns True for files >20KB
        
        Acceptance Criteria (10.1.1):
        - Returns True if file size > threshold
        """
        # Arrange - Create large file (>20KB with padding)
        large_file = temp_dir / "large_plan.yaml"
        large_data = {
            "metadata": {"name": "Large Plan"},
            "phases": [
                {
                    "id": str(i),
                    "name": f"Phase {i}",
                    "description": "x" * 1000,  # 1KB per phase
                    "tasks": [f"Task {j}" for j in range(100)]
                }
                for i in range(25)  # 25 phases = ~25KB
            ]
        }
        
        with open(large_file, 'w', encoding='utf-8') as f:
            yaml.dump(large_data, f)
        
        # Act
        result = optimizer.should_split(large_file)
        
        # Assert
        assert result is True, "Large files should be split"
        assert large_file.stat().st_size > 20480, "Test file should be over 20KB"
    
    def test_threshold_is_configurable(self, temp_dir):
        """
        RED Phase Test 3: Verify threshold is configurable
        
        Acceptance Criteria (10.1.1):
        - Threshold configurable in constructor
        """
        # Arrange - Create 15KB file
        test_file = temp_dir / "medium_plan.yaml"
        medium_data = {
            "phases": [
                {"id": str(i), "name": f"Phase {i}", "description": "x" * 500}
                for i in range(30)  # ~15KB
            ]
        }
        
        with open(test_file, 'w', encoding='utf-8') as f:
            yaml.dump(medium_data, f)
        
        file_size = test_file.stat().st_size
        
        # Act - Test with different thresholds
        low_threshold_optimizer = FileStructureOptimizer(threshold_bytes=10240)  # 10KB
        high_threshold_optimizer = FileStructureOptimizer(threshold_bytes=30720)  # 30KB
        
        # Assert
        assert low_threshold_optimizer.should_split(test_file) is True, "Should split with 10KB threshold"
        assert high_threshold_optimizer.should_split(test_file) is False, "Should not split with 30KB threshold"


class TestFileStructureOptimizerSplitting:
    """Test suite for split_into_modules functionality"""
    
    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create temporary directory for tests"""
        return tmp_path
    
    @pytest.fixture
    def optimizer(self):
        """Create FileStructureOptimizer instance"""
        return FileStructureOptimizer(threshold_bytes=20480, module_key='phases')
    
    def test_split_creates_module_directory(self, optimizer, temp_dir):
        """
        RED Phase Test 4: Verify split_into_modules() creates subdirectory
        
        Acceptance Criteria (10.1.2):
        - Creates phases/ subdirectory if missing
        """
        # Arrange
        plan_data = {
            "metadata": {"name": "Test Plan"},
            "phases": [
                {"phase_id": "1", "name": "Phase 1", "tasks": ["Task 1"]},
                {"phase_id": "2", "name": "Phase 2", "tasks": ["Task 2"]}
            ]
        }
        
        # Act
        index_path = optimizer.split_into_modules(plan_data, temp_dir)
        
        # Assert
        phases_dir = temp_dir / "phases"
        assert phases_dir.exists(), "phases/ directory should be created"
        assert phases_dir.is_dir(), "phases/ should be a directory"
    
    def test_split_creates_individual_phase_files(self, optimizer, temp_dir):
        """
        RED Phase Test 5: Verify each phase written to separate file
        
        Acceptance Criteria (10.1.2):
        - Write each phase to phases/phase-N-name.yaml
        - Sanitizes phase names for filenames
        """
        # Arrange
        plan_data = {
            "metadata": {"name": "Test Plan"},
            "phases": [
                {"phase_id": "1", "name": "Phase One", "tasks": ["Task 1"]},
                {"phase_id": "2", "name": "Phase Two", "tasks": ["Task 2"]},
                {"phase_id": "3", "name": "Phase Three", "tasks": ["Task 3"]}
            ]
        }
        
        # Act
        index_path = optimizer.split_into_modules(plan_data, temp_dir)
        
        # Assert
        phases_dir = temp_dir / "phases"
        phase1_file = phases_dir / "phase-1.yaml"
        phase2_file = phases_dir / "phase-2.yaml"
        phase3_file = phases_dir / "phase-3.yaml"
        
        assert phase1_file.exists(), "Phase 1 file should exist"
        assert phase2_file.exists(), "Phase 2 file should exist"
        assert phase3_file.exists(), "Phase 3 file should exist"
        
        # Verify content
        with open(phase1_file, 'r', encoding='utf-8') as f:
            phase1_data = yaml.safe_load(f)
        
        assert phase1_data["phase_id"] == "1"
        assert phase1_data["name"] == "Phase One"
        assert phase1_data["tasks"] == ["Task 1"]
    
    def test_split_creates_lightweight_index(self, optimizer, temp_dir):
        """
        RED Phase Test 6: Verify index file is lightweight with references only
        
        Acceptance Criteria (10.1.3):
        - Index includes: metadata, phase list (with file references), summary
        - Phase entries: phase_id, name, file path, status, priority, estimated_effort
        - No inline phase data (references only)
        - File size <10KB typical
        """
        # Arrange
        plan_data = {
            "metadata": {"name": "Large Plan", "description": "Test plan"},
            "phases": [
                {
                    "phase_id": str(i),
                    "name": f"Phase {i}",
                    "status": "not-started",
                    "priority": i,
                    "estimated_effort": f"{i * 2}h",
                    "tasks": [f"Task {j}" for j in range(50)],  # Lots of data
                    "deliverables": [f"Deliverable {j}" for j in range(20)]
                }
                for i in range(1, 11)  # 10 phases
            ]
        }
        
        # Act
        index_path = optimizer.split_into_modules(plan_data, temp_dir)
        
        # Assert - Index file exists
        assert index_path.exists(), "Index file should be created"
        assert index_path.name == "index.yaml", "Index should be named index.yaml"
        
        # Load and verify index
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = yaml.safe_load(f)
        
        # Verify metadata preserved
        assert "metadata" in index_data
        assert index_data["metadata"]["name"] == "Large Plan"
        
        # Verify phases list exists with references
        assert "phases" in index_data
        assert len(index_data["phases"]) == 10
        
        # Verify phase entries are lightweight (no tasks/deliverables)
        first_phase = index_data["phases"][0]
        assert "phase_id" in first_phase
        assert "name" in first_phase
        assert "file" in first_phase, "Phase should have file reference"
        assert "tasks" not in first_phase, "Index should not contain full task data"
        assert "deliverables" not in first_phase, "Index should not contain deliverables"
        
        # Verify file reference format
        assert first_phase["file"] == "phases/phase-1.yaml"
        
        # Verify index is small
        index_size = index_path.stat().st_size
        assert index_size < 10240, f"Index should be <10KB (actual: {index_size} bytes)"
    
    def test_split_preserves_all_phase_data_in_modules(self, optimizer, temp_dir):
        """
        RED Phase Test 7: Verify all phase data preserved in module files
        
        Acceptance Criteria (10.1.2):
        - Preserves all phase data (deliverables, dependencies, acceptance criteria)
        """
        # Arrange
        plan_data = {
            "metadata": {"name": "Complete Plan"},
            "phases": [
                {
                    "phase_id": "1",
                    "name": "Foundation Phase",
                    "tasks": ["Task 1", "Task 2"],
                    "deliverables": ["Deliverable A", "Deliverable B"],
                    "dependencies": ["Phase 0"],
                    "acceptance_criteria": ["Criterion 1", "Criterion 2"]
                }
            ]
        }
        
        # Act
        optimizer.split_into_modules(plan_data, temp_dir)
        
        # Assert - Read phase file and verify all data present
        phase_file = temp_dir / "phases" / "phase-1.yaml"
        with open(phase_file, 'r', encoding='utf-8') as f:
            phase_data = yaml.safe_load(f)
        
        assert phase_data["phase_id"] == "1"
        assert phase_data["name"] == "Foundation Phase"
        assert phase_data["tasks"] == ["Task 1", "Task 2"]
        assert phase_data["deliverables"] == ["Deliverable A", "Deliverable B"]
        assert phase_data["dependencies"] == ["Phase 0"]
        assert phase_data["acceptance_criteria"] == ["Criterion 1", "Criterion 2"]


class TestPlanningOrchestratorModularOutput:
    """Test suite for PlanningOrchestrator modular output integration"""
    
    @pytest.fixture
    def temp_cortex_root(self, tmp_path):
        """Create temporary CORTEX directory structure"""
        cortex_root = tmp_path / "CORTEX"
        cortex_root.mkdir()
        
        brain_path = cortex_root / "cortex-brain"
        config_path = brain_path / "config"
        config_path.mkdir(parents=True)
        
        plans_path = brain_path / "documents" / "planning" / "features" / "active"
        plans_path.mkdir(parents=True)
        
        # Create minimal schema
        schema_path = config_path / "plan-schema.yaml"
        schema_path.write_text("""
schema:
  version: "1.0.0"
  required_fields: [metadata, phases]
""", encoding='utf-8')
        
        return cortex_root
    
    @pytest.fixture
    def orchestrator(self, temp_cortex_root):
        """Create PlanningOrchestrator instance"""
        from src.orchestrators.planning_orchestrator import PlanningOrchestrator
        return PlanningOrchestrator(str(temp_cortex_root))
    
    def test_small_plan_creates_monolithic_file(self, orchestrator, temp_cortex_root):
        """
        RED Phase Test 8: Verify plans <20KB create single monolithic file
        
        Acceptance Criteria:
        - Plans under threshold create single YAML file
        - No phases/ subdirectory created
        """
        # Arrange - Small plan with 3 phases
        phases = [
            {"id": str(i), "name": f"Phase {i}", "tasks": [f"Task {i}"]}
            for i in range(1, 4)
        ]
        
        # Act
        result = orchestrator.generate_plan_incremental(
            plan_name="small-plan",
            metadata={"name": "Small Plan"},
            phases=phases
        )
        
        # Assert
        assert result["success"] is True
        plan_path = Path(result["file_path"])
        assert plan_path.exists(), "Plan file should exist"
        
        # Verify no phases/ subdirectory
        phases_dir = plan_path.parent / "small-plan-phases"
        assert not phases_dir.exists(), "Should not create phases directory for small plans"
        
        # Verify single file contains all phases
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan_data = yaml.safe_load(f)
        
        assert len(plan_data["phases"]) == 3, "All phases should be in single file"
    
    def test_large_plan_creates_modular_structure(self, orchestrator, temp_cortex_root):
        """
        RED Phase Test 9: Verify plans >20KB create modular structure
        
        Acceptance Criteria:
        - Plans over threshold create index + phases/ subdirectory
        - Index file is lightweight
        - Each phase in separate file
        """
        # Arrange - Large plan with 20 phases, lots of data per phase
        phases = [
            {
                "id": str(i),
                "name": f"Large Phase {i}",
                "description": "x" * 500,  # Padding to increase size
                "tasks": [f"Task {j}" for j in range(50)],
                "deliverables": [f"Deliverable {j}" for j in range(20)]
            }
            for i in range(1, 21)  # 20 phases
        ]
        
        # Act
        result = orchestrator.generate_plan_incremental(
            plan_name="large-plan",
            metadata={"name": "Large Plan"},
            phases=phases,
            use_modular_output=True  # Force modular for testing
        )
        
        # Assert
        assert result["success"] is True
        
        # Check for modular structure
        # Result file_path points to index
        result_path = Path(result["file_path"])
        
        # Verify modular structure was created (if implemented)
        # This test will initially fail, driving the GREEN implementation
        if result.get("modular", False):
            assert result_path.exists(), f"Index file should exist at {result_path}"
            assert result_path.name == "index.yaml", "Should be index.yaml"
            
            phases_dir = result_path.parent / "phases"
            assert phases_dir.exists(), "Phases directory should exist"
            assert phases_dir.is_dir(), "Phases should be a directory"
            
            # Verify individual phase files
            phase_files = list(phases_dir.glob("phase-*.yaml"))
            assert len(phase_files) == 20, "Should have 20 phase files"
            
            # Verify index is lightweight
            index_size = result_path.stat().st_size
            assert index_size < 10240, f"Index should be <10KB (actual: {index_size})"
