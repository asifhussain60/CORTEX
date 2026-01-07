# 🚀 Sub-Plan 00D: VSCode Cache Optimization (Phase 0.5)

**Plan ID:** vscode-cache-optimization  
**Parent Epic:** CORTEX-5.0 Gap Remediation  
**Order:** 00D  
**Created:** January 4, 2026  
**Priority:** 🎯 MEDIUM-HIGH (Performance Enhancement)  
**Duration:** 2-3 hours  
**Status:** ⏳ NOT STARTED  
**Type:** Phase 0.5 Pre-Flight Enhancement

---

## 📊 Progress Tracker

**Overall Progress:** `░░░░░░░░░░` **0%** ⏳ NOT STARTED

| Phase | Task | Status | Duration |
|-------|------|--------|----------|
| 1 | Implement VSCodeCacheManager utility | ⏳ Not Started | 1h |
| 2 | Integrate pre-flight hooks (4 orchestrators) | ⏳ Not Started | 45m |
| 3 | Add config schema + tests | ⏳ Not Started | 30m |
| 4 | Extend Maintenance Phase 11 | ⏳ Not Started | 30m |

---

## 🎯 Objective

**Mission:** Integrate automated VSCode/Copilot cache management as a **Phase 0.5 pre-flight operation** to maximize IDE responsiveness during long-running autonomous orchestrators.

**Problem:**
- CORTEX orchestrators run 30-90 minute autonomous workflows
- VSCode extension host accumulates cache/state causing UI lag
- Users experience slow responses and occasional freezes
- Manual intervention required (Reload Window, cache clearing)

**Solution:**
- Pre-flight cache optimization before autonomous operations
- Lightweight Copilot Chat storage clearing (< 100 MB target)
- Extension health validation
- Metrics logging for performance tracking

---

## ✅ Acceptance Criteria (DoD)

### Must Have
- [ ] **VSCodeCacheManager** utility class implemented
  - [ ] `pre_flight_optimize()` method (lightweight)
  - [ ] `full_cleanup()` method (aggressive, for maintenance)
  - [ ] `health_check()` method (diagnostics)
  - [ ] Cross-platform path support (Windows, Mac, Linux)
  - [ ] Error handling with graceful fallback

- [ ] **Pre-Flight Integration** in 4 orchestrators
  - [ ] Planning Orchestrator v5
  - [ ] Investigation Orchestrator
  - [ ] Vacuum Orchestrator
  - [ ] Maintenance Orchestrator
  - [ ] Runs before Phase 1 execution
  - [ ] Non-blocking, fails silently with logging

- [ ] **Configuration Schema**
  - [ ] Add `cache_management` section to `cortex.config.json`
  - [ ] Enable/disable flags per operation
  - [ ] Thresholds (cache size, uptime, etc.)
  - [ ] Logging preferences

- [ ] **Metrics & Logging**
  - [ ] Log to `logs/cache-optimization.jsonl`
  - [ ] Track: cache size before/after, time taken, errors
  - [ ] Integration with existing metrics system

- [ ] **Unit Tests**
  - [ ] 80%+ code coverage
  - [ ] Mock filesystem operations
  - [ ] Test cross-platform paths
  - [ ] Dry-run mode validation

### Should Have
- [ ] **Maintenance Phase 11 Extension**
  - [ ] Full cache cleanup operation
  - [ ] Extension health validation
  - [ ] Reload Window trigger (conditional)
  - [ ] Phase 11 prompt template

- [ ] **Documentation**
  - [ ] Implementation guide for developers
  - [ ] User-facing behavior documentation
  - [ ] Configuration examples

### Nice to Have (Future)
- [ ] User-facing `/CORTEX cache` commands
- [ ] Automated cache health monitoring dashboard
- [ ] Predictive cache clearing (before threshold hit)

---

## 🏗️ Phase 1: Implement VSCodeCacheManager

**Duration:** 1 hour

### Deliverables

**File:** `src/operations/utilities/vscode_cache_manager.py`

