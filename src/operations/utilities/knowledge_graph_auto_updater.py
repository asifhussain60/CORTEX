"""
Knowledge Graph Auto-Updater - Automated knowledge graph maintenance.

Extracts patterns from execution context and safely updates knowledge-graph.yaml
with file locking, backup/rollback, and concurrent access protection.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml
import logging
import fcntl
import time
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class UpdateResult:
    """Result of knowledge graph update operation."""
    success: bool
    patterns_added: int
    duplicates_skipped: int
    backup_path: Optional[Path] = None
    error_message: Optional[str] = None


class PatternExtractor:
    """Extracts reusable patterns from execution context."""
    
    @staticmethod
    def extract_from_context(context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract 3-5 patterns from execution context.
        
        Args:
            context: Execution context with metrics
            
        Returns:
            List of pattern dictionaries
        """
        patterns = []
        
        # Pattern 1: High test coverage
        coverage = context.get('coverage', 0)
        if coverage >= 90:
            patterns.append({
                'name': 'high-test-coverage-pattern',
                'description': f'Achieved {coverage:.1f}% test coverage',
                'confidence': min(100, int(coverage))
            })
        
        # Pattern 2: Multi-file modification
        files_modified = context.get('files_modified', [])
        if len(files_modified) >= 3:
            patterns.append({
                'name': 'multi-file-modification-pattern',
                'description': f'Modified {len(files_modified)} files in single feature',
                'confidence': min(100, len(files_modified) * 20)
            })
        
        # Pattern 3: Quality gates passed
        quality_gates = context.get('quality_gates', [])
        if len(quality_gates) >= 3:
            patterns.append({
                'name': 'comprehensive-quality-validation-pattern',
                'description': f'Passed {len(quality_gates)} quality gates',
                'confidence': len(quality_gates) * 30
            })
        
        # Pattern 4: High test pass rate
        tests_run = context.get('tests_run', 0)
        tests_passed = context.get('tests_passed', 0)
        if tests_run > 0 and tests_passed == tests_run:
            patterns.append({
                'name': 'perfect-test-pass-rate-pattern',
                'description': f'100% test pass rate ({tests_passed}/{tests_run})',
                'confidence': 100
            })
        
        # Pattern 5: Feature complexity indicator
        if len(files_modified) >= 5 and coverage >= 90:
            patterns.append({
                'name': 'complex-feature-high-quality-pattern',
                'description': 'Complex feature with high quality metrics',
                'confidence': 95
            })
        
        # Return 3-5 patterns (trim if needed)
        return patterns[:5]


