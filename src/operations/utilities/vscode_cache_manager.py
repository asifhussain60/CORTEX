"""
VSCode Cache Manager - CORTEX v5.0
Optimizes IDE performance before/during autonomous operations.

Author: Asif Hussain
Created: January 4, 2026
Part of: CORTEX-5.0 Sub-Plan 00D
"""

import os
import shutil
import platform
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime
from enum import Enum


logger = logging.getLogger(__name__)


class Platform(Enum):
    """Supported platforms."""
    WINDOWS = "Windows"
    MAC = "Darwin"
    LINUX = "Linux"


class VSCodeCacheManager:
    """
    Manages VSCode/Copilot cache for optimal CORTEX performance.
    
    Features:
    - Pre-flight optimization before autonomous operations
    - Full cleanup for maintenance workflows
    - Cross-platform support (Windows, macOS, Linux)
    - Health diagnostics and metrics logging
    
    Usage:
        # Pre-flight (lightweight, before autonomous operations)
        manager = VSCodeCacheManager()
        results = manager.pre_flight_optimize()
        
        # Full cleanup (aggressive, for maintenance)
        results = manager.full_cleanup()
        
        # Health check
        health = manager.health_check()
    """
    
    # Platform-specific cache paths
    CACHE_PATHS = {
        Platform.WINDOWS: {
            "copilot_chat": "%APPDATA%\\Code\\User\\globalStorage\\github.copilot-chat",
            "extension_vsix": "%APPDATA%\\Code\\CachedExtensionVSIXs",
            "general_cache": "%APPDATA%\\Code\\Cache",
            "cached_data": "%APPDATA%\\Code\\CachedData"
        },
        Platform.MAC: {
            "copilot_chat": "~/Library/Application Support/Code/User/globalStorage/github.copilot-chat",
            "extension_vsix": "~/Library/Application Support/Code/CachedExtensionVSIXs",
            "general_cache": "~/Library/Application Support/Code/Cache",
            "cached_data": "~/Library/Application Support/Code/CachedData"
        },
        Platform.LINUX: {
            "copilot_chat": "~/.config/Code/User/globalStorage/github.copilot-chat",
            "extension_vsix": "~/.config/Code/CachedExtensionVSIXs",
            "general_cache": "~/.config/Code/Cache",
            "cached_data": "~/.config/Code/CachedData"
        }
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize VSCode Cache Manager.
        
        Args:
            config: Optional configuration dict with keys:
                - enabled: bool (default True)
                - pre_flight.enabled: bool (default True)
                - pre_flight.threshold_mb: int (default 100)
                - pre_flight.log_metrics: bool (default True)
                - maintenance.full_cleanup: bool (default True)
        """
        self.config = config or {}
        self.platform = self._detect_platform()
        self.paths = self._resolve_paths()
        
        logger.debug(f"VSCodeCacheManager initialized for {self.platform.value}")
    
    def _detect_platform(self) -> Platform:
        """Detect current operating system."""
        system = platform.system()
        
        if system == "Windows":
            return Platform.WINDOWS
        elif system == "Darwin":
            return Platform.MAC
        elif system == "Linux":
            return Platform.LINUX
        else:
            logger.warning(f"Unknown platform: {system}, defaulting to Linux")
            return Platform.LINUX
    
    def _resolve_paths(self) -> Dict[str, Path]:
        """
        Resolve platform-specific cache paths.
        
        Returns:
            Dict mapping cache names to resolved Path objects
        """
        raw_paths = self.CACHE_PATHS[self.platform]
        resolved = {}
        
        for cache_name, path_template in raw_paths.items():
            try:
                # Expand environment variables and user home
                if self.platform == Platform.WINDOWS:
                    # Windows: %APPDATA% → C:\Users\{user}\AppData\Roaming
                    expanded = os.path.expandvars(path_template)
                else:
                    # macOS/Linux: ~ → /Users/{user} or /home/{user}
                    expanded = os.path.expanduser(path_template)
                
                resolved[cache_name] = Path(expanded)
                logger.debug(f"Resolved {cache_name}: {resolved[cache_name]}")
                
            except Exception as e:
                logger.error(f"Failed to resolve path for {cache_name}: {e}")
                resolved[cache_name] = None
        
        return resolved
    
    def _get_directory_size(self, path: Path) -> float:
        """
        Calculate directory size in MB.
        
        Args:
            path: Directory path
        
        Returns:
            Size in MB (0.0 if path doesn't exist or error)
        """
        if not path or not path.exists():
            return 0.0
        
        try:
            total_size = 0
            for entry in path.rglob('*'):
                if entry.is_file():
                    total_size += entry.stat().st_size
            
            return total_size / (1024 * 1024)  # Convert to MB
        except Exception as e:
            logger.warning(f"Error calculating size for {path}: {e}")
            return 0.0
    
    def _clear_cache_directory(
        self,
        cache_name: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Clear a specific cache directory.
        
        Args:
            cache_name: Name of cache (e.g., 'copilot_chat')
            dry_run: If True, only report what would be deleted
        
        Returns:
            Dict with keys: success, before_mb, after_mb, freed_mb, error
        """
        path = self.paths.get(cache_name)
        
        if not path:
            return {
                "success": False,
                "error": f"Path not resolved for {cache_name}"
            }
        
        if not path.exists():
            logger.debug(f"{cache_name} does not exist, skipping")
            return {
                "success": True,
                "before_mb": 0.0,
                "after_mb": 0.0,
                "freed_mb": 0.0,
                "skipped": True
            }
        
        try:
            # Calculate size before
            before_mb = self._get_directory_size(path)
            
            if dry_run:
                logger.info(f"[DRY RUN] Would clear {cache_name}: {before_mb:.2f} MB")
                return {
                    "success": True,
                    "before_mb": before_mb,
                    "after_mb": before_mb,  # No change in dry run
                    "freed_mb": 0.0,
                    "dry_run": True
                }
            
            # Actual deletion
            logger.info(f"Clearing {cache_name}: {before_mb:.2f} MB")
            shutil.rmtree(path)
            
            # Recreate empty directory (preserve structure)
            path.mkdir(parents=True, exist_ok=True)
            
            after_mb = self._get_directory_size(path)
            freed_mb = before_mb - after_mb
            
            logger.info(f"✅ Cleared {cache_name}: {freed_mb:.2f} MB freed")
            
            return {
                "success": True,
                "before_mb": before_mb,
                "after_mb": after_mb,
                "freed_mb": freed_mb
            }
        
        except PermissionError as e:
            logger.warning(f"Permission denied clearing {cache_name}: {e}")
            return {
                "success": False,
                "error": f"Permission denied: {e}"
            }
        except Exception as e:
            logger.error(f"Error clearing {cache_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def pre_flight_optimize(
        self,
        dry_run: bool = False,
        log_metrics: bool = True,
        fail_silently: bool = True
    ) -> Dict[str, Any]:
        """
        Lightweight cache optimization before autonomous operations.
        
        Target: Copilot Chat storage (primary cache growth source)
        Threshold: Clear if > threshold_mb (default 100 MB)
        
        Args:
            dry_run: If True, only report what would be done
            log_metrics: If True, log metrics to cache-optimization.jsonl
            fail_silently: If True, catch exceptions and return error info
        
        Returns:
            Dict with keys:
                - success: bool
                - timestamp: str
                - duration_ms: int
                - cache_cleared: Dict[str, Dict] (results per cache)
                - summary: str
                - error: str (if failed)
        """
        start_time = datetime.now()
        
        try:
            # Check if enabled
            if not self.config.get("enabled", True):
                logger.debug("Cache management disabled in config")
                return {
                    "success": True,
                    "skipped": True,
                    "reason": "disabled_in_config"
                }
            
            pre_flight_config = self.config.get("pre_flight", {})
            if not pre_flight_config.get("enabled", True):
                logger.debug("Pre-flight optimization disabled in config")
                return {
                    "success": True,
                    "skipped": True,
                    "reason": "pre_flight_disabled"
                }
            
            threshold_mb = pre_flight_config.get("threshold_mb", 100)
            
            # Health check first
            copilot_chat_path = self.paths.get("copilot_chat")
            if not copilot_chat_path or not copilot_chat_path.exists():
                logger.debug("Copilot Chat cache not found, nothing to optimize")
                return {
                    "success": True,
                    "skipped": True,
                    "reason": "cache_not_found"
                }
            
            current_size = self._get_directory_size(copilot_chat_path)
            
            # Only clear if above threshold
            if current_size < threshold_mb:
                logger.debug(f"Copilot Chat cache ({current_size:.2f} MB) below threshold ({threshold_mb} MB)")
                return {
                    "success": True,
                    "skipped": True,
                    "reason": "below_threshold",
                    "current_size_mb": current_size,
                    "threshold_mb": threshold_mb
                }
            
            # Clear Copilot Chat cache
            logger.info(f"Pre-flight: Clearing Copilot Chat cache ({current_size:.2f} MB)")
            cache_result = self._clear_cache_directory("copilot_chat", dry_run=dry_run)
            
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            result = {
                "success": cache_result["success"],
                "timestamp": start_time.isoformat(),
                "duration_ms": duration_ms,
                "cache_cleared": {
                    "copilot_chat": cache_result
                },
                "summary": f"Freed {cache_result.get('freed_mb', 0):.2f} MB from Copilot Chat cache"
            }
            
            # Log metrics
            if log_metrics and pre_flight_config.get("log_metrics", True):
                self._log_metrics("pre_flight_optimize", result)
            
            return result
        
        except Exception as e:
            if fail_silently:
                logger.warning(f"Pre-flight optimization failed (non-critical): {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "timestamp": start_time.isoformat()
                }
            else:
                raise
    
    def full_cleanup(
        self,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Aggressive cache cleanup for maintenance workflows.
        
        Clears all VSCode caches:
        - Copilot Chat storage
        - Extension VSIX cache
        - General cache
        - Cached data
        
        Args:
            dry_run: If True, only report what would be done
        
        Returns:
            Dict with keys:
                - success: bool
                - timestamp: str
                - duration_ms: int
                - cache_cleared: Dict[str, Dict] (results per cache)
                - total_freed_mb: float
                - summary: str
        """
        start_time = datetime.now()
        
        logger.info("Starting full VSCode cache cleanup")
        
        # Check if enabled
        maintenance_config = self.config.get("maintenance", {})
        if not maintenance_config.get("full_cleanup", True):
            logger.debug("Full cleanup disabled in config")
            return {
                "success": True,
                "skipped": True,
                "reason": "full_cleanup_disabled"
            }
        
        # Clear all caches
        cache_results = {}
        for cache_name in ["copilot_chat", "extension_vsix", "general_cache", "cached_data"]:
            result = self._clear_cache_directory(cache_name, dry_run=dry_run)
            cache_results[cache_name] = result
        
        # Calculate totals
        total_freed = sum(
            result.get("freed_mb", 0)
            for result in cache_results.values()
        )
        
        all_success = all(
            result.get("success", False) or result.get("skipped", False)
            for result in cache_results.values()
        )
        
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        result = {
            "success": all_success,
            "timestamp": start_time.isoformat(),
            "duration_ms": duration_ms,
            "cache_cleared": cache_results,
            "total_freed_mb": total_freed,
            "summary": f"Full cleanup: {total_freed:.2f} MB freed from {len(cache_results)} caches"
        }
        
        logger.info(f"✅ {result['summary']}")
        
        return result
    
    def health_check(self) -> Dict[str, Any]:
        """
        Diagnostic information about VSCode caches.
        
        Returns:
            Dict with keys:
                - timestamp: str
                - platform: str
                - caches: Dict[str, Dict] with size and status per cache
                - total_size_mb: float
                - recommendations: List[str]
        """
        logger.debug("Running cache health check")
        
        cache_info = {}
        total_size = 0.0
        recommendations = []
        
        for cache_name, path in self.paths.items():
            if not path:
                cache_info[cache_name] = {
                    "status": "error",
                    "error": "path_not_resolved"
                }
                continue
            
            if not path.exists():
                cache_info[cache_name] = {
                    "status": "not_found",
                    "path": str(path)
                }
                continue
            
            size_mb = self._get_directory_size(path)
            total_size += size_mb
            
            # Status based on size
            if cache_name == "copilot_chat" and size_mb > 100:
                status = "warning"
                recommendations.append(f"Copilot Chat cache is large ({size_mb:.2f} MB), consider clearing")
            elif size_mb > 500:
                status = "warning"
                recommendations.append(f"{cache_name} is large ({size_mb:.2f} MB)")
            else:
                status = "healthy"
            
            cache_info[cache_name] = {
                "status": status,
                "size_mb": round(size_mb, 2),
                "path": str(path)
            }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "platform": self.platform.value,
            "caches": cache_info,
            "total_size_mb": round(total_size, 2),
            "recommendations": recommendations
        }
    
    def _log_metrics(self, operation: str, result: Dict[str, Any]):
        """
        Log metrics to cache-optimization.jsonl.
        
        Args:
            operation: Operation name (e.g., 'pre_flight_optimize')
            result: Operation result dict
        """
        try:
            from pathlib import Path
            import json
            
            # Log file location
            log_dir = Path.cwd() / "logs"
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / "cache-optimization.jsonl"
            
            # Metrics entry
            metrics = {
                "timestamp": result.get("timestamp", datetime.now().isoformat()),
                "operation": operation,
                "platform": self.platform.value,
                "duration_ms": result.get("duration_ms", 0),
                "success": result.get("success", False),
                "cache_cleared": result.get("cache_cleared", {}),
                "total_freed_mb": result.get("total_freed_mb", sum(
                    cache.get("freed_mb", 0)
                    for cache in result.get("cache_cleared", {}).values()
                ))
            }
            
            # Append to JSONL file
            with open(log_file, "a") as f:
                f.write(json.dumps(metrics) + "\n")
            
            logger.debug(f"Metrics logged to {log_file}")
        
        except Exception as e:
            logger.warning(f"Failed to log metrics: {e}")


# Convenience functions for quick access

def optimize_pre_flight(config: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Quick pre-flight optimization.
    
    Args:
        config: Optional config dict
    
    Returns:
        Operation results
    """
    manager = VSCodeCacheManager(config)
    return manager.pre_flight_optimize()


def run_full_cleanup(config: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Quick full cleanup.
    
    Args:
        config: Optional config dict
    
    Returns:
        Operation results
    """
    manager = VSCodeCacheManager(config)
    return manager.full_cleanup()


def check_cache_health(config: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Quick health check.
    
    Args:
        config: Optional config dict
    
    Returns:
        Health check results
    """
    manager = VSCodeCacheManager(config)
    return manager.health_check()
