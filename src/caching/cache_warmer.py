"""
Background Cache Warming
Automatically pre-populates ValidationCache after git operations

Pre-warms expensive discovery operations in background thread:
- Orchestrator discovery (align operation)
- Agent discovery (align operation)
- Integration scoring (deploy operation)
- Governance drift analysis (optimize operation)
- Filesystem scans (cleanup operation)

Triggered by git hooks: post-checkout, post-merge
Zero impact on interactive workflows (runs in background)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import threading
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
import time

logger = logging.getLogger(__name__)


class CacheWarmer:
    """Background cache warmer for expensive discovery operations."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize cache warmer.
        
        Args:
            project_root: Project root directory (auto-detected if None)
        """
        if project_root is None:
            project_root = Path.cwd()
            while project_root != project_root.parent:
                if (project_root / '.git').exists():
                    break
                project_root = project_root.parent
        
        self.project_root = project_root
        self.warming_thread: Optional[threading.Thread] = None
        self.is_warming = False
    
    def warm_cache_background(self, operations: Optional[List[str]] = None):
        """
        Start cache warming in background thread.
        
        Args:
            operations: List of operations to warm (all by default)
                       Options: 'align', 'deploy', 'optimize', 'cleanup'
        """
        if self.is_warming:
            logger.info("Cache warming already in progress, skipping")
            return
        
        if operations is None:
            operations = ['align', 'deploy', 'optimize', 'cleanup']
        
        self.warming_thread = threading.Thread(
            target=self._warm_cache_worker,
            args=(operations,),
            daemon=True,
            name="CacheWarmer"
        )
        
        self.is_warming = True
        self.warming_thread.start()
        logger.info(f"🔥 Started background cache warming for: {', '.join(operations)}")
    
    def _warm_cache_worker(self, operations: List[str]):
        """
        Worker thread that performs cache warming.
        
        Args:
            operations: List of operations to warm
        """
        try:
            start_time = time.time()
            results = {}
            
            logger.info("🔥 Cache warming started in background")
            
            # Warm align operation (orchestrator + agent discovery)
            if 'align' in operations:
                try:
                    results['align'] = self._warm_align_cache()
                except Exception as e:
                    logger.warning(f"Failed to warm align cache: {e}")
                    results['align'] = {'success': False, 'error': str(e)}
            
            # Warm deploy operation (integration scoring)
            if 'deploy' in operations:
                try:
                    results['deploy'] = self._warm_deploy_cache()
                except Exception as e:
                    logger.warning(f"Failed to warm deploy cache: {e}")
                    results['deploy'] = {'success': False, 'error': str(e)}
            
            # Warm optimize operation (governance drift, EPMO health)
            if 'optimize' in operations:
                try:
                    results['optimize'] = self._warm_optimize_cache()
                except Exception as e:
                    logger.warning(f"Failed to warm optimize cache: {e}")
                    results['optimize'] = {'success': False, 'error': str(e)}
            
            # Warm cleanup operation (filesystem scans)
            if 'cleanup' in operations:
                try:
                    results['cleanup'] = self._warm_cleanup_cache()
                except Exception as e:
                    logger.warning(f"Failed to warm cleanup cache: {e}")
                    results['cleanup'] = {'success': False, 'error': str(e)}
            
            elapsed = time.time() - start_time
            
            # Log summary
            successful = sum(1 for r in results.values() if r.get('success', False))
            logger.info(f"✅ Cache warming complete: {successful}/{len(operations)} operations warmed in {elapsed:.1f}s")
            
            for op, result in results.items():
                if result.get('success'):
                    logger.info(f"  ✓ {op}: {result.get('items_cached', 0)} items cached")
                else:
                    logger.warning(f"  ✗ {op}: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            logger.error(f"Cache warming failed: {e}", exc_info=True)
        
        finally:
            self.is_warming = False
    
    def _warm_align_cache(self) -> Dict[str, Any]:
        """
        Warm cache for align operation (orchestrator + agent discovery).
        
        Returns:
            Result dictionary with success status and items cached
        """
        from src.operations.modules.admin.system_alignment_orchestrator import SystemAlignmentOrchestrator
        
        logger.info("Warming align cache (orchestrator + agent discovery)...")
        
        try:
            orchestrator = AlignSystemOrchestrator(self.project_root)
            
            # Run discovery (will cache results automatically)
            context = {'mode': 'cache-warming'}
            orchestrator._discover_orchestrators()
            orchestrator._discover_agents()
            
            return {
                'success': True,
                'items_cached': 2,  # orchestrators + agents
                'operation': 'align'
            }
        
        except Exception as e:
            logger.warning(f"Failed to warm align cache: {e}")
            return {
                'success': False,
                'error': str(e),
                'operation': 'align'
            }
    
    def _warm_deploy_cache(self) -> Dict[str, Any]:
        """
        Warm cache for deploy operation (integration scoring).
        
        Returns:
            Result dictionary with success status and items cached
        
        Note: DeployOrchestrator deprecated - deploy now handled by scripts/deploy_cortex.py
        """
        # from src.deployment.deploy_orchestrator import DeployOrchestrator
        
        logger.info("Skipping deploy cache warming (orchestrator deprecated)...")
        
        return {
            'success': True,
            'items_cached': 0,
            'operation': 'deploy',
            'note': 'Deploy orchestrator deprecated - using scripts instead'
        }
        
        # Legacy code commented out:
        # try:
        #     orchestrator = DeployOrchestrator(self.project_root)
            
            # Run scoring (will cache results automatically)
            orchestrator._calculate_integration_scores()
            
            return {
                'success': True,
                'items_cached': 1,  # integration scores
                'operation': 'deploy'
            }
        
        except Exception as e:
            logger.warning(f"Failed to warm deploy cache: {e}")
            return {
                'success': False,
                'error': str(e),
                'operation': 'deploy'
            }
    
    def _warm_optimize_cache(self) -> Dict[str, Any]:
        """
        Warm cache for optimize operation (governance drift + EPMO health).
        
        Returns:
            Result dictionary with success status and items cached
        """
        from src.operations.modules.system.optimize_system_orchestrator import OptimizeSystemOrchestrator
        
        logger.info("Warming optimize cache (governance drift + EPMO health)...")
        
        try:
            orchestrator = OptimizeSystemOrchestrator(self.project_root)
            
            # Run analyses (will cache results automatically)
            context = {'mode': 'cache-warming'}
            orchestrator._check_governance_drift(context)
            orchestrator._check_epmo_health()
            
            return {
                'success': True,
                'items_cached': 2,  # governance + EPMO
                'operation': 'optimize'
            }
        
        except Exception as e:
            logger.warning(f"Failed to warm optimize cache: {e}")
            return {
                'success': False,
                'error': str(e),
                'operation': 'optimize'
            }
    
    def _warm_cleanup_cache(self) -> Dict[str, Any]:
        """
        Warm cache for cleanup operation (filesystem scans).
        
        Returns:
            Result dictionary with success status and items cached
        """
        from src.operations.cleanup import find_temp_files, find_old_logs, find_large_cache_files
        from src.caching import get_cache
        
        logger.info("Warming cleanup cache (filesystem scans)...")
        
        try:
            cache = get_cache()
            
            # Run scans (will cache results automatically)
            find_temp_files(self.project_root, cache_instance=cache)
            find_old_logs(self.project_root, days_old=30, cache_instance=cache)
            find_large_cache_files(self.project_root, min_size_mb=10, cache_instance=cache)
            
            return {
                'success': True,
                'items_cached': 3,  # temp + logs + cache files
                'operation': 'cleanup'
            }
        
        except Exception as e:
            logger.warning(f"Failed to warm cleanup cache: {e}")
            return {
                'success': False,
                'error': str(e),
                'operation': 'cleanup'
            }
    
    def wait_for_completion(self, timeout: Optional[float] = None):
        """
        Wait for cache warming to complete.
        
        Args:
            timeout: Maximum time to wait in seconds (None = wait forever)
        """
        if self.warming_thread and self.warming_thread.is_alive():
            self.warming_thread.join(timeout=timeout)


def warm_cache_after_git_operation(
    project_root: Optional[Path] = None,
    operations: Optional[List[str]] = None
):
    """
    Convenience function to warm cache after git operations.
    Called by git hooks (post-checkout, post-merge).
    
    Args:
        project_root: Project root directory (auto-detected if None)
        operations: List of operations to warm (all by default)
    """
    try:
        warmer = CacheWarmer(project_root)
        warmer.warm_cache_background(operations)
        
        # Don't wait - let it run in background
        logger.info("Cache warming initiated (running in background)")
    
    except Exception as e:
        # Don't fail git operations if cache warming fails
        logger.warning(f"Failed to start cache warming: {e}")


def main():
    """CLI entry point for manual cache warming."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='CORTEX Cache Warmer - Pre-populate cache for faster operations'
    )
    parser.add_argument(
        '--project-root',
        type=Path,
        help='Project root directory (auto-detected if not specified)'
    )
    parser.add_argument(
        '--operations',
        nargs='+',
        choices=['align', 'deploy', 'optimize', 'cleanup'],
        help='Operations to warm (default: all)'
    )
    parser.add_argument(
        '--wait',
        action='store_true',
        help='Wait for warming to complete before exiting'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Start warming
    warmer = CacheWarmer(args.project_root)
    warmer.warm_cache_background(args.operations)
    
    if args.wait:
        print("Waiting for cache warming to complete...")
        warmer.wait_for_completion()
        print("✅ Cache warming complete")
    else:
        print("🔥 Cache warming started in background")
        print("   (Operations will complete asynchronously)")


if __name__ == '__main__':
    main()
