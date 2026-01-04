# VSCode Cache Optimization - CORTEX-5.0 Enhancement Proposal

**Status:** 📋 PROPOSAL  
**Priority:** MEDIUM-HIGH (Phase 0.5 Pre-Flight Enhancement)  
**Effort:** 2-3 hours  
**Impact:** Performance optimization for autonomous orchestrators  
**Author:** GitHub Copilot  
**Date:** January 4, 2026  

---

## 🎯 Executive Summary

Integrate automated VSCode/Copilot cache management as a **Phase 0.5 pre-flight operation** to maximize IDE responsiveness during long-running autonomous orchestrators (Planning v5, Investigation, Vacuum, Maintenance).

**Key Insight:** While cache clearing doesn't prevent token-based summarization, it significantly reduces extension host lag, UI freezes, and accumulated state corruption during multi-phase operations.

---

## 📊 Problem Statement

**Current Gap:**
- CORTEX orchestrators run 30-90 minute autonomous workflows
- VSCode extension host accumulates state/cache during execution
- Users experience UI lag, slow responses, and occasional freezes
- Manual intervention required (`Reload Window`, cache clearing)

**Impact:**
- Reduced perceived performance of CORTEX operations
- User frustration during critical autonomous phases
- Increased support burden for "Why is Copilot slow?" questions

---

## ✅ Proposed Solution

### Architecture

```
┌─────────────────────────────────────────────────────┐
│  User Issues: /CORTEX plan user-authentication     │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │  PHASE 0: Pre-Flight│ ◄─── NEW INTEGRATION POINT
         │  Cache Optimization │
         └─────────┬───────────┘
                   │
                   ├─► Clear Copilot Chat Storage
                   ├─► Verify Extension Health
                   ├─► Reload Window (if stale)
                   └─► Log Optimization Metrics
                   │
                   ▼
         ┌─────────────────────┐
         │  PHASE 1-N: Plan    │
         │  Execution          │
         └─────────────────────┘
```

### Integration Points

**1. Pre-Flight Middleware (RECOMMENDED)**
- **Trigger:** Before any autonomous orchestrator starts
- **Scope:** Planning v5, Investigation, Vacuum, Maintenance
- **Behavior:** Silent, non-blocking, logs to metrics

**2. Maintenance Orchestrator (SUPPLEMENTAL)**
- **Trigger:** User runs `/CORTEX maintenance` or scheduled intervals
- **Scope:** System-wide cleanup (broader than pre-flight)
- **Behavior:** Aggressive cache clearing + validation

**3. Manual Command (OPTIONAL)**
- **Trigger:** `/CORTEX cache clear|reload|health`
- **Scope:** User-initiated troubleshooting
- **Behavior:** Interactive with confirmation prompts

---

## 🛠️ Implementation Plan

### Phase 0.5 Components

#### **1. New Utility Module**
**File:** `src/operations/utilities/vscode_cache_manager.py`

```python
"""
VSCode Cache Manager - CORTEX v5.0
Optimizes IDE performance before/during autonomous operations
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class VSCodeCacheManager:
    """Manages VSCode/Copilot cache for optimal CORTEX performance"""
    
    CACHE_PATHS = {
        "copilot_chat": "%APPDATA%\\Code\\User\\globalStorage\\github.copilot-chat",
        "extension_vsix": "%APPDATA%\\Code\\CachedExtensionVSIXs",
        "general_cache": "%APPDATA%\\Code\\Cache",
        "cached_data": "%APPDATA%\\Code\\CachedData"
    }
    
    def pre_flight_optimize(self) -> Dict[str, bool]:
        """
        Lightweight pre-flight optimization (Phase 0)
        - Clears Copilot Chat storage only
        - Non-blocking, fails silently
        - Logs metrics for monitoring
        """
        pass
    
    def full_cleanup(self) -> Dict[str, bool]:
        """
        Aggressive cleanup (Maintenance Phase 11)
        - Clears all cache paths
        - Validates extension health
        - Triggers reload window
        """
        pass
    
    def health_check(self) -> Dict[str, any]:
        """
        Diagnostics for user-facing /CORTEX cache health
        - Cache sizes
        - Last modified timestamps
        - Extension host uptime
        """
        pass
```

