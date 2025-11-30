"""
CORTEX Adaptive Crawling Strategies
Size-aware strategies for efficient codebase analysis

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

import os
import random
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import hashlib

from .size_detector import SizeCategory


class CrawlStrategy(Enum):
    """Available crawling strategies"""
    FULL_ANALYSIS = "FULL_ANALYSIS"
    CHUNKED_ANALYSIS = "CHUNKED_ANALYSIS"
    SAMPLING_CHUNKED = "SAMPLING_CHUNKED"
    INTELLIGENT_SAMPLING = "INTELLIGENT_SAMPLING"


@dataclass
class CrawlConfig:
    """Configuration for crawling strategy"""
    strategy: CrawlStrategy
    chunk_size: int  # Files per chunk
    sample_rate: float  # 0.0 to 1.0
    time_budget_seconds: int
    checkpoint_interval: int  # Checkpoint every N files
    expected_accuracy: float  # Expected accuracy percentage


@dataclass
class CrawlProgress:
    """Progress tracking for crawling operation"""
    files_processed: int
    files_total: int
    chunks_completed: int
    chunks_total: int
    current_file: str
    elapsed_seconds: float
    estimated_remaining_seconds: float


@dataclass
class CrawlResult:
    """Results from crawling operation"""
    files_analyzed: int
    files_skipped: int
    total_loc_analyzed: int
    strategy_used: CrawlStrategy
    actual_time_seconds: float
    accuracy_estimate: float
    checkpoints_created: int
    relationships_found: Dict[str, List[str]]  # file -> dependencies
    modules_discovered: List[str]


class AdaptiveCrawler:
    """
    Adaptive crawler that selects strategy based on codebase size
    
    Strategies:
    - FULL_ANALYSIS: Analyze every file (SMALL codebases)
    - CHUNKED_ANALYSIS: Process in manageable chunks (MEDIUM codebases)
    - SAMPLING_CHUNKED: Sample 20% + chunk processing (LARGE codebases)
    - INTELLIGENT_SAMPLING: Sample 5% strategically (MASSIVE codebases)
    """
    
    # Strategy mappings
    STRATEGY_MAP = {
        SizeCategory.SMALL: CrawlStrategy.FULL_ANALYSIS,
        SizeCategory.MEDIUM: CrawlStrategy.CHUNKED_ANALYSIS,
        SizeCategory.LARGE: CrawlStrategy.SAMPLING_CHUNKED,
        SizeCategory.MASSIVE: CrawlStrategy.INTELLIGENT_SAMPLING
    }
    
    # Time budgets (in seconds)
    TIME_BUDGETS = {
        SizeCategory.SMALL: 300,      # 5 minutes
        SizeCategory.MEDIUM: 900,     # 15 minutes
        SizeCategory.LARGE: 1200,     # 20 minutes
        SizeCategory.MASSIVE: 1800    # 30 minutes
    }
    
    # Chunk sizes
    CHUNK_SIZES = {
        CrawlStrategy.FULL_ANALYSIS: 1000,          # No chunking needed
        CrawlStrategy.CHUNKED_ANALYSIS: 100,        # 100 files per chunk
        CrawlStrategy.SAMPLING_CHUNKED: 50,         # 50 files per chunk
        CrawlStrategy.INTELLIGENT_SAMPLING: 25      # 25 files per chunk
    }
    
    # Sample rates
    SAMPLE_RATES = {
        CrawlStrategy.FULL_ANALYSIS: 1.0,           # 100%
        CrawlStrategy.CHUNKED_ANALYSIS: 1.0,        # 100%
        CrawlStrategy.SAMPLING_CHUNKED: 0.20,       # 20%
        CrawlStrategy.INTELLIGENT_SAMPLING: 0.05    # 5%
    }
    
    # Expected accuracy
    EXPECTED_ACCURACY = {
        CrawlStrategy.FULL_ANALYSIS: 1.0,           # 100%
        CrawlStrategy.CHUNKED_ANALYSIS: 1.0,        # 100%
        CrawlStrategy.SAMPLING_CHUNKED: 0.85,       # 85-95%
        CrawlStrategy.INTELLIGENT_SAMPLING: 0.70    # 70-85%
    }
    
    def __init__(self, progress_callback: Optional[Callable[[CrawlProgress], None]] = None):
        """
        Initialize adaptive crawler
        
        Args:
            progress_callback: Optional callback for progress updates
        """
        self.progress_callback = progress_callback
        self.checkpoints: List[Dict[str, Any]] = []
    
    def select_strategy(self, size_category: SizeCategory) -> CrawlConfig:
        """
        Select appropriate crawling strategy based on size
        
        Args:
            size_category: Detected size category
        
        Returns:
            Crawl configuration
        """
        strategy = self.STRATEGY_MAP[size_category]
        
        return CrawlConfig(
            strategy=strategy,
            chunk_size=self.CHUNK_SIZES[strategy],
            sample_rate=self.SAMPLE_RATES[strategy],
            time_budget_seconds=self.TIME_BUDGETS[size_category],
            checkpoint_interval=100,
            expected_accuracy=self.EXPECTED_ACCURACY[strategy]
        )
    
    def crawl(self, 
              root_path: str, 
              file_list: List[str],
              config: CrawlConfig,
              analyzer_func: Callable[[str], Dict[str, Any]]) -> CrawlResult:
        """
        Execute crawling with selected strategy
        
        Args:
            root_path: Root directory path
            file_list: List of files to potentially analyze
            config: Crawl configuration
            analyzer_func: Function to analyze individual files
        
        Returns:
            Crawl results
        """
        import time
        start_time = time.time()
        
        # Select files based on strategy
        if config.strategy == CrawlStrategy.FULL_ANALYSIS:
            selected_files = file_list
        elif config.strategy == CrawlStrategy.CHUNKED_ANALYSIS:
            selected_files = file_list
        elif config.strategy == CrawlStrategy.SAMPLING_CHUNKED:
            selected_files = self._stratified_sample(file_list, config.sample_rate)
        else:  # INTELLIGENT_SAMPLING
            selected_files = self._intelligent_sample(file_list, config.sample_rate)
        
        # Process files in chunks
        files_analyzed = 0
        files_skipped = len(file_list) - len(selected_files)
        total_loc = 0
        relationships = {}
        modules = set()
        checkpoints_created = 0
        
        chunks = self._create_chunks(selected_files, config.chunk_size)
        
        for chunk_idx, chunk in enumerate(chunks):
            # Check time budget
            elapsed = time.time() - start_time
            if elapsed > config.time_budget_seconds:
                # Time budget exceeded - graceful degradation
                break
            
            for file_idx, file_path in enumerate(chunk):
                # Analyze file
                try:
                    analysis = analyzer_func(file_path)
                    
                    files_analyzed += 1
                    total_loc += analysis.get('loc', 0)
                    
                    # Extract relationships
                    if 'dependencies' in analysis:
                        relationships[file_path] = analysis['dependencies']
                    
                    # Extract modules
                    if 'module' in analysis:
                        modules.add(analysis['module'])
                    
                    # Checkpoint every N files
                    if files_analyzed % config.checkpoint_interval == 0:
                        self._create_checkpoint(
                            files_analyzed, 
                            relationships, 
                            list(modules)
                        )
                        checkpoints_created += 1
                    
                    # Progress callback
                    if self.progress_callback:
                        progress = CrawlProgress(
                            files_processed=files_analyzed,
                            files_total=len(selected_files),
                            chunks_completed=chunk_idx,
                            chunks_total=len(chunks),
                            current_file=os.path.basename(file_path),
                            elapsed_seconds=elapsed,
                            estimated_remaining_seconds=self._estimate_remaining(
                                files_analyzed, 
                                len(selected_files), 
                                elapsed
                            )
                        )
                        self.progress_callback(progress)
                
                except Exception as e:
                    # Skip files that fail analysis
                    files_skipped += 1
                    continue
        
        actual_time = time.time() - start_time
        
        return CrawlResult(
            files_analyzed=files_analyzed,
            files_skipped=files_skipped,
            total_loc_analyzed=total_loc,
            strategy_used=config.strategy,
            actual_time_seconds=actual_time,
            accuracy_estimate=config.expected_accuracy,
            checkpoints_created=checkpoints_created,
            relationships_found=relationships,
            modules_discovered=list(modules)
        )
    
    def _stratified_sample(self, file_list: List[str], sample_rate: float) -> List[str]:
        """
        Perform stratified sampling across file types
        
        Args:
            file_list: Complete file list
            sample_rate: Sampling rate (0.0 to 1.0)
        
        Returns:
            Sampled file list
        """
        # Group by extension
        by_extension = {}
        for file_path in file_list:
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in by_extension:
                by_extension[ext] = []
            by_extension[ext].append(file_path)
        
        # Sample from each group
        sampled = []
        for ext, files in by_extension.items():
            sample_size = max(1, int(len(files) * sample_rate))
            sampled.extend(random.sample(files, min(sample_size, len(files))))
        
        return sampled
    
    def _intelligent_sample(self, file_list: List[str], sample_rate: float) -> List[str]:
        """
        Intelligent sampling prioritizing key files
        
        Strategy:
        - Always include: entry points, config files, main modules
        - Prioritize: larger files, central files (many dependencies)
        - Random sample: remaining files
        
        Args:
            file_list: Complete file list
            sample_rate: Sampling rate (0.0 to 1.0)
        
        Returns:
            Intelligently sampled file list
        """
        priority_files = []
        regular_files = []
        
        # Priority patterns
        priority_patterns = [
            'main.', 'index.', 'app.', '__init__.', 'startup.',
            'config.', 'settings.', 'program.cs', 'application.'
        ]
        
        for file_path in file_list:
            basename = os.path.basename(file_path).lower()
            
            # Check if priority file
            is_priority = any(pattern in basename for pattern in priority_patterns)
            
            if is_priority:
                priority_files.append(file_path)
            else:
                regular_files.append(file_path)
        
        # Calculate sampling for regular files
        total_sample_size = max(1, int(len(file_list) * sample_rate))
        priority_count = len(priority_files)
        remaining_slots = max(0, total_sample_size - priority_count)
        
        # Sample regular files
        if remaining_slots > 0 and regular_files:
            sampled_regular = random.sample(
                regular_files, 
                min(remaining_slots, len(regular_files))
            )
        else:
            sampled_regular = []
        
        return priority_files + sampled_regular
    
    def _create_chunks(self, file_list: List[str], chunk_size: int) -> List[List[str]]:
        """
        Split file list into chunks
        
        Args:
            file_list: List of files
            chunk_size: Files per chunk
        
        Returns:
            List of file chunks
        """
        chunks = []
        for i in range(0, len(file_list), chunk_size):
            chunks.append(file_list[i:i + chunk_size])
        return chunks
    
    def _create_checkpoint(self, 
                          files_processed: int,
                          relationships: Dict[str, List[str]],
                          modules: List[str]) -> None:
        """
        Create checkpoint for resumable crawling
        
        Args:
            files_processed: Number of files processed so far
            relationships: Discovered relationships
            modules: Discovered modules
        """
        checkpoint = {
            'files_processed': files_processed,
            'relationships_count': len(relationships),
            'modules_count': len(modules),
            'checkpoint_hash': self._generate_checkpoint_hash(files_processed)
        }
        self.checkpoints.append(checkpoint)
    
    def _generate_checkpoint_hash(self, files_processed: int) -> str:
        """
        Generate unique hash for checkpoint
        
        Args:
            files_processed: Number of files processed
        
        Returns:
            Checkpoint hash
        """
        data = f"checkpoint_{files_processed}_{len(self.checkpoints)}"
        return hashlib.md5(data.encode()).hexdigest()[:8]
    
    def _estimate_remaining(self, 
                           processed: int, 
                           total: int, 
                           elapsed: float) -> float:
        """
        Estimate remaining time
        
        Args:
            processed: Files processed
            total: Total files
            elapsed: Elapsed time
        
        Returns:
            Estimated remaining seconds
        """
        if processed == 0:
            return 0.0
        
        rate = elapsed / processed
        remaining_files = total - processed
        return rate * remaining_files
    
    def format_strategy_summary(self, config: CrawlConfig) -> str:
        """
        Format strategy summary for user display
        
        Args:
            config: Crawl configuration
        
        Returns:
            Formatted summary string
        """
        lines = [
            f"📊 **Crawl Strategy Selected:** {config.strategy.value.replace('_', ' ').title()}",
            f"   Sample Rate: {config.sample_rate * 100:.0f}% of files",
            f"   Chunk Size: {config.chunk_size} files per chunk",
            f"   Time Budget: {config.time_budget_seconds // 60} minutes",
            f"   Expected Accuracy: {config.expected_accuracy * 100:.0f}%",
            f"   Checkpoints: Every {config.checkpoint_interval} files"
        ]
        return "\n".join(lines)
    
    def format_crawl_results(self, result: CrawlResult) -> str:
        """
        Format crawl results for user display
        
        Args:
            result: Crawl results
        
        Returns:
            Formatted results string
        """
        lines = [
            f"✅ **Crawl Complete**",
            f"   Files Analyzed: {result.files_analyzed:,}",
            f"   Files Skipped: {result.files_skipped:,}",
            f"   Total LOC: {result.total_loc_analyzed:,}",
            f"   Actual Time: {result.actual_time_seconds / 60:.1f} minutes",
            f"   Strategy Used: {result.strategy_used.value.replace('_', ' ').title()}",
            f"   Estimated Accuracy: {result.accuracy_estimate * 100:.0f}%",
            f"   Checkpoints Created: {result.checkpoints_created}",
            "",
            f"📦 **Discoveries:**",
            f"   Modules Found: {len(result.modules_discovered)}",
            f"   Relationships Mapped: {len(result.relationships_found):,}"
        ]
        return "\n".join(lines)
