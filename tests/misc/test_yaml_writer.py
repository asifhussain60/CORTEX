"""
Tests for YAML Writer & Validator (Phase 5)
Validates schema checking, atomic writes, backup/rollback, and ID generation.

RED Phase Test Creation - These tests should fail initially.
"""

import pytest
from pathlib import Path
import yaml
import tempfile
import shutil
from datetime import datetime

from src.operations.modules.learning.yaml_writer import (
    YAMLWriter,
    SchemaValidationError,
    generate_lesson_id
)
from src.operations.modules.learning.lesson_capture import CapturedLesson


@pytest.fixture
def temp_yaml_file():
    """Create temporary YAML file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        # Write initial lessons structure
        initial_content = {
            'lessons': [
                {
                    'id': 'test-001',
                    'problem': 'Existing lesson problem',
                    'root_cause': 'Existing root cause',
                    'solution': 'Existing solution',
                    'prevention_rules': ['Existing rule'],
                    'time_cost': '1h',
                    'created': '2024-12-01T10:00:00'
                }
            ]
        }
        yaml.safe_dump(initial_content, f)
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()
    backup_path = temp_path.with_suffix('.yaml.backup')
    if backup_path.exists():
        backup_path.unlink()


@pytest.fixture
def sample_lesson():
    """Create sample captured lesson for testing."""
    return CapturedLesson(
        problem="Payment processing failed with null pointer exception",
        root_cause="Missing null check in payment validator",
        solution="Added null checks before processing payment data",
        prevention_rules=["Always validate inputs before processing", "Use Optional types"],
        time_cost="2h",
        commit_hash="abc123",
        confidence=0.85
    )


@pytest.fixture
def yaml_writer(temp_yaml_file):
    """Create YAMLWriter instance with temporary file."""
    return YAMLWriter(yaml_file=temp_yaml_file)


class TestLessonIDGeneration:
    """Test automatic lesson ID generation."""
    
    def test_generate_lesson_id_format(self):
        """Test that generated IDs follow 'git-learning-NNN' format."""
        lesson_id = generate_lesson_id(existing_ids=['git-learning-001', 'git-learning-002'])
        
        assert lesson_id.startswith('git-learning-')
        assert lesson_id == 'git-learning-003'
        
    def test_generate_lesson_id_handles_empty_list(self):
        """Test ID generation with no existing lessons."""
        lesson_id = generate_lesson_id(existing_ids=[])
        
        assert lesson_id == 'git-learning-001'
        
    def test_generate_lesson_id_finds_max_number(self):
        """Test that ID generation finds highest existing number."""
        lesson_id = generate_lesson_id(existing_ids=['git-learning-005', 'git-learning-002', 'git-learning-009'])
        
        assert lesson_id == 'git-learning-010'


class TestSchemaValidation:
    """Test YAML schema validation."""
    
    def test_validate_lesson_structure_valid(self, yaml_writer, sample_lesson):
        """Test that valid lesson passes schema validation."""
        lesson_dict = yaml_writer._lesson_to_dict(sample_lesson, lesson_id='git-learning-002')
        
        # Should not raise exception
        yaml_writer._validate_lesson_schema(lesson_dict)
        
    def test_validate_lesson_structure_missing_required_field(self, yaml_writer):
        """Test that missing required fields fail validation."""
        invalid_lesson = {
            'id': 'git-learning-002',
            'problem': 'Test problem',
            # Missing root_cause, solution, etc.
        }
        
        with pytest.raises(SchemaValidationError) as exc_info:
            yaml_writer._validate_lesson_schema(invalid_lesson)
        
        assert 'required field' in str(exc_info.value).lower()
        
    def test_validate_lesson_structure_invalid_type(self, yaml_writer):
        """Test that invalid field types fail validation."""
        invalid_lesson = {
            'id': 'git-learning-002',
            'problem': 'Test problem',
            'root_cause': 'Test cause',
            'solution': 'Test solution',
            'prevention_rules': 'Not a list',  # Should be list
            'time_cost': '2h',
            'created': '2024-12-07T12:00:00'
        }
        
        with pytest.raises(SchemaValidationError) as exc_info:
            yaml_writer._validate_lesson_schema(invalid_lesson)
        
        assert 'prevention_rules' in str(exc_info.value).lower()


class TestBackupAndRollback:
    """Test backup creation and rollback functionality."""
    
    def test_create_backup_before_write(self, yaml_writer, temp_yaml_file):
        """Test that backup is created before modifying file."""
        original_content = temp_yaml_file.read_text()
        
        backup_path = yaml_writer._create_backup()
        
        assert backup_path.exists()
        assert backup_path.read_text() == original_content
        
    def test_rollback_on_write_failure(self, yaml_writer, temp_yaml_file, sample_lesson):
        """Test that file is rolled back if write fails."""
        original_content = temp_yaml_file.read_text()
        
        # Force write failure by mocking _write_yaml
        with pytest.raises(Exception):
            with yaml_writer._atomic_write_context():
                raise Exception("Simulated write failure")
        
        # File should be restored to original state
        assert temp_yaml_file.read_text() == original_content
        
    def test_cleanup_backup_after_success(self, yaml_writer, temp_yaml_file, sample_lesson):
        """Test that backup is cleaned up after successful write."""
        backup_path = temp_yaml_file.with_suffix('.yaml.backup')
        
        yaml_writer.append_lesson(sample_lesson)
        
        # Backup should be removed
        assert not backup_path.exists()


class TestAtomicWrites:
    """Test atomic write operations."""
    
    def test_write_lesson_atomically(self, yaml_writer, temp_yaml_file, sample_lesson):
        """Test that lesson is written atomically (all or nothing)."""
        original_count = len(yaml_writer._read_yaml()['lessons'])
        
        yaml_writer.append_lesson(sample_lesson)
        
        updated_content = yaml_writer._read_yaml()
        assert len(updated_content['lessons']) == original_count + 1
        
    def test_append_lesson_preserves_existing(self, yaml_writer, temp_yaml_file, sample_lesson):
        """Test that appending preserves existing lessons."""
        original_content = yaml_writer._read_yaml()
        original_first_lesson = original_content['lessons'][0]
        
        yaml_writer.append_lesson(sample_lesson)
        
        updated_content = yaml_writer._read_yaml()
        assert updated_content['lessons'][0] == original_first_lesson
        
    def test_verify_write_integrity(self, yaml_writer, temp_yaml_file, sample_lesson):
        """Test that written content can be read back correctly."""
        yaml_writer.append_lesson(sample_lesson)
        
        updated_content = yaml_writer._read_yaml()
        new_lesson = updated_content['lessons'][-1]
        
        assert new_lesson['problem'] == sample_lesson.problem
        assert new_lesson['root_cause'] == sample_lesson.root_cause
        assert new_lesson['solution'] == sample_lesson.solution
        assert new_lesson['time_cost'] == sample_lesson.time_cost


class TestYAMLFormatting:
    """Test YAML formatting and structure preservation."""
    
    def test_preserve_yaml_formatting(self, yaml_writer, temp_yaml_file, sample_lesson):
        """Test that YAML formatting is preserved during writes."""
        yaml_writer.append_lesson(sample_lesson)
        
        content = temp_yaml_file.read_text()
        
        # Should have proper YAML structure
        assert 'lessons:' in content
        assert '- id:' in content or '  - id:' in content  # Accept either format
        assert 'problem:' in content
        
    def test_lesson_to_dict_conversion(self, yaml_writer, sample_lesson):
        """Test conversion of CapturedLesson to dict format."""
        lesson_dict = yaml_writer._lesson_to_dict(sample_lesson, lesson_id='git-learning-002')
        
        assert lesson_dict['id'] == 'git-learning-002'
        assert lesson_dict['problem'] == sample_lesson.problem
        assert lesson_dict['root_cause'] == sample_lesson.root_cause
        assert lesson_dict['solution'] == sample_lesson.solution
        assert lesson_dict['prevention_rules'] == sample_lesson.prevention_rules
        assert lesson_dict['time_cost'] == sample_lesson.time_cost
        assert 'created' in lesson_dict
        assert 'commit_hash' in lesson_dict