**Features:**
- ✅ Windows path resolution (`%APPDATA%` expansion)
- ✅ Cross-platform support (Mac/Linux paths)
- ✅ Safe deletion with error handling
- ✅ Metrics logging to `logs/cache-optimization.jsonl`
- ✅ Dry-run mode for testing

---

#### **2. Configuration Schema**
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

---

#### **3. Pre-Flight Hook Integration**
**File:** `src/orchestrators/planning_orchestrator_v5.py` (example)

```python
# BEFORE PHASE 1 EXECUTION
from operations.utilities.vscode_cache_manager import VSCodeCacheManager

def execute_plan(self, plan_path: str):
    """Execute planning workflow with pre-flight optimization"""
    
    # PHASE 0: Pre-Flight Optimization
    if config.cache_management.pre_flight.enabled:
        cache_mgr = VSCodeCacheManager()
        optimization_results = cache_mgr.pre_flight_optimize()
        self.log_metrics("pre_flight_cache", optimization_results)
    
    # PHASE 1-N: Standard execution
    self.load_plan(plan_path)
    self.execute_phases()
    ...
```

**Integration Targets:**
- ✅ `planning_orchestrator_v5.py`
- ✅ `investigation_orchestrator.py`
- ✅ `vacuum_orchestrator.py`
- ✅ `maintenance_orchestrator.py`

---

#### **4. Maintenance Phase 11 Extension**
**File:** `.github/prompts/maintenance/phase-11-vscode-optimization.prompt.md` (NEW)

```markdown
# Phase 11: VSCode Cache & Extension Optimization

**Objective:** Deep clean VSCode caches, validate extension health, optimize IDE performance

## Operations

1. **Cache Analysis**
   - Scan all cache directories
   - Report sizes and staleness
   - Identify corruption candidates

2. **Copilot Storage Cleanup**
   - Clear `github.copilot-chat` storage
   - Preserve user settings
   - Log cleared conversation count

3. **Extension Cache Cleanup**
   - Clear `CachedExtensionVSIXs`
   - Clear `Cache` and `CachedData`
   - Backup if > 1GB before deletion

4. **Extension Health Check**
   - Verify Copilot extension version
   - Check for update availability
   - Validate extension host responsiveness

5. **Reload Window**
   - Trigger soft restart
   - Validate post-reload state
   - Measure startup time improvement

## Success Criteria
- ✅ All caches < threshold sizes
- ✅ Extension host restart successful
- ✅ No errors in VSCode console
- ✅ Copilot responds within 2s post-reload
```

---

#### **5. User-Facing Command (Optional)**
**File:** `CORTEX.prompt.md` (add routing)

```yaml
| `cache clear`, `cache reload`, `cache health` | **Cache Manager** | 999 | utility |
```

**Behavior:**
```
User: /CORTEX cache clear
CORTEX: 
  🧹 Clearing Copilot Chat storage... ✅ (47 MB freed)
  🔄 Reloading window... (please wait 5s)
  
User: /CORTEX cache health
CORTEX:
  📊 VSCode Cache Health Report
  
  Copilot Chat Storage: 52 MB (⚠️ Above 50 MB threshold)
  Extension Cache: 234 MB (✅ Normal)
  Extension Host Uptime: 6.2 hours (✅ Healthy)
  
  Recommendation: Run /CORTEX cache clear before next long operation
```

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

## 🚧 Implementation Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| **Cache clearing breaks active session** | Pre-flight only clears Copilot Chat storage (safe), not core VSCode cache |
| **Cross-platform path issues** | Test on Windows/Mac/Linux, use `Path` library for abstraction |
| **User loses conversation history** | Document behavior, provide opt-out in config |
| **Reload Window disrupts workflow** | Make reload conditional (uptime > 4 hours), skip if user active |
| **Over-engineering** | Keep Phase 0.5 minimal (single file, < 200 lines), defer complex features |

---

## 🗓️ Integration Timeline

**Assuming Phase 00 Architecture is in progress:**

