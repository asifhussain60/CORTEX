"""
CORTEX Intelligent Crawler - Integration Module
Combines size detection, adaptive strategies, and timeout prevention

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
import os

from .size_detector import SizeDetector, SizeEstimate, SizeCategory
from .adaptive_strategies import AdaptiveCrawler, CrawlConfig, CrawlResult
from .timeout_prevention import TimeoutPreventor, TimeoutConfig, TimeoutStrategy, ProgressiveDisclosure


@dataclass
class CrawlerOptions:
    """Options for intelligent crawler"""
    root_path: str
    extensions: Optional[list] = None
    timeout_seconds: Optional[int] = None
    allow_time_extension: bool = True
    progress_callback: Optional[Callable] = None
    enable_progressive_disclosure: bool = True


class IntelligentCrawler:
    """
    Intelligent crawler with automatic size detection and strategy selection
    
    Workflow:
    1. Detect codebase size (fast, <30s)
    2. Select appropriate strategy (FULL/CHUNKED/SAMPLING)
    3. Configure timeout prevention
    4. Execute crawling with progress updates
    5. Handle timeouts gracefully
    6. Present results with accuracy indicators
    """
    
    def __init__(self, options: CrawlerOptions):
        """
        Initialize intelligent crawler
        
        Args:
            options: Crawler options
        """
        self.options = options
        self.size_detector = SizeDetector()
        self.adaptive_crawler = AdaptiveCrawler(progress_callback=options.progress_callback)
        self.timeout_preventor: Optional[TimeoutPreventor] = None
        self.progressive_disclosure: Optional[ProgressiveDisclosure] = None
        
        if options.enable_progressive_disclosure:
            self.progressive_disclosure = ProgressiveDisclosure(update_callback=self._disclosure_callback)
    
    def crawl(self, analyzer_func: Callable[[str], Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute intelligent crawling
        
        Args:
            analyzer_func: Function to analyze individual files
        
        Returns:
            Complete crawl results with metadata
        """
        # Phase 1: Size Detection
        print("🔍 Phase 1: Detecting codebase size...")
        size_estimate = self.size_detector.detect(
            self.options.root_path,
            self.options.extensions
        )
        print(self.size_detector.format_estimate(size_estimate))
        print()
        
        # Phase 2: Strategy Selection
        print("📊 Phase 2: Selecting crawl strategy...")
        crawl_config = self.adaptive_crawler.select_strategy(size_estimate.size_category)
        
        # Override timeout if specified
        if self.options.timeout_seconds:
            crawl_config.time_budget_seconds = self.options.timeout_seconds
        
        print(self.adaptive_crawler.format_strategy_summary(crawl_config))
        print()
        
        # Phase 3: Timeout Prevention Setup
        print("⏱️ Phase 3: Configuring timeout prevention...")
        timeout_config = TimeoutConfig(
            max_time_seconds=crawl_config.time_budget_seconds,
            warning_threshold=0.8,
            strategy=TimeoutStrategy.GRACEFUL_STOP,
            allow_extension=self.options.allow_time_extension,
            max_extensions=2
        )
        self.timeout_preventor = TimeoutPreventor(timeout_config)
        self.timeout_preventor.start_timer()
        print(f"✅ Timeout prevention active (budget: {crawl_config.time_budget_seconds}s)")
        print()
        
        # Phase 4: Execute Crawling
        print("🚀 Phase 4: Executing crawl...")
        
        # Get file list
        file_list = self._get_file_list(self.options.root_path, self.options.extensions)
        
        # Wrap analyzer with timeout and disclosure
        wrapped_analyzer = self._wrap_analyzer(analyzer_func)
        
        # Execute crawl
        crawl_result = self.adaptive_crawler.crawl(
            root_path=self.options.root_path,
            file_list=file_list,
            config=crawl_config,
            analyzer_func=wrapped_analyzer
        )
        
        print()
        print(self.adaptive_crawler.format_crawl_results(crawl_result))
        print()
        
        # Phase 5: Timeout Report
        if self.timeout_preventor:
            print(self.timeout_preventor.format_timeout_report())
            print()
        
        # Combine results
        return {
            'size_estimate': size_estimate,
            'crawl_config': crawl_config,
            'crawl_result': crawl_result,
            'timeout_warnings': self.timeout_preventor.warnings_issued if self.timeout_preventor else [],
            'progressive_results': self.progressive_disclosure.get_cumulative_results() if self.progressive_disclosure else None
        }
    
    def _get_file_list(self, root_path: str, extensions: Optional[list]) -> list:
        """
        Get list of files to analyze
        
        Args:
            root_path: Root directory
            extensions: File extensions to include
        
        Returns:
            List of file paths
        """
        target_extensions = set(extensions) if extensions else set(self.size_detector.CODE_EXTENSIONS.keys())
        
        files = []
        for root, dirs, filenames in os.walk(root_path):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if not self.size_detector._should_skip_dir(d)]
            
            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext in target_extensions:
                    files.append(os.path.join(root, filename))
        
        return files
    
    def _wrap_analyzer(self, analyzer_func: Callable[[str], Dict[str, Any]]) -> Callable[[str], Dict[str, Any]]:
        """
        Wrap analyzer with timeout checking and progressive disclosure
        
        Args:
            analyzer_func: Original analyzer function
        
        Returns:
            Wrapped analyzer function
        """
        def wrapped(file_path: str) -> Dict[str, Any]:
            # Check timeout
            if self.timeout_preventor and self.timeout_preventor.should_stop():
                raise TimeoutError("Crawl time budget exceeded")
            
            # Execute analysis
            result = analyzer_func(file_path)
            
            # Progressive disclosure (if enabled)
            if self.progressive_disclosure:
                # Disclosure handled at batch level in adaptive_crawler
                pass
            
            return result
        
        return wrapped
    
    def _disclosure_callback(self, message: str) -> None:
        """
        Callback for progressive disclosure updates
        
        Args:
            message: Disclosure message
        """
        print(message)


def quick_crawl(root_path: str, 
                analyzer_func: Callable[[str], Dict[str, Any]],
                extensions: Optional[list] = None) -> Dict[str, Any]:
    """
    Quick crawl with default options
    
    Args:
        root_path: Root directory to crawl
        analyzer_func: Function to analyze files
        extensions: Optional file extensions to focus on
    
    Returns:
        Crawl results
    """
    options = CrawlerOptions(
        root_path=root_path,
        extensions=extensions,
        timeout_seconds=None,  # Use automatic
        allow_time_extension=True,
        progress_callback=None,
        enable_progressive_disclosure=False
    )
    
    crawler = IntelligentCrawler(options)
    return crawler.crawl(analyzer_func)
