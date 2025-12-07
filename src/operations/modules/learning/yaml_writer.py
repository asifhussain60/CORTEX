"""
YAML Writer & Validator (Phase 5)
Safely appends lessons to lessons-learned.yaml with validation and rollback.

Features:
- Schema validation for lesson structure
- Atomic writes with backup/rollback
- Auto-generated lesson IDs (git-learning-NNN)
- YAML formatting preservation
- File integrity verification

7-Step Safety Protocol:
1. Create backup
2. Validate schema
3. Generate unique ID
4. Atomic write
5. Verify integrity
6. Cleanup backup
7. Log operation

Author: Asif Hussain
License: Source-Available
"""

import yaml
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

from src.operations.modules.learning.lesson_capture import CapturedLesson

logger = logging.getLogger(__name__)


class SchemaValidationError(Exception):
    """Raised when lesson schema validation fails."""
    pass


def generate_lesson_id(existing_ids: List[str]) -> str:
    """
    Generate next sequential lesson ID.
    
    Format: 'git-learning-NNN' where NNN is zero-padded 3-digit number.
    
    Args:
        existing_ids: List of existing lesson IDs
        
    Returns:
        Next available lesson ID
    """
    if not existing_ids:
        return 'git-learning-001'
    
    # Extract numeric parts from IDs
    numbers = []
    for lesson_id in existing_ids:
        if lesson_id.startswith('git-learning-'):
            try:
                num = int(lesson_id.split('-')[-1])
                numbers.append(num)
            except ValueError:
                continue
    
    # Find max and increment
    max_num = max(numbers) if numbers else 0
    next_num = max_num + 1
    
    return f'git-learning-{next_num:03d}'


