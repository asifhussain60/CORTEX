"""
Batch Test Generator for Parallel Processing

Generates tests for multiple files/functions in parallel for improved performance.

Author: Asif Hussain
Created: 2025-11-23
Phase: TDD Mastery Phase 3 - Milestone 3.2 (Production Optimization)
"""

from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from pathlib import Path
import time
from dataclasses import dataclass, field


@dataclass
class BatchResult:
    """Result of batch test generation."""
    source_file: str
    success: bool
    test_count: int = 0
    test_file: Optional[str] = None
    duration_seconds: float = 0.0
    error: Optional[str] = None
    tests: List[dict] = field(default_factory=list)


class BatchTestGenerator:
    """
    Generate tests for multiple functions/files in parallel.
    
    Uses ThreadPoolExecutor for I/O-bound test generation tasks.
    
    Performance Impact:
    - Expected speedup: 2-4x with 4 workers (I/O bound)
    - Memory overhead: ~50-100MB per worker
    """
    
    def __init__(self, orchestrator, max_workers: int = 4):
        """
        Initialize batch processor.
        
        Args:
            orchestrator: TDDWorkflowOrchestrator instance
            max_workers: Maximum parallel workers
        """
        self.orchestrator = orchestrator
        self.max_workers = max_workers
    
    def generate_tests_batch(
        self,
        source_files: List[str],
        scenarios: Optional[List[str]] = None,
        function_names: Optional[Dict[str, str]] = None
    ) -> Dict[str, BatchResult]:
        """
        Generate tests for multiple files in parallel.
        
        Args:
            source_files: List of source file paths
            scenarios: Test scenarios to generate
            function_names: Optional dict mapping file -> function name
            
        Returns:
            Dictionary mapping source_file -> BatchResult
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {}
            
            for source_file in source_files:
                function_name = function_names.get(source_file) if function_names else None
                
                future = executor.submit(
                    self._generate_single,
                    source_file,
                    function_name,
                    scenarios
                )
                
                future_to_file[future] = source_file
            
            # Collect results as they complete
            for future in as_completed(future_to_file):
                source_file = future_to_file[future]
                
                try:
                    result = future.result()
                    results[source_file] = result
                    
                except Exception as e:
                    results[source_file] = BatchResult(
                        source_file=source_file,
                        success=False,
                        error=str(e)
                    )
        
        return results
    
    def _generate_single(
        self,
        source_file: str,
        function_name: Optional[str],
        scenarios: Optional[List[str]]
    ) -> BatchResult:
        """
        Generate tests for single file.
        
        Args:
            source_file: Source file path
            function_name: Optional function name
            scenarios: Test scenarios
            
        Returns:
            BatchResult with generation details
        """
        start_time = time.time()
        
        try:
            result = self.orchestrator.generate_tests(
                source_file=source_file,
                function_name=function_name,
                scenarios=scenarios
            )
            
            duration = time.time() - start_time
            
            return BatchResult(
                source_file=source_file,
                success=True,
                test_count=result.get('test_count', 0),
                test_file=result.get('test_file'),
                duration_seconds=duration,
                tests=result.get('tests', [])
            )
            
        except Exception as e:
            duration = time.time() - start_time
            
            return BatchResult(
                source_file=source_file,
                success=False,
                duration_seconds=duration,
                error=str(e)
            )
    
    def generate_tests_module(
        self,
        module_path: str,
        scenarios: Optional[List[str]] = None,
        recursive: bool = True
    ) -> Dict[str, BatchResult]:
        """
        Generate tests for entire module (all .py files).
        
        Args:
            module_path: Path to module directory
            scenarios: Test scenarios to generate
            recursive: Include subdirectories
            
        Returns:
            Dictionary mapping source_file -> BatchResult
        """
        module_dir = Path(module_path)
        
        if not module_dir.is_dir():
            raise ValueError(f"Module path is not a directory: {module_path}")
        
        # Find all Python files
        if recursive:
            source_files = list(module_dir.glob("**/*.py"))
        else:
            source_files = list(module_dir.glob("*.py"))
        
        # Filter out __init__.py and test files
        source_files = [
            str(f) for f in source_files
            if f.name != "__init__.py" and not f.name.startswith("test_")
        ]
        
        if not source_files:
            return {}
        
        return self.generate_tests_batch(source_files, scenarios)
    
    def summarize_batch_results(self, results: Dict[str, BatchResult]) -> Dict[str, Any]:
        """
        Summarize batch generation results.
        
        Args:
            results: Batch results dictionary
            
        Returns:
            Summary statistics
        """
        total_files = len(results)
        successful = sum(1 for r in results.values() if r.success)
        failed = total_files - successful
        
        total_tests = sum(r.test_count for r in results.values() if r.success)
        total_duration = sum(r.duration_seconds for r in results.values())
        avg_duration = total_duration / total_files if total_files > 0 else 0
        
        # Find slowest files
        slowest_files = sorted(
            [(file, r.duration_seconds) for file, r in results.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Collect errors
        errors = {
            file: r.error
            for file, r in results.items()
            if not r.success and r.error
        }
        
        return {
            "total_files": total_files,
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful / total_files * 100):.1f}%" if total_files > 0 else "0%",
            "total_tests_generated": total_tests,
            "total_duration_seconds": round(total_duration, 2),
            "average_duration_seconds": round(avg_duration, 2),
            "slowest_files": slowest_files,
            "errors": errors
        }


class BatchSmellDetector:
    """
    Analyze multiple files for code smells in parallel.
    
    Performance Impact:
    - Expected speedup: 2-4x with 4 workers
    """
    
    def __init__(self, smell_detector, max_workers: int = 4):
        """
        Initialize batch smell detector.
        
        Args:
            smell_detector: CodeSmellDetector instance
            max_workers: Maximum parallel workers
        """
        self.smell_detector = smell_detector
        self.max_workers = max_workers
    
    def analyze_files_batch(
        self,
        source_files: List[str]
    ) -> Dict[str, List[dict]]:
        """
        Analyze multiple files for code smells in parallel.
        
        Args:
            source_files: List of source file paths
            
        Returns:
            Dictionary mapping source_file -> list of detected smells
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(
                    self.smell_detector.analyze_file,
                    source_file
                ): source_file
                for source_file in source_files
            }
            
            for future in as_completed(future_to_file):
                source_file = future_to_file[future]
                
                try:
                    smells = future.result()
                    results[source_file] = smells
                    
                except Exception as e:
                    results[source_file] = []
        
        return results
    
    def analyze_module_batch(
        self,
        module_path: str,
        recursive: bool = True
    ) -> Dict[str, List[dict]]:
        """
        Analyze entire module for code smells.
        
        Args:
            module_path: Path to module directory
            recursive: Include subdirectories
            
        Returns:
            Dictionary mapping source_file -> list of smells
        """
        module_dir = Path(module_path)
        
        if recursive:
            source_files = list(module_dir.glob("**/*.py"))
        else:
            source_files = list(module_dir.glob("*.py"))
        
        source_files = [
            str(f) for f in source_files
            if f.name != "__init__.py" and not f.name.startswith("test_")
        ]
        
        return self.analyze_files_batch(source_files)
    
    def summarize_smells(self, results: Dict[str, List[dict]]) -> Dict[str, Any]:
        """
        Summarize code smell analysis results.
        
        Args:
            results: Analysis results dictionary
            
        Returns:
            Summary statistics
        """
        total_files = len(results)
        files_with_smells = sum(1 for smells in results.values() if smells)
        total_smells = sum(len(smells) for smells in results.values())
        
        # Count smell types
        smell_type_counts = {}
        for smells in results.values():
            for smell in smells:
                smell_type = smell.get('type', 'unknown')
                smell_type_counts[smell_type] = smell_type_counts.get(smell_type, 0) + 1
        
        # Find files with most smells
        files_by_smell_count = sorted(
            [(file, len(smells)) for file, smells in results.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "total_files_analyzed": total_files,
            "files_with_smells": files_with_smells,
            "files_clean": total_files - files_with_smells,
            "total_smells": total_smells,
            "smell_type_distribution": smell_type_counts,
            "files_with_most_smells": files_by_smell_count,
            "average_smells_per_file": round(total_smells / total_files, 2) if total_files > 0 else 0
        }