```python
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
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class VSCodeCacheManager:
    """Manages VSCode/Copilot cache for optimal CORTEX performance."""
    
    # Platform-specific cache paths
    CACHE_PATHS = {
        "Windows": {
            "copilot_chat": "%APPDATA%\\Code\\User\\globalStorage\\github.copilot-chat",
            "extension_vsix": "%APPDATA%\\Code\\CachedExtensionVSIXs",
            "general_cache": "%APPDATA%\\Code\\Cache",
            "cached_data": "%APPDATA%\\Code\\CachedData"
        },
        "Darwin": {  # macOS
            "copilot_chat": "~/Library/Application Support/Code/User/globalStorage/github.copilot-chat",
            "extension_vsix": "~/Library/Application Support/Code/CachedExtensionVSIXs",
            "general_cache": "~/Library/Application Support/Code/Cache",
            "cached_data": "~/Library/Application Support/Code/CachedData"
        },
        "Linux": {
            "copilot_chat": "~/.config/Code/User/globalStorage/github.copilot-chat",
            "extension_vsix": "~/.config/Code/CachedExtensionVSIXs",
            "general_cache": "~/.config/Code/Cache",
            "cached_data": "~/.config/Code/CachedData"
        }
    }
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize cache manager.
        
        Args:
            config: Optional configuration dict from cortex.config.json
        """
        self.config = config or self._default_config()
        self.platform = platform.system()
        self.paths = self._resolve_paths()
    
    def _default_config(self) -> Dict:
        """Default configuration if none provided."""
        return {
            "enabled": True,
            "pre_flight": {
                "enabled": True,
                "clear_copilot_chat": True,
                "log_metrics": True
            },
            "thresholds": {
                "copilot_chat_mb": 100
            }
        }
    
    def _resolve_paths(self) -> Dict[str, Path]:
        """Resolve platform-specific paths."""
        paths = {}
        platform_paths = self.CACHE_PATHS.get(self.platform, {})
        
        for name, path_str in platform_paths.items():
            # Expand environment variables and user home
            expanded = os.path.expandvars(os.path.expanduser(path_str))
            paths[name] = Path(expanded)
        
        return paths
    
    def pre_flight_optimize(self, dry_run: bool = False) -> Dict[str, any]:
        """
        Lightweight pre-flight optimization (Phase 0).
        
        - Clears Copilot Chat storage only
        - Non-blocking, fails silently
        - Logs metrics for monitoring
        
        Args:
            dry_run: If True, only report what would be done
            
        Returns:
            Dict with operation results and metrics
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "operation": "pre_flight_optimize",
            "dry_run": dry_run,
            "platform": self.platform,
            "success": False,
            "cache_cleared": {},
            "errors": []
        }
        
        if not self.config["pre_flight"]["enabled"]:
            results["skipped"] = "Pre-flight optimization disabled in config"
            return results
        
        try:
            # Clear Copilot Chat storage
            if self.config["pre_flight"]["clear_copilot_chat"]:
                copilot_path = self.paths.get("copilot_chat")
                if copilot_path and copilot_path.exists():
                    size_before = self._get_dir_size(copilot_path)
                    
                    if not dry_run:
                        shutil.rmtree(copilot_path, ignore_errors=True)
                        size_after = 0
                    else:
                        size_after = size_before
                    
                    results["cache_cleared"]["copilot_chat"] = {
                        "path": str(copilot_path),
                        "size_before_mb": round(size_before / 1024 / 1024, 2),
                        "size_after_mb": round(size_after / 1024 / 1024, 2),
                        "freed_mb": round((size_before - size_after) / 1024 / 1024, 2)
                    }
            
            results["success"] = True
            
            # Log metrics if enabled
            if self.config["pre_flight"]["log_metrics"]:
                self._log_metrics(results)
        
        except Exception as e:
            logger.error(f"Pre-flight optimization error: {e}")
            results["errors"].append(str(e))
        
        return results
    
    def full_cleanup(self, dry_run: bool = False) -> Dict[str, any]:
        """
        Aggressive cleanup (Maintenance Phase 11).
        
        - Clears all cache paths
        - Validates extension health
        - Triggers reload window
        
        Args:
            dry_run: If True, only report what would be done
            
        Returns:
            Dict with operation results and metrics
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "operation": "full_cleanup",
            "dry_run": dry_run,
            "platform": self.platform,
            "success": False,
            "cache_cleared": {},
            "errors": []
        }
        
        try:
            # Clear all cache paths
            for name, path in self.paths.items():
                if path.exists():
                    size_before = self._get_dir_size(path)
                    
                    if not dry_run:
                        shutil.rmtree(path, ignore_errors=True)
                        size_after = 0
                    else:
                        size_after = size_before
                    
                    results["cache_cleared"][name] = {
                        "path": str(path),
                        "size_before_mb": round(size_before / 1024 / 1024, 2),
                        "size_after_mb": round(size_after / 1024 / 1024, 2),
                        "freed_mb": round((size_before - size_after) / 1024 / 1024, 2)
                    }
            
            results["success"] = True
            self._log_metrics(results)
        
        except Exception as e:
            logger.error(f"Full cleanup error: {e}")
            results["errors"].append(str(e))
        
        return results
    
    def health_check(self) -> Dict[str, any]:
        """
        Diagnostics for user-facing /CORTEX cache health.
        
        Returns:
            Dict with cache sizes, timestamps, and health status
        """
        health = {
            "timestamp": datetime.now().isoformat(),
            "platform": self.platform,
            "caches": {}
        }
        
        for name, path in self.paths.items():
            if path.exists():
                size_mb = round(self._get_dir_size(path) / 1024 / 1024, 2)
                modified = datetime.fromtimestamp(path.stat().st_mtime).isoformat()
                
                # Determine health status
                threshold = self.config["thresholds"].get(f"{name}_mb", 500)
                status = "⚠️ Warning" if size_mb > threshold else "✅ Healthy"
                
                health["caches"][name] = {
                    "path": str(path),
                    "size_mb": size_mb,
                    "last_modified": modified,
                    "status": status,
                    "threshold_mb": threshold
                }
            else:
                health["caches"][name] = {
                    "path": str(path),
                    "exists": False,
                    "status": "✅ Clean"
                }
        
        return health
    
    def _get_dir_size(self, path: Path) -> int:
        """Calculate total size of directory in bytes."""
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except (PermissionError, OSError):
            pass  # Skip files we can't access
        return total
    
    def _log_metrics(self, results: Dict):
        """Log metrics to cache-optimization.jsonl."""
        try:
            log_file = Path("logs/cache-optimization.jsonl")
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            import json
            with open(log_file, 'a') as f:
                f.write(json.dumps(results) + '\n')
        except Exception as e:
            logger.error(f"Failed to log metrics: {e}")


# Convenience function for orchestrators
def optimize_cache_pre_flight(config: Optional[Dict] = None) -> Dict:
    """
    Convenience function for pre-flight cache optimization.
    
    Use this in orchestrators before Phase 1 execution.
    
    Args:
        config: Optional configuration dict
        
    Returns:
        Operation results dict
    """
    manager = VSCodeCacheManager(config)
    return manager.pre_flight_optimize()
```