### **Option A: Parallel Track (RECOMMENDED)**
- **Week 1:** Implement `vscode_cache_manager.py` + unit tests
- **Week 2:** Integrate pre-flight hooks into 4 orchestrators
- **Week 3:** Add Maintenance Phase 11, test end-to-end
- **Week 4:** Documentation + user acceptance testing

**Dependencies:** None (parallel to Phase 00 Architecture)

### **Option B: Sequential Integration**
- **After Phase 00 Complete:** Add as Phase 0.5 enhancement
- **Duration:** 1 week (fast-follow after architecture stabilizes)

---

## 📋 Acceptance Criteria

**Must Have (Phase 0.5):**
- ✅ `VSCodeCacheManager` class implemented with pre-flight method
- ✅ Pre-flight hooks in Planning v5, Investigation, Vacuum, Maintenance
- ✅ Config schema added to `cortex.config.json`
- ✅ Metrics logging to `logs/cache-optimization.jsonl`
- ✅ Unit tests with 80%+ coverage

**Should Have:**
- ✅ Maintenance Phase 11 with full cleanup
- ✅ Cross-platform path support (Windows + Mac/Linux)
- ✅ Dry-run mode for safe testing

**Nice to Have (Future):**
- `/CORTEX cache` user-facing commands
- Automated cache health monitoring dashboard
- Predictive cache clearing (before threshold hit)

---

## 🎯 Recommendation for Phase 00 Architecture Design

**How to Integrate:**

1. **Add Pre-Flight Layer to Master Orchestrator**
   - Insert between "Request Transform" and "Orchestrator Execution"
   - Make it a configurable middleware component
   - Document in `master-orchestrator.yaml`

2. **Extend Orchestrator Base Class**
   ```python
   class BaseOrchestrator:
       def __init__(self):
           self.pre_flight_enabled = config.cache_management.pre_flight.enabled
       
       def execute(self):
           if self.pre_flight_enabled:
               self._run_pre_flight_optimization()
           self._run_phases()
   ```

3. **Add to Phase 0 Visual Progress**
   ```
   PHASE 0: Pre-Flight Optimization [████████████] 100%
     ├─ Cache optimization... ✅
     ├─ Extension health check... ✅
     └─ Environment validation... ✅
   
   PHASE 1: Discovery & Planning [██▒▒▒▒▒▒▒▒▒▒] 15%
   ```

---

## 📚 Related Documents

- **Source:** `.asif/backlog/vscode-cache.md` (original analysis)
- **Architecture:** `cortex-brain/documents/orchestrators-quick-ref.md`
- **Config Template:** `cortex.config.template.json`
- **Maintenance Prompt:** `.github/prompts/maintenance/index.prompt.md`

---

## 🎉 Expected Outcome

**User Experience:**
```
User: /CORTEX plan user-authentication

🧠 CORTEX Planning System v5.0 - Master Orchestrator
PHASE 0: Pre-Flight Optimization [████████████] 100%
  ✅ IDE cache optimized (47 MB freed)
  ✅ Extension health verified
  ✅ Environment ready for autonomous execution

PHASE 1: Discovery & Context Gathering [████████████] 100%
  ... (smooth, no lag or freezes)
```

**Developer Experience:**
- No manual cache management required
- Metrics available for performance debugging
- Simple opt-out if issues arise

**CORTEX Philosophy Alignment:**
- ✅ **Proactive:** Prevents issues before they occur
- ✅ **Autonomous:** Zero user intervention
- ✅ **Performance-focused:** Measurable throughput gains
- ✅ **Context-aware:** Knows when optimization needed

---

## ✅ Final Recommendation

**INCLUDE as Phase 0.5 enhancement** with the following priority:

1. **CORE (Must Ship):** Pre-flight cache optimization for autonomous orchestrators
2. **EXTENDED (Should Ship):** Maintenance Phase 11 integration
3. **FUTURE (Nice to Have):** User-facing `/CORTEX cache` commands

**Rationale:** Low implementation cost (2-3 hours), high user satisfaction impact, aligns with CORTEX's autonomous optimization philosophy.

---

**Document Status:** ✅ READY FOR PHASE 00 ARCHITECTURE REVIEW  
**Next Action:** Review during Phase 00 architecture design session, assign to implementation sprint
