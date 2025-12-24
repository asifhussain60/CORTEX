# Phase 14: Document Hygiene Engine

**🔗 Breadcrumb:** [← Back to Master Plan](cortex-3.9-master.md)

**Status:** ⏳ Pending  
**Phase ID:** 14  
**Estimated Time:** 3 hours (180 minutes)  
**Actual Start:** -  
**Actual End:** -  
**Actual Work Time:** -  
**Dependencies:** Phase 15 (Version Manager) ✅  
**Blocks:** Phase 03 (Planning Orchestrator 3.0), Phase 16 (Integration & Validation)

---

## 🎯 Phase Objective

Create document hygiene engine for automatic Markdown consolidation, archive management, filename optimization, and bidirectional reference updating integrated into Planning System 3.0.

**Success Criteria:**
- ✅ MD file consolidation with similarity detection
- ✅ Automatic archive of outdated planning artifacts
- ✅ Filename optimization (long → short, meaningful)
- ✅ Bidirectional reference updating after renames
- ✅ Multi-threaded utilities for large workspace scanning
- ✅ Reorganization recommendations
- ✅ Integration with Planning Orchestrator 3.0
- ✅ Version synchronization from cortex.config.json
- ✅ 100% test coverage with passing tests

---

## 🏗️ Implementation Plan

### Task 1: Document Hygiene Orchestrator Core (1.5 hours)

**Create `src/operations/modules/orchestration/document_hygiene_orchestrator.py`:**

