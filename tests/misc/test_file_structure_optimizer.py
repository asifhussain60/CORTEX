"""
Tests for File Structure Optimizer
Validates automatic splitting of large YAML files into modular phase-based structures.

Author: Asif Hussain
Created: 2025-12-01
"""

import pytest
import yaml
from pathlib import Path
from src.utils.file_structure_optimizer import FileStructureOptimizer, PlanProxy
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def large_yaml_file(temp_dir):
    """Create a large YAML file with multiple phases."""
    data = {
        'metadata': {
            'plan_id': 'TEST-PLAN-001',
            'feature_name': 'Test Feature',
            'created': '2025-12-01',
            'version': '1.0.0'
        },
        'phases': [
            {
                'phase_id': f'phase_{i}',
                'name': f'Phase {i}',
                'description': f'Description for phase {i}' * 100,  # Make it big
                'deliverables': [
                    {'id': f'del_{j}', 'title': f'Deliverable {j}', 'status': 'not-started'}
                    for j in range(10)
                ],
                'status': 'not-started'
            }
            for i in range(10)
        ],
        'summary': {
            'total_phases': 10,
            'total_deliverables': 100
        }
    }
    
    file_path = temp_dir / 'test-plan.yaml'
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)
    
    return file_path


class TestFileStructureOptimizer:
    """Test suite for FileStructureOptimizer."""
    
    def test_should_split_large_file(self, large_yaml_file):
        """Test that optimizer detects large files."""
        optimizer = FileStructureOptimizer(threshold_bytes=10 * 1024)  # 10KB
        assert optimizer.should_split(large_yaml_file)
    
    def test_should_not_split_small_file(self, temp_dir):
        """Test that optimizer doesn't split small files."""
        small_file = temp_dir / 'small.yaml'
        with open(small_file, 'w') as f:
            yaml.dump({'test': 'data'}, f)
        
        optimizer = FileStructureOptimizer(threshold_bytes=20 * 1024)
        assert not optimizer.should_split(small_file)
    
    def test_split_into_phases(self, large_yaml_file):
        """Test splitting large file into modular structure."""
        optimizer = FileStructureOptimizer()
        index_path, phase_paths = optimizer.split_into_phases(large_yaml_file)
        
        # Verify index file exists and is smaller
        assert index_path.exists()
        assert index_path.stat().st_size < large_yaml_file.with_suffix('.yaml.bak').stat().st_size
        
        # Verify all phase files created
        assert len(phase_paths) == 10
        
        # Verify phases directory exists
        phases_dir = large_yaml_file.parent / 'phases'
        assert phases_dir.exists()
        assert phases_dir.is_dir()
    
    def test_index_file_structure(self, large_yaml_file):
        """Test that index file has correct structure."""
        optimizer = FileStructureOptimizer()
        index_path, _ = optimizer.split_into_phases(large_yaml_file)
        
        with open(index_path, 'r') as f:
            index_data = yaml.safe_load(f)
        
        # Verify modular structure metadata
        assert '_modular_structure' in index_data
        assert index_data['_modular_structure']['enabled'] is True
        assert index_data['_modular_structure']['phase_count'] == 10
        
        # Verify phases are references, not full data
        assert 'phases' in index_data
        assert len(index_data['phases']) == 10
        
        # Verify phase reference structure
        phase_ref = index_data['phases'][0]
        assert 'phase_id' in phase_ref
        assert 'name' in phase_ref
        assert 'file' in phase_ref
        assert 'deliverables_count' in phase_ref
        
        # Verify full deliverables NOT in reference
        assert 'deliverables' not in phase_ref or len(str(phase_ref.get('deliverables', ''))) < 100
    
    def test_phase_files_content(self, large_yaml_file):
        """Test that phase files contain full phase data."""
        optimizer = FileStructureOptimizer()
        _, phase_paths = optimizer.split_into_phases(large_yaml_file)
        
        # Load first phase file
        with open(phase_paths[0], 'r') as f:
            phase_data = yaml.safe_load(f)
        
        # Verify full phase data preserved
        assert 'phase_id' in phase_data
        assert 'name' in phase_data
        assert 'deliverables' in phase_data
        assert len(phase_data['deliverables']) == 10
    
    def test_load_plan_with_phases(self, large_yaml_file):
        """Test lazy loading of modular plan structure."""
        optimizer = FileStructureOptimizer()
        index_path, _ = optimizer.split_into_phases(large_yaml_file)
        
        # Load plan with lazy loading
        plan_data = optimizer.load_plan_with_phases(index_path)
        
        # Verify plan data is PlanProxy
        assert isinstance(plan_data, PlanProxy)
        
        # Verify can access metadata
        assert plan_data['metadata']['plan_id'] == 'TEST-PLAN-001'
    
    def test_plan_proxy_lazy_loading(self, large_yaml_file):
        """Test PlanProxy lazy loads phases on demand."""
        optimizer = FileStructureOptimizer()
        index_path, _ = optimizer.split_into_phases(large_yaml_file)
        
        plan_proxy = optimizer.load_plan_with_phases(index_path)
        
        # Access phases (should trigger lazy load)
        phases = plan_proxy['phases']
        
        # Verify all phases loaded
        assert len(phases) == 10
        
        # Verify full phase data
        assert 'deliverables' in phases[0]
        assert len(phases[0]['deliverables']) == 10
    
    def test_plan_proxy_load_single_phase(self, large_yaml_file):
        """Test loading single phase by index."""
        optimizer = FileStructureOptimizer()
        index_path, _ = optimizer.split_into_phases(large_yaml_file)
        
        plan_proxy = optimizer.load_plan_with_phases(index_path)
        
        # Load specific phase
        phase_5 = plan_proxy.load_phase(5)
        
        # Verify correct phase loaded
        assert phase_5['phase_id'] == 'phase_5'
        assert phase_5['name'] == 'Phase 5'
        assert len(phase_5['deliverables']) == 10
    
    def test_backup_created(self, large_yaml_file):
        """Test that original file is backed up."""
        optimizer = FileStructureOptimizer()
        optimizer.split_into_phases(large_yaml_file)
        
        # Verify backup exists
        backup_path = large_yaml_file.with_suffix('.yaml.bak')
        assert backup_path.exists()
    
    def test_performance_improvement(self, large_yaml_file):
        """Test that index file is significantly smaller than original."""
        optimizer = FileStructureOptimizer()
        
        original_size = large_yaml_file.stat().st_size
        index_path, _ = optimizer.split_into_phases(large_yaml_file)
        index_size = index_path.stat().st_size
        
        # Verify at least 70% reduction
        reduction = (1 - index_size / original_size) * 100
        assert reduction >= 70, f"Expected 70%+ reduction, got {reduction:.1f}%"


class TestPlanningOrchestratorIntegration:
    """Test integration with PlanningOrchestrator."""
    
    def test_optimizer_integration_ready(self):
        """Test that FileStructureOptimizer is ready for PlanningOrchestrator integration."""
        optimizer = FileStructureOptimizer(threshold_bytes=20 * 1024)
        
        # Verify optimizer has all required methods
        assert hasattr(optimizer, 'should_split')
        assert hasattr(optimizer, 'split_into_phases')
        assert hasattr(optimizer, 'load_plan_with_phases')
        
        # Verify threshold configured
        assert optimizer.threshold_bytes == 20 * 1024
        
        print("✓ FileStructureOptimizer ready for PlanningOrchestrator integration")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
