"""
Parallel Dashboard Data Collector

Multi-threaded collector orchestration for fast dashboard data generation.
Runs all 6 collectors in parallel (one thread per tab).

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)


class ParallelCollectorOrchestrator:
    """
    Orchestrates parallel execution of dashboard collectors.
    
    Features:
    - One thread per collector (6 parallel threads)
    - Exception handling per collector
    - Progress tracking
    - Fallback to minimal structure on failure
    
    Target: <5 seconds for all collectors
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize parallel collector orchestrator.
        
        Args:
            project_path: Path to project to analyze
        """
        self.project_path = project_path
        self.collectors = {}
        self._init_collectors()
    
    def _init_collectors(self):
        """Initialize all collectors."""
        try:
            from dashboard.data.tech_stack_collector import TechStackCollector
            from dashboard.data.security_collector_optimized import SecurityCollectorOptimized
            from dashboard.data.architecture_collector import ArchitectureCollector
            from dashboard.data.code_org_collector import CodeOrganizationCollector
            from dashboard.data.vendor_detector import VendorDetector
            from dashboard.data.team_metrics_collector import TeamMetricsCollector
            
            self.collectors = {
                "tech-stack": TechStackCollector(self.project_path),
                "security": SecurityCollectorOptimized(self.project_path),
                "architecture": ArchitectureCollector(self.project_path),
                "code-organization": CodeOrganizationCollector(self.project_path),
                "team-metrics": TeamMetricsCollector(self.project_path),
                "vendors": VendorDetector(self.project_path)
            }
            
            logger.info(f"Initialized {len(self.collectors)} collectors for parallel execution")
        
        except Exception as e:
            logger.error(f"Failed to initialize collectors: {e}")
            raise
    
    def collect_all_parallel(self) -> Tuple[Dict[str, Any], float]:
        """
        Execute all collectors in parallel.
        
        Returns:
            Tuple of (collected_data dict, execution_time)
        """
        start_time = time.time()
        collected_data = {}
        
        logger.info("Starting parallel collection with 6 threads...")
        
        # Execute collectors in parallel
        with ThreadPoolExecutor(max_workers=6, thread_name_prefix="Collector") as executor:
            # Submit all collectors
            future_to_name = {
                executor.submit(self._safe_collect, name, collector): name
                for name, collector in self.collectors.items()
            }
            
            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_name):
                collector_name = future_to_name[future]
                completed += 1
                
                try:
                    data = future.result()
                    collected_data[f"{collector_name}.json"] = data
                    logger.info(f"  [{completed}/6] ✓ {collector_name} completed")
                
                except Exception as e:
                    logger.error(f"  [{completed}/6] ✗ {collector_name} failed: {e}")
                    collected_data[f"{collector_name}.json"] = self._get_minimal_structure(collector_name)
        
        execution_time = time.time() - start_time
        logger.info(f"Parallel collection completed in {execution_time:.2f}s")
        
        return collected_data, execution_time
    
    def _safe_collect(self, name: str, collector) -> Dict[str, Any]:
        """
        Safely execute collector with exception handling.
        
        Args:
            name: Collector name
            collector: Collector instance
        
        Returns:
            Collected data or minimal structure
        """
        try:
            logger.debug(f"Starting {name} collector...")
            
            # Execute collection
            if hasattr(collector, 'collect'):
                data = collector.collect()
            elif hasattr(collector, 'detect'):
                data = collector.detect()
            else:
                raise AttributeError(f"Collector {name} has no collect() or detect() method")
            
            # Validate data
            if not data or (isinstance(data, dict) and not any(data.values())):
                logger.warning(f"{name} returned no data, using minimal structure")
                return self._get_minimal_structure(name)
            
            return data
        
        except Exception as e:
            logger.error(f"{name} collector failed: {e}", exc_info=True)
            return self._get_minimal_structure(name)
    
    def _get_minimal_structure(self, collector_name: str) -> Dict[str, Any]:
        """
        Get minimal structure for collector when no data found.
        
        Args:
            collector_name: Name of collector
        
        Returns:
            Minimal structure dict
        """
        from datetime import datetime
        
        structures = {
            "tech-stack": {
                "frontend": [],
                "backend": [],
                "database": [],
                "devops": [],
                "summary": {
                    "total_technologies": 0,
                    "current_count": 0,
                    "outdated_count": 0,
                    "deprecated_count": 0,
                    "last_scan": datetime.now().isoformat()
                }
            },
            "security": {
                "overall_score": 0,
                "last_scan": datetime.now().isoformat(),
                "categories": [],
                "vulnerabilities": [],
                "scan_mode": "fast"
            },
            "architecture": {
                "components": [],
                "layers": 0,
                "patterns": []
            },
            "code-organization": {
                "total_files": 0,
                "total_lines": 0,
                "hotspots": [],
                "file_types": {},
                "directories": 0
            },
            "team-metrics": {
                "total_commits": 0,
                "contributor_count": 0,
                "last_commit_date": "N/A",
                "active_contributors": []
            },
            "vendors": {
                "vendors": [],
                "total_vendors": 0
            }
        }
        
        return structures.get(collector_name, {})
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return {
            "total_collectors": len(self.collectors),
            "parallel_workers": 6,
            "project_path": str(self.project_path)
        }