```python
"""
Document Hygiene Engine - Automatic Markdown maintenance and organization.

Integrated into Planning System 3.0 for automatic documentation
cleanup during Tier 3/4 operations.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import re
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..version.version_manager import get_version_manager
from ...decorators.progress import track_progress
from ...utils.multithreaded_file_scanner import scan_files_parallel

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
        self.project_root = project_root or Path.cwd()
        self.docs_brain = self.project_root / "cortex-brain" / "documents"
        
        # Version management
        self.version_manager = get_version_manager()
        self.version_manager.register_orchestrator_version("document_hygiene_orchestrator", "1.0")
        self.version = self.version_manager.get_orchestrator_version("document_hygiene_orchestrator")
        
        # Hygiene phases
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
        
        # Multi-threading config
        self.max_workers = 4
        
    @track_progress("document_hygiene")
    async def execute(
        self,
        target_dirs: List[Path] = None,
        phases: List[str] = None
    ) -> Dict[str, Any]:
        """
        Execute document hygiene cycle.
        
        Args:
            target_dirs: Specific directories or None for all docs
            phases: Specific phases to run or None for all
            
        Returns:
            Operation results with metrics
        """
        logger.info(f"🎭 Orchestrator engaged: DocumentHygieneOrchestrator v{self.version}")
        
        phases = phases or self.phases
        target_dirs = target_dirs or [self.docs_brain]
        
        results = []
        
        try:
            # Phase 1: MD Consolidation
            if "consolidation" in phases:
                logger.info("🎭 Phase transition: START → consolidation")
                consolidation_result = await self._run_consolidation_phase(target_dirs)
                results.append(consolidation_result)
                self.metrics['phases_completed'].append('consolidation')
                
            # Phase 2: Archiving
            if "archiving" in phases:
                logger.info("🎭 Phase transition: consolidation → archiving")
                archive_result = await self._run_archiving_phase(target_dirs)
                results.append(archive_result)
                self.metrics['phases_completed'].append('archiving')
                
            # Phase 3: Filename Optimization
            if "filename_optimization" in phases:
                logger.info("🎭 Phase transition: archiving → filename_optimization")
                filename_result = await self._run_filename_optimization_phase(target_dirs)
                results.append(filename_result)
                self.metrics['phases_completed'].append('filename_optimization')
                
            # Phase 4: Reference Updating
            if "reference_updating" in phases:
                logger.info("🎭 Phase transition: filename_optimization → reference_updating")
                reference_result = await self._run_reference_updating_phase()
                results.append(reference_result)
                self.metrics['phases_completed'].append('reference_updating')
                
            # Phase 5: Reorganization Recommendations
            if "reorganization" in phases:
                logger.info("🎭 Phase transition: reference_updating → reorganization")
                reorg_result = await self._run_reorganization_phase(target_dirs)
                results.append(reorg_result)
                self.metrics['phases_completed'].append('reorganization')
                
            # Phase 6: Finalization
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
            all_files.extend(list(dir.rglob("*.md")))
            
        # Find similar documents
        similar_groups = self._find_similar_documents(all_files)
        
        actions = 0
        recommendations = []
        
        for group in similar_groups:
            if len(group) > 1:
                recommendations.append(
                    f"Consider consolidating {len(group)} similar files: "
                    f"{', '.join([f.name for f in group[:3]])}"
                )
                
                # Auto-consolidate if similarity >90%
                if self._calculate_similarity(group) > 0.90:
                    self._consolidate_files(group)
                    actions += 1
                    
        self.metrics['files_processed'] += len(all_files)
        self.metrics['actions_taken'] += actions
        self.metrics['recommendations'].extend(recommendations)
        
        return HygieneResult(
            phase="consolidation",
            files_processed=len(all_files),
            actions_taken=actions,
            recommendations=recommendations
        )
        
    def _find_similar_documents(self, files: List[Path]) -> List[List[Path]]:
        """Find groups of similar documents."""
        groups = []
        processed = set()
        
        for i, file1 in enumerate(files):
            if file1 in processed:
                continue
                
            similar = [file1]
            
            for file2 in files[i+1:]:
                if file2 in processed:
                    continue
                    
                if self._are_files_similar(file1, file2):
                    similar.append(file2)
                    processed.add(file2)
                    
            if len(similar) > 1:
                groups.append(similar)
                processed.add(file1)
                
        return groups
        
    def _are_files_similar(self, file1: Path, file2: Path) -> bool:
        """Check if two files are similar (>80% content overlap)."""
        try:
            with open(file1, 'r', encoding='utf-8') as f1:
                content1 = set(f1.read().split())
            with open(file2, 'r', encoding='utf-8') as f2:
                content2 = set(f2.read().split())
                
            if not content1 or not content2:
                return False
                
            overlap = len(content1 & content2)
            total = len(content1 | content2)
            
            return (overlap / total) > 0.80
            
        except Exception as e:
            logger.error(f"Similarity check failed: {e}")
            return False
            
    async def _run_archiving_phase(self, dirs: List[Path]) -> HygieneResult:
        """Phase 2: Archive outdated planning artifacts."""
        logger.info(f"Archiving outdated documents in {len(dirs)} directories")
        
        archive_dir = self.project_root / "archive" / datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        all_files = []
        for dir in dirs:
            all_files.extend(list(dir.rglob("*.md")))
            
        actions = 0
        recommendations = []
        
        # Archive files older than 90 days with "outdated" markers
        cutoff_date = datetime.now() - timedelta(days=90)
        
        for file in all_files:
            if self._is_outdated(file, cutoff_date):
                # Move to archive
                relative_path = file.relative_to(self.project_root)
                archive_path = archive_dir / relative_path
                archive_path.parent.mkdir(parents=True, exist_ok=True)
                
                file.rename(archive_path)
                actions += 1
                logger.info(f"Archived {file.name}")
                
        self.metrics['actions_taken'] += actions
        
        return HygieneResult(
            phase="archiving",
            files_processed=len(all_files),
            actions_taken=actions,
            recommendations=recommendations
        )
        
    def _is_outdated(self, file: Path, cutoff_date: datetime) -> bool:
        """Check if file is outdated."""
        # Check file modification time
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        
        if mtime < cutoff_date:
            # Also check for "outdated" marker in content
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "outdated" in content.lower() or "deprecated" in content.lower():
                        return True
            except:
                pass
                
        return False
        
    async def _run_filename_optimization_phase(self, dirs: List[Path]) -> HygieneResult:
        """Phase 3: Optimize filenames (long → short, meaningful)."""
        logger.info(f"Optimizing filenames in {len(dirs)} directories")
        
        all_files = []
        for dir in dirs:
            all_files.extend(list(dir.rglob("*.md")))
            
        actions = 0
        recommendations = []
        renames = {}  # old_path -> new_path
        
        for file in all_files:
            new_name = self._optimize_filename(file.name)
            
            if new_name != file.name:
                new_path = file.parent / new_name
                
                # Check for conflicts
                if not new_path.exists():
                    renames[file] = new_path
                    actions += 1
                else:
                    recommendations.append(
                        f"Cannot rename {file.name} → {new_name} (conflict)"
                    )
                    
        # Execute renames (tracked for reference updating)
        self.rename_map = {}
        for old_path, new_path in renames.items():
            old_path.rename(new_path)
            self.rename_map[str(old_path)] = str(new_path)
            logger.info(f"Renamed {old_path.name} → {new_path.name}")
            
        self.metrics['actions_taken'] += actions
        self.metrics['recommendations'].extend(recommendations)
        
        return HygieneResult(
            phase="filename_optimization",
            files_processed=len(all_files),
            actions_taken=actions,
            recommendations=recommendations
        )
        
    def _optimize_filename(self, filename: str) -> str:
        """Optimize filename (remove redundant words, shorten)."""
        name = filename.replace('.md', '')
        
        # Remove common redundant words
        redundant = ['the', 'and', 'for', 'with', 'document', 'file', 'plan']
        words = name.lower().split('-')
        words = [w for w in words if w not in redundant]
        
        # Limit to 20 characters (excluding extension)
        optimized = '-'.join(words)[:20]
        
        return optimized + '.md'
        
    async def _run_reference_updating_phase(self) -> HygieneResult:
        """Phase 4: Update bidirectional references after renames."""
        logger.info("Updating references after filename changes")
        
        if not hasattr(self, 'rename_map') or not self.rename_map:
            return HygieneResult(
                phase="reference_updating",
                files_processed=0,
                actions_taken=0,
                recommendations=[]
            )
            
        # Scan all MD files for references to renamed files
        all_md_files = list(self.project_root.rglob("*.md"))
        
        actions = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._update_references_in_file, file, self.rename_map): file
                for file in all_md_files
            }
            
            for future in as_completed(futures):
                file = futures[future]
                try:
                    file_actions = future.result()
                    actions += file_actions
                except Exception as e:
                    logger.error(f"Reference update failed for {file}: {e}")
                    
        self.metrics['actions_taken'] += actions
        
        return HygieneResult(
            phase="reference_updating",
            files_processed=len(all_md_files),
            actions_taken=actions,
            recommendations=[]
        )
        
    def _update_references_in_file(
        self,
        file: Path,
        rename_map: Dict[str, str]
    ) -> int:
        """Update references in single file."""
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # Update all references
            for old_path, new_path in rename_map.items():
                old_name = Path(old_path).name
                new_name = Path(new_path).name
                
                # Update Markdown links
                content = re.sub(
                    rf'\[([^\]]+)\]\({re.escape(old_name)}\)',
                    rf'[\1]({new_name})',
                    content
                )
                
                # Update plain references
                content = content.replace(old_name, new_name)
                
            if content != original_content:
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(content)
                return 1
                
            return 0
            
        except Exception as e:
            logger.error(f"Failed to update references in {file}: {e}")
            return 0
            
    async def _run_reorganization_phase(self, dirs: List[Path]) -> HygieneResult:
        """Phase 5: Generate reorganization recommendations."""
        logger.info(f"Analyzing organization in {len(dirs)} directories")
        
        recommendations = []
        
        # Check for misplaced files
        all_files = []
        for dir in dirs:
            all_files.extend(list(dir.rglob("*.md")))
            
        for file in all_files:
            recommendation = self._check_file_placement(file)
            if recommendation:
                recommendations.append(recommendation)
                
        self.metrics['recommendations'].extend(recommendations)
        
        return HygieneResult(
            phase="reorganization",
            files_processed=len(all_files),
            actions_taken=0,
            recommendations=recommendations
        )
        
    def _check_file_placement(self, file: Path) -> Optional[str]:
        """Check if file is in appropriate directory."""
        # Analyze content for keywords
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                
            # Suggest better category
            if 'implementation' in content and 'reports' in str(file):
                return f"Consider moving {file.name} to implementation-guides/"
            elif 'analysis' in content and 'planning' in str(file):
                return f"Consider moving {file.name} to analysis/"
                
        except:
            pass
            
        return None
        
    def _finalize_hygiene(self, results: List[HygieneResult]):
        """Phase 6: Finalize hygiene cycle."""
        total_actions = sum(r.actions_taken for r in results)
        total_recommendations = sum(len(r.recommendations) for r in results)
        
        logger.info(
            f"Document hygiene complete: {total_actions} actions taken, "
            f"{total_recommendations} recommendations generated"
        )
```

