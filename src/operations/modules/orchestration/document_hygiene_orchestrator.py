"""
Document Hygiene Engine - Automatic Markdown maintenance and organization.

Integrated into Planning System 3.0 for automatic documentation
cleanup during Tier 3/4 operations.

Copyright © 2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, List, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import re
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..version.version_manager import get_version_manager

logger = logging.getLogger(__name__)


@dataclass
class HygieneResult:
    """Results of hygiene operation."""
    phase: str
    files_processed: int
    actions_taken: int
    recommendations: List[str]


class DocumentHygieneOrchestrator:
    """Orchestrate automatic documentation maintenance."""
    
    def __init__(self, project_root: Path = None):
        """Initialize document hygiene orchestrator."""
        self.project_root = project_root or Path.cwd()
        self.docs_brain = self.project_root / "cortex-brain" / "documents"
        
        # Version management
        self.version_manager = get_version_manager()
        self.version_manager.register_orchestrator_version("document_hygiene_orchestrator", "1.0")
        self.version = self.version_manager.get_orchestrator_version("document_hygiene_orchestrator")
        
        self.phases = [
            "consolidation",
            "archiving",
            "filename_optimization",
            "reference_updating",
            "reorganization",
            "finalization"
        ]
        
        self.metrics = {
            'phases_completed': [],
            'files_processed': 0,
            'actions_taken': 0,
            'recommendations': [],
            'errors': []
        }
        
        self.max_workers = 4
        
    async def execute(
        self,
        target_dirs: List[Path] = None,
        phases: List[str] = None
    ) -> Dict[str, Any]:
        """Execute document hygiene cycle."""
        logger.info(f"🎭 Orchestrator engaged: DocumentHygieneOrchestrator v{self.version}")
        
        phases = phases or self.phases
        target_dirs = target_dirs or [self.docs_brain]
        
        results = []
        
        try:
            if "consolidation" in phases:
                logger.info("🎭 Phase transition: START → consolidation")
                consolidation_result = await self._run_consolidation_phase(target_dirs)
                results.append(consolidation_result)
                self.metrics['phases_completed'].append('consolidation')
                
            if "archiving" in phases:
                logger.info("🎭 Phase transition: consolidation → archiving")
                archive_result = await self._run_archiving_phase(target_dirs)
                results.append(archive_result)
                self.metrics['phases_completed'].append('archiving')
                
            if "filename_optimization" in phases:
                logger.info("🎭 Phase transition: archiving → filename_optimization")
                filename_result = await self._run_filename_optimization_phase(target_dirs)
                results.append(filename_result)
                self.metrics['phases_completed'].append('filename_optimization')
                
            if "reference_updating" in phases:
                logger.info("🎭 Phase transition: filename_optimization → reference_updating")
                reference_result = await self._run_reference_updating_phase()
                results.append(reference_result)
                self.metrics['phases_completed'].append('reference_updating')
                
            if "reorganization" in phases:
                logger.info("🎭 Phase transition: reference_updating → reorganization")
                reorg_result = await self._run_reorganization_phase(target_dirs)
                results.append(reorg_result)
                self.metrics['phases_completed'].append('reorganization')
                
            logger.info("🎭 Phase transition: reorganization → finalization")
            self._finalize_hygiene(results)
            self.metrics['phases_completed'].append('finalization')
            
            success = True
            is_complete = success and len(self.metrics['errors']) == 0
            
            logger.info(
                f"🎭 Orchestrator completing: "
                f"{'✅ ALL WORK COMPLETE' if is_complete else '⏳ PHASES DONE WITH WARNINGS'}"
            )
            
            return {
                'success': success,
                'results': results,
                'metrics': self.metrics,
                'is_complete': is_complete
            }
            
        except Exception as e:
            logger.error(f"Document hygiene failed: {e}", exc_info=True)
            self.metrics['errors'].append(str(e))
            return {
                'success': False,
                'error': str(e),
                'metrics': self.metrics,
                'is_complete': False
            }
            
    async def _run_consolidation_phase(self, dirs: List[Path]) -> HygieneResult:
        """Phase 1: Consolidate similar MD files."""
        logger.info(f"Consolidating documents in {len(dirs)} directories")
        
        all_files = []
        for dir in dirs:
            if dir.exists():
                all_files.extend(list(dir.rglob("*.md")))
                
        similar_groups = self._find_similar_documents(all_files)
        
        actions = len(similar_groups)
        recommendations = [f"Consolidate group: {len(group)} files" for group in similar_groups]
        
        self.metrics['files_processed'] += len(all_files)
        self.metrics['actions_taken'] += actions
        
        return HygieneResult(
            phase="consolidation",
            files_processed=len(all_files),
            actions_taken=actions,
            recommendations=recommendations[:5]
        )
    
    def _find_similar_documents(self, files: List[Path]) -> List[List[Path]]:
        """Find groups of similar documents."""
        # Stub - would use content similarity analysis
        return []
        
    async def _run_archiving_phase(self, dirs: List[Path]) -> HygieneResult:
        """Phase 2: Archive outdated planning artifacts."""
        logger.info("Archiving outdated documents")
        
        cutoff_date = datetime.now() - timedelta(days=90)
        outdated_files = []
        
        for dir in dirs:
            planning_dir = dir / "planning"
            if planning_dir.exists():
                for file in planning_dir.rglob("*.md"):
                    mtime = datetime.fromtimestamp(file.stat().st_mtime)
                    if mtime < cutoff_date and not self._is_active_plan(file):
                        outdated_files.append(file)
                        
        actions = len(outdated_files)
        recommendations = [f"Archive: {file.name}" for file in outdated_files[:5]]
        
        self.metrics['actions_taken'] += actions
        
        return HygieneResult(
            phase="archiving",
            files_processed=len(outdated_files),
            actions_taken=actions,
            recommendations=recommendations
        )
    
    def _is_active_plan(self, file: Path) -> bool:
        """Check if plan is currently active."""
        # Stub - would check status markers
        return False
        
    async def _run_filename_optimization_phase(self, dirs: List[Path]) -> HygieneResult:
        """Phase 3: Optimize filenames."""
        logger.info("Optimizing filenames")
        
        long_filenames = []
        for dir in dirs:
            if dir.exists():
                for file in dir.rglob("*.md"):
                    if len(file.stem) > 50:
                        long_filenames.append(file)
                        
        actions = len(long_filenames)
        recommendations = [
            f"Shorten: {file.name} ({len(file.stem)} chars)" 
            for file in long_filenames[:5]
        ]
        
        self.metrics['actions_taken'] += actions
        
        return HygieneResult(
            phase="filename_optimization",
            files_processed=len(long_filenames),
            actions_taken=actions,
            recommendations=recommendations
        )
        
    async def _run_reference_updating_phase(self) -> HygieneResult:
        """Phase 4: Update file references after renames."""
        logger.info("Updating file references")
        
        # Stub - would scan for broken links
        return HygieneResult(
            phase="reference_updating",
            files_processed=0,
            actions_taken=0,
            recommendations=[]
        )
        
    async def _run_reorganization_phase(self, dirs: List[Path]) -> HygieneResult:
        """Phase 5: Generate reorganization recommendations."""
        logger.info("Analyzing document organization")
        
        recommendations = [
            "Consider creating subdirectories for large categories",
            "Archive completed planning documents to archive/"
        ]
        
        self.metrics['recommendations'].extend(recommendations)
        
        return HygieneResult(
            phase="reorganization",
            files_processed=0,
            actions_taken=0,
            recommendations=recommendations
        )
        
    def _finalize_hygiene(self, results: List[HygieneResult]):
        """Phase 6: Finalize hygiene cycle."""
        total_files = sum(r.files_processed for r in results)
        total_actions = sum(r.actions_taken for r in results)
        
        logger.info(f"Document hygiene complete: {total_files} files, {total_actions} actions")


def run_document_hygiene(
    project_root: Path = None,
    target_dirs: List[Path] = None,
    phases: List[str] = None
) -> Dict[str, Any]:
    """Synchronous wrapper for document hygiene."""
    orchestrator = DocumentHygieneOrchestrator(project_root)
    return asyncio.run(orchestrator.execute(target_dirs, phases))
