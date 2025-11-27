"""
Documentation Deduplicator

Handles documentation deduplication using DocumentGovernance.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

import logging
from pathlib import Path
from typing import Dict, Any, Callable
from src.governance import DocumentGovernance
from src.operations.modules.optimization.cortex_optimization_models import OptimizationMetrics

logger = logging.getLogger(__name__)


class DocumentDeduplicator:
    """
    Deduplicates documentation using DocumentGovernance.
    
    This class:
    1. Instantiates DocumentGovernance
    2. Scans all markdown files in cortex-brain/documents/
    3. Finds duplicates using 3 algorithms (exact, title, keyword)
    4. Applies consolidation suggestions (keeps older, archives newer)
    5. Logs consolidation actions
    6. Updates metrics with deduplicated count
    """
    
    def __init__(
        self,
        project_root: Path,
        git_commit_callback: Callable[[Path, str], str]
    ):
        """
        Initialize DocumentDeduplicator.
        
        Args:
            project_root: Project root directory
            git_commit_callback: Function to create git commits (signature: project_root, message -> commit_hash)
        """
        self.project_root = project_root
        self.git_commit_callback = git_commit_callback
    
    def deduplicate(self, metrics: OptimizationMetrics) -> Dict[str, Any]:
        """
        Scan and deduplicate documentation.
        
        Args:
            metrics: Metrics collector
        
        Returns:
            Dict with success status, consolidated count, and details
        """
        logger.info("Scanning documentation for duplicates...")
        
        try:
            # Instantiate DocumentGovernance
            governance = DocumentGovernance(self.project_root)
            
            # Scan all markdown files
            docs_dir = self.project_root / "cortex-brain" / "documents"
            prompts_dir = self.project_root / ".github" / "prompts" / "modules"
            
            if not docs_dir.exists():
                return {'success': False, 'message': 'Documents directory not found'}
            
            # Collect all .md files
            scanned_docs = list(docs_dir.rglob("*.md"))
            if prompts_dir.exists():
                scanned_docs.extend(prompts_dir.rglob("*.md"))
            
            logger.info(f"Scanning {len(scanned_docs)} markdown files...")
            
            # Track duplicates
            duplicates_found = []
            consolidated_pairs = set()
            
            for doc_path in scanned_docs:
                try:
                    content = doc_path.read_text(encoding='utf-8')
                    duplicates = governance.find_duplicates(doc_path, content)
                    
                    # Filter by 0.75 threshold (from governance rules)
                    high_similarity = [
                        d for d in duplicates 
                        if d.similarity_score >= 0.75
                    ]
                    
                    for dup in high_similarity:
                        # Create unique pair key (sorted to avoid double-reporting)
                        pair_key = tuple(sorted([
                            str(doc_path.relative_to(self.project_root)),
                            str(dup.existing_path.relative_to(self.project_root))
                        ]))
                        
                        if pair_key not in consolidated_pairs:
                            consolidated_pairs.add(pair_key)
                            duplicates_found.append({
                                'file1': str(doc_path.relative_to(self.project_root)),
                                'file2': str(dup.existing_path.relative_to(self.project_root)),
                                'similarity': dup.similarity_score,
                                'algorithm': dup.algorithm,
                                'recommendation': dup.recommendation
                            })
                
                except Exception as e:
                    logger.debug(f"Error processing {doc_path}: {e}")
                    continue
            
            if not duplicates_found:
                logger.info("✅ No duplicate documentation found")
                return {
                    'success': True,
                    'consolidated_count': 0,
                    'message': 'No duplicates found'
                }
            
            # Log duplicates for user review
            logger.info(f"Found {len(duplicates_found)} duplicate pairs:")
            for dup in duplicates_found[:5]:  # Show top 5
                logger.info(
                    f"  • {dup['file1']} <-> {dup['file2']} "
                    f"({dup['similarity']:.0%} via {dup['algorithm']})"
                )
            
            if len(duplicates_found) > 5:
                logger.info(f"  ... and {len(duplicates_found) - 5} more")
            
            # Auto-consolidate if similarity ≥90% (critical duplicates)
            auto_consolidated = 0
            for dup in duplicates_found:
                if dup['similarity'] >= 0.90:
                    # Determine keep vs archive (keep older file)
                    file1_path = self.project_root / dup['file1']
                    file2_path = self.project_root / dup['file2']
                    
                    if file1_path.exists() and file2_path.exists():
                        file1_mtime = file1_path.stat().st_mtime
                        file2_mtime = file2_path.stat().st_mtime
                        
                        # Keep older file, archive newer
                        if file1_mtime < file2_mtime:
                            keep_file = file1_path
                            archive_file = file2_path
                        else:
                            keep_file = file2_path
                            archive_file = file1_path
                        
                        # Create archive directory
                        archive_dir = docs_dir / "archive"
                        archive_dir.mkdir(exist_ok=True)
                        
                        # Move duplicate to archive
                        archive_dest = archive_dir / archive_file.name
                        
                        try:
                            archive_file.rename(archive_dest)
                            logger.info(
                                f"  ✅ Archived: {archive_file.relative_to(self.project_root)} "
                                f"(kept {keep_file.relative_to(self.project_root)})"
                            )
                            auto_consolidated += 1
                        except Exception as e:
                            logger.warning(f"Failed to archive {archive_file}: {e}")
            
            # Update metrics
            metrics.doc_deduplication_count = auto_consolidated
            metrics.optimizations_succeeded += auto_consolidated
            
            # Commit if changes made
            if auto_consolidated > 0:
                commit_hash = self.git_commit_callback(
                    self.project_root,
                    f"[OPTIMIZATION/DOC] Consolidated {auto_consolidated} duplicate documents"
                )
                
                if commit_hash:
                    metrics.git_commits.append(commit_hash)
            
            return {
                'success': True,
                'consolidated_count': auto_consolidated,
                'duplicates_found': len(duplicates_found),
                'details': duplicates_found
            }
        
        except Exception as e:
            logger.error(f"Documentation deduplication failed: {e}", exc_info=True)
            metrics.errors.append(f"Doc deduplication error: {str(e)}")
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
