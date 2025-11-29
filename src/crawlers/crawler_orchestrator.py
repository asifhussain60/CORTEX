"""
CrawlerOrchestrator - Progressive application crawler with multi-level scanning.

This orchestrator coordinates file system scanning, language analysis, and metrics
collection for application health dashboards.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""


class CrawlerOrchestrator:
    """
    Orchestrates progressive crawling of application codebases.
    
    Supports three scan levels:
    - Overview: Fast scan (file counts, basic structure)
    - Standard: Medium depth (includes complexity metrics)
    - Deep: Full analysis (security, dependencies, quality)
    """
    
    def __init__(self, scan_level: str = "standard"):
        """
        Initialize CrawlerOrchestrator with specified scan level.
        
        Args:
            scan_level: Scan depth - "overview", "standard", or "deep" (default: "standard")
        """
        self.scan_level = scan_level
    
    def scan(self, root_path: str):
        """
        Scan application codebase starting from root_path.
        
        Args:
            root_path: Root directory to scan
            
        Returns:
            ScanResult: Object containing scan metrics and findings
        """
        from src.crawlers.scan_result import ScanResult
        from src.crawlers.file_system_walker import FileSystemWalker
        
        # Configure FileSystemWalker based on scan level
        walker = FileSystemWalker()
        
        # Apply scan level-specific exclusions
        if self.scan_level == "overview":
            walker.set_exclusions(['.git', 'node_modules', '__pycache__', '.pytest_cache'])
        elif self.scan_level == "standard":
            walker.set_exclusions(['.git', '__pycache__', '.pytest_cache'])
        # Deep scan: no exclusions (scan everything)
        
        files = walker.walk(root_path)
        
        # Count file types and build file path list
        file_types = {}
        file_paths = []
        for file_path in files:
            ext = file_path.suffix
            file_types[ext] = file_types.get(ext, 0) + 1
            file_paths.append(str(file_path))
        
        return ScanResult(
            root_path=root_path,
            scan_level=self.scan_level,
            total_files=len(files),
            file_types=file_types,
            file_paths=file_paths
        )