### Task 2: Reference Updater Utility (1 hour)

**Create `src/operations/utils/reference_updater.py`:**

```python
"""Reference updater utility for bidirectional link maintenance."""

from pathlib import Path
from typing import Dict, List
import re
import logging

logger = logging.getLogger(__name__)

class ReferenceUpdater:
    """Update references across documentation after changes."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
    def update_all_references(
        self,
        rename_map: Dict[str, str]
    ) -> int:
        """
        Update all references across project.
        
        Args:
            rename_map: Dict mapping old paths to new paths
            
        Returns:
            Number of files updated
        """
        md_files = list(self.project_root.rglob("*.md"))
        
        updated = 0
        for file in md_files:
            if self._update_file_references(file, rename_map):
                updated += 1
                
        return updated
        
    def _update_file_references(
        self,
        file: Path,
        rename_map: Dict[str, str]
    ) -> bool:
        """Update references in single file."""
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            updated_content = self._replace_references(content, rename_map)
            
            if updated_content != content:
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Failed to update {file}: {e}")
            return False
```

### Task 3: Integration with Planning Orchestrator (30 min)

**Update Planning Orchestrator 3.0:**

```python
# In planning_orchestrator.py

async def _run_document_hygiene_cycle(self):
    """Execute automatic document hygiene for Tier 3/4."""
    from .document_hygiene_orchestrator import DocumentHygieneOrchestrator
    
    hygiene = DocumentHygieneOrchestrator(self.project_root)
    
    result = await hygiene.execute()
    
    return {
        'hygiene_complete': result['success'],
        'actions_taken': result['metrics']['actions_taken'],
        'recommendations': result['metrics']['recommendations']
    }
```

