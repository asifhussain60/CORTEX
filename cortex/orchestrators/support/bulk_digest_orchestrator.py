"""
Bulk Digest Orchestrator - AC-BULK-DIGEST-001

Orchestrates bulk markdown file ingestion with intelligent routing and cleanup.

Key Features:
- Pattern-based file discovery (*.md)
- Exclusion patterns (docs/, README.md)
- Confidence-based filtering (min_confidence)
- Parallel processing support
- Safe deletion after successful ingestion
- Dry-run mode for validation
- Detailed progress reporting

CORE Compliance:
- CORE-002: Prevents markdown bloat via ingestion + deletion
- CORE-011: Type hints (mypy --strict)
- CORE-012: Google-style docstrings
- CORE-013: Specific exceptions
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import time
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from cortex.orchestrators.support.digest_session_orchestrator import (
    DigestSessionOrchestrator,
    DigestResult
)
from cortex.orchestrators.response.ascii_progress_bar import ASCIIProgressBar

logger = logging.getLogger(__name__)


@dataclass
class BulkDigestStats:
    """Statistics for bulk digest operation.
    
    Attributes:
        files_found: Total files matching pattern
        files_processed: Files successfully processed
        files_skipped: Files skipped (low confidence, excluded)
        files_deleted: Files deleted after ingestion
        files_failed: Files that failed processing
        total_enhancements: Total enhancements extracted
        processing_time_seconds: Total processing time
        files_by_category: Breakdown by file category
    """
    files_found: int = 0
    files_processed: int = 0
    files_skipped: int = 0
    files_deleted: int = 0
    files_failed: int = 0
    files_excluded: int = 0
    total_enhancements: int = 0
    processing_time_seconds: float = 0.0
    files_by_category: Dict[str, int] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


@dataclass
class FileProcessingResult:
    """Result of processing a single file.
    
    Attributes:
        file_path: Path to processed file
        success: Whether processing succeeded
        digest_result: DigestResult from orchestrator
        deleted: Whether file was deleted
        skipped: Whether file was skipped
        skip_reason: Reason for skipping
        error_message: Error message if failed
    """
    file_path: str
    success: bool
    digest_result: Optional[DigestResult] = None
    deleted: bool = False
    skipped: bool = False
    skip_reason: str = ""
    error_message: str = ""


class BulkDigestOrchestrator:
    """Orchestrates bulk markdown file ingestion.
    
    Coordinates DigestSessionOrchestrator for batch processing with
    intelligent filtering, parallel execution, and safe cleanup.
    
    Attributes:
        digest_orchestrator: DigestSessionOrchestrator instance
        default_exclude_patterns: Default patterns to exclude
    """
    
    # Default exclusions
    DEFAULT_EXCLUDE_PATTERNS = [
        "docs/**",
        "README.md",
        ".github/**",
        "node_modules/**",
        "venv/**",
        ".venv/**",
    ]
    
    def __init__(self) -> None:
        """Initialize bulk digest orchestrator."""
        self.digest_orchestrator = DigestSessionOrchestrator()
        self.progress_bar = ASCIIProgressBar()
        
        # Enable bulk mode to skip history writes (performance optimization)
        self.digest_orchestrator._skip_history_write = True
    
    def process_directory(
        self,
        directory: str = ".",
        pattern: str = "*.md",
        exclude_patterns: Optional[List[str]] = None,
        min_confidence: float = 5.0,
        auto_delete: bool = True,
        dry_run: bool = False,
        parallel: bool = False,
        max_workers: int = 4,
        continue_on_error: bool = True
    ) -> Dict[str, Any]:
        """Process all markdown files in directory.
        
        Args:
            directory: Directory to scan
            pattern: Glob pattern for file matching
            exclude_patterns: Patterns to exclude (added to defaults)
            min_confidence: Minimum confidence score (0-10)
            auto_delete: Delete files after successful ingestion
            dry_run: Simulate without deleting files
            parallel: Enable parallel processing
            max_workers: Max parallel workers
            continue_on_error: Continue processing on errors
            
        Returns:
            Dictionary with processing statistics and results
            
        Example:
            >>> orchestrator = BulkDigestOrchestrator()
            >>> result = orchestrator.process_directory(
            ...     directory=".",
            ...     pattern="*.md",
            ...     auto_delete=True,
            ...     dry_run=False
            ... )
            >>> print(f"Processed {result['files_processed']} files")
        """
        start_time = time.time()
        stats = BulkDigestStats()
        
        # Merge exclude patterns
        exclude = self.DEFAULT_EXCLUDE_PATTERNS.copy()
        if exclude_patterns:
            exclude.extend(exclude_patterns)
        
        try:
            # Find files
            directory_path = Path(directory).resolve()
            all_files = list(directory_path.glob(pattern))
            stats.files_found = len(all_files)
            
            logger.info(f"Found {stats.files_found} files matching '{pattern}'")
            
            # Filter files
            files_to_process = self._filter_files(all_files, exclude, stats)
            
            logger.info(f"Processing {len(files_to_process)} files after filtering")
            
            # Process files
            if parallel and len(files_to_process) > 1:
                results = self._process_parallel(
                    files_to_process,
                    min_confidence,
                    auto_delete,
                    dry_run,
                    max_workers,
                    continue_on_error
                )
            else:
                results = self._process_sequential(
                    files_to_process,
                    min_confidence,
                    auto_delete,
                    dry_run,
                    continue_on_error
                )
            
            # Aggregate results
            self._aggregate_results(results, stats)
            
            stats.processing_time_seconds = time.time() - start_time
            
            return {
                "success": True,
                "files_found": stats.files_found,
                "files_processed": stats.files_processed,
                "files_skipped": stats.files_skipped,
                "files_excluded": stats.files_excluded,
                "files_deleted": stats.files_deleted,
                "files_failed": stats.files_failed,
                "total_enhancements": stats.total_enhancements,
                "processing_time_seconds": round(stats.processing_time_seconds, 2),
                "files_by_category": stats.files_by_category,
                "dry_run": dry_run,
                "parallel": parallel,
                "errors": stats.errors[:10]  # Limit errors in response
            }
            
        except Exception as e:
            logger.error(f"Bulk digest failed: {e}")
            return {
                "success": False,
                "error_message": str(e),
                "files_found": stats.files_found,
                "files_processed": stats.files_processed,
                "processing_time_seconds": time.time() - start_time
            }
    
    def _filter_files(
        self,
        files: List[Path],
        exclude_patterns: List[str],
        stats: BulkDigestStats
    ) -> List[Path]:
        """Filter files based on exclusion patterns.
        
        Args:
            files: List of file paths
            exclude_patterns: Patterns to exclude
            stats: Statistics object to update
            
        Returns:
            Filtered list of files
        """
        filtered = []
        
        for file_path in files:
            if not file_path.is_file():
                continue
                
            relative_path = str(file_path.relative_to(Path.cwd()))
            
            if self._should_process(relative_path, exclude_patterns):
                filtered.append(file_path)
            else:
                stats.files_excluded += 1
                logger.debug(f"Excluded: {relative_path}")
        
        return filtered
    
    def _should_process(self, file_path: str, exclude_patterns: List[str]) -> bool:
        """Check if file should be processed.
        
        Args:
            file_path: Relative file path
            exclude_patterns: Patterns to exclude
            
        Returns:
            True if file should be processed
        """
        from fnmatch import fnmatch
        
        for pattern in exclude_patterns:
            if fnmatch(file_path, pattern):
                return False
        
        return True
    
    def _process_sequential(
        self,
        files: List[Path],
        min_confidence: float,
        auto_delete: bool,
        dry_run: bool,
        continue_on_error: bool
    ) -> List[FileProcessingResult]:
        """Process files sequentially.
        
        Args:
            files: List of file paths
            min_confidence: Minimum confidence threshold
            auto_delete: Delete after success
            dry_run: Simulate without deletion
            continue_on_error: Continue on errors
            
        Returns:
            List of processing results
        """
        results = []
        total_files = len(files)
        
        # Print header
        self._print_progress_header(total_files, dry_run)
        
        for idx, file_path in enumerate(files, 1):
            # Show progress bar
            progress = idx / total_files
            self._print_progress(idx, total_files, file_path.name, progress)
            
            result = self._process_single_file(
                file_path,
                min_confidence,
                auto_delete,
                dry_run
            )
            
            results.append(result)
            
            # Show result inline
            self._print_file_result(result, idx, total_files)
            
            if not result.success and not continue_on_error:
                logger.error(f"Stopping due to error: {result.error_message}")
                break
        
        # Print completion
        self._print_completion(results, total_files)
        
        return results
    
    def _process_parallel(
        self,
        files: List[Path],
        min_confidence: float,
        auto_delete: bool,
        dry_run: bool,
        max_workers: int,
        continue_on_error: bool
    ) -> List[FileProcessingResult]:
        """Process files in parallel.
        
        Args:
            files: List of file paths
            min_confidence: Minimum confidence threshold
            auto_delete: Delete after success
            dry_run: Simulate without deletion
            max_workers: Maximum parallel workers
            continue_on_error: Continue on errors
            
        Returns:
            List of processing results
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    self._process_single_file,
                    file_path,
                    min_confidence,
                    auto_delete,
                    dry_run
                ): file_path
                for file_path in files
            }
            
            for future in as_completed(futures):
                file_path = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"Completed: {file_path.name}")
                except Exception as e:
                    logger.error(f"Parallel processing error for {file_path}: {e}")
                    if not continue_on_error:
                        break
        
        return results
    
    def _process_single_file(
        self,
        file_path: Path,
        min_confidence: float,
        auto_delete: bool,
        dry_run: bool
    ) -> FileProcessingResult:
        """Process a single markdown file.
        
        Args:
            file_path: Path to file
            min_confidence: Minimum confidence threshold
            auto_delete: Delete after success
            dry_run: Simulate without deletion
            
        Returns:
            Processing result
        """
        try:
            # FAST PATH: Skip actual digestion for dry-run (just detect chat file)
            if dry_run:
                # Quick check - just count enhancements without deep processing
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Quick detection
                score = self.digest_orchestrator.detector.calculate_score(content)
                
                if not score.total_score >= min_confidence:
                    return FileProcessingResult(
                        file_path=str(file_path),
                        success=True,
                        skipped=True,
                        skip_reason=f"Low confidence ({score.total_score:.1f})"
                    )
                
                # Quick enhancement count (just count ✅ markers)
                enhancement_count = content.count('✅')
                
                return FileProcessingResult(
                    file_path=str(file_path),
                    success=True,
                    digest_result=DigestResult(
                        success=True,
                        is_chat_file=True,
                        confidence_score=score.total_score,
                        enhancements_found=enhancement_count
                    ),
                    deleted=False  # Dry-run never deletes
                )
            
            # FULL PATH: Actual digestion for live mode
            digest_result = self.digest_orchestrator.digest_session(
                file_path=str(file_path),
                auto_apply=False,  # Never auto-apply in bulk mode
                min_confidence=min_confidence
            )
            
            # Check if should skip
            if not digest_result.is_chat_file:
                return FileProcessingResult(
                    file_path=str(file_path),
                    success=True,
                    digest_result=digest_result,
                    skipped=True,
                    skip_reason=f"Low confidence ({digest_result.confidence_score:.1f})"
                )
            
            # Success - attempt deletion
            deleted = False
            if digest_result.success and auto_delete and not dry_run:
                try:
                    file_path.unlink()
                    deleted = True
                    logger.info(f"Deleted: {file_path.name}")
                except Exception as e:
                    logger.warning(f"Failed to delete {file_path.name}: {e}")
            
            return FileProcessingResult(
                file_path=str(file_path),
                success=digest_result.success,
                digest_result=digest_result,
                deleted=deleted
            )
            
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
            return FileProcessingResult(
                file_path=str(file_path),
                success=False,
                error_message=str(e)
            )
    
    def _aggregate_results(
        self,
        results: List[FileProcessingResult],
        stats: BulkDigestStats
    ) -> None:
        """Aggregate results into statistics.
        
        Args:
            results: List of processing results
            stats: Statistics object to update
        """
        for result in results:
            if result.success:
                if result.skipped:
                    stats.files_skipped += 1
                else:
                    stats.files_processed += 1
                    
                    if result.digest_result:
                        stats.total_enhancements += result.digest_result.enhancements_found
                    
                    if result.deleted:
                        stats.files_deleted += 1
            else:
                stats.files_failed += 1
                if result.error_message:
                    stats.errors.append(f"{Path(result.file_path).name}: {result.error_message}")
    
    def _create_batches(self, items: List[Any], batch_size: int) -> List[List[Any]]:
        """Create batches from list.
        
        Args:
            items: List of items
            batch_size: Size of each batch
            
        Returns:
            List of batches
        """
        return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
    
    def _update_progress(self, current: int, total: int, file_name: str) -> None:
        """Update progress (placeholder for future enhancement).
        
        Args:
            current: Current file index
            total: Total files
            file_name: Current file name
        """
        progress = (current / total) * 100 if total > 0 else 0
        logger.debug(f"Progress: {progress:.1f}% - {file_name}")
    
    def _print_progress_header(self, total_files: int, dry_run: bool) -> None:
        """Print progress header.
        
        Args:
            total_files: Total files to process
            dry_run: Whether in dry-run mode
        """
        mode = "DRY RUN" if dry_run else "LIVE"
        print("\n" + "━" * 70, flush=True)
        print(f"📋 Bulk Markdown Ingestion ({mode})", flush=True)
        print("━" * 70, flush=True)
        print(f"Files to process: {total_files}", flush=True)
        print("━" * 70 + "\n", flush=True)
    
    def _print_progress(
        self,
        current: int,
        total: int,
        file_name: str,
        progress: float
    ) -> None:
        """Print progress bar.
        
        Args:
            current: Current file index
            total: Total files
            file_name: Current file name
            progress: Progress (0.0-1.0)
        """
        bar = self.progress_bar.generate_bar(progress)
        percentage = int(progress * 100)
        
        # Use carriage return to overwrite same line
        print(
            f"\r{bar} {percentage:3d}% | File {current}/{total}: {file_name[:40]:40}",
            end="",
            flush=True
        )
    
    def _print_file_result(
        self,
        result: FileProcessingResult,
        current: int,
        total: int
    ) -> None:
        """Print file processing result.
        
        Args:
            result: Processing result
            current: Current file index
            total: Total files
        """
        file_name = Path(result.file_path).name
        
        if result.success:
            if result.skipped:
                status = "⚪ SKIP"
                reason = result.skip_reason
            elif result.deleted:
                status = "✅ DONE"
                enhancements = result.digest_result.enhancements_found if result.digest_result else 0
                reason = f"Deleted ({enhancements} enhancements)"
            else:
                status = "✅ DONE"
                enhancements = result.digest_result.enhancements_found if result.digest_result else 0
                reason = f"Kept ({enhancements} enhancements)"
        else:
            status = "❌ FAIL"
            reason = result.error_message
        
        # Clear line and print result
        print(f"\r{' ' * 70}\r{status} | {file_name[:40]:40} | {reason[:25]}", flush=True)
    
    def _print_completion(
        self,
        results: List[FileProcessingResult],
        total: int
    ) -> None:
        """Print completion summary.
        
        Args:
            results: List of processing results
            total: Total files
        """
        processed = sum(1 for r in results if r.success and not r.skipped)
        skipped = sum(1 for r in results if r.skipped)
        deleted = sum(1 for r in results if r.deleted)
        failed = sum(1 for r in results if not r.success)
        total_enhancements = sum(
            r.digest_result.enhancements_found
            for r in results
            if r.digest_result
        )
        
        print("\n" + "━" * 70, flush=True)
        print("📊 Bulk Ingestion Complete", flush=True)
        print("━" * 70, flush=True)
        print(f"✅ Processed:    {processed:3d}/{total}", flush=True)
        print(f"⚪ Skipped:      {skipped:3d}/{total}", flush=True)
        print(f"🗑️  Deleted:      {deleted:3d}/{total}", flush=True)
        print(f"❌ Failed:       {failed:3d}/{total}", flush=True)
        print(f"💡 Enhancements: {total_enhancements}", flush=True)
        print("━" * 70 + "\n", flush=True)