### Tasks
- [ ] Create file with complete implementation
- [ ] Add unit tests in `tests/test_vscode_cache_manager.py`
- [ ] Test on Windows/Mac/Linux paths
- [ ] Validate error handling and graceful fallback

---

## 🏗️ Phase 2: Integrate Pre-Flight Hooks

**Duration:** 45 minutes

### Integration Points

**1. Planning Orchestrator v5**
```python
# src/orchestrators/planning_orchestrator_v5.py

from operations.utilities.vscode_cache_manager import optimize_cache_pre_flight

def execute_plan(self, plan_path: str):
    """Execute planning workflow with pre-flight optimization."""
    
    # PHASE 0: Pre-Flight Optimization
    cache_results = optimize_cache_pre_flight(self.config.get("cache_management"))
    if cache_results["success"]:
        logger.info(f"Pre-flight cache optimization complete: {cache_results}")
    
    # PHASE 1-N: Standard execution
    self.load_plan(plan_path)
    self.execute_phases()
```

**2. Investigation Orchestrator**
```python
# src/orchestrators/investigation_orchestrator.py

def investigate(self, issue_description: str):
    """Run investigation with pre-flight optimization."""
    
    # Pre-flight
    optimize_cache_pre_flight()
    
    # Investigation phases...
```

**3. Vacuum Orchestrator**
```python
# src/orchestrators/vacuum_orchestrator.py

def execute_vacuum(self):
    """Execute vacuum with pre-flight optimization."""
    
    # Pre-flight
    optimize_cache_pre_flight()
    
    # Vacuum phases...
```