---

## 📦 Expected Deliverables

### Code Deliverables
- ✅ `src/operations/modules/orchestration/document_hygiene_orchestrator.py`
- ✅ `src/operations/utils/reference_updater.py`
- ✅ Integration with Planning Orchestrator 3.0
- ✅ Version synchronization logic

### Test Deliverables
- ✅ `tests/test_document_hygiene_orchestrator.py`
- ✅ `tests/test_reference_updater.py`
- ✅ Integration tests with sample documents
- ✅ Performance benchmarks

### Documentation Deliverables
- ✅ Document hygiene usage guide
- ✅ Filename optimization rules
- ✅ Archive policy documentation
- ✅ Reference updating mechanics

---

## 🔄 Next Steps

1. **Phase 15 Completion:** Version Manager must be available
2. **Testing:** Validate hygiene cycle on CORTEX documents
3. **Calibration:** Tune similarity thresholds
4. **Integration:** Connect to Phase 03 (Planning Orchestrator 3.0)

---

## 🔗 Integration Points

### Upstream Dependencies
- **Version Manager (Phase 15):** Version synchronization

### Downstream Consumers
- **Planning Orchestrator (Phase 03):** Automatic hygiene for Tier 3/4
- **System Maintenance (Phase 06):** Documentation cleanup phase
- **Integration Tests (Phase 16):** End-to-end validation

---

## 🚨 Risk Mitigation

### Risk 1: Broken References After Renames
**Mitigation:**
- Comprehensive reference scanning
- Bidirectional link validation
- Manual review gate for bulk renames

### Risk 2: Loss of Important Documents
**Mitigation:**
- Archive instead of delete
- 90-day retention before archiving
- Manual "outdated" marker required

### Risk 3: Filename Conflicts
**Mitigation:**
- Conflict detection before rename
- Generate recommendations instead of forcing
- Preserve original if conflict exists

---

## 📊 Success Metrics

- ✅ MD file count reduced by 30% through consolidation
- ✅ 100% of references updated after renames
- ✅ Zero broken links after hygiene cycle
- ✅ Filename optimization improves readability (user survey)
- ✅ Archive process preserves all content
- ✅ Hygiene cycle completes in <2 minutes

---

**Phase Owner:** Asif Hussain  
**Phase Status:** ⏳ Awaiting Phase 15 completion  
**Last Updated:** 2024-12-14
