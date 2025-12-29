"""
Cleanup Orchestrator - File organization and reference updates.

Organizes files into proper cortex-brain/documents/{category}/ structure
and updates references across the codebase.

Integration:
- BaseOrchestrator: Phase management, error handling, lifecycle
- MaintenanceOrchestrator: Phase 3 of 7-phase maintenance workflow

Copyright © 2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging
import re
import shutil
from datetime import datetime

from src.orchestration_4_0.base.base_orchestrator import BaseOrchestrator

logger = logging.getLogger(__name__)


@dataclass
class CleanupResult:
    """Results of cleanup operation."""
    success: bool
    data: Dict[str, Any]
    message: str = ""
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class CleanupOrchestrator(BaseOrchestrator):
    """
    Orchestrate file organization and cleanup operations.
    
    Phases:
    1. scan - Identify misplaced files
    2. categorize - Determine correct category for each file
    3. organize - Move files to proper locations
    4. update_references - Update links and imports
    5. finalization - Generate summary report
    """
    
    def __init__(self, project_root: Path = None):
        """
        Initialize cleanup orchestrator.
        
        Args:
            project_root: Root path of CORTEX project
        """
        super().__init__(name="cleanup", logger=logger)
        
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.cortex_brain = self.project_root / "cortex-brain"
        self.documents = self.cortex_brain / "documents"
        
        # Valid document categories
        self.categories = [
            "reports", "analysis", "summaries", "investigations",
            "planning", "implementation-guides", "diagrams",
            "conversation-captures", "archive"
        ]
        
        # Metrics tracking
        self.metrics = {
            'files_moved': 0,
            'references_updated': 0,
            'duplicates_detected': 0,
            'backup_path': None,
            'files_scanned': 0,
            'dry_run': True,
            'errors': []
        }
        
        # Files to skip (never move)
        self.protected_files = {
            'README.md', 'LICENSE', 'CONTRIBUTING.md', '.gitignore',
            'requirements.txt', 'setup.py', 'pyproject.toml'
        }
        
    def _setup(self, context: Dict[str, Any]) -> None:
        """Initialize orchestrator resources."""
        self.logger.info("🎭 Orchestrator engaged: CleanupOrchestrator")
        self.logger.info(f"Project root: {self.project_root}")
        self.metrics['dry_run'] = context.get('dry_run', True)
        
    def _register_phases(self) -> None:
        """Register cleanup phases."""
        self.phase_manager.register_phase("scan", "Scan for misplaced files", required=True)
        self.phase_manager.register_phase("categorize", "Categorize files by content", required=True)
        self.phase_manager.register_phase("organize", "Move files to correct locations", required=True)
        self.phase_manager.register_phase("update_references", "Update file references", required=False)
        self.phase_manager.register_phase("finalization", "Generate summary report", required=True)
        
    def _execute_phase(self, phase_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single cleanup phase.
        
        Args:
            phase_name: Name of phase to execute
            context: Phase execution context
            
        Returns:
            Phase result dictionary
        """
        if phase_name == "scan":
            return self._run_scan_phase(context)
        elif phase_name == "categorize":
            return self._run_categorize_phase(context)
        elif phase_name == "organize":
            return self._run_organize_phase(context)
        elif phase_name == "update_references":
            return self._run_update_references_phase(context)
        elif phase_name == "finalization":
            return self._run_finalization_phase(context)
        else:
            return {'success': False, 'error': f"Unknown phase: {phase_name}"}
            
    def _teardown(self, context: Dict[str, Any]) -> None:
        """Cleanup orchestrator resources."""
        self.logger.info("🎭 Orchestrator completing: CleanupOrchestrator")
        self.logger.info(f"Files moved: {self.metrics['files_moved']}")
        
    # ========================================================================
    # Phase Implementations
    # ========================================================================
    
    def _run_scan_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scan for misplaced files in repository root and cortex-brain root.
        
        Args:
            context: Phase context
            
        Returns:
            Phase result with misplaced files list
        """
        self.logger.info("🎭 Phase transition: START → scan")
        
        misplaced_files = []
        
        try:
            # Scan repository root for markdown files (except protected)
            for file_path in self.project_root.glob("*.md"):
                if file_path.name not in self.protected_files:
                    misplaced_files.append(file_path)
                    self.metrics['files_scanned'] += 1
                    
            # Scan cortex-brain root for markdown files
            if self.cortex_brain.exists():
                for file_path in self.cortex_brain.glob("*.md"):
                    if file_path.name not in self.protected_files:
                        misplaced_files.append(file_path)
                        self.metrics['files_scanned'] += 1
                        
            self.logger.info(f"✅ Found {len(misplaced_files)} misplaced files")
            
            # Store for next phase
            context['misplaced_files'] = misplaced_files
            
            return {
                'success': True,
                'misplaced_files': len(misplaced_files),
                'files_scanned': self.metrics['files_scanned'],
                'skipped': False
            }
            
        except Exception as e:
            error_msg = f"Scan phase failed: {e}"
            self.logger.warning(error_msg)
            self.metrics['errors'].append(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'skipped': False
            }
            
    def _run_categorize_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Categorize files based on filename patterns and content.
        
        Args:
            context: Phase context with misplaced_files list
            
        Returns:
            Phase result with categorization map
        """
        self.logger.info("🎭 Phase transition: scan → categorize")
        
        misplaced_files = context.get('misplaced_files', [])
        categorization_map = {}
        
        try:
            for file_path in misplaced_files:
                category = self._determine_category(file_path)
                categorization_map[str(file_path)] = category
                self.logger.debug(f"Categorized {file_path.name} → {category}")
                
            self.logger.info(f"✅ Categorized {len(categorization_map)} files")
            
            # Store for next phase
            context['categorization_map'] = categorization_map
            
            return {
                'success': True,
                'files_categorized': len(categorization_map),
                'categories_used': list(set(categorization_map.values())),
                'skipped': False
            }
            
        except Exception as e:
            error_msg = f"Categorization phase failed: {e}"
            self.logger.warning(error_msg)
            self.metrics['errors'].append(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'skipped': False
            }
            
    def _run_organize_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Move files to their categorized locations.
        
        Args:
            context: Phase context with categorization_map
            
        Returns:
            Phase result with files moved count
        """
        self.logger.info("🎭 Phase transition: categorize → organize")
        
        categorization_map = context.get('categorization_map', {})
        dry_run = self.metrics['dry_run']
        files_moved = 0
        
        try:
            # Create backup if not dry run
            if not dry_run:
                backup_dir = self.project_root / "backups" / f"cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                backup_dir.mkdir(parents=True, exist_ok=True)
                self.metrics['backup_path'] = str(backup_dir)
                self.logger.info(f"Created backup at: {backup_dir}")
            
            for file_path_str, category in categorization_map.items():
                file_path = Path(file_path_str)
                
                if not file_path.exists():
                    continue
                    
                # Determine destination
                dest_dir = self.documents / category
                dest_path = dest_dir / file_path.name
                
                # Handle duplicates
                if dest_path.exists():
                    self.metrics['duplicates_detected'] += 1
                    base = dest_path.stem
                    suffix = dest_path.suffix
                    counter = 1
                    while dest_path.exists():
                        dest_path = dest_dir / f"{base}_{counter}{suffix}"
                        counter += 1
                    self.logger.warning(f"Duplicate found, renaming to: {dest_path.name}")
                
                if dry_run:
                    self.logger.info(f"[DRY RUN] Would move: {file_path} → {dest_path}")
                else:
                    # Create backup
                    backup_path = Path(self.metrics['backup_path']) / file_path.name
                    shutil.copy2(file_path, backup_path)
                    
                    # Create destination directory
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Move file
                    shutil.move(str(file_path), str(dest_path))
                    self.logger.info(f"✅ Moved: {file_path.name} → {category}/")
                    
                files_moved += 1
                
            self.metrics['files_moved'] = files_moved
            
            return {
                'success': True,
                'files_moved': files_moved,
                'duplicates_detected': self.metrics['duplicates_detected'],
                'backup_path': self.metrics['backup_path'],
                'skipped': False
            }
            
        except Exception as e:
            error_msg = f"Organize phase failed: {e}"
            self.logger.warning(error_msg)
            self.metrics['errors'].append(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'skipped': False
            }
            
    def _run_update_references_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update file references in markdown files after moves.
        
        Args:
            context: Phase context
            
        Returns:
            Phase result with references updated count
        """
        self.logger.info("🎭 Phase transition: organize → update_references")
        
        # Skip reference updates for now (complex operation)
        # Future enhancement: Parse markdown files, find broken links, update paths
        
        self.logger.info("✅ Reference updates skipped (manual review recommended)")
        
        return {
            'success': True,
            'references_updated': 0,
            'skipped': True,
            'reason': 'Reference updates require manual review'
        }
        
    def _run_finalization_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary report and finalize cleanup.
        
        Args:
            context: Phase context
            
        Returns:
            Phase result with summary
        """
        self.logger.info("🎭 Phase transition: update_references → finalization")
        
        summary = {
            'files_scanned': self.metrics['files_scanned'],
            'files_moved': self.metrics['files_moved'],
            'duplicates_detected': self.metrics['duplicates_detected'],
            'references_updated': self.metrics['references_updated'],
            'backup_path': self.metrics['backup_path'],
            'dry_run': self.metrics['dry_run'],
            'errors': self.metrics['errors']
        }
        
        self.logger.info("=" * 60)
        self.logger.info("CLEANUP SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Files scanned: {summary['files_scanned']}")
        self.logger.info(f"Files moved: {summary['files_moved']}")
        self.logger.info(f"Duplicates detected: {summary['duplicates_detected']}")
        self.logger.info(f"References updated: {summary['references_updated']}")
        if summary['backup_path']:
            self.logger.info(f"Backup location: {summary['backup_path']}")
        if summary['dry_run']:
            self.logger.info("Mode: DRY RUN (no files actually moved)")
        if summary['errors']:
            self.logger.warning(f"Errors: {len(summary['errors'])}")
        self.logger.info("=" * 60)
        
        return {
            'success': True,
            'summary': summary,
            'skipped': False
        }
        
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _determine_category(self, file_path: Path) -> str:
        """
        Determine appropriate category for a file based on name and content.
        
        Args:
            file_path: Path to file
            
        Returns:
            Category name
        """
        filename = file_path.name.lower()
        
        # Pattern-based categorization
        if any(pattern in filename for pattern in ['report', 'status', 'completion', 'result']):
            return 'reports'
        elif any(pattern in filename for pattern in ['analysis', 'review', 'audit']):
            return 'analysis'
        elif any(pattern in filename for pattern in ['summary', 'overview']):
            return 'summaries'
        elif any(pattern in filename for pattern in ['investigation', 'bug', 'issue']):
            return 'investigations'
        elif any(pattern in filename for pattern in ['plan', 'roadmap', 'milestone']):
            return 'planning'
        elif any(pattern in filename for pattern in ['guide', 'howto', 'tutorial']):
            return 'implementation-guides'
        elif any(pattern in filename for pattern in ['diagram', 'architecture', 'flow']):
            return 'diagrams'
        elif any(pattern in filename for pattern in ['conversation', 'chat', 'discussion']):
            return 'conversation-captures'
        else:
            # Default to archive for unknown files
            return 'archive'
            
    def execute(self, context: Dict[str, Any] = None) -> CleanupResult:
        """
        Execute full cleanup operation.
        
        Args:
            context: Optional execution context with dry_run flag
            
        Returns:
            CleanupResult with success status and metrics
        """
        context = context or {}
        
        try:
            # Execute all phases using BaseOrchestrator
            result = super().execute(context)
            
            return CleanupResult(
                success=result.get('success', False),
                data={
                    'files_moved': self.metrics['files_moved'],
                    'references_updated': self.metrics['references_updated'],
                    'duplicates_detected': self.metrics['duplicates_detected'],
                    'backup_path': self.metrics['backup_path']
                },
                message=result.get('message', ''),
                errors=self.metrics['errors']
            )
            
        except Exception as e:
            self.logger.error(f"Cleanup operation failed: {e}", exc_info=True)
            return CleanupResult(
                success=False,
                data={},
                message=f"Cleanup operation failed: {e}",
                errors=[str(e)]
            )