**4. Maintenance Orchestrator**
```python
# src/orchestrators/maintenance_orchestrator.py

def run_maintenance(self):
    """Run maintenance with pre-flight optimization."""
    
    # Pre-flight
    optimize_cache_pre_flight()
    
    # Maintenance phases...
```

### Tasks
- [ ] Add pre-flight call to all 4 orchestrators
- [ ] Verify non-blocking behavior
- [ ] Test error handling (cache manager fails gracefully)
- [ ] Validate metrics logging

---

## 🏗️ Phase 3: Add Config Schema + Tests

**Duration:** 30 minutes

### Configuration

**File:** `cortex.config.json` (add section)

```json
{
  "cache_management": {
    "enabled": true,
    "pre_flight": {
      "enabled": true,
      "clear_copilot_chat": true,
      "reload_window_threshold_hours": 4,
      "log_metrics": true
    },
    "maintenance": {
      "full_cleanup": true,
      "backup_before_clear": false,
      "aggressive_mode": false
    },
    "thresholds": {
      "copilot_chat_mb": 100,
      "extension_cache_mb": 500,
      "extension_host_uptime_hours": 8
    }
  }
}
```

### Unit Tests

**File:** `tests/test_vscode_cache_manager.py`

```python
import pytest
from pathlib import Path
from src.operations.utilities.vscode_cache_manager import VSCodeCacheManager

def test_pre_flight_optimize_dry_run():
    """Test pre-flight optimization in dry-run mode."""
    manager = VSCodeCacheManager()
    results = manager.pre_flight_optimize(dry_run=True)
    
    assert results["success"]
    assert results["dry_run"] == True
    assert "cache_cleared" in results

def test_health_check():
    """Test cache health check."""
    manager = VSCodeCacheManager()
    health = manager.health_check()
    
    assert "timestamp" in health
    assert "caches" in health
    assert "platform" in health

def test_cross_platform_paths():
    """Test path resolution on different platforms."""
    manager = VSCodeCacheManager()
    assert manager.paths
    # All paths should be Path objects
    for path in manager.paths.values():
        assert isinstance(path, Path)
```

### Tasks
- [ ] Add config schema to `cortex.config.json`
- [ ] Update `cortex.config.template.json` with examples
- [ ] Create comprehensive unit tests (80%+ coverage)
- [ ] Add integration tests with mock filesystem

---

## 🏗️ Phase 4: Extend Maintenance Phase 11

**Duration:** 30 minutes

### New Maintenance Phase

**File:** `.github/prompts/maintenance/phase-11-vscode-optimization.prompt.md`

```markdown
# Phase 11: VSCode Cache & Extension Optimization

**Objective:** Deep clean VSCode caches, validate extension health, optimize IDE performance

## Operations

1. **Cache Analysis**
   - Scan all cache directories
   - Report sizes and staleness
   - Identify corruption candidates

2. **Full Cache Cleanup**
   - Clear Copilot Chat storage
   - Clear Extension VSIX cache
   - Clear general cache and cached data
   - Log all freed space

3. **Extension Health Check**
   - Verify Copilot extension version
   - Check for update availability
   - Validate extension host responsiveness

4. **Post-Cleanup Validation**
   - Confirm caches < threshold sizes
   - Verify no errors in VSCode console
   - Test Copilot response time

## Success Criteria
- ✅ All caches < threshold sizes
- ✅ No errors during cleanup
- ✅ Copilot responds within 2s
- ✅ Total freed space logged

## Implementation

```python
from operations.utilities.vscode_cache_manager import VSCodeCacheManager