class KnowledgeGraphAutoUpdater:
    """
    Automatically updates knowledge-graph.yaml with new patterns.
    
    Features:
    - File locking (fcntl) for concurrent access safety
    - Automatic backup before modification
    - Rollback on failure
    - Pattern deduplication
    - Extracts 3-5 patterns per run
    """
    
    def __init__(self, graph_path: Path = None):
        """
        Initialize auto-updater.
        
        Args:
            graph_path: Path to knowledge-graph.yaml (default: cortex-brain/)
        """
        if graph_path is None:
            graph_path = Path("cortex-brain/knowledge-graph.yaml")
        
        self.graph_path = graph_path
        self._lock_file = None
        self._lock_fd = None
    
    def acquire_lock(self) -> bool:
        """
        Acquire exclusive lock on knowledge graph file.
        
        Returns:
            True if lock acquired, False otherwise
        """
        try:
            lock_path = self.graph_path.parent / f"{self.graph_path.name}.lock"
            self._lock_file = open(lock_path, 'w')
            fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self._lock_fd = self._lock_file.fileno()
            return True
        except (OSError, IOError) as e:
            logger.warning(f"Could not acquire lock: {e}")
            if self._lock_file:
                self._lock_file.close()
                self._lock_file = None
            return False
    
    def release_lock(self) -> bool:
        """
        Release lock on knowledge graph file.
        
        Returns:
            True if lock released successfully
        """
        try:
            if self._lock_file:
                fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_UN)
                self._lock_file.close()
                self._lock_file = None
                self._lock_fd = None
            return True
        except Exception as e:
            logger.error(f"Error releasing lock: {e}")
            return False
    
    def create_backup(self) -> Optional[Path]:
        """
        Create backup of current knowledge graph.
        
        Returns:
            Path to backup file or None on failure
        """
        try:
            if not self.graph_path.exists():
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.graph_path.parent / f"{self.graph_path.name}.backup.{timestamp}"
            
            content = self.graph_path.read_text()
            backup_path.write_text(content)
            
            logger.info(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    def restore_from_backup(self, backup_path: Path) -> bool:
        """
        Restore knowledge graph from backup.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if restore successful
        """
        try:
            if not backup_path.exists():
                logger.error(f"Backup not found: {backup_path}")
                return False
            
            content = backup_path.read_text()
            self.graph_path.write_text(content)
            
            logger.info(f"Restored from backup: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            return False
    
    def extract_patterns(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract patterns from execution context.
        
        Args:
            context: Execution context with metrics
            
        Returns:
            List of 3-5 pattern dictionaries
        """
        return PatternExtractor.extract_from_context(context)
    
    def update_knowledge_graph(self, context: Dict[str, Any]) -> UpdateResult:
        """
        Update knowledge graph with patterns from execution context.
        
        Workflow:
        1. Acquire lock
        2. Create backup
        3. Load current graph
        4. Extract and add new patterns (deduplicate)
        5. Write updated graph
        6. Release lock
        7. Rollback on failure
        
        Args:
            context: Execution context with execution metrics
            
        Returns:
            UpdateResult with success status and metrics
        """
        backup_path = None
        patterns_added = 0
        duplicates_skipped = 0
        
        try:
            # Acquire lock
            if not self.acquire_lock():
                return UpdateResult(
                    success=False,
                    patterns_added=0,
                    duplicates_skipped=0,
                    error_message="Could not acquire file lock"
                )
            
            # Create backup
            backup_path = self.create_backup()
            
            # Load current graph
            if self.graph_path.exists():
                content = self.graph_path.read_text()
                graph_data = yaml.safe_load(content) or {}
            else:
                graph_data = {'patterns': [], 'relationships': [], 'metadata': {}}
            
            # Extract new patterns
            new_patterns = self.extract_patterns(context)
            
            # Get existing pattern names for deduplication
            existing_patterns = graph_data.get('patterns', [])
            existing_names = {p.get('name') for p in existing_patterns if isinstance(p, dict)}
            
            # Add new patterns (deduplicate)
            for pattern in new_patterns:
                if pattern['name'] not in existing_names:
                    graph_data['patterns'].append({
                        'name': pattern['name'],
                        'description': pattern['description'],
                        'confidence': pattern['confidence'],
                        'added_date': datetime.now().isoformat()
                    })
                    patterns_added += 1
                else:
                    duplicates_skipped += 1
            
            # Update metadata
            graph_data['metadata'] = graph_data.get('metadata', {})
            graph_data['metadata']['last_updated'] = datetime.now().isoformat()
            graph_data['metadata']['version'] = graph_data.get('metadata', {}).get('version', '1.0')
            
            # Write updated graph
            with open(self.graph_path, 'w') as f:
                yaml.safe_dump(graph_data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(f"✅ Knowledge graph updated: {patterns_added} patterns added, {duplicates_skipped} duplicates skipped")
            
            return UpdateResult(
                success=True,
                patterns_added=patterns_added,
                duplicates_skipped=duplicates_skipped,
                backup_path=backup_path
            )
            
        except Exception as e:
            logger.error(f"❌ Knowledge graph update failed: {e}")
            
            # Rollback on failure
            if backup_path and backup_path.exists():
                self.restore_from_backup(backup_path)
            
            return UpdateResult(
                success=False,
                patterns_added=0,
                duplicates_skipped=0,
                backup_path=backup_path,
                error_message=str(e)
            )
            
        finally:
            # Always release lock
            self.release_lock()