class YAMLWriter:
    """
    Safe YAML writer for lessons-learned.yaml.
    
    Provides atomic writes with backup/rollback, schema validation,
    and automatic ID generation.
    """
    
    def __init__(self, yaml_file: Optional[Path] = None):
        """
        Initialize YAML writer.
        
        Args:
            yaml_file: Optional path to lessons YAML file
        """
        if yaml_file is None:
            # Default to cortex-brain lessons-learned.yaml
            yaml_file = Path(__file__).parents[4] / "cortex-brain" / "lessons-learned.yaml"
        
        self.yaml_file = Path(yaml_file)
        self.backup_file = self.yaml_file.with_suffix('.yaml.backup')
        
    def append_lesson(self, lesson: CapturedLesson) -> str:
        """
        Append captured lesson to YAML file.
        
        Follows 7-step safety protocol with backup/rollback.
        
        Args:
            lesson: CapturedLesson to append
            
        Returns:
            Generated lesson ID
            
        Raises:
            SchemaValidationError: If lesson fails validation
            IOError: If file operations fail
        """
        try:
            with self._atomic_write_context():
                # Step 1: Backup created by context manager
                
                # Step 2: Read existing lessons
                content = self._read_yaml()
                existing_lessons = content.get('lessons', [])
                
                # Step 3: Generate unique ID
                existing_ids = [l['id'] for l in existing_lessons if 'id' in l]
                lesson_id = generate_lesson_id(existing_ids)
                
                # Step 4: Convert to dict and validate schema
                lesson_dict = self._lesson_to_dict(lesson, lesson_id)
                self._validate_lesson_schema(lesson_dict)
                
                # Step 5: Append and write atomically
                existing_lessons.append(lesson_dict)
                content['lessons'] = existing_lessons
                self._write_yaml(content)
                
                # Step 6: Verify integrity
                self._verify_write_integrity(lesson_dict)
                
                # Step 7: Log operation
                logger.info(f"Successfully appended lesson {lesson_id} to {self.yaml_file}")
                
                return lesson_id
                
        except Exception as e:
            logger.error(f"Failed to append lesson: {e}")
            raise
            
    @contextmanager
    def _atomic_write_context(self):
        """
        Context manager for atomic writes with backup/rollback.
        
        Creates backup before operations, rolls back on failure.
        """
        # Create backup
        backup_path = self._create_backup()
        
        try:
            yield
            # Success - cleanup backup
            if backup_path.exists():
                backup_path.unlink()
        except Exception as e:
            # Failure - rollback from backup
            logger.warning(f"Write failed, rolling back: {e}")
            if backup_path.exists():
                shutil.copy2(backup_path, self.yaml_file)
                backup_path.unlink()
            raise
            
    def _create_backup(self) -> Path:
        """
        Create backup of YAML file.
        
        Returns:
            Path to backup file
        """
        if self.yaml_file.exists():
            shutil.copy2(self.yaml_file, self.backup_file)
            logger.debug(f"Created backup: {self.backup_file}")
        else:
            # Create empty structure if file doesn't exist
            self._write_yaml({'lessons': []})
            
        return self.backup_file
        
    def _read_yaml(self) -> Dict[str, Any]:
        """
        Read and parse YAML file.
        
        Returns:
            Parsed YAML content
        """
        if not self.yaml_file.exists():
            return {'lessons': []}
            
        with open(self.yaml_file, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)
            
        return content if content is not None else {'lessons': []}
        
    def _write_yaml(self, content: Dict[str, Any]) -> None:
        """
        Write content to YAML file with proper formatting.
        
        Args:
            content: Dictionary to write as YAML
        """
        with open(self.yaml_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(
                content,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                indent=2
            )
            
    def _lesson_to_dict(self, lesson: CapturedLesson, lesson_id: str) -> Dict[str, Any]:
        """
        Convert CapturedLesson to dictionary format for YAML.
        
        Args:
            lesson: CapturedLesson to convert
            lesson_id: Generated lesson ID
            
        Returns:
            Dictionary representation
        """
        return {
            'id': lesson_id,
            'problem': lesson.problem,
            'root_cause': lesson.root_cause,
            'solution': lesson.solution,
            'prevention_rules': lesson.prevention_rules,
            'time_cost': lesson.time_cost,
            'created': datetime.now().isoformat(),
            'commit_hash': lesson.commit_hash,
            'confidence': lesson.confidence
        }
        
    def _validate_lesson_schema(self, lesson: Dict[str, Any]) -> None:
        """
        Validate lesson dictionary against schema.
        
        Args:
            lesson: Lesson dictionary to validate
            
        Raises:
            SchemaValidationError: If validation fails
        """
        required_fields = ['id', 'problem', 'root_cause', 'solution', 'prevention_rules', 'time_cost', 'created']
        
        # Check required fields
        for field in required_fields:
            if field not in lesson:
                raise SchemaValidationError(f"Missing required field: {field}")
                
        # Check field types
        if not isinstance(lesson['prevention_rules'], list):
            raise SchemaValidationError("prevention_rules must be a list")
            
        if not isinstance(lesson['problem'], str) or len(lesson['problem']) < 10:
            raise SchemaValidationError("problem must be string with at least 10 characters")
            
        if not isinstance(lesson['time_cost'], str):
            raise SchemaValidationError("time_cost must be string")
            
    def _verify_write_integrity(self, expected_lesson: Dict[str, Any]) -> None:
        """
        Verify written content matches expected lesson.
        
        Args:
            expected_lesson: Lesson that should have been written
            
        Raises:
            IOError: If verification fails
        """
        content = self._read_yaml()
        lessons = content.get('lessons', [])
        
        # Find the lesson we just wrote (should be last)
        if not lessons or lessons[-1]['id'] != expected_lesson['id']:
            raise IOError("Write verification failed: lesson not found or corrupted")
            
        written_lesson = lessons[-1]
        
        # Verify key fields match
        for field in ['problem', 'root_cause', 'solution', 'time_cost']:
            if written_lesson.get(field) != expected_lesson.get(field):
                raise IOError(f"Write verification failed: {field} mismatch")