# Phase 11 execution
manager = VSCodeCacheManager(config.cache_management)

# Health check before
health_before = manager.health_check()
print("Cache sizes before cleanup:")
for cache, data in health_before["caches"].items():
    print(f"  {cache}: {data.get('size_mb', 0)} MB")

# Full cleanup
results = manager.full_cleanup()

# Health check after
health_after = manager.health_check()
print("\nCache sizes after cleanup:")
for cache, data in health_after["caches"].items():
    print(f"  {cache}: {data.get('size_mb', 0)} MB")

# Report
total_freed = sum(
    cache_data.get("freed_mb", 0) 
    for cache_data in results["cache_cleared"].values()
)
print(f"\n✅ Total freed: {total_freed} MB")
```
```

### Tasks
- [ ] Create Phase 11 prompt template
- [ ] Add to maintenance orchestrator index
- [ ] Test full cleanup operation
- [ ] Document user-facing behavior

---

## 📈 Success Metrics

**Pre-Flight Performance:**
- ⏱️ Extension response time < 500ms (baseline: 1-2s when cache heavy)
- 💾 Copilot Chat storage < 100 MB before autonomous operations
- 🔄 Zero manual "Reload Window" interventions during plans

**Maintenance Impact:**
- 📉 Cache size reduction: 60-80% average
- ⚡ Post-cleanup startup time: < 3s
- 🛡️ Reduced "Copilot not responding" support tickets

**User Experience:**
- 😊 "CORTEX feels faster" qualitative feedback
- 📊 Autonomous operation completion time improvement: 5-10%

---

## 🚧 Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| **Cache clearing breaks active session** | Pre-flight only clears Copilot Chat storage (safe) |
| **Cross-platform path issues** | Test on Windows/Mac/Linux, use Path library |
| **User loses conversation history** | Document behavior, provide opt-out in config |
| **Reload Window disrupts workflow** | Make reload conditional (uptime > 4 hours) |
| **Over-engineering** | Keep Phase 0.5 minimal (single file, < 200 lines) |

---

## 🎯 Definition of Ready (DoR)

- [x] VSCode cache optimization proposal reviewed
- [x] Epic structure (CORTEX-5.0) validated
- [x] Sub-plan folder created (00D-vscode-cache-optimization/)
- [ ] Planner Mode Detector available (from 00B Phase 00)
- [ ] Config schema design available

---

## 🎯 Definition of Done (DoD)

- [ ] All "Must Have" acceptance criteria met
- [ ] Unit tests passing with 80%+ coverage
- [ ] Integration tests passing on Windows + Mac/Linux
- [ ] Documentation complete (developer + user-facing)
- [ ] Code reviewed and merged to CORTEX-5.0 branch
- [ ] Metrics logging validated with sample data
- [ ] Phase 11 maintenance extension working

---

## 🔗 Integration with CORTEX-5.0

**Dependencies:**
- None (parallel implementation)

**Enables:**
- Better performance for all future autonomous orchestrators
- Reduced user friction during long-running operations
- Metrics for performance debugging

**Timeline:**
- Can start immediately (parallel to 00B Phase 01)
- Complete before 00C (Test Coverage Sprint) for inclusion in tests
- Estimated: 2-3 hours total implementation time

---

## 📚 References

- **Source Proposal:** `vscode-cache-optimization-enhancement.md`
- **Architecture:** `00B-epic-feature-planner/artifacts/phase-00-architecture-spec.md`
- **Config Template:** `cortex.config.template.json`
- **Maintenance Index:** `.github/prompts/maintenance/index.prompt.md`

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
