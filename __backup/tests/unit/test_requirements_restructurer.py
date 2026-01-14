"""
Tests for requirements restructuring tool.

TDD: RED phase - Define expected behavior before implementation.
"""

import pytest
import yaml
from pathlib import Path
import tempfile
import shutil


class TestRequirementsRestructurer:
    """Test suite for requirements YAML restructuring."""
    
    def test_restructure_flat_list_to_nested_object(self):
        """Test converting flat list structure to nested object structure."""
        from src.tools.requirements_restructurer import RequirementsRestructurer
        
        # Flat list structure (incorrect)
        input_yaml = """
- requirement_id: REQ-001
  description: "Test requirement"
  acceptance_criteria:
    - "Criterion 1"
  priority: P0_CRITICAL
  status: COMPLETE
"""
        
        # Expected nested structure (correct)
        expected_structure = {
            'feature_id': 'feat01',
            'feature_name': 'Test Feature',
            'requirements': [
                {
                    'requirement_id': 'REQ-001',
                    'description': 'Test requirement',
                    'acceptance_criteria': ['Criterion 1'],
                    'priority': 'P0_CRITICAL',
                    'status': 'COMPLETE'
                }
            ]
        }
        
        restructurer = RequirementsRestructurer()
        result = restructurer.restructure_yaml_content(
            input_yaml,
            feature_id='feat01',
            feature_name='Test Feature'
        )
        
        parsed_result = yaml.safe_load(result)
        assert parsed_result['feature_id'] == expected_structure['feature_id']
        assert parsed_result['feature_name'] == expected_structure['feature_name']
        assert len(parsed_result['requirements']) == 1
        assert parsed_result['requirements'][0]['requirement_id'] == 'REQ-001'
    
    def test_batch_restructure_multiple_files(self):
        """Test batch restructuring of multiple requirement files."""
        from src.tools.requirements_restructurer import RequirementsRestructurer
        
        # Create temp directory with test files
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create feat01 directory
            feat01_dir = tmppath / "feat01-foundation"
            feat01_dir.mkdir()
            
            # Create flat list requirements file
            req_file = feat01_dir / "requirements.yaml"
            req_file.write_text("""
- requirement_id: REQ-001
  description: "Test req 1"
  acceptance_criteria:
    - "Criterion 1"
  priority: P0_CRITICAL
  status: COMPLETE
""")
            
            restructurer = RequirementsRestructurer()
            feature_map = {
                'feat01-foundation': {
                    'feature_id': 'feat01',
                    'feature_name': 'Foundation Layer'
                }
            }
            
            results = restructurer.batch_restructure(tmppath, feature_map)
            
            assert len(results) == 1
            assert results[0].file == str(req_file)
            assert results[0].success is True
            assert results[0].requirements_count == 1
    
    def test_preserve_existing_nested_structure(self):
        """Test that already-correct files are not modified."""
        from src.tools.requirements_restructurer import RequirementsRestructurer
        
        # Already correct structure
        input_yaml = """
feature_id: feat01
feature_name: "Test Feature"
requirements:
  - requirement_id: REQ-001
    description: "Test requirement"
    acceptance_criteria:
      - "Criterion 1"
    priority: P0_CRITICAL
    status: COMPLETE
"""
        
        restructurer = RequirementsRestructurer()
        result = restructurer.restructure_yaml_content(
            input_yaml,
            feature_id='feat01',
            feature_name='Test Feature'
        )
        
        # Should return same structure
        parsed_input = yaml.safe_load(input_yaml)
        parsed_result = yaml.safe_load(result)
        
        assert parsed_input == parsed_result
    
    def test_extract_feature_info_from_directory_name(self):
        """Test extracting feature ID and name from directory structure."""
        from src.tools.requirements_restructurer import RequirementsRestructurer
        
        restructurer = RequirementsRestructurer()
        
        # Test standard naming pattern
        feature_id, feature_name = restructurer.extract_feature_info('feat01-foundation')
        assert feature_id == 'feat01'
        assert feature_name == 'Foundation'
        
        feature_id, feature_name = restructurer.extract_feature_info('feat02-todo-orchestrator')
        assert feature_id == 'feat02'
        assert feature_name == 'Todo Orchestrator'
    
    def test_validate_restructured_output(self):
        """Test that restructured output passes schema validation."""
        from src.tools.requirements_restructurer import RequirementsRestructurer
        
        input_yaml = """
- requirement_id: REQ-001
  description: "Test requirement with proper length"
  acceptance_criteria:
    - "Criterion 1"
  priority: P0_CRITICAL
  status: COMPLETE
"""
        
        restructurer = RequirementsRestructurer()
        result = restructurer.restructure_yaml_content(
            input_yaml,
            feature_id='feat01',
            feature_name='Test Feature'
        )
        
        # Validate structure
        is_valid = restructurer.validate_structure(result)
        assert is_valid is True
    
    def test_dry_run_mode(self):
        """Test dry-run mode that doesn't modify files."""
        from src.tools.requirements_restructurer import RequirementsRestructurer
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            feat01_dir = tmppath / "feat01-foundation"
            feat01_dir.mkdir()
            
            req_file = feat01_dir / "requirements.yaml"
            original_content = """
- requirement_id: REQ-001
  description: "Test requirement"
  acceptance_criteria:
    - "Criterion 1"
"""
            req_file.write_text(original_content)
            
            restructurer = RequirementsRestructurer()
            feature_map = {
                'feat01-foundation': {
                    'feature_id': 'feat01',
                    'feature_name': 'Foundation Layer'
                }
            }
            
            results = restructurer.batch_restructure(
                tmppath,
                feature_map,
                dry_run=True
            )
            
            # File should not be modified
            assert req_file.read_text() == original_content
            assert results[0].dry_run is True
    
    def test_backup_original_files(self):
        """Test that original files are backed up before modification."""
        from src.tools.requirements_restructurer import RequirementsRestructurer
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            feat01_dir = tmppath / "feat01-foundation"
            feat01_dir.mkdir()
            
            req_file = feat01_dir / "requirements.yaml"
            original_content = """
- requirement_id: REQ-001
  description: "Test requirement"
  acceptance_criteria:
    - "Criterion 1"
"""
            req_file.write_text(original_content)
            
            restructurer = RequirementsRestructurer()
            feature_map = {
                'feat01-foundation': {
                    'feature_id': 'feat01',
                    'feature_name': 'Foundation Layer'
                }
            }
            
            results = restructurer.batch_restructure(
                tmppath,
                feature_map,
                create_backup=True
            )
            
            # Backup should exist
            backup_file = feat01_dir / "requirements.yaml.bak"
            assert backup_file.exists()
            assert backup_file.read_text() == original_content
    
    def test_error_handling_invalid_yaml(self):
        """Test error handling for invalid YAML syntax."""
        from src.tools.requirements_restructurer import RequirementsRestructurer
        
        invalid_yaml = """
- requirement_id: REQ-001
  description: "Test
  invalid syntax here
"""
        
        restructurer = RequirementsRestructurer()
        
        with pytest.raises(yaml.YAMLError):
            restructurer.restructure_yaml_content(
                invalid_yaml,
                feature_id='feat01',
                feature_name='Test'
            )
    
    def test_generate_summary_report(self):
        """Test generation of summary report after batch restructuring."""
        from src.tools.requirements_restructurer import RequirementsRestructurer
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create multiple feature directories
            for i in range(1, 4):
                feat_dir = tmppath / f"feat0{i}-test"
                feat_dir.mkdir()
                req_file = feat_dir / "requirements.yaml"
                req_file.write_text(f"""
- requirement_id: REQ-00{i}
  description: "Test requirement {i}"
  acceptance_criteria:
    - "Criterion {i}"
""")
            
            restructurer = RequirementsRestructurer()
            feature_map = {
                f'feat0{i}-test': {
                    'feature_id': f'feat0{i}',
                    'feature_name': f'Test Feature {i}'
                }
                for i in range(1, 4)
            }
            
            results = restructurer.batch_restructure(tmppath, feature_map)
            report = restructurer.generate_summary_report(results)
            
            assert report['total_files'] == 3
            assert report['successful'] == 3
            assert report['failed'] == 0
            assert report['total_requirements'] == 3
